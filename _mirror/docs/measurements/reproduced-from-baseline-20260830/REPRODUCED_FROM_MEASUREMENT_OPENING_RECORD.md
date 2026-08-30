# OPENING RECORD — medição de `REPRODUCED_FROM`

**Data:** 2026-08-30 · **T0 da sessão:** `2026-08-30T01:01:32-03:00`
**Máquina:** `LenovoAIO27ARR9` · ext4. Nenhum script é executado a partir de `/mnt/g`.
**Repo:** `a049354d67d0374490138979c0a520a4abe2d495`, árvore limpa, 460 arquivos rastreados.
**Status:** `DECLARED_BEFORE_ANY_MEASUREMENT`.

> **O que foi inspecionado antes de escrever este record.** Apenas **schema e declarações
> de proveniência**: nomes de campo dos `EVIDENCE.jsonl`, os valores de
> `source_excerpt.source_file` / `source_sha256`, e o formato de marcação temporal dos L0.
> Nenhum predicado foi avaliado; nenhum PASS/FAIL, nenhuma contagem de elegíveis, nenhum
> denominador foi observado. Sem os nomes dos campos não há predicado mecânico possível;
> conhecê-los não antecipa resultado.

**Este record não é editado depois de hasheado.** Se a medição revelar defeito de
definição, o resultado é `INVALID` — o record não é reescrito para acomodar o achado.

---

## 0. O QUE ESTA MEDIÇÃO NÃO É

Não há limiar, piso, portão ou critério de aprovação. O objetivo é **descobrir um
baseline** que hoje não existe.

**`139/226 = 61,50%` está INVALIDADO e é PROIBIDO nesta medição**, inclusive como
referência ou expectativa. `139` é a contagem de regras com `precedence: UNDEFINED` do
P002 (população de 149 regras); `226` é a contagem de citações de identificador das três
rodadas cegas. A razão cruza populações. Não aparece em nenhum cálculo deste record nem
do instrumento.

---

## 1. CORPUS

Unidade de medida: **uma `evidence`** dos `EVIDENCE.jsonl` dos três bundles selados.

### 1.1 Os três `EVIDENCE.jsonl`

| bundle | caminho | bytes | sha256 |
|---|---|---|---|
| P002 | `_mirror/pilots/PILOT-002-v2/EVIDENCE.jsonl` | 290.173 | `64853f7ac06a470f09333a80469b38e443ea5ce7aa3aee2e116ea1877059abfd` |
| P003 | `_mirror/pilots/PILOT-003-v2/EVIDENCE.jsonl` | 1.508.572 | `64830129e3e806635110f8f7313e82f119fd89a4604eb2729419740478e6f4b0` |
| P004 | `_mirror/pilots/PILOT-004/02_PASS2/EVIDENCE.jsonl` | 79.376 | `f5951b32192c50bfede98fa911ba7829a2c5025bdfd4f7e96d4624167e10fd62` |

O instrumento recomputa os três sha256 e **aborta com `MEASUREMENT_INVALID`** se algum divergir.

### 1.2 L0 elegível — declarado pelo próprio bundle, resolvido por hash

Cada `evidence` declara sua própria proveniência em `source_excerpt.source_file` e
`source_excerpt.source_sha256`. Inspecionado: **dentro de cada bundle o par declarado é
unânime** (448/448 · 2463/2463 · 134/134).

| bundle | `source_file` declarado | `source_sha256` declarado | resolve, no repo rastreado, para |
|---|---|---|---|
| P002 | `L0-transcript-CUT.txt` | `85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29` | `_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt` (96.246 B) |
| P003 | `L0-transcript.txt` | `04fda222febbaeece075f0096274ae8be00a7eedd5582006dd99d6ccc465e192` | `_mirror/pilots/PILOT-003/00_SOURCE/L0-transcript.txt` (369.035 B) |
| P004 | `L0-transcript.txt` | `607f5a986bada49e81e8fcf3f1bce3ed2cdb63798ad6bcd4a8ab32018f2cb3f5` | `_mirror/pilots/PILOT-004/00_SOURCE/L0-transcript.txt` (19.624 B) |

A resolução é **por igualdade de sha256** sobre a varredura de `git ls-files` — não por
nome, não por semelhança. Cada sha bateu com **exatamente um** arquivo rastreado.

> **Regra de falha, fixada agora:** se o L0 de um bundle não resolver mecanicamente —
> caminho ausente, sha divergente, ou mais de um candidato — **todas as evidences daquele
> bundle recebem `INVALID` por instrumento**, com o motivo registrado, e o bundle sai do
> baseline. **É proibido escolher outro L0 "parecido".**
>
> Consequência já declarada: para o P002 o L0 elegível é o **cortado** (`-CUT`), porque é
> o que o bundle declara. `L0-transcript.txt` do P002 (107.653 B) **não** é elegível.

---

## 2. POPULAÇÃO, ELEGIBILIDADE E DENOMINADOR

### 2.1 Campos exatos encontrados no schema

Os três bundles têm schema idêntico. O material de reencontro é
**`source_excerpt.quote`** (string). O locator posicional é
**`source_excerpt.span`**, objeto com **`start_s`** e **`end_s`** (segundos).
Não existe nenhum outro campo de quote, excerpt ou âncora no schema.

### 2.2 Estados — definidos antes

- **`ELEGÍVEL`** — `source_excerpt.quote` presente e **não-vazia após `strip()`**.
  Só elegíveis recebem `PASS`/`FAIL`.
