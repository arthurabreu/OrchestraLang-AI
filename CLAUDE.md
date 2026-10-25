# OrchestraLang AI

Projeto de estudo: aprender LangChain 1.x **construindo** agentes úteis (não monólito).  
Dono: Tao. Pasta: `~/Documentos/py/OrchestraLang AI`.

## Stack

- Python ≥3.11, gerenciador **`uv`**
- LangChain ≥1.0 (`create_agent`, `@tool`)
- LLM default: **Ollama local** (`OLLAMA_MODEL`, ex. `qwen3:8b`)
- Comparação: OpenRouter `:free` (prefixo de display `open router: `) e Grok/xAI (`XAI_API_KEY`) — **não** OpenAI como provedor principal
- Pacote: `src/orchestralang/` · CLI: `uv run orchestralang …`

## Estado atual (importante)

Há **Fase Chat**: `uv run orchestralang` — 1 Ollama / 2 xAI / 3 OpenRouter, multi-turn (`/back`, `/exit`). Sem key, xAI e OpenRouter falham claro.  
O hello (`get_time` / `run hello`) foi removido.  
Também: `config` / `models` / `llm` + CLI `ping` / `models-ollama` / `models-openrouter`. Launcher: `scripts/dev/` (`uv run python scripts/dev/start.py`).

- Estudo por arquivo (espelho de `src/`): `docs/src/` (**versionado**)
- Roadmap + checklist: `docs/roadmap/learning-roadmap.md`
- Notas por etapa: `docs/estudo/` — **árvore inteira local**, gitignored (inclui `README.md`)

**Não escreva a próxima fase de código até Tao pedir** (ex.: Fase 1 ADB).

## Code study docs (`docs/src/`)

Todo arquivo sob `src/` tem gêmeo sob `docs/src/` com o **mesmo caminho/nome** e extensão `.md`, explicando o módulo pra aprender (propósito, entrada→saída, detalhes, o que ainda não faz).

- Ex.: `src/orchestralang/llm.py` → `docs/src/orchestralang/llm.md`
- Convenção: `docs/src/README.md`
- **Ao adicionar/alterar** um `.py` em `src/`, criar/atualizar o `.md` correspondente **na mesma mudança**.

## Sync trio (CLAUDE ↔ AGENTS ↔ Cursor `.mdc`)

Sempre que Tao (ou um agente) pedir pra **atualizar o CLAUDE.md**, atualizar **também** `AGENTS.md` e `.cursor/rules/orchestralang.mdc` com as **mesmas** mudanças de convenção/política. Os três ficam alinhados — nunca só um.

## Git — commits / push / PR (só com pedido explícito)

**Nunca** `git commit`, `git push` ou `gh pr create` (nem equivalente) **sem Tao pedir explicitamente**.  
Agente implementa e deixa working tree sujo (ou só staged se ajudar a revisão). Tao revisa o código primeiro; commit/push/PR só depois do ok dele.

Quando Tao pedir commit: Conventional Commits — `tipo: frase curta` (PT ou EN; preferir frase curta em português).

Tipos: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `style`, `perf`, `ci`

Exemplos:
- `feat: add hello agent with create_agent`
- `docs: mirror llm.py study notes`
- `chore: bootstrap OrchestraLang AI with conventions and model scaffold`

## Git — branches

- `feat/nome-curto-kebab`
- `fix/nome-curto-kebab`
- `docs/nome-curto-kebab`
- `chore/nome-curto-kebab`
- `refactor/nome-curto-kebab`
- `test/nome-curto-kebab`

Preferir branch a partir de `main`. Branch local ok pra isolar trabalho; **push / PR só se Tao pedir**.  
Sem nomes aleatórios. Depois do bootstrap, **não** commit direto em `main` pra features (bootstrap/primeiro commit pode ir em `main`).

## Arquitetura (SOLID + Clean — pragmático)

Learning repo: o bastante pra não virar vibe-code monstro; **sem** cerimônia enterprise.

- Um agente = um job; tools testáveis **sem** LLM
- Dependência de abstrações nas bordas (factory `llm`, tools) — não hardcodar provider dentro do agente
- CLI fino; domínio/tools separados do wiring LangChain
- Módulos pequenos; sem god-classes; estender via novas tools/agentes, não mega-arquivos

## Princípios (anti-monstro)

1. Um agente = um job.
2. Tool first — valor nas tools, não no prompt.
3. Spec curta antes de código (`specs/`).
4. Vertical slice: cada fase roda no terminal e serve de verdade.
5. Não portar código morto dos repos antigos (`orchestra-ai-agno`, `fsociety`, `Orchestra-AI`, …). Ideias sim; arquitetura/código, não.
6. Local por padrão; API paga só se local falhar no job (tool calling fraco, etc.).
7. Python “mínimo” — só o que a próxima tool exigir.

## Layout alvo

```text
src/orchestralang/
  config.py, llm.py, cli.py, models.py
  agents/<nome>/     # um job por pasta
  tools/             # tools testáveis sem LLM
tests/
specs/               # contrato do agente (não diário de estudo)
docs/src/            # espelho .md de cada .py sob src/
docs/estudo/         # notas locais/efêmeras por etapa (árvore inteira gitignored)
docs/roadmap/        # plano + checklist de progresso
specs/               # contrato do agente (versionado quando existir)
```

## Study notes `docs/estudo/`

- **Temporárias** — aprendizado da etapa, escritas no fim do estágio
- **Árvore inteira gitignored** — inclui `README.md`; nada de `docs/estudo/` entra no git
- Estudo permanente de módulos: `docs/src/**` (**tracked**)
- Specs: `specs/` (**tracked** quando existirem)
- `.cursor/` local (não versionado). `uv.lock` local (não versionado)

## Convenções de código

- Preferir type hints; `from __future__ import annotations`.
- Factory de modelo: `get_chat_model(name)` em `llm.py`.
- OpenRouter free: nomes `open router: <provider/model:free>`; IDs em `models.OPENROUTER_FREE_IDS`.
- Arquivos de env (`.env`, `.env.*`, inclusive `.env.example`) **nunca** no git. Keys só no `.env` local.
- Comandos: `uv sync`, `uv run pytest`, `uv run orchestralang` (chat), `uv run python scripts/dev/start.py` (Konsole), `uv run orchestralang ping`, `uv run orchestralang models-ollama`, `uv run orchestralang models-openrouter`.

## Processo por etapa

1. Spec (se agente) → código  
2. pytest das tools **sem** LLM quando der  
3. Teste manual documentado (comando + resultado)  
4. MD **local** em `docs/estudo/fase-N-….md` (não versionar)  
5. Se tocou `.py` em `src/`: atualizar espelho em `docs/src/`

## Ollama keepers — NUNCA `ollama rm`

`nomic-embed-text:latest`, `gemma3:4b`, `qwen3:8b`, `gemma4:e4b`, `ornith:9b`, `qwen3.5:9b`  
Refresh = `ollama pull <modelo>` (não existe `ollama update`).

## Idioma

Respostas e docs do projeto em **português** (código/comentários podem misturar PT/EN curto; nomes de API em inglês).
