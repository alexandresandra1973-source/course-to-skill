# MS-000B — QUALIFIED IDENTITY NAMESPACE AUDIT REPORT

*Auditoria read-only executada em 2026-08-30 sobre `HEAD = a690c9d9c254a23701a16a3037fe6fba98b3adc1`.
Zero escrita, zero commit, zero chamadas de modelo. Preservada aqui como evidência; os números
são reproduzíveis por `identity_audit_measure.py`.*

## 1. Gate

`HEAD` = `origin/main` = `a690c9d9c254a23701a16a3037fe6fba98b3adc1` · tree limpo (0) · Freeze **17/17** · `SHA256SUMS` **0 FAILED** em `PILOT-MS-000B` (18), `round-2` (18), `round-3` (93), `round-4` (10) · seis Source Packages `selo=PASS`, `completude=PASS` · Drive 0 escritas. **GATE = PASS.**

`round-4/out/SHA256SUMS-OUT.txt` reporta 13/14 OK — o único FAILED é o manifesto listando **a si próprio**, cujo hash foi computado antes de o arquivo existir. Defeito cosmético do manifesto auxiliar; os 13 artefatos reais conferem.

## 2. População de entidades

| package | artifact | anchor | evidence | claim | rule_cand | wf_cand | wf_step | anti_pat | **total** |
|---|---|---|---|---|---|---|---|---|---|
| RUN-1/A | 2 | 44 | 44 | 38 | 13 | 6 | 19 | 4 | **170** |
| RUN-1/B | 2 | 56 | 56 | 43 | 19 | 4 | 23 | 3 | **206** |
| RUN-2/A | 2 | 44 | 44 | 41 | 13 | 6 | 19 | 4 | **173** |
| RUN-2/B | 2 | 56 | 56 | 42 | 19 | 4 | 23 | 3 | **205** |
| RUN-3/A | 2 | 44 | 44 | 42 | 13 | 6 | 19 | 4 | **174** |
| RUN-3/B | 2 | 56 | 56 | 38 | 19 | 4 | 23 | 3 | **201** |
| | 12 | 300 | 300 | 244 | 96 | 30 | 126 | 21 | **1.129** |

`workflow_step` é endereçável — 126 objetos com `local_id` próprio, que a auditoria da Round 4 não tinha alcançado. Cada pacote tem ainda 12 `seal_member`, endereçados por **caminho relativo**, namespace distinto de `local_id`, fora desta população.

## 3. Colisões de `(source_package_hash, local_id)`

1.129 objetos · 1.108 tuplas distintas · **21 colisões**. Sete `local_id` distintos, repetidos nos três runs: `R-0095`, `R-0098`, `R-0101`, `R-0102` (pkg-A) e `R-0109`, `R-0112`, `R-0124` (pkg-B), todos `rule_candidate` × `anti_pattern_candidate`.

## 4. Same-kind vs cross-kind

**CROSS-KIND: 21. SAME-KIND: 0.** O caso grave não ocorre.

## 5. Teste de `(source_package_hash, entity_kind, local_id)`

1.129 objetos · **1.129 tuplas distintas · 0 colisões** → **`TYPED_QUALIFICATION_IS_UNIQUE`**.

Matriz de sobreposição lexical **medida**, não deduzida de prefixo: único par não nulo é `anti_pattern × rule = 7`, e são **7 de 7** — 100% dos ids de anti-pattern são emprestados de rules (`run_round3.py` constrói o anti-pattern com o `local_id` da rule). Todos os demais pares: 0.

## 6. Referências existentes, por forma

| forma | ocorrências |
|---|---|
| `NAKED_LOCAL_ID` intra-pacote com `ref_scope: SELF` | **890** |
| `CURRENT_FROZEN_FORM` `(sph, local_id)` | **391** |
| `NAKED_LOCAL_ID` em listas de defeito (R3) | **60** |
| `TYPED_FORM` como **tupla** | **0** |

Onde a Round 4 "usou kind", o kind é um **campo adjacente**, nunca dentro da ref.

