# 🍽️ Restaurant & Food Delivery Database System
**ECE 501C Final Project**  
**Authors:** Austin Cortopassi, David Pelley, Amaka Njoku  
**Database:** SQLite3 | **Language:** Python

---

## 📘 Overview
This project implements a **SQLite-based database system** to manage restaurants, customers, orders, deliveries, and payments.  
It is designed to demonstrate principles of **database normalization, integrity constraints, query optimization, and scalability**.

### 🎯 Goals
- Design a **normalized (3NF)** schema to prevent redundancy and maintain consistency.
- Implement and test **transactions**, **foreign keys**, and **error handling**.
- Evaluate **performance and scalability** with and without optimization (e.g., indexes).
- Provide reproducible **Python scripts** for database creation, population, and testing.

---

## 🗂️ Repository Structure
restaurant_delivery_db/
│
├── create_restaurant_db.py # Builds the SQLite database and inserts sample data
├── schema.sql # Contains all CREATE TABLE and INDEX statements
├── evaluate_db.py # (Optional) Script for performance, scalability, and constraint testing
├── queries.py # (Optional) Common query examples (fetch orders, revenue, etc.)
├── restaurant_delivery.db # Generated SQLite database file (created after running script)
└── README.md # Project documentation

---

## ⚙️ Setup Instructions

### 1️⃣ Install Requirements
Ensure you have **Python 3.8+** installed.

pip install pandas matplotlib

SQLite3 is included with Python by default — no extra installation needed.

### 2️⃣ Create the Database
Run the setup script:
python create_restaurant_db.py

This will:

Create a new SQLite database: restaurant_delivery.db

Build all tables (Customers, Restaurants, Orders, etc.)

Insert sample data for quick testing

### 3️⃣ Verify Tables
Open SQLite shell:
sqlite3 restaurant_delivery.db
.tables

You should see:
Customers  Dishes  Orders  Order_Items  Couriers  Deliveries  Payments  Restaurants
🧱 Database Schema (3NF)
Main entities and relationships:

Customers (1–M) Orders

Restaurants (1–M) Dishes

Orders (1–M) Order_Items (M–1) Dishes

Orders (1–1) Payments

Orders (1–1) Deliveries (M–1) Couriers

Each table uses foreign keys, CHECK constraints, and ON DELETE CASCADE to maintain integrity.

📊 Evaluation Plan
Test	Goal	Method	Metric
1. Query Performance	Measure speedup from indexes	Compare SELECT runtimes before/after indexing	Avg query time (ms)
2. Transaction Test	Validate atomicity and rollback	Simulate order+payment inserts with intentional failure	Success vs. rollback outcome
3. Scalability	Assess performance growth with data volume	Insert 1k, 10k, 50k+ orders	Insert time (s), query latency
4. Constraint Testing	Ensure data integrity	Insert invalid data (negative price, bad FK, duplicates)	Pass/Fail results

Optional scripts in evaluate_db.py automate these tests.

🧪 Example Queries
-- 1. Orders by a specific customer
SELECT * FROM Orders WHERE customer_id = 1;

-- 2. Total revenue by restaurant
SELECT r.name, SUM(o.total_amount) AS total_revenue
FROM Orders o
JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY r.restaurant_id;

-- 3. Average delivery time
SELECT courier_id, AVG(julianday(delivery_time) - julianday(order_date)) * 24 AS avg_hours
FROM Deliveries
JOIN Orders USING (order_id)
GROUP BY courier_id;
🚀 Extensions (for Extra Credit)
Dynamic delivery fee calculation based on distance or time.

Analytics dashboard (using Streamlit or Flask).

Recommendation system for customers (based on order history).

🧾 References
SQLite Documentation

Python sqlite3 Module

Course Material – ECE 501C Database Systems

✅ Authors
Austin Cortopassi

David Pelley

Amaka Njoku

