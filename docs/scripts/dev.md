# `scripts/dev/` — abrir o app no Konsole

Não mora em `src/`. O app em si é `uv run orchestralang` em qualquer terminal. Esta pasta só abre duas abas.

## Quem chama quem

1. **`start.sh`** entra na raiz do repo e faz `uv run python scripts/dev/start.py`. Serve para double-click.
2. **`start.py`** lê os bash irmãos, troca marcadores e entrega um arquivo temp por aba (`--tabs-from-file`). Konsole quebra comando longo entre aspas; por isso o Python lê o `.sh` e grava outro `.sh` curto.
   - `@ROOT@` → caminho do repo entre aspas (`OrchestraLang AI` tem espaço)
   - `@OLLAMA_CMD@` → `ollama serve`, ou `prime-run ollama serve` se existir `/dev/nvidia0` e `prime-run`
   - Sem `konsole`, ou sem `DISPLAY`/`WAYLAND_DISPLAY`: imprime para rodar `uv run orchestralang` e sai 1
   - `-e /bin/true` no fim come a aba default extra do Konsole
3. **`chat.sh`** (aba `orchestralang`): `cd` na raiz, `uv sync`, `uv run orchestralang`, depois `fish` para a janela não fechar quando você sai do chat.
4. **`ollama.sh`** (aba `ollama`): se `:11434` já responde, fica num bash idle. Senão roda o comando do marcador e, quando ele cair, outro bash idle.

## Resumo

`uv run python scripts/dev/start.py` = aba do chat + aba do Ollama. O código da conversa não está aqui.
