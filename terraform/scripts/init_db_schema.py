#!/usr/bin/env python3
"""
Initialize PostgreSQL schema for CDC.
Called by Terraform null_resource to create the users table and publication.
"""

import os
import sys
import time
import json
import hashlib
import psycopg2

import init_db_data


TABLES = ["users", "products", "stores", "partners"]


def hash_password(password: str):
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def populate_users(conn):
    """Populate the users table in Postgres (which will be CDC'd to Kafka)."""
    try:
        cursor = conn.cursor()

        for user in init_db_data.users:
            # Insert user into Postgres
            cursor.execute(
                """
                INSERT INTO users (username, first_name, last_name, date_of_birth, password_hash, customer_tier)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    date_of_birth = EXCLUDED.date_of_birth,
                    password_hash = EXCLUDED.password_hash,
                    customer_tier = EXCLUDED.customer_tier
            """,
                (
                    user["username"],
                    user["first_name"],
                    user["last_name"],
                    user["date_of_birth"],
                    hash_password("secret"),
                    user["customer_tier"],
                ),
            )

            print(f"User {user['username']} inserted into Postgres")

        conn.commit()
        cursor.close()

        print(
            "✅ All users populated successfully in Postgres (will be CDC'd to Kafka)"
        )
    except Exception as e:
        print(f"❌ Error populating users: {e}")
        raise


def populate_products(conn):
    """Populate the products table in Postgres (which will be CDC'd to Kafka)."""
    try:
        cursor = conn.cursor()

        for product in init_db_data.products:
            # Insert product into Postgres
            cursor.execute(
                """
                INSERT INTO products (product_id, name, category, price, description, icon)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    price = EXCLUDED.price,
                    description = EXCLUDED.description,
                    icon = EXCLUDED.icon
            """,
                (
                    product["product_id"],
                    product["name"],
                    product["category"],
                    product["price"],
                    product["description"],
                    product["icon"],
                ),
            )

            print(f"Product {product['product_id']} inserted into Postgres")

        conn.commit()
        cursor.close()

        print(
            "✅ All products populated successfully in Postgres (will be CDC'd to Kafka)"
        )
    except Exception as e:
        print(f"❌ Error populating products: {e}")
        raise


def populate_stores(conn):
    """Populate the stores table in Postgres (which will be CDC'd to Kafka)."""
    try:
        cursor = conn.cursor()

        for store in init_db_data.stores:
            # Convert promotions array to JSON string for JSONB column
            promotions_json = json.dumps(store["promotions"])

            # Insert store into Postgres
            cursor.execute(
                """
                INSERT INTO stores (store_id, name, location, icon, promotions)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (store_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    location = EXCLUDED.location,
                    icon = EXCLUDED.icon,
                    promotions = EXCLUDED.promotions
            """,
                (
                    store["store_id"],
                    store["name"],
                    store["location"],
                    store["icon"],
                    promotions_json,
                ),
            )

            print(f"Store {store['store_id']} inserted into Postgres")

        conn.commit()
        cursor.close()

        print(
            "✅ All stores populated successfully in Postgres (will be CDC'd to Kafka)"
        )
    except Exception as e:
        print(f"❌ Error populating stores: {e}")
        raise


def populate_partners(conn):
    """Populate the partners table in Postgres (which will be CDC'd to Kafka)."""
    try:
        cursor = conn.cursor()

        for partner in init_db_data.partners:
            # Convert categories map to JSON string for JSONB column
            categories_json = json.dumps(partner["categories"])

            # Insert partner into Postgres
            cursor.execute(
                """
                INSERT INTO partners (partner_id, name, categories, icon)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (partner_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    categories = EXCLUDED.categories,
                    icon = EXCLUDED.icon
            """,
                (
                    partner["partner_id"],
                    partner["name"],
                    categories_json,
                    partner["icon"],
                ),
            )

            print(f"Partner {partner['partner_id']} inserted into Postgres")

        conn.commit()
        cursor.close()

        print(
            "✅ All partners populated successfully in Postgres (will be CDC'd to Kafka)"
        )
    except Exception as e:
        print(f"❌ Error populating partners: {e}")
        raise


def create_schema_tables(
    host,
    port,
    database,
    username,
    password,
):
    """Create tables and publication for CDC."""
    # Retry logic for connecting to RDS (it may take time to become available)
    max_retries = 20
    retry_delay = 15  # seconds

    conn = None
    for attempt in range(1, max_retries + 1):
        try:
            print(
                f"Attempt {attempt}/{max_retries}: Connecting to PostgreSQL at {host}:{port}..."
            )
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                connect_timeout=10,
            )
            print("✅ Successfully connected to PostgreSQL!")
            break
        except Exception as e:
            if attempt < max_retries:
                print(
                    f"⏳ Database not ready yet. Waiting {retry_delay} seconds before retry..."
                )
                print(f"   Error: {e}")
                time.sleep(retry_delay)
            else:
                print(f"❌ Failed to connect after {max_retries} attempts")
                print(f"   Final error: {e}")
                return 1

    if not conn:
        print("❌ Failed to establish database connection")
        return 1

    try:

        cursor = conn.cursor()

        print("Dropping existing tables and publication if they exist...")
        for table in TABLES:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        cursor.execute("DROP PUBLICATION IF EXISTS postgres_dbz_publication")

        for table in TABLES:
            print(f"Creating {table} table...")
            with open(
                os.path.join("sql", f"create_{table}.sql"),
                "r",
            ) as f:
                sql = f.read()
                cursor.execute(sql)

        print("Creating publication for CDC...")
        cursor.execute(
            f"CREATE PUBLICATION postgres_dbz_publication FOR TABLE {','.join(TABLES)}"
        )

        conn.commit()
        cursor.close()

        print(
            f"✅ Successfully created all tables ({','.join(TABLES)}) and CDC publication"
        )

    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return 1

    try:

        print("\n" + "=" * 60)
        print("POPULATING USERS IN POSTGRES (CDC to Kafka)")
        print("=" * 60)
        populate_users(conn)

        print("\n" + "=" * 60)
        print("POPULATING PRODUCTS IN POSTGRES (CDC to Kafka)")
        print("=" * 60)
        populate_products(conn)

        print("\n" + "=" * 60)
        print("POPULATING STORES IN POSTGRES (CDC to Kafka)")
        print("=" * 60)
        populate_stores(conn)

        print("\n" + "=" * 60)
        print("POPULATING PARTNERS IN POSTGRES (CDC to Kafka)")
        print("=" * 60)
        populate_partners(conn)

        print("\n" + "=" * 60)
        print("✅ INITIALIZATION COMPLETE!")
        print("=" * 60)

        conn.close()
        return 0

    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return 1


if __name__ == "__main__":
    # Read from environment variables (set by Terraform)
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    database = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")

    # Validate all required environment variables are present
    if not all([host, port, database, username, password]):
        print("❌ Missing required environment variables:")
        print("   Required: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        sys.exit(1)

    sys.exit(
        create_schema_tables(
            host,
            port,
            database,
            username,
            password,
        )
    )
