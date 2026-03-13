#!/usr/bin/env python3
"""
Flask backend for the Retail AI Demo.
Handles user authentication, Kafka event production, and real-time event consumption.
"""
import json
import time
import uuid
import threading

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
from confluent_kafka import Producer, Consumer, KafkaError
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import (
    SerializationContext,
    MessageField,
    StringDeserializer,
)

from utils import *

app = Flask(__name__)
app.secret_key = "a35e8e5da02bf8a6623a86dcbaad08614052637b4ac8b14dc9e8f1c9b2"  # Change this to a secure random key in production
CORS(
    app,
    supports_credentials=True,
)

# Global variables
HOST = "localhost"
PORT = 8000
MAX_EVENTS_STORED = 100
MAX_AI_PREDICTIONS = 100

producer = None
event_consumers = dict()
latest_events = {
    RETAIL_DEMO_USERS: list(),
    RETAIL_DEMO_VIEW_PRODUCT: list(),
    RETAIL_DEMO_ADD_TO_CART: list(),
    RETAIL_DEMO_ABANDON_CART: list(),
    RETAIL_DEMO_STORE_ENTRY: list(),
    RETAIL_DEMO_PARTNER_BROWSE: list(),
}
# Store AI-generated messages from Flink tables
ai_predictions = {
    "cart_recovery": list(),  # From RETAIL_DEMO_CART_RECOVERY_MESSAGES table
    "store_context": list(),  # From RETAIL_DEMO_STORE_VISIT_CONTEXT table
    "partner_ads": list(),  # From RETAIL_DEMO_PARTNER_BROWSE_ADS table
}
# Store reference data from compacted topics
products = dict()  # Key: product_id, Value: product dict
stores = dict()  # Key: store_id, Value: store dict
partners = dict()  # Key: partner_id, Value: partner dict
users_cache = dict()  # Key: username, Value: user dict


def init_producer():
    """Initialize Kafka producer."""
    global producer
    producer_config = kafka_config.copy()
    producer = Producer(producer_config)


def get_user_from_kafka(username):
    """Fetch user from Kafka topic."""
    consumer_config = kafka_config.copy()
    consumer_config.update(
        {
            "group.id": f"user_lookup_{uuid.uuid4()}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "isolation.level": "read_uncommitted",
        }
    )

    consumer = Consumer(consumer_config)
    consumer.subscribe([RETAIL_DEMO_USERS])

    user_deserializer = AvroDeserializer(schema_registry_client)
    string_deserializer = StringDeserializer("utf-8")

    user_data = None
    timeout = time.time() + 10  # 10 second timeout

    try:
        while time.time() < timeout:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                continue

            key = string_deserializer(msg.key())
            if key == username:
                value = user_deserializer(
                    msg.value(),
                    SerializationContext(RETAIL_DEMO_USERS, MessageField.VALUE),
                )
                user_data = value
                break
    finally:
        consumer.close()

    return user_data


def produce_event(topic, key, value_dict, schema_str):
    """Produce an event to Kafka."""
    try:
        avro_serializer = AvroSerializer(schema_registry_client, schema_str)
        serialized_value = avro_serializer(
            value_dict, SerializationContext(topic, MessageField.VALUE)
        )

        producer.produce(topic=topic, key=key.encode("utf-8"), value=serialized_value)
        producer.flush()
        return True
    except Exception as e:
        print(f"Error producing event to {topic}: {e}")
        return False


def consume_users_thread():
    """Background thread to consume users from RETAIL_DEMO_USERS topic (compacted)."""
    consumer_config = kafka_config.copy()
    consumer_config.update(
        {
            "group.id": f"users_consumer_{uuid.uuid4()}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
            "isolation.level": "read_uncommitted",
        }
    )

    consumer = Consumer(consumer_config)
    consumer.subscribe([RETAIL_DEMO_USERS])

    deserializer = AvroDeserializer(schema_registry_client)

    print("Started users consumer (reading from RETAIL_DEMO_USERS)")

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error on RETAIL_DEMO_USERS: {msg.error()}")
                    continue

            value = deserializer(
                msg.value(),
                SerializationContext(
                    RETAIL_DEMO_USERS,
                    MessageField.VALUE,
                ),
            )

            # Store user in memory by username
            if value["username"] not in users_cache:
                users_cache[value["username"]] = value
                print(
                    f"User loaded: {value['username']} - {value['first_name']} {value['last_name']}"
                )

                # Add to latest events for Kafka Events tab
                latest_events[RETAIL_DEMO_USERS].insert(
                    0, {"timestamp": datetime.now().isoformat(), "data": value}
                )
                # Keep only last MAX_EVENTS_STORED events
                latest_events[RETAIL_DEMO_USERS] = latest_events[RETAIL_DEMO_USERS][
                    :MAX_EVENTS_STORED
                ]

        except Exception as e:
            print(f"Error consuming from RETAIL_DEMO_USERS: {e}")
            time.sleep(1)


