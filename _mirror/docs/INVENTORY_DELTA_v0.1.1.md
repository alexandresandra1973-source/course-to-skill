# INVENTORY_DELTA_v0.1.1 — DELTA PASS da Fase 1

**Escopo:** abertura dos ZIPs deixados de fora do `PROJECT_INVENTORY.md`, recontagem da seção D contra a skill `-corrected` e auditoria de integridade do teste cego.
**Data:** 2026-08-10
**Modo:** READ-ONLY absoluto sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/`. Todos os ZIPs foram descompactados em `/tmp/delta/`. Nada foi escrito no Drive fora de `Course-to-Skill-Claude/docs/`.
**Regra de relato:** número medido. Onde a medida depende de um mapeamento heurístico meu, isso está dito na linha.

---

## 0. PORTÃO DO DELTA — quais ZIPs existem

| ZIP pedido no brief | Existe? |
|---|---|
| `01_TOOL/releases/v0.1.1/course-to-skill-compiler-v0.1.1-pilot-ready.zip` | **SIM** — 190.320 B |
| `02_PILOTS/PILOT-001/01_GENERATED-SKILL/PILOT-001-generated-skill-v0.1.1-corrected.zip` | **NÃO EXISTE nesse caminho.** O que há em `01_GENERATED-SKILL/` é `PILOT-001-agent-input-v0.1.1.zip` (23.203 B). O ZIP `-generated-skill-v0.1.1-corrected.zip` existe, mas em **`Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/`** (28.653 B). Abri os dois. |
| `02_PILOTS/PILOT-001/02_VALIDATION/PILOT-001-final-blind-test-kit.zip` | **SIM** — 38.349 B |
| `02_PILOTS/PILOT-001/03_FINAL-BLIND-TEST/AGENT/PILOT-001-agent-input-v0.1.1.zip` | **SIM** — 23.203 B |
| `02_PILOTS/PILOT-001/03_FINAL-BLIND-TEST/JUDGE/PILOT-001-judge-private-v0.1.1.zip` | **SIM** — 15.580 B |
| `02_VALIDATION/PREFLIGHT_REPORT.md` | **SIM** — 2.844 B, lido |

### 0.1 Achado que muda o enquadramento do delta

Comparação por MD5, arquivo a arquivo, entre o conteúdo dos 6 ZIPs e as árvores já descompactadas no Drive:

| ZIP | arquivos | já presentes no Drive (MD5) | **NOVOS** |
|---|---|---|---|
| release v0.1.1 | 71 | 71 | **0** |
| agent-input (01_) | 14 | 14 | **0** |
| final-blind-test-kit | 24 | 24 | **0** |
| agent-input (03_AGENT) | 14 | 14 | **0** |
| judge-private (03_JUDGE) | 11 | 11 | **0** |
| generated-skill-corrected | 14 | 14 | **0** |

Comparação também **por caminho relativo**, ZIP contra a pasta descompactada correspondente: `só_no_ZIP = 0`, `só_no_disco = 0`, `conteúdo_difere = 0` em todos os cinco pares.

**Consequência:** os ZIPs são espelhos byte-idênticos de árvores que já estavam descompactadas no Drive e que já foram inventariadas na Fase 1. **Nenhuma contagem, nenhum arquivo e nenhuma conclusão da Fase 1 muda por causa da abertura dos binários.** A lacuna de escopo era de forma (proveniência do empacotamento), não de conteúdo.

---

## 1. DELTA vs INVENTÁRIO

### 1.1 Tabela das 5 inconsistências reportadas na Fase 1

| # | Inconsistência da Fase 1 | Veredicto | Evidência no arquivo |
|---|---|---|---|
| 1 | `confidence.score` é constante disfarçada de medida | **NÃO MEXEU** | `Z6/generated-skill/knowledge/decision-rules.yaml`: scores `{0.94, 0.96}` em 8 ADRs, `level` HIGH 8/8. `knowledge/workflows.yaml`: `WF-0001` = 0.97/HIGH. `knowledge/principles.yaml`: os 6 princípios **não têm campo `confidence`**. `analysis/evidence.jsonl`: 44 registros, score distinto = `{0.97}`. Nenhum código lê o campo. |
| 2 | Proveniência termina em ID; pacote entregue não contém a evidência | **NÃO MEXEU** | `Z6/generated-skill/` tem exatamente 14 arquivos e **`evidence.jsonl` não está entre eles**. `provenance/evidence-map.jsonl` (16 linhas) mantém os 5 campos só-de-ID: `entity_id`, `entity_type`, `source_evidence_ids`, `origin_class`, `promotion_level`. Sem texto, sem timestamp, sem citação. |
| 3 | O validador obrigatório falha no pacote que o projeto manda entregar | **NÃO MEXEU** | `Z1_release/.../scripts/validate_generated_skill.py` é byte-idêntico ao do disco (MD5 já catalogado). Linha 38 continua exigindo `tests/test-candidates.yaml`; o `runtime-bundle` continua sem `tests/`. Rodado: `ERROR MISSING_FILE: tests/test-candidates.yaml`. |
| 4 | De L2 em diante nenhum estágio vê a fonte | **NÃO MEXEU** | Os 5 prompts dentro do ZIP do release são byte-idênticos aos do disco (e **todos diferem** dos 5 do workspace `Course-to-Skill/`). `prompts/skill-compiler.md` e `prompts/evaluator.md`: 0 ocorrências de `transcript`/`vídeo`/`fonte original`/`evidence.jsonl`. |
| 5a | `SKILL.md` §15 só reconhece AUTO/REVIEW/APPROVAL | **NÃO MEXEU** | `Z1_release/.../SKILL.md`: 0 ocorrências de `UNDEFINED` em 26.249 B. §15 continua com *"Toda futura Skill deve definir decisões em **três** níveis"*. Enquanto isso, 7/8 ADRs e 7/8 steps estão em `UNDEFINED`. |
| 5b | 4 schemas obsoletos com nomes canônicos no disco | **CORRIGIU NO RELEASE, PERMANECE NO WORKSPACE** | O ZIP do release contém **apenas 5 schemas, todos corretos**, com nomes canônicos: `decision.schema.yaml` (18.154 B = versão `-updated`), `evidence`, `workflow` (25.708 B = `-updated-v2`), `test` (30.702 B, com `BYPASSED_HUMAN_REVIEW`), `held-out-registry`. **Nenhum dos 4 obsoletos está no pacote.** Eles só existem em `Course-to-Skill/course-to-skill-compiler/`, que não é o release. |

**Placar: 4 NÃO MEXEU · 1 dividido (corrigido no release, permanece no workspace) · 0 corrigido integralmente.**

### 1.2 Recontagem da seção D contra a skill `-corrected` (`Z6`)

| Pergunta do brief | Fase 1 | Delta (medido em `Z6/generated-skill/`) | Mudou? |
|---|---|---|---|
| `confidence` ainda é constante? | evidências `{0.97}`; ADRs `{0.94, 0.96}` | **Idem.** ADRs `{0.94, 0.96}`, level HIGH 8/8; `WF-0001` 0.97/HIGH; **os 6 princípios sequer têm o campo `confidence`** (detalhe novo). | **NÃO** |
| `source_excerpt` continua vazio? | 0 de 44 | **0 de 44.** E `evidence.jsonl` continua fora do pacote entregue. | **NÃO** |
| SOURCE_EXPLICIT vs MODEL_INFERENCE | 44/44 e 8/8 SOURCE_EXPLICIT; 10/10 perguntas MODEL_INFERENCE | `decision_rules` 8 → **8 SOURCE_EXPLICIT**; `principles` 6 → **6 SOURCE_EXPLICIT**; `tools` 3 → **3 SOURCE_EXPLICIT**; `workflows` 1 → **SOURCE_EXPLICIT**; `evidence-map` 16 entradas → **16 SOURCE_EXPLICIT**; `questions` 10 → **10 MODEL_INFERENCE**. **Novo:** `anti_patterns` (7) e `quality_criteria` (6) **não têm campo `origin_class`** — 13 entidades da skill sem classificação epistêmica nenhuma. | **NÃO** (e piora com o achado novo) |
| `UNDEFINED` ainda em 87,5% do autonomy? | 7/8 ADRs, 7/8 steps | **7/8 ADRs (87,5%) e 7/8 steps (87,5%).** Idêntico. | **NÃO** |

### 1.3 Conclusões da Fase 1 que ficam OBSOLETAS

Três, e apenas três. As demais permanecem válidas.

1. **OBSOLETA — `PROJECT_INVENTORY.md` D.8, frase final:** *"O isolamento runtime↔judge está efetivamente implementado e o lock reproduz."*
   O que a Fase 1 mediu foi **isolamento de arquivos**, e isso continua verdadeiro (nenhum arquivo de teste, nenhuma rubrica, nenhum gabarito no `runtime-bundle`; hashes conferem). Mas a frase induz a conclusão errada. O isolamento **epistêmico** é nulo: a resposta esperada de 9 dos 10 casos está literalmente dentro do pacote entregue ao candidato (§2 abaixo). A redação correta é *"o isolamento de arquivos está implementado; o isolamento de conteúdo não existe."*

2. **OBSOLETA — `PROJECT_INVENTORY.md` seção A, premissa de cobertura:** o inventário registrou 8 ZIPs como "não abertos — só nome, tamanho, data", deixando em aberto se continham material não catalogado.
   Medido agora: **contêm zero conteúdo novo**. A ressalva pode ser removida; a cobertura de conteúdo da Fase 1 era de 100%.

3. **PARCIALMENTE OBSOLETA — `PROJECT_INVENTORY.md` F.9:** *"Quatro schemas obsoletos continuam no disco, sem marcação"*.
   Continua factualmente correto sobre o **workspace**, mas a Fase 1 não distinguiu workspace de release. Medido agora: o **pacote distribuível v0.1.1 está limpo** — 5 schemas, todos corretos, nomes canônicos. O risco é de quem trabalha na pasta de desenvolvimento, não de quem consome o release. A gravidade cai de "o release reprova o próprio piloto" para "o workspace reprova o próprio piloto".

**Permanecem válidas sem alteração:** F.1, F.2, F.3, F.4, F.5, F.6, F.7, F.8, F.10, F.11, F.12 e as 8 menores de F.13.

---

## 2. INTEGRIDADE DO TESTE CEGO

### 2.0 Inventário comparado AGENT × JUDGE

| Pacote | arquivos | conteúdo |
|---|---|---|
| **AGENT** (`PILOT-001-agent-input-v0.1.1.zip`) | **12** no runtime + `README-FIRST.md` + `RUNNER_PROMPT.md` = 14 | `SKILL.md`, `manifest.yaml`, `knowledge/{decision-rules, workflows, principles, anti-patterns, questions, quality-criteria, tools, glossary, examples}.yaml/jsonl`, `provenance/evidence-map.jsonl` |
| **JUDGE** (`PILOT-001-judge-private-v0.1.1.zip`) | **11** | `FINAL_TEST_PROTOCOL.md`, `PREFLIGHT_REPORT.md`, `README-FIRST.md`, `VERIFY_KIT.py`, `judge-private/{FINAL_TEST_LOCK.yaml, JUDGE_INSTRUCTIONS.md, baseline-summary.md, case-prompts-public-view.yaml, held-out-registry.yaml, test-suite.yaml, validation-decision-template.yaml}` |
| **Interseção de arquivos** | **0** | Nenhum arquivo do JUDGE aparece no AGENT. Separação de arquivos: **correta**. |

**Ressalva de empacotamento:** o terceiro ZIP, `PILOT-001-final-blind-test-kit.zip` (24 arquivos), **contém os dois pacotes juntos** — `agent-input/` e `judge-private/` no mesmo arquivo. A separação em dois ZIPs distintos só existe em `03_FINAL-BLIND-TEST/`. Quem receber o kit de `02_VALIDATION/` recebe gabarito e candidato no mesmo download; o protocolo depende de disciplina humana, não do empacotamento.

---

### 2 (a) O pacote do AGENT contém a resposta que ele deveria descobrir?

**SIM. De forma direta, literal e em 9 dos 10 casos.**

#### Prova 1 — o bloco `isolation` é ficção verificável

Cada um dos 10 testes declara `isolation.answer_hidden: true`, `rationale_hidden: true`, `source_hidden: true`, `contamination_risk: LOW` e lista `hidden_items`. Busquei cada item declarado como oculto dentro do texto dos 12 arquivos entregues ao candidato:

| Teste | `hidden_items` declarados | Presentes no pacote do AGENTE |
|---|---|---|
| TEST-0001 | `ADR-0001, EV-0004, EV-0005` | **os 3** |
| TEST-0002 | `ADR-0004` | **1 de 1** |
| TEST-0003 | `ADR-0003` | **1 de 1** |
| TEST-0004 | `ADR-0005` | **1 de 1** |
| TEST-0005 | `ADR-0007` | **1 de 1** |
| TEST-0006 | `WF-0001` | **1 de 1** |
| TEST-0007 | `WF-0001` | **1 de 1** |
| TEST-0008 | `WF-0001` | **1 de 1** |
| TEST-0009 | `ADR-0003` | **1 de 1** |
| TEST-0010 | `ADR-0001, EV-0004, EV-0005` | **os 3** |

**10 de 10 testes declaram ocultar itens que estão inteiramente dentro do pacote do candidato.** O `runtime-bundle` entrega os 8 ADRs (`ADR-0001` … `ADR-0008`) e o único workflow (`WF-0001`) com todos os campos: `conditions`, `selected`, `action`, `validation_criteria`, `do_not`, `exceptions`, `ask_user_if_missing`. O `contamination_risk: LOW` é falso por construção; o risco é total.

#### Prova 2 — a decisão do professor está no pacote, condição por condição

`Z4/agent-input/runtime-bundle/knowledge/decision-rules.yaml`, `ADR-0003`, entregue ao candidato:

```yaml
conditions:
  - "Já usa HubSpot Professional ou Enterprise."                    => "Começar por HubSpot/Breeze."
  - "Quer construir sem código e o trabalho é pesado em pesquisa..." => "Preferir Claude."
  - "É um pensador visual."                                         => "Considerar Gumloop."
  - "Já usa Zapier."                                                => "Considerar Zapier Agents."
  - "Nenhuma ferramenta comum conecta ao software necessário."      => "Considerar OpenClaw como último recurso..."
