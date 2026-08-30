# COURSE-TO-SKILL MULTI-SOURCE — ARCHITECTURE PROPOSAL v1

**Antecessores:** `ARCHITECTURE PROPOSAL v0` (`READY_FOR_DESIGN_REVIEW`) → `DESIGN REVIEW v0` + `ADENDO A` (`ARCHITECTURE_REVISION_REQUIRED`, aceita) → **esta v1**
**Data:** 29/08/2026
**Escopo:** SOMENTE DESENHO. Nada implementado.
**Não alterado:** Compiler atual · `compiler-v2-v0.2.2` · `compiler-s3-v0.1.1` · `cts/` · runners · pilotos · N1–N9 · freezes · manifests · `_mirror/` · Drive · Git.
**Classificação final:** `ARCHITECTURE_REVISION_REQUIRED` — **duas decisões**, ambas de Alexandre, ambas com recomendação escrita na §20. Detalhe e justificativa na classificação final.

**Nota de método (limite do instrumento):** escrito sem leitura ao vivo do repo ou do Drive. Onde este documento diz "não existe X", a afirmação verificável é "X não aparece no registro acumulado do projeto". Conferência contra o corpus real é pré-requisito do freeze, e o espaço de busca inclui **mensagem de commit** (§ DECLARATION SPACE).

---

## 1. EXECUTIVE DECISIONS

| # | Decisão | Status |
|---|---|---|
| **E1** | O Compiler atual permanece **estritamente source-local**: uma fonte por execução, sem consciência de outras fontes. Nunca é alterado por esta arquitetura. | **CONGELÁVEL** |
| **E2** | Fronteira de cinco nós: `SOURCE → COMPILE ISOLATED → PACKAGE ASSEMBLY → VALIDATE/SEAL → SOURCE PACKAGE → FUSION` | **CONGELÁVEL** |
| **E3** | **DESIGN C adotado** — o Source Package carrega *candidatos* source-local (regras, workflows, anti-patterns) além de evidence e claims. Candidatos **não são** as regras finais do sistema. Justificativa e comparação na §18. | **CONGELÁVEL sob 3 condições (§18.4)** |
| **E4** | `Claim` é unidade de **COMPARAÇÃO**. Nunca de proveniência. Nunca, sozinha, de decisão. | **CONGELÁVEL** |
| **E5** | Proveniência ancora em **`SOURCE_ANCHOR`**, locator abstrato com contrato de resolubilidade. `text_span` é um subtipo, não o modelo. | **CONGELÁVEL** |
| **E6** | Identidade global por **qualificação**: `(source_package_hash, local_id)`. Nenhum artefato histórico é renumerado. | **CONGELÁVEL** |
| **E7** | Três grafos formalmente separados: `SEMANTIC_RELATION` · `MODULE_DEPENDENCY` · `GOVERNANCE_DECISION`. Dependência de módulo **não é inferida do corpus**. | **CONGELÁVEL** |
| **E8** | Dois contratos de runtime coexistentes e mutuamente excludentes: `LEGACY_SINGLE_SOURCE` (congelado, comportamento medido) e `MODULAR_SKILL_PACK` (novo). | **CONGELÁVEL** |
| **E9** | Independência entre fontes é **estado com evidência**, nunca booleano confiante. Default `UNKNOWN`, e `UNKNOWN` não é tratado como independente. | **CONGELÁVEL** |
| **E10** | Fusão é **incremental por construção**: acrescentar a fonte *k+1* gera *k* conjuntos de pares novos, não `C(k+1,2)`. | **CONGELÁVEL** |
| **E11** | **Fusão estrutural é seleção ou escalada — nunca síntese.** Compor uma sequência nova a partir de duas sequências é invenção. | **ABERTA — bloqueia o freeze (§20.1)** |
| **E12** | Estatuto do produto de fonte única depois do rebaixamento a "candidato" (o que acontece com `READY_FOR_CONTROLLED_USE` dos pilotos existentes). | **ABERTA — bloqueia o freeze (§20.2)** |

---

## 2. ARCHITECTURAL INVARIANTS

Cada invariante é um predicado verificável por script, com canário cuja fixture **tem de falhar**. Sem script, não é invariante — é intenção.

| # | Invariante | Verificação |
|---|---|---|
| **I1** | Nenhum artefato do Compiler atual é lido, escrito ou referenciado por caminho mutável durante a fusão. | varredura de escrita; fixture que escreve e falha |
| **I2** | Nenhuma versão selada compartilha diretório com outra versão selada. | conjunto de diretórios × conjunto de selos, interseção vazia |
| **I3** | Todo `SEAL-RECORD` valida **no lugar**, contra o diretório em que vive. | executar validação a partir do próprio diretório |
| **I4** | Todo identificador citado em qualquer produto é **qualificado**: `(source_package_hash, local_id)`. | zero `local_id` nu em qualquer produto |
| **I5** | Toda `claim` resolve para ≥1 `evidence`; toda `evidence` resolve para ≥1 `SOURCE_ANCHOR`; todo `SOURCE_ANCHOR` **resolve deterministicamente** contra o artefato selado. | resolução end-to-end, 100% ou falha |
| **I6** | Toda `rule` operacional mantém aresta **direta** para `evidence`, além da aresta via `claim`. | ausência da aresta direta = falha |
| **I7** | `NOT_APPLICABLE` e `MISSING` são valores **distintos** em todo campo de ancoragem. | canário que troca um pelo outro e tem de falhar |
| **I8** | Nenhum objeto marcado `SOURCE_LOCAL_CANDIDATE` é carregável por runtime algum. | canário que planta candidato em slot operacional; tem de falhar |
| **I9** | `MODULE_DEPENDENCY` é DAG. | detecção de ciclo; fixture que planta ciclo e tem de falhar |
| **I10** | Nenhuma `MODULE_DEPENDENCY` é derivada de `SEMANTIC_RELATION` sem `GOVERNANCE_DECISION` explícita. | toda aresta de módulo tem `decision_id` |
| **I11** | Nenhum estado de conflito é campo mutável. Alteração só por registro aditivo com supersessão. | diff de histórico; mutação = falha |
| **I12** | Toda decisão carrega **ator**, base, e o hash da versão da política de precedência vigente. | campo ausente = falha |
| **I13** | Precedência nunca é global por fonte. Toda precedência é `(escopo, dimensão)`. | precedência sem escopo = falha |
| **I14** | Escopo sai de **vocabulário fechado e pré-declarado**. Escopo ausente ⇒ `INDETERMINATE` + escalada. Nunca escopo inventado. | valor fora do vocabulário = falha |
| **I15** | Corroboração é reportada como **dois campos**: contagem e estado de independência. Nunca colapsada num escalar. | campo único = falha |
| **I16** | Nenhum relatório traz número digitado à mão. | todo número tem procedência em script |
| **I17** | Toda busca de conteúdo é por **radical**, nunca por forma literal, e entra com controle positivo. | 8 falhas medidas justificam o portão |
| **I18** | Nenhum limiar entra em uso sem ter sido **pré-declarado** antes da rodada que o consome. | cadeia lock → registry → opening-record por hash |
| **I19** | A **partição de chamadas** que produziu cada artefato gerador é registrada no `COMPILE-TRACE`. | ausência = falha (ver §2.1) |
| **I20** | `FUSION` que encontra defeito em Source Package **para e reporta**. Nunca corrige. | qualquer escrita em pacote selado = falha |

