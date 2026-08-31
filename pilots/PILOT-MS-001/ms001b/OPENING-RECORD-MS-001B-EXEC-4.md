# OPENING RECORD — PILOT-MS-001B — EXECUÇÃO 4

Selado e pushed **ANTES** de qualquer chamada semântica da execução 4.
Data: 2026-08-31. Os Opening Records das execuções 1, 2 e 3 permanecem **intocados**.

---

## 1. Histórico das execuções anteriores

* **EXEC-1** — `INVALID / BLOCKED`. Interrompida por saldo de API em 13/15 chamadas.
* **EXEC-2** — `BLOCKED`. `HARD STOP — API CREDIT` na chamada 1, antes de qualquer
  julgamento. Nenhum dado semântico produzido.
* **EXEC-3** — `INVALID`. Razão primária: **`RELATION_SCHEMA_BATCH_ID_MISMATCH`**.
  O transporte Route B foi provado e funcionou; a falha foi de instrumento.

    MS_001B_EXEC_3 = INVALID

Os 86 julgamentos válidos e os controles J1–J10 PASS da EXEC-3 permanecem auditáveis em
`out-ms001b-exec3/`, mas **não** entram em estabilidade, distribuição final, Fusion ou
veredito de aceitação. **Nenhum judgment ou control da EXEC-3 é reutilizado.**
A EXEC-4 começa do zero.

## 2. Route B P0 PASS

    MS_001_MAX_PLAN_ROUTE_B_P0_PASS

Prova de nível de transporte em `../transport-audit/MS-001-P0-ROUTE-B-PROOF.md`:
header `authorization` presente, `x-api-key` **ausente**, beta `oauth-2025-04-20`,
`tools: []`, `~/.anthropic_key` não lida.

## 3. Correção DEF-1 — relation schema v2

Aditiva. `RELATION-SCHEMA-v1.json` preservado. Diff completo — duas linhas:

    - "title": "MS-001B RELATION JUDGMENT v1"
    + "title": "MS-001B RELATION JUDGMENT v2"
    - "batch_id": {"type": "string", "pattern": "^BATCH-[1-4]$"}
    + "batch_id": {"type": "string", "enum": ["BATCH-1","BATCH-2","BATCH-3","BATCH-4A","BATCH-4B"]}

Enum explícita da partição ativa. Nenhuma outra alteração semântica.
`lib/relation_validate.py` **inalterado**.

## 4. Correção DEF-2 — errata declarativa

`../ERRATA-MS001B-BLOCKER-CONTROL-SEMANTICS.md`. Nenhum dado alterado.

    BC_BUCKET_MEMBERSHIP  !=  EXPECTED_SEMANTIC_RELATION
    BLOCKER RETAINS A PAIR   não implica   SEMANTIC RELATION EXISTS

    BLOCKER_CONTROL   = BC1-BC5 = retention / coverage probe, sem expected relation
    SEMANTIC_CONTROL  = J1-J10  = único controle discriminante, 10/10 exigido por run

Não foram criados pares BC curados após observar judgments. Claims não foram remapeados.
O blocker não foi recalibrado. Não existe blocker v0.4. V1 não mudou. Os 97 pares e o
`PAIRSET_HASH` não mudaram.

## 5. Canários pré-execução — 76/76 PASS, zero modelo

    premodel_canaries.py      22/22
    batch_canaries.py          7/7
    mechanical_canaries.py    36/36
    schema_canaries_v2.py     11/11   (RS1-RS11)

Destaques de `schema_canaries_v2.py`:

* **RS1/RS2/RS3** — `BATCH-1`, `BATCH-4A`, `BATCH-4B` PASS.
* **RS4** — `BATCH-4` FALHA, por não pertencer à partição ativa.
* **RS5** — `BATCH-5` FALHA.
* **RS6** — o payload real do BATCH-4A da EXEC-3, com `batch_id` corrigido, valida sob
  o schema v2: o defeito era exclusivamente o rótulo.
* **RS7** — 10/11 → completude FALHA (`R15_PAIR_MISSING`).
* **RS8** — 11/11 → schema v2 PASS e validador PASS.
* **RS9** — v2 difere de v1 somente em `title` e `batch_id`, verificado mecanicamente.

## 6. Prompt semântico — SYSTEM byte-idêntico

    SYSTEM sha256 = 37dc021103d168d6a86ee45ee4068979de866f8cd4a89e7715bac6888f7bf1e9

Idêntico ao `system_sha256` registrado pela EXEC-1 sob o transporte antigo (SDK Python
+ PAYG). Mudou apenas o envelope do USER, pela substituição de `{JSON_SCHEMA}` pelo
schema v2. Nenhuma regra de relação foi alterada.

## 7. Transporte — inalterado

    MODEL_TRANSPORT = CLAUDE_CODE_MAX_OAUTH_PRINT_MODE
    Claude Code 2.1.251
    env obrigatório  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
    env proibido     ANTHROPIC_API_KEY · ANTHROPIC_AUTH_TOKEN · ANTHROPIC_BASE_URL
                     CLAUDE_CODE_OAUTH_TOKEN · Bedrock/Vertex/Foundry (verificado em runtime)

    claude -p --model claude-opus-5 --system-prompt-file <SYSTEM congelado>
             --tools "" --disable-slash-commands --strict-mcp-config
             --no-session-persistence --permission-mode dontAsk --setting-sources ""
             --settings '{"alwaysThinkingEnabled":false}' --output-format json

    USER por stdin, bytes exatos do arquivo congelado.

