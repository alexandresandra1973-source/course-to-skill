# `PILOT-MS-001A` — EXECUÇÃO 2 — VEREDITO

Opening Record `50e98b5a9a64108f33b04c842acc765518ec6d61863f70cad2a9ad092b6bd7c0`,
pushed em `8a299b8e783fa3e398f33ba7d9d77e1d33c9e15f` **antes da primeira chamada**.

## 1. Portões — 9/9

`corpus_intact` · `calls_within_cap` · `sealed_claims_B` · `sealed_claims_C` ·
`invalid_provenance_zero` · `both_complete` · `both_sealed` · `local_coherence` ·
`no_cross_source`.

## 2. Controles de instrumento

**`EC1`–`EC6`: 6/6.** Inclui `EC2`, a armadilha — a proposição não sustentada não foi emitida.
**`JE1`–`JE5`: 5/5**, com o par discriminante correto: `JE4` `INDETERMINATE` (a fonte declara
a questão em aberto) × `JE5` `NOT_ENTAILED` (mesmo objeto, silenciosa sobre o atributo).

`resolved_model` = `claude-opus-5` = `model_requested` nas dez chamadas.

## 3. Extração e claims

| | `MS001-SRC-B` | `MS001-SRC-C` |
|---|---|---|
| slices | `SL-B-01/02/03` | `SL-C-01/02/03` |
| raw claims | 30 | 39 |
| após dedup | 30 | 39 |
| `ENTAILED` | **30** | **36** |
| `NOT_ENTAILED` | 0 | **3** |
| `INDETERMINATE` | 0 | 0 |
| **SEALED Claims** | **30** | **36** |
| claims em audit | 0 | 3 |

Dedup não colapsou nenhum par — as 69 claims são semanticamente distintas sob a chave da
`ID-DERIVATION-v3`.

## 4. Candidates e elegibilidade

| | `MS001-SRC-B` | `MS001-SRC-C` |
|---|---|---|
| raw candidates | 8 | 12 |
| após dedup | 8 | 12 |
| `ELIGIBLE` | **8** | **8** |
| `NOT_ELIGIBLE` | 0 | **4** |
| `INVALID_PROVENANCE` | **0** | **0** |

Os quatro `NOT_ELIGIBLE` de C são **casos reais, não sintéticos**: `R-0002`, `WF-0001`,
`WF-0004` e `WF-0005` dependem de claims que voltaram `NOT_ENTAILED`, com
`claim_dependency_status = UNSATISFIED_BY_ENTAILMENT`. `WF-0005`, por exemplo, tem seis
`sealed_claim_refs` válidas e **uma** dependência não selada — permanece no package como
conhecimento source-local e **não** entra na população cross-source. **Nenhuma ref quebrada
foi criada.**

É exatamente o que `CP7`/`CP8` previram, e o que faltava na v1 do design.

## 5. Por que três claims de C não foram seladas

O juiz rejeitou claims cuja Evidence é **cortada na fronteira da auto-caption**:

- `CL-0003` — *"EV-0009 termina em 'clica em submit e agora ele vai', não afirmando que o
  sistema dá a chave"*;
- `CL-0005` — *"EV-0018 sustenta voltar ao n8n e clicar para ouvir um evento de teste, mas é
  cortada antes de dizer que se envia"*;
- `CL-0023` — *"nenhuma evidência menciona"* o atributo afirmado.

São os casos **(B)** e **(D)** da semântica congelada. As três permanecem em
`AUDIT-CLAIMS-MS001-SRC-C.json`. **Nada foi apagado.**

## 6. Source Packages

| | `pkg-B` | `pkg-C` |
|---|---|---|
| `SOURCE_PACKAGE_HASH` | `a0a73dde03410d5c744129bf8ba635815a678dbf5ce46cd124e6a31f8f67dc1f` | `5959b4ea1e8b91f570c17d61d03c4f2b6d00698801056a72a53c8e02b5a1d6c2` |
| `SEAL-RECORD` sha256 | `fe68130c51cd161ac98f5bcd1a43ddcc1e92291fd567f5323f65fb197247caae` | `672d2105a74a502bb87403b54c2e0719a99e3a33153c56e0ebb5dab864cb7563` |
| membros no manifesto | 11 | 11 |
| completude **antes** do selo | `FAIL` (falta `SEAL-RECORD`) | `FAIL` |
| completude **depois** | **`PASS`** | **`PASS`** |
| selo | **`PASS`** | **`PASS`** |

## 7. Kills de mutação — 7/7

`PK1` claim · `PK2` candidate · `PK3` `COMPILE-TRACE` identity-relevant · `PK4` evidence →
selo `FAIL` e hash muda. `PK5` membro ausente → completude `FAIL`. `PK6` sem `SEAL-RECORD` →
`INVALID`. **`PK7`: os packages reais permanecem byte-idênticos** — as mutações rodaram só
em cópias.

## 8. Contabilidade de chamadas

```
EXEC_1  calls = 2    status = INVALID
EXEC_2  calls = 10   status = PASS
CUMULATIVE_MS001A_MODEL_CALLS = 12
```

O cap de 10 é **por execução selada**. `EXEC_2` usou **10/10**, dentro do cap.

## 9. Populações para o futuro

```
CROSS_SOURCE_ELIGIBLE_CLAIM_POPULATION      B=30  C=36
CROSS_SOURCE_ELIGIBLE_CANDIDATE_POPULATION  B=8   C=8
```

**Nada foi comparado. Blocker não executado, não calibrado.**

## 10. Classificação

# `PILOT_MS_001A_PASS`

# `MS_001A_SOURCE_PACKAGES_READY_FOR_CHATGPT_REVIEW`