### 2.1 Por que a partição de chamadas é invariante e não metadado

Medido: **o mesmo texto em 3 chamadas rende 1,5× mais que em 1**. Logo a saída do extractor não é função apenas do texto — é função de `(texto, partição)`. Um artefato que registra o texto e omite a partição **não é reproduzível**, e "reproduzível" é a propriedade que a compilação isolada existe para garantir. Nenhum piloto registrou isso até hoje.

---

## 3. CURRENT PIPELINE BOUNDARY

```
┌─ ZONA CONGELADA — nunca alterada por esta arquitetura ────────────┐
│  Compiler atual (compiler-v2-v0.2.2, compiler-s3-v0.1.1)          │
│  cts/ · runners · PILOT-001..004 · freezes · manifests            │
│  Contrato de runtime LEGACY_SINGLE_SOURCE                         │
└───────────────────────────────────────────────────────────────────┘
              │ saída lida, nunca modificada
              ▼
┌─ ZONA NOVA ───────────────────────────────────────────────────────┐
│  PACKAGE ASSEMBLY → VALIDATE/SEAL → SOURCE PACKAGE                │
│  CLAIM PASS → BLOCK → DETECT → DECIDE → FUSION PACKAGE            │
│  PACK → SKILL PACK  ·  Contrato MODULAR_SKILL_PACK                │
└───────────────────────────────────────────────────────────────────┘
```

**Regra da fronteira:** o único acoplamento permitido é **leitura**. A zona nova nunca escreve, renomeia, recompila ou renumera nada da zona congelada.

**Três pontos de pressão conhecidos, e onde cada um é absorvido:**

| Pressão | Absorvido em | Como |
|---|---|---|
| N9 — `evidence_id` colide (todos de EV-0001) | **VALIDATE/SEAL** | qualificação `(source_package_hash, local_id)`. O `local_id` histórico **permanece intacto**; a unicidade vem do par |
| Campo de língua ausente no schema | **PACKAGE ASSEMBLY** | `lang` é derivado no assembly e vive no pacote, não no artefato histórico |
| N1/N4/N5 — produtor, `artifact_id` e `files:` não confiáveis | **VALIDATE/SEAL** | o selo **recomputa** identidade e produtor; não copia campo do bundle |

**Consequência que precisa ser declarada, não descoberta:** artefatos históricos nunca tiveram `source_package_hash`. Qualificá-los exige selá-los agora, o que **cria** um hash que não existia quando o artefato foi feito. Isso é **ato de decisão criando um fato**, exatamente como a canonicidade do Item 2 — e o ADR correspondente tem de dizer isso, sendo proibido escrever que "descobrimos que já era assim".

---

## 4. SOURCE PACKAGE CONTRACT

### 4.1 Membros obrigatórios

| Membro | Papel | Existe hoje? |
|---|---|---|
| `SOURCE-PROFILE` | quem é a fonte, língua, tipo de mídia, autoridade **declarada**, estado de independência | **não** |
| `L0` selado | fonte imutável endereçada por conteúdo | sim |
| `ARTIFACTS` | derivados de L0 (transcrição, mapa temporal, páginas, tabelas) | parcial |
| `SOURCE_ANCHORS` | locators de primeira classe (§5) | **não** (hoje é span implícito) |
| `EVIDENCE` | asserções com âncora | sim |
| `CLAIMS` | unidades normalizadas de comparação, **seladas** | **não** |
| `SOURCE_LOCAL_CANDIDATES` | `rule_candidates` · `workflow_candidates` · `anti_pattern_candidates` | sim, **mas hoje rotulados como finais** |
| `COMPILE-TRACE` | chamadas, modelo resolvido, **partição**, checkpoints | **não existe de nenhum piloto** |
| `LOCAL-COHERENCE-REPORT` | contradições **internas** à fonte, detectadas antes da fusão | **não** |
| `DECLARATION-SPACE-INDEX` | onde vivem as declarações sobre este pacote (§5.4) | **não** |
| `SEAL-RECORD` | o selo (§4.2) | parcial e defeituoso |

### 4.2 Definição operacional de `SEALED`

Um conjunto está `SEALED` se e somente se, **todas** as condições valem:

1. existe `SEAL-RECORD` que **enumera todos os membros** por caminho relativo + `sha256`;
2. o `SEAL-RECORD` é ele próprio hasheado, e esse hash é registrado **fora** do conjunto selado;
3. o `SEAL-RECORD` **valida no lugar**, contra o diretório em que vive;
4. o diretório do conjunto **não é escrito por nenhuma outra versão** (I2);
5. o **produtor** é referência a uma entidade `TOOLCHAIN` com hash próprio, **não** um campo de texto;
6. a validação é **determinística e offline** — não depende de rede, relógio ou `mtime`;
7. nenhum membro se auto-referencia no próprio manifesto de membros.

**Cada condição vem de um defeito medido**, não de teoria: (4) de `v0.2.0`/`v0.2.1` compartilharem `compiler-v2/` e serem sobrescritos no lugar; (3) do `FREEZE-RECORD` da `v0.2.2` ser cópia byte-idêntica do registro `0.2.0` e falhar contra o próprio diretório; (5) de N1; (7) de N5; (6) da desqualificação do `mtime` do lado DrvFs/Drive.

