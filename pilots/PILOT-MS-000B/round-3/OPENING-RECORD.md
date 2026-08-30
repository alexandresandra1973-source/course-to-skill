# PILOT-MS-000B / ROUND 3 — OPENING RECORD

**Status:** `DECLARED_BEFORE_FIRST_EVALUATIVE_MODEL_CALL_OF_ROUND_3`
**Data:** 2026-08-30 · **Máquina:** `LenovoAIO27ARR9`, ext4
**HEAD ao selar:** `cd5cea34faae1f5cf1e3c9f66c19dd65381b256e`
**Architecture Freeze:** `6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b` · selo `f35016cb…`
**Decisões:** `DR-MS-000A-001` · `DR-MS-000B-001` · `DR-MS-000B-R1-002` (errata) · `DR-MS-000B-R2-001` · `DR-MS-000B-R3-001`

> **O objetivo desta rodada não é repetir um PASS.** É testar pela primeira vez o
> `SOURCE PACKAGE` que o Architecture Freeze realmente congelou.
> **Depois deste push, nenhuma metodologia muda.** Round 1 e Round 2 preservadas
> byte-a-byte; nenhum resultado avaliativo delas é transportado.

---

## 1. CORPUS E IDENTIDADES

| nível | sha256 |
|---|---|
| `FULL L0` | `43b58271feb0a1d518ae6f81ab29836eb9c7f2bec5eb02e53f70c7bd1eb514ed` |
| `CUT L0` | `85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29` |
| `EVIDENCE.jsonl` P002 | `64853f7ac06a470f09333a80469b38e443ea5ce7aa3aee2e116ea1877059abfd` |

| pacote | `SOURCE_ID` | `SOURCE_CONTENT_HASH` | cap | evidências |
|---|---|---|---|---|
| A | `MS000B-SRC-P002-CH12` | `6d9e718cf5dbb08811f0d73673a13e83084d79457a506bc523d81e6b32de33b7` | 12 | 44 |
| B | `MS000B-SRC-P002-CH13` | `2768b11c40836371…` (recomputado no ato) | 13 | 56 |

**`SOURCE = chapter` é `PILOT_MS_000B_ONLY`** e não vira contrato de produção.
**`source_independence = KNOWN_DEPENDENT`** nos dois.

### As três identidades, distintas

| identidade | muda quando | estável entre runs? |
|---|---|---|
| **`SOURCE_ID`** | a fonte lógica muda | **sim, sempre** |
| **`SOURCE_CONTENT_HASH`** | os bytes do slice mudam | **sim** |
| **`SOURCE_PACKAGE_HASH`** | **qualquer** membro identity-relevant muda | **não, e não deve ser** |

**Nunca fabricar diferença de hash artificialmente.**

## 2. REFERÊNCIAS INTERNAS — `SELF` — e a circularidade resolvida

Dentro do pacote, toda referência é:

```json
{"ref_scope": "SELF", "local_id": "EV-0001"}
```

**`SELF`** significa *resolver contra o Source Package que contém este objeto*.
**Nenhum membro contém o `source_package_hash` do conjunto que o contém** — é isso que
elimina a circularidade.

Depois de selado, toda referência que **atravessa a fronteira** é materializada como
`(source_package_hash, local_id)`.

**Regras:** `local_id` nu **cross-package** = `FAIL` · `SELF` fora do pacote de origem =
`FAIL` · a Fusion nunca recebe referência ambígua · nenhum membro precisa conhecer
antecipadamente o hash do conjunto que o contém.

> **Interpretação registrada de `I4`/`E6`:** referências **internas** são relativas ao
> namespace `SELF`; referências **entre produtos/pacotes** são qualificadas pelo package hash.

## 3. TIMESTAMP NÃO É IDENTIDADE

O **`COMPILE-TRACE` membro** carrega só o identity-relevant: run/source lógicos ·
`input_sha256` · **partição** · `prompt_version` · modelo requisitado e **resolvido** ·
`thinking` · `max_tokens` · `output_sha256` · `stop_reason` · tokens.

Timestamps e informação puramente operacional vão para **`out/OPERATIONAL-RUN-LOG.jsonl`**,
**fora de todo pacote** e **fora do canonical member set**.

> **Dois pacotes byte-equivalentes não podem ter hashes diferentes só por terem rodado em
> segundos distintos.**

## 4. OS 11 MEMBROS OBRIGATÓRIOS — nomenclatura literal da v1 §4.1

