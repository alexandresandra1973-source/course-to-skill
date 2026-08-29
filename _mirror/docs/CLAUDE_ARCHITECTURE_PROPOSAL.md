# CLAUDE_ARCHITECTURE_PROPOSAL — Course-to-Skill

**Fase 3 — Proposta de arquitetura.** Entradas: `PROJECT_INVENTORY.md`, `INVENTORY_DELTA_v0.1.1.md`, `ARCHITECTURE_REVIEW.md`.
**Data:** 2026-08-10 · **Baseline congelado:** `BASELINE_MANIFEST_20260810.txt` (257 arquivos, sha256+bytes+mtime; 0 alterados desde a Fase 1; 28 novos vindos da esteira paralela).
**Escopo:** desenho. **Nenhum código, nenhuma implementação, nenhum arquivo original tocado.**

Cada decisão desta proposta tem uma ADR em `docs/adr/`. Onde não sei, está escrito **EM ABERTO** com o que decidiria.

---

## 0. O DIAGNÓSTICO EM UMA FRASE

Medido nas três fases: **o projeto tem um bom modelo de dados, um bom crítico, e nenhum referente externo.** Todos os defeitos graves — provenance auto-referencial, rubrica circular, caso "cego" que é recall, rótulos degenerados — são a mesma falha vista de ângulos diferentes: **as verificações fecham contra o artefato que deveriam verificar.** A arquitetura abaixo é, essencialmente, a introdução de um referente externo imutável (L0 endereçado por conteúdo) e a reordenação do que acontece antes dele ser lido.

A tabela que mais informou o desenho — dispersão dos campos de classificação do PILOT-001, calculada nesta fase:

| Campo | N | k | distintos | H (bits) | H normalizada | Estado |
|---|---:|---:|---:|---:|---:|---|
| `category` (evidência) | 44 | 14 | 12 | 3,291 | **0,864** | OK |
| `evidence_strength` | 44 | 5 | 3 | 0,789 | 0,340 | NEAR_COLLAPSED |
| `autonomy.level` (ADR) | 8 | 4 | 2 | 0,544 | 0,272 | NEAR_COLLAPSED |
| `origin_class` (evidência) | 44 | 3 | **1** | 0 | **0** | **COLLAPSED** |
| `origin_class` (ADR) | 8 | 2 | **1** | 0 | **0** | **COLLAPSED** |
| `status` (evidência) | 44 | 5 | **1** | 0 | **0** | **COLLAPSED** |
| `status` (ADR) | 8 | 5 | **1** | 0 | **0** | **COLLAPSED** |
| `confidence.level` | 44 | 3 | **1** | 0 | **0** | **COLLAPSED** |
| `rationale.state` (ADR) | 8 | 4 | **1** | 0 | **0** | **COLLAPSED** |
| `promotion_level` (ADR) | 8 | 3 | **1** | 0 | **0** | **COLLAPSED** |

**8 de 10 campos carregam 0 bits ou quase.** E o padrão não é aleatório: o **único** campo saudável (`category`, H_n = 0,864) é o único que descreve **o que o conteúdo é** — derivável de traço textual observável. Os 7 colapsados são todos **juízos sobre o estado epistêmico da evidência**, sem regra de derivação. Exatamente os campos que deveriam exercer o controle epistêmico são os que não têm informação nenhuma. Esse achado é a base de **R2** e da ADR-0005.

---

## 1. PRINCÍPIOS DE DESENHO (cada um amarrado a uma restrição medida)

| # | Princípio | Restrição | Achado que o originou |
|---|---|---|---|
| P1 | **Todo check ancora fora do que verifica.** A cadeia de referência termina em bytes de L0. | R1 | `validate_generated_skill.py` linhas 92–101: `union(EV usados) ⊆ union(EV no evidence-map)`, ambos escritos pelo mesmo compilador. `evidence.jsonl` não é lido nem empacotado. |
| P2 | **Rótulo só existe com (i) regra de derivação a partir de fato contável e (ii) consumidor cujo comportamento muda.** Sem isso, o campo é removido. | R2 | `confidence.score` = 1 valor em 44; `origin_class` = 1 valor em 44 e em 8. Tabela §0: 7 campos com 0 bits. |
| P3 | **Held-out é cortado em L0, antes de qualquer extração**, por sorteio com semente, e removido fisicamente do corpus entregue ao extrator. | R3 | TEST-0009 rotulado `BLIND_EVALUATION` é `EV-0027`, fonte 08:05–08:20. `held-out-registry`: `created_before_modeling: false`, `cases: []`. |
| P4 | **Empacotar é função pura.** Depois do Packager há portão, não só antes: o conjunto de afirmações do artefato compilado tem de ser subconjunto do que sobreviveu à auditoria. | R4 | SC-001: o compilador adicionou níveis AUTO/REVIEW/APPROVAL em 5 ADRs *não ensinados*. O gate existente (`skill-compiler.md` §2) só olha `audit_decision.status`, antes. |
| P5 | **Teto de maturidade é função do corpus** e é recusado quando a base não sustenta. | R5 | 0 casos held-out; `minimum_decision_accuracy: 0.85` sobre `input_case` n=1 por teste; ainda assim compilou a S3. |
| P6 | **Métrica sem definição computável não é métrica.** Escala única [0,1]. | R6 | 4 de 6 `comparison_metrics` sem critério de rubrica; colisão `0.85` (0–1) vs `minimum_score: 85` (0–100) para o mesmo nome. |
| P7 | **O adversário é componente, não revisão.** Mantido e promovido a portão bloqueante legível por máquina. | — | Único componente com valor medido: 6/6 correções verificadas nos arquivos, produzidas **sem** ler L0. |

