# DECISION RECORD — MS-001B MODEL TRANSPORT

    MS_001B_MODEL_TRANSPORT = CLAUDE_CODE_MAX_OAUTH_PRINT_MODE
    PAYG_API_FORBIDDEN
    MODEL_TRANSPORT_RECOVERY

Data: 2026-08-31.

## Decisão

O transporte de modelo do MS-001B passa de

    Python Anthropic SDK + API key (~/.anthropic_key)     [ROUTE A, PAYG]

para

    processo `claude -p` novo por chamada + OAuth Claude Max   [ROUTE B]

Base: `transport-audit/MS-001-P0-ROUTE-B-PROOF.md` (`MS_001_MAX_PLAN_ROUTE_B_P0_PASS`)
e `MS-001-MAX-PLAN-TRANSPORT-FEASIBILITY-REPORT.md`.

## Classificação

Isto é **`MODEL_TRANSPORT_RECOVERY`**, não mudança semântica. Permanecem
byte-idênticos e não reabertos:

Source Packages · blocker v0.3 · V1 · `PAIRSET_HASH` · os 97 pares ·
`RELATION-PROMPT-v2.txt` · `RELATION-SCHEMA-v1.json` · `RELATION-TAXONOMY-v1.txt` ·
`JUDGE-CONTROLS-J1-J10.json` · `PARTITION-MS001B-v2.json` (25/25/25/11/11) ·
`BLOCKED-TRACE-MS001B-V1.json` · `FUSION-CONFIG-MS001B.json` · Evidence ·
Candidate transport · stability policy · Fusion semantics · `lib/relation_validate.py`.

## Proibições permanentes

`ANTHROPIC PAYG API = PERMANENTLY PROHIBITED FOR THIS PROJECT`

Proibido, sem exceção: carregar `~/.anthropic_key`; exportar `ANTHROPIC_API_KEY` ou
`ANTHROPIC_AUTH_TOKEN` ou `ANTHROPIC_BASE_URL`; usar o SDK Python da Anthropic;
usar `--bare`; habilitar extra usage pago; usar Console API; Bedrock/Vertex/Foundry;
`apiKeyHelper`.

## Contrato de invocação congelado

    Claude Code            2.1.251
    env obrigatório        CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
    env proibido (UNSET)   ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN,
                           ANTHROPIC_BASE_URL, CLAUDE_CODE_OAUTH_TOKEN
    flags                  -p --model claude-opus-5
                           --system-prompt-file <SYS>
                           --tools "" --disable-slash-commands --strict-mcp-config
                           --no-session-persistence --permission-mode dontAsk
                           --setting-sources "" --settings {"alwaysThinkingEnabled":false}
                           --output-format json
    USER                   por stdin, bytes do arquivo congelado
    proibido               --bare, --continue, --resume, reuso de sessão

Mudança de versão do Claude Code invalida o congelamento e exige nova P0.

## Limite do plano

Se o plano Max atingir o limite durante a execução: **não** recorrer à API, **não**
habilitar extra usage. Persistir estado e classificar
`MS_001_PAUSED_MAX_PLAN_USAGE_LIMIT` — pausa operacional, não `INVALID` metodológico.
