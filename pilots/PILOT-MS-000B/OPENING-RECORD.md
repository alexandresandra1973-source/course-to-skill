# PILOT-MS-000B — OPENING RECORD

**Status:** `DECLARED_BEFORE_FIRST_EVALUATIVE_MODEL_CALL`
**Data:** 2026-08-30 · **Máquina:** `LenovoAIO27ARR9`, ext4
**HEAD ao selar:** `f5fce972a00157d730a0b459ddc3528c48339e28`
**Architecture Freeze:** `6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b` · selo `f35016cbedf4617a45a4b03a89acefb01495d6d50651b77065b26c7fd901a0c3`
**Decisões:** `DR-MS-000A-001` (aceitação) · `DR-MS-000B-001` (escopo)

> **Depois deste record, expectativa e metodologia não mudam em reação a resultado.**
> Se o instrumento precisar de correção após a abertura, a rodada é **`INVALID`** e a
> correção vai para rodada nova e explicitamente separada. Não se remenda e continua.

---

## 1. CORPUS E CADEIA DE PROVENIÊNCIA

| nível | sha256 |
|---|---|
| `FULL L0` | `43b58271feb0a1d518ae6f81ab29836eb9c7f2bec5eb02e53f70c7bd1eb514ed` |
| `CUT L0` (pai operacional) | `85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29` |
| `EVIDENCE.jsonl` do P002 | `64853f7ac06a470f09333a80469b38e443ea5ce7aa3aee2e116ea1877059abfd` |
| `CHAPTER SLICE` A e B | computados no ato, gravados no `SOURCE-PROFILE` |

```
FULL L0  →  CUT L0  →  CHAPTER SLICE  →  SOURCE PACKAGE
```

**O chapter slice é artefato NOVO e derivado de 2026-08-30.** Não se finge que sempre
existiu. Os L0 pais são selados e **não são escritos**.

### Boundaries — vindos da própria fonte

| pacote | cap | título | linhas no CUT | tempo | evidências |
|---|---|---|---|---|---|
| **A** | 12 | `Managing Version Control with GitHub` | 1831–2212 | 3.202–3.762 s | 44 |
| **B** | 13 | `Connecting Tools & Deploying Apps via MCP and CLI` | 2213–2574 | 3.767–4.312 s | 56 |

Fronteira = linha `## ` presente na transcrição original. **Nenhuma fronteira inventada.**

## 2. `SOURCE` E INDEPENDÊNCIA

**`SOURCE = CHAPTER`, `scope = PILOT_MS_000B_ONLY`.** Não altera o modelo de produção
(`SOURCE = curso`, `ARTIFACT = aula`). **`source_independence = KNOWN_DEPENDENT`** nos dois,
declarado antes de rodar — mesmo autor, mesma gravação, mesmo curso. **Corroboração entre A
e B não conta como independência**; é reportada em dois campos (`I15`).

**Colisão deliberada:** ambos os pacotes renumeram `local_id` a partir de `EV-0001`,
reproduzindo `N9` sobre corpus real. A resolução é por qualificação `(source_package_hash, local_id)`.

## 3. MODELO, POLICY E PARTIÇÃO

| campo | valor |
|---|---|
| modelo | **`claude-opus-5`** |
| thinking | **`{"type": "disabled"}`** |
| `max_tokens` | 8000 |
| `prompt_version` | `ms000b-claimgen-v1` |
| `judge_version` | `ms000b-entail-v1` |

Determinado sem ambiguidade: é o **mesmo** modelo e a mesma política de thinking já
autorizados em `claude_extractor.py`, `p002_blind_run.py`, `p002_judge.py` e
`p003_apply_step4.py`. Nenhuma troca por modelo "melhor".

**Partição, idêntica nos três runs:**
- **geração de claims:** 1 chamada por `(source, run)` — todas as evidências do pacote numa
  chamada. 2 sources × 3 runs = **6 chamadas**.
- **`ENTAILED_BY`:** 1 chamada por run, julgando **todas** as claims candidatas do run,
  **sem amostra**. 3 runs = **3 chamadas**.
- **relações:** **0 chamadas** — só `IDENTICAL` mecânica (`D15`).

## 4. ORÇAMENTO

**Hard cap: 24 chamadas.** Planejado: **9**. O runner **aborta antes** de ultrapassar.
Tokens por chamada registrados no `COMPILE-TRACE`. **Nenhum limiar monetário inventado.**

## 5. `RAW_PROPOSED_CLAIM` × `SEALED_CLAIM`

Uma claim proposta só vira `SEALED_CLAIM` se, cumulativamente:

1. `evidence_refs` ≠ vazio e todos os ids existem no pacote;
2. os anchors resolvem;
3. a evidência passa pela política de ancoragem;
4. **`CLAIM —ENTAILED_BY→ {EVIDENCE}` sem acréscimo**.

**Critério congelado: 100% das `SEALED_CLAIMS` satisfazem `ENTAILED_BY = ENTAILED`.**
Isso **não** exige que 100% das propostas sejam boas. Proposta que falha é
`REJECT_FROM_SEALED_CLAIM_SET` e **permanece auditável no trace**.

**Reportados separadamente, sem maquiar a taxa bruta:** raw propostas · rejeitadas antes
do selo · seladas · seladas com entailment.

## 6. `ENTAILED_BY` — rubrica pré-declarada

> **Toda afirmação da claim segue do conjunto de evidências referenciado, sem introduzir
> fato, causalidade, condição ou generalização nova?**

Estados: **`ENTAILED`** · **`NOT_ENTAILED`** · **`INDETERMINATE`**.
**`INDETERMINATE` não é admitida como `SEALED_CLAIM`.**
**Semelhança lexical ou substring NÃO é entailment.** Auditadas **todas** as claims do
microcorpus — sem amostra, porque o volume cabe no cap.