---

## 2. COMPONENTES

Notação de estágio: **V** (vault), **C** (cutter), **R** (rubric), **E** (extractor), **N** (consolidator), **A** (adversary), **P** (packager), **J** (judge/evaluator).

### V — Source Vault  · **NOVO**
**Responsabilidade.** Armazenar L0 imutável, endereçado por conteúdo, e resolver *spans*.
**Contrato de saída.** `vault/objects/<sha256>` + `vault/manifest.jsonl` (`path, sha256, bytes, mime, media{duration, marks[]}`).
**Endereçamento de span** — o átomo de referência de toda a arquitetura:
```
L0:<sha256[:12]>:c=<char_ini>-<char_fim>      texto
L0:<sha256[:12]>:t=<hh:mm:ss>-<hh:mm:ss>      mídia temporal
L0:<sha256[:12]>:frame=<sha256[:12]>          imagem/quadro
```
**Impede.** Provenance auto-referencial (F.2) e ausência de âncora lexical (F.11).
**Prova de funcionamento.** `span_resolve(span) → bytes ≠ ∅` para 100% dos spans citados em qualquer artefato. Regressão disponível hoje: dos 94 timestamps do PILOT-001, **93 resolvem e 1 não** (`EV-0001`, `end 00:00:29`, ausente das 180 marcas do transcript). Esse é o fixture negativo real: se o gate não reprovar `EV-0001`, o gate está quebrado.

### C — Corpus Cutter / Held-out  · **NOVO**
**Responsabilidade.** Segmentar L0 em unidades portadoras de decisão e sortear o held-out **antes** de qualquer leitura extrativa.
**Contrato.** `corpus/<course>/segments.jsonl` (span + rótulo estrutural derivado de marcas de tempo/capítulos, sem julgar conteúdo) → `holdout/<course>.lock` (`seed`, `rate`, `spans[]`, `sha256_do_conjunto`, `sealed_at`) → `corpus/<course>/train.jsonl` = segments − holdout.
**Impede.** Rotulagem retroativa de held-out (`created_before_modeling: false`); TEST-0009 como falso caso cego.
**Prova.** (i) `sha256(train) ≠ sha256(segments)`; (ii) `holdout_leak = |{spans citados por qualquer artefato} ∩ {spans do lock}| == 0`. Aplicado ao PILOT-001 hoje, `holdout_leak` seria indefinido porque `cases: []` — e é justamente isso que o gate G1 passa a proibir.
**Granularidade.** Corte por **span decisório**, não por aula: medido, a aula tem **1 caso ponta-a-ponta (82 s, 9,1%)** e **14 ramos condicionais**; corte por aula é impossível nesta escala.

### R — Rubric Author  · **NOVO**, executa em L0 antes de E
**Responsabilidade.** Escrever a rubrica e os prompts de caso **só a partir de L0**, e selar por hash.
**Contrato.** `rubric/<course>.lock`: para cada caso — `prompt`, `expected_label` (conjunto fechado), `required_asks[]`, `allowed_spans[]`, `forbidden_behaviors[]`, `weights`. Tudo citando `L0:`.
**Restrição verificável.** `grep -E '(ADR|WF|EV|CLAIM|RULE)-[0-9]{4,}' rubric/*.lock` deve retornar **0**. Hoje o equivalente retorna 10/10 (`source_scope` inteiramente em IDs internos).
**Impede.** Avaliação circular (10/10 `evaluator_instructions` = *"Avaliar somente contra a metodologia extraída do PILOT-001"*).
**Prova.** O lock é anterior por hash ao primeiro artefato de E; e o grep de IDs internos é vazio.

