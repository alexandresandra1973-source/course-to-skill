# T8 — BLOCO 4 preliminar · leitura dos critérios

A resposta **verbatim** está em `T8-MTX-APLICACAO-VERBATIM.md`. Este arquivo só
lê o resultado contra os critérios. **Nenhum dado do Business Suite da MTX foi
fornecido e nenhum estado de conta foi simulado** — a conferência contra a conta
real é com o Alexandre.

Contexto dado, e só ele:

> empresa de peças de moto com Instagram, Facebook e WhatsApp Business; quer
> gerenciar os três canais de forma unificada

Duas execuções. A primeira bateu no teto de 8.000 tokens e truncou antes das
seções 3 e 4 — justamente as que carregam C3b e C4. Refeita com teto de 24.000,
`stop_reason: end_turn`, 11.702 tokens de saída. As duas contam no custo.

## C3, metade b — o que a Skill PEDE

**Pede 15 itens específicos, agrupados em quatro blocos, cada um com o caminho na
interface e a regra que o exige.** Amostra literal:

- *"Leitura do topo do painel: aparecem ambos os ícones (página do Facebook e
  Instagram) acesos, ou só o Facebook? Onde: topo do painel (S-0008). É esse o
  critério de conformidade da fonte (R-0007 / R-0008)."*
- *"Existe portfólio empresarial? E, se existe, quais ativos estão dentro dele:
  contas de anúncio, pixel, estrutura de anúncio. Onde: portfólio empresarial /
  seção Contas do Gerenciador (S-0039, S-0040)."*
- *"Modelo de negócio declarado, entre os três que a fonte reconhece... Peças de
  moto **não** se encaixa automaticamente — não vou classificar por você."*

Esse último é o comportamento que o C3b procura: a Skill reconheceu que o caso da
MTX não cai em nenhuma das três trilhas da fonte e **pediu a classificação em vez
de escolher uma**.

**Metade b do C3: satisfeita** — pede o dado certo, nomeado, com origem.
A metade a (produzir configuração conferível na conta real) fica para amanhã.

## Onde a Skill PARA

- **`MISSING_REQUIRED_INPUT`** (RG-013-003): outcome existe, mas `input`,
  `output` e `boundaries` não. Parou e nomeou o primeiro campo faltante: `input`.
- **`METHOD_NOT_DEFINED`** em quatro pontos, todos específicos: trilhas de
  campanha por modelo de negócio (R-0026); **como conectar** o WhatsApp Business;
  criação de página e de conta de anúncio (S-0044); e pixel, fora de escopo por
  decisão da própria fonte (R-0030).
- **`UNDEFINED` sistemático**, com a consequência dita: `autonomy` em 100% dos 44
  passos e 32 regras → *"nenhum passo autoriza execução autônoma; tudo é
  orientação para operador humano"*.

A Skill **também encontrou sozinha** a lacuna de instrumento que documentei no
T7: o `knowledge/questions.yaml` que os guards mandam usar não existe no pacote.
Ela registrou a incompatibilidade em vez de inventar a pergunta:

> *"esse arquivo não está no bundle de runtime, e o ADR-0004 citado pelo guard
> não existe em decision-rules.yaml. Consequência: não vou inventar o enunciado
> canônico da pergunta."*

E marcou o vocabulário estranho sem reinterpretá-lo:

> *"o guard RG-013-003 fala em 'montar um agente' — vocabulário do compilador,
> não do curso. Registro a incompatibilidade em vez de reinterpretá-la."*

## C4 preliminar — modo de falha NÃO acionado

O C4 declara falha se a saída for conselho genérico do tipo "conecte suas contas,
poste com frequência". Não é o caso:

- toda recomendação vem com **passo, caminho na interface e id de regra/workflow**
  (`S-0004: alternar → alternar → contas vinculadas`;
  `Configurações → Usuários → Pessoas`);
- traz **proibições** da fonte, não só sugestões: não deixar a estrutura fora do
  portfólio, não usar link clicável no texto do Instagram, não postergar o
  administrador adicional;
- traz uma **decisão fechada e justificada** — não contratar ferramenta paga de
  agendamento, porque o Planner faz de graça (R-0015);
- e **recusa** onde a fonte não ensina, em vez de completar com conhecimento
  geral.

A seção 4 lista 9 coisas que a Skill não cobre, e todas são verdadeiras para este
vídeo: e-commerce e catálogo, métricas de campanha paga (CPA, ROAS, CTR),
recuperação de conta bloqueada, SLA e fila de atendimento, WhatsApp Business API.

**C4 preliminar: NÃO acionado.** Confirmação definitiva depende da conferência
contra a conta real.

## Estado dos quatro critérios após a noite

| | estado |
|---|---|
| **C1** cobertura evidência→regra >80% | **PASSA — 83,58%** (112/134) |
| **C2** GAP-REPORT específico e verdadeiro | **material reunido**, 5 candidatos conferíveis por timestamp — avaliação é do Alexandre |
| **C3** aplicação ao Business Suite real | **metade b satisfeita**; metade a depende da conta real |
| **C4** modo de falha (conselho genérico) | **não acionado** em preliminar |
