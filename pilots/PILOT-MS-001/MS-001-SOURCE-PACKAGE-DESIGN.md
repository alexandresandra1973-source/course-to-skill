# MS-001 — SOURCE PACKAGE + FUSION PRE-DESIGN

**Data:** 2026-08-30 · **Classe:** `GIT_NATIVE_BY_DESIGN` · **Natureza:** desenho, não execução.
**Estado:** `MS_001_EXECUTION_NOT_AUTHORIZED` · **Zero chamadas de modelo nesta rodada.**

| base normativa | sha256 |
|---|---|
| `ARCHITECTURE-FREEZE` (original, preservado) | `6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b` |
| `IDENTITY-QUALIFICATION-ERRATA-v1` | `2f8232f6c184668370ed9e440256b0de3f6ee801a7bee67285eb291c1a527ad2` |
| `DECISION-RECORD-MS-000B-FINAL-ACCEPTANCE` | `5e689af702a2c043adfa6be63e864465dc3d579dff2f2066787456c3fb13d4d8` |
| `ADDENDUM-MS-000B-CANDIDATE-PROVENANCE-CAUSE` | `e0be4ef6696e2540f1389d72135ce8b6bdc4dae489bd0f836b08d029628fbc14` |
| `MS-001-CONTROLLED-CORPUS-DESIGN-REPORT` | `23234f936efa5542257dd9d644dae2c799b71a4e8a5fe70d03cdc05a5af71d17` |
| `DECISION-RECORD-MS-001-INDEPENDENCE` | `00976ae7f7c5020a2a8bf0202e2184f7c37896e4accfee336414f4fb4e58baeb` |
| `00_SOURCE/SOURCE-MANIFEST-MS-001.yaml` | `790fe0e72a784a7f8b695345d68f850d6970844675c0bb51fff2b3dba3a5cbc0` |
| `00_SOURCE/FROZEN-SLICES.json` | `0460dd5fd0107fac5bc073c160b92b137ee17b2de9d599cae3b681fc3f7d244e` |

---

## 1. CAMADAS DE ARTEFATO

```
SOURCE                        MS001-SRC-B / MS001-SRC-C, identidade logica
  → RAW CAPTION ARTIFACT      byte-faithful, congelado, base do SOURCE_CONTENT_HASH
  → CONTROLLED SLICE ARTIFACT derivado; RESOLVE para segmentos do raw por indice
  → SOURCE_ANCHORS            spans + quote verbatim + segment ids
  → EVIDENCE                  nasce ANTES de claims/candidates
  → CLAIMS                    unidade semantica primaria de comparacao
  → SOURCE_LOCAL_CANDIDATES   com provenance criada NA PROPRIA GERACAO
  → SOURCE PACKAGE            selado
```

**O RAW CAPTION permanece byte-faithful.** A slice é representação derivada e tem de resolver
para segmentos do raw artifact pelos índices já congelados em `FROZEN-SLICES.json`.
**Cada transformação exige trace.**

## 2. `SOURCE_ANCHOR` — contrato

```
SOURCE_ANCHOR
  source_id                 MS001-SRC-B | MS001-SRC-C
  artifact_hash             sha256 do caption congelado
  video_id                  dtAoZYMEzcM | NvrBpnbNfv4
  start_s, end_s            derivados dos segmentos
  quote                     verbatim, reproduzido do artifact
  transcript_segment_ids    indices que resolvem no array original
```

**Requisitos:** `artifact_hash` aponta ao caption congelado · `transcript_segment_ids`
resolvem no array original · `start`/`end` derivam dos segmentos · `quote` é reproduzido,
nunca reescrito · **overlaps são permitidos** (propriedade da auto-caption) · ordem canônica
por `start_s` e depois índice do segmento. **O anchor não depende de texto corrigido à mão.**

## 3. `EVIDENCE` — desenho

Evidence nasce **antes** de Claims e Candidates. Preferência arquitetural: **construção
mecânica** a partir de anchors/grupos de segmento sempre que possível.

```
EVIDENCE
  local_id                  EV-nnnn, unico por (entity_kind, local_id) no package
  entity_kind               "evidence"     (para travessia de fronteira)
  source_anchor_refs        ref SELF, kind schema-implied = source_anchor
  quote / source_excerpt    verbatim do raw caption
  language                  pt
  provenance                anchor → artifact_hash → video_id
```

