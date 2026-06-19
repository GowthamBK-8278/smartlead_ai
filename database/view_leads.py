import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "smartlead.db"
)

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql(
    "SELECT * FROM leads",
    conn
)

print(df)

conn.close()