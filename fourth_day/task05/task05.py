import sqlite3
import requests
import csv
import sys

# Configuration
API_URL = "https://jsonplaceholder.typicode.com/posts"
DB_NAME = "capstone.db"
CSV_EXPORT = "analysis_results.csv"

def fetch_data(url):
    """Fetch data from public API with error handling."""
    try:
        print(f"[*] Fetching data from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[!] API Error: Could not fetch data. {e}")
        sys.exit(1)

def store_data(data, db_name):
    """Store all fetched data in a structured SQLite database."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Table Structure
        cursor.execute("DROP TABLE IF EXISTS posts")
        cursor.execute('''
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                body TEXT
            )
        ''')

        # Formatting data for executemany
        formatted_data = [(i['id'], i['userId'], i['title'], i['body']) for i in data]
        
        cursor.executemany("INSERT INTO posts VALUES (?, ?, ?, ?)", formatted_data)
        conn.commit()
        print(f"[+] Successfully stored {len(data)} records in {db_name}")
        return conn
    except sqlite3.Error as e:
        print(f"[!] Database Error: {e}")
        sys.exit(1)

def run_analysis(conn):
    """Run 3 meaningful SQL queries and return results for export."""
    results = {}
    try:
        cursor = conn.cursor()

        # Query 1: Count posts per user
        print("\n--- Analysis 1: Posts Per User ---")
        cursor.execute("SELECT user_id, COUNT(*) FROM posts GROUP BY user_id")
        results['posts_per_user'] = cursor.fetchall()
        for row in results['posts_per_user']:
            print(f"User {row[0]}: {row[1]} posts")

        # Query 2: Top 5 longest post titles
        print("\n--- Analysis 2: Top 5 Longest Titles ---")
        cursor.execute("SELECT title, LENGTH(title) as len FROM posts ORDER BY len DESC LIMIT 5")
        results['longest_titles'] = cursor.fetchall()
        for row in results['longest_titles']:
            print(f"({row[1]} chars) {row[0][:50]}...")

        # Query 3: Search for specific keyword frequency
        print("\n--- Analysis 3: Posts containing 'voluptas' ---")
        cursor.execute("SELECT COUNT(*) FROM posts WHERE body LIKE '%voluptas%'")
        results['keyword_match'] = cursor.fetchone()
        print(f"Found {results['keyword_match'][0]} posts containing the keyword.")

        return results
    except sqlite3.Error as e:
        print(f"[!] Analysis Error: {e}")
        return None

def export_to_csv(analysis_data, filename):
    """Export combined results to a CSV file."""
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Exporting Posts per User
            writer.writerow(["ANALYSIS 1: POSTS PER USER"])
            writer.writerow(["User ID", "Post Count"])
            writer.writerows(analysis_data['posts_per_user'])
            writer.writerow([]) # Spacer

            # Exporting Longest Titles
            writer.writerow(["ANALYSIS 2: LONGEST TITLES"])
            writer.writerow(["Title", "Character Length"])
            writer.writerows(analysis_data['longest_titles'])
            
        print(f"\n[+] Results successfully exported to {filename}")
    except IOError as e:
        print(f"[!] File Export Error: {e}")

def main():
    """Bonus: Automates the entire pipeline upon running."""
    print("=== STARTING CAPSTONE DATA SYSTEM ===")
    
    # Step 1: Fetch
    raw_data = fetch_data(API_URL)
    
    # Step 2: Store
    connection = store_data(raw_data, DB_NAME)
    
    # Step 3: Analyze
    report_data = run_analysis(connection)
    
    # Step 4: Export
    if report_data:
        export_to_csv(report_data, CSV_EXPORT)
    
    connection.close()
    print("\n=== SYSTEM TASK COMPLETE ===")

if __name__ == "__main__":
    main()