# COURSE-TO-SKILL MULTI-SOURCE — ARCHITECTURE PROPOSAL v1.1

**Antecessores:** `PROPOSAL v0` → `DESIGN REVIEW v0 + ADENDO A` → `PROPOSAL v1` (`ARCHITECTURE_REVISION_REQUIRED`, 2 decisões abertas) → cross-review Claude Chat ↔ ChatGPT → **esta v1.1**
**Data:** 30/08/2026
**Natureza:** delta consolidado sobre a v1. **O que a v1 congela e esta v1.1 não menciona, permanece como na v1** (D1–D27, invariantes I1–I20, contratos das §§3–17). Nada é reescrito por reescrever.
**Escopo:** SOMENTE DESENHO. Nada implementado. Nada alterado em Git, Drive, Compiler, pilotos, N1–N9, freezes, manifests, `_mirror/`, `cts/` ou runners.
**Classificação final:** **`READY_TO_FREEZE_ARCHITECTURE`** — justificativa e a única condição do ATO de freeze na §12.

---

## 1. DECISÕES FECHADAS DESDE A v1

### 1.1 — §20.2 FECHADA (recomendação (a) aceita)

| Contrato | Estatuto |
|---|---|
| `LEGACY_SINGLE_SOURCE` | **preservado**. Pilotos históricos continuam válidos sob o contrato atual (`LOAD ORDER — MANDATORY`, fail-closed). `READY_FOR_CONTROLLED_USE — CONDICIONAL` segue valendo para fonte única. **Não passam retroativamente pela Fusion Layer.** Nenhuma mudança em runtime, freezes ou artefatos existentes |
| `MODULAR_SKILL_PACK` | caminho **novo e paralelo**, contrato próprio, **não substitui** o legado retroativamente |

`E12` da v1 muda de `ABERTA` para **`FECHADA`**.

### 1.2 — §20.1 REFORMULADA E FECHADA

"Selecionar ou escalar — nunca sintetizar" **não é invariante global**. Vale **dentro da camada semântica de FUSION**. A síntese é legal — mas em **outra camada**, geradora e governada (§2). `E11` da v1 muda de `ABERTA` para **`FECHADA (com escopo)`**.

### 1.3 — Retratação registrada: o critério de morte da v1 media a aresta errada

A v1 congelou como critério de morte: *"a camada de claim derruba `REPRODUCED_FROM` abaixo de 61,50%"*. **Isso era vazio sob a própria arquitetura da v1**: claims são computadas do lado da fusão a partir de pacotes **selados** — a camada de evidência e suas âncoras não são tocadas, logo `REPRODUCED_FROM` (propriedade de `EVIDENCE ↔ SOURCE_ANCHOR`) **não pode** cair por causa da geração de claims. Critério que não pode disparar não é critério. A correção do cross-review está certa e é aceita; o critério reformulado está na §7.3.

---

## 2. A NOVA SEPARAÇÃO: `FUSION` × `OPERATIONALIZATION`

Duas camadas, dois regimes, e a linha entre elas é a linha entre **o que o corpus sustenta** e **o que a MTX decidiu fazer**.

| | `FUSION LAYER` | `OPERATIONALIZATION / MTX ASSEMBLY LAYER` *(nova)* |
|---|---|---|
| Natureza | **seletiva** — nunca gera conteúdo novo | **geradora** — explicitamente, e governada |
| Pode | selecionar · manter ambos · `CONTEXT_SPLIT` · decidir precedência quando autorizada · escalar · deferir | compor artefato operacional novo a partir de elementos compatíveis de várias fontes + política MTX |
| Não pode | **inventar um terceiro workflow e atribuí-lo às fontes** | sintetizar sobre conflito não resolvido · atribuir a fonte o que a fonte não ensinou |
| Preserva | o que cada fonte realmente afirma; relações; corroboração; especialização; complemento; contradição; supersessão; proveniência integral | proveniência **por elemento** + identificação explícita do que é decisão MTX |
| Lê `MTX-POLICY`? | **NUNCA** (I26) | sim — é a única camada que lê |
| Determinismo | recomputável dado (pacotes, políticas, decisões) | não determinística → **computada uma vez e SELADA**, como as claims |
| Ator típico | regra · modelo · humano, por decision record | **MTX** — modelo propõe, política define quem aprova (§5.3) |

