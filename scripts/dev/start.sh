#!/usr/bin/env bash
# Double-click / terminal: sobe o Konsole via o Python que lê os .sh daqui.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 1
exec uv run python "$ROOT/scripts/dev/start.py"
