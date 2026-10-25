# `chat.py`

App do dia a dia. Sem args, `cli.main` cai aqui. Não usa tools.

## Fluxo (leia nesta ordem)

1. **`run_chat()`** imprime a temperatura (`LLM_TEMPERATURE`, default 0.2) e fica no menu:
   - `1` → `pick_local()`
   - `2` → `pick_xai()`
   - `3` → `pick_openrouter()`
   - `q` / `quit` / `exit` / Ctrl-C / EOF → imprime `tchau` e acaba
2. Se o pick devolve `None` (voltar, lista vazia, ou key ausente), o menu repete. Não sai do app.
3. Com um nome de modelo, **`chat_session(model)`**:
   - `True` = usuário pediu `/exit` ou `/quit` → `run_chat` imprime `tchau` e acaba
   - `False` = `/back` ou Ctrl-C → volta ao menu de provedor
4. Dentro da sessão o histórico é uma lista LangChain. A primeira mensagem é `SystemMessage(SYSTEM)` (“responda no idioma do usuário, curto”). Cada linha vira `HumanMessage`, `llm.invoke(history)` devolve a resposta, o texto é impresso, e a resposta entra no histórico. A próxima linha vê tudo que já foi dito.
5. Se o invoke falha, a `HumanMessage` que acabou de entrar é removida (`history.pop()`), o erro imprime, o loop continua. A conversa anterior não se perde.

## Marcado

- **classe**&nbsp;:&nbsp;&nbsp;nenhuma. <span style="color:#6a9955">Só funções.</span>
- **`SYSTEM`**&nbsp;:&nbsp;&nbsp;prompt fixo do chat. <span style="color:#6a9955">Uma frase: idioma do usuário, curto.</span>
- **`message_text(out)`**&nbsp;:&nbsp;&nbsp;tira string de `AIMessage.content`. <span style="color:#6a9955">String direto, ou lista de blocos `{"text": …}`.</span>
- **`_read(prompt)`**&nbsp;:&nbsp;&nbsp;`input().strip()`. <span style="color:#6a9955">EOF ou Ctrl-C → None.</span>
- **`_pick(title, items)`**&nbsp;:&nbsp;&nbsp;lista numerada. <span style="color:#6a9955">0, Enter ou Ctrl-C → None.</span>
- **`pick_local()`**&nbsp;:&nbsp;&nbsp;`list_ollama_local()` e devolve a tag (`gemma3:4b`). <span style="color:#6a9955">Ollama offline → aviso e None. Chat não exige tools — gemma3 entra.</span>
- **`pick_xai()`**&nbsp;:&nbsp;&nbsp;sem `XAI_API_KEY` → ERRO e None. <span style="color:#6a9955">Com key, escolhe em `XAI_MODELS` e devolve `xai:grok-3` (o prefixo manda o factory pro xAI).</span>
- **`pick_openrouter()`**&nbsp;:&nbsp;&nbsp;sem `OPENROUTER_API_KEY` → ERRO e None. <span style="color:#6a9955">Com key, lista os nomes `open router: …` do catálogo.</span>
- **`get_chat_model(model)`**&nbsp;:&nbsp;&nbsp;chamado uma vez no começo da sessão. <span style="color:#6a9955">`RuntimeError` (key) volta ao menu sem traceback.</span>
- **comandos na sessão**&nbsp;:&nbsp;&nbsp;`/back` volta · `/exit` e `/quit` saem. <span style="color:#6a9955">Linha vazia é ignorada. A palavra `exit` sem barra vai pro modelo.</span>
- **ainda não**&nbsp;:&nbsp;&nbsp;streaming, salvar histórico em disco, trocar temperatura no meio do chat. <span style="color:#6a9955">Temperatura = `.env` e reabre o app.</span>

## Resumo

Menu de 3 provedores, depois um loop de mensagens com memória só na sessão. Sem key, xAI e OpenRouter avisam e voltam. Sem tools.
