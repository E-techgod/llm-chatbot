"""Tests for slash-command behavior and command integration.

Place this file at:

    tests/test_commands.py

Run with:

    python -m pytest tests/test_commands.py -q
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from unittest.mock import Mock

import pytest

import commands
import main
from config import SYSTEM_PROMPT


@pytest.fixture
def sessions_data() -> dict[str, Any]:
    """Return deterministic in-memory sessions for every test."""
    return {
        "sessions": {
            "session-1": {
                "title": "First conversation",
                "messages": [
                    {"role": "user", "content": "first question"},
                    {"role": "assistant", "content": "first answer"},
                ],
            },
            "session-2": {
                "title": "Second conversation",
                "messages": [
                    {"role": "user", "content": "second question"},
                    {"role": "assistant", "content": "second answer"},
                ],
            },
        }
    }


def expected_history(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}] + messages


def test_show_help(capsys: pytest.CaptureFixture[str]) -> None:
    commands.show_help()

    output = capsys.readouterr().out

    assert "Available commands:" in output
    assert "/help" in output
    assert "/new" in output
    assert "/sessions" in output
    assert "/rename" in output
    assert "/delete" in output
    assert "exit" in output


def test_new_session_creates_and_switches(
    monkeypatch: pytest.MonkeyPatch,
    sessions_data: dict[str, Any],
) -> None:
    save_mock = Mock()
    monkeypatch.setattr(commands, "save_sessions", save_mock)
    monkeypatch.setattr(
        commands,
        "create_new_session",
        lambda data: data["sessions"].setdefault(
            "session-3",
            {"title": "New Conversation", "messages": []},
        )
        and "session-3",
    )

    session_id, chat_history = commands.handle_commands(
        "/new",
        sessions_data,
        "session-1",
    )

    assert session_id == "session-3"
    assert sessions_data["sessions"]["session-3"] == {
        "title": "New Conversation",
        "messages": [],
    }
    assert chat_history == expected_history([])
    save_mock.assert_called_once_with(sessions_data)


def test_sessions_switches_context(
    monkeypatch: pytest.MonkeyPatch,
    sessions_data: dict[str, Any],
) -> None:
    monkeypatch.setattr(
        commands,
        "select_existing_session",
        lambda _: "session-2",
    )

    session_id, chat_history = commands.handle_commands(
        "/sessions",
        sessions_data,
        "session-1",
    )

    assert session_id == "session-2"
    assert chat_history == expected_history(
        sessions_data["sessions"]["session-2"]["messages"]
    )


def test_sessions_cancel_keeps_current_session(
    monkeypatch: pytest.MonkeyPatch,
    sessions_data: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(commands, "select_existing_session", lambda _: None)

    session_id, chat_history = commands.handle_commands(
        "/sessions",
        sessions_data,
        "session-1",
    )

    assert session_id == "session-1"
    assert chat_history == expected_history(
        sessions_data["sessions"]["session-1"]["messages"]
    )
    assert "No session selected" in capsys.readouterr().out


def test_rename_with_inline_title(
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_mock = Mock(side_effect=AssertionError("input() should not be called"))
    monkeypatch.setattr("builtins.input", input_mock)

    session_id, chat_history = commands.handle_commands(
        "/rename Project planning",
        sessions_data,
        "session-1",
    )

    assert session_id == "session-1"
    assert sessions_data["sessions"]["session-1"]["title"] == "Project planning"
    assert chat_history == expected_history(
        sessions_data["sessions"]["session-1"]["messages"]
    )
    input_mock.assert_not_called()


def test_rename_prompts_for_title(
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "Prompted title")

    commands.handle_commands(
        "/rename",
        sessions_data,
        "session-1",
    )

    assert sessions_data["sessions"]["session-1"]["title"] == "Prompted title"


@pytest.mark.parametrize("entered_title", ["", "   "])
def test_rename_rejects_empty_title(
    entered_title: str,
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    original_title = sessions_data["sessions"]["session-1"]["title"]
    monkeypatch.setattr("builtins.input", lambda _: entered_title)

    commands.handle_commands(
        "/rename",
        sessions_data,
        "session-1",
    )

    assert sessions_data["sessions"]["session-1"]["title"] == original_title
    assert "Title cannot be empty" in capsys.readouterr().out


def test_delete_cancelled(
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    original = deepcopy(sessions_data)
    monkeypatch.setattr("builtins.input", lambda _: "no")

    session_id, chat_history = commands.handle_commands(
        "/delete",
        sessions_data,
        "session-1",
    )

    assert session_id == "session-1"
    assert sessions_data == original
    assert chat_history == expected_history(
        sessions_data["sessions"]["session-1"]["messages"]
    )
    assert "Delete cancelled" in capsys.readouterr().out


def test_delete_with_remaining_sessions(
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answers = iter(["yes"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(
        commands,
        "select_existing_session",
        lambda _: "session-2",
    )

    session_id, chat_history = commands.handle_commands(
        "/delete",
        sessions_data,
        "session-1",
    )

    assert "session-1" not in sessions_data["sessions"]
    assert session_id == "session-2"
    assert chat_history == expected_history(
        sessions_data["sessions"]["session-2"]["messages"]
    )


def test_delete_last_session_creates_new_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    all_sessions = {
        "sessions": {
            "only-session": {
                "title": "Only conversation",
                "messages": [{"role": "user", "content": "hello"}],
            }
        }
    }
    monkeypatch.setattr("builtins.input", lambda _: "yes")

    def fake_create_new_session(data: dict[str, Any]) -> str:
        data["sessions"]["replacement-session"] = {
            "title": "New Conversation",
            "messages": [],
        }
        return "replacement-session"

    monkeypatch.setattr(commands, "create_new_session", fake_create_new_session)

    session_id, chat_history = commands.handle_commands(
        "/delete",
        all_sessions,
        "only-session",
    )

    assert "only-session" not in all_sessions["sessions"]
    assert session_id == "replacement-session"
    assert chat_history == expected_history([])


def test_unknown_command(
    sessions_data: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    session_id, chat_history = commands.handle_commands(
        "/does-not-exist",
        sessions_data,
        "session-1",
    )

    assert session_id == "session-1"
    assert chat_history == expected_history(
        sessions_data["sessions"]["session-1"]["messages"]
    )
    assert "Unknown command" in capsys.readouterr().out


def test_command_rebuilds_chat_history(
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_history = expected_history(sessions_data["sessions"]["session-1"]["messages"])
    monkeypatch.setattr(
        commands,
        "select_existing_session",
        lambda _: "session-2",
    )

    _, rebuilt_history = commands.handle_commands(
        "/sessions",
        sessions_data,
        "session-1",
    )

    assert rebuilt_history != old_history
    assert rebuilt_history == expected_history(
        sessions_data["sessions"]["session-2"]["messages"]
    )
    assert rebuilt_history[0] == {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }


def test_command_does_not_call_llm(
    monkeypatch: pytest.MonkeyPatch,
    sessions_data: dict[str, Any],
) -> None:
    """Integration test: slash commands must bypass model inference."""
    llm_mock = Mock(side_effect=AssertionError("LLM must not be called"))
    save_mock = Mock()
    command_mock = Mock(
        return_value=(
            "session-1",
            expected_history(sessions_data["sessions"]["session-1"]["messages"]),
        )
    )

    user_inputs = iter(["/help", "exit"])

    monkeypatch.setattr(main, "load_sessions", lambda: sessions_data)
    monkeypatch.setattr(main, "choose_session", lambda _: "session-1")
    monkeypatch.setattr(main, "save_sessions", save_mock)
    monkeypatch.setattr(main, "handle_commands", command_mock)
    monkeypatch.setattr(main, "get_chatbot_response", llm_mock)
    monkeypatch.setattr("builtins.input", lambda _: next(user_inputs))

    main.run_chatbot()

    command_mock.assert_called_once_with(
        command="/help",
        all_sessions=sessions_data,
        current_session_id="session-1",
    )
    llm_mock.assert_not_called()


# ---------------------------------------------------------------------------
# Additional high-value edge and contract tests
# ---------------------------------------------------------------------------


def test_command_names_are_case_insensitive(
    sessions_data: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    session_id, _ = commands.handle_commands(
        "/HeLp",
        sessions_data,
        "session-1",
    )

    assert session_id == "session-1"
    assert "Available commands:" in capsys.readouterr().out


def test_rename_preserves_spaces_inside_title(
    sessions_data: dict[str, Any],
) -> None:
    commands.handle_commands(
        "/rename A title with several words",
        sessions_data,
        "session-1",
    )

    assert (
        sessions_data["sessions"]["session-1"]["title"] == "A title with several words"
    )


def test_help_does_not_mutate_sessions(
    sessions_data: dict[str, Any],
) -> None:
    original = deepcopy(sessions_data)

    commands.handle_commands(
        "/help",
        sessions_data,
        "session-1",
    )

    assert sessions_data == original


def test_unknown_command_does_not_mutate_sessions(
    sessions_data: dict[str, Any],
) -> None:
    original = deepcopy(sessions_data)

    commands.handle_commands(
        "/unknown",
        sessions_data,
        "session-1",
    )

    assert sessions_data == original


def test_switch_sessions_prints_selected_title(
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        commands,
        "select_existing_session",
        lambda _: "session-2",
    )

    selected = commands.switch_sessions(sessions_data)

    assert selected == "session-2"
    assert "Switched to Second conversation" in capsys.readouterr().out


@pytest.mark.parametrize("answer", ["YES", " yes ", "Yes"])
def test_delete_confirmation_is_case_and_whitespace_insensitive(
    answer: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    all_sessions = {
        "sessions": {
            "session-1": {
                "title": "Delete me",
                "messages": [],
            }
        }
    }
    monkeypatch.setattr("builtins.input", lambda _: answer)
    monkeypatch.setattr(
        commands,
        "create_new_session",
        lambda data: data["sessions"].setdefault(
            "new-session",
            {"title": "New Conversation", "messages": []},
        )
        and "new-session",
    )

    session_id = commands.delete_session(all_sessions, "session-1")

    assert session_id == "new-session"
    assert "session-1" not in all_sessions["sessions"]


def test_delete_remaining_session_selection_cancelled_keeps_valid_state(
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Documents current behavior when deletion succeeds but reselection is cancelled."""
    monkeypatch.setattr("builtins.input", lambda _: "yes")
    monkeypatch.setattr(commands, "select_existing_session", lambda _: None)

    session_id = commands.delete_session(sessions_data, "session-1")

    assert session_id is None
    assert "session-1" not in sessions_data["sessions"]
    assert "session-2" in sessions_data["sessions"]


