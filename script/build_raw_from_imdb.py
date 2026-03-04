import pandas as pd
import os

# 🔐 Always resolve paths from PROJECT ROOT
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

print("📂 RAW DIR:", RAW_DIR)

print("📥 Loading IMDb basics...")
basics = pd.read_csv(
    os.path.join(RAW_DIR, "title.basics.tsv.gz"),
    sep="\t",
    low_memory=False
)

print("📥 Loading IMDb ratings...")
ratings = pd.read_csv(
    os.path.join(RAW_DIR, "title.ratings.tsv.gz"),
    sep="\t",
    low_memory=False
)

# Filter movies only
movies = basics[basics["titleType"] == "movie"]

# Merge ratings
df = movies.merge(ratings, on="tconst", how="left")

# Keep 2024 movies
df = df[df["startYear"] == "2024"]

# Save raw CSV
output_path = os.path.join(RAW_DIR, "imdb_2024_raw.csv")
df.to_csv(output_path, index=False)

print(f"✅ RAW DATA CREATED: {output_path}")
print("🎬 Total movies:", len(df))
