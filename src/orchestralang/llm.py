"""Factory de chat models: Ollama (default), OpenRouter free, Grok/xAI."""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from orchestralang import config
from orchestralang.models import (
    OPENROUTER_FREE,
    OPENROUTER_PREFIX,
    openrouter_name,
    resolve_openrouter_id,
)


def get_chat_model(name: str | None = None) -> BaseChatModel:
    """
    Resolve modelo por nome.

    - ``None`` / ollama tag → ChatOllama (``OLLAMA_MODEL``)
    - ``open router: provider/model:free`` → OpenRouter via API OpenAI-compat
    - ``grok:...`` / ``xai:...`` → Grok (xAI) se ``XAI_API_KEY`` set
    """
    if name is None:
        name = config.ollama_model()

    name = name.strip()

    if name.startswith(OPENROUTER_PREFIX) or name in OPENROUTER_FREE.values():
        model_id = resolve_openrouter_id(name) or name.removeprefix(OPENROUTER_PREFIX).strip()
        key = config.openrouter_api_key()
        if not key:
            raise RuntimeError(
                "OPENROUTER_API_KEY ausente. Crie key em https://openrouter.ai/keys "
                "e coloque em .env (ver .env.example). "
                f"Modelo pedido: {openrouter_name(model_id)}"
            )
        return ChatOpenAI(
            model=model_id,
            api_key=key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/local/orchestralang",
                "X-Title": "OrchestraLang AI",
            },
        )

    if name.startswith("grok:") or name.startswith("xai:"):
        key = config.xai_api_key()
        if not key:
            raise RuntimeError("XAI_API_KEY ausente para Grok (xAI).")
        model_id = name.split(":", 1)[1].strip() or "grok-2-latest"
        return ChatOpenAI(
            model=model_id,
            api_key=key,
            base_url="https://api.x.ai/v1",
        )

    return ChatOllama(model=name)


def list_openrouter_free() -> list[str]:
    """Nomes de display prontos pra CLI / config."""
    return sorted(OPENROUTER_FREE.keys())
