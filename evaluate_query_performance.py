import sqlite3
import time
import statistics
import csv

DB_PATH = "restaurant_delivery.db"

# ============================================
# Define Test Queries
# ============================================
TEST_QUERIES = {
    "Customer Orders Lookup": "SELECT * FROM Orders WHERE customer_id = 1;",
    "Restaurant Revenue": """
        SELECT r.name, SUM(o.total_amount) AS total_revenue
        FROM Orders o
        JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
        GROUP BY r.restaurant_id;
    """,
    "Delivery Join Query": """
        SELECT c.name, d.status, o.total_amount
        FROM Deliveries d
        JOIN Orders o ON o.order_id = d.order_id
        JOIN Customers c ON c.customer_id = o.customer_id
        WHERE d.status = 'Delivered';
    """
}

# ============================================
# Helper: Run a query and time its execution
# ============================================
def time_query(conn, query, repetitions=5):
    times = []
    cursor = conn.cursor()
    for _ in range(repetitions):
        start = time.perf_counter()
        cursor.execute(query).fetchall()
        times.append(time.perf_counter() - start)
    return statistics.mean(times)

# ============================================
# Helper: Disable or enable indexes
# ============================================
def drop_indexes(conn):
    cursor = conn.cursor()
    cursor.executescript("""
        DROP INDEX IF EXISTS idx_orders_customer_id;
        DROP INDEX IF EXISTS idx_orders_restaurant_id;
        DROP INDEX IF EXISTS idx_order_items_dish_id;
        DROP INDEX IF EXISTS idx_deliveries_courier_id;
        DROP INDEX IF EXISTS idx_payments_order_id;
    """)
    conn.commit()

def recreate_indexes(conn):
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON Orders(customer_id);
        CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON Orders(restaurant_id);
        CREATE INDEX IF NOT EXISTS idx_order_items_dish_id ON Order_Items(dish_id);
        CREATE INDEX IF NOT EXISTS idx_deliveries_courier_id ON Deliveries(courier_id);
        CREATE INDEX IF NOT EXISTS idx_payments_order_id ON Payments(order_id);
    """)
    conn.commit()

# ============================================
# Run the Performance Tests
# ============================================
def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    results = []

    print("Running Query Performance Evaluation...")
    print("Testing without indexes...")

    drop_indexes(conn)
    for name, query in TEST_QUERIES.items():
        no_index_time = time_query(conn, query)
        print(f"{name}: {no_index_time:.5f} sec (no index)")
        results.append({"Query": name, "Indexed": False, "Avg Time (s)": no_index_time})

    print("\nRecreating indexes...")
    recreate_indexes(conn)

    print("Testing with indexes...")
    for name, query in TEST_QUERIES.items():
        with_index_time = time_query(conn, query)
        print(f"{name}: {with_index_time:.5f} sec (with index)")
        results.append({"Query": name, "Indexed": True, "Avg Time (s)": with_index_time})

    # Save results to CSV
    with open("query_performance_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Query", "Indexed", "Avg Time (s)"])
        writer.writeheader()
        writer.writerows(results)

    print("\nResults saved to query_performance_results.csv")
    conn.close()

if __name__ == "__main__":
    main()