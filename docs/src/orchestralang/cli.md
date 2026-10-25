# `cli.py`

Fino. Sem args abre o chat. Os outros subcomandos só listam modelos ou mandam uma frase.

## Fluxo

1. **`main()`** sem argumentos importa `run_chat` e volta. É o `uv run orchestralang`.
2. Com argumentos, o `ArgumentParser` exige um subcomando:
   - **`chat`** — o mesmo `run_chat()`.
   - **`models-ollama`** — `list_ollama_local()` e imprime `nome\t(tools|sem tools|tools?)`. Offline → exit 1. A marca `tools` é informação do Ollama; o chat não chama tool.
   - **`models-openrouter`** — um nome `open router: …` por linha. Não chama a API.
   - **`ping [modelo] [--msg]`** — `get_chat_model` + um `invoke`. Imprime o texto. OpenRouter também escreve `(model=…)` no stderr.
3. **`_print_llm_error`** — qualquer erro vira `ERRO: …` e exit 1. Sem traceback.

## Marcado

- **classe**&nbsp;:&nbsp;&nbsp;nenhuma. <span style="color:#6a9955">O chat está em `chat.py`.</span>
- **default**&nbsp;:&nbsp;&nbsp;zero args = chat. <span style="color:#6a9955">Não há subcomando `run`.</span>
- **ainda não**&nbsp;:&nbsp;&nbsp;flags de temperatura na CLI. <span style="color:#6a9955">Isso é `LLM_TEMPERATURE` no `.env`.</span>

## Resumo

`uv run orchestralang` conversa. `ping` é uma frase só, para ver se o modelo responde.