**Nenhum LLM inventa evidência.** A camada de Evidence é derivada dos bytes congelados.

## 4. `SOURCE-LOCAL-EXTRACTION-BUNDLE` — a chamada que cria provenance na origem

**Uma chamada de extração por slice.** Entrada: a slice + o **catálogo fechado de
`evidence_id` permitidos** + schema fechado. Saída única:

```
SOURCE-LOCAL-EXTRACTION-BUNDLE
  slice_id, source_id, evidence_catalog_hash
  raw_claims[]
     temporary_claim_id
     text
     evidence_refs[]        NAO VAZIAS, todas do catalogo
     scope / qualifiers     explicitos (plataforma, etapa, condicao, ambiente)
     language
  raw_candidates[]
     entity_kind            rule_candidate | workflow_candidate | workflow_step |
                            anti_pattern_candidate
     local_id (temporario)
     structure              campos do kind
     evidence_refs[]        NAO VAZIAS, todas do catalogo
     claim_temp_refs[]      quando aplicaveis
     conditions / exceptions / prerequisites  quando aplicaveis
     source_local_defects[]
```

> **Isto é o que fecha a limitação herdada.** A relação candidate→evidence e
> candidate→claim vem **no mesmo output source-local**, antes de existir qualquer resultado
> cross-source. Não há janela onde a provenance possa ser inventada depois.

## 5. FINALIZAÇÃO DETERMINÍSTICA DE CLAIM

Depois da chamada de extração, **mecanicamente e sem modelo**:

```
temporary_claim_id → claim normalizada → claim_id final / content identity
```

As `claim_temp_refs` dos candidates são reescritas pelo mapa
`temporary_claim_id → sealed claim_id`.

**Por que isto não é provenance retrofitting**, registrado como princípio:

1. a relação candidate→claim **já veio** no output source-local;
2. **apenas o identificador temporário** é substituído;
3. **nenhuma relação cross-source existe ainda** — a Fusion nem começou.

Retrofitting seria *criar* a relação depois de ver o resultado. Aqui a relação preexiste ao
resultado; só o rótulo muda.

## 6. `CANDIDATE-PROVENANCE-GATE`

Antes de o Source Package poder ser selado, todo candidate é avaliado:

```
candidate → evidence_refs → SOURCE_ANCHOR → RAW CAPTION
candidate → claim_refs    → evidence            (quando aplicavel)
```

| estado | condição |
|---|---|
| `ELIGIBLE_FOR_CROSS_SOURCE_DECISION` | cadeia completa e resolvida |
| `NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION` | `evidence_refs = []` |
| `INVALID_PROVENANCE` | ref presente que não resolve, ou cadeia que não alcança anchor/raw |

**Regra dura:** `evidence_refs = []` → `NOT_ELIGIBLE`. **Nunca aceitar por vacuidade.** Foi
exatamente a vacuidade que a Round 3 do MS-000B produziu, e a policy `v0.1` teve de tratá-la
como medida em vez de rejeição porque 147/147 estavam vazios. Aqui o bundle garante refs
não vazias na origem, então a regra pode ser **dura desde o começo**.

## 7. `CP1–CP6`

| canário | fixture | esperado |
|---|---|---|
| `CP1` | candidate real com evidence ref válida | `ELIGIBLE` |
| `CP2` | evidence ref inexistente | `INVALID_PROVENANCE` |
| `CP3` | `evidence_refs` vazias | `NOT_ELIGIBLE` |
| `CP4` | claim ref quebrada | `INVALID_PROVENANCE` |
| `CP5` | evidence que não alcança anchor/raw | `INVALID_PROVENANCE` |
| `CP6` | cadeia completa resolvida | `ELIGIBLE` |

`CP1`/`CP6` terão fixture **real** do corpus compilado; `CP2`–`CP5` sintéticos, plantados
fora do corpus. O Opening Record do MS-001A deve conter todos os seis.

## 8. IDENTIDADE TIPADA

Normativa, pela errata:

```
GLOBAL_OBJECT_IDENTITY = (source_package_hash, entity_kind, local_id)
```

Dentro do package, `(entity_kind, local_id)` **único**. **Nunca indexar por `local_id`
sozinho** — defeito que reincidiu três vezes no código do MS-000B.

