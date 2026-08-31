# PILOT-MS-001 — EXEC-4 FINAL CLOSEOUT REPORT

Data: 2026-08-31 · Claude Code `2.1.251` · transporte Route B (Claude Max OAuth).

    PILOT_MS_001_PASS
    MS_001_ACCEPTED_FOR_EXPERIMENTAL_MULTI_SOURCE_FUSION
    MODEL_TRANSPORT = CLAUDE_MAX_OAUTH
    PAYG_API_USED = 0

    fusion_id = 345fd8fc6d5fbdf5d164ddd290aef3cd6a2d4c7d451e722b392cd0f024c08306

---

## 1. Gate

Duas decisões externas: DEF-1 autorizado como correção aditiva de schema; DEF-2
autorizado como correção **declarativa**, sem tocar dados. Princípio de conservadorismo
respeitado integralmente — nenhum ajuste do experimento aos resultados.

Sequência executada: correções → canários → commit 1 + push → Opening Record EXEC-4 →
commit 2 + push → **só então** as 18 chamadas semânticas. Zero chamadas de modelo antes
do segundo push, verificado (`out-ms001b-exec4` não existia).

## 2. EXEC-3 preservation

    MS_001B_EXEC_3 = INVALID
    razão primária: RELATION_SCHEMA_BATCH_ID_MISMATCH

`out-ms001b-exec3/` intacto e auditável: 86 julgamentos válidos antes da falha e
controles J1–J10 PASS. **Nenhum judgment ou control da EXEC-3 foi reutilizado** — não
entra em estabilidade, distribuição, Fusion ou veredito. A EXEC-4 é integralmente nova:
18 chamadas fresh.

## 3. DEF-1 — diagnóstico e correção

**Diagnóstico.** `RELATION-SCHEMA-v1.json` declarava
`"batch_id": {"pattern": "^BATCH-[1-4]$"}`. O schema vai **verbatim** dentro do prompt.
A partição v2 rebatizou o batch final como `BATCH-4A`/`BATCH-4B`, que não casam com
esse pattern. Na EXEC-3, o juiz obedeceu ao schema que recebeu e emitiu
`batch_id = "BATCH-4"`, com os 11 julgamentos corretos; o validador falhou fechado com
`R03_BATCH_ID_MISMATCH`. Prompt e schema se contradiziam dentro da mesma mensagem.

**Correção.** `RELATION-SCHEMA-v2.json`, aditivo, duas linhas de diff:

    - "title": "MS-001B RELATION JUDGMENT v1"
    + "title": "MS-001B RELATION JUDGMENT v2"
    - "batch_id": {"type": "string", "pattern": "^BATCH-[1-4]$"}
    + "batch_id": {"type": "string", "enum": ["BATCH-1","BATCH-2","BATCH-3","BATCH-4A","BATCH-4B"]}

Enum explícita, preferida à regex. Nenhuma outra alteração semântica.
`lib/relation_validate.py` **inalterado**.

**Confirmação empírica.** Na EXEC-4, `BATCH-4A` e `BATCH-4B` passaram em **todas as
três runs** — 11 + 11 julgamentos por run, seis chamadas, zero `R03`.

## 4. BC semantics errata

`ERRATA-MS001B-BLOCKER-CONTROL-SEMANTICS.md`, aditiva, nenhum dado alterado:

    BC_BUCKET_MEMBERSHIP  !=  EXPECTED_SEMANTIC_RELATION
    BLOCKER RETAINS A PAIR   não implica   SEMANTIC RELATION EXISTS

    BLOCKER_CONTROL   = BC1-BC5 = retention / coverage probe
    SEMANTIC_CONTROL  = J1-J10  = synthetic discriminant fixtures

Não foram criados pares BC curados após observar judgments. Claims não remapeados.
Blocker não recalibrado. Sem blocker v0.4. V1 inalterada. 97 pares e `PAIRSET_HASH`
inalterados.

