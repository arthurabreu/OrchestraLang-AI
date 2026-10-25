# `llm.py`

## Marcado

- **classe**&nbsp;:&nbsp;&nbsp;nenhuma (devolve BaseChatModel pronto). <span style="color:#6a9955">Só funções factory.</span>
- **`get_chat_model(name=None)`**&nbsp;:&nbsp;&nbsp;factory — nome → chat model LangChain. <span style="color:#6a9955">Único telefone pro LLM hoje.</span>
- **`list_openrouter_free()`**&nbsp;:&nbsp;&nbsp;nomes display ordenados. <span style="color:#6a9955">Alimenta o subcomando models-openrouter.</span>
- **L54–55 `name is None`**&nbsp;:&nbsp;&nbsp;usa config.ollama_model(). <span style="color:#6a9955">Default = Ollama local do .env.</span>
- **L59–76 ramo OpenRouter**&nbsp;:&nbsp;&nbsp;prefixo / id free → ChatOpenAI + URL OpenRouter; sem key → RuntimeError. <span style="color:#6a9955">Mesma classe OpenAI-compat, outra base_url.</span>
- **L78–87 ramo Grok/xAI**&nbsp;:&nbsp;&nbsp;grok: / xai: → ChatOpenAI + api.x.ai; sem key → RuntimeError. <span style="color:#6a9955">Mesmo truque: URL + key diferentes.</span>
- **L89 fallback**&nbsp;:&nbsp;&nbsp;qualquer outro nome → ChatOllama(model=name). <span style="color:#6a9955">Tags tipo qwen3:8b caem aqui.</span>
- **ainda não**&nbsp;:&nbsp;&nbsp;create_agent, tools, streaming, retries. <span style="color:#6a9955">Só factory + lista free.</span>

## Resumo

Um nome (ou None) vira um telefone pro LLM. Default = Ollama local; cloud só se o nome pedir.
