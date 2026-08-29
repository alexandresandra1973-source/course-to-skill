# A alegação se sustenta para notas inteiras — e quebra a partir de duas casas decimais

- Gerado: `2026-08-11T04:50:25+00:00` · gerador `tol_reachability_proof.py`
- Aritmética **exata** (`Fraction` sobre `Decimal`). Nenhum float entra na prova — float seria o próprio erro que ela investiga.
- Enumeração **completa** do espaço alcançável, não amostra.

## Veredito

**Confirmada para notas inteiras.** Nenhuma margem alcançável cai em `(upper, upper+TOL]` nem em `[lower-TOL, lower)`. A margem alcançável mais próxima acima de `upper` está a **0.031335907** dele, e a mais próxima abaixo de `lower` a **0.031335907** — ambas maiores que TOL = 0.01.

**Mas a folga é fina.** Com notas de **2 casas decimais** o desvio passa a ser alcançável: `39.17`, `39.172`, `39.174`, `39.176`. Se o contrato do juiz algum dia aceitar nota fracionária além de uma casa, esta prova deixa de valer.

## Método

O total ponderado de um braço é `0,4·a + 0,2·b + 0,2·c + 0,2·d`. O script **constrói** o conjunto de totais alcançáveis somando os quatro critérios sobre toda a grade de notas — não assume que o resultado é aritmético. Depois constrói o conjunto de margens como todas as diferenças entre dois totais alcançáveis, e testa a pertinência às duas faixas.

Fronteiras testadas, da regra de decisão congelada `540df728…`:

- limiar canônico: `34`
- meia-largura `w`: `5.168664093`
- `lower` = limiar − w = `28.831335907`
- `upper` = limiar + w = `39.168664093`
- `TOL` do scorer: `0.01`

## Resultado por grade de nota

| grade | passo da margem | margens possíveis | cai em `(upper, upper+TOL]` | cai em `[lower-TOL, lower)` | folga acima de `upper` | folga abaixo de `lower` |
|---|---|---|---|---|---|---|
| inteira | `0.2` | 1001 | nenhuma | nenhuma | `0.031335907` | `0.031335907` |
| 1 casa decimal | `0.02` | 10001 | nenhuma | nenhuma | `0.011335907` | `0.011335907` |
| 2 casas decimais | `0.002` | 100001 | **39.17, 39.172, 39.174…** | **28.822, 28.824, 28.826…** | `0.001335907` | `0.001335907` |

## A checagem simétrica, que é mais dura

As duas faixas do enunciado são de um lado só. A pergunta mais forte é se existe margem alcançável a menos de TOL de uma fronteira, para qualquer lado — porque um desvio pode empurrar para dentro ou para fora.

| grade | margens a ≤ TOL de `upper` | margens a ≤ TOL de `lower` | seguro |
|---|---|---|---|
| inteira | nenhuma | nenhuma | sim |
| 1 casa decimal | 39.16 | 28.84 | **não** |
| 2 casas decimais | 39.16, 39.162, 39.164… | 28.822, 28.824, 28.826… | **não** |

**A leitura conservadora já falha em 1 casa decimal.** Com uma casa decimal existe margem alcançável a `0.008664093` de `upper` — abaixo de TOL. Ela está do lado de DENTRO, então a faixa de um lado só do enunciado não a pega; a pergunta simétrica pega. A alegação original é verdadeira como foi enunciada, e a margem de segurança é menor do que o enunciado sugere.

## O que esta prova NÃO cobre

1. **Só o modelo aritmético declarado.** Pesos exatamente 0,4/0,2/0,2/0,2, quatro critérios, margem como diferença de dois totais ponderados. Se o scorer arredondar em outro ponto do cálculo, ou se algum critério mudar de peso, a prova precisa ser refeita.
2. **Não diz que TOL é inofensivo em geral** — diz que, nesta grade de notas e nestas fronteiras, ele não alcança nenhuma margem possível. São coisas diferentes.
3. **A folga depende da grade.** Ela é confortável com nota inteira e some com duas casas decimais. Isso é propriedade das fronteiras escolhidas, não uma margem de segurança projetada.

> **Ressalva sobre a origem da alegação.** Ela é minha, e antes disto estava conferida em quatro valores à mão. Amostra de quatro não distingue "nenhuma margem cai na faixa" de "as quatro que olhei não caíam". Esta enumeração distingue.

