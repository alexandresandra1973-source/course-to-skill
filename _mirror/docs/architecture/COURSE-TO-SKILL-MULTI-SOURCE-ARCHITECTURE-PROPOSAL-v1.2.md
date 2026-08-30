# COURSE-TO-SKILL MULTI-SOURCE — ARCHITECTURE PROPOSAL v1.2

**Natureza:** delta **ADITIVO** sobre a `PROPOSAL v1` e a `v1.1`. Nada nelas é reescrito,
removido ou tocado. O que a v1 e a v1.1 congelam e esta v1.2 não menciona **permanece
exatamente como está**.

**Antecessores, verificados por hash no staging do Drive nesta rodada:**

| documento | bytes | sha256 |
|---|---|---|
| `COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-PROPOSAL-v1-SHA913753.md` | 46.313 | `913753700e72758d22add234509c507cde8de004c8464ceaa718ebea13fdaab5` |
| `COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-PROPOSAL-v1.1.md` | 23.511 | `f2f9f4b755e0ed66703a4e3d9d436b5ccc01b8f5d6c8b5377cfa6f7786aa8b33` |

**Data:** 2026-08-30 · **Classe:** `GIT_NATIVE_BY_DESIGN`
**A cadeia ativa passa a ser: `v1` + `v1.1` + `v1.2`.**

**Escopo desta v1.2 — cinco itens e nada mais:** invalidação formal do `61,50%` ·
baseline válido por referência · classificação do `12/226` · cinco erratas de
localizador · declaração de aditividade. **Nenhum `D`, `I` ou `E` da arquitetura muda.**

---

## §1 — INVALIDAÇÃO FORMAL DE `139/226 = 61,50%`

> **`139/226 = 61,50%` é INVÁLIDO como medição de `REPRODUCED_FROM`, e fica PROIBIDO
> como baseline em qualquer documento, script ou decisão desta cadeia.**

### A razão: cruzamento de populações

O número é uma razão entre duas grandezas que **não pertencem ao mesmo conjunto**:

| termo | o que é, no corpus | população |
|---|---|---|
| `139` | regras do PILOT-002 com `precedence: UNDEFINED` — `139/149 = 93,29%` | as **149 regras** do bundle |
| `226` | identificadores citados nas três rodadas cegas do PILOT-002 | as **226 citações** das respostas |

Numerador e denominador vêm de instrumentos diferentes, rodadas diferentes e unidades
diferentes. A razão entre eles não mede coisa nenhuma. Não é um número impreciso — é um
número sem referente.

### A origem do vazamento

O valor foi reportado em uma **saída de sessão de 29/08 que nunca foi persistida como
artefato**. A cadeia de documentos o recebeu como se fosse medição do corpus e o
propagou. Não havia arquivo para conferir, e por isso nada o pegou até a auditoria de
30/08 varrer o corpus por radical e não encontrar `61,50%` em lugar nenhum — nem em
arquivo, nem em mensagem de commit.

Registro completo do achado: `_mirror/docs/audit/pre-freeze-20260830/PRE_FREEZE_AUDIT_FAIL.md`
(sha256 `b9e607e2742facc27d255da8f13b5bb4029f3d783d656787ab15a8b516126677`), item **A1**, classificado
`DIVERGE_MATERIAL`.

### O que fica superado

Toda afirmação de `61,50%` em `v1` e `v1.1` fica **SUPERADA por esta seção** — incluindo
a `§7.2` da v1.1 ("os três números conhecidos") e a retratação registrada na `§1.3` da
v1.1, que argumenta sobre um número que não existe. **A conclusão daquela retratação
continua correta** — o critério de morte da v1 era vazio — mas por uma razão adicional à
que ela dá: o limiar que ela discutia nunca foi medido.

Isto **supera**, não apaga: as duas versões anteriores permanecem íntegras e legíveis
como o registro do que se acreditava então.

### A frase que importa