### 4.3 Proibições

- Fusão **nunca escreve** em Source Package (I20).
- Defeito descoberto na fusão emite `SOURCE_PACKAGE_DEFECT_FOUND_IN_FUSION`, **para** e reporta. Recompilar é ato separado, com selo novo e hash novo — nunca correção no lugar.
- Nenhum candidato é promovido a regra operacional dentro do Source Package.

---

## 5. SOURCE_ANCHOR / PROVENANCE MODEL

### 5.1 O locator abstrato

`SPAN` deixa de ser o modelo e passa a ser um subtipo. `SOURCE_ANCHOR` tem três campos e **um contrato**:

```
SOURCE_ANCHOR
  anchor_type   : text_span | transcript_timestamp | video_timestamp_range |
                  pdf_page_region | commit_message | code_range | table_range | …
  locator       : payload específico do tipo
  artifact_ref  : (source_package_hash, artifact_local_id)
```

**Contrato de resolubilidade — é isto que congela, não a lista de tipos:**

> Para todo `anchor_type` admitido, existe uma função `resolve(anchor, artefato_selado) → região`, **determinística, offline e total** sobre o domínio declarado. Um tipo sem `resolve` implementado e canariado não é admitido.

A lista de tipos é **aberta e extensível**; o contrato é **fechado**. É isso que permite corpus multimodal/documental sem redesenhar proveniência.

### 5.2 As três relações de ancoragem

| Relação | Pergunta | Decidível mecanicamente? |
|---|---|---|
| `LOCATED_IN` | a região existe e resolve? | **sim** |
| `REPRODUCED_FROM` | o conteúdo citado é reencontrável na região? | **sim**, quando aplicável |
| `SUPPORTED_BY` | a substância da asserção é sustentada pela região? | **não** — exige juízo |

Renomeado de `QUOTED_FROM` para `REPRODUCED_FROM` porque "quote" presume texto. Para `table_range`, reprodução é conjunto de células; para `video_timestamp_range` visual, é hash de frame ou `NOT_APPLICABLE`.

**Estes são os três números que hoje colapsam num campo só:** `LOCATED_IN` 226/226 (100%) · `REPRODUCED_FROM` 139/226 (61,50%) · `SUPPORTED_BY` 12/226 (5,3%). Enquanto forem uma aresta, o consumidor lê 100% quando o número que decide é 5,3%.

### 5.3 Política de reprodução por tipo

`ANCHORING-POLICY` é **artefato versionado e hasheado**, referenciado por todo pacote selado. Declara, por `anchor_type`, se `REPRODUCED_FROM` é `REQUIRED`, `OPTIONAL` ou `NOT_APPLICABLE`.

- Para evidência **textual** (`text_span`, `transcript_timestamp`, `commit_message`): reprodução verbatim pode ser `REQUIRED` conforme a política que vier a ser congelada.
- Para evidência **não textual**: **proibido impor `anchor_quote` artificialmente.** `NOT_APPLICABLE` é valor legítimo.
- **`NOT_APPLICABLE` ≠ `MISSING`** (I7). Confundi-los é a família exata do incidente do `50848d02`, em que ausência esperada teria sido lida como divergência — e a correção de rótulo evitou um FAIL falso.

### 5.4 `commit_message` como tipo de âncora, e o que ele tem de especial

Vem direto da lição do Item 2, oitava ocorrência de "verificação que não alcança onde o dado está". Propriedade que nenhum outro tipo tem: **é imutável e ordenado pelo DAG do git**, logo é o único tipo que suporta anterioridade *dentro* do repositório. Fora dele, continua valendo que hash prova integridade, não anterioridade.

**`DECLARATION SPACE`** é o conjunto enumerado e **bounded** de lugares onde uma declaração pode viver: ADR · manifest · errata · freeze record · **mensagem de commit**. Bounded por: repositórios nomeados + refs nomeadas + o conjunto selado. Sem esses limites, uma auditoria de corpus não termina.

**Item herdado e ainda não resolvido:** a taxonomia que governa o espelho — `GIT_NATIVE_BY_DESIGN`, os 14 arquivos, a direção D2, a proibição de `--delete` — **vive só na mensagem do commit `378d764`**. Qualquer script de empacotamento desta arquitetura será escrito por quem varre arquivos e não a encontrará. Extração para arquivo é pré-requisito de qualquer código (§19).

---

## 6. CLAIM + SOURCE-LOCAL CANDIDATE MODEL

### 6.1 Claim

```
CLAIM
  claim_id        : hash de conteúdo (nunca sequencial)
  package_ref     : source_package_hash
  text_normalized : forma canônica para comparação
  text_source_lang: conteúdo na língua da fonte  ← obrigatório
  lang            : código de língua
  evidence_refs   : conjunto N:M de (source_package_hash, evidence_local_id)
  anchor_refs     : conjunto de SOURCE_ANCHOR
  status          : SEALED
```

**Cardinalidade `evidence → claim` é N:M**, fechando a ambiguidade da v0: uma claim pode se apoiar em várias evidências (corroboração intra-fonte), e uma evidência pode sustentar várias claims. A regra de ouro — deduplicar representação não é deduplicar proveniência — **exige** N:M; a notação linear da v0 sugeria 1:N.

**Claims são computadas uma vez e seladas.** O passe é gerador, logo não determinístico. Recomputar em voo mudaria ids e quebraria decisões a jusante.

**Critério de morte pré-registrado, herdado do Adendo A e mantido:** claim é paráfrase, e paráfrase é a operação que destrói recuperabilidade verbatim.

> **Previsão congelada antes de qualquer rodada: a camada de claim derruba `REPRODUCED_FROM` abaixo de 61,50% sem levantar `SUPPORTED_BY` acima de 5,3%.**

Se confirmada, a camada não entra na forma proposta. **Sob DESIGN C esse risco é menor** — a estrutura sobrevive nos candidatos, então a claim carrega menos peso — mas não é nulo, porque DETECTION continua rodando sobre claims.

### 6.2 Candidatos source-local