## 7. Round 4 — o que foi realmente usado

O verificador foi corrigido; **o formato persistido continua no contrato antigo**.

| artefato / campo | forma persistida | ambígua? |
|---|---|---|
| `run_round4.py` detector de vazamento | `(sph, kind, local_id)` — só em memória | não |
| `run_round4.py` índice dos canários | `(kind, local_id)` — só em memória | não |
| `admitted_candidate_refs` | `(sph, local_id)` | **SIM** |
| `rejected_candidate_refs_NOT_CONSUMABLE` | `(sph, local_id)` | **SIM** |
| `fusion/*[].candidate_ref` | `(sph, local_id)` + `kind` irmão | ambígua na tupla |
| `candidate_admission_report[].qualified_ref` | `(sph, local_id)` + `kind` irmão | ambígua na tupla |
| R3 `claims_qualified` | `(sph, local_id)` | não — `CL-*` não colide |

**420 refs persistidas; 105 (25,00%) ambíguas em isolamento.** E o caso limite: a tupla `["d5fd5dad…","R-0095"]` aparece em `admitted_candidate_refs` **e** em `rejected_candidate_refs_NOT_CONSUMABLE` — 7 por run, **21 no total**.

## 8. Impacto

**Identity resolution — NÃO.** 21 de 1.129 tuplas denotam dois objetos.
**Provenance — SIM.** 105 arestas persistidas ambíguas. As 890 refs `SELF` não apontam hoje para id colidente, mas por coincidência lexical medida (`EV∩AN = EV∩ART = AN∩ART = 0`), não por garantia de contrato.
**Candidate Admission — SIM, muda decisões.** Contrafactual medido: unicidade por pacote → 126/147 admitidos; por `(kind, local_id)` → 147/147. Delta 21.
**Fusion — SIM.** `admitted` e `rejected_NOT_CONSUMABLE` deixam de ser disjuntos.
**Reproduction — NÃO sem heurística.**

## 9. Options A / B / C

**A — `local_id` único package-wide:** não renumeraria corpus histórico (rule/workflow/step ids vêm do P002; só o anti-pattern é derivado), mas mudaria `SOURCE-LOCAL-CANDIDATES.json` → `member_manifest` → **os seis `source_package_hash`**, invalidando pacotes, registry, Fusion R3/R4, admission reports, Opening Records e vereditos. Impacto máximo.

**B — qualificação tipada:** preserva os 1.129 `local_id`, resolve 21/21 colisões, mantém os pacotes selados intactos, exige errata aditiva sobre E6/I4/D5 e I23.

**C — `object_id` próprio:** conceitualmente o mais limpo; introduz quarta identidade e obriga a reabrir a família de invariantes. Avaliado só conceitualmente.

## 10. Classificação arquitetural

**`ARCHITECTURE_FREEZE_ERRATA_REQUIRED`.** Não `IMPLEMENTATION_ERRATA_ONLY`: o freeze não contém `kind`, `tipo` ou `namespace` em cláusula de identidade alguma, e a 2-tupla dita literalmente **não é injetiva** sobre 1.129 objetos. Não `ARCHITECTURE_REOPEN_REQUIRED`: a Option B preserva a segunda cláusula de E6, não toca os quatro produtos, o contrato de selo, o namespace `SELF`, a fronteira Fusion/MTX nem `I26`.

## 11. Impacto sobre a Round 4

**`TARGETED_IDENTITY_REWRITE_AND_REVERIFY`.** Não `NO_RERUN_REQUIRED` porque 105 refs são ambíguas e 21 tuplas estão nas duas listas, e porque a decisão sobre 21 anti-patterns depende da regra de unicidade. Não `ROUND_4_RERUN_REQUIRED` porque a admissão é determinística e offline, os pacotes estão intactos, os records já carregam `kind`, e o transporte já foi provado com controle negativo.

## 12–14. Zero escrita · zero commit · zero modelo

Confirmados na execução da auditoria.

## 15. Classificação final

# `IDENTITY_AUDIT_COMPLETE`
