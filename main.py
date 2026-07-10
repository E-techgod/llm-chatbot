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
from chatbot import get_chatbot_response_genai, get_chatbot_response_openai, get_chatbot_response_anthropic

def run_chatbot():
    print("Welcome to your Week 9 LLM Chatbot")
    print("Type 'exit to stop the loop")

    while True:
        user_message= input("You: ")

        if user_message.lower() == "exit":
            print("Chatbot closed.")
            break
        
        response = None

        # --- STEP 1: Try Anthropic ---
        if response is None:
            try:
                response = get_chatbot_response_anthropic(user_message)
            except Exception as e:
                pass # Silently fail or log, then move to the next check

        # --- STEP 2: Try OpenAI (Fallback 1) ---
        if response is None:
            try:
                response = get_chatbot_response_openai(user_message)
            except Exception as e:
                pass
        
         # --- STEP 2: Try Gemini (Fallback 2) ---
        if response is None:
            try: 
                response= get_chatbot_response_genai(user_message)
            except Exception as e:
                print("Error: All models failed or ran out of funds.")

        if response:
            print(f"\nAI {response}\n")
        else:
            print("\nAI: Sorry, I am currently unavailable.\n")

if __name__ == "__main__":
    run_chatbot()

