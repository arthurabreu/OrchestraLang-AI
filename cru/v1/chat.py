import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from models import Model

llm = ChatOpenAI(
    model=Model.GEMMA3_4B,
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",
    temperature=0.3,            # “quão aleatório” a resposta, sobe = mais chance de palavra “improvável”; baixo = quase sempre a favorita
    frequency_penalty=0,       # castiga repetir muito o mesmo token, se "gato" saiu 5×, castiga "gato" 5× mais forte
    presence_penalty=0,       # castiga qualquer token que já apareceu (mesmo 1×), se "gato" saiu 1×, já empurra pra escolher outra palavra     
    top_p=0.9,                 # filtro na próxima palavra: "me dá só opções boas até ~90% de chance"; ex.: candidatos [mar 40%, oceano 30%, azul 20%, xyz 10%] com p=0.9 → usa mar+oceano+azul (90%), ignora xyz; p=1 usa os 4. “alternativa à temperature” , nao usar com temperature alto
    # stop=["3.", "\n3"],    # freio: para se for gerar isso (gatilho NÃO entra na resposta); "3." = item da lista; "\n3" = variação com quebra de linha; só "stop = "3" é perigoso (para em qualquer dígito 3 no meio do texto)             
    # seed=1,               # escolhe QUAL trilha da sorte (1≠25≠99 = textos diferentes); NÃO é “número maior = mais variação” — isso é temperature/top_p; repetir o MESMO seed tenta a mesma lista; nao repetir seed para variar a mesma trilha de tokens
    # logprobs=True,       # não muda a resposta: só devolve a “nota” (log da chance) de cada pedaço gerado; perto de 0 = certeza, bem negativo = raro
    # top_logprobs=3,     # no mesmo passo, lista as 3 melhores opções; ex.: Paris -0.01 vs Par -4.7 — temp=0 pega Paris; temp=1 às vezes pega Par → "París"
   
)

SYSTEM = SystemMessage(content="Responda curto, no idioma de quem fala.")

PROMPT = HumanMessage(content="Explique o que é um LLM em 3 frases curtas.")

# Resposta direta: invoke() espera tudo → imprime de uma vez
# out = llm.invoke([SYSTEM, PROMPT])
# print(out.content)

# Resposta com stream: stream() pedaços (chunk) conforme o modelo gera; mostra “aos poucos”
print("--- stream ---")
for chunk in llm.stream([SYSTEM, PROMPT]):
    print(chunk.content, end="", flush=True)
print()

# Resposta com logprobs:
# print("--- logprobs ---")
# print(out.response_metadata.get("logprobs"))
