# =============================================================================
# LIÇÃO: atendimento longo — o modelo lê só o fim, o checkpointer guarda tudo
# =============================================================================
#
# SITUAÇÃO
# --------
# Um chamado de loja já tem 15 mensagens.
# A primeira diz: pedido PED-100, prazo antigo de 15 dias.
# No meio só tem pergunta de estoque. Isso existe pra alongar o fio.
# Perto do fim uma mensagem diz: o prazo agora é 2 dias úteis.
# A última mensagem pergunta qual é o prazo agora.
#
# O modelo tem que responder "2 dias úteis".
# Se ele reler o começo, mistura com "15 dias".
# O começo não pode ser apagado: daqui a uma semana alguém audita o
# chamado e ainda precisa achar PED-100 e o prazo antigo.
#
#
# DUAS LISTAS, AO MESMO TEMPO
# ---------------------------
# 1) Conversa completa.
#    O invoke recebe as 15 mensagens. O checkpointer (InMemorySaver)
#    grava todas na thread "chamado-1". get_tuple lê essa gravação
#    depois, sem chamar o modelo de novo.
#
# 2) Recorte desta chamada.
#    Antes do Ollama responder, o middleware corta_vista roda.
#    trim_messages fica com as últimas mensagens que cabem em 90 tokens.
#    request.override(messages=recorte) manda SÓ esse recorte ao modelo.
#    Esse override não grava. A conversa completa continua no checkpointer.
#    O modelo não escolhe o middleware. O middleware roda sempre.
#
# Por isso dá para responder uma sequência recente (o prazo novo está
# no recorte) e ainda assim guardar o começo (está na conversa completa).
# O que ficou de fora do recorte o modelo não usa.
#
#
# O QUE O LOG MOSTRA, NESTA ORDEM
# -------------------------------
# Passo 1. trim_messages sozinha, sem Ollama. Prova que o corte já
#          tira "15 dias" e PED-100 e deixa "2 dias úteis".
# Passo 2. O agent roda. O middleware imprime o tamanho das duas listas.
# Passo 3. A frase que o modelo devolveu.
# Passo 4. As mensagens do recorte, uma a uma. É isso que entrou no Ollama.
# Passo 5. As mensagens do checkpointer, uma a uma. É o fio inteiro,
#          com o começo e com a resposta nova no final.
# Passo 6. Checagem das três coisas: recorte, checkpointer, frase.
#
#
# CONTRASTE
# ---------
# cru/v3/agent_memory.py guarda o fio e manda o fio inteiro ao modelo.
# Este arquivo guarda o fio e manda só o fim.
# before_model que devolve {"messages": recorte} grava essa lista no
# state. Não é "o que o modelo lê agora". Quem ainda manda
# RemoveMessage pra forçar o corte apaga o começo do checkpointer.
# O teto de 90 tokens é baixo de propósito, pra "15 dias" cair fora
# neste lab. Num agent real o teto é o limite do modelo. O padrão é o mesmo.
#
# Uma versão anterior deste arquivo perguntava o prazo sem nenhuma
# mensagem ter escrito o número. O modelo inventou "5 dias úteis".
# O corte tinha funcionado. A pergunta é que não tinha resposta.
# =============================================================================

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.messages import AIMessage, HumanMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

from models import Model

MARCA = "PED-100"
PRAZO_VELHO = "15 dias"
PRAZO_NOVO = "2 dias úteis"
TETO = 90  # tokens aproximados. Baixo de propósito: o 15 cai, o 2 fica.


def ticket() -> list:
    """Começo desatualizado. O prazo que vale está perto do fim."""
    msgs: list = [
        HumanMessage(
            "Abri o chamado. Código do pedido PED-100. No site o prazo de envio era 15 dias."
        )
    ]
    for i in range(6):
        msgs.append(HumanMessage(f"A loja centro ainda tem o tamanho quarenta e dois? (turno {i})"))
        msgs.append(AIMessage(f"Sim. Estoque da loja centro confirmado. (turno {i})"))
    msgs.append(AIMessage("Atualização do atendimento: o prazo de envio agora é 2 dias úteis."))
    msgs.append(HumanMessage("Qual o prazo de envio agora? Repita só o número desta atualização."))
    return msgs


def janela(msgs: list) -> list:
    """Últimas mensagens que cabem no teto. Não mexe na lista original."""
    return trim_messages(
        msgs,
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=TETO,
        start_on="human",
        end_on=("human", "tool"),
    )


def _texto(msgs: list) -> str:
    return "\n".join(str(getattr(m, "content", "")) for m in msgs)