### E — Extractor  · **MANTIDO** (endurecido)
**Medição que sustenta manter.** L1 produziu **100% do conteúdo decisório**: 44 evidências, 8 ADRs, 1 workflow, 6 princípios, 7 anti-padrões, 10 perguntas, 3 ferramentas, com **0 erros de schema**. O diff campo a campo L1→L3 nos 8 ADRs mostra **1 único campo alterado** (`autonomy`). O extrator é o motor real.
**Mantido também o passe único** decision+workflow+principle — H6 caiu: `lesson-analyzer.md` §10 já executa PASS 3/4/5 no mesmo prompt, e funcionou.
**Endurecimento — a tripla obrigatória.** Todo registro de afirmação carrega:
```
span   : endereço L0 (obrigatório)
quote  : bytes verbatim, no idioma da fonte, extraídos daquele span (obrigatório)
claim  : a afirmação modelada, no idioma de trabalho (obrigatório)
```
`quote` tem de ser **substring byte-exata** de `span_resolve(span)` após normalização de espaço. Hoje `source_excerpt` está em **0/44** e fonte (EN) e observação (PT) não compartilham nenhuma sequência literal — não existe verificação lexical possível. Com a tripla, existe.
**Limite declarado.** A tripla entrega **ancoragem**, não **fidelidade**: prova que a string existe em 08:05, não que a `claim` decorre dela. Essa segunda camada é do adversário (A) e permanece juízo. Vender âncora como solução de alucinação repetiria o erro de `SKILL.md` §13.

### N — Consolidator  · **REBAIXADO a função condicional**
**Medição.** Em escopo de aula única, L2+L3 alteraram **1 campo em 8 registros**, e a alteração foi ordenada pelo adversário, não gerada pelo modelador. Além disso o modelador não entregou 4 dos 11 arquivos que seu próprio §5 prescreve.
**Regra nova.** N **só executa com corpus > 1 aula**, e sua saída é um **diff explícito** contra E, nunca uma reescrita. Diff vazio é registrado como resultado, não escondido.
**EM ABERTO.** Se N se paga em escala de módulo. **O que decidiria:** medir `|diff(E, N)|` em corpus de ≥5 aulas — se o diff continuar em unidades de campo, N é overhead e deve ser absorvido por E.

### A — Adversary  · **MANTIDO e PROMOVIDO**
**Medição que sustenta manter.** v1: 3 HIGH + 3 MEDIUM; v2: 1 HIGH + 2 MEDIUM; v3: 0/0/0 — e **6 de 6 correções verificadas nos arquivos** (autonomy 0/8→7/8 UNDEFINED; `max_iterations` 5→null; 10 perguntas→MODEL_INFERENCE; princípios 7→6 + `structures`; HC-002 APPROVAL→REVIEW; `stop_conditions` 4→2). Tudo isso **sem acesso a L0** — razão pela qual H5 caiu.
**Promoção.** Saída passa a ser legível por máquina e **consumida pelo build** (hoje o `skeptic-review.yaml` não é lido por código nenhum; as correções foram aplicadas à mão). Mapeamento severidade→ação, que é o consumidor exigido por R2:
```
CRITICAL → build FAIL
HIGH     → build FAIL
MEDIUM   → build WARN + exige waiver assinado com justificativa e span
LOW      → registra
```
**Correção de contrato.** Hoje produziu **1 dos 7** arquivos prescritos por `skeptic-critic.md` §5. Passa a ter contrato único e verificado: `audit/findings.jsonl` + `audit/decision.json`.
**Entrada.** Recebe E completo (com `quote`), **não** L0 — conforme a refutação de H5. Recebe também o resultado dos gates G2/G3, para atacar onde a máquina já suspeita.

### P — Packager  · **IMPROVE + portão depois**
**Responsabilidade.** Função pura: seleciona, formata e empacota. **Não cria conteúdo.**
**Verificação (R4).** `claims(bundle) ⊆ claims(pós-A)` como conjunto de hashes de texto normalizado. Diferença não vazia = `COMPILER_INVENTION`, build FAIL.
**Medição que justifica.** SC-001: o compilador inseriu governança em 5 ADRs. O portão existente é **antes** dele.
**Contrato de saída.** O bundle passa a levar `provenance/claims.jsonl` — os registros completos com `span`+`quote`, não um mapa de IDs. Hoje `evidence-map.jsonl` tem 5 campos só-de-ID e `evidence.jsonl` **não viaja** (14 arquivos no pacote, nenhum é ele). Custo medido: `evidence.jsonl` = 72.414 B contra bundle de ~68,5 KB — o pacote dobra. Aceitável.

### J — Judge / Evaluator  · **contrato REPLACE, componente EM AVALIAÇÃO**
**Estado medido.** **Nunca executou**: 9 métricas em `null`, `evaluation.status: NOT_YET_VALIDATED`, 0 arquivos de resultado. Por isso o componente não é classificado como REPLACE — não há observação de comportamento. O que é substituído é o **contrato**.
**Entrada.** `rubric/<course>.lock` + saídas brutas do candidato. **Não** lê o bundle compilado. Hoje `evaluator.md` §4 recebe `generated-skill/` e tem **0 ocorrências** de `transcript`/`vídeo`/`fonte original` em 1.616 linhas.
**Saída.** `runs/<run_id>/scores.json` com as métricas de §5, mais os outputs brutos preservados.

---

## 3. FLUXO E PORTÕES