def test_build_chat_history_returns_new_list(
    sessions_data: dict[str, Any],
) -> None:
    saved_messages = sessions_data["sessions"]["session-1"]["messages"]

    history = commands.build_chat_history(sessions_data, "session-1")

    assert history is not saved_messages
    assert history[1:] == saved_messages


def test_build_chat_history_always_places_system_prompt_first(
    sessions_data: dict[str, Any],
) -> None:
    history = commands.build_chat_history(sessions_data, "session-1")

    assert history[0]["role"] == "system"
    assert history[0]["content"] == SYSTEM_PROMPT


def test_new_session_saves_after_creation(
    monkeypatch: pytest.MonkeyPatch,
    sessions_data: dict[str, Any],
) -> None:
    call_order: list[str] = []

    def fake_create(data: dict[str, Any]) -> str:
        call_order.append("create")
        data["sessions"]["created"] = {
            "title": "New Conversation",
            "messages": [],
        }
        return "created"

    def fake_save(data: dict[str, Any]) -> None:
        call_order.append("save")
        assert "created" in data["sessions"]

    monkeypatch.setattr(commands, "create_new_session", fake_create)
    monkeypatch.setattr(commands, "save_sessions", fake_save)

    returned_id = commands.new_session(sessions_data)

    assert returned_id == "created"
    assert call_order == ["create", "save"]


