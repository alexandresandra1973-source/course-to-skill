# OPENING RECORD — MS-000B **TARGETED IDENTITY REWRITE AND REVERIFY**

**Selado e pushed ANTES de qualquer execução avaliatória sobre os pacotes reais.**
Depois deste push **nenhuma metodologia muda**. Data: 2026-08-30.

> **Isto NÃO é a Round 5.** É `TARGETED_IDENTITY_REWRITE_AND_REVERIFY`, operando sobre os
> **mesmos seis Source Packages selados da Round 3**, que permanecem read-only.

Base normativa: `ARCHITECTURE-FREEZE-ERRATA-IDENTITY-QUALIFICATION-v1.md`
(`2f8232f6c184668370ed9e440256b0de3f6ee801a7bee67285eb291c1a527ad2`)
e `DR-ARCH-IDENTITY-001`
(`a4b0736a96f5ea912b94785b535611c7a62e58607c2f503641043b7c6a27df92`),
commitados e pushed em `2aeafc1733f38c9d4a4600502a4e268f6a0a1547`.

## 1. IDENTIDADE NORMATIVA

```
GLOBAL_OBJECT_IDENTITY = (source_package_hash, entity_kind, local_id)
```

`entity_kind` canônico: `artifact` · `source_anchor` · `evidence` · `claim` ·
`rule_candidate` · `workflow_candidate` · `workflow_step` · `anti_pattern_candidate`.

## 2. OS SEIS SOURCE PACKAGES — CONGELADOS, READ-ONLY

| pacote | `source_package_hash` | `SEAL-RECORD.yaml` |
|---|---|---|
| RUN-1/pkg-A | `d5fd5dad81cfe5d1bad04f3fceeaada1b7e9b357b9c081f49dd5f287e2dbd212` | `35236db37cdbdca146ceef4c6b1dc7d14b0e33f3ccc6ac538ec39a4b917b6208` |
| RUN-1/pkg-B | `c66b269533cedcabb8db4df28c06a2548b45a87615e298d7b57cc6333f97ebff` | `a8ae6f2c60976670a06982bc49223d7dd6d35ae9a0b3e286817dbbc8547aab71` |
| RUN-2/pkg-A | `70c11cfbc96f4e038266dc4a33de95cf149041b21973c650a1194296a6a87fd6` | `13170bb49d93d4479f450d2fb61440d517989797f5d36b6818592aeafa6b5e7b` |
| RUN-2/pkg-B | `9ba68de595573c24b4ccc2920eebddf757706bdaa0dcad5c05e750cdc18ba8d9` | `87842e187e93950139979b1a4a33ee54112b28c761b36e7a1a00d5b2084adb39` |
| RUN-3/pkg-A | `5133d40dd62c7c0f3a6fdd8d762bbad1a58f13dc291da40a96a9c7a00f6e0439` | `6bcb0c735534b093df6e6aff3a0ce63ff9c041ac378723098d957b501afe1544` |
| RUN-3/pkg-B | `c9ce7f61760a05cea8d6d1a7603f2ba279691b86f364f60aa73912c337186911` | `3ffd2e904661ebbbe9e828459f35bfd4424dfac9adbd22415835aca0d3bc7dd4` |

`EXTERNAL-SEAL-REGISTRY.txt`: `8b2eee5681b007eaf39ab40057888ff7b39b8ca3efd20e2d3f67f48815e5943f`

**Não reabrir · não renumerar · não editar candidates · não reselar · não gerar Claims.**
Hash de pacote, selo, completude e registry verificados **antes e depois**. Qualquer
alteração → `FAIL`.

## 3. ARTEFATOS CONGELADOS POR HASH

