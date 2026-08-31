# OPENING RECORD — PILOT-MS-001B — EXECUÇÃO 3

Selado e pushed **ANTES** da primeira chamada semântica da execução 3.
Data: 2026-08-31. Classificação da mudança: **`MODEL_TRANSPORT_RECOVERY`**.

Os Opening Records das execuções 1 e 2 permanecem **intocados**.

---

## 1. Histórico das execuções anteriores

* **Execução 1** — `BLOCKED`. Interrompida por saldo de API em 13/15 chamadas;
  controles 30/30 PASS. Registro: `out-ms001b/MS-001B-EXEC-1-BLOCKED.md`.
  Depois reclassificada quando a partição v1 revelou um par omitido em batch grande.
* **Execução 2** — `BLOCKED`. `HARD STOP — API CREDIT` na **chamada 1**, antes de
  qualquer julgamento. Nenhum dado semântico produzido.
  Registro: `MS-001-FINAL-RECOVERY-BLOCKED.md`, `MS-001B-EXEC-2-RECOVERY-NOTE.md`.

Nenhuma run parcial das execuções 1 ou 2 é reutilizada. A execução 3 começa do zero.

## 2. Decisão externa que motiva a execução 3

    ANTHROPIC PAYG API = PERMANENTLY PROHIBITED FOR THIS PROJECT

O transporte muda; a semântica não. Ver
`../DECISION-RECORD-MS-001B-MODEL-TRANSPORT.md`.

## 3. P0 — prova de transporte

    MS_001_MAX_PLAN_ROUTE_B_P0_PASS

Executada fora do corpus, com fixture sintético, em 2026-08-31.
Prova completa: `../transport-audit/MS-001-P0-ROUTE-B-PROOF.md`.

Evidência central, de nível de transporte: o request enviado carrega header
`authorization` e o beta flag `oauth-2025-04-20`, e **não** carrega `x-api-key` —
que é o header exigido pelo Console pay-as-you-go. `~/.anthropic_key` não foi lida
(atime inalterado). Prefixo fixo do Claude Code determinístico:
`input_tokens = 415` em três processos independentes com input byte-idêntico.

## 4. Claude Code version

    2.1.251 (Claude Code) · instalação native · user-agent claude-cli/2.1.251 (external, sdk-cli)

Mudança de versão **invalida** o congelamento e exige nova P0 antes de qualquer
chamada.

## 5. Contrato de invocação — congelado

    env obrigatório    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
    env proibido       ANTHROPIC_API_KEY · ANTHROPIC_AUTH_TOKEN · ANTHROPIC_BASE_URL
    (UNSET, verificado ANTHROPIC_CUSTOM_HEADERS · CLAUDE_CODE_OAUTH_TOKEN
     em runtime)       CLAUDE_CODE_USE_BEDROCK · CLAUDE_CODE_USE_VERTEX
                       AWS_BEARER_TOKEN_BEDROCK

    claude -p --model claude-opus-5
             --system-prompt-file <SYSTEM congelado>
             --tools ""
             --disable-slash-commands
             --strict-mcp-config
             --no-session-persistence
             --permission-mode dontAsk
             --setting-sources ""
             --settings '{"alwaysThinkingEnabled":false}'
             --output-format json

    USER: por stdin, bytes exatos do arquivo congelado.

### Proibição de `--bare`

`--bare` **nunca** pode ser usado nesta execução. A documentação é explícita: em bare
mode o Claude Code nunca lê credenciais OAuth nem o keychain, e exige
`ANTHROPIC_API_KEY`. Usar `--bare` converteria a Route B em Route A (PAYG) de forma
silenciosa. O orquestrador falha fechado se a flag aparecer.

Também proibidos: `--continue`, `--resume`, reuso de sessão, `apiKeyHelper`,
extra usage pago, Console API, Bedrock/Vertex/Foundry.

## 6. Isolamento por processo fresh

Cada uma das 18 chamadas é um **processo `claude -p` novo**, que nasce, responde e
morre. Não há herança de julgamento anterior, de estado conversacional, nem de
resultados de outra run. O orquestrador (`run_ms001b_routeB.py`) é código
determinístico: prepara os inputs congelados, dispara, persiste o raw e valida
mecanicamente. **Nenhum LLM parent** reescreve prompt, Claims, Evidence, pair payload
ou output.

Injeção residual do harness, medida e aceita: um único bloco constante do lado USER,
`<total_tokens>… tokens left</total_tokens>`, e três blocos fixos do lado SYSTEM,
congelados por versão + configuração (§3, §4).

## 7. Contratos semânticos — INALTERADOS

O SYSTEM montado pela Route B tem sha256
`37dc021103d168d6a86ee45ee4068979de866f8cd4a89e7715bac6888f7bf1e9`,
**idêntico** ao `system_sha256` registrado pela execução 1 sob o transporte antigo
(SDK Python). O instrumento semântico é o mesmo, byte a byte.

