# PILOT-MS-001 — MAX PLAN AUTONOMOUS FINAL CLOSEOUT REPORT

Data: 2026-08-31 · Claude Code `2.1.251` · transporte Route B (Claude Max OAuth).

    TRANSPORTE:  MS_001_MAX_PLAN_ROUTE_B_P0_PASS
    EXECUCAO:    MS_001B_HARD_STOP_INSTRUMENT_DEFECT
    PAYG_API_USED = 0

O transporte foi provado e funcionou. A execução do MS-001B parou em dois defeitos de
instrumento, ambos anteriores a esta rodada e ambos em artefatos selados que o §11 do
briefing proíbe alterar. **Não há `PILOT_MS_001_PASS`.**

---

## 1. P0 proof

`MS_001_MAX_PLAN_ROUTE_B_P0_PASS`. Fixture sintético, fora do corpus, sentinelas
`P0_SYSTEM_SENTINEL_7F3A` / `P0_USER_SENTINEL_91BC`, saída `P0_MAX_PLAN_OK`.
As 10 condições de PASS do §6 do briefing foram satisfeitas.
Detalhe: `transport-audit/MS-001-P0-ROUTE-B-PROOF.md`.

Prova de nível de transporte, capturada com `ANTHROPIC_LOG=debug`:

    url        https://api.anthropic.com/v1/messages?beta=true
    user-agent claude-cli/2.1.251 (external, sdk-cli)
    authorization  PRESENTE (bearer OAuth)
    x-api-key      AUSENTE
    anthropic-beta …,oauth-2025-04-20,…
    tools: []   thinking_tokens: 0   model: claude-opus-5

## 2. auth / billing path

    OAuth claude.ai · subscriptionType = max · rateLimitTier = default_claude_max_20x
    scopes: user:inference, user:profile, user:sessions:claude_code, …
    ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / ANTHROPIC_BASE_URL / CLAUDE_CODE_OAUTH_TOKEN = UNSET
    apiKeyHelper ausente · managed-settings ausente · Bedrock/Vertex/Foundry ausentes
    hasExtraUsageEnabled = false  (org_level_disabled)

Duas travas independentes tornam gasto PAYG impossível: não há credencial de API no
caminho, e usage credits estão desligados na origem — no limite, o Claude Code **para**.

`~/.anthropic_key` não foi lida em nenhum momento: atime
`2026-08-30 03:19:56.449976008 -0300` idêntico do início ao fim da rodada.

## 3. transport Decision Record

`DECISION-RECORD-MS-001B-MODEL-TRANSPORT.md`:

    MS_001B_MODEL_TRANSPORT = CLAUDE_CODE_MAX_OAUTH_PRINT_MODE
    PAYG_API_FORBIDDEN
    MODEL_TRANSPORT_RECOVERY

## 4. Opening Record Exec 3

`ms001b/OPENING-RECORD-MS-001B-EXEC-3.md`, selado e **pushed antes da primeira
chamada** (commit `a461b10`). Registra histórico das execuções 1 e 2, P0, versão do
Claude Code, flags exatas, proibição de `--bare`, requisitos de auth, isolamento por
processo fresh, contratos semânticos inalterados, partição 25/25/25/11/11, J1–J10,
3 runs, tratamento do limite Max e zero PAYG. Os Opening Records anteriores ficaram
intocados.

## 5. fresh-process isolation

Cada chamada foi um processo `claude -p` novo, que nasceu, respondeu e morreu.
Sem `--continue`, sem `--resume`, sem reuso de sessão, `--no-session-persistence`,
`--tools ""` (confirmado `tools: []` no transporte — o juiz não teve ferramenta
alguma e não pôde ler o repositório nem outputs anteriores).

O orquestrador `run_ms001b_routeB.py` é código determinístico: prepara inputs
congelados, dispara, persiste raw e valida mecanicamente. **Nenhum LLM parent** tocou
prompt, Claims, Evidence, pair payload ou output.

Injeção residual medida: um bloco constante do lado USER
(`<total_tokens>… tokens left</total_tokens>`) e três blocos fixos do lado SYSTEM,
congelados por versão + configuração. Determinismo comprovado:
`input_tokens = 415` em três processos independentes com input byte-idêntico.

Nota de transporte: o `claude -p` usa prompt caching (`cache_read = 1754` nos batches,
o prefixo SYSTEM compartilhado). O cache guarda **apenas entrada**, nunca saída — não há
vazamento entre chamadas ou runs, e o modelo recebe exatamente os mesmos tokens.

## 6. calls / run accounting

| # | chamada | modelo | in (tot) | out | thinking | stop | turns |
|---|---|---|---|---|---|---|---|
| 1 | `RUN-1-CONTROL` | `claude-opus-5` | 9449 | 2942 | 0 | `end_turn` | 1 |
| 2 | `RUN-1-BATCH-1` | `claude-opus-5` | 30618 | 5191 | 0 | `end_turn` | 1 |
| 3 | `RUN-1-BATCH-2` | `claude-opus-5` | 30337 | 5350 | 0 | `end_turn` | 1 |
| 4 | `RUN-1-BATCH-3` | `claude-opus-5` | 31206 | 5320 | 0 | `end_turn` | 1 |
| 5 | `RUN-1-BATCH-4A` | `claude-opus-5` | 15361 | 2768 | 0 | `end_turn` | 1 |
| 6 | `RUN-2-CONTROL` | `claude-opus-5` | 9449 | 3026 | 0 | `end_turn` | 1 |

    executadas 6 · HARD CAP 18 · retry 0 · modelo resolvido claude-opus-5 em 6/6
    thinking_tokens = 0 em 6/6 · stop_reason = end_turn em 6/6 · num_turns = 1 em 6/6

