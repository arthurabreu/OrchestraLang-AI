# Chat cru

Um `ChatOpenAI` no Ollama local (`/v1`). Sem menu.

Na raiz do repositório, nesta ordem. `ollama serve` segura o terminal: o chat roda em outro. O último comando para o Ollama.

```bash
uv sync
ollama serve
uv run python cru/chat.py qwen3:8b
uv run python cru/chat.py gemma3:4b
pkill -x ollama
```

`qwen3:8b` e `gemma3:4b` são os dois exemplos locais. Saia com `quit`, `exit` ou `q` antes de trocar o modelo.

Tags pra copiar: `uv run python cru/models.py`. O loop `you>` está em `docs/chat.md`.
