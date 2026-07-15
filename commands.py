from typing import Any 
from config import SYSTEM_PROMPT
from storage import save_sessions
from sessions import create_new_session, select_existing_session

def build_chat_history(all_sessions: dict[str, Any], session_id: str) -> list[dict]:

    saved_messages = all_sessions["sessions"][session_id]["messages"]

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ] + saved_messages

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
    print("/new          Creates a new conversation")
    print("/sessions     Shows all conversations and switch in between")
    print("/rename       Renames the current conversation")
    print("/delete       Deletes the current conversation")
    print("exit          Closes chatbot")

def new_session(all_sessions: dict[str, Any]) ->str:
    """Create and switch to a new conversations"""
    session_id= create_new_session(all_sessions)
    save_sessions(all_sessions)

    print("A new conversation has been created")

    return session_id

def switch_sessions(all_sessions: dict[str, Any]) -> str | None:
    """Let the user switch to an existing session"""
    
    session_id= select_existing_session(all_sessions)

    if not session_id:
        print("No session selected")
        return None
    
    title= all_sessions["sessions"][session_id].get("title", "Untitled conversation")

    print(f"Switched to {title}")

    return session_id

def rename_session(all_sessions: dict[str, Any], session_id: str, new_title: str | None = None) -> None:
    """Rename current session."""

    if not new_title:
        new_title = input("New title: ").strip()

    if not new_title:
        print("Title cannot be empty")
        return

    all_sessions["sessions"][session_id]["title"] = new_title
    save_sessions(all_sessions)

    print(f"\nConversation renamed: '{new_title}'")

def delete_session(all_sessions: dict[str, Any], session_id: str) -> str | None:
    """
    Delete the current session.

    If sessions remain, ask the user to select another.
    If none remain, create a new session automatically.
    """

    current_title= all_sessions["sessions"][session_id].get("title", "Untitled conversation")

    confirm= input(f"Are you sure you want to delete the current session: {current_title}. Type 'yes' to confirm\n").strip().lower()

    if confirm != "yes":
        print("Delete cancelled")
        return session_id
    
    del all_sessions["sessions"][session_id]
    save_sessions(all_sessions)

    print("\nConversation deleted")

    if not all_sessions["sessions"]:
        new_session_id = create_new_session(all_sessions)
        save_sessions(all_sessions)
        print("No sessions left. Started a new conversation.")
        return new_session_id

    print("Choose another session to continue.")

    return select_existing_session(all_sessions)

def handle_commands(command: str, all_sessions: dict[str, Any], current_session_id: str) -> tuple[str, list[dict]]:
    """
    Handles /commands inside the chatbot  
    """

    command_parts= command.split(maxsplit=1) # Split at the first space you find : /help "rest of the prompt", splitting in two parts [0] the command and [1] the message
    command_name= command_parts[0].lower()

    if command_name == "/help":
        show_help()
    
    elif command_name == "/new":
        current_session_id= new_session(all_sessions)
    
    elif command_name == "/sessions":
        selected_session_id= switch_sessions(all_sessions)

        if selected_session_id:
            current_session_id= selected_session_id

    elif command_name == "/rename":
        new_title= command_parts[1] if len(command_parts) > 1 else None
        rename_session(all_sessions, current_session_id, new_title)

    elif command_name == "/delete":
        new_session_id= delete_session(all_sessions, current_session_id)

        if new_session_id:
            current_session_id = new_session_id
    else:
        print("Unknown command. Type /help to see available commands.")

    chat_history= build_chat_history(
        all_sessions,
        current_session_id
    )

    return current_session_id, chat_history

 