```

Confronto com os dois testes que dependem dele:

- **TEST-0003 (COUNTERFACTUAL).** Input: `hubspot_pro_or_enterprise: false, no_code: true, work_type: research_and_content`. Resposta esperada: *"No caso-base, preferir Claude; no cenário perturbado com HubSpot Professional, preferir HubSpot/Breeze."* → **as duas metades são a 2ª e a 1ª linha da tabela acima**, entregues ao candidato.
- **TEST-0009 (BLIND_EVALUATION, "blind new platform case").** Input: `already_uses_zapier: true, work_type: light_operations`. Resposta esperada: *"Favorecer Zapier Agents."* → **é a 4ª linha da tabela**, entregue ao candidato.

Idem para os demais: `ADR-0007` entrega *"Economiza pelo menos 2 horas/semana E o output é melhor que o manual → Expandir"* / *"Qualquer um dos dois falha → reconstruir"*, e TEST-0005 dá `hours_saved: 4, output_better_than_manual: false` esperando *"Não expandir; reconstruir"*. `ADR-0005` entrega *"primeiros 30 dias → revisar cada output"*, e TEST-0004 dá `days_in_production: 3` esperando *"Manter revisão humana"*.

#### Prova 3 — as perguntas esperadas são strings idênticas às entregues

A suíte inteira tem exatamente 2 `expected_questions`. As duas têm **correspondência exata, caractere a caractere**, com entradas de `knowledge/questions.yaml` no pacote do candidato:

| Teste | `expected_questions` (JUDGE) | Está em `knowledge/questions.yaml` (AGENT)? |
|---|---|---|
| TEST-0001 | `"Qual resultado ou função você quer que o agente assuma?"` | **SIM — match exato** |
| TEST-0002 | `"O que esse agente nunca poderá fazer?"` | **SIM — match exato** |

#### O que efetivamente **não** vazou

Não há gabarito literal: `expected_output.reference_answer` é `null` nos dois testes que têm `expected_output`; `test-suite.yaml`, rubricas, `critical_failures` e `pass_criteria` **não estão** no pacote do AGENT; o `VERIFY_KIT.py` confirma ausência de marcadores (`expected_behavior:`, `TEST-000`, `judge-private`, `baseline-summary`) — reproduzi, **0 ocorrências**.

**Veredicto (a): o vazamento não é de arquivo, é de conteúdo.** O candidato não recebe a folha de respostas; recebe a tabela de decisão da qual a folha de respostas foi extraída. Nove dos dez casos se resolvem por consulta condicional dentro do próprio pacote. O único caso que não se resolve assim é **TEST-0010** (pedido de classificação NCM), e mesmo ele tem a resposta na seção `## DO NOT USE WHEN` + no código `METHOD_NOT_DEFINED` do `SKILL.md` entregue.

