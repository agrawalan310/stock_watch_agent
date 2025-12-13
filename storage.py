"""Database storage operations for stock_watch_agent."""
import sqlite3
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from models import StockNote
import config


class Storage:
    """Handles SQLite database operations."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize storage with database path."""
        self.db_path = db_path or config.DB_PATH
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_notes (
                    id TEXT PRIMARY KEY,
                    raw_text TEXT NOT NULL,
                    symbol TEXT,
                    action_type TEXT,
                    buy_price REAL,
                    conditions TEXT,
                    user_opinion TEXT,
                    created_at TEXT NOT NULL,
                    last_checked TEXT,
                    active INTEGER NOT NULL DEFAULT 1
                )
            """)
            conn.commit()

    def add_note(self, note: StockNote) -> bool:
        """Add a new stock note to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                data = note.to_dict()
                cursor.execute("""
                    INSERT INTO stock_notes 
                    (id, raw_text, symbol, action_type, buy_price, conditions, 
                     user_opinion, created_at, last_checked, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["id"],
                    data["raw_text"],
                    data["symbol"],
                    data["action_type"],
                    data["buy_price"],
                    data["conditions"],
                    data["user_opinion"],
                    data["created_at"],
                    data["last_checked"],
                    data["active"]
                ))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding note: {e}")
            return False

    def get_active_notes(self) -> List[StockNote]:
        """Get all active stock notes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM stock_notes 
                WHERE active = 1
                ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            return [StockNote.from_dict(dict(row)) for row in rows]

    def update_last_checked(self, note_id: str):
        """Update the last_checked timestamp for a note."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE stock_notes 
                SET last_checked = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), note_id))
            conn.commit()

    def deactivate_note(self, note_id: str):
        """Deactivate a note."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE stock_notes 
                SET active = 0
                WHERE id = ?
            """, (note_id,))
            conn.commit()

