# JUDGE_PACKAGE_VERIFICATION — v0.1.2 · pasta real: `07_REPORTS/final-judge`

**Gerado:** `2026-08-10T18:01:55.824077+00:00` · Relatório produzido por script (`judge_package_verify.py`); nenhum número foi digitado.  
**Caminho completo:** `/mnt/g/Meu Drive/Chat GPT/Course-to-Skill/PILOT-001/v0.1.2/07_REPORTS/final-judge`  
**Escopo:** leitura apenas. Nada foi movido, renomeado ou escrito dentro de `Course-to-Skill/`.


## 1. SHA-256 — publicado como adendo separado

Os hashes estão em **`BASELINE_MANIFEST_ADDENDUM-v0.1.2-judge.txt`**. O `BASELINE_MANIFEST_20260810.txt` **não foi editado** — ele é a referência congelada da auditoria e estes artefatos são posteriores a ela.

| arquivo | bytes | mtime | sha256 |
|---|---|---|---|
| JUDGE_REPORT-v0.1.2.md | 5606 | 2026-08-10T14:46:56 | d15d6bd3063ccf9520f1cfd2… |
| validation-decision-v0.1.2.yaml | 3463 | 2026-08-10T14:47:12 | 9e325493aeb76e3d16b5d28d… |
| blind-test-results-v0.1.2.yaml | 2077 | 2026-08-10T14:47:28 | 36e2ece71468367988f05581… |
| REVISION-PLAN-v0.1.3.yaml | 3420 | 2026-08-10T14:47:48 | cb56850141b8a09d05489993… |
| PILOT-001-v0.1.2-JUDGE-RESULTS.zip | 7290 | 2026-08-10T14:49:26 | 824945e067c5bec82021b0fe… |

**Conteúdo do zip**

| membro | bytes | sha256 | vs arquivo solto |
|---|---|---|---|
| validation-decision-v0.1.2.yaml | 3463 | 9e325493aeb76e3d16b5d28d… | idêntico ao solto |
| JUDGE_REPORT-v0.1.2.md | 5606 | d15d6bd3063ccf9520f1cfd2… | idêntico ao solto |
| blind-test-results-v0.1.2.yaml | 2077 | 36e2ece71468367988f05581… | idêntico ao solto |
| REVISION-PLAN-v0.1.3.yaml | 3420 | cb56850141b8a09d05489993… | idêntico ao solto |

O zip é um espelho dos quatro arquivos soltos — não traz nada além deles.


## 2. COMPUTADO OU JULGADO

> **Não há decomposição por critério em nenhum arquivo do pacote. Os totais por caso e por braço são afirmados pelo juiz, não medidos a partir de escores por critério.**

| nome de critério da régua travada | ocorrências no pacote inteiro |
|---|---|
| EXECUTION_QUALITY | 0 |
| CONSISTENCY | 0 |
| HUMAN_CHECKPOINT_COMPLIANCE | 0 |
| METHODOLOGY_FIDELITY | 1 |

As duas únicas ocorrências são menções em prosa (`METHODOLOGY_FIDELITY` numa nota explicativa e `CONSISTENCY` em texto corrido). **Nenhum par critério→nota existe.** Logo, os valores 98,6 · 97,4 · 99,3 · 86,7 não podem ser recompostos a partir dos pesos 0,4 / 0,2 / 0,2 / 0,2 — a soma ponderada é irreconstruível.


**O que É recomputável a partir dos totais publicados:**

| métrica | afirmado | recomputado | veredito | como |
|---|---|---|---|---|
| total_score (média descritiva dos 10 casos) | 84.6 | 84.6 | ✅ confere | média aritmética dos escores dos 10 casos de aceitação |
| acceptance_pass_count | 7 | 7 | ✅ confere | contagem de result == PASS |
| acceptance_fail_count | 3 | 3 | ✅ confere | contagem de result != PASS |
| automatic_critical_failure_count | 3 | 3 | ✅ confere | soma de automatic_failures nos casos |
| missing_input_pass_rate | 0.0 | 0.0 | ✅ confere | TEST-0002 é o único caso MISSING_INPUT |
| counterfactual_pass_rate | 1.0 | 1.0 | ✅ confere | TEST-0003 é o único caso COUNTERFACTUAL |

**Coerência entre os dois arquivos de resultado, caso a caso**

| caso | validation-decision | blind-test-results | veredito |
|---|---|---|---|
| TEST-0001 | 42.0 | 42.0 | confere |
| TEST-0002 | 8.0 | 8.0 | confere |
| TEST-0003 | 100.0 | 100.0 | confere |
| TEST-0004 | 100.0 | 100.0 | confere |
| TEST-0005 | 100.0 | 100.0 | confere |
| TEST-0006 | 98.0 | 98.0 | confere |
| TEST-0007 | 98.6 | 98.6 | confere |
| TEST-0008 | 99.3 | 99.3 | confere |
| TEST-0009 | 100.0 | 100.0 | confere |
| TEST-0010 | 100.0 | 100.0 | confere |

10/10 casos batem entre os dois arquivos.


**O que NÃO é recomputável:**

| métrica | afirmado | por quê |
|---|---|---|
| decision_accuracy | 0.9 | não há decomposição publicada nem definição de quais casos entram no denominador; 7/10 PASS = 0.70 e 3/4 casos decisórios = 0.75, nenhum dos dois dá o valor afirmado |
| methodology_fidelity | 0.955 | declarado como média dos escores do critério METHODOLOGY_FIDELITY 'where that criterion exists' — esses escores por critério não estão em nenhum arquivo do pacote |

