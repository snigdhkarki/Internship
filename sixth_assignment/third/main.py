import pandas as pd
import requests
import sqlite3
import logging

# Configure production-style logging (prints directly to terminal/stdout)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ==========================================
# 1. EXTRACT
# ==========================================
def extract(api_url: str) -> pd.DataFrame:
    """Fetches data from a public API with robust error handling."""
    logging.info("Starting EXTRACT phase...")
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status() # Catches 4xx and 5xx errors
        
        # The DummyJSON API wraps the list in a 'products' key
        data = response.json().get('products', [])
        df = pd.DataFrame(data)
        
        logging.info(f"Extract successful. Received {len(df)} rows.")
        return df
        
    except requests.exceptions.Timeout:
        logging.error("API request timed out.")
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
    except requests.exceptions.RequestException as err:
        logging.error(f"Connection Error: {err}")
    
    return pd.DataFrame() # Return empty DataFrame on failure

# ==========================================
# 2. CLEAN
# ==========================================
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes types, drops duplicates, and handles missing data."""
    if df.empty:
        return df
        
    logging.info(f"Starting CLEAN phase with {len(df)} rows...")
    
    # Drop exact duplicates based on the primary key
    df_clean = df.drop_duplicates(subset=['id']).copy()
    
    # Handle Nulls (DummyJSON usually has clean data, but we enforce it here)
    df_clean['price'] = pd.to_numeric(df_clean['price'], errors='coerce').fillna(0)
    df_clean['category'] = df_clean['category'].fillna('Unknown').str.title()
    
    logging.info(f"Clean complete. Output {len(df_clean)} rows.")
    return df_clean

# ==========================================
# 3. TRANSFORM
# ==========================================
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Engineers new columns and generates summary statistics."""
    if df.empty:
        return df
        
    logging.info(f"Starting TRANSFORM phase with {len(df)} rows...")
    
    # Transformation 1: Calculate absolute discount amount
    df['discount_amount'] = (df['price'] * (df['discountPercentage'] / 100)).round(2)
    
    # Transformation 2: Calculate final consumer price
    df['final_price'] = (df['price'] - df['discount_amount']).round(2)
    
    # Transformation 3: Categorical Stock Status (Pass/Fail equivalent)
    df['stock_status'] = df['stock'].apply(lambda x: 'Critical/Low' if x < 20 else 'Healthy')
    
    # Generate and print Summary Table using GroupBy
    print("\n--- Category Pricing Summary ---")
    summary = df.groupby('category')['price'].agg(['mean', 'min', 'max']).round(2)
    print(summary)
    print("--------------------------------\n")
    
    # Select a subset of useful columns for the final load
    final_cols = ['id', 'title', 'category', 'price', 'discountPercentage', 
                  'discount_amount', 'final_price', 'stock', 'stock_status']
    
    df_transformed = df[final_cols]
    
    logging.info(f"Transform complete. Output {len(df_transformed)} rows.")
    return df_transformed

# ==========================================
# 4. LOAD
# ==========================================
def load(df: pd.DataFrame, csv_filename: str, db_name: str, table_name: str):
    """Loads data to CSV and SQLite idempotently (avoids duplicates)."""
    if df.empty:
        logging.warning("No data to load. Pipeline aborting.")
        return

    logging.info(f"Starting LOAD phase with {len(df)} rows...")

    # A. Load to CSV
    df.to_csv(csv_filename, index=False)
    logging.info(f"Saved to CSV: {csv_filename}")

    # B. Load to SQLite
    conn = sqlite3.connect(db_name)
    
    try:
        # Try to fetch existing IDs
        existing_ids_query = f"SELECT id FROM {table_name}"
        existing_ids = pd.read_sql(existing_ids_query, conn)['id'].tolist()
        
        # Filter: Keep only rows where 'id' is NOT in the database
        df_new = df[~df['id'].isin(existing_ids)]
        logging.info(f"Found {len(existing_ids)} existing records. Filtering for {len(df_new)} new rows.")
        
    except (pd.errors.DatabaseError, sqlite3.OperationalError):
        # This triggers if the table doesn't exist yet (First Run)
        df_new = df
        logging.info(f"Table '{table_name}' not found. Initializing first-time load.")

    if not df_new.empty:
        # 'append' mode will create the table if it doesn't exist
        df_new.to_sql(table_name, conn, if_exists='append', index=False)
        logging.info(f"Successfully loaded {len(df_new)} records to SQLite.")
    else:
        logging.info("No new records to load. Database is already up to date.")

    conn.close()
# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    API_URL = "https://dummyjson.com/products"
    CSV_FILE = "products_enriched.csv"
    DB_FILE = "inventory.db"
    TABLE = "products"

    # Run Pipeline
    raw_data = extract(API_URL)
    cleaned_data = clean(raw_data)
    enriched_data = transform(cleaned_data)
    load(enriched_data, CSV_FILE, DB_FILE, TABLE)