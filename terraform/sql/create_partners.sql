CREATE TABLE partners (
    partner_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    categories JSONB NOT NULL,
    icon VARCHAR(50) NOT NULL
)