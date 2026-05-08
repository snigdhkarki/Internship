import os
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

def task_2():
    print("--- TASK 2: Fetch & Save to CSV ---")
    url = os.getenv('POSTS_API_URL')
    response = requests.get(url)

    if response.status_code == 200:
        posts = response.json()

        with open('posts.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'body'])
            writer.writeheader()
            for post in posts:
                writer.writerow({'id': post['id'], 'title': post['title'], 'body': post['body']})
        print("Saved all fetched posts to 'posts.csv'.")

        filtered_posts = []
        with open('posts.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word_count = len(row['title'].split())
                if word_count > 5:
                    filtered_posts.append(row)

        with open('filtered_posts.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'body'])
            writer.writeheader()
            writer.writerows(filtered_posts)
        print(f"Filtered {len(filtered_posts)} posts and saved to 'filtered_posts.csv'.")

    else:
        print(f"Failed to fetch. Status code: {response.status_code}")

if __name__ == "__main__":
    task_2()