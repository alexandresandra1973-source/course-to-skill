# OPENING RECORD — `PILOT-MS-001A` — SOURCE PACKAGE COMPILATION

**Selado e pushed ANTES da primeira chamada de modelo.** Data: 2026-08-30.
Depois deste push **nenhuma metodologia muda**. `HEAD` de partida: `418b99fc8a265f4adaf4dc477213b09a8965503d`.

Estado de entrada: `MS_001A_READY_FOR_OPENING_RECORD`.

## 1. CORPUS — CONGELADO, READ-ONLY

| `source_id` | `SOURCE_CONTENT_HASH` | vídeo | autoridade |
|---|---|---|---|
| `MS001-SRC-B` | `2a6ab098868e0714e5d4bc5cebb8018216d78f0243ee890b2c531516fbda7862` | `dtAoZYMEzcM` | Anderson Adelino |
| `MS001-SRC-C` | `ed967fae27146d9aa9cc45769672f751d8eb199bc6ed7564bbb5fdb4a226fab7` | `NvrBpnbNfv4` | Guilherme Lazarotto |

`SOURCE-MANIFEST-MS-001.yaml`: `790fe0e72a784a7f8b695345d68f850d6970844675c0bb51fff2b3dba3a5cbc0`
`FROZEN-SLICES.json`: `0460dd5fd0107fac5bc073c160b92b137ee17b2de9d599cae3b681fc3f7d244e`
`SELECTION-ALGORITHM.txt`: `1d974b5342125d77ac130c444a979cdc692e1ffda76308f0b3ac48fe471509f7`

**Zero reaquisição de YouTube.** `K11`: qualquer caption com bytes diferentes → `MS_001A_INVALID`.

### As seis slices

| `slice_id` | source | janela | segmentos | `slice_text_sha256` |
|---|---|---|---|---|
| `SL-B-01` | `MS001-SRC-B` | 0–90 s | 0..41 | `60d5da35e07209a053dbbb8cd91b7a6c6d64d6fb7f0c81be097d71fa50039113` |
| `SL-B-02` | `MS001-SRC-B` | 150–240 s | 71..112 | `ac37fa83349fd1c4509b9fc478be5a223047a90f76a339ff3157dfea5089c1a7` |
| `SL-B-03` | `MS001-SRC-B` | 270–360 s | 128..169 | `d03eaa3a6806cf7024d95b7de1edfc1a46698596f7dac767aabdacfb57df7731` |
| `SL-C-01` | `MS001-SRC-C` | 30–120 s | 15..59 | `bfbab44cb3c251bc0d946b1f6b95808445edfaeea11f412a04160663b0adef28` |
| `SL-C-02` | `MS001-SRC-C` | 120–210 s | 60..96 | `5918fe7cd59e180ada88d406529dcfad75bb3b01465cdca8010aeec817e3c36a` |
| `SL-C-03` | `MS001-SRC-C` | 210–300 s | 97..136 | `a7157b09428082b900dc5846045b7c9e88ca9c947226e0f3b4525247be9081bb` |

## 2. INDEPENDÊNCIA

`DECLARED_INDEPENDENT` por `DR-MS-001-INDEP-001`
(`00976ae7f7c5020a2a8bf0202e2184f7c37896e4accfee336414f4fb4e58baeb`), escopo estrito ao PILOT-MS-001 e aos dois
artefatos acima. Se os hashes mudarem, **a declaração não se transfere**.

## 3. EVIDENCE — CONSTRUÇÃO MECÂNICA, ZERO MODELO

**`N = 4` segmentos contíguos**, não sobrepostos; grupo final com menos de **2** segmentos é
fundido no anterior. Escolha por medição: 6,75 evidences por 1.000 chars, dentro da banda
histórica (P003 6,67 · P004 6,83).

Resultado: **33 Evidence em B** (11+11+11) e **30 em C** (11+9+10). Cada chamada recebe o
**catálogo fechado da sua slice** e nada mais.

Algoritmo em `lib/builders.py` (`38763c6e6cef5afc7bc2e3aa380463ca121283ab2a24648fc5fe3bff41d7ce3c`).

## 4. EXTRAÇÃO

