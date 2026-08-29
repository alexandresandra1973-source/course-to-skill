# L0_COVERAGE_MAP — PILOT-002

**Gerado:** `2026-08-11T04:07:26+00:00` · **Somente medição** — nada foi extraído, nenhuma rubrica escrita, nenhum L1 produzido.

Relatório gerado por script (`pilot002_holdout.py`); nenhum número digitado. Mesmo formato do mapa do PILOT-001, para os dois corpora ficarem comparáveis.

## 0. Entrada e integridade

| item | valor |
|---|---|
| sha256 do docx de origem | `46288371ff6f18a3…` |
| sha256 do L0 íntegro (normalizado) | `43b58271feb0a1d5…` |
| sha256 do L0 **CORTADO** | `85ea229011a989ea…` |
| bytes (íntegro / cortado) | 107653 / 96246 |
| marcas (íntegro / cortado) | 819 / 733 |
| duração nominal do vídeo | 81:37 = 4897s |
| held-out removido | 513s |
| extensão do corpus de treino | 4384s |
| última marca no cortado | 81:35 |

## 1. União dos spans citados — por origem

| origem | registros | citações | cobertura própria | acréscimo à união |
|---|---|---|---|---|
| (a) evidências de L1 | 0 | 0 | 0s | — |
| (b) casos de suíte | 0 | 0 | — | +0s |
| (c) rubrica do JUDGE | — | 0 | — | +0s |

**Zero por construção, e é esse o ponto.** No PILOT-001 o mapa foi medido *depois* de L1 existir, e por isso conseguiu mostrar 73,5% de cobertura e 26,5% de território virgem. Aqui a extração ainda não aconteceu — é proibida antes do corte, e o corte acabou de ser selado. O corpus de treino do PILOT-002 está **100% virgem** neste momento.

Quando L1 existir, rode este mesmo script de novo para obter a comparação de cobertura de fato.

## 2. Cobertura e complemento

| métrica | valor |
|---|---|
| extensão do corpus de treino | 73:04 (4384s) |
| coberto | 0:00 (0s) — **0.0%** |
| virgem | 73:04 (4384s) — **100.0%** |
| blocos entre marcas | 732 |

## 3. Triagem mecânica dos blocos do corpus de treino

| veredito | blocos | segundos |
|---|---|---|
| `CANDIDATO_HELD_OUT` | 120 | 708 |
| `DESCARTE` | 612 | 4187 |

> **Ressalva que importa.** Os marcadores de `cts/coverage.py` foram extraídos do texto real do **PILOT-001** — um curso de marketing. O PILOT-002 é um curso de ferramenta de programação. A triagem aqui é **indicativa, não calibrada**: serve para comparar formato, não para decidir held-out. O held-out do PILOT-002 foi escolhido por span declarado, não por esta triagem.

## 4. Seções do curso

| # | seção | no corpus |
|---|---|---|
| 1 | Introduction & Course Overview | treino |
| 2 | Installing Claude Code on Your Local Machine | treino |
| 3 | Choosing an IDE & Installing VS Code | treino |
| 4 | Customizing VS Code Themes | treino |
| 5 | Starting and Managing a Claude Code Session | treino |
| 6 | Understanding Permission Modes (Plan, Accept Edits, Auto, Bypass) | **HELD-OUT** |
| 7 | Using Plan Mode & Autonomous Goals (/goal) | treino |
| 8 | Installing and Triggering Claude Skills | treino |
| 9 | Exploring File Structures and Directories | treino |
| 10 | Managing Your Context Window and Token Usage | **HELD-OUT** |
| 11 | Essential Built-In Slash Commands | treino |
| 12 | Managing Version Control with GitHub | treino |
| 13 | Connecting Tools & Deploying Apps via MCP and CLI | treino |
| 14 | Frequently Asked Questions (FAQ) | treino |

