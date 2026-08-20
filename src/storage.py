"""
storage.py
Local JSON history log, same interface/pattern as Module 1's storage.py.
No name/ID stored — just item_id, text, score, timestamp.
Adds get_exposure_count() to support the "re-reading" tracking from the notes:
each time a word/phrase is attempted, the count for that item_id goes up,
so the app can decide when to bring it back for repeat practice.
"""

import json
import os
from datetime import datetime, timezone

DEFAULT_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "module2_history.json")


def _load(log_path: str = DEFAULT_LOG_PATH):
    if not os.path.exists(log_path):
        return []
    with open(log_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(history, log_path: str = DEFAULT_LOG_PATH):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def log_attempt(item_id: str, item_type: str, target_text: str, transcribed_text: str,
                 score: int, log_path: str = DEFAULT_LOG_PATH):
    """Append one attempt record to the local history file."""
    history = _load(log_path)
    history.append({
        "item_id": item_id,
        "type": item_type,          # "word" or "phrase"
        "target_text": target_text,
        "transcribed_text": transcribed_text,
        "score": score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save(history, log_path)


def get_exposure_count(item_id: str, log_path: str = DEFAULT_LOG_PATH) -> int:
    """How many times this word/phrase has been attempted before (for re-reading logic)."""
    history = _load(log_path)
    return sum(1 for entry in history if entry["item_id"] == item_id)


def get_history(log_path: str = DEFAULT_LOG_PATH):
    """Return full attempt history (for the feasibility report / volunteer testing logs)."""
    return _load(log_path)