---

### 2 (b) A rubrica do JUDGE foi derivada da FONTE ou da SKILL COMPILADA?

**Da SKILL COMPILADA. A evidência é literal e unânime.**

**Evidência 1 — a instrução ao avaliador, nos 10 testes.** Contagem: `evaluator_instructions` tem **um único valor distinto nos 10 registros**:

> `"Avaliar somente contra a metodologia extraída do PILOT-001."`

Não "contra a aula", não "contra a transcrição": **contra a metodologia extraída**. O padrão de referência é o produto sob teste.

**Evidência 2 — a suíte nunca menciona a fonte.** Grep no `test-suite.yaml` inteiro (37.150 B):

| termo | ocorrências |
|---|---|
| `transcript` / `transcrição` | **0** |
| `frame` | **0** |
| `timestamp` | **0** |
| `00:` (qualquer timestamp) | **0** |
| `video` / `vídeo` | **0** |
| `YkdAx2XjWDs` (id do vídeo) | **0** |
| `source_excerpt` | **0** |

**Evidência 3 — o campo `source_scope` aponta para artefatos compilados, não para a fonte.** Distribuição nos 10 testes: `DECISION` 6, `WORKFLOW` 3, `EVIDENCE` 1 — total 10 âncoras, **todas IDs internos** (`ADR-*`, `WF-*`, `EV-*`). Zero âncoras em arquivo de fonte. O enum do `test.schema.yaml` nem sequer é o problema: o campo foi preenchido apontando para o output.

