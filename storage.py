import json
from pathlib import Path
from typing import Any

CONVERSATION_HISTORY_FILE = Path("conversations_history.json")


def load_sessions() -> dict[str, Any]:
    """
    Load all chatbot sessions from the JSON file.
    """

    if not CONVERSATION_HISTORY_FILE.exists():
        return {"sessions": {}}

    try:
        with CONVERSATION_HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(
            data, dict
        ):  # Data must match the expected dictionary structure; otherwise, return a default template.
            return {"sessions": {}}

        """
        {
            "sessions": {
                "session_1": [...],
                "session_2": [...]
            }
        }
        """
        if (
            "sessions" not in data
        ):  # If the sessions key is missing, return a default template.
            return {"sessions": {}}

        return data

    except (json.JSONDecodeError, OSError):
        return {"sessions": {}}


def save_sessions(data: dict[str, Any]) -> None:
    """
    Save all chatbot sessions to the JSON file.
    """

    with CONVERSATION_HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )
