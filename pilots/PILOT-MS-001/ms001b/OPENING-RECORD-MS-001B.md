# OPENING RECORD — `PILOT-MS-001B` — SEMANTIC FUSION

**Selado e pushed ANTES de qualquer chamada de modelo semântica.** Data: 2026-08-30.

## 1. SOURCE PACKAGES — IMUTÁVEIS

| | hash | selo | completude |
|---|---|---|---|
| `pkg-B` | `a0a73dde03410d5c744129bf8ba635815a678dbf5ce46cd124e6a31f8f67dc1f` | PASS | PASS |
| `pkg-C` | `5959b4ea1e8b91f570c17d61d03c4f2b6d00698801056a72a53c8e02b5a1d6c2` | PASS | PASS |

B: 30 SEALED Claims, 8 Candidates ELIGIBLE. C: 36 SEALED Claims, 8 ELIGIBLE.
**Não regenerar. Não recompilar. Não reselar.**

## 2. BLOCKER E PAIRSET

`BLOCKER-DESIGN-v0.3.json` `fa62c8159f2cef53ce435d56b3f7f68aedea950acb6ea47822bff8767059cba8` · variante **V1** por
`DR-MS-001B-VARIANT-001` `93646a9b734031d399cd41d45fd1a3b59c50d9d74fa8e5073af7220fe9d6e810`.

Recomputado: **1.080 brutos → 97 retidos, 983 bloqueados, 91,02% de redução**, cobertura
22/30 e 16/36. `BC1` 27/45 · `BC2` 7/24 · `BC3` 55/78 · `BC4` 9/21 retidos · `BC5` **0/36**.

```
PAIRSET_HASH = a0b116d93f754576cf8fbbbf6eb1757b2837b7ea18b415f8e2bce30c1ee517f5
pair_id = sha256(canon({left_typed_ref, right_typed_ref, blocker_design_hash, blocker_variant}))
```

Direção **B → C**, refs sempre tipadas. Adicionar, remover, trocar ou reordenar par →
**`PAIRSET_DRIFT`** → `INVALID`.

## 3. INSTRUMENTOS CONGELADOS

| artefato | sha256 |
|---|---|
| `RELATION-TAXONOMY-v1.txt` | `377879d2cd6a3e5460279466842b7549eda3898ab070b13aae64ab7e0dd3f5eb` |
| `RELATION-PROMPT-v1.txt` | `840d4ccbfbe7351a7d1b80a567e8273cfe6c354f695e64e70bd22db45a074ee3` |
| `RELATION-SCHEMA-v1.json` | `35c5814841711d4c92b9dc7e869b01902405bd40944a48720ad2d3f4c4db1973` |
| `JUDGE-CONTROLS-J1-J10.json` | `761785cd26e07764ad06ab09fdd512ede78a24dbd7d70c5a09e867a8ad1879ff` |
| `MODEL-POLICY-MS001B.txt` | `cd37131a0be14ad8090efc13ae4f509fdfc3b0ecc69539fa753e85e5aa4bee64` |
| `PARTITION-MS001B.json` | `d220f587e8cdb8e5fe86752aba794f6165643f7f471bb73fd2f6e7220ece03fd` |
| `FUSION-CONFIG-MS001B.json` | `0b4fd07ea7492ea5de8ee438152415067bf6362e88f4440ad312f2f0bb8863bd` |
| `lib/relation_validate.py` | `7283a123dd59dda2205a1e47a486fef94f279eed4ef1197fb273b1350cbb6dd5` |
| `PAIRSET-MS001B-V1.json` | `e576a17ff954d3197c3168ed82fc26605603f565c7fe24d2671cdd59c54480b6` |

## 4. TAXONOMIA

Sete labels: `IDENTICAL` · `CORROBORATES` · `SPECIALIZES` · `CONTRADICTS` · `SUPERSEDES` ·
`UNRELATED` · `INDETERMINATE`. `PRESUPPOSES` = `OPEN / NOT_REQUIRED`. Nenhuma outra.

**Convenção de direção, única:** `LEFT` = Claim de B, `RIGHT` = Claim de C.
`LEFT_TO_RIGHT` = *LEFT tem a propriedade em relação a RIGHT* — em `SPECIALIZES`, LEFT é a
mais específica; em `SUPERSEDES`, LEFT substitui RIGHT.

Simétricas com `direction = NONE`: `IDENTICAL`, `CORROBORATES`, `CONTRADICTS`,
`UNRELATED`, `INDETERMINATE`. Direcionais: `SPECIALIZES`, `SUPERSEDES`.

## 5. ESCOPO — PRIMEIRO, SEMPRE

`EQUIVALENT_SCOPE` · `NESTED_COMPATIBLE_SCOPE` · `DIFFERENT_SCOPE` · `AMBIGUOUS_SCOPE`.

`IDENTICAL` exige `EQUIVALENT_SCOPE`. `SPECIALIZES` normalmente `NESTED_COMPATIBLE_SCOPE`.
`CONTRADICTS` exige compatibilidade material de escopo. **`DIFFERENT_SCOPE` não pode virar
falsa contradição.** Validado mecanicamente.

## 6. GOVERNANÇA SEPARADA

