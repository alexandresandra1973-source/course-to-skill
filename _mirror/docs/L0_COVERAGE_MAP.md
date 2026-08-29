# L0_COVERAGE_MAP — PILOT-001

**Gerado:** `2026-08-10T16:52:26.977478+00:00` · **Somente medição** — nada foi cortado, nenhum caso de teste foi escrito, a v0.1.2 não foi tocada.

Relatório gerado por script (`coverage_map.py`); nenhum número foi digitado.


## 0. Entrada e integridade

| arquivo lido (relativo a 'Meu Drive/Chat GPT') | vs BASELINE_MANIFEST |
|---|---|
| Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources/transcript/transcript-original-en.txt | CONFERE |
| Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources/metadata/source-metadata.yaml | CONFERE |
| Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/analysis/evidence.jsonl | CONFERE |
| Course-to-Skill-Compiler/02_PILOTS/PILOT-001/02_VALIDATION/PILOT-001-final-blind-test-kit/PILOT-001-final-blind-test-kit/judge-private/test-suite.yaml | CONFERE |

| item | valor |
|---|---|
| sha256 do L0 | 068b4998c160d143… |
| bytes | 20712 |
| marcas de tempo | 180 |
| duração nominal (`source-metadata.yaml`) | 15:05 = 905s |
| última marca endereçável | 14:44 = 884s |
| cauda sem marca (não endereçável por `t=`) | 21s |

> A extensão usada como denominador é a **duração nominal**. Os últimos **21s** não têm marca de tempo e, portanto, não são endereçáveis pela gramática `L0:…:t=` — são território virgem por impossibilidade de endereçamento, não por escolha.


## 1. União dos spans citados — por origem

| origem | registros | citações | cobertura própria | acréscimo à união |
|---|---|---|---|---|
| (a) evidências de L1 | 44 | 47 | 665s | — |
| (b) 10 casos da suíte | 10 | 40 | — | +0s sobre (a) |
| (c) rubrica do JUDGE | — | 0 | — | +0s sobre (a)+(b) |

**A suíte de teste alcança 18 das 44 evidências, e não acrescenta 1 segundo à união** — toda a sua cobertura é herdada por referência a IDs internos.

**A rubrica do JUDGE, isolada dos casos, contém 0 referências a evidência e 0 timestamps.** Ela não tem alcance próprio nenhum sobre L0 — é a medida direta da circularidade já reportada na Fase 2 (régua derivada do artefato, não da fonte).


## 2. Cobertura e complemento

| métrica | valor |
|---|---|
| extensão de L0 | 15:05 (905s) |
| coberto | 11:05 (665s) — **73.5%** |
| virgem | 4:00 (240s) — **26.5%** |
| blocos cobertos contíguos | 11 |
| blocos virgens contíguos | 11 |
| maior bloco virgem | 74s |
| blocos virgens ≥ 60s | 1 |

## 3. Blocos virgens ≥ 60s

| início | fim | duração | triagem |
|---|---|---|---|
| 3:02 | 4:16 | 74s | CANDIDATO_HELD_OUT |

**3:02–4:16** (74s) → `CANDIDATO_HELD_OUT`  
marcadores: `{'metodo': ['if you', 'step'], 'transicao': ['by the end', 'in this video', 'keep it in mind'], '_regra_v1_so_metodo': 'CANDIDATO_HELD_OUT'}`

> distinction shapes everything else in this video, so keep it in mind. So, if you've been relying on chat bots and automations and wondering why things still fall through the cracks, now you know why. AI agent adoption is accelerating faster than most people realize, and [music] the gap between early movers and everyone else is already opening up. Let's talk about why. The AI agents market nearly ## Why Everyone Is Building AI Agents? doubled this year, and it's on track to hit $50 billion by 2030. That's not a trend, my friend. That's infrastructure. Gardner predicts that by 2028, 60% of brand…


## 4. Todos os blocos virgens, com triagem

| início | fim | dur | triagem | marcadores de método | plug / CTA | utilizável (≥60s) |
|---|---|---|---|---|---|---|
| 3:02 | 4:16 | 74s | CANDIDATO_HELD_OUT | if you, step | — | sim |
| 14:09 | 15:05 | 56s | DESCARTE | if you, make sure | free guide, highly recommend checking, put together, subscribe | — |
| 0:29 | 1:00 | 31s | DESCARTE | should | free guide, playbook, put together | — |
| 5:30 | 5:49 | 19s | CANDIDATO_HELD_OUT | should | — | — |
| 13:41 | 13:55 | 14s | DESCARTE | — | comments, drop your, how fast you can, pause this, your turn | — |
| 12:13 | 12:23 | 10s | DESCARTE | — | — | — |
| 13:12 | 13:22 | 10s | DESCARTE | — | — | — |
| 8:59 | 9:08 | 9s | CANDIDATO_HELD_OUT | step | — | — |
| 2:09 | 2:15 | 6s | DESCARTE | — | — | — |
| 7:13 | 7:19 | 6s | CANDIDATO_HELD_OUT | should | — | — |
| 1:55 | 2:00 | 5s | DESCARTE | — | — | — |

**4 candidatos** (108s) · **7 descartes** (132s).

**Utilizáveis — candidatos com pelo menos 60s: 1 bloco(s), 74s.** É este o número que importa: um bloco de 6 ou 9 segundos não sustenta caso de teste nenhum.

> **A triagem é mecânica, não decisão.** Regra vigente (v2): `CANDIDATO_HELD_OUT` só quando há marcador de método **e** nenhum marcador de plug ou de CTA — um bloco que vende algo ou pede engajamento não é metodologia, ainda que contenha um verbo instrucional. Títulos de seção em markdown são removidos antes da triagem: são rótulo do transcript, não fala do professor. Os marcadores foram extraídos do texto real do PILOT-001, não inventados, e viajam junto com o veredito para que a chamada seja revisível — 'sem conteúdo de método' é juízo semântico e nenhum contador o substitui.


### 4.1 Onde a regra mudou de veredito

A primeira versão da regra (`v1`, só marcador de método) classificava como candidato qualquer bloco com um verbo instrucional. Ela errava exatamente na classe que este mapa precisa isolar. A divergência está registrada em vez de apagada:

| início | fim | dur | regra v1 | regra v2 (vigente) |
|---|---|---|---|---|
| 0:29 | 1:00 | 31s | CANDIDATO_HELD_OUT | DESCARTE |
| 14:09 | 15:05 | 56s | CANDIDATO_HELD_OUT | DESCARTE |

Os dois blocos maiores que a `v1` chamaria de candidatos são o **plug de abertura** e o **outro com patrocínio** — 87s que a `v2` manda para descarte, e corretamente.


## 5. Blocos cobertos (para conferência)

| início | fim | duração |
|---|---|---|
| 0:00 | 0:29 | 29s |
| 1:00 | 1:55 | 55s |
| 2:00 | 2:09 | 9s |
| 2:15 | 3:02 | 47s |
| 4:16 | 5:30 | 74s |
| 5:49 | 7:13 | 84s |
| 7:19 | 8:59 | 100s |
| 9:08 | 12:13 | 185s |
| 12:23 | 13:12 | 49s |
| 13:22 | 13:41 | 19s |
| 13:55 | 14:09 | 14s |

---

**Escopo desta medição:** nada foi cortado, nenhum caso de teste foi escrito, nenhum arquivo de `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado.
