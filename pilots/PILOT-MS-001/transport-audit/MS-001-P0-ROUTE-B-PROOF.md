# MS-001 — P0 ROUTE B TRANSPORT PROOF

    MS_001_MAX_PLAN_ROUTE_B_P0_PASS

Data: 2026-08-31 · Claude Code `2.1.251` · fora do corpus MS-001.

## 1. Fixture sintético

Nenhum Claim, Evidence, pairset, controle BC ou output anterior foi usado.

| arquivo | bytes | sha256 |
|---|---|---|
| `p0/P0-SYSTEM.txt` | 325 | `a114aec9894b5f95bf331944260f0dbc85e2c568d89419cf928f47caf67a87cd` |
| `p0/P0-USER.txt` | 39 | `36448a3240987d6911b50239122ef5535879ff34c8a54446d483593eb510c444` |
| `p0/P0C-SYSTEM.txt` | 380 | `9457b21fad6c26349eefbc825b7f3eae4d7f3049ecdf383e3887a577273342cf` |
| `p0/P0C-USER.txt` | 32 | `03014543cdc969b646e80bc29ca3b3624254f6811ae6875d530d0c83ed6afc03` |

Sentinelas: `P0_SYSTEM_SENTINEL_7F3A` (SYSTEM), `P0_USER_SENTINEL_91BC` (USER),
saída esperada `P0_MAX_PLAN_OK`.

## 2. Invocação

    cat P0-USER.txt | CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 claude -p \
      --model claude-opus-5 \
      --system-prompt-file P0-SYSTEM.txt \
      --tools "" --disable-slash-commands --strict-mcp-config \
      --no-session-persistence --permission-mode dontAsk --setting-sources "" \
      --settings '{"alwaysThinkingEnabled":false}' \
      --output-format json --debug api --debug-file raw/P0-DEBUG.log

Sem `--bare`. Sem `--continue`. Sem `--resume`. cwd fora de repositório git e sem
`CLAUDE.md`. Exit code `0` em todas as sondas.

## 3. Sondas executadas

| sonda | propósito | resultado | input_tokens | modelos |
|---|---|---|---|---|
| P0 | prova funcional + debug api | `P0_MAX_PLAN_OK` | **415** | opus-5 + haiku (título) |
| P0B | idem, com `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` | `P0_MAX_PLAN_OK` | **415** | **opus-5 apenas** |
| P0C | introspecção de payload via `ANTHROPIC_LOG=debug` | recusa (ver §6) | 414 | opus-5 apenas |
| P0D | idem P0B com transcript persistido | `P0_MAX_PLAN_OK` | **415** | opus-5 apenas |

## 4. Prova de billing path — nível de transporte

`ANTHROPIC_LOG=debug` capturou o request efetivamente enviado
(`p0/raw/P0C-STDOUT.sanitized.txt`):

    url        : https://api.anthropic.com/v1/messages?beta=true
    user-agent : claude-cli/2.1.251 (external, sdk-cli)
    headers    : authorization  → PRESENTE (bearer OAuth, redigido)
                 x-api-key      → AUSENTE
    anthropic-beta: claude-code-20250219,**oauth-2025-04-20**,…

A ausência de `x-api-key` e a presença de `authorization` + do beta flag
`oauth-2025-04-20` são prova direta de que a chamada correu pela **assinatura
Claude Max via OAuth**, e não pelo Console pay-as-you-go, que exige `x-api-key`.

Estado de auth antes e depois de cada sonda (`p0/raw/P0-PRE.txt`, `P0-POST.txt`):
`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`,
`CLAUDE_CODE_OAUTH_TOKEN` = **UNSET**.

`~/.anthropic_key` **não foi lida**: atime `2026-08-30 03:19:56.449976008 -0300`
idêntico antes e depois de todas as sondas (`/` montado com `relatime`; o atime é
anterior ao mtime, logo uma leitura o teria atualizado).

Nenhum processo Python / SDK Anthropic executou.

`total_cost_usd` no JSON é **estimativa client-side a preço de tabela**, não cobrança:
`hasExtraUsageEnabled=false` / `org_level_disabled` tornam qualquer gasto impossível.

