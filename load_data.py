"""
load_data.py (historical_data adaptation)
Loads historical delivery data into an SQLite database following schema.sql.
"""
import sqlite3
import pandas as pd
from pathlib import Path

DATA_CSV = Path("historical_data.csv")
DB_PATH = Path("restaurant_order_recommender.db")

df = pd.read_csv(DATA_CSV, low_memory=False, on_bad_lines="skip")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create schema
with open("schema.sql", "r", encoding="utf-8") as f:
    cur.executescript(f.read())

# Insert restaurants (distinct store_id)
restaurants = df[["store_id","store_primary_category","market_id","min_item_price","max_item_price"]].drop_duplicates()
restaurants["avg_price"] = restaurants[["min_item_price","max_item_price"]].mean(axis=1)

for _, row in restaurants.iterrows():
    cur.execute("""
        INSERT OR IGNORE INTO restaurants (restaurant_id, cuisine_type, location, avg_price)
        VALUES (?,?,?,?)
    """, (int(row.store_id),
          str(row.store_primary_category) if pd.notna(row.store_primary_category) else None,
          int(row.market_id) if pd.notna(row.market_id) else None,
          float(row.avg_price) if pd.notna(row.avg_price) else None))

# Insert orders
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO orders (
            restaurant_id, order_datetime, delivery_time, subtotal,
            total_items, num_distinct_items, min_item_price, max_item_price,
            total_onshift_dashers, total_busy_dashers, total_outstanding_orders,
            estimated_order_place_duration, estimated_store_to_consumer_driving_duration
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (int(row.store_id) if pd.notna(row.store_id) else None,
          str(row.created_at) if pd.notna(row.created_at) else None,
          str(row.actual_delivery_time) if pd.notna(row.actual_delivery_time) else None,
          float(row.subtotal) if pd.notna(row.subtotal) else None,
          int(row.total_items) if pd.notna(row.total_items) else None,
          int(row.num_distinct_items) if pd.notna(row.num_distinct_items) else None,
          float(row.min_item_price) if pd.notna(row.min_item_price) else None,
          float(row.max_item_price) if pd.notna(row.max_item_price) else None,
          float(row.total_onshift_dashers) if pd.notna(row.total_onshift_dashers) else None,
          float(row.total_busy_dashers) if pd.notna(row.total_busy_dashers) else None,
          float(row.total_outstanding_orders) if pd.notna(row.total_outstanding_orders) else None,
          float(row.estimated_order_place_duration) if pd.notna(row.estimated_order_place_duration) else None,
          float(row.estimated_store_to_consumer_driving_duration) if pd.notna(row.estimated_store_to_consumer_driving_duration) else None))

conn.commit()
conn.close()
print("Database created and populated as restaurant_order_recommender.db")