```
        ┌─ V  Vault (sela L0) ──────────────────── G0 vault-seal
        │
        ├─ C  Cutter ── holdout.lock ──────────────G1 holdout-lock      ─┐ ambos
        │                                                                │ ANTES
        └─ R  Rubric Author (lê só L0) ── rubric.lock                    │ de E
                                                                        ─┘
   corpus/train  ──►  E  Extractor  ──► claims.jsonl
                                          │
                                          ├──────────────────────────── G2 anchor
                                          ├──────────────────────────── G3 dispersion
                                          ▼
                              [N Consolidator]  (só se corpus > 1 aula; emite diff)
                                          ▼
                                     A  Adversary  ─────────────────── G4 adversary
                                          ▼
                                     P  Packager   ─────────────────── G5 closure
                                          ▼
                                     bundle/  ────────────────────────  G6 ceiling
                                          ▼
                       J  Judge  (lê rubric.lock, não lê bundle) ────── G7 evaluation
```

| Gate | Onde | O que verifica | Falha medida que impede |
|---|---|---|---|
| **G0** vault-seal | após ingestão | todo objeto com sha256; manifesto selado | nenhuma âncora estável |
| **G1** holdout-lock | após C, **antes de E** | lock existe, selado, `sha256(train) ≠ sha256(segments)` | `created_before_modeling: false`; TEST-0009 |
| **G2** anchor | após E | 100% das afirmações com `span` que resolve **e** `quote` substring byte-exata | `source_excerpt` 0/44; EV-0001 `00:00:29` |
| **G3** dispersion | após E | nenhum campo COLLAPSED (ver §4) | 7 campos com 0 bits |
| **G4** adversary | após A | zero CRITICAL/HIGH em aberto; MEDIUM com waiver | achados existiam mas não bloqueavam por código |
| **G5** closure | após P | `claims(bundle) ⊆ claims(pós-A)`; `holdout_leak == 0`; rubrica sem ID interno | SC-001 (invenção pós-auditoria); vazamento semântico 10/10 |
| **G6** ceiling | antes de publicar maturidade | nível declarado ≤ teto suportado pelo corpus (§6) | compilou a S3 com 0 held-out |
| **G7** evaluation | após J | métricas de §5 computadas; limiares aplicados; margem sobre baseline | 9 métricas `null` |

**Onde o PILOT-001 pararia hoje, se rodasse nesta arquitetura: em G2.** `quote` está vazio em 44/44 — não alcançaria nem S1. Isso não é crítica ao piloto; é a demonstração de que o gate discrimina.

---

## 4. DEGENERAÇÃO POR DISPERSÃO — definição computável (H7 caiu na métrica)

H7 propunha um gate de **densidade metodológica**. Refutado por medida: a aula tem 2,9 evidências/min, 8 ADRs e 14 ramos em 14,75 min — **passaria** em qualquer limiar razoável de densidade, e passou por todos os gates existentes até S3. A patologia não é escassez, é **ausência de informação nos rótulos**.

**Definição.** Para um campo categórico `F` de domínio `D` (|D| = k) observado em `N` registros, com contagens `n_v`:

```
distinct(F) = |{v : n_v > 0}|
H(F)        = − Σ (n_v/N) · log₂(n_v/N)
H_norm(F)   = H(F) / log₂(k)              ∈ [0,1]
```

**Estados e ações:**

| Estado | Condição | Ação no build |
|---|---|---|
| `COLLAPSED` | `distinct(F) == 1` **e** `N ≥ 20` | **FAIL** |
| `NEAR_COLLAPSED` | `H_norm(F) < θ` **e** `N ≥ 20` | WARN + exige justificativa por span |
| `OK` | caso contrário | segue |
| `UNDERPOWERED` | `N < 20` | não avalia; registra e reduz o teto de maturidade |

**Por que o limiar de `COLLAPSED` não é arbitrário:** um campo com um único valor carrega exatamente **0 bits**. Por R2, ele não pode alterar o comportamento de nenhum consumidor — logo ou está errado, ou não deveria existir. Isso decorre da definição, não de calibração.

**θ de `NEAR_COLLAPSED` é EM ABERTO.** O que decidiria: medir `H_norm` dos mesmos campos em ≥2 corpora com qualidade conhecida (um que se sabe bom, um que se sabe ruim) e escolher θ que separe os dois. Com n=1 corpus, qualquer θ é chute. Referência disponível: no PILOT-001, `category` = 0,864 (saudável) e `evidence_strength` = 0,340 (suspeito) — θ estará entre esses dois, e não dá para dizer mais do que isso.

**`N ≥ 20`** vem do mesmo lugar que o teto de maturidade (§6) e é o menor N em que uma proporção começa a ser distinguível de ruído.

---

## 5. MÉTRICAS COMPUTÁVEIS (R6)

Escala **única [0,1]** em toda a arquitetura — elimina a colisão medida (`minimum_methodology_fidelity: 0.85` vs `minimum_score: 85`).
Toda métrica é definida **no nível da suíte**, nunca por caso: cada teste tem exatamente **1 `input_case`**, logo uma "acurácia" por teste só assume 0 ou 1 e um limiar de 0,85 é decorativo.

Seja `C` o conjunto de casos da rubrica e `resp(c)` a saída bruta do candidato.

