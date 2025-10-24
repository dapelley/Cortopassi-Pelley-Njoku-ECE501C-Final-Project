"""
evaluate_db.py (historical_data adaptation)
Quick data checks and table counts.
"""
import sqlite3

DB_PATH = "restaurant_order_recommender.db"

def table_counts():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for t in ["restaurants","orders"]:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            print(t, cur.fetchone()[0])
        except Exception as e:
            print("Error querying", t, e)
    conn.close()

if __name__ == "__main__":
    table_counts()
