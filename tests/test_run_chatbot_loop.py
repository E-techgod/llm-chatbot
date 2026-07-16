"""
Integration-style test for main.run_chatbot.

Everything external is mocked (session choice, the LLM call, input, and save),
so this exercises the real loop wiring: a user turn is appended, the assistant
reply is appended and persisted, blank input is rejected, and "exit" stops.
"""

import pytest

import main


def test_user_turn_is_persisted_and_exit_stops(monkeypatch):
    sessions_data = {"sessions": {"sess-1": {"title": "New chat", "messages": []}}}

    monkeypatch.setattr(main, "load_sessions", lambda: sessions_data)
    monkeypatch.setattr(main, "choose_session", lambda all_sessions: "sess-1")

    saved = []
    monkeypatch.setattr(main, "save_sessions", lambda data: saved.append(True))
    monkeypatch.setattr(main, "get_chatbot_response", lambda history: "AI reply")

    # blank -> reprompt, "hello" -> one exchange, "exit" -> stop.
    inputs = iter(["", "hello", "exit"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    main.run_chatbot()

    messages = sessions_data["sessions"]["sess-1"]["messages"]
    assert messages == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "AI reply"},
    ]
    # System prompt must not be persisted into the session store.
    assert all(m["role"] != "system" for m in messages)
    assert saved  # save_sessions was called at least once


def test_exit_immediately_persists_nothing(monkeypatch):
    sessions_data = {"sessions": {"sess-1": {"title": "New chat", "messages": []}}}
    monkeypatch.setattr(main, "load_sessions", lambda: sessions_data)
    monkeypatch.setattr(main, "choose_session", lambda all_sessions: "sess-1")
    monkeypatch.setattr(main, "save_sessions", lambda data: None)

    called = {"llm": False}

    def _fail_llm(history):
        called["llm"] = True
        return "nope"

    monkeypatch.setattr(main, "get_chatbot_response", _fail_llm)
    monkeypatch.setattr("builtins.input", lambda _="": "exit")

    main.run_chatbot()

    assert sessions_data["sessions"]["sess-1"]["messages"] == []
    assert called["llm"] is False  # LLM never called on an immediate exit


def test_none_session_choice_returns_without_llm(monkeypatch):
    monkeypatch.setattr(main, "load_sessions", lambda: {"sessions": {}})
    monkeypatch.setattr(main, "choose_session", lambda all_sessions: None)
    monkeypatch.setattr(main, "get_chatbot_response", lambda h: pytest_fail())
    # If choose_session returns None the function should return before any input.
    monkeypatch.setattr("builtins.input", lambda _="": pytest_fail())
    main.run_chatbot()  # should simply return, no exception


def pytest_fail():
    raise AssertionError("this code path should not be reached")


@pytest.mark.parametrize("error_type", [KeyboardInterrupt, EOFError])
def test_interrupts_close_without_traceback(monkeypatch, capsys, error_type):
    sessions_data = {"sessions": {"sess-1": {"title": "New chat", "messages": []}}}

    monkeypatch.setattr(main, "load_sessions", lambda: sessions_data)
    monkeypatch.setattr(main, "choose_session", lambda all_sessions: "sess-1")
    monkeypatch.setattr(main, "save_sessions", lambda data: None)
    monkeypatch.setattr(
        "builtins.input", lambda _="": (_ for _ in ()).throw(error_type())
    )

    main.run_chatbot()

    captured = capsys.readouterr()
    assert "Traceback" not in captured.err
    assert "Chatbot closed." in captured.out
