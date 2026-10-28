# OrchestraLang AI — handoff `tests/v4` (estudo LangChain 1.x)

Você é o agente de coding neste repo. Tao = senior (aprende rápido). Ritmo = o de v3: **um experimento claro por vez**, arquivo novo, ele testa manual, confirma, commit msg sob pedido, próximo. Não infantilizar; não monólogo; não expandir o app principal sem pedido.

Responder em **português**, direto. Caveman/fragments ok se a sessão estiver em modo caveman; código e commits = normal.

## Hard limits (repo)

- Branch de estudo local: criar `tests/v4` off `tests/v3` (padrão `tests/vN`). **Commit / push / PR só se Tao pedir.**
- **Não** expandir Fase 1+ do app (`uv run orchestralang`) sem pedir.
- Env (`.env*`) fora do git. Sem `ollama rm` nos keepers.
- Docs LangChain: Context7 `libraryId=/websites/langchain`, `language=Python`, uma query por conceito. Preferir Context7 a chute de treino.
- Ao mudar `src/`: espelho `docs/src/` na mesma mudança. Pasta `cru/` = brinquedo de estudo — **não** exige espelho `docs/src` salvo regra mudar.
- Sync trio CLAUDE/AGENTS/orchestralang.mdc só se pedirem atualizar regras.

## Como estudamos (estilo obrigatório)

1. **Brinquedo em `cru/`**, não produção. Scripts pequenos, rodam sozinhos.
2. **Um arquivo novo por lição.** Se precisar de >1 arquivo da mesma lição → subpasta. Layout atual:
   - `cru/models.py` — shared (`Model` StrEnum)
   - `cru/v1/`, `cru/v2/`, `cru/v3/` — por branch
   - Novos de v4 → **`cru/v4/`**
3. Imports de subpasta: no topo, path hack curto pro parent `cru/`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import Model
```

4. **Comentários-cola PT** no topo + inline: conceito curto + exemplo concreto (ver `cru/v3/*.py`).
5. **Tools testáveis sem LLM** (`assert tool.invoke(...)`) antes do agent.
6. Print didático da trilha (`messages`, nós do stream, bau do checkpointer).
7. **`# RESULTADO:`** no fim do arquivo (comentário) — Tao cola o output real do terminal depois do teste. Você **não** inventa RESULTADO; ele preenche. Pode deixar placeholder `RESULTADO:` vazio ou omitir até ele colar.
8. Modelo default estudo: Ollama `ChatOllama` + `Model.QWEN3_8B`, `temperature=0`. Qwen3: preferir `reasoning=False` (senão “trava” pensando). Se tool_calls falhar → troca Model / reforça prompt (FAIL didático, não panic).
9. Fluxo de trabalho: **planejar → implementar só quando pedir → ele testa → confirma → msg de commit sob pedido → próximo.** Ask mode = só instruir; Agent = editar.
10. Não rodar LLM pra ele a menos que peça; comando `uv run python …` basta.

## O que já foi aprendido (não repetir como “novidade”)

### v1 (`cru/v1/chat.py`)

- ChatOpenAI → Ollama OpenAI-compat `http://127.0.0.1:11434/v1`
- Sampling + invoke vs stream

### v2 (`cru/v2/`)

- `ChatOllama` nativo + `top_k`
- Multi-turn lista System/Human/AI; amnésia sem AIMessage (`chat_v2.py`)
- `@tool` + `bind_tools` + loop manual (`tool_loop.py`) — sem create_agent de propósito
- `with_structured_output(Pydantic)` (`structured.py`) — Field = dica, não hard limit

### v3 (`cru/v3/`) — fechado A–E

| | Lição | Arquivo |
|---|--------|---------|
| A | `create_agent` = loop do tool_loop automático; trilha Human→AI(tool)→Tool→AI | `agent_basic.py` |
| B | várias tools + roteamento (soma/multiplica/subtrai); `reasoning=False` | `agent_tools.py` |
| C | `InMemorySaver` + `thread_id`; `mostra_bau` via `checkpointer.get_tuple` | `agent_memory.py` |
| D | `agent.stream(stream_mode="updates"|"messages")` | `agent_stream.py` |
| E | tools + `response_format=ToolStrategy(Pydantic)` → `structured_response` | `agent_structured.py` |

Commits recentes em `tests/v3` (referência de estilo msg): `test: v3 …` Conventional Commits, PT curto.

## Objetivo agora — branch `tests/v4`

Continuar LangChain 1.x **um passo além de v3**, foco: **explorar superfície de API** que ainda não tocamos — especialmente parâmetros de `create_agent` e afins — com o mesmo formato de micro-labs.

### `create_agent` — params ainda pouco/não explorados (priorizar)

Assinatura atual (venv do projeto):

```text
create_agent(
  model, tools=None, *,
  system_prompt=None,
  middleware=(),
  response_format=None,      # já em v3 E
  state_schema=None,
  context_schema=None,
  checkpointer=None,         # já InMemorySaver em v3 C
  store=None,                # memória longa / cross-thread — novo
  interrupt_before=None,     # HITL — novo
  interrupt_after=None,
  debug=False,
  name=None,
  cache=None,
  transformers=None,
)
```

### Plano v4 sugerido (prioridade — ajustar com Context7 + Tao)

1. **`context_schema` + `context=` no invoke** — dados por-run (user_id etc.) legíveis por tools/middleware; ≠ checkpointer.
2. **`middleware` mínimo** — 1 middleware didático (ex. log/contar model calls, ou bloquear tool); lição: middleware ≠ tool.
3. **`interrupt_before` / HITL** — pausa antes de tools; resume; print estado. (cuidado: manter brinquedo, 1 fluxo).
4. **`store` (BaseStore)** — memória cross-thread vs checkpointer short-term (contraste com v3 C).
5. **Extras se sobrar fôlego:** `state_schema` custom; `ProviderStrategy` vs `ToolStrategy` (já usamos Tool); `stream_events` / outros `stream_mode`; `debug=True` / `name=`; `cache=`.

### NÃO meter em v4 (ainda)

- Multi-agente / deepagents / subagents pesados
- Checkpointer SQLite/Postgres “produção”
- RAG / vectorstore (salvo Tao pedir)
- Refatorar app `src/` / Fase 1+
- Portar monólitos antigos vibe-coded

### Formato de entrega por lição (igual v3)

1. Checklist curto do que v3 já cobriu (1 linha cada) se Tao pedir confirmação.
2. Arquivo novo em `cru/v4/…` com cola PT + asserts + prints.
3. Instrução de run: `cd …/cru/v4 && uv run python <arquivo>.py`
4. Critério de ok / FAIL didático.
5. Msg de commit só quando pedir (`test: v4 …`).

## Primeira ação nesta sessão

1. Confirmar branch: criar/checkout `tests/v4` off `tests/v3` (local).
2. Consultar Context7: **um** conceito — preferir `create_agent context_schema` **ou** `middleware` (o que Tao escolher; default = **context_schema** se ele disser só “go”).
3. Implementar **só o experimento #1** em `cru/v4/` (não A–E de uma vez).
4. Parar e deixar Tao testar + colar RESULTADO.

Não editar código até Tao pedir implementação (“go”, “faz X”). Se a mensagem já for “go” / “faz v4”, começar pelo experimento #1 acima.