`entity_kind` canônicos aplicados desde o desenho: `artifact` · `source_anchor` ·
`evidence` · `claim` · `rule_candidate` · `workflow_candidate` · `workflow_step` ·
`anti_pattern_candidate`.

Refs `SELF` compactas **somente** quando o schema implica o kind inequivocamente
(`claim.evidence_refs → evidence`, `evidence.source_anchor_refs → source_anchor`,
`source_anchor.artifact_ref → artifact`). `SELF` genérica sem kind determinado é
`INVALID_REF`.

## 9. `SOURCE-PROFILE` — só fatos da fonte

Inclui: `SOURCE_ID` · `SOURCE_CONTENT_HASH` · `video_id` · URL canônica · autoridade/uploader
· `channel_id` · idioma · `caption_type` · `media_type` · `source_boundary` · cadeia de
proveniência · `source_independence_state: DECLARED_INDEPENDENT` com referência ao
`DR-MS-001-INDEP-001`.

**NÃO inclui** — pertence ao `COMPILE-TRACE`: modelo · prompt · juiz · config de thinking ·
timestamps operacionais · partição experimental.

## 10. MEMBER SET — confrontado com a lista autoritativa

Confrontei a enumeração recebida com a fonte autoritativa (o `REQUIRED_MEMBERS` aceito do
MS-000B, nomenclatura literal da v1 §4.1) e registro **duas divergências**:

| # | membro (nome literal) | caminho no MS-000B | caminho no MS-001 |
|---|---|---|---|
| 1 | `SOURCE-PROFILE` | `SOURCE-PROFILE.json` | idem |
| 2 | `L0` | `L0/CHAPTER-SLICE.txt` | **`L0/CONTROLLED-SLICE.txt`** |
| 3 | `ARTIFACTS` | `ARTIFACTS/ARTIFACT-INDEX.json` | idem |
| 4 | `SOURCE_ANCHORS` | `SOURCE-ANCHORS.jsonl` | idem |
| 5 | `EVIDENCE` | `EVIDENCE.jsonl` | idem |
| 6 | `CLAIMS` | `CLAIMS.jsonl` | idem |
| 7 | `SOURCE_LOCAL_CANDIDATES` | `SOURCE-LOCAL-CANDIDATES.json` | idem |
| 8 | `COMPILE-TRACE` | `COMPILE-TRACE.jsonl` | idem |
| 9 | `LOCAL-COHERENCE-REPORT` | `LOCAL-COHERENCE-REPORT.json` | idem |
| 10 | `DECLARATION-SPACE-INDEX` | `DECLARATION-SPACE-INDEX.json` | idem |
| 11 | `SEAL-RECORD` | `SEAL-RECORD.yaml` | idem |
| — | `TOOLCHAIN` | `TOOLCHAIN.json` | idem — artefato do **produtor**, não 12ª categoria de conteúdo |

**Divergência 1 — `L0`.** O nome do membro é `L0` e permanece. O **caminho**
`L0/CHAPTER-SLICE.txt` é herança do escopo `SOURCE = chapter`, que **encerrou no MS-000B**.
Para MS-001 a fonte é vídeo e a unidade é slice controlada; proponho
`L0/CONTROLLED-SLICE.txt`. É mudança de caminho, **não** de contrato: o membro literal
continua `L0`.

**Divergência 2 — "membership/manifest".** A enumeração recebida lista *membership/manifest*
como membro. Na lista autoritativa **não é um arquivo membro**: o `member_manifest` é
**computado** dos membros e **exclui o `SEAL-RECORD`** (condição 7 de `SEALED` — nenhum
membro se auto-referencia). Registrado para não ser implementado como arquivo.

## 11. `LOCAL-COHERENCE-REPORT` — mecânico, antes do selo

Verifica: membros obrigatórios · **unicidade de `(entity_kind, local_id)`** · resolução de
refs · **candidate provenance** · claims duplicadas pela regra local · workflows
estruturalmente válidos · workflows vazios · ordenação inválida · condições/refs quebradas ·
defeitos declarados.

**Não é** coerência semântica cross-source. O relatório carrega o marcador explícito, como no
MS-000B.

## 12. SELO — ciclo de vida, sem invenção

