#EDA - Exploratory Data Analysis

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==========================================
# Step 1: Load the dataset
# ==========================================
db_name = 'etl_pipeline.db' 

if not os.path.exists(db_name):
    print(f" Error: Could not find '{db_name}'. Please update the variable!")
else:
    conn = sqlite3.connect(db_name)
    query = "SELECT * FROM users"
    df = pd.read_sql(query, conn)
    conn.close()
    print("Step 1: 'users' dataset loaded successfully.\n")

    # ==========================================
    # Step 2: Shape, Info, and Dtypes
    # ==========================================
    print("--- Step 2: Shape, Info, Dtypes ---")
    print(f"Shape of DataFrame: {df.shape}")
    print("\nData Types:")
    print(df.dtypes)
    print("\nInfo Summary:")
    df.info()

    # ==========================================
    # Step 3: Check for missing values & %
    # ==========================================
    print("\n--- Step 3: Missing Values ---")
    missing_counts = df.isnull().sum()
    missing_percentages = (missing_counts / len(df)) * 100

    missing_df = pd.DataFrame({
        'Missing Values': missing_counts, 
        'Percentage (%)': missing_percentages
    })
    print(missing_df)

    # ==========================================
    # Step 4: Describe and identify observations
    # ==========================================
    print("\n--- Step 4: Describe ---")
    print(df.describe())

    # ==========================================
    # Step 5: Value counts on a categorical column
    # ==========================================
    print("\n--- Step 5: Value Counts ---")
    print("Value counts for 'city':")
    print(df['city'].value_counts())

    # ==========================================
    # Step 6: Plot a histogram for every numeric column
    # ==========================================
    print("\n--- Step 6: Histograms ---")
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

    plt.figure(figsize=(12, 8))
    df[numeric_cols].hist(bins=20, edgecolor='black', figsize=(12, 8))
    plt.suptitle('Histograms of Numeric Columns', fontsize=16)
    plt.tight_layout()
    plt.savefig('step6_histograms.png')
    print("Saved 'step6_histograms.png' to your current directory.")
    plt.close()

    # ==========================================
    # Step 7: Plot a box plot for at least 2 columns
    # ==========================================
    print("\n--- Step 7: Box Plots ---")
    cols_to_plot = ['age', 'salary'] 

    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df[cols_to_plot])
    plt.title('Box Plots for Age and Salary')
    plt.savefig('step7_boxplots.png')
    print("Saved 'step7_boxplots.png' to your current directory.")
    plt.close()

    # ==========================================
    # Bonus Step: sns.pairplot() on numeric columns
    # ==========================================
    print("\n--- Bonus Step: Pairplot ---")
    if len(numeric_cols) > 1:
        cols_for_pairplot = [col for col in numeric_cols if col != 'id']
        sns.pairplot(df[cols_for_pairplot])
        plt.savefig('bonus_pairplot.png')
        print("Saved 'bonus_pairplot.png' to your current directory.")
        plt.close()