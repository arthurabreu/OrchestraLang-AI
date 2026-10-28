# =============================================================================
# LIÇÃO: store= — memória que atravessa a conversa
# =============================================================================
#
# PERGUNTA
# --------
# "Guardei um codinome num chat. Outro invoke, sem histórico, precisa ler
#  esse codinome. O checkpointer não serve: thread nova começa vazia."
#
# DUAS MEMÓRIAS
# -------------
# checkpointer (v3 C) = mensagens DESTE thread_id. Muda o fio, esquece.
# store (AQUI)        = gaveta compartilhada. namespace + chave + valor.
#                       Não é o chat. Qualquer invoke com o mesmo store lê.
#
# Este lab NÃO passa checkpointer de propósito.
# Invoke 2 não recebe as messages do invoke 1.
# O único jeito de achar "Tofu" é runtime.store.
#
# API
# ---
# store = InMemoryStore()          # RAM, some com o processo (igual o saver)
# create_agent(..., store=store)   # injeta em runtime.store nas tools
# store.put((namespace,), chave, dict)
# store.get((namespace,), chave) → Item.value ou None
#
# InMemoryStore não é produção. Postgres/Redis seria outro store com a
# mesma put/get. Fora deste lab.
# =============================================================================

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_ollama import ChatOllama
from langgraph.store.memory import InMemoryStore

from models import Model

NS = ("perfil",)
CHAVE = "tao"

store = InMemoryStore()

# --- sem LLM: a gaveta funciona sozinha ---
store.put(NS, "demo", {"codinome": "X"})
assert store.get(NS, "demo").value["codinome"] == "X"
store.delete(NS, "demo")
assert store.get(NS, "demo") is None
print("assert ok: put / get / delete no InMemoryStore")


@tool
def guardar_codinome(codinome: str, runtime: ToolRuntime) -> str:
    """Grava o codinome na memória longa (store), não no chat."""
    runtime.store.put(NS, CHAVE, {"codinome": codinome})
    return f"guardado {codinome}"


@tool
def ler_codinome(runtime: ToolRuntime) -> str:
    """Lê o codinome da memória longa. Não inventa."""
    item = runtime.store.get(NS, CHAVE)
    if item is None:
        return "vazio"
    return f"codinome={item.value['codinome']}"


llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)

# sem checkpointer: cada invoke só vê as messages que você passar agora
agent = create_agent(
    model=llm,
    tools=[guardar_codinome, ler_codinome],
    store=store,
    system_prompt=(
        "Para gravar um codinome, chame guardar_codinome. "
        "Para ler, chame ler_codinome. Não invente codinome. Responda curto."
    ),
)


def mostra(titulo: str, msgs: list) -> None:
    print(f"--- {titulo} ---")
    for i, msg in enumerate(msgs):
        kind = type(msg).__name__
        calls = getattr(msg, "tool_calls", None) or []
        print(f"  [{i}] {kind}: {getattr(msg, 'content', None)!r}")
        if calls:
            print(f"      tool_calls: {calls}")


print("\n=== 1) grava, sem thread_id ===")
gravou = agent.invoke(
    {"messages": [{"role": "user", "content": "Guarde o codinome Tofu. Use a ferramenta."}]}
)
mostra("messages do invoke 1", gravou["messages"])
item = store.get(NS, CHAVE)
print("  store agora:", None if item is None else item.value)

if item is None or item.value.get("codinome") != "Tofu":
    print("FAIL: store não ficou com Tofu. Modelo não chamou guardar_codinome?")
    raise SystemExit(0)
print("ok grava: Tofu está no store, não só no chat")

print("\n=== 2) outro invoke, messages novas, MESMO store ===")
print("  (não há checkpointer: o modelo não vê 'Guarde o codinome Tofu')")
leu = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Qual codinome está guardado? Use ler_codinome. Não invente.",
            }
        ]
    }
)
mostra("messages do invoke 2", leu["messages"])

# prova de que o chat não vazou: a pergunta do passo 1 não está nesta lista
textos = [str(getattr(m, "content", "")) for m in leu["messages"]]
if any("Guarde o codinome" in t for t in textos):
    print("FAIL: invoke 2 ainda tem a mensagem do invoke 1.")
    raise SystemExit(0)

tool_ler = next((m for m in leu["messages"] if type(m).__name__ == "ToolMessage"), None)
if tool_ler is None or "Tofu" not in str(tool_ler.content):
    print("FAIL: ler_codinome não devolveu Tofu. Troca Model / reforça prompt.")
else:
    print("ok: invoke 2 não tem o chat anterior e mesmo assim leu Tofu no store.")
    print("checkpointer = histórico do fio. store = fato que sobrevive ao fio.")

# RESULTADO:
# assert ok: put / get / delete no InMemoryStore

# === 1) grava, sem thread_id ===
# --- messages do invoke 1 ---
#   [0] HumanMessage: 'Guarde o codinome Tofu. Use a ferramenta.'
#   [1] AIMessage: ''
#       tool_calls: [{'name': 'guardar_codinome', 'args': {'codinome': 'Tofu'}, 'id': '558a67b3-c474-4ee5-9a64-3db2dff9e1ae', 'type': 'tool_call'}]
#   [2] ToolMessage: 'guardado Tofu'
#   [3] AIMessage: 'O codinome Tofu foi guardado.'
#   store agora: {'codinome': 'Tofu'}
# ok grava: Tofu está no store, não só no chat

# === 2) outro invoke, messages novas, MESMO store ===
#   (não há checkpointer: o modelo não vê 'Guarde o codinome Tofu')
# --- messages do invoke 2 ---
#   [0] HumanMessage: 'Qual codinome está guardado? Use ler_codinome. Não invente.'
#   [1] AIMessage: ''
#       tool_calls: [{'name': 'ler_codinome', 'args': {}, 'id': 'a3b563e1-5038-4d14-bf1f-424f75493b8a', 'type': 'tool_call'}]
#   [2] ToolMessage: 'codinome=Tofu'
#   [3] AIMessage: 'O codinome guardado é Tofu.'
# ok: invoke 2 não tem o chat anterior e mesmo assim leu Tofu no store.
# checkpointer = histórico do fio. store = fato que sobrevive ao fio.