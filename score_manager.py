"""
score_manager.py
----------------
Aucun appel réseau dans le thread principal.

offline → top 10 local (JSON uniquement)
online  → fusion local + cache distant, top 10
"""

import threading
import utils.db_manager as db

_remote_cache: list = []
_cache_lock = threading.Lock()


# ------------------------------------------------------------------ écriture

def add_new_score(username: str, score: int, elapsed_time: float, game_state: int):
    score_id = db.save_score_locally(username, score, elapsed_time, game_state)
    if db.is_sync_enabled(username):
        _push_score_async(username, score_id, score, elapsed_time)


def _push_score_async(username: str, score_id: int, score: int, timer: float):
    def _worker():
        import requests
        try:
            r = requests.post(
                "http://localhost:8000/scores",
                json={"username": username, "score_value": score, "timer": timer},
                timeout=5
            )
            if r.status_code == 200 and r.json().get("status") == "success":
                db.mark_score_as_synced(score_id)
        except Exception as e:
            print(f"[score_manager] push error: {e}")
    threading.Thread(target=_worker, daemon=True).start()


def sync_existing_scores(username: str):
    threading.Thread(
        target=db.sync_scores_to_server,
        args=(username,),
        daemon=True
    ).start()


# ------------------------------------------------------------------ lecture

def get_leaderboard(username: str) -> list:
    """Instantané, aucun réseau."""
    local = db.get_top_10_local()

    if not db.is_sync_enabled(username):
        return local

    with _cache_lock:
        remote = list(_remote_cache)

    seen = set()
    merged = []
    for s in local + remote:
        key = (s["username"], s["score"], s["timer"])
        if key not in seen:
            seen.add(key)
            merged.append(s)

    merged.sort(key=lambda x: (-x["score"], x["timer"]))
    return merged[:10]


def refresh_online_cache(username: str):
    """Rafraîchit le cache distant en arrière-plan après un game over."""
    if not db.is_sync_enabled(username):
        return

    def _worker():
        remote = db.fetch_online_leaderboard()
        with _cache_lock:
            _remote_cache.clear()
            _remote_cache.extend(remote)

    threading.Thread(target=_worker, daemon=True).start()