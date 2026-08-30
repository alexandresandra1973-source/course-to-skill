# COURSE-TO-SKILL MULTI-SOURCE — ARCHITECTURE FREEZE

**Status:** `ARCHITECTURE_FROZEN`
**Data:** 2026-08-30
**Commit base (HEAD ao congelar):** `8d3bc019f150e1f54feaa09c73461513c87e4c40`
**Projeto:** Course-to-Skill Multi-Source / Skill Pack Modular
**Classe:** `GIT_NATIVE_BY_DESIGN`

**Este documento congela contratos e invariantes. Não implementa nada.** Nenhuma linha de
código de multi-source, Source Packager, Fusion Engine, Operationalization, router ou
Skill Pack existe neste commit. O Compiler, `cts/`, os runners, os pilotos, os freezes e
manifests históricos e os defeitos `N1–N9` estão intocados.

**Como ler:** este freeze **consolida**; não substitui a cadeia normativa. Onde ele
resume, a fonte é o membro citado. Ele é auto-contido o bastante para que uma
implementação futura saiba o que está congelado sem reler conversa nenhuma — e cada
afirmação resolve para um membro com hash.

---

## 0. PORTÕES CUMPRIDOS

| portão | resultado |
|---|---|
| PRE-FREEZE AUDIT inicial | `FREEZE_BLOCKED` — 1 `DIVERGE_MATERIAL` (A1) |
| invalidação do baseline `61,50%` | executada, formalizada na v1.2 §1 |
| medição real de `REPRODUCED_FROM` | `BASELINE_ESTABLISHED`, instrumento e evidência preservados |
| `ARCHITECTURE PROPOSAL v1.2` | commitada (`985e386`) |
| A18 | `A18_CLOSED_AS_DOCUMENTARY_LIMITATION` (`f52d81d`) |
| PRE-FREEZE RE-AUDIT | `PASS` — 18/18 sem divergência material |
| governança do `378d764` | materializada aditivamente (`8d3bc01`) |

---

## 1. MEMBROS DO FREEZE

Todos resolvem **dentro do repositório**. Os três primeiros membros normativos foram
ingeridos do Drive nesta rodada, byte-fiéis, precisamente para que o freeze não dependa de
arquivos fora do controle de versão.

| classe | caminho | bytes | sha256 |
|---|---|---|---|
| `normativo` | `_mirror/docs/architecture/COURSE-TO-SKILL-MULTI-SOURCE-DESIGN-REVIEW-v0.md` | 39700 | `ae4d4efd9b916f8bf3f0333dc6d8f2dc02dfd8f830537235a04de15726b975b6` |
| `normativo` | `_mirror/docs/architecture/COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-PROPOSAL-v1-SHA913753.md` | 46313 | `913753700e72758d22add234509c507cde8de004c8464ceaa718ebea13fdaab5` |
| `normativo` | `_mirror/docs/architecture/COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-PROPOSAL-v1.1.md` | 23511 | `f2f9f4b755e0ed66703a4e3d9d436b5ccc01b8f5d6c8b5377cfa6f7786aa8b33` |
| `normativo` | `_mirror/docs/architecture/COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-PROPOSAL-v1.2.md` | 13151 | `54e1eee3100bee0072b8df82173404a624dca37b7000fd31e63be09918f08e92` |
| `evidencia` | `_mirror/docs/audit/pre-freeze-20260830/PRE_FREEZE_AUDIT_FAIL.md` | 16770 | `b9e607e2742facc27d255da8f13b5bb4029f3d783d656787ab15a8b516126677` |
| `evidencia` | `_mirror/docs/measurements/reproduced-from-baseline-20260830/REPRODUCED_FROM_MEASUREMENT_OPENING_RECORD.md` | 9088 | `35cd4abf5df72758c1d0e9019c757e8503c1a1aba02fea8ffef0b22babba8634` |
| `evidencia` | `_mirror/docs/measurements/reproduced-from-baseline-20260830/measure_reproduced_from.py` | 17467 | `4843c331d0d88d91e70d92bd44d7ea208e9354c670bbc75f2054ed72b884010c` |
| `evidencia` | `_mirror/docs/measurements/reproduced-from-baseline-20260830/fixtures/fixture-cases.json` | 716 | `59d091289570c7c0e3b0c4035ebfefda616a01352cb7ba78327beae4757fef1c` |
| `evidencia` | `_mirror/docs/measurements/reproduced-from-baseline-20260830/out/reproduced-from-raw.jsonl` | 365339 | `7fce84bc543ce5d0257682092f0e5515433ac76b83cf8a603d2f3cfda57d1bd6` |
| `evidencia` | `_mirror/docs/measurements/reproduced-from-baseline-20260830/out/reproduced-from-summary.json` | 4682 | `95d7d0b80edbfa2a787b6a539f7d0af8ec3351545fd0e2549a8e6fa5a659df73` |
| `evidencia` | `_mirror/docs/measurements/reproduced-from-baseline-20260830/out/REPRODUCED-FROM-BASELINE-REPORT.md` | 2867 | `c680ff6aac2d1b3d0200223705db59501e72b892708da9c90f8c251520e251eb` |
| `evidencia` | `_mirror/docs/measurements/reproduced-from-baseline-20260830/out/SUPPORTED-BY-12-226-LOCATION.md` | 6310 | `9b69e129b748fd5b627673e049a753c340d112d900261e25797afeab7d2b64f3` |
| `governanca` | `_mirror/docs/architecture/PROPOSAL-V0-NOT-ARCHIVED.md` | 8556 | `8cdaf2a8255857e3976b0c993eaed8f66ac72ebffa45561ba26d99ed6cad050c` |
| `governanca` | `_mirror/docs/GIT-NATIVE-BY-DESIGN-GOVERNANCE-MATERIALIZED-FROM-378d764.md` | 12066 | `a87de14b1abff422995457e9c3d5e26826ec65048e010090af848c5ed406a823` |
| `governanca` | `_mirror/docs/ADR-ACERVO-001-CANONICIDADE-PILOT-003-ACCOUNT-AUDIT.md` | 8652 | `c5b63d02ce8d18e2fdd6601a5a20a8bfe17d3e06776aa509018ae1265561e1e8` |
| `governanca` | `_mirror/docs/ERRATA-MIRROR-MANIFEST-N6-20260829-AUDIT-PILOT-003.md` | 3888 | `0d45635a9a3ccfb1f8f64a1fe590e773c1f4fc62a9a274c9814773ac963a40bc` |

