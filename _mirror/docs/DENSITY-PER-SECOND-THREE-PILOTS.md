# DENSIDADE POR SEGUNDO — a métrica que mostra se o conserto escalou

**Status:** MEDIÇÃO · registrada 2026-08-12 · gerada por script

## A métrica

`evidências ÷ segundos de corpus`. O yield por segmento esconde isto, porque
depende de quantos segmentos o PASS 1 produziu — decisão do segmentador, não
propriedade do corpus.

| piloto | evidências | corpus (s) | **ev/s** | segmentos | s/segmento | ev/segmento |
|---|---|---|---|---|---|---|
| PILOT-001 | 149 | 905 | **0.1646** | 9 | 100.6 | 16.56 |
| PILOT-002 | 448 | 4384 | **0.1022** | 41 | 106.9 | 10.93 |
| PILOT-003 | 2463 | 13857 | **0.1777** | 148 | 93.6 | 16.64 |

Conta explícita: 149/905 · 448/4384 · 2463/13857

## O que ela mostra

O corpus do PILOT-003 é **15.3x maior** que o do PILOT-001 e a densidade
por segundo **subiu** (0.1646 -> 0.1777, +8.0%).
O conserto escalou: extrair de 3h50m nao degradou a taxa de extracao.

## O que ela NAO mostra, e a correcao do registro anterior

Escrevi que o yield do PILOT-003 era "consistente com o teto por chamada".
**Estava errado, e o erro inverte o sinal.**

| | s/segmento | ev/segmento |
|---|---|---|
| PILOT-003 | 93.6 | 16.64 |
| PILOT-001 | 100.6 | 16.56 |
| PILOT-002 | 106.9 | 10.93 |

De 93.6s para 100.6s (+7.4% de duracao) o yield
por segmento move -0.5%. De 100.6s para 106.9s
(+6.3%) ele cai -34.0%.

**E penhasco, nao curva.** Uma lei de potencia `y = A*dur^k` com `k<1` preve
crescimento SUBLINEAR — mas crescimento. Aqui ha estagnacao seguida de colapso,
que nenhum expoente produz.

E a direcao contraria o teto: o teto preve **segmento maior rendendo MAIS por
segmento**. O PILOT-002 tem o maior segmento e o menor yield dos tres.

**A duracao de segmento varia 14% entre os tres pilotos. A densidade varia
74%.** Uma variavel que se move 14% nao explica uma que se move 74%.

## Consequencia

**O PILOT-002 continua sendo o outlier, e o residual de 1,515 segue sem
explicacao.** O PILOT-003 nao o explica: reforca que o PILOT-002 e o ponto fora,
com dois pilotos agora acima de 0,16 ev/s e ele sozinho em 0,10.

O teto por chamada, medido causalmente em 1,500 no experimento de corte,
**nao recebe credito por este piloto**.
