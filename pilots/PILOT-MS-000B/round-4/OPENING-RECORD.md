# OPENING RECORD — `PILOT-MS-000B` **ROUND 4** — CANDIDATE → FUSION CONTRACT

**Selado e pushed ANTES de qualquer execucao avaliatoria sobre os pacotes reais.**
Depois deste push **nenhuma metodologia muda**. Data: 2026-08-30.

Estado de entrada: `CANDIDATE_AUDIT_PRESERVED` · `MS_000B_ROUND_3_STRUCTURAL_PASS` ·
`CANDIDATE_TO_FUSION_LAYER = NON_QUALIFYING_IN_ROUND_3`.
`HEAD` de partida: `7f1e8ad6d489709cb901d81fc0823a5c03e7e2e0`.

## 1. OBJETIVO

Testar **exclusivamente** `SOURCE_LOCAL_CANDIDATE → CANDIDATE ADMISSION → FUSION`.
Rodada **pos-Source-Package**. **ZERO chamadas de modelo.** Nenhuma Claim nova. Nenhum
Source Package recompilado.

## 2. OS SEIS SOURCE PACKAGES — CONGELADOS POR HASH

| pacote | `source_package_hash` | `SEAL-RECORD.yaml` sha256 |
|---|---|---|
| `RUN-1/pkg-A` | `d5fd5dad81cfe5d1bad04f3fceeaada1b7e9b357b9c081f49dd5f287e2dbd212` | `35236db37cdbdca146ceef4c6b1dc7d14b0e33f3ccc6ac538ec39a4b917b6208` |
| `RUN-1/pkg-B` | `c66b269533cedcabb8db4df28c06a2548b45a87615e298d7b57cc6333f97ebff` | `a8ae6f2c60976670a06982bc49223d7dd6d35ae9a0b3e286817dbbc8547aab71` |
| `RUN-2/pkg-A` | `70c11cfbc96f4e038266dc4a33de95cf149041b21973c650a1194296a6a87fd6` | `13170bb49d93d4479f450d2fb61440d517989797f5d36b6818592aeafa6b5e7b` |
| `RUN-2/pkg-B` | `9ba68de595573c24b4ccc2920eebddf757706bdaa0dcad5c05e750cdc18ba8d9` | `87842e187e93950139979b1a4a33ee54112b28c761b36e7a1a00d5b2084adb39` |
| `RUN-3/pkg-A` | `5133d40dd62c7c0f3a6fdd8d762bbad1a58f13dc291da40a96a9c7a00f6e0439` | `6bcb0c735534b093df6e6aff3a0ce63ff9c041ac378723098d957b501afe1544` |
| `RUN-3/pkg-B` | `c9ce7f61760a05cea8d6d1a7603f2ba279691b86f364f60aa73912c337186911` | `3ffd2e904661ebbbe9e828459f35bfd4424dfac9adbd22415835aca0d3bc7dd4` |

`EXTERNAL-SEAL-REGISTRY.txt`: `8b2eee5681b007eaf39ab40057888ff7b39b8ca3efd20e2d3f67f48815e5943f`

**Read-only.** Hash de pacote, selo e completude verificados **antes e depois**. Qualquer
alteracao → `FAIL`. **Nao reselar, nao regenerar.**

## 3. ARTEFATOS NORMATIVOS — CONGELADOS POR HASH

| artefato | sha256 |
|---|---|
| `CANDIDATE-ADMISSION-POLICY-v0.1.json` | `64c2feaeebf1ac62c559031f1918741a35856fb1115b5b10e7707a1e922a75c9` |
| `FUSION-CONFIG-R4.json` | `cc34c4834a54291c2db822463bacf1f40c3ed3bf0179a34e83b542a115fcfe79` |
| `DECISION-RECORD-MS-000B-R4.md` | `dafe98e5325c56cdf4bb671f6bdde599ca09aa90f6a9ecaa597ff48b62a2619c` |
| `lib/admission.py` | `88d74f22251b8cb996ea458a7c451ae1b9db48162d9739094f9ce1c7ab4b0e27` |
| `lib/fusion.py` | `5c03d3f694548ae9843240b979cfeadec91d90417dfc1bd323a183b23efe24b1` |
| `canaries_r4.py` | `24ce2311a22c1ff8484a508e501ff2b2a054343261539474ae2d2f72afdd1f5a` |
| `i26_canary.py` | `889369305b2bf3dca29cb2a5fea547aca96d0f87bc71a285e3072d5c2f65406f` |
| `run_round4.py` | `02581b10660124647fe0913525eb0409216c2a06428854760e89c50029d7c9d6` |

## 4. REGRAS POR `kind` — PRE-DECLARADAS

Predicados de rejeicao, **lista exaustiva**: `LOCAL_ID_INVALIDO` · `REQUIRED_FIELD_AUSENTE`
· `WORKFLOW_SEM_PASSOS` · `ORDEM_INVALIDA` · `EVIDENCE_REF_QUEBRADA` · `CLAIM_REF_QUEBRADA`.
Estados: `ADMITTED` · `REJECTED_STRUCTURAL`. Nada mais rejeita.

**`rule_candidates`** — campos obrigatorios `local_id · name · trigger · condition · action`;
`EV-RESOLVABILITY`; `CLAIM-RESOLVABILITY`.
**`workflow_candidates`** — `local_id · name · steps`; `len(steps) >= 1`; `order_key` presente,
sem duplicata, estritamente crescente na ordem persistida; cada step com
`local_id · order_key · action`; `EV-RESOLVABILITY` no workflow e em cada step.
**`anti_pattern_candidates`** — `local_id · do_not` nao vazio; `EV-RESOLVABILITY`;
`CLAIM-RESOLVABILITY`. **Nao e admitido incondicionalmente** (fecha `D-8`).

## 5. `PRECEDENCE_UNDEFINED`

**`PRECEDENCE_UNDEFINED != REJECT`.** Rule estruturalmente valida cujo unico defeito seja
`precedence: UNDEFINED` e **`ADMITTED`**. Preserva `precedence = UNDEFINED`, preserva
provenance, preserva candidate ref. **Nao adjudica. Nao descarta.** Nao converte
automaticamente em `DEFERRED_TO_RUNTIME` — nao ha conflito real que o exija; nao se cria
conflito artificial. O que esta rodada prova e somente **`UNDEFINED ≠ INVALID`**.

## 6. `PASSO_UNICO`

**`PASSO_UNICO != REJECT`.** Workflow de um passo e estruturalmente valido. Marcado
`inherited_defect = PASSO_UNICO`, transportado **exatamente como um passo**. Nao expandir,
nao remover, nao corrigir.

## 7. LASTRO — DOIS PREDICADOS SEPARADOS, E A LIMITACAO DECLARADA

Medido **antes** deste Opening Record: os **147** candidates dos seis pacotes tem
`evidence_refs` **vazio**; `claim_refs` **nao existe** em candidate algum.

| predicado | tipo | efeito |
|---|---|---|
| `EV-RESOLVABILITY`: `evidence_refs ⊆ evidence_ids(pkg)` | **REJEICAO** | ref quebrada → `REJECTED_STRUCTURAL` / `EVIDENCE_REF_QUEBRADA`; **conjunto vazio satisfaz vacuamente** |
| `EV-POPULATION`: refs nao vazias | **MEDIDA** | `inherited_defect = EVIDENCE_REFS_EMPTY_INHERITED_FROM_R3_PACKAGING` |
| `CLAIM-RESOLVABILITY`: `claim_refs ⊆ sealed_claim_ids(pkg)` | **REJEICAO** | campo ausente → `NOT_APPLICABLE`, nunca `PASS` silencioso |

**Limitacao pre-declarada:** `EVIDENCE_LASTRO_NON_EMPTINESS_NOT_TESTABLE_ON_R3_CORPUS`.
Esta rodada prova que ref **quebrada** rejeita e ref **valida** admite; **nao** prova
comportamento sobre corpus com lastro populado, porque tal corpus nao existe.

## 8. CANARIOS `CA1–CA9` — MATRIZ DE EXPECTATIVA, DECLARADA AGORA

| canario | fixture | esperado |
|---|---|---|
| `CA1` | rule valida com `precedence = UNDEFINED` | `ADMITTED` + defeito `PRECEDENCE_UNDEFINED` preservado |
| `CA2` | workflow valido de **um** passo | `ADMITTED` + defeito `PASSO_UNICO` preservado |
| `CA3` | workflow **sem** steps | `REJECTED_STRUCTURAL` |
| `CA4` | workflow com order duplicada/invalida | `REJECTED_STRUCTURAL` |
| `CA5` | candidate com `evidence_ref` inexistente | `REJECTED_STRUCTURAL` |
| `CA5b` | candidate com `claim_ref` inexistente | `REJECTED_STRUCTURAL` |
| `CA5c` | candidate com `claim_ref` valida | `ADMITTED` |
| `CA6` | anti-pattern valido | `ADMITTED` |
| `CA7` | anti-pattern com `evidence_ref` quebrada | `REJECTED_STRUCTURAL` |
| `CA8` | candidate admitido | `PRESENT_AND_CONSUMABLE` no conjunto consumivel da Fusion |
| `CA9` | candidate rejeitado | `NOT_CONSUMABLE` — pode existir em auditoria/provenance, nunca como knowledge admitido |

