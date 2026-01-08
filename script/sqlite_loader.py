import sqlite3
import pandas as pd
import os

CSV_PATH = "data/processed/imdb_2024_cleaned.csv"
DB_PATH = "imdb_2024.db"

print("📥 Loading cleaned CSV...")
df = pd.read_csv(CSV_PATH)
print("Rows loaded:", len(df))

print("🗄 Connecting to SQLite...")
conn = sqlite3.connect(DB_PATH)

df.to_sql("movies", conn, if_exists="replace", index=False)

conn.close()

print("✅ SQLite database created:", DB_PATH)
