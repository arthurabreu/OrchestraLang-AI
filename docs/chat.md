# `cru/chat.py` linha a linha

Este arquivo é um chat no terminal. Você escolhe **um** modelo Ollama na hora de rodar. O programa fica perguntando `you> ` até você sair.

```bash
uv run python cru/chat.py qwen3:8b
```

`qwen3:8b` cai em `sys.argv[1]`. Sem esse nome, o script só imprime a lista e termina.

## O arquivo

```python
import sys

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from models import MODELS

if len(sys.argv) < 2:
    print("falta o modelo. cole um destes:")
    for name in MODELS:
        print(name)
    print("uv run python cru/chat.py qwen3:8b")
    raise SystemExit(2)

nome = sys.argv[1]

llm = ChatOpenAI(
    model=nome,
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",
    temperature=0.2,
)

history = [SystemMessage(content="Responda curto, no idioma de quem fala.")]

while True:
    try:
        line = input("you> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if not line:
        continue
    if line in ("quit", "exit", "q"):
        break
    history.append(HumanMessage(content=line))
    out = llm.invoke(history)
    text = out.content if isinstance(out.content, str) else str(out.content)
    print(text)
    history.append(AIMessage(content=text))
```

## Cada linha

`import sys` — traz o módulo que lê a linha de comando. `sys.argv` é a lista do que você digitou depois de `python`.

`from langchain_core.messages import ...` — três tipos de mensagem. `SystemMessage` é a regra fixa do chat. `HumanMessage` é o que você escreveu. `AIMessage` é a resposta do modelo. A lista `history` guarda as três, em ordem.

`from langchain_openai import ChatOpenAI` — cliente OpenAI-compatível. Aqui aponta pro Ollama (`/v1`), não pra API da OpenAI. Sem menu, sem xAI, sem OpenRouter.

`from models import MODELS` — a tupla de tags em `cru/models.py` (`qwen3:8b`, `gemma3:4b`, `gemma4:e4b`, `ornith:9b`, `qwen3.5:9b`). O `import` funciona porque `uv run python cru/chat.py` coloca a pasta `cru/` no caminho do Python.

`if len(sys.argv) < 2:` — `argv[0]` é o caminho do script. O modelo seria `argv[1]`. Se a lista tem menos de 2 itens, você não passou modelo.

`print("falta o modelo...")` — avisa. Os dois `print` seguintes mostram cada tag e um comando pronto pra colar.

`raise SystemExit(2)` — fecha o programa na hora. Código 2 = faltou argumento. O `while` lá embaixo não roda.

`nome = sys.argv[1]` — a tag, por exemplo `gemma3:4b`. Um processo, um modelo. Pra trocar, saia e rode de novo.

`llm = ChatOpenAI(...)` — cria o cliente. `model` é a tag. `base_url` termina em `/v1` (API compatível OpenAI do Ollama). `api_key="ollama"` é placeholder: o SDK OpenAI exige chave, o Ollama local ignora. `temperature=0.2` deixa a resposta mais estável. Sem `.env`.

`history = [SystemMessage(...)]` — o histórico começa com uma frase só. Tudo que você e o modelo disserem entra nessa lista.

## O loop `you>`

`while True:` — repete para sempre. Só para com `break` (sair). Outro erro do modelo (Ollama fora, etc.) ainda aparece no terminal.

`try:` / `line = input("you> ").strip()` — mostra `you> ` e espera texto. `strip()` tira espaços e a quebra de linha das pontas.

`except (EOFError, KeyboardInterrupt):` — Ctrl-D (fim de arquivo) ou Ctrl-C. `print()` solta uma linha vazia pra o terminal não ficar grudado. `break` sai do `while` e o processo acaba.

`if not line: continue` — Enter sozinho vira string vazia. `continue` volta pro `you>` sem chamar o modelo.

`if line in ("quit", "exit", "q"): break` — essas três palavras encerram. Não vão pro histórico.

`history.append(HumanMessage(content=line))` — guarda a sua frase no fim da lista.

`out = llm.invoke(history)` — manda a lista inteira (regra + conversa até agora). Por isso o modelo “lembra” o que já foi dito neste processo. Sair do programa apaga a lista.

`text = out.content if isinstance(out.content, str) else str(out.content)` — a resposta costuma ser texto. Se vier outra forma, vira texto do mesmo jeito.

`print(text)` — mostra a resposta, sem prefixo.

`history.append(AIMessage(content=text))` — guarda a resposta. Na próxima volta, `invoke` recebe você + modelo de novo. Aí o `while` volta pro `you>`.
