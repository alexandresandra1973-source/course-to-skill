# PILOT-MS-000B — VEREDITO DA RODADA

**Classificação:** **`PILOT_MS_000B_INVALID`**
**Data:** 2026-08-30 · **Opening Record:** `3e251d7cdbf5307aef89840d3b733aad49211fa0c887883710b622e93dd01638`

> **Motivo: instrumento incapaz de medir o que declara** — condição de `INVALID`
> explicitamente prevista na §13 do Opening Record, escrita **antes** da execução.

---

## 1. POR QUE `INVALID` E NÃO `FAIL`

`FAIL` significaria que um defeito **real** escapou no corpus ou no pipeline.
Não foi o que aconteceu. **Dois dos meus próprios medidores estão quebrados**, e os
resultados que eles produziram não medem o que dizem medir.

### Divergência declarada com o `summary.json`

`consolidate.py` gravou `PILOT_MS_000B_FAIL`. **Esse artefato fica preservado como está.**
O classificador dele foi escrito com apenas dois ramos — `PASS` ou `FAIL` — e **não
implementa o ramo `INVALID` que o próprio Opening Record declara**. Isso é uma terceira
falha de instrumento, e está registrada aqui em vez de corrigida em silêncio.

Este veredito aplica o critério **declarado no Opening Record**, não um critério novo.

---

## 2. DEFEITO 1 — o tokenizador cola pontuação ao token

`content_tokens()` usa `[a-z0-9][a-z0-9\-_/\.]{2,}`, que admite `.` **dentro** do token.
Pontos finais de frase grudam na palavra:

```
'pushing commits to github.'  ->  ['commits', 'github.', 'pushing']
'the remote repository.'      ->  ['remote', 'repository.']
'Claude Code.'                ->  ['claude', 'code.']
```

Logo `github.` ≠ `github` e `repository.` ≠ `repository`.

**Os dois controles positivos foram desenhados para compartilhar 2 tokens** —
`github` + `repository` no `BLK-CTRL-01`, `remote` + `repository` no `BLK-CTRL-02`.
O tokenizador os separou e a interseção caiu para **1**, abaixo da regra `>= 2`.

| controle | interseção medida | esperado pelo desenho |
|---|---|---|
| `BLK-CTRL-01` | `['repository']` = 1 | `github` + `repository` = 2 |
| `BLK-CTRL-02` | `['remote']` = 1 | `remote` + `repository` = 2 |

**O controle não reprovou a blocagem — ele reprovou o tokenizador.** Os números de redução
de par (`158/1968`, `115/1722`, `137/1620`) foram computados com o mesmo tokenizador
quebrado e **não são interpretáveis**.

## 3. DEFEITO 2 — o predicado de isolamento confunde vocabulário com exclusividade

`isolation_check()` define informação exclusiva de um pacote como *token de conteúdo
presente nas quotes dele e ausente nas do outro*. Medido:

| token | em A | em B | classificado como |
|---|---|---|---|
| `claude` | sim | não | **exclusivo de A** |
| `code.` | não | sim | **exclusivo de B** |
| `code` | sim | sim | — |
| `github` | sim | sim | — |

**O curso inteiro é sobre Claude Code.** Uma claim do pacote B mencionar `claude` **não é
falsa atribuição** — é o assunto do material. As 11, 6 e 11 "violações" dos três runs são
quase todas exatamente isso.

O predicado conflate **"token ausente nas quotes do outro pacote"** com **"informação
exclusiva daquele pacote"**. São coisas diferentes: ausência de uma palavra nas citações de
B não torna essa palavra propriedade de A. Somado ao defeito 1, `code` e `code.` viram
tokens distintos e produzem exclusividade fantasma nos dois sentidos.

**O predicado não mede isolamento.** Mede diferença de vocabulário citado.

---

## 4. O QUE ESTA RODADA MEDIU DE FORMA VÁLIDA

