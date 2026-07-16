"""
Tests for storage.load_sessions / save_sessions.

Persistence is where user data lives. The key deployment risk is a corrupt or
unexpected JSON file crashing the app on startup, so the "return a safe default"
branches matter as much as the happy path.

CONVERSATION_HISTORY_FILE is a module-level Path, so we point it at a temp file
per test via monkeypatch instead of touching the real repo file.
"""

import json

import pytest

import storage


@pytest.fixture
def temp_store(tmp_path, monkeypatch):
    path = tmp_path / "conversations_history.json"
    monkeypatch.setattr(storage, "CONVERSATION_HISTORY_FILE", path)
    return path


def test_load_returns_default_when_file_missing(temp_store):
    assert not temp_store.exists()
    assert storage.load_sessions() == {"sessions": {}}


def test_save_then_load_roundtrips(temp_store):
    data = {
        "sessions": {
            "id1": {"title": "t", "messages": [{"role": "user", "content": "hi"}]}
        }
    }
    storage.save_sessions(data)
    assert temp_store.exists()
    assert storage.load_sessions() == data


def test_load_returns_default_on_malformed_json(temp_store):
    temp_store.write_text("{ this is not valid json ", encoding="utf-8")
    assert storage.load_sessions() == {"sessions": {}}


def test_load_returns_default_when_top_level_is_not_dict(temp_store):
    temp_store.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
    assert storage.load_sessions() == {"sessions": {}}


def test_load_returns_default_when_sessions_key_missing(temp_store):
    temp_store.write_text(json.dumps({"something_else": 1}), encoding="utf-8")
    assert storage.load_sessions() == {"sessions": {}}


def test_save_preserves_non_ascii(temp_store):
    # ensure_ascii=False is set; confirm accents/emoji survive a round trip.
    data = {"sessions": {"id": {"title": "Café ñoño 🚀", "messages": []}}}
    storage.save_sessions(data)
    raw = temp_store.read_text(encoding="utf-8")
    assert "Café ñoño 🚀" in raw
    assert storage.load_sessions() == data