O selo enumerável vive em `ARCHITECTURE-FREEZE-RECORD.yaml`, ao lado deste documento.
**O hash do próprio selo é registrado fora do conjunto selado** — na mensagem do commit
que o cria — conforme a condição 2 de `SEALED` (§14).

### Cadeia normativa ativa

```
DESIGN REVIEW v0 → ARCHITECTURE PROPOSAL v1 → v1.1 → v1.2
```

**`UNARCHIVED EXTERNAL PROPOSAL v0 → DESIGN REVIEW v0`** permanece como relação histórica
reconhecida. O `PROPOSAL v0` **não é reconstruído** (§21).

---

## 2. E1–E12 — DECISÕES EXECUTIVAS

Forma final acumulada por v1 + v1.1. **Todas fechadas.**

| # | decisão | estado |
|---|---|---|
| **E1** | O Compiler atual permanece **estritamente source-local**: uma fonte por execução, sem consciência de outras fontes. Nunca é alterado por esta arquitetura | `CONGELADA` |
| **E2** | Fronteira de nós do pipeline (§3 abaixo) | `CONGELADA` |
| **E3** | **DESIGN C adotado** — o Source Package carrega *candidatos* source-local além de evidence e claims; candidatos **não são** as regras finais | `CONGELADA` (3 condições da v1 §18.4) |
| **E4** | `Claim` é unidade de **COMPARAÇÃO**. Nunca de proveniência. Nunca, sozinha, de decisão | `CONGELADA` |
| **E5** | Proveniência ancora em **`SOURCE_ANCHOR`**, locator abstrato com contrato de resolubilidade. `text_span` é subtipo, não o modelo | `CONGELADA` |
| **E6** | Identidade global por qualificação: `(source_package_hash, local_id)`. Nenhum artefato histórico é renumerado | `CONGELADA` |
| **E7** | Três grafos formalmente separados. Dependência de módulo **não é inferida do corpus** | `CONGELADA` |
| **E8** | Dois contratos de runtime coexistentes e mutuamente excludentes: `LEGACY_SINGLE_SOURCE` (congelado, comportamento medido) e `MODULAR_SKILL_PACK` | `CONGELADA` |
| **E9** | Independência entre fontes é **estado com evidência**, nunca booleano confiante. Default `UNKNOWN`, e `UNKNOWN` não é independência | `CONGELADA` |
| **E10** | Fusão é **incremental por construção**: a fonte *k+1* gera *k* conjuntos de pares novos, não `C(k+1,2)` | `CONGELADA` |
| **E11** | "Fusão estrutural é seleção ou escalada — nunca síntese" — **com escopo: FUSION LAYER**. Síntese é legal em outra camada, governada | `CONGELADA (com escopo)` — v1.1 §1.2 |
| **E12** | Estatuto do produto de fonte única: `LEGACY_SINGLE_SOURCE` **preservado**, `READY_FOR_CONTROLLED_USE — CONDICIONAL` segue valendo; pilotos **não** passam retroativamente pela fusão; `MODULAR_SKILL_PACK` é caminho **paralelo**, não substituto | `CONGELADA` — v1.1 §1.1 |

---

## 3. FRONTEIRA DO PIPELINE — CONGELADA

```
SOURCE
  → COMPILE ISOLATED
    → PACKAGE ASSEMBLY
      → VALIDATE / SEAL
        → SOURCE PACKAGE
          → FUSION
            → FUSION PACKAGE
              → OPERATIONALIZATION / MTX ASSEMBLY
                → OPERATIONAL PACKAGE
                  → SKILL PACK
```

O Compiler atual ocupa **somente** `SOURCE → … → SOURCE PACKAGE`, e não é transformado em
multi-source.

---

## 4. OS QUATRO PRODUTOS E SUAS AUTORIDADES — CONGELADO

