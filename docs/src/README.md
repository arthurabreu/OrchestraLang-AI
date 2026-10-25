# Espelho de estudo — `docs/src/` ↔ `src/`

Cada arquivo `.py` sob `src/` tem um gêmeo `.md` aqui, **mesmo caminho e nome**, só a extensão muda.

| Fonte | Estudo |
| --- | --- |
| `src/orchestralang/llm.py` | `docs/src/orchestralang/llm.md` |
| `src/orchestralang/cli.py` | `docs/src/orchestralang/cli.md` |
| … | … |

## Por quê

- Ler o módulo **sem** abrir só o código: propósito, entrada→saída, o que ainda **não** faz.
- Separar **estudo por arquivo** (`docs/src/`) de **estudo por fase** (`docs/estudo/`) e de **spec de agente** (`specs/`).

## Quando atualizar

- Criou ou mudou um `.py` em `src/` → criar/atualizar o `.md` correspondente **na mesma mudança**.
- Remoção de `.py` → remover o `.md` espelho (ou deixar nota curta se a remoção for temporária).

## O que **não** vai aqui

- Diário de fase (Fase 0, 1, …) → `docs/estudo/`
- Contrato do agente → `specs/`
- Roadmap / checklist → `docs/roadmap/learning-roadmap.md`
