# =============================================================================
# MIDDLEWARE, versão curta — leia isto ANTES de create_agent_middleware.py
# =============================================================================
#
# O que é
# -------
# Middleware = função SUA que o create_agent encaixa no caminho.
# Você passa em create_agent(..., middleware=[...]).
# O modelo não escolhe chamar. Não aparece em tool_calls. Não é uma tool.
#
# Tool (soma, saldo) = o MODELO decide se chama.
# Middleware         = o FRAMEWORK chama, sempre, no ponto que você marcou.
#
# Pra que serve
# -------------
# Coisa que tem que acontecer em toda corrida, sem confiar no modelo:
#   - log / contagem
#   - cortar a corrida antes de gastar o LLM
#   - (no outro arquivo) impedir uma tool específica
#
# Este arquivo tem SÓ dois ganchos, e nenhuma tool:
#
#   @before_model   roda ANTES do LLM. state["messages"] já tem a pergunta.
#   @after_model    roda DEPOIS que o LLM respondeu.
#
# Corrida A — "diga ok"
#   before_model imprime
#   LLM responde
#   after_model imprime
#   → middleware observou. O modelo não "chamou" o middleware.
#
# Corrida B — texto contém "BLOQUEIA"
#   before_model devolve jump_to="end" + uma AIMessage escrita por NÓS
#   o LLM não é chamado (after_model não imprime)
#   → middleware mandou. O modelo nem entrou.
#
# create_agent_middleware.py é isto + um terceiro gancho (@wrap_tool_call)
# que senta em volta da tool e pode recusar a bomba sem executá-la.
# =============================================================================

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.agents.middleware import AgentState, after_model, before_model
from langchain.messages import AIMessage
from langchain_ollama import ChatOllama
from langgraph.runtime import Runtime

from models import Model

# True só se after_model rodou = o LLM foi chamado nesta corrida.
_llm_rodou = [False]


@before_model(can_jump_to=["end"])
def guarda(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Porta da frente. Olha a pergunta. Pode deixar passar ou encerrar."""
    texto = state["messages"][-1].content
    print(f"  [before_model] vi a pergunta: {texto!r}")
    if "BLOQUEIA" in str(texto):
        print("  [before_model] corto aqui. O modelo NÃO será chamado.")
        # jump_to=end pula o LLM. A frase abaixo é nossa, não do modelo.
        return {
            "messages": [AIMessage("parado pelo middleware, sem chamar o modelo")],
            "jump_to": "end",
        }
    print("  [before_model] deixo passar. Agora o modelo roda.")
    return None


@after_model
def depois(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Só existe se o modelo chegou a responder."""
    _llm_rodou[0] = True
    texto = state["messages"][-1].content
    print(f"  [after_model] modelo respondeu: {texto!r}")
    return None


llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)

# tools=[] de propósito: middleware não precisa de tool pra existir.
agent = create_agent(
    model=llm,
    tools=[],
    middleware=[guarda, depois],
    system_prompt="Responda exatamente: ok",
)


def corre(pergunta: str) -> list:
    _llm_rodou[0] = False
    print(f"\n--- pergunta: {pergunta!r} ---")
    result = agent.invoke({"messages": [{"role": "user", "content": pergunta}]})
    print("  llm foi chamado?", _llm_rodou[0])
    for i, msg in enumerate(result["messages"]):
        print(f"  [{i}] {type(msg).__name__}: {getattr(msg, 'content', None)!r}")
    return result["messages"]


print("=== A: middleware só observa. Modelo responde. ===")
msgs_a = corre("diga ok")

print("\n=== B: middleware corta. Modelo não entra. ===")
msgs_b = corre("BLOQUEIA esta pergunta")

print("\n=== leitura ===")
print("A e B usaram o MESMO agent. A diferença é o if dentro do before_model.")
print("Nenhuma das duas corridas tem ToolMessage: não havia tool.")
print("create_agent_middleware.py = estes dois prints + wrap em volta da tool.")

ok = True
ultimo_a = str(getattr(msgs_a[-1], "content", ""))
ultimo_b = str(getattr(msgs_b[-1], "content", ""))
if "parado pelo middleware" in ultimo_a:
    print("FAIL A: o middleware cortou uma pergunta normal.")
    ok = False
elif "ok" not in ultimo_a.lower():
    print("FAIL A: esperava o modelo responder ok. Troca Model / prompt.")
    ok = False
else:
    print("ok A: modelo falou; before/after só viram a passagem.")

if "parado pelo middleware" not in ultimo_b:
    print("FAIL B: esperava a frase do middleware, não a do modelo.")
    ok = False
elif _llm_rodou[0]:
    print("FAIL B: after_model rodou — o modelo foi chamado mesmo com o corte.")
    ok = False
else:
    print("ok B: middleware encerrou; LLM não rodou.")

if ok:
    print("ok: middleware é o seu código no caminho, não uma tool do modelo.")

# RESULTADO:
# === A: middleware só observa. Modelo responde. ===

# --- pergunta: 'diga ok' ---
#   [before_model] vi a pergunta: 'diga ok'
#   [before_model] deixo passar. Agora o modelo roda.
#   [after_model] modelo respondeu: 'ok'
#   llm foi chamado? True
#   [0] HumanMessage: 'diga ok'
#   [1] AIMessage: 'ok'

# === B: middleware corta. Modelo não entra. ===

# --- pergunta: 'BLOQUEIA esta pergunta' ---
#   [before_model] vi a pergunta: 'BLOQUEIA esta pergunta'
#   [before_model] corto aqui. O modelo NÃO será chamado.
#   llm foi chamado? False
#   [0] HumanMessage: 'BLOQUEIA esta pergunta'
#   [1] AIMessage: 'parado pelo middleware, sem chamar o modelo'

# === leitura ===
# A e B usaram o MESMO agent. A diferença é o if dentro do before_model.
# Nenhuma das duas corridas tem ToolMessage: não havia tool.
# create_agent_middleware.py = estes dois prints + wrap em volta da tool.
# ok A: modelo falou; before/after só viram a passagem.
# ok B: middleware encerrou; LLM não rodou.
# ok: middleware é o seu código no caminho, não uma tool do modelo.
