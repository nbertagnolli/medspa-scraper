import random
import time
import string


def chunk(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def generate_x_request_id():
    # Generate the first part (8 lowercase letters)
    first_part = "".join(random.choices(string.ascii_lowercase, k=8))
    # Generate the second part (current timestamp in milliseconds)
    second_part = str(int(time.time() * 1000))
    return f"{first_part}-{second_part}"


def generate_random_email():
    first_names = [
        "James",
        "Mary",
        "John",
        "Patricia",
        "Robert",
        "Jennifer",
        "Michael",
        "Linda",
        "William",
        "Elizabeth",
        "David",
        "Barbara",
        "Richard",
        "Susan",
        "Joseph",
        "Jessica",
        "Thomas",
        "Sarah",
        "Charles",
        "Karen",
    ]

    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Hernandez",
        "Lopez",
        "Gonzalez",
        "Wilson",
        "Anderson",
        "Thomas",
        "Taylor",
        "Moore",
        "Jackson",
        "Martin",
    ]

    first_name = random.choice(first_names)
    middle_initial = random.choices(string.ascii_lowercase, k=1)[0]
    digits = "".join(random.choices("0123456789", k=8))
    last_name = random.choice(last_names)
    email = random.choice(["gmail", "msn", "yahoo"])

    return f"{first_name}{middle_initial}{last_name}{digits}@{email}.com"


def check_provider_exists(rds_data, credentials, provider_id) -> bool:
    response = rds_data.execute_statement(
        resourceArn=credentials["db_cluster_arn"],
        secretArn=credentials["db_secret_arn"],
        database=credentials["db_name"],
        sql=f"select count(*) from providers where provider_id = '{provider_id}'",
    )

    # Extract the result
    return response["records"][0][0]["longValue"] >= 1
