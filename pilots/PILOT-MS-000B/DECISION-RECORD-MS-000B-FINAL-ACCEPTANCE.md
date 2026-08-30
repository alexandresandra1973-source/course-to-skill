# DECISION RECORD — `MS_000B_ACCEPTED`

**`decision_id`:** `DR-MS-000B-FINAL-001`
**Decisão:** **`MS_000B_ACCEPTED`**
**Ator:** Design Review externa
**Data:** 2026-08-30
**Base:** `PILOT-MS-000B`, Rounds 1–4 mais o `TARGETED_IDENTITY_REWRITE_AND_REVERIFY`
**Política vigente:** `ARCHITECTURE FREEZE`
`6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b`, selo
`f35016cbedf4617a45a4b03a89acefb01495d6d50651b77065b26c7fd901a0c3`, **mais** a
`IDENTITY QUALIFICATION ERRATA v1`
`2f8232f6c184668370ed9e440256b0de3f6ee801a7bee67285eb291c1a527ad2`
**Classe:** `GIT_NATIVE_BY_DESIGN` · registro **aditivo**; **nenhuma rodada é reescrita ou
reclassificada**

---

## 1. O QUE FICA ACEITO

Cada item abaixo corresponde a medição registrada, não a asserção de encerramento:

| # | escopo aceito | onde foi medido |
|---|---|---|
| 1 | **Source Package Contract** | Round 3 — 11 membros + `TOOLCHAIN`, `PC1–PC8` |
| 2 | **Package Completeness** | Round 3 — `completude=PASS` nos seis; portão separado do verificador de selo |
| 3 | **Seal Contract** | Round 3 — sete condições, `seal_verifier.py` do MS-000A reusado sem alteração |
| 4 | **`SOURCE_ID` / `SOURCE_CONTENT_HASH` / `SOURCE_PACKAGE_HASH`** | Round 3 — três identidades distintas e estáveis |
| 5 | **typed global identity pela Identity Errata** | Reverify — `ID1–ID8` + `ID5b`, 9/9; 1.129/1.129 tuplas únicas |
| 6 | **Claim provenance** | Round 3 — `PROVENANCE-LEDGER`, `ref_scope: SELF` interno, qualificação na fronteira |
| 7 | **Claim entailment gate** | Round 3 — `KILL-3`: 244 claims seladas, 244 com entailment |
| 8 | **Candidate Admission** | Reverify — policy `v0.2`, 147 recebidos, 147 `ADMITTED` |
| 9 | **Candidate→Fusion consumption** | Reverify — 147 admitidos = 147 materializados, 0 vazamentos |
| 10 | **workflow structural transport** | Reverify — origem e destino em arquivos distintos, controle negativo detecta as cinco mutações |
| 11 | **`PASSO_UNICO` preservation** | Reverify — 12/12, 1 step → 1 step, hash conferindo |
| 12 | **`PRECEDENCE_UNDEFINED` preservation** | Reverify — 90/90, `UNDEFINED` preservada, `adjudication: null` |
| 13 | **multi-package isolation** | Round 3 — `JC-POSITIVE`, `JC-CROSS-A-IN-B`, `JC-CROSS-B-IN-A` PASS; 0 claims em pacote errado |
| 14 | **Fusion consumindo somente packages válidos** | Round 3 e Reverify — `fusion_consumes_valid_only`, seals `PASS` verificados antes do consumo |

## 2. ARQUITETURA

# `ARCHITECTURE_FROZEN_WITH_IDENTITY_ERRATA`

Normativa:

```
GLOBAL_OBJECT_IDENTITY = (source_package_hash, entity_kind, local_id)
```

O **Architecture Freeze original permanece histórico e byte-idêntico** —
`6d0eb7dd…`, `FREEZE-RECORD` 17/17. A errata supersede **somente** `E6`, `I4`, `D5` e a
interpretação de `I23`. **Não** é `ARCHITECTURE_REOPENED`.

## 3. NÃO AUTORIZADO

# `PRODUCTION = NOT_AUTHORIZED`

**Nenhum componente experimental é promovido a produção.** Runners, libs, canários,
policies e pacotes do MS-000B permanecem experimentais. `SOURCE = chapter` continua
`PILOT_MS_000B_ONLY` e não vira contrato de produção.

## 4. LIMITAÇÃO OBRIGATÓRIA

