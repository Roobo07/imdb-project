import pandas as pd
import os

RAW_PATH = "data/raw/imdb_2024_raw.csv"
OUT_PATH = "data/processed/imdb_2024_cleaned.csv"

os.makedirs("data/processed", exist_ok=True)

df = pd.read_csv(RAW_PATH)

df.replace("\\N", pd.NA, inplace=True)

df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["votes"] = pd.to_numeric(df["votes"], errors="coerce")
df["duration_minutes"] = pd.to_numeric(df["duration_minutes"], errors="coerce")

df = df.dropna(subset=["movie_name", "genre"])

df.to_csv(OUT_PATH, index=False)

print("✅ Cleaned data saved:", OUT_PATH)
print("Rows:", len(df))
