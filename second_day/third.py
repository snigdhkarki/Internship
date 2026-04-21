import os
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

def task_3():
    print("--- TASK 3: Real API + Analysis ---")
    url = os.getenv('WEATHER_API_URL')

    params = {
        "latitude": 27.7172,
        "longitude": 85.3240,
        "daily": "temperature_2m_max",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        
        dates = data['daily']['time']
        max_temps = data['daily']['temperature_2m_max']

        weather_data = list(zip(dates, max_temps))

        with open('weather.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'max_temp'])
            writer.writerows(weather_data)
        print("Saved 7-day forecast to 'weather.csv'.")

        hottest_day = max(weather_data, key=lambda x: x[1])
        coldest_day = min(weather_data, key=lambda x: x[1])

        print(f"Hottest Day is {hottest_day[0]} with a max temperature of {hottest_day[1]}°C")
        print(f"Coldest Day is {coldest_day[0]} with a max temperature of {coldest_day[1]}°C")

        with open('weather_summary.txt', 'w', encoding='utf-8') as f:
            f.write("7-Day Weather Forecast Summary for Kathmandu\n")
            f.write("-" * 45 + "\n")
            f.write(f"Hottest Day recorded: {hottest_day[0]} ({hottest_day[1]}°C)\n")
            f.write(f"Coldest Day recorded: {coldest_day[0]} ({coldest_day[1]}°C)\n")
        print("Saved analysis summary to 'weather_summary.txt'.")

    else:
        print(f"Failed to fetch. Status code: {response.status_code}")

if __name__ == "__main__":
    task_3()