**Evidência 4 — os critérios de rubrica são propriedades do artefato, não da aula.** `EXECUTION_QUALITY` = *"Executa o workflow completo"* (o workflow é `WF-0001`, gerado); `CONSISTENCY` = *"Mantém a ordem lógica e os gates"* (gates de `WF-0001`); `METHODOLOGY_FIDELITY` = *"Não inventa etapas metodológicas"* / *"Usa apenas as condições ensinadas"* — onde "as condições ensinadas" operacionalmente significa as condições de `ADR-0003`. `expected_output.structural_requirements`: *"A sequência deve respeitar a lógica de **WF-0001**."*

**Veredicto (b): avaliação circular.** O que a nota mede é *"a skill reproduz a skill"*. Um erro de extração cometido em L1/L2 é invisível para essa rubrica: se a extração inventou uma condição, o candidato que a repetir ganha nota máxima em `METHODOLOGY_FIDELITY`. É exatamente o modo de falha que o `skeptic-critic` pegou à mão na 1ª passada (SC-001, SC-002, SC-003) e que a validação comportamental, por construção, não pode pegar.

**Contraponto justo, medido:** o `baseline-summary.md` **não** é circular. Verifiquei fato a fato contra a transcrição — `30 days`, `2 hours a week`, `HubSpot Professional or Enterprise`, `Breeze`, `Gum Loop`, `Zapier agents`, `OpenClaw`, `last resort`, `taste` — **todos presentes na fonte** (alguns com grafia diferente: "Gum Loop" com espaço, "2 hours" e não "two hours", "last **8:59** resort" partido por marca de tempo). E o baseline **omite o framework ROBOT**, que está na transcrição em `9:52` e é central na skill. Um resumo derivado da skill dificilmente omitiria ROBOT. Portanto: **o baseline é fiel à fonte; a rubrica não é.** O resultado prático é pior do que se ambos fossem circulares — o braço "resumo" é julgado por uma régua construída a partir do braço "skill", e é penalizado em `EXECUTION_QUALITY` (peso 0,3, mínimo 85) por não produzir um "ROBOT prompt" que ele nunca poderia conhecer. `required_margin_over_baseline: 5` sobre um comparativo assim não mede vantagem metodológica.

