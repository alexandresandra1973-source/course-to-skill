# `GIT_NATIVE_BY_DESIGN` — materialização da governança do espelho

**Natureza:** `POSTERIOR_MATERIALIZATION_OF_EXISTING_DECLARATION`
**Commit-fonte:** `378d764352661eb81ee3c0e6a5d0a52ec4e26332`
**Data desta materialização:** 2026-08-30
**Classe deste arquivo:** `GIT_NATIVE_BY_DESIGN` — ele próprio nasce no git e não tem
contraparte no Drive por desenho.

---

## O que este arquivo é, e o que ele não é

**A fonte histórica permanece o commit `378d764`.** Este arquivo **não** o substitui, não o
corrige e não o reescreve. A mensagem daquele commit é imutável e continua sendo a
autoridade sobre o que foi declarado em 2026-08-29.

**Este arquivo foi criado posteriormente**, em 2026-08-30, com um objetivo único: tornar a
declaração de governança **encontrável por auditoria baseada em arquivo**. Antes dele, a
regra que protege 12 artefatos de remoção por sincronização existia **apenas** dentro de
uma mensagem de commit. Qualquer script de empacotamento que varra o sistema de arquivos
— e é o que scripts de empacotamento fazem — não a encontraria, e poderia apagar os
artefatos que ela protege.

> **Não se alega que este arquivo existia à época do commit.** Ele não existia. Tudo aqui
> na seção **A** é citação ou consequência direta do que o commit declarou; tudo na seção
> **B** é posterior e está marcado como tal.

---

# A. `HISTORICAL_DECLARATION_AT_378d764`

Tudo nesta seção está sustentado pela mensagem do commit `378d764352661eb81ee3c0e6a5d0a52ec4e26332`
(AuthorDate e CommitDate `2026-08-29T02:20:40-03:00`, autor Alexandre Sandra,
árvore `d6ffc4608d2c234874d1502bccb384e181123357`, pai `72f4151a78bd26c2eb46fce35c58b611b9fa2dda`).
Recuperável por `git show --format=fuller --no-patch 378d764`.

## A.1 — A taxonomia e a regra de preservação

**Linhas 14–15 da mensagem, verbatim:**

```
12 arquivos sao GIT_NATIVE_BY_DESIGN: existem so no git, nao sao ausencias,
  nunca podem ser removidos por sincronizacao baseada na origem.
```

Três afirmações, todas literais:

| # | o que o commit declara |
|---|---|
| 1 | o termo é **`GIT_NATIVE_BY_DESIGN`** |
| 2 | esses arquivos **existem só no git** e **não são ausências** — a inexistência deles no Drive não é lacuna de espelhamento, é a forma correta do artefato |
| 3 | **nunca podem ser removidos por sincronização baseada na origem** |

**O conjunto governado naquele momento: 12 arquivos.**

### A regra 3, dita como ela é

A formulação histórica é **semântica, não sintática**: ela proíbe *a remoção por
sincronização baseada na origem*, sem nomear ferramenta, comando ou flag. Quem for
implementar um empacotador deve implementar **essa proibição**, e não procurar por uma
flag específica.

## A.2 — Direção da sincronização (D2)

**Linha 3, verbatim:**

```
Espelho unidirecional Drive -> Git de 293 artefatos + 1 ZIP canonico externo.
```

**Linha 4, verbatim:**

```
Escopo: 312 artefatos-fonte. cts/ fora (ja versionado na raiz).
```

A direção declarada é **unidirecional, Drive → Git**. É essa unidirecionalidade que torna
a regra A.1 necessária: um espelho que espelha *da origem* trata "não está na origem" como
sinal, e sem a regra o sinal viraria remoção.

> Esta materialização **registra** os números declarados (`293`, `1`, `312`); **não os
> valida nem os reconcilia**. Validar contagens do espelhamento é ato separado e não
> pertence a esta rodada.

## A.3 — Regra de preservação do acervo

**Linhas 6–10, verbatim:**

```
Regra deste acervo: espelhar bytes, NAO corrigir. Os defeitos historicos N3
(v0.2.0 com 4 arquivos sobrescritos), N4 (artifact_id repetido em 3 manifests),
N5 (auto-hash divergente no manifesto do P002) e N7 (opus-5/max_tokens=2000
dentro do pacote s3-v0.1.1) sao PRESERVADOS COMO ESTAO. Corrigi-los e decisao
separada, futura e por aditivo.
```

Espelhar bytes, não corrigir. Os defeitos nomeados — **N3, N4, N5, N7** — ficam
preservados como estão, e sua correção é decisão separada, futura, e **por aditivo**.

## A.4 — O artefato divergente, e o estado em que foi deixado

**Linhas 12–13, verbatim:**

```
docs/PILOT-003-ACCOUNT-AUDIT.md: DIVERGENT_CONTENT - DECISION_REQUIRED.
  drive 08f9acfc...  git 3dba046d...  Nenhum lado alterado.
```

