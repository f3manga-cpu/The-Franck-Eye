import json
import hashlib
import os
import datetime
from src.config import CATEGORIES
from src.fetchers.google_rss import fetch_google_news
from src.fetchers.reddit_praw import fetch_reddit_posts

# File Paths
DATA_DIR = "data"
ARCHIVE_FILE = os.path.join(DATA_DIR, "news_archive.json")
ARCHIVE_DIR = os.path.join(DATA_DIR, "archives")

def generate_id(text, source):
    """
    Creates a unique ID based on Title + Source to prevents duplicates 
    even if the URL changes (e.g. tracking params).
    """
    raw_string = f"{text}{source}".lower().strip()
    return hashlib.md5(raw_string.encode('utf-8')).hexdigest()

def load_data():
    """Loads the current 'Hot' DB."""
    if not os.path.exists(ARCHIVE_FILE):
        return []
    try:
        with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_data(data):
    """Saves the 'Hot' DB."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def append_to_cold_storage(old_items):
    """
    Appends items removed from Hot DB to a monthly cold storage file.
    Example: data/archives/archive_2024_01.json
    """
    if not old_items:
        return

    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    current_month = datetime.datetime.now().strftime("%Y_%m")
    cold_file = os.path.join(ARCHIVE_DIR, f"archive_{current_month}.json")

    # Load existing cold data if it exists
    cold_data = []
    if os.path.exists(cold_file):
        try:
            with open(cold_file, 'r', encoding='utf-8') as f:
                cold_data = json.load(f)
        except:
            pass
    
    # Append and Save
    cold_data.extend(old_items)
    with open(cold_file, 'w', encoding='utf-8') as f:
        json.dump(cold_data, f, indent=2, ensure_ascii=False)
    print(f"Archived {len(old_items)} items to {cold_file}")

def run_pipeline():
    print("🚀 Starting Intelligence Pipeline...")
    
    # 1. Load Existing Data
    existing_data = load_data()
    existing_ids = {item['id'] for item in existing_data}
    
    new_items = []

    # 2. Fetch Data for each Category
    for category, conf in CATEGORIES.items():
        print(f"Processing Category: {category}...")
        
        # A. Google News
        if "google_query" in conf:
            g_articles = fetch_google_news(
                conf["google_query"], 
                category, 
                lang=conf.get("lang", "en"), 
                loc=conf.get("loc", "US")
            )
            for item in g_articles:
                item['id'] = generate_id(item['title'], item['source'])
                if item['id'] not in existing_ids:
                    new_items.append(item)
                    existing_ids.add(item['id']) # Prevent duplicates within same run

        # B. Reddit
        if "subreddits" in conf and conf["subreddits"]:
            for sub in conf["subreddits"]:
                r_posts = fetch_reddit_posts(
                    sub, 
                    conf["reddit_query"], 
                    category
                )
                for item in r_posts:
                    item['id'] = generate_id(item['title'], item['source'])
                    if item['id'] not in existing_ids:
                        new_items.append(item)
                        existing_ids.add(item['id'])

    print(f"✅ Fetched {len(new_items)} new items.")

    # 3. Merge & Sort
    # Combine old + new
    all_data = new_items + existing_data
    
    # Sort by published_at (descending) - Simple string comparison works for ISO format
    # But sometimes formats vary, so we strictly put new items at top for now 
    # (or parsing dates if we want strict accuracy, but let's trust the fetch order)
    
    # 4. Enforce Limits (Hot vs Cold Storage)
    MAX_ITEMS = 1000
    if len(all_data) > MAX_ITEMS:
        hot_data = all_data[:MAX_ITEMS]
        cold_items = all_data[MAX_ITEMS:]
        append_to_cold_storage(cold_items)
    else:
        hot_data = all_data

    # 5. Save Live DB
    save_data(hot_data)
    print("💾 Database updated.")

if __name__ == "__main__":
    run_pipeline()
