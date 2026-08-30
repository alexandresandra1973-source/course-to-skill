# REPRODUCED_FROM — BASELINE MEASUREMENT REPORT

**Gerado integralmente por `measure_reproduced_from.py`.** Nenhum número deste
documento foi digitado à mão.

- Início da execução: `2026-08-30T01:05:11.173087-03:00`
- Opening Record: `35cd4abf5df72758c1d0e9019c757e8503c1a1aba02fea8ffef0b22babba8634`
- Tolerância do locator secundário: **30 s** (declarada antes de rodar)

## 1. Controles (rodados ANTES da medição)

| fixture | esperado | obtido | comportou como desenhado |
|---|---|---|---|
| `FX-POS-001` | PASS | PASS | SIM |
| `FX-NEG-001` | FAIL | FAIL | SIM |

## 2. Integridade dos insumos

| bundle | artefato | sha256 confere |
|---|---|---|
| P002 | `_mirror/pilots/PILOT-002-v2/EVIDENCE.jsonl` | OK |
| P003 | `_mirror/pilots/PILOT-003-v2/EVIDENCE.jsonl` | OK |
| P004 | `_mirror/pilots/PILOT-004/02_PASS2/EVIDENCE.jsonl` | OK |

| bundle | L0 resolvido por sha256 | bytes | marcadores `**M:SS**` | erro |
|---|---|---|---|---|
| P002 | `_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt` | 96246 | 733 | — |
| P003 | `_mirror/pilots/PILOT-003/00_SOURCE/L0-transcript.txt` | 369035 | 2052 | — |
| P004 | `_mirror/pilots/PILOT-004/00_SOURCE/L0-transcript.txt` | 19624 | 186 | — |

## 3. Resultados por bundle

| bundle | examinado | elegíveis | PASS | FAIL | NOT_APPLICABLE | INVALID |
|---|---|---|---|---|---|---|
| P002 | 448 | 448 | 421 | 27 | 0 | 0 |
| P003 | 2463 | 2463 | 2366 | 97 | 0 | 0 |
| P004 | 134 | 134 | 134 | 0 | 0 | 0 |
| **AGREGADO** | **3045** | **3045** | **2921** | **124** | **0** | **0** |

## 4. Baseline — `PASS / (PASS + FAIL)` sobre elegíveis

| bundle | fórmula | baseline |
|---|---|---|
| P002 | 421 / (421 + 27) = 421/448 | **93.9732%** |
| P003 | 2366 / (2366 + 97) = 2366/2463 | **96.0617%** |
| P004 | 134 / (134 + 0) = 134/134 | **100.0000%** |
| **AGREGADO** | 2921 / (2921 + 124) = 2921/3045 | **95.9278%** |

`NOT_APPLICABLE` e `INVALID` estão fora do denominador, por definição do Opening Record.

## 5. Prova: numerador ⊆ denominador

| bundle | \|PASS\| | \|PASS ∪ FAIL\| | PASS ⊆ (PASS∪FAIL) | PASS∩FAIL = ∅ | contagens batem |
|---|---|---|---|---|---|
| P002 | 421 | 448 | SIM | SIM | SIM |
| P003 | 2366 | 2463 | SIM | SIM | SIM |
| P004 | 134 | 134 | SIM | SIM | SIM |

**Todas as asserções passaram: SIM**

## 6. Breakdown secundário do locator (não altera o baseline)

| bundle | IN_REGION | OUT_OF_REGION | LOCATOR_UNRESOLVED |
|---|---|---|---|
| P002 | 421 | 0 | 0 |
| P003 | 2366 | 0 | 0 |
| P004 | 134 | 0 | 0 |
| **AGREGADO** | **2921** | **0** | **0** |

`IN_REGION + OUT_OF_REGION` conta apenas evidences com ocorrência **e** locator resolvido.

## 7. Classificação

# `BASELINE_ESTABLISHED`

- controles como desenhados: SIM
- integridade dos EVIDENCE.jsonl: SIM
- L0 de todos os bundles resolvido: SIM
- asserções numerador/denominador: SIM
