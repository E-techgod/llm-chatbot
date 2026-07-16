"""
Shared pytest setup.

IMPORTANT: config.py raises ValueError at *import time* if any API key is
missing, and chatbot.py builds SDK clients at import time. So before any test
module imports those, we inject dummy keys into the environment here. This file
is imported by pytest before the test modules, so the env is ready in time.

The dummy keys are never used to make real network calls — every test that
touches a provider mocks it out.
"""

import os
import sys
import pytest
from pathlib import Path

# Make the project modules (chatbot, storage, sessions, ...) importable
# regardless of where pytest is invoked from.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Must be set before config.py / chatbot.py are imported anywhere.
for _key in (
    "OPENAI_API_KEY",
    "GROQ_API_KEY",
    "GOOGLE_GENAI_API_KEY",
    "ANTHROPIC_API_KEY",
):
    os.environ.setdefault(_key, "test-dummy-key")

@pytest.fixture
def sample_history():
    """A small, realistic chat_history list."""
    return [
        {"role": "system", "content": "You are a math program."},
        {"role": "user", "content": "1+1"},
        {"role": "assistant", "content": "2"},
        {"role": "user", "content": "2+2"},
        {"role": "assistant", "content": "4"},
    ]


@pytest.fixture
def empty_sessions():
    return {"sessions": {}}


@pytest.fixture
def one_session():
    return {
        "sessions": {
            "sess-1": {"title": "First chat", "messages": []},
        }
    }
