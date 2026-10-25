from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "qwen3:8b").strip() or "qwen3:8b"


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