**As 7 condições da síntese viram invariantes (I22–I25 + D29):**

1. todo artefato sintetizado é marcado **`MTX_DERIVED`**;
2. **nunca** atribuído falsamente a uma fonte;
3. cada regra, passo, condição ou exceção preserva proveniência para os elementos que a sustentam;
4. conteúdo realmente novo introduzido pela MTX é identificado como **decisão/política MTX**;
5. conflito não resolvido **não é sintetizado em silêncio**;
6. síntese estrutural possui **trace próprio**;
7. a **política** determina quando aprovação humana é obrigatória.

---

## 3. QUARTO PRODUTO: `OPERATIONAL PACKAGE` — ADOTADO

**Análise pedida, resposta: SIM.** A fronteira de autoridade fica mais limpa por **três razões independentes que caem no mesmo lugar** — e quando três eixos distintos desenham a mesma linha, a linha é real:

1. **Seletivo × gerador.** O Fusion Package permanece recomputável e determinístico dado seus insumos; a geração — não determinística por medição (variância 1,5× do extractor é da mesma família) — fica **quarentenada** num pacote selado uma vez. Misturar os dois no mesmo pacote destruiria a recomputabilidade da fusão.
2. **Ator do corpus × ator MTX.** Decisões de fusão têm regime próprio (regra/modelo/humano por record); síntese e applicability têm regime MTX com aprovação por política. Regimes de aprovação diferentes → pacotes diferentes.
3. **Invalidação por corpus × invalidação por política.** Mudar a prioridade de canal da MTX **não pode** forçar re-fusão — invalida artefatos operacionais, e só. Fonte recompilada invalida fusão → cascateia. A fronteira de cache é exatamente a fronteira do pacote.

**Cadeia final de produtos (quatro, quatro selos):**

```
SOURCE PACKAGE(S)
   → FUSION
      → FUSION PACKAGE
         → OPERATIONALIZATION / MTX ASSEMBLY
            → OPERATIONAL PACKAGE          [NOVO — selado uma vez]
               → SKILL PACK
```

**Endereçamento:**
`operational_id = H( fusion_package_hash ∪ hash(MTX-POLICY vigente) ∪ hash(conjunto de APPLICABILITY_DECISIONS) ∪ hash(conjunto de SYNTHESIS_TRACES) )`

**Regra de construção (I28):** o Skill Pack constrói-se **sempre** de um Operational Package — mesmo quando nada exige síntese, caso em que o Operational Package é passagem fina (seleção dos itens `DIRECT_USE`). Um caminho só; nunca duas rotas de construção para o mesmo produto. É a mesma lição da dupla verdade, um nível acima.

**Custo declarado:** um tipo de pacote e um selo a mais. Justificado porque a alternativa — síntese dentro da fusão — quebraria a recomputabilidade e misturaria autoridades; e o caminho legado (Decisão 1) não carrega nada disso.

---

## 4. MODELO DO `MTX_DERIVED_OPERATIONAL_ARTIFACT`

```
MTX_DERIVED_OPERATIONAL_ARTIFACT          (workflow | rule | anti-pattern operacional)
  artifact_id        : hash de conteúdo
  origin             : MTX_DERIVED                  ← nunca "ensinado pela fonte X"
  applicability      : ADAPT_TO_MTX | DIRECT_USE    (estado herdado dos elementos + decisão)
  elements[]         : cada passo/regra/condição/exceção com EXATAMENTE UM de:
      claim_refs / candidate_refs : (source_package_hash, local_id)+  — o que o sustenta
      mtx_policy_ref              : decisão/política MTX que o introduziu
  synthesis_trace    : ator · data · fusion_package_hash de origem · modelo e
                       PARTIÇÃO DE CHAMADAS quando gerado por modelo (I19) ·
                       aprovação humana quando a política exigir
  open_questions[]   : conflitos DEFERRED_TO_RUNTIME carregados COMO PERGUNTAS
  approval_record    : quando a política exigir (§5.3)
```

**Exemplo conceitual (do cross-review, adotado como forma canônica):**

`MTX_WORKFLOW W1` — passo 1 ← claim/candidate da Fonte A · passo 2 ← claim/candidate da Fonte B · exceção ← Fonte C · escolha de canal ← política MTX.
**W1 não é "workflow ensinado pela Fonte A/B/C". É um `MTX_DERIVED_OPERATIONAL_ARTIFACT`** — a atribuição a fontes existe só no nível de **elemento**, apontando ids qualificados.

