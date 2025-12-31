
import sqlite3

DB_PATH = "data.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT,
            asset_type TEXT,
            quantity REAL,
            price REAL,
            date TEXT
        )
        """
    )
    conn.commit()
    conn.close()
