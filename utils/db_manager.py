import sqlite3
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database.db"

def init_db():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        online_sync_enabled INTEGER DEFAULT 0
    )
''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS score (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        score_value INTEGER NOT NULL,
        timer REAL NOT NULL,
        date TEXT NOT NULL,
        status_sync INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES user (id)
    )''')
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, sync_enabled):
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user (username, password_hash, online_sync_enabled)
            VALUES (?, ?, ?)
        ''', (username, hash_password(password), 1 if sync_enabled else 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        if conn:
            conn.close()