**Regra de compatibilidade (operacionaliza a condição 5):** elementos só são componíveis se **nenhuma** claim que os sustenta está em conflito aberto (`NOT_YET_ADJUDICATED`, `CONTRADICTS` sem decisão, `ESCALATED_TO_HUMAN` pendente). Exceção única: `DEFERRED_TO_RUNTIME`, que entra **como pergunta explícita** em `open_questions[]`, nunca como resolução implícita.

**Canários novos (§9):** artefato `MTX_DERIVED` atribuído a fonte → TEM de falhar · elemento sem proveniência nenhuma → TEM de falhar · síntese sobre conflito aberto → TEM de falhar.

---

## 5. MTX APPLICABILITY — RESTAURADA

**Omissão real da v1, assumida:** o requisito de classificação crítica do briefing inicial não sobreviveu à v1. Restaurado aqui como parte formal da arquitetura.

### 5.1 Os estados

`DIRECT_USE` · `ADAPT_TO_MTX` · `REFERENCE_ONLY` · `REJECT` — mais o default implícito **`NOT_YET_CLASSIFIED`**.

- O estado é atribuído a **claims, candidatos e artefatos derivados**, referenciados por id qualificado `(source_package_hash, local_id)` — o Source Package é **referenciado, nunca modificado**.
- **`NOT_YET_CLASSIFIED` é fail-closed (I27):** a Operationalization não consome item sem estado decidido. E a classificação é feita **sob demanda**, no momento da operacionalização — não em varredura prévia das 2.463 claims. O trabalho humano fica proporcional ao que é de fato operacionalizado. Empresa de médio porte não classifica corpus inteiro por precaução.
- `REJECT` não apaga nada: o item permanece no Fusion Package com proveniência intacta; apenas não entra em Operational Package. Rejeição é aditiva e reversível, como todo o resto.

### 5.2 Onde vivem

Como **`APPLICABILITY_DECISION`** — subtipo de `GOVERNANCE_DECISION` (§9 da v1), com tudo que o record já exige: `decision_id` · hash · **ator** · base · `mtx_policy_hash` vigente · cadeia de supersessão aditiva. Vivem no **Operational Package** (ledger de decisões consumido pela Operationalization). Auditáveis, versionadas, nunca campo mutável.

### 5.3 Quem decide

- **Modelo pode PROPOR estado; proposta não é decisão.**
- A **`MTX-POLICY`** declara a matriz de aprovação — quais estados e transições exigem aprovação humana.
- **Default inicial, até a política dizer diferente: o ator é humano MTX (Alexandre).** Coerente com a regra da casa — agente que não sabe pergunta; não inventa critério de classificação por conta própria.
- Mudança de `MTX-POLICY` → toda `APPLICABILITY_DECISION` com `mtx_policy_hash` divergente entra em fila de re-adjudicação (extensão da §13 da v1; ver §9/D34).

---

## 6. POLÍTICA DE CANAIS MTX — POSIÇÃO ARQUITETURAL

### 6.1 O artefato

**`MTX-POLICY`** — artefato **versionado e hasheado**, mesmo regime das políticas de ancoragem e precedência. Conteúdo inicial, declarado pelo dono:

1. **Instagram** — canal principal, especialmente vídeos/imagens;
2. **WhatsApp** — conversação comercial e Status;
3. **Google Ads** — mídia paga;
4. **email, SMS e voice** — normalmente implementação de referência, salvo necessidade específica.

### 6.2 A posição — e o invariante que a protege

A política é lida por **uma única camada: Operationalization**. Source Package e Fusion Layer **nunca** a leem.

> **I26 — FUSÃO É CEGA À `MTX-POLICY`.** `fusion_id` não inclui `mtx_policy_hash`. Verificação: recomputar a mesma fusão sob duas políticas distintas produz saída **byte-idêntica**. Canário: uma fusão cuja saída muda com a política TEM de falhar.

É o que garante que as prioridades da MTX **não adulteram** o que as fontes disseram nem as relações entre elas.

### 6.3 O exemplo canônico, camada por camada