```
SOURCE_LOCAL_CANDIDATE
  kind          : rule_candidate | workflow_candidate | anti_pattern_candidate
  local_id      : preservado do artefato histórico, nunca renumerado
  structure     : sequência, condições, exceções, pré-requisitos — PRESERVADAS
  claim_refs    : as claims que o compõem
  evidence_refs : aresta DIRETA, além da via claim (I6)
  status        : SOURCE_LOCAL_CANDIDATE   ← nunca carregável em runtime (I8)
  defects       : campos UNDEFINED, passos únicos, e o que o portão local mediu
```

O campo `defects` existe porque os candidatos **herdam defeitos medidos**: `precedence` UNDEFINED em 93,3% / 88,7% / 96,9%, workflows de passo único em 25–35%, e o `DISPATCH` ocupando 90% do `SKILL.md`. Transportar candidato sem transportar o defeito medido junto seria lavar o artefato.

---

## 7. FUSION PACKAGE CONTRACT

### 7.1 Endereçamento

```
fusion_id = H( conjunto ORDENADO de source_package_hash
             ∪ hash(FUSION-CONFIG)
             ∪ hash(ANCHORING-POLICY)
             ∪ hash(PRECEDENCE-POLICY)
             ∪ hash(conjunto de DECISION RECORDS) )
```

Sem isso não se distinguem duas fusões nem se responde "qual fusão produziu este pacote", e a reprodutibilidade morre em k>2.

### 7.2 Autoridade — quem manda sobre o quê

| Pacote | Natureza | Autoritativo sobre | **Não** autoritativo sobre |
|---|---|---|---|
| `SOURCE PACKAGE` | imutável | conteúdo daquela fonte | qualquer outra fonte |
| `FUSION PACKAGE` | derivado, recomputável | relações, decisões, regras operacionais | conteúdo de fonte |
| `SKILL PACK` | artefato de consumo | nada | tudo — toda saída resolve para trás |

### 7.3 Membros

`FUSED-CLAIMS` (canônicas) · `OPERATIONAL-RULES` · `WORKFLOWS` · `ANTI-PATTERNS` · `RELATION-SET` · `CONFLICT-SETS` · `DECISION-RECORDS` · `CANDIDATE-ADMISSION-REPORT` · `PROVENANCE-LEDGER` (por módulo, para permitir L3 sem carregar tudo) · `FUSION-TRACE`.

### 7.4 Portão de admissão de candidatos

Fusão **não consome candidato sem passar por portão**, sob pena de herdar todos os defeitos medidos. O portão existe e congela como contrato; **seus limiares não congelam agora** — saem medidos do `PILOT-MS-000B`, conforme a regra de não congelar número sem medição.

---

## 8. SEMANTIC RELATION MODEL

### 8.1 Dois eixos

```
representation : IDENTICAL | EQUIVALENT | DISTINCT
                 + flag translated_comparison   (comparação atravessou línguas)
content        : CORROBORATES | COMPLEMENTS | SPECIALIZES(direção) |
                 CONTRADICTS_FACT | CONFLICTS_ADVICE | SUPERSEDES |
                 INDETERMINATE
```

`UNRELATED` **não é rótulo — é o default**, a ausência de asserção. É o que impede que todo par tenha de ser classificado, e é a decisão de custo mais importante do modelo.

### 8.2 Procedimento por relação, e quem pode produzi-la

| Relação | Procedimento | Produzida por modelo? |
|---|---|---|
| `representation: IDENTICAL` | hash de conteúdo normalizado | **NÃO — mecânica** |
| `representation: EQUIVALENT` | blocagem + classificador | sim, com controle negativo |
| `CORROBORATES` | classificador + estado de independência (§9.4) | sim |
| `COMPLEMENTS` | classificador | sim |
| `SPECIALIZES` | classificador + escopo de vocabulário fechado | sim |
| `SUPERSEDES` | sinal de versão **no texto**, com citação obrigatória. Nunca metadado, nunca `mtime` | sim |
| `CONTRADICTS_FACT` | classificador; resolução por evidência | sim |
| `CONFLICTS_ADVICE` | classificador; resolução por escopo/objetivo | sim |
| `INDETERMINATE` | saída legítima, não falha | — |

**Motivo de separar decidível de indecidível:** misturá-los numa lista plana é o defeito já medido neste projeto, onde `confidence.score` ficou constante em 0,97 e 8 de 10 campos de classificação tinham entropia zero. **Os campos que carregavam a garantia pararam de carregar informação.** Relação mecanicamente decidível produzida por modelo repete isso.

**Por que `SUPERSEDES` é obrigatória e não opcional:** no corpus pretendido — ferramentas que mudam rápido — "B fala de uma versão mais nova da mesma coisa" é provavelmente a relação **mais frequente**. Sem ela, colapsa em `CONTRADICTS` e dispara maquinaria de conflito para algo que não é discordância.

### 8.3 `PRESUPPOSES` — rebaixada, e retratação registrada

O `ADENDO A` propôs `PRESUPPOSES` como a relação que **derivaria** o grafo de dependências de módulo. **Isso estava errado, e Alexandre está certo:** era inventar uma relação semântica para justificar uma decisão de packaging. Fica registrado como retratação, não silenciado.

`PRESUPPOSES` permanece **candidata** a relação semântica, admitida só se demonstrar utilidade própria em `PILOT-MS-001`. **Dependência de módulo não depende dela** (§9.5).

### 8.4 Blocagem obrigatória

```
claims seladas → BLOCAGEM não-geradora → DETECTION (só candidatos) → DECISION
```

Nenhum par chega a um modelo antes da blocagem. **Ressalva permanente:** blocagem é matcher mecânico, e matcher mecânico falhou **8 vezes** neste projeto. Entra como **instrumento medido**, com controle positivo e recall pré-declarado contra pares plantados — nunca como otimização silenciosa. O algoritmo de blocagem **não congela nesta rodada**.

---

## 9. CONFLICT / GOVERNANCE / PRECEDENCE MODEL

### 9.1 Estados de conflito (append-only)

`NOT_YET_ADJUDICATED` · `UNDECIDABLE_BY_DESIGN` · `CONTEXT_SPLIT` · `RESOLVED_BY_SCOPE_REFINEMENT` · `BOTH_VALID` · `PRECEDENCE_DECIDED` · `ESCALATED_TO_HUMAN` · `DEFERRED_TO_RUNTIME` · `MISSING_REQUIRED_INPUT` · `CLAIM_REJECTED` · `REOPENED_BY_NEW_SOURCE`

