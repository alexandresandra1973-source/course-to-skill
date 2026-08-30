# MS-000B — `TARGETED_IDENTITY_REWRITE_AND_REVERIFY` — VEREDITO

Execução 2 · 2026-08-30 · **zero chamadas de modelo** · **não é Round 5**.

Errata `ARCHITECTURE-FREEZE-ERRATA-IDENTITY-QUALIFICATION-v1` · policy `v0.2` ·
`typed-ref-v1`. Opening Record `8a159946…` (pushed em `284200f1`) e adendo `68093ff9…`
(pushed em `fe2ba2f4`). Execução 1: `MS_000B_TYPED_IDENTITY_REVERIFY_INVALID`, preservada.

## 1. Portões — 16/16

`errata_registrada` · `identity_canaries_ID1_ID8` · `i26` · `source_packages_intact` ·
`typed_qualification_zero_collisions` · `todas_refs_derivadas_tipadas` ·
`admitted_rejected_disjuntos` · `admitted_materializados` · `rejected_nao_consumidos` ·
`transporte_preservado` · `objetos_distintos` · `real_passo_unico` ·
`real_precedence_undefined` · `anti_pattern_outcome_medido` · `fusion_id_sem_mtx_policy` ·
`zero_model_calls`.

## 2. `ID1–ID8` (+ `ID5b`) — 9/9

`ID1` cross-kind duplicate → ambos `ADMITTED` e **refs distintas** · `ID2` same-kind
duplicate → `REJECTED_STRUCTURAL` / `LOCAL_ID_INVALIDO` · `ID3` typed ref → `RESOLVED n=1`
para os dois objetos · `ID4` tupla antiga → **`AMBIGUOUS_REF`** · `ID5` disjunção `= 0` em
package que satisfaz a unicidade congelada · **`ID5b`** interseção `= 1` em package que a
viola — **limite declarado do modelo** · `ID6` `SELF` schema-implied → `RESOLVED` ·
`ID7` `SELF` genérica → **`INVALID_REF`** · `ID8` **6/6 idênticos**.

## 3. `I26` — 6/6

`A` mesmo input+config → mesmo `fusion_id` · `B` policy diferente → id novo, permitido ·
`C1` duas MTX-POLICY → byte-idêntico · `C2` injetar `mtx_policy_hash` → **`FAIL`** ·
`C3` assinatura sem `mtx_policy_hash` · `C4` inputs declarados passam no guard.

## 4. Candidate Admission recomputada sob `v0.2`

| kind | recebidos | `ADMITTED` | `REJECTED_STRUCTURAL` |
|---|---|---|---|
| `rule_candidate` | 96 | **96** | 0 |
| `workflow_candidate` | 30 | **30** | 0 |
| `anti_pattern_candidate` | 21 | **21** | 0 |
| **total** | **147** | **147** | **0** |

Por pacote: A `23 → 23/0`, B `26 → 26/0`, idêntico nos três runs.

## 5. Anti-patterns — o ponto obrigatório, medido e não assumido

Os **21** rejeitados na Round 4 por `LOCAL_ID_INVALIDO` foram **reavaliados**, não promovidos:
**21 `ADMITTED`, 0 rejeitados**, nenhum outro predicado disparou (conjunto de motivos vazio).
Os **21** chegam a `fusion/anti_patterns` com ref tipada inequívoca e hash estrutural
conferindo.

Prova de distinção sobre a colisão real, no mesmo pacote:

```
rule         → {"entity_kind":"rule_candidate",        "local_id":"R-0095", ...}  F-RU-rule_candidate-R-0095
anti_pattern → {"entity_kind":"anti_pattern_candidate","local_id":"R-0095", ...}  F-AN-anti_pattern_candidate-R-0095
```

## 6. Refs tipadas e ambiguidade

**Refs não tipadas nos artefatos derivados: 0.** **Refs ambíguas: 0.** O varredor percorre
todo o Fusion Package e exige `source_package_hash` + `entity_kind` + `local_id` **dentro**
da própria ref, em `admitted_candidate_refs`, `rejected_candidate_refs_NOT_CONSUMABLE`,
`candidate_admission_report[].qualified_ref`, `fusion/*[].candidate_ref` e
`provenance_ledger[].element_ref` (49 entradas por run).

## 7. Disjunção — e o que ela vale neste corpus

| run | admitidos | rejeitados | interseção | disjuntos |
|---|---|---|---|---|
| RUN-1 · RUN-2 · RUN-3 | 49 | **0** | 0 | **SIM** |

> **Honestidade sobre a força desta evidência.** Com 147/147 admitidos, o conjunto rejeitado
> é **vazio**, e a disjunção no corpus real é satisfeita **trivialmente**. A prova
> não trivial é `ID5`, com conjunto rejeitado **não vazio**, e o contraste é `ID5b`.
> Comparação com a Round 4, onde a mesma medida dava **21 tuplas nas duas listas**: lá o
> conjunto rejeitado era não vazio e a sobreposição era real.

## 8. Consumo e transporte

147 admitidos = **147 materializados**. **Vazamentos: 0.** Origem lida do
`SOURCE-LOCAL-CANDIDATES.json` do pacote selado; destino **relido** de
`out/fusion/fusion-package-IDENTITY-{RUN}.json` já gravado. Arquivos distintos.

Controle negativo — o teste continua podendo reprovar: remover step **detecta** · inverter
ordem **detecta** · mudar `action` **detecta** · mudar `do_not` de anti-pattern **detecta**.

## 9. `PRECEDENCE_UNDEFINED` e `PASSO_UNICO`

**90/90** rules `UNDEFINED`: `ADMITTED`, na Fusion, `precedence = UNDEFINED` preservada,
`adjudication: null`, hash conferindo. **12/12** workflows de um passo: `ADMITTED`,
`inherited_defect = PASSO_UNICO`, 1 step → 1 step, hash conferindo. A identidade tipada
**não mudou semântica de precedence**.

## 10. `fusion_id`

| run | `fusion_id` | `mtx_policy_hash` |
|---|---|---|
| RUN-1 | `7e785a0aba34db524893e69fc4e0d064a7806320b802067ded0b938b65050562` | `null` |
| RUN-2 | `f5e781ffc3d053c0e3de3200610ef5fc3972f0b27133f78c5c17548887ee9ba7` | `null` |
| RUN-3 | `77db636be51f088701e9801f588ef202e7d46433d98880c3ec746e4bc6b60deb` | `null` |

Cobre `source_package_hashes` · `fusion_config_hash` · `candidate_admission_report_hash` ·
`admitted_candidate_set_hash` · `outputs_hash` · **`identity_errata_hash`**.

## 11. Source Packages

**6/6 byte-equivalentes** antes e depois. `EXTERNAL-SEAL-REGISTRY`
`8b2eee5681b007eaf39ab40057888ff7b39b8ca3efd20e2d3f67f48815e5943f` inalterado. Nenhum
reaberto, renumerado, editado, reselado. Nenhuma Claim gerada.

## 12. Classificação

# `MS_000B_TYPED_IDENTITY_REVERIFY_PASS`

# `IDENTITY_MODEL_QUALIFIED_BY_ERRATA`

`MS_000B_ACCEPTED` **não** é declarado. A aceitação final é do gate externo.