## 5. Blocker — inalterado

`blocker v0.3` permanece **`BLOCKER_FEATURE_MODEL_QUALIFIED`**. A qualificação é
mecânica e segue intacta: três canais de feature, zero `FEATURE_CHANNEL_LEAK`,
conceitos e named objects congelados, separação de content-token, geração determinística
de pares, provenance e identidade tipada. Deixa-se de alegar que BC1–BC5 provam relações
semânticas.

    blocker_design_hash = fa62c8159f2cef53ce435d56b3f7f68aedea950acb6ea47822bff8767059cba8

## 6. V1 — inalterada

    SELECTED_VARIANT = V1

Selecionada **antes** de qualquer semantic judgment, por decisão externa de recall.
Seleção não repetida; V1 × V2 não recomparadas com judgments. Conservador por desenho:
evita seleção de variante posterior ao resultado.

## 7. Pairset / hash — inalterados

    97 pares exatos
    PAIRSET_HASH = a0b116d93f754576cf8fbbbf6eb1757b2837b7ea18b415f8e2bce30c1ee517f5
    partição 25 / 25 / 25 / 11 / 11

`PAIRSET_DRIFT = false`. Nenhum par desconhecido em nenhuma run.

## 8. Schema v2 / hash

    RELATION-SCHEMA-v1.json  35c5814841711d4c92b9dc7e869b01902405bd40944a48720ad2d3f4c4db1973  (preservado)
    RELATION-SCHEMA-v2.json  62f37d6d889c923d88505a6d4b6d3cee09f7a0a74d9bd55b6bf217ea7a2c5fba  (ativo)

## 9. Canários — 76/76 PASS, zero modelo

    premodel_canaries.py      22/22
    batch_canaries.py          7/7
    mechanical_canaries.py    36/36
    schema_canaries_v2.py     11/11

RS1 `BATCH-1` PASS · RS2 `BATCH-4A` PASS · RS3 `BATCH-4B` PASS ·
RS4 `BATCH-4` **FAIL** · RS5 `BATCH-5` **FAIL** ·
RS6 payload real do BATCH-4A da EXEC-3 com `batch_id` corrigido → schema PASS ·
RS7 10/11 → completude FAIL (`R15_PAIR_MISSING`) · RS8 11/11 → PASS ·
RS9 v2 difere de v1 só em `title` e `batch_id`, verificado mecanicamente ·
RS10 pairset intacto · RS11 partição ativa.

## 10. Opening Record EXEC-4

`ms001b/OPENING-RECORD-MS-001B-EXEC-4.md`, selado e **pushed antes de qualquer chamada
semântica** (commit `50fd4d8`). Opening Records das execuções 1, 2 e 3 intocados.

## 11. Max / OAuth proof

Prova de nível de transporte (`transport-audit/MS-001-P0-ROUTE-B-PROOF.md`):

    url            https://api.anthropic.com/v1/messages?beta=true
    user-agent     claude-cli/2.1.251 (external, sdk-cli)
    authorization  PRESENTE (bearer OAuth)
    x-api-key      AUSENTE          <- o header exigido pelo Console PAYG
    anthropic-beta …,oauth-2025-04-20,…
    tools          []

    subscriptionType = max · rateLimitTier = default_claude_max_20x
    hasExtraUsageEnabled = false (org_level_disabled)

Antes e depois das 18 chamadas: `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`,
`ANTHROPIC_BASE_URL`, `CLAUDE_CODE_OAUTH_TOKEN` = **UNSET**.
`~/.anthropic_key` **nunca lida** — atime `2026-08-30 03:19:56.449976008 -0300`
inalterado do início ao fim de toda a rodada.

## 12–14. RUN-1 · RUN-2 · RUN-3

