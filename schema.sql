-- schema.sql (historical_data adaptation)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS restaurants (
    restaurant_id INTEGER PRIMARY KEY,
    cuisine_type TEXT,
    location INTEGER,
    avg_price REAL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    order_datetime TEXT,
    delivery_time TEXT,
    subtotal REAL,
    total_items INTEGER,
    num_distinct_items INTEGER,
    min_item_price REAL,
    max_item_price REAL,
    total_onshift_dashers REAL,
    total_busy_dashers REAL,
    total_outstanding_orders REAL,
    estimated_order_place_duration REAL,
    estimated_store_to_consumer_driving_duration REAL,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);
