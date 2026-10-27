# COLA: modelo só PEDE a tool (tool_calls). Quem executa é o Python.
# Fluxo: Human → AI(tool_calls) → ToolMessage(resultado) → AI(texto final)
# NÃO usar create_agent aqui — loop manual de propósito.

from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from models import Model


@tool
def soma(a: int, b: int) -> int:
    """Soma dois inteiros. Use para qualquer conta de adição."""
    return a + b


# --- 1) tool sem LLM (tem que passar) ---
assert soma.invoke({"a": 2, "b": 3}) == 5
print("assert ok: soma(2,3)=5")

# --- 2) modelo com tool ligada ---
# se tool_calls vier [], tenta Model.QWEN3_8B
llm = ChatOllama(model=Model.QWEN3_8B, temperature=0)
llm_tools = llm.bind_tools([soma])

messages = [
    HumanMessage(content="Quanto é 17 + 25? Use a ferramenta soma. Responda com o número."),
]

print("--- passo 1: modelo decide ---")
ai = llm_tools.invoke(messages)
print("content:", ai.content)
print("tool_calls:", ai.tool_calls)

if not ai.tool_calls:
    print("FAIL: modelo não pediu tool. Troca o Model e roda de novo.")
else:
    messages.append(ai)  # AI com tool_calls precisa entrar no histórico

    print("--- passo 2: Python executa ---")
    for call in ai.tool_calls:
        # call tem name/args/id; Tool.invoke aceita o dict do tool_call
        result = soma.invoke(call)
        print("executou", call["name"], call["args"], "→", result)
        messages.append(result)  # costuma já ser ToolMessage

    print("--- passo 3: modelo vê o resultado ---")
    final = llm_tools.invoke(messages)
    print("final:", final.content)


# RESULTADO:
# assert ok: soma(2,3)=5
# --- passo 1: modelo decide ---
# content: 
# tool_calls: [{'name': 'soma', 'args': {'a': 17, 'b': 25}, 'id': '0be3f763-de15-4436-ba18-4f8a67a398fa', 'type': 'tool_call'}]
# --- passo 2: Python executa ---
# executou soma {'a': 17, 'b': 25} → content='42' name='soma' tool_call_id='0be3f763-de15-4436-ba18-4f8a67a398fa'
# --- passo 3: modelo vê o resultado ---
# final: 42

# RESULTADO sem messages.append(ai):
# assert ok: soma(2,3)=5
# --- passo 1: modelo decide ---
# content: 
# tool_calls: [{'name': 'soma', 'args': {'a': 17, 'b': 25}, 'id': 'c3932172-75c2-4b33-8280-682e7a8fcf8a', 'type': 'tool_call'}]
# --- passo 2: Python executa ---
# executou soma {'a': 17, 'b': 25} → content='42' name='soma' tool_call_id='c3932172-75c2-4b33-8280-682e7a8fcf8a'
# --- passo 3: modelo vê o resultado ---
# final: 