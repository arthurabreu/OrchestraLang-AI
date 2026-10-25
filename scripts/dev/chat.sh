#!/usr/bin/env bash
# Tab Konsole: sobe o chat. start.py troca o marcador ROOT antes de gravar o temp.
set +e
cd @ROOT@ || exit 1
echo "OrchestraLang — sync…"
uv sync
echo
uv run orchestralang
echo
exec fish
