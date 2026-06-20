# -----------------------------------------------------------------------------
# SmartLead AI – Lead Query Layer
# Functions for filtering and retrieving leads from the SQLite database.
# -----------------------------------------------------------------------------

import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "smartlead.db")


def _connect():
    return sqlite3.connect(DB_PATH)


def get_all_leads() -> pd.DataFrame:
    """Fetch all leads from the database."""
    try:
        conn = _connect()
        df = pd.read_sql_query(
            "SELECT * FROM leads ORDER BY id DESC",
            conn
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def get_leads_by_filters(
    domain: str = "All",
    platform: str = "All",
    category: str = "All",
    username_search: str = "",
) -> pd.DataFrame:
    """Filter leads by domain, platform, category and/or username search."""
    df = get_all_leads()
    if df.empty:
        return df

    if domain != "All":
        df = df[df["domain"] == domain]

    if platform != "All":
        df = df[df["platform"] == platform]

    if category != "All":
        df = df[df["lead_category"] == category]

    if username_search.strip():
        df = df[
            df["username"].str.contains(
                username_search.strip(), case=False, na=False
            )
        ]

    return df


def get_lead_trend() -> pd.DataFrame:
    """Return lead counts grouped by date for trend chart."""
    try:
        conn = _connect()
        df = pd.read_sql_query(
            """
            SELECT date, COUNT(*) as count
            FROM leads
            WHERE date IS NOT NULL AND date != ''
            GROUP BY date
            ORDER BY date ASC
            """,
            conn
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["date", "count"])


def get_top_hot_leads(limit: int = 10) -> pd.DataFrame:
    """Return the top HOT leads by interest score."""
    try:
        conn = _connect()
        df = pd.read_sql_query(
            """
            SELECT domain, platform, username, comment, interest_score, date
            FROM leads
            WHERE lead_category = 'HOT LEAD'
            ORDER BY interest_score DESC
            LIMIT ?
            """,
            conn,
            params=(limit,)
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def get_domain_platform_breakdown() -> pd.DataFrame:
    """Return lead counts grouped by domain and platform."""
    try:
        conn = _connect()
        df = pd.read_sql_query(
            """
            SELECT domain, platform, COUNT(*) as count
            FROM leads
            GROUP BY domain, platform
            ORDER BY count DESC
            """,
            conn
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()