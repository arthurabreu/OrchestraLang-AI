# =============================================================================
# LIÇÃO: HITL — pausar ANTES da tool e retomar
# =============================================================================
#
# PERGUNTA
# --------
# "O modelo pediu pra pagar. Quero ver o valor e dizer sim ANTES da função
#  pagar() rodar. Como o agent dorme e acorda?"
#
# DOIS BOTÕES NA FACTORY (não misturar)
# ------------------------------------
# interrupt_before=["tools"]  = pausa o NÓ inteiro de tools (LangGraph cru).
#                               Toda tool para. Você retoma o grafo.
# HumanInTheLoopMiddleware    = o jeito LangChain 1.x. Pausa SÓ as tools
#                               listadas em interrupt_on. Você manda
#                               approve ou reject. Por baixo é um interrupt.
#
# Este lab usa o middleware. O script PARA e lê o teclado.
# A primeira versão mandava approve sozinha — por isso "não aprovei nada"
# e mesmo assim pagar() rodou. O humano era o código, não você.
#
# O QUE PRECISA
# -------------
# checkpointer + thread_id (v3 C). A pausa fica no baú. Sem isso não há
# de onde retomar. InMemorySaver = some quando o processo morre.
#
# CICLO
# -----
# 1. invoke(pergunta, config)  → modelo pede pagar(40) e PARA
#    A função pagar() ainda NÃO rodou. result["__interrupt__"] traz o pedido.
# 2. Você decide.
# 3. invoke(Command(resume={"decisions": [{"type": "approve"}]}), MESMO config)
#    → aí sim pagar() executa e o modelo fecha a frase.
#
# ≠ wrap_tool_call do middleware (create_agent_middleware.py):
#   lá o CÓDIGO veta sozinho. Aqui um humano decide em runtime.
#
# reject (não rodamos): Command(resume={"decisions": [{"type": "reject",
#   "message": "não pagar"}]}) — a tool não executa.
# =============================================================================

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from models import Model

# corpo da tool anota aqui. Se a lista cresce na pausa, o interrupt falhou.
_pagou: list[int] = []


@tool
def pagar(valor: int) -> str:
    """Paga um valor em reais. Use quando pedirem para pagar."""
    _pagou.append(valor)
    return f"pago {valor}"


assert pagar.invoke({"valor": 1}) == "pago 1"
_pagou.clear()
print("assert ok: pagar(1) fora do agent; lista zerada de novo")

llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)
checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    tools=[pagar],
    system_prompt=(
        "Se pedirem para pagar, chame a ferramenta pagar com o valor. "
        "Depois responda curto com o retorno da ferramenta."
    ),
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"pagar": True})],
    checkpointer=checkpointer,
)

# mesmo thread nas duas invokes: a segunda acorda a pausa da primeira
config = {"configurable": {"thread_id": "pagar-1"}}


def mostra(msgs: list) -> None:
    for i, msg in enumerate(msgs):
        kind = type(msg).__name__
        calls = getattr(msg, "tool_calls", None) or []
        print(f"    [{i}] {kind}: {getattr(msg, 'content', None)!r}")
        if calls:
            print(f"        tool_calls: {calls}")


print("\n=== 1) invoke — deve PAUSAR antes de pagar() ===")
pausado = agent.invoke(
    {"messages": [{"role": "user", "content": "Pague 40 reais. Use a ferramenta pagar."}]},
    config,
)

interrupts = pausado.get("__interrupt__") or ()
print("  __interrupt__?", bool(interrupts))
print("  pagar() já rodou?", _pagou)
print("  messages na pausa:")
mostra(pausado.get("messages") or [])

if not interrupts:
    print("FAIL: sem pausa. Modelo não chamou pagar, ou middleware não armou.")
    raise SystemExit(0)

pedido = interrupts[0].value["action_requests"][0]
valor = pedido["args"].get("valor")
print(f"\n  humano vê: tool={pedido['name']!r} args={pedido['args']}")
print("  (a função ainda não rodou — a lista _pagou segue vazia)")

if pedido["name"] != "pagar" or _pagou:
    print("FAIL: pausa estranha — tool errada ou pagar() rodou cedo.")
    raise SystemExit(0)
print("ok pausa: pedido visível, corpo da tool intacto")
print("  o processo está parado. pagar() só corre se você digitar approve.")