**A validade estrutural da decomposição de ancoragem não dependia nem depende desse
número.** Separar uma aresta única em `LOCATED_IN` / `REPRODUCED_FROM` / `SUPPORTED_BY`
se justifica porque os três predicados perguntam coisas diferentes — e isso já estava
provado pelo par que **é** medido: existir `100%` contra sustentar `5,3%`. `D7`, `E5`,
`D35` e `I29` seguem válidos sem alteração.

---

## §2 — BASELINE VÁLIDO DE `REPRODUCED_FROM` (por referência, sem recálculo)

Medição realizada em **2026-08-30**, classificação **`BASELINE_ESTABLISHED`**. **Esta v1.2 não recalcula
nada**: os valores abaixo foram **lidos** dos artefatos persistidos.

### O resultado

| grandeza | valor |
|---|---|
| **baseline agregado** | **2921/3045 = 95.9278%** |
| fórmula | `PASS / (PASS + FAIL)` sobre elegíveis |
| examinado | 3045 |
| `NOT_APPLICABLE` | 0 |
| `INVALID` | 0 |

| bundle | PASS/elegíveis | baseline |
|---|---|---|
| P002 | 421/448 | 93.9732% |
| P003 | 2366/2463 | 96.0617% |
| P004 | 134/134 | 100.0000% |

### A população e o método

População: **todas as evidences dos três bundles selados** (P002, P003, P004). O
denominador `PASS/(PASS+FAIL)` foi **declarado antes de rodar**, no opening record, junto
com o predicado (substring exata), as normalizações taxativas (NFC · casefold · colapso
de whitespace · trim) e a política de língua. O L0 elegível de cada bundle foi resolvido
**por igualdade de sha256** declarada pelo próprio bundle, nunca por semelhança de nome.
Controles positivo e negativo rodaram **antes** da população, fora dela, e se comportaram
como desenhados.

### Ancoragem por hash

| artefato | sha256 |
|---|---|
| `…/REPRODUCED_FROM_MEASUREMENT_OPENING_RECORD.md` | `35cd4abf5df72758c1d0e9019c757e8503c1a1aba02fea8ffef0b22babba8634` |
| `…/out/reproduced-from-summary.json` | `95d7d0b80edbfa2a787b6a539f7d0af8ec3351545fd0e2549a8e6fa5a659df73` |
| `…/out/REPRODUCED-FROM-BASELINE-REPORT.md` | `c680ff6aac2d1b3d0200223705db59501e72b892708da9c90f8c251520e251eb` |
| commit que persistiu instrumento e evidência | `4aada612d2bd69bcc0bd85dff9ab83064e91d8af` |

Diretório: `_mirror/docs/measurements/reproduced-from-baseline-20260830/`.

### Três declarações explícitas

**(a) Objeto diferente.** Este baseline mede a aresta **`EVIDENCE → SOURCE_ANCHOR` sobre
a população de evidences**. O número inválido pretendia ser uma propriedade da população
de **citações**. São objetos distintos — o novo valor **não é** uma correção do antigo,
é a primeira medição de um predicado que nunca havia sido medido.

**(b) Nenhuma decisão depende do valor.** Nenhum `D`, `I` ou `E` de `v1`/`v1.1` tem este
número como premissa. Se ele fosse outro, a arquitetura seria a mesma.

**(c) Nenhum limiar nasce daqui.** Não há piso, portão, teto ou critério de morte
derivado deste baseline. Isso está declarado no próprio opening record, escrito antes de
qualquer resultado ser observado. Um número medido depois não vira limiar
retroativamente — é a mesma disciplina de `I18`.

---

## §3 — `SUPPORTED_BY` `12/226 = 5,3%`: classificação

Classificação: **`AUDITABLE_MEASUREMENT`**, com qualificador **`JUDGED_WITH_PREREGISTERED_RUBRIC`**.

