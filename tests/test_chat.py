from __future__ import annotations

from unittest.mock import patch

from orchestralang.chat import message_text, pick_openrouter, pick_xai


def test_message_text_str_and_blocks() -> None:
    class Msg:
        content = "ok"

    assert message_text(Msg()) == "ok"
    assert message_text(type("M", (), {"content": [{"text": "a"}, "b"]})()) == "ab"


def test_pick_xai_without_key() -> None:
    with patch("orchestralang.chat.config.xai_api_key", return_value=None):
        assert pick_xai() is None


def test_pick_openrouter_without_key() -> None:
    with patch("orchestralang.chat.config.openrouter_api_key", return_value=None):
        assert pick_openrouter() is None
