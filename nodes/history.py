import json
import os
from datetime import datetime, timezone

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "scrape_history.json")


def _load() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(data: dict):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record(username: str, influencer: dict, trust_score: int):
    history = _load()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trust_score": trust_score,
        "followers": influencer.get("followers", 0),
        "engagement_rate": influencer.get("engagement_rate", 0),
        "posts_count": influencer.get("posts_count", 0),
    }
    history.setdefault(username, []).append(entry)
    _save(history)


def get(username: str) -> list:
    return _load().get(username, [])
