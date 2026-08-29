# Calibração do medidor de densidade — reprovado no canário

- Gerado: `2026-08-11T04:06:54+00:00` · gerador `density_calibration.py`
- READ-ONLY sobre `Course-to-Skill/`
- Fonte: `Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources/transcript/transcript-original-en.txt` · sha256 `068b4998c160d143…`

## Canário de calibração

| | |
|---|---|
| exigido | PILOT-001 deve sair **FINA** |
| medidor deu | **NAO_FINA** (49 pontos de decisão > 45) |
| resultado | **REPROVADO** |

**Nenhum veredito de densidade é emitido enquanto o medidor não passar no canário.** O `SOURCE-DENSITY-COMPARISON.md` não deve ser usado para qualificar o PILOT-002.

## 1. Os 49 itens que o medidor contou, nominalmente

| # | disparo | categoria | trecho | por quê |
|---|---|---|---|---|
| 1 | `should` | RETORICA | In this video, we're going to answer every question you should be asking about AI agents right  | enquadramento do vídeo |
| 2 | `start with` | RETORICA | All right, let's start with the most uncomfortable question of them all. | transição de seção |
| 3 | `If` | RETORICA | If your answer is, "I'm not sure," that's usually a yes, and here's how to tell. | diagnóstico retórico, sem ação |
| 4 | `don't` | AFIRMACAO | Marketing teams don't fail because they're not creative. | tese, não regra |
| 5 | `when` | AFIRMACAO | And when you start with outcomes, you stop building one-off automations and start building some | consequência declarada |
| 6 | `if` | RETORICA | So if you feel like you need to hire someone or things keep falling through the cracks, yeah, y | diagnóstico retórico |
| 7 | `If` | DEFINICAO | If this happens, do that. | define o que é automação |
| 8 | `when` | DEFINICAO | Like an automation that sends a welcome email when someone signs up. | exemplo ilustrativo |
| 9 | `when` | DEFINICAO | And it adapts when conditions change. | define o que é agente |
| 10 | `if` | RETORICA | So, if you've been relying on chat bots and automations and wondering why things still fall thr | transição retórica |
| 11 | `start with` | RETORICA | So let's start with the most important one. | transição de seção |
| 12 | `If` | AFIRMACAO | If any one of these is missing or weak, the whole thing falls apart. | asserção sobre o modelo |
| 13 | `must` | DEFINICAO | Who it is, what it does, what it's allowed to do and what it must never do. | define o system prompt |
| 14 | `never` | DEFINICAO | Eager, tireless, and never complains, but needs clear instructions and someone checking their w | analogia do novo contratado |
| 15 | `should` | RETORICA | So with that being said, which agents should you build first? | transição de seção |
| 16 | `start with` | RETORICA | We won't start with the flashiest or the most complex ones, but let's start with the agents tha | narração da seleção |
| 17 | `should` | RETORICA | But the next question people ask is, "What platform should you build on?" Honestly, it matters  | transição + asserção |
| 18 | `choose` | **RAMO** | Here's how to choose based on where you are right now. | abre a tabela de plataforma |
| 19 | `If` | **RAMO** | If you're already on HubSpot Professional or Enterprise, start here. | ramo: HubSpot Breeze |
| 20 | `if` | **RAMO** | is the fastest way to your first working agent if you're already in the ecosystem. | reafirma a condição HubSpot |
| 21 | `If` | **RAMO** | If you want to build without any code, and you're doing research or content heavy work, Claude  | ramo: Claude |
| 22 | `If` | **RAMO** | If you're more of a visual thinker, Gum Loop is worth a look. | ramo: Gumloop |
| 23 | `If` | **RAMO** | If you're already on Zapier, Zapier agents lets an AI take over decisions inside your existing  | ramo: Zapier Agents |
| 24 | `If` | **RAMO** | If you can't run a command line, this isn't safe for you. | portão de segurança do OpenClaw |
| 25 | `If` | **RAMO** | If any of the tools we just covered do what you need, start there. | prefira o já coberto |
| 26 | `when` | **RAMO** | Open Claw is the one you reach for when you have a specific piece of software that nothing else | ramo: último recurso |
| 27 | `start with` | **PASSO_LINEAR** | Step one, start with the outcome. | passo 1 do checklist |
| 28 | `never` | DEFINICAO | Basically, what the agent is never allowed to do. | define boundaries |
| 29 | `never` | DEFINICAO | For the HubSpot YouTube intelligence agent, this looked like three competitor URLs as the input | exemplo trabalhado |
| 30 | `instead of` | AFIRMACAO | You'll end up automating a task instead of owning an outcome. | consequência do erro |
| 31 | `choose` | **PASSO_LINEAR** | Step three, choose your platform and connect the tools. | passo 3 do checklist |
| 32 | `choose` | **PASSO_LINEAR** | This is where you choose what you're building in and what it's going to connect to. | reafirma o passo 3 |
| 33 | `choose` | **PASSO_LINEAR** | Whatever platform you choose, one of the first things you want to look at is what it can actual | olhar integrações |
| 34 | `If` | **RAMO** | If you want to run it automatically every Monday without touching it, you'd add a Zapier schedu | opcional: agendar no Zapier |
| 35 | `Instead of` | **PASSO_LINEAR** | Instead of starting from scratch every time, you give it context about who you are, who you ser | passo 4: memória |
| 36 | `If` | **RAMO** | If you're an e-commerce brand, it's your product catalog and customer personas. | ramo: contexto de e-commerce |
| 37 | `If` | **RAMO** | If you're a B2B company, it's your ICP and your positioning doc. | ramo: contexto B2B |
| 38 | `if` | **RAMO** | And if you're an agency, it's your client brief. | ramo: contexto de agência |
| 39 | `don't` | AFIRMACAO | Every time it produces something off brand or surface level, don't make the mistake of giving u | não desista |
| 40 | `if` | **RAMO** | After 30 days, if it's consistently solid, loosen the review and let it run. | portão: afrouxar revisão |
| 41 | `If` | **RAMO** | If both are yes, expand it. | portão: expandir |
| 42 | `If` | **RAMO** | If either's a no, go back and rebuild it. | portão: reconstruir |
| 43 | `Don't` | AFIRMACAO | Don't let dead agents live in your stack. | slogan |
| 44 | `Make sure` | **PASSO_LINEAR** | Make sure that's toggled on so it pulls live data. | ligar a busca web |
| 45 | `don't` | AFIRMACAO | But don't try to build everything at once. | conselho genérico |
| 46 | `Start with` | **PASSO_LINEAR** | Start with one gap. | escolher o primeiro agente |
| 47 | `If` | CTA_PLUG | If you want to go deeper on any of this, I highly recommend checking out the free guide linked  | brinde |
| 48 | `If` | CTA_PLUG | If this video helped in any way, give it a like to let us know and make sure to share it with y | curtir e compartilhar |
| 49 | `make sure` | CTA_PLUG | For more helpful marketing content and resources, make sure to subscribe to HubSpot Marketing f | inscrever-se |