| pacote | natureza | endereçamento | **autoritativo sobre** | **NÃO autoritativo sobre** |
|---|---|---|---|---|
| `SOURCE PACKAGE` | imutável, selado | hash do conjunto | **o que aquela fonte afirma** | outras fontes · adequação à MTX · regra operacional final multi-source |
| `FUSION PACKAGE` | derivado, recomputável | `fusion_id` por conjunto ordenado de hashes, **sem** `mtx_policy_hash` | **relações entre claims · conflitos · adjudicações · precedência registrada · seleção semântica** | conteúdo de fonte · o que a MTX decidiu operar |
| `OPERATIONAL PACKAGE` | gerado, **selado uma vez** | `operational_id = H(fusion_package_hash ∪ hash(MTX-POLICY) ∪ hash(APPLICABILITY_DECISIONS) ∪ hash(SYNTHESIS_TRACES))` | **o que a MTX decidiu operar** — applicability · adaptações · sínteses MTX · políticas operacionais · traces e aprovações | o que as fontes afirmam · relações do corpus |
| `SKILL PACK` | artefato de consumo | hash + `operational_package_hash` | **nada** — não é fonte de verdade autônoma | tudo |

**A Fusion é seletiva**, não uma camada livre de síntese operacional.
**Toda saída do Skill Pack resolve para trás**, até L0 ou até uma decisão MTX registrada.

---

## 5. PROVENIÊNCIA — CONGELADA

### Cadeia conceitual

```
SOURCE → ARTIFACT → SOURCE_ANCHOR → EVIDENCE → CLAIM
       → SOURCE_LOCAL_CANDIDATE → FUSION → OPERATIONAL ARTIFACT → MODULE → SKILL PACK
```

### Os dois saltos, medidos separadamente

```
CLAIM ──ENTAILED_BY──▶ {EVIDENCE} ──┬─ LOCATED_IN ──────▶ SOURCE_ANCHOR / L0
                                    ├─ REPRODUCED_FROM ──▶
                                    └─ SUPPORTED_BY ─────▶
```

| relação | o que afirma |
|---|---|
| `LOCATED_IN` | o span existe e resolve contra o artefato selado |
| `REPRODUCED_FROM` | a quote reaparece verbatim no L0 elegível |
| `SUPPORTED_BY` | a substância sustenta a asserção |
| `ENTAILED_BY` | **toda** asserção da claim segue da união das suas `evidence_refs`, **sem acréscimo** |

> **É proibido colapsar os predicados num campo só.** Cada salto tem régua própria e
> relatório próprio. `NOT_APPLICABLE` e `MISSING` são valores **distintos** em todo campo
> de ancoragem.

---

## 6. BASELINES DE ANCORAGEM — CONGELADOS

### 6.1 `REPRODUCED_FROM` — INVÁLIDO

> **`139/226 = 61,50%` é INVÁLIDO como baseline de `REPRODUCED_FROM` e não pode ser
> reutilizado em nenhum documento, script ou decisão.**

Motivo: mistura populações. `139` é a contagem de regras com `precedence: UNDEFINED` do
PILOT-002 (sobre 149 regras); `226` é a contagem de citações das três rodadas cegas. A
razão entre elas não tem referente.

### 6.2 `REPRODUCED_FROM` — VÁLIDO

Valores lidos dos artefatos persistidos, **não redigitados**.

| grandeza | valor |
|---|---|
| classificação | **`BASELINE_ESTABLISHED`** |
| **baseline agregado** | **2921/3045 = 95.9278%** |
| fórmula | `PASS / (PASS + FAIL)` sobre elegíveis |
| examinado | 3045 · `NOT_APPLICABLE` 0 · `INVALID` 0 |

| bundle | PASS/elegíveis | baseline |
|---|---|---|
| P002 | 421/448 | 93.9732% |
| P003 | 2366/2463 | 96.0617% |
| P004 | 134/134 | 100.0000% |

Artefatos: `REPRODUCED_FROM_MEASUREMENT_OPENING_RECORD.md` · `measure_reproduced_from.py`
· `fixtures/fixture-cases.json` · `out/reproduced-from-raw.jsonl` ·
`out/reproduced-from-summary.json` · `out/REPRODUCED-FROM-BASELINE-REPORT.md` — hashes na §1.

**Nenhum limiar de aprovação nasce deste baseline.** O opening record declarou isso antes
de qualquer resultado ser observado.

### 6.3 `SUPPORTED_BY`

`12/226 = 5,3%` classificado **`AUDITABLE_MEASUREMENT`**, qualificador **`JUDGED_WITH_PREREGISTERED_RUBRIC`**.
Os dois números recomputam dos artefatos brutos; o veredito de substância é **julgamento**
com rubrica pré-registrada e output persistido por hash, auditável por **replay**.

> **É proibido transformar esse julgamento em medição mecânica.**

---

## 7. SEMANTIC RELATIONS — MODELO CONGELADO, TAXONOMIA CANDIDATA

**O modelo em dois eixos é congelado. A lista final de `content` não é.**

```
representation : IDENTICAL | EQUIVALENT | DISTINCT
                 + flag translated_comparison
content        : CORROBORATES | COMPLEMENTS | SPECIALIZES(direção) |
                 SUPERSEDES | CONTRADICTS_FACT | CONFLICTS_ADVICE | INDETERMINATE
```

- **`UNRELATED` não é rótulo — é o default**, a ausência de asserção. Nenhum par é obrigado
  a receber relação.
