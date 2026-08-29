# Densidade de decisão — PILOT-001 × candidato PILOT-002

- Gerado: `2026-08-11T04:07:15+00:00` · gerador `source_density.py`
- READ-ONLY sobre `Course-to-Skill/`
- **Um único script mede as duas fontes.** Não há caminho de código por fonte: mesmas regex, mesmos cortes, mesma definição de ponto de decisão.

## Como cada coisa é contada

| métrica | definição operacional |
|---|---|
| ponto de decisão | frase distinta (após normalizar) que contém marca condicional **ou** marca normativa |
| condicional | `\b(if|when|unless|except|depends|depending|otherwise|caso|quando)\b` |
| normativa | `\b(never|always|must|should|don't|do not|avoid|instead of|rather than|choose|pick|decide|select|start with|prefer|make sure|nunca|sempre|deve|escolha|evite)\b` |
| framework/procedimento | nome próprio seguido de framework/method/model/principle/process/system/checklist/loop/pattern, mais `step N` |
| limiar numérico | número com unidade (%/h/min/dias/vezes) ou faixa `N a M` |
| **densidade de decisão** | pontos de decisão distintos ÷ minutos |
| teste da uma página | 1 bullet por ponto de decisão; ≤ 45 linhas ⇒ FINA |

Marcas de tempo e títulos de seção são removidos antes de contar, nas duas fontes.

## Medição

| métrica | PILOT-001 | candidato |
|---|---|---|
| duração (min) | 15.08 | — |
| palavras | 3049 | — |
| frases | 285 | — |
| frases condicionais | 25 | — |
| frases normativas | 26 | — |
| **pontos de decisão distintos** | 49 | — |
| frameworks/procedimentos nomeados | 9 | — |
| limiares numéricos | 4 | — |
| palavras/min | 202.1 | — |
| **decisões/min** | 3.249 | — |

## Teste da uma página

| fonte | bullets | limite | cabe? | veredito |
|---|---|---|---|---|
| PILOT-001 — HubSpot, How to Build Your | 49 | 45 | não | **NAO_FINA** |
| candidato | — | — | — | **NÃO MEDIDO** |

## Canário de calibração

| | |
|---|---|
| exigido | PILOT-001 deve sair **FINA** |
| medidor deu | **NAO_FINA** |
| resultado | **REPROVADO** |

O PILOT-001 tem **uma** tabela de decisão multi-ramo e o resto é checklist linear. O medidor conta 49 pontos porque `if`, `when`, `should` e `make sure` são cola de discurso em aula falada — **26 dos 49 não são decisão nenhuma**. Diagnóstico item a item em `DENSITY-METER-CALIBRATION.md`.

## Veredito

**NÃO EMITIDO — medidor reprovado no canário.**

Nenhum veredito de qualificação sai deste relatório enquanto a contagem léxica não separar metodologia de discurso. Emitir um número que já se sabe errado no caso conhecido, para decidir sobre o caso desconhecido, seria o pior uso possível deste instrumento.

As contagens de superfície abaixo continuam válidas — duração, palavras, palavras/min, limiares e frameworks nomeados são o que dizem ser. O que não vale é `decisões/min` e o teste da uma página.


## Detalhe por fonte

### PILOT-001 — HubSpot, How to Build Your First AI Agent

- fonte: `Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources/transcript/transcript-original-en.txt`
- sha256: `068b4998c160d143ee6bc2942e444157fdaebb4311b2ca9eced625c22626df67`
- frameworks/procedimentos: The model, The system, step five, step four, step one, step seven, step six, step three, step two
- limiares: 19 seconds, 30 days, 6 minutes, at least 2 hours

