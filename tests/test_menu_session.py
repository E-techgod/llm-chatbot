"""
Tests for menu_session.choose_session — the top-level menu loop.

It loops until it gets a valid outcome, so we feed it a sequence of inputs and
confirm it returns the right thing (new id / existing id / None) and re-prompts
on bad input instead of crashing or exiting.
"""

import menu_session


def _feed(monkeypatch, answers):
    """Feed a fixed list of answers to successive input() calls."""
    it = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _="": next(it))


def test_choice_1_starts_new_session(monkeypatch, empty_sessions):
    _feed(monkeypatch, ["1"])
    session_id = menu_session.choose_session(empty_sessions)
    assert session_id in empty_sessions["sessions"]


def test_choice_3_exits_with_none(monkeypatch, empty_sessions):
    _feed(monkeypatch, ["3"])
    assert menu_session.choose_session(empty_sessions) is None


def test_choice_2_selects_existing(monkeypatch, one_session):
    # "2" -> continue, then "1" -> pick the first listed conversation.
    _feed(monkeypatch, ["2", "1"])
    assert menu_session.choose_session(one_session) == "sess-1"


def test_invalid_choice_reprompts_then_succeeds(monkeypatch, empty_sessions):
    # Garbage input should loop, not crash; then "3" exits.
    _feed(monkeypatch, ["banana", "3"])
    assert menu_session.choose_session(empty_sessions) is None


def test_choice_2_with_bad_selection_reprompts(monkeypatch, one_session):
    # "2" then invalid selection -> select_existing returns None -> loop.
    # Then "1" starts a fresh session so the loop terminates.
    _feed(monkeypatch, ["2", "abc", "1"])
    result = menu_session.choose_session(one_session)
    assert result in one_session["sessions"]
