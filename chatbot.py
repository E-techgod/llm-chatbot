from openai import OpenAI
from anthropic import Anthropic
from google import genai
from google.genai import types

from config import GOOGLE_GENAI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY

clientOpenAI= OpenAI(api_key=OPENAI_API_KEY)
clientGoogleGenAI= genai.Client(api_key=GOOGLE_GENAI_API_KEY)
clientAnthropicAI= Anthropic()

def get_chatbot_response_openai(user_message: str) -> str:
    """ 
    1. Called the model .chat.create()
        1.1. Select the model
        1.2. messages [{}]
            1.2.1. Select the roles for system and user
        1.3 Select the temperature 
        1.4 Return .choices[0].message.content
    """
    responseOpenAI = clientOpenAI.chat.completions.create( 
        model= "gpt-4.1-mini", 
        messages=[  
            {
                "role": "system",
                "content": "You are a helpfull AI tutor. Explain things clearly and simple"
            },
            {
                "role": "user",
                "content": user_message
            }
        ], 
        temperature=0.7 
    )
    
    return responseOpenAI.choices[0].message.content

def get_chatbot_response_genai(user_message: str) -> str:
    """ 
    1. Called the model models.generate_content()
        1.1. Select the model
        1.2. Contents for the user_message
        1.3. config using types.GenerateContentConfig ()
            1.2.1. Select the role for the system
            1.2.2 Select the temperature 
        1.4 Return .text
    """
    
    responseGoogleGenAI= clientGoogleGenAI.models.generate_content(
        model="gemini-3.1-flash-lite",

        contents=user_message, # Uses contents for the user input instead of 'messages' like OpenAI

        config=types.GenerateContentConfig(
            system_instruction= "You are a helpfull AI tutor. Explain things clearly and simple",
            temperature= 0.7
        )
    )

    return responseGoogleGenAI.text

def get_chatbot_response_anthropic(user_message: str) -> str:
    """ 
    1. Called the model messages.create()
        1.1. Select the model
        1.2. Select max_tokens
        1.3. Select system role
        1.4. Messages with the role of the user and its content [{}]
        1.5. Select Temperature
        1.6. Return .content[0].text
    """

    reponseAnthropicAI= clientAnthropicAI.messages.create(

        model="claude-haiku-4-5-20251001", 
        max_tokens=1024,
        system="You are a helpfull AI tutor. Explain things clearly and simple",
        messages=[
            {"role": "user", "content": user_message},
        ],
        temperature=0.7
    )

    return reponseAnthropicAI.content[0].text


