"""
Tests for chatbot.get_chatbot_response — the provider fallback chain.

This is the reliability core of the app: it tries providers in order
(Groq -> Anthropic -> OpenAI -> Gemini) and returns the first success, or None
if all fail. We mock each provider so no network calls happen; we only assert
on ordering, short-circuiting, and the all-fail path.
"""
import chatbot

PROVIDERS = [
    "get_chatbot_response_groq",
    "get_chatbot_response_anthropic",
    "get_chatbot_response_openai",
    "get_chatbot_response_genai",
]


def _patch_all(monkeypatch, behaviors):
    """
    behaviors: dict mapping provider function name -> either a return string or
    an Exception instance to raise. Also records call order into `calls`.
    """
    calls = []

    def make(name, behavior):
        def fake(chat_history):
            calls.append(name)
            if isinstance(behavior, Exception):
                raise behavior
            return behavior
        return fake

    for name in PROVIDERS:
        monkeypatch.setattr(chatbot, name, make(name, behaviors[name]))
    return calls


def test_returns_groq_result_first(monkeypatch):
    calls = _patch_all(
        monkeypatch,
        {
            "get_chatbot_response_groq": "groq answer",
            "get_chatbot_response_anthropic": RuntimeError("should not run"),
            "get_chatbot_response_openai": RuntimeError("should not run"),
            "get_chatbot_response_genai": RuntimeError("should not run"),
        },
    )
    result = chatbot.get_chatbot_response([{"role": "user", "content": "hi"}])
    assert result == "groq answer"
    # Only the first provider should have been called.
    assert calls == ["get_chatbot_response_groq"]


def test_falls_through_to_anthropic_when_groq_fails(monkeypatch):
    calls = _patch_all(
        monkeypatch,
        {
            "get_chatbot_response_groq": RuntimeError("groq down"),
            "get_chatbot_response_anthropic": "anthropic answer",
            "get_chatbot_response_openai": RuntimeError("should not run"),
            "get_chatbot_response_genai": RuntimeError("should not run"),
        },
    )
    result = chatbot.get_chatbot_response([{"role": "user", "content": "hi"}])
    assert result == "anthropic answer"
    assert calls == ["get_chatbot_response_groq", "get_chatbot_response_anthropic"]


def test_full_fallthrough_order_to_gemini(monkeypatch):
    calls = _patch_all(
        monkeypatch,
        {
            "get_chatbot_response_groq": RuntimeError("x"),
            "get_chatbot_response_anthropic": RuntimeError("x"),
            "get_chatbot_response_openai": RuntimeError("x"),
            "get_chatbot_response_genai": "gemini answer",
        },
    )
    result = chatbot.get_chatbot_response([{"role": "user", "content": "hi"}])
    assert result == "gemini answer"
    assert calls == PROVIDERS  # tried all four, in order


def test_returns_none_when_all_providers_fail(monkeypatch, capsys):
    _patch_all(
        monkeypatch,
        {name: RuntimeError(f"{name} down") for name in PROVIDERS},
    )
    result = chatbot.get_chatbot_response([{"role": "user", "content": "hi"}])
    assert result is None
    # The all-failed summary should be printed for operators to see.
    assert "All models failed" in capsys.readouterr().out
