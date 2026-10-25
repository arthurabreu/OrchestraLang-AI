# OrchestraLang AI — instruções para agentes (Cursor e outros)

Mesmo contexto que `CLAUDE.md`. Cursor e modelos do workspace leem este arquivo como orientação de projeto.

## O que é

Estudo de LangChain 1.x construindo agentes úteis. **Não** monólito tipo repos antigos (`orchestra-ai-agno`, `fsociety`, …).

- Stack: Python ≥3.11, `uv`, LangChain ≥1.0, **Ollama local default**, OpenRouter free / Grok(xAI) pra comparação
- Pacote: `src/orchestralang/` · CLI: `uv run orchestralang …`

## Estado — leia antes de editar

**Fase Chat** no ar: `uv run orchestralang` — local / xAI / OpenRouter, multi-turn. Sem key falha claro. Notas: `docs/src/orchestralang/chat.md`.  
O hello (`get_time` / `run hello`) foi removido.  
Também: `config` / `models` / `llm` + CLI `ping` / `models-ollama` / `models-openrouter`. Konsole: `scripts/dev/` (notas em `docs/scripts/dev.md`).

- Estudo por arquivo: `docs/src/` (espelho de cada `.py` sob `src/` — **tracked**)
- Roadmap + checklist: `docs/roadmap/learning-roadmap.md`
- Estudo por etapa: `docs/estudo/` — **árvore inteira local**, gitignored (inclui `README.md`)

**Não implementar a próxima fase até pedido explícito** (ex.: Fase 1 ADB).

## Code study docs (`docs/src/`)

Cada arquivo em `src/` tem gêmeo em `docs/src/` com mesmo path/nome e extensão `.md`.  
Ao criar/mudar um `.py` em `src/`, atualizar/criar o `.md` na **mesma** mudança. Ver `docs/src/README.md`.

## Sync trio (CLAUDE ↔ AGENTS ↔ Cursor `.mdc`)

Se pedirem pra atualizar `CLAUDE.md`, atualizar **também** este `AGENTS.md` e `.cursor/rules/orchestralang.mdc` com a mesma política/convenção. Nunca divergir os três.

## Git — commits / push / PR (só com pedido explícito)

**Nunca** `git commit`, `git push` ou `gh pr create` sem Tao pedir explicitamente.  
Implementar e deixar working tree sujo (ou só staged se ajudar revisão). Tao revisa antes; commit/push/PR só com ok dele.

Quando Tao pedir commit: Conventional Commits — `tipo: frase curta` (PT/EN; preferir PT curto).  
Tipos: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `style`, `perf`, `ci`  
Exemplos: `feat: add hello agent with create_agent` · `docs: mirror llm.py study notes`

## Git — branches

- `feat|fix|docs|chore|refactor|test/nome-curto-kebab`
- Branch a partir de `main` (local ok pra isolar); **push / PR só se Tao pedir**
- Sem nomes aleatórios; após bootstrap, sem commit de feature direto em `main`

## Arquitetura (SOLID + Clean — pragmático)

- Um agente = um job; tools testáveis sem LLM
- Abstrações nas bordas (`llm` factory, tools) — não hardcodar provider no agente
- CLI fino; domínio/tools separados do wiring LangChain
- Módulos pequenos; estender com tools/agentes novos, não mega-arquivos
- Leve — sem cerimônia enterprise

## Study notes `docs/estudo/`

Árvore `docs/estudo/` inteira local/gitignored (inclui `README.md`). Permanente: `docs/src/**` (tracked). Specs: `specs/` (tracked quando existirem). Env (`.env`, `.env.*`, inclusive `.env.example`) nunca no git. `uv.lock` e `.cursor/` locais.

## Regras de ouro

- Um agente = um job; tool first; spec antes de código
- Vertical slice utilizável; local por padrão
- Não portar código morto dos monólitos antigos
- Secrets em `.env` apenas; keepers Ollama nunca `rm` (lista em `models.OLLAMA_KEEPERS` / roadmap)
- Prefixo OpenRouter: `open router: <id>`

## Comandos úteis

```bash
uv sync
uv run pytest
uv run orchestralang                   # chat: 1 local / 2 xAI / 3 OpenRouter
uv run python scripts/dev/start.py    # Konsole: chat + ollama
uv run orchestralang models-ollama
uv run orchestralang models-openrouter
uv run orchestralang ping                 # OLLAMA_MODEL
uv run orchestralang ping "open router: openrouter/free"
```

## Processo

código (+ pytest tools sem LLM) → teste manual → MD **local** `docs/estudo/fase-N-….md` (não commit) (+ espelho `docs/src/` se tocou `.py`)

Detalhe completo: `CLAUDE.md` e `docs/roadmap/learning-roadmap.md`.
