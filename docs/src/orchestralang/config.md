# `config.py`

## Marcado

- **classe**&nbsp;:&nbsp;&nbsp;nenhuma. <span style="color:#6a9955">Só getters de env.</span>
- **L12–13 `load_dotenv` (no import)**&nbsp;:&nbsp;&nbsp;carrega .env do cwd e da raiz do repo (parents[2]). <span style="color:#6a9955">Roda ao importar — uv run de qualquer pasta do repo acha o .env.</span>
- **`ollama_model()`**&nbsp;:&nbsp;&nbsp;lê OLLAMA_MODEL; default qwen3:8b. <span style="color:#6a9955">Strip vazio vira default.</span>
- **`openrouter_api_key()`**&nbsp;:&nbsp;&nbsp;OPENROUTER_API_KEY → str ou None. <span style="color:#6a9955">None = sem key (não string vazia).</span>
- **`openrouter_default_model()`**&nbsp;:&nbsp;&nbsp;OPENROUTER_MODEL → display open router: …. <span style="color:#6a9955">Default open router: openrouter/free.</span>
- **`xai_api_key()`**&nbsp;:&nbsp;&nbsp;XAI_API_KEY → str ou None. <span style="color:#6a9955">Mesmo padrão das outras keys.</span>
- **padrão keys**&nbsp;:&nbsp;&nbsp;vazio vira None. <span style="color:#6a9955">llm.py transforma em RuntimeError legível.</span>

## Resumo

Lê .env e devolve modelo/keys. Config fora do código; não valida se Ollama tem o modelo.
