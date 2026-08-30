# DECISION RECORD — escopo da `ROUND 4` do `PILOT-MS-000B`

**`decision_id`:** `DR-MS-000B-R4-001` · **Data:** 2026-08-30 · **Ator:** Alexandre Sandra
**Base:** `DECISION-RECORD-MS-000B-R3-CANDIDATE-AUDIT.md`
(`e69004810a9472d85a7b84c2d6f3ad255f74185966923d9aeae83a4f3f7fef5d`)
**Classe:** `GIT_NATIVE_BY_DESIGN`

> Objetivo: testar **corretamente e exclusivamente** a travessia
> `SOURCE_LOCAL_CANDIDATE → CANDIDATE ADMISSION → FUSION`.
> A Round 4 e **pos-Source-Package**.

Estado de entrada autorizado: `CANDIDATE_AUDIT_PRESERVED` ·
`MS_000B_ROUND_3_STRUCTURAL_PASS` · `CANDIDATE_TO_FUSION_LAYER = NON_QUALIFYING_IN_ROUND_3`.

---

## D1 — Inputs congelados
Os **seis Source Packages selados da Round 3**, read-only: `RUN-{1,2,3}/pkg-{A,B}`.
Hash de pacote, selo e completude verificados **antes e depois**. **Nao reselar. Nao
regenerar. Nao modificar.** `I20` continua valendo.

## D2 — A Round 3 nao e reescrita
Permanece aceita para Source Package Contract · Seal Contract · Package Identity ·
Provenance · Compile Trace · completude · Fusion aceitando so pacotes completos/selados.
**Nao prova** Candidate Admission · Candidate→Fusion consumption · workflow transport real.

## D3 — `CANDIDATE-ADMISSION-POLICY` ≠ `MTX-POLICY`

| | pertence a | pode tocar `fusion_id`? |
|---|---|---|
| `MTX-POLICY` | **Operationalization** | **NAO** — proibido por `I26` |
| `CANDIDATE-ADMISSION-POLICY` | **`FUSION-CONFIG`** | **SIM** — e configuracao estrutural do proprio pipeline da Fusion |

Isto **nao** viola `I26`. O erro da Round 3 nao foi a policy influenciar `fusion_id`; foi a
policy ter sido **criada depois do Opening Record**, **nao autorizada** e **desconectada do
consumo real** (achados `D-1`, `D-5`, `D-6`).

## D4 — `CANDIDATE-ADMISSION-POLICY v0.1`
sha256 `64c2feaeebf1ac62c559031f1918741a35856fb1115b5b10e7707a1e922a75c9`. Principio: **admission decide somente se o candidate esta
estruturalmente apto a ser consumido pela Fusion.** Nao resolve precedence, nao decide
applicability MTX, nao avalia preferencia comercial, nao elimina knowledge por conter
questao nao resolvida, nao "melhora" candidate.

Predicados de rejeicao — **lista exaustiva, pre-declarada**: `LOCAL_ID_INVALIDO` ·
`REQUIRED_FIELD_AUSENTE` · `WORKFLOW_SEM_PASSOS` · `ORDEM_INVALIDA` ·
`EVIDENCE_REF_QUEBRADA` · `CLAIM_REF_QUEBRADA`.

**`PRECEDENCE_UNDEFINED != REJECT`** e **`PASSO_UNICO != REJECT`**. Ambos preservados como
`inherited_defect`. Sem adjudicacao, sem expansao, sem correcao, sem conversao automatica
em `DEFERRED_TO_RUNTIME` — nao existe conflito real que a exija.

## D5 — `FUSION-CONFIG-R4`
sha256 `cc34c4834a54291c2db822463bacf1f40c3ed3bf0179a34e83b542a115fcfe79`. Carrega o hash da policy, as versoes de consumo e de transporte, a
politica de relacao (`NOT_APPLIED_IN_ROUND_4`) e o toolchain. `mtx_policy_hash: null`.

## D6 — Lastro de evidencia: o predicado e separado em dois, e a limitacao e declarada

**Constatacao medida antes do Opening Record:** os **147** candidates dos seis pacotes tem
`evidence_refs` **vazio** — `run_round3.py` grava a lista literal vazia — e o campo
`claim_refs` **nao existe** em candidate algum. Os *claims* tem lastro (38/38 no RUN-1/A);
os *candidates* nao tem nenhum.

Exigir `evidence_refs` **nao vazias** rejeitaria **147/147** e tornaria os itens 13, 14, 18
e 19 do bloco — que exigem `ADMITTED` e materializacao na Fusion — impossiveis de
satisfazer. Seria descartar 100% do corpus por defeito do **empacotador da Round 3**, nao da
camada sob teste, repetindo o achado `D-3` num campo diferente.

Decisao, **pre-declarada antes de qualquer avaliacao**, na disciplina
`MISSING ≠ NOT_APPLICABLE`:

| predicado | tipo | efeito |
|---|---|---|
| `EV-RESOLVABILITY` — `evidence_refs ⊆ evidence_ids(pkg)` | **REJEICAO** | ref quebrada → `REJECTED_STRUCTURAL`; conjunto vazio satisfaz vacuamente |
| `EV-POPULATION` — refs nao vazias | **MEDIDA, nao rejeicao** | marca `EVIDENCE_REFS_EMPTY_INHERITED_FROM_R3_PACKAGING` |
| `CLAIM-RESOLVABILITY` | **REJEICAO** | `NOT_APPLICABLE` no corpus R3 (campo ausente); testado por canario sintetico |

**Limitacao registrada, nao escondida:**
`EVIDENCE_LASTRO_NON_EMPTINESS_NOT_TESTABLE_ON_R3_CORPUS`. A Round 4 prova que refs
**quebradas** rejeitam (CA5, CA7, CA5b) e que refs **validas** admitem (CA6, CA5c). **Nao**
prova comportamento sobre um corpus com lastro populado, porque esse corpus nao existe.

## D7 — Transporte tem de poder falhar
Origem e destino sao **arquivos distintos**, lidos separadamente: origem no
`SOURCE-LOCAL-CANDIDATES.json` do pacote selado, destino relido do
`fusion-package-R4-{RUN}.json` **ja gravado em disco**. Nunca duas referencias ao mesmo
objeto em memoria — que foi exatamente o achado `D-4`.

## D8 — Blocagem
`NOT_APPLIED_IN_ROUND_4`, declarado no Opening Record. A travessia candidate→fusion nao
depende dele, e claim blocking nao mede candidate admission.

## D9 — Zero chamadas de modelo
Nenhum cliente Anthropic e instanciado. Contador `MODEL_CALLS = 0` no runner. Qualquer
chamada → `PILOT_MS_000B_ROUND_4_INVALID`.

## D10 — Classificacao possivel
`PILOT_MS_000B_ROUND_4_PASS` / `_FAIL` / `_INVALID`. Em PASS declara-se **somente**
`CANDIDATE_TO_FUSION_LAYER = QUALIFIED_IN_ROUND_4`. **`MS_000B_ACCEPTED` nao e declarado
automaticamente** — a aceitacao final e do design-review externo, combinando Round 3
(Source Package layer) e Round 4 (Candidate→Fusion layer).
