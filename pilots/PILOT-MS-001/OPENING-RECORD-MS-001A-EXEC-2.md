# OPENING RECORD — `PILOT-MS-001A` **EXECUÇÃO 2**

**Selado e pushed ANTES da primeira chamada de modelo da Execução 2.** Data: 2026-08-30.
Artefato **aditivo**: o `OPENING-RECORD-MS-001A.md` da Execução 1
(`6085247024692705032c7e97f697f5658597e1a8997976ec8167187de5e924f7`) **não é editado**.

## 0. EXECUÇÃO 1 — FECHADA

```
EXEC_1   calls = 2   status = INVALID   motivo = ENTAILMENT_INSTRUMENT_DIVERGENCE
```

Preservada em `MS-001A-EXEC-1-INSTRUMENT-INVALID.md`
(`e4cd6118ceeceeed785f5e1b11874a6031a46f3135c91b678f1dc58d016529e9`), com os raw das duas chamadas em `out/raw/`.
**Não será retomada.** Suas chamadas **não** são reutilizadas como controles da Execução 2.

## 1. SUPERSEDED PARA A EXECUÇÃO 2

| artefato | sha256 | estado |
|---|---|---|
| `ENTAILMENT-PROMPT-v1.txt` | `70bd6dacb792e872feb8846e1699efc047c8b91ab16b2682a78f781dd6ee989a` | **SUPERSEDED** — preservado, não apagado |
| `JUDGE-CONTROLS-JE.txt` (v1) | `5593dd0c0b0762d1491f38830aa3882f5871d433c1593f05d77242dd2b2348b3` | **SUPERSEDED** — preservado, não apagado |
| semântica ambígua de `INDETERMINATE` da v1 | — | **SUPERSEDED** |

## 2. ATIVOS NA EXECUÇÃO 2

| artefato | sha256 |
|---|---|
| `instruments/ENTAILMENT-PROMPT-v2.txt` | `762fdd82c09e5fa02e80d8278774fbe31b4e42a72acf752901a7fba6ba6e0ff5` |
| `instruments/JUDGE-CONTROLS-JE-v2.txt` | `9d5e368981ad87100036e721eda5cee8ce30b0f1aba094c7f3921337ea991b84` |
| `instruments/ENTAILMENT-SCHEMA-v2.json` **(inalterado)** | `b31d70083f300b1e8e05b13849720eb42d7f993bd539ab029db305f5fdaf4c07` |
| `lib/entail_validate.py` | `74e317e94deedc2cc3e338e8a8877afae94b6775f0891cc3afe97aac1457f7ea` |
| `MS-001A-ENTAILMENT-RECOVERY-NOTE.md` | `c4bf10faee2d7af48430c18be0f4b29c4590c2bab06ed25fa8acb7b6202c88cc` |

## 3. BYTE-IDÊNTICOS — herdados da Execução 1 sem alteração

| artefato | sha256 |
|---|---|
| corpus B | `2a6ab098868e0714e5d4bc5cebb8018216d78f0243ee890b2c531516fbda7862` |
| corpus C | `ed967fae27146d9aa9cc45769672f751d8eb199bc6ed7564bbb5fdb4a226fab7` |
| `FROZEN-SLICES.json` | `0460dd5fd0107fac5bc073c160b92b137ee17b2de9d599cae3b681fc3f7d244e` |
| `EXTRACTION-PROMPT-v1.txt` | `2e4e316859fee250936a6c5dfdc12821396dc80e0f46eafe7392f8817acb83c5` |
| `EXTRACTION-SCHEMA-v1.json` | `d100354c7ecc300e87f5a059970eea10903789137569eecb49e8da3bbddd2f24` |
| `EXTRACTOR-CONTROLS-EC.txt` | `a37e16a531ce3700ba6a25add59d06eb8184be83e2e29a9e091c14da84efe591` |
| `ID-DERIVATION-v3.txt` | `9687f75e85acd23f153ac5b37cb0f70bdfbbd0a8678c6b91b073dbe04e5e915d` |
| `lib/builders.py` | `38763c6e6cef5afc7bc2e3aa380463ca121283ab2a24648fc5fe3bff41d7ce3c` |
| `lib/identity.py` | `ede48d1f1458f82e2f697af9a221a78c054623028eb441f673d382cc1a323d2b` |
| `lib/validate.py` | `0faed47838971cc70d23ac307e39559abef3d0cc97d08ae4964c2a0f87fe4a32` |
| `lib/gate.py` | `8d6e037e6735a73fad74a4ecd1f274c1e6b5090c0da65f3e94994e24b4baea17` |
| `lib/package.py` | `59f0096b8fe5423a934e4a7c7b10c29382ecb57acfff4fd75365375917b7d3ca` |

Evidence `N=4`, anchors, identidade/dedup, provenance states, contrato de package e
verificador de selo: **inalterados**.

## 4. SEMÂNTICA CONGELADA DAS TRÊS CLASSES

**`ENTAILED`** — a Evidence sustenta a Claim inteira: conteúdo principal, qualificadores,
condições e escopo, sem acréscimo material não suportado.

**`NOT_ENTAILED`** — quatro casos: **(A)** a Evidence contradiz positivamente ·
**(B)** a Claim acrescenta ou generaliza conteúdo material não sustentado ·
**(C)** a Evidence é de assunto/objeto diferente ·
**(D)** a Evidence é **silenciosa** sobre um atributo factual afirmado, sem expressar
incerteza sobre ele.

**`INDETERMINATE`** — somente quando a Evidence pertinente deixa a proposição
**explicitamente** ambígua, incerta, dependente de alternativa não resolvida ou
inconclusiva. **Não é "não achei"; é "a fonte declara a questão em aberto".**

