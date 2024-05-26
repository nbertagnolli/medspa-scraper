import os
import boto3


def lambda_handler(event, context):
    """
    Get the business_ids/location_ids that we want to scrape from the database.
    this lambda acts before the actual scraping lambda to get all of the data necessary.
    We have this in a set of step functions because to be polite we wait a long time
    between requests. This means that lambda can take a while to run.
    """
    # Database connection parameters
    credentials = {
        "db_name": os.environ["DB_NAME"],
        "db_secret_arn": os.environ["DB_SECRET_ARN"],
        "db_cluster_arn": os.environ["DB_CLUSTER_ARN"],
        "db_port": os.environ.get("DB_PORT", 5432),
    }
    rds_data = boto3.client("rds-data")

    # Warmup request. Aurora is often spun down. This will spin it up catch the timeout error
    # and then let us continue with our program.
    try:
        rds_data.execute_statement(
            resourceArn=credentials["db_cluster_arn"],
            secretArn=credentials["db_secret_arn"],
            database=credentials["db_name"],
            sql="SELECT 1;",
        )
    except TimeoutError:
        pass

    # Query the database for all locations
    response = rds_data.execute_statement(
        resourceArn=credentials["db_cluster_arn"],
        secretArn=credentials["db_secret_arn"],
        database=credentials["db_name"],
        sql="SELECT business_id, location_id, time_zone FROM locations",
    )
    return {
        "body": [
            {
                "business_id": x[0]["stringValue"],
                "location_id": x[1]["stringValue"],
                "time_zone": x[2]["stringValue"],
            }
            for x in response["records"]
        ]
    }
