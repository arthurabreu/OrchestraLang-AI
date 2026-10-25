"""Chat mínimo: escolhe provedor, conversa, volta pro menu."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from orchestralang import config
from orchestralang.llm import get_chat_model, list_ollama_local, list_openrouter_free
from orchestralang.models import XAI_MODELS

SYSTEM = (
    "Você é o chat do OrchestraLang. "
    "Responda no idioma do usuário, curto e direto."
)


def message_text(out: Any) -> str:
    content = getattr(out, "content", out)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text", "")))
            else:
                parts.append(str(block))
        return "".join(parts).strip()
    return str(content)


def _read(prompt: str) -> str | None:
    """None = EOF / Ctrl-C."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def _pick(title: str, items: list[str]) -> str | None:
    if not items:
        print("(lista vazia)")
        return None
    print(title)
    for i, name in enumerate(items, start=1):
        print(f"  {i}) {name}")
    print("  0) voltar")
    raw = _read("> ")
    if raw is None or raw in ("", "0"):
        return None
    try:
        idx = int(raw)
    except ValueError:
        print(f"opção inválida: {raw!r}")
        return None
    if idx < 1 or idx > len(items):
        print(f"fora da lista: {idx}")
        return None
    return items[idx - 1]


def pick_local() -> str | None:
    models = list_ollama_local()
    if not models:
        print(
            f"Ollama sem modelos (ou offline em {config.ollama_base_url()}). "
            "Rode `ollama serve` na outra aba."
        )
        return None
    labels = [m.name for m in models]
    return _pick("Ollama local:", labels)


def pick_xai() -> str | None:
    if not config.xai_api_key():
        print(
            "ERRO: XAI_API_KEY ausente.\n"
            "  Coloque a key no .env (veja .env.example) e abra de novo.\n"
            "  Sem key o xAI não carrega."
        )
        return None
    name = _pick("xAI (Grok):", list(XAI_MODELS))
    if name is None:
        return None
    return f"xai:{name}"


def pick_openrouter() -> str | None:
    if not config.openrouter_api_key():
        print(
            "ERRO: OPENROUTER_API_KEY ausente.\n"
            "  1) Key em https://openrouter.ai/keys\n"
            "  2) .env → OPENROUTER_API_KEY=\n"
            "  Sem key o OpenRouter não carrega."
        )
        return None
    return _pick("OpenRouter free:", list_openrouter_free())


def chat_session(model: str) -> bool:
    """Conversa. True = sair do app. False = voltar ao menu."""
    print(f"\nmodelo {model}  temp={config.llm_temperature()}")
    print("comandos: /back  volta · /exit  sai\n")
    try:
        llm = get_chat_model(model)
    except RuntimeError as err:
        print(f"ERRO: {err}")
        return False

    history: list[BaseMessage] = [SystemMessage(SYSTEM)]
    while True:
        line = _read("you> ")
        if line is None or line == "/back":
            return False
        if line in ("/exit", "/quit"):
            return True
        if not line:
            continue
        history.append(HumanMessage(line))
        try:
            out = llm.invoke(history)
        except Exception as err:
            history.pop()
            print(f"ERRO: {err}")
            continue
        text = message_text(out)
        print(text)
        print()
        history.append(out if isinstance(out, AIMessage) else AIMessage(text))


def run_chat() -> None:
    print(f"OrchestraLang chat  ·  temp={config.llm_temperature()}  (LLM_TEMPERATURE no .env)")
    while True:
        print()
        print("Provedor:")
        print("  1) LLM local (Ollama)")
        print("  2) xAI")
        print("  3) OpenRouter")
        print("  q) sair")
        choice = _read("> ")
        if choice is None or choice in ("q", "quit", "exit"):
            print("tchau")
            return
        if choice == "1":
            model = pick_local()
        elif choice == "2":
            model = pick_xai()
        elif choice == "3":
            model = pick_openrouter()
        else:
            print(f"opção inválida: {choice!r}")
            continue
        if not model:
            continue
        if chat_session(model):
            print("tchau")
            return
