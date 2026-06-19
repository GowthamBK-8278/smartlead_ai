import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "smartlead.db"
)

def get_all_leads():
    
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        "SELECT * FROM leads",
        conn
    )

    conn.close()

    return df