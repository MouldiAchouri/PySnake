import json
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "data/user.json"

def init_db():
    if not JSON_PATH.exists():
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        _save_all({"users": {}, "scores": []})

def _load_all():
    try:
        with open(JSON_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": {}, "scores": []}

def _save_all(data):
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    data = _load_all()
    if username in data["users"]:
        return False
    data["users"][username] = {"password_hash": hash_password(password)}
    _save_all(data)
    return True

def login_user(username, password):
    data = _load_all()
    user = data["users"].get(username)
    if user:
        return user["password_hash"] == hash_password(password)
    return False

def has_configured_sync(username):
    data = _load_all()
    user = data["users"].get(username)
    if user is None:
        return False
    return "online_sync_enabled" in user

def set_sync_preference(username, share_online: bool):
    data = _load_all()
    if username in data["users"]:
        data["users"][username]["online_sync_enabled"] = share_online
        _save_all(data)

def save_score(username, score, timer):
    data = _load_all()
    data["scores"].append({
        "username": username,
        "score": score,
        "timer": round(timer, 2),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    _save_all(data)

def get_top_10():
    data = _load_all()
    sorted_scores = sorted(data["scores"], key=lambda x: (-x["score"], x["timer"]))
    return sorted_scores[:10]

def is_sync_enabled(username):
    data = _load_all()
    user = data["users"].get(username)
    return user.get("online_sync_enabled", False) if user else False