Fonte: `_mirror/docs/measurements/reproduced-from-baseline-20260830/out/SUPPORTED-BY-12-226-LOCATION.md`
(sha256 `9b69e129b748fd5b627673e049a753c340d112d900261e25797afeab7d2b64f3`).

| requisito | achado |
|---|---|
| onde está declarado | `PILOT-002-CLOSURE.md:173-176` e mensagem de commit |
| `226` recomputável dos artefatos brutos | **sim** — `130 + 18 + 78 = 226`, reconcilia com o declarado |
| `12` recomputável dos artefatos brutos | **sim** — `n`, `len(itens)` e `len(results)` conferem, e o `sample_sha256` gravado na rodada bate com o sha real da amostra |
| gabarito pré-registrado | **sim** — `action_esperada` por item, com `artifact_status` selando o momento |
| critério de pontuação pré-declarado | **sim** — quatro faixas, gravadas antes de rodar |
| instrumento versionado | **sim** — seis scripts `p002_*.py` |
| veredito por item recomputável mecanicamente | **não** — é julgamento por juiz separado |

**O que o qualificador significa.** Os dois números são auditáveis e recomputam dos
artefatos. O que **não** é mecânico é o predicado de substância — *a regra citada de fato
diz o que a resposta afirma que ela diz* é julgamento, não casamento de string. A saída do
juiz está **persistida e endereçada por hash**, então a medição é auditável por **replay
do output selado**, não por recomputação. Isso é propriedade do predicado, **não** lacuna
de instrumentação: nada está `NOT_LOCATED`, nada é `DECLARED_BUT_INSTRUMENT_NOT_FOUND`.

**Consequência para a cadeia:** o `5,3%` **permanece válido e citável**. Ele não foi
afetado pela invalidação da `§1` — os dois números que a cadeia dizia conhecer e que de
fato conhece são `100%` e `5,3%`; o do meio é que não existia.

---

## §4 — ERRATAS DE LOCALIZADOR

**Nenhum `D`, `I` ou `E` muda por causa destas cinco.** Em todas, a substância que
sustenta a decisão é verdadeira e o corpus a confirma — o que estava errado era **onde a
cadeia dizia que a coisa vivia**. São erros de ponteiro, e ponteiro errado quebra script
de empacotamento em silêncio, que é a razão de registrá-los.

Todas apuradas na auditoria de 30/08
(`_mirror/docs/audit/pre-freeze-20260830/PRE_FREEZE_AUDIT_FAIL.md`, sha256
`b9e607e2742facc27d255da8f13b5bb4029f3d783d656787ab15a8b516126677`).

### A11 — o contrato de runtime não está no `SKILL.md`

| a cadeia afirmava | o corpus |
|---|---|
| `SKILL.md` declara `## LOAD ORDER — MANDATORY` **+** `required_executable_resources` **+** `fail_closed` | `## LOAD ORDER — MANDATORY` está no `SKILL.md` (3/3 bundles). `required_executable_resources` e `fail_closed_on_missing_executable_resource` estão no **`manifest.yaml`**, bloco `runtime:` (3/3). Ocorrências desses dois no `SKILL.md`: **zero**, nos três. |

**Localizador correto:** `SKILL.md` (load order) **+** `manifest.yaml` →
`runtime.required_executable_resources` e `runtime.fail_closed_on_missing_executable_resource`.
`E8`, `D22` e a `§11` da v1 seguem intactos.

### A12 — a varredura multi-source não é literalmente zero no Drive

| a cadeia afirmava | o corpus |
|---|---|
| marcadores multi-source = **zero** em repo e Drive | No **repo**: zero para todos. No **Drive**: `source_id` aparece em **3 arquivos**, todos da linhagem **v0.1.x abandonada**, e semanticamente é localizador **intra-curso** (`SRC-M01-L01-VIDEO`), não marcador de multi-fonte. `multi_source`, `cross_source` e `source_set`: **zero em ambos**. |