escolha = input("\n=== 2) digite approve ou reject: ").strip().lower()
if escolha == "approve":
    decisao = {"type": "approve"}
elif escolha == "reject":
    decisao = {"type": "reject", "message": "não pagar. não tente de novo."}
else:
    print("FAIL: só approve ou reject. Nada foi retomado; pagar() não rodou.")
    raise SystemExit(0)

print(f"  resume {escolha!r} no mesmo thread_id")
final = agent.invoke(Command(resume={"decisions": [decisao]}), config)
print("  pagar() rodou?", _pagou)
print("  messages depois do resume:")
mostra(final.get("messages") or [])

tool_msg = next(
    (m for m in final.get("messages") or [] if type(m).__name__ == "ToolMessage"),
    None,
)
if escolha == "approve":
    if _pagou != [valor]:
        print(f"FAIL: esperava _pagou == [{valor}], veio {_pagou}.")
    elif tool_msg is None or f"pago {valor}" not in str(tool_msg.content):
        print("FAIL: ToolMessage sem o retorno de pagar.")
    else:
        print("ok: SEU approve soltou a tool.")
elif _pagou:
    print("FAIL: reject e mesmo assim pagar() rodou.")
else:
    print("ok: SEU reject segurou a tool. _pagou continua [].")

# RESULTADO:

# APPROVE
# assert ok: pagar(1) fora do agent; lista zerada de novo

# === 1) invoke — deve PAUSAR antes de pagar() ===
#   __interrupt__? True
#   pagar() já rodou? []
#   messages na pausa:
#     [0] HumanMessage: 'Pague 40 reais. Use a ferramenta pagar.'
#     [1] AIMessage: ''
#         tool_calls: [{'name': 'pagar', 'args': {'valor': 40}, 'id': '4ab4f4fa-ac26-4fc0-8049-23f7cc74c1b2', 'type': 'tool_call'}]

#   humano vê: tool='pagar' args={'valor': 40}
#   (a função ainda não rodou — a lista _pagou segue vazia)
# ok pausa: pedido visível, corpo da tool intacto
#   o processo está parado. pagar() só corre se você digitar approve.

# === 2) digite approve ou reject: approve
#   resume 'approve' no mesmo thread_id
#   pagar() rodou? [40]
#   messages depois do resume:
#     [0] HumanMessage: 'Pague 40 reais. Use a ferramenta pagar.'
#     [1] AIMessage: ''
#         tool_calls: [{'name': 'pagar', 'args': {'valor': 40}, 'id': '4ab4f4fa-ac26-4fc0-8049-23f7cc74c1b2', 'type': 'tool_call'}]
#     [2] ToolMessage: 'pago 40'
#     [3] AIMessage: 'Pago 40 reais.'
# ok: SEU approve soltou a tool.


# REJECT
# assert ok: pagar(1) fora do agent; lista zerada de novo

# === 1) invoke — deve PAUSAR antes de pagar() ===
#   __interrupt__? True
#   pagar() já rodou? []
#   messages na pausa:
#     [0] HumanMessage: 'Pague 40 reais. Use a ferramenta pagar.'
#     [1] AIMessage: ''
#         tool_calls: [{'name': 'pagar', 'args': {'valor': 40}, 'id': '7e9b0286-c8b7-413f-b0ae-b02ff7b6b255', 'type': 'tool_call'}]

#   humano vê: tool='pagar' args={'valor': 40}
#   (a função ainda não rodou — a lista _pagou segue vazia)
# ok pausa: pedido visível, corpo da tool intacto
#   o processo está parado. pagar() só corre se você digitar approve.

# === 2) digite approve ou reject: reject
#   resume 'reject' no mesmo thread_id
#   pagar() rodou? []
#   messages depois do resume:
#     [0] HumanMessage: 'Pague 40 reais. Use a ferramenta pagar.'
#     [1] AIMessage: ''
#         tool_calls: [{'name': 'pagar', 'args': {'valor': 40}, 'id': '7e9b0286-c8b7-413f-b0ae-b02ff7b6b255', 'type': 'tool_call'}]
#     [2] ToolMessage: 'User rejected the tool call for `pagar` with reason: não pagar. não tente de novo.'
#     [3] AIMessage: 'Não posso pagar.'
# ok: SEU reject segurou a tool. _pagou continua [].