import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    conn = sqlite3.connect("restaurant_delivery.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # =====================================================
    # Schema Definition
    # =====================================================
    schema = """
    CREATE TABLE IF NOT EXISTS Customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        address TEXT
    );

    CREATE TABLE IF NOT EXISTS Restaurants (
        restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        phone TEXT
    );

    CREATE TABLE IF NOT EXISTS Dishes (
        dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        price REAL CHECK(price >= 0),
        FOREIGN KEY (restaurant_id)
            REFERENCES Restaurants(restaurant_id)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        restaurant_id INTEGER NOT NULL,
        order_date TEXT DEFAULT (datetime('now')),
        total_amount REAL CHECK(total_amount >= 0),
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (customer_id)
            REFERENCES Customers(customer_id)
            ON DELETE CASCADE,
        FOREIGN KEY (restaurant_id)
            REFERENCES Restaurants(restaurant_id)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Order_Items (
        order_id INTEGER NOT NULL,
        dish_id INTEGER NOT NULL,
        quantity INTEGER CHECK(quantity > 0),
        subtotal REAL CHECK(subtotal >= 0),
        PRIMARY KEY (order_id, dish_id),
        FOREIGN KEY (order_id)
            REFERENCES Orders(order_id)
            ON DELETE CASCADE,
        FOREIGN KEY (dish_id)
            REFERENCES Dishes(dish_id)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Couriers (
        courier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        vehicle_type TEXT CHECK(vehicle_type IN ('Car', 'Bike', 'Scooter', 'Other'))
    );

    CREATE TABLE IF NOT EXISTS Deliveries (
        delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER UNIQUE NOT NULL,
        courier_id INTEGER,
        delivery_time TEXT,
        status TEXT DEFAULT 'Out for Delivery',
        FOREIGN KEY (order_id)
            REFERENCES Orders(order_id)
            ON DELETE CASCADE,
        FOREIGN KEY (courier_id)
            REFERENCES Couriers(courier_id)
            ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER UNIQUE NOT NULL,
        amount REAL CHECK(amount >= 0),
        method TEXT CHECK(method IN ('Credit Card', 'Debit Card', 'Cash', 'Online')),
        status TEXT DEFAULT 'Pending',
        payment_date TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (order_id)
            REFERENCES Orders(order_id)
            ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON Orders(customer_id);
    CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON Orders(restaurant_id);
    CREATE INDEX IF NOT EXISTS idx_order_items_dish_id ON Order_Items(dish_id);
    CREATE INDEX IF NOT EXISTS idx_deliveries_courier_id ON Deliveries(courier_id);
    CREATE INDEX IF NOT EXISTS idx_payments_order_id ON Payments(order_id);
    """
    cursor.executescript(schema)

    # =====================================================
    # Sample Base Data (Customers, Restaurants, Dishes, Couriers)
    # =====================================================
    customers = [
        ("John Doe", "john@example.com", "555-1234", "123 Elm St"),
        ("Jane Smith", "jane@example.com", "555-5678", "456 Oak Ave"),
        ("Mike Johnson", "mike@example.com", "555-4321", "789 Pine Rd"),
        ("Emily Brown", "emily@example.com", "555-8765", "101 Maple Blvd"),
        ("Chris Lee", "chris@example.com", "555-9988", "505 Cedar Ln")
    ]
    cursor.executemany(
        "INSERT INTO Customers (name, email, phone, address) VALUES (?, ?, ?, ?);",
        customers
    )

    restaurants = [
        ("Pasta Palace", "10 Main St", "555-9876"),
        ("Burger Haven", "22 Market St", "555-6543"),
        ("Sushi World", "33 Ocean Ave", "555-2468"),
        ("Taco Town", "44 Fiesta Rd", "555-1357"),
        ("Pizza Planet", "55 Space Way", "555-9753")
    ]
    cursor.executemany(
        "INSERT INTO Restaurants (name, address, phone) VALUES (?, ?, ?);",
        restaurants
    )

    dishes = [
        (1, "Spaghetti", 12.99),
        (1, "Fettuccine Alfredo", 14.99),
        (2, "Cheeseburger", 10.99),
        (2, "Fries", 3.99),
        (3, "Salmon Roll", 13.49),
        (3, "Tuna Sashimi", 15.49),
        (4, "Chicken Taco", 4.99),
        (4, "Beef Burrito", 8.99),
        (5, "Pepperoni Pizza", 11.99),
        (5, "Veggie Pizza", 10.49)
    ]
    cursor.executemany(
        "INSERT INTO Dishes (restaurant_id, name, price) VALUES (?, ?, ?);",
        dishes
    )

    couriers = [
        ("Alex Rider", "Bike"),
        ("Sam Rivers", "Car"),
        ("Jordan West", "Scooter"),
        ("Taylor King", "Bike")
    ]
    cursor.executemany(
        "INSERT INTO Couriers (name, vehicle_type) VALUES (?, ?);",
        couriers
    )

    conn.commit()

    # =====================================================
    # Generate 10,000 Random Orders
    # =====================================================
    print("🧱 Inserting 10,000 random orders... (this may take a few seconds)")

    num_orders = 10000
    payment_methods = ["Credit Card", "Debit Card", "Cash", "Online"]
    statuses = ["Pending", "Delivered", "Cancelled"]

    start_date = datetime(2024, 1, 1)

    orders_data = []
    order_items_data = []
    payments_data = []
    deliveries_data = []

    for i in range(1, num_orders + 1):
        customer_id = random.randint(1, len(customers))
        restaurant_id = random.randint(1, len(restaurants))
        order_date = start_date + timedelta(days=random.randint(0, 300))
        status = random.choice(statuses)

        # Choose 1–3 dishes for this order
        selected_dishes = random.sample(dishes, random.randint(1, 3))
        total_amount = sum(d[2] for d in selected_dishes)

        # Add to orders
        orders_data.append((customer_id, restaurant_id, order_date.strftime("%Y-%m-%d %H:%M:%S"), total_amount, status))

    cursor.executemany(
        "INSERT INTO Orders (customer_id, restaurant_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?);",
        orders_data
    )
    conn.commit()

    # Build dependent tables
    for order_id in range(1, num_orders + 1):
        dish = random.choice(dishes)
        quantity = random.randint(1, 3)
        subtotal = dish[2] * quantity
        order_items_data.append((order_id, dish[0], quantity, subtotal))

        amount = subtotal
        payment_method = random.choice(payment_methods)
        payment_status = "Completed" if random.random() > 0.05 else "Failed"
        payments_data.append((order_id, amount, payment_method, payment_status))

        courier_id = random.randint(1, len(couriers))
        delivery_status = "Delivered" if payment_status == "Completed" else "Cancelled"
        delivery_time = (start_date + timedelta(days=random.randint(0, 300))).strftime("%Y-%m-%d %H:%M:%S")
        deliveries_data.append((order_id, courier_id, delivery_time, delivery_status))

    cursor.executemany(
        "INSERT INTO Order_Items (order_id, dish_id, quantity, subtotal) VALUES (?, ?, ?, ?);",
        order_items_data
    )
    cursor.executemany(
        "INSERT INTO Payments (order_id, amount, method, status) VALUES (?, ?, ?, ?);",
        payments_data
    )
    cursor.executemany(
        "INSERT INTO Deliveries (order_id, courier_id, delivery_time, status) VALUES (?, ?, ?, ?);",
        deliveries_data
    )

    conn.commit()
    conn.close()
    print("✅ Database 'restaurant_delivery.db' created successfully with 10,000 orders.")


if __name__ == "__main__":
    create_database()
