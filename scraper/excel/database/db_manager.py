import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "smartlead.db"
)

def create_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        domain TEXT,
        platform TEXT,
        title TEXT,
        username TEXT,
        comment TEXT,
        interest_score INTEGER,
        sentiment TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_leads(df, domain):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    for _, row in df.iterrows():

        cursor.execute("""
        INSERT INTO leads(
            domain,
            platform,
            title,
            username,
            comment,
            interest_score,
            sentiment
        )
        VALUES(?,?,?,?,?,?,?)
        """, (

            domain,
            row["Platform"],
            row["Title"],
            row["Username"],
            row["Comment"],
            row["Interest Score"],
            row["Sentiment"]
        ))

    conn.commit()
    conn.close()