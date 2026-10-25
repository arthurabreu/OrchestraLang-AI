# OrchestraLang AI

Agentes LangChain 1.x — Ollama local por padrão; OpenRouter free e Grok (xAI) pra comparação.

## Setup

```bash
cd "~/Documentos/py/OrchestraLang AI"
uv sync
cp .env.example .env
# cole OPENROUTER_API_KEY (key nova em https://openrouter.ai/keys)
```

## Modelos OpenRouter free

Nomes de display usam o prefixo **`open router: `**:

```text
open router: nousresearch/hermes-3-llama-3.1-405b:free
open router: openrouter/free
```

Listar:

```bash
uv run orchestralang models-openrouter
```

Smoke (precisa de key no `.env`):

```bash
uv run orchestralang ping "open router: openrouter/free"
```

Default local:

```bash
uv run orchestralang ping          # usa OLLAMA_MODEL
uv run orchestralang ping qwen3:8b
```

Catálogo: `src/orchestralang/models.py` (atualizar lista depois).

## Como rodar / testar

**Pré-requisito:** daemon Ollama no ar (`ollama serve` se precisar) e pelo menos um modelo local (`ollama list` — default do projeto: `qwen3:8b` via `OLLAMA_MODEL`).

**App (chat):** escolhe **1 local** / **2 xAI** / **3 OpenRouter**, depois conversa. `/back` troca modelo, `/exit` sai. Sem API key o provedor avisa e volta ao menu.

```bash
cd "~/Documentos/py/OrchestraLang AI"
uv sync
cp .env.example .env   # cole OPENROUTER_API_KEY e/ou XAI_API_KEY se for usar
uv run orchestralang
```

**Konsole (2 abas):** o Python lê os bash em `scripts/dev/`. Leitura do código: `docs/src/orchestralang/chat.md` e `docs/scripts/dev.md`.

```bash
uv run python scripts/dev/start.py
# ou double-click / ./scripts/dev/start.sh
```

`LLM_TEMPERATURE` no `.env` (default 0.2).

Outros comandos:

```bash
uv run orchestralang models-ollama
uv run orchestralang models-openrouter
uv run orchestralang ping
uv run orchestralang ping "open router: openrouter/free"   # precisa da key
```
