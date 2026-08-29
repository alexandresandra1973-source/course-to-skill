# PROJECT_INVENTORY — Course-to-Skill / Course-to-Skill-Compiler

**Fase:** 1 — DISCOVERY (auditoria técnica independente)
**Data da varredura:** 2026-08-10
**Modo:** READ-ONLY sobre as duas pastas auditadas. Nenhum arquivo criado, alterado, movido ou apagado dentro delas.
**Único artefato criado:** esta árvore `Course-to-Skill-Claude/docs/`.
**Escopo desta fase:** descrever o que existe e medir. Nenhuma correção é proposta aqui.

Convenção de relato: todo número abaixo foi **medido** (find / md5sum / sha256sum / parser YAML-JSON / `jsonschema` 4.10.3). Onde não foi possível medir, está escrito **NÃO MEDIDO**.

---

## PORTÃO G0

| Verificação | Resultado |
|---|---|
| `/mnt/g` montado | **MOUNTED** (`mountpoint -q` retornou verdadeiro) |
| `Course-to-Skill/` existe | **SIM** |
| `Course-to-Skill-Compiler/` existe | **SIM** |
| `Course-to-Skill/` — arquivos / diretórios / tamanho | **89 arquivos**, 28 diretórios, **1,7 MB** |
| `Course-to-Skill-Compiler/` — arquivos / diretórios / tamanho | **140 arquivos**, 55 diretórios, **1,2 MB** |

**G0: PASSOU.** Prosseguido com a auditoria.

Composição por tipo (as duas pastas somadas, 229 arquivos):
- 218 arquivos de texto (md / yaml / yml / jsonl / txt / py)
- 8 arquivos `.zip` (não abertos — só nome, tamanho, data)
- 3 arquivos `.png` (não abertos — só nome, tamanho, data)

---

## A) ESTRUTURA

### A.1 O que é cada pasta

- **`Course-to-Skill/`** — workspace de desenvolvimento. Contém o compilador em forma solta (`course-to-skill-compiler/`), o piloto com **as fontes originais** (transcrição + 3 frames + metadados) e todo o rastro de iteração da análise (`analysis/`, com sufixos `-revised`, `-v2`, `-v3`).
- **`Course-to-Skill-Compiler/`** — empacotamento/release. Contém o release `v0.1.1-pilot-ready` (`01_TOOL/`) e os kits de handoff do piloto (`02_PILOTS/`). **Não contém as fontes originais** — nem transcrição, nem frames, nem `evidence.jsonl`.

### A.2 Árvore de diretórios (real)

```
Course-to-Skill/                                             89 arq | 1,7M
├── course-to-skill-compiler/                                        311K
│   ├── SKILL.md                              22.886  2026-08-09 21:10
│   ├── decision.schema.yaml                  18.754  2026-08-09 21:52   [VERSÃO ANTIGA]
│   ├── evidence.schema.yaml                  11.550  2026-08-09 21:51   [= release]
│   ├── test.schema.yaml                      30.632  2026-08-09 21:53   [VERSÃO ANTIGA]
│   ├── workflow.schema.yaml                  27.288  2026-08-09 21:52   [VERSÃO ANTIGA]
│   ├── prompts/            (5 arquivos)      109.282 2026-08-09 21:53–22:09  [VERSÃO ANTIGA]
│   ├── schemas/
│   │   ├── decision-schema-updated.yaml      18.154  2026-08-09 23:54   [= release decision.schema.yaml]
│   │   ├── workflow-schema-updated.yaml      25.525  2026-08-09 23:57   [ÓRFÃO — v1 intermediária]
│   │   └── workflow-schema-updated-v2.yaml   25.708  2026-08-09 23:58   [= release workflow.schema.yaml]
│   └── templates/
│       ├── generated-skill-template.zip       8.462  2026-08-09 22:14
│       ├── generated-skill-template/generated-skill/  (14 arq)  2026-08-10 01:13
│       └── generated-skill/                  <DIRETÓRIO VAZIO>          [ÓRFÃO]
└── pilots/PILOT-001-HubSpot-AI-Agent/                               1,4M
    ├── sources/
    │   ├── transcript/transcript-original-en.txt   20.712  23:05
    │   ├── metadata/source-metadata.yaml              537  23:09
    │   └── frames/  frame-12m34s.png  193.374  23:16
    │                frame-13m02s.png  239.595  23:18
    │                frame-13m27s.png  474.504  23:19
    ├── analysis/   (26 arquivos, 23:12 → 00:09)
    │   ├── evidence.jsonl                    72.414  23:22
    │   ├── decisions.yaml / decisions-revised.yaml
    │   ├── workflows.yaml / -revised / -revised-v2 / -revised-v3
    │   ├── principles.yaml / -revised
    │   ├── questions.yaml / -revised
    │   ├── tools.yaml / -revised / -revised-v2
    │   ├── test-candidates.yaml / -revised
    │   ├── skeptic-review.yaml / -v2 / -v3
    │   ├── anti-patterns.yaml, quality-criteria.yaml,
    │   │   quality-criteria (1).yaml                              [DUPLICATA EXATA]
    │   ├── temporal-map.yaml, revision-plan.yaml
    │   └── visual-observations.yaml, visual-review-required.yaml
    ├── PILOT-001-generated-skill.zip          26.924  00:11
    ├── PILOT-001-generated-skill/             (14 arq)  [v0.1.0 — SUPERSEDED]
    ├── PILOT-001-generated-skill-v0.1.1-corrected.zip  28.653  00:22
    └── PILOT-001-generated-skill-v0.1.1-corrected/  (14 arq)  [ATUAL]

Course-to-Skill-Compiler/                                   140 arq | 1,2M
├── 01_TOOL/releases/v0.1.1/                                        782K
│   ├── course-to-skill-compiler-v0.1.1-pilot-ready.zip  190.320  00:48
│   └── course-to-skill-compiler-v0.1.1-pilot-ready/
│       └── course-to-skill-compiler-v0.1.1-pilot-ready/     [ANINHAMENTO DUPLO]
│           ├── SKILL.md              26.249   03:30
│           ├── README.md / CHANGELOG.md
│           ├── docs/PILOT-001-lessons-learned.md
│           ├── prompts/   (5 arq, 116.499 bytes, 03:30)   [VERSÃO CORRENTE]
│           ├── schemas/   (5 arq: decision, evidence, workflow, test,
│           │               held-out-registry)              [VERSÃO CORRENTE]
│           ├── scripts/validate_generated_skill.py   6.533   03:30
│           └── pilot/PILOT-001/
│               ├── runtime-bundle/        (12 arq)
│               ├── validation-input/      (16 arq)
│               └── final-test/            (agent-input + judge-private)
└── 02_PILOTS/PILOT-001/                                            430K
    ├── 01_GENERATED-SKILL/PILOT-001-agent-input-v0.1.1[.zip]
    ├── 02_VALIDATION/PILOT-001-final-blind-test-kit[.zip]  + PREFLIGHT_REPORT.md
    └── 03_FINAL-BLIND-TEST/
        ├── AGENT/PILOT-001-agent-input-v0.1.1[.zip]        [cópia de 01_]
        └── JUDGE/PILOT-001-judge-private-v0.1.1[.zip]
```

### A.3 Duplicação — medida por MD5

218 arquivos de texto → **94 conteúdos distintos**. **57% dos arquivos de texto são cópias byte-idênticas de outro arquivo.**

| Recorte | Conteúdos únicos |
|---|---|
| Presentes nas **duas** pastas | 17 |
| Só em `Course-to-Skill/` | 49 |
| Só em `Course-to-Skill-Compiler/` | 28 |

Arquivos mais replicados (nº de cópias byte-idênticas):

| Cópias | Arquivo |
|---|---|
| 10× | `knowledge/quality-criteria.yaml` |
| 9× | `anti-patterns.yaml`, `questions(-revised).yaml`, `principles(-revised).yaml`, `tools(-revised-v2).yaml` |
| 8× | `decision-rules.yaml`, `glossary.yaml`, **`examples.jsonl` (todas as 8 cópias com 0 bytes)** |
| 7× | `SKILL.md` (da skill gerada), `manifest.yaml`, `workflows.yaml`, `evidence-map.jsonl` |
| 5× | `PREFLIGHT_REPORT.md` |
| 4× | `test-suite.yaml`, `held-out-registry.yaml`, `baseline-summary.md`, `RUNNER_PROMPT.md`, `skeptic-review-v3.yaml` |

Causa estrutural: o `runtime-bundle` da skill do PILOT-001 (12 arquivos) foi replicado em 6 locais diferentes entre release, kit de validação e kit de blind test, e mais uma vez em `Course-to-Skill/pilots/`. Não há link simbólico nem referência — são cópias físicas.

### A.4 Versões antigas identificadas (por MD5, não por nome)

