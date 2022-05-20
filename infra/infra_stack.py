from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    BundlingOptions
)

from constructs import Construct


class FrontendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_prefix = self.node.try_get_context("app_prefix")
        bucket = s3.Bucket(self, "frontend_file_hosting", bucket_name=f"{app_prefix}-frontend-hosting")


class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_prefix = self.node.try_get_context("app_prefix")

        #        api_layer = pylambda.PythonLayerVersion(self, f"{app_prefix}-api-layer",
        #            entry="backend/api-layer"
        #        )

        api_layer = lambda_.LayerVersion(self, f"{app_prefix}-api-layer",
                                         code=lambda_.Code.from_asset(
                                             "backend/api",
                                             bundling=BundlingOptions(
                                                 image=lambda_.Runtime.PYTHON_3_9.bundling_image,
                                                 command=["bash", "-c",
                                                          "pip install -r requirements.txt -t /asset-output/python"])
                                         ))

        api_lambda = lambda_.Function(self, f"{app_prefix}-api-lambda",
                                      code=lambda_.Code.from_asset("backend/api"),
                                      runtime=lambda_.Runtime.PYTHON_3_9,
                                      handler="lambda_function.lambda_handler",
                                      layers=[api_layer]
                                      )
