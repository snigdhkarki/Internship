import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# ==========================================
# STEP 1: Fetch Weather Data & Store in SQLite
# ==========================================
print("Step 1: Fetching 7-day weather data from Open-Meteo API...")

cities = {
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
    "Cairo": {"lat": 30.0444, "lon": 31.2357}
}

# Connect to SQLite database (creates weather.db if it doesn't exist)
conn = sqlite3.connect('weather.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS weather')
cursor.execute('''
    CREATE TABLE weather (
        city TEXT,
        date TEXT,
        max_temp REAL,
        min_temp REAL,
        rainfall REAL
    )
''')

for city_name, coords in cities.items():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&daily=temperature_2m_max,temperature_2m_min,rain_sum&timezone=auto"
    response = requests.get(url).json()
    
    daily = response['daily']
    for i in range(len(daily['time'])):
        cursor.execute('''
            INSERT INTO weather (city, date, max_temp, min_temp, rainfall)
            VALUES (?, ?, ?, ?, ?)
        ''', (city_name, daily['time'][i], daily['temperature_2m_max'][i], daily['temperature_2m_min'][i], daily['rain_sum'][i]))

conn.commit()
print("-> Data successfully saved to weather.db\n")

# ==========================================
# STEP 2: Load into Pandas & Run EDA Checklist
# ==========================================
print("Step 2: Running full EDA Checklist...")
df = pd.read_sql_query("SELECT * FROM weather", conn)

print(f"\n[Shape of Dataset]: {df.shape}")
print("\n[Null Values count]:")
print(df.isnull().sum())
print("\n[Descriptive Statistics]:")
print(df.describe())
print("\n[Value Counts per City]:")
print(df['city'].value_counts())
print("-" * 50)

# Set global plotting style for aesthetic graphs
sns.set_theme(style="whitegrid")

# ==========================================
# STEP 3: Histogram of Combined Max Temperatures
# ==========================================
print("Step 3: Generating combined Max Temperature Histogram...")
plt.figure(figsize=(8, 5))
sns.histplot(df['max_temp'], kde=True, color='#4A90E2', bins=12)
plt.title('Distribution of Max Temperatures Across All Cities Combined', fontsize=12, fontweight='bold')
plt.xlabel('Max Temperature (°C)')
plt.ylabel('Frequency Counts')
plt.tight_layout()
plt.savefig('chart1_histogram.png', dpi=300)
plt.close()

# ==========================================
# STEP 4: Side-by-Side Box Plots
# ==========================================
print("Step 4:rs each box plot according to its regional location, then hides the resulting duplicate tracking chart legend box since the horizont Generating Side-by-Side Box Plots...")
plt.figure(figsize=(10, 6))
sns.boxplot(x='city', y='max_temp', data=df, palette='Set2')
plt.title('Max Temperature Comparison Across 5 Cities', fontsize=14, fontweight='bold')
plt.xlabel('City')
plt.ylabel('Max Temperature (°C)')
plt.tight_layout()
plt.savefig('chart2_boxplot.png', dpi=300)
plt.close()

# ==========================================
# STEP 5: Identify Outliers Using IQR Method
# ==========================================
print("Step 5: Identifying Outliers via IQR Method...")
outliers_df = pd.DataFrame()

for city in df['city'].unique():
    city_data = df[df['city'] == city]
    Q1 = city_data['max_temp'].quantile(0.25)
    Q3 = city_data['max_temp'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df[numeric_cols].hist(bins=20, edgecolor='black', figsize=(12, 8))
    # Filter records outside limits
    city_outliers = city_data[(city_data['max_temp'] < lower_bound) | (city_data['max_temp'] > upper_bound)]
    outliers_df = pd.concat([outliers_df, city_outliers])

print("\n--- Outlier Days Found ---")
if outliers_df.empty:
    print("No statistical outliers found in this 7-day window.")
else:
    print(outliers_df)
print("-" * 50)

# ==========================================
# STEP 6: KDE Curve Comparison (Spread Analysis)
# ==========================================
print("Step 6: Generating KDE Curves...")
plt.figure(figsize=(10, 6))
sns.kdeplot(data=df, x='max_temp', hue='city', fill=True, common_norm=False, alpha=0.2, linewidth=2)
plt.title('Kernel Density Estimate (KDE) of Max Temperatures per City', fontsize=14, fontweight='bold')
plt.xlabel('Max Temperature (°C)')
plt.ylabel('Density Distribution')
plt.tight_layout()
plt.savefig('chart3_kde.png', dpi=300)
plt.close()

# ==========================================
# STEP 7: Grouped Summary Table
# ==========================================
print("Step 7: Grouped Statistical Summary Table:")
summary_table = df.groupby('city')['max_temp'].agg(['mean', 'median', 'std', 'min', 'max']).round(2)
print("\n", summary_table)
print("-" * 50)

# ==========================================
# BONUS: Rainfall Distribution Comparison
# ==========================================
print("Bonus Step: Generating Rainfall Evaluation Chart...")
plt.figure(figsize=(10, 6))
sns.barplot(x='city', y='rainfall', data=df, estimator=sum, errorbar=None, palette='Blues_r')
plt.title('Total Rainfall Accumulation Over 7 Days', fontsize=14, fontweight='bold')
plt.xlabel('City')
plt.ylabel('Total Precipitation (mm)')
plt.tight_layout()
plt.savefig('chart4_rainfall.png', dpi=300)
plt.close()

# Close DB connection cleanly
conn.close()
print("\nAll tasks finalized! Output charts saved locally as .png files.")