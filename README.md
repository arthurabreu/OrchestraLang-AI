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