Relação semântica **nunca** produz precedência. `CONTRADICTS` →
`governance_state = NOT_YET_ADJUDICATED`, fora do output do juiz. **Proibido** escolher B ou
C por data, autor, canal, modelo ou confiança informal. Campos `precedence`, `winner`,
`mtx_policy` ou `governance_state` no output do juiz → `R12_FORBIDDEN_FIELD` → run `INVALID`.

## 7. INPUT DO JUIZ

Por lado: typed ref · texto · idioma · qualifiers · Evidence daquela Claim · excerpts ·
anchor mínimo. **Ausentes por desenho:** blocker controls · relação esperada · rótulos
`S1`/`S2`/`S4` · Candidates · outros pares · ranking de autoridade · precedência · MTX policy.

**Igualdade de evidence por lado:** `set(checked) == set(fornecidas)`. Acrescentada ou
omitida → run `INVALID`.

## 8. CONTROLES `J1`–`J10`

Uma control call por run. `J1` IDENTICAL · `J2` CORROBORATES · `J3` SPECIALIZES
`RIGHT_TO_LEFT` · `J4` CONTRADICTS verdadeiro · `J5` SUPERSEDES `RIGHT_TO_LEFT` ·
`J6` UNRELATED · `J7` INDETERMINATE · `J8` falso conflito (**não-CONTRADICTS**) ·
`J9` diferença de escopo (**não-CONTRADICTS**) · `J10` paráfrase → IDENTICAL.

**10/10 obrigatório.** Falha → run `INVALID`, **sem queimar os quatro batches**, zero retry.

## 9. MODELO

`claude-opus-5` · `thinking = {"type":"disabled"}` · `max_tokens = 8000` · `temperature`
omitida · SDK `anthropic 0.121.0`. **A primeira call de cada run valida a resolução ao vivo.**
Mismatch → run `INVALID`. **Sem substituição silenciosa.**

## 10. BATCHES E RUNS

Ordenação por `pair_id` ascendente, lote **25**:
`BATCH-1` 25 · `BATCH-2` 25 · `BATCH-3` 25 · `BATCH-4` 22 = **97**.

**As três runs usam exatamente os mesmos quatro batches.** Proibido rebalancear conforme
outputs. Nada é regenerado entre runs.

```
por run: 1 control + 4 batches = 5
PLANNED = 15 · HARD_CAP = 15 · RETRY = 0 · call 16 -> MS_001B_INVALID
```

## 11. ESTABILIDADE — SEM VOTO SILENCIOSO

Persistência por `(run_id, pair_id)`. `relation_result` **nunca** é campo mutável
compartilhado. **`STABLE`** 3/3 mesma relation, direção e escopo materialmente compatível ·
**`PARTIALLY_STABLE`** 2/3 · **`UNSTABLE`** sem maioria material.

> **Proibido eleger "a maioria" como verdade final.** O estado é fato registrado, não
> resolução. Os três judgments são preservados.

## 12. `PASS` / `FAIL` / `INVALID`

**`PASS`** — Source Packages válidos · blocker V1 reproduzido · pairset de 97 estável ·
canários pré-modelo PASS · toda run utilizada passa `J1`–`J10` · 97/97 julgados por run
válida · provenance 100% · identidade tipada 100% · Fusion consistente · zero escopo
proibido · nenhuma metodologia pós-resultado.

**Não exigido:** `CONTRADICTS` real > 0 · 100% `STABLE` · qualquer relação desejada.

**`FAIL`** — violação de contrato experimental explicitamente pré-declarado.

**`INVALID`** — controle falha · modelo divergente · schema/tooling quebra · call 16 ·
`PAIRSET_DRIFT` · `PACKAGE_DRIFT` · instrumento alterado após este Opening Record.

> **Resultado experimental "ruim" não é FAIL.** Muitas `UNRELATED`, muitas
> `INDETERMINATE`, alta instabilidade ou zero `CONTRADICTS` podem ser resultados legítimos
> do corpus, e serão reportados objetivamente.

**Previsão registrada antes da execução:** sob V1, espero **taxa alta de `UNRELATED`** —
plausivelmente a maioria dos 97. Seria confirmação do trade-off de recall, não falha.
Falha seria `CONTRADICTS` nos pares de `BC4`, ou `UNRELATED` engolindo os 27 de `BC1`.

## 13. KILLS

`PAIRSET_DRIFT` · `PACKAGE_DRIFT` · `SILENT_MAJORITY` · `MTX_IN_FUSION` ·
`PRECEDENCE_AUTO_ASSIGNED` · `UNTYPED_CROSS_PRODUCT_REF`.

## 14. FUSION

`fusion_id` = sha256 sobre hashes de B e C · blocker design · variante V1 · pairset ·
taxonomia · prompt · schema · política de modelo · outputs persistidos.
**Não inclui `mtx_policy_hash` nem timestamp operacional.**

Zero Operationalization · zero Operational Package · zero Skill Pack · zero MTX policy.

## 15. TRAVAS

Mesmo em `PASS`: não iniciar Operationalization, Router, Skill Pack, corpus A, produção,
MTX policy nem N1–N9. **O fim é MS-001 fechado experimentalmente.**
