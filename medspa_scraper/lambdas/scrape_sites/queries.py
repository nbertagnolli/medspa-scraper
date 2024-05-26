# CREATE TABLE locations (
#     business_id VARCHAR(255),
#     location_id VARCHAR(255),
#     state VARCHAR(255),
#     city VARCHAR(255),
#     address VARCHAR(255),
#     time_zone VARCHAR(255),
#     business_name VARCHAR(255),
#     booking_provider VARCHAR(255),
#     PRIMARY KEY (business_id, location_id)
# );

UPDATE_PROVIDERS_QUERY = """
INSERT INTO providers (
    provider_id,
    business_id,
    location_id,
    scraped_at,
    display_name,
    first_name,
    last_name,
    credentials,
    image_url
) VALUES (
    '{provider_id}',
    '{business_id}',
    '{location_id}',
    '{scraped_at}',
    '{display_name}',
    '{first_name}',
    '{last_name}',
    '{credentials}',
    '{image_url}'
);
"""


UPDATE_AVAILABLE_DATES = """
INSERT INTO available_dates (
    business_id,
    location_id,
    scraped_at,
    available_date,
    provider_id,
    available_time
) VALUES {values}
"""

AVAILABLE_DATES_VALUE = """
(    
    '{business_id}',
    '{location_id}',
    '{scraped_at}',
    '{available_date}',
    '{provider_id}',
    '{available_time}'
    )
"""

UPDATE_LOCATIONS_QUERY = """
INSERT INTO locations (
    business_id,
    location_id,
    state,
    city,
    zip_code,
    address,
    time_zone,
    business_name,
    booking_provider
) VALUES {values};
"""

LOCATIONS_VALUE = """
('{business_id}',
    '{location_id}',
    '{state}',
    '{city}',
    '{zip_code}',
    '{address}',
    '{time_zone}',
    '{business_name}',
    '{booking_provider}')"""
