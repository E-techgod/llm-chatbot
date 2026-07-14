"""
Tests for main.trim_chat_history.

This is the memory-window function: it must always keep the system prompt and
only the most recent N user/assistant messages. If this is wrong, the bot
either forgets the system prompt (wrong persona) or sends an ever-growing
history to the API (rising cost + eventual context-limit errors).
"""
from main import trim_chat_history


def _msg(role, content):
    return {"role": role, "content": content}


def test_system_prompt_is_always_kept():
    history = [_msg("system", "SP")] + [_msg("user", str(i)) for i in range(50)]
    trimmed = trim_chat_history(history, max_memory_limit=10)
    assert trimmed[0] == {"role": "system", "content": "SP"}


def test_keeps_only_last_n_non_system_messages():
    convo = [_msg("user" if i % 2 == 0 else "assistant", str(i)) for i in range(20)]
    history = [_msg("system", "SP")] + convo
    trimmed = trim_chat_history(history, max_memory_limit=6)

    # 1 system + 6 most-recent conversation messages
    assert len(trimmed) == 7
    kept_contents = [m["content"] for m in trimmed[1:]]
    assert kept_contents == [str(i) for i in range(14, 20)]


def test_history_shorter_than_limit_is_unchanged():
    history = [_msg("system", "SP"), _msg("user", "hi"), _msg("assistant", "hello")]
    trimmed = trim_chat_history(history, max_memory_limit=10)
    assert trimmed == history


def test_empty_conversation_returns_only_system():
    history = [_msg("system", "SP")]
    trimmed = trim_chat_history(history, max_memory_limit=10)
    assert trimmed == [_msg("system", "SP")]


def test_relative_order_is_preserved():
    convo = [_msg("user", "a"), _msg("assistant", "b"), _msg("user", "c")]
    history = [_msg("system", "SP")] + convo
    trimmed = trim_chat_history(history, max_memory_limit=2)
    assert [m["content"] for m in trimmed] == ["SP", "b", "c"]


def test_limit_of_zero_keeps_ENTIRE_history_a_known_footgun():
    """
    BUG / FOOTGUN: with max_memory_limit=0 you'd expect all conversation to be
    dropped. Instead, `list[-0:]` is `list[0:]`, so the WHOLE conversation is
    returned. The live app hard-codes MAX_MEMORY_MESSAGES=10 so this never
    triggers today, but any future config that could reach 0 would silently
    disable trimming. Guard against non-positive limits before shipping a
    configurable value.

    This test asserts the *actual* (surprising) behavior so it fails loudly if
    someone "fixes" the slice without also updating the expectation here.
    """
    history = [_msg("system", "SP"), _msg("user", "a"), _msg("assistant", "b")]
    trimmed = trim_chat_history(history, max_memory_limit=0)
    assert trimmed == history  # <-- not just the system message!
