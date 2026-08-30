# `PROPOSAL_V0_NOT_ARCHIVED` — registro de limitação documental (A18)

**Data:** 2026-08-30 · **Classe do artefato:** `GIT_NATIVE_BY_DESIGN`
**Status:** `PROPOSAL_V0_NOT_ARCHIVED`
**Classificação:** **`DOCUMENTARY_PRESERVATION_LIMITATION`**

Este registro fecha o item **A18** da auditoria pré-freeze **como limitação declarada**,
sem reconstruir o predecessor.

---

## 1. O FATO

A `DESIGN REVIEW v0` declara, na sua linha 3, o objeto que revisa:

> **Objeto:** `COURSE-TO-SKILL MULTI-SOURCE — ARCHITECTURE PROPOSAL v0`

**O texto exato desse predecessor não foi localizado no corpus arquivado verificável.**
Nem no repositório, nem no Drive, nem em mensagem de commit.

### O que a ausência NÃO significa

**Não significa que o `ARCHITECTURE PROPOSAL v0` nunca existiu.** A `DESIGN REVIEW v0`
engaja com ele de forma substantiva e detalhada — cita princípios dele por letra e
número, aponta o que ele não viu, e declara preservar seu núcleo:

| linha | o que a DESIGN REVIEW v0 diz sobre a proposta |
|---|---|
| 15 | "Estes princípios **da proposta** sobrevivem à confrontação e devem ser preservados na revisão." |
| 32 | "**A6** — Módulos definidos por CAPACIDADE, não por fonte; lista não congelada **na v0**." |
| 63 | "**C4** — Carregamento seletivo contradiz o contrato de runtime vigente. **A proposta não viu.**" |
| 298 | "**Alterações mínimas sobre a v0. O núcleo é preservado.**" |

Uma revisão não confronta ponto a ponto um documento que não existe. **Ele existiu e
tinha conteúdo real.** O que falta é a sua **representação exata arquivada** — os bytes.

### Como ele existiu

Como **input externo / conversacional** da `DESIGN REVIEW v0`: transmitido no fluxo de
trabalho, consumido pela revisão, e nunca gravado como arquivo no repositório nem no
Drive. É a mesma classe de falha de preservação que produziu o `61,50%` — valor de saída
de sessão tratado como artefato, sem arquivo para conferir.

> **Precisão de localizador, registrada em vez de silenciada.** A instrução desta rodada
> atribuía à `DESIGN REVIEW v0` uma "NOTA DE MÉTODO" dizendo que a revisão foi feita
> "sobre a descrição da proposta transmitida por Alexandre, não sobre leitura direta do
> documento". **Essa frase não existe na `DESIGN REVIEW v0`** — busca por cinco formas
> distintas devolveu zero ocorrências. O método que ela declara, verbatim na linha 9, é
> outro:
>
> > `Método: cada achado é confrontado contra estado **medido** do projeto. Onde não há`
> > `medição, o achado é declarado como hipótese e rotulado.`
>
> A nota de método que a instrução descreve **existe**, mas na **`PROPOSAL v1.1`, §11,
> linha 265**, e diz algo adjacente, não idêntico:
>
> > `(nota de método mantida desde a v0: tudo foi escrito sobre a descrição transmitida,`
> > `sem leitura ao vivo do repo/Drive)`
>
> Essa nota fala de **repo e Drive não lidos ao vivo** — não do Proposal v0 ter sido
> descrição em vez de documento. É a mesma disciplina aplicada na errata **A14** da
> v1.2: **paráfrase posterior não vira conteúdo histórico literal.** O fato 4 fica
> registrado com o localizador que se verifica, e com a diferença dita.

---

## 2. AS DUAS CADEIAS

### Cadeia documental arquivável — começa na revisão

```
DESIGN REVIEW v0  →  ARCHITECTURE PROPOSAL v1  →  v1.1  →  v1.2
```

| elo | localização | sha256 |
|---|---|---|
| `DESIGN REVIEW v0` | Drive `…/Course-to-Skill-Claude/docs/` | `ae4d4efd9b916f8bf3f0333dc6d8f2dc02dfd8f830537235a04de15726b975b6` |
| `ARCHITECTURE PROPOSAL v1` | Drive, idem | `913753700e72758d22add234509c507cde8de004c8464ceaa718ebea13fdaab5` |
| `ARCHITECTURE PROPOSAL v1.1` | Drive, idem | `f2f9f4b755e0ed66703a4e3d9d436b5ccc01b8f5d6c8b5377cfa6f7786aa8b33` |
| `ARCHITECTURE PROPOSAL v1.2` | repo `_mirror/docs/architecture/` | `54e1eee3100bee0072b8df82173404a624dca37b7000fd31e63be09918f08e92` |

### Relação histórica conceitual — permanece, e é anterior à cadeia arquivável

```
UNARCHIVED EXTERNAL PROPOSAL v0  →  DESIGN REVIEW v0
```

A seta é real. O nó de origem **não é arquivável** e é assim que ele deve ser citado.
Escrever a cadeia começando na `DESIGN REVIEW v0` sem esta linha apagaria a existência
do predecessor; escrevê-la como se o v0 estivesse arquivado seria falso. As duas
representações coexistem por desenho.

