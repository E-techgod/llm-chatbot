"""
Tests for sessions.py — creating, listing, and selecting conversations.

select_existing_session parses raw user input, so the failure modes (letters,
out-of-range numbers, "0") are the important cases: they must degrade to None
rather than raise.
"""
import uuid

import pytest

import sessions
import commands


def test_create_new_session_adds_and_returns_id(empty_sessions):
    session_id = sessions.create_new_session(empty_sessions)

    assert session_id in empty_sessions["sessions"]
    created = empty_sessions["sessions"][session_id]
    assert created == {"title": "New Conversation", "messages": []}
    # id should be a real uuid4 string
    uuid.UUID(session_id)  # raises if malformed


def test_create_new_session_ids_are_unique(empty_sessions):
    ids = {sessions.create_new_session(empty_sessions) for _ in range(5)}
    assert len(ids) == 5


def test_display_sessions_empty_returns_empty_list(empty_sessions, capsys):
    result = sessions.display_sessions(empty_sessions)
    assert result == []
    assert "No previous conversations." in capsys.readouterr().out


def test_display_sessions_returns_ids_in_order():
    data = {
        "sessions": {
            "a": {"title": "First", "messages": []},
            "b": {"title": "Second", "messages": []},
        }
    }
    assert sessions.display_sessions(data) == ["a", "b"]


def test_select_existing_valid_choice(monkeypatch):
    data = {
        "sessions": {
            "a": {"title": "First", "messages": []},
            "b": {"title": "Second", "messages": []},
        }
    }
    monkeypatch.setattr("builtins.input", lambda _="": "2")
    assert sessions.select_existing_session(data) == "b"


def test_select_existing_non_numeric_returns_none(monkeypatch, capsys):
    data = {"sessions": {"a": {"title": "First", "messages": []}}}
    monkeypatch.setattr("builtins.input", lambda _="": "abc")
    assert sessions.select_existing_session(data) is None
    assert "Invalid conversation selection." in capsys.readouterr().out


def test_select_existing_out_of_range_returns_none(monkeypatch):
    data = {"sessions": {"a": {"title": "First", "messages": []}}}
    monkeypatch.setattr("builtins.input", lambda _="": "99")
    assert sessions.select_existing_session(data) is None


def test_select_existing_zero_returns_none(monkeypatch):
    # index 0 -> selected_index = -1, which must be rejected, not wrap around.
    data = {"sessions": {"a": {"title": "First", "messages": []}}}
    monkeypatch.setattr("builtins.input", lambda _="": "0")
    assert sessions.select_existing_session(data) is None


def test_select_existing_when_empty_returns_none(empty_sessions, monkeypatch):
    # Should short-circuit before ever prompting.
    monkeypatch.setattr("builtins.input", lambda _="": pytest.fail("should not prompt"))
    assert sessions.select_existing_session(empty_sessions) is None


def test_rename_session_updates_session_title(monkeypatch):
    data = {"sessions": {"a": {"title": "Old title", "messages": []}}}
    monkeypatch.setattr("builtins.input", lambda _="": "New title")

    commands.rename_session(data, "a")

    assert data["sessions"]["a"]["title"] == "New title"
