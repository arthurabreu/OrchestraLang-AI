from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "qwen3:8b").strip() or "qwen3:8b"


def ollama_base_url() -> str:
    """Base URL do Ollama (sem path). Default local."""
    raw = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").strip()
    return raw.rstrip("/") or "http://127.0.0.1:11434"


def llm_temperature() -> float:
    """Temperatura LangChain — fácil de mudar no .env (LLM_TEMPERATURE)."""
    raw = os.getenv("LLM_TEMPERATURE", "0.2").strip() or "0.2"
    try:
        return float(raw)
    except ValueError:
        return 0.2


def openrouter_api_key() -> str | None:
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    return key or None


def openrouter_default_model() -> str:
    """Nome de display default OpenRouter (prefixo ``open router:``)."""
    raw = os.getenv("OPENROUTER_MODEL", "open router: openrouter/free").strip()
    return raw or "open router: openrouter/free"


def xai_api_key() -> str | None:
    key = os.getenv("XAI_API_KEY", "").strip()
    return key or None
