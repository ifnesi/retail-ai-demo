CREATE TABLE products (
    product_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(50) NOT NULL
)