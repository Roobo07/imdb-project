import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Page Configuration
st.set_page_config(page_title="IMDb 2024 Movies Dashboard", layout="wide")
st.title("🎬 IMDb 2024 Movies Analysis Dashboard")

# 2. Database Setup
DB_PATH = "imdb_2024.db"

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        st.error(f"Database not found: {DB_PATH}. Please ensure Git LFS uploaded the file correctly.")
        st.stop()
    conn = sqlite3.connect(DB_PATH)
    # Reading data from your actual database table
    df = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()
    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🎛 Filters")
all_genres = sorted(set(g.strip() for genres in df["genre"].dropna().str.split(",") for g in genres))
selected_genres = st.sidebar.multiselect("Select Genres", all_genres, default=all_genres)
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 5.0, 0.1)

# ---------------- DATA FILTERING ----------------
filtered_df = df[df["rating"] >= min_rating].copy()
filtered_df = filtered_df[
    filtered_df["genre"].apply(lambda x: any(g in x for g in selected_genres) if isinstance(x, str) else False)
]

# ---------------- TOP MOVIES (RESTORED TITLES & S.NO) ----------------
st.subheader("🏆 Top 10 Movies")

if not filtered_df.empty:
    # 1. Get top 10 movies by rating
    top10 = filtered_df.sort_values("rating", ascending=False).head(10).copy()
    
    # 2. Reset index to remove random DB IDs and create a clean 1, 2, 3... sequence
    top10 = top10.reset_index(drop=True)
    top10.index = top10.index + 1
    
    # 3. Rename columns to match your database screenshot
    # We use 'movie_name' because that is the column name in your SQLite file
    top10 = top10.rename(columns={
        "movie_name": "Movie Name", 
        "rating": "Rating",
        "genre": "Genre",
        "votes": "Votes"
    })
    
    # 4. Final Display with professional headers
    display_cols = ["Movie Name", "Rating", "Genre", "Votes"]
    st.dataframe(top10[display_cols], use_container_width=True)
else:
    st.warning("No movies match these filters.")