| Métrica | Definição computável | Requisito de instrumentação |
|---|---|---|
| `DECISION_ACCURACY` | `|{c ∈ C_dec : label(resp(c)) = expected_label(c)}| / |C_dec|` | cada caso declara `expected_label` em conjunto fechado; runner emite rótulo legível por máquina |
| `MISSING_INPUT_ACCURACY` | `|{c ∈ C_ask : required_asks(c) ⊆ asks(resp(c)) ∧ ¬proceeded(resp(c))}| / |C_ask|` | caso declara `required_asks[]`; avaliação por continência de conjunto |
| `HALLUCINATION_RATE` | `|{claims em resp(c) que não resolvem para nenhum span ∈ allowed_spans(c)}| / |claims em resp(c)|` | runner cita span por afirmação; **só é computável porque V existe** |
| `METHODOLOGY_FIDELITY` | `|{passos de resp(c) que mapeiam para span declarado na rubrica}| / |passos de resp(c)|` | explicitamente **não** "casa com a skill compilada" |
| `HELDOUT_PASS_RATE` | `|{c ∈ C_holdout : passou}| / |C_holdout|`, reportada **com o limite inferior de Wilson 95%** | `C_holdout` vem de `holdout.lock`, jamais rotulado a posteriori |
| `MARGIN_OVER_BASELINE` | `score(braço_skill) − score(braço_baseline)`, mesmo modelo, mesmas ferramentas, mesmo prompt | pacote e runner próprios para o braço-B |
| `TOTAL_SCORE` | soma ponderada — **e não é portão** | os portões são as métricas obrigatórias + zero falhas críticas |

**Por que `TOTAL_SCORE` deixa de ser portão:** hoje coexistem `minimum_total_score: 85` e critérios `mandatory: true`. Se um obrigatório reprova, o total não salva; se todos passam, o total é redundante. Mantê-lo como portão cria a ilusão de que uma nota alta compensa uma falha crítica — que é literalmente o que `evaluator.md` §1 proíbe (*"compensar falha crítica com pontuação alta"*).

**Correção de escopo do braço-baseline.** O `baseline-summary.md` é fiel à fonte (verifiquei fato a fato contra o transcript), mas a rubrica atual exige `"ROBOT prompt"` — que ele não menciona e a fonte menciona em `9:52`. Na arquitetura nova a rubrica vem de L0, então ambos os braços são julgados pela mesma régua externa e a comparação passa a significar algo.

---

## 6. TETO DE MATURIDADE EM FUNÇÃO DO CORPUS (R5)

| Nível | Exige | PILOT-001 hoje |
|---|---|---|
| `S0 INGESTED` | G0 | alcança |
| `S1 ANCHORED` | G2 (100% span+quote resolvem) | **NÃO** — `quote` 0/44 |
| `S2 MODELED` | G3 (nenhum campo COLLAPSED) | não — 7 campos com 0 bits |
| `S3 AUDITED` | G4 | — |
| `S4 CLOSED` | G5 | — |
| `S5 VALIDATED` | G7 **e** `n_holdout ≥ 16` com Wilson LB ≥ limiar | **impossível** — `cases: []` |
| `production_ready: true` | somente em S5 | correto hoje: `false` |

**O número 16 é calculado, não escolhido.** Para uma taxa observada de 100% de acerto (`p̂ = 1`), o limite inferior de Wilson a 95% é `LB = n / (n + z²)`, com `z = 1,96`:

| n | 13 | 14 | 15 | **16** | 17 | 20 |
|---|---|---|---|---|---|---|
| LB | 0,772 | 0,785 | 0,796 | **0,806** | 0,816 | 0,839 |

**n = 16 é o menor tamanho de held-out em que um limiar de 0,80 pode ser afirmado a 95% — e mesmo assim só com acerto perfeito.** Abaixo disso, o limiar é indefensável por construção, independentemente do resultado.

**Corpus necessário**, à densidade medida de **14 ramos condicionais por aula**:

| taxa de held-out | instâncias necessárias | aulas desta densidade |
|---|---|---|
| 15% | 107 | **8** |
| 20% | 80 | **6** |
| 25% | 64 | **5** |

Isto **refina** a estimativa da Fase 2 ("8 a 12 aulas"), que partia de n=20 arredondado; com o piso calculado de n=16 o mínimo cai para **5–8 aulas**, conforme a taxa de reserva. Ambas as contas concordam na ordem de grandeza: **um módulo, não uma aula.**

**Regra de recusa.** Se o corpus não sustenta o nível, o build não emite o nível — emite o teto com a razão. É o comportamento que o `manifest.yaml` do piloto já teve ao escrever `scope.*: null` com a nota *"values remain null to avoid inventing coverage"*. Isso vira norma, não exceção.

---

## 7. CONTRATO DE DADOS — os campos que sobrevivem a R2

Cada campo precisa de regra de derivação **e** de consumidor cujo comportamento mude. Campos sem os dois são removidos.

