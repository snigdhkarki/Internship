import sqlite3
import requests

# API Endpoints
USERS_URL = "https://jsonplaceholder.typicode.com/users"
POSTS_URL = "https://jsonplaceholder.typicode.com/posts"

def build_pipeline():
    # 2. Create app.db and establish a connection
    conn = None
    try:
        print("Connecting to database...")
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()

        # Create the users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                city TEXT,
                company_name TEXT
            )
        ''')

        # 7. Add a second table for posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                body TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # 1. Fetch all users from the API
        print("Fetching users from API...")
        response_users = requests.get(USERS_URL)
        response_users.raise_for_status() # Raises an error for bad HTTP status codes
        users_data = response_users.json()

        # 3 & 4. Extract nested data and Insert all 10 users with error handling
        print("Inserting users into database...")
        users_to_insert = []
        for user in users_data:
            users_to_insert.append((
                user.get('id'),
                user.get('name'),
                user.get('email'),
                user.get('phone'),
                user.get('address', {}).get('city'),     # Extract nested city
                user.get('company', {}).get('name')      # Extract nested company name
            ))
        
        # Using INSERT OR IGNORE prevents crashing if you run the script multiple times
        cursor.executemany('''
            INSERT OR IGNORE INTO users (id, name, email, phone, city, company_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', users_to_insert)

        # 7. Fetch posts and insert ONLY posts by user_id 1, 2, and 3
        print("Fetching posts from API...")
        response_posts = requests.get(POSTS_URL)
        response_posts.raise_for_status()
        posts_data = response_posts.json()

        print("Filtering and inserting posts...")
        posts_to_insert = []
        for post in posts_data:
            if post.get('userId') in [1, 2, 3]:
                posts_to_insert.append((
                    post.get('id'),
                    post.get('userId'),
                    post.get('title'),
                    post.get('body')
                ))

        cursor.executemany('''
            INSERT OR IGNORE INTO posts (id, user_id, title, body)
            VALUES (?, ?, ?, ?)
        ''', posts_to_insert)

        # Commit all the insertions
        conn.commit()
        print("Data successfully committed!\n")

        # ==========================================
        # QUERIES & DELIVERABLES
        # ==========================================

        # 5. Query 1: Print all users sorted alphabetically by name
        print("--- Query 1: Users Sorted Alphabetically ---")
        cursor.execute("SELECT name, city, company_name FROM users ORDER BY name ASC")
        for row in cursor.fetchall():
            print(f"{row[0]:<25} | {row[1]:<15} | {row[2]}")
        print("\n")

        # 6. Query 2: Find users from the same city (GROUP BY city, HAVING COUNT > 1)
        print("--- Query 2: Cities with Multiple Users ---")
        cursor.execute('''
            SELECT city, COUNT(*) as count 
            FROM users 
            GROUP BY city 
            HAVING count > 1
        ''')
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"City: {row[0]}, Count: {row[1]}")
        else:
            print("No cities have more than 1 user in this dataset.")
        print("\n")

        # Bonus: JOIN users and posts — print each user's name + how many posts they have
        print("--- Bonus Query: Users and their Post Counts ---")
        cursor.execute('''
            SELECT u.name, COUNT(p.id) as total_posts
            FROM users u
            JOIN posts p ON u.id = p.user_id
            GROUP BY u.id
        ''')
        for row in cursor.fetchall():
            print(f"User: {row[0]:<20} | Total Posts: {row[1]}")

    except requests.exceptions.RequestException as req_err:
        print(f"Network Error occurred while fetching data: {req_err}")
    except sqlite3.Error as sql_err:
        print(f"Database Error occurred: {sql_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Always ensure the connection is closed
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    build_pipeline()