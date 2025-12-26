# src/config.py

# Structure: Category Name -> (Query, Subreddits_List, Language, Region)
CATEGORIES = {
    "Chess": {
        "google_query": '(FIDE OR "Grandmaster") AND (Tournament OR Match)',
        "subreddits": ["chess"],
        "reddit_query": "tournament OR match",
        "lang": "en", "loc": "US"
    },
    "Poker": {
        "google_query": '(WSOP OR WPT) AND (Result OR Bracelet)',
        "subreddits": ["poker"],
        "reddit_query": "result OR win",
        "lang": "en", "loc": "US"
    },
    "Politics": {
        "google_query": '(Lyon OR France OR "EU") AND (Election OR Parlement OR Loi)',
        "subreddits": ["france", "lyon"],
        "reddit_query": "politique OR election",
        "lang": "fr", "loc": "FR" # Note the French locale
    },
    "A.I.": {
        "google_query": '("Artificial Intelligence" OR "LLM") -stock',
        "subreddits": ["LocalLLaMA", "artificial"],
        "reddit_query": "model OR release",
        "lang": "en", "loc": "US"
    }
}
