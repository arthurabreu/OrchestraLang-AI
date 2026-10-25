# `models.py`

Catálogo estático. Não fala com Ollama nem com API. A lista ao vivo do Ollama mora em `llm.list_ollama_local`.

## Marcado

- **classe**&nbsp;:&nbsp;&nbsp;nenhuma. <span style="color:#6a9955">Constantes e dois helpers.</span>
- **`OPENROUTER_PREFIX`**&nbsp;:&nbsp;&nbsp;`"open router: "` (com espaço). <span style="color:#6a9955">Nome que o humano vê ≠ id da API.</span>
- **`OPENROUTER_FREE_IDS`**&nbsp;:&nbsp;&nbsp;tupla de ids `:free`. <span style="color:#6a9955">Atualizar a tupla atualiza o dict abaixo.</span>
- **`OPENROUTER_FREE`**&nbsp;:&nbsp;&nbsp;dict `open router: <id>` → id. <span style="color:#6a9955">O chat opção 3 mostra as chaves.</span>
- **`XAI_MODELS`**&nbsp;:&nbsp;&nbsp;`grok-4`, `grok-3`, `grok-3-mini`, `grok-2-latest`. <span style="color:#6a9955">O chat prefixa `xai:` antes de chamar a factory.</span>
- **`OLLAMA_MODELS_LOCAL`**&nbsp;:&nbsp;&nbsp;6 tags keepers. <span style="color:#6a9955">Política: nunca `ollama rm` nestes. O menu do chat não lê esta tupla — lê `/api/tags`.</span>
- **`openrouter_name(model_id)`**&nbsp;:&nbsp;&nbsp;id → display. <span style="color:#6a9955">Se já tem o prefixo, devolve igual.</span>
- **`resolve_openrouter_id(name)`**&nbsp;:&nbsp;&nbsp;display do catálogo → id, ou None. <span style="color:#6a9955">Fora do catálogo a factory ainda aceita o id solto.</span>

## Resumo

Três listas fixas (OpenRouter free, Grok, keepers Ollama) e a tradução nome ↔ id do OpenRouter.
