"""Catálogo de modelos. Nomes OpenRouter free: ``open router: <id>``."""

from __future__ import annotations

OPENROUTER_PREFIX = "open router: "

OPENROUTER_FREE_IDS: tuple[str, ...] = (
    "cohere/north-mini-code:free",
    "nex-agi/nex-n2-pro:free",
    "nvidia/nemotron-3.5-content-safety:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3-nano-30b-a3b-reasoning:free",
    "poolside/laguna-xs.2:free",
    "poolside/laguna-m.1:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
    "qwen/qwen3-coder:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "openrouter/free",
)

OPENROUTER_FREE: dict[str, str] = {
    f"{OPENROUTER_PREFIX}{mid}": mid for mid in OPENROUTER_FREE_IDS
}

XAI_MODELS: tuple[str, ...] = (
    "grok-4",
    "grok-3",
    "grok-3-mini",
    "grok-2-latest",
)

OLLAMA_MODELS_LOCAL: tuple[str, ...] = (
    "nomic-embed-text:latest",
    "gemma3:4b",
    "qwen3:8b",
    "gemma4:e4b",
    "ornith:9b",
    "qwen3.5:9b",
)

def openrouter_name(model_id: str) -> str:
    """``nousresearch/hermes-3-llama-3.1-405b:free`` → ``open router: …``."""
    if model_id.startswith(OPENROUTER_PREFIX):
        return model_id
    return f"{OPENROUTER_PREFIX}{model_id}"


def resolve_openrouter_id(name: str) -> str | None:
    """Nome de display → id OpenRouter, ou None se não for OpenRouter."""
    key = name if name.startswith(OPENROUTER_PREFIX) else openrouter_name(name)
    return OPENROUTER_FREE.get(key)
