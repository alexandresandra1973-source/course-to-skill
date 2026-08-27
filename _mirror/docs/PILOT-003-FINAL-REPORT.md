# PILOT-003 — RELATÓRIO FINAL

**Curso:** *(2026) Ecommerce Google Ads Free Course (4+ Hours)* · `c6qEURhNsYw`
**Fonte:** L0 `04fda222febbaeec…` · 3h50m57s · 2.052 marcas · ASR automático
**Ground truth:** conta MTX IMPORTS - ATUAL 24/25 (170-554-4703), 15/05–12/08/2026

## Diferença de desenho declarada

**Held-out NÃO aplicado.** Os PILOT-001 e 002 escondiam território para testar se
a Skill inventava. Aqui o ground truth é EXTERNO — uma conta viva. Esconder
pedaço da fonte não testaria nada e só degradaria a Skill. Nenhum número deste
piloto é comparável aos de resistência à invenção dos outros dois.

## Pipeline

| etapa | resultado |
|---|---|
| PASS 1 (12 janelas de 20 min) | 148 segmentos · cobertura 100% · `2c09e3ce74afce8c…` |
| PASS 2 (148 chamadas) | **2.463 evidências** · cobertura L0 **78,86%** · SATISFIED · 0 revarreduras |
| pré-classificação | SOURCE_EXPLICIT 2.169 · correção ASR 47 · paráfrase 59 · **inferência genuína 188 (7,6%)** |
| compilação (148 chamadas) | **835 regras · 601 passos · 158 workflows** · 0 erros |
| cobertura evidência→regra | **89,8%** |

Densidade por segundo: **0,1777 ev/s** — a mais alta dos três pilotos, sobre o
corpus 15,3x maior que o PILOT-001.

## Os quatro critérios

**1. Cobertura > 80% — PASSA.** 89,8%.

**2. Achado específico e verdadeiro sobre o curso — PASSA.**
`negative keyword` aparece **3 vezes em 3h50m** de curso de Google Ads para
e-commerce. Sobreviveu a sete tentativas falhas de medição porque é termo inglês
buscado em texto inglês: sem tradução, sem reordenação, sem diacrítico no
caminho. E a conta confirma: **0 termos negativados em 24.795 linhas**.
Além dele: **87,5% dos campos de governança em UNDEFINED**, contra 85% do
PILOT-002. Dois cursos, dois domínios, mesma ausência.

**3(a) Conclusão específica dos dados que tem — PASSA.**
- PMax não qualifica (R-0430): exige US$50–100/dia e 30–50 conv/mês; realizado
  **R$31,11/dia e 4,83 conv/mês**;
- gate de smart bidding não atingido (R-0044): exige >=1 conv/dia por 30 dias;
  conta **0,849**, PMax **0,161**;
- **100% das keywords em correspondência ampla** — zero exata, zero frase;
- **75,7% do gasto do PMax é opaco**;
- **1.099 termos com custo e zero conversão, R$2.325,35**;
- nenhuma campanha de marca nem de Shopping operou no período.

**3(b) Pede dado que não foi dado — PASSA.** 14 pedidos explícitos, cada um com
a regra que o exige — incluindo configuração das ações de conversão (R-0130,
R-0377), motivado por ela notar que o valor médio por conversão varia
778 → 1.471 → 5.402 entre campanhas.

**4. Modo de falha (conselho genérico) — NÃO CAIU.** Toda conclusão cita
identificador de regra e número da conta. Três comportamentos que conselho
genérico não produz: recusou-se a julgar antes do break-even (R-0517); corrigiu
um erro próprio entre as etapas; e detectou três colunas quebradas nos recortes
por reconciliação aritmética, recusando-se a raciocinar sobre dados corrompidos.

## Onde parou

- **METHOD_NOT_DEFINED** — piso de volume para R-0393: a fonte manda remover
  termos com cliques e sem conversão (R-0393) e proíbe concluir de volume baixo
  (R-0389), sem definir a fronteira;
- **conflito sem precedência** — R-0386 ("nunca usar frase") contra R-0175/R-0338
  ("usar frase para variações comprovadas"). Nenhuma declara precedência. É o
  `precedence: UNDEFINED` (741 ocorrências) mordendo na primeira aplicação real;
- **lacuna de integridade** — 13,55 conversões (17,7%) sem bucket identificável.

## Reconciliação do ROAS

| | fórmula | resultado |
|---|---|---|
| 34,19 | `120.624,38 ÷ 3.528,32` — VENDAS\|ATUAL sozinha | 34,19 |
| 18,04 | `172.730,01 ÷ 9.577,32` — conta inteira | 18,04 |
| ~17,2 | `165.000 ÷ 9.580` — conta inteira, telas | 17,22 |

O 34,19 é a coluna `Valor conv. / custo` do próprio CSV, linha da campanha,
copiada verbatim e corretamente rotulada. **O fator 2 é escopo, não erro.**
Soma das 3 campanhas = linha Total: 9.577,32 e 172.730,01, ambas conferem.

**DEFEITO ENCONTRADO:** a Skill somou o custo da conta como **9.586,54** em vez
de 9.577,32 (+R$9,22), dando ROAS **18,02** onde o CSV traz **18,04**. As
parcelas que citou estão certas; a soma delas não. Ela estabeleceu a disciplina
que pegaria isso — *"custo/conv confere em todas as linhas"* — verificou as
linhas e não verificou o total.

**NÃO RECONCILIADO:** valor de conversão do CSV (172.730,01) contra as telas
(~165.000): diferença de R$7.730 (4,5%), com o custo batendo nos dois. Fechar
exige a tela de Metas — que é o pedido #4 da própria Skill, não exportado.
Registrado sem hipótese.

## RESTRIÇÃO DE PRODUTO — custo por invocação

**415.478 tokens de entrada por invocação.** O bundle compilado tem 869.405
caracteres: `decision-rules.yaml` 516 KB, `workflows.yaml` 332 KB.

Isto é **restrição de produto, não detalhe de execução.** Uma Skill de 835 regras
custa isso TODA VEZ que carrega. Consequências:

1. o custo por consulta é fixo e alto, independente da pergunta;
2. escala com o tamanho do curso: 4 horas deram 835 regras; um curso de 20 horas
   daria ~4.000 e o bundle não caberia com folga em nenhuma janela;
3. o `DISPATCH` do SKILL.md ocupa **90% do arquivo** (167 de 196 linhas) listando
   158 workflows, dos quais **40 têm passo único**;
4. carregamento seletivo — só as regras da família roteada — deixa de ser
   otimização e passa a ser requisito de viabilidade.

Previ que o DISPATCH ilegível contaminaria a aplicação. **Não contaminou** — a
Skill roteou corretamente para WF-0022, WF-0002, WF-0105 e WF-0177. Errei na
direção pessimista e registro.
