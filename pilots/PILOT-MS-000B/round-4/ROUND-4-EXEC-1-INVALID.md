# `PILOT_MS_000B_ROUND_4_INVALID` — execução 1 da Round 4

**Data:** 2026-08-30 · Opening Record R4 vigente:
`fff9e05aac9fe89b135b23d57560ad87780e3231f25c53b98f1d5557516b3726`
(selado e pushed em `3b44084d1c66070efe26b92ca6280b54f1407df4`, **antes** desta execução).

Classificação por **§14 do Opening Record**: *"`INVALID` precede `FAIL`: instrumento
quebrado não reprova produto."*

---

## 1. O que a execução reportou

15 portões, 13 OK, 2 FALHA:

| portão | resultado |
|---|---|
| `rejected_nao_consumidos` | **FALHA** — 21 "vazamentos" |
| `real_precedence_undefined` | **FALHA** — 18 de 90 casos |

Todos os demais PASS, incluindo `canaries_CA` (11/11), `canaries_I26` (6/6),
`source_packages_intact`, `admitted_materializados` (126 = 126), `transporte_preservado`,
`objetos_distintos`, `real_passo_unico`, `zero_model_calls`.

## 2. A causa — verificada, e é do INSTRUMENTO

Nos seis Source Packages da Round 3, `anti_pattern_candidates` **reusam o `local_id` da
rule de origem**. `run_round3.py:95` constrói o anti-pattern a partir da rule preservando o
mesmo id:

```python
A=[{"local_id":r["local_id"],"do_not":r["do_not"],"evidence_refs":[]} for r in R if r["do_not"]]
```

Logo `R-0095` nomeia **uma rule e um anti-pattern** dentro do mesmo pacote. Em `RUN-1/pkg-A`
colidem `R-0095`, `R-0098`, `R-0101`, `R-0102`.

Meus dois verificadores indexam por `local_id` sozinho:

- o detector de vazamento compara `(source_package_hash, local_id)` **ignorando `kind`**;
- o canário real monta `arec = {x["local_id"]: x}`, e o registro `REJECTED_STRUCTURAL` do
  anti-pattern **sobrescreve** o `ADMITTED` da rule homônima.

## 3. Recontagem com chave `(source_package_hash, kind, local_id)`

| verificação | com `local_id` | com `kind` + `local_id` |
|---|---|---|
| vazamentos reais | 21 | **0** (RUN-1 0 · RUN-2 0 · RUN-3 0) |
| rules `UNDEFINED` corretas | 72/90 | **90/90** |

Nenhum candidato rejeitado foi materializado. Nenhuma rule com `precedence: UNDEFINED`
deixou de ser admitida, transportada, preservada como `UNDEFINED` e não adjudicada.

## 4. O achado real que estava por baixo — e que NÃO é do instrumento

> **`(source_package_hash, local_id)` não é chave única nos Source Packages da Round 3.**
> É ambígua entre `kind`s.

O Architecture Freeze manda qualificar por `(source_package_hash, local_id)` na travessia de
fronteira. Estes pacotes quebram a unicidade que essa qualificação pressupõe. É defeito
herdado do empacotador da Round 3, da mesma família de `evidence_refs: []` — e some do
radar quando só se olha uma população por vez.

## 5. Resultado de produto medido nesta execução — preservado, não descartado

| kind | `ADMITTED` | `REJECTED_STRUCTURAL` |
|---|---|---|
| `rule_candidates` | 96 | 0 |
| `workflow_candidates` | 30 | 0 |
| `anti_pattern_candidates` | 0 | **21** — todos por `LOCAL_ID_INVALIDO` |

As 21 rejeições de anti-pattern são **legítimas**: o predicado `LOCAL_ID_INVALIDO` foi
pré-declarado como *"`local_id` válido (não vazio, string, **único no pacote**)"* e disparou
sobre uma colisão real. **A policy não é alterada por causa deste resultado** — alterá-la
depois de ver o número seria repetir exatamente o achado `D-1` da Round 3.

## 6. O que muda, e só isso

Corrigir **apenas** os dois verificadores de `run_round4.py`, para indexar por
`(source_package_hash, kind, local_id)`. **Não muda:**
`CANDIDATE-ADMISSION-POLICY-v0.1.json` · `FUSION-CONFIG-R4.json` · `lib/admission.py` ·
`lib/fusion.py` · `canaries_r4.py` · `i26_canary.py` · nenhum critério, nenhum predicado,
nenhum limiar.

Precedente seguido: `PILOT-MS-000A RUN-0`, registrado `INVALID`, instrumento corrigido,
**rodada nova com Opening Record novo**. A execução 1 fica preservada em
`out-invalid-exec-1/` e **não é apagada**.

## 7. Classificação

# `PILOT_MS_000B_ROUND_4_INVALID`

Execução 1 encerrada. Round 4 **não** classificada como `FAIL` — o produto não foi reprovado
por um instrumento que não distinguia uma rule de um anti-pattern.
