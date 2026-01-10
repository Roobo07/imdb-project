import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="IMDb 2024 Movies", layout="wide")

st.title("🎬 IMDb 2024 Movies Dashboard")

DATA_PATH = "data/sample/imdb_sample.csv"
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Dataset not found. Please check the file path.")
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")

genres = ["All"] + sorted(df["genre"].unique().tolist())
selected_genre = st.sidebar.selectbox("Select Genre", genres)

min_rating = st.sidebar.slider(
    "Minimum IMDb Rating",
    min_value=float(df["rating"].min()),
    max_value=float(df["rating"].max()),
    value=7.0,
    step=0.1
)

# Apply filters
filtered_df = df.copy()

if selected_genre != "All":
    filtered_df = filtered_df[filtered_df["genre"] == selected_genre]

filtered_df = filtered_df[filtered_df["rating"] >= min_rating]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("🎥 Movies", len(filtered_df))
col2.metric("⭐ Avg Rating", round(filtered_df["rating"].mean(), 2))
col3.metric("🗳 Total Votes", int(filtered_df["votes"].sum()))

st.divider()

# Top 10 movies
st.subheader("🏆 Top 10 Movies by Rating")

top10 = filtered_df.sort_values(by="rating", ascending=False).head(10)
st.dataframe(top10, use_container_width=True)

# Bar chart
st.subheader("📊 Average Rating by Genre")

genre_avg = (
    filtered_df.groupby("genre")["rating"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots()
genre_avg.plot(kind="bar", ax=ax)
ax.set_ylabel("Average Rating")
ax.set_xlabel("Genre")
plt.xticks(rotation=45)
st.pyplot(fig)

st.divider()

# Full table
st.subheader("📋 All Movies")
st.dataframe(filtered_df, use_container_width=True)