| Camada | O que acontece |
|---|---|
| Fonte | ensina *"use automated email follow-up"* |
| Fusion | preserva a claim **exatamente**, com proveniência e âncora |
| Applicability | `REFERENCE_ONLY` (email é referência na política vigente) |
| Operationalization | deriva regra de follow-up contextual para **WhatsApp**, marcada **`ADAPT_TO_MTX`**, com elemento apontando a claim do email + `mtx_policy_ref` para a troca de canal |
| O que fica proibido | atribuir ao instrutor a regra de WhatsApp — ele não a ensinou |

---

## 7. CORREÇÃO `CLAIM ↔ EVIDENCE`

### 7.1 A relação nova — e o nome

O cross-review sugeriu `SEMANTICALLY_SUPPORTED_BY`. **Proposta desta v1.1: `ENTAILED_BY`**, definida assim:

> `CLAIM —ENTAILED_BY→ {EVIDENCE}` : **toda asserção da claim é sustentada pela união das suas `evidence_refs`, sem acréscimo.**

Por que `ENTAILED_BY` e não `SEMANTICALLY_SUPPORTED_BY`: *supported* tolera sustentação **parcial** — e sustentação parcial com excesso é exatamente a família de achados que o adversário mediu neste projeto (*"a claim excede o que a fonte sustenta"*: sobre-extensão, promoção de categoria, falsa explicitude). O predicado tem de ser **total**: a claim inteira segue do conjunto, ou a relação não vale. É julgamento (indecidível mecanicamente), como `SUPPORTED_BY` — e é medido como julgamento, com rubrica e variância de juiz (§7.3).

### 7.2 A cadeia de dois saltos — cada um com sua régua

```
CLAIM ──ENTAILED_BY──▶ {EVIDENCE} ──┬─ LOCATED_IN ────▶ SOURCE_ANCHOR / L0
                                    ├─ REPRODUCED_FROM ▶   (quando aplicável)
                                    └─ SUPPORTED_BY ───▶
```

- `LOCATED_IN` / `REPRODUCED_FROM` / `SUPPORTED_BY` continuam medindo **exclusivamente** `EVIDENCE ↔ SOURCE_ANCHOR` — os três números conhecidos (100% · 61,50% · 5,3%) são propriedades **desse** salto e não se movem com a camada de claim.
- Uma claim normalizada **não é obrigada a reaparecer verbatim** em lugar nenhum — verbatim é obrigação da evidência, conforme a `ANCHORING-POLICY` por tipo de âncora.
- **Validade de claim (I29):** `ENTAILED_BY(claim, evidence_set)` **∧** ancoragem das evidências no salto de baixo. Dois saltos, duas medições, **nunca colapsados num campo** — a lição dos três predicados, aplicada um nível acima.

### 7.3 Critério de morte reformulado — sem inventar número

Três gatilhos, nenhum com limiar digitado agora:

- **KILL-1 — mecânico, sem limiar (I30):** a geração de claims não altera **um byte** da camada selada abaixo. Verificação por **igualdade** de hashes de `EVIDENCE`/`ANCHORS` antes e depois. Qualquer diferença → morte imediata. (É o sucessor honesto do critério da v1: o que se protege é a camada de evidência, e igualdade não é limiar.)
- **KILL-2 — variância, contra número já MEDIDO:** conjuntos de claims de execuções independentes divergindo além da tolerância pré-declarada, com teto de referência na variância **medida** do extractor (1,5×). Referencia medição existente; não inventa nada.
- **KILL-3 — piso de `ENTAILED_BY`, declarado ANTES da rodada que o consome:** o **método** congela agora (rubrica escrita a partir das evidências · amostra pré-declarada · **variância do juiz medida antes do limiar** — a lição do teto degenerado: limiar dentro do ruído do juiz é inválido, não FAIL). O **número** entra no opening record do piloto, nunca nesta v1.1.

---

## 8. AUTORIDADES — OS QUATRO PRODUTOS

| Pacote | Natureza | Endereçamento | Autoritativo sobre | **Não** autoritativo sobre |
|---|---|---|---|---|
| `SOURCE PACKAGE` | imutável, selado | hash do conjunto | **o que a fonte afirma** | qualquer outra fonte; adequação à MTX |
| `FUSION PACKAGE` | derivado, recomputável | `fusion_id` (v1 §7.1, **sem** `mtx_policy_hash`) | **relações e decisões entre claims** | conteúdo de fonte; o que a MTX faz com isso |
| `OPERATIONAL PACKAGE` *(novo)* | gerado, **selado uma vez** | `operational_id` (§3) | **o que a MTX decidiu operar** — applicability, síntese, adaptação de canal | o que as fontes afirmam; relações do corpus |
| `SKILL PACK` | artefato de consumo | hash + `operational_package_hash` | **nada** — toda saída resolve para trás | tudo |