| Arquivo | Situação medida |
|---|---|
| `Course-to-Skill/course-to-skill-compiler/decision.schema.yaml` | **ANTIGO.** MD5 `e53a24ff…`; o release usa o conteúdo de `schemas/decision-schema-updated.yaml` (`14e36fa0…`). Diferença semântica única: enum `autonomy.level` **sem** `UNDEFINED`. |
| `Course-to-Skill/course-to-skill-compiler/workflow.schema.yaml` | **ANTIGO.** MD5 `34bc9484…`; release usa `workflow-schema-updated-v2.yaml` (`1de7ae3c…`). Diferenças: `step.autonomy` sem `UNDEFINED`; `loop.max_iterations` só `integer` (release aceita `null`). |
| `Course-to-Skill/course-to-skill-compiler/test.schema.yaml` | **ANTIGO.** Falta o enum `BYPASSED_HUMAN_REVIEW` em 2 pontos (linhas 136 e 321 do dump normalizado). |
| `Course-to-Skill/course-to-skill-compiler/schemas/workflow-schema-updated.yaml` | **ÓRFÃO.** Versão intermediária, superada pela `-v2`. Não está em lugar nenhum do release. |
| `Course-to-Skill/course-to-skill-compiler/prompts/*.md` (5 arquivos) | **ANTIGOS.** Todos diferem em conteúdo dos 5 prompts do release (ex.: `evaluator.md` 20.161 bytes vs 21.860 no release). Os prompts do release trazem o "v0.1.1 HARDENING ADDENDUM". |
| `Course-to-Skill/pilots/…/PILOT-001-generated-skill/` | **SUPERSEDED** por `-v0.1.1-corrected/`. Diferem em 5 arquivos: `SKILL.md` e `manifest.yaml` (0.1.0→0.1.1 + campos `scope`), `provenance/evidence-map.jsonl` (**EV-0034 ausente na versão antiga**), `knowledge/workflows.yaml`, `tests/test-candidates.yaml`. |
| `analysis/quality-criteria (1).yaml` | **DUPLICATA EXATA** de `quality-criteria.yaml` (mesmo MD5, mesmo mtime 23:48). Artefato de download repetido. |
| `templates/generated-skill/` | **DIRETÓRIO VAZIO** (0 arquivos). |
| `01_TOOL/…/course-to-skill-compiler-v0.1.1-pilot-ready/course-to-skill-compiler-v0.1.1-pilot-ready/` | **ANINHAMENTO DUPLO** do mesmo nome — resultado de descompactar o zip dentro de pasta homônima. Idem em `02_PILOTS` (4 ocorrências). |

---

## B) SCHEMAS

Schemas lidos na íntegra: `evidence.schema.yaml`, `decision.schema.yaml` (antigo e release), `workflow.schema.yaml` (antigo, v1 e v2/release), `test.schema.yaml` (antigo e release), `held-out-registry.schema.yaml`.

### B.1 Campos obrigatórios vs opcionais

**`evidence.schema.yaml`** (`additionalProperties: false`)

Obrigatórios (13): `schema_version`, `evidence_id`, `course`, `lesson`, `category`, `observation`, `origin_class`, `source_refs` (minItems 1), `modalities` (minItems 1), `confidence`, `evidence_strength`, `status`.

Opcionais (16): `secondary_categories`, `context`, **`source_excerpt`**, `demonstrated_behavior`, `reason_given`, `inference`, `visual_dependency`, `visual_dependency_note`, `contradiction`, `related_evidence_ids`, `derived_from_evidence_ids`, `candidate_links`, `tags`, `superseded_by`, `reviewer_note`, `created_at`/`updated_at`.

Obrigatoriedade condicional (`allOf`), presente e correta:
- `origin_class = MODEL_INFERENCE` → exige `inference` e `derived_from_evidence_ids` com minItems 1;
- `visual_dependency = true` → exige `visual_dependency_note` não-vazio;
- `status = SUPERSEDED` → exige `superseded_by`.

**Ponto material:** `source_excerpt` — o único campo que carregaria o **texto literal da fonte** — é **opcional** e pode ser `null`. O schema exige um *ponteiro* (`source_refs`), nunca a *citação*.

**`decision.schema.yaml`** (release)

Obrigatórios (15): `schema_version`, `decision_id`, `name`, `problem`, `context`, `inputs_observed` (minItems 1), `alternatives` (minItems 1), `selected`, `decision_variables` (minItems 1), `rationale`, `source_evidence` (minItems 1, padrão `^EV-[0-9]{4,}$`), `origin_class`, `confidence`, `status`, `autonomy`.

Opcionais e com `default` (23), entre eles os que carregam a executabilidade: **`conditions` (default `[]`)**, **`action` (pode ser `null`)**, `exceptions`, `ask_user_if_missing`, `do_not`, `validation_criteria`, `precedence`, `required_inputs`, `trigger`, `output_expectation`, `promotion_level`, `test_candidates`.

**Ponto material:** `conditions` e `action` — o par condição→ação — **não são obrigatórios**. Um ADR válido pode existir sem nenhuma condição e sem nenhuma ação.

**`workflow.schema.yaml`** (release) e **`test.schema.yaml`**: estruturalmente análogos. `test.schema.yaml` do release acrescenta o código `BYPASSED_HUMAN_REVIEW` em 2 enums.

### B.2 O estado UNDEFINED é representável no schema?

**Parcialmente — e só num campo.** Diff semântico dos schemas (carregados e comparados chave a chave):

| Local | `UNDEFINED` representável? |
|---|---|
| `decision.schema.yaml` (release) → `$defs/autonomy/properties/level/enum` | **SIM** — `[AUTO, REVIEW, APPROVAL, UNDEFINED]` |
| `workflow.schema.yaml` (release) → `$defs/step/properties/autonomy/enum` | **SIM** — `[AUTO, REVIEW, APPROVAL, UNDEFINED]` |
| `evidence.schema.yaml` — `origin_class`, `status`, `confidence.level`, `evidence_strength` | **NÃO.** Zero ocorrências de `UNDEFINED` no arquivo inteiro. |
| `test.schema.yaml` | **NÃO.** Zero ocorrências. |
| `held-out-registry.schema.yaml` | **NÃO.** Zero ocorrências. |
| `decision.schema.yaml` / `workflow.schema.yaml` **antigos** (ainda no disco) | **NÃO** — enum de 3 valores. |

Contagem literal de `UNDEFINED` por arquivo:

```
0  evidence.schema.yaml          0  test.schema.yaml (ambas versões)
0  workflow.schema.yaml (antigo) 0  held-out-registry.schema.yaml
0  decision.schema.yaml (antigo) 0  workflow-schema-updated.yaml (v1 órfã)
3  decision-schema-updated.yaml (= release)   ← 1 no enum + 2 em `description`
2  workflow-schema-updated-v2.yaml (= release) ← 1 no enum + 1 em `description`
```

Fora de `autonomy`, **`UNDEFINED` existe apenas como texto de prompt**, não como valor de schema. Ocorrências nos prompts do release:

```
methodology-modeler.md : 6  (linhas 1038, 1053, 1180 `MARK_UNDEFINED`, 1353 "16 — UNDEFINED REGIONS", 1578, 1697 "UNDEFINED RATE")
skeptic-critic.md      : 2  (516, 822 `MARK_UNDEFINED`)
evaluator.md           : 1  (942 — "existem regiões `UNDEFINED`")
skill-compiler.md      : 1  (1259 — exemplo `pricing = UNDEFINED`)
lesson-analyzer.md     : 0
SKILL.md (ferramenta)  : 0
```

Consequência medida: `methodology-modeler.md` manda calcular uma "UNDEFINED RATE" e marcar "UNDEFINED REGIONS", mas **não existe campo de schema onde essa marcação possa ser gravada** fora de `autonomy.level` / `step.autonomy`. Não há `undefined_regions.yaml`, não há `coverage.yaml` com schema. No `manifest.yaml` da skill gerada existe `scope.undefined_count`, e no PILOT-001 seu valor é `null`.

### B.3 evidence_id — existe? é obrigatório? cabe valor sem evidência?

**Existe e é obrigatório na raiz das entidades principais:**

- `evidence.schema.yaml`: `evidence_id` é **obrigatório**, padrão `^EV-[0-9]{4,}$`.
- `decision.schema.yaml`: `source_evidence` é **obrigatório**, `minItems: 1`, itens no padrão `^EV-[0-9]{4,}$`. **Não é possível registrar um ADR sem pelo menos um EV.**
- `workflow.schema.yaml`: `source_evidence` idem.

**Mas há caminhos legítimos para valor sem evidência, dentro do mesmo schema de decisão:**

| Sub-objeto | Campo de evidência | Obrigatório? |
|---|---|---|
| `$defs/input_observed` | `evidence_id` | **NÃO** — e aceita explicitamente `null` (`type: [string, "null"]`) |
| `$defs/rejected_option` | `evidence_id` | **NÃO** — aceita `null` |
| `$defs/decision_variable` | `evidence_id` | **NÃO** — aceita `null` |
| `$defs/condition` | `evidence_ids` | **NÃO** — `default: []` |
| `$defs/exception` | `evidence_ids` | **NÃO** — `default: []` |
| `$defs/rationale` | `evidence_ids` | **NÃO** — `default: []`; e `rationale` só exige `state` |
| `$defs/precedence` | (nenhum campo de evidência existe) | — |
| `$defs/missing_input_action` (`ask_user_if_missing`) | (nenhum campo de evidência existe) | — |
| `$defs/autonomy` | (nenhum campo de evidência existe) | — |
| `decision.validation_criteria`, `decision.do_not`, `decision.action` | (são `string`/array de `string` puros) | — |

Ou seja: a **decisão** precisa de evidência; a **condição de disparo**, a **variável decisiva**, a **exceção**, o **critério de validação**, a **ação**, a **regra de precedência** e o **nível de autonomia** podem todos ser gravados **sem nenhum `evidence_id`** e o registro continua válido contra o schema. Isso foi confirmado por validação: os 8 ADRs do PILOT-001 passam com `autonomy` sem qualquer campo de proveniência.