| # | membro | caminho |
|---|---|---|
| 1 | `SOURCE-PROFILE` | `SOURCE-PROFILE.json` |
| 2 | `L0` | `L0/CHAPTER-SLICE.txt` |
| 3 | `ARTIFACTS` | `ARTIFACTS/ARTIFACT-INDEX.json` |
| 4 | `SOURCE_ANCHORS` | `SOURCE-ANCHORS.jsonl` |
| 5 | `EVIDENCE` | `EVIDENCE.jsonl` |
| 6 | `CLAIMS` | `CLAIMS.jsonl` |
| 7 | `SOURCE_LOCAL_CANDIDATES` | `SOURCE-LOCAL-CANDIDATES.json` |
| 8 | `COMPILE-TRACE` | `COMPILE-TRACE.jsonl` |
| 9 | `LOCAL-COHERENCE-REPORT` | `LOCAL-COHERENCE-REPORT.json` |
| 10 | `DECLARATION-SPACE-INDEX` | `DECLARATION-SPACE-INDEX.json` |
| 11 | `SEAL-RECORD` | `SEAL-RECORD.yaml` |

**`TOOLCHAIN.json`** existe porque a **condição 5** de `SEALED` exige produtor como
referência com hash próprio, não campo de texto. **Não é uma 12ª categoria de conteúdo.**

O `SOURCE-PROFILE` **não contém** `model`, `prompt_version`, `judge_version`, `thinking`,
`max_tokens`, `partition`, outputs de modelo nem timestamps.

## 5. FÓRMULA DO `SOURCE_PACKAGE_HASH`

```
Fase A  membros identity-relevant escritos no diretório do pacote
Fase B  member_manifest = [{path, sha256}] de TODOS os arquivos do diretório,
        EXCETO SEAL-RECORD.yaml, ordenado por path sob LC_ALL=C
Fase C  SOURCE_PACKAGE_HASH := sha256( canon(member_manifest) )
        canon = json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False), UTF-8
Fase D  SEAL-RECORD declara: source_id · source_content_hash · member_manifest_hash ·
        source_package_hash · producer{toolchain_path, toolchain_sha256} ·
        seal_contract_version · members[]
Fase E  seal_record_hash registrado em packages/EXTERNAL-SEAL-REGISTRY.txt,
        FORA de todos os diretórios selados
```

`member_manifest_hash ≡ SOURCE_PACKAGE_HASH` (mesmo valor). `seal_record_hash` difere por
construção — o selo contém mais que o manifesto. **Auto-referência evitada:** o
`SEAL-RECORD` não consta de `members[]` (condição 7).

## 6. DOIS INSTRUMENTOS SEPARADOS

**`PACKAGE COMPLETENESS GATE`** — confronta o pacote contra os 11 obrigatórios. Código:
**`REQUIRED_MEMBER_MISSING`**.
**`SEAL VERIFIER`** — `seal_verifier.py` do MS-000A, **sem alteração**.

> **O selo NÃO detecta membro que nunca entrou no manifesto.** Provado em `PC5`–`PC7`: com
> `CLAIMS` ausente, o selo isolado diz **`PASS`**. Por isso os dois instrumentos existem.

## 7. `PC1`–`PC8` — todos passam **antes** da primeira chamada

| # | mutação | obrigatório |
|---|---|---|
| `PC1` | alterar `CLAIMS` membro | hash muda **e** selo falha (`MEMBER_HASH_MISMATCH` + `DOES_NOT_VALIDATE_IN_PLACE`) |
| `PC2` | alterar `SOURCE_LOCAL_CANDIDATES` | idem |
| `PC3` | alterar `COMPILE-TRACE` identity-relevant | idem **+ `SOURCE_ID` permanece igual** |
| `PC4` | model/prompt/judge fora do profile | `SOURCE-PROFILE` **byte-idêntico entre runs** |
| `PC5` | sem `CLAIMS` | `REQUIRED_MEMBER_MISSING` no completeness gate |
| `PC6` | sem `SOURCE_LOCAL_CANDIDATES` | idem |
| `PC7` | sem `COMPILE-TRACE` | idem |
| `PC8` | sem `SEAL-RECORD` | **estado pré-declarado: `INVALID_PACKAGE`** — verifier devolve `INVALID`/`SEAL_RECORD_MISSING`. **Não é defeito semântico da fonte** |

## 8. INSTRUMENTOS REVALIDADOS ANTES DE ABRIR

tokenizer **9/9** · consolidator **7/7** (`INVALID` precede `FAIL`) · `PC1`–`PC8` **8/8** ·
judge controls **5/5** (consome **1** das 10 chamadas) · isolation controls `ISO-A`/`ISO-B` ·
blocker controls `BLK-CTRL-01/02`. **Qualquer falha ⇒ `PILOT_MS_000B_ROUND_3_INVALID` e PARA.**

## 9. MODELO, PARTIÇÃO E ORÇAMENTO

