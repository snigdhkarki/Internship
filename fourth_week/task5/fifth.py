import requests
import pandas as pd
import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# ==========================================
# 1. EXTRACT
# ==========================================
def extract(url: str) -> list:
    """Fetches data from a public API with full error handling."""
    logging.info(f"EXTRACT: Starting extraction from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        results = data.get('results', [])
        logging.info(f"EXTRACT: Successfully extracted {len(results)} records.")
        return results
        
    except requests.exceptions.HTTPError as errh:
        logging.error(f"EXTRACT: HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"EXTRACT: Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"EXTRACT: Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logging.error(f"EXTRACT: Something went wrong: {err}")
    
    return [] # Return empty list if extraction fails

# ==========================================
# 2. TRANSFORM
# ==========================================
def transform(raw_data: list) -> pd.DataFrame:
    """Loads raw JSON into Pandas, cleans, and enriches it."""
    if not raw_data:
        logging.warning("TRANSFORM: No data to transform.")
        return pd.DataFrame()
        
    logging.info("TRANSFORM: Loading data into Pandas DataFrame.")
    
    # Flatten the nested JSON structure
    df = pd.json_normalize(raw_data)
    
    initial_rows = len(df)
    
    # --- A. CLEANING ---
    # Keep only relevant columns for our database
    columns_to_keep = [
        'login.uuid', 'name.first', 'name.last', 'email', 
        'dob.age', 'registered.date', 'phone'
    ]
    df = df[columns_to_keep].copy()
    
    # Rename columns to be database friendly (remove dots)
    df.columns = ['user_id', 'first_name', 'last_name', 'email', 'age', 'registration_date', 'phone']
    
    # 1. String Issues: Standardize names to title case, emails to lowercase
    df['first_name'] = df['first_name'].str.title()
    df['last_name'] = df['last_name'].str.title()
    df['email'] = df['email'].str.lower()
    
    # 2. Nulls: Fill missing phone numbers with a default string
    df['phone'] = df['phone'].fillna('Unknown')
    
    # 3. Data Types: Ensure age is integer, cast registration to datetime
    df['age'] = df['age'].astype(int)
    df['registration_date'] = pd.to_datetime(df['registration_date']).dt.tz_localize(None)
    
    # 4. Duplicates: Drop exact duplicate rows based on user_id
    df = df.drop_duplicates(subset=['user_id'])
    
    # --- B. ENRICHMENT (2 Calculated Columns) ---
    logging.info("TRANSFORM: Adding enriched/calculated columns.")
    
    # Enrichment 1: Full Name combination
    df['full_name'] = df['first_name'] + ' ' + df['last_name']
    
    # Enrichment 2: Age Category
    def categorize_age(age):
        if age < 30: return 'Young Adult'
        elif age < 50: return 'Adult'
        else: return 'Senior'
        
    df['age_category'] = df['age'].apply(categorize_age)
    
    # Enrichment 3 (Bonus): Ingestion timestamp to track when we got this data
    df['ingested_at'] = datetime.now()
    
    final_rows = len(df)
    logging.info(f"TRANSFORM: Cleaning complete. Dropped {initial_rows - final_rows} rows. Current row count: {final_rows}.")
    
    return df

# ==========================================
# 3. LOAD
# ==========================================
def load(df: pd.DataFrame, db_name: str, table_name: str, csv_filename: str):
    """Saves to CSV and loads into SQLite, preventing duplicate entries."""
    if df.empty:
        logging.warning("LOAD: DataFrame is empty. Skipping load phase.")
        return

    # 1. Export to Clean CSV
    df.to_csv(csv_filename, index=False)
    logging.info(f"LOAD: Successfully exported {len(df)} rows to {csv_filename}")

    # 2. Load to SQLite (Handling the Bonus: No Duplicates on 2nd Run)
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        
        # BONUS LOGIC: Explicitly check if the table exists first
        check_table_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        table_exists = not pd.read_sql(check_table_query, conn).empty
        
        if table_exists:
            # Table exists, fetch existing IDs
            existing_ids_df = pd.read_sql(f"SELECT user_id FROM {table_name}", conn)
            existing_ids = existing_ids_df['user_id'].tolist()
            
            # Filter the incoming dataframe to only include NEW user_ids
            df_to_insert = df[~df['user_id'].isin(existing_ids)]
            logging.info(f"LOAD: Found existing table. {len(df) - len(df_to_insert)} duplicate rows filtered out.")
        else:
            # Table doesn't exist yet (first run), insert everything
            df_to_insert = df
            logging.info("LOAD: Target table does not exist yet. Creating new table.")

        if not df_to_insert.empty:
            # Append new records to the database
            df_to_insert.to_sql(table_name, conn, if_exists='append', index=False)
            logging.info(f"LOAD: Successfully inserted {len(df_to_insert)} new rows into SQLite table '{table_name}'.")
        else:
            logging.info("LOAD: No new rows to insert. Database is up to date.")

    except sqlite3.Error as e:
        logging.error(f"LOAD: SQLite Error: {e}")
    except Exception as e:
        logging.error(f"LOAD: Unexpected Error: {e}")
    finally:
        if conn:
            conn.close()
# ==========================================
# 4. ORCHESTRATION (Main Pipeline)
# ==========================================
def run_pipeline():
    # Configuration
    API_URL = "https://randomuser.me/api/?results=50&inc=login,name,email,dob,registered,phone"
    DB_FILE = "capstone_warehouse.db"
    TABLE_NAME = "users"
    CSV_FILE = "clean_users_export.csv"
    
    logging.info("--- PIPELINE START ---")
    
    # 1. Extract
    raw_data = extract(API_URL)
    
    # 2. Transform
    clean_df = transform(raw_data)
    
    # 3. Load
    load(clean_df, DB_FILE, TABLE_NAME, CSV_FILE)
    
    logging.info("--- PIPELINE COMPLETE ---\n")

# ==========================================
# EXECUTION (Including Bonus Requirement)
# ==========================================
if __name__ == "__main__":
    print("Executing Run 1 (Initial Data Load)...")
    run_pipeline()
    
    print("Executing Run 2 (Bonus: Testing duplicate prevention)...")
    # Running it immediately again. Because we use RandomUser API, we will get 50 NEW users.
    # To test the duplicate logic effectively, let's artificially force a duplicate run 
    # by capturing the exact same DataFrame from the first run and trying to load it again.
    
    # Simulate picking up the same data file by accident:
    print("Simulating accidentally running the pipeline on the EXACT same data...")
    logging.info("--- PIPELINE START (DUPLICATE SIMULATION) ---")
    existing_clean_df = pd.read_csv("clean_users_export.csv") 
    load(existing_clean_df, "capstone_warehouse.db", "users", "clean_users_export.csv")
    logging.info("--- PIPELINE COMPLETE (DUPLICATE SIMULATION) ---\n")