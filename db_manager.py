#!/usr/bin/env python3
"""
db_manager.py
Basic SQLite DB manager to store and retrieve label extraction results.
"""

import sqlite3
from typing import Optional, Dict, Any

DB_PATH = "ocr_labels.db"


def init_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_text TEXT UNIQUE,
        recipient_name TEXT,
        address TEXT
    );
    """)
    conn.commit()
    conn.close()


def get_existing_result(raw_text: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, recipient_name, address FROM labels WHERE raw_text = ?", (raw_text,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    _id, recipient_name, address = row
    # Consider None or empty -> treat as missing to trigger AI
    def valid(s):
        return s is not None and str(s).strip() != ""
    if not valid(recipient_name) and not valid(address):
        return None
    return {"id": _id, "recipient_name": recipient_name, "address": address}


def save_result(raw_text: str, recipient_name: str, address: str, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Insert or update
    c.execute("""
    INSERT INTO labels (raw_text, recipient_name, address)
    VALUES (?, ?, ?)
    ON CONFLICT(raw_text) DO UPDATE SET
      recipient_name=excluded.recipient_name,
      address=excluded.address;
    """, (raw_text, recipient_name, address))
    conn.commit()
    conn.close()