| Campo | Regra de derivação (fato contável) | Consumidor · o que muda no comportamento | Veredicto |
|---|---|---|---|
| `span` | endereço L0 | G2 resolve ou reprova | **novo, obrigatório** |
| `quote` | bytes verbatim do span | G2 confere substring; sem quote não há `SOURCE_EXPLICIT` | **novo, obrigatório** |
| `origin_class` | `SOURCE_EXPLICIT` exige quote não vazio; `MODEL_INFERENCE` exige `derived_from[]` não vazio **e** quote ausente | claim `MODEL_INFERENCE` não entra na camada decisória do runtime sem `autonomy = REVIEW` | **mantido, agora derivado** |
| `evidence_strength` | contagem de spans distintos **em segmentos distintos**: 1 → `SINGLE_EXAMPLE`; ≥2 → `CORROBORATED` | `SINGLE_EXAMPLE` **não pode** ser promovido a princípio → torna HR-03 executável pela primeira vez | **mantido, agora derivado** |
| `autonomy` | nasce `UNDEFINED`; valor ≠ UNDEFINED exige span+quote que enuncie supervisão | runtime: AUTO age · REVIEW sinaliza · APPROVAL para · UNDEFINED pergunta | **mantido** — único campo com mudança de comportamento já medida (0/8 → 7/8) |
| `promotion_level` | função de `origin_class` + `evidence_strength` + desempenho no held-out | `CONFIRMED` entra em produção; `PROBABLE` vira advisory; `WEAK` não controla | **mantido, agora derivado** |
| `category` | traço textual observável | roteamento de empacotamento | **mantido** — único campo saudável hoje (H_n 0,864) |
| `status` | ciclo de vida do registro | reprocessamento | **mantido, mas fora do gate G3** (é operacional, não epistêmico) |
| `confidence.score` | — nenhuma | — nenhum | **REMOVIDO** |
| `confidence.level` | — nenhuma | — nenhum | **REMOVIDO** |
| `rationale.state` | derivável de quote presente/ausente para a razão | idem `origin_class` | **fundido** em `origin_class` da razão |

**Nota sobre H1 (que caiu).** A hipótese propunha substituir `confidence` por uma escala ordinal ancorada. Não foi adotada: **essa escala já existe** (`evidence_strength`: DIRECT/CORROBORATED/SINGLE_EXAMPLE/INFERRED/WEAK) **e já colapsou** (37/4/3, com 0 usos de 2 valores, H_n = 0,340). Trocar o vocabulário não resolveria — o que resolve é o par regra+consumidor da tabela acima. `confidence` é removido, não substituído.

---

## 8. ARMAZENAMENTO E EXECUÇÃO

```
vault/objects/<sha256>              L0 imutável
vault/manifest.jsonl                path, sha256, bytes, mime, media
corpus/<course>/segments.jsonl      spans estruturais
corpus/<course>/train.jsonl         segments − holdout
holdout/<course>.lock               seed, rate, spans[], sha256, sealed_at
rubric/<course>.lock                casos, expected_label, allowed_spans, pesos
claims/<course>.jsonl               saída de E — span+quote+claim
model/<course>.diff.jsonl           saída de N — só o delta contra E
audit/<course>/findings.jsonl       saída de A, legível por máquina
audit/<course>/decision.json        severidade → ação
bundle/<skill>/…                    saída de P, com provenance/claims.jsonl
gates/<run>/G<n>.json               relatório de cada portão, com os números
runs/<run_id>/raw/                  saídas brutas do candidato, imutáveis
runs/<run_id>/scores.json           métricas de §5
```

**Execução.** Driver determinístico, DAG com entradas endereçadas por conteúdo → mesmo input, mesmo output. Cada portão escreve `gates/<run>/G<n>.json` com **os números medidos**, não com `PASS`. A lição vem do `PREFLIGHT_REPORT.md`: das 11 afirmações "PASS", uma não tinha predicado, uma media outra coisa e uma era NO-OP porque nenhuma pré-condição do ramo era satisfeita. **Um portão que não publica o número que mediu não é auditável.**

**Testes do próprio compilador (meta-testes).** Cada portão nasce com dois fixtures — um que o faz disparar e um que o faz passar. É assim que se prova que o componente novo funciona:

| Portão | Fixture negativo (tem de FALHAR) | Fixture positivo |
|---|---|---|
| G2 | claim com `quote` que não é substring do span · **e o caso real `EV-0001` com `end 00:00:29`** | claim com quote verbatim |
| G3 | 25 registros com 1 valor distinto em `origin_class` | distribuição com H_norm > θ |
| G5 | claim presente no bundle e ausente do conjunto pós-A · rubrica contendo `ADR-0001` | bundle = subconjunto |
| G1 | artefato citando span do `holdout.lock` | nenhuma interseção |
| G6 | `production_ready: true` com `n_holdout = 12` | S5 com n ≥ 16 |

---

## 9. ONDE CONVIRJO COM O CHATGPT — E POR QUÊ

Convergência medida é evidência; divergir de tudo seria contrariedade. Onde o desenho original está certo, ele é mantido — e a medição que o sustenta está ao lado.