Distinções que carregam peso:

- **`NOT_YET_ADJUDICATED` ≠ `UNDECIDABLE_BY_DESIGN`.** O primeiro é fila de trabalho; o segundo é propriedade do corpus e **tem de alcançar o runtime como condição de parada**.
- **`DEFERRED_TO_RUNTIME`** é o comportamento provado do P003 — a Skill parou e **pediu** decisão quando `precedence: UNDEFINED` mordeu. É o melhor comportamento que este projeto já produziu e a arquitetura tem de preservá-lo como estado de primeira classe, não perdê-lo em arbitragem automática.
- **`REOPENED_BY_NEW_SOURCE`** (novo, §13): fonte nova pode invalidar um `CONTEXT_SPLIT` ao cobrir a lacuna que o justificava.

### 9.2 Decision record

Estado numa aresta não é registro. Toda decisão é objeto endereçável:

```
DECISION_RECORD
  decision_id · hash · actor (humano | regra | modelo — obrigatório)
  basis · precedence_policy_hash · conflict_set_ref
  supersedes : decision_id | null      ← cadeia aditiva, nunca mutação
```

O `actor` é load-bearing: neste projeto, juízo de modelo não é medição. Uma decisão sem ator é indistinguível de fato descoberto — que é exatamente o erro que o ADR do Item 2 foi obrigado a não cometer.

### 9.3 Precedência

- **Nunca global por fonte.** Toda precedência é `(escopo, dimensão)`.
- **Externa às fontes.** Uma fonte não pode saber de fontes que nunca viu; precedência declarada dentro dela é necessariamente incompleta e fica errada assim que uma fonte é acrescentada.
- **Vocabulário de escopo fechado e pré-declarado.** Escopo insuficiente ⇒ `INDETERMINATE` + escalada. **Proibido inventar escopo.**
- A `PRECEDENCE-POLICY` é artefato versionado e hasheado; toda decisão carrega o hash da versão vigente.

**Risco nomeado:** escopo é a saída de emergência que faz toda contradição desaparecer. Com `precedence: UNDEFINED` medido em ~90% e escopo tendo de ser inferido, precedência scope-aware sem o vocabulário fechado degenera em "fabrique uma diferença de escopo e declare `BOTH_VALID`" — o falso negativo do multi-source, e silencioso.

### 9.4 Independência de fontes

```
source_independence : UNKNOWN | DECLARED_INDEPENDENT |
                      PARTIALLY_DEPENDENT | KNOWN_DEPENDENT
  + evidence/justification obrigatória para tudo que não seja UNKNOWN
```

Default é `UNKNOWN`, e **`UNKNOWN` não é tratado como independente**. Corroboração é sempre reportada em **dois campos** — contagem e estado de independência — nunca colapsada num escalar de confiança (I15). Cursos copiam cursos; concordância entre dois que copiaram um terceiro não é evidência independente, e o viés cresce com o corpus.

### 9.5 Os três grafos

| Grafo | O que liga | Origem | Custo do erro | Verificação |
|---|---|---|---|---|
| `SEMANTIC_RELATION` | claim ↔ claim | **derivada** do corpus | degrada qualidade | canário de detecção |
| `MODULE_DEPENDENCY` | módulo → módulo | **declarada** pelo packager | **quebra execução** | DAG + canário de ciclo |
| `GOVERNANCE_DECISION` | explica por que a aresta existe | **registrada** por ator | destrói auditabilidade | todo par tem `decision_id` |

**É por terem custos de erro e procedimentos de verificação diferentes que não podem ser um mecanismo só.** Dependência de módulo **não precisa ser inferida do corpus** — pode ser decisão de arquitetura, e nesse caso o que a justifica é o `GOVERNANCE_DECISION`, não uma relação semântica fabricada.

---

## 10. SKILL PACK CONTRACT

```
SKILL_PACK
  manifest:
    runtime_contract   : MODULAR_SKILL_PACK      ← obrigatório e exclusivo
    fusion_package_hash
    modules[]          : id, capability_ref, dependencies[], budget
    router_ref
    disclosure_levels  : L0 índice | L1 core | L2 referências | L3 proveniência
  provenance_ledger    : por módulo — permite L3 sem carregar o pacote inteiro
```

- Módulos definidos por **capacidade**, nunca por fonte. Módulo por fonte é o pacote confessando que não fundiu nada.
- Nomes definitivos de módulos **não congelam nesta rodada**.
- `dependencies[]` é declarada e verificada como DAG (I9), com `decision_id` por aresta (I10).
- **Nenhum `SOURCE_LOCAL_CANDIDATE` entra num Skill Pack** (I8).

---

## 11. LEGACY RUNTIME vs MODULAR RUNTIME

| | `LEGACY_SINGLE_SOURCE` | `MODULAR_SKILL_PACK` |
|---|---|---|
| Carregamento | `## LOAD ORDER — MANDATORY` — tudo, sempre | seletivo por rota |
| Recursos | `required_executable_resources` obrigatórios | por módulo, com estados |
| Ausência | `fail_closed_on_missing_executable_resource: true` → **recusa** | distingue dois casos (abaixo) |
| Estado | **CONGELADO** — comportamento medido no TEST-0007 | novo |
| Alterações | **nenhuma, nunca** | evolutivo |

### 11.1 A fronteira

> **Um pacote declara exatamente um contrato de runtime. Um runtime recusa, fail-closed, qualquer pacote que declare o outro. Não existe shim de compatibilidade.**

Shim é exatamente onde os dois contratos vazariam um no outro. A ausência dele é a garantia.

### 11.2 A distinção que torna o seletivo compatível com fail-closed

O runtime legado tem **um** estado de ausência: ausente ⇒ recusa. Foi medido: no TEST-0007 o braço ablado **não tentou execução degradada — foi contratualmente instruído a recusar**.

O runtime modular tem **dois**:

- `NOT_LOADED_YET_FETCHABLE` — o módulo existe no pacote e é buscável. Ausência é normal, e a rota resolve.
- `ABSENT_REFUSE` — o módulo é requerido e não existe. Recusa, exatamente como o legado.

Confundir os dois é o que fazia carregamento seletivo parecer violação de fail-closed. Separados, os dois contratos coexistem sem que nenhum comportamento medido dos pilotos mude.

