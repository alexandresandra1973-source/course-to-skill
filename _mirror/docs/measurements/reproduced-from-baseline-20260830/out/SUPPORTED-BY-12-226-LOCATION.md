# `SUPPORTED_BY` 12/226 — LOCALIZAÇÃO DOCUMENTAL

**Gerado por script. Nenhum número digitado à mão. Nada foi reavaliado ou remedido.**

## 1. Onde os dois números estão declarados

| artefato | linha | texto |
|---|---|---|
| `_mirror/docs/PILOT-002-CLOSURE.md` | 47 | 226 citações de identificadores internos |
| `_mirror/docs/PILOT-002-CLOSURE.md` | 173 | \| identificadores citados nas três rodadas \| **226** \| |
| `_mirror/docs/PILOT-002-CLOSURE.md` | 174 | \| que **existem** no bundle \| **226** — verificado mecanicamente contra o índice \| |
| `_mirror/docs/PILOT-002-CLOSURE.md` | 175 | \| que foram verificados quanto a **ancorar o que dizem ancorar** \| **12** \| |
| `_mirror/docs/PILOT-002-CLOSURE.md` | 176 | \| cobertura da verificação \| **12 ÷ 226 = 5,3%** \| |
| `_mirror/docs/PILOT-002-CLOSURE.md` | 181 | em 226 de 226. |

Mensagem de commit (`git log --all --format='%H%n%B'`), no mesmo espaço de busca:

```
3.1 FIDELIDADE DOS IDENTIFICADORES — 226 citados existem, 12 verificados
    quanto a ancorar o que dizem = 5,3%. E a promessa central do produto.
Correcao de numero: o total de citacoes nas tres rodadas e 226, nao 160, e a
cobertura da verificacao de ancoragem e 5,3%, nao 7,5%. Contado dos artefatos.
```

## 2. O 226 é recomputável dos artefatos brutos

| rodada | artefato | sha256 | respostas | citações | inexistentes |
|---|---|---|---|---|---|
| primada | `p002-blind-run.json` | `4d441bfdb55cbcdb935ecb4c6513bce5da8bb4c98bb1006670b3b4522d347c5b` | 10 | 130 | 0 |
| sem priming | `p002-unprimed-run.json` | `1fa154cd346e3dd081ddb378109c6c6b294afbf4531cc1e21c24e0264f569e88` | 2 | 18 | 0 |
| falso-negativo | `p002-fn-run.json` | `8d9bc108307f54dcfb018183ea49be9e3979d4f96293e477b0332eee196f21e9` | 12 | 78 | 0 |
| **TOTAL** | | | | **226** | **0** |

CLOSURE declara `130 + 18 + 78 = 226`. Recomputado dos artefatos: **226**. **Reconcilia.**
Identificadores inexistentes no bundle, recomputado: **0** — é a origem do `226/226`.

## 3. O 12 é recomputável, e o gabarito é pré-registrado

- `p002-fn-sample.json` · sha256 `525a0eeac3ab15173dfbadc0fbbfc9f9eb26666c71f26426e623d4457bed6567`
- `artifact_status` = `SAMPLE_DECLARED_BEFORE_ANY_QUESTION_WAS_ASKED`
- `n` = 12 · `len(itens)` = 12 · `len(fn-run.results)` = 12
- todos os itens trazem `action_esperada`: True
- todos os itens trazem `ancora`: True
- `fn-run.sample_sha256` = `525a0eeac3ab15173dfbadc0fbbfc9f9eb26666c71f26426e623d4457bed6567` — **confere** com o sha real do sample
- critério de pontuação declarado antes: `['ACERTO', 'ACERTO_PARCIAL', 'FALSO_NEGATIVO', 'INCONCLUSIVO', 'rubrica']`
- sinais mecânicos da rodada: `{'n': 12, 'citou_a_regra_ancorada': 12, 'com_token_de_recusa': 0, 'identificadores_inexistentes_no_total': 0}`

Seleção da amostra, do próprio artefato:

