# DECISION RECORD — adoção da **OPTION B / TYPED QUALIFICATION**

**`decision_id`:** `DR-ARCH-IDENTITY-001` · **Data:** 2026-08-30 · **Ator:** Alexandre Sandra
**Classe:** `GIT_NATIVE_BY_DESIGN` · **Natureza:** **ADITIVA**

| artefato | sha256 |
|---|---|
| `ARCHITECTURE-FREEZE-ERRATA-IDENTITY-QUALIFICATION-v1.md` | `2f8232f6c184668370ed9e440256b0de3f6ee801a7bee67285eb291c1a527ad2` |
| `MS-000B-QUALIFIED-IDENTITY-NAMESPACE-AUDIT-REPORT.md` | `364f4afe55d87a02edae174efce621fc4f60adb3fab5c2fc57d4a874cee9e989` |
| `identity_audit_measure.py` | `e46da697e4a9c2326757cf52748ef5cdfd6dd1593b54b0f6408432082beb345e` |
| `out-identity-audit/identity-measurements.json` | `20ac4127add8b666f1f3068318651da1240456fff986c0e8403de22a00cfb184` |
| `COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-FREEZE.md` (original, **preservado**) | `6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b` |

---

## D1 — A decisão

**`OPTION B — TYPED QUALIFICATION` é a correção aprovada.**

```
GLOBAL_OBJECT_IDENTITY = (source_package_hash, entity_kind, local_id)
```

Rejeitadas: **Option A** (unicidade package-wide) — invalidaria os seis `source_package_hash`,
o registry, os Fusion R3/R4, os admission reports e os Opening Records, destruindo a camada
que a Final Design Review acabou de aceitar. **Option C** (`object_id` próprio) — mais limpa
conceitualmente, mas introduz uma quarta identidade ao lado de `SOURCE_ID` /
`SOURCE_CONTENT_HASH` / `SOURCE_PACKAGE_HASH` e obrigaria a reabrir a família de invariantes.

## D2 — A base empírica

**1.129** objetos endereçáveis · a 2-tupla congelada produz **1.108** tuplas distintas e
**21 colisões**, **21/21 cross-kind**, **0 same-kind** · a 3-tupla tipada produz
**1.129/1.129** e **0 colisões**. Todos os números lidos de `identity-measurements.json`,
nenhum digitado à mão.

## D3 — Cláusulas supersedidas — e somente estas

`E6` (linha 86) · `I4` (linha 496) · `I23` (linha 515, só interpretação) · `D5` (linha 534).
**Nenhuma outra decisão do freeze é tocada.**

## D4 — O que fica congelado pela errata

1. `GLOBAL_OBJECT_IDENTITY` como 3-tupla, com `entity_kind` **canônico segundo o schema**,
   extensível por registro aditivo, nunca por convenção implícita ou prefixo lexical;
2. **dentro do package**, `(entity_kind, local_id)` único; **entre packages**, a 3-tupla única;
3. um `local_id` **pode** repetir entre kinds — é o que preserva `rule_candidate R-0095` e
   `anti_pattern_candidate R-0095` como objetos diferentes;
4. `SELF` ref sem `entity_kind` é válida **somente** com kind `schema-implied`; campo que possa
   apontar para mais de um kind exige `entity_kind`; `SELF` genérica sem kind determinado é
   `INVALID_REF`;
5. **toda ref de fronteira resolve sozinha** — proibido depender de prefixo, campo irmão
   opcional, conhecimento externo ou heurística do consumidor.

## D5 — Preservação

O Architecture Freeze original permanece **byte-idêntico, selado e histórico**. Os seis Source
Packages da Round 3 permanecem **byte-idênticos**: `entity_kind` é derivável do membro em que o
objeto vive, então **nada precisa ser reaberto, renumerado ou reselado**. As Rounds 1–4
permanecem intactas.

## D6 — Consequência para o MS-000B

Habilita o `TARGETED_IDENTITY_REWRITE_AND_REVERIFY` — área derivada nova, policy `v0.2` cuja
**única** mudança normativa é a regra de unicidade, refs tipadas em todos os artefatos
derivados novos. **Não** é Round 5. **Não** recompila Source Package. **Zero chamadas de modelo.**

Fica registrado antes de qualquer medição: a mudança de unicidade **move 21 candidates** no
contrafactual já medido (126/147 → 147/147 admitidos). Esse número **não é predeclaração de
resultado** — a policy `v0.2` será executada e o resultado real medido, inclusive se outro
predicado legítimo rejeitar algum desses 21.

## D7 — Classificação

# `ARCHITECTURE_FROZEN_WITH_IDENTITY_ERRATA`

**Não** `ARCHITECTURE_REOPENED`.
