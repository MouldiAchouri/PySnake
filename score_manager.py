import json
import os
from datetime import datetime

DATA_PATH = "data/scores.json"

def ensure_data_exists():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump([], f)

def load_scores():
    ensure_data_exists()
    try:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def add_new_score(username, score, timer, game_state):

    scores = load_scores()

    new_entry = {
        "username": username,
        "score": score,
        "timer": timer,
        "game_state": game_state,
        "date": datetime.now().isoformat()
    }

    scores.append(new_entry)

    scores.sort(key=lambda x: (-x["score"], x["timer"]))

    top_10 = scores[:10]

    with open(DATA_PATH, "w") as f:
        json.dump(top_10, f, indent=4)

    return top_10