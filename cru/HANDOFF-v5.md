# OrchestraLang AI — handoff `tests/v5` (estudo LangChain 1.x)

Você é o agente de coding neste repo. Tao = senior (aprende rápido). Ritmo = o de v3/v4: **um experimento claro por vez**, arquivo novo, ele testa manual, confirma, commit msg sob pedido, próximo. Não infantilizar; não monólogo; não expandir o app principal sem pedido.

Responder em **português**, direto. Caveman/fragments ok se a sessão estiver em modo caveman; código e commits = normal.

Objetivo do estudo (não é mais “conhecer param”): Tao quer **montar agentes e mini-sistemas** em Python com LangChain 1.x — scripts que ele consiga explicar e repetir. Emprego um dia é consequência disso; não desviar pra currículo, RAG gigante ou multi-agente.

## Hard limits (repo)

- Branch de estudo local: criar `tests/v5` off `tests/v4` (padrão `tests/vN`). **Commit / push / PR só se Tao pedir.**
- **Não** expandir Fase 1+ do app (`uv run orchestralang`) sem pedir. Hoje o app principal nem tem `src/`; o estudo mora em `cru/`.
- Env (`.env*`) fora do git. Sem `ollama rm` nos keepers.
- Docs LangChain: Context7 `libraryId=/websites/langchain`, `language=Python`, uma query por conceito. Preferir Context7 a chute de treino. **Não editar** `.venv/.../langchain/agents/factory.py` — só ler a assinatura e passar kwargs nos labs.
- Ao mudar `src/`: espelho `docs/src/` na mesma mudança. Pasta `cru/` = brinquedo — **não** exige espelho `docs/src`.
- Sync trio CLAUDE/AGENTS/orchestralang.mdc só se pedirem atualizar regras.

## Como estudamos (estilo obrigatório)

0. **Útil acima de tudo.** Cada passo deste handoff e de todo `HANDOFF-vN` novo simula um problema que aparece ao montar um agent de verdade. Tao tem que conseguir copiar o padrão na próxima tool que escrever. Lab pequeno ok. Problema fictício não. Proibido mascote (`bomba` da v4: veto de uma tool que não existiria em produção). Teste antes de codar: "eu usaria isso num agent real?" Se a resposta for não, reescrever a lição. Referência boa: `cru/v5/mw_caso_real.py` — input ruim, tool estoura, middleware traduz, processo segue.
1. **Brinquedo em `cru/`**, não produção. Scripts pequenos, rodam sozinhos. O cenário é real; o script é curto.
2. **Um arquivo novo por lição.** Layout:
   - `cru/models.py` — shared (`Model` StrEnum)
   - `cru/v1/` … `cru/v4/` — fechados
   - Novos de v5 → **`cru/v5/`**
3. Imports de subpasta: no topo, path hack curto pro parent `cru/`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import Model
```

4. **Comentários-cola PT** no topo: a pergunta que a lição responde, o contraste com a lição anterior, um exemplo concreto. Se a lição juntar 3 ideias, Tao não entende — uma ideia nova por arquivo. Arquivo “mapa” extra só se ele pedir de novo.
5. **Tools testáveis sem LLM** (`assert tool.invoke(...)`) antes do agent.
6. Print didático da trilha (`messages`, interrupt, store).
7. **`# RESULTADO:`** no fim — Tao cola o output. Você **não** inventa. Cada linha do bloco colado tem que ser comentário `#`, senão o `.py` não compila (já quebrou em v4).
8. Modelo default: Ollama `ChatOllama` + `Model.QWEN3_8B`, `temperature=0`, `reasoning=False`. Tool call falhou → FAIL didático (troca Model / reforça prompt), não panic.
9. **Planejar → implementar só quando pedir → ele testa → msg de commit sob pedido → próximo.** Não rodar LLM por ele; o comando `uv run python …` basta. No fim de cada resposta, se o working tree estiver sujo (staged ou unstaged), entregar a msg de commit (`test: vN …`). Não commitar até pedir.
10. Se a lição diz “humano decide”, o script **espera** (`input`) ou o comentário deixa explícito que o código é o humano. Em v4 o HITL mandou `approve` sozinho e Tao achou que não tinha aprovado nada.

## O que já foi aprendido (não repetir como novidade)

### v1 `cru/v1/chat.py`

- `ChatOpenAI` → Ollama OpenAI-compat `http://127.0.0.1:11434/v1`
- invoke vs stream

### v2 `cru/v2/`

- `ChatOllama` nativo
- Multi-turn; amnésia sem `AIMessage` (`chat_v2.py`)
- `@tool` + `bind_tools` + loop manual (`tool_loop.py`) — sem `create_agent` de propósito
- `with_structured_output(Pydantic)` (`structured.py`)

### v3 `cru/v3/` — fechado

| | Lição | Arquivo |
|---|--------|---------|
| A | `create_agent` = loop automático; trilha Human→AI(tool)→Tool→AI | `agent_basic.py` |
| B | várias tools + roteamento; `reasoning=False` | `agent_tools.py` |
| C | `InMemorySaver` + `thread_id` | `agent_memory.py` |
| D | `agent.stream(stream_mode="updates"\|"messages")` | `agent_stream.py` |
| E | `response_format=ToolStrategy(Pydantic)` | `agent_structured.py` |

### v4 `cru/v4/` — fechado (branch `tests/v4`)