def consume_products_thread():
    """Background thread to consume products from RETAIL_DEMO_PRODUCTS topic (compacted)."""
    consumer_config = kafka_config.copy()
    consumer_config.update(
        {
            "group.id": f"products_consumer_{uuid.uuid4()}",
            "auto.offset.reset": "earliest",  # Read from beginning for compacted topic
            "enable.auto.commit": True,
            "isolation.level": "read_uncommitted",
        }
    )

    consumer = Consumer(consumer_config)
    consumer.subscribe([RETAIL_DEMO_PRODUCTS])

    deserializer = AvroDeserializer(schema_registry_client)

    print("Started products consumer (reading from RETAIL_DEMO_PRODUCTS)")

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error on RETAIL_DEMO_PRODUCTS: {msg.error()}")
                    continue

            value = deserializer(
                msg.value(),
                SerializationContext(
                    RETAIL_DEMO_PRODUCTS,
                    MessageField.VALUE,
                ),
            )

            # Store product in memory by product_id
            products[value["product_id"]] = value
            print(f"Product loaded: {value['product_id']} - {value['name']}")

        except Exception as e:
            print(f"Error consuming from RETAIL_DEMO_PRODUCTS: {e}")
            time.sleep(1)


def consume_stores_thread():
    """Background thread to consume stores from RETAIL_DEMO_STORES topic (compacted)."""
    consumer_config = kafka_config.copy()
    consumer_config.update(
        {
            "group.id": f"stores_consumer_{uuid.uuid4()}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
            "isolation.level": "read_uncommitted",
        }
    )

    consumer = Consumer(consumer_config)
    consumer.subscribe([RETAIL_DEMO_STORES])

    deserializer = AvroDeserializer(schema_registry_client)

    print("Started stores consumer (reading from RETAIL_DEMO_STORES)")

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error on RETAIL_DEMO_STORES: {msg.error()}")
                    continue

            value = deserializer(
                msg.value(),
                SerializationContext(
                    RETAIL_DEMO_STORES,
                    MessageField.VALUE,
                ),
            )

            # Store in memory by store_id
            stores[value["store_id"]] = value
            print(f"Store loaded: {value['store_id']} - {value['name']}")

        except Exception as e:
            print(f"Error consuming from RETAIL_DEMO_STORES: {e}")
            time.sleep(1)


def consume_partners_thread():
    """Background thread to consume partners from RETAIL_DEMO_PARTNERS topic (compacted)."""
    consumer_config = kafka_config.copy()
    consumer_config.update(
        {
            "group.id": f"partners_consumer_{uuid.uuid4()}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
            "isolation.level": "read_uncommitted",
        }
    )

    consumer = Consumer(consumer_config)
    consumer.subscribe([RETAIL_DEMO_PARTNERS])

    deserializer = AvroDeserializer(schema_registry_client)

    print("Started partners consumer (reading from RETAIL_DEMO_PARTNERS)")

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error on RETAIL_DEMO_PARTNERS: {msg.error()}")
                    continue

            value = deserializer(
                msg.value(),
                SerializationContext(
                    RETAIL_DEMO_PARTNERS,
                    MessageField.VALUE,
                ),
            )

            # Store in memory by partner_id
            partners[value["partner_id"]] = value
            print(f"Partner loaded: {value['partner_id']} - {value['name']}")

        except Exception as e:
            print(f"Error consuming from RETAIL_DEMO_PARTNERS: {e}")
            time.sleep(1)


def consume_events_thread(topic):
    """Background thread to consume events from a topic."""
    consumer_config = kafka_config.copy()
    consumer_config.update(
        {
            "group.id": f"{topic}_consumer_{uuid.uuid4()}",
            "auto.offset.reset": "latest",
            "enable.auto.commit": True,
            "isolation.level": "read_uncommitted",
        }
    )

    consumer = Consumer(consumer_config)
    consumer.subscribe([topic])

    deserializer = AvroDeserializer(schema_registry_client)

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error on {topic}: {msg.error()}")
                    continue

            value = deserializer(
                msg.value(), SerializationContext(topic, MessageField.VALUE)
            )

            # Add to latest events
            if topic in latest_events:
                latest_events[topic].insert(
                    0, {"timestamp": datetime.now().isoformat(), "data": value}
                )
                # Keep only last MAX_EVENTS_STORED events
                latest_events[topic] = latest_events[topic][:MAX_EVENTS_STORED]

        except Exception as e:
            print(f"Error consuming from {topic}: {e}")
            time.sleep(1)


