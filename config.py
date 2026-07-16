# pip install openai python-dotenv
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = "You are a helpful AI tutor. " "Explain things clearly and simply."

MAX_MEMORY_MESSAGES = (
    10  # Keep the last 10 non-system messages (users/assistant responses)
)


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
