# Tests

71 unit / integration tests covering the logic that has to be correct before
this ships. No test makes a real network call — every provider is mocked.

## Run

```bash
pip install pytest openai anthropic google-genai python-dotenv
python -m pytest            # from the repo root
python -m pytest -v         # verbose, one line per test
```

You do **not** need real API keys. `tests/conftest.py` injects dummy keys into
the environment before importing `config.py` (which otherwise raises on a
missing key) and `chatbot.py` (which builds SDK clients at import time).
You **do** need the SDK dependencies above installed, because some test modules
import `chatbot.py` during collection.

## What's covered

| File | Under test | Why it matters |
|------|-----------|----------------|
| `test_trim_history.py` | `main.trim_chat_history` | Memory window: keeps system prompt, trims to last N. Wrong = wrong persona or unbounded API cost. |
| `test_storage.py` | `storage.load/save_sessions` | Persistence + corrupt-file recovery so a bad JSON file can't crash startup. |
| `test_sessions.py` | `sessions.*` | Session creation and the input-parsing failure modes (letters, out-of-range, `0`). |
| `test_menu_session.py` | `menu_session.choose_session` | Menu loop returns/reprompts correctly. |
| `test_chatbot_convert.py` | Anthropic/Gemini prompt conversion | Per-request transforms that can silently drop the system prompt. |
| `test_chatbot_fallback.py` | `chatbot.get_chatbot_response` | Provider fallback order + short-circuit + all-fail → `None`. |
| `test_commands.py` | `commands.*` plus slash-command integration in `main.run_chatbot` | `/help`, `/new`, `/sessions`, `/rename`, `/delete`, unknown-command handling, history rebuilding, and the guarantee that slash commands bypass model calls. |
| `test_run_chatbot_loop.py` | `main.run_chatbot` | Loop wiring: turns persisted, blank rejected, `exit` stops. |

## Known findings surfaced by the suite

- `trim_chat_history(history, 0)` returns the **entire** history, not none,
  because `list[-0:] == list[0:]`. Harmless today (limit is hard-coded to 10)
  but a latent trap if that ever becomes configurable. See
  `test_limit_of_zero_keeps_ENTIRE_history_a_known_footgun`.

## Not covered (deliberately out of scope for unit tests)

- Real API responses from Groq/OpenAI/Anthropic/Gemini (needs live keys /
  contract tests).
- `config.py` import-time key validation (see notes in the review).