def consume_ai_predictions_thread(table_name, storage_key):
    """Background thread to consume AI predictions from Flink-generated tables."""
    consumer_config = kafka_config.copy()
    consumer_config.update(
        {
            "group.id": f"{table_name}_ai_consumer_{uuid.uuid4()}",
            "auto.offset.reset": "latest",
            "enable.auto.commit": True,
            "isolation.level": "read_uncommitted",
        }
    )

    consumer = Consumer(consumer_config)
    consumer.subscribe([table_name])

    print(f"Started AI predictions consumer for {table_name} (stored in {storage_key})")

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"AI Consumer error on {table_name}: {msg.error()}")
                    continue

            # Try AVRO first, fallback to JSON
            try:
                deserializer = AvroDeserializer(schema_registry_client)
                value = deserializer(
                    msg.value(), SerializationContext(table_name, MessageField.VALUE)
                )
            except Exception:
                # If AVRO fails, try JSON
                try:
                    value = json.loads(msg.value().decode("utf-8"))
                except Exception:
                    # Last resort: string
                    value = {"message": msg.value().decode("utf-8")}

            # Add to AI predictions storage
            if storage_key in ai_predictions:
                ai_predictions[storage_key].insert(
                    0, {"timestamp": datetime.now().isoformat(), "data": value}
                )
                # Keep only last MAX_AI_PREDICTIONS
                ai_predictions[storage_key] = ai_predictions[storage_key][
                    :MAX_AI_PREDICTIONS
                ]

                print(f"AI prediction received from {table_name}: {value}")

        except Exception as e:
            print(f"Error consuming AI predictions from {table_name}: {e}")
            time.sleep(1)


# API Routes
@app.route("/api/login", methods=["POST"])
def login():
    """Handle user login."""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Fetch user from Kafka
    user = get_user_from_kafka(username)

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Verify password
    password_hash = hash_password(password)
    if user["password_hash"] != password_hash:
        return jsonify({"error": "Invalid credentials"}), 401

    # Create session
    session["username"] = username
    session["first_name"] = user["first_name"]
    session["last_name"] = user["last_name"]
    session["customer_tier"] = user.get("customer_tier", "BRONZE")

    return jsonify(
        {
            "username": username,
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "customer_tier": user.get("customer_tier", "BRONZE"),
        }
    )


@app.route("/api/logout", methods=["POST"])
def logout():
    """Handle user logout."""
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@app.route("/api/session", methods=["GET"])
def get_session():
    """Get current session."""
    if "username" in session:
        return jsonify(
            {
                "username": session["username"],
                "first_name": session.get("first_name"),
                "last_name": session.get("last_name"),
                "customer_tier": session.get("customer_tier", "BRONZE"),
            }
        )
    return jsonify({"error": "Not authenticated"}), 401


@app.route("/api/products", methods=["GET"])
def get_products():
    """Get all products from the RETAIL_DEMO_PRODUCTS topic."""
    # Convert products dict to list sorted by product_id
    products_list = sorted(products.values(), key=lambda p: p["product_id"])
    return jsonify(products_list)


@app.route("/api/stores", methods=["GET"])
def get_stores():
    """Get all stores from the RETAIL_DEMO_STORES topic."""
    # Convert stores dict to list sorted by store_id
    stores_list = sorted(stores.values(), key=lambda s: s["store_id"])
    return jsonify(stores_list)


@app.route("/api/partners", methods=["GET"])
def get_partners():
    """Get all partners from the RETAIL_DEMO_PARTNERS topic."""
    # Convert partners dict to list sorted by partner_id
    partners_list = sorted(partners.values(), key=lambda p: p["partner_id"])
    return jsonify(partners_list)


