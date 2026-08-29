# compiler-v2 — PASS 2 por segmento + portão de saturação

Versão corrigida do compilador, conforme
**ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE**
(sha256 `b8cddc93b74a65d6cbc2ad6859e4e3b8a4a81404137d4f95260f1b92668cf3f8`).

O compilador original **não foi tocado**: ele vive em
`Course-to-Skill-Compiler/`, sob READ-ONLY. `prompts/lesson-analyzer-v2.md` é um
**delta** sobre o release, não uma cópia.

## Arquitetura

```text
PASS 1 → temporal-map.yaml persistido e hasheado
       → PASS 2[SEG-001] → PASS 2[SEG-002] → … → PASS 2[SEG-N]
       → dedup → portão de cobertura/saturação
       → revarredura DIRIGIDA aos blocos descobertos → dedup
       → COMPILATION_MANIFEST
```

## Módulos

| arquivo | papel |
|---|---|
| `ctsc2/thresholds.py` | limiares **congelados**, pré-declarados |
| `ctsc2/model.py` | `Segment`, `Evidence`, `IdAllocator`, contrato `Extractor` |
| `ctsc2/temporal_map.py` | PASS 1 persistido e hasheado antes do PASS 2 |
| `ctsc2/extraction.py` | Decisão A — PASS 2 por segmento + rastro de yield |
| `ctsc2/dedup.py` | identidade exata de claim; nunca semelhança |
| `ctsc2/coverage_gate.py` | Decisão B — portão + revarredura dirigida |
| `ctsc2/manifest.py` | `COMPILATION_MANIFEST` estendido |
| `ctsc2/pipeline.py` | orquestração |

## Canário

```bash
CTS_ROOT=/caminho/para/raiz/com/cts python3 canary/run_canary.py
```

Cada caso roda contra a implementação real (**tem de passar**) e contra um
mutante que encarna o defeito (**tem de falhar**). Mutante que passa reprova a
suíte inteira: um teste que não falha quando a proteção some não é teste.

## Dependência externa

A métrica de cobertura é a de `cts/coverage.py`, importada e **pinada por
hash**. Se ela mudar, a comparabilidade entre pilotos cai e o portão avisa.
Aponte `CTS_ROOT` para a raiz que contém `cts/`.

## O que este pacote NÃO faz

- **não chama modelo nenhum** — `Extractor` é um Protocol; as únicas
  implementações são fixtures de canário;
- **não compilou nenhum piloto** — nem PILOT-001, nem PILOT-002;
- **não tem alvo de contagem** — nem 44, nem 200. O único número que decide é o
  piso de cobertura, `> 73,5%`, estritamente maior.