Reusa o contrato aceito de MS-000A/MS-000B. **Nada novo.** Um Source Package só é válido após:

```
completeness → local coherence → member manifest → package hash
             → SEAL-RECORD → external seal registry
```

O verificador é o `seal_verifier.py` já aceito
(`63cfe229de85713a2717b2d9cd3cd6d49de871b10bad255284af379259dc717f`), reusado sem alteração.

## 13. MS-001A — SOURCE PACKAGE COMPILATION

**Objetivo:** produzir **exatamente dois** Source Packages, B e C, cada um compilado **uma
vez** a partir das **três slices congeladas**.

Testa: anchors · evidence · claims · **candidate provenance** · local coherence · selo.

**Nenhuma relação cross-source. Nenhuma Fusion.**

**Orçamento preliminar:** **6 chamadas de extração**, uma por slice.

**Controles do schema de extração — decisão registrada:** os controles de *forma*
(campos obrigatórios, refs não vazias, refs dentro do catálogo, kinds canônicos, unicidade
tipada, JSON parseável) são **inteiramente mecânicos, zero modelo** — são predicados sobre o
output, não sobre o julgamento. **Uma** chamada de controle de modelo passa a ser necessária
apenas se o Opening Record exigir provar que o extrator **recusa** produzir claim sem
evidence quando instruído a tal — um controle negativo de comportamento, não de forma. Deixo
a decisão registrada como **OPEN**, com a recomendação de que **não seja necessária**: o
portão mecânico já rejeita o bundle malformado, e um bundle rejeitado é resultado, não falha.

## 14. MS-001B — FUSION RELATION EXPERIMENT

**Só começa** depois que B e C estiverem completos, selados e aceitos no gate intermediário.
Os **mesmos dois package hashes ficam fixos para todas as runs da Fusion** — é isso que
isola a variância do juiz semântico da variância da compilação source-local.

## 15. CAMADA DE COMPARAÇÃO

`CLAIM = primary semantic comparison unit`. Candidates **não** substituem Claims como
unidade universal. A camada de candidate preserva estruturas — sequência, condições,
exceções, pré-requisitos, defeitos, proveniência — e pode **receber e transportar**
resultados quando a relação for aplicável.

## 16. TAXONOMIA EXPERIMENTAL DE RELAÇÕES

| label | direção | simetria | requisito de escopo | governança |
|---|---|---|---|---|
| `IDENTICAL` | — | **simétrica** | escopos **compatíveis**; vocabulário igual com escopo incompatível **não** é `IDENTICAL` | nenhuma |
| `CORROBORATES` | — | **simétrica** | escopos compatíveis | nenhuma |
| `SPECIALIZES` | **A → B** | **assimétrica** | escopo de A **contido** no de B | nenhuma |
| `CONTRADICTS` | — | **simétrica** | **mesmo objeto + mesma condição + mesmo escopo relevante** | abre estado de conflito |
| `SUPERSEDES` | **A → B** | **assimétrica** | eixo temporal/versão **explícito** | abre estado de conflito |
| `UNRELATED` | — | **simétrica** | ausência de asserção; é o **default** | nenhuma |
| `INDETERMINATE` | — | **simétrica** | evidência insuficiente para decidir | vai a `open_questions` |

`PRESUPPOSES`: **`OPEN / NOT_REQUIRED`.** Não se torna obrigatória sem evidência.

**Nenhuma label determina precedência automaticamente.** Eixo A (semântico) e eixo B
(governança/precedência) permanecem separados: `CONTRADICTS` diz *que há conflito*, nunca
*quem vence*.

## 17. CONTRADIÇÃO REAL NÃO É CRITÉRIO DE APROVAÇÃO

```
REAL_CORPUS_CONTRADICTS_COUNT MAY BE ZERO
```

O MS-001 **não falha** se o caso VPS × local resultar em `SPECIALIZES`, `INDETERMINATE` ou
outra relação coerente. **Não existe** o requisito `REAL_CORPUS_MUST_PRODUCE_CONTRADICTS`.

O juiz, entretanto, **tem de passar um controle sintético pré-declarado de contradição
verdadeira** (`J4`). É o que impede fabricar resultado no corpus real para provar poder
discriminante.

### Propriedades observadas do corpus — **não são relações julgadas**