> **`SILÊNCIO ≠ INDETERMINATE`.**

## 5. CONTRATO ÚNICO DE SAÍDA DO JUIZ

Por Claim, **exatamente** quatro campos:

```json
{"claim_id":"...","judgment":"ENTAILED|NOT_ENTAILED|INDETERMINATE",
 "entail_why":"...","evidence_refs_checked":["EV-...."]}
```

**Proibidos:** `temporary_claim_id` · `state` · `why` · aliases · campos adicionais.

**Completude:** todos os `claim_id` enviados, cada um **exatamente uma vez**, zero
desconhecida, zero omitida.

**`evidence_refs_checked`:** `set(checked) == set(enviadas)` — **igualdade, não
subconjunto**. Códigos distintos: `E19_JUDGE_ADDED_EVIDENCE` ·
`E27_JUDGE_OMITTED_EVIDENCE` · `E26_FOREIGN_EVIDENCE`.

## 6. CONTROLES `JE1`–`JE5` — uma única Call 2

| # | fixture | esperado |
|---|---|---|
| `JE1` | exigência de token, claim igual | **`ENTAILED`** |
| `JE2` | *"para quem está começando"* → *"para todos os usuários"* | **`NOT_ENTAILED`** (B) |
| `JE3` | Evidence de Redis, Claim de Evolution API | **`NOT_ENTAILED`** (C) |
| `JE4` | fonte **declara** não estar definido se X é obrigatório | **`INDETERMINATE`** |
| `JE5` | Evidence sobre VPS, Claim sobre exigência de 4 GB de RAM | **`NOT_ENTAILED`** (D) |

**Portão de discriminação negativa:** Call 2 só passa com os **cinco exatos**. Qualquer
divergência → `MS_001A_EXEC_2_INSTRUMENT_INVALID` e **PARA**. **Não reinterpretar depois.**

`JE5` é o par de contraste de `JE4` e existe para provar mecanicamente que silêncio não é
indeterminação.

## 7. CANÁRIOS MECÂNICOS DO VALIDADOR — já executados, 11/11 PASS

`EO0` referência · `EO1` claim omitida · `EO2` duplicada · `EO3` desconhecida ·
`EO4` campo extra · `EO5` enum inválida · **`EO6` formato antigo da v1** ·
`EO7` evidence acrescentada · `EO8` omitida · `EO9` estrangeira · `EO10`
`evidence_refs_checked` ausente. Registro: `out/entail-validator-canaries.json`.

Os 36 canários mecânicos e o dry-run de selo 8/8 da Execução 1 **permanecem válidos** — seus
instrumentos são byte-idênticos.

## 8. PLANO DE CHAMADAS DA EXECUÇÃO 2

```
call 1     EXTRACTOR MODEL CONTROL     EC1-EC6      (reexecutado, nao reaproveitado)
call 2     ENTAILMENT JUDGE CONTROL    JE1-JE5 v2
call 3     extraction SL-B-01
call 4     extraction SL-B-02
call 5     extraction SL-B-03
call 6     extraction SL-C-01
call 7     extraction SL-C-02
call 8     extraction SL-C-03
call 9     entailment MS001-SRC-B
call 10    entailment MS001-SRC-C

EXEC_2: PLANNED = 10 · HARD_CAP = 10 · RETRY = 0 · executed_calls <= 10
call 11 -> MS_001A_EXEC_2_INVALID
```

A call 1 é também a verificação de resolução: `resolved_model != claude-opus-5` →
`MS_001A_EXEC_2_INSTRUMENT_INVALID`.

## 9. CONTABILIDADE HISTÓRICA — registrada para o auditor futuro

```
EXEC_1_CALLS  = 2    EXEC_1_STATUS = INVALID
EXEC_2_CALLS  = N <= 10
CUMULATIVE_MS001A_MODEL_CALLS = 2 + N
```

**A restrição de 10 é POR EXECUÇÃO SELADA.** Se a Execução 2 completar, o cumulativo será
**12**, e **isso não é violação**. Registrado aqui para que ninguém some 2+10 e declare
estouro falso.

## 10. INALTERADO PARA AS CALLS 3–10

Prompt e schema de extração · identidade · dedup · agrupamento de Evidence · Candidate
Provenance · montagem de package · selo. **Nada disso muda.**

**Entailment real (calls 9 e 10):** por Claim, envia-se a Claim, seus qualifiers e
**somente as Evidence daquela Claim**. Nenhum candidate. Nenhuma outra source. Nunca o
catálogo inteiro.

## 11. PASS / FAIL / INVALID

**`PASS`** — controles mecânicos PASS · EC PASS · JE 5/5 PASS · corpus intacto ·
≤10 chamadas · ≥1 SEALED Claim em B e em C · `INVALID_PROVENANCE == 0` · dois packages
completos e selados · zero refs/relações cross-source · raw preservado · Compile Trace completo.

**`FAIL`** — instrumento válido, produto viola contrato.

**`INVALID`** — EC falha · JE falha · modelo divergente · schema/tooling quebra · corpus
diverge · instrumento alterado após este Opening Record · chamada 11.

**Não exigir 100% `ENTAILED`.** `ENTAILED` → `CLAIMS`/`SEALED`; `NOT_ENTAILED` e
`INDETERMINATE` → audit only. **Nenhum threshold de taxa.** Nenhum threshold de blocker.

## 12. TRAVAS

Mesmo em `PASS`: não calibrar blocker · não executar blocker · não iniciar MS-001B · não
julgar relação cross-source · não produzir Fusion Package · não usar MTX policy · não usar
Source A · zero escritas no Drive.
