# pip install openai python-dotenv
import os 
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
GOOGLE_GENAI_API_KEY= os.getenv("GOOGLE_GENAI_API_KEY")
ANTHROPIC_API_KEY= os.getenv("ANTHROPIC_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPEN_API_KEY was not found. Check your .env")

if not GOOGLE_GENAI_API_KEY:
    raise ValueError("GOOGLE_GENAI_API_KEY was not found. Check your .env")

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY was not found. Check your .env")