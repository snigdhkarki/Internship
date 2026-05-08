import sqlite3
import csv
import os

def run_task_a():
    db_file = 'store_db.sqlite'
    conn = None
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 1. Create Tables
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS customers")

        cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                city TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # 2. Insert Data using ? placeholders
        customers = [("Alice", "New York"), ("Bob", "Los Angeles"), ("Charlie", "Chicago"), ("Diana", "Houston"), 
                     ("Evan", "Phoenix"), ("Fiona", "New York"), ("George", "Chicago"), ("Hannah", "Los Angeles"), 
                     ("Ian", "Seattle"), ("Julia", "Austin")]
        cursor.executemany("INSERT INTO customers (name, city) VALUES (?, ?)", customers)

        products = [("Laptop", 999.99), ("Mouse", 25.50), ("Keyboard", 45.00), ("Monitor", 199.99), 
                    ("Desk", 250.00), ("Chair", 150.00), ("Webcam", 59.99), ("Headset", 89.99)]
        cursor.executemany("INSERT INTO products (name, price) VALUES (?, ?)", products)

        orders = [(1,1,1), (1,2,2), (2,3,1), (3,4,2), (4,5,1), (5,6,4), (6,7,1), (7,8,2), (8,1,1), (9,2,3),
                  (10,3,1), (1,4,1), (2,5,2), (3,6,1), (4,7,2), (5,8,1), (6,1,2), (7,2,1), (8,3,2), (1,8,1)]
        cursor.executemany("INSERT INTO orders (customer_id, product_id, quantity) VALUES (?, ?, ?)", orders)
        conn.commit()

        # 3. Required Queries
        print("--- Total Money Spent Per Customer ---")
        cursor.execute("""
            SELECT c.name, SUM(p.price * o.quantity) as total 
            FROM orders o JOIN customers c ON o.customer_id = c.id 
            JOIN products p ON o.product_id = p.id 
            GROUP BY c.id ORDER BY total DESC
        """)
        revenue_results = cursor.fetchall()
        for row in revenue_results: print(f"{row[0]}: ${row[1]:.2f}")

        print("\n--- Most Ordered Product ---")
        cursor.execute("SELECT p.name, SUM(o.quantity) FROM orders o JOIN products p ON o.product_id = p.id GROUP BY p.id ORDER BY SUM(o.quantity) DESC LIMIT 1")
        print(cursor.fetchone())

        print("\n--- Customers with > 2 Orders ---")
        cursor.execute("SELECT c.name, COUNT(o.id) FROM orders o JOIN customers c ON o.customer_id = c.id GROUP BY c.id HAVING COUNT(o.id) > 2")
        for row in cursor.fetchall(): print(f"{row[0]} ({row[1]} orders)")

        print("\n--- Avg Order Value Per City ---")
        cursor.execute("""
            SELECT c.city, AVG(p.price * o.quantity) FROM orders o 
            JOIN customers c ON o.customer_id = c.id JOIN products p ON o.product_id = p.id GROUP BY c.city
        """)
        for row in cursor.fetchall(): print(f"{row[0]}: ${row[1]:.2f}")

        # 4. Export CSV
        with open('revenue_report.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Customer', 'Revenue'])
            writer.writerows(revenue_results)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

run_task_a()