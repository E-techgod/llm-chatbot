import json
from pathlib import Path
from typing import Any

CONVERSATION_HISTORY_FILE = Path("conversations_history.json")
CORRUPT_HISTORY_FILE = Path("conversations_history.corrupt.json")


def _default_sessions() -> dict[str, Any]:
    return {"sessions": {}}


def _session_messages_are_valid(messages: Any) -> bool:
    if not isinstance(messages, list):
        return False

    for message in messages:
        if not isinstance(message, dict):
            return False

        if set(message.keys()) != {"role", "content"}:
            return False

        if not isinstance(message["role"], str) or not isinstance(
            message["content"], str
        ):
            return False

    return True


def _sessions_are_valid(sessions: Any) -> bool:
    if not isinstance(sessions, dict):
        return False

    for session_id, session_data in sessions.items():
        if not isinstance(session_id, str):
            return False

        if not isinstance(session_data, dict):
            return False

        if "title" not in session_data or "messages" not in session_data:
            return False

        if not isinstance(session_data["title"], str):
            return False

        if not _session_messages_are_valid(session_data["messages"]):
            return False

    return True


def _write_corrupt_history_backup() -> None:
    backup_path = CONVERSATION_HISTORY_FILE.with_name(CORRUPT_HISTORY_FILE.name)
    backup_path.write_text(CONVERSATION_HISTORY_FILE.read_text(encoding="utf-8"))
    print("Warning: history file is corrupted.")
    print(f"Backup created at {backup_path.name}.")
    print("Starting with empty history.")


def load_sessions() -> dict[str, Any]:
    """
    Load all chatbot sessions from the JSON file.
    """

    if not CONVERSATION_HISTORY_FILE.exists():
        return _default_sessions()

    try:
        with CONVERSATION_HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(
            data, dict
        ):  # Data must match the expected dictionary structure; otherwise, return a default template.
            return _default_sessions()

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
            return _default_sessions()

        if not _sessions_are_valid(data["sessions"]):
            return _default_sessions()

        return data

    except json.JSONDecodeError:
        _write_corrupt_history_backup()
        return _default_sessions()
    except OSError:
        return _default_sessions()


def save_sessions(data: dict[str, Any]) -> None:
    """
    Save all chatbot sessions to the JSON file.
    """

    serialized = json.dumps(
        data,
        indent=4,
        ensure_ascii=False,
    )

    temp_path = CONVERSATION_HISTORY_FILE.with_name(
        f"{CONVERSATION_HISTORY_FILE.name}.tmp"
    )
    temp_path.write_text(serialized, encoding="utf-8")
    temp_path.replace(CONVERSATION_HISTORY_FILE)
