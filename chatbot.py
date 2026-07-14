import os
from google import genai
from openai import OpenAI
from anthropic import Anthropic
from functools import lru_cache
from config import require_key

@lru_cache(maxsize=None)
def get_groq_client() -> OpenAI:
    return OpenAI(
        api_key=require_key("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )
 
@lru_cache(maxsize=None)
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=require_key("OPENAI_API_KEY"))
 
@lru_cache(maxsize=None)
def get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=require_key("ANTHROPIC_API_KEY"))
 
@lru_cache(maxsize=None)
def get_genai_client() -> genai.Client:
    return genai.Client(api_key=require_key("GOOGLE_GENAI_API_KEY"))

def convert_messages_from_anthropic_to_openai_format(chat_history: list[dict]) -> tuple[str, list[dict]]:
    """
    Anthropic expects the system prompt separately from the user/assistant messages.
    """
    system_prompt = ""
    messages = []

    for message in chat_history:
        if message["role"] == "system":
            system_prompt = message["content"]
        else:
            messages.append(message)

    return system_prompt, messages

def convert_messages_from_gemini_to_openai_format(chat_history: list[dict]) -> str:
    """
    Simple Gemini conversion: flatten the conversation into one text prompt.
    This is not perfect, but it works for now.
    """

    lines = []

    for message in chat_history:
        role = message["role"]
        content = message["content"]

        if role == "system":
            lines.append(f"System instructions: {content}")
        elif role == "user":
            lines.append(f"User: {content}")
        elif role == "assistant":
            lines.append(f"Assistant: {content}")

    lines.append("Assistant:")

    return "\n".join(lines)

def get_chatbot_response_groq(chat_history: list[dict]) ->str:

    response=get_groq_client().chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=chat_history,
        temperature=0.7
    )

    return response.choices[0].message.content


def get_chatbot_response_openai(chat_history: list[dict]) -> str:
    """ 
    1. Called the model .chat.create()
        1.1. Select the model
        1.2. messages [{}]
            1.2.1. Select the roles for system and user
        1.3 Select the temperature 
        1.4 Return .choices[0].message.content
    """
    responseOpenAI = get_openai_client().chat.completions.create( 
        model= "gpt-4.1-mini", 
        messages=chat_history,
        temperature=0.7 
    )
    
    return responseOpenAI.choices[0].message.content

def get_chatbot_response_genai(chat_history: list[dict]) -> str:
    """ 
    1. Called the model models.generate_content()
        1.1. Select the model
        1.2. Contents for the user_message
        1.3. config using types.GenerateContentConfig ()
            1.2.1. Select the role for the system
            1.2.2 Select the temperature 
        1.4 Return .text
    """
    prompt= convert_messages_from_gemini_to_openai_format(chat_history)
    
    response= get_genai_client().models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    return response.text

def get_chatbot_response_anthropic(chat_history: list[dict]) -> str:
    """ 
    1. Called the model messages.create()
        1.1. Select the model
        1.2. Select max_tokens
        1.3. Select system role
        1.4. Messages with the role of the user and its content [{}]
        1.5. Select Temperature
        1.6. Return .content[0].text
    """
    system_prompt, messages= convert_messages_from_anthropic_to_openai_format(chat_history)

    response_anthropic = get_anthropic_client().messages.create(

        model="claude-haiku-4-5-20251001", 
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
        temperature=0.7
    )

    return response_anthropic.content[0].text

def get_chatbot_response(chat_history: list[dict]) -> str | None:
    errors = []
 
    providers = [
        ("Groq", get_chatbot_response_groq),
        ("Anthropic", get_chatbot_response_anthropic),
        ("OpenAI", get_chatbot_response_openai),
        ("Gemini", get_chatbot_response_genai),
    ]

    for name, call in providers:
        try:
            # print(f"{name} ")
            return call(chat_history)
        except Exception as e:
            # Missing key, rate limit, network error, etc. -> try the next one.
            errors.append(f"{name} failed: {e}")
 
    print("Error: All models failed or ran out of funds.")
    for error in errors:
        print(error)
 
    return None

