# -----------------------------------------------------------------------------
# SmartLead AI – Dashboard Statistics
# Aggregates KPI metrics from the SQLite database for the dashboard cards.
# -----------------------------------------------------------------------------

import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "smartlead.db")


def _load_df() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    return df


def get_dashboard_data() -> dict:
    """Return all KPI stats for the dashboard header cards."""
    try:
        df = _load_df()
    except Exception:
        return _empty_stats()

    if df.empty:
        return _empty_stats()

    return {
        "total_leads":  len(df),
        "hot_leads":    len(df[df["lead_category"] == "HOT LEAD"]),
        "warm_leads":   len(df[df["lead_category"] == "WARM LEAD"]),
        "cold_leads":   len(df[df["lead_category"] == "COLD LEAD"]),
        "domains":      df["domain"].nunique(),
        "platforms":    df["platform"].nunique(),
    }


def _empty_stats() -> dict:
    return {
        "total_leads": 0,
        "hot_leads":   0,
        "warm_leads":  0,
        "cold_leads":  0,
        "domains":     0,
        "platforms":   0,
    }