# `CANDIDATE_DIRECT_PROVENANCE_NOT_YET_QUALIFIED`

No corpus real do MS-000B, os `SOURCE_LOCAL_CANDIDATE` herdados tinham:

- **`evidence_refs = []`** — 147 de 147, medido;
- **`claim_refs` ausentes** — `NOT_APPLICABLE` em 147 de 147, medido.

Portanto o MS-000B **não demonstrou em corpus real** a cadeia direta completa:

```
SOURCE_LOCAL_CANDIDATE → claim/evidence → SOURCE_ANCHOR → L0
```

O que **foi** demonstrado: que ref **quebrada** rejeita e ref **válida** admite (`CA5`,
`CA5b`, `CA5c`, `CA6`, `CA7`) — **sinteticamente**. E que a cadeia
`claim → evidence → anchor → L0` existe e resolve para as **claims** (`I29`, `KILL-3`,
`LOCAL-COHERENCE-REPORT` com `findings: []`). O elo que falta é o que parte do
**candidate**.

> **Isto não invalida o acceptance do MS-000B no seu escopo.** Vira **condição obrigatória
> do próximo piloto.**

Limitações irmãs, já registradas e mantidas:
`EVIDENCE_LASTRO_NON_EMPTINESS_NOT_TESTABLE_ON_R3_CORPUS` ·
`CLAIM_REFS_NOT_APPLICABLE_ON_R3_CORPUS` ·
`ANTI_PATTERN_ADMISSION_NOT_EXERCISABLE_ON_R3_CORPUS` (esta última **superada** pela
reverify: 21/21 admitidos sob identidade tipada).

## 5. GATE PARA O MS-001

# `MS_001_DESIGN_AUTHORIZED`

# `MS_001_EXECUTION_NOT_YET_AUTHORIZED`

A execução do MS-001 **só pode ser aberta** depois que o seu Opening Record incluir
explicitamente, **selado antes de qualquer execução avaliatória**, um teste de

### `CANDIDATE PROVENANCE`

Para **todo** candidate usado em relação cross-source:

1. `evidence_refs` **não vazias**, **ou** mecanismo normativo equivalente **aprovado** —
   aprovado antes, não improvisado durante;
2. refs **resolvíveis**;
3. `claim_refs` quando aplicáveis;
4. cadeia `candidate → evidence/claim → anchor → L0` **completa e verificada**;
5. **nenhuma relação semântica cross-source sobre candidate órfão**.

Candidate sem lastro suficiente:

```
NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION
```

> **Não inventar provenance posteriormente.** Preencher `evidence_refs` depois de ver o
> resultado seria a mesma falha do achado `D-1` — a regra nascendo depois da medição.

## 6. CADEIA DE EVIDÊNCIA — aditiva, sem reclassificação

O acceptance final é resultado da **combinação aditiva** destas evidências. **Nenhuma rodada
histórica é reclassificada:** a Round 1 continua `INVALID`, a Round 2 continua
`NON_QUALIFYING`, a Round 3 continua `STRUCTURAL PASS`.

### MS-000A

| artefato | sha256 |
|---|---|
| `DECISION-RECORD-MS-000A-ACCEPTED.md` | `abcfa0ac27b6e8266601419f24401a9532d23f34ec5ab09fd16cd4b3f45d2a97` |

### MS-000B

