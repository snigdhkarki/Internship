import sqlite3
import requests

# 1. Configuration for 3 cities (Kathmandu, Pokhara, Lalitpur)
CITIES = [
    {"name": "Kathmandu", "lat": 27.70, "lon": 85.32},
    {"name": "Pokhara", "lat": 28.20, "lon": 83.98},
    {"name": "Lalitpur", "lat": 27.67, "lon": 85.31}
]

DB_NAME = "weather.db"
REPORT_FILE = "summary.txt"

def fetch_and_store_weather():
    try:
        # 2. Create weather.db and forecasts table
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS forecasts")
        cursor.execute('''
            CREATE TABLE forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                date TEXT,
                max_temp REAL,
                min_temp REAL
            )
        ''')

        # 1 & 3. Fetch data and Insert 21 rows
        print("Fetching weather data from Open-Meteo...")
        for city in CITIES:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
            response = requests.get(url)
            data = response.json()
            
            daily = data['daily']
            for i in range(7):
                cursor.execute('''
                    INSERT INTO forecasts (city, date, max_temp, min_temp)
                    VALUES (?, ?, ?, ?)
                ''', (city['name'], daily['time'][i], daily['temperature_2m_max'][i], daily['temperature_2m_min'][i]))

        conn.commit()
        print(f"Successfully stored 21 rows in {DB_NAME}.\n")

        # --- ANALYSIS QUERIES ---
        report_content = []

        # 4. Query 1: City with the highest average max temperature
        cursor.execute('''
            SELECT city, AVG(max_temp) as avg_max 
            FROM forecasts GROUP BY city ORDER BY avg_max DESC LIMIT 1
        ''')
        q1 = cursor.fetchone()
        res1 = f"Query 1: City with highest avg max temp: {q1[0]} ({q1[1]:.2f}°C)"
        report_content.append(res1)

        # 5. Query 2: Single hottest day across all 3 cities
        cursor.execute('SELECT city, date, max_temp FROM forecasts ORDER BY max_temp DESC LIMIT 1')
        q2 = cursor.fetchone()
        res2 = f"Query 2: Hottest day: {q2[0]} on {q2[1]} ({q2[2]}°C)"
        report_content.append(res2)

        # 6. Query 3: Days where temp difference (max - min) > 10°C
        cursor.execute('SELECT city, date, (max_temp - min_temp) as diff FROM forecasts WHERE diff > 10')
        q3 = cursor.fetchall()
        res3 = "Query 3: Days with temp difference > 10°C:\n" + "\n".join([f" - {r[0]} ({r[1]}): {r[2]:.2f}°C" for r in q3])
        report_content.append(res3)

        # 7. Save summary report to summary.txt
        with open(REPORT_FILE, "w") as f:
            f.write("WEATHER ANALYSIS REPORT\n")
            f.write("=======================\n\n")
            f.write("\n\n".join(report_content))
        
        # Print to console for visibility
        for line in report_content: print(line)
        print(f"\nReport saved to {REPORT_FILE}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    fetch_and_store_weather()