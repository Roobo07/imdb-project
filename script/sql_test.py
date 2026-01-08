import sqlite3
import pandas as pd

conn = sqlite3.connect("imdb_2024.db")

df = pd.read_sql("SELECT * FROM movies LIMIT 5", conn)
print(df)

conn.close()
