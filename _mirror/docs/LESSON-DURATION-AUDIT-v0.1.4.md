# Duração real da fonte L0 × custo estimado por aula

- Gerado: `2026-08-11T03:11:21+00:00`
- Gerador: `lesson_duration_audit.py` (nenhum número digitado)
- READ-ONLY sobre `Course-to-Skill/`

## Veredito

**Nenhum dos dois números está errado. Eles medem coisas diferentes, e a premissa de que um contradiz o outro é que está errada.**

- **00:15:05** é a duração do vídeo-fonte.
- **~77 min** é o tempo de PIPELINE para processar uma aula, declarado no próprio texto como *"de ponta a ponta por aula (L0 → 3 passadas de adversário → bundle)"*.

Um é a duração do insumo; o outro é o custo de processá-lo. A razão entre eles é **5.1×** — processar a aula custa 5.1 vezes o tempo de assisti-la, o que é coerente, não contraditório.

## Duração real da fonte

| evidência | valor |
|---|---|
| `source-metadata.yaml` → `source.duration` | **00:15:05** = 905s |
| última marca de tempo no transcript | `14:44` = 884s |
| cauda após a última marca | 21s |
| marcas de tempo no transcript | 180 |
| palavras no transcript | 3282 |
| bytes do transcript | 20712 |

A última marca (`14:44`) fica 21s antes do fim declarado, o que é o esperado: o segmento final não recebe marca nova. As três fontes são consistentes com **00:15:05**.

- transcript sha256: `068b4998c160d143ee6bc2942e444157fdaebb4311b2ca9eced625c22626df67`
- metadata sha256: `d0cb047025350ecf8a800300d3365cc6dad5646b24cdd42dd9bb8c5f2b87fd9a`

## Onde cada número aparece

**`FINAL_ENGINEERING_REPORT.md`** — a única ocorrência de "77":

- linha 264: | **O que custa** | Medido no piloto: **~77 min de ponta a ponta por aula** (L0 → 3 passadas de adversário → bundle), fora o retrabalho de ferramenta. Para 6 aulas: **~8 h de pipeline**, mais revisão humana das passadas de adversário |

**`PROJECT_INVENTORY.md`** — declara a duração:

- linha 364: Fonte: uma aula única — vídeo do YouTube `YkdAx2XjWDs`, canal "HubSpot Marketing", *"How to Build Your First AI Agent (Step-by-step Tutorial)"*, duração `00:15:05`, idioma inglês. Transcrição: 20.174 bytes / 3.282 palavras, com 180 marcas de tempo em formato `m:ss` (última: `14:44`).

**`L0_COVERAGE_MAP.md`** — usa a duração como extensão de L0:

- linha 22: | duração nominal (`source-metadata.yaml`) | 15:05 = 905s |
- linha 46: | extensão de L0 | 15:05 (905s) |
- linha 71: | 14:09 | 15:05 | 56s | DESCARTE | if you, make sure | free guide, highly recommend checking, put together, subscribe | — |

## Custo do corpus de 5–8 aulas

O custo do corpus **não muda** ao confirmar que a aula tem 15:05, porque a estimativa de ~77 min já é por aula processada e não deriva da duração do vídeo.

| aulas | pipeline |
|---|---|
| 5 | 385 min = **6.42 h** |
| 6 | 462 min = **7.7 h** |
| 7 | 539 min = **8.98 h** |
| 8 | 616 min = **10.27 h** |

Para 6 aulas dá **7.7 h**, o que confere com as *"~8 h de pipeline"* do relatório.

## Ressalva sobre a base da estimativa

O ~77 min é *"medido no piloto"* — ou seja, **n = 1 aula**, e essa aula tem 00:15:05. Se o corpus incluir aulas mais longas, a estimativa por aula não transfere direto: a parte proporcional à duração (L0, passadas de adversário sobre o transcript) escala com o texto, a parte fixa não. O que está medido é o custo de processar **uma aula de 15 min**, não o de processar uma aula qualquer.

Isso não corrige nenhum dos dois números; delimita o que a estimativa cobre.

