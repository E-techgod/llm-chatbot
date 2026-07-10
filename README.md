# LLM Chatbot

A simple command-line chatbot built in Python that tries multiple LLM providers in sequence:

1. Anthropic
2. OpenAI
3. Google Gemini

The app reads API keys from a `.env` file and falls back to the next provider if one request fails.

## Files

- `main.py` runs the chatbot loop.
- `chatbot.py` contains the provider-specific response functions.
- `config.py` loads environment variables.
- `requirements.txt` lists Python dependencies currently tracked in the project.

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If needed, also install any provider SDKs your local environment does not already have:

```bash
pip install openai anthropic google-genai python-dotenv
```

## Environment Variables

Create a `.env` file in this folder with:

```env
OPENAI_API_KEY=your_openai_key
GOOGLE_GENAI_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Run

```bash
python main.py
```

Type `exit` to close the chatbot.

## Notes

- The chatbot currently uses a single-turn prompt per provider call rather than persistent conversation memory.
- The code is set up to try Anthropic first, then OpenAI, then Gemini.