---

### 2 (c) O caso do teste cego aparece em `evidence.jsonl` / `decisions.yaml` / `workflows.yaml`?

**SIM. Verificado por ID, por conteúdo e por timestamp. Não é held-out — é recall com outro nome.**

O caso rotulado `BLIND_EVALUATION` é **TEST-0009 — "Blind case — plataforma em ecossistema Zapier"**.

**Por ID:** `source_scope: [{type: DECISION, id: ADR-0003}]`, `linked_decision_ids: [ADR-0003]`, `linked_evidence_ids: [EV-0024, EV-0025, EV-0026, EV-0027, EV-0028]`. O próprio registro do teste declara as evidências de origem.

**Por conteúdo e por timestamp** — as 5 evidências citadas, lidas em `analysis/evidence.jsonl` com a marca temporal da fonte:

| ID | Timestamp na fonte | Observação registrada |
|---|---|---|
| EV-0024 | `00:07:19–00:07:42` | *"Se a empresa já usa HubSpot Professional ou Enterprise, o professor recomenda começar pelo ecossistema HubSpot/Breeze."* |
| EV-0025 | `00:07:42–00:07:56` | *"Para construção sem código com trabalho pesado de pesquisa ou conteúdo, o professor diz que escolheria Claude."* |
| EV-0026 | `00:07:56–00:08:10` | *"Para uma pessoa que pensa visualmente, o professor sugere Gumloop..."* |
| **EV-0027** | **`00:08:05–00:08:20`** | ***"Para quem já usa Zapier, o professor sugere Zapier Agents para decisões dentro dos Zaps existentes e operações leves."*** |
| EV-0028 | `00:08:20–00:08:59` | *"O professor trata OpenClaw como opção de último recurso..."* |

O input de TEST-0009 é `already_uses_zapier: true` + `work_type: light_operations`; a resposta esperada é *"Favorecer Zapier Agents"*. **É a transcrição literal de EV-0027, minuto 8:05–8:20 da aula** — inclusive o par "Zapier existente + operações leves", que aparece na evidência com essas mesmas duas palavras-chave.

Confirmação na fonte primária: a transcrição, em `**8:10**`, traz *"If you're already on Zapier, Zapier agents lets an AI take over decisions inside your…"*.

Cadeia completa medida: **transcrição 8:05–8:20 → EV-0027 → ADR-0003 (condição 4) → `knowledge/decision-rules.yaml` entregue ao candidato → TEST-0009 pergunta exatamente isso.**

**O registro do projeto já admite isso, e o rótulo do teste contradiz o registro.** `held-out-registry.yaml`: `registry_status: NOT_AVAILABLE`, `created_before_modeling: false`, `locked: false`, **`cases: []`**, com a razão escrita: *"Não é permitido rotular casos retroativamente como held-out."* Ou seja: **zero casos held-out existem**, e mesmo assim um teste carrega `test_type: BLIND_EVALUATION` e o `PREFLIGHT_REPORT.md` §5 o descreve como *"1 blind new platform case"*.

**Extensão para os outros 9:** apliquei o mesmo teste. `TEST-0001/0002/0003/0004/0005` ancoram em ADRs presentes no pacote; `TEST-0006/0007/0008` ancoram em `WF-0001`, presente no pacote. **O único caso genuinamente fora da metodologia extraída é TEST-0010** (*"Qual NCM devo usar para um escapamento de motocicleta?"*), com `source_scope: []` e `linked_*: []` — e ele testa recusa, não generalização.

**Anomalia adicional:** TEST-0010, apesar de `source_scope: []`, declara `isolation.hidden_items: ["ADR-0001","EV-0004","EV-0005"]` — **string idêntica à de TEST-0001**. É cópia-e-cola: o bloco de isolamento de um teste de reprodução foi carregado para um teste fora de escopo, onde não faz sentido nenhum.

