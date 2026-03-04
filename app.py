import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Page configuration
st.set_page_config(page_title="IMDb 2024 Movies Dashboard", layout="wide")

st.title("🎬 IMDb 2024 Movies Analysis Dashboard")

# 2. Database path
st.set_page_config(
    page_title="IMDb 2024 Movies Dashboard",
    layout="wide"
)

st.title("🎬 IMDb 2024 Movies Analysis Dashboard")

DB_PATH = "imdb_2024.db"

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        st.error(f"Database not found: {DB_PATH}")
        st.stop()
    conn = sqlite3.connect(DB_PATH)
    # Loading exactly as it exists in your SQLite file

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()
    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🎛 Filters")

# Handle comma-separated genre strings
all_genres = sorted(set(g.strip() for genres in df["genre"].dropna().str.split(",") for g in genres))

selected_genres = st.sidebar.multiselect("Select Genres", all_genres, default=all_genres)
all_genres = sorted(
    set(
        g.strip()
        for genres in df["genre"].dropna().str.split(",")
        for g in genres
    )
)

selected_genres = st.sidebar.multiselect(
    "Select Genres", all_genres, default=all_genres
)

min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 5.0, 0.1)
min_votes = st.sidebar.number_input("Minimum Votes", 0, value=1000, step=1000)

min_dur, max_dur = st.sidebar.slider("Duration (minutes)", 0, 300, (60, 180))

# ---------------- DATA FILTERING ----------------
# Use 'duration_min' to match the schema shown in your database screenshot
duration_col = "duration_min" if "duration_min" in df.columns else "duration_minutes"
min_dur, max_dur = st.sidebar.slider(
    "Duration (minutes)", 0, 300, (60, 180)
)

filtered_df = df[
    (df["rating"] >= min_rating) &
    (df["votes"] >= min_votes) &
    (df[duration_col].between(min_dur, max_dur))
].copy()

filtered_df = filtered_df[
    filtered_df["genre"].apply(lambda x: any(g in x for g in selected_genres) if isinstance(x, str) else False)
    (df["duration_minutes"].between(min_dur, max_dur))
]

filtered_df = filtered_df[
    filtered_df["genre"].apply(
        lambda x: any(g in x for g in selected_genres)
        if isinstance(x, str) else False
    )
]

# ---------------- METRICS ----------------
c1, c2, c3 = st.columns(3)
if not filtered_df.empty:
    c1.metric("🎥 Movies", len(filtered_df))
    c2.metric("⭐ Avg Rating", round(filtered_df["rating"].mean(), 2))
    c3.metric("⏱ Avg Duration", f"{round(filtered_df[duration_col].mean(), 1)} min")
# ---------------- TOP MOVIES (FIXED FOR TITLE VISIBILITY) ----------------
st.subheader("🏆 Top 10 Movies")

if not filtered_df.empty:
    # 1. Sort and get top 10
    top10 = filtered_df.sort_values("rating", ascending=False).head(10).copy()
    
    # 2. Reset the index to remove scattered DB row numbers (0, 10, 41...)
    top10 = top10.reset_index(drop=True)
    top10.index = top10.index + 1 # Clean Serial Numbers 1-10
    
    # 3. CRITICAL STEP: Identify if the title column is 'title' or 'movie_name'
    # Based on your image, it is lowercase 'title'
    if 'title' in top10.columns:
        top10 = top10.rename(columns={"title": "Movie Name"})
    elif 'movie_name' in top10.columns:
        top10 = top10.rename(columns={"movie_name": "Movie Name"})

    # 4. Standardize other columns
    top10 = top10.rename(columns={
        "rating": "Rating",
        "genre": "Genre",
        "duration_min": "Duration (Min)",
        "duration_minutes": "Duration (Min)",
        "votes": "Votes"
    })
    
    # 5. Explicitly select the NEW names for display
    display_cols = ["Movie Name", "Rating", "Genre", "Duration (Min)", "Votes"]
    
    # Safety: Only show columns that actually exist now
    existing_cols = [c for c in display_cols if c in top10.columns]
    
    # This will now show the Movie Name column as the first column
    st.dataframe(top10[existing_cols], use_container_width=True)
else:
    st.warning("No movies found. Try adjusting your sidebar filters.")
# ---------------- VISUALIZATIONS ----------------
if not filtered_df.empty:
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

# ---------------- DATA TABLE (CLEAN S.NO) ----------------
st.subheader("📋 Full Movie Data")
display_df = filtered_df.reset_index(drop=True)
display_df.index = display_df.index + 1
st.dataframe(display_df, use_container_width=True)

c1.metric("🎥 Movies", len(filtered_df))
c2.metric("⭐ Avg Rating", round(filtered_df["rating"].mean(), 2))
c3.metric("⏱ Avg Duration", round(filtered_df["duration_minutes"].mean(), 1))

# ---------------- TOP MOVIES ----------------
st.subheader("🏆 Top 10 Movies")

top10 = filtered_df.sort_values("rating", ascending=False).head(10)
st.dataframe(top10, use_container_width=True)

# ---------------- GENRE DISTRIBUTION ----------------
st.subheader("🎭 Genre Distribution")

gdf = filtered_df.copy()
gdf["genre"] = gdf["genre"].str.split(",")
gdf = gdf.explode("genre")
gdf["genre"] = gdf["genre"].str.strip()

genre_counts = gdf["genre"].value_counts().head(10)

fig1, ax1 = plt.subplots()
genre_counts.plot(kind="bar", ax=ax1)
ax1.set_ylabel("Movies")
st.pyplot(fig1)

# ---------------- RATING DISTRIBUTION ----------------
st.subheader("⭐ Rating Distribution")

fig2, ax2 = plt.subplots()
ax2.hist(filtered_df["rating"].dropna(), bins=20)
st.pyplot(fig2)

# ---------------- RATING VS VOTES ----------------
st.subheader("📈 Rating vs Votes")

fig3, ax3 = plt.subplots()
ax3.scatter(filtered_df["votes"], filtered_df["rating"], alpha=0.5)
ax3.set_xlabel("Votes")
ax3.set_ylabel("Rating")
st.pyplot(fig3)

# ---------------- DATA TABLE ----------------
st.subheader("📋 Movie Data")
st.dataframe(filtered_df, use_container_width=True)