---

## 3. PROIBIÇÃO DE RECONSTRUÇÃO

> **É proibido reconstruir conteúdo, bytes ou hash do `ARCHITECTURE PROPOSAL v0`** — por
> inferência, por memória, ou a partir da própria `DESIGN REVIEW v0`.

A `DESIGN REVIEW v0` cita o predecessor de forma seletiva e **adversarial**: ela cita o
que aceita e o que rejeita, não o que o documento dizia por inteiro. Reconstruí-lo dali
produziria um texto que **parece** o v0 sem **ser** o v0 — e, uma vez com hash, seria
indistinguível de um original para qualquer verificação posterior. Isso é pior que a
ausência: transformaria uma lacuna honesta em um artefato falso.

Vale para qualquer reconstrução, ainda que declarada como aproximação.

---

## 4. INCORPORAÇÃO FUTURA, SE APARECER

Se uma **cópia exata** aparecer, ela pode ser incorporada **aditivamente**, como
`ARCHIVAL_COPY`, sob três condições:

1. proveniência da descoberta registrada — onde foi encontrada, como, quando, por quem;
2. sha256 e bytes da cópia publicados no ato;
3. **este registro não é reescrito.** Ele passa a conviver com a cópia, documentando o
   período em que o v0 esteve não arquivado e como isso foi tratado.

Nenhuma cópia é aceita sem as três.

---

## 5. O QUE ESTA CLASSIFICAÇÃO É, E O QUE NÃO É

`PROPOSAL_V0_NOT_ARCHIVED` é uma **`DOCUMENTARY_PRESERVATION_LIMITATION`**.

**Não é:**

| não é | por quê |
|---|---|
| divergência arquitetural | nenhum `D`, `I` ou `E` depende do texto do v0 |
| invalidação da `DESIGN REVIEW v0` | a revisão permanece **íntegra e válida**; seus achados foram confrontados contra estado medido do projeto, não contra o texto do v0 |
| razão para modificar `v1`, `v1.1` ou `v1.2` | nenhuma das três é alterada por este registro |
| razão para reconstruir o predecessor | ver §3 |

**A `DESIGN REVIEW v0` histórica permanece intacta.** Este registro é aditivo sobre ela,
não uma correção dela.

---

## 6. PROVENIÊNCIA

| âncora | onde | o que estabelece |
|---|---|---|
| `DESIGN REVIEW v0`, linha 3 | Drive, sha256 `ae4d4efd9b916f8bf3f0333dc6d8f2dc02dfd8f830537235a04de15726b975b6` | identifica o `PROPOSAL v0` como objeto da revisão |
| `DESIGN REVIEW v0`, linhas 15 · 32 · 63 · 298 | idem | engajamento substantivo — evidência de que o v0 existiu com conteúdo |
| `DESIGN REVIEW v0`, linha 9 | idem | o método que ela **de fato** declara |
| `PROPOSAL v1.1`, §11 linha 265 | Drive, sha256 `f2f9f4b755e0ed66703a4e3d9d436b5ccc01b8f5d6c8b5377cfa6f7786aa8b33` | a nota de método sobre "descrição transmitida, sem leitura ao vivo do repo/Drive" |
| `PRE_FREEZE_AUDIT_FAIL.md`, item **A18** | repo, sha256 `b9e607e2742facc27d255da8f13b5bb4029f3d783d656787ab15a8b516126677` | classificou A18 como **`NOT_LOCATED` (não bloqueante)** |

### A busca executada nesta rodada

Espaço: arquivos do repo (`git ls-files`), árvore `Chat GPT` inteira do Drive em leitura,
e **mensagens de commit** (`git log --all --format='%H%n%B'`). Busca por **radical**.

**Por nome de arquivo** — nenhum candidato. Os únicos arquivos com radical `PROPOSAL` ou
`MULTI-SOURCE` são a própria cadeia (`DESIGN-REVIEW-v0`, `PROPOSAL-v1`, `v1.1`,
`v1-SHA913753`, `v1.2`) e o `CLAUDE_ARCHITECTURE_PROPOSAL.md` de 2026-08-10, que é a
proposta da **Fase 3** — documento diferente, com **zero** ocorrências de "multi-source".

**Por conteúdo** — todas as ocorrências de `ARCHITECTURE PROPOSAL v0` estão em documentos
que **se referem** a ele: a própria `DESIGN REVIEW v0`, as duas transcrições da `v1`, e o
`PRE_FREEZE_AUDIT_FAIL.md`. **Nenhuma é o documento.**

**Controle positivo** — `DESIGN REVIEW v0` e `ARCHITECTURE PROPOSAL v1` retornaram
ocorrências ≠ 0 em ambas as árvores. O instrumento acha o que existe; **não achou o v0
porque o v0 não está lá.**

---

## 7. ESCOPO DESTE REGISTRO

Não repete a auditoria `A1–A18`, não materializa a taxonomia do `378d764`, não executa
`ARCHITECTURE FREEZE`, não inicia `PILOT-MS-000A`, não implementa nada de multi-source, e
não altera `v1`, `v1.1`, `v1.2` nem qualquer arquivo preexistente.

**A18 fica fechado como limitação documental declarada e permanente.**