**Veredicto (c): 9 de 10 casos são reprodução do material que o candidato recebe; 1 é teste de recusa; 0 são held-out.** O rótulo `BLIND_EVALUATION` em TEST-0009 é factualmente incorreto.

---

### 2 (d) O AGENT recebe o run sem baseline? Existe controle?

**Existem 2 controles bem especificados, e eles cobrem apenas 2 dos 10 testes.**

| Teste | Tipo | Bloco `baseline` | `required_margin_over_baseline` |
|---|---|---|---|
| TEST-0001 | DECISION_REPRODUCTION | **ausente** | — |
| TEST-0002 | MISSING_INPUT | **ausente** | — |
| TEST-0003 | COUNTERFACTUAL | **ausente** | — |
| TEST-0004 | ANTI_PATTERN | **ausente** | — |
| TEST-0005 | DECISION_REPRODUCTION | **ausente** | — |
| TEST-0006 | EXECUTION | **ausente** | — |
| **TEST-0007** | ABLATION | **presente** — `type: ALTERNATIVE_SKILL`, *"Ablated runtime: usar o mesmo SKILL.md e contexto geral, mas ocultar `knowledge/decision-rules.yaml` e `knowledge/workflows.yaml`"*, com `same_model_required`, `same_tools_required`, `same_prompt_required` = true | **5** |
| **TEST-0008** | SUMMARY_VS_SKILL | **presente** — `type: COURSE_SUMMARY`, `configuration: judge-private/baseline-summary.md`, mesmas 3 travas de paridade | **5** |
| TEST-0009 | BLIND_EVALUATION | **ausente** | — |
| TEST-0010 | EDGE_CASE | **ausente** | — |

O AGENT, por sua vez, **não recebe baseline nenhum** — correto e esperado: o baseline é um segundo braço rodado pelo juiz, não um insumo do candidato. Os dois testes com controle também trazem `blind_evaluation: {enabled: true, anonymize_outputs: true, randomize_order: true, evaluator_blind_to_source: true, labels: [A, B]}`, e o `JUDGE_INSTRUCTIONS.md` reforça: *"For TEST-0007 and TEST-0008, use the same model/runtime settings for both arms. Blind-label outputs A/B before judging."*

**Veredicto (d):** o desenho de controle **existe e é bem-feito onde existe** — é a parte mais sólida do kit. Mas:

1. **8 de 10 testes (80%) rodam sem qualquer comparação.** Neles a nota é absoluta contra `minimum_total_score: 85`. Sem braço de controle, esses 8 medem "a resposta agradou a rubrica", e a rubrica veio do artefato (item b). Isso é "ficou bom" com escala numérica.
2. **Os 2 controles são julgados pela régua enviesada.** Ambos usam `evaluator_instructions: "Avaliar somente contra a metodologia extraída do PILOT-001."` e `expected_output.required_elements` inclui `"ROBOT prompt"` — elemento que o braço-baseline não pode produzir (o `baseline-summary.md` não menciona ROBOT; confirmado por grep). A ablação de TEST-0007 remove `decision-rules.yaml` e `workflows.yaml` mas mantém o `SKILL.md`, que já traz o procedimento ROBOT de 9 passos e os limiares (3–5 testes, 2 h/semana) — a ablação é parcial e o braço "ablated" carrega grande parte da metodologia.
3. **Nenhum controle roda sem contaminação de conteúdo** (item a). Como o braço "skill" tem a tabela de decisão no pacote, a margem de 5 pontos mede sobretudo *quanto conteúdo cada braço recebeu*, não *quanto de metodologia cada braço internalizou*.

---

### 2.5 Achado adicional do delta: a regra que o v0.1.1 foi criado para resolver continua violada

`docs/PILOT-001-lessons-learned.md` cita como primeiro risco sistêmico: *"test cases can contradict their own required-input policy"*. O hardening §C **Test input closure** codificou a regra:

> `expected_behavior.should_ask_user = false` → todos os inputs REQUIRED para a decisão esperada devem estar presentes em `input_case.inputs` ou `known_context`.

Apliquei a regra à suíte travada, mapeando cada `ask_user_if_missing[].input_name` dos ADRs ligados contra os inputs de cada caso *(mapeamento nome→chave feito por mim; está listado abaixo para auditoria)*:

| Teste | Decisões ligadas | Fecha? |
|---|---|---|
| TEST-0003 | ADR-0003 | **SIM** |
| TEST-0005 | ADR-0007 | **SIM** |
| TEST-0009 | ADR-0003 | **SIM** |
| TEST-0010 | — | **SIM** (vazio) |
| TEST-0004 | ADR-0005 | **NÃO** — falta `Consistência dos outputs`. *Defensável*: `days_in_production: 3` < 30 aciona a 1ª condição de ADR-0005, tornando a consistência irrelevante. |
| TEST-0008 | ADR-0004/0005/0006/0007 | **NÃO** — faltam `Consistência dos outputs`, `Resultados de 3 a 5 testes`, `Horas economizadas por semana`, `Comparação de qualidade` |
| **TEST-0006** | ADR-0004/0005/0006/0007 | **NÃO** — faltam 5 inputs, incluindo `Resultados de 3 a 5 testes` cuja ação declarada é **`STOP`** |
| **TEST-0007** | ADR-0004/0005/0006/0007 | **NÃO** — idem TEST-0006 |