def test_inline_rename_with_only_spaces_is_rejected(
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Regression test for '/rename    '.

    With the current implementation, command.split(maxsplit=1) produces only
    ['/rename'], so rename_session prompts. The supplied prompt response is empty,
    and the rename must be rejected.
    """
    old_title = sessions_data["sessions"]["session-1"]["title"]
    monkeypatch.setattr("builtins.input", lambda _: "")

    commands.handle_commands(
        "/rename    ",
        sessions_data,
        "session-1",
    )

    assert sessions_data["sessions"]["session-1"]["title"] == old_title
    assert "Title cannot be empty" in capsys.readouterr().out


def test_command_input_is_not_added_to_session_messages(
    sessions_data: dict[str, Any],
) -> None:
    original_messages = deepcopy(sessions_data["sessions"]["session-1"]["messages"])

    commands.handle_commands(
        "/help",
        sessions_data,
        "session-1",
    )

    assert sessions_data["sessions"]["session-1"]["messages"] == original_messages


def test_multiple_commands_do_not_duplicate_system_prompt(
    sessions_data: dict[str, Any],
) -> None:
    _, first_history = commands.handle_commands(
        "/help",
        sessions_data,
        "session-1",
    )
    _, second_history = commands.handle_commands(
        "/help",
        sessions_data,
        "session-1",
    )

    assert sum(message["role"] == "system" for message in first_history) == 1
    assert sum(message["role"] == "system" for message in second_history) == 1


def test_delete_does_not_select_another_session_when_cancelled(
    sessions_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "no")
    select_mock = Mock()
    monkeypatch.setattr(commands, "select_existing_session", select_mock)

    returned_id = commands.delete_session(sessions_data, "session-1")

    assert returned_id == "session-1"
    select_mock.assert_not_called()
