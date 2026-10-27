import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from models import Model

llm = ChatOllama(
    model=Model.GEMMA3_4B,
    temperature=0.3,   # igual ideia do v1
    top_p=0.9,         # igual ideia do v1
    top_k=80,          # filtro por QUANTIDADE na próxima palavra: “só as k melhores”; ex. candidatos [mar, oceano, azul, … 200] com k=3 → só mar/oceano/azul; k=1 ≈ sempre a #1. top_p = corta por %; top_k = corta por contagem (dá pra combinar)
)

SYSTEM = SystemMessage(content="Responda curto, no idioma de quem fala.")
PROMPT = HumanMessage(content="Liste 5 palavras relacionadas a oceano. Só a lista numerada.")

print("--- ChatOllama ---")
for chunk in llm.stream([SYSTEM, PROMPT]):
    print(chunk.content, end="", flush=True)
print()
