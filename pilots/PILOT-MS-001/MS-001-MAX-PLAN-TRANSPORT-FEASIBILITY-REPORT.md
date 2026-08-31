# MS-001 — MAX PLAN TRANSPORT FEASIBILITY REPORT

Data: 2026-08-31 · Escopo: **diagnóstico de transporte/autenticação apenas**.
MS-001B **NÃO** foi executado. J1–J10, os 97 pares, as 18 chamadas, Fusion, Opening
Records, Source Packages, blocker e pairset permanecem intocados.

---

## 1. Claude Code version

    2.1.251 (Claude Code)
    binário: /home/mtx/.local/share/claude/versions/2.1.251  (ELF nativo)
    installMethod: native

## 2. Current auth mechanism

Sessão autenticada por **OAuth da assinatura Claude (claude.ai)**, não por API key.

    ~/.claude/.credentials.json → claudeAiOauth
      subscriptionType   = "max"
      rateLimitTier      = "default_claude_max_20x"
      scopes             = user:file_upload, user:inference, user:mcp_servers,
                           user:profile, user:sessions:claude_code
    ~/.claude.json → oauthAccount
      organizationType         = "claude_max"
      organizationRateLimitTier= "default_claude_max_20x"
      billingType              = "google_play_subscription"
      hasExtraUsageEnabled     = false
      cachedExtraUsageDisabledReason = "org_level_disabled"

Nenhum token/segredo foi impresso ou copiado em nenhum momento.

## 3. API-key environment status

    ANTHROPIC_API_KEY        UNSET
    ANTHROPIC_AUTH_TOKEN     UNSET
    ANTHROPIC_BASE_URL       UNSET
    ANTHROPIC_MODEL          UNSET
    ANTHROPIC_SMALL_FAST_MODEL UNSET
    CLAUDE_CODE_OAUTH_TOKEN  UNSET
    CLAUDE_CODE_USE_BEDROCK  UNSET
    CLAUDE_CODE_USE_VERTEX   UNSET
    AWS_BEARER_TOKEN_BEDROCK UNSET
    ANTHROPIC_CUSTOM_HEADERS UNSET

Perfis de shell (`.bashrc`, `.bash_profile`, `.profile`, `.zshrc`, `/etc/environment`):
**zero** referências a Anthropic/Claude. Nenhuma configuração força Console/API:
`apiKeyHelper` ausente em todos os settings; `/etc/claude-code/managed-settings.json`
ausente; `.claude/settings.json` do projeto ausente.

Prioridade de auth confirmada na documentação oficial (`/docs/en/env-vars`):

> **ANTHROPIC_API_KEY** — "When set, this key is used instead of your Claude Pro, Max,
> Team, or Enterprise subscription even if you are logged in. In non-interactive mode
> (`-p`), the key is always used when present."

Ou seja: uma `ANTHROPIC_API_KEY` de ambiente **substituiria** a assinatura. Ela **não
está definida** neste ambiente e **nada foi apagado** nesta rodada. Requisito
operacional permanente: manter `ANTHROPIC_API_KEY` UNSET em toda execução MS-001B.

## 4. `~/.anthropic_key` role

    EXISTE · 109 bytes · modo 600 · mtime 2026-08-27 15:19:34

Papel: **exclusivamente dos runners Python.** `run_ms001b.py:64` faz
`pathlib.Path("~/.anthropic_key").read_text()` → `anthropic.Anthropic(api_key=key)`.

O binário do Claude Code **não conhece esse caminho**: varredura de `strings` sobre os
214 MB do executável → `anthropic_key` = **0 ocorrências** (contra `ANTHROPIC_API_KEY`
68, `apiKeyHelper` 45, `claudeAiOauth` 7). O arquivo **não interfere** no Claude Code.

## 5. ROUTE A classification — DIRECT ANTHROPIC SDK

    PAYG_API — PROIBIDA
