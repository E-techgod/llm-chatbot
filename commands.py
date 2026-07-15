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

 