Um segundo ponto: o padrão `^EV-[0-9]{4,}$` valida **formato**, não **existência**. Nenhum schema pode verificar se `EV-0099` existe — isso é responsabilidade de código externo (ver seção C.4).

### B.4 confidence — numérico? em que escala? há definição do que cada número significa?

**Sim, numérico.** Definição idêntica em `evidence.schema.yaml` e `decision.schema.yaml`:

```yaml
confidence:
  type: object
  required: [score, level]           # em decision.schema.yaml: [score, level, reason]
  properties:
    score:  { type: number, minimum: 0, maximum: 1 }
    level:  { type: string, enum: [HIGH, MEDIUM, LOW] }
    reason: { type: [string, "null"] }   # em decision: string, minLength 1
```

Escala: **número real contínuo em [0, 1]**, acompanhado de um rótulo ordinal de 3 níveis.

**Definição do significado — existe apenas em faixas, e apenas no prompt, não no schema.** `prompts/lesson-analyzer.md` §40 "CONFIDENCE GUIDANCE" (linhas 1349–1387):

```
HIGH   0.85–1.00   "declaração clara; ou demonstração clara; ou múltiplas evidências consistentes"
MEDIUM 0.60–0.84   "boa evidência, porém com ambiguidade"
LOW    0.00–0.59   "evidência parcial, frágil ou dependente de inferência"
"Pontuação não substitui explicação. Sempre preencher: confidence.reason"
```

O que **não existe** em lugar nenhum:
- nenhuma definição do que distingue 0,90 de 0,97 dentro da faixa HIGH;
- nenhuma regra de calibração, nenhuma tabela de ancoragem, nenhum exemplo por valor;
- **nenhuma restrição de schema ligando `score` a `level`** — um registro com `score: 0.10` e `level: HIGH` é válido contra `evidence.schema.yaml`;
- nenhuma verificação mecânica de `score` (o `validate_generated_skill.py` não olha `confidence`).

O único acoplamento existente é indireto e está em `decision.schema.yaml`: `if promotion_level == CONFIRMED then confidence.level ∈ {HIGH, MEDIUM}`. Isso restringe o **rótulo**, nunca o **número**.

`methodology-modeler.md` §60 ("CONFIDENCE IS NOT PROMOTION", linhas 1262–1276) separa explicitamente as duas coisas: *"Confiança mede certeza da interpretação. Promotion mede autoridade para controlar a Skill."* — mas continua sem definir o que o número significa.

---

## C) PROMPTS

Prompts lidos (versão do release v0.1.1, que difere da versão em `Course-to-Skill/`): `lesson-analyzer.md` (1.888 linhas), `methodology-modeler.md` (1.973), `evaluator.md` (1.616), `skeptic-critic.md` (1.267), `skill-compiler.md` (1.643).

### C.1 O prompt manda o modelo produzir score numérico de confiança?

**Sim, em 3 dos 5 estágios — e o score é gerado pelo próprio modelo, sem nenhuma âncora externa.**

| Prompt | Manda produzir score numérico? | Onde |
|---|---|---|
| `lesson-analyzer.md` | **SIM.** Template de evidência com `confidence: score:` (linhas 490–491) e template de ADR (1771–1772). §40 fixa as faixas 0.85/0.60/0.00. | 490, 1349–1387, 1771 |
| `methodology-modeler.md` | **SIM.** `confidence:` em 5 templates de registro (389, 576, 754, 819, 1224) e `confidence: score:` em 1444–1445. | idem |
| `skill-compiler.md` | **NÃO gera** — instrui a **não alterar** `confidence` sem registro explícito (§12, linhas 282–290). | 288 |
| `skeptic-critic.md` | **NÃO gera** — apenas lê `origin_class`/`confidence`/`promotion_level` no PASS 2 (INFERENCE AUDIT). | 254–266 |
| `evaluator.md` | **SIM, mas outra coisa.** Produz score de *desempenho*, não de confiança: `total_score`, `DECISION_ACCURACY >= 0.80`, `METHODOLOGY_FIDELITY >= 0.80`, `HELD_OUT_PASS_RATE >= 0.80`, `COUNTERFACTUAL_PASS_RATE >= 0.80`, `MISSING_INPUT_PASS_RATE >= 0.90`, `minimum_total_score: 85`. | 795, 814–818, 1434–1500 |

### C.2 Cada estágio lê a FONTE original, ou só o output do estágio anterior?

Medido pelo bloco "INPUT CONTRACT" / "REQUIRED INPUT PACKAGE" de cada prompt, e por grep de referências a fonte (`transcript`, `vídeo`, `fonte original`, `evidence.jsonl`, `model/`, `methodology-report`).

| Estágio | Entrada declarada | Lê a fonte original (L0)? |
|---|---|---|
| **L1 — Lesson Analyzer** | `analysis_request` com `source_files`, `supporting_files`, `available_channels{audio, transcript, video_screen, slides, pdf, templates, exercises}` (§8, linhas 231–273). §5 SOURCE POLICY define hierarquia de fontes. | **SIM.** É o único estágio que lê L0. |
| **L2 — Methodology Modeler** | `modeling_request` com `evidence_records`, `decision_records`, `workflow_records`, `principle_candidates`, `anti_patterns`, `quality_criteria`, `questions`, `tool_usage`, `test_candidates`, `review_notes` + o booleano **`original_sources_available: true \| false`** (§4, linhas 114–144). | **NÃO.** Recebe só o output de L1. A fonte aparece como *flag booleano*, sem caminho de arquivo, sem canal e sem instrução de reler. |
| **L2b — Skeptic / Critic** | `audit_request` com `methodology_package{principles, decision_rules, workflows, anti_patterns, quality_criteria, questions, tools, conflicts, coverage, provenance_map}` + `source_access{original_sources_available, evidence_records_available, decision_records_available, workflow_records_available}` (§4, linhas 91–125). | **NÃO por padrão.** Também recebe só flags booleanos. Há uma única menção a voltar à fonte, e é condicional: linha 883, *"é necessário voltar a vídeo"* — como sinal de um achado, não como procedimento de entrada. |
| **L3 — Skill Compiler** | `compiler-input/` com os 11 YAMLs do modelo L2 (§3, linhas 62–88). | **NÃO.** Grep por `transcript`, `vídeo`, `fonte original`, `original_sources`, `evidence.jsonl`, `model/`, `methodology`: **0 ocorrências** no arquivo inteiro. |
| **L4 — Evaluator** | `validation-input/` = `generated-skill/`, `test-candidates.yaml`, `held-out-registry.yaml`, `audit-decision.yaml`, `compilation-report.md`, `source references / provenance` (§4, linhas 83–95). | **NÃO.** Grep por `transcript`, `vídeo`, `fonte original`, `methodology-report`, `decision-rules`, `model/`, `L0`, `L2`: **0 ocorrências** no arquivo inteiro. |

Conclusão medida: **apenas L1 toca a fonte.** De L2 em diante o pipeline opera exclusivamente sobre o output do estágio anterior. Não existe, em nenhum prompt, uma instrução de reabrir a transcrição ou o frame para conferir um `evidence_id`.

### C.3 O evaluator tem acesso ao modelo de metodologia (L2) ou só à fonte (L0)?

**Nenhum dos dois.** O pacote de entrada do Evaluator (§4) não lista nem os arquivos L2 (`principles.yaml`, `decision-rules.yaml`, `workflows.yaml`, `coverage.yaml`, `provenance-map.yaml` na forma do Modeler) nem qualquer arquivo L0. Ele recebe **L3 — a skill já compilada** — mais os artefatos de teste. A linha "source references / provenance" (linha 94) refere-se ao `provenance/evidence-map.jsonl` empacotado dentro da skill, que (medido, ver D.2) contém **apenas IDs**, sem texto, sem timestamp e sem citação.

Confirmação prática no artefato: o `runtime-bundle` entregue ao agente candidato contém `SKILL.md`, `manifest.yaml`, `knowledge/`, `provenance/` — e **não contém** `evidence.jsonl`, transcrição ou frames. O `JUDGE_INSTRUCTIONS.md` e o `RUNNER_PROMPT.md` também não dão acesso à fonte a nenhuma das partes.

### C.4 Onde aparece "não invente" — e há verificação mecânica correspondente?

Ocorrências de proibição de invenção (grep case-insensitive por `não invent|nao invent|não inferir|no invented|do not invent|não fabric|não atribu|não assumir`):

```
SKILL.md (ferramenta)   3
evaluator.md            3
methodology-modeler.md  4
lesson-analyzer.md      2
skeptic-critic.md       0
skill-compiler.md       0
```

Locais principais, citados:

- `SKILL.md` **§13 HALLUCINATION CONTROL** (linhas 726–746): *"É proibido: inventar uma regra e atribuí-la ao professor; completar uma metodologia usando conhecimento geral sem sinalização; transformar correlação em causalidade sem evidência; tratar exemplo isolado como princípio universal; remover exceções para simplificar; esconder contradições; inventar rationale para decisão não explicada."* Seguido de 5 estados textuais: `METHOD_NOT_DEFINED`, `RATIONALE_NOT_EXPLICIT`, `INSUFFICIENT_EVIDENCE`, `CONTRADICTION_DETECTED`, `MISSING_REQUIRED_INPUT`.
- `lesson-analyzer.md` **§7 HARD RULES** (179–228): HR-01 NO SILENT INFERENCE, HR-02 NO INVENTED RATIONALE, HR-03 NO SINGLE-EXAMPLE GENERALIZATION, HR-05 CONTRADICTIONS MUST SURVIVE, HR-06 MISSING DATA MUST SURVIVE.
- `lesson-analyzer.md` **§5.3 Regra de atribuição** (134–141): *"Nunca atribua ao professor: conhecimento geral do modelo; uma inferência não declarada; uma boa prática externa; uma conclusão apenas plausível."*
- `SKILL.md` **§29 NON-GOALS** (1214–1225): *"não afirmar que capturou conhecimento tácito não demonstrado; não atribuir conhecimento externo ao professor; não gerar regras universais a partir de um único exemplo; não tratar transcrição como representação completa de vídeo."*

