# `MS_000B_TYPED_IDENTITY_REVERIFY_INVALID` — execução 1

**Data:** 2026-08-30 · Opening Record vigente
`8a1599468ce46635a63e57215c69e274979c66a39282fc8db794979a640e9d72`, pushed em
`284200f16c9bcdec78d2b8b28a0e544647203003` **antes** desta execução.

Classificação por §11 do Opening Record: **`INVALID` precede `FAIL`** — instrumento
quebrado não reprova produto.

## 1. O que a execução reportou

16 portões, 13 OK, 3 FALHA: `todas_refs_derivadas_tipadas` ·
`admitted_materializados` (147 admitidos, 126 materializados) · `real_precedence_undefined`.

`ID1–ID8` **todos PASS**. `I26` **todos PASS**. `source_packages_intact` **PASS**.
`admitted_rejected_disjuntos` **PASS**. `rejected_nao_consumidos` **PASS** (0 vazamentos).
`transporte_preservado` e `objetos_distintos` **PASS**. `zero_model_calls` **PASS**.

## 2. Causa (A) — varredor de refs com heurística frouxa

O varredor sinalizou **6** refs "não tipadas", 2 por run. Ambas são **falso-positivo**:

| caminho | conteúdo | por que não é ref |
|---|---|---|
| `participating_source_package_hashes` | `["c66b2695…","d5fd5dad…"]` | lista legítima de dois `source_package_hash` |
| `fusion.workflows.structure.steps.required_inputs` | `["Projeto aberto no VS Code com repositório sob controle de versão", "Mudanças locais realizadas"]` | texto livre; o primeiro elemento tem **coincidentemente** 64 caracteres |

A heurística era *"lista de 2 strings cujo primeiro elemento tem 64 caracteres"*. Refs
realmente não tipadas nos artefatos derivados: **0**.

## 3. Causa (B) — `materialize` indexa por `local_id` sozinho

`lib/fusion.py::materialize`, herdado da Round 4 e não corrigido quando as refs viraram
tipadas:

```python
adm = {r["local_id"]: r for r in admission if r["state"] == "ADMITTED"}
...
if lid not in adm or adm[lid]["kind"] != kind: continue
```

O registro de `anti_pattern_candidate R-0095` **sobrescreve** o de `rule_candidate R-0095`;
o teste `adm[lid]["kind"] != kind` então descarta a rule. Por run: 32 rules admitidas → **25
materializadas**. Agregado: 147 admitidos → 126 materializados.

`real_precedence_undefined` falhou **em consequência disso** — as rules ausentes da população
não podiam ser encontradas no índice de transporte.

## 4. O que este INVALID demonstra

> É a **terceira** vez que um índice em `local_id` nu produz defeito no meu próprio código:
> execução 1 da Round 4, e agora duas vezes aqui, dentro da rodada que existe **justamente
> para corrigir esse modelo de identidade**.

Isso não enfraquece a errata — é evidência empírica direta a favor dela. Uma chave que não
distingue objetos distintos é um **atrator de defeito**, e nem escrever código sob a errata
impediu a reincidência enquanto um índice interno continuou destipado.

## 5. O que muda, e só isso

1. `lib/fusion.py::materialize` passa a indexar por `(entity_kind, local_id)`;
2. o varredor de `run_reverify.py` passa a exigir que o primeiro elemento seja **64 hex** e o
   segundo **não** seja, em vez de contar caracteres.

**Não muda:** `CANDIDATE-ADMISSION-POLICY-v0.2.json` · `FUSION-CONFIG-IDENTITY-REVERIFY.json`
· `lib/typedref.py` · `lib/admission.py` · `identity_canaries.py` · `i26_canary.py` ·
predicado algum · critério algum · a matriz `ID1–ID8`.

Saídas da execução 1 preservadas em `out-invalid-exec-1/`, **não apagadas**.

## 6. Classificação

# `MS_000B_TYPED_IDENTITY_REVERIFY_INVALID`