| artefato | sha256 |
|---|---|
| `ms001b/RELATION-PROMPT-v2.txt` | `0324219d1f62bbba9578894c41599794e7563be4a3d952d787a9ee61c5c34500` |
| `ms001b/RELATION-SCHEMA-v1.json` | `35c5814841711d4c92b9dc7e869b01902405bd40944a48720ad2d3f4c4db1973` |
| `ms001b/RELATION-TAXONOMY-v1.txt` | `377879d2cd6a3e5460279466842b7549eda3898ab070b13aae64ab7e0dd3f5eb` |
| `ms001b/JUDGE-CONTROLS-J1-J10.json` | `761785cd26e07764ad06ab09fdd512ede78a24dbd7d70c5a09e867a8ad1879ff` |
| `ms001b/PAIRSET-MS001B-V1.json` | `e576a17ff954d3197c3168ed82fc26605603f565c7fe24d2671cdd59c54480b6` |
| `ms001b/PAIR-INPUTS-MS001B.json` | `f1d05aca8b13c3f2686c3a80463289b1d969565eea9d3293dc1b61a78aa657b0` |
| `ms001b/PARTITION-MS001B-v2.json` | `62c3fccae8b4acdff984e68bce9e33499e37bea94daec813f6eff6835538debc` |
| `ms001b/BLOCKED-TRACE-MS001B-V1.json` | `ef4413e85b5560a2c4abad0a62695c5295be136d3fad427629d03872aebe5a16` |
| `ms001b/FUSION-CONFIG-MS001B.json` | `0b4fd07ea7492ea5de8ee438152415067bf6362e88f4440ad312f2f0bb8863bd` |
| `lib/relation_validate.py` | `7283a123dd59dda2205a1e47a486fef94f279eed4ef1197fb273b1350cbb6dd5` |
| `run_ms001b_routeB.py` | `0af3275b2c1ccba9accb79214b28e440b0b5525b2449ceacca14e089509a0232` |

    PAIRSET_HASH = a0b116d93f754576cf8fbbbf6eb1757b2837b7ea18b415f8e2bce30c1ee517f5
    pares        = 97

Não alterados e não reabertos: dois Source Packages, blocker v0.3, V1, taxonomia,
schema, prompt semântico, J1–J10, Evidence, Candidate transport, stability policy,
Fusion semantics.

Canários pré-modelo reexecutados antes desta selagem: **65/65 PASS**
(22 pré-modelo + 7 de batch + 36 mecânicos).

## 8. Partição — 25 / 25 / 25 / 11 / 11

    BATCH-1   25 pares
    BATCH-2   25 pares
    BATCH-3   25 pares
    BATCH-4A  11 pares
    BATCH-4B  11 pares
    ------------------
    total     97 pares exatos

## 9. Controles J1–J10

Cada run abre com **uma** chamada de controle com os 10 controles J1–J10.
Se o controle falhar, a run é `INVALID` e **os batches não são queimados**.

## 10. Três runs independentes

    RUN-1 · RUN-2 · RUN-3

Cada run: 1 controle + 5 batches = 6 chamadas. Total planejado: **18 chamadas**.
`HARD_CAP = 18`, `RETRY = 0`. Nenhuma run tem conhecimento das outras.

## 11. Modelo

    requested   claude-opus-5
    resolved    verificado em TODAS as chamadas via modelUsage do JSON de saída;
                resolved != claude-opus-5  ->  MS_001B_INVALID
    thinking    desligado via alwaysThinkingEnabled:false; thinking_tokens verificado
    max_tokens  64000 (teto do harness; não configurável — era 8000 na política v1)
    temperature omitida

Ver `MODEL-POLICY-MS001B-v2.txt`.

## 12. Validação — contratos mantidos

`lib/relation_validate.py` **inalterado**: schema estrito, `expected_pair_count`,
`expected_pair_ids`, igualdade exata de evidence por lado, sem faltantes, sem
duplicatas, sem desconhecidos, sem drift de pairset, campos proibidos rejeitados.
Nenhuma correção semântica de output é permitida.

## 13. Limite do plano Max

Se o plano atingir o limite durante a execução: **não** recorrer à API, **não**
habilitar extra usage pago. Persistir o estado e classificar

    MS_001_PAUSED_MAX_PLAN_USAGE_LIMIT

Pausa operacional, não `INVALID` metodológico. A retomada só pode ocorrer conforme
este Opening Record. **Contrato de retomada, pré-declarado:** uma run interrompida no
meio dos batches é descartada por inteiro e reexecutada do controle; nenhum batch
parcial é reaproveitado, e o `HARD_CAP` de 18 conta apenas chamadas de runs completas.

## 14. Zero PAYG

    PAYG_API_USED = 0

Verificado antes de cada chamada pelo guard de ambiente do orquestrador, que aborta
se qualquer variável proibida estiver definida.