**Verificação mecânica correspondente:** existe **um único** artefato executável em todo o projeto — `scripts/validate_generated_skill.py` (6.533 bytes, 138 linhas). Foi lido na íntegra e executado (a partir de `/tmp`, contra os pacotes no Drive, sem escrita).

O que ele **verifica**:

| Check | O que faz de fato |
|---|---|
| `schema-validation` | Valida `decision_rules`, `workflows` e os testes contra os schemas JSON. |
| `test-version-closure` | `test.subject.skill_version == manifest.skill.version`. |
| `canonical-tool-refs` | Todo `TOOL-*` citado em workflows existe em `tools.yaml`. |
| `core-reference-closure` | `linked_decision_ids` / `linked_workflow_ids` dos testes resolvem. |
| `provenance-closure` | `union(EV- usados em decisions/workflows/tools) ⊆ union(EV- em provenance/evidence-map.jsonl)`. |
| `maturity-production-gate` | `production_ready: true` exige `S4_VALIDATED`. |
| `held-out-registry-state` | Registry `ACTIVE` exige `created_before_modeling` e `locked`. |
| (warning) | `BYPASSED_APPROVAL` nos testes sem token `APPROVAL` no `SKILL.md`. |

O que ele **não verifica** — e é exatamente o objeto das regras "não invente":

1. **Não confere se um `EV-xxxx` existe.** O `provenance-closure` compara os IDs usados na skill contra os IDs listados no `evidence-map.jsonl` **gerado pela própria skill**. É um fechamento auto-referencial: o compilador escreve o mapa e depois é conferido contra o mapa que escreveu. O `evidence.jsonl` real (L1) **não é lido** pelo validador e nem sequer está no pacote validado.
2. **Não confere nenhuma âncora textual na fonte.** Não lê transcrição, não lê frame, não compara `observation` com `source_excerpt`, não checa timestamps.
3. **Não confere `confidence`.** Nem valor, nem coerência score↔level, nem faixa.
4. **Não confere `origin_class`.** Nada impede um `MODEL_INFERENCE` rotulado como `SOURCE_EXPLICIT`.
5. **Não confere `UNDEFINED`.** Não mede cobertura, não mede "UNDEFINED RATE", não valida `scope.undefined_count`.
6. **Não implementa nenhum dos 5 estados de §13** (`METHOD_NOT_DEFINED`, `RATIONALE_NOT_EXPLICIT`, `INSUFFICIENT_EVIDENCE`, `CONTRADICTION_DETECTED`, `MISSING_REQUIRED_INPUT`). São strings de prompt e de `SKILL.md` gerado, sem verificador.
7. **Não confere HR-03** (exemplo isolado → princípio). O campo `evidence_strength: SINGLE_EXAMPLE` existe no schema, mas nenhum código o lê.

O segundo executável do projeto, `VERIFY_KIT.py` (1.844 bytes), verifica **integridade e isolamento** — SHA-256 dos 5 arquivos travados + hash da árvore do runtime + ausência de marcadores privados. Não toca em proveniência, confiança ou invenção.

**Resumo da C.4:** a regra "não invente" aparece **12 vezes em texto de prompt** e tem **zero verificações mecânicas** que a testem. A única verificação de proveniência existente confere consistência interna de IDs, não existência nem ancoragem na fonte.

---

## D) PILOT-001-HubSpot-AI-Agent — CONTAGENS REAIS

Fonte: uma aula única — vídeo do YouTube `YkdAx2XjWDs`, canal "HubSpot Marketing", *"How to Build Your First AI Agent (Step-by-step Tutorial)"*, duração `00:15:05`, idioma inglês. Transcrição: 20.174 bytes / 3.282 palavras, com 180 marcas de tempo em formato `m:ss` (última: `14:44`).

### D.1 Quantidades por artefato

Números do estado **final** (`-revised`/`-v3`), que é o que foi compilado.

| Entidade | Nº | Arquivo medido |
|---|---|---|
| Evidências | **44** (`EV-0001` … `EV-0044`, 44 IDs únicos) | `analysis/evidence.jsonl` |
| Decisões (ADR) | **8** | `analysis/decisions-revised.yaml` |
| Workflows | **1** (`WF-0001`, com 8 steps, 2 decision points, 1 loop, 1 exception, 1 human checkpoint) | `analysis/workflows-revised-v3.yaml` |
| Princípios | **6** (+ 1 "structure" separada) | `analysis/principles-revised.yaml` |
| Anti-padrões | **7** | `analysis/anti-patterns.yaml` |
| Perguntas | **10** | `analysis/questions-revised.yaml` |
| Critérios de qualidade | **6** | `analysis/quality-criteria.yaml` |
| Ferramentas | **3** | `analysis/tools-revised-v2.yaml` |
| Observações visuais | **3** | `analysis/visual-observations.yaml` |
| Testes candidatos (na skill) | **6** | `generated-skill/tests/test-candidates.yaml` |
| Testes na suíte final (judge) | **10** | `judge-private/test-suite.yaml` |

O `manifest.yaml` da skill gerada declara: principles 6, conceptual_structures 1, decision_rules 8, workflows 1, anti_patterns 7, quality_criteria 6, questions 10, tools 3. **Confere com a medição.**

### D.2 Quantas carregam evidence_id VÁLIDO (apontando para evidência existente)

Resolução feita contra o conjunto real `{EV-0001 … EV-0044}` extraído de `evidence.jsonl`.

| Artefato | Refs `EV-` (total) | Distintas | **Quebradas** | Itens sem nenhuma ref |
|---|---|---|---|---|
| `decisions-revised.yaml` (8 ADRs) | 89 | 19 | **0** | 0 |
| `workflows-revised-v3.yaml` (1 WF) | 46 | 24 | **0** | 0 |
| `principles-revised.yaml` (6) | 19 | 18 | **0** | 0 |
| `anti-patterns.yaml` (7) | 14 | 14 | **0** | 0 |
| `questions-revised.yaml` (10) | 15 | 10 | **0** | 0 |
| `quality-criteria.yaml` (6) | 12 | 8 | **0** | 0 |
| `tools-revised-v2.yaml` (3) | 6 | 5 | **0** | 0 |
| `visual-observations.yaml` (3) | 0 | 0 | — | **3 de 3** |
| `tests/test-candidates.yaml` (6) | 24 | 18 | **0** | 0 |
| `knowledge/glossary.yaml` | 0 | 0 | — | (não aplicável) |

**Total: 0 referências `EV-` quebradas em todo o piloto.** Todas as 32 evidências distintas citadas pela skill gerada existem em `evidence.jsonl` e todas estão cobertas pelo `provenance/evidence-map.jsonl` (`union(usados) − union(mapeados) = ∅`).

Cobertura no sentido inverso: **28 das 44 evidências (63,6%) são referenciadas por algum artefato de análise**; **16 nunca são referenciadas por nada**: `EV-0001, EV-0002, EV-0003, EV-0007, EV-0008, EV-0009, EV-0010, EV-0011, EV-0012, EV-0015, EV-0016, EV-0019, EV-0020, EV-0021, EV-0022, EV-0023`. Considerando a skill compilada, **32 das 44** são citadas.

**Sobre o `evidence-map.jsonl`** (16 linhas, 3.001 bytes): campos são exatamente `entity_id`, `entity_type`, `source_evidence_ids`, `origin_class`, `promotion_level`. **Não contém `observation`, `source_excerpt`, `timestamp` nem `source_refs`.** Exemplo literal:

```json
{"entity_id": "ADR-0001", "entity_type": "DECISION_RULE", "source_evidence_ids": ["EV-0004", "EV-0005"], "origin_class": "SOURCE_EXPLICIT", "promotion_level": "CONFIRMED"}
```

O `runtime-bundle` entregue ao avaliador **não inclui `evidence.jsonl`**. Portanto, dentro do pacote entregue, `EV-0004` é um ID que não resolve para nada.

### D.3 SOURCE_EXPLICIT vs MODEL_INFERENCE vs GENERAL_KNOWLEDGE

| Artefato | SOURCE_EXPLICIT | MODEL_INFERENCE | GENERAL_KNOWLEDGE |
|---|---|---|---|
| Evidências (44) | **44 (100%)** | **0** | **0** |
| ADRs — `decisions.yaml` (8) | 8 | 0 | 0 |
| ADRs — `decisions-revised.yaml` (8) | 8 | 0 | 0 |
| ADRs na skill gerada (8) | 8 | 0 | 0 |
| Workflow `WF-0001` | SOURCE_EXPLICIT | — | — |
| Princípios (6) | 6 | 0 | 0 |
| **Perguntas (10)** | **0** | **10 (100%)** | 0 |

Campos correlatos das 44 evidências:

- `status`: **ACTIVE 44/44**. Nenhuma `DISPUTED`, `NEEDS_REVIEW`, `SUPERSEDED` ou `REJECTED`.
- `evidence_strength`: `DIRECT` 37, `SINGLE_EXAMPLE` 4, `CORROBORATED` 3. Nenhuma `INFERRED`, nenhuma `WEAK`.
- `confidence.level`: **HIGH 44/44**. Nenhuma MEDIUM, nenhuma LOW.
- `confidence.score`: **valor único 0,97 nas 44 evidências.** Não há dispersão — o conjunto de scores distintos é `{0.97}`.
- `contradiction`: `null` em 44/44.
- `inference`: `null` em 44/44.
- `category`: DECISION 8, CONCEPT 7, EXAMPLE 6, PROCEDURE 6, PRINCIPLE 4, QUALITY_CRITERION 3, ANTI_PATTERN 2, WARNING 2, CONSTRAINT 2, TOOL_USAGE 2, RATIONALE 1, EXCEPTION 1.
- `rationale.state` dos 8 ADRs: **EXPLICIT 8/8**. Nenhum `PARTIAL`, `INFERRED` ou `NOT_EXPLICIT`.
- `promotion_level` dos 8 ADRs: **CONFIRMED 8/8**.
- `confidence.score` dos 8 ADRs: `{0.94, 0.96}`.
- Preenchimento textual das 44 evidências: **`source_excerpt` preenchido em 0/44**; `reason_given` em 6/44; `demonstrated_behavior` em 3/44; `context` em 1/44.

### D.4 Quantas ficaram UNDEFINED

`UNDEFINED` só existe em um campo (ver B.2). Estado final medido:

| Local | ANTES (v1) | DEPOIS (revisado / compilado) |
|---|---|---|
| `autonomy.level` dos 8 ADRs | `AUTO` 3, `REVIEW` 4, `APPROVAL` 1 — **0 UNDEFINED** | **`UNDEFINED` 7, `REVIEW` 1** |
| `step.autonomy` dos 8 steps de `WF-0001` | `REVIEW` 6, `AUTO` 1, `APPROVAL` 1 — **0 UNDEFINED** | **`UNDEFINED` 7, `REVIEW` 1** (só `STEP-006`) |
| `loop.max_iterations` (`LOOP-001`) | `5` | **`null`** |
| Evidências com `UNDEFINED` em qualquer campo | — | **0 de 44** (não é representável) |
| `manifest.scope.undefined_count` | — | **`null`** — com a nota literal: *"Scope counts were not carried into the generated-skill package; values remain null to avoid inventing coverage."* |

Em números absolutos, o único uso de `UNDEFINED` no piloto inteiro é: **14 ocorrências** (7 ADRs + 7 steps), todas no campo `autonomy`.

### D.5 Frames e observações visuais

| Item | Medido |
|---|---|
| Frames existentes | **3** — `frame-12m34s.png` (193.374 B), `frame-13m02s.png` (239.595 B), `frame-13m27s.png` (474.504 B). Não abertos. |
| `visual_observations` em `visual-observations.yaml` | **3** — cada uma nomeia o frame (`frame`) e o timestamp. **Nenhuma carrega `evidence_id`.** O arquivo declara `screenshots_reviewed: 3`, `visual_review: COMPLETE`. |
| Evidências com `visual_dependency: true` | **3 de 44** — `EV-0041`, `EV-0042`, `EV-0043` |
| Evidências que referenciam um frame específico | **3** — cada uma tem um `source_ref` `source_type: VIDEO` com `file_name` apontando para um dos 3 PNGs e `frame_description` preenchida. Cobertura 1:1 com os frames. |
| `source_refs` por tipo (nas 44 evidências) | `TRANSCRIPT` 44, `VIDEO` 3 (total 47 refs). Todas as 44 evidências têm ao menos um ref de transcrição. |
| `visual_dependency_note` das 3 | Texto **idêntico** nas três: *"A demonstração visual confirma ou acrescenta detalhes operacionais à fala."* |

**Verificação de ancoragem temporal (feita nesta auditoria, não existe no projeto):** dos **94 timestamps** citados nos `source_refs` das 44 evidências, **93 coincidem exatamente** com uma das 180 marcas do transcript. **1 não coincide**: `EV-0001`, `timestamp.end = 00:00:29` → `0:29` não existe entre as marcas do transcript.

### D.6 O que exatamente o Skeptic reprovou

Três passadas. Contagens declaradas: v1 = 0 CRITICAL / **3 HIGH** / 3 MEDIUM; v2 = 0 CRITICAL / **1 HIGH** / 2 MEDIUM; v3 = 0/0/0 + **2 LOW**.

**`skeptic-review.yaml` — 1ª passada — `REQUIRES_REVISION`, `compilation_allowed: false`. Achados na íntegra:**

- **SC-001 — HIGH — OVER_AUTOMATION** — afeta `ADR-0002, ADR-0003, ADR-0005, ADR-0007, ADR-0008`.
  *"Alguns níveis AUTO/REVIEW/APPROVAL e exigências de aprovação foram adicionados pelo compilador, mas não são explicitamente ensinados na aula."*
  Fix exigido: *"Separar governança derivada da metodologia explícita. Marcar essas escolhas como MODEL_INFERENCE ou removê-las quando não sustentadas."*
- **SC-002 — HIGH — INVENTED_STEP** — afeta `WF-0001`, `LOOP-001`.
  *"O limite max_iterations: 5 foi inferido a partir da orientação de executar 3–5 testes. A fonte não diz que o ciclo de correção pode repetir no máximo cinco vezes."*
  Fix: *"Remover o limite inventado ou marcar a política como não definida pela metodologia."*
- **SC-003 — HIGH — FALSE_EXPLICITNESS** — afeta `questions.yaml`.
  *"As perguntas operacionais são boas derivações dos inputs obrigatórios, mas a aula não formula essas dez perguntas literalmente."*
  Fix: *"Classificar as perguntas derivadas como MODEL_INFERENCE e manter vínculo com as evidências que justificam cada pergunta."*
- **SC-004 — MEDIUM — TOOL_AS_METHOD** — afeta `tools.yaml`, `WF-0001`.
  *"Algumas verificações e fallbacks de ferramentas foram transformados em política operacional embora não tenham sido explicitamente ensinados."*
- **SC-005 — MEDIUM — CONCEPT_PROMOTED_TO_PRINCIPLE** — afeta `PR-0003`.
  *"Os cinco blocos de um agente são apresentados claramente como estrutura/conceito, mas foram promovidos a princípio operacional."*
- **SC-006 — MEDIUM — TEST_DESIGN_OVERREACH** — afeta `TEST-0004`.
  *"O teste usa o runtime code USER_APPROVAL_REQUIRED, enquanto a fonte ensina revisão humana inicial, não esse código operacional específico."*

Decisão v1: *"Há inferências operacionais úteis misturadas com conteúdo SOURCE_EXPLICIT. A Skill não deve ser compilada antes de separar essas camadas."*

**`skeptic-review-v2.yaml` — 2ª passada — `REQUIRES_REVISION`, `compilation_allowed: false`. Achados na íntegra:**

- **SC2-001 — HIGH — OVER_AUTOMATION** — afeta `WF-0001`, `HC-002`.
  *"O checkpoint HC-002 ainda está classificado como APPROVAL e diz que a política de revisão humana deve estar 'aprovada'. A aula exige revisão humana, mas não define um gate formal de aprovação."*
- **SC2-002 — MEDIUM — METHOD_RUNTIME_BLUR** — afeta `WF-0001`.
  *"Stop conditions genéricas como TOOL_UNAVAILABLE e QUALITY_GATE_FAILED são políticas do runtime do compiler, não ensinamentos explícitos da aula."*
- **SC2-003 — MEDIUM — FALSE_EXPLICITNESS** — afeta `tools.yaml`.
  *"Alguns campos estruturados de required_inputs e expected_output das ferramentas foram formulados pelo compiler, embora cada ferramenta em si seja demonstrada explicitamente."*

**`skeptic-review-v3.yaml` — 3ª passada — `APPROVED_WITH_WARNINGS`, `compilation_allowed: true`. 0 CRITICAL/HIGH/MEDIUM. 2 avisos LOW:**

- **SC3-001 — LOW — PILOT_SCOPE_LIMITATION** — *"A metodologia foi extraída de uma única aula de aproximadamente 15 minutos."*
- **SC3-002 — LOW — NO_HELD_OUT_VALIDATION_YET** — *"Os testes candidatos existem, mas a Skill ainda não passou por validação comportamental independente."*

**Verificação independente de que as correções foram de fato aplicadas** (feita nesta auditoria, comparando v1 vs v3 nos artefatos):

| Achado | Correção declarada | Aplicada nos arquivos? |
|---|---|---|
| SC-001 | autonomia não ensinada → `UNDEFINED` | **SIM.** ADRs: 3 AUTO/4 REVIEW/1 APPROVAL → 7 UNDEFINED/1 REVIEW. |
| SC-002 | remover `max_iterations: 5` | **SIM.** `LOOP-001.max_iterations`: `5` → `null`. |
| SC-003 | perguntas → MODEL_INFERENCE | **SIM.** As 10 perguntas em `questions-revised.yaml` têm `origin_class: MODEL_INFERENCE`, com `inference_basis` e `source_evidence_ids`. |
| SC-005 | PR-0003 deixar de ser princípio | **SIM.** `principles-revised.yaml` caiu de 7 para 6 princípios e ganhou bloco separado `structures: [1 item]`. |
| SC2-001 | HC-002 `APPROVAL` → `REVIEW` | **SIM.** `human_checkpoints` de `WF-0001` tem 1 item, `HC-002`, `level: REVIEW`, sem linguagem de aprovação. |
| SC2-002 | remover stop conditions do compiler | **SIM.** `stop_conditions` caiu de 4 (`MISSING_REQUIRED_INPUT`, `USER_APPROVAL_REQUIRED`, `TOOL_UNAVAILABLE`, `QUALITY_GATE_FAILED`) para 2. |

