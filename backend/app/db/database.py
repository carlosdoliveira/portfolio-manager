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

            asset_class TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            product_name TEXT NOT NULL,
            ticker TEXT,

            movement_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            value REAL NOT NULL,

            trade_date TEXT NOT NULL,
            created_at TEXT NOT NULL,

            source TEXT NOT NULL,

            market TEXT,
            institution TEXT,

            UNIQUE (
                trade_date,
                movement_type,
                market,
                institution,
                ticker,
                quantity,
                price,
                source
            )
        )
    """)

    conn.commit()
    conn.close()
