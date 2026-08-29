# RÉGUA DO PAR DE IDIOMA — resultado

P001-v2 (905 s, fonte EN) × P004 (903 s, fonte PT). Medidas segundo a régua
declarada antes do PASS 1, na ordem que ela mesma fixou: M4 primeiro.

## M4 — falhas de medição por idioma

### Classe A — travessia PT×EN: **0 reais**

O detector automático marcou 1 ocorrência (EV-0054, "post"/"reels"). **É falso
positivo:** as duas palavras aparecem em português na própria fonte
(`grep` no L0: "um post", "story", "live"), são empréstimos correntes do
vocabulário de marketing em pt-BR, não travessia de idioma.

A medição estrutural, feita nos três pilotos com o mesmo detector:

| | fonte | quotes com marcadores EN | claims em PT | claims em EN |
|---|---|---|---|---|
| PILOT-001-v2 | EN | 99/149 (**66%**) | 112/149 (75%) | 0 |
| PILOT-003-v2 | EN | 1933/2463 (**78%**) | 1849/2463 (75%) | 2 |
| **PILOT-004** | **PT** | **0/134 (0%)** | 103/134 (77%) | 0 |

Isto é o achado central do objetivo secundário. Nos dois pilotos de fonte
inglesa, **toda evidência é uma travessia por construção**: a `quote` fica em
inglês e o `claim` sai em português. Não era um defeito ocasional que aconteceu
6 vezes no P003 — era a forma normal de operação do pipeline sobre fonte EN, e
as 6 ocorrências catalogadas eram a fração em que a travessia produziu erro
visível.

No P004 a travessia **não existe**: 0 de 134 quotes carregam marcador de inglês.
A hipótese de que as 6 do P003 eram falha de tradução fica **sustentada** no que
diz respeito à classe A.

### Classe B — ruído de ASR em português: **2**

Ambas reais, ambas herdadas do ASR e já previstas na régua:

- **EV-0001** (SEG-001) carrega "Suitech", do ASR "Meta Business Suitech".
- **EV-0134** (SEG-013) tem claim "Meta Ads" onde o ASR disse "Metaed". Aqui o
  modelo **corrigiu** o ruído — o que é acerto de conteúdo, mas afasta o claim
  do literal citado e por isso também aparece na classe C.

É ruído de fonte, não de idioma cruzado. O par em inglês tem o análogo dele.

### Classe C — validador de citação: **54 avisos, 0 rejeições**

Todos do mesmo motivo: `CLAIM_DIVERGE_DO_LITERAL_COM_ROTULO_SOURCE_EXPLICIT`,
com a lista de entidades ausentes da quote. Padrão típico: o falante diz "essa
ferramenta" e o claim escreve "Meta Business Suite" — resolução de anáfora, não
fabricação.

O portão duro **não rejeitou nada**: 134 rascunhos retornados, 134 aceitos
(100%), 0 rejeições, 0 aceitos apenas após normalização. O validador de citação
exercitado pelo canário C6 se comportou sobre texto português sem rejeitar
citação legítima nem afrouxar.

**Ressalva de comparabilidade, e ela é séria:** 54 avisos em 134 evidências é
40%, e **não tenho contra o que comparar**. Os artefatos publicados do P001-v2 e
do P003-v2 trazem `EVIDENCE.jsonl` e `COMPILATION_MANIFEST.yaml`, mas **não os
registros de chamada** onde os avisos ficam. Então não sei se 40% é alto, normal
ou baixo para este pipeline. A classe C do P004 é um número absoluto sem
denominador histórico.

Isso importa porque é exatamente o cenário que a régua antecipou: **A baixo com
C alto não sustentaria a hipótese, só moveria o problema de lugar.** Não posso
descartar esse cenário com o que está publicado. Para fechar, seria preciso o
checkpoint do P001-v2 (ou reprocessar o P001-v2 com o runner atual) e contar a
mesma classe C lá.

## M1 — densidade de evidência por segundo

| | evidências | extent | ev/s |
|---|---|---|---|
| PILOT-001-v2 | 149 | 905 s | 0,16464 |
| **PILOT-004** | **134** | **903 s** | **0,14839** |

Razão P004/P001-v2 = **0,9013**. Denominadores praticamente idênticos (0,22% de
diferença), então a razão é essencialmente a razão das contagens brutas: o P004
rendeu **10% menos evidência por segundo** que o par em inglês.

## M2 — yield por segmento: **DIAGNÓSTICO, não comparação**

| | segmentos | yield/segmento | na banda 7–11 |
|---|---|---|---|
| PILOT-001-v2 | 9 | 16,5556 | sim |
| **PILOT-004** | **13** | **10,3077** | **NÃO** |

O PASS 1 do P004 produziu **13 segmentos**, fora da banda de comparabilidade
congelada `pass1_band_inclusive: [7, 11]`. Pela regra do próprio P001-v2 —
"Comparação de yield contra 4,89 só vale com PASS 1 dentro de 7–11 segmentos
(§12). Fora da banda, yield é diagnóstico" — **M2 não é comparação válida neste
piloto**. `variance_flag: SEGMENT_COUNT_13_FORA_DA_BANDA_7_11`.

Vale notar que M1 e M2 apontam para o mesmo lado por razões diferentes: a
densidade caiu 10%, mas o yield por segmento caiu 38% — quase todo o segundo
número é efeito de dividir a mesma massa de evidência por 13 caixas em vez de 9.
Só M1 diz algo sobre o pipeline aqui.

## M3 — cobertura do L0

| | cobertura | piso | resultado | revarreduras |
|---|---|---|---|---|
| PILOT-001-v2 | 90,61% | 0,735 | SATISFIED | 0 (`THRESHOLD_SATISFIED_WITHOUT_RESCAN`) |
| **PILOT-004** | **85,16%** | 0,735 | **SATISFIED** | 0 |

Mesma métrica `L0_UNION_SPAN_COVERAGE`, mesmo módulo, com pino de hash conferido
nos dois lados (`cts/coverage.py` = `ea58c05e…`, `cts/spans.py` = `7bcdcde2…`) —
esta é a condição de comparabilidade que a régua exigiu, e ela está satisfeita.
As duas cobrem folgadamente acima do piso, sem revarredura.

Ressalva de método: o runner `p00X_pass2_ckpt.py` mede a cobertura uma vez e não
implementa o ramo de revarredura. Como o piso foi satisfeito na primeira
medição, o ramo não seria acionado de todo modo — mas o `rescan_iterations: 0`
do P004 significa "não precisou", não "tentou e parou", que é o mesmo sentido do
P001-v2.

## Leitura conjunta

O pipeline rodou em português com **zero travessia de idioma**, cobertura acima
do piso e nenhuma rejeição de citação — a fonte em PT eliminou a classe de falha
que dominava os dois pilotos em inglês. O custo foi 10% menos densidade (M1).

O que **não** está fechado é a classe C: 40% das evidências com claim divergindo
do literal sob rótulo `SOURCE_EXPLICIT`, sem baseline histórico para dizer se
isso é o normal do pipeline ou uma degradação específica do português. Enquanto
esse número não tiver par, a conclusão sobre o objetivo secundário é **parcial**:
a travessia sumiu, mas não está provado que nada tomou o lugar dela.
