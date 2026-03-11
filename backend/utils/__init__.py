import os
import json
import hashlib
import configparser

from confluent_kafka.schema_registry import SchemaRegistryClient


# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMAS_DIR = os.path.join(SCRIPT_DIR, "schemas")
CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")

# Kafka Topics
RETAIL_DEMO_USERS = "RETAIL_DEMO_USERS"
RETAIL_DEMO_PRODUCTS = "RETAIL_DEMO_PRODUCTS"
RETAIL_DEMO_STORES = "RETAIL_DEMO_STORES"
RETAIL_DEMO_PARTNERS = "RETAIL_DEMO_PARTNERS"
RETAIL_DEMO_VIEW_PRODUCT = "RETAIL_DEMO_VIEW_PRODUCT"
RETAIL_DEMO_ADD_TO_CART = "RETAIL_DEMO_ADD_TO_CART"
RETAIL_DEMO_ABANDON_CART = "RETAIL_DEMO_ABANDON_CART"
RETAIL_DEMO_STORE_ENTRY = "RETAIL_DEMO_STORE_ENTRY"
RETAIL_DEMO_PARTNER_BROWSE = "RETAIL_DEMO_PARTNER_BROWSE"
# Flink Tables
RETAIL_DEMO_CART_RECOVERY_MESSAGES = "RETAIL_DEMO_CART_RECOVERY_MESSAGES"
RETAIL_DEMO_STORE_VISIT_CONTEXT = "RETAIL_DEMO_STORE_VISIT_CONTEXT"
RETAIL_DEMO_PARTNER_BROWSE_ADS = "RETAIL_DEMO_PARTNER_BROWSE_ADS"


def load_schema(schema_name: str):
    """Load AVRO schema from JSON file."""
    with open(os.path.join(SCHEMAS_DIR, f"{schema_name}.json"), "r") as f:
        return json.dumps(json.load(f))


def hash_password(password: str):
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_config(config_file: str):
    """Load Kafka and Schema Registry configuration."""
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_DIR, config_file))
    kafka_config = dict(config["kafka"])
    sr_config = dict(config["schema-registry"])
    schema_registry_client = SchemaRegistryClient(sr_config)
    return kafka_config, sr_config, schema_registry_client


# Load all AVRO schemas from JSON files
USER_VALUE_SCHEMA = load_schema("RETAIL_DEMO_USERS")
PRODUCT_SCHEMA = load_schema("RETAIL_DEMO_PRODUCTS")
STORE_SCHEMA = load_schema("RETAIL_DEMO_STORES")
PARTNER_SCHEMA = load_schema("RETAIL_DEMO_PARTNERS")
VIEW_PRODUCT_SCHEMA = load_schema("RETAIL_DEMO_VIEW_PRODUCT")
ADD_TO_CART_SCHEMA = load_schema("RETAIL_DEMO_ADD_TO_CART")
ABANDON_CART_SCHEMA = load_schema("RETAIL_DEMO_ABANDON_CART")
STORE_ENTRY_SCHEMA = load_schema("RETAIL_DEMO_STORE_ENTRY")
PARTNER_BROWSE_SCHEMA = load_schema("RETAIL_DEMO_PARTNER_BROWSE")
