"""
Tests for the message-format conversion helpers in chatbot.py.

Anthropic wants the system prompt passed separately; Gemini wants one flat
string. These transforms run on every request to those providers, so a mistake
here silently corrupts the prompt (e.g. system instructions dropped).
"""
import chatbot


def test_anthropic_conversion_splits_system_out(sample_history):
    system_prompt, messages = chatbot.convert_messages_from_anthropic_to_openai_format(
        sample_history
    )
    assert system_prompt == "You are a math program."
    # No system-role entries should remain in the messages list.
    assert all(m["role"] != "system" for m in messages)
    assert messages == sample_history[1:]


def test_anthropic_conversion_no_system_yields_empty_string():
    history = [{"role": "user", "content": "hi"}]
    system_prompt, messages = chatbot.convert_messages_from_anthropic_to_openai_format(history)
    assert system_prompt == ""
    assert messages == history


def test_gemini_conversion_flattens_and_ends_with_assistant(sample_history):
    prompt = chatbot.convert_messages_from_gemini_to_openai_format(sample_history)
    lines = prompt.split("\n")

    assert lines[0] == "System instructions: You are a math program."
    assert "User: 1+1" in lines
    assert "Assistant: 2" in lines
    # Must end with the open "Assistant:" cue so the model continues the turn.
    assert lines[-1] == "Assistant:"


def test_gemini_conversion_labels_each_role():
    history = [
        {"role": "user", "content": "q"},
        {"role": "assistant", "content": "a"},
    ]
    prompt = chatbot.convert_messages_from_gemini_to_openai_format(history)
    assert prompt == "User: q\nAssistant: a\nAssistant:"
