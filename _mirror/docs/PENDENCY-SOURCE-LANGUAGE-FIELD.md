# PENDÊNCIA DE SPEC — campo em língua da fonte ao lado de todo campo traduzido

**Status:** PENDENCIA_ABERTA · registrada 2026-08-12 · **NÃO implementar agora**
(o compilador está congelado no meio do PILOT-003)

## O defeito

O pipeline produz texto em **português** a partir de fonte em **inglês**:
`claim`, `topic` e `function` do PASS 1, nomes de tema. A fonte — `quote`, L0 —
permanece em inglês. **Todo verificador mecânico que compara os dois lados
compara línguas diferentes**, e falha.

Não é hipótese. São quatro ocorrências medidas:

| # | verificador | como falhou | custo |
|---|---|---|---|
| 1 | aviso claim×literal | acusava toda tradução: IA↔AI, 'agente 1'↔'Agent one', 4.000↔4,000, US$↔$ | **60 falsos positivos em 149**, 40% de disparo; APOSENTADO |
| 2 | medidor de cobertura de tema (2ª tentativa) | tópicos PT contra citações EN | zeros artificiais em todos os temas |
| 3 | controle positivo em L0 (1ª versão) | palavra portuguesa sem acento dá zero em texto inglês | 8 temas marcados como ARTEFATO, eram indecidíveis |
| 4 | medidor de tema (6ª tentativa) | ordem/adjacência: `youtube instream` vs `anúncio instream do YouTube` | rotulou LACUNA_DE_EXTRACAO num tópico com **48 evidências** |

A ocorrência 4 é a mais grave porque **produziu uma alegação falsa com a forma
exata de um achado verdadeiro**: "o curso cobre X e nossa extração falhou".

## A causa, e é sempre a mesma

Um campo traduzido não preserva: a grafia do termo técnico, a ordem das palavras,
a adjacência, nem a fronteira de token. Qualquer verificador que case string
entre `claim` e `quote` está apostando que a tradução preservou uma dessas
quatro coisas. Nenhuma se preserva.

## O conserto proposto

**Manter, ao lado de cada campo traduzido, um campo em LÍNGUA DA FONTE.**

| campo hoje | campo a acrescentar |
|---|---|
| `claim` (pt) | `claim_source_language` (en) |
| `topic` (pt) | `topic_source_language` (en) |
| `function` (pt) | `function_source_language` (en) |
| nome de tema (pt) | termo canônico na língua da fonte |

Com isso, todo verificador mecânico compara **inglês com inglês**, e as quatro
falhas acima deixam de ser possíveis por construção — não por disciplina de quem
escreve o próximo verificador.

## Por que isto é spec e não bug deste piloto

Cada verificador novo custou **três a seis tentativas** para acertar, e cada
tentativa produziu um achado falso com a forma de achado verdadeiro. Sem o campo
na língua da fonte, o próximo verificador repete o ciclo — e o custo não cai com
experiência, porque a armadilha é estrutural.

## Custo declarado

Acrescenta um campo por entidade e obriga o extrator a emitir a claim duas
vezes. Aumenta tokens de saída e o tamanho dos artefatos. É preço de exatidão de
medição, e a alternativa medida é seis tentativas por verificador.

## Não fazer agora

O compilador está congelado no meio do PILOT-003. Mudar o esquema aqui quebraria
a comparabilidade entre os três pilotos, que é a única base de comparação
existente. Fica para a próxima versão.
