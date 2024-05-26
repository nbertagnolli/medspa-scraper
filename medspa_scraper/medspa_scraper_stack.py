"""
- Deploy the CDK to Jeffrey's AWS account
- Create the Aurora table
- Test the lambda that it can read from the database
- Update permissions until the lambda can read
- Use the lambda to write to the aurora database.
- Add secrets to AWS secrets manager for the db
- Read these secrets in the lambda
- Create the three tables
- 

"""

from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
)
from .ingestion_state_machine import IngestionStateMachine


class MedspaScraperStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "AuroraVPC", max_azs=3)  # Default is all AZs in the region

        # Create a security group for the Aurora cluster
        aurora_security_group = ec2.SecurityGroup(
            self,
            "AuroraSecurityGroup",
            vpc=vpc,
            description="Allow connections to Aurora PostgreSQL from Lambda",
            allow_all_outbound=True,
        )

        # Create a database secret
        db_secret = secretsmanager.Secret(
            self,
            "MedSpaScrapeDBSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username":"postgres"}',
                generate_string_key="password",
                exclude_characters='@/" ',
            ),
        )

        # Create the Aurora Serverless v2 PostgreSQL cluster
        cluster = rds.ServerlessCluster(
            self,
            "MedSpaScrapePostgresCluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_13_12
            ),
            vpc=vpc,
            scaling=rds.ServerlessScalingOptions(
                auto_pause=Duration.minutes(
                    5
                ),  # Auto pause after 5 minutes of inactivity
                min_capacity=rds.AuroraCapacityUnit.ACU_2,  # Min capacity 2 ACUs
                max_capacity=rds.AuroraCapacityUnit.ACU_8,  # Max capacity 8 ACUs
            ),
            security_groups=[aurora_security_group],
            default_database_name="MedSpaScrapeDB",
            credentials=rds.Credentials.from_secret(db_secret),
        )

        # Create the lambda functions and the state machine
        self.state_machine = IngestionStateMachine(
            self, "IngestionStateMachine", vpc=vpc, cluster=cluster
        )

        # Allow Lambda to connect to Aurora
        aurora_security_group.add_ingress_rule(
            self.state_machine.lambda_security_group,
            ec2.Port.tcp(5432),
            "Allow Lambda security group to connect to Aurora",
        )

        # Grant the Lambda function permissions to access the Aurora cluster
        cluster.grant_data_api_access(self.state_machine.scrape_medspa_fn)
        cluster.grant_data_api_access(self.state_machine.get_locations_function)
        db_secret.grant_read(self.state_machine.scrape_medspa_fn)

        # Create an EventBridge rule to trigger the Lambda function at 3:00 AM PST every day
        rule = events.Rule(
            self,
            "NightlyMedspaScrape",
            schedule=events.Schedule.cron(
                minute="0",
                hour="11",  # 3:00 AM PST is 11:00 AM UTC (depending on daylight saving time)
            ),
        )
        rule.add_target(targets.LambdaFunction(self.state_machine.scrape_medspa_fn))