| Mantido do desenho original | Medição que sustenta |
|---|---|
| **Decomposição por função epistêmica** (extrair / modelar / atacar / empacotar / avaliar) | O adversário, que só existe porque a decomposição o previu, foi o **único** componente com valor demonstrado: 6/6 correções verificadas nos arquivos. |
| **O adversário como componente separado** | 3 HIGH + 3 MEDIUM na 1ª passada, 1 HIGH + 2 MEDIUM na 2ª — e todos os seis achados eram reais e foram corrigidos. |
| **`origin_class` em três classes** | O conceito é correto e é o eixo certo; falhou por falta de regra e consumidor, não por desenho. Mantido, com derivação mecânica. |
| **`evidence_strength` como escala ordinal ancorada em fato observável** | Antecipa exatamente o que H1 propunha reinventar. Mantido; ganha a regra de derivação por contagem de spans. |
| **`UNDEFINED` como estado de primeira classe** | Ideia do próprio hardening v0.1.1, e é a **única mudança de comportamento medida em todo o projeto**: 0/8 → 7/8 ADRs e steps. É o modelo do que R2 exige. |
| **Held-out tem de ser travado antes da modelagem** (hardening §A) | O mecanismo, o schema e **o código de trava já existem** (`validate_generated_skill.py` 117–123, `HELD_OUT_ACTIVE_WITHOUT_PREMODEL_LOCK`) — nunca acionados. Minha divergência é de **uma etapa** (antes da extração, não da modelagem), não de conceito. |
| **Isolamento runtime ↔ judge** (hardening §B) | Funciona no nível de arquivo: 6/6 SHA-256 conferem, 0 marcadores privados, 0 arquivos proibidos. Mantido integralmente; acrescento a camada semântica. |
| **Preflight estático obrigatório** (hardening §H) | O script existe, roda e 8 das 11 afirmações reproduzem. Mantido e estendido — não reescrito. |
| **Escada de maturidade S0–S4 com `production_ready` travado** | O check `PRODUCTION_READY_WITHOUT_S4` funciona. Mantido; acrescento o teto em função do corpus. |
| **Recusar inventar contagens** | `manifest.scope.*: null` com a nota *"to avoid inventing coverage"* é o comportamento correto. Vira norma da arquitetura (§6). |
| **ADR como unidade atômica de decisão** | 278 usos consistentes, 0 ambiguidades internas. Mantido — só renomeio o namespace (ADR-0012). |
| **Passe único decision+workflow+principle** | H6 caiu: já era assim, e o extrator produziu 100% do conteúdo. Mantido deliberadamente. |
| **`test.schema.yaml` e o desenho dos casos** | 10 casos concretos, 26 campos, `user_prompt` literal, 0 erros de schema. O artesanato dos testes é bom; o que muda é de onde vem a rubrica. |

**Resumo honesto:** dos 5 estágios originais, mantenho 4 (E, A, P, J) e rebaixo 1 (N). Dos schemas, mantenho a estrutura e removo 2 campos. Do hardening v0.1.1, mantenho as 8 regras e endureço 2 (§A timing, §H escopo). **O que substituo não é o desenho — é o referente das verificações.**

---

## 10. EM ABERTO

Sete pontos. Não preenchi nenhum com plausibilidade.

| # | Em aberto | O que decidiria |
|---|---|---|
| 1 | **θ de `NEAR_COLLAPSED`** | `H_norm` dos mesmos campos em ≥2 corpora de qualidade conhecida (um aprovável, um reprovável). Hoje só tenho o intervalo: entre 0,340 (`evidence_strength`, suspeito) e 0,864 (`category`, saudável). |
| 2 | **Se N (Consolidator) se paga em escala de módulo** | `|diff(E, N)|` em corpus ≥5 aulas. Se continuar na ordem de 1 campo, N é absorvido por E. |
| 3 | **Detecção mecânica de "a claim excede a quote"** | Um conjunto rotulado de pares claim/quote com julgamento humano de exagero, para testar se verificação automática de implicação atinge precisão útil. Sem isso, essa camada é do adversário e permanece juízo — e eu digo isso em vez de fingir que a âncora resolve. |
| 4 | **Granularidade do corte de held-out** (span · ramo · caso) | Rodar as três no mesmo corpus e comparar variância do `HELDOUT_PASS_RATE`. Escolhi ramo/span por impossibilidade aritmética do corte por aula (1 caso ponta-a-ponta), não por evidência comparativa. |
| 5 | **Se `GENERAL_KNOWLEDGE` deve existir** | 0 usos em 44 registros — não dá para distinguir campo morto de campo não exercitado. Decide: um corpus onde o professor importe explicitamente conhecimento externo. |
| 6 | **Se o candidato consegue emitir citação de span por afirmação** | `HALLUCINATION_RATE` depende disso. É uma capacidade do modelo avaliado, não do compilador. Decide: uma rodada piloto medindo a fração de afirmações que o candidato consegue citar. Se for baixa, a métrica precisa de outro instrumento. |
| 7 | **Se uma rubrica não-circular é escrevível na prática** | Quem lê L0 forma um modelo mental — a independência é de origem, não de cognição. Decide: dois autores independentes escrevendo rubrica do mesmo L0 sem contato, medindo concordância nos `expected_label`. Baixa concordância significa que a rubrica carrega o modelo do autor e o problema mudou de lugar em vez de ser resolvido. |

