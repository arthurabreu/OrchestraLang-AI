# `models.py`

## Marcado

- **classe**&nbsp;:&nbsp;&nbsp;nenhuma. <span style="color:#6a9955">Só constantes e helpers.</span>
- **`OPENROUTER_PREFIX`**&nbsp;:&nbsp;&nbsp;"open router: " — nome humano ≠ id da API. <span style="color:#6a9955">CLI/config usam display; API usa id cru.</span>
- **`OPENROUTER_FREE_IDS`**&nbsp;:&nbsp;&nbsp;tupla de ids :free. <span style="color:#6a9955">Catálogo estático — zero rede.</span>
- **`OPENROUTER_FREE`**&nbsp;:&nbsp;&nbsp;dict display → id (gerado da tupla). <span style="color:#6a9955">Atualiza a tupla → dict acompanha.</span>
- **`OLLAMA_MODELS_LOCAL`**&nbsp;:&nbsp;&nbsp;6 tags locais. <span style="color:#6a9955">Política do projeto: nunca ollama rm nestes.</span>
- **`openrouter_name(model_id)`**&nbsp;:&nbsp;&nbsp;id → display com prefixo. <span style="color:#6a9955">Se já tiver prefixo, devolve igual.</span>
- **`resolve_openrouter_id(name)`**&nbsp;:&nbsp;&nbsp;display/id do catálogo → id API, ou None. <span style="color:#6a9955">Fora do catálogo = None (llm ainda pode usar id solto).</span>

## Resumo

Catálogo estático OpenRouter free + lista Ollama local + helpers nome↔id. Sem inteligência, sem API.
