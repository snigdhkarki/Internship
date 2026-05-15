import pandas as pd
import requests
import sqlite3
import io
import numpy as np
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================================
# 1. EXTRACT
# ==========================================

# A. Setup Fault-Tolerant API Connection
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

try:
    print("Fetching API data...")
    response = session.get('https://jsonplaceholder.typicode.com/users', timeout=5)
    response.raise_for_status() # Catches HTTP Error Codes (4xx, 5xx)
    api_data = response.json()
except requests.exceptions.RequestException as e:
    print(f"API Extraction Failed: {e}")
    api_data = []

# B. Mocking a Local Messy CSV
messy_csv_content = """id,Name, EMAIL_ADDR ,city,age,salary
101,  John Doe , Sincere@april.biz, New York, 25, 50000
102, Jane Smith, jane@example.com, , 200, -100
103, Bob  , bob@test.com, Chicago, thirty, 60000
101,  John Doe , Sincere@april.biz, New York, 25, 50000
"""
csv_buffer = io.StringIO(messy_csv_content)
df_csv = pd.read_csv(csv_buffer)


# ==========================================
# 2. NORMALIZE & MERGE
# ==========================================

# Normalize Nested JSON (Extracting address.city)
df_api = pd.json_normalize(api_data)[['id', 'name', 'email', 'address.city']]
df_api.rename(columns={'address.city': 'city'}, inplace=True)

# Standardize merge keys (emails)
df_api['email'] = df_api['email'].astype(str).str.lower().str.strip()

# FIX: Rename both the email and the Name column to match the API DataFrame exactly
df_csv.rename(columns={' EMAIL_ADDR ': 'email', 'Name': 'name'}, inplace=True)
df_csv['email'] = df_csv['email'].astype(str).str.lower().str.strip()

# Merge with Conflict Resolution (Outer join to keep everything)
df_merged = pd.merge(df_csv, df_api, on='email', how='outer', suffixes=('_csv', '_api'))

# Conflict Resolution: Combine columns, prioritizing API data over CSV data
# Because both were called 'name' before the merge, they now have the proper suffixes
df_merged['name'] = df_merged['name_api'].combine_first(df_merged['name_csv'])
df_merged['city'] = df_merged['city_api'].combine_first(df_merged['city_csv'])
df_merged['id'] = df_merged['id_api'].combine_first(df_merged['id_csv'])

# 3. Cleanup (Now it's safe to drop the suffixed columns)
columns_to_drop = [col for col in df_merged.columns if col.endswith('_csv') or col.endswith('_api')]
df_merged.drop(columns=columns_to_drop, inplace=True)

# ==========================================
# 3. CLEANING (The 6 Techniques)
# ==========================================

# 1. Whitespace: Strip leading/trailing spaces from all string columns
for col in df_merged.select_dtypes(include=['object']).columns:
    df_merged[col] = df_merged[col].astype(str).str.strip()

# 2. Casing: Standardize name formatting
df_merged['name'] = df_merged['name'].str.title()

# 3. Duplicates: Drop exact duplicate rows based on email
df_merged.drop_duplicates(subset=['email'], keep='first', inplace=True)

# 4. Types: Coerce age and salary to numeric (turns "thirty" into NaN)
df_merged['age'] = pd.to_numeric(df_merged['age'], errors='coerce')
df_merged['salary'] = pd.to_numeric(df_merged['salary'], errors='coerce')

# 5. Outliers: Remove impossible ages (>120) and negative salaries by turning them to NaN
df_merged.loc[(df_merged['age'] > 120) | (df_merged['age'] < 0), 'age'] = np.nan
df_merged.loc[df_merged['salary'] < 0, 'salary'] = np.nan

# 6. Nulls: Impute missing numerical data with medians, categorical with 'Unknown'
df_merged['age'] = df_merged['age'].fillna(df_merged['age'].median())
df_merged['salary'] = df_merged['salary'].fillna(df_merged['salary'].median())
df_merged['city'] = df_merged['city'].replace('nan', 'Unknown') # Clean up string 'nan' from whitespace step
df_merged['city'] = df_merged['city'].fillna('Unknown')

print("\n--- Cleaned & Merged DataFrame ---")
print(df_merged[['email', 'name', 'city', 'age', 'salary']].head())

# ==========================================
# 4. LOAD
# ==========================================

# Load 1: To CSV
csv_filename = "unified_clean_data.csv"
df_merged.to_csv(csv_filename, index=False)
print(f"\nData successfully saved to {csv_filename}")

# Load 2: To SQLite (Idempotent / No Duplicates on second run)
db_name = "etl_pipeline.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create table with a UNIQUE constraint on email
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    email TEXT UNIQUE,
    id REAL,
    name TEXT,
    city TEXT,
    age REAL,
    salary REAL
)
''')

# Iterate and INSERT OR IGNORE to ensure idempotency
inserted_count = 0
for _, row in df_merged.iterrows():
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, id, name, city, age, salary)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (row['email'], row['id'], row['name'], row['city'], row['age'], row['salary']))
    
    if cursor.rowcount > 0:
        inserted_count += 1

conn.commit()
conn.close()

print(f"Inserted {inserted_count} new rows into SQLite '{db_name}'.")
print("Run the script again: you will see 0 new rows inserted due to the UNIQUE constraint.")