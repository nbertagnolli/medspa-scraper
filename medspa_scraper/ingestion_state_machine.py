from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_stepfunctions_tasks as tasks,
    aws_stepfunctions as sfn,
    aws_s3 as s3,
    aws_logs as logs,
    aws_ec2 as ec2,
    aws_rds as rds,
)
from aws_cdk import Duration


class IngestionStateMachine(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        cluster=rds.IServerlessCluster,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        # Create a security group for the Lambda function to interact with aurora
        self.lambda_security_group = ec2.SecurityGroup(
            self,
            "LambdaSecurityGroup",
            vpc=vpc,
            description="Security group for Lambda function",
            allow_all_outbound=True,
        )

        # Create the layers we'll use in the lambda functions
        self.requests_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "requests",
            "arn:aws:lambda:us-west-2:770693421928:layer:Klayers-p311-requests:7",
        )
        self.boto_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "boto3",
            "arn:aws:lambda:us-west-2:770693421928:layer:Klayers-p311-boto3:10",
        )

        # Create the location search lambda
        self.get_locations_function = _lambda.Function(
            self,
            "GetLocationsFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="main.lambda_handler",
            code=_lambda.Code.from_asset(
                "medspa_scraper/lambdas/get_locations_to_scrape"
            ),
            vpc=vpc,
            security_groups=[self.lambda_security_group],
            timeout=Duration.seconds(60),
            layers=[self.requests_layer, self.boto_layer],
            environment={
                "DB_CLUSTER_ARN": cluster.cluster_arn,
                "DB_SECRET_ARN": cluster.secret.secret_arn,
                "DB_HOST": cluster.cluster_endpoint.hostname,
                "DB_NAME": "MedSpaScrapeDB",
                "DB_USER": "postgres",
                "DB_PASSWORD": "MedSpaScrapeDBSecret",
                "DB_PORT": "5432",
            },
            log_retention=logs.RetentionDays.TWO_WEEKS,
        )

        # Create the Lambda function
        self.scrape_medspa_fn = _lambda.Function(
            self,
            "ScrapeMedSpasFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="main.lambda_handler",
            code=_lambda.Code.from_asset("medspa_scraper/lambdas/scrape_sites"),
            vpc=vpc,
            security_groups=[self.lambda_security_group],
            timeout=Duration.seconds(900),
            layers=[self.requests_layer, self.boto_layer],
            environment={
                "DB_CLUSTER_ARN": cluster.cluster_arn,
                "DB_SECRET_ARN": cluster.secret.secret_arn,
                "DB_HOST": cluster.cluster_endpoint.hostname,
                "DB_NAME": "MedSpaScrapeDB",
                "DB_USER": "postgres",
                "DB_PASSWORD": "MedSpaScrapeDBSecret",
                "DB_PORT": "5432",
            },
            log_retention=logs.RetentionDays.TWO_WEEKS,
        )

        # Create the state machine
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_stepfunctions/README.html
        chunk_locations = tasks.LambdaInvoke(
            self,
            "ChunkLocations",
            lambda_function=self.get_locations_function,
            output_path="$.Payload",
        )
        scrape_medspas = tasks.LambdaInvoke(
            self,
            "ScrapeMedSpas",
            lambda_function=self.scrape_medspa_fn,
            output_path="$.Payload",
        )
        # Map out state
        # https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-map-state.html
        map_locations = sfn.Map(
            self,
            "MapChunkedLocations",
            max_concurrency=1,
            items_path="$.body",
        )
        map_locations.iterator(
            scrape_medspas,
        )
        sfn_definition = chunk_locations.next(map_locations)

        # Define the state machine
        self.state_machine = sfn.StateMachine(
            self,
            "MedSpaScraperStateMachine",
            definition=sfn_definition,
            timeout=Duration.minutes(15),
        )
