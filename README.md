# LLM Chatbot

A Python command-line chatbot with short-term memory, local chat persistence, and multi-provider fallback across Groq, Anthropic, OpenAI, and Google Gemini.

## Current Model Order

The app tries providers in this order:

1. Groq: `llama-3.1-8b-instant`
2. Anthropic: `claude-haiku-4-5-20251001`
3. OpenAI: `gpt-4.1-mini`
4. Google Gemini: `gemini-3.1-flash-lite`

If one provider fails, the chatbot automatically tries the next one.

## Features

- CLI chat loop in `main.py`
- System prompt applied to every conversation
- Short-term memory using the most recent conversation messages
- Saved chat history in `chat_history.json`
- Automatic fallback across multiple LLM providers

## Project Files

- `main.py`: runs the chatbot loop and manages conversation history
- `chatbot.py`: provider clients, message conversion helpers, and fallback logic
- `storage.py`: loads and saves `chat_history.json`
- `config.py`: loads API keys from `.env`
- `requirements.txt`: Python dependencies

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in this folder with:

```env
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
GOOGLE_GENAI_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
```

All four keys are currently required by `config.py`.

## Run

```bash
python main.py
```

Type `exit` to close the chatbot.

## How Memory Works

- The chatbot loads previous messages from `chat_history.json`
- It always keeps the system prompt
- It sends only the most recent `4` non-system messages to the model
- After each successful reply, it saves the updated conversation back to disk

## Notes

- Gemini currently receives a flattened text prompt converted from the shared chat history format.
- Anthropic receives the system prompt separately from the conversation messages.
