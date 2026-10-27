# COLA: várias tools no create_agent — modelo escolhe pelo nome/descrição + prompt.
# Ex.: “some 3 e 4” → soma; “multiplica …” → multiplica; “subtrai …” → subtrai.
# qwen3: reasoning=False evita “pensar” infinito (eco/texto vago travava no Ollama).
# Asserts sem LLM = tools ok; trilha = prova do roteamento.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama

from models import Model


@tool
def soma(a: int, b: int) -> int:
    """Soma dois inteiros. Use só para adição (+)."""
    return a + b


@tool
def multiplica(a: int, b: int) -> int:
    """Multiplica dois inteiros. Use só para multiplicação (*)."""
    return a * b


@tool
def subtrai(a: int, b: int) -> int:
    """Subtrai b de a (a - b). Use só para subtração (-)."""
    return a - b


# --- 1) tools sem LLM ---
assert soma.invoke({"a": 2, "b": 3}) == 5
assert multiplica.invoke({"a": 2, "b": 3}) == 6
assert subtrai.invoke({"a": 10, "b": 3}) == 7
print("assert ok: soma / multiplica / subtrai")

# --- 2) agente com 3 tools ---
# reasoning=False: qwen3 não entra em <think> longo (senão parece “travado”)
llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)

agent = create_agent(
    model=llm,
    tools=[soma, multiplica, subtrai],
    system_prompt=(
        "Você tem ferramentas: soma, multiplica, subtrai. "
        "Use a ferramenta certa pro pedido. Responda curto."
    ),
)


def nomes_tools_chamadas(result: dict) -> list[str]:
    """Extrai nomes das tools pedidas nos AIMessage.tool_calls da trilha."""
    nomes: list[str] = []
    for msg in result["messages"]:
        for call in getattr(msg, "tool_calls", None) or []:
            nomes.append(call["name"])
    return nomes


def roda(titulo: str, pergunta: str, esperado: list[str]) -> None:
    print(f"\n=== {titulo} ===")
    print("pergunta:", pergunta)
    result = agent.invoke({"messages": [{"role": "user", "content": pergunta}]})
    nomes = nomes_tools_chamadas(result)
    print("tools chamadas:", nomes)
    for i, msg in enumerate(result["messages"]):
        kind = type(msg).__name__
        tool_calls = getattr(msg, "tool_calls", None) or []
        print(f"[{i}] {kind} content={getattr(msg, 'content', None)!r}")
        if tool_calls:
            print("    tool_calls:", tool_calls)
    print("final:", result["messages"][-1].content)
    if nomes != esperado:
        print(f"FAIL roteamento: esperado {esperado}, veio {nomes}. Troca Model / reforça prompt.")
    else:
        print("ok roteamento:", esperado)


# casos didáticos: cada um deve bater a tool certa
roda(
    "caso soma",
    "Quanto é 17 + 25? Use a ferramenta de adição. Só o número.",
    ["soma"],
)
roda(
    "caso multiplica",
    "Quanto é 6 * 7? Use a ferramenta de multiplicação. Só o número.",
    ["multiplica"],
)
roda(
    "caso subtrai",
    "Quanto é 50 - 8? Use a ferramenta de subtração. Só o número.",
    ["subtrai"],
)


# RESULTADO:
# assert ok: soma / multiplica / subtrai

# === caso soma ===
# pergunta: Quanto é 17 + 25? Use a ferramenta de adição. Só o número.
# tools chamadas: ['soma']
# [0] HumanMessage content='Quanto é 17 + 25? Use a ferramenta de adição. Só o número.'
# [1] AIMessage content=''
#     tool_calls: [{'name': 'soma', 'args': {'a': 17, 'b': 25}, 'id': 'c426f05e-4fc9-453b-8b81-403acb37d591', 'type': 'tool_call'}]
# [2] ToolMessage content='42'
# [3] AIMessage content='42'
# final: 42
# ok roteamento: ['soma']

# === caso multiplica ===
# pergunta: Quanto é 6 * 7? Use a ferramenta de multiplicação. Só o número.
# tools chamadas: ['multiplica']
# [0] HumanMessage content='Quanto é 6 * 7? Use a ferramenta de multiplicação. Só o número.'
# [1] AIMessage content=''
#     tool_calls: [{'name': 'multiplica', 'args': {'a': 6, 'b': 7}, 'id': '38331dee-52aa-4a51-9ecc-32c49745bd53', 'type': 'tool_call'}]
# [2] ToolMessage content='42'
# [3] AIMessage content='42'
# final: 42
# ok roteamento: ['multiplica']

# === caso subtrai ===
# pergunta: Quanto é 50 - 8? Use a ferramenta de subtração. Só o número.
# tools chamadas: ['subtrai']
# [0] HumanMessage content='Quanto é 50 - 8? Use a ferramenta de subtração. Só o número.'
# [1] AIMessage content=''
#     tool_calls: [{'name': 'subtrai', 'args': {'a': 50, 'b': 8}, 'id': 'c5531c46-6a51-48ca-89c1-3256e89f3b76', 'type': 'tool_call'}]
# [2] ToolMessage content='42'
# [3] AIMessage content='42'
# final: 42
# ok roteamento: ['subtrai']