## 2. Quantos são condicionais triviais de tutorial

| categoria | itens | é decisão? |
|---|---|---|
| `RETORICA` | 9 | não |
| `AFIRMACAO` | 7 | não |
| `DEFINICAO` | 7 | não |
| `CTA_PLUG` | 3 | não |
| `PASSO_LINEAR` | 7 | sim |
| `RAMO` | 16 | sim |

**26 dos 49 (53%) não são decisão nenhuma.** São pergunta retórica, transição de seção, definição de termo, exemplo, slogan e chamada para curtir e se inscrever. O medidor os contou porque `if`, `when`, `should`, `never` e `make sure` aparecem em todos eles — em inglês falado essas palavras são cola de discurso, não sintaxe de regra.

Casos que mostram bem o problema:

- **item 7** — *"If this happens, do that."* → define o que é automação
- **item 14** — *"Eager, tireless, and never complains, but needs clear instructions and someone checking th"* → analogia do novo contratado
- **item 48** — *"If this video helped in any way, give it a like to let us know and make sure to share it w"* → curtir e compartilhar

## 3. O que sobra por leitura estrutural

Tirando os 26 não-decisões, sobram 7 passos lineares e 16 itens com ramo. Esses 16 não são 16 decisões independentes: colapsam em **5 estruturas**.

