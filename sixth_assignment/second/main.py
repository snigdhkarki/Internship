import requests
import pandas as pd
import numpy as np
import sqlite3
from typing import Dict

# ==========================================
# 1. EXTRACT & INJECT NOISE (For Demonstration)
# ==========================================
def fetch_and_corrupt_data() -> pd.DataFrame:
    """Fetches clean data and injects noise to demonstrate the audit system."""
    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url)
    df = pd.DataFrame(response.json())
    
    # --- Injecting Artificial Data Issues ---
    # 1. Nulls
    df.loc[0:2, 'title'] = np.nan 
    # 2. Duplicates
    df = pd.concat([df, df.iloc[[5, 6]]], ignore_index=True) 
    # 3. Type Mismatch (String in numeric column)
    df.loc[10, 'userId'] = "User_11" 
    # 4. Out-of-Range (Negative ID)
    df.loc[15, 'id'] = -99 
    # 5. Inconsistent String Format (ALL CAPS when expected lowercase/title)
    df.loc[20, 'title'] = "THIS IS AN INCONSISTENT ALL CAPS TITLE" 
    
    return df

# ==========================================
# 2. DATA QUALITY AUDIT SYSTEM
# ==========================================
def profile_data(df: pd.DataFrame) -> Dict[str, int]:
    """Profiles the dataframe and returns a dictionary of issue counts."""
    audit = {}
    
    # Basic Counts
    audit['Total Rows'] = len(df)
    audit['Total Nulls'] = df.isnull().sum().sum()
    audit['Duplicate Rows'] = df.duplicated().sum()
    
    # Type Mismatches (userId should be numeric)
    # Checks if values are not numeric types
    is_not_numeric = df['userId'].apply(lambda x: not isinstance(x, (int, float, np.integer, np.floating)))
    audit['Type Mismatches'] = is_not_numeric.sum()
    
    # Out-of-Range Values (id should be > 0)
    # We coerce errors to NaN so we can safely compare strings that got mixed into numeric columns
    numeric_ids = pd.to_numeric(df['id'], errors='coerce')
    audit['Out-of-Range (id <= 0)'] = (numeric_ids <= 0).sum()
    
    # Inconsistent String Formats (Checking for fully uppercase titles)
    valid_titles = df['title'].dropna()
    audit['Inconsistent Strings (ALL CAPS)'] = valid_titles.apply(lambda x: str(x).isupper()).sum()
    
    return audit

def generate_audit_report(audit_before: dict, audit_after: dict):
    """Compares before/after metrics and prints a formatted audit report."""
    print("\n" + "="*60)
    print(" DATA QUALITY AUDIT REPORT ".center(60, "="))
    print("="*60)
    
    report_data = []
    for key in audit_before.keys():
        before_val = audit_before[key]
        after_val = audit_after[key]
        
        if "Rows" in key:
            fixed = "N/A"
        else:
            fixed = before_val - after_val
            
        report_data.append({
            "Metric": key,
            "Before Cleaning": before_val,
            "After Cleaning": after_val,
            "Issues Fixed": fixed
        })
        
    report_df = pd.DataFrame(report_data)
    print(report_df.to_string(index=False))
    print("="*60 + "\n")
    
    # Optionally save to CSV
    report_df.to_csv("data_quality_audit_report.csv", index=False)

# ==========================================
# 3. TRANSFORM & CLEAN
# ==========================================
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Applies cleaning, transformations, and enrichments."""
    cleaned_df = df.copy()
    
    # -- Cleaning --
    # 1. Drop duplicates
    cleaned_df = cleaned_df.drop_duplicates()
    
    # 2. Fix Type mismatches (Force to numeric, invalid becomes NaN)
    cleaned_df['userId'] = pd.to_numeric(cleaned_df['userId'], errors='coerce')
    cleaned_df['id'] = pd.to_numeric(cleaned_df['id'], errors='coerce')
    
    # 3. Drop Nulls (This catches original nulls + those created by fixing type mismatches)
    cleaned_df = cleaned_df.dropna()
    
    # 4. Filter Out-of-Range
    cleaned_df = cleaned_df[cleaned_df['id'] > 0]
    
    # -- Transformation & Enrichment --
    # 5. Title Casing (Fixes inconsistent ALL CAPS strings)
    cleaned_df['title'] = cleaned_df['title'].str.title()
    
    # 6. Word Count Enrichment
    cleaned_df['word_count'] = cleaned_df['body'].str.split().str.len()
    
    # 7. Filtering (Only keep posts with more than 10 words)
    cleaned_df = cleaned_df[cleaned_df['word_count'] > 10]
    
    # 8. Ranking (Rank by longest posts)
    cleaned_df['post_length_rank'] = cleaned_df['word_count'].rank(ascending=False, method='min').astype(int)
    
    return cleaned_df

# ==========================================
# 4. LOAD
# ==========================================
def load_to_sqlite(df: pd.DataFrame, db_name: str = "posts_data.db"):
    """Loads the cleaned DataFrame into a SQLite database."""
    conn = sqlite3.connect(db_name)
    df.to_sql('clean_posts', conn, if_exists='replace', index=False)
    conn.close()
    print(f"Successfully loaded {len(df)} rows into SQLite database '{db_name}'.")

# ==========================================
# EXECUTE PIPELINE
# ==========================================
if __name__ == "__main__":
    # 1. Extract
    raw_data = fetch_and_corrupt_data()
    
    # 2. Pre-Cleaning Audit
    pre_audit_metrics = profile_data(raw_data)
    
    # 3. Transform
    clean_data = transform_data(raw_data)
    
    # 4. Post-Cleaning Audit
    post_audit_metrics = profile_data(clean_data)
    
    # 5. Generate Report
    generate_audit_report(pre_audit_metrics, post_audit_metrics)
    
    # 6. Load
    load_to_sqlite(clean_data)