| run | controle J1–J10 | BATCH-1 | BATCH-2 | BATCH-3 | BATCH-4A | BATCH-4B | total | status |
|---|---|---|---|---|---|---|---|---|
| RUN-1 | **10/10** | 25 | 25 | 25 | 11 | 11 | **97/97** | **VALID** |
| RUN-2 | **10/10** | 25 | 25 | 25 | 11 | 11 | **97/97** | **VALID** |
| RUN-3 | **10/10** | 25 | 25 | 25 | 11 | 11 | **97/97** | **VALID** |

Cada uma das 18 chamadas foi um processo `claude -p` novo. Sem `--continue`, sem
`--resume`, sem reuso de sessão, `--tools ""` (confirmado `tools: []` no transporte:
o juiz não teve ferramenta alguma e não pôde ler o repositório nem julgamentos alheios).

| # | chamada | modelo | in (tot) | out | thinking | stop | turns |
|---|---|---|---|---|---|---|---|
| 1 | `RUN-1-CONTROL` | `claude-opus-5` | 9478 | 2494 | 0 | `end_turn` | 1 |
| 2 | `RUN-1-BATCH-1` | `claude-opus-5` | 30647 | 5279 | 0 | `end_turn` | 1 |
| 3 | `RUN-1-BATCH-2` | `claude-opus-5` | 30366 | 5140 | 0 | `end_turn` | 1 |
| 4 | `RUN-1-BATCH-3` | `claude-opus-5` | 31235 | 5464 | 0 | `end_turn` | 1 |
| 5 | `RUN-1-BATCH-4A` | `claude-opus-5` | 15390 | 2791 | 0 | `end_turn` | 1 |
| 6 | `RUN-1-BATCH-4B` | `claude-opus-5` | 15390 | 2508 | 0 | `end_turn` | 1 |
| 7 | `RUN-2-CONTROL` | `claude-opus-5` | 9478 | 2433 | 0 | `end_turn` | 1 |
| 8 | `RUN-2-BATCH-1` | `claude-opus-5` | 30647 | 5218 | 0 | `end_turn` | 1 |
| 9 | `RUN-2-BATCH-2` | `claude-opus-5` | 30366 | 6199 | 0 | `end_turn` | 1 |
| 10 | `RUN-2-BATCH-3` | `claude-opus-5` | 31235 | 5313 | 0 | `end_turn` | 1 |
| 11 | `RUN-2-BATCH-4A` | `claude-opus-5` | 15390 | 3152 | 0 | `end_turn` | 1 |
| 12 | `RUN-2-BATCH-4B` | `claude-opus-5` | 15390 | 2629 | 0 | `end_turn` | 1 |
| 13 | `RUN-3-CONTROL` | `claude-opus-5` | 9478 | 2341 | 0 | `end_turn` | 1 |
| 14 | `RUN-3-BATCH-1` | `claude-opus-5` | 30647 | 5248 | 0 | `end_turn` | 1 |
| 15 | `RUN-3-BATCH-2` | `claude-opus-5` | 30366 | 5133 | 0 | `end_turn` | 1 |
| 16 | `RUN-3-BATCH-3` | `claude-opus-5` | 31235 | 5447 | 0 | `end_turn` | 1 |
| 17 | `RUN-3-BATCH-4A` | `claude-opus-5` | 15390 | 2964 | 0 | `end_turn` | 1 |
| 18 | `RUN-3-BATCH-4B` | `claude-opus-5` | 15390 | 2588 | 0 | `end_turn` | 1 |

    18/18 chamadas · HARD CAP 18 · retry 0
    modelo resolvido claude-opus-5 em 18/18 · thinking_tokens = 0 em 18/18
    stop_reason = end_turn em 18/18 · num_turns = 1 em 18/18
    system_sha256 único nas 18 chamadas: 37dc0211… (idêntico ao da EXEC-1)
    user_sha256 idêntico entre runs para cada label: CONTROL, BATCH-1..4B → 1 hash cada

## 15. Controls

