# pip install openai python-dotenv
import os 
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
GOOGLE_GENAI_API_KEY= os.getenv("GOOGLE_GENAI_API_KEY")
ANTHROPIC_API_KEY= os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY= os.getenv("GROQ_API_KEY")

def require_key(name: str) -> str:
    """
    Return the API key `name`, or raise if it isn't set.
 
    Called lazily, right before a provider is used, so the app can start (and
    run on whichever providers ARE configured) even if some keys are missing.
    """
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} was not found. Check your .env")
    return value