O caso mais nítido, sem margem de leitura: **`ADR-0006`, entregue ao candidato, declara `ask_user_if_missing: [("Resultados de 3 a 5 testes", action: STOP)]`.** TEST-0006 e TEST-0007 não fornecem esse input e, ao mesmo tempo, exigem `should_ask_user: false` e `should_stop: false`. **A suíte pune o candidato que obedecer à regra que a própria skill lhe entregou.** TEST-0007 está com `status: READY` e travado por SHA-256.

E o `validate_generated_skill.py` **não implementa nenhum check de input closure** — li as 138 linhas: os 7 checks são schema, versão de teste, tool refs, referência decision/workflow, provenance, maturity/production, held-out state. A regra §C existe só como texto de prompt.

---

## 3. O QUE O PREFLIGHT_REPORT.md AFIRMA E O QUE É VERIFICÁVEL

`PREFLIGHT_REPORT.md` (2.844 B, presente em 5 cópias byte-idênticas). Testei cada afirmação.

### 3.1 §1 "Static integrity" — 11 afirmações

| # | Afirmação | Verificável? | Resultado da minha verificação |
|---|---|---|---|
| 1 | "Corrected generated Skill: PASS" | **NÃO** — não define o que "PASS" significa; não há critério nem teste correspondente | **NÃO VERIFICÁVEL** (afirmação sem predicado) |
| 2 | "Schema validation — decision records: PASS" | SIM | **CONFIRMA.** 8 ADRs × `decision.schema.yaml` do release → **0 erros** |
| 3 | "Schema validation — workflow records: PASS" | SIM | **CONFIRMA.** 1 WF × `workflow.schema.yaml` → **0 erros** |
| 4 | "Schema validation — 6 compiled test candidates: PASS" | SIM | **CONFIRMA.** 6 testes × `test.schema.yaml` → **0 erros** |
| 5 | "Schema validation — 10-test final suite: PASS" | SIM | **CONFIRMA.** 10 testes × `test.schema.yaml` → **0 erros** |
| 6 | "Held-out registry schema: PASS" | SIM | **CONFIRMA.** 1 registry × `held-out-registry.schema.yaml` → **0 erros**. *Ressalva: valida a forma de um registry que declara `cases: []`.* |
| 7 | "Canonical tool references: PASS" | SIM | **CONFIRMA** — check implementado (linhas 76–80), executado, sem `UNKNOWN_TOOL_IDS` |
| 8 | "Decision/workflow reference closure: PASS" | SIM | **CONFIRMA** — check implementado (83–90), executado |
| 9 | "Provenance evidence closure: PASS" | SIM, mas **mede outra coisa** | **CONFIRMA o check, NÃO a proveniência.** Compara `union(EV usados)` ⊆ `union(EV no evidence-map)` — os dois escritos pelo mesmo compilador. `evidence.jsonl` não é lido nem está no pacote. *Conferi por fora: os 32 EV citados existem de fato — mas o projeto não tem como saber.* |
| 10 | "Test/manifest version closure: PASS" | SIM | **CONFIRMA** — check implementado (69–73) |
| 11 | "REVIEW vs APPROVAL semantic closure: PASS" | SIM, mas é **NO-OP neste caso** | **VAZIO.** A única checagem (linhas 106–107) dispara `WARNING` se `BYPASSED_APPROVAL` ∈ testes **e** `APPROVAL` ∉ `SKILL.md`. Medido: `BYPASSED_APPROVAL` **não está** nos testes (`BYPASSED_HUMAN_REVIEW` está) e `APPROVAL` **está** no `SKILL.md`. Ambas as pré-condições falham → o ramo nunca executa. "PASS" aqui significa "a checagem não rodou". |

**Placar §1: 8 confirmadas · 1 não verificável (nº 1) · 1 confirmada mas medindo outra coisa (nº 9) · 1 vazia (nº 11).**

### 3.2 §2 "Runtime isolation: PASS"

**Verificável e verdadeiro no nível de arquivo.** Reproduzi os checks do `VERIFY_KIT.py`: o `runtime-bundle` tem 12 arquivos, nenhum com `test`/`judge`/`audit` no nome, e **0 ocorrências** dos marcadores `expected_behavior:`, `reference_answer:`, `critical_failures:`, `TEST-000`, `judge-private`, `baseline-summary`.

**Mas a afirmação é enganosa como está escrita.** O texto diz: *"No test suite, expected behavior, reference answer, critical-failure definition, baseline summary, audit file or judge-private material is present in the candidate runtime."* Isso é literalmente verdade e **epistemicamente falso**: o *expected behavior* de 9 dos 10 casos está no runtime, não como arquivo de teste, mas como as condições de `ADR-0001…0008` e de `WF-0001` das quais aquele expected behavior foi derivado (§2a). O checador procura por *nomes e marcadores*; a resposta vaza por *semântica*.