J1–J10, controles sintéticos curados, **10/10 em cada uma das três runs** — 30/30 no
total. As sete relações foram exercitadas e acertadas: IDENTICAL, CORROBORATES,
SPECIALIZES/RIGHT_TO_LEFT, CONTRADICTS, SUPERSEDES/RIGHT_TO_LEFT, UNRELATED,
INDETERMINATE. Único gate discriminante, conforme a errata.

## 16. Completeness

Por run: 97/97 julgamentos · zero faltante · zero duplicado · zero desconhecido ·
schema v2 PASS · igualdade exata de evidence por lado PASS. Três runs, 291 julgamentos.

## 17. Relation distributions

| | RUN-1 | RUN-2 | RUN-3 |
|---|---|---|---|
| UNRELATED | 97 | 97 | 97 |
| demais relações | 0 | 0 | 0 |
| direction NONE | 97 | 97 | 97 |
| scope DIFFERENT_SCOPE | 97 | 97 | 97 |

Conforme §19 do briefing, **isso é resultado válido**. Nada foi alterado em função dele:
blocker, V1 e taxonomia permanecem como estavam. `POST_RESULT_TUNING = false`.

## 18. Stability

    STABLE            97
    PARTIALLY_STABLE   0
    UNSTABLE           0

Estabilidade total: os três julgamentos coincidem em relation, direction e scope_state
para todos os 97 pares. Os três judgments são persistidos por `(run_id, pair_id)`;
nenhuma run sobrescreve outra. **Zero silent majority** — nenhuma arbitragem de maioria
foi aplicada, porque não houve divergência a arbitrar.

## 19. BC bucket descriptive distributions

Descritivo, sem PASS/FAIL semântico, conforme a errata:

| bucket | declarados | produto cartesiano | retidos no pairset V1 | relations (cada run) |
|---|---|---|---|---|
| BC1_genuine_overlap | 45 | 45 | 27 | 27 × UNRELATED |
| BC2_scope_difference | 24 | 24 | 7 | 7 × UNRELATED |
| BC3_specialization | 78 | 78 | 55 | 55 × UNRELATED |
| BC4_false_conflict | 21 | 21 | 9 | 9 × UNRELATED |
| BC5_unrelated | 36 | 36 | **0** | — |
| (sem bucket) | — | — | 20 | 20 × UNRELATED |

BC5 com zero pares retidos é consistente com o blocker ter funcionado: pares
declaradamente não relacionados não chegaram ao juiz. Nenhum desses números é usado
para alterar blocker, variante ou taxonomia.

## 20. Contradictions

**Zero.** Nenhum `CONTRADICTS` no corpus real, nas três runs. Registro de contradições
vazio. Nenhum `governance_state` foi resolvido: todos os 97 pares permanecem
`NOT_YET_ADJUDICATED`. Nenhuma precedence derivada.

## 21. Candidate transport

Transportados separadamente da camada de Claim, sem que nenhuma relation reescreva
estrutura source-local:

    pkg-B   8 ELIGIBLE  ·  0 NOT_ELIGIBLE
    pkg-C   8 ELIGIBLE  ·  4 NOT_ELIGIBLE   (permanecem source-local, não transportados)

Total transportado: **16 ELIGIBLE**, refs tipadas.

## 22. Provenance

**100%.** Todos os 97 pares resolvem a âncora de evidência em ambos os lados; lista de
pares sem âncora vazia. Source Packages selados e não reabertos:
`a0a73dde…` (B), `5959b4ea…` (C), registro de selo externo verificado.

## 23. Typed identity

**100%.** Refs do pairset, refs de `PAIR-INPUTS` e refs de Candidate — todas com a
tripla `{source_package_hash, entity_kind, local_id}`, hash de 64 hex.

## 24. Fusion Package

