# PILOT-MS-000B / ROUND 3 — VEREDITO

**Classificação:** **`PILOT_MS_000B_PASS`** · **22/22 portões** · **10/10 chamadas, cap 10**
**Opening Record:** `9aa050b2e01121441fbbea3da4ed6e7d3f8b389b423ca9695f3e10b217a1b302`
**Round 1** `INVALID_INSTRUMENT` e **Round 2** `NON_QUALIFYING` — preservadas, **não reutilizadas**.

> Esta rodada não repetiu um PASS. **Testou pela primeira vez o `SOURCE PACKAGE` que o
> Architecture Freeze realmente congelou** — com os 11 membros, selo e as três identidades.

---

## 1. SEIS PACOTES REAIS, SELADOS E COMPLETOS

| run/pkg | `SOURCE_ID` | `SOURCE_PACKAGE_HASH` | membros | completude | selo | coerência |
|---|---|---|---|---|---|---|
| RUN-1/A | `MS000B-SRC-P002-CH12` | `d5fd5dad81cfe5d1ba…` | 12 | PASS | PASS | OK |
| RUN-1/B | `MS000B-SRC-P002-CH13` | `c66b269533cedcabb8…` | 12 | PASS | PASS | OK |
| RUN-2/A | `MS000B-SRC-P002-CH12` | `70c11cfbc96f4e0382…` | 12 | PASS | PASS | OK |
| RUN-2/B | `MS000B-SRC-P002-CH13` | `9ba68de595573c24b4…` | 12 | PASS | PASS | OK |
| RUN-3/A | `MS000B-SRC-P002-CH12` | `5133d40dd62c7c0f3a…` | 12 | PASS | PASS | OK |
| RUN-3/B | `MS000B-SRC-P002-CH13` | `c9ce7f61760a05cea8…` | 12 | PASS | PASS | OK |

**6 package hashes distintos de 6** — e isso é **consequência dos membros**, não decreto:
as claims e o compile-trace diferem entre runs, logo os manifestos diferem.
Em todos, o hash recomputado **confere** com o declarado no `SEAL-RECORD`.

**As três identidades comportaram-se como projetado:**
`SOURCE_ID` — **2 distintos**, um por capítulo, estáveis nos três runs.
`SOURCE_CONTENT_HASH` — **2 distintos**, estáveis nos três runs.
`SOURCE_PACKAGE_HASH` — **6 distintos**, um por compilação.

## 2. `CLAIMS`, `CANDIDATES` e `COMPILE-TRACE` são membros e estão cobertos

`CLAIMS.jsonl`, `SOURCE-LOCAL-CANDIDATES.json` e `COMPILE-TRACE.jsonl` presentes no
`member_manifest` de **6/6** pacotes. Era o defeito central da Round 2.

## 3. `SOURCE-PROFILE` ESTÁVEL — e é o que separa as identidades

| pacote | sha do profile | distintos entre runs |
|---|---|---|
| A | `a95ac6b90e681447…` | **1** |
| B | `1091597926cc2577…` | **1** |

Zero campos de `model`/`prompt_version`/`judge_version`/`thinking`/`partition` no profile —
todos migraram para o `COMPILE-TRACE`. Na Round 2 o profile mudava só porque o prompt mudava.

## 4. TIMESTAMP NÃO É IDENTIDADE — verificado

`trace_membro_sem_timestamp: true` — nenhum `COMPILE-TRACE` membro carrega timestamp.
`oplog_tem_timestamp: true` — os 10 timestamps vivem em `OPERATIONAL-RUN-LOG.jsonl`, **fora
de todo pacote e fora do canonical member set**.

## 5. `PACKAGE-KILL` 1–5 — todos verificados sobre os pacotes reais

| kill | resultado |
|---|---|
| **PK-1** claim membro mutada | hash **muda** e selo **falha** (`MEMBER_HASH_MISMATCH` + `DOES_NOT_VALIDATE_IN_PLACE`) |
| **PK-2** candidate membro mutado | idem |
| **PK-3** compile-trace mutado | idem |
| **PK-4** pacote incompleto atravessa o gate | **não ocorreu** — 6/6 `PASS` no completeness gate |
| **PK-5** objeto sem selo consumido pela Fusion | **não ocorreu** — a Fusion só consumiu pacotes com selo `PASS` |

## 6. CANDIDATE ADMISSION — primeira medição real

Ocorre **depois** do selo e **não altera o pacote**: `package_unchanged: true` em 6/6,
verificado por recomputação do hash antes e depois.

