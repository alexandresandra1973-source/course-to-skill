# T2 — baseline da classe C em inglês · pendência do BLOCO 2b **FECHADA**

O BLOCO 2b terminou com um buraco: os 54 avisos do validador de citação no P004
(40% das evidências) não tinham com o que ser comparados, porque os registros de
chamada do P001-v2 nunca foram publicados. O T2 fecha isso reprocessando o
PILOT-001-v2 **neste bot**, nas mesmas condições, para gerar os registros que
faltavam.

## Condições idênticas nos dois lados

| | |
|---|---|
| runner | `p00X_pass2_ckpt.py` — mesmo código, só pinos e caminhos diferem |
| extractor | `bd17ca4147d8ee7dc68cc2969e0132b7d4d5ca11403083c6537b019d2b09db5c` |
| compilador | `compiler-v2/0.2.1-frozen` |
| modelo | `claude-opus-5`, effort `high` |
| máquina | bot-04 |
| detector da classe C | idêntico, mesma função nos dois |

Insumos do P001-v2 vieram do Drive com hash conferido contra o
`COMPILATION_MANIFEST.yaml` dele: L0 `068b4998…` **CONFERE**, temporal-map
`845cea7d…` **CONFERE**. Tudo em `p001v2-remac/`. **Nada do PILOT-001-v2
histórico foi tocado.**

## Resultado

| | PT (PILOT-004) | EN (PILOT-001-v2-remac) |
|---|---|---|
| segmentos | 13 | 9 |
| drafts retornados | 134 | 175 |
| drafts aceitos | 134 | 175 |
| **aceitos só após normalização** | **0** | **108** |
| rejeições | 0 | 0 |
| avisos | 54 | 79 |
| **classe C por evidência** | **40,30%** | **45,14%** |
| cobertura L0 | 85,16% | 85,08% |

Motivo, nos dois: `CLAIM_DIVERGE_DO_LITERAL_COM_ROTULO_SOURCE_EXPLICIT`, único.

## Leitura

**Os 40% do português não são degradação.** A taxa em inglês é **45,14%**, ou
seja, quase 5 pontos **mais alta**. O aviso de claim divergindo do literal sob
rótulo `SOURCE_EXPLICIT` é comportamento de base do pipeline, não efeito do
idioma. O cenário que a régua temia — "A baixo com C alto só move o problema de
lugar" — **não se realizou**: A caiu a zero e C ficou abaixo do baseline.

**A diferença maior está em outra linha, e é maior que a da taxa de avisos.**
`aceitos_só_após_normalização`: **0 em português, 108 em inglês** — 62% das
evidências em EN só passaram no portão de citação depois da normalização de
formato (remoção de marca `**M:SS**` e colapso de espaço). Em português,
**nenhuma** precisou: as 134 citações casaram literalmente na primeira tentativa.

Isso diz que a fonte em PT produz citação que bate direto, e que a proteção
exercitada pelo canário C6 — a que separa normalizar formato de afrouxar o
portão — carrega quase todo o peso no lado inglês e fica ociosa no lado
português. Nos dois casos ela não deixou passar nada indevido: **0 rejeições e 0
citações fabricadas aceitas** dos dois lados.

## Ressalva de comparabilidade, declarada

O reprocessamento rendeu **175 evidências** contra as **149** do P001-v2
histórico, com o mesmo L0 e o mesmo temporal-map — 17% a mais. As causas
possíveis são o extractor (o histórico rodou na Lenovo, com código sem
contraparte conferível — ver `R1_ABERTO_SEM_CONTRAPARTE`) e a variação normal do
modelo entre execuções.

Por isso: **a comparação de classe C acima é válida** — ela põe frente a frente
duas execuções feitas na mesma noite, na mesma máquina, com o mesmo código, e é
para isso que o T2 existe. Já a comparação do **M1/M2 do BLOCO 2b**, que usou os
números **históricos** do P001-v2, permanece como está e não foi refeita: mudar
o denominador agora, depois de ver o resultado, seria trocar o critério com o
jogo em andamento. Se quiser M1/M2 recalculados contra o remac, é decisão sua —
registrado como **PENDENTE-ALEXANDRE**.

Para referência, sem substituir nada: com o remac, o P001-v2 daria densidade
175/905 = 0,19337 ev/s contra 0,14839 do P004 (razão 0,767, contra 0,901 do
cálculo histórico).

## Conclusão sobre o objetivo secundário

Agora é **completa**, não mais parcial:

- classe A (travessia PT×EN): **0** no P004, contra travessia estrutural em
  66% e 78% das quotes de P001-v2 e P003-v2;
- classe C: **abaixo** do baseline em inglês (40,30% × 45,14%);
- dependência de normalização: **0% × 62%**;
- rejeições e citações fabricadas aceitas: **0** dos dois lados.

A travessia de idioma sumiu e **nada tomou o lugar dela**.