---

## 12. ROUTING / SELECTIVE LOADING

**O router é o novo `DISPATCH`, e `DISPATCH` é defeito medido:** no P003 ocupou 167 linhas, 90% do `SKILL.md`, listando 158 workflows dos quais 40 tinham passo único. Um router sobre módulos de muitas fontes é esse problema elevado a *k*.

Invariantes de roteamento:

1. **Orçamento do índice L0 declarado como teto rígido**, e o teto é medido, não estimado.
2. **Acerto de roteamento é métrica com portão**, medida sobre consultas plantadas, com limiar pré-declarado. Sem isso, carregamento progressivo é suposição, não mecanismo.
3. **Falha de roteamento escala ou pergunta — nunca adivinha módulo.** Preserva o comportamento provado do P003.
4. Tensão declarada e não resolvida: um índice discriminativo o bastante para rotear certo **tende a convergir para carregar o texto da regra**. Só medição decide onde o ponto de equilíbrio está — daí o portão do item 2.

Tecnologia de índice, embeddings e banco vetorial **não congelam nesta rodada**.

---

## 13. INCREMENTAL FUSION / INVALIDATION

### 13.1 Incrementalidade

Acrescentar a fonte *k+1* gera **apenas** os conjuntos de pares que a envolvem: *k* conjuntos novos, não `C(k+1,2)`. O custo por adição é linear em *k*, não quadrático — e é isso que torna o crescimento do corpus sustentável.

### 13.2 Cache

Resultado de relação é chaveado por `(claim_hash_A, claim_hash_B, relation_policy_hash)`. Estável sob adição de fontes; invalida corretamente sob mudança de política.

### 13.3 Invalidação — as três regras

| Evento | Efeito |
|---|---|
| Fonte **recompilada** (novo `source_package_hash`) | decisões vinculadas por hash de conteúdo de claim **quebram alto**. Nunca deriva em silêncio |
| Fonte **acrescentada** | não invalida decisões existentes, mas **marca** `REOPENED_BY_NEW_SOURCE` toda decisão cujo conflict set ganhou membro |
| **Política** alterada (precedência ou ancoragem) | toda decisão cujo `precedence_policy_hash` diverge do vigente entra em fila de re-adjudicação |

**Sem a segunda regra o Fusion Package deriva silenciosamente para fora da correção conforme cresce** — e o defeito só apareceria com dezenas de fontes, que é exatamente onde ninguém quer descobri-lo.

---

## 14. TEST ARCHITECTURE

Herdado e não negociável: toda alegação vira script · todo verificador entra com canário cujas fixtures **têm de falhar** · todo limiar é pré-declarado · nenhum número digitado à mão · busca por radical com controle positivo · duas pistas de saída (`INVALID`/exit 2 para instrumento, `FAIL`/exit 1 para candidata).

**Canários obrigatórios, um por invariante de risco:**

| Canário | Fixture que TEM de falhar |
|---|---|
| **Selo** | duas versões compartilhando diretório · `SEAL-RECORD` que não valida no lugar · manifesto auto-referente (N5) · produtor divergente do real (N1) |
| **Candidato** | `SOURCE_LOCAL_CANDIDATE` plantado em slot operacional |
| **Ciclo** | ciclo plantado no `MODULE_DEPENDENCY` |
| **Falso dedup** | duas claims que diferem só num qualificador de escopo que a paráfrase largou |
| **Falsa contradição** | mesma substância em duas línguas · versões diferentes da mesma ferramenta (deve dar `SUPERSEDES`, não `CONTRADICTS`) |
| **Falso acordo** | mesmo vocabulário, substância diferente |
| **Roteamento** | consulta cuja rota correta é "não sei" — tem de escalar, não adivinhar |
| **Independência** | corroboração sob `UNKNOWN` contada como confirmação |
| **Âncora** | `NOT_APPLICABLE` trocado por `MISSING` |
| **Ancoragem** | quote que existe mas não sustenta (`REPRODUCED_FROM` ok, `SUPPORTED_BY` falso) |

**Lição incorporada:** canário só vale o quanto a fixture modela a realidade — o REV4 passou 29/29 carregando um mundo impossível. Toda fixture de comparação usa hashes distintos por fase.

---

## 15. PILOT-MS-000A — SEAL CANARY

**Objetivo:** provar que o selo novo pega os defeitos que o selo velho não pegou. **Sem corpus novo. Sem chamada de modelo. Custo ~zero.**

**Fixtures que TÊM de falhar:** (a) duas versões seladas compartilhando diretório com sobrescrita no lugar · (b) `FREEZE-RECORD` que não valida contra o diretório em que vive · (c) manifesto auto-referente e divergente (N5) · (d) carimbo de produtor divergente do produtor real (N1) · (e) `artifact_id` repetido entre pacotes (N4) · (f) `local_id` nu, sem qualificação (N9).

**PASS:** 6/6 fixtures falham como desenhado, e ≥1 fixture de caminho feliz passa.
**KILL:** qualquer fixture passando. Se o selo não pega os seis, **nada acima dele vale** e a arquitetura não avança.
**Ordem:** primeiro. É o mais barato e o de maior poder de invalidação.

---

## 16. PILOT-MS-000B — MULTI-AULA, MESMO AUTOR

**Objetivo:** fechar o buraco real de que **corpus multi-aula nunca foi testado** — os 4 pilotos são vídeo único com timeline contínua.

**Corpus:** duas aulas sequenciais do mesmo curso, mesmo autor, mesma língua.

**Por que antes do MS-001:** exercita Source Package, qualificação de identidade, claims, blocagem, admissão de candidatos, fusão e Skill Pack **sem** o problema de DECISION — a precedência é natural pela ordem. Isola encanamento de arbitragem. O `MS-001` testaria os dois ao mesmo tempo, e na falha não se saberia qual falhou.

**Mede, e são medições que ninguém tem:** limiares do portão de admissão de candidatos (§7.4) · se a estrutura de workflow sobrevive à travessia (o teste do DESIGN C) · variância do passe de claim entre execuções · custo real de blocagem + detecção numa escala conhecida.

