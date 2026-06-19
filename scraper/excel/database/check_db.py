import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "smartlead.db"
)

df = pd.read_sql(
    "SELECT * FROM leads",
    conn
)

print(df)

conn.close()