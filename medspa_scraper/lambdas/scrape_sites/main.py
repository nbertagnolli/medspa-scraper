from boulevard_sdk import (
    get_bookable_dates,
    get_patient_type,
    get_providers,
    get_patient_type,
    get_times,
    set_provider,
    auth_boulevard,
    clear_cart,
)
from utils import (
    generate_random_email,
    generate_x_request_id,
    check_provider_exists,
    chunk,
)
from queries import (
    UPDATE_PROVIDERS_QUERY,
    UPDATE_AVAILABLE_DATES,
    AVAILABLE_DATES_VALUE,
)
from datetime import datetime, timezone
import time
import random
import os
import boto3


def lambda_handler(event, context):
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

    headers = {
        "authority": "dashboard.boulevard.io",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://dashboard.boulevard.io",
        "referer": "https://dashboard.boulevard.io/booking/businesses/5f19cd16-cd8b-4ea3-a559-9758d69847dc/widget",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-blvd-bid": "5f19cd16-cd8b-4ea3-a559-9758d69847dc",  # THIS IS THE BUSINESS ID!!!!
        "x-request-id": "ioayicng6-1716396987064",
    }
    # TODO:: Do this for each location_id in the locations table.
    current_time = datetime.now(timezone.utc).isoformat()
    business_id = event["business_id"]
    headers["x-blvd-bid"] = business_id
    headers["x-request-id"] = generate_x_request_id()
    email = generate_random_email()
    location_id = event["location_id"]

    # Auth with the system to get a unique cart token
    cart_token = auth_boulevard(headers, location_id, email)["data"]["createCart"][
        "cartToken"
    ]
    time.sleep(random.randrange(0, 3))
    # Get the item ids which represent what proceedure you want done
    item_id = get_patient_type(headers, cart_token)[0]["availableItems"][0][
        "id"
    ]  # TODO:: MAKE sure this is botox
    time.sleep(random.randrange(0, 3))
    # List out the providers that will perform the service
    # TODO:: MAKE A PROVIDERS TABLE SO WE DON'T SAVE THIS EVERY DAY.  CHECK IF PROVIDER IN TABLE THEN SCRAPE.
    providers = get_providers(headers, cart_token, item_id)["data"]["cart"][
        "availableItem"
    ]["staffVariants"]
    time.sleep(random.randrange(0, 3))

    # Scrape availabilities for each provider
    data = []
    for provider in providers:
        print(provider["id"])
        set_provider(headers, cart_token, provider["id"], item_id)

        # Update Provider Table if not present
        if not check_provider_exists(rds_data, credentials, provider["id"]):
            provider_data = {
                "provider_id": provider["id"],
                "business_id": business_id,
                "location_id": location_id,
                "scraped_at": current_time,
                "display_name": provider["staff"]["displayName"],
                "first_name": provider["staff"]["firstName"],
                "last_name": provider["staff"]["lastName"],
                "credentials": provider["staff"]["staffRole"]["name"],
                "image_url": provider["staff"]["avatar"],
            }
            rds_data.execute_statement(
                resourceArn=credentials["db_cluster_arn"],
                secretArn=credentials["db_secret_arn"],
                database=credentials["db_name"],
                sql=UPDATE_PROVIDERS_QUERY.format(**provider_data),
            )

        time.sleep(random.randrange(0, 3))
        available_dates = get_bookable_dates(headers, cart_token, n_days=93)
        time.sleep(random.randrange(0, 3))
        # Step through all available dates for the provider
        for available_date in available_dates["data"]["cartBookableDates"]:
            # Get the current time in PST as the time this date was scraped
            current_time = datetime.now(timezone.utc).isoformat()
            time.sleep(random.randrange(0, 3))
            availabilities = get_times(
                headers,
                cart_token,
                available_date["date"],
                time_zone=event["time_zone"],
            )
            availabilities = [
                x["startTime"] for x in availabilities["data"]["cartBookableTimes"]
            ]
            # Create a row of data for each time.
            # business, scraped_at, provider_id, location_id, available_date, available_time, State, City, Address, booking_Service
            for availability in availabilities:
                d = {
                    "business_id": business_id,
                    "location_id": location_id,
                    "scraped_at": current_time,
                    "available_date": available_date["date"],
                    "provider_id": provider["id"],
                    "available_time": availability,
                }
                data.append(d)

        clear_cart(headers, cart_token)

    # You can't send more than 65536 characters in a SQL query. So we need to chunk this.
    for subset in chunk(data, 50):
        query = UPDATE_AVAILABLE_DATES.format(
            values=",".join([AVAILABLE_DATES_VALUE.format(**d) for d in subset])
        )

        rds_data.execute_statement(
            resourceArn=credentials["db_cluster_arn"],
            secretArn=credentials["db_secret_arn"],
            database=credentials["db_name"],
            sql=query,
        )
