import feedparser
import urllib.parse

def fetch_google_news(query, category_name, lang="en", loc="US"):
    """
    Fetches news from Google News RSS.
    Args:
        query (str): The boolean search string.
        category_name (str): The category label (e.g., 'Chess').
        lang (str): Language code (en, fr).
        loc (str): Location code (US, FR).
    """
    # URL Encode the query
    encoded_query = urllib.parse.quote(query)
    
    # Construct URL with localization
    # ceid usually combines loc:lang, e.g., US:en or FR:fr
    ceid = f"{loc}:{lang}"
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={lang}-{loc}&gl={loc}&ceid={ceid}"
    
    print(f"Fetching {category_name} ({lang}-{loc})...")
    
    feed = feedparser.parse(rss_url)
    articles = []

    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "url": entry.link,
            "source": entry.source.title if 'source' in entry else "Google News",
            "category": category_name,
            "published_at": entry.published,
            "type": "news"
        })
        
    return articles

if __name__ == "__main__":
    # Test: Fetch AI news (English) and Politics (French/Lyon)
    ai_news = fetch_google_news('("Artificial Intelligence" OR "LLM") -stock', "A.I.")
    lyon_news = fetch_google_news('(Lyon OR France) AND (Politique OR Election)', "Politics", lang="fr", loc="FR")
    
    print(f"Found {len(ai_news)} AI articles and {len(lyon_news)} French articles.")
