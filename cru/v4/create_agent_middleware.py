# =============================================================================
# LIÇÃO: middleware= em create_agent
# =============================================================================
#
# PERGUNTA
# --------
# "Quero LOGAR / CONTAR / BLOQUEAR coisas no ciclo do agent SEM virar tool
#  que o LLM escolhe chamar. Onde isso vive?"
#
# Resposta: middleware — ganchos no grafo (antes/depois do model, em volta
# da tool). create_agent(..., middleware=[...]).
#
#
# MIDDLEWARE ≠ TOOL
# -----------------
# tool        = função que o MODELO decide chamar (soma, saldo…).
# middleware  = código SEU que roda sempre no ciclo (log, limite, veto).
#               LLM não "escolhe" middleware; o framework injeta.
#
#
# DOIS ESTILOS NESTE LAB
# ----------------------
# 1) @before_model / @after_model — nós em volta da chamada ao LLM.
# 2) @wrap_tool_call — envelopa CADA tool: pode logar, mudar args, ou
#    BLOQUEAR (devolver ToolMessage de erro sem executar a tool).
#
# Utilidade real: rate limit, auditoria, negar tool perigosa, injetar
# métricas — cross-cutting, não "mais uma tool no prompt".
#
# Ref: docs langchain middleware custom + factory.create_agent(middleware=).
# =============================================================================

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.agents.middleware import AgentState, after_model, before_model, wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools import tool
from langchain.tools.tool_node import ToolCallRequest
from langchain_ollama import ChatOllama
from langgraph.runtime import Runtime

from models import Model

# contador didático (lista = mutável no closure)
_model_calls = [0]


@tool
def soma(a: int, b: int) -> int:
    """Soma dois inteiros. Use para adição."""
    return a + b


@tool
def bomba(x: int) -> str:
    """Tool 'perigosa' de estudo — middleware deve bloquear."""
    return f"BOOM {x}"  # se chegar aqui, o veto falhou


assert soma.invoke({"a": 2, "b": 3}) == 5
assert bomba.invoke({"x": 1}) == "BOOM 1"
print("assert ok: tools sozinhas (sem middleware)")


@before_model
def log_antes(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Roda ANTES de cada chamada ao modelo. Não é tool."""
    n = len(state.get("messages") or [])
    print(f"  [middleware before_model] msgs no state={n} | model_calls_até_agora={_model_calls[0]}")
    return None  # None = não mexe no state; só observa


@after_model
def log_depois(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Roda DEPOIS da resposta do modelo (pode ter tool_calls)."""
    _model_calls[0] += 1
    last = (state.get("messages") or [])[-1]
    calls = getattr(last, "tool_calls", None) or []
    print(
        f"  [middleware after_model] model_call#{_model_calls[0]} "
        f"tipo={type(last).__name__} tool_calls={len(calls)}"
    )
    return None


@wrap_tool_call
def veto_bomba(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage],
) -> ToolMessage:
    """Envolve toda tool: deixa soma passar; bloqueia bomba."""
    name = request.tool_call["name"]
    print(f"  [mw wrap_tool_call] pediu tool={name!r}")
    if name == "bomba":
        print("  [mw wrap_tool_call] VETO — não executa bomba")
        # ToolMessage de erro: modelo vê a recusa; handler(bomba) NÃO roda
        return ToolMessage(
            content="bloqueado pelo middleware: bomba não permitida",
            tool_call_id=request.tool_call["id"],
        )
    return handler(request)  # executa a tool de verdade


llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)

agent = create_agent(
    model=llm,
    tools=[soma, bomba],
    middleware=[log_antes, log_depois, veto_bomba],
    system_prompt=(
        "Você tem tools: soma e bomba. "
        "Se pedirem soma, chame soma. Se pedirem bomba, chame bomba. "
        "Responda curto com o retorno da tool."
    ),
)


def corre(texto: str) -> list:
    print(f"\n--- user: {texto} ---")
    result = agent.invoke({"messages": [{"role": "user", "content": texto}]})
    return result["messages"]


def mostra(msgs: list) -> None:
    for i, msg in enumerate(msgs):
        kind = type(msg).__name__
        print(f"  [{i}] {kind}: {getattr(msg, 'content', None)!r}")
        tcs = getattr(msg, "tool_calls", None) or []
        if tcs:
            print(f"      tool_calls: {tcs}")


print("\n=== O QUE OLHAR ===")
print("1) Prints [mw …] = middleware (não aparecem como tool pro LLM escolher).")
print("2) Corrida soma: wrap deixa passar → ToolMessage com número.")
print("3) Corrida bomba: wrap VETA → ToolMessage 'bloqueado…' (sem BOOM).")

