# OrchestraLang AI — plano de estudo e desenvolvimento

Plano para aprender LangChain 1.x **construindo** OrchestraLang AI (agentes úteis), sem repetir os monólitos vibe-coded (`orchestra-ai-agno`, `fsociety`, `Orchestra-AI`, `apps-with-langchain`).

Pasta do projeto: `~/Documentos/py/OrchestraLang AI`  
Stack alvo: Python 3.11+, LangChain ≥1.0 (hoje ~1.3), `create_agent`, **Ollama local por padrão**, OpenRouter free / **Grok (xAI)** como opções de comparação (não OpenAI).

---

## Princípios (anti-monstro)

1. **Um agente = um job.** Nada de “Orchestra” genérica no dia 1.
2. **Tool first.** O valor está nas tools (ADB, arquivos, APIs), não no prompt.
3. **Spec antes de código.** Prompt solto → spec curta (objetivo, inputs, tools, critérios de “pronto”) → só então implementar.
4. **Vertical slice.** Cada fase entrega algo que você roda no terminal e usa de verdade.
5. **Herdar depois.** “Agente master + RAG por agente” só depois de 2–3 agentes úteis sozinhos.
6. **Não portar código morto** dos repos antigos. Ideias sim; arquitetura e código, não.
7. **Local por padrão.** Ollama; API paga (**Grok / xAI**) só quando o modelo local falhar no job (tool calling fraco, etc.). OpenRouter `:free` = comparação barata antes de pagar.
8. **Aprender construindo.** Foco em OrchestraLang AI — Python “mínimo” só o que a próxima tool exigir.

---

## Checklist de progresso

Marque com `[x]` quando a fatia estiver fechada (código + teste manual + MD de estudo, quando a fase exigir). Itens grosseiros — uma linha por fase.

- [x] **Scaffold precoce** — pacote `src/orchestralang/` (`config`, `models`, `llm`, CLI `ping` / `models-openrouter`); sem `create_agent`
- [x] **Convenções de estudo** — espelho `docs/src/` ↔ `src/`; sync trio `CLAUDE.md` / `AGENTS.md` / `.cursor/rules/orchestralang.mdc`
- [x] **Etapa Ollama** — inventário → `pull` keepers → smoke `ollama run` → `rm` só extras quebrados (nunca keepers)
- [ ] **Fase 0 — Hello agent** — `create_agent` + 1 tool (`get_time`/`echo`); `orchestralang run hello …`
  - [ ] código + pytest (tool sem LLM)
  - [ ] teste manual documentado
  - [ ] MD em `docs/estudo/`
- [ ] **Fase 1 — Agente ADB Android** — tools allowlist + dry-run `--plan`
- [ ] **Fase 2 — Inbox de ideias**
- [ ] **Fase 3 — Vertical de vida** (rotinas / nutrição / lugares — uma só)
- [ ] **Fase 4 — Desktop vision** (só ver → ver+clicar com HITL)
- [ ] **Fase 5 — Kotlin debug-log helper**
- [ ] **Fase 6 — Telecinese** (UI automation completa; depois harness maduro)
- [ ] **Fase 7 — Memória / RAG por agente**
- [ ] **Fase 8 — App cliente**
- [ ] **Fase séria** — Ambev / Mercantil / agents de trabalho (**só no fim**)

Estudo por arquivo do código atual: [`docs/src/`](../src/README.md).

---

## O que LangChain 1.x muda (o que estudar de verdade)

| Conceito | Por quê |
| --- | --- |
| `create_agent` | Loop modelo → tools → resposta (substitui `create_react_agent`) |
| `@tool` / tools tipadas | Interface entre LLM e o mundo (ADB, disco, HTTP) |
| `ChatOllama` / `init_chat_model` | Trocar local ↔ cloud sem reescrever o agente |
| Middleware | Guardrails, human-in-the-loop, sumarização (fase avançada) |
| Messages + streaming | Ver o agente pensar e chamar tools |

**Não estudar no começo:** LangGraph custom complexo, multi-agent orchestration, fine-tuning, “agente criador de RAG”, agents de trabalho Ambev/Mercantil.

---

## Trilha de aprendizado (intercalada com builds)

Foco: construir OrchestraLang. Sem bloco de “Python mínimo” separado.

### LangChain 1.x core (junto com Agente 0 e 1)
- chat com Ollama sem agent
- um `@tool` e `create_agent`
- inspecionar `tool_calls` e mensagens
- trocar modelo (Ollama ↔ OpenRouter free ↔ Grok/xAI) via config

