import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------
# App configuration
# -----------------------------
st.set_page_config(
    page_title="IMDb Analysis App",
    layout="wide"
)

st.title("🎬 IMDb Analysis Dashboard")
st.success("✅ App started successfully")

# -----------------------------
# Dataset path (Cloud-safe)
# -----------------------------
DATA_PATH = Path("data/sample/imdb_sample.csv")

# -----------------------------
# Load dataset safely
# -----------------------------
if not DATA_PATH.exists():
    st.error("❌ No dataset found at data/sample/imdb_sample.csv")
    st.info("Make sure the file exists in the GitHub repository.")
    st.stop()

df = pd.read_csv(DATA_PATH)

# -----------------------------
# Show data
# -----------------------------
st.subheader("📊 Sample IMDb Dataset")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Simple analytics
# -----------------------------
st.subheader("⭐ Average Rating")
st.metric(
    label="Average IMDb Rating",
    value=round(df["rating"].mean(), 2)
)

st.subheader("🎭 Movies by Genre")
genre_counts = df["genre"].value_counts()
st.bar_chart(genre_counts)

# -----------------------------
# Footer
# -----------------------------
st.caption("Built with ❤️ using Streamlit")
