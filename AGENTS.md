# OrchestraLang AI

Estudo LangChain 1.x: agentes úteis, anti-monólito. Python/`uv`, Ollama default, OpenRouter free (`open router: …`) e Grok/xAI opcional.

## LangChain docs (Context7) — obrigatório

Sempre que precisar de info sobre LangChain (API, sintaxe, agentes, tools, models, migração, exemplos) — **mesmo se achar que sabe** — consultar Context7. Treino pode estar desatualizado (LangChain 1.x muda rápido).

- **Library ID:** `/websites/langchain`
- **Fonte:** https://context7.com/websites/langchain/llms.txt?tokens=10000
- **Fluxo:** `query-docs` com `libraryId=/websites/langchain`, `language=Python`, query focada em **um** conceito. Preferir Context7 a web search para docs LangChain.
- Não chamar `resolve-library-id` se o ID acima já for o alvo; usar direto.

## Hard limits

- Estado: Fase Chat (`uv run orchestralang` — Ollama / xAI / OpenRouter). Hello removido. **Não expandir** (Fase 1+) sem Tao pedir.
- Não portar código dos repos antigos vibe-coded; ideias ok.
- Spec curta antes de agente novo; tools testáveis sem LLM; um agente = um job.
- Arquivos de env (`.env`, `.env.*`, inclusive `.env.example`) **nunca** no git. Nunca `ollama rm` nos keepers (`OLLAMA_KEEPERS`).

## Git

- **Nunca** `git commit` / `git push` / `gh pr create` sem Tao pedir explicitamente. Implementar → working tree sujo (ou só staged); Tao revisa primeiro.
- Quando Tao pedir commit: `tipo: frase curta` (Conventional Commits; PT/EN; preferir PT curto). Tipos: `feat` `fix` `docs` `chore` `test` `refactor` `style` `perf` `ci`.
- Branches: `feat|fix|docs|chore|refactor|test/nome-curto-kebab` off `main` (local ok). **Push / PR só se Tao pedir.** Sem commit de feature em `main` após bootstrap.

## Arquitetura (pragmática)

Abstrações nas bordas (`llm` factory, tools); CLI fino; domínio separado do wiring LangChain; módulos pequenos — sem god-classes / mega-arquivos.

## Code study docs (`docs/src/`)

Todo `.py` sob `src/` tem gêmeo `.md` sob `docs/src/` (mesmo path/nome) — **tracked**. Ao mudar código em `src/`, atualizar o espelho na mesma mudança. Índice: `docs/src/README.md`.

## Study notes `docs/estudo/`

Árvore `docs/estudo/` inteira **local/gitignored** (inclui `README.md`). Permanente: `docs/src/**` (tracked). Specs em `specs/` (tracked quando existirem). `uv.lock` e `.cursor/` locais — não versionar.

## Sync trio (CLAUDE ↔ AGENTS ↔ `.cursor/rules/orchestralang.mdc`)

Pedido pra “atualizar o CLAUDE.md” ⇒ atualizar **também** `AGENTS.md` e `orchestralang.mdc` com as mesmas regras. Manter os três sincronizados.

## Orientação

- Roadmap + checklist: `docs/roadmap/learning-roadmap.md`
- Instruções longas: `AGENTS.md` / `CLAUDE.md`
- Docs de fase: `docs/estudo/` local depois de código + teste manual (não versionar)
- Responder em português
