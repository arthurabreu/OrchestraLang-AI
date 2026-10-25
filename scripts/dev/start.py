#!/usr/bin/env python3
"""Abre o chat no Konsole (aba chat + aba ollama).

Lê os bash irmãos neste diretório (chat.sh, ollama.sh), troca os
marcadores e entrega cada um como comando de aba. Konsole não aguenta
comando longo entre aspas — por isso o .py lê o .sh e grava um temp.

    uv run python scripts/dev/start.py
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

TABS: tuple[tuple[str, str], ...] = (
    ("orchestralang", "chat.sh"),
    ("ollama", "ollama.sh"),
)


def ollama_cmd() -> str:
    if Path("/dev/nvidia0").exists() and shutil.which("prime-run"):
        return "prime-run ollama serve"
    return "ollama serve"


def render(name: str) -> str:
    raw = (HERE / name).read_text(encoding="utf-8")
    return raw.replace("@ROOT@", shlex.quote(str(ROOT))).replace("@OLLAMA_CMD@", ollama_cmd())


def main() -> int:
    if not shutil.which("konsole"):
        print("konsole não está no PATH.", file=sys.stderr)
        print(f"  cd {ROOT}", file=sys.stderr)
        print("  uv run orchestralang", file=sys.stderr)
        return 1
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        print("Sem DISPLAY/WAYLAND_DISPLAY — rode no terminal:", file=sys.stderr)
        print("  uv run orchestralang", file=sys.stderr)
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="orchestralang-tabs-"))
    lines: list[str] = []
    for title, script in TABS:
        dest = tmp / script
        dest.write_text(render(script), encoding="utf-8")
        dest.chmod(0o755)
        lines.append(f"title: {title};; workdir: {ROOT};; command: {dest}")

    tabs_file = tmp / "tabs"
    tabs_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # -e /bin/true por último: troca a aba default extra do Konsole.
    subprocess.Popen(
        [
            "konsole",
            "--hold",
            "--show-tabbar",
            "--tabs-from-file",
            str(tabs_file),
            "-e",
            "/bin/true",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print("Konsole: aba orchestralang (chat) + aba ollama")
    print(f"  app direto: uv run orchestralang")
    print(f"  runners: {tmp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