O valor **84,6** é o único da lista da tarefa que se confirma por conta própria: é a média aritmética dos 10 escores de caso. Os outros quatro (98,6 · 97,4 · 99,3 · 86,7) são totais de rubrica **julgados**.


## 3. TEST-0007 contra o teto de 3,0

| item | valor |
|---|---|
| escore do braço completo (A = FULL) | 98.6 |
| escore do braço ablado (B = ABLATION) | 97.4 |
| margem observada | 1.2 |
| margem exigida | 5.0 |
| piso ponderado da régua (Σ w·min) | 85.0 |
| o braço ablado passou nos mínimos? | **SIM** — 97,4 ≥ 85,0 |
| regime da rodada | **PISO** |
| teto evidencial no regime PISO (RUBRIC_CEILING_ANALYSIS) | 3.0 |
| teto aritmético no PISO, se TODOS os critérios pudessem diferir | 15.0 |

**A margem observada de 1.2 cabe sob o teto de 3.0** — confere. E a margem exigida de 5.0 **NÃO era alcançável** neste regime.

O braço ablado tirou 97,4, muito acima do piso de 85,0 — ou seja, **passou em todos os mínimos obrigatórios**. Sob esse regime, o `RUBRIC_CEILING_ANALYSIS` já havia calculado, antes da rodada, que a margem máxima disponível era **3,0** pontos, porque só `METHODOLOGY_FIDELITY` (peso 0,2) consegue separar os braços. **O `FAIL_MARGIN` registrado é um resultado do instrumento, não da Skill:** exigir +5 de um teste cujo teto é 3,0 reprova por construção, qualquer que fosse o desempenho.


**Sobre o `+11` atribuído à v0.1.1:** o pacote contém **0 menções** à v0.1.1, e o `validation-decision-template.yaml` da v0.1.1 segue em `PENDING_BLIND_EXECUTION` com `margin: None`. **Não existe, em nenhum arquivo, uma margem de ablação registrada para a v0.1.1** — aquela rodada nunca foi executada. Se um `+11` foi atribuído a ela em algum lugar, não é neste material; e sob o regime de piso ele seria impossível, pois excede o teto de 3.0 e até o teto aritmético de 15.0 só seria atingível com todos os quatro critérios separando ao mesmo tempo.


## 4. REVISION-PLAN-v0.1.3 — a correção está lá, textualmente

**Sim.** `FAIL-013-003`, severidade `HIGH`, `blocking: True`, camada `compiler/runtime architecture`. Verbatim:

> **root_cause_hypothesis:** SKILL.md duplicates enough executable methodology that removing decision-rules.yaml and workflows.yaml does not materially degrade behavior.

> **recommended_general_fix:** Reduce executable duplication in SKILL.md and make it explicitly route to structured decision/workflow artifacts for gates, sequencing and exceptions. Preserve general fallback behavior, but ensure the structured artifacts carry meaningful operational detail.

E no `JUDGE_REPORT-v0.1.2.md`, §6, item 3, verbatim:

> **Structured-artifact leverage:** move meaningful executable gate/sequence detail into `decision-rules.yaml` and `workflows.yaml` so the full runtime materially outperforms the ablated runtime without weakening the normal candidate.

**Leitura:** o diagnóstico da causa está correto e coincide com o que a análise de teto mediu — o `SKILL.md` duplica metodologia executável suficiente para que a ablação não degrade o comportamento. A correção prescrita, porém, não age sobre o instrumento: ela manda **reduzir a capacidade autônoma do `SKILL.md`** e transferir detalhe para os artefatos estruturados, de modo que o braço ablado piore e a margem apareça. Isso é ajustar o produto à régua.

Os dois textos trazem a ressalva `preserve general fallback behavior` / `without weakening the normal candidate`. As duas metas estão em tensão direta: o braço ablado só pode cair se o `SKILL.md` que sobrevive à ablação for menos capaz. Satisfazer as duas exige que o roteamento para os arquivos estruturados seja perfeito — o runtime completo não perde nada e o ablado perde muito. **Essa condição não está demonstrada em lugar nenhum do plano.**


## 5. Contradição entre os dois `validation-decision` do mesmo pacote

**Contradizem.** Os dois estão registrados abaixo; nenhum é escolhido.

| campo | decisão emitida | template do pacote do juiz |
|---|---|---|
| arquivo | `07_REPORTS/final-judge/validation-decision-v0.1.2.yaml` | `judge-private/validation-decision-template.yaml` (dentro de `PILOT-001-judge-private-v0.1.2.zip`) |
| status | `REQUIRES_REVISION` | `PENDING_REGRESSION_BLIND_EXECUTION` |
| total_score | 84.6 | None |
| summary_vs_skill.margin | 12.6 | None |
| regression_cases | {"REG-012-001": "PASS", "REG-012-002": "PASS", "REG-012-003": "PASS"} | {"REG-012-001": null, "REG-012-002": null, "REG-012-003": null} |
| production_ready | False | False |

O template não foi atualizado após a rodada. Os dois arquivos convivem no material da v0.1.2 descrevendo estados incompatíveis do mesmo candidato: um diz que a rodada terminou e reprovou; o outro, que ela ainda não começou. Quem abrir só o pacote do juiz lê o segundo.


---

**Escopo:** conferência apenas. Nenhum arquivo foi movido, renomeado ou criado dentro de `Course-to-Skill/`; o `BASELINE_MANIFEST_20260810.txt` não foi editado.
