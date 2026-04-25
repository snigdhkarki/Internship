import requests
import pandas as pd
import os
from datetime import datetime, timezone, timedelta
import time

API_KEY = '0acf739a675f79db70dadeaecf51df94'
COUNTRIES = {'np': 'Nepal', 'in': 'India', 'us': 'USA', 'gb': 'UK', 'au': 'Australia'}
MAIN_CSV = 'all_headlines.csv'
FILTERED_CSV = 'filtered_headlines.csv'

def fetch_and_save_data():
    """Fetches data from GNews API, cleans it, prevents duplicates, and saves to CSV."""
    all_articles = []
    
    for code, country_name in COUNTRIES.items():
        url = f"https://gnews.io/api/v4/top-headlines?country={code}&apikey={API_KEY}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                for article in articles:
                    all_articles.append({
                        'title': article.get('title'),
                        'description': article.get('description'),
                        'content': article.get('content'),
                        'url': article.get('url'),
                        'image': article.get('image'),
                        'publishedat': article.get('publishedAt'),
                        'sourcename': article.get('source', {}).get('name') if article.get('source') else None,
                        'sourceurl': article.get('source', {}).get('url') if article.get('source') else None,
                        'country': country_name
                    })
            else:
                print(f"Failed to fetch {country_name}: {response.status_code}")
                time.sleep(1)
        except Exception as e:
            print(f"Error fetching {country_name}: {e}")

    new_df = pd.DataFrame(all_articles)

    if new_df.empty:
        print("No data fetched from the API.")
        return False

    new_df.columns = [col.lower().replace(' ', '') for col in new_df.columns]

    new_df = new_df.fillna("N/A")
    new_df = new_df.replace(r'^\s*$', "N/A", regex=True)

    if os.path.exists(MAIN_CSV):
        existing_df = pd.read_csv(MAIN_CSV)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    combined_df = combined_df.drop_duplicates(subset=['url', 'country'], keep='first')

    combined_df.to_csv(MAIN_CSV, index=False)
    return True

def analyze_data():
    """Reads strictly from the saved CSV to answer the analytical questions."""
    
    df = pd.read_csv(MAIN_CSV)
    
    df = df.fillna("N/A")

    df['word_count'] = df['title'].apply(lambda x: len(str(x).split()) if x != "N/A" else 0)

    print("\n--- PIPELINE ANALYSIS RESULTS ---")

    most_headlines_country = df['country'].value_counts().idxmax()
    print(f"1. Country with most headlines: {most_headlines_country}")

    print("2. Average words per headline by country:")
    avg_words = df.groupby('country')['word_count'].mean()
    for country, avg in avg_words.items():
        print(f"   - {country}: {avg:.2f} words")

    title_counts = df.groupby('title')['country'].nunique()
    multi_country = title_counts[title_counts > 1]
    if not multi_country.empty:
        print(f"3. Yes, {len(multi_country)} headline(s) appeared in multiple countries:")
        for title in multi_country.index:
            countries_list = df[df['title'] == title]['country'].unique()
            print(f"   - '{title}' (Seen in: {', '.join(countries_list)})")
    else:
        print("3. No headlines appeared in more than one country.")

    valid_sources = df[df['sourcename'] != "N/A"]
    top_source = valid_sources['sourcename'].value_counts().idxmax()
    print(f"4. News source with most headlines overall: {top_source}")

    now = pd.Timestamp.utcnow()
    df['publishedat_dt'] = pd.to_datetime(df['publishedat'], errors='coerce', utc=True)
    
    valid_dates = df['publishedat_dt'].dropna()
    if not valid_dates.empty:
        time_diff = now - valid_dates
        last_6_hours_count = (time_diff <= pd.Timedelta(hours=6)).sum()
        total_count = len(valid_dates)
        
        pct_recent = (last_6_hours_count / total_count) * 100
        pct_older = 100 - pct_recent
        print(f"5. Time distribution: {pct_recent:.1f}% published in the last 6 hours, {pct_older:.1f}% are older.")
    else:
        print("5. Time distribution: N/A (No valid dates found).")

    print("6. Duplicate prevention: Handled gracefully. If you run the script twice, it loads the existing CSV, appends the new API data, and drops duplicates based on a combination of the 'url' and 'country' columns before saving it back.")

    filtered_df = df[df['word_count'] > 6].copy()
    filtered_df = filtered_df.drop(columns=['word_count', 'publishedat_dt'], errors='ignore')
    filtered_df.to_csv(FILTERED_CSV, index=False)
    print(f"7. Filtered CSV created ('{FILTERED_CSV}'). Number of headlines passing the >6 word filter: {len(filtered_df)}")

    longest_country = avg_words.idxmax()
    shortest_country = avg_words.idxmin()
    print(f"8. Longest average headline: {longest_country} ({avg_words[longest_country]:.2f} words)")
    print(f"   Shortest average headline: {shortest_country} ({avg_words[shortest_country]:.2f} words)")

if __name__ == "__main__":
    success = fetch_and_save_data()
    if success:
        analyze_data()