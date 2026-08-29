# RUBRIC_CEILING_ANALYSIS — TEST-0007 e TEST-0008

**Gerado:** `2026-08-10T17:43:50.401481+00:00` · Relatório produzido por script (`rubric_ceiling_report.py`); nenhum número foi digitado.


## 0. As entradas nomeadas na tarefa não existem

| arquivo pedido | localização no Drive |
|---|---|
| blind-test-results-v0.1.2.yaml | **NÃO ENCONTRADO** |
| JUDGE_REPORT-v0.1.2.md | **NÃO ENCONTRADO** |

O estado registrado pelo próprio pacote do juiz é `status: PENDING_REGRESSION_BLIND_EXECUTION`, com `total_score`, `margin` e todos os escores em `null`. **A rodada cega não foi executada** — não há pontuação por critério para extrair, de nenhum dos dois testes.

O que segue não depende dos escores: é o teto do **instrumento**, computável a partir da régua e dos pacotes dos braços. Ele responde à pergunta do item 3 antes de a rodada acontecer.


---

## Régua v0.1.2


### TEST-0007 — ABLATION (`status: READY`)

Braço completo: `TEST-0007:A` (15 arquivos) · comparado: `TEST-0007:B` (13 arquivos)

| critério | peso | mínimo | obrigatório |
|---|---|---|---|
| EXECUTION_QUALITY | 0.4 | 85 | sim |
| CONSISTENCY | 0.2 | 80 | sim |
| HUMAN_CHECKPOINT_COMPLIANCE | 0.2 | 90 | sim |
| METHODOLOGY_FIDELITY | 0.2 | 85 | sim |

**Teto aritmético**

| item | valor |
|---|---|
| soma dos pesos | 1.0 |
| piso ponderado de um braço que passa (Σ w·min) | 85.0 |
| máximo da escala | 100 |
| folga acima do piso | 15.0 |
| margem máxima se AMBOS os braços passam | 15.0 |
| margem exigida (`required_margin_over_baseline`) | 5 |

**Teto evidencial — quanto peso da régua consegue separar os braços**

| critério | peso | veredito | exclusivo do braço completo | presente nos DOIS braços |
|---|---|---|---|---|
| EXECUTION_QUALITY | 0.4 | EMPATA | — | procedimento de execução completo, etapa de testes, etapa de medição |
| CONSISTENCY | 0.2 | EMPATA | — | ordem lógica das etapas, gates |
| HUMAN_CHECKPOINT_COMPLIANCE | 0.2 | EMPATA | — | checkpoint de revisão humana, período inicial |
| METHODOLOGY_FIDELITY | 0.2 | SEPARA | corpo de regra de decisão (condicao->consequencia), condição de plataforma nomeada | anti-padrões |

- peso que **separa**: **0.2** · peso que **empata**: **0.8**
- **margem máxima disponível pelos critérios que separam: 20.0 pontos**

**Margem disponível, por regime do braço comparado**

| regime | margem máx. | vs exigida = 5 |
|---|---|---|
| PISO — o braço comparado também respeita os mínimos obrigatórios (Σ w·(max−min) sobre os critérios que separam) | 3.0 | **INATINGÍVEL** |
| LIVRE — o braço comparado não precisa passar (Σ w·max) | 20.0 | ALCANÇÁVEL |

> **A margem de 5 só existe se o braço comparado REPROVAR na régua.** Não basta ele ser pior: ele tem de cair abaixo dos mínimos obrigatórios. Um braço comparado meramente inferior, mas aprovado, não consegue produzir a margem exigida.


> **Confundidor de desenho:** o braço comparado mantém, no `SKILL.md`, ponteiro para arquivo que a ablação removeu — `PILOT-001-agent-input-v0.1.2/agent-input/runtime-bundle/knowledge/decision-rules.yaml`. O agente pode responder "as regras estão em `knowledge/decision-rules.yaml`" e ser penalizado por artefato de empacotamento, não por falta de conhecimento.


**Elementos exigidos em `expected_output.required_elements`**

| elemento | braço completo | braço comparado |
|---|---|---|
| Outcome, input, output e boundaries | sim | sim |
| ROBOT prompt | sim | sim |
| Plataforma e ferramentas | sim | sim |
| Memória/contexto | sim | sim |
| 3 a 5 testes | sim | sim |
| Humano no loop | sim | sim |
| Critérios de medição | sim | sim |

0 de 7 elementos exigidos são exclusivos do braço completo.


### TEST-0008 — SUMMARY_VS_SKILL (`status: READY`)

Braço completo: `TEST-0008:B` (15 arquivos) · comparado: `TEST-0008:A` (3 arquivos)

| critério | peso | mínimo | obrigatório |
|---|---|---|---|
| EXECUTION_QUALITY | 0.3 | 85 | sim |
| CONSISTENCY | 0.2 | 80 | sim |
| HUMAN_CHECKPOINT_COMPLIANCE | 0.2 | 90 | sim |
| METHODOLOGY_FIDELITY | 0.2 | 85 | sim |

**Teto aritmético**