_model_calls[0] = 0
msgs_soma = corre("Quanto é 7+8? Use a ferramenta soma.")
print("--- trilha soma ---")
mostra(msgs_soma)

_model_calls[0] = 0
msgs_bomba = corre("Dispare a ferramenta bomba com x=9.")
print("--- trilha bomba ---")
mostra(msgs_bomba)

print("\n=== CHECAGEM ===")
tool_soma = next(
    (m for m in msgs_soma if type(m).__name__ == "ToolMessage"),
    None,
)
tool_bomba = next(
    (m for m in msgs_bomba if type(m).__name__ == "ToolMessage"),
    None,
)

ok = True
if tool_soma is None or "15" not in str(getattr(tool_soma, "content", "")):
    print("FAIL soma: esperava ToolMessage com 15 (ou tool não chamada).")
    ok = False
else:
    print("ok soma: tool executou; middleware só observou/logou.")

if tool_bomba is None:
    print("FAIL bomba: sem ToolMessage (modelo não chamou tool?).")
    ok = False
elif "BOOM" in str(getattr(tool_bomba, "content", "")):
    print("FAIL bomba: middleware NÃO vetou — conteudo tem BOOM.")
    ok = False
elif "bloqueado" not in str(getattr(tool_bomba, "content", "")).lower():
    print("FAIL bomba: esperava ToolMessage de bloqueio do middleware.")
    ok = False
else:
    print("ok bomba: middleware vetou; tool real não rodou.")

if ok:
    print("ok: middleware ≠ tool — log + veto sem ser função do catálogo do LLM.")

# RESULTADO:
# assert ok: tools sozinhas (sem middleware)

# === O QUE OLHAR ===
# 1) Prints [mw …] = middleware (não aparecem como tool pro LLM escolher).
# 2) Corrida soma: wrap deixa passar → ToolMessage com número.
# 3) Corrida bomba: wrap VETA → ToolMessage 'bloqueado…' (sem BOOM).

# --- user: Quanto é 7+8? Use a ferramenta soma. ---
#   [mw before_model] msgs no state=1 | model_calls_até_agora=0
#   [mw after_model] model_call#1 tipo=AIMessage tool_calls=1
#   [mw wrap_tool_call] pediu tool='soma'
#   [mw before_model] msgs no state=3 | model_calls_até_agora=1
#   [mw after_model] model_call#2 tipo=AIMessage tool_calls=0
# --- trilha soma ---
#   [0] HumanMessage: 'Quanto é 7+8? Use a ferramenta soma.'
#   [1] AIMessage: ''
#       tool_calls: [{'name': 'soma', 'args': {'a': 7, 'b': 8}, 'id': '9b69804d-29fc-4709-ac17-59bc579ec796', 'type': 'tool_call'}]
#   [2] ToolMessage: '15'
#   [3] AIMessage: '7 + 8 = 15.'

# --- user: Dispare a ferramenta bomba com x=9. ---
#   [mw before_model] msgs no state=1 | model_calls_até_agora=0
#   [mw after_model] model_call#1 tipo=AIMessage tool_calls=1
#   [mw wrap_tool_call] pediu tool='bomba'
#   [mw wrap_tool_call] VETO — não executa bomba
#   [mw before_model] msgs no state=3 | model_calls_até_agora=1
#   [mw after_model] model_call#2 tipo=AIMessage tool_calls=0
# --- trilha bomba ---
#   [0] HumanMessage: 'Dispare a ferramenta bomba com x=9.'
#   [1] AIMessage: ''
#       tool_calls: [{'name': 'bomba', 'args': {'x': 9}, 'id': 'b0dc63ad-08b2-4608-9a02-81c681ffdef7', 'type': 'tool_call'}]
#   [2] ToolMessage: 'bloqueado pelo middleware: bomba não permitida'
#   [3] AIMessage: 'A ferramenta "bomba" está bloqueada pelo middleware e não pode ser utilizada.'

# === CHECAGEM ===
# ok soma: tool executou; middleware só observou/logou.
# ok bomba: middleware vetou; tool real não rodou.
# ok: middleware ≠ tool — log + veto sem ser função do catálogo do LLM.

# L2 passou. Exit 0. As três checagens no fim do arquivo bateram.

# Corrida	Trilha	Leitura
# soma
# before_model → after_model (1 tool_call) → wrap deixa passar → ToolMessage: 15 → before_model de novo (3 msgs) → resposta final
# Tool rodou de verdade. Middleware só logou.
# bomba
# Mesmo ciclo, mas wrap imprime VETO e não chama handler
# ToolMessage = texto de bloqueio. Sem BOOM. Modelo leu o veto e repetiu na resposta final.
# O segundo before_model (state com 3 mensagens) é o loop do agent: depois da tool, o modelo roda de novo para fechar a resposta. O # RESULTADO: está comentado; o arquivo compila.