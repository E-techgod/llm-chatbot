import uuid
from typing import Any

def create_new_session(all_sessions: dict[str, Any]) -> str:
    """
    Create a new session and return its new ID.
    """
    session_id= str(uuid.uuid4())

    all_sessions["sessions"][session_id]={
        "title": "New Conversation",
        "messages": []
    }

    return session_id

def display_sessions(all_sessions: dict[str, Any]) -> list[str]:
    """
    Display saved sessions and return their IDs in display order.
    """

    session_ids= list(all_sessions["sessions"].keys())

    if not session_ids:
        print("No previous conversations.")
        return []
    
    print("\nSaved conversations.")

    for index, session_id in enumerate(session_ids, start=1):
        session= all_sessions["sessions"][session_id]
        title= session.get("title", "New Conversation")
        message_count= len(session.get("messages", []))

        print(f"{index}. {title}: ({message_count} messages)")

    return session_ids


def select_existing_session(all_sessions: dict[str, Any]) -> str | None:
    """
    Let the user select one saved conversation.
    """

    session_ids = display_sessions(all_sessions)

    if not session_ids:
        return None

    selection = input("Select a conversation: ").strip()

    try:
        selected_index = int(selection) - 1

        if selected_index < 0:
            raise ValueError

        return session_ids[selected_index]

    except (ValueError, IndexError):
        print("Invalid conversation selection.")
        return None
    
def update_session_title(all_sessions: dict[str, Any], session_id: str, user_message: str) -> None:
    """
    Give a new conversation a basic title using the first user message.
    """

    current_title= all_sessions["sessions"][session_id]["title"]

    if current_title != "New Conversation":
        return
    
    title= user_message[:40]

    if len(user_message) > 40:
        title += "..."

    all_sessions["sessions"][session_id]["title"]= title
    