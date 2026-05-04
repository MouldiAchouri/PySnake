from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from backend.database import DB_PATH, init_server_db

init_server_db()

app = FastAPI()

class ScoreData(BaseModel):
    username: str
    score_value: int
    timer: float

@app.get("/")
def read_root():
    return {"status": "Online"}

@app.post("/scores")
async def post_score(data: ScoreData):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO global_scores (username, score_value, timer) VALUES (?, ?, ?)",
            (data.username, data.score_value, data.timer),
        )
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        print(f"Erreur DB: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@app.get("/leaderboard")
async def get_leaderboard():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username, score_value, timer FROM global_scores ORDER BY score_value DESC LIMIT 10")
        rows = cursor.fetchall()
        return [{"username": r[0], "score": r[1], "timer": r[2]} for r in rows]
    finally:
        conn.close()

@app.get("/scores/{username}")
async def get_user_scores(username: str):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT score_value, timer, date FROM global_scores WHERE username = ?"
                            "ORDER BY score_value DESC", (username,))

        rows = cursor.fetchall()
        return [{"score_value": r[0], "timer": r[1], "date": r[2]} for r in rows]
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()