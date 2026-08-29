# HANDOFF — sessão autônoma v0.1.4

- Gerado: `2026-08-11T03:03:04+00:00`
- Gerador: `handoff_v014.py` (nenhum número digitado)
- Regime: READ-ONLY sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/`
- Nenhum lock, registry ou opening record foi criado ou congelado.

## Pronto

**1. `STRUCTURAL-CEILING-REPORT-v0.1.4.yaml`** — `artifact_status: FINAL`
- sha256 `f0b65495df12608f287a973107fa461e085a16e31c9b14935c6b02bd30352fa1` · 18673 B
- Portão de hash: **PASS** (5/5 artefatos)
- Teto estrutural **60.0**, banda **[34.0, 60.0]**
- Par de braços amarrado ao relatório:
  - `FULL@AFTER_DEDUP` → `b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028`
  - `ABLATED@AFTER_DEDUP` → `da9b326dbd80af1711c67a5f95999118bdc54ce6b84b6e54dbd756b4d657a205`

**2. `TEST-0008-METRICS-DISCREPANCY.md`** — Frente 2, discrepância 5×6 do TEST-0008
- sha256 `08010bb32ae39c6cb0354dd870407fe692568520f261f7261c35da3bf18450c9` · 8321 B

## Canários

| canário | esperado | obtido | |
|---|---|---|---|
| `structural_ceiling` | 60.0 | 60.0 | OK |
| `informative_margin_band` | [34.0, 60.0] | [34.0, 60.0] | OK |
| `canonical_threshold` | 34.0 | 34.0 | OK |
| `ablated_predicted_total` | 56.0 | 56.0 | OK |
| `predicted_margin` | 44.0 | 44.0 | OK |

Resultado: **PASS** — nenhum dos cinco divergiu, logo não houve parada.

## Cinco checks estruturais

CORROBORA a conferência prévia; nenhum dos cinco divergiu. Conferência prévia: operador (Alexandre), antes desta rodada.

- **PASS** — `a_arms_distinct`
- **PASS** — `b_runtime_policy_identical`
- **PASS** — `c_wording_literal_in_runtime_policy`
- **PASS** — `d_before_to_after_only_skill_md`
- **PASS** — `e_after_to_ablated_removes_exactly_two`

## O que divergiu

**Caminho de entrada.** O diretório declarado `Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007/ARMS_WORDING_FROZEN` não existe. Os três braços foram localizados por busca de conteúdo em `Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007/ARMS_WORDING_FROZEN/PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN.zip` — que está sob a árvore `v0.1.3`, não `v0.1.4`. Os cinco hashes declarados conferem a partir dessa origem, então **a divergência é de caminho, não de conteúdo**, e não bloqueou nada. Vale arrumar a árvore antes do próximo freeze.

Nenhuma divergência numérica: os cinco canários bateram e os cinco checks estruturais passaram.

## Reteste do juiz — resolvido, não pendente

**Não.** w permanece aplicável e passa a ser CONSERVADOR: foi medido sobre um estímulo equivalente ao novo, e a fonte de variância que ele reconhecidamente não cobre — seleção de âncora, ver scope_limitation da própria regra de decisão — diminui quando a recusa passa a reafirmar o checkpoint explicitamente.

Ressalva registrada: w mede repetibilidade numérica intra-âncora sobre saídas não ambíguas. Ele continua sem estimar variância de seleção de âncora; o anchor_selection_guard da regra de decisão congelada permanece o instrumento para isso.

## A decisão que sobrou para o Alexandre

**Fixar o limiar de margem da v0.1.4 — ou reconfirmar 34,0 — antes do próximo blind run.**

Este relatório publica a banda informativa [34.0, 60.0] e **não deriva nem congela limiar**. O 34,0 aparece aqui só como canário conferido; sua fonte é `TEST-0007-DECISION-RULE-v0.1.3.yaml`, congelada na v0.1.3.

O que torna isso uma decisão e não uma formalidade: a banda não mudou da v0.1.3 para a v0.1.4 porque a régua não mudou — só o candidato mudou. Cabe decidir se o limiar herdado continua valendo para um estímulo novo, ou se a v0.1.4 merece regra própria pré-declarada.