As correções do Skeptic são reais e verificáveis nos arquivos. Nenhuma foi declarada sem ter sido feita.

### D.7 Os arquivos de teste têm casos reais ou são placeholder/vazios?

**Casos reais, concretos e completos — mas nenhum foi executado.**

`generated-skill/tests/test-candidates.yaml` — **6 testes**, tipos: `DECISION_REPRODUCTION` 2, `MISSING_INPUT` 1, `COUNTERFACTUAL` 1, `ANTI_PATTERN` 1, `EXECUTION` 1. Cada teste tem 26 campos preenchidos, incluindo `input_case.user_prompt` literal, `expected_behavior` com diagnóstico/decisão/ação/perguntas esperadas, `prohibited_behavior`, `evaluation.rubric` com pesos e `minimum_score`, e `isolation.hidden_items`. Exemplo real (TEST-0001):

```yaml
input_case.user_prompt: "Quero criar um agente para automatizar meus posts. Qual ferramenta eu uso?"
expected_behavior.should_ask_user: true
expected_behavior.expected_questions: ["Qual resultado ou função você quer que o agente assuma?"]
prohibited_behavior: ["Recomendar imediatamente Claude, Zapier, HubSpot, Gumloop ou OpenClaw.", ...]
```

`judge-private/test-suite.yaml` — **10 testes** (`TEST-0001` … `TEST-0010`), acrescentando `ABLATION`, `SUMMARY_VS_SKILL`, `BLIND_EVALUATION`, `EDGE_CASE`.

**Estado de execução — medido:**

| Item | Valor |
|---|---|
| `status` dos 6 testes da skill | **`DRAFT` 6/6** — nenhum `READY` |
| `status` dos 10 testes da suíte final | `DRAFT` 6, `READY` 4 |
| `manifest.evaluation.status` | **`NOT_YET_VALIDATED`**, `candidate_tests: 6` |
| `validation-decision-template.yaml` | `status: PENDING_BLIND_EXECUTION`; `total_score`, `decision_accuracy`, `methodology_fidelity`, `counterfactual_pass_rate`, `missing_input_pass_rate`, `held_out_pass_rate`, `skill_score`, `baseline_score`, `margin` — **todos `null`** |
| Arquivo de resultados de execução | **Não existe nenhum** nas duas pastas |
| `held-out-registry.yaml` | `registry_status: NOT_AVAILABLE`, `created_before_modeling: false`, `locked: false`, **`cases: []`** |
| `knowledge/examples.jsonl` da skill | **0 bytes** (todas as 8 cópias no projeto) |

**Placeholders reais existem, mas em outro lugar** — no template `templates/generated-skill-template/generated-skill/`: `decision_rules: []`, `tests: []`, e as linhas `{"_template": true, …, "note": "Remover esta linha quando o mapa real for gerado."}` em `evidence-map.jsonl` e `examples.jsonl`, além de `{{SKILL_ID}}`, `{{SKILL_NAME}}` etc. no `manifest.yaml`.

### D.8 Integridade do kit de blind test (verificada nesta auditoria)

Reproduzi os checks do `VERIFY_KIT.py` de forma read-only:

| Check | Resultado |
|---|---|
| SHA-256 `test_suite` | **CONFERE** (`9dc5313c…eb1927`) |
| SHA-256 `baseline_summary` | **CONFERE** (`6e34a788…1bc2b`) |
| SHA-256 `public_cases` | **CONFERE** (`f13b7cd9…034ed6`) |
| SHA-256 `candidate_manifest` | **CONFERE** (`d5349b1f…2cd13b`) |
| SHA-256 `runner_prompt` | **CONFERE** (`54364665…f68531`) |
| Hash da árvore `runtime-bundle` | **CONFERE** (`4d66c81d…b2aecc`) |
| Nomes proibidos no runtime (`test`/`judge`/`audit`) | **nenhum** |
| Marcadores privados no runtime (`expected_behavior:`, `TEST-000`, `judge-private`, …) | **nenhum** |

O isolamento runtime↔judge está efetivamente implementado e o lock reproduz.

### D.9 Validação de schema (executada nesta auditoria, `jsonschema` 4.10.3)

| Registros | Contra schema | Erros |
|---|---|---|
| `evidence.jsonl` (44) | `evidence.schema.yaml` (release) | **0** |
| `decisions-revised.yaml` (8) | `decision.schema.yaml` (**release**) | **0** |
| `decisions-revised.yaml` (8) | `decision.schema.yaml` (**antigo, ainda no disco**) | **7** — `'UNDEFINED' is not one of ['AUTO','REVIEW','APPROVAL']` |
| `workflows-revised-v3.yaml` (1) | `workflow.schema.yaml` (**release**) | **0** |
| `workflows-revised-v3.yaml` (1) | `workflow.schema.yaml` (**antigo**) | **8** — 7× `UNDEFINED` em `steps[].autonomy` + 1× `loops[0].max_iterations: None is not of type 'integer'` |
| `test-candidates-revised.yaml` (6) | `test.schema.yaml` (release) | **0** |

Execução do validador oficial `validate_generated_skill.py`:

- contra `pilot/PILOT-001/validation-input/generated-skill` → **`RESULT: PASS`**, 7 checks, 1 warning (`HELD_OUT_NOT_AVAILABLE`). Reproduz o que o `PREFLIGHT_REPORT.md` afirma.
- contra `pilot/PILOT-001/runtime-bundle` (o pacote que vai para o agente) → **`ERROR MISSING_FILE: tests/test-candidates.yaml` / falha imediata**, com e sem `--held-out-registry`.

---

## E) SKILL GERADA — regra executável ou prosa?

**Resposta medida: as duas coisas, em camadas separadas — e a camada que o agente lê primeiro é prosa.**

O pacote tem duas naturezas distintas:

- **`SKILL.md` (3.885 bytes, 141 linhas)** — prosa explicativa e listas em linguagem natural. Não contém um único par condição→ação formal. As seções `## DECISION RULES` inteira tem 3 linhas e delega: *"As regras completas estão em: `knowledge/decision-rules.yaml`"*.
- **`knowledge/decision-rules.yaml` (31.551 bytes)** — **8 regras estruturadas**, das quais **8/8 têm `conditions` não-vazio** e **8/8 têm `action` não-nulo**. Cada regra traz `conditions[].expression` → `conditions[].consequence`, `action`, `do_not[]`, `ask_user_if_missing[].action ∈ {ASK_USER, STOP}`, `validation_criteria[]` e `exceptions[]`.

### Três exemplos citados do arquivo, com julgamento

**Exemplo 1 — `ADR-0007` "Expandir ou reconstruir conforme dois critérios"** (`knowledge/decision-rules.yaml`)

```yaml
conditions:
  - expression: "Economiza pelo menos 2 horas/semana E o output é melhor que o manual."
    consequence: "Expandir o agente."
  - expression: "Qualquer um dos dois critérios falha."
    consequence: "Voltar e reconstruir o agente."
action: "Medir os dois critérios e escolher expandir ou reconstruir."
do_not: ["Não expandir se apenas um dos dois critérios estiver atendido.", ...]
ask_user_if_missing:
  - {input_name: "Horas economizadas por semana", action: ASK_USER}
  - {input_name: "Comparação de qualidade com processo manual", action: ASK_USER}
autonomy: {level: UNDEFINED}
```

**Julgamento: EXECUTÁVEL.** É a melhor regra do conjunto. Tem limiar numérico (2 h/semana), operador booleano explícito (E), ramo de falha, ação, proibição e política de input faltante. Um agente consegue avaliar isso sem interpretar. Ressalva: o segundo critério ("output melhor que o manual") é subjetivo e não tem rubrica — o teste dessa metade depende de julgamento.

**Exemplo 2 — `ADR-0005` "Manter humano no loop durante o período inicial"**

```yaml
conditions:
  - expression: "Agente está nos primeiros 30 dias de operação."
    consequence: "Revisar cada output antes que ele siga adiante."
  - expression: "Após 30 dias, o desempenho está consistentemente sólido."
    consequence: "A revisão pode ser reduzida."
action: "Manter revisão humana no período inicial e só reduzir após evidência de consistência."
autonomy: {level: REVIEW}
```

**Julgamento: EXECUTÁVEL COM BURACO.** A primeira condição é mecânica (30 dias é contável). A segunda tem um predicado não definido: *"consistentemente sólido"* não tem limiar, nem contagem, nem critério em nenhum lugar do pacote. O `ask_user_if_missing` mitiga (pergunta "Consistência dos outputs"), mas empurra o julgamento para o humano sem lhe dar régua. **É o ponto em que a regra deixa de ser regra e vira consulta.** Comparação com a fonte: o `baseline-summary.md` diz *"reviewing outputs during the first 30 days and reducing review only after consistently solid performance"* — o compilador preservou a vagueza da fonte em vez de inventar um limiar, o que é coerente com HR-02, mas produz uma regra que não fecha sozinha.

**Exemplo 3 — `SKILL.md`, seção `## CORE PRINCIPLES`**

```markdown
1. Começar pelo outcome/função, não por uma tarefa isolada.
2. Usar humanos para julgamento e agentes para execução.
3. Tornar as instruções específicas e estruturadas.
4. Escolher a plataforma conforme o contexto, não antes de definir o problema.
5. Testar, registrar falhas e corrigir.
6. Expandir somente quando o agente prova economia de tempo e qualidade superior ao processo manual.
```