| artefato | sha256 |
|---|---|
| `CANDIDATE-ADMISSION-POLICY-v0.2.json` | `f142938853239c58ff3cb80dbcc650da8ea1461d2cde2ea38978ba478d1b9caf` |
| `FUSION-CONFIG-IDENTITY-REVERIFY.json` | `e1da64fad9b0ff02a9d3d906d1aa5aa7bc155ace49b13bc045da380e3079dea5` |
| `lib/typedref.py` | `03df6113f24360b8a5b52a2c63a483748dde5049e140fdb974aebe3800fa451b` |
| `lib/admission.py` | `24ab979a54fec4d93e7c45e39ddc44489c08e6d9732318ad7e8afb1675d0871c` |
| `lib/fusion.py` | `28308bf008db36abae24eeb364330d77ff7088b12d9de5ae9a5311e3cb1ed40d` |
| `identity_canaries.py` | `be0739f2773218db2209fca11dfde46df34bf4c89cf686efead680410738a7fb` |
| `i26_canary.py` | `b80010e8bb335bdc5d1f79c3bf936c434072fb26fcce55aab4ac931c2db8f567` |
| `run_reverify.py` | `0daa15584d741d0e2e6f3c69dd6f97a4cf1f82a3ee9c6d04749d9307476bb229` |
| `identity_audit_measure.py` | `e46da697e4a9c2326757cf52748ef5cdfd6dd1593b54b0f6408432082beb345e` |
| `out-identity-audit/identity-measurements.json` | `20ac4127add8b666f1f3068318651da1240456fff986c0e8403de22a00cfb184` |

## 4. POLICY v0.2 — A MUDANÇA NORMATIVA É UMA SÓ

| | |
|---|---|
| **OLD v0.1** | `local_id` deve ser único **package-wide** |
| **NEW v0.2** | `(entity_kind, local_id)` deve ser único **dentro do package** |

Todos os demais predicados permanecem semanticamente equivalentes. **Nenhuma regra nova de
qualidade.** O diff contra a v0.1 toca apenas a chave de unicidade e a emissão de refs
tipadas — está no commit B e é auditável linha a linha.

Predicados de rejeição, lista **exaustiva** e inalterada: `LOCAL_ID_INVALIDO` ·
`REQUIRED_FIELD_AUSENTE` · `WORKFLOW_SEM_PASSOS` · `ORDEM_INVALIDA` ·
`EVIDENCE_REF_QUEBRADA` · `CLAIM_REF_QUEBRADA`. `PRECEDENCE_UNDEFINED` e `PASSO_UNICO`
continuam **não rejeitando**.

## 5. NENHUMA CONTAGEM É PREDECLARADA

O contrafactual da auditoria mediu 126/147 → 147/147 sob a nova regra de unicidade. **Esse
número não é predeclaração de resultado.** As 21 rejeições antigas por `LOCAL_ID_INVALIDO`
serão **reavaliadas**, não promovidas automaticamente; se outro predicado legítimo rejeitar
alguma, o motivo real é registrado.

## 6. SCHEMA DE REFERÊNCIA TIPADA

```json
{ "source_package_hash": "...", "entity_kind": "rule_candidate", "local_id": "R-0095" }
```

**Nunca** `[sph, "R-0095"]`. Campos obrigatórios **dentro** da própria ref. Aplicado a:
`admitted_candidate_refs` · `rejected_candidate_refs_NOT_CONSUMABLE` ·
`candidate_admission_report[].qualified_ref` · `fusion/rules[].candidate_ref` ·
`fusion/workflows[].candidate_ref` · `fusion/anti_patterns[].candidate_ref` ·
`provenance_ledger[].element_ref`. Um varredor mecânico percorre todo artefato derivado e
falha se encontrar **qualquer** ref não tipada.

**Os artefatos históricos da R3 e da R4 NÃO são alterados para isso.**

## 7. CANÁRIOS `ID1–ID8` — MATRIZ DECLARADA AGORA

