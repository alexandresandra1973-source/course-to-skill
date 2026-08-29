# TEST-0008 — discrepância 5×6 dos `comparison_metrics`

- Gerado: `2026-08-11T23:13:13+00:00` · gerador `test0008_metrics_discrepancy.py`
- READ-ONLY sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/`
- **Casamento por identidade**: `TEST-0008` como chave de YAML, ou `artifact_id`/nome de arquivo. Menção no corpo do texto nunca conta.
- Nada congelado, nenhuma lista canônica proposta.

## 1. A frase literal, e de qual arquivo veio cada número

### `ARCHITECTURE_REVIEW.md` — Fase 2 — Revisão de arquitetura

- Autodeclaração de fase: linha 3: **Fase 2 — Architecture Review.**

- **linha 36:** (v) **4 de 6 `comparison_metrics`** (`DECISION_ACCURACY`, `MISSING_INPUT_ACCURACY`, `HALLUCINATION_RATE`, `TOTAL_SCORE`) **não têm critério de rubrica correspondente**;
- **linha 174:** **(4)** definição computável de 4 das 6 `comparison_metrics` — `DECISION_ACCURACY`, `MISSING_INPUT_ACCURACY`, `HALLUCINATION_RATE` e `TOTAL_SCORE` **não têm critério de rubrica correspondente** em nenhum dos 10 testes.
- **linha 219:** Isso **não** altera o restante de (c): o braço de **TEST-0008 (SUMMARY_VS_SKILL)** continua sem pacote — `baseline-summary.md` segue apenas dentro de `judge-private/`, sem runner próprio, e permanecem os outros três impedimentos (contradição de protocolo, `"ROBOT prompt"` exigido de um baseline que não o conhece, 4 de 6 `comparison_metrics` sem critério de rubrica).

### `CLAUDE_ARCHITECTURE_PROPOSAL.md` — Fase 3 — Proposta de arquitetura

- Autodeclaração de fase: linha 3: **Fase 3 — Proposta de arquitetura.**

- **linha 43:** | P6 | **Métrica sem definição computável não é métrica.** Escala única [0,1]. | R6 | 4 de 6 `comparison_metrics` sem critério de rubrica; colisão `0.85` (0–1) vs `minimum_score: 85` (0–100) para o mesmo nome. |
- **linha 375:** **Permanecem em aberto os outros 2:** a rubrica ainda exige `"ROBOT prompt"` em `expected_output.required_elements`, elemento que o baseline não menciona e a fonte menciona em `9:52`; e **4 de 6** `comparison_metrics` continuam sem critério de rubrica correspondente.

**Número declarado: 4 de 6.**

**De qual arquivo foi contado:** os dois docs **não citam caminho nenhum** para essa contagem. Não há como atribuí-la a um arquivo por leitura do texto; o que dá para fazer é reconstruir a contagem, que é a §3.

## 2. RELEASE × WORKSPACE, lado a lado

Artefatos em que `TEST-0008` declara `comparison_metrics` **como chave**: **8**.

| posição | artefatos | conjuntos distintos | métricas |
|---|---|---|---|
| **RELEASE** | 4 | 1 | `TOTAL_SCORE`, `DECISION_ACCURACY`, `METHODOLOGY_FIDELITY`, `EXECUTION_QUALITY`, `HALLUCINATION_RATE` |
| **WORKSPACE** | 4 | 1 | `TOTAL_SCORE`, `DECISION_ACCURACY`, `METHODOLOGY_FIDELITY`, `EXECUTION_QUALITY`, `HALLUCINATION_RATE` |

**Um único conjunto, de 5 métricas, em todas as posições.** RELEASE e WORKSPACE declaram exatamente o mesmo.

| # | posição | artefato | sha256 | métricas |
|---|---|---|---|---|
| 1 | RELEASE | `Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1/course-to-skill-compiler-v0.1.1-pilot-ready.zip :: course-to-skill-compiler-v0.1.1-pilot-ready/pilot/PILOT-001/final-test/judge-private/test-suite.yaml` | `9dc5313c0171` | 5 |
| 2 | RELEASE | `Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1/course-to-skill-compiler-v0.1.1-pilot-ready.zip :: course-to-skill-compiler-v0.1.1-pilot-ready/pilot/PILOT-001/validation-input/final-test-suite.yaml` | `9dc5313c0171` | 5 |
| 3 | RELEASE | `Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1/course-to-skill-compiler-v0.1.1-pilot-ready/course-to-skill-compiler-v0.1.1-pilot-ready/pilot/PILOT-001/final-test/judge-private/test-suite.yaml` | `9dc5313c0171` | 5 |
| 4 | RELEASE | `Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1/course-to-skill-compiler-v0.1.1-pilot-ready/course-to-skill-compiler-v0.1.1-pilot-ready/pilot/PILOT-001/validation-input/final-test-suite.yaml` | `9dc5313c0171` | 5 |
| 5 | WORKSPACE | `Course-to-Skill-Compiler/02_PILOTS/PILOT-001/02_VALIDATION/PILOT-001-final-blind-test-kit.zip :: PILOT-001-final-blind-test-kit/judge-private/test-suite.yaml` | `9dc5313c0171` | 5 |
| 6 | WORKSPACE | `Course-to-Skill-Compiler/02_PILOTS/PILOT-001/02_VALIDATION/PILOT-001-final-blind-test-kit/PILOT-001-final-blind-test-kit/judge-private/test-suite.yaml` | `9dc5313c0171` | 5 |
| 7 | WORKSPACE | `Course-to-Skill-Compiler/02_PILOTS/PILOT-001/03_FINAL-BLIND-TEST/JUDGE/PILOT-001-judge-private-v0.1.1.zip :: PILOT-001-judge-private-v0.1.1/judge-private/test-suite.yaml` | `9dc5313c0171` | 5 |
| 8 | WORKSPACE | `Course-to-Skill-Compiler/02_PILOTS/PILOT-001/03_FINAL-BLIND-TEST/JUDGE/PILOT-001-judge-private-v0.1.1/PILOT-001-judge-private-v0.1.1/judge-private/test-suite.yaml` | `9dc5313c0171` | 5 |

## 3. A diferença é workspace × release?

**Não.** As duas posições declaram o mesmo conjunto, de **5** métricas. Não existe sexta métrica em nenhum dos lados, e portanto não há sexta métrica "morando" em lugar nenhum.

O `TEST-0007` declara **5**: `TOTAL_SCORE`, `DECISION_ACCURACY`, `METHODOLOGY_FIDELITY`, `EXECUTION_QUALITY`, `MISSING_INPUT_ACCURACY`

- interseção (4): `DECISION_ACCURACY`, `EXECUTION_QUALITY`, `METHODOLOGY_FIDELITY`, `TOTAL_SCORE`
- só no `TEST-0007`: `MISSING_INPUT_ACCURACY`
- só no `TEST-0008`: `HALLUCINATION_RATE`

**União dos dois testes comparativos: 6** — `DECISION_ACCURACY`, `EXECUTION_QUALITY`, `HALLUCINATION_RATE`, `METHODOLOGY_FIDELITY`, `MISSING_INPUT_ACCURACY`, `TOTAL_SCORE`

É esse o **6** da auditoria: união `TEST-0007` ∪ `TEST-0008`, não a contagem do `TEST-0008` isolado.

## 4. Os contratos legados que declaram o TEST-0008

Contratos com `TEST-0008` como **chave** de `comparative_tests`: **13**.

**Nenhum declara `comparison_metrics` próprio.** Eles trazem só `comparison` e `margin_threshold`, ou seja, dizem COMO comparar e não O QUE medir. Não há terceira contagem escondida aqui.

| artefato | `comparison` | `margin_threshold` | chaves |
|---|---|---|---|
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV2.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV2/JUDGE-SCORING-CONTRACT-v0.1.3-REV2.yaml` | `SKILL_MINUS_SUMMARY` | `FROM_ABLATION_MARGIN_LOCK` | comparison, full_preservation_guard_required, margin_threshold |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV2.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV2/canary/contract-canary.yaml` | `None` | `None` | full_preservation_guard_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV2.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV2/canary/contract-undefined-aggregation.yaml` | `None` | `None` | full_preservation_guard_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV3.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV3/JUDGE-SCORING-CONTRACT-v0.1.3-REV3.yaml` | `SKILL_MINUS_SUMMARY` | `FROM_ABLATION_MARGIN_LOCK` | comparison, full_preservation_guard_required, margin_threshold, structural_ceiling_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV3.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV3/canary/contract-canary.yaml` | `None` | `None` | full_preservation_guard_required, structural_ceiling_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV3.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV3/canary/contract-undefined-aggregation.yaml` | `None` | `None` | full_preservation_guard_required, structural_ceiling_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV4.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV4/JUDGE-SCORING-CONTRACT-v0.1.3-REV4.yaml` | `SKILL_MINUS_SUMMARY` | `FROM_ABLATION_MARGIN_LOCK` | comparison, full_preservation_guard_required, margin_threshold, structural_ceiling_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV4.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV4/canary/contract-canary.yaml` | `None` | `None` | full_preservation_guard_required, structural_ceiling_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV4.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV4/canary/contract-undefined-aggregation.yaml` | `None` | `None` | full_preservation_guard_required, structural_ceiling_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV5.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV5/JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `SKILL_MINUS_SUMMARY` | `FROM_ABLATION_MARGIN_LOCK` | comparison, full_preservation_guard_required, margin_threshold, structural_ceiling_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV5.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV5/canary/contract-canary.yaml` | `None` | `None` | full_preservation_guard_required, structural_ceiling_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV5.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV5/canary/contract-undefined-aggregation.yaml` | `None` | `None` | full_preservation_guard_required, structural_ceiling_required |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK.zip :: PILOT-001-v0.1.3-REVISION-PACK/JUDGE-SCORING-CONTRACT-v0.1.3.yaml` | `SKILL_MINUS_SUMMARY` | `PRELOCKED_IN_TEST_SUITE_OR_COMPARISON_LOCK` | comparison, margin_threshold |

## 5. As contagens encontradas

| contagem | de onde vem |
|---|---|
| **5** | declaração do `TEST-0008` nos artefatos de suíte |
| **6** | união `TEST-0007` ∪ `TEST-0008` |

Nenhuma foi escolhida como canônica. Congelar a lista é decisão de quem conduz o teste, e o ADR de paridade de informação a lista como bloqueador número 1 do TEST-0008.