### Harness (depois de Agente 1 estável)
- system prompt curto e testável
- limites: allowlist de packages/paths/comandos ADB
- logs estruturados de cada tool call
- testes das tools **sem** LLM (pytest)

### Memória e RAG (só após 2 agentes)
- histórico de sessão (checkpointer / arquivo)
- um store simples por agente (começando com SQLite + embeddings)
- “agente configurador de RAG” fica no backlog / fase séria, não no MVP

---

## Arquitetura alvo (simples)

```text
OrchestraLang AI/
  pyproject.toml
  README.md
  .env.example          # OLLAMA_MODEL, OPENROUTER_API_KEY (nomes "open router: …"), XAI_API_KEY / GROK
  src/orchestralang/
    __init__.py
    config.py           # modelos, paths
    llm.py              # factory ChatOllama / OpenRouter / Grok(xAI)
    cli.py              # `orchestralang run <agent>`
    agents/
      adb_android/      # Agente 1
      ideas_inbox/      # Agente 2 (candidato)
      ...
    tools/              # tools reutilizáveis e testáveis
  tests/
  specs/                # uma spec .md por agente
```

Cada agente: `spec.md` + pasta própria + tools dedicadas. Sem framework de “herança de agentes” até memória/RAG.

---

## Etapa precoce — atualizar / verificar Ollama + escolher modelos

**Antes (ou logo ao lado) da Fase 0.** Política: **UPDATE + VERIFY** (não limpar slate / wipe-by-default).

Objetivo: inventário → **atualizar** LLMs locais com `ollama pull` → **garantir que carregam** (`ollama run` / smoke) → `ollama rm` **só** extras que falharem o load (nunca keepers) → planejar pulls novos só se faltar tool calling.  
**Nesta tarefa de planejamento: NÃO executar `ollama rm` / pulls.** Só documentar. Tao / sessão futura roda os comandos.

Ollama **não tem** `ollama update`. Refresh = `ollama pull <modelo>` (baixa revision nova se houver no registry).

### Protegidos — NUNCA deletar

Estes ficam no disco mesmo se algum teste falhar (aí debuga / re-puxa; **não** `rm`):

- `nomic-embed-text:latest`
- `gemma3:4b`
- `qwen3:8b`
- `gemma4:e4b`
- `ornith:9b`
- `qwen3.5:9b`

### 1) Verificar o que está instalado

```bash
ollama serve   # se o daemon estiver parado
ollama list
```

Inventário visto em disco em 2026-10-25 (daemon offline; manifests em `~/.ollama/models/manifests/` — confirmar com `ollama list` quando o serviço subir):

**Keepers (protegidos):**

- `nomic-embed-text:latest`
- `gemma3:4b`
- `qwen3:8b`
- `gemma4:e4b`
- `ornith:9b`
- `qwen3.5:9b`

**Extras (podem sair só se não carregarem):**

- `hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q8_0`
- `hf.co/DuoNeural/OpenYourMind-Gemma4-12B-IT-Abliterated-GGUF:Q5_K_M`
- `hf.co/tpls/gemma-4-12B-coder-fable5-composer2.5-v1-sft-v5-abliterated-GGUF:Q5_K_M`

### 2) Atualizar o que o registry permitir

```bash
# Library tags (keepers) — pull = refresh se houver versão nova
for m in nomic-embed-text:latest gemma3:4b qwen3:8b gemma4:e4b ornith:9b qwen3.5:9b; do
  ollama pull "$m"
done

# Extras hf.co — pull só se ainda quiser manter; senão pular pro smoke test
# ollama pull "hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q8_0"
# ...
```

### 3) Smoke test — garantir que carregam

```bash
# Embeddings
ollama run nomic-embed-text:latest "ping"   # ou API /api/embeddings

# Chat keepers — 1 prompt curto cada; se carregar + responde, OK
for m in gemma3:4b qwen3:8b gemma4:e4b ornith:9b qwen3.5:9b; do
  echo "=== $m ==="
  ollama run "$m" "diga ok em uma palavra"
done
```

- **Carrega?** → mantém. Sem wipe.
- **Keeper falha?** → anotar erro; tentar `ollama pull` de novo / checar VRAM/`ollama show`. **Não** `ollama rm` nos protegidos.
- **Extra (hf.co) falha e não importa?** → aí sim `ollama rm <nome>` e, se ainda precisar da capacidade, baixar substituto depois.

```bash
# Só extras quebrados / indesejados — NUNCA nos keepers:
# ollama rm "hf.co/..."
```

### 4) Candidatos a avaliar (atualizar lista depois)