- **Relação mecanicamente decidível nunca é produzida por modelo.** `representation:
  IDENTICAL` é hash de conteúdo normalizado.
- **`SUPERSEDES` exige sinal de versão no texto, com citação obrigatória.** Nunca metadado,
  nunca `mtime`.
- **Blocagem obrigatória antes da classificação cara.**
- **A lista de `content` pode ser podada pelo `MS-001`.**
- **`PRESUPPOSES` permanece deliberadamente NÃO congelada** como relação definitiva.

---

## 8. CONFLITO · GOVERNANÇA · PRECEDÊNCIA — CONGELADO

### 8.1 As três separações

> **`DETECTION` ≠ `DECISION` ≠ `ENFORCEMENT`.**

**Nenhuma resolução silenciosa.** **`latest source wins` é proibido.**

### 8.2 Estados de conflito — append-only

`NOT_YET_ADJUDICATED` · `UNDECIDABLE_BY_DESIGN` · `CONTEXT_SPLIT` ·
`RESOLVED_BY_SCOPE_REFINEMENT` · `BOTH_VALID` · `PRECEDENCE_DECIDED` ·
`ESCALATED_TO_HUMAN` · `DEFERRED_TO_RUNTIME` · `MISSING_REQUIRED_INPUT` ·
`CLAIM_REJECTED` · `REOPENED_BY_NEW_SOURCE`

- `NOT_YET_ADJUDICATED` ≠ `UNDECIDABLE_BY_DESIGN` — o primeiro é fila de trabalho; o
  segundo é propriedade do corpus e **tem de alcançar o runtime como condição de parada**.
- `DEFERRED_TO_RUNTIME` preserva o comportamento medido do P003: a Skill parou e **pediu**
  decisão. É estado de primeira classe, não perda em arbitragem automática.
- **Nenhum estado é campo mutável.** Alteração só por registro aditivo com supersessão.

### 8.3 Precedência

- **Nunca global por fonte.** Toda precedência é **`(escopo, dimensão)`**.
- Escopo vem de **vocabulário fechado e pré-declarado**, governado.
- Escopo ausente ou insuficiente ⇒ **`INDETERMINATE` + escalada**.
- **Proibido inventar escopo para resolver conflito.**

### 8.4 `DECISION_RECORD`

Toda decisão carrega **ator**, **base**, **hash da política de precedência vigente**, e
cadeia **aditiva** de supersessão.

---

## 9. INDEPENDÊNCIA DE FONTES — CONGELADA

```
source_independence : UNKNOWN | DECLARED_INDEPENDENT | PARTIALLY_DEPENDENT | KNOWN_DEPENDENT
  + evidência/justificativa obrigatória para tudo que não seja UNKNOWN
```

Default **`UNKNOWN`**, e **`UNKNOWN` não conta como independência**.

**Corroboração é reportada em dois campos** — contagem de fontes que concordam **e** estado
de independência. **Nunca colapsada num escalar.** Cursos copiam cursos; concordância entre
dois que copiaram um terceiro não é evidência independente.

---

## 10. `FUSION` × `OPERATIONALIZATION` — CONGELADO

| | `FUSION LAYER` | `OPERATIONALIZATION / MTX ASSEMBLY` |
|---|---|---|
| natureza | **seletiva** — nunca gera conteúdo novo | **geradora**, explicitamente, e governada |
| pode | selecionar · manter ambos · `CONTEXT_SPLIT` · decidir precedência quando autorizada · escalar · deferir | compor artefato operacional novo a partir de elementos compatíveis + política MTX |
| não pode | **inventar um terceiro workflow e atribuí-lo às fontes** | sintetizar sobre conflito não resolvido · atribuir a fonte o que a fonte não ensinou |
| lê `MTX-POLICY`? | **NUNCA** | **sim — é a única camada que lê** |
| determinismo | recomputável dados (pacotes, políticas, decisões) | não determinística → **computada uma vez e SELADA** |

### `MTX_DERIVED_OPERATIONAL_ARTIFACT` — condições cumulativas

1. marcado **`MTX_DERIVED`**;
2. **nunca** atribuído falsamente a uma fonte — atribuição só no nível de **elemento**, por
   id qualificado;
3. cada elemento preserva proveniência: **exatamente uma** de `claim_refs`/`candidate_refs`
   **ou** `mtx_policy_ref`;
4. conteúdo novo da MTX identificado como decisão/política MTX;
5. **conflito não resolvido não é sintetizado em silêncio** — exceção única,
   `DEFERRED_TO_RUNTIME`, entra em `open_questions[]` **como pergunta explícita**;
6. **`synthesis_trace` próprio**, com ator · data · `fusion_package_hash` de origem ·
   modelo e **partição de chamadas** quando gerado por modelo;
7. **aprovação humana quando a política exigir**.

---

## 11. MTX APPLICABILITY — CONGELADA

`NOT_YET_CLASSIFIED` · `DIRECT_USE` · `ADAPT_TO_MTX` · `REFERENCE_ONLY` · `REJECT`

- **`NOT_YET_CLASSIFIED` é fail-closed** para a Operationalization.
- Classificação **sob demanda**, no momento da operacionalização — não em varredura prévia
  do corpus inteiro.
