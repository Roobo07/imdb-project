import streamlit as st
import pandas as pd
import os

# ------------------------------
# App config
# ------------------------------
st.set_page_config(
    page_title="IMDb Movie Analysis",
    layout="wide"
)

st.title("🎬 IMDb Movie Data Analysis")

# ------------------------------
# Helper: detect Streamlit Cloud
# ------------------------------
def running_on_streamlit_cloud():
    return os.getenv("STREAMLIT_CLOUD") == "true" or os.path.exists("/mount/src")

# ------------------------------
# Data paths
# ------------------------------
RAW_DATA_PATH = "data/raw/title.basics.tsv.gz"
SAMPLE_DATA_PATH = "data/sample/title_basics_sample.csv"

# ------------------------------
# Load data safely
# ------------------------------
@st.cache_data
def load_data():
    if os.path.exists(RAW_DATA_PATH):
        st.success("Loaded full IMDb dataset")
        return pd.read_csv(
            RAW_DATA_PATH,
            sep="\t",
            compression="gzip",
            low_memory=False
        )

    elif os.path.exists(SAMPLE_DATA_PATH):
        st.warning("Using sample dataset (Streamlit Cloud mode)")
        return pd.read_csv(SAMPLE_DATA_PATH)

    else:
        st.error("❌ No dataset found")
        return None

df = load_data()

if df is None:
    st.stop()

# ------------------------------
# Basic cleaning
# ------------------------------
df = df[df["titleType"] == "movie"]
df = df[df["startYear"] != "\\N"]
df["startYear"] = df["startYear"].astype(int)

# ------------------------------
# Sidebar filters
# ------------------------------
st.sidebar.header("🔎 Filters")

year_range = st.sidebar.slider(
    "Release Year",
    int(df["startYear"].min()),
    int(df["startYear"].max()),
    (2000, 2022)
)

filtered_df = df[
    (df["startYear"] >= year_range[0]) &
    (df["startYear"] <= year_range[1])
]

# ------------------------------
# Metrics
# ------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Movies", len(filtered_df))
col2.metric("Earliest Year", filtered_df["startYear"].min())
col3.metric("Latest Year", filtered_df["startYear"].max())

# ------------------------------
# Visualization
# ------------------------------
st.subheader("📊 Movies Released Per Year")

movies_per_year = (
    filtered_df
    .groupby("startYear")
    .size()
    .reset_index(name="count")
)

st.bar_chart(
    movies_per_year.set_index("startYear")
)

# ------------------------------
# Data preview
# ------------------------------
st.subheader("📄 Data Preview")
st.dataframe(filtered_df.head(20))