cheio = ticket()
vista_sem_llm = janela(cheio)
assert MARCA in _texto(cheio) and PRAZO_VELHO in _texto(cheio) and PRAZO_NOVO in _texto(cheio)
assert MARCA not in _texto(vista_sem_llm)
assert PRAZO_VELHO not in _texto(vista_sem_llm)
assert PRAZO_NOVO in _texto(vista_sem_llm)
assert len(vista_sem_llm) < len(cheio)
print("=== PASSO 1 — trim_messages sem chamar o modelo ===")
print(
    "A função recebe a conversa completa e devolve outra lista, menor. "
    "A lista original não é apagada."
)
print(
    f"assert ok: conversa completa = {len(cheio)} mensagens; "
    f"recorte = {len(vista_sem_llm)} mensagens, "
    f"com {PRAZO_NOVO!r}, sem {PRAZO_VELHO!r} e sem {MARCA}."
)
print("Leitura: o corte já está certo antes de existir agent ou Ollama.")

_vista_do_modelo: list[list] = []


@wrap_model_call
def corta_vista(
    request: ModelRequest,
    handler,
) -> ModelResponse:
    """Corta o que esta chamada manda ao modelo. Não grava o recorte no state."""
    conversa_completa = list(request.messages)
    recorte = janela(conversa_completa)
    _vista_do_modelo.append(recorte)
    print("  [middleware corta_vista] Isto roda imediatamente antes do Ollama.")
    print(
        f"  [middleware] conversa completa nesta chamada: {len(conversa_completa)} mensagens. "
        "O modelo não recebe essa lista."
    )
    print(
        f"  [middleware] recorte enviado ao modelo agora: {len(recorte)} mensagens. "
        "request.override troca só esta chamada. O checkpointer não é reescrito."
    )
    print(
        f"  [middleware] no recorte, {PRAZO_NOVO!r}={PRAZO_NOVO in _texto(recorte)}, "
        f"{PRAZO_VELHO!r}={PRAZO_VELHO in _texto(recorte)}, "
        f"{MARCA}={MARCA in _texto(recorte)}."
    )
    return handler(request.override(messages=recorte))


llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)
checkpointer = InMemorySaver()
THREAD = "chamado-1"

agent = create_agent(
    model=llm,
    tools=[],
    middleware=[corta_vista],
    checkpointer=checkpointer,
    system_prompt=(
        "Você é o atendimento da loja. O cliente pede o prazo atual. "
        "Copie o prazo da atualização que está nas mensagens que você recebeu. "
        "Uma frase. Não invente outro número. Não use prazo antigo."
    ),
)


def _config() -> dict:
    return {"configurable": {"thread_id": THREAD}}


def mostra(titulo: str, msgs: list) -> None:
    print(f"--- {titulo} ---")
    for i, msg in enumerate(msgs):
        print(f"  [{i}] {type(msg).__name__}: {getattr(msg, 'content', None)!r}")


print("\n=== PASSO 2 — agent de verdade, thread chamado-1 ===")
print(
    f"invoke manda as {len(cheio)} mensagens. O checkpointer grava as {len(cheio)}. "
    "As linhas [middleware], logo abaixo, são o corte, antes do Ollama responder."
)
result = agent.invoke({"messages": cheio}, _config())

print("\n=== PASSO 3 — frase que o modelo devolveu ===")
print(result["messages"][-1].content)
print(
    "Leitura: '2 dias' = copiou o recorte. "
    "'15 dias' = usou o começo do chamado. "
    "Outro número = inventou um prazo que não estava no recorte."
)

print("\n=== PASSO 4 — mensagens que entraram no modelo ===")
print("Lista abaixo = o recorte. Não é o histórico guardado.")
if not _vista_do_modelo:
    print("  (o middleware não rodou)")
else:
    mostra("recorte", _vista_do_modelo[-1])

tup = checkpointer.get_tuple(_config())
bau_msgs = []
if tup is not None:
    bau_msgs = (tup.checkpoint.get("channel_values") or {}).get("messages") or []
print("\n=== PASSO 5 — mensagens gravadas no checkpointer ===")
print(
    "Lista abaixo = get_tuple da thread 'chamado-1'. "
    "Tem o começo (PED-100, 15 dias), o meio, o prazo novo e a resposta do passo 3."
)
print("O middleware não apagou essa lista. Ele só escondeu o começo do modelo.")
mostra("checkpointer", bau_msgs)

print("\n=== PASSO 6 — checagem ===")
print(
    "Três testes. Recorte = o que o modelo leu. "
    "Checkpointer = o que ficou gravado. Frase = o que ele respondeu."
)
ok = True
vista = _vista_do_modelo[-1] if _vista_do_modelo else []
vista_txt = _texto(vista)
bau_txt = _texto(bau_msgs)
resposta = str(result["messages"][-1].content)

if not vista or PRAZO_NOVO not in vista_txt or PRAZO_VELHO in vista_txt or MARCA in vista_txt:
    print("FAIL recorte: o modelo não recebeu só o prazo novo.")
    ok = False
else:
    print(f"ok recorte: o modelo recebeu {PRAZO_NOVO!r} e não recebeu {PRAZO_VELHO!r} nem {MARCA}.")

if PRAZO_VELHO not in bau_txt or MARCA not in bau_txt:
    print("FAIL checkpointer: o começo do chamado foi apagado.")
    ok = False
else:
    print(f"ok checkpointer: get_tuple ainda tem {PRAZO_VELHO!r} e {MARCA}.")

