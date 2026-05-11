from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.database import get_conn, init_server_db

init_server_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {"status": "Online", "message": "PySnake Server"}


@app.post("/scores")
async def post_score(data: ScoreData):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO global_scores (username, score_value, timer) VALUES (%s, %s, %s) RETURNING id",
            (data.username, data.score_value, data.timer),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return {"status": "success", "id": new_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


@app.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT username, score_value, timer FROM global_scores ORDER BY score_value DESC, timer ASC LIMIT %s",
            (limit,)
        )
        rows = cur.fetchall()
        return [{"username": r[0], "score": r[1], "timer": r[2]} for r in rows]
    except Exception as e:
        return []
    finally:
        conn.close()

@app.get("/scores/{username}")
async def get_user_scores(username: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT score_value, timer FROM global_scores WHERE username = %s ORDER BY score_value DESC",
            (username,)
        )
        rows = cur.fetchall()
        return [{"score": r[0], "timer": r[1]} for r in rows]
    except Exception as e:
        return[]
    finally:
        conn.close()