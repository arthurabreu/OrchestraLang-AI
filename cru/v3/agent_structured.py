# COLA: v2 = with_structured_output no LLM sozinho (sem tools no loop).
# v3 E = create_agent(tools=…, response_format=…).
# Fluxo típico: Human → AI(tool soma) → ToolMessage → AI(tool Conta) → structured_response.
# Ollama: ToolStrategy(Pydantic) mais estável que ProviderStrategy / schema “cru”.
# result["structured_response"] = instância Pydantic (não só texto no último AIMessage).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from models import Model


class Conta(BaseModel):
    """Resposta final tipada depois de usar tools."""
    operacao: str = Field(description="nome curto da operação (ex.: adição)")
    resultado: int = Field(description="número final")
    explicacao: str = Field(description="uma frase curta")


@tool
def soma(a: int, b: int) -> int:
    """Soma dois inteiros. Use para qualquer conta de adição."""
    return a + b


assert soma.invoke({"a": 2, "b": 3}) == 5
print("assert ok: soma(2,3)=5")

llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)

agent = create_agent(
    model=llm,
    tools=[soma],
    system_prompt=(
        "Use a ferramenta soma para adição. "
        "Depois preencha o formato estruturado Conta. Responda curto."
    ),
    response_format=ToolStrategy(Conta),
)

print("--- agent.invoke (tools + structured) ---")
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Quanto é 17 + 25? Use a ferramenta soma.",
            }
        ]
    }
)

print("--- trilha messages ---")
had_soma = False
for i, msg in enumerate(result["messages"]):
    kind = type(msg).__name__
    tool_calls = getattr(msg, "tool_calls", None) or []
    print(f"[{i}] {kind} content={getattr(msg, 'content', None)!r}")
    if tool_calls:
        print("    tool_calls:", tool_calls)
        if any(c.get("name") == "soma" for c in tool_calls):
            had_soma = True

print("--- structured_response ---")
sr = result.get("structured_response")
print("tipo:", type(sr))
print("valor:", sr)
if sr is not None and hasattr(sr, "model_dump_json"):
    print(sr.model_dump_json(indent=2))

if not had_soma:
    print("FAIL: não usou tool soma. Troca Model / reforça prompt.")
elif not isinstance(sr, Conta):
    print("FAIL: structured_response não é Conta. Tenta outro Model.")
elif sr.resultado != 42:
    print(f"FAIL didático: resultado={sr.resultado}, esperado 42.")
else:
    print("ok: tool + structured_response (Conta) juntos")

# RESULTADO:
# assert ok: soma(2,3)=5
# --- agent.invoke (tools + structured) ---
# --- trilha messages ---
# [0] HumanMessage content='Quanto é 17 + 25? Use a ferramenta soma.'
# [1] AIMessage content=''
#     tool_calls: [{'name': 'soma', 'args': {'b': 25, 'a': 17}, 'id': '725e0306-42c6-4b28-8b24-e279ad8e1b41', 'type': 'tool_call'}]
# [2] ToolMessage content='42'
# [3] AIMessage content=''
#     tool_calls: [{'name': 'Conta', 'args': {'operacao': 'adição', 'resultado': 42, 'explicacao': 'A soma de 17 e 25 é 42.'}, 'id': '64b08b3d-7d6d-43d5-8f33-7ac5f9233c76', 'type': 'tool_call'}]
# [4] ToolMessage content="Returning structured response: operacao='adição' resultado=42 explicacao='A soma de 17 e 25 é 42.'"
# --- structured_response ---
# tipo: <class '__main__.Conta'>
# valor: operacao='adição' resultado=42 explicacao='A soma de 17 e 25 é 42.'
# {
#   "operacao": "adição",
#   "resultado": 42,
#   "explicacao": "A soma de 17 e 25 é 42."
# }
# ok: tool + structured_response (Conta) juntos