# PILOT-MS-000B / ROUND 2 — OPENING RECORD

**Status:** `DECLARED_BEFORE_FIRST_EVALUATIVE_MODEL_CALL_OF_ROUND_2`
**Data:** 2026-08-30 · **Máquina:** `LenovoAIO27ARR9`, ext4
**Rodada:** `ROUND 2` — **nova**. Não reutiliza o Opening Record da Round 1
(`3e251d7cdbf5307aef89840d3b733aad49211fa0c887883710b622e93dd01638`).
**Architecture Freeze:** `6d0eb7dd…` · selo `f35016cb…`
**Round 1:** `INVALID_INSTRUMENT` — `ROUND-1-CLASSIFICATION.md`, preservada byte-a-byte.

> **Nenhum resultado avaliativo da Round 1 é copiado como se fosse da Round 2.**
> Geração, julgamento e métricas pertencem todos a **este** record.
> Alteração de instrumento depois deste ponto **invalida a Round 2**.

---

## 1. CORPUS — inalterado, referenciado por hash

| nível | sha256 |
|---|---|
| `FULL L0` | `43b58271feb0a1d518ae6f81ab29836eb9c7f2bec5eb02e53f70c7bd1eb514ed` |
| `CUT L0` | `85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29` |
| `EVIDENCE.jsonl` | `64853f7ac06a470f09333a80469b38e443ea5ce7aa3aee2e116ea1877059abfd` |
| `SLICE A` (cap 12) | `6d9e718cf5dbb088…` — recomputado no ato |
| `SLICE B` (cap 13) | `2768b11c40836371…` — recomputado no ato |

Mesmos dois sources experimentais: **cap 12** `Managing Version Control with GitHub` (44 ev)
e **cap 13** `Connecting Tools & Deploying Apps via MCP and CLI` (56 ev).
**`SOURCE = CHAPTER`, `scope = PILOT_MS_000B_ONLY`. `KNOWN_DEPENDENT` nos dois.**
Cadeia `FULL → CUT → SLICE → SOURCE PACKAGE` preservada. Bytes **não** duplicados só para
fingir independência: os determinísticos são referenciados por hash.

## 2. MODELO E PARTIÇÃO — inalterados, para permitir comparação

`claude-opus-5` · `THINKING = {"type":"disabled"}` · `max_tokens` 8000.
**Mesma partição da Round 1:** 1 chamada por `(source, run)` para geração; 1 por run para
julgamento. Nenhuma mudança silenciosa de partição.
`prompt_version` `ms000b-r2-claimgen-v1` · `judge_version` `ms000b-r2-entail-v1`.

> O `JUDGE_SYS` foi **fortalecido** em relação à Round 1 para tornar os três estados
> operacionais: *"se a evidência dada não trata do assunto da claim, o estado é
> `NOT_ENTAILED`; se toca o assunto mas é insuficiente para concluir e insuficiente para
> negar, é `INDETERMINATE`"*. **Mudança declarada aqui, antes da execução** — é a
> `CORREÇÃO 3` exigida, não ajuste posterior.

## 3. PLANO DE CHAMADAS — hard cap 24

| etapa | chamadas |
|---|---|
| controles mecânicos (tokenizer, consolidador) | **0** |
| controles do juiz — 5 controles em 1 chamada | **1** |
| geração de claims — 2 sources × 3 runs | **6** |
| julgamento `ENTAILED_BY` — 1 por run, todas as claims | **3** |
| **TOTAL PLANEJADO** | **10 de 24** |

O runner **aborta** antes de ultrapassar o cap.

## 4. CORREÇÃO 1 — TOKENIZER

Pontuação **periférica** removida das pontas; **estrutura interna preservada**.

**Positive equivalence controls** — DEVEM colapsar no mesmo token:
`PEQ-01` `github` `github.` `github,` `(github)` `github:` `github;` `'github'` → `github` ·
`PEQ-02` `repository` e variantes → `repository` · `PEQ-03` `commit` e variantes ·
`PEQ-04` `remote` e variantes.

**Negative controls** — NÃO podem colapsar:
`NEG-01` `knowledge/decision-rules.yaml` ≠ `decision-rules` ·
`NEG-02` `--dangerously-skip-permissions` ≠ `permissions` ·
`NEG-03` `claude.md` ≠ `claude` · `NEG-04` `v0.2.1` ≠ `v0` · `NEG-05` `github.com` ≠ `github`.

**O blocker só entra na avaliação depois que estes controles passarem.**

## 5. CORREÇÃO 2 — ISOLAMENTO

> **Estatística de vocabulário comum está PROIBIDA como prova de exclusividade.**
> `claude`, `code`, `github`, `repository` **não são sentinelas de isolamento.**

Substituído por **controles de proveniência/asserção pré-declarados**, escolhidos **antes**
de qualquer geração da Round 2, a partir da evidência real:

**`ISO-A` (A→B)** — proposição exclusiva do cap 12:
> *"When inspecting a change, the green section shows what is being added and the red
> section shows what is on the left."*
Evidência positiva: `A/EV-0011`. Exclusividade verificada mecanicamente: `green`,
`red section`, `being added` ocorrem nas quotes de A e **não** nas de B.

