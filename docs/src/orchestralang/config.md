# `config.py`

Lê ambiente. Importar o módulo já carrega o `.env`.

## Marcado

- **classe**&nbsp;:&nbsp;&nbsp;nenhuma. <span style="color:#6a9955">Só getters.</span>
- **`load_dotenv` no import**&nbsp;:&nbsp;&nbsp;cwd, depois a raiz do repo (`parents[2]` a partir deste arquivo). <span style="color:#6a9955">`uv run` acha o `.env` do projeto.</span>
- **`ollama_model()`**&nbsp;:&nbsp;&nbsp;`OLLAMA_MODEL`, senão `qwen3:8b`. <span style="color:#6a9955">Usado quando `get_chat_model(None)` — o ping sem argumento. O chat local manda a tag escolhida.</span>
- **`ollama_base_url()`**&nbsp;:&nbsp;&nbsp;`OLLAMA_HOST`, senão `http://127.0.0.1:11434`, sem barra final. <span style="color:#6a9955">`list_ollama_local` chama `{url}/api/tags`.</span>
- **`llm_temperature()`**&nbsp;:&nbsp;&nbsp;`LLM_TEMPERATURE`, senão `0.2`. Texto inválido também vira 0.2. <span style="color:#6a9955">Chat e ping usam este número. Mudou o `.env` → abre o app de novo.</span>
- **`openrouter_api_key()`**&nbsp;:&nbsp;&nbsp;string ou None. <span style="color:#6a9955">Vazio = None. O chat opção 3 checa antes de listar.</span>
- **`openrouter_default_model()`**&nbsp;:&nbsp;&nbsp;`OPENROUTER_MODEL` ou `open router: openrouter/free`. <span style="color:#6a9955">Não é o que o menu mostra; o menu lista o catálogo inteiro.</span>
- **`xai_api_key()`**&nbsp;:&nbsp;&nbsp;`XAI_API_KEY` ou None. <span style="color:#6a9955">Chat opção 2.</span>

## Resumo

Modelo default, URL do Ollama, temperatura e as duas keys. Sem key não é string vazia — é None, e quem chama decide a mensagem.