**Ollama (pulls — priorizar tool calling estável):** keepers primeiro; pulls novos só se faltar.  
**OpenRouter free — já no projeto** (`OrchestraLang AI/src/orchestralang/models.py`). Nome de display = prefixo **`open router: `** + id. Key nova em `.env` → `OPENROUTER_API_KEY` (https://openrouter.ai/keys). **Atualizar lista depois** quando revisarmos catálogo.

| Nome (usar no agente / CLI) |
| --- |
| `open router: cohere/north-mini-code:free` |
| `open router: nex-agi/nex-n2-pro:free` |
| `open router: nvidia/nemotron-3.5-content-safety:free` |
| `open router: nvidia/nemotron-3-ultra-550b-a55b:free` |
| `open router: nvidia/nemotron-3-nano-30b-a3b-reasoning:free` |
| `open router: poolside/laguna-xs.2:free` |
| `open router: poolside/laguna-m.1:free` |
| `open router: google/gemma-4-26b-a4b-it:free` |
| `open router: google/gemma-4-31b-it:free` |
| `open router: nvidia/nemotron-3-super-120b-a12b:free` |
| `open router: liquid/lfm-2.5-1.2b-thinking:free` |
| `open router: liquid/lfm-2.5-1.2b-instruct:free` |
| `open router: nvidia/nemotron-3-nano-30b-a3b:free` |
| `open router: nvidia/nemotron-nano-12b-v2-vl:free` |
| `open router: qwen/qwen3-next-80b-a3b-instruct:free` |
| `open router: nvidia/nemotron-nano-9b-v2:free` |
| `open router: openai/gpt-oss-120b:free` |
| `open router: openai/gpt-oss-20b:free` |
| `open router: qwen/qwen3-coder:free` |
| `open router: cognitivecomputations/dolphin-mistral-24b-venice-edition:free` |
| `open router: meta-llama/llama-3.3-70b-instruct:free` |
| `open router: meta-llama/llama-3.2-3b-instruct:free` |
| `open router: nousresearch/hermes-3-llama-3.1-405b:free` |
| `open router: openrouter/free` |

```bash
uv run orchestralang models-openrouter
uv run orchestralang ping "open router: nousresearch/hermes-3-llama-3.1-405b:free"
```

Origem da lista: `orchestra-ai-agno/.../openrouter.py`. Detalhe: [internal/telecinese-and-models.md](../internal/telecinese-and-models.md).

**Pago (comparação, não default):** **Grok (xAI)** — isolar “bug do modelo” vs “bug da tool” quando Ollama/OpenRouter free falharem em tool calling.

---

## Roadmap de agentes (prioridade — fases de aprendizado)

### Fase 0 — Hello agent (1 sessão)
**Objetivo:** Ollama + `create_agent` + 1 tool inútil (`get_time` ou `echo`).  
**Aprende:** setup, invoke, ver tool call.  
**Pronto quando:** `uv run orchestralang run hello "que horas são?"` funciona.

### Fase 1 — Agente ADB Android (primeiro útil) ← começar aqui
**Objetivo:** bot que inspeciona e age em apps Android via `adb` (skill + tool clara).  
**Spec mínima:**
- Inputs: pedido em linguagem natural (“abre Settings e me diga o Wi‑Fi”)
- Tools (v1, allowlist):
  - `adb_devices`
  - `adb_shell` (comandos permitidos: `pm`, `am`, `input`, `dumpsys` subset)
  - `adb_screenshot` (pull + path local)
  - `adb_ui_dump` (uiautomator dump → texto/resumo)
- Fora do v1: clicar por coordenadas cegas sem dump; root; sideload
- Critérios: device conectado; cada ação logada; dry-run mode (`--plan`) que só propõe comandos

**Aprende:** subprocess, parsing, tools com schema, safety.  
**Pronto quando:** 3 tarefas reais (ex.: abrir app, ler texto na tela, tap via dump) passam.  
**Base local:** padrões de `telecinese-droid` (ver fase abaixo) — no v1, só o mínimo.

### Fase 2 — Agente de ideias (inbox)
**Objetivo:** salvar, categorizar e organizar ideias (WhatsApp → arquivo/Markdown).  
**Tools:** append note, list/search by tag, refile.  
**Aprende:** persistência local, structured output.  
Encaixa “agents do dia a dia” e alimenta depois um RAG.

### Fase 3 — Escolher UMA vertical de vida
Pick um (não três):
- **Rotinas** (checklist diário / lembretes em Markdown)
- **Nutrição** (registro de refeições + regras suas — não “coach médico”)
- **Lugares** (onde comer / ver paisagem — APIs de maps/places depois)

Entregar um agente fino, não um “life OS”.

### Fase 4 — Desktop vision (cuidado)
Dois modos explícitos:
1. **Só ver** — screenshot + descrever/analisar (baixo risco) — bots só-visão
2. **Ver + clicar** — só com confirmação humana / allowlist de apps

Depois do ADB estável; reaproveita o padrão de tools + safety.

### Fase 5 — Kotlin debug-log helper
Script/agente que propõe (ou aplica com review) `Log.d` em classes Kotlin.  
Bom segundo braço Android; pode ser tool do ADB agent ou CLI separado.

### Fase 6 — Agente estilo telecinese (UI automation completa)
**Quando:** depois Fase 1 estável e harness (allowlist, pytest, `--plan`) maduros — **não agora**.  
**Objetivo:** agent “telekinesis” que orquestra fluxos multi-step no Android (login, navegar, evidências).  
**Reusar de** `~/Documentos/py/telecinese-droid/`:
- `AdbDevice` → wrappers `@tool` (tap, tap_text, type, key, swipe, wait_*, launch, screenshot, elements, logcat)
- CLI como smoke test das tools sem LLM
- gotchas do README (WebView/MSAL, BACK, timing)
- `logcat_image` opcional (evidência PNG)
**Reinventar sob `create_agent`:** loop LLM, system prompt, HITL, dry-run, allowlist de packages; **não** portar fluxos de trabalho de empresa.  
Avaliação completa: [internal/telecinese-and-models.md](../internal/telecinese-and-models.md).

### Fase 7 — Memória / RAG por agente (aprendizado avançado)
- store por agente
- gravar resumos úteis de cada sessão
- “agente criador de RAG” e herança de master **só aqui**
- ainda **sem** agents de emprego — só infraestrutura

### Fase 8 — App cliente (depois)
App Android (ou TUI) para falar com o Orchestra.  
Só quando houver ≥2 agentes estáveis e uma API/CLI clara. Não começar pelo app.

---

## Fase séria / trabalho (TARDE — depois de tudo bem testado)

**Não agora.** Só depois de hello + ADB + pelo menos mais 1 agente útil + harness + (ideal) telecinese/RAG básicos estáveis.

| Ideia | Nota |
| --- | --- |
| **Agentes Ambev** | Jobs reais do trabalho; tasks diversas para stress-test de LLMs locais |
| **Agentes Mercantil** | Idem — segundo emprego; specs e allowlists separadas |
| Agents para **outros projetos Android / Python** | Mesmo padrão tool-first; um agent por fluxo |
| Fine-tuning (estudo) | Teórico; não bloqueia utilidade |
| Site de CV | **Fora de escopo** deste repo (Claude/Cursor / frontend separado) |

Ambev/Mercantil = mesmo padrão de tools + memória de domínio, **specs separadas**, nunca monólito “Orchestra trabalho”.

---

## Backlog completo (todas as ideias das notas)

Marcas: **aprendizado** = fases 0–8; **séria/trabalho** = só no fim; **fora** = outro projeto.

| Ideia | Onde | Marca |
| --- | --- | --- |
| ADB mexe em apps Android | Fase 1 | aprendizado |
| Inbox de ideias + categorias / organizar | Fase 2 | aprendizado |
| Lugares para sair / paisagem | Fase 3 | aprendizado |
| Rotinas do dia a dia | Fase 3 | aprendizado |
| Nutrição | Fase 3 | aprendizado |
| Helpers de vida cotidiana (outros) | Fase 3+ | aprendizado |
| Desktop ver / ver+clicar | Fase 4 | aprendizado |
| Bots só-visão para análise | Fase 4 | aprendizado |
| Debug logs automáticos em Kotlin | Fase 5 | aprendizado |
| Agente telecinese-droid (UI automation) | Fase 6 | aprendizado |
| RAG que aprende do histórico | Fase 7 | aprendizado |
| Cada agente com DB/RAG próprio | Fase 7 | aprendizado |
| Agente criador de RAG | Fase 7 | aprendizado |
| Herança de agente master | Fase 7 | aprendizado |
| App cliente Orchestra AI | Fase 8 | aprendizado |
| Spec-driven (prompt → spec) | processo contínuo desde Fase 1 | aprendizado |
| Agents Ambev (tarefas diversas / LLM local) | fase séria | **séria/trabalho** |
| Agents Mercantil | fase séria | **séria/trabalho** |
| Agents outros projetos Android/Python | fase séria | **séria/trabalho** |
| Fine-tuning (estudo) | pós utilidade | estudo tardio |
| Site de CV | — | **fora de escopo** |

---

## Fora deste projeto (por enquanto)

- Site de CV (Claude/Cursor) — projeto separado de frontend/conteúdo
- Fine-tuning — estudo teórico depois; não bloqueia utilidade
- Links/Instagram de inspiração — só se virarem spec concreta
- Qualquer fluxo Ambev/Mercantil **antes** das fases de aprendizado estarem sólidas

---

## Setup sugerido (Fase 0)

```bash
cd "~/Documentos/py/OrchestraLang AI"
uv init --package   # ou pyproject manual
uv add "langchain>=1.0" langchain-ollama python-dotenv
# depois, conforme precisar:
# uv add langchain-openrouter   # ou cliente OpenAI-compat p/ OpenRouter
# uv add langchain-xai          # Grok (xAI) — API paga de comparação
ollama pull <modelo-com-tool-calling>   # só se keepers não bastarem / tool calling fraco
```

`.env.example` (comentários alvo):

```bash
OLLAMA_MODEL=...                 # default local
# OPENROUTER_API_KEY=...         # free :free models (comparação)
# XAI_API_KEY=...                # Grok (xAI) — pago opcional; NÃO OpenAI
```

Modelo local: priorizar **tool calling** estável; se falhar, testar o mesmo agente com OpenRouter free e, se necessário, **Grok (xAI)** para isolar “bug do modelo” vs “bug da tool”.

---

## Processo de cada etapa

Vale **para toda fase daqui pra frente** (Fase 0, 1, 2, …). Uma etapa só fecha quando os três passos existem.

### 1. Código

- Implementar **só** o pedaço da fase (spec curta antes, se a fase tiver agente).
- Preferir tools/funções testáveis **sem LLM**.
- Pytest unitário das tools/funções puras (subprocess mockado, parsing, allowlist, etc.).
- LLM entra depois que a tool sozinha passa.

### 2. Teste manual

- Um cenário real documentado: **comando** + **resultado esperado** (e device/serviço necessário, ex. Ollama ou `adb devices`).
- Smoke do agente (`uv run orchestralang …`) conta; não substitui o pytest do passo 1.

### 3. MD de estudo (temporário / local)

- Escrever o que fizemos + 2–5 conceitos LangChain/Python da etapa.
- **Convenção:** MD em `docs/estudo/` (ex. `docs/estudo/fase-0-hello.md`) — **temporário e local**.
- **Não versionar** `docs/estudo/` inteiro (inclui `README.md`): a árvore é local e está no `.gitignore`.
- `specs/` = contrato do agente (objetivo, tools, critérios) — **tracked** quando existir. **Não** misturar diário de estudo com spec.
- Estudo permanente de módulos: `docs/src/` (espelho de `src/`) — **tracked**.

### Ritmo na sessão

1. Spec/`critério de pronto` da fatia atual (se couber).
2. Código + pytest.
3. Teste manual documentado.
4. MD **local** em `docs/estudo/` (não commit).

Se a sessão virar “refatorar arquitetura genérica”, parar — voltar ao critério de pronto da fase.

### Código precoce (Fase 0/1 vazada)

Já existe no repo um scaffold (`src/orchestralang/`: config, catálogo OpenRouter, factory LLM, CLI `ping` / `models-openrouter`) **sem** `create_agent` e **sem** agente ADB.  
**Fica.** Não apagar, não expandir “porque já começou”.  
Próximo trabalho consciente de código **só quando Tao pedir** a etapa. Até lá: só roadmap / estudo.

---

## Definição de sucesso (aprendizado)

- Você explica `create_agent` + tools sem ler doc.
- Agente ADB faz ≥3 tarefas reais no device.
- Inbox de ideias está em uso.
- Repo pequeno, testável, sem pasta `agents/` fantasma.
- Decisão consciente de quando subir para telecinese completa / RAG / (muito depois) Ambev·Mercantil.

---

## Próximo passo concreto

1. Etapa precoce (quando Tao pedir): subir Ollama → `ollama list` → `ollama pull` nos keepers → smoke `ollama run` → `rm` **só** extras quebrados (nunca os 6 protegidos) → pulls novos só se faltar + refrescar lista OpenRouter free.  
2. Scaffold mínimo de modelos/CLI **já está no repo** — ver `docs/src/`. Não recriar do zero.  
3. Próximo código consciente: só após pedido explícito — ex. `specs/adb-android.md` e/ou Fase 0 hello (`create_agent` + 1 tool) seguindo o **Processo de cada etapa** acima.