@app.route("/api/users", methods=["GET"])
def get_users():
    """Get all users from the RETAIL_DEMO_USERS topic (for display on login page)."""
    # Convert users dict to list sorted by username, excluding password hash
    users_list = [
        {
            "username": user["username"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
        }
        for user in sorted(users_cache.values(), key=lambda u: u["username"])
    ]
    return jsonify(users_list)


@app.route("/api/events/view-product", methods=["POST"])
def view_product():
    """Record product view event."""
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    event = {
        "event_id": str(uuid.uuid4()),
        "username": session["username"],
        "product_id": data["product_id"],
        "product_name": data["product_name"],
        "category": data["category"],
        "price": float(data["price"]),
        "description": data.get("description", ""),
        "timestamp": int(datetime.now().timestamp() * 1000),
    }

    success = produce_event(
        RETAIL_DEMO_VIEW_PRODUCT,
        session["username"],
        event,
        VIEW_PRODUCT_SCHEMA,
    )
    return jsonify({"success": success, "event": event})


@app.route("/api/events/add-to-cart", methods=["POST"])
def add_to_cart():
    """Record add to cart event."""
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    event = {
        "event_id": str(uuid.uuid4()),
        "username": session["username"],
        "product_id": data["product_id"],
        "product_name": data["product_name"],
        "quantity": int(data.get("quantity", 1)),
        "price": float(data["price"]),
        "timestamp": int(datetime.now().timestamp() * 1000),
    }

    success = produce_event(
        RETAIL_DEMO_ADD_TO_CART,
        session["username"],
        event,
        ADD_TO_CART_SCHEMA,
    )
    return jsonify({"success": success, "event": event})


@app.route("/api/events/abandon-cart", methods=["POST"])
def abandon_cart():
    """Record cart abandonment event."""
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    event = {
        "event_id": str(uuid.uuid4()),
        "username": session["username"],
        "customer_tier": session.get("customer_tier", "BRONZE"),
        "cart_value": float(data["cart_value"]),
        "items_count": int(data["items_count"]),
        "timestamp": int(datetime.now().timestamp() * 1000),
    }

    success = produce_event(
        RETAIL_DEMO_ABANDON_CART,
        session["username"],
        event,
        ABANDON_CART_SCHEMA,
    )
    return jsonify({"success": success, "event": event})


@app.route("/api/events/store-entry", methods=["POST"])
def store_entry():
    """Record store entry event with last product viewed context."""
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json

    # Get last viewed product for this user from in-memory cache
    last_product_viewed = None
    last_product_category = None
    last_product_price = None

    if latest_events.get(RETAIL_DEMO_VIEW_PRODUCT):
        for view_event in latest_events[RETAIL_DEMO_VIEW_PRODUCT]:
            if view_event["data"]["username"] == session["username"]:
                last_product_viewed = view_event["data"]["product_name"]
                last_product_category = view_event["data"]["category"]
                last_product_price = view_event["data"]["price"]
                break

    # Get store promotions from the stores cache and concatenate with semicolons
    store_promotions = ""
    if data["store_id"] in stores:
        promotions_list = stores[data["store_id"]].get("promotions", list())
        store_promotions = ";".join(promotions_list)

    event = {
        "event_id": str(uuid.uuid4()),
        "username": session["username"],
        "customer_tier": session.get("customer_tier", "BRONZE"),
        "store_id": data["store_id"],
        "store_name": data["store_name"],
        "location": data["location"],
        "last_product_viewed": last_product_viewed,
        "last_product_category": last_product_category,
        "last_product_price": last_product_price,
        "promotions": store_promotions,
        "timestamp": int(datetime.now().timestamp() * 1000),
    }

    success = produce_event(
        RETAIL_DEMO_STORE_ENTRY,
        session["username"],
        event,
        STORE_ENTRY_SCHEMA,
    )
    return jsonify({"success": success, "event": event})


@app.route("/api/events/partner-browse", methods=["POST"])
def partner_browse():
    """Record partner browse event with last product viewed context."""
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json

    # Get last viewed product for this user from in-memory cache
    last_product_viewed = None
    last_product_category = None
    last_product_price = None

    if latest_events.get(RETAIL_DEMO_VIEW_PRODUCT):
        for view_event in latest_events[RETAIL_DEMO_VIEW_PRODUCT]:
            if view_event["data"]["username"] == session["username"]:
                last_product_viewed = view_event["data"]["product_name"]
                last_product_category = view_event["data"]["category"]
                last_product_price = view_event["data"]["price"]
                break

    # Get partner promotions from the partners cache and concatenate with semicolons
    partner_promotions = ""
    for partner in partners.values():
        if partner["name"] == data["partner_name"]:
            categories_dict = partner.get("categories", dict())
            if data["category"] in categories_dict:
                promotions_list = categories_dict[data["category"]]
                partner_promotions = ";".join(promotions_list)
            break

    event = {
        "event_id": str(uuid.uuid4()),
        "username": session["username"],
        "customer_tier": session.get("customer_tier", "BRONZE"),
        "partner_name": data["partner_name"],
        "category": data["category"],
        "last_product_viewed": last_product_viewed,
        "last_product_category": last_product_category,
        "last_product_price": last_product_price,
        "promotions": partner_promotions,
        "timestamp": int(datetime.now().timestamp() * 1000),
    }

    success = produce_event(
        RETAIL_DEMO_PARTNER_BROWSE,
        session["username"],
        event,
        PARTNER_BROWSE_SCHEMA,
    )
    return jsonify({"success": success, "event": event})


@app.route("/api/events/latest", methods=["GET"])
def get_latest_events():
    """Get latest events from all topics."""
    return jsonify(latest_events)


@app.route("/api/events/latest/<topic>", methods=["GET"])
def get_latest_events_by_topic(topic):
    """Get latest events from a specific topic."""
    if topic in latest_events:
        return jsonify(latest_events[topic])
    return jsonify({"error": "Invalid topic"}), 404


@app.route("/api/ai/predictions", methods=["GET"])
def get_ai_predictions():
    """Get all AI predictions from Flink-generated tables."""
    return jsonify(ai_predictions)


@app.route("/api/ai/predictions/<prediction_type>", methods=["GET"])
def get_ai_predictions_by_type(prediction_type):
    """Get AI predictions by type (cart_recovery, recommendations, store_context)."""
    if prediction_type in ai_predictions:
        return jsonify(ai_predictions[prediction_type])
    return jsonify({"error": "Invalid prediction type"}), 404


@app.route("/api/ai/latest-recovery/<username>", methods=["GET"])
def get_latest_recovery_for_user(username):
    """Get latest cart recovery message for a specific user."""
    for prediction in ai_predictions.get("cart_recovery", list()):
        data = prediction.get("data", dict())
        if data.get("username") == username:
            return jsonify(prediction)
    return jsonify({"error": "No recovery message found"}), 404


if __name__ == "__main__":
    print("Loading configuration...")
    kafka_config, sr_config, schema_registry_client = load_config(
        "cflt-cloud-credentials.ini"
    )

    print("Initializing producer...")
    init_producer()

    print("Starting reference data consumers...")
    users_thread = threading.Thread(
        target=consume_users_thread,
        daemon=True,
    )
    users_thread.start()

    products_thread = threading.Thread(
        target=consume_products_thread,
        daemon=True,
    )
    products_thread.start()

    stores_thread = threading.Thread(
        target=consume_stores_thread,
        daemon=True,
    )
    stores_thread.start()

    partners_thread = threading.Thread(
        target=consume_partners_thread,
        daemon=True,
    )
    partners_thread.start()

    print("Starting event consumers...")
    for topic in [
        RETAIL_DEMO_VIEW_PRODUCT,
        RETAIL_DEMO_ADD_TO_CART,
        RETAIL_DEMO_ABANDON_CART,
        RETAIL_DEMO_STORE_ENTRY,
        RETAIL_DEMO_PARTNER_BROWSE,
    ]:
        thread = threading.Thread(
            target=consume_events_thread,
            args=(topic,),
            daemon=True,
        )
        thread.start()
        print(f"  - {topic} consumer started")

    print("\nStarting AI prediction consumers...")
    print("(These will only receive data if Flink SQL tables are created)")

    # AI prediction consumers - these tables are created by Flink SQL
    # Only include tables that have corresponding CREATE TABLE statements in GENAI_INTEGRATION.md
    ai_consumers = [
        (
            RETAIL_DEMO_CART_RECOVERY_MESSAGES,
            "cart_recovery",
        ),
        (
            RETAIL_DEMO_STORE_VISIT_CONTEXT,
            "store_context",
        ),
        (
            RETAIL_DEMO_PARTNER_BROWSE_ADS,
            "partner_ads",
        ),
    ]

    for table_name, storage_key in ai_consumers:
        thread = threading.Thread(
            target=consume_ai_predictions_thread,
            args=(table_name, storage_key),
            daemon=True,
        )
        thread.start()
        print(f"  - {table_name} -> {storage_key}")

    print(f"\n🚀 Backend server starting on http://{HOST}:{PORT}\n")
    print(
        "📊 Event topics: RETAIL_DEMO_VIEW_PRODUCT, RETAIL_DEMO_ADD_TO_CART, RETAIL_DEMO_ABANDON_CART, RETAIL_DEMO_STORE_ENTRY, RETAIL_DEMO_PARTNER_BROWSE"
    )
    print("🤖 AI predictions: cart_recovery, store_context, partner_ads")
    print("\nWaiting for events and AI predictions...")
    print("(Create Flink SQL tables to see AI predictions)")
    print("See GENAI_INTEGRATION.md to enable AI for Acts 2, 3 & 4\n")

    app.run(
        debug=True,
        host=HOST,
        port=PORT,
        use_reloader=False,
    )
