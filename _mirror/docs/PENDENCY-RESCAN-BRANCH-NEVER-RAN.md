# PENDÊNCIA — o ramo de revarredura nunca executou em produção

**Status:** PENDENCIA_ABERTA · registrada 2026-08-12

## O fato

| piloto | cobertura | piso | revarreduras |
|---|---|---|---|
| PILOT-001 | 90,61% | 73,5% | **0** |
| PILOT-002 | 82,39% | 73,5% | **0** |
| PILOT-003 | 78,86% | 73,5% | **0** |

Três pilotos, três portões satisfeitos na primeira passada. **O caminho de
revarredura dirigida nunca rodou sobre dados reais.**

## Por que isso importa

O ramo de revarredura é maquinaria de verdade: escolhe segmentos alvo pelo
complemento de cobertura, re-invoca o extractor com contexto dirigido, deduplica
contra o que já existe, remede a cobertura, e para por `MAX_RESCAN_ITERATIONS`
ou por `STOP_ON_ZERO_PROGRESS`. Tudo isso tem canário e nenhum uso.

Canário prova que o código faz o que o teste pede. Não prova que o teste pede a
coisa certa, nem que o ramo se comporta sob dados que ninguém antecipou. Toda a
disciplina deste projeto — fixture que TEM de falhar, mutante, limiar
pré-declarado — foi construída sobre a diferença entre "passou no teste" e
"funciona". Este ramo está do lado errado dessa diferença.

## O risco concreto

Se um piloto futuro cair abaixo de 73,5%, a revarredura roda **pela primeira
vez** no momento em que ela é necessária — e o resultado dela entra no artefato
publicado. Uma falha ali não seria detectada por comparação, porque não há
execução anterior com que comparar.

E a cobertura vem caindo de forma monotônica com o tamanho do corpus:
90,6% -> 82,4% -> 78,9%. Não violou o piso em nenhum, mas a margem encolheu de
17,1 para 5,4 pontos. O quarto piloto pode ser o primeiro a precisar.

## O que fecharia

Uma das duas, e a segunda é mais barata:

1. **caso real** — um piloto cujo corpus de fato caia abaixo do piso;
2. **teste forçado** — reexecutar um piloto já compilado com o piso elevado
   artificialmente (por exemplo 95%), só para exercitar o ramo, e comparar a
   evidência acrescentada contra a rodada original. O piso elevado é
   instrumento, não medição, e o resultado NÃO substitui o piloto publicado.

O (2) é executável hoje sobre o PILOT-001, que é o menor corpus: 9 segmentos,
custo de uma revarredura dirigida.

## Estado

Não agendada. Ninguém deve tratar o ramo de revarredura como validado até que
uma das duas aconteça.