if PRAZO_VELHO in resposta:
    print("FAIL frase: citou 15 dias. Ou o recorte estava errado, ou o modelo ignorou as mensagens que recebeu.")
    ok = False
elif "2 dias" not in resposta:
    print("FAIL frase: não copiou 2 dias. Inventou outro prazo. O mesmo modelo serve; o número precisa estar no recorte, como no passo 4.")
    ok = False
else:
    print("ok frase: copiou o prazo novo que estava no recorte.")

if ok:
    print("ok: o modelo respondeu o prazo novo, e o chamado inteiro continua no checkpointer.")

# RESULTADO:
# === PASSO 1 — trim_messages sem chamar o modelo ===
# A função recebe a conversa completa e devolve outra lista, menor. A lista original não é apagada.
# assert ok: conversa completa = 15 mensagens; recorte = 4 mensagens, com '2 dias úteis', sem '15 dias' e sem PED-100.
# Leitura: o corte já está certo antes de existir agent ou Ollama.

# === PASSO 2 — agent de verdade, thread chamado-1 ===
# invoke manda as 15 mensagens. O checkpointer grava as 15. As linhas [middleware], logo abaixo, são o corte, antes do Ollama responder.
#   [middleware corta_vista] Isto roda imediatamente antes do Ollama.
#   [middleware] conversa completa nesta chamada: 15 mensagens. O modelo não recebe essa lista.
#   [middleware] recorte enviado ao modelo agora: 4 mensagens. request.override troca só esta chamada. O checkpointer não é reescrito.
#   [middleware] no recorte, '2 dias úteis'=True, '15 dias'=False, PED-100=False.

# === PASSO 3 — frase que o modelo devolveu ===
# 2 dias úteis.
# Leitura: '2 dias' = copiou o recorte. '15 dias' = usou o começo do chamado. Outro número = inventou um prazo que não estava no recorte.

# === PASSO 4 — mensagens que entraram no modelo ===
# Lista abaixo = o recorte. Não é o histórico guardado.
# --- recorte ---
#   [0] HumanMessage: 'A loja centro ainda tem o tamanho quarenta e dois? (turno 5)'
#   [1] AIMessage: 'Sim. Estoque da loja centro confirmado. (turno 5)'
#   [2] AIMessage: 'Atualização do atendimento: o prazo de envio agora é 2 dias úteis.'
#   [3] HumanMessage: 'Qual o prazo de envio agora? Repita só o número desta atualização.'

# === PASSO 5 — mensagens gravadas no checkpointer ===
# Lista abaixo = get_tuple da thread 'chamado-1'. Tem o começo (PED-100, 15 dias), o meio, o prazo novo e a resposta do passo 3.
# O middleware não apagou essa lista. Ele só escondeu o começo do modelo.
# --- checkpointer ---
#   [0] HumanMessage: 'Abri o chamado. Código do pedido PED-100. No site o prazo de envio era 15 dias.'
#   [1] HumanMessage: 'A loja centro ainda tem o tamanho quarenta e dois? (turno 0)'
#   [2] AIMessage: 'Sim. Estoque da loja centro confirmado. (turno 0)'
#   [3] HumanMessage: 'A loja centro ainda tem o tamanho quarenta e dois? (turno 1)'
#   [4] AIMessage: 'Sim. Estoque da loja centro confirmado. (turno 1)'
#   [5] HumanMessage: 'A loja centro ainda tem o tamanho quarenta e dois? (turno 2)'
#   [6] AIMessage: 'Sim. Estoque da loja centro confirmado. (turno 2)'
#   [7] HumanMessage: 'A loja centro ainda tem o tamanho quarenta e dois? (turno 3)'
#   [8] AIMessage: 'Sim. Estoque da loja centro confirmado. (turno 3)'
#   [9] HumanMessage: 'A loja centro ainda tem o tamanho quarenta e dois? (turno 4)'
#   [10] AIMessage: 'Sim. Estoque da loja centro confirmado. (turno 4)'
#   [11] HumanMessage: 'A loja centro ainda tem o tamanho quarenta e dois? (turno 5)'
#   [12] AIMessage: 'Sim. Estoque da loja centro confirmado. (turno 5)'
#   [13] AIMessage: 'Atualização do atendimento: o prazo de envio agora é 2 dias úteis.'
#   [14] HumanMessage: 'Qual o prazo de envio agora? Repita só o número desta atualização.'
#   [15] AIMessage: '2 dias úteis.'

# === PASSO 6 — checagem ===
# Três testes. Recorte = o que o modelo leu. Checkpointer = o que ficou gravado. Frase = o que ele respondeu.
# ok recorte: o modelo recebeu '2 dias úteis' e não recebeu '15 dias' nem PED-100.
# ok checkpointer: get_tuple ainda tem '15 dias' e PED-100.
# ok frase: copiou o prazo novo que estava no recorte.
# ok: o modelo respondeu o prazo novo, e o chamado inteiro continua no checkpointer.
