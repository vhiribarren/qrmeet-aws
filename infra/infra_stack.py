from .config import Conf
from datetime import datetime

from aws_cdk import (
    # Duration,
    Stack, BundlingOptions, RemovalPolicy,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_apigateway as apigateway,
    aws_certificatemanager as acm,
    aws_s3_deployment as s3deploy,
    aws_ssm as ssm,
    aws_iam as iam,
    custom_resources as cr,
)

from constructs import Construct


class EdgeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *, conf: Conf, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        edge_redirect = cloudfront.experimental.EdgeFunction(self, f"{conf.app_prefix}-lambda-edge-redirect",
                                                                   function_name=f"{conf.app_prefix}-lambda-edge-redirect",
                                                                   runtime=lambda_.Runtime.NODEJS_14_X,
                                                                   handler="index.handler",
                                                                   code=lambda_.Code.from_asset(
                                                                       "backend/edge_redirect_index")
                                                                   )
        ssm_param = ssm.StringParameter(self, f"{conf.app_prefix}-param-edge-redirect-arn",
                                        parameter_name=f"/{conf.app_prefix}/edge-redirect-arn",
                                        string_value=edge_redirect.function_arn)

        self._edge_redirect = edge_redirect

    @property
    def edge_redirect(self) -> lambda_.Function:
        return self._edge_redirect


class FrontendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *, conf: Conf, api_gw: apigateway.RestApi,
                 zone: route53.HostedZone, edge: lambda_.Function, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # https://stackoverflow.com/questions/68695026/cdk-possible-to-put-the-stack-created-for-edgefunction-resource-in-another-cro
        get_edge_arn_custom_resource = cr.AwsCustomResource(self, "aws-custom",
                                          on_update=cr.AwsSdkCall(
                                              service="SSM",
                                              action="getParameter",
                                              parameters={
                                                  "Name": f"/{conf.app_prefix}/edge-redirect-arn",
                                              },
                                              region="us-east-1",
                                              physical_resource_id=cr.PhysicalResourceId.of(str(datetime.now()))
                                          ),
                                          policy=cr.AwsCustomResourcePolicy.from_statements([
                                              iam.PolicyStatement(
                                                  effect=iam.Effect.ALLOW,
                                                  actions=["ssm:GetParameter*"],
                                                  resources=[
                                                      self.format_arn(
                                                          service="ssm",
                                                          region="us-east-1",
                                                          resource="parameter",
                                                          resource_name=f"{conf.app_prefix}/*"
                                                      )
                                                  ]
                                              )
                                          ])
                                          )


        edge_redirect_arn = get_edge_arn_custom_resource.get_response_field("Parameter.Value")

        bucket = s3.Bucket(self, f"{conf.app_prefix}-frontend-hosting",
                           bucket_name=f"{conf.app_prefix}-frontend-hosting",
                           # website_index_document="index.html",
                           removal_policy=RemovalPolicy.DESTROY)

        certificate = acm.DnsValidatedCertificate(self, f"{conf.app_prefix}-cf-certificate",
                                                  domain_name=zone.zone_name,
                                                  hosted_zone=zone, region="us-east-1")

        api_gw_domaine_name = f"{api_gw.rest_api_id}.execute-api.{self.region}.{self.url_suffix}"
        origin_req_policy = cloudfront.OriginRequestPolicy(self,
                                                           f"{conf.app_prefix}-origin-req-policy",
                                                           origin_request_policy_name=f"{conf.app_prefix}-origin-req-policy",
                                                           query_string_behavior=cloudfront.OriginRequestQueryStringBehavior.all(),
                                                           cookie_behavior=cloudfront.OriginRequestCookieBehavior.all())
        cf_distrib = cloudfront.Distribution(self, f"{conf.app_prefix}-dist",
                                             domain_names=[zone.zone_name],
                                             certificate=certificate,
                                             default_root_object="index.html",
                                             default_behavior=cloudfront.BehaviorOptions(
                                                 origin=origins.S3Origin(bucket),
                                                 edge_lambdas=[cloudfront.EdgeLambda(
                                                     function_version=lambda_.Version.from_version_arn(self,
                                                                                                         f"{conf.app_prefix}-lambda-edge-redirect",
                                                                                                         edge_redirect_arn),
                                                     event_type=cloudfront.LambdaEdgeEventType.VIEWER_REQUEST)]
                                             )
                                             )
        cf_distrib.add_behavior("api/*",
                                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                                origin_request_policy=origin_req_policy,
                                origin=origins.HttpOrigin(
                                    domain_name=api_gw_domaine_name,
                                    origin_path=f"/{api_gw.deployment_stage.stage_name}",
                                ))
        cf_distrib.add_behavior("meet/*",
                                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                                origin_request_policy=origin_req_policy,
                                origin=origins.HttpOrigin(
                                    domain_name=api_gw_domaine_name,
                                    origin_path=f"/{api_gw.deployment_stage.stage_name}",
                                ))
        route53.ARecord(self, f"{conf.app_prefix}-cloudfront-alias",
                        zone=zone,
                        target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(cf_distrib)))

        s3deploy.BucketDeployment(self, f"{conf.app_prefix}-s3-hosting-deploy",
                                  sources=[s3deploy.Source.asset("frontend/public")],
                                  destination_bucket=bucket,
                                  distribution=cf_distrib,
                                  retain_on_delete=False)


class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *, conf: Conf, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api_layer = lambda_.LayerVersion(self, f"{conf.app_prefix}-api-layer",
                                         code=lambda_.Code.from_asset(
                                             "backend/api",
                                             bundling=BundlingOptions(
                                                 image=lambda_.Runtime.PYTHON_3_9.bundling_image,
                                                 command=["bash", "-c",
                                                          "pip install -r requirements.txt -t /asset-output/python"])
                                         ))

        api_lambda = lambda_.Function(self, f"{conf.app_prefix}-api-lambda",
                                      function_name=f"{conf.app_prefix}-api-lambda",
                                      code=lambda_.Code.from_asset("backend/api"),
                                      runtime=lambda_.Runtime.PYTHON_3_9,
                                      handler="lambda_function.lambda_handler",
                                      layers=[api_layer],
                                      environment={"MEET_REDIRECT_URL": conf.meet_redirect_url}
                                      )
        api_gw = apigateway.RestApi(self, f"{conf.app_prefix}-api-gw",
                                    endpoint_types=[apigateway.EndpointType.REGIONAL])
        api_gw.root.add_proxy(
            default_integration=apigateway.LambdaIntegration(api_lambda),
            any_method=True
        )
        self._api_gw = api_gw

    @property
    def api_gw(self) -> apigateway.RestApi:
        return self._api_gw


class DNSStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *, conf: Conf, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._dns_zone = route53.PublicHostedZone(self, f"{conf.app_prefix}-dns-zone",
                                                  zone_name=conf.route53_domain)

    @property
    def zone(self) -> route53.HostedZone:
        return self._dns_zone