`out-ms001b-exec4/fusion/FUSION-PACKAGE-MS001B-EXEC4.json`. Membros: hashes dos dois
Source Packages · blocker v0.3 + V1 · pairset completo com refs tipadas · blocker_trace ·
judgments das três runs por `(run_id, pair_id)` · `relation_stability_state` ·
`governance_state` · 16 `eligible_candidate_refs` · 4 não transportados ·
provenance_ledger · `unresolved_relation_states` · `open_questions` ·
FUSION-CONFIG-v2 · FUSION-TRACE.

    zero_operationalization = true
    zero_mtx_policy = true
    mtx_policy_hash = null

## 25. fusion_id

    345fd8fc6d5fbdf5d164ddd290aef3cd6a2d4c7d451e722b392cd0f024c08306

Derivado pela fórmula congelada, sobre exatamente os dez inputs declarados. Não inclui
`mtx_policy_hash`, timestamp operacional, número de run isolado ou estado de governança.

## 26. PAYG = zero

    PAYG_API_USED = 0

Nenhuma chamada pay-as-you-go. `~/.anthropic_key` nunca lida (atime inalterado).
SDK Python da Anthropic nunca executado. `--bare` nunca usado. Extra usage nunca
habilitado — está desligado na origem (`org_level_disabled`), o que torna gasto
impossível: no limite, o Claude Code para.

A soma de `total_cost_usd` das 18 chamadas foi **3,1662** — **estimativa client-side a
preço de tabela**, não cobrança. Na assinatura, o consumo é de franquia.

## 27. Max usage

