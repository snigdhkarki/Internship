import requests
import pandas as pd
import sqlite3
import sys

# --- 1. EXTRACT & BONUS (API Error Handling) ---
url = "https://jsonplaceholder.typicode.com/posts"
try:
    response = requests.get(url)
    response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Extraction Failed: Could not fetch data from API. Error: {e}")
    sys.exit(1)

# --- 2. Load into Pandas DataFrame ---
df = pd.DataFrame(data)
total_fetched = len(df)

# --- 3. TRANSFORM (Keep specific columns) ---
df = df[['userId', 'id', 'title', 'body']]

# --- BONUS: Validate userId values are integers ---
# If any userId cannot be cast to an integer, this will raise a ValueError
try:
    df['userId'] = df['userId'].astype(int)
except ValueError as e:
    print(f"Validation Error: 'userId' contains non-integer values. Details: {e}")
    sys.exit(1)

# --- 4. Add word_count column ---
df['word_count'] = df['title'].str.split().str.len()

# --- 5. Filter (word_count >= 4) ---
df = df[df['word_count'] >= 4].copy()
posts_after_filter = len(df)

# --- 6. Standardize (Title case, strip whitespace) ---
df['title'] = df['title'].str.title()
# The body from this specific API contains newline characters, so we'll replace them 
# with spaces before stripping the outer whitespace to make it perfectly clean.
df['body'] = df['body'].str.replace('\n', ' ').str.strip()

# --- 7. LOAD (Save to CSV and SQLite) ---
# Save to CSV
df.to_csv('clean_posts.csv', index=False)

# Save to SQLite posts.db
try:
    with sqlite3.connect('posts.db') as conn:
        df.to_sql('posts', conn, if_exists='replace', index=False)
except sqlite3.Error as e:
    print(f"Database Error: Failed to write to SQLite. Details: {e}")

# --- 8. Print Stats ---
print("\n=== PIPELINE EXECUTION STATS ===")
print(f"Total posts fetched: {total_fetched}")
print(f"Posts after filter:  {posts_after_filter}")
print("\nTop 3 users by post count:")
# .value_counts() automatically sorts by frequency descending
top_users = df['userId'].value_counts().head(3)
for user_id, count in top_users.items():
    print(f"User ID: {user_id} -> {count} posts")
print("================================")
print("Pipeline complete. Deliverables (clean_posts.csv, posts.db) generated successfully.")