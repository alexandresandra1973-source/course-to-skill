# PILOT-MS-000B / ROUND 1 — CLASSIFICAÇÃO

**`decision_id`:** `DR-MS-000B-R1-001` · **Data:** 2026-08-30
**Classificação:** **`INVALID_INSTRUMENT`**
**Ator:** Design Review externa · **Registro aditivo.** Nada da Round 1 é alterado.

> **Não é `FAIL` do corpus.** A Round 1 é evidência histórica válida de um **instrumento
> incapaz de medir integralmente o que declarou**.

---

## Os quatro motivos, independentes entre si

**1 · Tokenizer/blocker defeituoso.** `content_tokens()` admitia `.` dentro do token, então
pontuação terminal grudava na palavra: `github.` ≠ `github`, `repository.` ≠ `repository`.
Os dois controles positivos foram desenhados para compartilhar 2 tokens e o tokenizador os
separou — interseção 1, abaixo da regra `>= 2`. **O controle reprovou o tokenizador, não a
blocagem.** Os números de redução de par não são interpretáveis.

**2 · Predicado de isolamento confundia vocabulário com exclusividade.** Definia informação
exclusiva como *token presente nas quotes de um pacote e ausente nas do outro* —
classificando `claude` como exclusivo de A **num curso inteiro sobre Claude Code**. Ausência
de uma palavra nas citações de B não a torna propriedade de A. As 11/6/11 "violações" são
quase todas isso.

**3 · Juiz `ENTAILED_BY` sem controle negativo nem `INDETERMINATE` pré-declarados.** O
resultado 253/253 `ENTAILED` **não demonstra poder discriminante**: não há prova, naquela
rodada, de que o juiz fosse capaz de emitir `NOT_ENTAILED`. O juiz julgou de fato — as
justificativas citam o texto da evidência — mas isso não é o mesmo que discriminar.

**4 · Consolidador sem o ramo `INVALID`.** `consolidate.py` tinha apenas `PASS` ou `FAIL` e
**não implementava o ramo `INVALID` que o próprio Opening Record da Round 1 declarava**.
Por isso `summary.json` gravou `FAIL` onde o contrato pedia `INVALID`.

---

## O que fica proibido

A Round 1 **não** é apagada · **não** é reclassificada retroativamente · **não** é corrigida
no lugar · **não** é tratada como `PASS` parcial.

## `ROUND_1_OBSERVATION`

Resultados mecanicamente úteis da Round 1 podem ser citados **apenas** sob este rótulo, e
**nunca** como evidência final de aceitação do MS-000B:

| observação | valor |
|---|---|
| KILL-1 camada selada byte-idêntica | intacta |
| dois Source Packages com hashes distintos | A `4290b88f…` · B `5c32b8ed…` |
| identidades qualificadas distintas sob colisão deliberada | 100/100, 0 refs nuas |
| proveniência resolvendo até `FULL` | 253/253 |
| variância máx/mín | 1,0988× |
| preservação de workflow por hash de estrutura | idêntico nos 3 runs |
| `COMPILE-TRACE` | 9/9 chamadas, config idêntica |

**A Round 2 não reutiliza nenhum desses resultados avaliativos.** Ela reexecuta tudo.
