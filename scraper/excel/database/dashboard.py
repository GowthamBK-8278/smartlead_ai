import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "smartlead.db"
)

def get_dashboard_data():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        "SELECT * FROM leads",
        conn
    )

    conn.close()

    return {
        "total_leads": len(df),
        "high_interest": len(
            df[df["sentiment"] == "Highly Interested"]
        ),
        "domains": df["domain"].nunique(),
        "platforms": df["platform"].nunique()
    }