Interrompi a execução na chamada 6 deliberadamente, ao identificar que o defeito 1 é
determinístico e faria as três runs falharem de forma idêntica: continuar custaria
mais 12 chamadas de franquia para produzir três runs `INVALID`.

## 7. RUN-1

    CONTROL   J1-J10  10/10 OK
    BATCH-1   25 judgments OK
    BATCH-2   25 judgments OK
    BATCH-3   25 judgments OK
    BATCH-4A  R03_BATCH_ID_MISMATCH  ->  RUN-1 INVALID
    BATCH-4B  nao executado (fail-closed antes de queimar a chamada)

    status: INVALID · 75 judgments validados + 11 rejeitados por rotulo

## 8. RUN-2

    CONTROL   J1-J10  10/10 OK  (identico a RUN-1, relacao por relacao)
    batches   nao executados — execucao interrompida

## 9. RUN-3

    nao iniciada

## 10. completeness

Não atingida. Zero runs válidas. O contrato exige 97/97 em três runs independentes;
obteve-se 75/97 validados em uma run e nada nas outras duas.

## 11. relation distributions

Achado central, **reproduzido de forma independente nos dois transportes**:

| | EXEC-1 RUN-1 | EXEC-1 RUN-2 | EXEC-3 RUN-1 |
|---|---|---|---|
| transporte | SDK Python + PAYG | SDK Python + PAYG | `claude -p` + Max OAuth |
| UNRELATED | 96/96 | 96/96 | 86/86 |
| qualquer outra relação | 0 | 0 | 0 |

Todos os 97 pares admitidos pelo blocker são julgados `UNRELATED`, sob dois
transportes independentes. Ver §13 — a causa é o defeito 2.

Nos controles sintéticos J1–J10, a distribuição é rica e correta: IDENTICAL,
CORROBORATES, SPECIALIZES/RIGHT_TO_LEFT, CONTRADICTS, SUPERSEDES/RIGHT_TO_LEFT,
UNRELATED, INDETERMINATE — 10/10 em RUN-1 e 10/10 em RUN-2.

## 12. stability

Não calculável: exige três runs válidas. Nenhuma arbitragem de maioria foi aplicada,
nenhum estado `STABLE`/`PARTIALLY_STABLE`/`UNSTABLE` foi emitido.

Único dado de estabilidade disponível: a chamada de controle é **perfeitamente
reprodutível** entre RUN-1 e RUN-2 — 10/10 idênticos em relation, direction e
scope_state.

## 13. BC1–BC4 audit

**Os controles de corpus são inválidos como construídos.** Em
`blocker/control-mappings-v03.json`, os cinco conjuntos são **produtos cartesianos
puros** de claims B × claims C, rotulados em bloco:

| controle | B | C | pairs | \|B\|×\|C\| |
|---|---|---|---|---|
| BC1_genuine_overlap | 9 | 5 | 45 | 45 |
| BC2_scope_difference | 3 | 8 | 24 | 24 |
| BC3_specialization | 13 | 6 | 78 | 78 |
| BC4_false_conflict | 3 | 7 | 21 | 21 |
| BC5_unrelated | 6 | 6 | 36 | 36 |

Um produto cartesiano não pode ser inteiramente "genuine overlap". Exemplo real, par
BC1 `CL-0013|CL-0036`: à esquerda, gerar QR Code para conectar a instância; à direita,
os cinco campos do webhook. Compartilham a palavra "Instância" e nada mais. Os dois
transportes julgaram `UNRELATED` com a mesma justificativa. **O juiz está certo; o
rótulo BC1 está errado.**

Consequências: a auditoria pós-hoc não pode medir capacidade; o "PASS" de BC4 (zero
falsas contradições) é **degenerado**, pois passa porque tudo é UNRELATED, não porque o
juiz resistiu a vocabulário compartilhado; e a calibração do blocker e a seleção da
variante V1 foram feitas contra essas mesmas métricas cartesianas.

## 14. contradictions

Nenhuma contradição registrada: zero `CONTRADICTS` no corpus real, nos dois
transportes. Nenhum `governance_state` foi emitido. Nada foi adjudicado.

## 15. Candidate transport

Não executado — depende de um Fusion Package, que não foi criado. Os Candidates
permanecem source-local e intactos nos pacotes selados:
pkg-B 8 ELIGIBLE, pkg-C 8 ELIGIBLE + 4 NOT_ELIGIBLE.

## 16. provenance

