import sqlite3
from pathlib import Path

# Le chemin vers la base de données
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "server_data.db"

def init_server_db():
    """Initialise la base de données serveur"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score_value INTEGER NOT NULL,
            timer REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Base de données serveur initialisée.")

if __name__ == "__main__":
    init_server_db()