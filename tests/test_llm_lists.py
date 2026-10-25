from __future__ import annotations

from unittest.mock import patch

import pytest

from orchestralang.llm import get_chat_model, list_ollama_models, list_openrouter_free


def test_list_openrouter_free_uses_prefix() -> None:
    names = list_openrouter_free()
    assert names
    assert all(n.startswith("open router: ") for n in names)


def test_get_chat_model_openrouter_requires_key() -> None:
    with patch("orchestralang.llm.config.openrouter_api_key", return_value=None):
        with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
            get_chat_model("open router: openrouter/free")


def test_list_ollama_models_empty_when_offline() -> None:
    with patch("orchestralang.llm.urllib.request.urlopen", side_effect=OSError("down")):
        assert list_ollama_models() == []


def test_local_model_tools_flag() -> None:
    from orchestralang.llm import LocalModel

    assert LocalModel("gemma3:4b", ("completion", "vision")).supports_tools() is False
    assert LocalModel("qwen3:8b", ("completion", "tools")).supports_tools() is True
    assert LocalModel("unknown", ()).supports_tools() is None
