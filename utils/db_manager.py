import sqlite3
import hashlib
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data/database.db"

def init_db():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        player_uuid TEXT,
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

def get_create_uuid(username):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('SELECT player_uuid FROM user WHERE username = ?', (username,))
    row = cursor.fetchone()

    if row and row[0]:
        uid = row[0]
    else:
        uid = str(uuid.uuid4())
        cursor.execute('UPDATE user SET player_uuid = ? WHERE username = ?', (uid, username))
        conn.commit()

    conn.close()
    return uid


def save_score_locally(username, score, timer):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM user WHERE username = ?', (username,))
    user_id = cursor.fetchone()[0]

    from datetime import datetime
    cursor.execute('''
                   INSERT INTO score (user_id, score_value, timer, date, status_sync)
                   VALUES (?, ?, ?, ?, 0)
                   ''', (user_id, score, timer, datetime.now().isoformat()))

    score_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return score_id


def mark_score_as_synced(score_id):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('UPDATE score SET status_sync = 1 WHERE id = ?', (score_id,))
    conn.commit()
    conn.close()


def get_top_10_local():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT u.username, s.score_value, s.timer
                   FROM score s
                            JOIN user u ON s.user_id = u.id
                   ORDER BY s.score_value DESC, s.timer ASC LIMIT 10
                   ''')
    rows = cursor.fetchall()
    conn.close()
    return [{"username": r[0], "score": r[1], "timer": r[2]} for r in rows]



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

def login_user(username, password):
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM user WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            return row[0] == hash_password(password)
        return False
    finally:
        if conn: conn.close()
