import requests
import pandas as pd
import sqlite3

BASE_URL = "https://jsonplaceholder.typicode.com"

# --- 1 & 2. EXTRACT: Fetch data and create DataFrames ---
users_data = requests.get(f"{BASE_URL}/users").json()
posts_data = requests.get(f"{BASE_URL}/posts").json()
todos_data = requests.get(f"{BASE_URL}/todos").json()  # Extraction for Bonus

df_posts = pd.DataFrame(posts_data)
df_todos = pd.DataFrame(todos_data)

# --- 3. Normalize User Data ---
# pd.json_normalize flattens the 'address' dictionary into 'address.city'
df_users = pd.json_normalize(users_data)
df_users = df_users[['id', 'name', 'email', 'address.city']]
df_users = df_users.rename(columns={'address.city': 'city'})

# --- 4. Prepare Post Data ---
df_posts = df_posts[['userId', 'title']]
df_posts = df_posts.rename(columns={'userId': 'id'})

# --- 6. Count posts per user ---
# Grouping by user ID to get a total count for each student/user
post_counts = df_posts.groupby('id').size().reset_index(name='post_count')
df_users = pd.merge(df_users, post_counts, on='id', how='left')

# --- BONUS: Merge Todos and calculate completion rate ---
# completion_rate = (True values / Total tasks) * 100
df_todos = df_todos.rename(columns={'id': 'task_id', 'userId': 'id'})

# 2. Now 'id' refers to only one column (the User ID)
todo_stats = df_todos.groupby('id')['completed'].agg(['count', 'sum']).reset_index()

# 3. Calculate completion rate
todo_stats['completion_rate'] = (todo_stats['sum'] / todo_stats['count']) * 100
df_users = pd.merge(df_users, todo_stats[['id', 'completion_rate']], on='id', how='left')


# --- 5. TRANSFORM: Merge Users and Posts ---
# Merging into a unified dataset as per the task goal
df_merged = pd.merge(df_users, df_posts, on='id')

# --- 7. Clean: Lowercase, Strip, and Drop Nulls ---
df_merged['email'] = df_merged['email'].str.lower()
df_merged['name'] = df_merged['name'].str.strip()
df_merged['city'] = df_merged['city'].str.strip()
df_merged = df_merged.dropna()

# --- 8. LOAD: Save to CSV and SQLite ---
df_merged.to_csv('merged_data.csv', index=False)

with sqlite3.connect('merged.db') as conn:
    df_merged.to_sql('unified_data', conn, if_exists='replace', index=False)

# Print Top 3 most active users
print("=== TOP 3 MOST ACTIVE USERS ===")
# Sorting the user-level DataFrame by post_count
top_3 = df_users.sort_values(by='post_count', ascending=False).head(3)
for _, row in top_3.iterrows():
    print(f"User: {row['name']} | Posts: {row['post_count']} | Completion Rate: {row['completion_rate']:.2f}%")