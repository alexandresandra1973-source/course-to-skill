# Canário no bot-04 — BLOQUEADO, suíte não executável nesta máquina

Data: 2026-08-13 · Máquina: bot-04 (MacBook Pro M4 Max, macOS 26.5.2, arm64)
Python: 3.12.13 (`~/venv-mtx`) · Comando: `python run_canary.py` na suíte ATUAL

## Placar da execução no bot-04

```
1/6 casos com execução real verde E mutante vermelho
SUÍTE: REPROVADA   (exit 1)
```

| caso | resultado no bot-04 | motivo |
|---|---|---|
| C1_boundary_distinct | FAIL | `RuntimeError: cts/coverage.py não encontrado` |
| C2_true_duplicate | FAIL | idem |
| C3_zero_yield_visible | FAIL | idem |
| C4_below_threshold_rescans | FAIL | idem |
| C5_above_threshold_stops | FAIL | idem |
| C6_quote_normalization | **PASS** | não passa pelo pipeline — exercita o validador direto |

## Isto NÃO é falha de fixture

As 5 falhas são **a mesma exceção de importação**, antes de qualquer asserção
rodar. Nenhuma fixture foi avaliada e reprovada; o pipeline não chegou a
executar. A prova está em como elas falharam: nos 5 casos, tanto a execução real
quanto o mutante levantaram a **mesma** exceção. Um canário com poder de detecção
real não pode ter real e mutante falhando de forma idêntica — o "poder: falhou
como exigido" desses 5 é artefato da exceção, não detecção.

O único caso que produziu sinal verdadeiro foi o **C6**, que por desenho não
passa pelo pipeline (`NO_PIPELINE`) e exercita direto o validador de citação de
`ctsc2/extractors/claude_extractor.py`. Ele passou com poder real: aceitou as
duas citações legítimas, rejeitou a fabricada distante e a fabricada próxima
(uma palavra trocada, `CITACAO_NAO_RESOLVE`), e o mutante de casamento difuso
foi corretamente pego.

## Causa: dependência externa ausente nesta máquina

```
RuntimeError: cts/coverage.py não encontrado. Defina CTS_ROOT para a raiz que
contém cts/. Procurado em: ['/home/mtx/course-to-skill-claude',
                            '/Users/alexandresandra/course-to-skill-claude']
```

O `cts/` é um pacote **externo ao compiler-v2**. O README do próprio compiler-v2
declara isso na seção "Dependência externa": a métrica de cobertura é a de
`cts/coverage.py`, importada e **pinada por hash**.

Busca feita no bot-04: `cts/coverage.py` e `cts/spans.py` **não existem** em
lugar nenhum — nem no Google Drive inteiro (`Chat GPT/`), nem em `~`,
`~/Documents`, `~/Desktop`, `~/Downloads`, `~/cerebro-claude`, `~/OneDrive`.
O primeiro caminho da lista de busca, `/home/mtx/course-to-skill-claude`, é da
**Lenovo**. O `cts/` nunca foi sincronizado para o Drive.

## O canário atual PASSA — só não aqui

O `canary/canary-results.json` guardado no Drive (68917b69…, 2303 bytes) registra
**6/6, `suite_passed: true`**, já com o C6. Ou seja: a suíte ampliada é verde
numa máquina que tem o `cts/`. Isso reforça a leitura do BLOCO 1 — o que faltava
ao 0.2.0 era cobrir o `claude_extractor.py`, e o C6 é exatamente essa cobertura.

Esse resultado **não foi herdado** para nenhum registro deste bloco, conforme o
item 3. Ele está citado aqui como contexto, não como atestação.

## Consequência: o v0.2.1 NÃO foi criado

Selar um `FREEZE-RECORD-v0.2.1.yaml` exigiria um canário verde **datado no
bot-04**. Não existe. As duas saídas que restariam seriam ambas erradas:

- herdar o `suite_passed: true` do Drive — proibido pelo item 3;
- registrar `REPROVADA` — falso, porque a suíte não reprovou, ela não rodou.

Em vez disso ficou o `COMPILER-V2-INVENTORY-bot04.yaml`: inventário de hash
completo dos 17 executáveis, **incluindo** `ctsc2/extractors/`, com o estado
atual de `canary/`. É verdadeiro independentemente do canário, e vira o corpo do
v0.2.1 assim que houver canário verde nesta máquina.

## Para destravar

Sincronizar o `cts/` da Lenovo (`/home/mtx/course-to-skill-claude/cts/`) para o
Drive, ou apontar `CTS_ROOT` para uma cópia local. Ao chegar, conferir contra o
pino de hash que já existe no `COMPILATION_MANIFEST.yaml` do PILOT-001-v2:

- `cts/coverage.py` → `ea58c05efd778cb906ac4fee7669d00b7029a72e993f8077fc36231a8f97723b`
- `cts/spans.py` → `7bcdcde2c85e2f814ec9d80b2c5aba38c1905ce17c7001ca35a3b3a42d18bb74`

Se bater, o canário roda e o v0.2.1 pode ser selado no mesmo passo.

## Registro bruto

Saída completa da execução: `canary-bot04-BLOCKED.json`.
Nada foi escrito dentro de `compiler-v2` no Drive — a execução rodou sobre uma
cópia local conferida byte-a-byte (18/18 idênticos) e o
`canary-results.json` do Drive segue com o hash 68917b69… inalterado.
