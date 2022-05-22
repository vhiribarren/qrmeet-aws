from .config import Conf

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
)

from constructs import Construct


class FrontendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *, conf: Conf, api_gw: apigateway.RestApi,
                 zone: route53.HostedZone, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        certificate = acm.DnsValidatedCertificate(self, f"{conf.app_prefix}-cf-certificate",
                                                  domain_name=zone.zone_name,
                                                  hosted_zone=zone, region="us-east-1")

        bucket = s3.Bucket(self, f"{conf.app_prefix}-frontend-hosting",
                           bucket_name=f"{conf.app_prefix}-frontend-hosting",
                           #website_index_document="index.html",
                           removal_policy=RemovalPolicy.DESTROY)

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
                                                 origin=origins.S3Origin(bucket)))
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
                                      layers=[api_layer]
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
