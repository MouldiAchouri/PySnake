"""
db_manager.py
-------------
Une seule source de vérité : data/user.json, clé "local_scores".
Pas de SQL. Pas de réseau dans ce fichier.

Format user.json :
{
    "users": {
        "alice": {
            "password_hash": "...",
            "player_uuid": "...",
            "online_sync_enabled": true
        }
    },
    "local_scores": [
        {
            "id": 1,
            "username": "alice",
            "score": 12,
            "timer": 34.5,
            "game_state": 2,
            "date": "2026-05-11T...",
            "synced": false
        }
    ],
    "next_score_id": 2
}
"""

import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "data/user.json"


# ------------------------------------------------------------------ I/O

def init_db():
    if not JSON_PATH.exists():
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        _save({"users": {}, "local_scores": [], "next_score_id": 1})


def _load() -> dict:
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data.setdefault("users", {})
    data.setdefault("local_scores", [])
    data.setdefault("next_score_id", 1)

    # Sécurité : si des entrées sans "id" traînent encore, on leur en attribue un
    max_id = max((s.get("id", 0) for s in data["local_scores"]), default=0)
    counter = max_id + 1
    for s in data["local_scores"]:
        if "id" not in s:
            s["id"] = counter
            counter += 1
        s.setdefault("synced", False)
        s.setdefault("game_state", 2)
        # Normaliser score (au cas où un score_value traînerait encore)
        if "score_value" in s and "score" not in s:
            s["score"] = s.pop("score_value")

    data["next_score_id"] = max(data["next_score_id"], counter)
    return data


def _save(data: dict):
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ------------------------------------------------------------------ auth

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str) -> bool:
    data = _load()
    if username in data["users"]:
        return False
    data["users"][username] = {
        "password_hash": hash_password(password),
        "player_uuid": str(uuid.uuid4()),
    }
    _save(data)
    return True


def login_user(username: str, password: str) -> bool:
    data = _load()
    user = data["users"].get(username)
    return user is not None and user["password_hash"] == hash_password(password)


# ------------------------------------------------------------------ sync preference

def has_configured_sync(username: str) -> bool:
    data = _load()
    user = data["users"].get(username)
    return user is not None and "online_sync_enabled" in user


def set_sync_preference(username: str, enabled: bool):
    data = _load()
    if username in data["users"]:
        data["users"][username]["online_sync_enabled"] = enabled
        _save(data)


def update_user_sync_preference(username: str, enabled: bool):
    set_sync_preference(username, enabled)


def is_sync_enabled(username: str) -> bool:
    data = _load()
    user = data["users"].get(username)
    return bool(user.get("online_sync_enabled", False)) if user else False


# ------------------------------------------------------------------ scores locaux

def save_score_locally(username: str, score: int, timer: float, game_state: int) -> int:
    data = _load()
    score_id = data["next_score_id"]
    data["next_score_id"] += 1
    data["local_scores"].append({
        "id": score_id,
        "username": username,
        "score": score,
        "timer": round(timer, 3),
        "game_state": game_state,
        "date": datetime.now().isoformat(),
        "synced": False
    })
    _save(data)
    return score_id


def mark_score_as_synced(score_id: int):
    data = _load()
    for s in data["local_scores"]:
        if s["id"] == score_id:
            s["synced"] = True
            break
    _save(data)


def get_unsynced_scores(username: str) -> list:
    data = _load()
    return [
        {"id": s["id"], "score": s["score"], "timer": s["timer"]}
        for s in data["local_scores"]
        if s["username"] == username and not s.get("synced", False)
    ]


def get_top_10_local() -> list:
    """
    Top 10 tous joueurs confondus sur ce PC.
    Tri : score DESC, timer ASC.
    """
    data = _load()
    scores = [
        {"username": s["username"], "score": s["score"], "timer": s["timer"]}
        for s in data["local_scores"]
    ]
    scores.sort(key=lambda x: (-x["score"], x["timer"]))
    return scores[:10]


# ------------------------------------------------------------------ réseau (threads uniquement)

def sync_scores_to_server(username: str, server_url: str = "http://localhost:8000") -> bool:
    """NE PAS appeler depuis le thread principal."""
    import requests
    unsynced = get_unsynced_scores(username)
    if not unsynced:
        return True
    all_ok = True
    for entry in unsynced:
        try:
            r = requests.post(
                f"{server_url}/scores",
                json={"username": username, "score_value": entry["score"], "timer": entry["timer"]},
                timeout=5
            )
            if r.status_code == 200 and r.json().get("status") == "success":
                mark_score_as_synced(entry["id"])
            else:
                all_ok = False
        except Exception as e:
            print(f"[db_manager] sync error: {e}")
            all_ok = False
    return all_ok


def fetch_online_leaderboard(server_url: str = "http://localhost:8000", limit: int = 10) -> list:
    """NE PAS appeler depuis le thread principal."""
    import requests
    try:
        r = requests.get(f"{server_url}/leaderboard?limit={limit}", timeout=3)
        if r.status_code == 200:
            return [
                {
                    "username": e.get("username", "?"),
                    "score":    e.get("score", e.get("score_value", 0)),
                    "timer":    e.get("timer", 0.0),
                }
                for e in r.json()
            ]
    except Exception as e:
        print(f"[db_manager] leaderboard fetch error: {e}")
    return []