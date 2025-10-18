import sqlite3
import time
import statistics
import csv
import random
from datetime import datetime, timedelta

DB_PATH = "restaurant_delivery.db"

# ============================================
# Helper: Run Query and Measure Time
# ============================================
def time_query(conn, query, repeats=3):
    cursor = conn.cursor()
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        cursor.execute(query).fetchall()
        times.append(time.perf_counter() - start)
    return statistics.mean(times)

# ============================================
# Query Performance Test
# ============================================
def evaluate_query_performance(conn):
    print("🔹 Running Query Performance Evaluation...")
    queries = {
        "Customer Orders Lookup": "SELECT * FROM Orders WHERE customer_id = 1;",
        "Restaurant Revenue": """
            SELECT r.name, SUM(o.total_amount)
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

    def drop_indexes():
        cursor = conn.cursor()
        cursor.executescript("""
            DROP INDEX IF EXISTS idx_orders_customer_id;
            DROP INDEX IF EXISTS idx_orders_restaurant_id;
            DROP INDEX IF EXISTS idx_order_items_dish_id;
            DROP INDEX IF EXISTS idx_deliveries_courier_id;
            DROP INDEX IF EXISTS idx_payments_order_id;
        """)
        conn.commit()

    def recreate_indexes():
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON Orders(customer_id);
            CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON Orders(restaurant_id);
            CREATE INDEX IF NOT EXISTS idx_order_items_dish_id ON Order_Items(dish_id);
            CREATE INDEX IF NOT EXISTS idx_deliveries_courier_id ON Deliveries(courier_id);
            CREATE INDEX IF NOT EXISTS idx_payments_order_id ON Payments(order_id);
        """)
        conn.commit()

    results = []

    # Without indexes
    drop_indexes()
    for name, q in queries.items():
        t = time_query(conn, q)
        print(f"❌ {name}: {t:.5f}s (no index)")
        results.append((name, "No Index", t))

    # With indexes
    recreate_indexes()
    for name, q in queries.items():
        t = time_query(conn, q)
        print(f"✅ {name}: {t:.5f}s (with index)")
        results.append((name, "With Index", t))

    return results

# ============================================
# Transaction Test
# ============================================
def evaluate_transactions(conn):
    print("\n🔹 Running Transaction Test...")
    results = []
    cursor = conn.cursor()

    # Successful transaction
    try:
        conn.execute("BEGIN;")
        cursor.execute("INSERT INTO Orders (customer_id, restaurant_id, total_amount, status) VALUES (1, 1, 25.99, 'Pending');")
        cursor.execute("INSERT INTO Payments (order_id, amount, method, status) VALUES (last_insert_rowid(), 25.99, 'Credit Card', 'Completed');")
        conn.commit()
        results.append(("Valid Transaction", "Committed"))
        print("Valid transaction committed successfully.")
    except Exception as e:
        conn.rollback()
        results.append(("Valid Transaction", f"Failed: {e}"))

    # Failed transaction (simulate error)
    try:
        conn.execute("BEGIN;")
        cursor.execute("INSERT INTO Orders (customer_id, restaurant_id, total_amount, status) VALUES (1, 1, -10, 'Pending');")
        cursor.execute("INSERT INTO Payments (order_id, amount, method, status) VALUES (last_insert_rowid(), -10, 'Cash', 'Failed');")
        raise Exception("Simulated payment failure")
    except Exception as e:
        conn.rollback()
        results.append(("Failed Transaction", "Rolled Back"))
        print("Failed transaction rolled back correctly.")

    return results

# ============================================
# Scalability Test
# ============================================
def evaluate_scalability(conn):
    print("\n🔹 Running Scalability Test...")
    cursor = conn.cursor()

    def bulk_insert(num_orders):
        start = time.perf_counter()
        orders = []
        start_date = datetime(2024, 1, 1)
        for _ in range(num_orders):
            cust = random.randint(1, 5)
            rest = random.randint(1, 5)
            total = round(random.uniform(10, 60), 2)
            date = start_date + timedelta(days=random.randint(0, 300))
            orders.append((cust, rest, date.strftime("%Y-%m-%d %H:%M:%S"), total, "Delivered"))
        cursor.executemany("INSERT INTO Orders (customer_id, restaurant_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?);", orders)
        conn.commit()
        return time.perf_counter() - start

    sizes = [1000, 10000, 50000]
    results = []
    for size in sizes:
        t = bulk_insert(size)
        print(f"Inserted {size} orders in {t:.2f}s")
        results.append((f"Insert {size} Orders", "N/A", t))

    return results

# ============================================
# Constraint Testing
# ============================================
def evaluate_constraints(conn):
    print("\nRunning Constraint Validation Tests...")
    cursor = conn.cursor()
    results = []

    tests = [
        ("Negative Price", "INSERT INTO Dishes (restaurant_id, name, price) VALUES (1, 'Bad Dish', -5);"),
        ("Duplicate Email", "INSERT INTO Customers (name, email, phone, address) VALUES ('Dup', 'john@example.com', '555', 'dup');"),
        ("Invalid Foreign Key", "INSERT INTO Orders (customer_id, restaurant_id, total_amount, status) VALUES (9999, 1, 10, 'Pending');")
    ]

    for name, sql in tests:
        try:
            cursor.execute(sql)
            conn.commit()
            results.append((name, "Failed — constraint not enforced"))
            print(f"{name}: constraint not enforced")
        except Exception:
            conn.rollback()
            results.append((name, "Passed — constraint enforced"))
            print(f"{name}: constraint enforced")

    return results

# ============================================
# Main Runner
# ============================================
def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    all_results = []
    all_results.extend(evaluate_query_performance(conn))
    all_results.extend(evaluate_transactions(conn))
    all_results.extend(evaluate_scalability(conn))
    all_results.extend(evaluate_constraints(conn))

    # Write results to CSV
    with open("evaluation_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Test", "Condition", "Time (s) / Result"])
        writer.writerows(all_results)

    print("\nEvaluation complete. Results saved to evaluation_results.csv.")
    conn.close()

if __name__ == "__main__":
    main()