Todos os artefatos verificados e inalterados. O SYSTEM montado pela Route B tem
sha256 `37dc021103d168d6a86ee45ee4068979de866f8cd4a89e7715bac6888f7bf1e9`,
**idêntico** ao `system_sha256` registrado pela execução 1 sob o transporte antigo —
prova de que a troca de transporte preservou o instrumento semântico byte a byte.

Source Packages selados e não reabertos:
`a0a73dde…` (B) e `5959b4ea…` (C). Canários pré-modelo: **65/65 PASS**.

## 17. Fusion Package

**Não criado.** Requer três runs válidas. `analyze_ms001b_exec3.py` está pronto e
testado sintaticamente, mas não foi executado sobre dados inválidos.

## 18. fusion_id

**Não emitido.**

## 19. final audit

| contrato | veredito |
|---|---|
| zero PAYG API | **PASS** |
| transporte plano Max provado | **PASS** |
| Opening Record selado antes da 1ª chamada | **PASS** |
| isolamento por processo fresh | **PASS** |
| modelo fixado e verificado em toda chamada | **PASS** (6/6) |
| thinking desligado | **PASS** (6/6) |
| raw preservado byte-a-byte | **PASS** |
| orquestrador determinístico, sem LLM parent | **PASS** |
| instrumentos selados inalterados | **PASS** |
| HARD CAP respeitado | **PASS** (6/18) |
| controles J1–J10 | **PASS** (10/10 em duas runs) |
| completude 97/97 × 3 runs | **FALHA** — defeito 1 |
| estabilidade | **NÃO CALCULÁVEL** |
| auditoria BC1–BC4 | **INVÁLIDA** — defeito 2 |
| Fusion / fusion_id | **NÃO EMITIDO** |

## 20. PAYG API usage

    PAYG_API_USED = 0

Nenhuma chamada à Anthropic API pay-as-you-go em nenhum momento desta rodada.
Nenhuma recarga, nenhum auto-recharge, nenhum extra usage. `~/.anthropic_key` nunca
lida. O SDK Python da Anthropic nunca importado em execução. `--bare` nunca usado.
Todo consumo correu sobre a assinatura Claude Max.

O campo `total_cost_usd` somou **1,7227** nas 6 chamadas — é **estimativa client-side a
preço de tabela**, não cobrança: na assinatura o consumo é de franquia, e extra usage
está desligado na origem.

## 21. Max-plan usage behavior

O plano **não** atingiu o limite. Nenhuma chamada foi bloqueada, nenhuma pausa por
limite ocorreu, `MS_001_PAUSED_MAX_PLAN_USAGE_LIMIT` não foi acionado. Latência típica
por chamada de batch: ~60 s. Uma chamada auxiliar a `claude-haiku-4-5`
(`generate_session_title`) foi observada na sonda P0 e **eliminada** com
`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`; nas 6 chamadas da execução,
`modelUsage` contém exclusivamente `claude-opus-5`.

## 22. historical executions preserved

Intactos: `out-ms001b/` (exec-1), `out-ms001b-exec2/` (exec-2),
`out-exec-2/` (MS-001A), `OPENING-RECORD-MS-001B.md`,
`OPENING-RECORD-MS-001B-EXEC-2.md`, `MODEL-POLICY-MS001B.txt`,
`run_ms001b.py`. Nada foi editado, sobrescrito ou apagado. A execução 3 escreve
apenas em `out-ms001b-exec3/` e em arquivos novos.

## 23. commits / push

    2f0b20f  transport(MS-001): P0 PASS — Route B claude -p sobre OAuth Max     [pushed]
    a461b10  opening(MS-001B exec-3): OPENING RECORD selado e pushed ANTES…      [pushed]
    (este)   results(MS-001B exec-3): HARD STOP por dois defeitos de instrumento

## 24. Drive

Nenhuma escrita. Nenhuma leitura. O conector Google Drive não foi usado nesta rodada.
(O MCP "Bridge MTX Lab" segue com falha de conexão — HTTP 502 no endpoint.)

## 25. final classification

    MS_001_MAX_PLAN_ROUTE_B_P0_PASS
    MS_001B_MODEL_TRANSPORT = CLAUDE_CODE_MAX_OAUTH_PRINT_MODE
    PAYG_API_USED = 0

    MS_001B_HARD_STOP_INSTRUMENT_DEFECT
    PILOT_MS_001_PASS            — NAO CONCEDIDO
    MS_001_ACCEPTED_FOR_EXPERIMENTAL_MULTI_SOURCE_FUSION  — NAO CONCEDIDO

O problema de transporte que parou este projeto está **resolvido**: o MS-001B pode
rodar inteiramente na franquia Claude Max, com isolamento por processo mais forte do
que o do transporte original e sem nenhum gasto PAYG.

O que agora bloqueia o MS-001B é outra coisa, e é anterior: dois defeitos nos
instrumentos selados, detalhados em
`MS-001B-EXEC-3-HARD-STOP-INSTRUMENT-DEFECT.md`. Corrigi-los exige decisão externa,
porque o §11 do briefing proíbe alterar schema, controles e calibração do blocker.

Nenhuma operationalização, Operational Package, Router, Skill Pack, Source A,
produção, MTX policy ou N1–N9 foi iniciada.