- **Modelo pode PROPOR; proposta não é decisão.** A decisão segue a `MTX-POLICY` e vive
  como `APPLICABILITY_DECISION`, subtipo de `GOVERNANCE_DECISION`, versionada e aditiva.
- **Default inicial, até a política dizer diferente: ator humano MTX (Alexandre).**
- **`REJECT` não apaga corpus.** O item permanece no Fusion Package com proveniência
  intacta; apenas não entra em Operational Package. Rejeição é aditiva e reversível.

---

## 12. `MTX-POLICY` — CONGELADA COMO ARTEFATO

Artefato **versionado e hasheado**, mesmo regime das políticas de ancoragem e precedência.

**Prioridades vigentes:**

1. **Instagram** — canal principal, especialmente vídeos e imagens;
2. **WhatsApp** — conversação comercial e Status;
3. **Google Ads** — mídia paga;
4. **email, SMS e voice** — normalmente implementação de referência, salvo necessidade
   específica.

**A política NÃO altera Source Package. NÃO altera Fusion Package.** É consumida
**somente** pela Operationalization.

Mudança de política **invalida/reabre objetos operacionais correspondentes** — entra em
fila de re-adjudicação toda `APPLICABILITY_DECISION` com `mtx_policy_hash` divergente — e
**não reescreve fontes nem relações semânticas**.

---

## 13. `SEALED` — DEFINIÇÃO OPERACIONAL CONGELADA

Um conjunto está `SEALED` **se e somente se todas** as sete condições valem:

1. existe `SEAL-RECORD` que **enumera todos os membros** por caminho relativo + `sha256`;
2. o `SEAL-RECORD` é ele próprio hasheado, e esse hash é registrado **fora** do conjunto selado;
3. o `SEAL-RECORD` **valida no lugar**, contra o diretório em que vive;
4. o diretório do conjunto **não é escrito por nenhuma outra versão selada**;
5. o **produtor** é referência a uma entidade `TOOLCHAIN` com hash próprio, **não** campo de texto;
6. a validação é **determinística e offline** — não depende de rede, relógio ou **`mtime`**;
7. **nenhum membro se auto-referencia** no próprio manifesto de membros.

**Cada condição vem de um defeito medido neste projeto**, não de teoria: (4) de `v0.2.0` e
`v0.2.1` compartilharem `compiler-v2/`; (3) do `FREEZE-RECORD` da `v0.2.2` ser cópia
byte-idêntica do registro `0.2.0` e **falhar contra o próprio diretório** (11 OK / 4
DIVERGE, reconfirmado no re-audit); (5) de `N1`; (7) de `N5`; (6) da desqualificação do
`mtime` do lado DrvFs.

### `SOURCE_PACKAGE_DEFECT_FOUND_IN_FUSION`

**A Fusion para e reporta. Nunca corrige Source Package selado.** Recompilar é ato
separado, com selo novo e hash novo — nunca correção no lugar.

---

## 14. INCREMENTALIDADE E INVALIDAÇÃO — CONGELADAS

Acrescentar a fonte *k+1* gera **apenas** os *k* conjuntos de pares que a envolvem — custo
linear em *k*, não quadrático — sujeito a blocagem e geração de candidatos.

**Cache:** resultado de relação é chaveado por
`(claim_hash_A, claim_hash_B, relation_policy_hash)`.

### As três regras de invalidação

| evento | efeito |
|---|---|
| fonte **recompilada** (novo `source_package_hash`) | decisões vinculadas por hash de conteúdo de claim **quebram alto**. Nunca derivam em silêncio |
| fonte **acrescentada** | não invalida decisões existentes, mas **marca** `REOPENED_BY_NEW_SOURCE` toda decisão cujo conflict set ganhou membro |
| **política** alterada (precedência ou ancoragem) | toda decisão cujo hash de política diverge do vigente entra em **fila de re-adjudicação** |

---

## 15. SELECTIVE LOADING E RUNTIME MODULAR — CONGELADOS

O `SKILL PACK` suporta: **Manifest** · **Router Index** · **módulos por capacidade** ·
**dependências** · **DAG** · **progressive disclosure** (`L0` índice · `L1` core · `L2`
referências · `L3` proveniência) · **selective loading** · **token budgeting** ·
**proveniência resolvível sob demanda** por `provenance_ledger` por módulo.

- Módulos definidos por **capacidade**, nunca por fonte.
- `dependencies[]` é **declarada** e verificada como **DAG**, com `decision_id` por aresta.
- **Nenhum `SOURCE_LOCAL_CANDIDATE` entra num Skill Pack.**
- `runtime_contract: MODULAR_SKILL_PACK` é **obrigatório e exclusivo** no manifesto.

### Os dois estados de ausência do runtime modular

| estado | significado |
|---|---|
| `NOT_LOADED_YET_FETCHABLE` | o módulo existe no pacote e é buscável. Ausência é normal, a rota resolve |
| `ABSENT_REFUSE` | o módulo é requerido e não existe. **Recusa**, exatamente como o legado |

**Confundi-los é o que fazia carregamento seletivo parecer violação de fail-closed.**

### Invariantes de roteamento

1. orçamento do índice `L0` como **teto rígido medido**, não estimado;
2. **acerto de roteamento é métrica com portão**, sobre consultas plantadas, com limiar
   pré-declarado;
