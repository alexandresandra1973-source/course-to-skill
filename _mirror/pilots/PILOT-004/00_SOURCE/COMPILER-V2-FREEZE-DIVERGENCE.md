# COMPILER-V2 — divergência de freeze detectada no bot-04

Conferência feita em 2026-08-13 (bot-04), **apenas leitura**, contra
`compiler-v2/FREEZE-RECORD.yaml` (`compiler_version: compiler-v2/0.2.0-frozen`,
`frozen_at_utc: 2026-08-12T01:40:24+00:00`).

Cópia conferida: a que está no Google Drive
(`Chat GPT/Course-to-Skill-Claude/compiler-v2`), acessível deste MacBook.
**Não foi necessário copiar nada da Lenovo** — o compiler-v2 está sincronizado no Drive.

## Resultado: 11 OK / 4 DIVERGENTES / 0 AUSENTES (de 15 arquivos no record)

### Íntegro — é o que executa o PASS 1
Todos byte-a-byte idênticos ao freeze:

- `ctsc2/__init__.py`, `model.py`, `dedup.py`, `thresholds.py`,
  `temporal_map.py`, `manifest.py`, `extraction.py`, `pipeline.py`,
  `coverage_gate.py` (9 arquivos)
- `prompts/lesson-analyzer-v2.md`
- `README.md`

### Divergente — todos em `canary/`, todos CRESCERAM depois do freeze

| arquivo | bytes no record | bytes em disco | mtime |
|---|---|---|---|
| `canary/canary-results.json` | 1779 | 2303 | 2026-08-11 23:55 |
| `canary/fixtures.py` | 4606 | 6716 | 2026-08-11 23:55 |
| `canary/mutants.py` | 6931 | 7948 | 2026-08-11 23:54 |
| `canary/run_canary.py` | 7252 | 9492 | 2026-08-11 23:55 |

O freeze é de 22:40 local (01:40 UTC) e bate com o mtime dos arquivos íntegros
(22:32–22:41). Os 4 divergentes foram mexidos ~1h15 **depois** do freeze.

**Leitura:** o `canary_suite_passed: true` do FREEZE-RECORD atesta uma suíte de
canário mais antiga que a que está em disco. A suíte foi ampliada depois; não há
resultado congelado correspondente ao canário atual. Isso **não** afeta o código
que roda a extração, mas invalida a atestação de teste como está escrita.

## Achado adicional: arquivo fora do freeze

Dois arquivos existem em disco e **não constam** da lista do FREEZE-RECORD:

- `ctsc2/extractors/__init__.py` (0 bytes)
- `ctsc2/extractors/claude_extractor.py` (**18.139 bytes**)

`claude_extractor.py` é o componente que faz as chamadas de extração. O conjunto
congelado, portanto, **não cobre o componente que efetivamente chama o modelo no
PASS 1** — o `frozen_set_sha256` sela 15 arquivos que excluem justamente esse.

## Consequência para o PILOT-004

Não bloqueia a selagem da fonte (BLOCO 1), que não usa o compiler.
Bloqueia o PASS 1 no seguinte sentido: rodar agora significa rodar com um
extrator não congelado e com uma suíte de canário sem resultado congelado
correspondente. Decisão do Alexandre:

1. re-congelar o compiler-v2 no estado atual (incluindo `extractors/`) e rodar o
   canário atual antes do PASS 1; ou
2. rodar o PASS 1 assim mesmo, declarando a divergência no manifesto do PASS 1; ou
3. restaurar os 4 arquivos de `canary/` ao estado do freeze — **não recomendado**,
   descarta trabalho posterior e continua sem cobrir o `claude_extractor.py`.