| pacote | recebidos | admitidos | rejeitados | rule / workflow / anti-pattern |
|---|---|---|---|---|
| A (cap 12) | **23** | **8** | **15** | 13 / 6 / 4 |
| B (cap 13) | **26** | **7** | **19** | 19 / 4 / 3 |

**Motivos de rejeição — todos defeitos herdados, não juízo de qualidade:**
`PRECEDENCE_UNDEFINED_DEFEITO_HERDADO` **13** (A) e **17** (B) ·
`PASSO_UNICO_DEFEITO_HERDADO` **2** em cada.

> **Nenhum threshold foi inventado.** Isto é **baseline** — a v1 §7.4 diz que os limiares do
> portão saem **medidos** deste piloto. O número mede o **corpus herdado**: os candidatos
> reprovam porque carregam `precedence: UNDEFINED` e workflows de passo único, os mesmos
> defeitos que A2 e A9 mediram nos pilotos históricos.

Idêntico nos três runs, como esperado — os candidatos são derivados deterministicamente.

## 7. CLAIMS E ENTAILMENT

| run | raw | rejeitadas | seladas | `ENTAILED` | `NOT_ENTAILED` | `INDETERMINATE` |
|---|---|---|---|---|---|---|
| RUN-1 | 81 | 0 | 81 | 81 | 0 | 0 |
| RUN-2 | 83 | 0 | 83 | 83 | 0 | 0 |
| RUN-3 | 80 | 0 | 80 | 80 | 0 | 0 |

**244/244 `ENTAILED`** — e o juiz **provou discriminar antes**, com os 5 controles
(`ENTAILED`, `NOT_ENTAILED`, `INDETERMINATE` e as duas travessias cross-source).
Vale a mesma ressalva da Round 2: mede **este** gerador, com **este** prompt.

**Proveniência: 244/244 = 100%** resolvendo `claim → evidence → anchor → slice → CUT → FULL`,
com toda referência interna em `ref_scope: SELF`.

## 8. VARIÂNCIA — KILL-2

81 / 83 / 80 · **máx/mín = 1,0375× ≤ 1,5×**.
Sobreposição textual: `R1∩R2` **10** · `R1∩R3` **22** · `R2∩R3` **10** · **núcleo comum aos
três: 7**.

> Diferente da Round 2, onde o núcleo comum era **0**. Sete claims idênticas normalizadas
> sobrevivem aos três runs. Ainda é pouco para sustentar comparação entre fontes no
> `MS-001`, mas não é mais zero — e a diferença é informação, não ruído.

## 9. BLOCAGEM, RELAÇÕES, WORKFLOW, ISOLAMENTO

| run | pares possíveis | sobreviventes | redução | controles | `IDENTICAL` |
|---|---|---|---|---|---|
| RUN-1 | 1.634 | 144 | 91,19% | **2/2** | 0 |
| RUN-2 | 1.722 | 132 | 92,33% | **2/2** | 0 |
| RUN-3 | 1.596 | 140 | 91,23% | **2/2** | 0 |

**Workflow preservado:** A 6 workflows / 19 steps · B 4 / 23 — estrutura idêntica na
travessia, nos três runs. **Isolamento:** 0 claims no pacote errado, controles `JC-CROSS`
corretos. Relações só `IDENTICAL` mecânica (`D15`); `UNRELATED` como default.

## 10. FUSION PACKAGE

Um por run, com os dois `source_package_hash` participantes, seals verificados,
`CANDIDATE-ADMISSION-REPORT`, blocking, workflow transportado, `PROVENANCE-LEDGER` e
`FUSION-TRACE`. `fusion_id` **sem `mtx_policy_hash`**.
`fusion_id`: RUN-1 `a2d31141…` · RUN-2 `0a747edd…` · RUN-3 `efdd7084…`.
**Nenhum `SEAL-RECORD` de Fusion foi inventado** — o freeze não o exige.
**Zero Operational Package. Zero Skill Pack.**

## 11. ORÇAMENTO E KILL HERDADOS

**10 de 10 chamadas.** Margem zero respeitada, zero retries.
`KILL-1` camada selada byte-idêntica · `KILL-2` 1,0375× · `KILL-3` 244/244.

## 12. LIMITAÇÕES DECLARADAS

1. **`SEMANTIC_COHERENCE_NOT_EVALUATED_IN_MS_000B`** — o `LOCAL-COHERENCE-REPORT` é
   **mecânico**. Isto **não** é "semantic coherence PASS".
2. **244/244 `ENTAILED`** mede este gerador com este prompt; não estabelece a taxa de um
   gerador não restringido.
3. **`SOURCE = chapter` continua exceção de piloto**, não contrato de produção.
4. **Núcleo comum de 7 claims** entre runs ainda é baixo para o que o `MS-001` precisará.