A cadeia de resolução fecha: saída do Skill Pack → artefato operacional → (elementos → claims/candidatos qualificados → evidence → anchor → L0) **ou** (→ `mtx_policy_ref` → decisão MTX registrada). Todo conteúdo tem exatamente uma dessas duas linhagens — a terceira opção, "veio do nada", deixa de existir por construção.

---

## 9. INVARIANTES NOVOS E ALTERADOS

I1–I20 da v1 permanecem. Acréscimos e ajustes:

| # | Invariante | Verificação |
|---|---|---|
| **I21** | `FUSION` nunca sintetiza artefato novo nem atribui composição a fontes; suas saídas são seleção · manutenção · split · precedência · escalada · deferimento | fixture de síntese na fusão TEM de falhar |
| **I22** | Síntese só em `OPERATIONALIZATION`; todo artefato sintetizado é `MTX_DERIVED` com `synthesis_trace` próprio | artefato gerado sem trace = falha |
| **I23** | Atribuição a fonte só no nível de **ELEMENTO**, por id qualificado; `MTX_DERIVED` atribuído a fonte no nível de artefato = falha | canário de atribuição falsa |
| **I24** | Todo elemento tem exatamente uma linhagem: `claim/candidate_refs` **ou** `mtx_policy_ref`; elemento órfão = falha | varredura de elementos |
| **I25** | Síntese sobre conflito aberto = falha; `DEFERRED_TO_RUNTIME` entra só como pergunta explícita | canário de conflito plantado |
| **I26** | Fusão cega à `MTX-POLICY`: mesma fusão sob duas políticas → saída byte-idêntica | recomputação sob política trocada |
| **I27** | Operationalization não consome `NOT_YET_CLASSIFIED`; fail-closed | canário de item sem estado |
| **I28** | Skill Pack constrói-se **sempre** de um Operational Package, mesmo pass-through | inspeção da cadeia de hashes |
| **I29** | Validade de claim = `ENTAILED_BY` ∧ ancoragem da evidência; os dois saltos medidos separadamente, nunca colapsados | dois campos, dois relatórios |
| **I30** | Geração (claims, candidatos, artefatos operacionais) nunca altera camada selada abaixo — igualdade de hash antes/depois | mecânico, sem limiar |
| *(alterado)* **E11** | "seleção ou escalada, nunca síntese" **com escopo: FUSION LAYER** | — fechada |
| *(alterado)* **E12** | estatuto legado preservado, recomendação (a) | — fechada |

---

## 10. DECISIONS READY TO FREEZE — LISTA FINAL

**D1–D27 da v1: mantidas integralmente** (com D27 = DESIGN C sob as três condições; a condição 3 — "seleção ou escalada, nunca síntese" — passa a valer **com o escopo da §1.2**: dentro da FUSION LAYER).

Novas:

| # | Decisão |
|---|---|
| **D28** | `E12` fechada: `LEGACY_SINGLE_SOURCE` preservado com `READY_FOR_CONTROLLED_USE — CONDICIONAL`; pilotos não passam retroativamente pela fusão; `MODULAR_SKILL_PACK` paralelo, contrato próprio |
| **D29** | `E11` fechada com escopo: fusão seletiva; síntese só em `OPERATIONALIZATION`, sob as 7 condições (I21–I25) |
| **D30** | **Quarto produto adotado: `OPERATIONAL PACKAGE`**, selado uma vez, endereçado por `operational_id` (§3); Skill Pack sempre construído dele (I28) |
| **D31** | Modelo `MTX_DERIVED_OPERATIONAL_ARTIFACT` (§4), com proveniência por elemento e regra de compatibilidade sobre conflitos |
| **D32** | MTX Applicability restaurada: `DIRECT_USE` · `ADAPT_TO_MTX` · `REFERENCE_ONLY` · `REJECT` + `NOT_YET_CLASSIFIED` fail-closed; classificação sob demanda; decisão como `APPLICABILITY_DECISION` (subtipo de `GOVERNANCE_DECISION`), versionada e aditiva |
| **D33** | Quem decide: modelo propõe, `MTX-POLICY` define a matriz de aprovação; **default inicial: ator humano MTX (Alexandre)** |
| **D34** | `MTX-POLICY` como artefato versionado/hasheado, lido só pela Operationalization; conteúdo inicial = prioridades de canal declaradas (§6.1). Invalidação estendida: política muda → `APPLICABILITY_DECISION`s e artefatos operacionais com hash divergente entram em re-adjudicação; fusão reaberta (`REOPENED_BY_NEW_SOURCE`) → artefatos operacionais que citam claims afetadas ficam flagged |
| **D35** | Relação `CLAIM —ENTAILED_BY→ {EVIDENCE}` (§7.1), total e sem acréscimo; validade de claim em dois saltos (I29) |
| **D36** | Critério de morte reformulado: KILL-1 mecânico por igualdade · KILL-2 variância contra o 1,5× medido · KILL-3 piso de entailment com método congelado agora e número no opening record — **nenhum limiar digitado nesta rodada** |
| **D37** | Autoridade de fonte **declarada externamente** no `SOURCE-PROFILE`, nunca derivada da qualidade das claims — a derivação fecha o ciclo autoridade↔precedência (Q6 da revisão), e ciclo é proibido pela família DAG |

**Permanecem deliberadamente pós-freeze, medidos e não digitados:** piso de `ENTAILED_BY` (opening record) · limiares do portão de admissão de candidatos (`MS-000B`) · poda da taxonomia e destino de `PRESUPPOSES` (`MS-001`) · tabela de reprodução por `anchor_type` (política) · enumeração de repos/refs do `DECLARATION SPACE` (configuração) · nomes de módulos · embeddings, banco vetorial, tecnologia de índice, linguagem.

---

## 11. O QUE AINDA IMPEDE O FREEZE

**Nenhum bloqueio estrutural restante.** As duas decisões que bloqueavam a v1 (§20.1 e §20.2) estão fechadas; a camada nova tem contrato, autoridade, endereçamento, invariantes e canários definidos; a correção `CLAIM ↔ EVIDENCE` remove o último critério mal calibrado.

Dois pré-requisitos **do ato de freeze e do primeiro código** — não são revisões de arquitetura:

1. **Conferência da cadeia v0 → v1 → v1.1 contra o corpus real** (nota de método mantida desde a v0: tudo foi escrito sobre a descrição transmitida, sem leitura ao vivo do repo/Drive). O freeze é selado no repo **depois** dessa conferência, e o espaço de busca inclui mensagens de commit.
2. **Extrair a taxonomia do espelho da mensagem do commit `378d764` para arquivo** — pré-requisito de qualquer script de empacotamento, já registrado na v1 e ainda pendente.

---

## 12. CLASSIFICAÇÃO FINAL

# `READY_TO_FREEZE_ARCHITECTURE`

**Por que agora e não antes:** a v0 tinha seis defeitos estruturais; a v1 tinha duas decisões abertas; **a v1.1 tem zero**. As duas foram fechadas pelo dono — uma por aceitação da recomendação (§1.1), outra por reformulação que é **melhor** que a recomendação original (§1.2): a proibição de síntese estava certa como proteção da fusão e errada como teto do sistema. Separar a camada seletiva da camada geradora, com a geradora governada, marcada e rastreada, resolve a tensão sem sacrificar nem a fidelidade ao corpus nem a utilidade operacional para a MTX — e o quarto produto dá a essa separação uma fronteira de autoridade verificável por hash.

**O que o freeze congela:** contratos e invariantes — E1–E12 (todas fechadas), I1–I30, D1–D37, os quatro produtos e suas autoridades, os dois contratos de runtime, a sequência `MS-000A → MS-000B → MS-001`.

**O que o freeze não congela, por decisão:** todo número não medido, toda ferramenta, todo nome de módulo, e a lista final de relações — que o piloto poda.

**Depois do freeze, a ordem não muda:** `PILOT-MS-000A` primeiro — custo próximo de zero, maior poder de invalidação. Se o selo não pega os seis defeitos plantados, nada acima dele vale.

---

**FIM DA v1.1. Nada implementado. Nada alterado em Git, Drive, Compiler, pilotos, N1–N9, freezes, manifests, `_mirror/`, `cts/` ou runners.**