### escolha de plataforma — tabela de decisão multi-ramo

- itens do medidor: 18, 19, 20, 21, 22, 23, 24, 25, 26
- ramos: HubSpot Breeze, Claude, Gumloop, Zapier Agents, OpenClaw (último recurso, com portão de segurança)
- nota: É a única tabela realmente multi-ramo da aula.

### que contexto dar por tipo de empresa — mapeamento ilustrativo

- itens do medidor: 36, 37, 38
- ramos: e-commerce, B2B, agência
- nota: Três ramos, mas ilustram o mesmo passo de memória com exemplos por segmento. Fica no limite entre tabela e exemplo.

### afrouxar a revisão humana — portão

- itens do medidor: 40
- ramos: ≥30 dias e consistente → afrouxa

### expandir ou reconstruir — portão

- itens do medidor: 41, 42
- ramos: ambas sim → expande, qualquer não → reconstrói

### agendamento automático — opcional

- itens do medidor: 34
- ramos: quer rodar sozinho → agenda no Zapier

A premissa da tarefa se confirma, com um ajuste: há **uma** tabela realmente multi-ramo — a de plataforma — e o resto é checklist linear mais três portões simples. O mapeamento por tipo de empresa tem três ramos, mas ilustra um único passo de memória; classificá-lo como tabela ou como exemplo é chamada de julgamento, e por isso está declarado, não escondido num contador.

## 4. Por que não ajustei o regex

| cenário de exclusão | contagem | daria |
|---|---|---|
| bruto, sem exclusão | 49 | NAO_FINA |
| menos CTA/plug | 46 | NAO_FINA |
| menos CTA/plug e retórica | 37 | FINA |
| menos tudo que não é decisão | 23 | FINA |

Dá para fazer o canário passar excluindo categorias. Mas repare no que isso é: as categorias foram lidas **deste** vídeo, uma fonte, à mão. Calibrar o contador contra n=1 até o número bater não produz um medidor — produz um número que concorda com quem o ajustou. É exatamente o defeito que o projeto persegue nos outros artefatos, e seria pior aqui, porque este medidor existe para decidir se vale gastar um corpus inteiro.

## 5. Achado

**A contagem puramente léxica não separa metodologia de discurso, e não deve ser a métrica que decide.**

Em transcrição de aula falada, `if`, `when`, `should`, `never` e `make sure` funcionam como conectivo retórico com a mesma frequência com que funcionam como condição de regra. Nenhum ajuste de vocabulário resolve isso sem ler a estrutura: a diferença entre *"If this happens, do that"* (definição de automação) e *"If you're already on Zapier…"* (ramo de tabela) não está nas palavras, está no papel que a frase cumpre.

**Consequência prática.** A métrica que decide se uma fonte qualifica precisa ser publicada como **lista enumerada e auditável** — cada ponto de decisão nomeado, com o trecho que o sustenta e a estrutura a que pertence, como nas seções 1 e 3 acima. Um número de regex pode acompanhar como indício, nunca como veredito.

O que o medidor continua servindo para medir sem ressalva: duração, palavras, palavras por minuto, limiares numéricos e frameworks nomeados. São contagens de superfície e é isso que elas dizem ser.

## 6. Estado do PILOT-002

Sem veredito. O canário reprovou, então o instrumento não está apto a qualificar ou desqualificar o candidato. Qualificar o PILOT-002 exige enumerar as decisões dele à mão, no formato da seção 3, e comparar estrutura com estrutura.