| canário | fixture | esperado |
|---|---|---|
| `ID1` | mesmo `local_id` em `rule_candidate` e `anti_pattern_candidate` | ambos válidos e **distintos** |
| `ID2` | mesmo `(kind, local_id)` duas vezes no package | `REJECTED_STRUCTURAL` / `LOCAL_ID_INVALIDO` |
| `ID3` | ref tipada | resolve **exatamente um** objeto |
| `ID4` | `(sph, R-0095)` sobre package com rule + anti-pattern | **`AMBIGUOUS_REF`** |
| `ID5` | package que **satisfaz** a unicidade congelada | `admitted ∩ rejected = ∅` |
| `ID5b` | package que **viola** unicidade same-kind | interseção **não vazia** — **limite declarado** |
| `ID6` | `SELF` ref em campo com kind `schema-implied` | resolve corretamente |
| `ID7` | `SELF` genérica, sem kind fixo e sem `entity_kind` | **`INVALID_REF`** |
| `ID8` | os seis packages antes/depois | **6/6 intactos** |

### `ID5b` — o limite que declaro antes de medir

A identidade tipada resolve colisão **cross-kind**. Ela **não pode** discriminar duplicata
**same-kind**: dois objetos com o mesmo `(sph, kind, local_id)` partilham a mesma
`GLOBAL_OBJECT_IDENTITY` **por construção**. É exatamente por isso que a errata §3 congela a
unicidade same-kind como **MUST**, e `ID2` é quem a aplica. Registrado como limite do modelo,
não contornado. No corpus real, `same-kind collisions = 0` — medido.

Qualquer `ID` que falhe → `MS_000B_TYPED_IDENTITY_REVERIFY_INVALID`, antes dos pacotes reais.

## 8. TRANSPORTE — CONTINUA PODENDO FALHAR

Origem lida de `round-3/out/packages/{RUN}/pkg-{k}/SOURCE-LOCAL-CANDIDATES.json`; destino
**relido** de `out/fusion/fusion-package-IDENTITY-{RUN}.json` **já gravado**. Dois arquivos,
duas leituras. **Não se volta ao teste tautológico da R3.**

## 9. `PRECEDENCE_UNDEFINED` E `PASSO_UNICO`

`UNDEFINED != REJECT`, preservada sem adjudicação. Identidade tipada **não muda semântica de
precedence**. `PASSO_UNICO` transportado exatamente como um passo.

## 10. `fusion_id` E `I26`

```
fusion_id = sha256(canon({ source_package_hashes, fusion_config_hash,
   candidate_admission_report_hash, admitted_candidate_set_hash,
   outputs_hash, identity_errata_hash }))
```

`mtx_policy_hash` **proibido**. A `CANDIDATE-ADMISSION-POLICY v0.2` entra via `FUSION-CONFIG`.
Canário `I26` reexecutado: **A** mesmo input/config → mesmo id; **B** policy diferente → id
novo, permitido; **C** injetar `mtx_policy_hash` → `FAIL`.

## 11. `PASS` / `FAIL` / `INVALID`

`INVALID` precede `FAIL`. `INVALID`: qualquer `ID` ou canário `I26` falha, ou qualquer
chamada de modelo. `FAIL`: Source Package alterado · ref derivada não tipada · ref ambígua ·
`admitted ∩ rejected ≠ ∅` · admitido não materializado · rejeitado consumido · hash de
transporte divergindo sem transformação declarada · `mtx_policy_hash` presente.

## 12. ZERO CHAMADAS DE MODELO

Nenhum cliente instanciado. `MODEL_CALLS = 0` verificado como portão. Qualquer chamada →
`IDENTITY_REVERIFY_INVALID`.

## 13. TRAVAS

Mesmo em `PASS`: não declarar `MS_000B_ACCEPTED`; não iniciar MS-001; não usar marketing
corpus; não regenerar Source Package; não implementar Operationalization, Operational
Package, Router ou Skill Pack; não tocar N1–N9; não reescrever o Architecture Freeze
original nem as Rounds 3 e 4.
