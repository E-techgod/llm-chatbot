# LLM Chatbot

A Python command-line chatbot that feels like a lightweight assistant you can keep talking to from the terminal. It remembers recent context, saves conversations between runs, and can fall back across multiple providers when one is unavailable.

## What it does

The app gives you a simple chat experience with a few helpful behaviors:

- it keeps a system prompt and a rolling memory of recent messages
- it saves conversations so you can return to them later
- it lets you create, switch between, rename, and delete conversation sessions
- it tries multiple providers if one fails or is missing a key

## Provider fallback

The chatbot currently tries providers in this order:

1. Groq
2. Anthropic
3. OpenAI
4. Google Gemini

If one provider fails, it moves on to the next one. The app also loads API keys lazily, so you do not need to provide every key up front.

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in this folder with whichever provider keys you want to use:

```env
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
GOOGLE_GENAI_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
```

You can start the app with just one working key, and the fallback chain will handle the rest.

## Run it

```bash
python3 main.py
```

From the chat prompt you can also use slash commands:

- `/help` to see the available commands
- `/new` to start a fresh conversation
- `/sessions` to switch between saved conversations
- `/rename` to rename the current conversation
- `/delete` to delete the current conversation

Type `exit` to close the chatbot.

## How memory works

The chatbot keeps the system prompt and only the most recent non-system messages in its active context. After each successful reply, it saves the updated conversation so the next session can pick up where it left off.

Memory is isolated per session, not shared across chats. On startup, `load_sessions()` reads the entire `conversations_history.json` file into memory, but only the messages belonging to the session you create or select are loaded into the active chat history sent to the LLM. Every other saved session's messages stay untouched in storage and are never mixed in. Each session keeps its own independent message list, and `save_sessions()` writes the whole sessions file back to disk after every reply.

## Testing

The project includes a pytest suite (71 tests) covering the core logic without making real API calls. You can run it with:

```bash
./venv/bin/python3 -m pytest -q
```