O commit declara os dois hashes e o estado `DECISION_REQUIRED`, e registra explicitamente
que **nenhum lado foi alterado**.

## A.5 — Diretório vazio

**Linha 16, verbatim:**

```
Diretorio vazio PRE_RUN_LOCK registrado so em MIRROR-DIRS (git nao versiona vazio).
```

## A.6 — Artefatos de infraestrutura, com hash, no próprio commit

**Linhas 18–22, verbatim:**

```
manifest  7bdba931244d59720ab9c038513a8abae631a0a8160549b0e904d2f6575544d0
dirs      87f3dfdaa3f3c74b5711be1bebfc227b8472636e449ef976a68acdcacd674c72
excluded  2b69c301f7cfe5b7e6d3df4e4250ef43dae62391c2fdcc076d6d11bb2658e5fb
step1     3dd4642eec1e7841733d7b0f299e4c4ba09cbc157a21ec3bc22f07b350e34d0c
gitattr   c284dbc46b85610c90ed5926b9bad4f649ece7b58f525c93aaebe60d9c9f9314
```

## A.7 — O que o commit **NÃO** declara

Registrado explicitamente para impedir atribuição futura:

| não está no commit | verificação |
|---|---|
| o literal **`--delete`** | 0 ocorrências na mensagem |
| a palavra **`rsync`** | 0 ocorrências |
| **`14`** como tamanho do conjunto | 0 ocorrências de "14 arquivos" ou "os 14" |
| a **enumeração** dos 12 arquivos | o commit declara o número, não a lista |

> **É proibido escrever que "o commit `378d764` proibiu `--delete`".** Ele não usou esse
> literal. A proibição existe na forma semântica citada em A.1, e é assim que deve ser
> citada. Paráfrase posterior não vira conteúdo histórico literal.

---

# B. `SUBSEQUENT_EVOLUTION`

**Tudo nesta seção é POSTERIOR ao commit `378d764` e não deve ser retroagido a ele.**

## B.1 — Derivação posterior do conjunto dos 12

O commit declara o **número**, não a lista. A lista abaixo é **derivada agora**, em
2026-08-30, por um critério mecânico aplicado à árvore do próprio commit:

> arquivos sob `_mirror/` presentes em `378d764`, **menos** os que constam do
> `MIRROR-MANIFEST-N6-20260829.tsv` (o inventário do lado Drive), **menos** os 5
> artefatos de infraestrutura cujos hashes o próprio commit lista (A.6), **menos** o
> 1 ZIP canônico externo que o commit contabiliza à parte (A.2).

O critério devolve **exatamente 12**, o que **corrobora** o número declarado. Corroboração
não é atribuição: a lista é desta materialização, o número é do commit.

```
_mirror/docs/PILOT-002-CLOSURE.md
_mirror/docs/PILOT-003-CLOSURE.md
_mirror/docs/RULE-SEARCH-BY-RADICAL-NOT-LITERAL-FORM.md
_mirror/pilots/PILOT-002-v2/blind/p002-blind-run.json
_mirror/pilots/PILOT-002-v2/blind/p002-fn-run.json
_mirror/pilots/PILOT-002-v2/blind/p002-fn-sample.json
_mirror/pilots/PILOT-002-v2/blind/p002-judge.json
_mirror/pilots/PILOT-002-v2/blind/p002-unprimed-run.json
_mirror/pilots/PILOT-003-v2/apply/p003-apply4.json
_mirror/pilots/PILOT-003-v2/apply/p003-apply4.md
_mirror/pilots/PILOT-003-v2/apply/p003-medicao-tokens.json
_mirror/pilots/PILOT-003-v2/apply/p003-recortes.json
```

Todos nasceram de trabalho feito no repositório — encerramentos, execuções cegas,
artefatos de aplicação. Nenhum jamais existiu no Drive.

## B.2 — A evolução 12 → 14

**Commit:** `a049354d67d0374490138979c0a520a4abe2d495`, `2026-08-29T21:48:51-03:00`,
*"Decisao de acervo: canonicidade de PILOT-003-ACCOUNT-AUDIT.md (aditivo)"*.

Adicionou **exatamente 2** arquivos, ambos git-native pelo mesmo critério de B.1:

```
_mirror/docs/ADR-ACERVO-001-CANONICIDADE-PILOT-003-ACCOUNT-AUDIT.md
_mirror/docs/ERRATA-MIRROR-MANIFEST-N6-20260829-AUDIT-PILOT-003.md
```

Esse mesmo commit **encerrou** o `DECISION_REQUIRED` registrado em A.4, promovendo
`3dba046d…` a `CANONICAL_ARTIFACT` e `08f9acfc…` a `PREVIOUS_STATE_SUPERSEDED`.

