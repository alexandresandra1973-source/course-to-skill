# COURSE-GAP-REPORT — PILOT-004

*Gerado da compilação evidência→Skill. Nenhum número digitado.*

## Resumo

| | |
|---|---|
| regras | 32 |
| workflows | 12 |
| passos | 44 |
| evidências consumidas | 112 de 134 (83.6%) |
| **regras só de inferência genuína** | **2** |
| campos UNDEFINED | 259 |

## Campos UNDEFINED — lacuna pedagógica

Os quatro preservados por decisão. Nenhum é metadado: os quatro são perguntas que a execução faz e o curso não responde.

| campo | vezes | a pergunta que o curso não responde |
|---|---|---|
| `autonomy` | 76 | até onde o agente pode agir sozinho antes de parar |
| `iteration_limit` | 76 | quantas vezes repetir antes de desistir |
| `missing_input_action` | 76 | o que fazer quando falta um insumo obrigatório |
| `precedence` | 31 | qual regra ganha quando duas se aplicam |

> **Nenhum metadado nesta lista.** O esquema é subconjunto: os 30 campos legados que eram metadado foram descartados por decisão registrada, com o motivo escrito em `ctss/schema.py`. O que sobra aqui é lacuna do curso.

---

## Regras e passos que o curso NÃO ensinou

**4** entidades se apoiam SÓ em inferência genuína. Funcionam — mas o modelo as preencheu, não o curso. Para cada uma, a cadeia:

### `R-0015` — Dispensar ferramenta paga de agendamento

**a regra diz:** O Planner do Meta Business Suite oferece agendamento de forma gratuita → Usar o Planner em vez de contratar ferramenta paga para essa função

> **o curso disse** (5:38): ferramenta cara aí para fazer postagem, agendamento de postagem, agendamento de

**o modelo concluiu:** O Planner do Meta Business Suite permite fazer agendamento de postagens de forma gratuita, dispensando a contratação de ferramenta paga para essa função

**distância:** (não medida)

### `S-0024` — Acessar a área de automações

**a regra diz:** Abrir a área de automações localizada na parte de cima da ferramenta para configurar mensagens automáticas e gatilhos → Abrir a área de automações localizada na parte de cima da ferramenta para configurar mensagens automáticas e gatilhos

> **o curso disse** (8:45): E aqui nas

**8:45**

automações você consegue configurar

**8:47**

mensagens automáticas, eh gatilhos, né? como se fosse quase um main chat

**8:52**

gratuito para algumas situações que vai facilitar para você também.

**o modelo concluiu:** Nas automações é possível configurar mensagens automáticas e gatilhos, funcionando como um chatbot gratuito para algumas situações

**distância:** (não medida)

### `S-0025` — Configurar mensagens automáticas e gatilhos

**a regra diz:** Dentro de automações, configurar mensagens automáticas e gatilhos, usando o recurso como um chatbot gratuito para algumas situações → Dentro de automações, configurar mensagens automáticas e gatilhos, usando o recurso como um chatbot gratuito para algumas situações

> **o curso disse** (8:45): E aqui nas

**8:45**

automações você consegue configurar

**8:47**

mensagens automáticas, eh gatilhos, né? como se fosse quase um main chat

**8:52**

gratuito para algumas situações que vai facilitar para você também.

**o modelo concluiu:** Nas automações é possível configurar mensagens automáticas e gatilhos, funcionando como um chatbot gratuito para algumas situações

**distância:** (não medida)

### `R-0026` — Selecionar trilha de campanha conforme modelo de negócio

**a regra diz:** O modelo de negócio do anunciante é identificado como negócio local, venda no X1 por mensagem, ou venda direta para infoprodutor/afiliado → Seguir a trilha de campanha correspondente ao modelo de negócio identificado (negócio local, venda no X1 via mensagem, ou venda direta para infoprodutor/afiliado)

> **o curso disse** (11:09): pegar na sua mão do básico avançado para negócio local, para vender no X1 através

**11:13**

de mensagem, para fazer campanhas para venda direta também, se você é um

**11:17**

infoprodutor, um afiliado.

**o modelo concluiu:** Campanhas de anúncios no Facebook/Instagram são tratadas em trilhas distintas conforme o modelo de negócio: negócio local, venda no X1 por mensagem, e venda direta para infoprodutor ou afiliado

**distância:** (não medida)

---

## Evidência não consumida

| disposição | n | significado |
|---|---|---|
| NON_METHODOLOGICAL | 20 | contexto, motivação, mercado — não é método |
| GAP | 2 | é método, mas a fonte não dá o suficiente |

### Método que a fonte menciona sem especificar

| onde | o que o curso disse |
|---|---|
| **0:43** | A abordagem adotada é uma demonstração prática na tela do computador, em formato de passo a passo completo da  |
| **9:17** | Entre as configurações disponíveis está identificar mensagens respondidas |

