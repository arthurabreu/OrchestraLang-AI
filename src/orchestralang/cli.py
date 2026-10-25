from __future__ import annotations

import argparse
import sys

from orchestralang.llm import get_chat_model, list_openrouter_free
from orchestralang.models import OPENROUTER_PREFIX


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="OrchestraLang")
    sub = p.add_subparsers(dest="cmd", required=True)

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

    if a.cmd == "models-openrouter":
        for name in list_openrouter_free():
            print(name)
        return

    if a.cmd == "ping":
        model_name = a.model
        try:
            llm = get_chat_model(model_name)
        except RuntimeError as err:
            sys.exit(str(err))
        out = llm.invoke(a.msg)
        text = getattr(out, "content", out)
        print(text)
        if model_name and model_name.startswith(OPENROUTER_PREFIX):
            print(f"(model={model_name})", file=sys.stderr)
        return


if __name__ == "__main__":
    main()