## 5. Payload — composição determinística

O corpo enviado (log de transporte):

    model      : "claude-opus-5"
    messages   : [ 2 blocos ]
    system     : [ 4 blocos ]
    tools      : []                  ← vazio, confirmado no transporte
    max_tokens : 64000
    thinking   : presente, mas thinking_tokens = 0 em todas as sondas
    stream     : true

**Lado USER.** O transcript escrito pelo próprio harness (`P0D`) mostra exatamente
uma mensagem de usuário, com os **39 bytes literais** do arquivo congelado, mais um
único bloco fixo injetado:

    {"type":"total_tokens_reminder","text":"<total_tokens>15000000 tokens left</total_tokens>"}

Constante, 44 caracteres, sem cwd, sem git status, sem data, sem CLAUDE.md,
sem conteúdo de execuções anteriores.

**Lado SYSTEM.** Quatro blocos: o nosso, vindo byte-a-byte de
`--system-prompt-file`, mais três blocos fixos do Claude Code. O conteúdo literal
desses três não é dumpado pelo logger (o inspector do runtime trunca objetos
aninhados), mas a sua **estabilidade está provada empiricamente**:

> P0, P0B e P0D são três processos independentes, com input byte-idêntico, e
> reportaram `input_tokens = 415` nas três vezes.

Com ~84 tokens de conteúdo próprio, o prefixo fixo do Claude Code é de ~331 tokens —
contra ~20.800 tokens de prefixo medidos na Route C (subagentes), uma redução de ~60×.

O prefixo é, portanto, **congelado por versão + configuração**: Claude Code `2.1.251`,
o conjunto exato de flags acima e o conjunto exato de variáveis de ambiente acima.
Qualquer mudança de versão invalida o congelamento e exige nova P0.

**A pergunta metodológica de §7 do briefing responde-se afirmativamente:** as
instruções semânticas e os inputs são injetados de forma determinística e
reproduzível, **sem nenhum LLM parent reescrevê-los** — SYSTEM vem de arquivo por
caminho, USER vem de stdin, e o orquestrador é código.

## 6. Nota sobre P0C

P0C pediu ao modelo que reproduzisse o próprio system prompt. O modelo **recusou**.
Isso é evidência corroborante de que um dos três blocos fixos é um bloco de
identidade/segurança do Claude Code, e confirma que a introspecção por auto-relato do
modelo não é um caminho de prova viável — razão pela qual a prova acima é feita por
captura de transporte e por determinismo de contagem de tokens, não por auto-relato.

## 7. Tráfego auxiliar eliminado

A sonda P0 disparou uma chamada extra a `claude-haiku-4-5` com
`source=generate_session_title`. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`
**elimina-a** (P0B e P0D usaram exclusivamente `claude-opus-5`). A variável passa a
ser obrigatória na execução do MS-001B: nenhuma inferência fora das 18 chamadas.

## 8. Condições de PASS

| # | condição | veredito | evidência |
|---|---|---|---|
| 1 | execução via OAuth Max | **PASS** | `authorization` + beta `oauth-2025-04-20` |
| 2 | zero API key | **PASS** | `x-api-key` ausente; env UNSET |
| 3 | zero leitura de `~/.anthropic_key` | **PASS** | atime inalterado |
| 4 | modelo esperado | **PASS** | `claude-opus-5`, `provider: firstParty` |
| 5 | SYSTEM sentinel no payload | **PASS** | regra existente só no SYSTEM foi obedecida; arquivo passado por caminho |
| 6 | USER sentinel no payload | **PASS** | transcript do harness: 39 bytes literais |
| 7 | sem injeção variável destrutiva | **PASS** | só `total_tokens_reminder` constante; 415 tokens em 3 processos |
| 8 | output exatamente capturável | **PASS** | campo `.result` = bytes exatos |
| 9 | processo encerra independentemente | **PASS** | exit 0, processo novo por chamada |
| 10 | zero PAYG API | **PASS** | §4 |

    MS_001_MAX_PLAN_ROUTE_B_P0_PASS
