"""
Main chatbot loop and memory window orchestration.

This file is no longer a single-file chatbot implementation. Its job in the
current project is to coordinate the main runtime flow across the session,
command, storage, and provider modules:

1. Load saved conversations from `conversations_history.json`.
2. Ask the user to start a new conversation or continue an existing one.
3. Rebuild `chat_history` by prepending the shared system prompt to the saved
   messages of the selected session.
4. Run the interactive loop:
   - `exit` closes the chatbot.
   - `/commands` are delegated to `handle_commands()`, which may create,
     switch, rename, or delete sessions and then rebuild the chat history.
   - Normal user input is appended to the current session history.
5. Apply `trim_chat_history()` before calling the model so the app keeps the
   system prompt plus only the most recent non-system messages in memory.
6. Delegate response generation to `get_chatbot_response()`, which tries the
   provider fallback chain implemented in `chatbot.py`.
7. On success, append the assistant reply, auto-title a new session from the
   first user message, and persist the conversation back to JSON.
8. On provider failure, remove the dangling user turn so stored history stays
   consistent.
"""
from dotenv import load_dotenv
from commands import handle_commands
from menu_session import choose_session
from chatbot import get_chatbot_response
from sessions import update_session_title
from storage import load_sessions, save_sessions
from config import SYSTEM_PROMPT, MAX_MEMORY_MESSAGES


def trim_chat_history(chat_history: list[dict], max_memory_limit: int) -> list[dict]:
    """
    Keep the system message and only the most recent user/assistant messages.

    Example:
    - Always keep the system prompt.
    - Keep only the last max_memory_messages from the rest of the conversation.
    """

    system_messages = [
        message for message in chat_history if message["role"] == "system"
    ]

    conversation_messages = [
        message
        for message in chat_history
        if message["role"]
        != "system"  # Includes user and assistant to be kept track of
    ]

    recent_messages = conversation_messages[-max_memory_limit:]

    return system_messages + recent_messages


def run_chatbot():
    load_dotenv()
    print("Welcome to the Multi-Model Chatbot Dashboard!")
    print("Type 'exit' to stop the loop")
    print(
        "To see the commands available please start or continue a chat and run '/help'"
    )

    all_sessions = load_sessions()

    session_id = choose_session(all_sessions)

    if session_id is None:
        print("Chatbot closed.")
        return

    save_sessions(all_sessions)

    saved_messages = all_sessions["sessions"][session_id]["messages"]

    chat_history = [{"role": "system", "content": SYSTEM_PROMPT}] + saved_messages

    while True:

        user_message = input("You: ").strip()

        if not user_message:
            print("Please type a message\n")
            continue

        if user_message.lower() == "exit":
            print("Chatbot closed.")
            break

        if user_message.startswith("/"):
            (
                session_id,
                chat_history,
            ) = handle_commands(
                command=user_message,
                all_sessions=all_sessions,
                current_session_id=session_id,
            )
            continue

        chat_history.append({"role": "user", "content": user_message})

        trimmed_chat_history = trim_chat_history(chat_history, MAX_MEMORY_MESSAGES)

        response = get_chatbot_response(trimmed_chat_history)

        if response:
            print(f"AI: {response}\n")

            update_session_title(all_sessions, session_id, user_message)

            chat_history.append({"role": "assistant", "content": response})

            history_without_system_prompt = [
                message for message in chat_history if message["role"] != "system"
            ]

            all_sessions["sessions"][session_id][
                "messages"
            ] = history_without_system_prompt

            save_sessions(all_sessions)

        else:
            print("\nAI: I'm currently unavailable")
            chat_history.pop()  # no reply -> drop the dangling user turn so history stays alternating


if __name__ == "__main__":
    run_chatbot()
