# COLA: agent.stream ≠ agent.invoke.
# invoke = espera o fim, devolve trilha completa.
# stream(stream_mode="updates") = cada nó do grafo emite quando termina:
#   model (AI + tool_calls) → tools (ToolMessage) → model (texto final).
# stream_mode="messages" = pedaços de AIMessage (tokens / chunks), mais “digitar ao vivo”.

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


assert soma.invoke({"a": 2, "b": 3}) == 5
print("assert ok: soma(2,3)=5")

llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)
agent = create_agent(
    model=llm,
    tools=[soma],
    system_prompt="Use a ferramenta soma para qualquer adição. Responda curto.",
)

PERGUNTA = "Quanto é 17 + 25? Use a ferramenta soma. Responda com o número."
inp = {"messages": [{"role": "user", "content": PERGUNTA}]}

# --- 1) updates: vê o loop do agent passo a passo (sem esperar o final) ---
print("\n=== stream_mode='updates' (nós do grafo) ===")
print("pergunta:", PERGUNTA)
had_tool = False
passo = 0
for chunk in agent.stream(inp, stream_mode="updates"):
    # chunk = {nome_do_no: {messages: [...]}}
    for no, payload in chunk.items():
        passo += 1
        print(f"\n--- passo {passo}: nó={no!r} ---")
        for msg in payload.get("messages", []):
            kind = type(msg).__name__
            tool_calls = getattr(msg, "tool_calls", None) or []
            print(f"  {kind} content={getattr(msg, 'content', None)!r}")
            if tool_calls:
                print("  tool_calls:", tool_calls)
            if kind == "ToolMessage":
                had_tool = True

if not had_tool:
    print("FAIL: sem ToolMessage no stream. Troca Model / reforça prompt.")
else:
    print("\nok: updates mostrou tool no meio do caminho (não só no fim)")

# --- 2) messages: chunks enquanto o modelo “fala” ---
print("\n=== stream_mode='messages' (chunks de texto) ===")
print("pergunta:", PERGUNTA)
print("final ao vivo: ", end="", flush=True)
for item in agent.stream(inp, stream_mode="messages"):
    # item = (AIMessageChunk, metadata)
    msg = item[0] if isinstance(item, tuple) else item
    piece = getattr(msg, "content", None) or ""
    if piece:
        print(piece, end="", flush=True)
    # tool_call_chunks = args da tool chegando aos poucos (quando o provider manda)
    tcc = getattr(msg, "tool_call_chunks", None) or []
    if tcc:
        print(f"\n  [tool_call_chunk] {tcc}", flush=True)
print()  # newline após o stream
print("ok: messages = pedaços; updates = passos do agent")