**PASS:** identidade qualificada sem colisão · nenhuma estrutura de workflow perdida na travessia · duas execuções independentes com conjuntos de claims dentro da tolerância pré-declarada · zero número digitado à mão.
**KILL:** `REPRODUCED_FROM` cai abaixo do medido hoje · variância do conjunto de claims excede o 1,5× já medido do extractor · estrutura de sequência perdida (invalida DESIGN C).

---

## 17. PILOT-MS-001 — DUAS MICROFONTES PLANTADAS

Só depois dos dois anteriores.

**Plantio — o da v0 cobre 5 das 7 relações. Acrescentar:**

1. **`UNRELATED` como controle negativo.** Sem ele, um classificador que responde "relacionado" a tudo tira nota máxima. É a adição mais importante.
2. **`representation: IDENTICAL`** — sem fixture, a categoria é asserção.
3. **Falso ACORDO** — mesmo vocabulário, substância diferente. É o espelho da contradição aparente, e o modo de falha mais provável dadas as 8 falhas de casamento por forma literal.
4. **A colisão N9 plantada de propósito** — as duas fontes numerando de EV-0001 internamente. Se o microcorpus não reproduz a colisão, não testa o mecanismo medido quebrado.
5. **Par cuja resposta certa é "não dá para decidir"** — canário no sentido da casa. Se DECISION devolver rótulo confiante ali, dispara. Teste direto da proibição de `latest-wins`.
6. **`SUPERSEDES` com sinal no TEXTO**, nunca em metadado — coerente com o Item 2, onde a ordem saiu de identidade de conteúdo, não de data.
7. **Duas línguas diferentes** — é a falha sistemática medida do pipeline, e o PILOT-004 já provou que o projeto opera em pt-BR.
8. **Duas escalas (ex.: ~30 e ~60 claims)** — **mede** o expoente de crescimento em vez de assumi-lo. Responde a pergunta de custo pelo preço de um microcorpus.
9. **Um par sob `source_independence: UNKNOWN`** — verifica que corroboração não é contada como confirmação.

**PASS:** relações plantadas recuperadas na taxa pré-declarada · `UNRELATED` não classificado errado · canários falharam como desenhado · duas execuções independentes dentro da tolerância · zero número digitado à mão.
**KILL:** ancoragem mecânica cai · variância de claims > 1,5× · crescimento entre as duas escalas sai quadrático apesar da blocagem.
**ORÇAMENTO:** teto absoluto de chamadas/tokens declarado antes, que interrompe a rodada. Modelo fixado por política já vigente (`claude-sonnet-5`), não por conveniência desta rodada.

**Trava:** o piloto **não passa por ser pequeno**. A extrapolação de escala é critério de aprovação, não trabalho posterior.

---

## 18. DESIGN A vs B vs C

### 18.1 Os três

| | **A — regras viajam como finais** | **B — para nas claims** | **C — candidatos source-local** |
|---|---|---|---|
| Source Package termina em | regras finais | claims atômicas | claims **+ candidatos estruturados** |
| Quem produz a regra operacional | o Compiler | a Fusão | a Fusão, **a partir de candidatos** |
| Estrutura (sequência, condição, exceção) | preservada | **perdida e re-derivada** | **preservada e transportada** |
| Fonte única | caminho separado, mantido para sempre | caso degenerado | **modo suportado, com estatuto a definir** |
| Contaminação do Compiler | nenhuma | nenhuma (mas rebaixa a saída atual a insumo) | nenhuma |

### 18.2 Por que B cai

B era minha recomendação anterior e **está errada pela razão que Alexandre apontou**. Um workflow é sequência ordenada com condições e exceções. Decompô-lo em claims atômicas e recompô-lo na fusão exige **reconstruir** a ordem — e reconstrução de sequência é ato gerador sem comportamento medido, isto é, invenção.

O baseline apoia a objeção: o P003 produziu **601 passos em 158 workflows**, e a ordem veio da sequência da própria fonte. Com **25–35% de workflows de passo único** já medidos, a extração de sequência é frágil *hoje*; atomizar e recompor a tornaria pior. B trocaria um defeito conhecido por um modo de falha novo e não medido.

### 18.3 Por que A cai

Em A, a regra se compromete com uma forma **antes** de existir contexto cross-source. Dedup em nível de regra ameaça diretamente a regra de ouro (proveniência preservada). E fonte única fica sendo um caminho paralelo mantido para sempre — dois pipelines, duas verdades.

### 18.4 Recomendação: **DESIGN C**, sob três condições

C preserva o que B destrói e evita o compromisso prematuro de A. E tem uma propriedade que os outros não têm: **o Compiler atual já produz exatamente esses objetos** — o selo apenas os **reclassifica** como candidatos, sem regenerar nada. "Compiler intocado" passa a ser literalmente verdade.

C também é honesto sobre o estado medido: com `SUPPORTED_BY` em 5,3%, essas regras **nunca foram seguramente finais**. Chamá-las de candidatos é corrigir um rótulo, não rebaixar um produto.

**As três condições, e nenhuma é opcional:**

1. **Candidato nunca carrega em runtime, fail-closed** (I8). Sem isso, C institucionaliza o defeito que o projeto já sofreu: `validation-decision-v0.1.2.yaml` dizia `REQUIRES_REVISION` e o `validation-decision-template.yaml` do **mesmo pacote** dizia `PENDING` — duas verdades no mesmo lugar, e quem abriu o pacote leu a errada. Duas populações de regra sem trava de carregamento é essa contradição elevada a k.
2. **Portão de admissão de candidatos antes da fusão** (§7.4). Candidatos carregam defeitos medidos; consumi-los sem portão é herdá-los.
3. **Fusão estrutural é seleção ou escalada — nunca síntese.** Ver §20.1: é a decisão que ainda bloqueia o freeze.

**Custo de C, declarado:** o Source Package fica maior (o bundle do P003 já tem 880.321 bytes, dominados por `decision-rules.yaml` 516 KB + `workflows.yaml` 332 KB). Mitigação: **candidatos não são carregados por runtime algum** — são artefatos de auditoria e fusão. O tamanho do Skill Pack é governado pela saída fundida, não pelos candidatos.

---

## 19. DECISIONS READY TO FREEZE

