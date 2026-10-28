# =============================================================================
# LIÇÃO: context_schema / Runtime Context
# =============================================================================
#
# PERGUNTA QUE ESTA LIÇÃO RESPONDE
# --------------------------------
# "O usuário logado perguntou 'qual meu saldo?'. Como a tool sabe QUAL conta
# consultar, se o texto do chat NÃO traz o user_id?"
#
# Resposta LangChain 1.x: Runtime Context — um dataclass que VOCÊ passa no
# invoke (fora das messages). Tools/middleware leem via ToolRuntime.context.
#
#
# TRÊS GAVETAS DIFERENTES (não misturar)
# --------------------------------------
# 1) messages          = o que o modelo lê (Human/AI/Tool). Texto da conversa.
# 2) checkpointer      = histórico POR thread_id entre turns (v3 C). "O que
#    já falamos neste fio." Some se mudar thread / processo (InMemory).
# 3) context (AQUI)    = crachá DESTA corrida. Quem é o user, tenant, api_key,
#    feature flag… Passa de novo a cada invoke. NÃO é histórico.
#
# Em produção costuma-se passar OS DOIS: thread_id (conversa) + context (quem).
# Nesta lição NÃO usamos checkpointer de propósito — só o crachá.
#
#
# POR QUE NÃO SÓ COLOCAR user_id NA MENSAGEM / SYSTEM PROMPT?
# -----------------------------------------------------------
# - Segredo: api_key no context fica na tool; modelo não precisa ver no prompt.
# - Tipado: dataclass/TypedDict — IDE e erros claros; não é string solta.
# - Mesmo agent, muitos users: CLI/web injeta Ctx(user_id=…) por request.
# - Modelo NÃO vê o context sozinho. Se ninguém (tool/middleware) ler e
#   devolver, o LLM inventa (foi o FAIL B da versão anterior: "Viking").
#   Por isso a lição força tool: verdade vem do runtime, não da imaginação.
#
#
# UTILIDADE REAL (mini)
# ---------------------
# SaaS multi-user: request autenticado → context=Ctx(user_id=sessão.uid)
# → tool saldo/consulta_db usa esse id. User digita só "meu saldo".
# Mesmo padrão: locale, plano (free/pro), conexão DB, flags.
#
# =============================================================================

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_ollama import ChatOllama

from models import Model

# --- "banco" fake: a verdade mora AQUI, não na cabeça do LLM ---
# Chave = user_id que vem do context (login), não do texto do user.
SALDOS: dict[str, int] = {
    "u-alice": 10,
    "u-bob": 999,
}


@dataclass
class Ctx:
    """Crachá da corrida. Shape fixo → create_agent(context_schema=Ctx)."""
    user_id: str  # quem está autenticado nesta request


@tool
def consultar_saldo(runtime: ToolRuntime[Ctx]) -> str:
    """Consulta o saldo da conta do usuário autenticado (não pede user_id)."""
    # runtime.context = o Ctx que você passou no agent.invoke(..., context=...)
    uid = runtime.context.user_id
    if uid not in SALDOS:
        return f"conta inexistente para user_id={uid}"
    return f"user_id={uid} saldo={SALDOS[uid]}"


# --- 1) domínio sem LLM (sempre passa; prova a regra do "banco") ---
assert SALDOS["u-alice"] == 10 and SALDOS["u-bob"] == 999
print("assert ok: banco fake alice=10 bob=999")
print(
    "nota: consultar_saldo só funciona com runtime injetado pelo agent;\n"
    "      invoke manual da tool sem ToolRuntime não é o caminho deste lab."
)

# --- 2) agent: mesma pergunta, crachás diferentes ---
llm = ChatOllama(model=Model.QWEN3_8B, temperature=0, reasoning=False)

agent = create_agent(
    model=llm,
    tools=[consultar_saldo],
    context_schema=Ctx,  # declara o formato do crachá
    system_prompt=(
        "Você é um caixa. Para qualquer pergunta sobre saldo ou dinheiro, "
        "OBRIGATÓRIO chamar a ferramenta consultar_saldo. "
        "Não invente números. Depois de receber o ToolMessage, responda "
        "em uma linha repetindo exatamente o retorno da ferramenta."
    ),
)

# Mesma frase nas duas corridas — user NÃO diz quem é.
# Quem diferencia A de B é só o context=Ctx(...), não o texto.
PERGUNTA = "Qual é o meu saldo? Use a ferramenta. Não invente."


