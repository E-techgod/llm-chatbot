from typing import Any 
from config import SYSTEM_PROMPT
from storage import save_sessions
from sessions import create_new_session, select_existing_session

SYSTEM_PROMPT

def build_chat_history(all_sessions: dict[str, Any], session_id: str) -> list[dict]:

    saved_messages = all_sessions["sessions"][session_id]["messages"]

    chat_history = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ] + saved_messages

    return chat_history

def show_help() -> None:
    """Display available chat commands
        /help
        /new
        /sessions
        /rename
        /delete
    """

    print("\nAvailable commands:")
    print("/help         Shows available commands")
    print("/new          Creates a new conversations")
    print("/sessions     Shows all conversations and switch in between")
    print("/rename       Renames the current conversation")
    print("/delete       Deletes the current conversation")
    print("exit          Closes chatbot")

def new_session(all_sessions: dict[str, Any]) ->str:
    """Create and switch to a new conversations"""
    session_id= create_new_session(all_sessions)
    save_sessions(all_sessions)

    print("\nStarted a new conversation")

    return session_id

def switch_sessions(all_sessions: dict[str, Any]) -> str | None:
    """Let the user switch to an existing session"""
    
    session_id= select_existing_session(all_sessions)

    if not session_id:
        print("No session selected")
        return None
    
    title= all_sessions["sessions"][session_id].get("title", "Untitle conversation")

    print(f"Switched to {title}")

    return session_id

def rename_session(all_sessions: dict[str, Any], session_id: str, new_title: str | None = None) -> None:
    """Rename current session"""

    if not new_title:
        new_title= input("New title: ").strip()

    if not new_title:
        print("Title cannot be empty")
        return
    
    all_sessions["sessions"][session_id["title"]] = new_title

    print(f"Conversation renamed to {new_title}")

def delete_session(all_sessions: dict[str, Any], session_id: str) -> str | None:
    """
    Delete the current session.

    If sessions remain, ask the user to select another.
    If none remain, create a new session automatically.
    """

    current_title= all_sessions["sessions"][session_id].get("title", "Untitled conversation")

    confirm= input(f"Are you sure you want to delete the current session: {current_title}. Type 'yes' to confirm").strip().lower()

    if confirm != "yes":
        print("Delete cancelled")
        return session_id
    
    del all_sessions["sessions"][session_id]

    print("\nConversation deleted")

    if not all_sessions["sessions"]:
        new_session_id = create_new_session(all_sessions)
        print("No sessions left. Started a new conversation.")
        return new_session_id

    print("Choose another session to continue.")

    return select_existing_session(all_sessions)

 