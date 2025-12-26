import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Intelligence Digest",
    page_icon="🧠",
    layout="wide"
)

# Constants
DATA_FILE = "data/news_archive.json"

def load_data():
    """Loads the JSON data into a Pandas DataFrame."""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    # Convert string dates to datetime objects for sorting
    # We handle errors just in case formats vary slightly
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce', utc=True)
    return df

def main():
    st.title("🧠 The Intelligence Digest")
    
    # 1. Load Data
    df = load_data()
    
    if df.empty:
        st.warning("No data found. Please run 'python src/processor.py' to fetch news.")
        return

    # 2. Sidebar Controls
    st.sidebar.header("Filters")
    
    # Category Filter
    all_categories = df['category'].unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "Select Categories", 
        options=all_categories, 
        default=all_categories
    )
    
    # Source Filter (Optional, good for noise reduction)
    all_sources = sorted(df['source'].unique().tolist())
    # selected_sources = st.sidebar.multiselect("Filter by Source", all_sources, default=all_sources) 

    # 3. Main Search & Sort
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Global Search (Title)", placeholder="Search keywords...")
    with col2:
        sort_order = st.selectbox("Sort By", ["Newest First", "Oldest First"])

    # 4. Filtering Logic
    filtered_df = df[df['category'].isin(selected_categories)]
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False)
        ]

    # Sorting
    if sort_order == "Newest First":
        filtered_df = filtered_df.sort_values(by='published_at', ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by='published_at', ascending=True)

    # 5. Display Stats
    st.markdown(f"**Showing {len(filtered_df)} items** (Total Database: {len(df)})")
    st.divider()

    # 6. Render News Cards
    # Using simple Markdown for speed and clarity
    for _, row in filtered_df.iterrows():
        # Visual cues based on source type
        icon = "🐦" if row['type'] == 'social' else "📰"
        score_badge = f"🔥 Score: {row['score']}" if row['type'] == 'social' and 'score' in row else ""
        
        # Formatting the timestamp
        time_str = row['published_at'].strftime("%Y-%m-%d %H:%M") if pd.notnull(row['published_at']) else "Just now"

        with st.container():
            st.markdown(f"""
            ### [{row['title']}]({row['url']})
            **{icon} {row['source']}** | *{row['category']}* | 🕒 {time_str} {score_badge}
            """)
            st.divider()

if __name__ == "__main__":
    main()
