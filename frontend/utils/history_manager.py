# frontend/utils/history_manager.py
import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join("data", "history.json")
MAX_HISTORY = 30  # limit records to prevent file growing too large


def _ensure_file():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_history():
    _ensure_file()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_to_history(sanskrit, hindi, simplified, glossary):
    _ensure_file()
    history = load_history()

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sanskrit": sanskrit,
        "hindi": hindi,
        "simplified": simplified,
        "glossary": glossary,
    }

    history.insert(0, entry)  # newest first

    # limit history size
    history = history[:MAX_HISTORY]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)