| artefato | sha256 |
|---|---|
| `instruments/EXTRACTION-PROMPT-v1.txt` | `2e4e316859fee250936a6c5dfdc12821396dc80e0f46eafe7392f8817acb83c5` |
| `instruments/EXTRACTION-SCHEMA-v1.json` | `d100354c7ecc300e87f5a059970eea10903789137569eecb49e8da3bbddd2f24` |
| `lib/validate.py` | `0faed47838971cc70d23ac307e39559abef3d0cc97d08ae4964c2a0f87fe4a32` |

Modelo: `claude-opus-5` · `thinking = {"type":"disabled"}` · `max_tokens = 8000` ·
`temperature` omitida · SDK `anthropic 0.121.0`.

Contrato do bundle: `raw_claims` e `raw_candidates` no **mesmo output**, ambos com
`evidence_refs` **não vazias** e restritas ao catálogo da chamada. Kinds autorizados:
`rule_candidate` · `workflow_candidate` · `anti_pattern_candidate`. Kind desconhecido →
rejeição.

## 5. IDENTIDADE — `IDENTITY != PROVENANCE`

`instruments/ID-DERIVATION-v3.txt` (`9687f75e85acd23f153ac5b37cb0f70bdfbbd0a8678c6b91b073dbe04e5e915d`) ·
`lib/identity.py` (`ede48d1f1458f82e2f697af9a221a78c054623028eb441f673d382cc1a323d2b`).

```
claim_semantic_key       = sha256(canon({source_id, normalized_text, source_language, qualifiers}))
candidate_structural_key = sha256(canon({source_id, entity_kind, structure_canon}))
```

**Não entram na identidade:** `evidence_refs` · claim refs · `entailed_by` · `entail_why` ·
judgment · `cross_source_eligibility` · `merged_from` · `defects` · ordem de emissão · slice.
**`precedence` entra** na rule por ser campo estrutural.

**Dedup ANTES do id final**, dentro de cada source, com união ordenada de `evidence_refs`,
dependências e defeitos, e `merged_from` preservado. **Nenhum dedup cross-source.**
Prefixos: `CL-` · `R-` · `WF-` · `AP-` · `S-`.

Identidade global: `(source_package_hash, entity_kind, local_id)`. **Nunca indexar só por
`local_id`.**

Canários `DI1`–`DI7` já executados e PASS.

## 6. ENTAILMENT — INSTRUMENTO INDEPENDENTE

| artefato | sha256 |
|---|---|
| `instruments/ENTAILMENT-PROMPT-v1.txt` | `70bd6dacb792e872feb8846e1699efc047c8b91ab16b2682a78f781dd6ee989a` |
| `instruments/ENTAILMENT-SCHEMA-v2.json` | `b31d70083f300b1e8e05b13849720eb42d7f993bd539ab029db305f5fdaf4c07` |
| `instruments/JUDGE-CONTROLS-JE.txt` | `5593dd0c0b0762d1491f38830aa3882f5871d433c1593f05d77242dd2b2348b3` |

**Isolamento:** o juiz recebe, por Claim, apenas `claim_id`, texto, qualifiers e **somente as
Evidence que aquela Claim referenciou**. Não vê a outra source, candidates, Fusion, MTX
policy nem taxonomia cross-source.

`evidence_refs_checked` tem de ser **subconjunto exato** das refs declaradas —
superset é `E19_JUDGE_ADDED_EVIDENCE`.

Controles `JE1` `ENTAILED` · `JE2` `NOT_ENTAILED` (generalização) · `JE3` `NOT_ENTAILED`
(fora do assunto) · `JE4` `INDETERMINATE`. Provam `NOT_ENTAILED != INDETERMINATE`.

**Somente `ENTAILED` entra no membro `CLAIMS`, com `status: SEALED`.** `NOT_ENTAILED` e
`INDETERMINATE` ficam auditáveis fora dele. Nada é apagado.

## 7. ELEGIBILIDADE DE CANDIDATE

`instruments/PROVENANCE-STATES-v2.txt` (`fec68ddd5baef097e8044106596174616516b10a271373216b1701f3b82345b6`) ·
`lib/gate.py` (`8d6e037e6735a73fad74a4ecd1f274c1e6b5090c0da65f3e94994e24b4baea17`).

`evidence_refs = []` → `E05` na **validação de schema**, antes do gate. **Nunca** vira
`NOT_ELIGIBLE` pelo caminho válido.

`NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION` = candidate estruturalmente válido e ancorado cuja
Claim requerida **não** foi selada. Permanece no package; **não** gera ref quebrada.

`INVALID_PROVENANCE` = defeito estrutural real → **Source Package FAIL**.

`CP1`–`CP8` já executados e PASS.

## 8. PLANO DE CHAMADAS

```
call 1     EXTRACTOR MODEL CONTROL       EC1-EC6
call 2     ENTAILMENT JUDGE CONTROL      JE1-JE4
call 3     extraction SL-B-01
call 4     extraction SL-B-02
call 5     extraction SL-B-03
call 6     extraction SL-C-01
call 7     extraction SL-C-02
call 8     extraction SL-C-03
call 9     entailment MS001-SRC-B
call 10    entailment MS001-SRC-C

PLANNED = 10 · HARD_CAP = 10 · RETRY = 0 · executed_calls <= 10
```

**8, 9 e 10 são válidas. SOMENTE a chamada 11 é `MS_001A_INVALID`.** Término antecipado por
`INVALID`/`FAIL` **não** exige queimar as restantes.

`ZERO_RAW_CLAIMS` numa source → `SOURCE_PACKAGE_FAIL`, **sem** gastar a call de entailment.

A **call 1 é também a verificação de resolução de modelo**: `resolved_model != claude-opus-5`
→ `MS_001A_INSTRUMENT_INVALID`. Nenhuma call de resolução separada.

## 9. PIPELINE — ORDEM LITERAL

```
Frozen L0 -> Controlled Slice ARTIFACTS -> SOURCE_ANCHORS -> EVIDENCE
-> Extraction Calls -> Raw outputs persisted
-> Claim Identity Finalization -> Entailment Judge -> SEALED CLAIM Selection
-> Candidate Finalization -> Candidate Provenance/Eligibility Gate
-> Local Coherence -> Compile Trace final -> Required Members -> Completeness
-> Member Manifest -> SOURCE_PACKAGE_HASH -> SEAL-RECORD -> External Seal Registry
```

## 10. MEMBROS E SELO

11 membros literais + `TOOLCHAIN.json`, com `L0 = L0/RAW-CAPTION.json`.
`lib/package.py` (`59f0096b8fe5423a934e4a7c7b10c29382ecb57acfff4fd75365375917b7d3ca`). Selo reusa o contrato aceito e o
`seal_verifier.py` do MS-000A **sem alteração**; `producer.{toolchain_path,toolchain_sha256}`
na forma literal aceita. Dry-run 8/8 já executado com fixtures sintéticos.

## 11. LOCAL COHERENCE

Unicidade tipada · resolução de refs · candidate provenance · estrutura de workflow · ordem
de steps · membros · declaration space · **`NO_CROSS_SOURCE_REF_ALLOWED`**: qualquer ref de
B para C ou de C para B → **FAIL**.

## 12. PASS / FAIL / INVALID

**`PASS`** — controles mecânicos PASS · EC PASS · JE PASS · corpus intacto · ≤10 chamadas ·
≥1 SEALED Claim em B e em C · `INVALID_PROVENANCE == 0` · dois packages completos · dois
selos PASS · zero refs/relações cross-source · raw outputs preservados · Compile Trace completo.

**`FAIL`** — instrumento válido, produto viola contrato.

**`INVALID`** — EC ou JE falha · `resolved_model` divergente · schema/tooling defeituoso ·
chamada 11 · hash de corpus diverge · instrumento alterado após este Opening Record ·
`ENTAILMENT_OUTPUT_INVALID`.

**Nenhum threshold de taxa** é fixado, nem para claims nem para candidates.
**Nenhum threshold de blocker** entra aqui — `K13`.

## 13. KILLS

`K11` corpus alterado · `K12` provenance retrofitada (verificada por ordem de eventos no
Compile Trace) · `K13` threshold de blocker escolhido com saída do juiz · `K14` packages
regenerados entre runs · `K15` ref cross-source sem identidade tipada.

## 14. TRAVAS

Mesmo em `PASS`: não calibrar blocker · não executar blocker · não iniciar MS-001B · não
julgar relações cross-source · não produzir Fusion Package · não usar MTX policy · não usar
Source A · zero escritas no Drive.
