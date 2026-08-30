# OPENING RECORD — ADENDO PARA A **EXECUÇÃO 2** DA REVERIFY

**Selado e pushed ANTES da re-execução.** Data: 2026-08-30.

Opening Record base, **integralmente normativo e não alterado**:
`8a1599468ce46635a63e57215c69e274979c66a39282fc8db794979a640e9d72`, selado em
`284200f16c9bcdec78d2b8b28a0e544647203003`.

Execução 1: `MS_000B_TYPED_IDENTITY_REVERIFY_INVALID`, registrada em
`REVERIFY-EXEC-1-INVALID.md` (`653e7425af60732b71ce9cc0a997bd116df6fe93144977282c63c44fea1dd818`), saídas preservadas em
`out-invalid-exec-1/`. Nada apagado.

## 1. AS DUAS CORREÇÕES — AMBAS DE INSTRUMENTO

**(1) `lib/fusion.py::materialize`** indexava candidatos admitidos por `local_id` sozinho. O
registro de `anti_pattern_candidate R-0095` sobrescrevia o de `rule_candidate R-0095`, e o
teste de `kind` subsequente descartava a rule: 32 rules admitidas por run → 25 materializadas.
Passa a indexar por `(entity_kind, local_id)`.

**(2) O varredor de refs** de `run_reverify.py` usava a heurística *"lista de 2 strings cujo
primeiro elemento tem 64 caracteres"*, que sinalizava `participating_source_package_hashes`
(lista legítima de dois hashes) e `required_inputs` (texto livre cujo primeiro elemento tem
coincidentemente 64 caracteres). Passa a exigir que o primeiro elemento **seja** hex de 64 e o
segundo **não seja** — que é a forma exata de uma 2-tupla nua `[sha256, local_id]`.

Refs realmente não tipadas nos artefatos derivados da execução 1: **0**.

| artefato | sha256 novo |
|---|---|
| `lib/fusion.py` | `1feda1d3f2f78b6f6d2ebdd4d364588060ab6dcf3bbfd775060b0307b6dc904f` |
| `run_reverify.py` | `96a49da7b291ce3d31d039799325f85bca2d6a75808a06c40b935168e4cf8e82` |

## 2. O QUE **NÃO** MUDA — BYTE-IDÊNTICO

| artefato | sha256 | estado |
|---|---|---|
| `CANDIDATE-ADMISSION-POLICY-v0.2.json` | `f142938853239c58ff3cb80dbcc650da8ea1461d2cde2ea38978ba478d1b9caf` | **inalterado** |
| `FUSION-CONFIG-IDENTITY-REVERIFY.json` | `e1da64fad9b0ff02a9d3d906d1aa5aa7bc155ace49b13bc045da380e3079dea5` | **inalterado** |
| `lib/typedref.py` | `03df6113f24360b8a5b52a2c63a483748dde5049e140fdb974aebe3800fa451b` | **inalterado** |
| `lib/admission.py` | `24ab979a54fec4d93e7c45e39ddc44489c08e6d9732318ad7e8afb1675d0871c` | **inalterado** |
| `identity_canaries.py` | `be0739f2773218db2209fca11dfde46df34bf4c89cf686efead680410738a7fb` | **inalterado** |
| `i26_canary.py` | `b80010e8bb335bdc5d1f79c3bf936c434072fb26fcce55aab4ac931c2db8f567` | **inalterado** |

Nenhum predicado, critério ou limiar muda. A matriz `ID1–ID8` e `ID5b` permanece exatamente
como declarada. Nenhuma contagem é predeclarada.

## 3. O QUE ESTE INVALID ACRESCENTA À EVIDÊNCIA DA ERRATA

> Terceira ocorrência do mesmo defeito no meu próprio código: índice em `local_id` nu
> confundindo objetos distintos. Execução 1 da Round 4, e agora duas vezes **dentro da rodada
> que existe para corrigir esse modelo de identidade**.

Registrado como reforço empírico da errata, não como atenuante: uma chave que não distingue
objetos distintos é um atrator de defeito, e escrever sob a errata não bastou enquanto um
índice interno continuou destipado.

## 4. CRITÉRIOS INALTERADOS

`PASS` / `FAIL` / `INVALID` exatamente como o §11 do Opening Record base declarou,
`INVALID` precedendo `FAIL`. **Zero chamadas de modelo.** Os seis Source Packages permanecem
read-only e byte-idênticos.