`anthropic.Anthropic(api_key=<~/.anthropic_key>)`. É o caminho atual do
`run_ms001b.py`. Cobrança Console pay-as-you-go. **Não usada nesta auditoria.**

## 6. ROUTE B classification — `claude -p` / Agent SDK CLI

    PLAN_BILLED_TODAY · APROVADA COM GATE DE REVERIFICAÇÃO

Fonte oficial (Anthropic Help Center, "Use the Claude Agent SDK with your Claude plan",
atualização de 2026-06-15):

> "We're pausing the changes to Claude Agent SDK usage described below. For now,
> nothing has changed: Claude Agent SDK, `claude -p`, and third-party app usage still
> draw from your subscription's usage limits."

O crédito mensal separado de Agent SDK **não está ativo**. Portanto `claude -p` **não**
está hoje associado a Agent SDK credit, nem a Console/API, nem a cobrança separada — ele
consome a franquia **normal** do Claude Max. Pelo próprio teste da Seção 8 do briefing,
não se classifica como `NOT_APPROVED_BY_USER`.

Risco declarado e registrado: a mudança está **pausada, não cancelada** ("We'll share an
update before anything takes effect"). Gate obrigatório: reverificar esse artigo
imediatamente antes de cada execução.

Proibição operacional absoluta nesta rota: **nunca usar `--bare`**. A documentação é
explícita — "bare mode doesn't use your subscription login … In bare mode, Claude Code
never reads OAuth credentials or the system keychain", exigindo `ANTHROPIC_API_KEY`.
`--bare` converteria a Route B em Route A.

## 7. ROUTE C classification — interactive Claude Code / built-in subagents

    PLAN_BILLED · VIÁVEL · adotada como FALLBACK, não como primária

Usa a autenticação OAuth Max desta sessão, conta contra os limites do plano
(`/usage` atribui consumo a "skills, subagents, plugins"), permite contexto isolado e
fixação de modelo. Rebaixada a fallback por três limitações metodológicas frente à
Route B (detalhe em §14): prefixo de sistema do harness não controlável, input entregue
por transcrição do parent, e ausência de `--system-prompt` por invocação.

## 8. Max/OAuth evidence

* `.credentials.json` contém **apenas** `claudeAiOauth` (accessToken/refreshToken/
  expiresAt/scopes/subscriptionType/rateLimitTier). Nenhum campo de API key.
* Escopo `user:inference` presente — a inferência desta sessão é servida pela assinatura.
* `subscriptionType = "max"`, `rateLimitTier = "default_claude_max_20x"`.
* Nenhuma variável de ambiente ou setting capaz de desviar para Console/API.

## 9. Billing-path evidence

Duas travas independentes tornam gasto PAYG **impossível** neste ambiente:

1. **Sem credencial de API no caminho do Claude Code.** `ANTHROPIC_API_KEY` UNSET,
   `ANTHROPIC_AUTH_TOKEN` UNSET, `apiKeyHelper` não configurado, `ANTHROPIC_BASE_URL`
   UNSET. Sem uma dessas, o Claude Code não tem como falar com o Console.
2. **Extra usage desligado na origem.** `hasExtraUsageEnabled = false` com
   `cachedExtraUsageDisabledReason = "org_level_disabled"`. Não há usage credits: ao
   atingir o limite do plano, o Claude Code **para**, não gasta.

Consequência: mesmo no cenário em que a Anthropic despause a separação de billing do
Agent SDK, o resultado seria **bloqueio por limite**, jamais cobrança PAYG.

## 10. Isolation capability

**Route B (primária) — isolamento por processo, o mais forte disponível.**
Cada julgamento é uma invocação `claude -p` própria: processo novo, contexto novo, sem
`--continue`/`--resume`, com `--no-session-persistence`. Um julgamento não tem como ver
outro julgamento, outro batch ou outra run. Com `--tools ""` o modelo **não tem
ferramenta alguma** — não pode ler o repositório, nem os outputs de runs anteriores.

**Route C (fallback)** — subagentes têm contexto fresco e isolado por design
("Each subagent starts with a fresh, isolated context window. It doesn't see your
conversation history…"), mas herdam CLAUDE.md, git status e roster de irmãos, e
carregam ferramentas por padrão.

## 11. Model-selection capability

Route B: `--model claude-opus-5` (nome completo aceito). Verificação mecânica ao vivo do
modelo efetivamente servido via `--output-format json` (per-model cost breakdown) ou
`--output-format stream-json` (evento `system/init` reporta o modelo) — preservando a
regra `resolved != claude-opus-5 → MS_001B_INVALID` sem chamada extra de resolução.

`thinking = disabled`: preservável via chave de settings **`alwaysThinkingEnabled: false`**
(confirmada em `/docs/en/settings-reference` e presente no binário instalado).

`max_tokens = 8000`: **não configurável**. Trata-se de teto, não de semântica; truncamento
já é capturado fail-closed pelo `relation_validate.py`.

## 12. Raw-output persistence capability

Route B: byte-exato e **sem LLM no caminho**. `claude -p … --output-format json >
RAW.json`; o texto do julgamento sai em `.result`, extraído por `jq`/python. O parent é
um script, não um modelo.

Route C: o harness grava o transcript JSONL completo do subagente em
`…/tasks/<agentId>.output`, do qual o texto pode ser extraído mecanicamente — mas a
**entrada** dependeria de transcrição pelo parent LLM (ver §14).

## 13. Three-run independence feasibility

Route B satisfaz plenamente. RUN-1/2/3 = 3 conjuntos disjuntos de processos, disparados
por um script determinístico a partir dos arquivos congelados. Zero conhecimento
cruzado: nenhum processo recebe, lê ou pode alcançar o resultado de outro.

## 14. Methodological impact

Confronto com os 17 requisitos, sob Route B:

| # | Requisito | Status |
|---|---|---|
| 1 | Source Packages byte-idênticos | **PRESERVADO** — intocados, lidos de arquivo |
| 2 | blocker v0.3 | **PRESERVADO** |
| 3 | V1 | **PRESERVADO** |
| 4 | PAIRSET_HASH | **PRESERVADO** |
| 5 | 97 pares | **PRESERVADO** |
| 6 | taxonomia atual | **PRESERVADO** |
| 7 | mesmo prompt semântico | **PRESERVADO, pendente gate P0** — `[SYSTEM]` via `--system-prompt-file`, `[USER]` via stdin, ambos byte-a-byte do arquivo congelado |
| 8 | mesmo schema | **PRESERVADO** (schema segue embutido no prompt; **não** usar `--json-schema`) |
| 9 | J1–J10 | **PRESERVADO** |
| 10 | três runs independentes | **PRESERVADO** |
| 11 | mesmo model family/config | **PRESERVADO NA MEDIDA SUPORTADA** — modelo e thinking sim; `max_tokens` não |
| 12 | isolamento entre calls/batches | **PRESERVADO E REFORÇADO** (isolamento por processo) |
| 13 | raw textual output preservável | **PRESERVADO** (redirecionamento de shell) |
| 14 | exatamente um resultado por pair | **PRESERVADO** (`relation_validate.py` inalterado) |
| 15 | evidence-check validation | **PRESERVADO** (mecânico, sem API) |
| 16 | zero conhecimento cruzado entre runs | **PRESERVADO** |
| 17 | zero PAYG API | **PRESERVADO** (§9, dupla trava) |

Por que a Route C foi rebaixada a fallback — três defeitos que a Route B não tem:

1. **Prefixo de sistema não controlável.** O teste mínimo de um prompt trivial consumiu
   ~20.8k tokens, evidenciando um system prompt do harness de milhares de tokens,
   prepended a cada julgamento, não documentado, não hasheável e que muda a cada release
   do Claude Code. O instrumento deixaria de ser selável e reproduzível.
2. **Entrada por transcrição.** O `prompt` da ferramenta Agent é emitido token a token
   pelo parent LLM. Um BATCH de 25 pares seria milhares de tokens de JSON re-digitados —
   destruindo a identidade byte-a-byte dos requisitos 1/5/7/8.
3. **Sem `[SYSTEM]`/`[USER]` por invocação** e sem desligar thinking por subagente.

Nenhum desses defeitos existe na Route B, onde o orquestrador é um script shell: ele
prepara inputs congelados, dispara, persiste o raw e valida mecanicamente — e é
**estruturalmente incapaz** de reinterpretar ou corrigir julgamentos.

**Gate P0 — única verificação pendente, custo monetário zero.** Uma invocação de sonda
`claude -p` com `--debug api --debug-file`, fora do corpus MS-001, para inspecionar o
corpo da requisição efetivamente enviada e confirmar que, com `--system-prompt-file` +
`--tools ""` + `--strict-mcp-config` + `--setting-sources`, o payload contém **apenas**
o SYSTEM e o USER congelados, sem seções dinâmicas do harness (cwd, git status,
CLAUDE.md, roster). A documentação sustenta isso — `--system-prompt` substitui
integralmente o prompt padrão, e `--exclude-dynamic-system-prompt-sections` é descrito
como "ignored with --system-prompt" — mas a prova byte-a-byte exige essa sonda. Ela
**não** foi executada: a Seção 7 do briefing autorizou **um único** teste mínimo, já
consumido pela Route C.

## 15. Opening Record recovery — possível

Sim, e a mudança é estritamente `MODEL_TRANSPORT_RECOVERY`. Não muda corpus, model
semantics, pairset, blocker, taxonomy nem relation policy.

Documentos que precisariam de novo registro (os atuais estão selados por SHA256 e **não
devem ser editados**):

* `ms001b/MODEL-POLICY-MS001B.txt` → **nova** `MODEL-POLICY-MS001B-v2.txt`. Muda apenas:
  `credencial ~/.anthropic_key` → OAuth Max; `SDK anthropic 0.121.0` → `claude -p 2.1.251`;
  `max_tokens 8000` → não configurável (teto do harness);
  `thinking disabled` → mantido via `alwaysThinkingEnabled: false`.
* `ms001b/OPENING-RECORD-MS-001B-EXEC-2.md` §6 (MODELO) e a cláusula
  "HARD STOP — API CREDIT" → **novo** `OPENING-RECORD-MS-001B-EXEC-3.md`, selado e
  pushed **antes** da primeira chamada, como nas execuções anteriores.
* `SHA256SUMS-INSTRUMENTS.txt` / `SHA256SUMS-EXEC-2.txt` → novo `SHA256SUMS-EXEC-3.txt`.
* `run_ms001b.py` → **novo** runner de transporte (shell/python orquestrando `claude -p`),
  reusando `lib/relation_validate.py` sem alteração. O runner atual fica preservado como
  registro histórico da Route A.

Inalterados e não reabertos: os dois Source Packages, `PAIRSET-MS001B-V1.json`,
`PAIR-INPUTS-MS001B.json`, `RELATION-PROMPT-v2.txt`, `RELATION-SCHEMA-v1.json`,
`RELATION-TAXONOMY-v1.txt`, `JUDGE-CONTROLS-J1-J10.json`, `PARTITION-MS001B-v2.json`,
`BLOCKED-TRACE-MS001B-V1.json`, `FUSION-CONFIG-MS001B.json`.

## 16. Minimal plan-only test performed

**Um** teste, fora do corpus MS-001, pela Route C (subagente isolado, modelo `opus`):

    prompt   : Return exactly: MAX_PLAN_TRANSPORT_OK
    resultado: MAX_PLAN_TRANSPORT_OK
    tool_uses: 0 · duration: 1633 ms · subagent_tokens: 20813

Prova de que não houve PAYG (evidências em `transport-audit/PRE_TEST.txt` e
`POST_TEST.txt`):

* `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_BASE_URL` = UNSET antes e depois.
* `~/.anthropic_key` **não foi lido**: atime idêntico antes e depois —
  `2026-08-30 03:19:56.449976008 -0300` (`/` montado com `relatime`; uma leitura teria
  atualizado o atime, pois o anterior é mais velho que o mtime).
* Nenhum processo do runner Python executou (`ps` antes e depois: nenhum `run_ms001`,
  nenhum processo `anthropic`).
* O binário do Claude Code não contém a string `anthropic_key` (0 ocorrências em 851.307
  linhas de `strings`), logo não tem como lê-lo.
* A execução ocorreu dentro desta sessão Claude Code, autenticada por
  `claudeAiOauth.subscriptionType = "max"`.

O gate P0 da Route B (§14) **não** foi executado.

## 17. ZERO PAYG API USED

**Confirmado explicitamente.** Nenhuma chamada à Anthropic API pay-as-you-go foi feita
nesta auditoria. Nenhuma recarga de saldo, nenhum auto-recharge, nenhuma troca para
outra API paga, nenhuma leitura de `~/.anthropic_key`. Todo consumo de modelo desta
rodada — a sessão e o único teste mínimo — correu sobre a assinatura Claude Max.

## 18. Repo writes

Apenas artefatos novos de diagnóstico; nada existente foi alterado:

    pilots/PILOT-MS-001/MS-001-MAX-PLAN-TRANSPORT-FEASIBILITY-REPORT.md   (este arquivo)
    pilots/PILOT-MS-001/transport-audit/PRE_TEST.txt
    pilots/PILOT-MS-001/transport-audit/POST_TEST.txt

Nenhum commit, nenhum push. Opening Records, Source Packages, blocker, pairset,
instrumentos e runners: **intocados**.

## 19. Drive writes

**Nenhuma.** O conector Google Drive não foi usado. (Nota operacional: o MCP
"Bridge MTX Lab" falhou ao conectar nesta sessão — HTTP 502 no endpoint; é falha de
conexão, não ausência de configuração.)

## 20. Final classification

    MS_001_MAX_PLAN_TRANSPORT_FEASIBLE

Rota primária: **ROUTE B — `claude -p` sobre OAuth Max, sem `--bare`, sem API key.**
Rota de fallback: ROUTE C (subagentes), metodologicamente inferior.
Gate único antes de qualquer execução: **P0** (§14) mais a reverificação da política de
billing do Agent SDK (§6). Ambos de custo monetário zero.

MS-001B **não** foi executado e permanece congelado no estado atual.

---

## ADENDO 2026-08-31 — P0 EXECUTADA

O gate P0 descrito em §14 foi autorizado e executado. Resultado:

    MS_001_MAX_PLAN_ROUTE_B_P0_PASS

Prova completa em `transport-audit/MS-001-P0-ROUTE-B-PROOF.md`. Achados que corrigem
ou refinam este relatório:

* O `--debug api` **não** dumpa corpos; a captura de transporte foi obtida com
  `ANTHROPIC_LOG=debug`, que expôs headers e esqueleto do payload.
* Prova direta de billing path: header `x-api-key` **ausente**, `authorization`
  presente, beta flag `oauth-2025-04-20`.
* O prefixo fixo do Claude Code é de ~331 tokens (não removível, mas determinístico:
  `input_tokens=415` em três processos independentes com input idêntico).
* Única injeção do lado USER: `<total_tokens>… tokens left</total_tokens>`, constante.
* `--settings '{"alwaysThinkingEnabled":false}'` funciona: `thinking_tokens=0`.
* `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` elimina uma chamada auxiliar a
  `claude-haiku-4-5` (`generate_session_title`) — passa a ser obrigatória.
* `stop_reason` **está** disponível no JSON de saída, ao contrário do que este
  relatório supunha em §11.
