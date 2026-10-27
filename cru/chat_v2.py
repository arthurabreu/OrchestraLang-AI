# COLA MENTAL
# messages = [
#   SystemMessage(...),   # regras fixas
#   HumanMessage(...),    # você turno 1
#   AIMessage(...),       # resposta do modelo turno 1  ← obrigatório append
#   HumanMessage(...),    # você turno 2
# ]
# llm.invoke(messages)    # vê o histórico inteiro
# Cada resposta → append na lista → próximo call manda tudo.
#
# AIMessage importa quando o próximo turno depende do que o MODELO falou
# (codinome inventado, cálculo, escolha). Se o fato já está no Human, ele
# continua na lista mesmo sem AI — por isso o teste da “cor” ainda acertava.

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from models import Model

# "demo" = 2 turnos fixos (codinome) | "repl" = você digita no terminal
MODE = "repl"

llm = ChatOllama(
    model=Model.GEMMA3_4B,
    temperature=0,  # teste de memória: menos invenção
)

messages = [
    SystemMessage(content="Responda curto, no idioma de quem fala."),
]

if MODE == "demo":
    # --- turno 1 ---
    messages.append(
        HumanMessage(content="Inventa um codinome de 1 palavra pra mim e diga só ele.")
    )
    print("--- turno 1 ---")
    out1 = llm.invoke(messages)
    print(out1.content)

    messages.append(AIMessage(content=out1.content))  # comenta esta linha = “amnésia”

    # --- turno 2 ---
    messages.append(HumanMessage(content="Qual codinome você escolheu?"))
    print("--- turno 2 ---")
    print("msgs:", len(messages), [type(m).__name__ for m in messages])
    out2 = llm.invoke(messages)
    print(out2.content)

elif MODE == "repl":
    # Mesma regra do demo, só que o Human vem do teclado a cada volta.
    # q / quit / sair → encerra. Histórico cresce: len(messages) sobe a cada turno.
    print("REPL multi-turn. Digite q para sair.")
    while True:
        text = input("you> ").strip()
        if text in {"q", "quit", "sair"}:
            break
        if not text:
            continue
        messages.append(HumanMessage(content=text))
        out = llm.invoke(messages)
        print(out.content)
        messages.append(AIMessage(content=out.content))  # sem isto = próxima pergunta “esquece”
        print("msgs:", len(messages), [type(m).__name__ for m in messages])