3. **falha de roteamento escala ou pergunta — nunca adivinha módulo**;
4. tensão declarada e não resolvida: um índice discriminativo o bastante tende a convergir
   para carregar o texto da regra. Só medição decide o ponto de equilíbrio.

**O comportamento do runtime legado não é alterado.** `LEGACY_SINGLE_SOURCE` mantém
`## LOAD ORDER — MANDATORY` e `fail_closed_on_missing_executable_resource: true`, com um
único estado de ausência: ausente ⇒ recusa. **Não existe shim de compatibilidade.**

> **Localizador, corrigido pela v1.2 §4 (errata A11):** no bundle vigente,
> `## LOAD ORDER — MANDATORY` está no **`SKILL.md`**; `required_executable_resources` e
> `fail_closed_on_missing_executable_resource` estão no **`manifest.yaml`**, bloco
> `runtime:` — **não** no `SKILL.md`.

---

## 16. DETERMINISMO — CORREÇÃO CONGELADA

> **Uma nova chamada ao modelo NÃO é presumida byte-determinística.**
> **`model re-run determinism` não é pressuposto arquitetural.**

O que a reprodução exige é **persistir e selar**:

- inputs;
- **outputs geradores e judiciais efetivamente utilizados**;
- configurações;
- políticas;
- `DECISION_RECORD`s;
- traces;
- hashes.

O `FUSION PACKAGE` é reproduzível **a partir dos seus artefatos persistidos**. A
verificação opera por **replay dos outputs selados**, **não** por chamadas novas.

**Não se exige que uma reinferência futura produza os mesmos tokens.**

Corolário congelado: a **partição de chamadas** que produziu cada artefato gerador é
registrada. Medido neste projeto: **dividir um segmento em três rende 1,500× mais
evidência** — logo a saída do extractor é função de `(texto, partição)`, e um artefato que
registra o texto e omite a partição **não é reproduzível**.

---

## 17. DECLARATION SPACE — CONGELADO

> ### `filesystem scan ≠ corpus audit`

O declaration space inclui, quando aplicável: **arquivos · ADRs · manifests · erratas ·
freeze records · mensagens de commit**.

**A materialização do `378d764` NÃO elimina mensagens de commit dessa obrigação.**
Elas continuam declaration space legítimo — versionadas, imutáveis, endereçadas por hash.
Toda auditoria futura deste acervo continua obrigada a incluir
`git log --all --format='%H%n%B'` no seu espaço de busca.

Congelado junto: **toda busca de conteúdo é por radical, nunca por forma literal, e entra
com controle positivo.**

---

## 18. A18 — LIMITAÇÃO DOCUMENTAL CONGELADA

**`PROPOSAL_V0_NOT_ARCHIVED`** é uma **`DOCUMENTARY_PRESERVATION_LIMITATION`**.

- A cadeia **arquivável** começa em `DESIGN REVIEW v0`.
- A relação histórica **`UNARCHIVED EXTERNAL PROPOSAL v0 → DESIGN REVIEW v0`** continua
  reconhecida.
- **Não reconstruir.** Conteúdo, bytes ou hash do `PROPOSAL v0` não podem ser derivados por
  inferência, memória ou a partir da própria `DESIGN REVIEW v0`.
- Cópia exata que apareça no futuro entra **aditivamente**, como `ARCHIVAL_COPY`, com
  proveniência e hash, **sem reescrever o registro**.

Não é divergência arquitetural, não invalida a `DESIGN REVIEW v0`, não é razão para
modificar `v1`/`v1.1`/`v1.2`.

---

## 19. I1–I30 — INVARIANTES CONGELADOS

Cada invariante é predicado verificável por script, com canário cuja fixture **tem de
falhar**. **Sem script, não é invariante — é intenção.** Os verificadores são construídos
depois do freeze; o contrato é o que está congelado aqui.

