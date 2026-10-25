"""Factory de chat models: Ollama (default), OpenRouter free, Grok/xAI."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

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


def get_chat_model(
    name: str | None = None,
    *,
    temperature: float | None = None,
) -> BaseChatModel:
    """
    Resolve modelo por nome.

    - ``None`` / ollama tag → ChatOllama (``OLLAMA_MODEL``)
    - ``open router: provider/model:free`` → OpenRouter via API OpenAI-compat
    - ``grok:...`` / ``xai:...`` → Grok (xAI) se ``XAI_API_KEY`` set

    Temperatura: arg ``temperature`` ou env ``LLM_TEMPERATURE`` (default 0.2).
    Fácil de mudar no .env pra testar LangChain manualmente.
    """
    if name is None:
        name = config.ollama_model()

    name = name.strip()
    temp = config.llm_temperature() if temperature is None else temperature

    if name.startswith(OPENROUTER_PREFIX) or name in OPENROUTER_FREE.values():
        model_id = resolve_openrouter_id(name) or name.removeprefix(OPENROUTER_PREFIX).strip()
        key = config.openrouter_api_key()
        if not key:
            raise RuntimeError(
                "OPENROUTER_API_KEY ausente. Crie key em https://openrouter.ai/keys "
                "e coloque em .env (ver .env.example). "
                f"Modelo pedido: {openrouter_name(model_id)}"
            )
        return ChatOllama(
            model=model_id,
            api_key=key,
            base_url="https://openrouter.ai/api/v1",
            temperature=temp,
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
            temperature=temp,
        )

    return ChatOllama(model=name, temperature=temp)


def list_openrouter_free() -> list[str]:
    """Nomes de display prontos pra CLI / config (catálogo em models.py)."""
    return sorted(OPENROUTER_FREE.keys())


@dataclass(frozen=True)
class LocalModel:
    """Tag Ollama + capabilities do ``/api/tags`` (ex.: tools, vision)."""

    name: str
    capabilities: tuple[str, ...]

    def supports_tools(self) -> bool | None:
        """True/False se a API disse; None se capabilities vazias (desconhecido)."""
        if not self.capabilities:
            return None
        return "tools" in self.capabilities


def _fetch_ollama_tags() -> list[dict]:
    url = f"{config.ollama_base_url()}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            payload = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return []
    models = payload.get("models", [])
    return models if isinstance(models, list) else []


def list_ollama_local(*, chat_only: bool = True) -> list[LocalModel]:
    """Modelos locais com capabilities. ``chat_only`` esconde embeddings."""
    out: list[LocalModel] = []
    for raw in _fetch_ollama_tags():
        name = str(raw.get("name") or "")
        if not name:
            continue
        caps = tuple(str(c) for c in (raw.get("capabilities") or ()))
        if chat_only and "embed" in name.lower():
            continue
        if chat_only and caps and "completion" not in caps:
            continue
        out.append(LocalModel(name=name, capabilities=caps))
    return sorted(out, key=lambda m: m.name)


def list_ollama_models(*, chat_only: bool = True) -> list[str]:
    """Tags instaladas no Ollama local. Lista vazia se offline."""
    return [m.name for m in list_ollama_local(chat_only=chat_only)]
