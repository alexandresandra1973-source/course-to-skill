# OPENING RECORD — `PILOT-MS-001B` **EXECUÇÃO 2**

**Selado e pushed ANTES da primeira chamada.** Data: 2026-08-31. Artefato **aditivo**: o
Opening Record da Execução 1 (`ebff25da40fb04fefcce7bd64ae1b76006c9d4a76b3c1a46b40f3fd36dc1b9ae`) **não é editado**.

## 0. HISTÓRICO

```
MS_001B_EXEC_1 = INVALID / BLOCKED   calls = 13
```

Preservado em `out-ms001b/MS-001B-EXEC-1-BLOCKED.md`
(`d88645760ca03d17019e293d3f6b77d6be0d08cac3e9bdd2a5fbc1f29f4a782f`), com os 13 raw e seus inputs.
**Não retomado. Seus 200 judgments não entram em estabilidade, Fusion nem distribuição válida.**

## 1. INALTERADO — declarado por hash

| artefato | sha256 |
|---|---|
| `pkg-B` | `a0a73dde03410d5c744129bf8ba635815a678dbf5ce46cd124e6a31f8f67dc1f` |
| `pkg-C` | `5959b4ea1e8b91f570c17d61d03c4f2b6d00698801056a72a53c8e02b5a1d6c2` |
| `BLOCKER-DESIGN-v0.3.json` | `fa62c8159f2cef53ce435d56b3f7f68aedea950acb6ea47822bff8767059cba8` |
| `DR-MS-001B-VARIANT-001` (V1) | `93646a9b734031d399cd41d45fd1a3b59c50d9d74fa8e5073af7220fe9d6e810` |
| `PAIRSET-MS001B-V1.json` | `e576a17ff954d3197c3168ed82fc26605603f565c7fe24d2671cdd59c54480b6` |
| `PAIRSET_HASH` | `a0b116d93f754576cf8fbbbf6eb1757b2837b7ea18b415f8e2bce30c1ee517f5` |
| `RELATION-TAXONOMY-v1.txt` | `377879d2cd6a3e5460279466842b7549eda3898ab070b13aae64ab7e0dd3f5eb` |
| `RELATION-SCHEMA-v1.json` | `35c5814841711d4c92b9dc7e869b01902405bd40944a48720ad2d3f4c4db1973` |
| `JUDGE-CONTROLS-J1-J10.json` | `761785cd26e07764ad06ab09fdd512ede78a24dbd7d70c5a09e867a8ad1879ff` |
| `MODEL-POLICY-MS001B.txt` | `cd37131a0be14ad8090efc13ae4f509fdfc3b0ecc69539fa753e85e5aa4bee64` |
| `lib/relation_validate.py` | `7283a123dd59dda2205a1e47a486fef94f279eed4ef1197fb273b1350cbb6dd5` |

Corpus, seis slices, Claims, Candidates, definições semânticas, `scope_state`, governança,
mappings `BC1`–`BC5`, fronteira MTX, Architecture Freeze e Identity Errata: **inalterados**.

## 2. MUDADO — e somente isto

**(a) Transporte da partição: `25 / 25 / 25 / 11 / 11`.**
`BATCH-1/2/3` preservados byte-a-byte, `batch_hash` idênticos à Execução 1. O antigo
`BATCH-4` (22) subdividido **posicionalmente** em `4A` = primeiros 11 e `4B` = últimos 11.
`PARTITION-MS001B-v2.json`: `62c3fccae8b4acdff984e68bce9e33499e37bea94daec813f6eff6835538debc`

**(b) Endurecimento de completude no envelope.** `expected_pair_count` e
`expected_pair_ids` explícitos, com instrução de verificar antes de finalizar e emitir
`INDETERMINATE` em vez de omitir. **A seção `[SYSTEM]` permanece byte-idêntica.**
`RELATION-PROMPT-v2.txt`: `0324219d1f62bbba9578894c41599794e7563be4a3d952d787a9ee61c5c34500`

**(c) Orçamento: 18.**

Nota de recuperação: `ecc9546dca9032e297b265647c0963c4b1fd754da1a5886912004f78e86b6af4`

## 3. COMPLETUDE — o validador é a autoridade

Por batch:

```
returned_count == expected_count
set(returned_pair_ids) == set(expected_pair_ids)
count(cada pair_id) == 1
```

Divergência → **run `INVALID`**. **Não completar automaticamente. Não pedir par faltante em
retry.**

## 4. CANÁRIOS — 29/29 PASS antes de qualquer chamada

22 pré-modelo reexecutados + `BATCH-C0`–`C6`: split 11+11 com união igual aos 22 e
interseção vazia · cinco batches cobrindo 97 sem duplicata · `PAIRSET_DRIFT` detectado por
remoção **e** por troca · 11/11 completo sem erro · 10 de 11 → `R15_PAIR_MISSING` ·
12 com duplicata → `R06_DUPLICATE_PAIR` · o par antes omitido localizado em `BATCH-4B`
posição 6 de 11.

## 5. ORÇAMENTO

```
por run: 1 control + 5 batches = 6
3 runs: PLANNED = 18 · HARD_CAP = 18 · RETRY = 0 · call 19 -> MS_001B_EXEC_2_INVALID
EXEC_1_CALLS = 13 (INVALID) — NAO entra neste cap; o cap e por execucao selada
```

## 6. MODELO

`claude-opus-5` · `thinking = disabled` · `max_tokens = 8000` · `temperature` omitida ·
SDK `anthropic 0.121.0`. Primeira chamada de cada run valida a resolução. Mismatch → run
`INVALID`. **Sem substituição silenciosa. Sem troca de modelo.**

**Se o saldo continuar insuficiente: `HARD STOP — API CREDIT`, sem alterar instrumento.**

## 7. VALIDADE DE RUN

`J1`–`J10` **10/10** · **97/97** judgments · zero desconhecido, faltante ou duplicado ·
schema estrito · igualdade exata de evidence por lado · modelo confere · mesmo pairset fixo.

## 8. `PASS` / `FAIL` / `INVALID`

Idênticos ao Opening Record da Execução 1. **Resultado experimental "ruim" não é FAIL.**

> **Previsão mantida, registrada antes desta execução:** sob V1, espero taxa alta de
> `UNRELATED`. Na Execução 1, 200 de 200 dos judgments obtidos foram `UNRELATED`, com
> zero `CONTRADICTS` em `BC4`. Se a Execução 2 reproduzir isso, é confirmação do
> trade-off de recall, **não** falha.

## 9. TRAVAS

Mesmo em `PASS`: não iniciar Operationalization, Operational Package, Router, Skill Pack,
corpus A, produção, MTX policy nem N1–N9.