| propriedade | estado |
|---|---|
| `GENUINE_OVERLAP_CANDIDATE_PRESENT` | **SIM** — instância/sessão Evolution API para WhatsApp |
| `SCOPE_DIFFERENCE_CANDIDATE_PRESENT` | **SIM** — B outbound/admin × C inbound/reply |
| `SPECIALIZATION_CANDIDATE_PRESENT` | **SIM** — Claude Code × n8n como orquestrador |
| `TRUE_CONFLICT_CANDIDATE_PRESENT` | **SIM** — onde rodar a Evolution API |

**Nenhuma relação final foi decidida.**

### Localização dos candidatos no microcorpus congelado — medida, não ajustada

| candidato | lado B | lado C |
|---|---|---|
| **true conflict** (VPS 24h × script local) | `SL-B-01` seg 34/37/38 ✔ | **FORA** — seg 11/12 em 22–24 s, antes de `SL-C-01` |
| **false conflict** ("chave de API") | `SL-B-03` seg 151 ✔ | `SL-C-01` seg 38 ✔ |
| **unrelated** | `SL-B-02` seg 72 ✔ | `SL-C-03` seg 97/105/110 ✔ |
| **genuine overlap** (instância/sessão) | `SL-B-03` seg 157/159 ✔ | `SL-C-02` seg 80 · `SL-C-03` seg 99/106 ✔ |

> **O lado C do candidato a conflito verdadeiro caiu FORA do microcorpus congelado**, e eu
> **não adicionei slice para capturá-lo** — o §8 proíbe selecionar slice por conter conflito,
> e a proibição vale principalmente quando é inconveniente. Consequência registrada:
> `TRUE_CONFLICT_CANDIDATE_PRESENT` vale para o **corpus**, não para o **microcorpus 3+3**.
> No microcorpus, o par de conflito só existirá se a compilação produzir, do lado C, uma
> claim sobre onde rodar a Evolution API a partir de `SL-C-01`, que fala de instalar Redis
> na VPS. Pode não produzir. **Isso é resultado válido**, pelo item acima.

## 18. CONTROLES REAIS DO CORPUS — congelados como candidatos

**`FALSE-CONFLICT CANDIDATE`** — "chave de API" com objetos diferentes: em B a *global API
key da Evolution API* (`SL-B-03`, seg 151); em C a *chave do Groq/OpenAI* (`SL-C-01`,
seg 38).

```
MUST_NOT_BE_CLASSIFIED_AS_IDENTICAL_OR_CONTRADICTS_MERELY_FROM_SHARED_WORDING
```

A relação final continua para o instrumento apropriado. A restrição é sobre o **motivo**, não
sobre o rótulo.

**`UNRELATED CANDIDATE`** — B *"os tipos de servidores, dois, quatro, oito"* (`SL-B-02`,
seg 72) × C *"os campos: quem mandou, a instância que recebeu"* (`SL-C-03`, seg 97).
Localização registrada **antes** de qualquer geração de Claims.

> **Este par não pode ser usado para ajustar o blocker depois da execução.** Registrá-lo
> agora é o que impede isso.

## 19. `CLAIM_BLOCKER = NOT_YET_QUALIFIED`

O teste sobre transcrição bruta **não serve como prova** — o topo do ranking foi dominado por
registro procedural (`clica`, `coloca`, `criar`, `nome`), casando *"criar uma instância do
WhatsApp"* com *"criar uma chave de API do Groq"*.

O blocker futuro opera sobre **Claims seladas dos dois Source Packages**. Requisitos:
determinístico · auditável · controles positivos · controles negativos/unrelated ·
sensível a escopo quando possível · redução mensurável · **não usar apenas vocabulário
procedural** · **nenhuma escolha de threshold depois de ver as relações do juiz**.

## 20. `BLOCKER CALIBRATION GATE` — etapa mecânica separada

Depois de MS-001A produzir os packages selados, e **antes de qualquer juiz semântico real**:

**Pode usar:** Claims seladas · controles pré-declarados · os candidatos de sobreposição e o
par unrelated **já identificados e localizados acima**.
**Não pode usar:** relações produzidas pelo juiz · resultado desejado · `CONTRADICTS` real
conhecido posteriormente.

Se o blocker não retiver a sobreposição positiva sem explosão:

```
MS_001_BC_CORPUS_REJECTED_AFTER_CLAIM_COMPILATION
```

**Isso continua sendo resultado válido**, e é o mesmo desfecho que o corpus preservado teve.

## 21. JUIZ SEMÂNTICO — a fixar **antes** da execução do MS-001B

modelo · **id de modelo exatamente resolvido** · thinking · versão/hash do prompt · JSON
schema · tamanho de lote · controles · `INDETERMINATE` · persistência · Compile/Fusion Trace ·
call cap.

**Determinismo de bytes NÃO é assumido.** Saídas julgadas são persistidas com trace e policy.

**Três runs avaliativas independentes** sobre **os mesmos pares bloqueados dos mesmos dois
Source Packages selados**. **Claims não são regeneradas entre runs.**

## 22. CONTROLES DO JUIZ

| # | controle |
|---|---|
| `J1` | `IDENTICAL` positivo |
| `J2` | `CORROBORATES` |
| `J3` | `SPECIALIZES` |
| `J4` | **`CONTRADICTS` verdadeiro — sintético, pré-declarado** |
| `J5` | `SUPERSEDES` / versão |
| `J6` | `UNRELATED` |
| `J7` | `INDETERMINATE` |
| `J8` | falso conflito por vocabulário igual / objeto diferente |
| `J9` | diferença de escopo |
| `J10` | mesma substância em formulação ou língua diferente, quando aplicável |

## 23. FUSION PACKAGE — MS-001B

Membros: dois `source_package_hash` participantes · refs **tipadas** · elegibilidade de
Candidate Provenance · blocker trace · conjunto de pares bloqueados · julgamentos de relação
persistidos · estado de relação semântica · **estado de governança separado** · conflitos ·
conflitos não resolvidos · estruturas source-local transportadas · provenance ledger ·
Fusion Config · Fusion Trace · `fusion_id` · open questions.

**Zero MTX-POLICY. Zero Operationalization.**

## 24. IDENTIDADE INCREMENTAL

```
fusion_input_identity = source_package_hash_B + source_package_hash_C
                      + fusion_config_hash + semantic_policy_hashes
```

Canários futuros: mesmos packages e config → mesma input identity · package muda → invalida ·
semantic policy muda → invalida · **MTX policy muda → NÃO invalida a Fusion** (`I26`).

## 25. KILL CONDITIONS

`K1`–`K10` preservados do Pre-Design, mais:

| # | condição | verificação |
|---|---|---|
| `K11` | raw caption reaquirido com bytes diferentes após o freeze | comparar `SOURCE_CONTENT_HASH` antes/depois; a declaração de independência não se transfere |
| `K12` | candidate provenance criada só depois do resultado de relação | o bundle §4 torna impossível por construção; verificar ordem no `COMPILE-TRACE` |
| `K13` | threshold do blocker escolhido usando saídas do juiz | `BLOCKER CALIBRATION GATE` roda antes do juiz e é commitado antes |
| `K14` | Source Packages regenerados entre runs da Fusion | igualdade de `source_package_hash` em todas as runs |
| `K15` | ref cross-source sem identidade tipada | varredor que falha em qualquer ref não tipada |

Cada uma exige fixture ou verificação correspondente no Opening Record.

## 26. DECISÕES FECHADAS NESTE DESIGN

1. `SOURCE_ID` congelados · 2. `SOURCE_CONTENT_HASH` congelados · 3. conjunto exato 3+3 ·
4. declaração de independência · 5. cadeia de artefatos · 6. construção de Evidence ·
7. schema do extraction bundle · 8. Candidate Provenance · 9. identidade tipada ·
10. member set confrontado com a fonte autoritativa · 11. local coherence · 12. ciclo do selo ·
13. split MS-001A/MS-001B · 14. taxonomia experimental · 15. não-requisito de contradição real ·
16. procedimento de calibração do blocker · 17. desenho dos controles do juiz ·
18. isolamento multi-run · 19. desenho do Fusion Package · 20. `K1`–`K15`.

## 27. CONTINUAM `OPEN`

modelo exato · prompt exato · thinking · densidade real de claims · threshold real do blocker ·
volume real de pares · call cap final do juiz · necessidade de uma chamada de controle de
modelo no MS-001A.

**Nenhum threshold é fixado aqui. Nenhum Opening Record é escrito.**
