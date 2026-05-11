from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from backend.database import DB_PATH, init_server_db

# Initialisation de la base de données
init_server_db()

app = FastAPI()

# Middleware CORS pour permettre les requêtes depuis le jeu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En développement, à restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScoreData(BaseModel):
    username: str
    score_value: int
    timer: float

@app.get("/")
def read_root():
    return {"status": "Online", "message": "Snake Game Server"}

@app.post("/scores")
async def post_score(data: ScoreData):
    """Enregistre un score dans la base de données globale"""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO global_scores (username, score_value, timer) VALUES (?, ?, ?)",
            (data.username, data.score_value, data.timer),
        )
        conn.commit()
        return {"status": "success", "id": cursor.lastrowid}
    except Exception as e:
        print(f"Erreur DB: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@app.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Récupère le top 10 des scores globaux"""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, score_value, timer FROM global_scores ORDER BY score_value DESC, timer ASC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        return [{"username": r[0], "score": r[1], "timer": r[2]} for r in rows]
    except Exception as e:
        print(f"Erreur lecture: {e}")
        return []
    finally:
        conn.close()