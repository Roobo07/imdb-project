import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Page Configuration (Must be called only once)
st.set_page_config(page_title="IMDb 2024 Movies Dashboard", layout="wide")
st.title("🎬 IMDb 2024 Movies Analysis Dashboard")

# 2. Database path
DB_PATH = "imdb_2024.db"

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        st.error(f"Database not found: {DB_PATH}. Ensure Git LFS upload is complete.")
        st.stop()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()
    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🎛 Filters")

# Handle unique genre extraction
all_genres = sorted(set(g.strip() for genres in df["genre"].dropna().str.split(",") for g in genres))
selected_genres = st.sidebar.multiselect("Select Genres", all_genres, default=all_genres)

min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 5.0, 0.1)
min_votes = st.sidebar.number_input("Minimum Votes", 0, value=1000, step=1000)

# Detect the correct duration column name from your schema
duration_col = "duration_min" if "duration_min" in df.columns else "duration_minutes"
min_dur, max_dur = st.sidebar.slider("Duration (minutes)", 0, 300, (60, 180))

# ---------------- DATA FILTERING ----------------
filtered_df = df[
    (df["rating"] >= min_rating) &
    (df["votes"] >= min_votes) &
    (df[duration_col].between(min_dur, max_dur))
].copy()

# Apply genre filter
filtered_df = filtered_df[
    filtered_df["genre"].apply(lambda x: any(g in x for g in selected_genres) if isinstance(x, str) else False)
]

# ---------------- TOP METRICS ----------------
if not filtered_df.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("🎥 Total Movies", len(filtered_df))
    m2.metric("⭐ Avg Rating", round(filtered_df["rating"].mean(), 2))
    m3.metric("⏱ Avg Duration", f"{round(filtered_df[duration_col].mean(), 1)} min")

# ---------------- TOP 10 MOVIES TABLE ----------------
st.subheader("🏆 Top 10 Movies")

if not filtered_df.empty:
    top10 = filtered_df.sort_values("rating", ascending=False).head(10).copy()
    
    # Reset index for clean 1-10 numbering
    top10 = top10.reset_index(drop=True)
    top10.index = top10.index + 1
    
    # Standardize column names for display
    name_col = "movie_name" if "movie_name" in top10.columns else "title"
    top10 = top10.rename(columns={
        name_col: "Movie Name",
        "rating": "Rating",
        "genre": "Genre",
        duration_col: "Duration (Min)",
        "votes": "Votes"
    })
    
    cols_to_show = ["Movie Name", "Rating", "Genre", "Duration (Min)", "Votes"]
    st.dataframe(top10[cols_to_show], use_container_width=True)
else:
    st.warning("No movies found. Try adjusting filters.")

# ---------------- VISUALIZATIONS ----------------
if not filtered_df.empty:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🎭 Genre Distribution")
        gdf = filtered_df.copy()
        gdf["genre"] = gdf["genre"].str.split(",")
        gdf = gdf.explode("genre").reset_index(drop=True)
        gdf["genre"] = gdf["genre"].str.strip()
        genre_counts = gdf["genre"].value_counts().head(10)
        
        fig1, ax1 = plt.subplots()
        genre_counts.plot(kind="bar", ax=ax1, color="skyblue")
        ax1.set_ylabel("Number of Movies")
        st.pyplot(fig1)

    with col_right:
        st.subheader("⭐ Rating Distribution")
        fig2, ax2 = plt.subplots()
        ax2.hist(filtered_df["rating"].dropna(), bins=20, color="orange", edgecolor="black")
        ax2.set_xlabel("Rating")
        st.pyplot(fig2)

    st.subheader("📈 Rating vs Votes")
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.scatter(filtered_df["votes"], filtered_df["rating"], alpha=0.5, color="green")
    ax3.set_xlabel("Votes")
    ax3.set_ylabel("Rating")
    st.pyplot(fig3)

# ---------------- FULL DATA TABLE ----------------
st.subheader("📋 Full Filtered Data")
final_display = filtered_df.reset_index(drop=True)
final_display.index = final_display.index + 1
st.dataframe(final_display, use_container_width=True)