**12 → 14.** Este é o fato que a v1.2 registra na errata **A14** e que **não pode** ser
lido como conteúdo de `378d764`.

## B.3 — Estado além dos 14

O conjunto continuou crescendo depois de `a049354`. Aplicando o critério de B.1 a cada
estado da cadeia:

| estado | conjunto |
|---|---|
| `378d764` | 12 |
| `2f77d61` | 12 |
| `a049354` | **14** |
| `f52d81d` (HEAD ao materializar) | **30** |

O salto de 14 para 30 vem dos commits `4aada61` (preservação do `PRE_FREEZE_AUDIT_FAIL` e
da evidência de `REPRODUCED_FROM`), `985e386` (`PROPOSAL v1.2`) e `f52d81d`
(`PROPOSAL_V0_NOT_ARCHIVED`). **O número 14 é o estado em `a049354`, não o estado atual.**

A regra de A.1 governa a **classe**, não uma lista congelada: todo artefato que nasce no
git e não tem contraparte no Drive por desenho entra na classe e fica protegido.

---

# C. DECLARATION SPACE — a lição, e o que esta materialização NÃO resolve

> ### `filesystem scan ≠ corpus audit`

A declaração de A.1 existiu por um dia inteiro **acessível apenas por mensagem de commit**.
Uma auditoria que varresse só arquivos não a encontraria — e foi exatamente isso que
aconteceu: a auditoria pré-freeze de 30/08 afirmou, na sua §6, que a única declaração de
hash para o audit divergente era a linha 156 do manifesto, porque varreu arquivos e não
mensagens. O `ADR-ACERVO-001` já registrou essa correção.

**Três consequências, explícitas:**

1. **Mensagens de commit continuam sendo declaration space legítimo.** Elas são
   versionadas, imutáveis e endereçadas por hash. Não são um lugar errado para declarar.
2. **Esta materialização NÃO elimina a obrigação de auditar mensagens de commit.**
   Qualquer auditoria futura deste acervo continua obrigada a incluir
   `git log --all --format='%H%n%B'` no seu espaço de busca.
3. **O objetivo aqui é estreito:** impedir que *esta* declaração específica permaneça
   acessível **exclusivamente** por esse canal, porque ela governa a sobrevivência de
   arquivos e será consumida por código que varre o sistema de arquivos.

**`materialized in file` não significa `commit messages no longer need auditing`.**

---

# D. PROVENIÊNCIA

## Seção A — histórico

Fonte única: a mensagem do commit `378d764352661eb81ee3c0e6a5d0a52ec4e26332`.

| afirmação | linha na mensagem |
|---|---|
| taxonomia `GIT_NATIVE_BY_DESIGN`, conjunto de 12, "existem só no git, não são ausências" | 14 |
| "nunca podem ser removidos por sincronizacao baseada na origem" | 15 |
| "Espelho unidirecional Drive -> Git de 293 artefatos + 1 ZIP canonico externo" | 3 |
| "Escopo: 312 artefatos-fonte. cts/ fora" | 4 |
| "espelhar bytes, NAO corrigir"; N3, N4, N5, N7 preservados | 6–10 |
| `DIVERGENT_CONTENT - DECISION_REQUIRED`, os dois hashes, "Nenhum lado alterado" | 12–13 |
| diretório vazio `PRE_RUN_LOCK` | 16 |
| hashes de manifest · dirs · excluded · step1 · gitattr | 18–22 |

## Seção B — evolução posterior

| afirmação | fonte |
|---|---|
| lista derivada dos 12 | derivação de 2026-08-30 sobre a árvore de `378d764` (critério em B.1) — **não é conteúdo do commit** |
| 12 → 14, com os dois arquivos | commit `a049354d67d0374490138979c0a520a4abe2d495` |
| encerramento do `DECISION_REQUIRED` | `_mirror/docs/ADR-ACERVO-001-CANONICIDADE-PILOT-003-ACCOUNT-AUDIT.md` |
| errata `A14` (cronologia e `--delete`) | `_mirror/docs/architecture/COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-PROPOSAL-v1.2.md` §4 |
| conjunto = 30 em `f52d81d` | derivação de 2026-08-30 sobre a árvore de `f52d81d` |

**As duas proveniências não se misturam.** Nenhuma afirmação da seção A depende de
artefato posterior; nenhuma afirmação da seção B é atribuída ao commit `378d764`.

---

# E. ESCOPO

Esta materialização **não** executa `ARCHITECTURE FREEZE`, não inicia `MS-000A`, não
implementa multi-source, Source Packager, Fusion Engine, Operationalization, router ou
Skill Pack, não altera o Compiler nem os pilotos, não resolve `N1–N9`, não altera
`v1`/`v1.1`/`v1.2` nem o registro `PROPOSAL_V0_NOT_ARCHIVED`, e **não reescreve nenhum
commit**.
