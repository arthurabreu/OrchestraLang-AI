# =============================================================================
# LIÇÃO: middleware em caso real — tool quebra, exceção vira ToolMessage
# =============================================================================
#
# PERGUNTA
# --------
# "A tool deu raise. O processo morre, ou o modelo lê o erro e continua?"
#
# Resposta: @wrap_tool_call em volta de handler(request). try deixa a tool
# rodar. except devolve ToolMessage(content=..., tool_call_id=...).
# O agent segue. O modelo vê a mensagem, não o stack trace no terminal.
#
#
# CONTRASTE COM v4 (create_agent_middleware.py)
# ---------------------------------------------
# veto_bomba recusa DE PROPÓSITO e NÃO chama handler. "Bomba" não existe
# em produção. Dividir por zero existe: input ruim, tool estoura.
# Aqui a tool roda, estoura, e o middleware TRADUZ. O processo segue.
#
# Doc também tem ToolErrorMiddleware pronto. Este lab escreve o wrap
# na mão pra ver o try/except. create_agent(..., middleware=[...]).
#
# Exemplo: dividir(8, 2) → 4. dividir(1, 0) → ZeroDivisionError →
# ToolMessage "Tool error: ..." e o script chega no CHECAGEM.
# =============================================================================

import sys
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools import tool
from langchain.tools.tool_node import ToolCallRequest
from langchain_ollama import ChatOllama

from models import Model


@tool
def dividir(a: int, b: int) -> float:
    """Divide a por b. b=0 estoura de propósito (estudo de erro)."""
    if b == 0:
        print("  [tool dividir] b=0 — vou estourar")
        raise ZeroDivisionError("divisão por zero")
    return a / b


assert dividir.invoke({"a": 8, "b": 2}) == 4.0
try:
    dividir.invoke({"a": 1, "b": 0})
    raise SystemExit("FAIL: dividir(1, 0) deveria estourar sem LLM")
except ZeroDivisionError as exc:
    assert "divisão por zero" in str(exc)
print("assert ok: dividir(8, 2)=4; dividir(1, 0) estoura ZeroDivisionError")


@wrap_tool_call
def handle_tool_errors(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage],
) -> ToolMessage:
    """Tool estourou: vira ToolMessage. Processo não morre."""
    name = request.tool_call["name"]
    print(f"  [mw wrap_tool_call] pediu tool={name!r}")
    try:
        return handler(request)
    except Exception as e:
        print(f"  [mw wrap_tool_call] tool estourou ({type(e).__name__}); traduzo")
        return ToolMessage(
            content=f"Tool error: verifique a entrada e tente de novo. ({e})",
            tool_call_id=request.tool_call["id"],
        )


llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)

agent = create_agent(
    model=llm,
    tools=[dividir],
    middleware=[handle_tool_errors],
    system_prompt=(
        "Você tem a tool dividir. Sempre chame dividir para contas. "
        "Responda curto com o retorno da tool. "
        "Se a tool devolver Tool error, repita o erro numa frase. Não invente número."
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


def acha_tool(msgs: list):
    return next((m for m in msgs if type(m).__name__ == "ToolMessage"), None)


print("\n=== O QUE OLHAR ===")
print("1) Assert sem LLM: a tool estoura sozinha.")
print("2) 8/2: handler passa; ToolMessage com 4.")
print("3) 1/0: tool roda, raise, middleware devolve ToolMessage. Sem traceback matando o script.")
print("4) ≠ veto da v4: lá handler(bomba) não roda. Aqui handler rodou e quebrou.")

msgs_ok = corre("Quanto é 8 dividido por 2? Use a ferramenta dividir com a=8 e b=2.")
print("--- trilha 8/2 ---")
mostra(msgs_ok)

msgs_zero = corre("Quanto é 1 dividido por 0? Use a ferramenta dividir com a=1 e b=0.")
print("--- trilha 1/0 ---")
mostra(msgs_zero)

print("\n=== CHECAGEM ===")
tool_ok = acha_tool(msgs_ok)
tool_zero = acha_tool(msgs_zero)
ok = True

if tool_ok is None or "4" not in str(getattr(tool_ok, "content", "")):
    print("FAIL 8/2: esperava ToolMessage com 4 (modelo não chamou a tool?).")
    ok = False
else:
    print("ok 8/2: tool executou.")

if tool_zero is None:
    print("FAIL 1/0: sem ToolMessage (modelo não chamou a tool?).")
    ok = False
elif "Tool error" not in str(getattr(tool_zero, "content", "")):
    print("FAIL 1/0: esperava ToolMessage traduzida pelo middleware.")
    ok = False
else:
    print("ok 1/0: exceção virou ToolMessage; script seguiu.")

if ok:
    print("ok: tool quebra, middleware traduz, agent continua.")

# RESULTADO:
# [tool dividir] b=0 — vou estourar
# assert ok: dividir(8, 2)=4; dividir(1, 0) estoura ZeroDivisionError

# === O QUE OLHAR ===
# 1) Assert sem LLM: a tool estoura sozinha.
# 2) 8/2: handler passa; ToolMessage com 4.
# 3) 1/0: tool roda, raise, middleware devolve ToolMessage. Sem traceback matando o script.
# 4) ≠ veto da v4: lá handler(bomba) não roda. Aqui handler rodou e quebrou.

# --- user: Quanto é 8 dividido por 2? Use a ferramenta dividir com a=8 e b=2. ---
#   [mw wrap_tool_call] pediu tool='dividir'
# --- trilha 8/2 ---
#   [0] HumanMessage: 'Quanto é 8 dividido por 2? Use a ferramenta dividir com a=8 e b=2.'
#   [1] AIMessage: ''
#       tool_calls: [{'name': 'dividir', 'args': {'a': 8, 'b': 2}, 'id': '3b231752-ca6f-4777-9c8c-b560cdcd52e8', 'type': 'tool_call'}]
#   [2] ToolMessage: '4.0'
#   [3] AIMessage: '8 dividido por 2 é 4.0.'

# --- user: Quanto é 1 dividido por 0? Use a ferramenta dividir com a=1 e b=0. ---
#   [mw wrap_tool_call] pediu tool='dividir'
#   [tool dividir] b=0 — vou estourar
#   [mw wrap_tool_call] tool estourou (ZeroDivisionError); traduzo
# --- trilha 1/0 ---
#   [0] HumanMessage: 'Quanto é 1 dividido por 0? Use a ferramenta dividir com a=1 e b=0.'
#   [1] AIMessage: ''
#       tool_calls: [{'name': 'dividir', 'args': {'a': 1, 'b': 0}, 'id': '84b059b3-b002-4867-905b-8433abc022ae', 'type': 'tool_call'}]
#   [2] ToolMessage: 'Tool error: verifique a entrada e tente de novo. (divisão por zero)'
#   [3] AIMessage: 'A divisão por zero é inválida.'

# === CHECAGEM ===
# ok 8/2: tool executou.
# ok 1/0: exceção virou ToolMessage; script seguiu.
# ok: tool quebra, middleware traduz, agent continua.