### 3.3 §3 "Frozen artifacts" — hashes

**Verificável e verdadeiro. 6 de 6 conferem**, recalculados nesta auditoria:

| Artefato | SHA-256 declarado | Confere |
|---|---|---|
| `judge-private/test-suite.yaml` | `9dc5313c…eb1927` | **SIM** |
| `judge-private/baseline-summary.md` | `6e34a788…1bc2b` | **SIM** |
| `judge-private/case-prompts-public-view.yaml` | `f13b7cd9…034ed6` | **SIM** |
| `agent-input/runtime-bundle/manifest.yaml` | `d5349b1f…2cd13b` | **SIM** |
| `agent-input/RUNNER_PROMPT.md` | `54364665…f68531` | **SIM** |
| `runtime-bundle` (hash de árvore) | `4d66c81d…b2aecc` | **SIM** |

É a parte mais sólida do kit: o congelamento é real, reprodutível e auditável por terceiros.

### 3.4 §4 "Held-out limitation"

**Verificável e honesto.** *"No legitimate held-out registry was locked before methodology modeling… The registry is therefore recorded as `NOT_AVAILABLE`, not retroactively fabricated."* Confere com `held-out-registry.yaml` (`cases: []`) e com `audit-decision.yaml` (`held_out_integrity: NOT_VERIFIABLE`).

**Porém §5 do mesmo relatório contradiz §4 na prática:** a lista da suíte travada inclui *"1 blind new platform case"* — que é TEST-0009, integralmente derivado de EV-0027 (§2c). O relatório declara corretamente que não há held-out e, quatro parágrafos depois, descreve um caso como se fosse cego.

### 3.5 O que o PREFLIGHT afirma e **não é verificável no material**

| Afirmação | Por quê não é verificável |
|---|---|
| "Corrected generated Skill: PASS" (§1.1) | Sem critério declarado. Não corresponde a nenhum check do validador. |
| "Preflight status: READY_FOR_FINAL_BLIND_TEST" | O predicado "blind" não é verificável — e o material contradiz (§2a, §2c). Verificável é apenas "READY_FOR_FINAL_TEST". |
| "Behavioral status: PENDING_BLIND_EXECUTION" | Verificável e **verdadeiro**: `validation-decision-template.yaml` tem todas as 9 métricas em `null`; não existe arquivo de resultados nas duas pastas. |
| §5 *"These hashes can be used to confirm that the final test was run without changing the locked suite"* | Verificável quanto ao congelamento (§3.3). **Não** verificável quanto ao "was run": nenhum run existe. |
| §1 como um todo, executado sobre o pacote que §2 manda entregar | **Contradição, não afirmação falsa.** Rodei `validate_generated_skill.py` contra `runtime-bundle` → `ERROR MISSING_FILE: tests/test-candidates.yaml`. Os 11 PASS só se obtêm apontando o validador para `validation-input/generated-skill/`, que contém `tests/` e `audit.yaml` — exatamente o pacote que §2 proíbe entregar. |

---

## 4. RESUMO DO DELTA

| Frente | Estado após o delta |
|---|---|
| ZIPs | 5 dos 6 no caminho indicado (1 divergência de caminho registrada). **0 conteúdo novo.** Nenhuma contagem da Fase 1 muda. |
| 5 inconsistências da Fase 1 | 4 NÃO MEXEU · 1 dividida (corrigida no release, permanece no workspace) · 0 corrigidas integralmente |
| Recontagem seção D | `confidence` ainda constante · `source_excerpt` ainda 0/44 · origin_class ainda monolítico (e 13 entidades sem o campo) · `UNDEFINED` ainda 87,5% |
| Isolamento de arquivo | **REAL** — 0 arquivos de teste no runtime, 6 hashes conferem |
| Isolamento de conteúdo | **INEXISTENTE** — 10/10 testes declaram ocultar itens que estão no pacote do candidato |
| Held-out | **0 casos.** O único rótulo `BLIND_EVALUATION` é EV-0027 (fonte 8:05–8:20) |
| Rubrica | **Circular** — `"Avaliar somente contra a metodologia extraída do PILOT-001."` em 10/10 |
| Baseline | Fiel à fonte, mas presente em **2 de 10** testes e julgado por régua derivada do artefato |
| Regra §C do próprio hardening | **Violada por 4 testes**, 1 deles sem margem de leitura, e sem nenhum check em código |
| PREFLIGHT §1 | 8 confirmadas · 1 sem predicado · 1 mede outra coisa · 1 vazia |

---

**FIM DO DELTA PASS.** Nenhuma correção aplicada, nenhum código escrito, Fase 2 não iniciada. Nenhum arquivo original criado, alterado, movido ou apagado. Todos os ZIPs foram descompactados em `/tmp/delta/`.