D1 E1 · D2 E2 · D3 definição operacional de `SEALED` (§4.2, sete condições) · D4 `SOURCE_PACKAGE_DEFECT_FOUND_IN_FUSION`: para e reporta, nunca corrige · D5 identidade qualificada `(source_package_hash, local_id)`, sem renumerar histórico · D6 `SOURCE_ANCHOR` com contrato de resolubilidade fechado e lista de tipos aberta · D7 três relações de ancoragem, e `NOT_APPLICABLE ≠ MISSING` · D8 `ANCHORING-POLICY` como artefato versionado · D9 claim = comparação; `evidence → claim` **N:M**; claim selada e nunca recomputada em voo · D10 `lang` + `text_source_lang` obrigatórios · D11 `SOURCE-PROFILE`, `COMPILE-TRACE` (com **partição de chamadas**) e `DECLARATION-SPACE-INDEX` como membros obrigatórios · D12 três produtos e suas autoridades (§7.2) · D13 `fusion_id` por conjunto ordenado de hashes · D14 dois eixos de relação; `UNRELATED` como default · D15 relação mecanicamente decidível nunca produzida por modelo · D16 blocagem obrigatória antes da classificação cara · D17 os 11 estados de conflito, append-only · D18 `DECISION_RECORD` com ator, base e `precedence_policy_hash` · D19 precedência `(escopo, dimensão)`, externa, vocabulário fechado, proibido inventar escopo · D20 independência em 4 estados, default `UNKNOWN`, corroboração em dois campos · D21 três grafos separados; `MODULE_DEPENDENCY` declarada, não inferida · D22 dois contratos de runtime, exclusivos, sem shim · D23 `NOT_LOADED_YET_FETCHABLE` ≠ `ABSENT_REFUSE` · D24 fusão incremental + cache + as três regras de invalidação · D25 arquitetura de teste e os 10 canários · D26 sequência `MS-000A → MS-000B → MS-001` · D27 DESIGN C sob as três condições da §18.4.

**Pré-requisito de qualquer código, independente do freeze:** extrair a taxonomia do espelho (`GIT_NATIVE_BY_DESIGN`, os 14, direção D2, proibição de `--delete`) da mensagem do commit `378d764` para **arquivo**. Quem escrever script de empacotamento varre arquivos e não a encontra.

---

## 20. DECISIONS STILL OPEN

### 20.1 — BLOQUEIA O FREEZE — Fusão estrutural: seleção, escalada ou síntese?

Duas fontes ensinam workflows diferentes para a mesma capacidade. A fusão:

- **(a) seleciona** um dos dois, com decisão registrada;
- **(b) escala** para humano;
- **(c) sintetiza** um terceiro, novo.

**Recomendação: (a) ou (b). Nunca (c).** Síntese de sequência é ato gerador sem comportamento medido — é a definição de invenção, e este projeto já mediu que invenção entra na camada de escrita, não na de empacotamento.

**Por que bloqueia:** decide se `FUSION` é componente **gerador** ou **seletivo**. Isso muda o contrato do Fusion Package, o custo, a auditabilidade e o modelo de proveniência inteiro. **Não é possível escrever a §7 de forma final sem essa decisão.**

### 20.2 — BLOQUEIA O FREEZE — Estatuto do produto de fonte única sob DESIGN C

Sob C, o bundle de hoje é **candidato**, não regra final. Pergunta: o `READY_FOR_CONTROLLED_USE` (condicional) dos pilotos existentes **sobrevive** a esse rótulo?

- **(a)** Sobrevive: fonte única é modo suportado, e um Source Package de uma fonte é consumível no runtime **LEGACY**, sem passar por fusão.
- **(b)** Não sobrevive: todo produto passa por fusão, inclusive k=1, e os pilotos ficam em outro estatuto até serem refundidos.

**Recomendação: (a).** Preserva o único produto funcionando que o projeto tem, mantém o contrato legado intacto e é coerente com E8. Mas **é decisão de produto, não de arquitetura, e é sua.**

**Por que bloqueia:** decide se `MODULAR_SKILL_PACK` é caminho **paralelo** ou **substituto**, o que muda §10, §11 e o significado de "fonte única" em toda a v1.

### 20.3 — Abertas, não bloqueantes

- Limiares do portão de admissão de candidatos → saem medidos do `MS-000B`.
- Tabela de reprodução por `anchor_type` → o contrato congela; a tabela sai da política.
- Escopo do `DECLARATION SPACE`: quais repos, quais refs, qual janela. Sem limite, auditoria de corpus não termina.
- `PRESUPPOSES` admitida ou descartada → decide o `MS-001`.
- Autoridade de fonte: declarada externamente (recomendado) — se derivada da qualidade das claims, fecha ciclo com a precedência.
- Vocabulário fechado de escopo: quem o escreve e a partir de quê.
- Não congelados por decisão sua: embeddings · banco vetorial · tecnologia de índice · linguagem · limiares sem medição · nomes de módulos.

---

## CLASSIFICAÇÃO FINAL

# `ARCHITECTURE_REVISION_REQUIRED`

**A distância mudou de categoria.** A v0 tinha seis defeitos estruturais. A v1 tem **27 decisões prontas para congelar e duas decisões abertas** — e as duas abertas não são defeitos do desenho: são escolhas que só Alexandre pode fazer, ambas com recomendação escrita.

**Exatamente o que impede o freeze:**

1. **§20.1 — fusão estrutural: seleção, escalada ou síntese.** Sem isso, o `FUSION PACKAGE CONTRACT` (§7) não pode ser escrito em forma final, porque não se sabe se `FUSION` é componente gerador ou seletivo.
2. **§20.2 — estatuto do produto de fonte única sob DESIGN C.** Sem isso, §10 e §11 ficam ambíguas sobre se o runtime modular é paralelo ou substituto — e o estatuto dos quatro pilotos existentes fica indefinido.

**Nada mais bloqueia.** Fechadas as duas — e a resposta pode ser "aceito as duas recomendações" —, a v1 vira **v1.1 `READY_TO_FREEZE_ARCHITECTURE`** na mesma rodada, sem novo ciclo de revisão.

Depois do freeze, a primeira coisa a rodar é o `PILOT-MS-000A`: custo próximo de zero e o maior poder de invalidação do conjunto. Se o selo não pega os seis defeitos plantados, nada construído acima dele vale.

---

**FIM DA PROPOSTA v1. Nada implementado. Nenhum artefato do projeto foi lido, alterado ou criado em Drive, Git, `_mirror/`, `cts/`, runners, freezes ou manifests.**
