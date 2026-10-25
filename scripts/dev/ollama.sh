#!/usr/bin/env bash
# Tab Konsole: ollama serve, ou fica quieto se já estiver no ar.
# start.py troca o marcador OLLAMA_CMD antes de gravar o temp.
set +e
if curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "ollama already running on :11434"
  echo "[tab idle — Ctrl+D ou exit]"
  exec bash
else
  echo "starting: @OLLAMA_CMD@"
  @OLLAMA_CMD@
  echo
  echo "[tab exited — Ctrl+D ou exit]"
  exec bash
fi
