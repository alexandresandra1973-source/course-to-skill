# ERRATA — hashes de Source Package citados na ROUND 1

**`decision_id`:** `DR-MS-000B-R1-002` · **Data:** 2026-08-30 · Registro **aditivo**.
**O relatório histórico NÃO é modificado.**

---

| | citado no relatório final da Round 1 e em `ROUND-1-CLASSIFICATION.md` | **valor real do artefato** |
|---|---|---|
| pacote A | `4290b88f…` | **`31df720fa727867912dfe16b6c7c36fa9d10524b4f99d4482919f3276bf33ab2`** |
| pacote B | `5c32b8ed…` | **`40a786072bd3faac832be876a62d082c17995ca5cd4b3e393041fb0d74e57f8e`** |

Confirmado por **duas fontes independentes**: `out/source-packages.json` da Round 1 e os
`qualified_refs` de todas as claims seladas daquela rodada.

## Origem do erro, reproduzida

`4290b88f…` é o hash do **dry-run**, computado com um `model_policy` simplificado
(`{'model': 'claude-opus-5', 'thinking': 'disabled'}`). Citei o número da execução
exploratória em vez de ler o artefato persistido. Com a `model_policy` real da Round 1, o
mesmo código devolve `31df720f…`.

## Regra que entra no Opening Record da Round 3

> **Todo hash citado em relatório é lido do artefato persistido, nunca de execução
> exploratória.**

É a mesma disciplina que a `PROPOSAL v1.2` aplicou às erratas de localizador.