| Lição | Arquivo | Commit |
|--------|---------|--------|
| `context_schema` + `context=` no invoke. Crachá da corrida (user_id). Tool lê `ToolRuntime.context`. O modelo **não** vê o dataclass sozinho. ≠ checkpointer | `create_agent_schema.py` | `9b365ac` |
| middleware ≠ tool. `@before_model` / `@after_model` observam ou cortam (`jump_to="end"`). `@wrap_tool_call` pode vetar sem rodar a tool | `create_agent_middleware_simples.py`, `create_agent_middleware.py` | `1e7b98f` |
| HITL: `HumanInTheLoopMiddleware(interrupt_on=...)` + checkpointer. Pausa antes da tool; `Command(resume={"decisions": [...]})` no mesmo `thread_id`. `interrupt_before=["tools"]` existe na factory e para o nó inteiro — o lab usou o helper 1.x | `create_agent_interrupt.py` | `639fd1d` |
| `store=InMemoryStore()`. `put` / `get` por namespace+chave. Sobrevive a outro invoke **sem** checkpointer. ≠ histórico do fio | `create_agent_store.py` | `79f5de9` |

Estilo de commit: `test: v4 …` Conventional Commits, PT curto.

Mapa mental que Tao já tem — não reexplicar do zero:

| Peça | O que guarda |
|------|----------------|
| `messages` | o que o modelo lê nesta corrida |
| `checkpointer` + `thread_id` | histórico curto daquele fio |
| `context=` | crachá desta request (quem / tenant). Não persiste sozinho |
| `store` | fato entre fios (codinome, preferência) |
| middleware | seu código no caminho; o modelo não escolhe |
| HITL | pausa no checkpointer até um humano (ou o script) decidir |

## Objetivo agora — branch `tests/v5`

Parar de turistar parâmetro de `create_agent`. v4 deixou `state_schema`, `debug`, `name`, `cache`, `transformers` de lado **de propósito**: servem pouco pra montar um sistema agora.

v5 = três problemas que aparecem ao montar um agent de verdade:

1. Tool que **quebra** (input ruim) e o agent continua. Feito: `mw_caso_real.py`.
2. Atendimento longo: o ticket fica guardado, o modelo só relê o fim.
3. Um caixa pequeno que junta crachá + fio + saldo que pode falhar.

### Plano v5 (prioridade)

1. **Erro de tool** — `cru/v5/mw_caso_real.py`  
   `@wrap_tool_call` com `try/except` em volta de `handler(request)`. Exceção → `ToolMessage(content=..., tool_call_id=request.tool_call["id"])`.  
   Tool de estudo que dá `raise` num input ruim (dividir por zero, id inexistente). Assert sem LLM de que a tool estoura. Com agent: trilha tem `ToolMessage` de erro, **não** stack trace matando o processo.  
   Contraste: o veto da v4 recusa de propósito; aqui a tool falhou e o middleware traduz.  
   API (Context7, doc tools): `handle_tool_errors` + `create_agent(..., middleware=[...])`.

2. **Fio longo sem amnésia** — `cru/v5/trim_messages.py`  
   Problema real: agent de chat com tools. Cada chamada vira várias mensagens. O atendimento precisa ficar guardado (retomar, auditar, "o que pedi no começo"). O modelo não pode reler o fio inteiro toda vez: estoura janela, fica lento, responde com lixo antigo.  
   O que se copia: checkpointer guarda o ticket completo. `trim_messages` (strategy `last`, teto de tokens ou contagem simples) manda ao modelo só o fim.  
   **Armadilha que quebra o agent de verdade:** devolver `{"messages": recorte}` num `before_model` pode **apagar** o ticket no state, não só a vista desta chamada. Antes de codar, Context7 numa query só: cortar o que o modelo vê **sem** destruir o baú. Print: baú cheio vs o que entrou no model.  
   Critério: o fato velho fica só no `get_tuple`. A resposta copia o fato novo, que está na janela. Pergunta cujo fato não está em mensagem nenhuma não serve: o modelo inventa e o lab parece quebrado.

3. **Um atendimento, não um param** — `cru/v5/caixa.py`  
   Caixa de loja, job único: quem é o cliente (`context` / user_id), o que ele já pediu neste atendimento (checkpointer no mesmo `thread_id`), saldo que pode falhar (middleware do item 1 — conta inexistente vira `ToolMessage`, não crash). Outro cliente = outro `thread_id`. Tool de saldo com assert sem LLM.  
   Sem store e sem HITL neste arquivo. Zero API nova. Tao sai com um script que já é um agent pequeno, não um tour de parâmetro.

### Se sobrar fôlego (não começar por aqui)

- `state_schema` só se o mini-sistema precisar de um campo extra no state (contador). Não como lab solto.
- Teste da **trilha** sem LLM (modelo falso), se a API Python existir — Context7 `testing agents` antes de inventar `fakeModel` (o exemplo fácil da doc está em JS).

### NÃO meter em v5

- Multi-agente / deepagents / subagents
- Checkpointer SQLite/Postgres, RAG, vectorstore
- `debug` / `name` / `cache` / `transformers` como lição
- Refatorar app / Fase 1+ / portar monólito antigo
- Reexplicar context, middleware, HITL ou store como se fossem novos

### Formato de entrega (igual v4)

1. Arquivo novo em `cru/v5/` com cola PT + assert sem LLM + prints.
2. Run: `cd …/cru/v5 && uv run python <arquivo>.py`
3. Ok / FAIL didático.
4. Commit msg só quando pedir (`test: v5 …`).

## Onde estamos

1. Feito: `cru/v5/mw_caso_real.py`. Tao colou `# RESULTADO:`. Exit 0. Sem commit ainda.
2. Escrito: `cru/v5/trim_messages.py`. Context7 feito (`wrap_model_call` + `request.override`, corte transitório). Tao ainda não colou `# RESULTADO:`.
3. Próximo só quando pedir: lição 3 (`caixa.py`). Não editar até lá.