| # | invariante | verificação |
|---|---|---|
| **I1** | Nenhum artefato do Compiler atual é lido, escrito ou referenciado por caminho mutável durante a fusão | varredura de escrita; fixture que escreve e falha |
| **I2** | Nenhuma versão selada compartilha diretório com outra versão selada | conjuntos de diretórios × selos, interseção vazia |
| **I3** | Todo `SEAL-RECORD` valida **no lugar**, contra o diretório em que vive | executar validação a partir do próprio diretório |
| **I4** | Todo identificador citado em qualquer produto é **qualificado** `(source_package_hash, local_id)` | zero `local_id` nu |
| **I5** | Toda `claim` resolve para ≥1 `evidence`; toda `evidence` para ≥1 `SOURCE_ANCHOR`; todo anchor resolve **deterministicamente** | resolução end-to-end, 100% ou falha |
| **I6** | Toda `rule` operacional mantém aresta **direta** para `evidence`, além da via `claim` | ausência da aresta direta = falha |
| **I7** | `NOT_APPLICABLE` e `MISSING` são valores **distintos** em todo campo de ancoragem | canário que troca um pelo outro |
| **I8** | Nenhum objeto `SOURCE_LOCAL_CANDIDATE` é carregável por runtime algum | canário que planta candidato em slot operacional |
| **I9** | `MODULE_DEPENDENCY` é **DAG** | detecção de ciclo; fixture que planta ciclo |
| **I10** | Nenhuma `MODULE_DEPENDENCY` é derivada de `SEMANTIC_RELATION` sem `GOVERNANCE_DECISION` explícita | toda aresta com `decision_id` |
| **I11** | Nenhum estado de conflito é campo mutável; alteração só por registro aditivo com supersessão | diff de histórico; mutação = falha |
| **I12** | Toda decisão carrega **ator**, base e hash da política vigente | campo ausente = falha |
| **I13** | Precedência **nunca global por fonte**; toda precedência é `(escopo, dimensão)` | precedência sem escopo = falha |
| **I14** | Escopo sai de **vocabulário fechado e pré-declarado**; ausente ⇒ `INDETERMINATE` + escalada; nunca inventado | valor fora do vocabulário = falha |
| **I15** | Corroboração é **dois campos** — contagem e estado de independência; nunca colapsada | campo único = falha |
| **I16** | Nenhum relatório traz número digitado à mão | todo número com procedência em script |
| **I17** | Toda busca de conteúdo é por **radical**, nunca por forma literal, com **controle positivo** | 8 falhas medidas justificam o portão |
| **I18** | Nenhum limiar entra em uso sem ter sido **pré-declarado** antes da rodada que o consome | cadeia lock → registry → opening-record por hash |
| **I19** | A **partição de chamadas** que produziu cada artefato gerador é registrada no `COMPILE-TRACE` | ausência = falha |
| **I20** | `FUSION` que encontra defeito em Source Package **para e reporta**. Nunca corrige | qualquer escrita em pacote selado = falha |
| **I21** | `FUSION` nunca sintetiza artefato novo nem atribui composição a fontes | fixture de síntese na fusão tem de falhar |
| **I22** | Síntese só em `OPERATIONALIZATION`; todo artefato sintetizado é `MTX_DERIVED` com `synthesis_trace` | artefato gerado sem trace = falha |
| **I23** | Atribuição a fonte só no nível de **ELEMENTO**, por id qualificado | canário de atribuição falsa |
| **I24** | Todo elemento tem **exatamente uma** linhagem: `claim/candidate_refs` **ou** `mtx_policy_ref`; órfão = falha | varredura de elementos |
| **I25** | Síntese sobre conflito aberto = falha; `DEFERRED_TO_RUNTIME` entra só como pergunta explícita | canário de conflito plantado |
| **I26** | **Fusão cega à `MTX-POLICY`**: `fusion_id` não inclui `mtx_policy_hash`; mesma fusão sob duas políticas → saída **byte-idêntica** | recomputação sob política trocada |
| **I27** | Operationalization não consome `NOT_YET_CLASSIFIED`; **fail-closed** | canário de item sem estado |
| **I28** | Skill Pack constrói-se **sempre** de um Operational Package, mesmo em pass-through | inspeção da cadeia de hashes |
| **I29** | Validade de claim = `ENTAILED_BY` **∧** ancoragem da evidência; dois saltos medidos separadamente, **nunca colapsados** | dois campos, dois relatórios |
| **I30** | Geração — claims, candidatos, artefatos operacionais — **nunca altera camada selada abaixo**; igualdade de hash antes/depois | mecânico, **sem limiar** |

---

## 20. D1–D37 — DECISÕES CONGELADAS