## 7. OS TRÊS PREDICADOS DE ANCORAGEM — medidos separadamente (`D7`, `I29`)

| predicado | como é decidido | estados |
|---|---|---|
| `LOCATED_IN` | o span resolve dentro da fatia | `PASS` / `FAIL` |
| `REPRODUCED_FROM` | a quote reaparece verbatim na fatia normalizada | `PASS` / `MISSING` |
| `SUPPORTED_BY` | substância — julgamento, **não medido nesta rodada** | `NOT_APPLICABLE` |

**`MISSING` ≠ `NOT_APPLICABLE`.** Nunca colapsados.

## 8. BLOCAGEM — regra estrutural declarada antes

**Regra: par sobrevive se as duas claims compartilham ≥ 2 tokens de conteúdo** (após
normalização e remoção de stopwords). É **regra estrutural declarada antes de rodar**, não
threshold ajustado. **Nenhum threshold de redução é definido nesta rodada.**

**Controles positivos sintéticos, fora da população, declarados aqui:**

| id | lado A | lado B |
|---|---|---|
| `BLK-CTRL-01` | *The repository must be initialized before pushing commits to github.* | *Authenticate the github repository before deploying through the cli.* |
| `BLK-CTRL-02` | *Commit changes locally before syncing the remote repository.* | *The remote repository connection is configured before the deploy step.* |

**100% dos controles positivos têm de sobreviver.** Se o blocker eliminar um: **`FAIL`**.
Se não reduzir nada: **não é `FAIL`** — é achado de eficiência.

## 9. ISOLAMENTO

Token de conteúdo **exclusivo** de um pacote = presente nas quotes dele e ausente nas do
outro. **Qualquer claim de A carregando token exclusivo de B — ou vice-versa — é falsa
atribuição e `FAIL`.** A fusão pode relacionar; **não pode mover proveniência**.

## 10. PRESERVAÇÃO DE WORKFLOW — critério crítico do DESIGN C

Candidatos source-local (workflow, rule, anti-pattern) são **transportados**, não
reconstruídos. Verificação: **hash canônico da estrutura no Source Package == hash na
travessia até o Fusion Package.**

Ordem dos passos · condições · exceções · `evidence_refs` · `claim_refs` preservados;
**nenhum passo criado ou removido em silêncio**. **PASS = 100% sem alteração não
registrada.** Qualquer reconstrução silenciosa: **`FAIL`**.

## 11. AS TRÊS EXECUÇÕES

`RUN-1`, `RUN-2`, `RUN-3` — mesmos sources, mesmos bytes, mesma partição, mesma config,
mesmo model/policy, mesmos prompts e versionamento, mesmo código.
**A variável observada é a variância geradora.** Divergência de qualquer um desses ⇒
**`INVALID`**.

Medido: raw claims · sealed claims · sobreposição · divergência · máx/mín.

## 12. `COMPILE-TRACE` — bloqueante (`I19`)

Gravado **após cada chamada**, em `out/COMPILE-TRACE.jsonl`, caminho **versionado**.
**Nunca só em `/tmp`** — foi assim que o trace do PILOT-004 se perdeu.

Campos: run · source · purpose · `input_sha256` · **partição** · `prompt_version` ·
modelo pedido e **resolvido** · thinking · `max_tokens` · `output_sha256` · `stop_reason` ·
tokens · timestamp operacional (**registro apenas, nunca identidade**).

**Ausência de trace de qualquer chamada avaliativa: `FAIL`.**

## 13. CRITÉRIOS

**`PILOT_MS_000B_PASS`** exige **todos**: gates válidos · dois Source Packages reais com
hashes distintos · identidade qualificada e **zero id global nu** · provenance **100%**
resolvível · **100%** das sealed `ENTAILED` · workflow preservado · isolamento sem falsa
atribuição · **100%** dos controles do blocker preservados · `COMPILE-TRACE` completo ·
variância dentro do limite · nenhum KILL · outputs persistidos com hash · histórico intacto ·
Drive read-only.

**`PILOT_MS_000B_FAIL`** — id nu cross-package · referência de proveniência quebrada ·
sealed claim sem entailment · workflow reconstruído em silêncio · falsa atribuição ·
controle positivo eliminado · chamada sem trace.

**`PILOT_MS_000B_INVALID`** — Opening Record posterior à primeira avaliação · fixture ou
controle defeituoso · modelo/config/partição divergindo entre runs · instrumento incapaz de
medir o que declara · **hard cap ultrapassado** · corpus/hash inesperado.

### KILL

- **KILL-1** — qualquer geração altera bytes da camada selada abaixo. Comparação por hash
  dos L0 pais e do `EVIDENCE.jsonl` antes/depois. **Mecânico, sem limiar.**
- **KILL-2** — variância da população comparável entre runs excedendo **1,500×**, o teto
  **medido** do extractor. `max(sealed) / min(sealed) > 1.5` ⇒ KILL.
- **KILL-3** — qualquer claim entrando em `SEALED_CLAIMS` sem `ENTAILED_BY = ENTAILED`.

## 14. FORA DE ESCOPO — não implementado nesta rodada

Operationalization · Operational Package produtivo · MTX Applicability · `MTX-POLICY` ·
Router · Skill Pack · progressive loading · vector DB · embeddings · precedência completa ·
arbitragem entre autoridades · `MS-001` · corpus de marketing reservado · o `.docx` de 6 h
(**`NOT AUTHORIZED`**, não extraído, não usado).

**`latest wins` continua proibido.** Nenhum `SUPERSEDES` é produzido nesta rodada.
