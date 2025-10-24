"""
recommend.py (historical_data adaptation)
Generates basic performance-based restaurant recommendations.
"""
import sqlite3

DB_PATH = "restaurant_order_recommender.db"

def top_fastest(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT restaurant_id,
               AVG((julianday(delivery_time) - julianday(order_datetime)) * 24 * 60) AS avg_minutes,
               COUNT(*) AS n_orders
        FROM orders
        WHERE delivery_time IS NOT NULL
        GROUP BY restaurant_id
        HAVING n_orders > 50
        ORDER BY avg_minutes ASC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def top_value(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT restaurant_id, AVG(subtotal) AS avg_value, COUNT(*) AS n_orders
        FROM orders
        GROUP BY restaurant_id
        HAVING n_orders > 50
        ORDER BY avg_value DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    print("Top value restaurants:", top_value(10))
    print("Fastest restaurants:", top_fastest(10))