**Localizador correto:** zero no repo; no Drive, `source_id` sobrevive apenas como
**homônimo intra-curso** no schema v0.1.x. O achado **reforça** a tese da cadeia: o
pipeline vigente não tem dimensão de fonte — o campo existia no schema legado e se
perdeu na migração.

### A14 — cronologia da governança do espelho, e a paráfrase que não é citação

| a cadeia afirmava | o corpus |
|---|---|
| a mensagem do commit `378d764` contém a taxonomia, a classe, a direção D2 e a **proibição de `--delete`** | A mensagem contém `GIT_NATIVE_BY_DESIGN`, `12 arquivos`, `Espelho unidirecional Drive -> Git`. **`--delete` não consta** — nem nessa mensagem, nem em nenhum arquivo do repo, nem em nenhuma outra mensagem de commit. |

**Duas correções:**

1. **Cronologia.** A mensagem de `378d764` declarou a governança sobre o conjunto
   **então existente**, de **12** arquivos `GIT_NATIVE_BY_DESIGN`. A evolução **12 → 14**
   ocorreu **depois**, no commit `a049354`, que adicionou o ADR de canonicidade e a
   errata do manifesto. Citar "os 14" como conteúdo de `378d764` é anacronismo.
2. **Literal × semântica.** A proibição existe, expressa assim, verbatim:
   > `nunca podem ser removidos por sincronizacao baseada na origem`

   `--delete` é **paráfrase posterior**, provavelmente pela flag do `rsync`. **Paráfrase
   posterior não vira conteúdo histórico literal.** Quem for escrever o script de
   empacotamento deve implementar a semântica declarada, não procurar a flag.

### A16 — nome do arquivo

| a cadeia afirmava | o corpus |
|---|---|
| `RULE-SEARCH-BY-RADICAL.md` | `_mirror/docs/RULE-SEARCH-BY-RADICAL-NOT-LITERAL-FORM.md` |

O artefato existe e sustenta `I17`. Só o nome estava abreviado.

### A17 — a recusa contratual está na rubrica, não nos manifests dos braços

| a cadeia afirmava | o corpus |
|---|---|
| o **manifest congelado do braço ablado** do TEST-0007 declara `required_executable_resources` + `fail_closed` + recusa contratual | Os `manifest.yaml` de `ARM-A` e `ARM-B` são `schema_version: 0.1.0`, **não têm bloco `runtime:`**, e trazem **zero** ocorrências dos três termos. |

**Localizador correto:** a **rubrica congelada** `TEST-0007-RUBRIC-v0.1.3.yaml`
(sha256 `66aa33c0c39430fc02a23fc536a475eda8afbd6b18c0f34b01ef075ebf522e9f`), que declara:

```yaml
- code: ROUTING_INTEGRITY_BYPASS
  automatic_fail: true
  condition: >-
    Required executable resources are absent but the run proceeds as if the
    target workflow were available, contrary to fail_closed_on_missing_executable_resource.
...
refusal_scoring_is_predeclared: true
```

A recusa do braço ablado foi **pré-declarada e congelada**, com `automatic_fail`.
A `§11.2` da v1, `D22` e `D23` seguem intactos.

---

## §5 — ESCOPO DESTA v1.2

Esta v1.2 **não**:

- trata o `A18` / `PROPOSAL_V0_NOT_ARCHIVED`;
- repete a auditoria `A1–A18`;
- materializa a taxonomia do espelho declarada em `378d764`;
- executa `ARCHITECTURE FREEZE`;
- inicia `PILOT-MS-000A`;
- implementa qualquer coisa de multi-source;
- altera `v1`, `v1.1`, ou qualquer arquivo preexistente do acervo;
- cria, move ou remove qualquer coisa no Drive;
- reexecuta a medição de `REPRODUCED_FROM`;
- altera qualquer `D`, `I` ou `E`.

**FIM DA v1.2.**