**Julgamento: PROSA, NÃO REGRA.** Nenhuma das 6 linhas tem gatilho, condição, ação ou critério de verificação. São máximas. Isso é exatamente o que a `SKILL.md` da ferramenta §14 EXECUTABLE BEHAVIOR proíbe, citando como contraexemplo *"Conhecer o público é importante."* e exigindo a forma `ação + condição + critério + exceção`. Contam a favor: (a) os princípios estão duplicados em forma estruturada em `knowledge/principles.yaml`; (b) a seção `## EXECUTION PROCEDURE` do mesmo `SKILL.md` é um procedimento numerado de 9 passos com o framework ROBOT e os limiares (3–5 testes, 2 h/semana). Ainda assim, a camada de entrada do agente é predominantemente descritiva.

**Contagem de fecho:** dos 141 renglones do `SKILL.md`, **0 contêm um par condição→ação formal**; 4 seções contêm códigos de estado (`MISSING_REQUIRED_INPUT`, `METHOD_NOT_DEFINED`) sem definir o gatilho em forma verificável. A executabilidade real do pacote está em `decision-rules.yaml` e `workflows.yaml`, não no `SKILL.md`.

---

## F) INCONSISTÊNCIAS

Listadas sem suavização. Cada uma com a evidência do arquivo ao lado.

### F.1 — `confidence.score` é uma constante disfarçada de medida

Todas as **44 evidências** têm `confidence.score = 0.97` e `confidence.level = HIGH`. Conjunto de valores distintos: `{0.97}`. Os 8 ADRs usam `{0.94, 0.96}` — 2 valores para 8 registros. `evidence_strength` também colapsa: `DIRECT` em 37 de 44, sem nenhum `INFERRED` nem `WEAK`.

O `lesson-analyzer.md` §40 dedica 38 linhas a definir faixas de confiança e manda "usar confiança com parcimônia". O resultado tem variância zero. O campo não distingue nada e nenhum consumidor o lê: o `validate_generated_skill.py` não verifica `confidence` em nenhuma linha, e não existe restrição de schema ligando `score` a `level` (um `score: 0.10` com `level: HIGH` passaria).

### F.2 — A cadeia de proveniência termina em ID e o pacote entregue não contém a evidência

`SKILL.md` da ferramenta §12 PROVENANCE promete rastreio com aula e timestamp:

```
DR-017
 ├── EV-0042 — M02-L03 — 00:18:32
```

O que o pacote realmente entrega, em `provenance/evidence-map.jsonl` (16 linhas), é só isto:

```json
{"entity_id":"ADR-0001","entity_type":"DECISION_RULE","source_evidence_ids":["EV-0004","EV-0005"],"origin_class":"SOURCE_EXPLICIT","promotion_level":"CONFIRMED"}
```

Sem aula, sem timestamp, sem citação. E o `runtime-bundle` (`SKILL.md`, `manifest.yaml`, `knowledge/`, `provenance/`) **não inclui `evidence.jsonl`** — verificado nas 6 cópias do bundle. Dentro do pacote que vai para o agente e para o avaliador, `EV-0004` não resolve para lugar nenhum.

Agrava: o `PREFLIGHT_REPORT.md` declara "Provenance evidence closure: PASS", e o check existe de fato — mas compara `union(EV usados)` contra `union(EV no evidence-map)`, ambos escritos pelo **mesmo compilador na mesma passada**. É fechamento auto-referencial. Nenhum código do projeto abre `evidence.jsonl` para confirmar que `EV-0004` existe. (Nesta auditoria, conferi: **existe, 0 refs quebradas** — mas o projeto não tem como saber disso.)

### F.3 — `SKILL.md` da ferramenta e o release contradizem-se sobre UNDEFINED

`SKILL.md` §15 HUMAN CHECKPOINTS (linha 788): *"Toda futura Skill deve definir decisões em **três** níveis"* — e lista `AUTO`, `REVIEW`, `APPROVAL`. `UNDEFINED` **não aparece uma única vez** nos 26.249 bytes do `SKILL.md` (grep: 0 ocorrências). O addendum de hardening §F trata só de REVIEW vs APPROVAL e também não menciona `UNDEFINED`.

Enquanto isso, o produto do piloto tem **7 de 8 ADRs e 7 de 8 steps em `UNDEFINED`** — ou seja, **87,5% do estado de autonomia da skill compilada está num valor que o documento normativo da ferramenta não reconhece.** O schema foi corrigido (`decision-schema-updated.yaml`), o `CHANGELOG.md` menciona a adoção dos "corrected decision/workflow schemas", mas a doutrina em `SKILL.md` §15 nunca foi atualizada.

### F.4 — `UNDEFINED` é obrigatório em processo e impossível de gravar em quase todo o modelo

`methodology-modeler.md` tem uma seção "16 — UNDEFINED REGIONS" (linha 1353), manda emitir `MARK_UNDEFINED` (linha 1180) e calcular uma "UNDEFINED RATE" (linha 1697). `evaluator.md` linha 942 exige verificar se *"existem regiões `UNDEFINED`"*. `skeptic-critic.md` também emite `MARK_UNDEFINED` (linha 822).

Mas `UNDEFINED` só é representável em **`decision.autonomy.level`** e **`workflow.step.autonomy`**. Não existe em `evidence.schema.yaml` (0 ocorrências), `test.schema.yaml` (0), `held-out-registry.schema.yaml` (0). Não há schema para `coverage.yaml`, nem para regiões indefinidas. O único campo agregado — `manifest.scope.undefined_count` — está com valor `null` no piloto, com nota admitindo que a contagem não foi transportada.

Resultado: os quatro prompts pedem uma métrica que o modelo de dados não sabe armazenar.

### F.5 — Nenhum estágio depois de L1 pode ver a fonte, mas os quatro são cobrados por fidelidade à fonte

Medição da seção C.2: `skill-compiler.md` e `evaluator.md` têm **0 ocorrências** de `transcript`, `vídeo`, `fonte original`, `evidence.jsonl`. `methodology-modeler.md` e `skeptic-critic.md` recebem a fonte apenas como flag booleano `original_sources_available:`.

Ao mesmo tempo, `skeptic-critic.md` tem um PASS 1 chamado **PROVENANCE AUDIT** e um PASS 2 **INFERENCE AUDIT** que devem decidir se algo foi inventado; e `evaluator.md` mede `METHODOLOGY_FIDELITY >= 0.80`. Ambos precisam julgar aderência a um material que não recebem. No PILOT-001 isso é visível no artefato: `skeptic-review.yaml` afirma no bloco `passed_checks` que *"Todas as referências EV usadas nos artefatos apontam para evidências existentes"* — uma afirmação de existência que o Skeptic, pelo seu próprio contrato de entrada, não tinha como verificar. (Nesta auditoria a afirmação se confirmou por medição independente; mas o Skeptic a emitiu sem ter os dados.)

### F.6 — O validador obrigatório falha no pacote que o próprio projeto manda entregar

`SKILL.md` §H "Mandatory static preflight" (linha 1344): *"Antes do handoff ao Evaluator, executar `scripts/validate_generated_skill.py`"*, e o handoff só pode ser `READY_FOR_BLIND_TEST` quando *"não há test leakage no runtime bundle"*.

O `PREFLIGHT_REPORT.md` §2 declara, corretamente, que o runtime candidato contém **apenas** `SKILL.md`, `manifest.yaml`, `knowledge/`, `provenance/` — sem `tests/`. **Runtime isolation: PASS.**

Mas a linha 38 do `validate_generated_skill.py` inclui `root/'tests/test-candidates.yaml'` na lista de arquivos **obrigatórios**, e a linha 41 aborta com código 2 se faltar. Executado:

```
$ validate_generated_skill.py .../pilot/PILOT-001/runtime-bundle --schemas .../schemas
ERROR MISSING_FILE: tests/test-candidates.yaml
```

O validador só passa quando apontado para `validation-input/generated-skill/`, que **contém** `tests/` e `audit.yaml` — ou seja, exatamente o pacote que a regra de isolamento proíbe entregar. As duas regras do hardening (§B isolamento e §H preflight obrigatório) são mutuamente inexequíveis sobre o mesmo artefato.

### F.7 — `held_out_integrity: true` sobrevive dentro do pacote entregue, depois de ter sido refutado

Três arquivos afirmam `held_out_integrity: true`: `skeptic-review.yaml`, `skeptic-review-v2.yaml`, `skeptic-review-v3.yaml`.

O `audit-decision.yaml` do release corrige:

```yaml
held_out_integrity:
  status: NOT_VERIFIABLE
  reason: "O audit v3 registrou true, porém nenhum held-out-registry físico pre-modeling foi localizado."
```

E `held-out-registry.yaml` confirma: `registry_status: NOT_AVAILABLE`, `created_before_modeling: false`, `locked: false`, `cases: []`.

**Mas o arquivo `generated-skill/audit.yaml`, que viaja dentro do pacote da skill, é cópia byte-idêntica do `skeptic-review-v3.yaml` e continua afirmando `held_out_integrity: true`.** A correção existe fora do pacote; a afirmação errada existe dentro dele. Quem abrir só a skill lê a versão refutada.

### F.8 — O template contradiz os schemas e reprovaria no validador do próprio projeto

`templates/generated-skill-template/generated-skill/knowledge/decision-rules.yaml` documenta esta forma:

```yaml
#   - rule_id: "DR-0001"          → schema exige decision_id, padrão ^ADR-[0-9]{4,}$
#     requires: []                → schema chama required_inputs
#     reason: "..."               → schema exige rationale (objeto com state)
#     quality_checks: []          → schema chama validation_criteria
#     source_evidence_ids: []     → schema exige source_evidence (minItems 1)
#     autonomy: "AUTO"            → schema exige objeto {level: ...}
```

Nenhum desses nomes existe em `decision.schema.yaml`, que tem `additionalProperties: false`. Um arquivo escrito no formato do template **falharia toda a validação de schema**.

Idem em `tests/test-candidates.yaml` do template: usa um documento único com chave `tests: []`, enquanto o real (e o que o validador lê, via `load_yaml_docs`, linha 48) é YAML multi-documento com um teste por documento. No formato do template, `t.get('subject')` retorna `None` e o check `test-version-closure` (linha 72) dispara `TEST_VERSION_MISMATCH`.

E o `manifest.yaml` do template declara `knowledge.quality_gates: 0`, enquanto o manifest real usa `quality_criteria`.

O template é de 2026-08-10 01:13 — **posterior** aos schemas (23:54–23:58) e ao piloto compilado. Foi escrito depois e mesmo assim não segue o contrato.

### F.9 — Quatro schemas obsoletos continuam no disco, sem marcação, e reprovam o próprio piloto

`Course-to-Skill/course-to-skill-compiler/` mantém `decision.schema.yaml`, `workflow.schema.yaml` e `test.schema.yaml` com **os nomes canônicos** — e os três são versões superadas. Os corretos vivem em `schemas/` com nomes de rascunho (`-updated`, `-updated-v2`). Além disso, `workflow-schema-updated.yaml` (v1) é órfã: não corresponde a nada no release.

Validado: `decisions-revised.yaml` produz **7 erros** contra `decision.schema.yaml` e `workflows-revised-v3.yaml` produz **8 erros** contra `workflow.schema.yaml`. Quem abrir a pasta e usar o arquivo de nome canônico reprova o output oficial do piloto. Nada no diretório indica qual é o vigente — só o MD5 comparado contra o release revela.

### F.10 — 100% SOURCE_EXPLICIT, 100% ACTIVE, 100% HIGH, 0 contradições — em 44 registros

As 44 evidências têm: `origin_class` SOURCE_EXPLICIT 44/44, `status` ACTIVE 44/44, `confidence.level` HIGH 44/44, `contradiction` null 44/44, `inference` null 44/44. Os 8 ADRs: `rationale.state` EXPLICIT 8/8, `promotion_level` CONFIRMED 8/8, `origin_class` SOURCE_EXPLICIT 8/8.

O modelo epistêmico tem 3 classes de origem, 5 estados de status, 4 estados de rationale, 3 de promoção, 5 de força de evidência e um bloco inteiro de contradição. **Na prática, o piloto usou uma opção de cada eixo.** Os campos `MODEL_INFERENCE`, `GENERAL_KNOWLEDGE`, `DISPUTED`, `NEEDS_REVIEW`, `PARTIAL`, `NOT_EXPLICIT`, `PROBABLE`, `WEAK_INFERENCE`, `INFERRED`, `WEAK`, `CONTRADICTION_DETECTED` existem no schema e têm zero uso.

A exceção — e ela é reveladora — são as **10 perguntas**, que estão 10/10 como `MODEL_INFERENCE`. E chegaram lá **só porque o Skeptic reprovou** (SC-003, HIGH). O L1 as tinha classificado como explícitas. A separação SOURCE_EXPLICIT/MODEL_INFERENCE não emergiu da extração; emergiu de uma auditoria manual em segunda passada.

### F.11 — `source_excerpt` vazio em 44/44: nada liga o texto da evidência ao texto da fonte

O campo `source_excerpt` — o único do schema que carregaria a citação literal — está `null` em **todas as 44 evidências**. `context` está preenchido em 1/44, `demonstrated_behavior` em 3/44, `reason_given` em 6/44.

Somando: a transcrição está em **inglês** e as 44 `observation` estão em **português**. Não há nenhuma sequência literal compartilhada entre a evidência e a fonte. Com `source_excerpt` vazio, **nenhuma verificação lexical de ancoragem é possível**, nem manual nem automática. O único vínculo verificável que sobrou é o timestamp — e ele funciona: conferi os 94 timestamps citados contra as 180 marcas do transcript, **93 batem exatamente, 1 não** (`EV-0001`, `end = 00:00:29` → `0:29` não existe no transcript). Esse é o teto atual de verificabilidade da proveniência do projeto, e ele foi medido nesta auditoria, não pelo projeto.

### F.12 — `manifest.evaluation.status: NOT_YET_VALIDATED` não é um valor previsto pela regra G

`SKILL.md` §G "Pilot validation ceiling" (linhas 1330–1338) define os valores permitidos para um piloto de aula única:

```
evaluation.status: PILOT_VALIDATED | PILOT_FINAL_TEST_READY
```

O `manifest.yaml` da skill entregue traz `evaluation.status: NOT_YET_VALIDATED` — fora do par definido. O `validate_generated_skill.py` linha 112 conhece `NOT_YET_VALIDATED` (só o usa em conjunto com `production_ready`), o que mostra que o valor é aceito na prática mas nunca foi incorporado à regra escrita. Divergência de menor gravidade que as anteriores, mas é doutrina e implementação apontando para vocabulários diferentes.

### F.13 — Contradições menores, medidas

| # | Contradição |
|---|---|
| a | `SKILL.md` §26 REQUIRED SCHEMAS lista **4** schemas; o release entrega **5** (inclui `held-out-registry.schema.yaml`, criado no hardening v0.1.1). A seção não foi atualizada. |
| b | `SKILL.md` §26 diz *"Até que esses arquivos existam, utilizar as estruturas conceituais descritas neste documento"* — os arquivos existem desde 2026-08-09 21:51. Texto pré-schema deixado no documento pós-schema. |
| c | `visual-observations.yaml` declara `ready_for_evidence_extraction: true` e `visual_review: COMPLETE`, mas as 3 observações **não têm `evidence_id`**. A ponte com `EV-0041/0042/0043` foi feita em outro arquivo, sem referência cruzada em nenhuma direção. |
| d | `source-metadata.yaml` declara `status.visual_review_pending: true`, enquanto `visual-observations.yaml` declara `visual_review: COMPLETE`. Os dois arquivos de estado da mesma fonte discordam. |
| e | `analysis/quality-criteria (1).yaml` é cópia byte-idêntica (mesmo MD5, mesmo mtime) de `quality-criteria.yaml`. Dois arquivos, um conteúdo, nenhum critério para saber qual é o bom. |
| f | `templates/generated-skill/` é um diretório vazio ao lado de `templates/generated-skill-template/generated-skill/`, que tem 14 arquivos. Dois caminhos com nome quase igual, um deles morto. |
| g | O release está aninhado em pasta homônima duplicada (`course-to-skill-compiler-v0.1.1-pilot-ready/course-to-skill-compiler-v0.1.1-pilot-ready/`), padrão repetido em 4 lugares de `02_PILOTS`. `01_GENERATED-SKILL/` e `03_FINAL-BLIND-TEST/AGENT/` contêm o **mesmo zip** (23.203 bytes) e a mesma árvore descompactada. |
| h | `knowledge/examples.jsonl` tem **0 bytes** nas 8 cópias distribuídas. O `skill-compiler.md` §3 lista `examples.jsonl` como entrada possível; o arquivo é entregue vazio em todos os pacotes, inclusive no runtime que vai ao agente. |

---

## RESUMO NUMÉRICO

| Métrica | Valor medido |
|---|---|
| Arquivos totais (2 pastas) | 229 (89 + 140) |
| Arquivos de texto | 218 |
| Conteúdos de texto distintos | **94** (57% de duplicação) |
| Binários (não abertos) | 8 zips + 3 pngs |
| Diretórios vazios | 1 |
| Schemas no disco | 9 arquivos → 6 conteúdos distintos → **4 vigentes + 1 novo (held-out) + 4 obsoletos** |
| Prompts | 5 × 2 versões (release + antiga), todas distintas |
| Executáveis no projeto | **2** (`validate_generated_skill.py`, `VERIFY_KIT.py`) |
| Evidências do piloto | 44 |
| Refs `EV-` quebradas | **0** |
| Evidências nunca referenciadas | **16 de 44** (12 se contado o pacote compilado) |
| `source_excerpt` preenchidos | **0 de 44** |
| Valores distintos de `confidence.score` nas evidências | **1** (`0.97`) |
| Timestamps citados / conferidos contra o transcript | 94 citados, **93 exatos, 1 divergente** |
| Achados do Skeptic | v1: 3 HIGH + 3 MEDIUM · v2: 1 HIGH + 2 MEDIUM · v3: 0 + 2 LOW |
| Correções do Skeptic verificadas nos arquivos | **6 de 6 aplicadas** |
| Testes escritos | 6 (skill) + 10 (suíte final) |
| Testes executados | **0** — todas as métricas de validação estão `null` |
| Held-out cases | **0** (`registry_status: NOT_AVAILABLE`) |
| `UNDEFINED` no piloto | 14 ocorrências, todas em `autonomy` |
| Inconsistências catalogadas | 12 principais + 8 menores |

---

**FIM DA FASE 1.** Nenhuma correção foi aplicada, nenhum código foi escrito, nenhuma implementação foi iniciada. Nada dentro de `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado.
