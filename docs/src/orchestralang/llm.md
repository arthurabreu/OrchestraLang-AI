# `llm.py`

Um nome vira um `BaseChatModel`. O chat e o ping passam por aqui. Nenhum deles escolhe a classe do provider sozinho.

## `get_chat_model(name=None, *, temperature=None)`

1. `name is None` → `config.ollama_model()` (`OLLAMA_MODEL`, default `qwen3:8b`).
2. Temperatura: argumento, senão `config.llm_temperature()` (`LLM_TEMPERATURE`, default 0.2).
3. **OpenRouter** se o nome começa com `open router: ` ou é um id do catálogo free:
   - resolve o id (`nousresearch/…:free`)
   - sem `OPENROUTER_API_KEY` → `RuntimeError` com o link da key e o nome pedido
   - senão `ChatOpenAI` em `https://openrouter.ai/api/v1`
4. **xAI** se o nome começa com `xai:` ou `grok:`:
   - sem `XAI_API_KEY` → `RuntimeError`
   - id = o que vem depois dos dois-pontos (`xai:grok-3` → `grok-3`; vazio → `grok-2-latest`)
   - `ChatOpenAI` em `https://api.x.ai/v1`
5. **Qualquer outro nome** → `ChatOllama(model=name, temperature=temp)`. `gemma3:4b` cai aqui. O chat não manda tools.

## Lista local

- **`LocalModel`**&nbsp;:&nbsp;&nbsp;tag + capabilities do `GET /api/tags`. <span style="color:#6a9955">`supports_tools()`: True/False se a API mandou a lista; None se veio vazia.</span>
- **`_fetch_ollama_tags()`**&nbsp;:&nbsp;&nbsp;JSON de `{OLLAMA_HOST}/api/tags`. <span style="color:#6a9955">Timeout 3s. Offline ou JSON ruim → lista vazia, sem exception.</span>
- **`list_ollama_local(chat_only=True)`**&nbsp;:&nbsp;&nbsp;pula nome com `embed` e modelo cuja capability não tem `completion`. <span style="color:#6a9955">`nomic-embed-text` sai. Ordena por nome.</span>
- **`list_ollama_models()`**&nbsp;:&nbsp;&nbsp;só os nomes, mesmo filtro. <span style="color:#6a9955">Atalho em cima de `list_ollama_local`.</span>
- **`list_openrouter_free()`**&nbsp;:&nbsp;&nbsp;chaves de `OPENROUTER_FREE`, ordenadas. <span style="color:#6a9955">Catálogo estático. Zero rede.</span>

## Marcado

- **classe de chat**&nbsp;:&nbsp;&nbsp;nenhuma além de `LocalModel`. <span style="color:#6a9955">O telefone é `ChatOllama` ou `ChatOpenAI`.</span>
- **ainda não**&nbsp;:&nbsp;&nbsp;streaming, retry, timeout de generate, tools. <span style="color:#6a9955">Esta factory só entrega o modelo.</span>

## Resumo

Nome (ou None) → modelo LangChain com a temperatura do `.env`. Cloud só se o nome pedir e a key existir.
