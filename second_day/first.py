import os
import requests
from dotenv import load_dotenv

load_dotenv()

def task_1():
    print("--- TASK 1: Fetch & Print ---")
    url = os.getenv('USERS_API_URL')
    response = requests.get(url)

    if response.status_code == 200:
        users = response.json()
        
        for user in users:
            name = user.get('name')
            email = user.get('email')
            city = user.get('address', {}).get('city') 
            print(f"Name: {name} | Email: {email} | City: {city}")
    else:
        print(f"Failed to fetch. Status code: {response.status_code}")

if __name__ == "__main__":
    task_1()