| # | evidência | artefato | sha256 |
|---|---|---|---|
| 1 | Round 1 **`INVALID`** | `ROUND-1-CLASSIFICATION.md` | `245811f7598d0848db8700be04265dd818edc34a898a1c5ccf970466ab824432` |
| 1b | errata de hash da Round 1 | `ROUND-1-HASH-ERRATA.md` | `f0e690e806c7979efdcb5f8aee18919e24f7fcaed57be4458e7edaad63516207` |
| 2 | Round 2 **`NON_QUALIFYING`** | `ROUND-2-CLASSIFICATION.md` | `4f8a879ba30e6b1c8ee3a151ad7b25e83f1e18d3c8cef85829a3a9e9c961ec50` |
| 3 | Round 3 **`STRUCTURAL PASS`** | `round-3/OPENING-RECORD.md` | `9aa050b2e01121441fbbea3da4ed6e7d3f8b389b423ca9695f3e10b217a1b302` |
| 3b | | `round-3/out/ROUND-3-VERDICT.md` | `6260059727f29a9fe2f7afdc2df8ff60f95752d242cd955c0422448c86a8bb5c` |
| 3c | | `DECISION-RECORD-MS-000B-R3.md` | `29dfb0dfeff6723d6d782a714ed9318f77374d8427b48b75e06b46f94d264c48` |
| 4 | **Candidate Admission Audit** | `MS-000B-ROUND-3-CANDIDATE-ADMISSION-AUDIT-REPORT.md` | `61e34ba0b8f43a14ed3e68dbbd94fd990eed156058536b5737ed615c18ef6f95` |
| 5 | **Candidate Audit Preservation** | `DECISION-RECORD-MS-000B-R3-CANDIDATE-AUDIT.md` | `e69004810a9472d85a7b84c2d6f3ad255f74185966923d9aeae83a4f3f7fef5d` |
| 6 | Round 4 escopo | `DECISION-RECORD-MS-000B-R4.md` | `dafe98e5325c56cdf4bb671f6bdde599ca09aa90f6a9ecaa597ff48b62a2619c` |
| 6b | Round 4 Opening Record | `round-4/OPENING-RECORD.md` | `fff9e05aac9fe89b135b23d57560ad87780e3231f25c53b98f1d5557516b3726` |
| 6c | Round 4 execução 1 `INVALID` | `round-4/ROUND-4-EXEC-1-INVALID.md` | `c98082b5d7739475d8042f2b602fd45f645909d76f50044fbd3ab175056a8b01` |
| 6d | Round 4 adendo | `round-4/OPENING-RECORD-ADDENDUM-EXEC-2.md` | `9e69849ac4d1b06875e0f9313b6082a49ff140d003fd9f84701763250fb8b407` |
| 6e | **Round 4 Candidate→Fusion PASS** | `round-4/out/ROUND-4-VERDICT.md` | `fe22afa6e000967fdabee44fd9b854893f1895a94ca23784a26a6d9b9ba08db1` |
| 7 | **Qualified Identity Namespace Audit** | `MS-000B-QUALIFIED-IDENTITY-NAMESPACE-AUDIT-REPORT.md` | `364f4afe55d87a02edae174efce621fc4f60adb3fab5c2fc57d4a874cee9e989` |
| 7b | medições reproduzíveis | `out-identity-audit/identity-measurements.json` | `20ac4127add8b666f1f3068318651da1240456fff986c0e8403de22a00cfb184` |
| 8 | **Architecture Freeze Identity Errata** | `ARCHITECTURE-FREEZE-ERRATA-IDENTITY-QUALIFICATION-v1.md` | `2f8232f6c184668370ed9e440256b0de3f6ee801a7bee67285eb291c1a527ad2` |
| 8b | Decision Record da errata | `DECISION-RECORD-IDENTITY-QUALIFICATION-ERRATA.md` | `a4b0736a96f5ea912b94785b535611c7a62e58607c2f503641043b7c6a27df92` |
| 9 | Reverify Opening Record | `round-4-identity-reverify/OPENING-RECORD.md` | `8a1599468ce46635a63e57215c69e274979c66a39282fc8db794979a640e9d72` |
| 9b | Reverify execução 1 `INVALID` | `round-4-identity-reverify/REVERIFY-EXEC-1-INVALID.md` | `653e7425af60732b71ce9cc0a997bd116df6fe93144977282c63c44fea1dd818` |
| 9c | Reverify adendo | `round-4-identity-reverify/OPENING-RECORD-ADDENDUM-EXEC-2.md` | `68093ff9cd1f9efe11c76538718fae29ee5b672edceaf362069c1578a50032ef` |
| 9d | **Typed Identity Reverify PASS** | `round-4-identity-reverify/out/REVERIFY-VERDICT.md` | `cf7fb12dc47e73d3c7b684e653c39c731bad60eb6517bb7d62150f1ed49871e3` |

## 7. O QUE ESTE REGISTRO **NÃO** FAZ

- não reclassifica Round 1, 2 ou 3;
- não altera código experimental, Source Package, Fusion Package ou runner algum;
- não altera o Architecture Freeze original;
- não resolve `N1`–`N9`;
- não promove nada a produção;
- não autoriza a **execução** do MS-001.

## 8. STATUS

# `MS_000B_ACCEPTED`
