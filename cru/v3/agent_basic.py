# COLA: create_agent = o loop do tool_loop.py, mas o framework executa sozinho.
# Mesma tool soma; diferença = sem while/append manual.
# result["messages"] = trilha completa: Human → AI(tool_calls) → ToolMessage → AI(final)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama

from models import Model


@tool
def soma(a: int, b: int) -> int:
    """Soma dois inteiros. Use para qualquer conta de adição."""
    return a + b


# --- 1) tool sem LLM (tem que passar) ---
assert soma.invoke({"a": 2, "b": 3}) == 5
print("assert ok: soma(2,3)=5")

# --- 2) agente pronto (substitui bind_tools + loop manual) ---
# se não chamar tool, tenta Model.QWEN3_8B / outro
llm = ChatOllama(model=Model.QWEN3_8B, temperature=0)

agent = create_agent(
    model=llm,
    tools=[soma],
    system_prompt="Use a ferramenta soma para qualquer adição. Responda curto.",
)

print("--- agent.invoke (loop interno) ---")
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Quanto é 17 + 25? Use a ferramenta soma. Responda com o número.",
            }
        ]
    }
)

# --- 3) inspeciona a trilha (comparar mentalmente com tool_loop.py) ---
print("--- trilha result['messages'] ---")
had_tool = False
for i, msg in enumerate(result["messages"]):
    kind = type(msg).__name__
    tool_calls = getattr(msg, "tool_calls", None) or []
    print(f"[{i}] {kind}")
    print("    content:", getattr(msg, "content", None))
    if tool_calls:
        print("    tool_calls:", tool_calls)
    if kind == "ToolMessage":
        had_tool = True

if not had_tool:
    print("FAIL: sem ToolMessage na trilha. Troca o Model / reforça o prompt.")
else:
    print("--- final ---")
    print(result["messages"][-1].content)

# RESULTADO:
# assert ok: soma(2,3)=5
# --- agent.invoke (loop interno) ---
# --- trilha result['messages'] ---
# [0] HumanMessage
#     content: Quanto é 17 + 25? Use a ferramenta soma. Responda com o número.
# [1] AIMessage
#     content: 
#     tool_calls: [{'name': 'soma', 'args': {'a': 17, 'b': 25}, 'id': '19f9fd9f-9ec5-4cdc-bc10-f94d6580b216', 'type': 'tool_call'}]
# [2] ToolMessage
#     content: 42
# [3] AIMessage
#     content: 42
# --- final ---
# 42