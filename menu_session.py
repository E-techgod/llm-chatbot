from typing import Any
from sessions import create_new_session, select_existing_session


def choose_session(all_sessions: dict[str, Any]) -> str | None:
    """
    Create a new conversation or select an existing one.
    """

    while True:
        print("\n1. Start a new conversation")
        print("2. Continue an existing conversation")
        print("3. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            return create_new_session(all_sessions)

        if choice == "2":
            session_id = select_existing_session(all_sessions)

            if session_id:
                return session_id

        elif choice == "3":
            return None

        else:
            print("Invalid option.")
