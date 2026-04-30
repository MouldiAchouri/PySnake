from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()

class ScoreData(BaseModel):
    username: str
    score_value: int
    timer: float

@app.get("/")
def read_root():
    return{"status": "Online"}

@app.post("/scores")
async def post_score(data: ScoreData):
    print(f"score reçu : {data.username} - {data.score_value}")
    return {"message" : "Score synchronisé avec succès", "user": data.username}