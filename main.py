"""
The logic for my LLM chatbot.

1. I need to have the API key of a model and insert it into a variable so it is not public knowledge.
    OPENAI_API_KEY or ANTHROPIC_API_KEY
2. Initialize the chosen model.
    ChatOpenAI or ChatAnthropic.
3. Initialize a chat memory in a Python script list: chat_history, given that the LLMs do not have innate memory.
4. Start this list (chat_history) with a system prompt:
    "You are a helpful coding assistant"
5. As the conversation flows, you will append the user's input and the LLM's output to the list.
6. The chat loop, to make the app interactive, wrap the logic around a continuous while loop.
    If the user types exit, the loop will break and exit the chat.
    If the user types a question, wrap it in a Human Message object and append it to the chat_history list.
    Then pass the entire ever-growing list of messages to the chat model using the .invoke() function.
    The model will read the entire history, calculate the next response, and return an AI Message, which the model will
        print to the screen and then append to the chat_history list to preserve the next memory.
"""
from chatbot import get_chatbot_response
from storage import load_sessions, save_sessions
from menu_session import choose_session
from sessions import update_session_title

"You are a helpful AI tutor. Explain things clearly and simply"
"Limit your answers to 3 words maximum or numbers"
"You are a math program. Give me just the correct answers"

SYSTEM_PROMPT = "Limit your answers to 3 words maximum or numbers"

MAX_MEMORY_MESSAGES = 10  # Keep the last 10 non-system messages (users/assistant responses)

def trim_chat_history(chat_history: list[dict], max_memory_limit: int) -> list[dict]:
    """
    Keep the system message and only the most recent user/assistant messages.

    Example:
    - Always keep the system prompt.
    - Keep only the last max_memory_messages from the rest of the conversation.
    """

    system_messages= [
        message for message in chat_history
        if message["role"] == "system"
    ]

    conversation_messages=[
        message for message in chat_history
        if message["role"] != "system" # Includes user and assistant to be keept track of 
    ]

    recent_messages= conversation_messages[-max_memory_limit:]

    return system_messages + recent_messages

def run_chatbot():
    print("Welcome to your Week 9 LLM Chatbot")
    print("Type 'exit' to stop the loop")

    all_sessions= load_sessions()

    session_id= choose_session(all_sessions)

    if session_id is None:
        print("Chatbot closed.")
        return 
    
    save_sessions(all_sessions)

    saved_messages = all_sessions["sessions"][session_id]["messages"]

    chat_history = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ] + saved_messages

    while True:

        user_message= input("You: ").strip()

        if not user_message:
            print("Please type a message\n")
            continue

        if user_message.lower() == "exit":
            print("Chatbot closed.")
            break
        
        update_session_title(
            all_sessions, session_id, user_message
        )

        chat_history.append(
            {
                "role" : "user",
                "content": user_message
            }
        )

        trimmed_chat_history = trim_chat_history(chat_history, MAX_MEMORY_MESSAGES)

        response= get_chatbot_response(trimmed_chat_history)

        if response:
            print(f"AI: {response}")

            chat_history.append(

                {
                    "role": "assistant",
                    "content": response
                }
            )

            history_without_system_prompt = [
                message for message in chat_history
                if message["role"] != "system"
            ]

            all_sessions["sessions"][session_id]["messages"] = history_without_system_prompt
            
            save_sessions(all_sessions)

        else:
            print("\nAI: I'm currently unavailable")


if __name__ == "__main__":
    run_chatbot()