- **`PASS`** — a quote normalizada ocorre como substring do L0 normalizado do seu bundle.
- **`FAIL`** — é elegível e a quote normalizada **não** ocorre.
- **`NOT_APPLICABLE`** — sem material de reencontro por construção: `source_excerpt`
  ausente, `quote` ausente, ou `quote` vazia após `strip()`. **Nunca é `FAIL`.**
  Fora do denominador.
- **`INVALID`** — defeito de instrumento: JSON ilegível, `evidence_id` ausente, ou bundle
  cujo L0 não resolveu (§1.2). Fora do denominador, reportado à parte.

### 2.3 Denominador — declarado antes de rodar

```
baseline = PASS / (PASS + FAIL)
```

sobre **elegíveis**. `NOT_APPLICABLE` e `INVALID` **fora** do denominador, reportados em
campos próprios. Reportado por bundle **e** agregado.

**Prova de inclusão exigida no relatório:** o instrumento emite o conjunto de
`evidence_id` do numerador e o do denominador e **assere `set(PASS) ⊆ set(PASS ∪ FAIL)`**,
além de `|PASS| + |FAIL| = |elegíveis|`. Se qualquer asserção falhar → `MEASUREMENT_INVALID`.

---

## 3. PREDICADO

### 3.1 PRIMÁRIO — decide o baseline

> A **quote** da evidence, normalizada, ocorre como **substring** do L0 elegível do seu
> bundle, também normalizado. Ocorre ⇒ `PASS`. Não ocorre ⇒ `FAIL`.

Substring exata (`in`) sobre strings normalizadas. **Nada de fuzzy, distância de edição,
tokenização ou casamento aproximado.** Quote que ocorre **mais de uma vez** é `PASS` —
o predicado é existencial.

### 3.2 SECUNDÁRIO — breakdown, NÃO altera o baseline

Quando a evidence traz `span.start_s`/`end_s` numéricos e o L0 permite resolvê-los, o
instrumento registra se **alguma** ocorrência da quote cai **dentro da região** do locator.

**Resolução da região.** Os três L0 marcam tempo com linhas `**M:SS**`. O instrumento
constrói a lista `(segundos, offset)` desses marcadores no texto normalizado. A região de
uma evidence com span `[a, b]` vai do offset do **último marcador com `sec ≤ a − W`** até
o offset do **primeiro marcador com `sec > b + W`** (ou fim do arquivo).

**Janela de tolerância `W = 30` segundos**, fixada agora, antes de qualquer resultado.

Estados do secundário: `IN_REGION` · `OUT_OF_REGION` · `LOCATOR_UNRESOLVED`.

> **`LOCATOR_UNRESOLVED`** — o span é declarado mas não resolve (não numérico, `start_s >
> end_s`, ou fora do alcance dos marcadores do L0). Vai para **contador próprio** e
> **não altera o estado primário**. Comportamento fixado aqui: uma falha de locator nunca
> converte um `PASS` em `FAIL` nem vice-versa.

### 3.3 NORMALIZAÇÕES — lista taxativa

Aplicadas **identicamente** à quote e ao L0, nesta ordem, e **nada além**:

1. `unicodedata.normalize("NFC", s)`
2. `s.casefold()`
3. colapso de whitespace: toda sequência `\s+` → um único `U+0020`
4. `strip()`

**Proibido:** remoção de acentos · remoção de pontuação · stemming/lematização ·
troca de aspas tipográficas · remoção das marcações `**M:SS**` · qualquer casamento
aproximado.

*(Nota de desenho: as marcações `**M:SS**` permanecem no L0 porque algumas quotes as
contêm literalmente. Removê-las seria normalização não declarada.)*

### 3.4 LÍNGUA

Cada quote é comparada **apenas** contra o L0 do seu próprio bundle, na língua daquela
fonte: **EN** para P002 e P003, **pt-BR** para P004. **Nenhuma tradução, nenhum casamento
cross-língua.** O campo `claim` — paráfrase normalizada em português nos três bundles —
**não entra na medição em ponto nenhum**: medir `claim` contra L0 mediria tradução ou
paráfrase, não reprodução.

---

## 4. CONTROLES

Em `~/reproduced-from-baseline/fixtures/`, **fora da população**, rodados **antes** da medição.

- **Controle positivo** — fixture cuja quote é copiada **verbatim** de um trecho real de
  um L0 do corpus. **TEM de dar `PASS`.**
- **Controle negativo** — a **mesma** fixture com a quote deliberadamente alterada.
  **TEM de dar `FAIL`.**

**Qualquer controle fora do esperado ⇒ `MEASUREMENT_INVALID` e parada imediata.** Sem
ajuste, sem segunda tentativa, sem reescrita deste record.

---

## 5. RESTRIÇÕES DE EXECUÇÃO

- Instrumento **read-only** sobre repo e Drive. Zero escrita em
  `/home/mtx/course-to-skill-claude` e em `/mnt/g`.
- **Zero chamadas de API.** A medição é casamento de string puro.
- **Contagem manual proibida.** Todo número do JSONL e do `.md` de saída é emitido pelo
  script. Nenhum número é digitado à mão em artefato algum desta rodada.
- Saídas: `out/reproduced-from-raw.jsonl` (um registro por evidence) e
  `out/REPRODUCED-FROM-BASELINE-REPORT.md`, ambos gerados pelo script.
