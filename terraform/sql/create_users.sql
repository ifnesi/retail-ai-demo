
CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    date_of_birth VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    customer_tier VARCHAR(50) NOT NULL
)