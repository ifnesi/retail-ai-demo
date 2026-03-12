#!/usr/bin/env python3
"""
Populate with initial data for the retail AI demo.
"""

from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.avro import AvroSerializer

from utils import *
from utils import load_data


# Global variables
kafka_config = dict()
sr_config = dict()
schema_registry_client = None


def populate_users(kafka_config):
    """Populate the retail_web_users topic with initial users."""
    avro_serializer = AvroSerializer(
        schema_registry_client,
        USER_VALUE_SCHEMA,
    )

    producer_config = kafka_config.copy()
    producer = Producer(producer_config)

    for user in load_data.users:
        user_data = {
            "username": user["username"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "date_of_birth": user["date_of_birth"],
            "password_hash": hash_password("secret"),
            "customer_tier": user["customer_tier"],
        }

        try:
            # Serialize value
            serialized_value = avro_serializer(
                user_data,
                SerializationContext(
                    RETAIL_DEMO_USERS,
                    MessageField.VALUE,
                ),
            )

            # Use username as key (string)
            producer.produce(
                topic=RETAIL_DEMO_USERS,
                key=user["username"].encode("utf-8"),
                value=serialized_value,
                callback=lambda err, msg: print(
                    f"User {msg.key().decode('utf-8')} produced"
                    if err is None
                    else f"Error: {err}"
                ),
            )
        except Exception as e:
            print(f"Error producing user {user['username']}: {e}")

    producer.flush()
    print("All users populated successfully")


def populate_products(kafka_config):
    """Populate the RETAIL_DEMO_PRODUCTS topic with initial products."""
    avro_serializer = AvroSerializer(
        schema_registry_client,
        PRODUCT_SCHEMA,
    )

    producer_config = kafka_config.copy()
    producer = Producer(producer_config)

    for product in load_data.products:
        try:
            # Serialize value
            serialized_value = avro_serializer(
                product,
                SerializationContext(
                    RETAIL_DEMO_PRODUCTS,
                    MessageField.VALUE,
                ),
            )

            # Use product_id as key (string)
            producer.produce(
                topic=RETAIL_DEMO_PRODUCTS,
                key=product["product_id"].encode("utf-8"),
                value=serialized_value,
                callback=lambda err, msg: print(
                    f"Product {msg.key().decode('utf-8')} produced"
                    if err is None
                    else f"Error: {err}"
                ),
            )
        except Exception as e:
            print(f"Error producing product {product['product_id']}: {e}")

    producer.flush()
    print("All products populated successfully")


def populate_stores(kafka_config):
    """Populate the RETAIL_DEMO_STORES topic with initial stores."""
    avro_serializer = AvroSerializer(
        schema_registry_client,
        STORE_SCHEMA,
    )

    producer_config = kafka_config.copy()
    producer = Producer(producer_config)

    for store in load_data.stores:
        try:
            # Serialize value
            serialized_value = avro_serializer(
                store,
                SerializationContext(
                    RETAIL_DEMO_STORES,
                    MessageField.VALUE,
                ),
            )

            # Use store_id as key (string)
            producer.produce(
                topic=RETAIL_DEMO_STORES,
                key=store["store_id"].encode("utf-8"),
                value=serialized_value,
                callback=lambda err, msg: print(
                    f"Store {msg.key().decode('utf-8')} produced"
                    if err is None
                    else f"Error: {err}"
                ),
            )
        except Exception as e:
            print(f"Error producing store {store['store_id']}: {e}")

    producer.flush()
    print("All stores populated successfully")


def populate_partners(kafka_config):
    """Populate the RETAIL_DEMO_PARTNERS topic with initial partners."""
    avro_serializer = AvroSerializer(
        schema_registry_client,
        PARTNER_SCHEMA,
    )

    producer_config = kafka_config.copy()
    producer = Producer(producer_config)

    for partner in load_data.partners:
        try:
            # Serialize value
            serialized_value = avro_serializer(
                partner,
                SerializationContext(
                    RETAIL_DEMO_PARTNERS,
                    MessageField.VALUE,
                ),
            )

            # Use partner_id as key (string)
            producer.produce(
                topic=RETAIL_DEMO_PARTNERS,
                key=partner["partner_id"].encode("utf-8"),
                value=serialized_value,
                callback=lambda err, msg: print(
                    f"Partner {msg.key().decode('utf-8')} produced"
                    if err is None
                    else f"Error: {err}"
                ),
            )
        except Exception as e:
            print(f"Error producing partner {partner['partner_id']}: {e}")

    producer.flush()
    print("All partners populated successfully")


if __name__ == "__main__":
    print("Loading configuration...")
    kafka_config, sr_config, schema_registry_client = load_config(
        "cflt-cloud-credentials.ini"
    )

    print("\nPopulating users...")
    populate_users(kafka_config)

    print("\nPopulating products...")
    populate_products(kafka_config)

    print("\nPopulating stores...")
    populate_stores(kafka_config)

    print("\nPopulating partners...")
    populate_partners(kafka_config)

    print("\n✅ Initialization complete!")
