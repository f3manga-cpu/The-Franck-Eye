import praw
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

def fetch_reddit_posts(subreddit_name, search_query, category_name, limit=10):
    """
    Fetches top posts from a subreddit using Boolean search logic.
    """
    # Initialize PRAW with error handling for missing keys
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "digest_bot_v1")
        )
    except Exception as e:
        print(f"Error initializing Reddit API: {e}")
        return []

    posts = []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        # Search within the subreddit
        for submission in subreddit.search(search_query, sort="relevance", time_filter="day", limit=limit):
            posts.append({
                "title": submission.title,
                "url": submission.url,
                "source": f"r/{subreddit_name}",
                "category": category_name,
                "published_at": datetime.datetime.fromtimestamp(submission.created_utc).isoformat(),
                "type": "social",
                "score": submission.score
            })
    except Exception as e:
        print(f"Error fetching from Reddit: {e}")

    return posts
