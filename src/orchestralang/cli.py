from __future__ import annotations

import argparse
import sys

from orchestralang import config
from orchestralang.llm import get_chat_model, list_ollama_local, list_openrouter_free
from orchestralang.models import OPENROUTER_PREFIX


def _print_llm_error(err: BaseException) -> None:
    print(f"ERRO: {err}", file=sys.stderr)


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    # Sem args = o app: escolher provedor e conversar.
    if not argv:
        from orchestralang.chat import run_chat

        run_chat()
        return

    p = argparse.ArgumentParser(prog="OrchestraLang")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("chat", help="escolhe local / xAI / OpenRouter e conversa")
    sub.add_parser("models-ollama", help="lista tags Ollama locais (API /api/tags)")
    sub.add_parser("models-openrouter", help="lista free OpenRouter (nomes open router: …)")

    s = sub.add_parser("ping", help="1 mensagem curta no modelo (smoke)")
    s.add_argument(
        "model",
        nargs="?",
        default=None,
        help='ex.: qwen3:8b ou "open router: openrouter/free"',
    )
    s.add_argument("--msg", default="diga ok em uma palavra")

    a = p.parse_args(argv)

    if a.cmd == "chat":
        from orchestralang.chat import run_chat

        run_chat()
        return

    if a.cmd == "models-ollama":
        local = list_ollama_local()
        if not local:
            print(
                f"(nenhum modelo — Ollama offline em {config.ollama_base_url()}?)",
                file=sys.stderr,
            )
            sys.exit(1)
        for m in local:
            flag = m.supports_tools()
            tag = "tools" if flag is True else "sem tools" if flag is False else "tools?"
            print(f"{m.name}\t({tag})")
        return

    if a.cmd == "models-openrouter":
        for name in list_openrouter_free():
            print(name)
        return

    if a.cmd == "ping":
        model_name = a.model
        try:
            llm = get_chat_model(model_name)
            out = llm.invoke(a.msg)
        except RuntimeError as err:
            sys.exit(str(err))
        except Exception as err:
            _print_llm_error(err)
            sys.exit(1)
        text = getattr(out, "content", out)
        print(text)
        if model_name and model_name.startswith(OPENROUTER_PREFIX):
            print(f"(model={model_name})", file=sys.stderr)
        return


if __name__ == "__main__":
    main()