**`ISO-B` (B→A)** — proposição exclusiva do cap 13:
> *"MCP stands for Model Context Protocol and can be thought of as a USB port for
> artificial intelligence."*
Evidência positiva: `B/EV-0006` e `B/EV-0008`. `mcp`, `model context protocol`, `usb port`
ocorrem nas quotes de B e **não** nas de A.

**O teste exige:** `proposição A + evidência A → ENTAILED` **e**
`proposição A + evidência B → NÃO ENTAILED`, e o espelho.
Isso testa **falsa atribuição**, não ocorrência lexical.
**Nenhuma proposição é escolhida depois de observar a geração.**

## 6. CORREÇÃO 3 — CONTROLES DO JUIZ, BLOQUEANTES

Julgados **antes** de qualquer claim gerada, numa única chamada:

| controle | esperado | por quê |
|---|---|---|
| `JC-POSITIVE` | **`ENTAILED`** | a proposição `ISO-A` segue integralmente de `A/EV-0011` |
| `JC-NEGATIVE` | **`NOT_ENTAILED`** | mesma claim **+ causalidade e um fato de cobrança** que a evidência não sustenta |
| `JC-INDETERMINATE` | **`INDETERMINATE`** | *"a maioria dos desenvolvedores prefere a rich diff"* contra `A/EV-0012`, que menciona a rich difference mas **não** diz preferência |
| `JC-CROSS-A-IN-B` | **`NOT_ENTAILED`** | proposição de A julgada contra evidência de B |
| `JC-CROSS-B-IN-A` | **`NOT_ENTAILED`** | proposição de B julgada contra evidência de A |

> **TRAVA:** se o juiz não devolver **exatamente** esses estados,
> **`PILOT_MS_000B_ROUND_2_INVALID` e PARA antes de julgar as claims geradas.**
> Não se ajusta prompt e repete dentro da mesma rodada.
> Se o juiz aprovar falsa atribuição cross-source: `INVALID_INSTRUMENT`.

## 7. CORREÇÃO 4 — CONSOLIDADOR

Três classes reais, com **precedência declarada**: `INVALID` sobre `FAIL`, porque
**instrumento quebrado não pode reprovar o produto**.

Fixtures sintéticas, testadas antes de abrir: `FX-PASS` → `PASS` · `FX-FAIL` e `FX-FAIL-2`
→ `FAIL` · `FX-KILL` → `FAIL` · `FX-INVALID` e `FX-INVALID-2` → `ROUND_2_INVALID` ·
**`FX-PRECED`** (instrumento **e** produto quebrados) → `ROUND_2_INVALID`.
**Se não distinguir `FAIL` de `INVALID`, a Round 2 não abre.**

## 8. EXECUÇÃO COMPLETA

`RUN-1`, `RUN-2`, `RUN-3` reexecutados por inteiro. **Nenhuma claim ou veredito da Round 1
é reutilizado.**

## 9. SEALED CLAIMS

Regra mantida: **100% das `SEALED_CLAIMS` com `ENTAILED_BY = ENTAILED`.**
Reportados: raw propostas · `ENTAILED` · `NOT_ENTAILED` · `INDETERMINATE` · rejeitadas antes
do selo · seladas.

> **100% `ENTAILED` nas claims reais pode ser válido** — desde que os controles negativo e
> indeterminate tenham sido corretamente rejeitados. **Não se reprova um resultado por ser
> 100%; reprova-se instrumento incapaz de discriminar.**

## 10. BLOCAGEM

Regra estrutural declarada: **≥ 2 tokens de conteúdo compartilhados**, com o tokenizador
corrigido. **Nenhum threshold de redução.**
`BLK-CTRL-01` e `BLK-CTRL-02`, sintéticos e fora da população, **100% têm de sobreviver**.
Reduzir zero preservando controles é **achado de eficiência, não `FAIL`**.

## 11. CRITÉRIOS MANTIDOS, NÃO AFROUXADOS

Identidade · proveniência 100% · preservação de workflow por hash de estrutura · candidate
admission · variância · `COMPILE-TRACE` completo · KILL-1 / KILL-2 / KILL-3 · custo · selo.

- **KILL-1** — camada selada byte-idêntica antes/depois. Mecânico, sem limiar.
- **KILL-2** — `max(sealed)/min(sealed) > 1,5` (teto **medido** do extractor) ⇒ KILL.
- **KILL-3** — qualquer selada sem `ENTAILED_BY = ENTAILED`.

## 12. ISOLAMENTO — critério de PASS

Controles `A→B` e `B→A` corretos · **zero** troca falsa de proveniência · **zero** id
cross-package nu · **nenhuma** claim selada atribuída ao pacote errado.
**Contagem de palavras comuns não é métrica de violação.**

## 13. FORA DE ESCOPO

`MS-001` · corpus de marketing · Operationalization · Router · Skill Pack ·
`SOURCE = chapter` como contrato de produção · `N1–N9` · o `.docx` de 6 h.
`latest wins` continua proibido; nenhum `SUPERSEDES` é produzido.
