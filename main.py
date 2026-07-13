"""
The logic for my LLM Chatbot

1. I need to have the API key of a model and insert that into a variable, so its not public knowledge 
    OPENAI_API_KEY or ANTHROPIC_API_KEY 
2. Initialize the chosen model
    ChatOpenAI or ChatAnhropic
3. Initialize a chat memory in a python script list: chat_history given that the LLMs do not have innate memory 
4. Start this list (chat_history) with a System Prompt:
    "You are a helpfull coding assistant"
5. As the conversation flows you will append the user's input and the LLM's output to the list
6. The Chat loop, to make the app interactive wrapp the logic arround a continuous while loop.
    If the users type exit, the loop will break exiting the chat
    If the user type a question, wrap it around a Human Message Object and append it to the chat_history list
    Then pass the entire ever-growing list of messages to the chat model using the .invoke() function 
    The model will read the entire history, calculate the next response and return an AI Message, which the model will 
        print to the screen and then append it to the chat_history list to preserve the next memory 
"""
from chatbot import get_chatbot_response
from storage import load_sessions, save_sessions
from menu_session import choose_session

"You are a helpful AI tutor. Explain things clearly and simply"
"Limit your answers to 3 words maximum or numbers"

SYSTEM_PROMPT= "You are a helpful AI tutor. Explain things clearly and simply"

MAX_MEMORY_MESSAGES= 10 # Keep the last 10 non-system messages (Users/Assistant responses)

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

    chat_history= [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ] + all_sessions

    while True:
        user_message= input("You: ").strip()

        if not user_message:
            print("Please type a message\n")
            continue

        if user_message.lower() == "exit":
            print("Chatbot closed.")
            break
        
        chat_history.append(
            {
                "role" : "user",
                "content": user_message
            }
        )

        trimmed_chat_history = trim_chat_history(chat_history, MAX_MEMORY_MESSAGES)

        response= get_chatbot_response(trimmed_chat_history)

        if response:
            print(f"\nAI: {response}\n")

            chat_history.append(

                {
                    "role": "assistant",
                    "content": response
                }
            )

            history_without_system_promt=[
                message for message in chat_history
                if message["role"] != "system"
            ]

            save_sessions(history_without_system_promt)

        else:
            print("\nAI: I'm currently unavailable")


if __name__ == "__main__":
    run_chatbot()
