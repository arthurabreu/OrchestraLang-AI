# `cli.py`

## Marcado

- **classe**&nbsp;:&nbsp;&nbsp;nenhuma. <span style="color:#6a9955">Só funções neste arquivo.</span>
- **`main(argv=None)`**&nbsp;:&nbsp;&nbsp;monta CLI e despacha o subcomando. <span style="color:#6a9955">Ponto de entrada do orchestralang.</span>
- **L11 `p = ArgumentParser`**&nbsp;:&nbsp;&nbsp;parser raiz = programa orchestralang. <span style="color:#6a9955">Define o nome que aparece no --help.</span>
- **L12 `sub = p.add_subparsers`**&nbsp;:&nbsp;&nbsp;gaveta de subcomandos; required=True = tem que escolher um. <span style="color:#6a9955">Só orchestralang sem comando → erro + help.</span>
- **L14 `sub.add_parser("models-openrouter")`**&nbsp;:&nbsp;&nbsp;comando lista nomes free OpenRouter (sem args). <span style="color:#6a9955">Só registra o nome; lógica vem depois no if.</span>
- **L16 `s = sub.add_parser("ping")`**&nbsp;:&nbsp;&nbsp;comando smoke de 1 mensagem. <span style="color:#6a9955">s = parser só deste subcomando.</span>
- **L17–23 `s.add_argument`**&nbsp;:&nbsp;&nbsp;model opcional + --msg (só o ping tem). <span style="color:#6a9955">models-openrouter não ganha esses args.</span>
- **L25 `a = p.parse_args`**&nbsp;:&nbsp;&nbsp;lê argv → objeto com cmd, e no ping também model/msg. <span style="color:#6a9955">Depois só se olha a.cmd.</span>
- **L27–30 `models-openrouter`**&nbsp;:&nbsp;&nbsp;chama list_openrouter_free(), imprime um nome por linha. <span style="color:#6a9955">Bom pra copiar/colar no ping.</span>
- **L32–43 `ping`**&nbsp;:&nbsp;&nbsp;get_chat_model → invoke(msg) → imprime resposta; OpenRouter marca modelo no stderr. <span style="color:#6a9955">Uma ida e volta — sem loop de agente.</span>
- **L36–37 `RuntimeError`**&nbsp;:&nbsp;&nbsp;key/config ruim → sys.exit com texto (sem traceback). <span style="color:#6a9955">Exit ≠ 0 no terminal.</span>
- **L46–47 `if __name__`**&nbsp;:&nbsp;&nbsp;permite python -m / entrypoint hatch. <span style="color:#6a9955">Também roda se chamar o arquivo direto.</span>

## Resumo

Menu fino no terminal: **lista modelos free** ou **manda 1 ping no LLM** pra ver se modelo/key/Ollama respondem. Ainda sem agente.
