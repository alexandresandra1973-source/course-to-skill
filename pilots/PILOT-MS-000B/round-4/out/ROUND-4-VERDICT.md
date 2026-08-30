# `PILOT-MS-000B` ROUND 4 — VEREDITO

**`CANDIDATE → FUSION CONTRACT`** · execução 2 · 2026-08-30 · **zero chamadas de modelo**.

Opening Record base `fff9e05aac9fe89b135b23d57560ad87780e3231f25c53b98f1d5557516b3726`
(pushed em `3b44084d`) · adendo da execução 2
`9e69849ac4d1b06875e0f9313b6082a49ff140d003fd9f84701763250fb8b407` (pushed em `093819ca`).
Execução 1: `PILOT_MS_000B_ROUND_4_INVALID`, preservada em `out-invalid-exec-1/`.

## 1. Portões — 15/15

`canaries_CA` · `canaries_I26` · `source_packages_intact` ·
`precedence_undefined_nao_rejeita` · `passo_unico_nao_rejeita` · `evidence_refs_verificadas`
· `claim_refs_verificadas` · `admitted_materializados` · `rejected_nao_consumidos` ·
`transporte_preservado` · `objetos_distintos` · `real_passo_unico` ·
`real_precedence_undefined` · `fusion_id_sem_mtx_policy` · `zero_model_calls`.

## 2. Canários — 11 `CA` + 6 `I26`, todos PASS

`CA1` `PRECEDENCE UNDEFINED → ADMITTED` · `CA2` `PASSO UNICO → ADMITTED` ·
`CA3` `SEM PASSOS → REJECTED_STRUCTURAL` · `CA4` `ORDEM INVALIDA → REJECTED_STRUCTURAL` ·
`CA5`/`CA5b` refs quebradas → `REJECTED_STRUCTURAL` · `CA5c`/`CA6` válidos → `ADMITTED` ·
`CA7` anti-pattern com evidence quebrada → `REJECTED_STRUCTURAL` ·
`CA8` `PRESENT_AND_CONSUMABLE` · `CA9` `NOT_CONSUMABLE`.

`I26-A` mesmo input+config → mesmo `fusion_id` · `I26-B` policy diferente → `fusion_id` novo,
**esperado e permitido** · `I26-C1` duas MTX-POLICY → byte-idêntico · `I26-C2` injetar
`mtx_policy_hash` → **`FAIL`** · `I26-C3` assinatura sem `mtx_policy_hash` · `I26-C4` inputs
declarados passam no guard.

## 3. Admissão — RUN × SOURCE × KIND

| kind | recebidos (6 pacotes) | `ADMITTED` | `REJECTED_STRUCTURAL` | motivo |
|---|---|---|---|---|
| `rule_candidates` | 96 | **96** | 0 | — |
| `workflow_candidates` | 30 | **30** | 0 | — |
| `anti_pattern_candidates` | 21 | 0 | **21** | `LOCAL_ID_INVALIDO` |
| **total** | **147** | **126** | **21** | |

Por pacote: A `23 → 19 adm / 4 rej` · B `26 → 23 adm / 3 rej`, idêntico nos três runs.

`PRECEDENCE_UNDEFINED` e `PASSO_UNICO` **não aparecem em `reasons` nenhuma vez**.

## 4. `UNDEFINED ≠ INVALID` — 90/90

Todas as 90 rules reais com `precedence: UNDEFINED` (30 por run): `ADMITTED`, presentes em
`fusion/rules`, `precedence` preservada como `UNDEFINED`, `adjudication: null`, hash
estrutural conferindo. Nenhuma `open_question` artificial criada.

## 5. `PASSO_UNICO` transportado — 12/12

`WF-0036`, `WF-0040` (A) e `WF-0041`, `WF-0044` (B), nos três runs: `ADMITTED`,
`inherited_defect = PASSO_UNICO`, **1 step na origem → 1 step na Fusion**, hash conferindo.
Nenhum passo adicionado, nenhum removido.

## 6. Transporte — e a prova de que ele PODE reprovar

