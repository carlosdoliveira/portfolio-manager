import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "portfolio.db"

def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_date TEXT NOT NULL,
            movement_type TEXT NOT NULL,
            market TEXT NOT NULL,
            institution TEXT NOT NULL,
            ticker TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            value REAL NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE (
                trade_date,
                movement_type,
                market,
                institution,
                ticker,
                quantity,
                price
            )
        )
    """)

    conn.commit()
    conn.close()