**PAYG PROIBIDO.** Nunca: SDK Python da Anthropic, `~/.anthropic_key`,
`ANTHROPIC_API_KEY`, `--bare`, extra usage pago, Console API, `--continue`, `--resume`.
O orquestrador aborta se qualquer variável proibida estiver definida.

## 8. Isolamento por processo fresh

18 processos `claude -p` novos, um por chamada. Sem herança de judgment, de estado
conversacional ou de resultados de outra run. Orquestrador determinístico; nenhum LLM
parent reescreve prompt, Claims, Evidence, pair payload ou output.

## 9. Partição — 25 / 25 / 25 / 11 / 11

    BATCH-1 25 · BATCH-2 25 · BATCH-3 25 · BATCH-4A 11 · BATCH-4B 11  =  97 pares exatos
    PAIRSET_HASH = a0b116d93f754576cf8fbbbf6eb1757b2837b7ea18b415f8e2bce30c1ee517f5

Se um único par mudar: **HARD STOP**.

## 10. Runs

    RUN-1 · RUN-2 · RUN-3, cada uma: 1 controle J1-J10 + 5 batches = 6 chamadas
    total 18 · HARD_CAP 18 · RETRY 0

Controle falho → run `INVALID` e batches **não** queimados.

## 11. Completude exigida por run

controles 10/10 · 97/97 julgamentos · zero faltante · zero duplicado · zero desconhecido ·
schema v2 PASS · igualdade de evidence PASS.

## 12. Taxa de UNRELATED não é critério de falha

Se uma ou mais runs devolverem 97/97 `UNRELATED`, **isso é resultado válido**. Não se
altera blocker, variante ou taxonomia em função da distribuição observada.
Zero post-result tuning.

## 13. Estabilidade

Após três runs válidas, por par: `STABLE` / `PARTIALLY_STABLE` / `UNSTABLE`.
Os três judgments são persistidos por `(run_id, pair_id)`. **Zero silent majority.**

## 14. Análise de bucket BC — apenas descritiva

Por bucket: número de pares retidos e distribuição de relations. Sem PASS/FAIL
semântico. Sem expected relation por par. Sem usar o resultado para alterar o blocker.

## 15. Limite do plano Max

    MS_001_PAUSED_MAX_PLAN_USAGE_LIMIT

Pausa operacional, não `INVALID`. Não trocar de transporte, não usar API, não habilitar
extra usage. Contrato de retomada: run interrompida no meio é descartada por inteiro e
reexecutada a partir do controle; nenhum batch parcial é reaproveitado.

## 16. Artefatos congelados

| artefato | sha256 |
|---|---|
| `ms001b/RELATION-PROMPT-v2.txt` | `0324219d1f62bbba9578894c41599794e7563be4a3d952d787a9ee61c5c34500` |
| `ms001b/RELATION-SCHEMA-v1.json` | `35c5814841711d4c92b9dc7e869b01902405bd40944a48720ad2d3f4c4db1973` |
| `ms001b/RELATION-SCHEMA-v2.json` | `62f37d6d889c923d88505a6d4b6d3cee09f7a0a74d9bd55b6bf217ea7a2c5fba` |
| `ms001b/RELATION-TAXONOMY-v1.txt` | `377879d2cd6a3e5460279466842b7549eda3898ab070b13aae64ab7e0dd3f5eb` |
| `ms001b/JUDGE-CONTROLS-J1-J10.json` | `761785cd26e07764ad06ab09fdd512ede78a24dbd7d70c5a09e867a8ad1879ff` |
| `ms001b/PAIRSET-MS001B-V1.json` | `e576a17ff954d3197c3168ed82fc26605603f565c7fe24d2671cdd59c54480b6` |
| `ms001b/PAIR-INPUTS-MS001B.json` | `f1d05aca8b13c3f2686c3a80463289b1d969565eea9d3293dc1b61a78aa657b0` |
| `ms001b/PARTITION-MS001B-v2.json` | `62c3fccae8b4acdff984e68bce9e33499e37bea94daec813f6eff6835538debc` |
| `ms001b/BLOCKED-TRACE-MS001B-V1.json` | `ef4413e85b5560a2c4abad0a62695c5295be136d3fad427629d03872aebe5a16` |
| `ms001b/MODEL-POLICY-MS001B-v2.txt` | `031103510cd0ae150e934d6fee1de45989371faacd0cdc7c95b0ac883c0a960a` |
| `lib/relation_validate.py` | `7283a123dd59dda2205a1e47a486fef94f279eed4ef1197fb273b1350cbb6dd5` |
| `run_ms001b_exec4.py` | `c53f88fd6d0ab89b82c7fd477c14dde1fee20b13432e5a74fa3cd89496148e31` |
| `schema_canaries_v2.py` | `bb7d4e21ee660920b641fa7d37111a436e728cbf62adb5a20dffd3e741f8cbdb` |
| `ERRATA-MS001B-BLOCKER-CONTROL-SEMANTICS.md` | `737d74b5e6b021c5a1e8ada43b93418e87cb1dc1371f6e7b4bd181258931088e` |
| `MS-001B-EXEC-4-RECOVERY-NOTE.md` | `a9bd3633b777b8c220d3776b39b141ff6b2b32a27bbf3347d61b44ddf2c2ffe7` |

## 17. Zero PAYG

    PAYG_API_USED = 0

Verificado antes de cada chamada pelo guard de ambiente do orquestrador.