---

## 11. ÍNDICE DE ADRs

| ADR | Título |
|---|---|
| [ADR-0001](adr/ADR-0001.md) | Vault L0 imutável endereçado por conteúdo como único referente de verdade |
| [ADR-0002](adr/ADR-0002.md) | Tripla obrigatória span + quote + claim |
| [ADR-0003](adr/ADR-0003.md) | Corte de held-out em L0, por span, antes da extração |
| [ADR-0004](adr/ADR-0004.md) | Remover `confidence`; derivar `evidence_strength` de contagem de spans |
| [ADR-0005](adr/ADR-0005.md) | Portão de degeneração por dispersão |
| [ADR-0006](adr/ADR-0006.md) | Adversário mantido e promovido a portão bloqueante legível por máquina |
| [ADR-0007](adr/ADR-0007.md) | Packager como função pura com portão de fechamento pós-compilação |
| [ADR-0008](adr/ADR-0008.md) | Rubrica escrita em L0 antes da extração, proibida de citar IDs internos |
| [ADR-0009](adr/ADR-0009.md) | Métricas computáveis em escala única; `TOTAL_SCORE` não é portão |
| [ADR-0010](adr/ADR-0010.md) | Teto de maturidade em função do corpus (n ≥ 16 held-out) |
| [ADR-0011](adr/ADR-0011.md) | Consolidator rebaixado a função condicional que emite diff |
| [ADR-0012](adr/ADR-0012.md) | Separar namespace de IDs do curso e do projeto |

---

---

## 12. ADENDO — deriva da esteira paralela durante a Fase 3

O manifesto foi congelado às **02:28** com 257 arquivos. Na verificação final, às **02:39**, apareceram **2 arquivos novos**, criados às 02:31 pela esteira paralela do usuário. **Não fui eu** — meus destinos de escrita foram `/tmp/` e `Course-to-Skill-Claude/docs/`. Os **257 arquivos do manifesto seguem byte-idênticos**; a deriva é somente por adição.

**O manifesto NÃO foi atualizado, deliberadamente.** Ele é a referência fixa da Fase 5; reescrevê-lo a cada adição destruiria sua função. A deriva fica registrada aqui:

| Arquivo | Bytes | Criado |
|---|---|---|
| `02_PILOTS/PILOT-001/TEST-0008/PILOT-001-TEST-0008-ARM-A.zip` | 2.774 | 2026-08-10T02:31:45 |
| `02_PILOTS/PILOT-001/TEST-0008/PILOT-001-TEST-0008-ARM-B.zip` | 25.148 | 2026-08-10T02:31:57 |

**Conteúdo** (extraído em `/tmp`, leitura apenas): são os dois braços do `SUMMARY_VS_SKILL`. **ARM-A** tem 3 arquivos — `README-FIRST.md`, `RUNNER_PROMPT.md` e um `SKILL.md` de 1.428 B que é **o `baseline-summary.md`** (confirmado por busca de trecho literal). **ARM-B** tem os 14 arquivos do pacote completo do candidato. O `RUNNER_PROMPT.md` é byte-idêntico nos dois braços, o que satisfaz `same_prompt_required: true`.

**Impacto nesta proposta:** fecha **2 dos 4** itens que a resposta (c) da Fase 2 listava como faltantes para o `SUMMARY_VS_SKILL` rodar — (1) pacote e runner do braço-baseline agora existem; (2) a contradição de protocolo se resolve ao servir o baseline como runtime do braço-A em vez de expor `judge-private/`. **Permanecem em aberto os outros 2:** a rubrica ainda exige `"ROBOT prompt"` em `expected_output.required_elements`, elemento que o baseline não menciona e a fonte menciona em `9:52`; e **4 de 6** `comparison_metrics` continuam sem critério de rubrica correspondente. Ambos são exatamente o que a ADR-0008 e a ADR-0009 endereçam — a montagem dos braços é necessária, mas não suficiente, enquanto a régua vier do artefato.

**Observação neutra de método:** servir o resumo como `SKILL.md` faz o `RUNNER_PROMPT.md` funcionar sem alteração, o que preserva a paridade de prompt — é a solução certa para o problema de execução. Vale registrar que isso enquadra um resumo como "Skill" para o braço-A; se isso enviesa a comparação é **EM ABERTO**, e decide-se rodando uma terceira condição em que o resumo é apresentado como resumo. Nenhuma classificação desta proposta muda por causa disso.

---

**FIM DA FASE 3.** Nenhum código foi escrito, nenhuma implementação foi criada, nenhum arquivo de `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado por mim.
