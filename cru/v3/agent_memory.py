# COLA: checkpointer = histórico do agent.invoke guardado por thread_id.
# Mesmo thread_id → lembra turnos anteriores (sem lista manual tipo chat_v2).
# Thread nova → amnésia. InMemorySaver = só RAM (some ao sair do processo).
# mostra_bau(id) = abre a gaveta no checkpointer e lista as msgs (tipo trilha do agent_basic).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

from models import Model

llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)

# sem checkpointer: cada invoke é mundo novo (só as msgs que você manda naquele call)
# com checkpointer + thread_id: o grafo recarrega o estado daquele fio
checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="Responda curto, no idioma de quem fala.",
    checkpointer=checkpointer,
)


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def fala(thread_id: str, texto: str) -> str:
    """Um turno no fio. config.thread_id escolhe qual histórico carregar/gravar."""
    print(f"  [bau] abre/grava thread_id={thread_id!r}")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": texto}]},
        _config(thread_id),
    )
    return result["messages"][-1].content


def mostra_bau(thread_id: str) -> None:
    """Lê o checkpointer sem chamar o LLM — o que está na gaveta agora."""
    print(f"\n--- bau thread_id={thread_id!r} ---")
    tup = checkpointer.get_tuple(_config(thread_id))
    if tup is None:
        print("  (vazio / nunca usado)")
        return

    # metadado curto: de onde veio este snapshot
    meta = tup.metadata or {}
    ckpt_id = (tup.config or {}).get("configurable", {}).get("checkpoint_id")
    print(f"  checkpoint_id={ckpt_id}")
    print(f"  metadata step={meta.get('step')} source={meta.get('source')}")

    msgs = (tup.checkpoint.get("channel_values") or {}).get("messages") or []
    if not msgs:
        print("  channel_values.messages = []")
        return

    for i, msg in enumerate(msgs):
        kind = type(msg).__name__
        content = getattr(msg, "content", None)
        print(f"  [{i}] {kind}: {content!r}")


print("--- fio A: guarda nome ---")
print("user:", "Meu codinome é Tofu. Só confirme.")
print("ai:  ", fala("A", "Meu codinome é Tofu. Só confirme."))
mostra_bau("A")

print("\n--- fio A: pergunta (deve lembrar) ---")
print("user:", "Qual é o meu codinome?")
out_a = fala("A", "Qual é o meu codinome?")
print("ai:  ", out_a)
mostra_bau("A")
if "tofu" not in out_a.lower():
    print("FAIL: fio A não lembrou. Troca Model / checa checkpointer.")
else:
    print("ok: fio A lembrou")

print("\n--- fio B: thread nova (deve NÃO saber) ---")
print("user:", "Qual é o meu codinome?")
out_b = fala("B", "Qual é o meu codinome?")
print("ai:  ", out_b)
mostra_bau("B")
mostra_bau("A")  # A intacto — prova que B não mistura
if "tofu" in out_b.lower():
    print("FAIL: fio B vazou memória do A (thread_id não isolou).")
else:
    print("ok: fio B amnésia (thread isolada)")
