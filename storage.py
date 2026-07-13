import json
from pathlib import Path

CHAT_HISTORY_FILE= Path("chat_history.json")

def load_chat_conversations() -> list[dict]:
    """
    Load chat_history, if doesn't exist return empty []
    """
    if not CHAT_HISTORY_FILE.exists():
        return []
    
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="UTF-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_chat_conversations(chat_history: list[dict]):

    with open(CHAT_HISTORY_FILE, "w", encoding="UTF-8") as f:
        return json.dump(chat_history, f, indent=4)