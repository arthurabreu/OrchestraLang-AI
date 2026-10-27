# COLA: with_structured_output = “responde no molde do Pydantic, não em prosa livre”.
# Retorno típico = instância Resumo(...), não str.
# Ollama: se der erro / None, tenta method="json_schema" ou outro Model (ex. QWEN3_8B).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama

from models import Model


class Resumo(BaseModel):
    """Resumo curto em formato fixo."""
    titulo: str = Field(description="título curto, poucas palavras")
    bullets: list[str] = Field(description="2 a 4 bullets objetivos")


llm = ChatOllama(model=Model.GEMMA3_4B, temperature=0)

# default costuma ir por tool/json do provider; se falhar, descomenta a linha de baixo
structured = llm.with_structured_output(Resumo)
# structured = llm.with_structured_output(Resumo, method="json_schema")

print("--- structured ---")
out = structured.invoke("Resuma o que é um LLM em formato estruturado.")

print("tipo:", type(out))
# print("out:", out)
print("out:", out.model_dump_json(indent=2)) # imprime o JSON da instância, mais legível

# Ve os atributos da instância:
print("--- getattr ---")
print("--------------------------------")
# print("titulo:", getattr(out, "titulo", None))
# print("bullets:", getattr(out, "bullets", None))
print("--------------------------------")