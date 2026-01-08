import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

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
    df = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()
    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🎛 Filters")

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

min_dur, max_dur = st.sidebar.slider(
    "Duration (minutes)", 0, 300, (60, 180)
)

filtered_df = df[
    (df["rating"] >= min_rating) &
    (df["votes"] >= min_votes) &
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
