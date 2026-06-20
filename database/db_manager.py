# -----------------------------------------------------------------------------
# SmartLead AI – Database Manager
# SQLite schema with full spec fields + safe migration for existing DBs.
# -----------------------------------------------------------------------------

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "smartlead.db")


def _get_connection():
    return sqlite3.connect(DB_PATH)


def create_database():
    """Create the leads table if it does not exist, and migrate if needed."""
    conn = _get_connection()
    cursor = conn.cursor()

    # ── Create table with full schema ────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            domain         TEXT,
            platform       TEXT,
            title          TEXT,
            username       TEXT,
            comment        TEXT,
            interest_score INTEGER,
            lead_category  TEXT,
            sentiment      TEXT,
            date           TEXT
        )
    """)

    # ── Safe migration: add columns if they don't exist (for old DBs) ────────
    existing_columns = {
        row[1] for row in cursor.execute("PRAGMA table_info(leads)")
    }

    migrations = {
        "lead_category": "ALTER TABLE leads ADD COLUMN lead_category TEXT",
        "date":          "ALTER TABLE leads ADD COLUMN date TEXT",
        "username":      "ALTER TABLE leads ADD COLUMN username TEXT",
    }

    for col, sql in migrations.items():
        if col not in existing_columns:
            cursor.execute(sql)

    conn.commit()
    conn.close()


def save_leads(df, domain: str):
    """Persist a leads DataFrame to the database."""
    conn = _get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO leads (
                domain, platform, title, username, comment,
                interest_score, lead_category, sentiment, date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            domain,
            row.get("Platform", ""),
            row.get("Title", ""),
            row.get("Username", ""),
            row.get("Comment", ""),
            row.get("Interest Score", 0),
            row.get("Lead Category", ""),
            row.get("Sentiment", ""),
            row.get("Date", ""),
        ))

    conn.commit()
    conn.close()


def clear_all_leads():
    """Delete all rows from leads table (for reset functionality)."""
    conn = _get_connection()
    conn.execute("DELETE FROM leads")
    conn.commit()
    conn.close()


# ── New Schema for Real Scraped Leads (leads_real.db) ────────────────────────
DB_REAL_PATH = os.path.join(os.path.dirname(__file__), "leads_real.db")

def _get_real_connection():
    return sqlite3.connect(DB_REAL_PATH)


def create_real_database():
    """Create the leads_real table in the separate leads_real.db database."""
    conn = _get_real_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_real (
            id                     INTEGER PRIMARY KEY AUTOINCREMENT,
            domain                 TEXT,
            platform               TEXT,
            source_account         TEXT,
            post_url               TEXT,
            commenter_username     TEXT,
            commenter_profile_url  TEXT,
            comment_text           TEXT,
            interest_score         INTEGER,
            dm_sent                INTEGER DEFAULT 0,
            dm_sent_at             TEXT,
            scraped_at             TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_real_lead(domain: str, platform: str, source_account: str, post_url: str,
                   commenter_username: str, commenter_profile_url: str,
                   comment_text: str, interest_score: int) -> bool:
    """
    Save a single real lead to the database. Avoids duplicates based on
    commenter_username, post_url and comment_text.
    Returns True if inserted, False if it was a duplicate.
    """
    conn = _get_real_connection()
    cursor = conn.cursor()
    
    # Check duplicate
    cursor.execute("""
        SELECT id FROM leads_real 
        WHERE commenter_username = ? AND post_url = ? AND comment_text = ?
    """, (commenter_username, post_url, comment_text))
    
    if cursor.fetchone():
        conn.close()
        return False
        
    cursor.execute("""
        INSERT INTO leads_real (
            domain, platform, source_account, post_url,
            commenter_username, commenter_profile_url, comment_text,
            interest_score, dm_sent, scraped_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (
        domain,
        platform,
        source_account,
        post_url,
        commenter_username,
        commenter_profile_url,
        comment_text,
        interest_score,
        datetime_now_str()
    ))
    
    conn.commit()
    conn.close()
    return True


def get_all_real_leads(domain: str = None, platform: str = None, dm_sent: int = None):
    """
    Retrieve all real scraped leads from leads_real.db.
    Can be filtered by domain, platform, and dm_sent status.
    """
    conn = _get_real_connection()
    # Return as list of dicts for easy pandas DataFrame conversion
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM leads_real WHERE 1=1"
    params = []
    
    if domain:
        query += " AND domain = ?"
        params.append(domain)
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if dm_sent is not None:
        query += " AND dm_sent = ?"
        params.append(dm_sent)
        
    query += " ORDER BY id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def mark_dm_sent_real_lead(lead_id: int):
    """Mark a real lead as DM sent in database."""
    conn = _get_real_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE leads_real 
        SET dm_sent = 1, dm_sent_at = ?
        WHERE id = ?
    """, (datetime_now_str(), lead_id))
    conn.commit()
    conn.close()


def clear_all_real_leads():
    """Clear all real leads from database."""
    conn = _get_real_connection()
    conn.execute("DELETE FROM leads_real")
    conn.commit()
    conn.close()


def datetime_now_str() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")