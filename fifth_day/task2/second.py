import sqlite3
import requests
from datetime import datetime

API_URL = "https://jsonplaceholder.typicode.com/posts"

def run_task_b():
    conn = None
    try:
        conn = sqlite3.connect('monitor_db.sqlite')
        cursor = conn.cursor()
        
        # Setup Tables
        cursor.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, userId INTEGER, title TEXT, body TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS change_log (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, change_type TEXT, change_time TEXT, run_id INTEGER)")
        
        def sync_data(run_id):
            print(f"\n--- Starting Sync Run {run_id} ---")
            response = requests.get(API_URL)
            data = response.json()
            
            for item in data:
                cursor.execute("SELECT title, body FROM posts WHERE id = ?", (item['id'],))
                existing = cursor.fetchone()
                
                if not existing:
                    cursor.execute("INSERT INTO posts VALUES (?, ?, ?, ?)", (item['id'], item['userId'], item['title'], item['body']))
                    cursor.execute("INSERT INTO change_log (post_id, change_type, change_time, run_id) VALUES (?, 'NEW', ?, ?)", (item['id'], datetime.now(), run_id))
                elif existing[0] != item['title'] or existing[1] != item['body']:
                    cursor.execute("UPDATE posts SET title=?, body=? WHERE id=?", (item['title'], item['body'], item['id']))
                    cursor.execute("INSERT INTO change_log (post_id, change_type, change_time, run_id) VALUES (?, 'MODIFIED', ?, ?)", (item['id'], datetime.now(), run_id))
            conn.commit()

        # Run 1
        sync_data(run_id=1)
        
        # Simulate Manual Change
        print("\n[Action Required] Manually updating ID 1 in database to trigger detection...")
        cursor.execute("UPDATE posts SET title='Changed Manually' WHERE id=1")
        conn.commit()
        
        # Run 2 (Detects that local 'Changed Manually' != API title)
        sync_data(run_id=2)

        # Print Results
        print("\n--- Change Log Entries (Latest Run) ---")
        cursor.execute("SELECT * FROM change_log WHERE run_id = 2")
        for row in cursor.fetchall(): print(row)

        print("\n--- Post Count Per User ---")
        cursor.execute("SELECT userId, COUNT(*) FROM posts GROUP BY userId")
        for row in cursor.fetchall(): print(f"User {row[0]}: {row[1]} posts")

        print("\n--- User with Most Changes ---")
        cursor.execute("SELECT p.userId, COUNT(c.id) FROM change_log c JOIN posts p ON c.post_id = p.id GROUP BY p.userId ORDER BY COUNT(c.id) DESC LIMIT 1")
        print(cursor.fetchone())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

run_task_b()