def corre(user_id: str) -> list:
    """Simula request autenticada: app já sabe o user_id; chat só traz a pergunta."""
    ctx = Ctx(user_id=user_id)
    print(f"  [request] messages=só a pergunta | context.user_id={user_id!r}")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": PERGUNTA}]},
        context=ctx,  # ← crachá desta corrida (fora de messages)
    )
    return result["messages"]


def mostra_trilha(msgs: list) -> str | None:
    tool_content = None
    for i, msg in enumerate(msgs):
        kind = type(msg).__name__
        tool_calls = getattr(msg, "tool_calls", None) or []
        print(f"  [{i}] {kind}")
        print("      content:", getattr(msg, "content", None))
        if tool_calls:
            print("      tool_calls:", tool_calls)
        if kind == "ToolMessage":
            tool_content = getattr(msg, "content", None)
    return tool_content


print("\n=== O QUE OLHAR ===")
print("1) HumanMessage é IDÊNTICO nas duas corridas.")
print("2) Diferença só no context (print [request]).")
print("3) ToolMessage deve vir do banco fake (alice→10, bob→999), não do LLM.")
print("4) Sem ToolMessage = modelo inventou = FAIL didático (troca Model/prompt).")

print("\n--- corrida Alice (context user_id=u-alice) ---")
tool_a = mostra_trilha(corre("u-alice"))

print("\n--- corrida Bob (context user_id=u-bob) ---")
tool_b = mostra_trilha(corre("u-bob"))

print("\n=== LEITURA ===")
print("Alice ToolMessage:", tool_a)
print("Bob   ToolMessage:", tool_b)
print(
    "Utilidade: mesmo agent + mesma pergunta; o 'quem' vem do login (context),\n"
    "não do texto. Checkpointer (v3) seria outro eixo: lembrar turns do fio."
)

ok = True
if not tool_a or "u-alice" not in str(tool_a) or "10" not in str(tool_a):
    print("FAIL Alice: esperava ToolMessage com u-alice e saldo 10.")
    ok = False
if not tool_b or "u-bob" not in str(tool_b) or "999" not in str(tool_b):
    print("FAIL Bob: esperava ToolMessage com u-bob e saldo 999.")
    ok = False
if tool_a and tool_b and str(tool_a) == str(tool_b):
    print("FAIL: Alice e Bob iguais — context não chegou na tool?")
    ok = False
if ok:
    print("ok: context_schema mudou o user_id entre invokes; tool leu o crachá.")

# RESULTADO:
# assert ok: banco fake alice=10 bob=999
# nota: consultar_saldo só funciona com runtime injetado pelo agent;
#       invoke manual da tool sem ToolRuntime não é o caminho deste lab.
#
# === O QUE OLHAR ===
# 1) HumanMessage é IDÊNTICO nas duas corridas.
# 2) Diferença só no context (print [request]).
# 3) ToolMessage deve vir do banco fake (alice→10, bob→999), não do LLM.
# 4) Sem ToolMessage = modelo inventou = FAIL didático (troca Model/prompt).
#
# --- corrida Alice (context user_id=u-alice) ---
#   [request] messages=só a pergunta | context.user_id='u-alice'
#   [0] HumanMessage
#       content: Qual é o meu saldo? Use a ferramenta. Não invente.
#   [1] AIMessage
#       content:
#       tool_calls: [{'name': 'consultar_saldo', 'args': {}, 'id': '2c7cb2e0-8ce2-4904-91f8-6c1999797700', 'type': 'tool_call'}]
#   [2] ToolMessage
#       content: user_id=u-alice saldo=10
#   [3] AIMessage
#       content: O seu saldo é 10.
#
# --- corrida Bob (context user_id=u-bob) ---
#   [request] messages=só a pergunta | context.user_id='u-bob'
#   [0] HumanMessage
#       content: Qual é o meu saldo? Use a ferramenta. Não invente.
#   [1] AIMessage
#       content:
#       tool_calls: [{'name': 'consultar_saldo', 'args': {}, 'id': '9eeb32b9-164c-4010-9b59-668c4b458d1c', 'type': 'tool_call'}]
#   [2] ToolMessage
#       content: user_id=u-bob saldo=999
#   [3] AIMessage
#       content: Seu saldo é 999.
#
# === LEITURA ===
# Alice ToolMessage: user_id=u-alice saldo=10
# Bob   ToolMessage: user_id=u-bob saldo=999
# Utilidade: mesmo agent + mesma pergunta; o 'quem' vem do login (context),
# não do texto. Checkpointer (v3) seria outro eixo: lembrar turns do fio.
# ok: context_schema mudou o user_id entre invokes; tool leu o crachá.