```json
{
  "metodo": "amostragem sistemática sobre a lista ordenada por rule_id",
  "passo": 5,
  "indices": [
    0,
    5,
    10,
    15,
    20,
    25,
    30,
    35,
    40,
    45,
    50,
    55
  ],
  "semente_aleatoria": null,
  "porque_nao_e_conveniencia": "o filtro é estrutural e o passo é aritmético; nenhuma regra foi lida antes de entrar. Reproduzível por qualquer um com o mesmo bundle."
}
```

## 4. Instrumentos versionados

| script | bytes | sha256 |
|---|---|---|
| `p002_false_negative_sample.py` | 7630 | `635f422af4961b35d76c2ad40e510416e07c2a4b53c43c23d4fce63bf70cc000` |
| `p002_false_negative_run.py` | 10067 | `dbbea9590cb99a4fad3ace02864ef6b77c35c2f9320f454423921eec30fff620` |
| `p002_judge.py` | 9516 | `aa0ccb5962efce9dafeb476c768f451462e31f77c9c0c208ec64e234d4d1806f` |
| `p002_rejudge.py` | 6082 | `abb30ef474b91d14a7141da19f60e5f5049fe2fa3325087b1d5fdb2260abf198` |
| `p002_blind_run.py` | 7996 | `c4d8a73cce5dc2266cbca508c66624753090abf1e78203e9d2a81c703824fc12` |
| `p002_unprimed.py` | 10809 | `3291be14b6180b3aae76a0d9b82248a2de007ab1acc7c8c21017290f2dfe13fd` |

## 5. Natureza do predicado

- juiz separado: `judge_model = claude-opus-5`
- o juiz **viu**: ['conteúdo esperado de cada item', 'resposta de cada item', 'a rubrica invertida']
- o juiz **não viu**: ['o rule_id ancorado', 'as perguntas', 'a base', 'qualquer identificação do projeto ou do domínio']
- julgamento vigente persistido: `payload_sha256 = 5dc9ebe6fa1412c272be35e8dcf36778dc3b0271895348f16f9350f336e96f35`
- agregado vigente: `{'ACERTO': 12, 'ACERTO_PARCIAL': 0, 'FALSO_NEGATIVO': 0, 'INCONCLUSIVO': 0}`
- julgamento superado **preservado**: `payload_sha256 = 9d96b9e8ae3be50717dc34f23afbcef7e67c1da10045e80dc897fdec3aabd151`
  - motivo: neutralizador substituía por substring; `recursos` e `Cursor` eram corrompidos. Preservado, não apagado.

O predicado de substância — *`R-0068` de fato diz o que a resposta afirma que ele diz* —
é **julgamento**, não casamento de string. Rodá-lo de novo exigiria chamada de modelo.
A saída do juiz está **persistida e endereçada por hash**, então é auditável por
**replay**, não por recomputação mecânica.

## 6. Classificação

# `AUDITABLE_MEASUREMENT`

**Qualificador:** `JUDGED_WITH_PREREGISTERED_RUBRIC`.

Justificativa, item a item:

| requisito | achado |
|---|---|
| artefato onde os números estão declarados | `PILOT-002-CLOSURE.md:173-176` + mensagem de commit |
| método descrito | funil estrutural de 6 filtros, passo aritmético 5, sem semente aleatória |
| instrumento versionado | 6 scripts `p002_*.py`, com sha256 |
| gabarito pré-registrado | sim — `action_esperada` por item, `artifact_status` sela o momento |
| critério de pontuação pré-declarado | sim — 4 faixas, rubrica invertida, gravada antes de rodar |
| 226 recomputável de artefatos brutos | **sim** — recomputado nesta rodada e reconcilia |
| 12 recomputável de artefatos brutos | **sim** — `n`, `len(itens)`, `len(results)` e o sha do sample conferem |
| veredito por item recomputável mecanicamente | **não** — é julgamento; auditável por replay do output selado |

Nada está `NOT_LOCATED` e nada é `DECLARED_BUT_INSTRUMENT_NOT_FOUND`: o instrumento
existe, está versionado, a amostra está selada e pré-registrada, e os dois números
recomputam dos artefatos. O que **não** é mecânico é o predicado de substância — e
isso é propriedade do predicado, não lacuna de instrumentação.