Origem: `round-3/out/packages/{RUN}/pkg-{k}/SOURCE-LOCAL-CANDIDATES.json` (pacote selado).
Destino: `round-4/out/fusion/fusion-package-R4-{RUN}.json` **relido do disco**.
Arquivos distintos, leituras distintas. 126/126 preservados.

Controle negativo sobre `WF-0035`, com a mesma função de hash:

| mutação | detecta |
|---|---|
| remover 1 step | **SIM** |
| inverter a ordem | **SIM** |
| mudar 1 `action` | **SIM** |
| mudar 1 `order_key` | **SIM** |
| adjudicar `precedence` numa rule | **SIM** |

Isto é o que a Round 3 não tinha: lá `struct_source` e `struct_fusion` saíam do mesmo
objeto e `preservado` não podia ser falso.

## 7. Consumo real da Fusion

Por run: `admitted_candidate_refs` **42** · `rejected_candidate_refs_NOT_CONSUMABLE` **7** ·
`fusion/rules` **32** · `fusion/workflows` **10** · `fusion/anti_patterns` **0**.
126 admitidos = 126 materializados. **Vazamentos: 0.**

| run | `fusion_id` | `mtx_policy_hash` |
|---|---|---|
| RUN-1 | `63ecddc905999a410b2fc56fa1e327206854009ebeeca4d407b54dc228f7f96b` | `null` |
| RUN-2 | `ab1d314db404b8e5cc4b2e0891b94df162dab608e49dca3b6a1c92697f7ffcd5` | `null` |
| RUN-3 | `d48e2e22d8943be76720c8a7f3f617159015f05ee2b71b3c5b3205ea2f3f6e4d` | `null` |

Os três diferem porque os `source_package_hash` diferem por run — os claims selados são
diferentes. `FUSION-CONFIG` e policy são os mesmos nos três.

## 8. Source Packages — intactos

6/6 byte-equivalentes antes e depois: `source_package_hash`, `SEAL-RECORD.yaml`, selo
`PASS`, completude `PASS`. `EXTERNAL-SEAL-REGISTRY.txt`
`8b2eee5681b007eaf39ab40057888ff7b39b8ca3efd20e2d3f67f48815e5943f` inalterado. Nenhum
reselo, nenhuma regeneração.

## 9. Três limitações registradas — não escondidas

1. **`EVIDENCE_LASTRO_NON_EMPTINESS_NOT_TESTABLE_ON_R3_CORPUS`** — os 147 candidatos têm
   `evidence_refs` vazio. `EV-RESOLVABILITY` foi provado por canário (ref quebrada rejeita,
   ref válida admite); comportamento sobre corpus com lastro populado **não foi medido**.
2. **`CLAIM_REFS_NOT_APPLICABLE_ON_R3_CORPUS`** — 147/147 `NOT_APPLICABLE`; o campo não
   existe. Predicado implementado e provado por `CA5b`/`CA5c`, **não exercitado** no corpus.
3. **`ANTI_PATTERN_ADMISSION_NOT_EXERCISABLE_ON_R3_CORPUS`** — os 21 anti-patterns colidem
   em `local_id` com a rule de origem. `CA6`/`CA7` provam o comportamento sinteticamente; o
   corpus real **não exercita** admissão de anti-pattern.

## 10. Achado arquitetural — registrado, não corrigido

> **`(source_package_hash, local_id)` não é chave única nos Source Packages da Round 3.**

`run_round3.py:95` dá ao anti-pattern o `local_id` da rule de origem. O Architecture Freeze
manda qualificar por `(source_package_hash, local_id)` na travessia de fronteira; estes
pacotes quebram a unicidade que essa qualificação pressupõe. Defeito herdado do empacotador
da Round 3, mesma família de `evidence_refs: []`. **Não corrigido nesta rodada.**

## 11. Classificação

# `PILOT_MS_000B_ROUND_4_PASS`

# `CANDIDATE_TO_FUSION_LAYER = QUALIFIED_IN_ROUND_4`

`MS_000B_ACCEPTED` **não** é declarado. A aceitação final é do design-review externo,
combinando Round 3 (Source Package layer) e Round 4 (Candidate→Fusion layer).