Estes resultados **não dependem** dos dois medidores quebrados e ficam registrados:

| medição | resultado |
|---|---|
| **KILL-1** camada selada byte-idêntica antes/depois | **intacta** — `FULL`, `CUT` e `EVIDENCE.jsonl` inalterados |
| **Dois Source Packages reais** com hashes distintos | A `4290b88f…` · B `5c32b8ed…` |
| **Colisão deliberada de `local_id`** | `EV-0001` em ambos; 100 ids nus, 100 identidades qualificadas distintas |
| **Referências cross-package nuas** | **0** |
| **Proveniência** `claim → evidence → anchor → slice → CUT → FULL` | **100%** das 253 claims seladas |
| **`LOCATED_IN` / `REPRODUCED_FROM`** medidos separadamente | A 44/44 e 43/44 · B 56/56 e 55/56 |
| **`ENTAILED_BY`** | 253/253 `ENTAILED` — ver ressalva §5 |
| **KILL-2 variância** | seladas 89 / 83 / 81 · máx/mín = **1,0988×** ≤ 1,5× |
| **Preservação de workflow** | hash canônico da estrutura **idêntico** source ↔ fusion nos 3 runs, nos 2 pacotes |
| **`COMPILE-TRACE`** | 9/9 chamadas, campos completos, config idêntica entre runs |
| **Orçamento** | **9 de 24** chamadas · 73.525 tokens de entrada, 34.385 de saída |

## 5. RESSALVA MATERIAL SOBRE O `ENTAILED_BY` — 253/253

O juiz **julgou de fato**: as justificativas citam o texto da evidência
(*"A evidência diz literalmente que…"*). Não carimbou.

**Mas 253 de 253 `ENTAILED`, com zero `NOT_ENTAILED` e zero `INDETERMINATE`, é um
resultado sem poder discriminante demonstrado.** O Opening Record declarou controles
positivos para a **blocagem** e **não declarou controle negativo para o juiz** — não existe,
nesta rodada, prova de que o instrumento seja capaz de emitir `NOT_ENTAILED`.

Duas leituras seguem abertas e esta rodada **não** as separa:
1. o gerador foi instruído a não acrescentar nada e obedeceu, produzindo reformulações
   conservadoras genuinamente implicadas;
2. o juiz é permissivo demais para discriminar.

**Não corrijo isso agora.** Adicionar controle negativo depois de ver 253/253 seria mudar
metodologia em reação ao resultado — exatamente o que o Opening Record proíbe. Fica como
requisito **declarado** para a próxima rodada.

---

## 6. O QUE NÃO FOI FEITO

- **Nada foi corrigido para obter `PASS`.**
- **Nenhuma rodada adicional foi iniciada** — §18 manda parar no primeiro portão.
- O Opening Record **não foi reescrito**.
- `summary.json`, `runs.json`, `COMPILE-TRACE.jsonl` e os Fusion Packages ficam **como
  foram produzidos**, inclusive o `FAIL` do consolidador.

## 7. CORREÇÕES QUE A PRÓXIMA RODADA PRECISA — declaradas, não aplicadas

1. **Tokenizador:** separar pontuação terminal; `github.` deve tokenizar como `github`.
2. **Predicado de isolamento:** redesenhar. Ausência de vocabulário não é exclusividade de
   informação. Plantar marcadores **sintéticos e únicos** em cada pacote e testar migração
   desses marcadores — como as fixtures do MS-000A, não por estatística de vocabulário.
3. **Controle negativo do juiz de entailment:** claims deliberadamente não-implicadas
   (com fato, causalidade ou generalização acrescentados) que **têm de** receber
   `NOT_ENTAILED`.
4. **Classificador do consolidador:** implementar o ramo `INVALID` que o Opening Record
   declara.

**Cada correção vai para uma rodada nova e explicitamente separada, com Opening Record
próprio** — a mesma disciplina que a ROUND 3 do MS-000A aplicou.