| item | valor |
|---|---|
| soma dos pesos | 0.9 |
| piso ponderado de um braço que passa (Σ w·min) | 76.5 |
| máximo da escala | 100 |
| folga acima do piso | 23.5 |
| margem máxima se AMBOS os braços passam | 23.5 |
| margem exigida (`required_margin_over_baseline`) | 5 |

**Teto evidencial — quanto peso da régua consegue separar os braços**

| critério | peso | veredito | exclusivo do braço completo | presente nos DOIS braços |
|---|---|---|---|---|
| EXECUTION_QUALITY | 0.3 | SEPARA | procedimento de execução completo, etapa de testes, etapa de medição | — |
| CONSISTENCY | 0.2 | SEPARA | ordem lógica das etapas, gates | — |
| HUMAN_CHECKPOINT_COMPLIANCE | 0.2 | EMPATA | — | checkpoint de revisão humana, período inicial |
| METHODOLOGY_FIDELITY | 0.2 | SEPARA | corpo de regra de decisão (condicao->consequencia), condição de plataforma nomeada, anti-padrões | — |

- peso que **separa**: **0.7** · peso que **empata**: **0.2**
- **margem máxima disponível pelos critérios que separam: 70.0 pontos**

**Margem disponível, por regime do braço comparado**

| regime | margem máx. | vs exigida = 5 |
|---|---|---|
| PISO — o braço comparado também respeita os mínimos obrigatórios (Σ w·(max−min) sobre os critérios que separam) | 11.5 | ALCANÇÁVEL |
| LIVRE — o braço comparado não precisa passar (Σ w·max) | 70.0 | ALCANÇÁVEL |

**Elementos exigidos em `expected_output.required_elements`**

| elemento | braço completo | braço comparado |
|---|---|---|
| Outcome, input, output e boundaries | sim | sim |
| ROBOT prompt | sim | não |
| Plataforma e ferramentas | sim | não |
| Memória/contexto | sim | não |
| 3 a 5 testes | sim | não |
| Humano no loop | sim | sim |
| Critérios de medição | sim | sim |

4 de 7 elementos exigidos são exclusivos do braço completo.


---

## Régua v0.1.1


### TEST-0007 — ABLATION (`status: READY`)

Braço completo: `TEST-0007:A` (14 arquivos) · comparado: `TEST-0007:B` (12 arquivos)

| critério | peso | mínimo | obrigatório |
|---|---|---|---|
| EXECUTION_QUALITY | 0.4 | 85 | sim |
| CONSISTENCY | 0.2 | 80 | sim |
| HUMAN_CHECKPOINT_COMPLIANCE | 0.2 | 90 | sim |
| METHODOLOGY_FIDELITY | 0.2 | 85 | sim |

**Teto aritmético**

| item | valor |
|---|---|
| soma dos pesos | 1.0 |
| piso ponderado de um braço que passa (Σ w·min) | 85.0 |
| máximo da escala | 100 |
| folga acima do piso | 15.0 |
| margem máxima se AMBOS os braços passam | 15.0 |
| margem exigida (`required_margin_over_baseline`) | 5 |

**Teto evidencial — quanto peso da régua consegue separar os braços**

| critério | peso | veredito | exclusivo do braço completo | presente nos DOIS braços |
|---|---|---|---|---|
| EXECUTION_QUALITY | 0.4 | EMPATA | — | procedimento de execução completo, etapa de testes, etapa de medição |
| CONSISTENCY | 0.2 | EMPATA | — | ordem lógica das etapas, gates |
| HUMAN_CHECKPOINT_COMPLIANCE | 0.2 | EMPATA | — | checkpoint de revisão humana, período inicial |
| METHODOLOGY_FIDELITY | 0.2 | SEPARA | corpo de regra de decisão (condicao->consequencia), condição de plataforma nomeada | anti-padrões |

- peso que **separa**: **0.2** · peso que **empata**: **0.8**
- **margem máxima disponível pelos critérios que separam: 20.0 pontos**

**Margem disponível, por regime do braço comparado**

| regime | margem máx. | vs exigida = 5 |
|---|---|---|
| PISO — o braço comparado também respeita os mínimos obrigatórios (Σ w·(max−min) sobre os critérios que separam) | 3.0 | **INATINGÍVEL** |
| LIVRE — o braço comparado não precisa passar (Σ w·max) | 20.0 | ALCANÇÁVEL |

> **A margem de 5 só existe se o braço comparado REPROVAR na régua.** Não basta ele ser pior: ele tem de cair abaixo dos mínimos obrigatórios. Um braço comparado meramente inferior, mas aprovado, não consegue produzir a margem exigida.


> **Confundidor de desenho:** o braço comparado mantém, no `SKILL.md`, ponteiro para arquivo que a ablação removeu — `PILOT-001-agent-input-v0.1.1/agent-input/runtime-bundle/knowledge/decision-rules.yaml`. O agente pode responder "as regras estão em `knowledge/decision-rules.yaml`" e ser penalizado por artefato de empacotamento, não por falta de conhecimento.


**Elementos exigidos em `expected_output.required_elements`**

