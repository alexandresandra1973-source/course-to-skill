# MS-001B EXEC-3 — HARD STOP: DOIS DEFEITOS DE INSTRUMENTO

    MS_001B_HARD_STOP_INSTRUMENT_DEFECT

Data: 2026-08-31. Execução interrompida na chamada 6 de 18, deliberadamente, para não
queimar franquia do plano em runs deterministicamente inválidas.

**Nem o transporte nem o modelo falharam.** Ambos os defeitos são anteriores a esta
execução e estavam latentes: a execução 1 morreu por saldo de API e a execução 2 morreu
na chamada 1, antes de qualquer batch pequeno. A execução 3 foi a primeira a chegar aos
dados e é por isso que os defeitos aparecem agora.

---

## DEFEITO 1 — o schema proíbe os rótulos da própria partição v2

`RELATION-SCHEMA-v1.json` declara:

    "batch_id": { "type": "string", "pattern": "^BATCH-[1-4]$" }

O schema é embutido **verbatim** no prompt do juiz. A partição v2, criada na recuperação
`169d514`, rebatizou o último batch como `BATCH-4A` / `BATCH-4B`. Nenhum dos dois casa
com `^BATCH-[1-4]$`.

Resultado em RUN-1 BATCH-4A: o juiz **obedeceu ao schema que recebeu** e emitiu
`batch_id = "BATCH-4"`, com os 11 julgamentos corretos e completos. O validador,
que compara com o rótulo literal `BATCH-4A`, falhou fechado:

    R03_BATCH_ID_MISMATCH  ->  RUN-1 INVALID

O prompt e o schema, dentro da mesma mensagem, se contradizem. O modelo escolheu o
schema. Não há saída: as três runs falhariam de forma idêntica em BATCH-4A e BATCH-4B,
consumindo 15 chamadas para produzir três runs `INVALID`.

Os canários pré-modelo não pegam isso: 65/65 passam porque nenhum deles confronta o
`pattern` do schema com os rótulos da partição. É uma lacuna de canário.

## DEFEITO 2 — os controles de corpus BC1–BC5 são produtos cartesianos

`blocker/control-mappings-v03.json`:

| controle | claims B | claims C | "pairs" declarados | produto cartesiano |
|---|---|---|---|---|
| BC1_genuine_overlap | 9 | 5 | 45 | **45** |
| BC2_scope_difference | 3 | 8 | 24 | **24** |
| BC3_specialization | 13 | 6 | 78 | **78** |
| BC4_false_conflict | 3 | 7 | 21 | **21** |
| BC5_unrelated | 6 | 6 | 36 | **36** |

Em todos os cinco casos `pairs == |B| × |C|`. Os controles não são pares curados: são
o produto cartesiano de dois conjuntos de claims, rotulado em bloco. Um produto
cartesiano não pode ser inteiramente "genuine overlap" — a maioria das células
combina claims que nada têm em comum.

Consequência medida, e **reproduzida de forma independente nos dois transportes**:

| conjunto | pares no pairset V1 | EXEC-1 (SDK Python, PAYG) | EXEC-3 (Route B, Max) |
|---|---|---|---|
| BC1_genuine_overlap | 27 | 27 × UNRELATED | 23/23 × UNRELATED |
| BC2_scope_difference | 7 | 7 × UNRELATED | 6/6 × UNRELATED |
| BC3_specialization | 55 | 54 × UNRELATED | 53/53 × UNRELATED |
| BC4_false_conflict | 9 | 9 × UNRELATED | 9/9 × UNRELATED |
| sem controle | 20 | 20 × UNRELATED | 16/16 × UNRELATED |
| **total julgado** | | **96/96 UNRELATED** (RUN-1)<br>**96/96** (RUN-2) | **86/86 UNRELATED** |

Exemplo, par BC1 `CL-0013|CL-0036`:

* esquerda: *"Com a instância aparecendo como desconectado, o usuário vai em
  configurações e gera QR Code…"*
* direita: *"Os cinco campos necessários são: quem mandou, a Instância que recebeu a
  mensagem, a mensagem, o ID da mensagem e o nome da pessoa."*

Os dois transportes chegaram à mesma conclusão, com a mesma razão:

* EXEC-3: *"O termo 'Instancia' aparece nos dois, mas designa contextos diferentes."*
* EXEC-1: *"Compartilham a palavra 'Instancia' mas tratam de objetos distintos."*

**O juiz está certo.** O par realmente não tem relação. O rótulo BC1 é que está errado.

### Por que isto não é falha do juiz

Os controles sintéticos J1–J10, que são pares curados, saem perfeitos:

    RUN-1 CONTROL  10/10 OK
    RUN-2 CONTROL  10/10 OK   (idêntico, relação por relação)

com distribuição rica — IDENTICAL, CORROBORATES, SPECIALIZES/RIGHT_TO_LEFT,
CONTRADICTS, SUPERSEDES/RIGHT_TO_LEFT, UNRELATED, INDETERMINATE. O juiz distingue as
sete relações quando os pares de fato as instanciam.

### O que isso invalida

* A auditoria pós-hoc BC1–BC4 não pode medir capacidade: o "ground truth" não é verdade.
* O "PASS" de BC4 (zero falsas contradições) é **degenerado** — passa porque tudo é
  UNRELATED, não porque o juiz resistiu a vocabulário compartilhado.
* A calibração do blocker e a seleção da variante V1 foram feitas contra essas
  mesmas métricas de produto cartesiano (`blocker/variant-metrics-v03.json`).

## O que NÃO foi feito

Nenhum output foi corrigido semanticamente. Nenhum instrumento selado foi alterado:
schema, prompt, taxonomia, pairset, blocker, partição, controles e Source Packages
permanecem byte-idênticos. Nenhum Fusion foi criado. Nenhum `fusion_id` foi emitido.

Corrigir o defeito 1 exigiria alterar `RELATION-SCHEMA-v1.json`; corrigir o defeito 2
exigiria refazer `control-mappings-v03.json` e reabrir a calibração do blocker. Ambos
são proibidos pelo §11 do briefing sem nova decisão externa.