Qualquer `CA` que falhe → `PILOT_MS_000B_ROUND_4_INVALID` e PARA, antes dos pacotes reais.

## 9. SEMANTICA DE CONSUMO DA FUSION

Cada Fusion Package R4 carrega `admitted_candidate_refs[]`, todos qualificados
`(source_package_hash, local_id)`. **Somente `ADMITTED` entra.** `rejected_candidate_refs`
existe para auditabilidade, no campo `rejected_candidate_refs_NOT_CONSUMABLE`, estado
inequivoco `NOT_CONSUMABLE`.

Populacoes materializadas, distintas dos inputs: `fusion/rules[]` · `fusion/workflows[]` ·
`fusion/anti_patterns[]`. **Nenhum candidate rejeitado pode aparecer nelas.** Precedence
**nao** e resolvida nesta rodada.

## 10. METODOLOGIA DO TRANSPORTE — TEM DE PODER FALHAR

**Origem:** objeto lido de `SOURCE-LOCAL-CANDIDATES.json` **dentro do pacote selado**.
**Destino:** objeto **relido** de `out/fusion/fusion-package-R4-{RUN}.json` **ja gravado em
disco**. Dois arquivos, duas leituras. **Nunca duas referencias ao mesmo objeto em
memoria** — que foi o achado `D-4` da Round 3.

Comparar `source_structure_hash` vs `fusion_structure_hash` sobre a **mesma projecao
canonica** aplicada aos dois lados, cobrindo id/ref de origem · order · steps · condicoes ·
excecoes · `evidence_refs` · `claim_refs`. **PASS = hashes iguais** quando nenhuma
transformacao foi declarada. **Nenhuma transformacao e esperada nesta rodada**; se houver,
exige Decision/Trace especifico.

## 11. CANARIOS REAIS NO CORPUS

Alem dos sinteticos: **todos** os workflows reais de um passo e **todas** as rules reais
estruturalmente validas com `precedence: UNDEFINED` devem ser `ADMITTED`, aparecer na
populacao da Fusion, com objetos de origem e destino distintos, estrutura preservada e
hash conferindo — um passo continua um passo, `UNDEFINED` continua `UNDEFINED`, sem
adjudicacao. **Quantidade nao e threshold.** Nao ha contagem esperada declarada.

## 12. BLOCAGEM E RELACOES

`NOT_APPLIED_IN_ROUND_4`. A travessia candidate→fusion nao depende de blocagem de claims, e
claim blocking nao mede candidate admission.

## 13. FORMULA DE `fusion_id`

```
fusion_id = sha256(canon({
   source_package_hashes, fusion_config_hash, candidate_admission_report_hash,
   admitted_candidate_set_hash, outputs_hash }))
```

**`mtx_policy_hash` e PROIBIDO** como input identitario. A `CANDIDATE-ADMISSION-POLICY`
entra **via `FUSION-CONFIG`**, por ser configuracao estrutural da propria Fusion — e isso
**nao** viola `I26`.

Canario `I26`: **A** mesmos pacotes + mesmo config → mesmo `fusion_id`; **B** policy
diferente → config novo → `fusion_id` novo, **esperado e permitido**; **C** injetar
`mtx_policy_hash` como input identitario → **`FAIL`**.

## 14. `PASS` / `FAIL` / `INVALID`

`INVALID` precede `FAIL`: instrumento quebrado nao reprova produto.

- **`INVALID`** — qualquer `CA` ou canario `I26` falha · qualquer chamada de modelo ·
  gate de abertura falha.
- **`FAIL`** — Source Package alterado · `PRECEDENCE_UNDEFINED` ou `PASSO_UNICO` sozinhos
  rejeitando · candidate estruturalmente invalido admitido · admitido nao materializado ·
  rejeitado consumido · hash de transporte divergindo sem transformacao declarada ·
  `mtx_policy_hash` presente em `fusion_id`.
- **`PASS`** — todos os portoes do item 25 do bloco.

## 15. ZERO CHAMADAS DE MODELO

Nenhum cliente Anthropic/OpenAI/outro e instanciado. `MODEL_CALLS = 0` no runner, verificado
como portao. Qualquer chamada → `PILOT_MS_000B_ROUND_4_INVALID`.

## 16. TRAVAS

Mesmo em `PASS`: nao iniciar MS-001 · nao usar marketing corpus · nao implementar
Operationalization · nao criar Operational Package · nao implementar Router · nao criar
Skill Pack · nao alterar o Architecture Freeze · nao resolver N1–N9 · nao modificar R1/R2/R3.
Em `PASS` declara-se **somente** `PILOT_MS_000B_ROUND_4_PASS` e
`CANDIDATE_TO_FUSION_LAYER = QUALIFIED_IN_ROUND_4`. **`MS_000B_ACCEPTED` nao.**