| # | o que congela |
|---|---|
| **D1** | `E1` — Compiler estritamente source-local, nunca alterado por esta arquitetura |
| **D2** | `E2` — a fronteira de nós do pipeline |
| **D3** | Definição operacional de `SEALED` — as **sete condições** da §13 |
| **D4** | `SOURCE_PACKAGE_DEFECT_FOUND_IN_FUSION`: para e reporta, **nunca corrige** |
| **D5** | Identidade qualificada `(source_package_hash, local_id)`, **sem renumerar histórico** |
| **D6** | `SOURCE_ANCHOR` com contrato de resolubilidade **fechado** e lista de tipos **aberta** |
| **D7** | As **três** relações de ancoragem, e `NOT_APPLICABLE ≠ MISSING` |
| **D8** | `ANCHORING-POLICY` como artefato **versionado** |
| **D9** | Claim = comparação; `evidence → claim` é **N:M**; claim selada e **nunca recomputada em voo** |
| **D10** | `lang` + `text_source_lang` **obrigatórios** |
| **D11** | `SOURCE-PROFILE`, `COMPILE-TRACE` (com **partição de chamadas**) e `DECLARATION-SPACE-INDEX` como membros **obrigatórios** |
| **D12** | Os produtos e suas autoridades (§4) |
| **D13** | `fusion_id` por **conjunto ordenado de hashes** |
| **D14** | **Dois eixos** de relação; `UNRELATED` como **default** |
| **D15** | Relação **mecanicamente decidível nunca é produzida por modelo** |
| **D16** | **Blocagem obrigatória** antes da classificação cara |
| **D17** | Os **11 estados** de conflito, **append-only** |
| **D18** | `DECISION_RECORD` com **ator**, base e `precedence_policy_hash` |
| **D19** | Precedência `(escopo, dimensão)`, externa, vocabulário fechado, **proibido inventar escopo** |
| **D20** | Independência em **4 estados**, default `UNKNOWN`, corroboração em **dois campos** |
| **D21** | **Três grafos separados**; `MODULE_DEPENDENCY` **declarada, não inferida** |
| **D22** | **Dois contratos de runtime**, exclusivos, **sem shim** |
| **D23** | `NOT_LOADED_YET_FETCHABLE` ≠ `ABSENT_REFUSE` |
| **D24** | Fusão **incremental** + cache + as **três regras de invalidação** |
| **D25** | Arquitetura de teste e os **10 canários** |
| **D26** | Sequência `MS-000A → MS-000B → MS-001` |
| **D27** | **DESIGN C** sob as três condições da v1 §18.4 — a condição 3 ("seleção ou escalada, nunca síntese") passa a valer **com o escopo da FUSION LAYER** |
| **D28** | `E12` fechada: `LEGACY_SINGLE_SOURCE` preservado com `READY_FOR_CONTROLLED_USE — CONDICIONAL`; pilotos **não** refundidos retroativamente; `MODULAR_SKILL_PACK` **paralelo** |
| **D29** | `E11` fechada **com escopo**: fusão seletiva; síntese só em `OPERATIONALIZATION`, sob as 7 condições (`I21–I25`) |
| **D30** | **Quarto produto adotado**: `OPERATIONAL PACKAGE`, selado uma vez, endereçado por `operational_id`; Skill Pack **sempre** construído dele (`I28`) |
| **D31** | Modelo `MTX_DERIVED_OPERATIONAL_ARTIFACT`, com proveniência **por elemento** e regra de compatibilidade sobre conflitos |
| **D32** | MTX Applicability: os 5 estados, `NOT_YET_CLASSIFIED` **fail-closed**, classificação **sob demanda**, decisão como `APPLICABILITY_DECISION` versionada e aditiva |
| **D33** | Quem decide: **modelo propõe**, `MTX-POLICY` define a matriz de aprovação; **default inicial: ator humano MTX (Alexandre)** |
| **D34** | `MTX-POLICY` versionada/hasheada, lida **só** pela Operationalization; invalidação estendida a `APPLICABILITY_DECISION`s e artefatos operacionais |
| **D35** | Relação `CLAIM —ENTAILED_BY→ {EVIDENCE}`, **total e sem acréscimo**; validade de claim em **dois saltos** (`I29`) |
| **D36** | Critério de morte: **KILL-1** mecânico por igualdade (`I30`) · **KILL-2** variância contra o **1,500× medido** · **KILL-3** piso de entailment com método congelado agora e número no opening record — **nenhum limiar digitado nesta rodada** |
| **D37** | Autoridade de fonte **declarada externamente** no `SOURCE-PROFILE`, **nunca derivada** da qualidade das claims — derivar fecha ciclo autoridade↔precedência, e ciclo é proibido pela família DAG |

---

## 21. NÃO CONGELADO — DELIBERADAMENTE PÓS-FREEZE

Tudo abaixo permanece **aberto por decisão**, e o piloto é quem fecha:

- **thresholds ainda não medidos** — incluindo o piso de `ENTAILED_BY` (vai ao opening
  record do piloto) e os limiares do portão de admissão de candidatos;
- **algoritmo específico de blocagem**;
- **embeddings**;
- **banco vetorial**;
- **tecnologia de índice**;
- **linguagem de implementação**;
- **nomes finais dos módulos**;
- **taxonomia final de relações**, após poda pelo piloto;
- **destino de `PRESUPPOSES`**;
- **tabela final de reprodução por `anchor_type`**;
- **enumeração de repos/refs do `DECLARATION SPACE`** (configuração);
- **qualquer valor que dependa de `MS-000B` ou `MS-001`**;
- **qualquer tecnologia que a arquitetura ainda não precise escolher**.

> Congelar número não medido é o defeito que este projeto já pagou para aprender. Ele não
> se repete aqui.

---

## 22. SEQUÊNCIA EXPERIMENTAL — CONGELADA

```
PILOT-MS-000A — SEAL CANARY
   → PILOT-MS-000B — MULTI-AULA / MESMO AUTOR
      → PILOT-MS-001 — DUAS MICROFONTES CONTROLADAS
```

**Nenhum salto de ordem sem novo `DECISION_RECORD`.**

`MS-000A` vem primeiro por ter **custo próximo de zero e o maior poder de invalidação**: se
o selo não pega os defeitos plantados, nada acima dele vale.

---

## 23. LIMITAÇÕES DECLARADAS DESTE FREEZE

1. **`PROPOSAL_V0_NOT_ARCHIVED`** — a cadeia arquivável começa na `DESIGN REVIEW v0` (§18).
2. **`I1–I30` não têm verificadores implementados.** O contrato está congelado; os scripts
   e canários são trabalho pós-freeze. Um invariante sem script é intenção — e isso está
   dito aqui, não escondido.
3. **`SUPPORTED_BY` não é mecânico** e não será: é julgamento com rubrica pré-registrada,
   auditável por replay (§6.3).
4. **A contagem de espelhamento do `378d764`** (`293 artefatos + 1 ZIP`, escopo `312`) foi
   materializada **como declarada** e **não** reconciliada. Reconciliar é ato separado.
5. **Nada foi implementado.** Este freeze é contrato, não código.
