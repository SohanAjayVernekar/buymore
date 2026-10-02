-- Initial schema, equivalent to python -m scripts.migrate.
BEGIN;
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    order_date TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING','PROCESSING','SHIPPED')),
    total_amount NUMERIC(12,2) NOT NULL CHECK (total_amount >= 0),
    updated_at TIMESTAMPTZ NOT NULL,
    version INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id VARCHAR(24) NOT NULL,
    title TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0)
);
CREATE INDEX IF NOT EXISTS ix_order_items_order_id ON order_items(order_id);
COMMIT;