`claude-opus-5` · `THINKING = {"type":"disabled"}` · `max_tokens` 8000 ·
`prompt_version` `ms000b-r3-claimgen-v1` · `judge_version` `ms000b-r3-entail-v1`
*(subida de versão estritamente necessária ao novo Package Contract, pré-declarada aqui)*.

**Partição idêntica à aprovada:** 1 chamada por `(source, run)` na geração; 1 por run no
entailment; **0** nas relações (só `IDENTICAL` mecânica, `D15`).

| etapa | chamadas |
|---|---|
| judge controls | **1** |
| geração — 2 sources × 3 runs | **6** |
| entailment — 1 por run | **3** |
| **TOTAL = HARD CAP** | **10** |

> **Margem zero.** Nenhuma chamada extra depois deste record.
> **Erro ou transiente que exija retry ⇒ `PILOT_MS_000B_ROUND_3_INVALID`.** Não se excede o cap.

## 10. LIFECYCLE — o selo é o ÚLTIMO passo

```
por RUN × SOURCE:
  source bytes → anchors/evidence → claim generation → entailment → SEALED_CLAIMS
  → SOURCE_LOCAL_CANDIDATES → COMPILE-TRACE → LOCAL-COHERENCE-REPORT
  → DECLARATION-SPACE-INDEX → ARTIFACT-INDEX → COMPLETENESS → MEMBER MANIFEST
  → SOURCE_PACKAGE_HASH → SEAL

só depois, por RUN:
  candidate admission → blocking → relation detection → fusion → FUSION PACKAGE
```

**Até `3 runs × 2 sources = 6 Source Packages`.**

> **Verificação correta, não decreto:** manifestos diferentes **⇒** hashes diferentes;
> manifestos byte-idênticos **⇒** hashes iguais. **Não se exige seis hashes distintos.**

## 11. CANDIDATE ADMISSION — obrigatório, e não altera o pacote

Ocorre **depois** dos pacotes selados, **antes** de a Fusion consumir. **Nunca modifica o
Source Package** (`I20`). Por run/source: `received` · `admitted` · `rejected` ·
`rejection_reason` · `inherited_defects` · `rule/workflow/anti_pattern candidates` ·
`source_package_ref`. **Sem threshold** — v1 §7.4 diz que os limiares saem **medidos** deste
piloto. Round 3 mede **baseline**.

## 12. FUSION PACKAGE

Experimental, por run. Resolve os dois `source_package_hash` participantes · claims e
relações usadas · `CANDIDATE-ADMISSION-REPORT` · blocking · workflow transportado ·
`PROVENANCE-LEDGER` · `FUSION-TRACE` · estado de conflito quando aplicável.
`fusion_id` **sem `mtx_policy_hash`** (`D13`, `I26`).
**O freeze não exige `SEAL-RECORD` de Fusion Package — não se inventa um.**
**Zero Operational Package. Zero Skill Pack.**

## 13. CRITÉRIOS

**`PASS`** exige, além dos critérios anteriores: ≤ 6 pacotes corretos · todos **completos** ·
`CLAIMS`, `CANDIDATES` e `COMPILE-TRACE` **membros e cobertos** pelo package hash ·
`SOURCE-PROFILE` estável entre runs · timestamps **não** alteram identidade · todos com
`SEAL-RECORD` válido · registro externo resolve · candidate admission **realmente medido** ·
Fusion consome **apenas** pacotes válidos · proveniência resolve · workflows preservados ·
controles preservados · **≤ 10 chamadas** · nenhum KILL.

**KILL de pacote — qualquer um ⇒ parada:**
`PACKAGE-KILL-1` claim membro muda sem mudar/invalidar identidade ·
`PACKAGE-KILL-2` idem para candidate · `PACKAGE-KILL-3` idem para compile-trace ·
`PACKAGE-KILL-4` pacote incompleto atravessa o completeness gate ·
`PACKAGE-KILL-5` objeto sem `SEAL-RECORD` consumido pela Fusion como pacote válido.

**KILL herdados:** `KILL-1` camada selada byte-idêntica · `KILL-2` variância ≤ **1,5×** ·
`KILL-3` 100% das `SEALED_CLAIMS` com `ENTAILED_BY = ENTAILED`.

**`ROUND_3_INVALID`:** controle pré-avaliação falha · instrumento incapaz de medir o que
declara · config/partição divergindo entre runs · **cap excedido** · corpus/hash inesperado.

## 14. FORA DE ESCOPO

`MS-001` · corpus de marketing · Operationalization · Operational Package · Router ·
Skill Pack · produção · alteração do Architecture Freeze · `N1–N9` · o `.docx` de 6 h.
`latest wins` proibido; nenhum `SUPERSEDES` produzido.

**Regra de citação:** todo hash em relatório é **lido do artefato persistido**, nunca de
execução exploratória.
