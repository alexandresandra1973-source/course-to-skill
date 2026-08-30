# PILOT-MS-000B — RELATÓRIO

**Gerado integralmente por `consolidate.py`.** Nenhum número digitado à mão.

- Opening Record: `3e251d7cdbf5307aef89840d3b733aad49211fa0c887883710b622e93dd01638`
- modelo resolvido: claude-opus-5 · thinking disabled
- chamadas: **9** de cap **24**

## 1. Portões

| portão | resultado |
|---|---|
| KILL-1 camada selada intacta | **OK** |
| identidade | **OK** |
| proveniencia 100% | **OK** |
| KILL-3 sealed 100% ENTAILED | **OK** |
| KILL-2 variancia <= 1,5x | **OK** |
| workflow preservado | **OK** |
| controles de blocagem | **FALHOU** |
| isolamento | **FALHOU** |
| COMPILE-TRACE completo | **OK** |
| config identica entre runs | **OK** |

## 2. Source Packages

| pacote | cap | slice sha256 | package hash | itens | LOCATED_IN | REPRODUCED_FROM |
|---|---|---|---|---|---|---|
| A | 12 | `6d9e718cf5dbb088…` | `31df720fa7278679…` | 44 | 44/44 | 43/44 |
| B | 13 | `2768b11c40836371…` | `40a786072bd3faac…` | 56 | 56/56 | 55/56 |

## 3. Identidade

- `local_id` totais: **100** · colisões nuas: **44** (deliberadas)
- identidades qualificadas distintas: **100**
- package hashes distintos: **True**
- **referências cross-package nuas: 0**

## 4. Claims — raw × selada × entailed

| run | raw propostas | rejeitadas antes do selo | seladas | seladas ENTAILED |
|---|---|---|---|---|
| RUN-1 | 89 | 0 | 89 | 89 |
| RUN-2 | 83 | 0 | 83 | 83 |
| RUN-3 | 81 | 0 | 81 | 81 |

Motivos de rejeição por run:

- `RUN-1`: —
- `RUN-2`: —
- `RUN-3`: —

## 5. Variância entre runs (KILL-2)

- seladas por run: {'RUN-1': 89, 'RUN-2': 83, 'RUN-3': 81}
- máx/mín = **1.0988×** · teto medido **1,5×** → dentro
- núcleo comum aos 3 runs: **2** claims idênticas normalizadas
- sobreposição par a par: {'RUN-1∩RUN-2': 8, 'RUN-1∩RUN-3': 13, 'RUN-2∩RUN-3': 5}

## 6. Preservação de workflow (DESIGN C)

| run | pacote | workflows | steps | struct source | struct fusion | preservado |
|---|---|---|---|---|---|---|
| RUN-1 | A | 6 | 19 | `cecfc4716257…` | `cecfc4716257…` | **OK** |
| RUN-1 | B | 4 | 23 | `ff95e7c0fa9c…` | `ff95e7c0fa9c…` | **OK** |
| RUN-2 | A | 6 | 19 | `cecfc4716257…` | `cecfc4716257…` | **OK** |
| RUN-2 | B | 4 | 23 | `ff95e7c0fa9c…` | `ff95e7c0fa9c…` | **OK** |
| RUN-3 | A | 6 | 19 | `cecfc4716257…` | `cecfc4716257…` | **OK** |
| RUN-3 | B | 4 | 23 | `ff95e7c0fa9c…` | `ff95e7c0fa9c…` | **OK** |

## 7. Blocagem

Regra declarada antes: `shared_content_tokens >= 2`

| run | pares possíveis | sobreviventes | redução | controles positivos |
|---|---|---|---|---|
| RUN-1 | 1968 | 158 | 91.97% | 0/2 |
| RUN-2 | 1722 | 115 | 93.32% | 0/2 |
| RUN-3 | 1620 | 137 | 91.54% | 0/2 |

## 8. Isolamento

| run | tokens exclusivos A | exclusivos B | falsa atribuição |
|---|---|---|---|
| RUN-1 | 189 | 221 | **11** |
| RUN-2 | 189 | 221 | **6** |
| RUN-3 | 189 | 221 | **11** |

## 9. Relações executadas

Só `IDENTICAL` mecânica (`D15`). `UNRELATED` é default, não rótulo.

| run | pares avaliados | IDENTICAL |
|---|---|---|
| RUN-1 | 158 | 0 |
| RUN-2 | 115 | 0 |
| RUN-3 | 137 | 0 |

## 10. COMPILE-TRACE

- chamadas registradas **9** de esperadas **9**
- tokens: entrada **73525** · saída **34385**
- campos completos em todas: **True**
- config idêntica entre runs: **True**
- partições: ['1 chamada por (source,run); todas as 44 evidencias do pacote A', '1 chamada por (source,run); todas as 56 evidencias do pacote B', '1 chamada por run; TODAS as 81 claims candidatas', '1 chamada por run; TODAS as 83 claims candidatas', '1 chamada por run; TODAS as 89 claims candidatas']

## 11. KILL checks

- **KILL-1** camada selada byte-idêntica: OK
- **KILL-2** variância 1.0988× ≤ 1,5×: OK
- **KILL-3** 253/253 seladas ENTAILED: OK

## 12. Classificação

# `PILOT_MS_000B_FAIL`