| elemento | braço completo | braço comparado |
|---|---|---|
| Outcome, input, output e boundaries | sim | sim |
| ROBOT prompt | sim | sim |
| Plataforma e ferramentas | sim | sim |
| Memória/contexto | sim | sim |
| 3 a 5 testes | sim | sim |
| Humano no loop | sim | sim |
| Critérios de medição | sim | sim |

0 de 7 elementos exigidos são exclusivos do braço completo.


### TEST-0008 — SUMMARY_VS_SKILL (`status: READY`)

Braço completo: `TEST-0008:B` (14 arquivos) · comparado: `TEST-0008:A` (3 arquivos)

| critério | peso | mínimo | obrigatório |
|---|---|---|---|
| EXECUTION_QUALITY | 0.3 | 85 | sim |
| CONSISTENCY | 0.2 | 80 | sim |
| HUMAN_CHECKPOINT_COMPLIANCE | 0.2 | 90 | sim |
| METHODOLOGY_FIDELITY | 0.2 | 85 | sim |

**Teto aritmético**

| item | valor |
|---|---|
| soma dos pesos | 0.9 |
| piso ponderado de um braço que passa (Σ w·min) | 76.5 |
| máximo da escala | 100 |
| folga acima do piso | 23.5 |
| margem máxima se AMBOS os braços passam | 23.5 |
| margem exigida (`required_margin_over_baseline`) | 5 |

**Teto evidencial — quanto peso da régua consegue separar os braços**

| critério | peso | veredito | exclusivo do braço completo | presente nos DOIS braços |
|---|---|---|---|---|
| EXECUTION_QUALITY | 0.3 | SEPARA | procedimento de execução completo, etapa de testes, etapa de medição | — |
| CONSISTENCY | 0.2 | SEPARA | ordem lógica das etapas, gates | — |
| HUMAN_CHECKPOINT_COMPLIANCE | 0.2 | EMPATA | — | checkpoint de revisão humana, período inicial |
| METHODOLOGY_FIDELITY | 0.2 | SEPARA | corpo de regra de decisão (condicao->consequencia), condição de plataforma nomeada, anti-padrões | — |

- peso que **separa**: **0.7** · peso que **empata**: **0.2**
- **margem máxima disponível pelos critérios que separam: 70.0 pontos**

**Margem disponível, por regime do braço comparado**

| regime | margem máx. | vs exigida = 5 |
|---|---|---|
| PISO — o braço comparado também respeita os mínimos obrigatórios (Σ w·(max−min) sobre os critérios que separam) | 11.5 | ALCANÇÁVEL |
| LIVRE — o braço comparado não precisa passar (Σ w·max) | 70.0 | ALCANÇÁVEL |

**Elementos exigidos em `expected_output.required_elements`**

| elemento | braço completo | braço comparado |
|---|---|---|
| Outcome, input, output e boundaries | sim | sim |
| ROBOT prompt | sim | não |
| Plataforma e ferramentas | sim | não |
| Memória/contexto | sim | não |
| 3 a 5 testes | sim | não |
| Humano no loop | sim | sim |
| Critérios de medição | sim | sim |

4 de 7 elementos exigidos são exclusivos do braço completo.


---

## Comparação entre versões — a folga encolheu

| teste | versão | peso que separa | margem máx. disponível | margem exigida | elementos exclusivos | alcançável? |
|---|---|---|---|---|---|---|
| TEST-0007 | 0.1.1 | 0.2 | 20.0 | 5 | 0/7 | sim |
| TEST-0007 | 0.1.2 | 0.2 | 20.0 | 5 | 0/7 | sim |
| TEST-0008 | 0.1.1 | 0.7 | 70.0 | 5 | 4/7 | sim |
| TEST-0008 | 0.1.2 | 0.7 | 70.0 | 5 | 4/7 | sim |

**Regime PISO — a conta que decide**

| teste | versão | critérios que separam | margem máx. (piso) | exigida | alcançável? |
|---|---|---|---|---|---|
| TEST-0007 | 0.1.1 | METHODOLOGY_FIDELITY | 3.0 | 5 | **não** |
| TEST-0007 | 0.1.2 | METHODOLOGY_FIDELITY | 3.0 | 5 | **não** |
| TEST-0008 | 0.1.1 | EXECUTION_QUALITY, CONSISTENCY, METHODOLOGY_FIDELITY | 11.5 | 5 | sim |
| TEST-0008 | 0.1.2 | EXECUTION_QUALITY, CONSISTENCY, METHODOLOGY_FIDELITY | 11.5 | 5 | sim |

**A folga não encolheu entre as versões — ela já era insuficiente na v0.1.1 e continua idêntica na v0.1.2.** O que mudou foi a substância: o `SKILL.md` do braço ablado passou de 3885 para 8269 bytes, absorvendo os GATES 0–3 com o procedimento de 9 passos inline. Em ambas as versões, **7 de 7 `required_elements` estão nos dois braços** — a ablação não retira nada do que a régua exige.


---

**Escopo:** medição apenas. A v0.1.2 não foi tocada, nenhuma v0.1.3 foi proposta, nenhum arquivo de projeto foi criado, alterado ou apagado.