O plano **não** atingiu o limite. Nenhuma chamada bloqueada, nenhuma pausa,
`MS_001_PAUSED_MAX_PLAN_USAGE_LIMIT` não acionado. Latência típica: ~60 s por batch
grande. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` manteve `modelUsage` com
exclusivamente `claude-opus-5` nas 18 chamadas — nenhuma inferência auxiliar.

## 28. Final audit

| contrato | veredito |
|---|---|
| J1–J10 em todas as runs válidas | **PASS** (10/10 × 3) |
| 97/97 por run | **PASS** (3 × 97) |
| zero faltante / duplicado / desconhecido | **PASS** |
| schema v2 PASS | **PASS** |
| igualdade de evidence | **PASS** |
| provenance 100% | **PASS** |
| typed identity 100% | **PASS** |
| stability produzida | **PASS** (97 STABLE) |
| Fusion consistente + fusion_id | **PASS** |
| contracts intactos | **PASS** |
| PAYG = zero | **PASS** |
| zero post-result tuning | **PASS** |
| PAIRSET_DRIFT | false |
| PACKAGE_DRIFT | false |
| SILENT_MAJORITY | false |
| MTX_IN_FUSION | false |
| HARD_CAP_EXCEEDED | false (18/18) |
| MODEL_DRIFT | false |

## 29. Historical executions

Preservadas integralmente, nada editado ou apagado: `out-ms001b/` (EXEC-1),
`out-ms001b-exec2/` (EXEC-2), `out-ms001b-exec3/` (EXEC-3), `out-exec-2/` (MS-001A),
`OPENING-RECORD-MS-001B.md`, `…-EXEC-2.md`, `…-EXEC-3.md`,
`MODEL-POLICY-MS001B.txt`, `RELATION-SCHEMA-v1.json`, `run_ms001b.py`,
`run_ms001b_routeB.py`.

## 30. Hashes

| artefato | sha256 |
|---|---|
| `ms001b/RELATION-SCHEMA-v1.json` | `35c5814841711d4c92b9dc7e869b01902405bd40944a48720ad2d3f4c4db1973` |
| `ms001b/RELATION-SCHEMA-v2.json` | `62f37d6d889c923d88505a6d4b6d3cee09f7a0a74d9bd55b6bf217ea7a2c5fba` |
| `ms001b/RELATION-PROMPT-v2.txt` | `0324219d1f62bbba9578894c41599794e7563be4a3d952d787a9ee61c5c34500` |
| `ms001b/RELATION-TAXONOMY-v1.txt` | `377879d2cd6a3e5460279466842b7549eda3898ab070b13aae64ab7e0dd3f5eb` |
| `ms001b/JUDGE-CONTROLS-J1-J10.json` | `761785cd26e07764ad06ab09fdd512ede78a24dbd7d70c5a09e867a8ad1879ff` |
| `ms001b/PAIRSET-MS001B-V1.json` | `e576a17ff954d3197c3168ed82fc26605603f565c7fe24d2671cdd59c54480b6` |
| `ms001b/PARTITION-MS001B-v2.json` | `62c3fccae8b4acdff984e68bce9e33499e37bea94daec813f6eff6835538debc` |
| `ms001b/MODEL-POLICY-MS001B-v2.txt` | `031103510cd0ae150e934d6fee1de45989371faacd0cdc7c95b0ac883c0a960a` |
| `lib/relation_validate.py` | `7283a123dd59dda2205a1e47a486fef94f279eed4ef1197fb273b1350cbb6dd5` |
| `run_ms001b_exec4.py` | `c53f88fd6d0ab89b82c7fd477c14dde1fee20b13432e5a74fa3cd89496148e31` |
| `schema_canaries_v2.py` | `bb7d4e21ee660920b641fa7d37111a436e728cbf62adb5a20dffd3e741f8cbdb` |
| `analyze_ms001b_exec4.py` | `68d22fdda7601209d02306e3c32622646aeb91ca73c7393bcb2ae0aaea324eab` |
| `ERRATA-MS001B-BLOCKER-CONTROL-SEMANTICS.md` | `737d74b5e6b021c5a1e8ada43b93418e87cb1dc1371f6e7b4bd181258931088e` |
| `ms001b/OPENING-RECORD-MS-001B-EXEC-4.md` | `628a122de66352035f99adf71221357b99da49430d23ddb0e6850a66b52b3955` |
| `out-ms001b-exec4/fusion/FUSION-PACKAGE-MS001B-EXEC4.json` | `5e0f93c269159042300fcfa67260a8cb20e9aa354774d843f0433cb2f6886b28` |
| `out-ms001b-exec4/fusion/FUSION-CONFIG-MS001B-v2.json` | `eb59dd24aa8ade342ce585652c164b4f09442a9996cd2a422fcde7270c8594af` |
| `out-ms001b-exec4/fusion/FUSION-TRACE-MS001B-EXEC4.json` | `93cc5f6763d8682664034b8696688cdee53e251720d62618a172abedd4a8a145` |

## 31. Commits / push

    2f0b20f  transport(MS-001): P0 PASS — Route B claude -p sobre OAuth Max      [pushed]
    a461b10  opening(MS-001B exec-3): OPENING RECORD antes da 1a chamada         [pushed]
    2073114  results(MS-001B exec-3): HARD STOP por dois defeitos de instrumento [pushed]
    b3bee9c  recovery(MS-001B exec-4): schema v2 + errata BC + canarios          [pushed]
    50fd4d8  opening(MS-001B exec-4): OPENING RECORD antes de qualquer chamada   [pushed]
    (este)   results(MS-001B exec-4): 3 runs VALID, Fusion e fusion_id

## 32. Drive

Nenhuma escrita e nenhuma leitura. O conector Google Drive não foi usado.
(O MCP "Bridge MTX Lab" seguiu com falha de conexão — HTTP 502 no endpoint.)

## 33. Forbidden scope

Não iniciado: Operationalization · Operational Package · Router · Skill Pack ·
Source A · MTX policy · N1–N9 · produção. Produção **não** autorizada.

## 34. Final classification

    PILOT_MS_001_PASS
    MS_001_ACCEPTED_FOR_EXPERIMENTAL_MULTI_SOURCE_FUSION
    MODEL_TRANSPORT = CLAUDE_MAX_OAUTH
    PAYG_API_USED = 0
    fusion_id = 345fd8fc6d5fbdf5d164ddd290aef3cd6a2d4c7d451e722b392cd0f024c08306

    STOPPED — READY FOR FINAL CHATGPT REVIEW
