# ARCHITECTURE_REVIEW — Course-to-Skill Compiler v0.1.1

**Fase 2 — Architecture Review.** Entradas: `docs/PROJECT_INVENTORY.md` e `docs/INVENTORY_DELTA_v0.1.1.md`, mais releitura direcionada dos artefatos.
**Data:** 2026-08-10 · **Modo:** READ-ONLY absoluto sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/`.
**Regra de prova:** nenhuma classificação sem número ou citação. Onde falta medida: `EVIDÊNCIA_INSUFICIENTE` + o que precisaria ser medido.
**Escopo:** classificar. **Não** escrever a arquitetura nova.

---

## 0. CORREÇÃO DE MEDIDA DA FASE 1

Ao reler as 16 evidências "nunca citadas" para responder o item (a), refiz a varredura sobre **toda** a pasta `analysis/` (a Fase 1 percorreu um subconjunto de arquivos).

**Número correto: 12 evidências órfãs, não 16.**
`EV-0001, EV-0002, EV-0003, EV-0007, EV-0008, EV-0009, EV-0010, EV-0015, EV-0020, EV-0021, EV-0022, EV-0023`.
`EV-0011`, `EV-0012`, `EV-0016` e `EV-0019` **são** citadas (EV-0019 aparece 10× em `analysis/` e 6× na skill compilada).

O denominador correto é **32/44 referenciadas (72,7%), 12 órfãs (27,3%)** — e o mesmo conjunto de 12 vale tanto para `analysis/` quanto para a skill compilada. A Fase 1 já reportava "32 das 44 são citadas" para o pacote compilado; o "28/44 · 16 órfãs" da tabela D.2 estava errado por varredura incompleta. **Corrige-se D.2 do `PROJECT_INVENTORY.md`.** Nenhuma outra conclusão depende desse número.

---

## 1. TABELA DOS 15 PONTOS

| # | Ponto | Classificação | Evidência que sustenta |
|---|---|---|---|
| 1 | **Conceito** (curso → skill executável, com camada epistêmica) | **KEEP** | Produziu artefato executável real: 8/8 ADRs com `conditions` não-vazio e `action` não-nulo; `ADR-0007` com limiar numérico ("2 horas/semana E output melhor") e ramo de falha; `ADR-0003` com 5 ramos condicionais. A camada epistêmica funcionou ao menos uma vez: o Skeptic detectou 3 HIGH que eram invenção do compilador (SC-001/002/003) e **6/6 correções foram verificadas nos arquivos**. |
| 2 | **Arquitetura de camadas** (L0→L1→L2→L3→L4) | **IMPROVE** | Medição nova e decisiva: comparando `analysis/decisions.yaml` (L1) com `knowledge/decision-rules.yaml` (L3) campo a campo nos 8 ADRs — **exatamente 1 campo mudou: `autonomy` (8/8 registros). Todos os outros campos são idênticos.** L2+L3 não acrescentaram nenhum conteúdo decisório; a única mudança foi imposta pelo Skeptic (SC-001). Some-se: **13 artefatos prescritos nunca foram produzidos** (0 ocorrências nas duas pastas): `coverage.yaml`, `conflicts.yaml`, `provenance-map.yaml`, `methodology-report.md`, `modeling-review.md`, `lesson-report.md`, `review-notes.md`, `skeptic-report.md`, `findings.yaml`, `challenged-entities.yaml`, `provenance-failures.yaml`, `conflict-review.yaml`, `contamination-review.yaml`. As camadas existem como texto; os contratos entre elas não são exigidos por ninguém. |
| 3 | **Schemas** | **IMPROVE** (não REPLACE) | Funcionam: 44 evidências, 8 ADRs, 1 WF, 6+10 testes e 1 registry → **0 erros** de validação contra os schemas do release. Os defeitos são de cobertura, não de desenho: `UNDEFINED` existe em **2 enums** (`decision.autonomy.level`, `workflow.step.autonomy`) e falta em `origin_class`, `status`, `evidence_strength`, `rationale.state`, `promotion_level`; `conditions` (`default: []`) e `action` (`null`) são **opcionais** no par que define executabilidade; `anti-patterns` (7) e `quality-criteria` (6) **não têm campo `origin_class`** — 13 entidades da skill sem classificação epistêmica. Trocar o schema descartaria a única coisa do projeto com 0 defeitos medidos. |
| 4 | **Prompts** | **IMPROVE** + **REMOVE** as cópias antigas | Volume sem vinculação: 5 prompts, 1.267–1.973 linhas cada (7.  387 linhas no release), e 13 dos artefatos que eles mandam produzir não existem (ponto 2). `lesson-analyzer.md` §40 gasta 38 linhas definindo faixas de confiança que resultaram em **1 valor distinto em 44 registros**. REMOVE: existem 5 prompts duplicados em `Course-to-Skill/course-to-skill-compiler/prompts/`, **todos diferentes** dos do release (5/5 MD5 divergentes) e sem marcação de qual vale. |
| 5 | **Provenance** | **REPLACE** | O fechamento é auto-referencial por construção: `validate_generated_skill.py` linhas 92–101 compara `union(EV usados)` ⊆ `union(EV em provenance/evidence-map.jsonl)` — **os dois escritos pelo mesmo compilador na mesma passada**. `evidence.jsonl` não é lido pelo validador e **não está no pacote** (14 arquivos em `generated-skill/`, nenhum é ele). `evidence-map.jsonl` tem 16 linhas com 5 campos só-de-ID (`entity_id, entity_type, source_evidence_ids, origin_class, promotion_level`) — sem texto, sem timestamp. `source_excerpt` preenchido em **0/44**. O `SKILL.md` §12 promete `EV-0042 — M02-L03 — 00:18:32`; o entregue não tem aula nem timestamp. Não é ajuste de campo: o referente do check está errado. |
| 6 | **Controle de inferência** (`origin_class`) | **REPLACE** | O mecanismo tem 3 classes e produziu 1: `SOURCE_EXPLICIT` **44/44** evidências, **8/8** ADRs, 6/6 princípios, 3/3 ferramentas, 1/1 workflow, 16/16 entradas do evidence-map. Zero `MODEL_INFERENCE`, zero `GENERAL_KNOWLEDGE`. A **única** diferenciação do projeto inteiro — as 10 perguntas em `MODEL_INFERENCE` — foi produzida por uma reprovação humana em 2ª passada (SC-003, HIGH: *"a aula não formula essas dez perguntas literalmente"*), não pelo mecanismo. Um classificador que emite uma única classe em 74 de 84 oportunidades e depende de auditoria manual para a exceção não está controlando nada. |
| 7 | **Visual dependency** | **IMPROVE** | O pouco que existe está correto: 3 frames, 3 `visual_observations`, 3 evidências com `visual_dependency: true` (`EV-0041/0042/0043`), cobertura 1:1, cada uma com `source_ref` `VIDEO` apontando o PNG e `frame_description` preenchida. Defeitos medidos: `visual_dependency_note` é a **mesma frase literal nas 3** (*"A demonstração visual confirma ou acrescenta detalhes operacionais à fala."*); `visual-observations.yaml` tem **0 `evidence_id`** nas 3 entradas (a ponte é implícita); `source-metadata.yaml` diz `visual_review_pending: true` enquanto `visual-observations.yaml` diz `visual_review: COMPLETE`; e **0 frames, 0 `.png`, 0 `VIDEO_SCREEN` no runtime-bundle** — a dependência visual é declarada e depois descartada no empacotamento. |
| 8 | **Skeptic** | **KEEP** (componente de maior valor medido) + **IMPROVE** contrato de saída | Único estágio com valor demonstrável: v1 = 3 HIGH + 3 MEDIUM, v2 = 1 HIGH + 2 MEDIUM, v3 = 0/0/0. Verifiquei nos arquivos que **6 de 6 correções foram efetivamente aplicadas** (autonomy 3-AUTO/4-REVIEW/1-APPROVAL → 7-UNDEFINED/1-REVIEW; `max_iterations` 5 → `null`; 10 perguntas → `MODEL_INFERENCE`; princípios 7→6 + bloco `structures`; HC-002 APPROVAL→REVIEW; `stop_conditions` 4→2). E fez isso **sem ler L0**. IMPROVE: `skeptic-critic.md` §5 prescreve 7 saídas; **6 das 7 não existem** — produziu-se um `skeptic-review.yaml` ad hoc, fora do contrato. |
| 9 | **Skill Compiler** | **IMPROVE** | O `ENTRY GATE` (§2) só checa `audit_decision.status`. O `REQUIRED INPUT PACKAGE` (§3) exige 11 arquivos, dos quais **`coverage.yaml`, `conflicts.yaml` e `provenance-map.yaml` nunca existiram** — e a compilação seguiu. Resultado: `manifest.scope.{in_scope_count, out_of_scope_count, undefined_count}` = `null` nos três, com nota admitindo o buraco; `knowledge/examples.jsonl` = **0 bytes nas 8 cópias**. O compilador é honesto sobre o que não sabe (não inventou contagens) e é exatamente por isso que o gate precisa reprovar em vez de deixar passar com `null`. |
| 10 | **Evaluator** | **EVIDÊNCIA_INSUFICIENTE** para o componente · **REPLACE** para o contrato de entrada | **Nunca rodou.** `validation-decision-template.yaml`: 9 métricas em `null` (`total_score`, `decision_accuracy`, `methodology_fidelity`, `counterfactual_pass_rate`, `missing_input_pass_rate`, `held_out_pass_rate`, `skill_score`, `baseline_score`, `margin`); `manifest.evaluation.status: NOT_YET_VALIDATED`; **0 arquivos de resultado** nas duas pastas. Classificar o componente exigiria ≥1 execução com outputs brutos salvos. O que **é** classificável agora é o contrato: `evaluator.md` §4 recebe `generated-skill/` e **0 ocorrências** de `transcript`/`vídeo`/`fonte original` no arquivo inteiro (1.616 linhas) → REPLACE do contrato (ver §3, pergunta central). |
| 11 | **Suíte de testes** | **IMPROVE** | Artesanato bom: 10 casos concretos, 26 campos preenchidos cada, `user_prompt` literal, `prohibited_behavior`, `critical_failures`, **0 erros de schema**. Defeitos medidos: (i) **10/10** declaram `isolation.hidden_items` que estão inteiros no pacote do candidato; (ii) **4 testes violam a §C** do próprio hardening; (iii) **8/10 sem bloco `baseline`**; (iv) colisão de escala — `pass_criteria.minimum_methodology_fidelity: 0.85` (0–1) vs `rubric[].minimum_score: 85` (0–100) para o mesmo nome; (v) **4 de 6 `comparison_metrics`** (`DECISION_ACCURACY`, `MISSING_INPUT_ACCURACY`, `HALLUCINATION_RATE`, `TOTAL_SCORE`) **não têm critério de rubrica correspondente**; (vi) cada teste tem exatamente **1 `input_case`**, logo `minimum_decision_accuracy: 0.85` sobre n=1 só é satisfazível com 1,0 — o limiar é decorativo. |
| 12 | **Hallucination control** | **REPLACE** | 12 proibições textuais (`SKILL.md` §13, §29; `lesson-analyzer.md` HR-01/02/03/05/06, §5.3) e **0 verificações mecânicas**: o validador (138 linhas, 7 checks) não lê `confidence`, não lê `origin_class`, não resolve `EV-` contra `evidence.jsonl`, não confere âncora textual, não implementa nenhum dos 5 estados de §13 (`METHOD_NOT_DEFINED`, `RATIONALE_NOT_EXPLICIT`, `INSUFFICIENT_EVIDENCE`, `CONTRADICTION_DETECTED`, `MISSING_REQUIRED_INPUT`). No lado do teste: `HALLUCINATION_CONTROL` é critério de rubrica em **2 de 10** testes; `HALLUCINATED_METHODOLOGY` é `critical_failure` em 5 de 10, mas julgado pela rubrica circular do ponto 15 — que por construção aprova a alucinação já embutida no artefato. |
| 13 | **Data leakage** | **REPLACE** | **10/10** testes declaram `answer_hidden: true`, `source_hidden: true`, `contamination_risk: LOW` e listam `hidden_items` que estão **100% presentes** no `runtime-bundle`. As **2 únicas** `expected_questions` da suíte têm match **exato, caractere a caractere**, com entradas de `knowledge/questions.yaml` entregue ao candidato. O `VERIFY_KIT.py` procura *nomes de arquivo* e *marcadores de string* (`TEST-000`, `expected_behavior:`) — reproduzi, 0 ocorrências, correto — mas o vazamento é semântico e passa por baixo de qualquer grep. |
| 14 | **Overfitting** | **ADD** (instrumento inexistente) | Não há o que melhorar: **0 casos held-out** (`held-out-registry.yaml`: `registry_status: NOT_AVAILABLE`, `cases: []`, `created_before_modeling: false`). 9 dos 10 testes ancoram em IDs internos (`source_scope`: DECISION 6, WORKFLOW 3, EVIDENCE 1 — nenhuma âncora em arquivo de fonte). O único `BLIND_EVALUATION` (TEST-0009) é `EV-0027`, minuto **8:05–8:20** da aula. Generalização hoje é medida sobre material de treino. |
| 15 | **Avaliação circular** | **REPLACE** (do mecanismo, não do componente) | `evaluator_instructions` tem **1 único valor distinto nos 10 testes**: *"Avaliar somente contra a metodologia extraída do PILOT-001."* A suíte (37.150 B) tem **0** ocorrências de `transcript`, `frame`, `timestamp`, `00:`, `video`, `source_excerpt`, `YkdAx2XjWDs`. `expected_output.structural_requirements`: *"A sequência deve respeitar a lógica de **WF-0001**"* — o padrão de referência é o artefato sob teste. Um erro de extração cometido em L1 é invisível a essa rubrica e é premiado com nota máxima em `METHODOLOGY_FIDELITY`. |

**Placar:** KEEP 2 · IMPROVE 6 · REPLACE 5 · ADD 1 · EVIDÊNCIA_INSUFICIENTE 1.

---

## 2. AS 7 HIPÓTESES — JULGADAS

### H1 — `confidence` numérico → REPLACE por escala ordinal ancorada
**Diagnóstico ACEITO · remédio REFUTADO.**

O diagnóstico está medido e é forte: `confidence.score` tem **1 valor distinto em 44 evidências (0,97)**; 2 valores em 8 ADRs; os 6 princípios **não têm o campo**; nenhum schema liga `score` a `level` (um `0.10`/`HIGH` é válido); nenhum código lê o campo.

O remédio proposto, porém, **já existe no schema e já colapsou**. `evidence.schema.yaml` define `evidence_strength: [DIRECT, CORROBORATED, SINGLE_EXAMPLE, INFERRED, WEAK]` — uma escala ordinal ancorada em fato observável, que mapeia quase 1:1 na proposta:

| Proposta H1 | Campo existente | Uso medido no piloto |
|---|---|---|
| `DECLARADO_EXPLÍCITO` | `DIRECT` | **37/44** |
| `DEMONSTRADO_1x` | `SINGLE_EXAMPLE` | 4/44 |
| `DEMONSTRADO_Nx` | `CORROBORATED` | 3/44 |
| `PADRÃO_INFERIDO` | `INFERRED` | **0/44** |
| — | `WEAK` | **0/44** |

Trocar o vocabulário não corrige nada, porque **o colapso não foi causado pelo vocabulário**: foi causado por (i) ausência de regra mecânica de atribuição e (ii) ausência de consumidor. `evidence_strength` colapsou exatamente como `confidence.score`, com nomes bons.

Objeção adicional de desenho: a escala proposta mistura dois eixos que hoje estão separados. `DECLARADO_EXPLÍCITO` é `origin_class`; `DEMONSTRADO_Nx` é contagem de suporte. Fundi-los é perda de expressividade — hoje é possível representar "inferido a partir de 3 demonstrações"; na escala de 4 valores, não.

**Conclusão:** REMOVE `confidence.score` (é ruído com aparência de medida). Mantenha os dois eixos existentes e **vincule `evidence_strength` a um fato contável** — número de `source_refs` distintos, ou de timestamps distintos, ou de modalidades distintas que sustentam a mesma observação — de modo que o valor seja derivado, não escolhido. E dê a ele um consumidor: hoje nada lê nem `confidence` nem `evidence_strength`.

### H2 — "não inventar" vira trava de schema: campo nasce UNDEFINED; valor ≠ UNDEFINED exige `evidence_id` válido
**ACEITA, com uma correção que decide se funciona ou não.**

Há um experimento natural no próprio piloto que sustenta o mecanismo: `autonomy` foi o **único** campo onde `UNDEFINED` virou obrigatório após SC-001, e o efeito foi imediato e verificável — **0/8 → 7/8 ADRs** e **0/8 → 7/8 steps**. Quando o estado indefinido é representável e exigido, ele aparece; quando não é, o modelo preenche com plausibilidade (3 AUTO / 4 REVIEW / 1 APPROVAL, todos reprovados como não ensinados).

Custo medido: `UNDEFINED` existe hoje em **2 enums**; para "todo campo nasce UNDEFINED" seriam necessários ao menos mais 5 (`origin_class`, `status`, `evidence_strength`, `rationale.state`, `promotion_level`), além de tornar `conditions`/`action` obrigatórios com estado vazio explícito.

**A correção que decide tudo:** *"exige `evidence_id` válido"* — se "válido" significar o que o projeto hoje chama de válido (casar `^EV-[0-9]{4,}$` e constar no `evidence-map.jsonl`), **H2 reproduz F.2 com mais etapas**. Esse check já existe (`provenance-closure`), já passa (`PASS`), e fecha contra um mapa escrito pelo próprio compilador. Para H2 ter efeito, "válido" precisa significar: **resolve para um registro de evidência empacotado junto, que carrega um trecho verbatim de L0 localizável mecanicamente na fonte**. Sem isso, a trava tranca a porta e deixa a chave na fechadura.

### H3 — `source_excerpt` verbatim obrigatório no L1 e evidência dentro do pacote de runtime
**ACEITA.**

Sustentação: `source_excerpt` está em **0/44**; a transcrição é em inglês e as 44 `observation` em português — **não existe nenhuma sequência literal compartilhada entre evidência e fonte**, logo nenhuma verificação lexical é possível hoje, nem manual nem automática. A única âncora que sobrou é o timestamp, e ela funciona: **93 de 94** timestamps citados batem exatamente com uma das 180 marcas do transcript (1 diverge: `EV-0001`, `end 00:00:29`). Com excerpt verbatim, essa divergência seria detectável por código, não por auditoria externa.

Custo medido, e é baixo: `evidence.jsonl` = 72.414 B contra um runtime-bundle atual de ~68,5 KB — o pacote cerca de dobra. Irrelevante frente ao ganho.

**Ressalva que precisa ficar escrita:** o excerpt entrega **ancoragem**, não **fidelidade**. Um checker pode provar que a string existe em `00:08:05`; não pode provar que a `observation` em português decorre dela. A parte de julgamento permanece humana ou de LLM-juiz. Vender excerpt como solução de alucinação seria repetir o erro de §13 (proibição textual tratada como controle). E o campo precisa nascer com **assert de substring contra o arquivo de L0** — do contrário será o 14º artefato prescrito e não produzido (ponto 2).

### H4 — Evaluator vê SOMENTE L0; rubrica escrita antes da compilação
**ACEITA quanto ao Evaluator · a segunda metade é FRACA DEMAIS e precisa endurecer.**

Primeira metade, sustentada: 10/10 `evaluator_instructions` mandam avaliar contra a metodologia extraída; 0 referências à fonte na suíte; `source_scope` 10/10 em IDs internos. E é implementável: o padrão de referência necessário está em L0 — a aula diz literalmente, em `11:48`, *"add a human in the loop for the first 30 days. Review every output before it goes anywhere"*. Uma rubrica escrita daí não precisa de nenhum artefato compilado.

Segunda metade, **insuficiente como enunciada**. "Antes da compilação" (antes de L3) ainda permite exatamente o defeito medido: TEST-0009 foi rotulado `BLIND_EVALUATION` e é `EV-0027` (fonte 8:05–8:20) → a contaminação entrou em **L1**, não em L3. O `held-out-registry.yaml` já nomeia o requisito correto e registra a falha: `created_before_modeling: **false**`. A trava tem de ser **antes de L1 ser lido por qualquer humano ou estágio**, com os casos recortados diretamente de L0 e congelados por hash. Escrever a rubrica "antes da compilação" produziria de novo um caso cego que é recall.

### H5 — todo estágio downstream relê L0/L1, não só o output anterior
**PARCIALMENTE REFUTADA.** É a hipótese que a evidência menos sustenta.

Contraevidência direta: o Skeptic produziu **3 HIGH + 3 MEDIUM na 1ª passada e 1 HIGH + 2 MEDIUM na 2ª, com 6/6 correções verificadas nos arquivos — sem acesso a L0**. Seu contrato de entrada (`skeptic-critic.md` §4) dá apenas flags booleanas (`original_sources_available`, `evidence_records_available`). Os três achados HIGH — governança adicionada pelo compilador, `max_iterations: 5` inventado, perguntas apresentadas como explícitas — foram derivados por raciocínio sobre os artefatos. **A afirmação "é preciso reler L0 para pegar invenção" é refutada pelo único ponto de dados que o projeto tem.**

Segunda contraevidência, de risco: o Skill Compiler é estágio de **empacotamento**. Dar-lhe L0 cria uma superfície nova de invenção — conteúdo re-derivado da fonte **depois** da auditoria do Skeptic, entrando na skill sem passar por crítica. Isso piora o controle em vez de melhorar.

O que a evidência **sustenta**: (i) o Skeptic afirmou em `passed_checks` que *"Todas as referências EV usadas nos artefatos apontam para evidências existentes"* — uma afirmação de existência que ele não tinha como verificar com flags booleanas; o que falta ali é **L1 real (registros de evidência), não L0**; (ii) quem escreve a rubrica precisa de **L0 e só L0** (H4); (iii) o checker estático precisa de **L0** para validar excerpts (H3).

**Reformulação sustentada pela medida:** L1 completo (com excerpt) deve ser legível por Skeptic e Evaluator; L0 deve ser legível por quem escreve rubrica e pelo verificador de excerpt. Releitura irrestrita de L0 por todos os estágios é custo sem captura medida, e no caso do Compiler é dano.

### H6 — Decision + Workflow + Principle num passe só, não agentes separados
**REFUTADA por inexistência do alvo — e o alvo real está a uma camada de distância.**

Não existem agentes separados por tipo de entidade. `lesson-analyzer.md` §10 executa, **num único prompt**: PASS 3 Decision Mining, PASS 4 Workflow Mining, PASS 5 Principle/Anti-pattern Mining. `methodology-modeler.md` §6 executa, **num único prompt**: PASS 2 Decision Consolidation, PASS 4 Principle Formation, PASS 5 Workflow Consolidation. A separação dos 5 estágios é por **função epistêmica** (extrair / modelar / atacar / empacotar / testar), não por tipo de entidade. H6 descreve a arquitetura que já está lá.

O que a medição aponta como candidato real a fusão é outro: **L1 → L2**. Diff campo a campo dos 8 ADRs entre `analysis/decisions.yaml` (L1) e `knowledge/decision-rules.yaml` (L3): **1 único campo mudou — `autonomy`, em 8/8 registros. Todo o resto é idêntico.** E essa mudança foi ordenada pelo Skeptic, não gerada pelo Modeler. Some-se que o Modeler não produziu 4 dos 11 arquivos que seu próprio §5 prescreve (`methodology-report.md`, `conflicts.yaml`, `provenance-map.yaml`, `modeling-review.md`). Em um piloto de uma aula, **a camada L2 teve delta mensurável de um campo**.

Ressalva honesta: n=1 aula. Para uma aula, consolidação entre lições é vacuidade por definição — L2 existe para reconciliar evidência de múltiplas aulas. **EVIDÊNCIA_INSUFICIENTE para eliminar L2**; o que seria preciso medir é o delta L1→L2 em um módulo com ≥5 aulas, onde há de fato o que consolidar. O que está provado é apenas que **em escopo de aula única L2 é overhead**, e que o gate de entrada de L3 não percebeu que L2 entregou 7 de 11 arquivos.

### H7 — falta gate de METHODOLOGY_DENSITY antes de compilar, com `COURSE_NOT_COMPILABLE`
**Premissa ACEITA · métrica proposta REFUTADA como suficiente · limiar EVIDÊNCIA_INSUFICIENTE.**

Premissa correta e medida: **0 ocorrências** de `DENSITY`, `COMPILABLE`, `NOT_COMPILABLE` em todo o release. O conceito adjacente existe só como prosa — `methodology-modeler.md` §46–47 define uma COVERAGE MATRIX com estados `COVERED / PARTIALLY_COVERED / UNDEFINED / CONTRADICTORY / HELD_OUT` — mas **`coverage.yaml` nunca foi produzido (0 arquivos)**, não tem schema (o release tem 5 schemas, nenhum de cobertura), e `manifest.scope.undefined_count` saiu `null`. Não há gate.

Por que a métrica proposta não é a que os dados pedem: a aula tem **2,9 evidências/min, 8 ADRs, 14 ramos condicionais, 1 workflow de 8 steps em 14,75 min**. Por qualquer limiar razoável de *densidade* ela **passaria** — e passou por todos os gates existentes até S3. A densidade não é a restrição ativa. A patologia medida é outra: **degeneração de dispersão**. `confidence.score` 1 valor distinto/44; `origin_class` 1/44 e 1/8; `status` 1/44; `rationale.state` 1/8; `promotion_level` 1/8; `evidence_strength` 0 usos de 2 dos 5 valores.

**Um gate de degeneração é computável hoje e teria disparado no PILOT-001** — "reprovar quando um campo de classificação apresenta 1 único valor distinto em N ≥ 20 registros" —, ao passo que um limiar de densidade exigiria calibração sobre ≥2 corpora que não existem. Para propor um número de densidade seria preciso medir: densidade evidência/min e ADR/min em pelo menos 2 cursos de qualidade conhecida, um aprovável e um reprovável. Sem isso, qualquer limiar é arbitrário — **EVIDÊNCIA_INSUFICIENTE**.

---

## 3. PERGUNTA CENTRAL

> A circularidade medida (juiz derivado da skill, caso cego vindo do treino, provenance fechando contra si) é corrigível DENTRO desta arquitetura, ou exige REPLACE do Evaluator e do harness?

### O critério (antes da resposta)

Uma avaliação é **não-circular** se, e somente se, existir um artefato **A** tal que:

1. **A** é derivado exclusivamente de L0;
2. **A** é congelado por hash **antes** de qualquer estágio ler L0 e produzir L1;
3. a pontuação lê **A** e não lê o artefato sob teste.

Disso decorre o critério de decisão, que não depende de preferência:

> **IMPROVE** se a arquitetura já possui (i) um lugar nomeado para congelar **A**, (ii) um caminho de dados capaz de entregar L0 a quem escreve **A**, e (iii) um ponto de execução onde a violação de (1)–(3) possa reprovar o build — de modo que a correção seja *popular slots existentes e reordenar*, sem novo componente.
> **REPLACE** se qualquer um dos três for estruturalmente inexistente, isto é, se a correção exigir criar um componente novo ou romper o contrato de outros estágios.

### Aplicação do critério, item por item

**(i) Lugar nomeado para congelar A — EXISTE.** `held-out-registry.yaml` já tem os campos exatos: `registry_status`, `created_before_modeling`, `locked`, `cases: []`, `validation_policy.full_s4_allowed`. Existe um `held-out-registry.schema.yaml` (1.973 B) que valida sem erro. E **existe código de execução**: `validate_generated_skill.py` linhas 117–123 já reprova com `HELD_OUT_ACTIVE_WITHOUT_PREMODEL_LOCK` quando o registry está `ACTIVE` sem `created_before_modeling` e `locked`. O slot e a trava estão prontos — nunca foram populados (`cases: []`).

**(ii) Caminho de dados L0 → autor da rubrica — EXISTE e é trivial.** L0 é um arquivo de texto de 20.174 B com 180 marcas de tempo. `lesson-analyzer.md` §8 já modela um `analysis_request` com `source_files`. Entregar L0 a um estágio de rubrica não exige nada que a arquitetura não faça.

**(iii) Ponto de execução que reprova — EXISTE.** `SKILL.md` §H torna o preflight obrigatório; `validate_generated_skill.py` já retorna exit code 1 e imprime `RESULT: FAIL`. Acrescentar asserts (excerpt ∈ L0; `hidden_items` ∉ runtime-bundle; rubrica sem referência a ID interno) é adicionar linhas a um script existente, não criar um componente.

### Resposta

**Corrigível DENTRO da arquitetura. Três dos quatro defeitos são de ordem e de contrato, não de estrutura.**

- **Caso cego vindo do treino → IMPROVE.** O slot (`held-out-registry`) e a trava (linhas 117–123) existem e funcionam. O que faltou foi ordem de execução: `created_before_modeling: false`. Corrigir é popular o registry antes de L1 e deixar a trava que já está escrita fazer o trabalho.
- **Juiz derivado da skill → IMPROVE por reordenação + REPLACE de duas linhas de contrato.** A mudança é: `evaluator.md` §4 deixa de listar `generated-skill/` como referência de pontuação e passa a listar L0; e `evaluator_instructions` deixa de dizer *"Avaliar somente contra a metodologia extraída do PILOT-001"* (10/10 hoje). São edições em um prompt e num campo repetido 10 vezes. Nenhum outro estágio muda de contrato.
- **Provenance fechando contra si → REPLACE do referente do check.** Este **não** é corrigível por reordenação: o check compara duas saídas do mesmo produtor, e nenhuma ordem de execução conserta um referente errado. Precisa passar a ancorar em L0 (`source_excerpt` ⊂ arquivo de fonte) e a empacotar a evidência. Mas é REPLACE de **um check dentro do preflight**, não do harness.
- **Data leakage semântico → ADD, e é o único que a arquitetura não tem onde encaixar.** Nenhum campo, arquivo ou script atual mede "a resposta esperada é derivável do pacote entregue". O `isolation` existe como **declaração** (`hidden_items`), não como verificação — e mentiu em 10/10. É um verificador novo. Mesmo assim, cabe como mais um check do preflight existente, não como componente.

**O Evaluator NÃO deve ser classificado como REPLACE — e a razão é metodológica, não de gosto: ele nunca executou.** As 9 métricas estão em `null`, não há um único output bruto salvo, `evaluation.status: NOT_YET_VALIDATED`. Substituir um componente com **zero observações de comportamento** seria exatamente o defeito que esta auditoria mediu nos outros pontos: decidir por plausibilidade e chamar isso de conclusão. O que está medido e é substituível é o **contrato de entrada** e a **origem da rubrica** — não a máquina de avaliar.

**Critério de reversão declarado:** se, executada uma rodada com rubrica cortada de L0 e held-out congelado antes de L1, o Evaluator ainda produzir aprovação para artefatos com defeito conhecido — isto é, se os 6 achados que o Skeptic pegou passassem pela rubrica não-circular —, então o REPLACE do componente passa a ter base empírica. Antes disso, não tem.

---

## 4. RESPOSTAS DIRETAS

**(a) As 12 evidências nunca citadas (correção: 12, não 16): extração demais ou modelagem de menos?**
**Modelagem de menos, com uma extração correta** — li as 12: 4 são `EXAMPLE` (EV-0001 e os três arquétipos de agente EV-0020/0021/0022), 3 `CONCEPT` definicionais (chatbot vs automação vs agente, EV-0007/0008/0010), 2 `PRINCIPLE` (EV-0015 "sem ferramentas o agente é chatbot", EV-0023 "os três agentes formam sistema"), 1 `WARNING`, 1 `RATIONALE` — mas **EV-0003 é categoria `DECISION`** (*"atribuir gaps operacionais a agentes capazes de raciocinar, agir e fazer handoff, em vez de mais pessoas ou SOPs"*, com `reason_given` preenchido) e **não virou ADR nenhum**: uma decisão explícita do professor, com razão declarada, extraída corretamente e perdida na modelagem.

**(b) HELD_OUT é recuperável no PILOT-001? Quantos casos trabalhados a aula tem?**
**Não é recuperável, e não por burocracia:** a aula tem **1 único caso trabalhado de ponta a ponta** — SEG-008 "Live Build Challenge", `00:12:23–00:13:45`, **82 segundos = 9,1% da aula** — de modo que reservá-lo antes da modelagem elimina a própria demonstração da qual o workflow foi extraído; o resto são **14 ramos condicionais** (5 deles em `ADR-0003`), e segurar 1 ou 2 ramos daria n=1–2, sem poder estatístico algum. O menor curso que daria: mantida a densidade medida de **0,54 ADR/min e ~0,95 ramo condicional/min**, chegar a ~20 instâncias held-out a uma taxa de 20% exige ~100 instâncias decisórias, isto é, **≈ 8 a 12 aulas desta densidade (2–3 h de curso, um módulo completo)** — e a reserva tem de ser feita por ramo, sorteada e congelada por hash antes de L1.

**(c) Existe `baseline-summary.md` e só 2 de 10 testes o usam. O que falta para o SUMMARY_VS_SKILL rodar?**
Faltam quatro coisas concretas, todas ausentes hoje: **(1)** um pacote e um runner para o braço-B — existe **1 único `RUNNER_PROMPT.md`**, que manda *"Load only the attached runtime-bundle/"*, e nenhum arquivo com `arm` no nome em todo o material; **(2)** resolver a contradição de protocolo — `baseline-summary.md` vive em `judge-private/`, que o `FINAL_TEST_PROTOCOL.md` §3 manda manter privado, mas o braço-B precisa recebê-lo; **(3)** uma rubrica que o braço-B possa satisfazer — `expected_output.required_elements` exige *"ROBOT prompt"*, e o baseline **não menciona ROBOT** (verificado por grep), embora a fonte mencione em `9:52`, de modo que o braço-resumo é penalizado em `EXECUTION_QUALITY` (peso 0,3, mínimo 85) por não conhecer algo que a régua herdou do outro braço; **(4)** definição computável de 4 das 6 `comparison_metrics` — `DECISION_ACCURACY`, `MISSING_INPUT_ACCURACY`, `HALLUCINATION_RATE` e `TOTAL_SCORE` **não têm critério de rubrica correspondente** em nenhum dos 10 testes.

**(d) Os 4 testes que violam a §C: defeito de teste ou o schema permite o estado?**
**O schema permite o estado — é defeito de arquitetura, não de teste:** `test.schema.yaml` não tem nenhuma regra condicional ligando `expected_behavior.should_ask_user: false` aos `required_inputs`/`ask_user_if_missing` das decisões em `linked_decision_ids` (os 10 testes passam com **0 erros**), e o caso mais nítido é `ADR-0006`, que declara `ask_user_if_missing: [("Resultados de 3 a 5 testes", action: **STOP**)]` enquanto TEST-0006 e TEST-0007 não fornecem esse input e exigem `should_stop: false` — a suíte pune quem obedecer à regra que a skill entregou. O check **deveria estar no `validate_generated_skill.py`**, junto dos outros sete fechamentos (é resolução cruzada de IDs, exatamente o que as linhas 83–90 já fazem para `linked_decision_ids`), e hoje a §C existe apenas como prosa no `SKILL.md` §C.

**(e) A colisão de nome ADR causa dano real ou é cosmética?**
**Cosmética neste corpus, mas com um custo de acoplamento real:** o projeto usa `ADR` de forma consistente e única — 278 ocorrências de `ADR-NNNN`, sempre como *Atomic Decision Record*, definido em `SKILL.md:351` e no `title` do `decision.schema.yaml`, e **zero** ocorrências de "Architecture/Architectural Decision" em qualquer arquivo —, logo não há ambiguidade interna nem dano medido; o custo é externo e futuro: o padrão `^ADR-[0-9]{4,}$` está cravado em 4 schemas e no validador, então se o projeto passar a registrar decisões de arquitetura *do próprio compilador* (que é o que a Fase 3 vai produzir), os dois espaços de nome colidem em um regex já congelado.

**(f) Release limpo e workspace sujo convivendo: qual vira fonte de verdade?**
**O release**, e a medida decide sozinha: `01_TOOL/releases/v0.1.1/` contém **5 schemas, todos corretos, com nomes canônicos** e **nenhum dos 4 obsoletos**, enquanto `Course-to-Skill/course-to-skill-compiler/` mantém `decision.schema.yaml`, `workflow.schema.yaml` e `test.schema.yaml` com **os nomes canônicos apontando para versões superadas** — que reprovam o próprio output do piloto com **7 e 8 erros** de validação — além de 5 prompts divergentes (5/5 MD5 diferentes do release) e uma pasta vazia; o workspace hoje não é fonte de verdade de nada, é um histórico não versionado com nomes que mentem, e o único motivo para ele não ter causado dano é que ninguém apontou o validador para lá.

---

## 5. SÍNTESE

| Classificação | Pontos |
|---|---|
| **KEEP** | 1 Conceito · 8 Skeptic (com IMPROVE do contrato de saída) |
| **IMPROVE** | 2 Camadas · 3 Schemas · 4 Prompts · 7 Visual dependency · 9 Skill Compiler · 11 Suíte de testes |
| **REPLACE** | 5 Provenance (referente do check) · 6 Controle de inferência · 12 Hallucination control · 13 Data leakage · 15 Avaliação circular (mecanismo, não componente) |
| **ADD** | 14 Overfitting (instrumento inexistente) · gate de degeneração de dispersão |
| **REMOVE** | 5 prompts duplicados e 4 schemas obsoletos do workspace · `confidence.score` |
| **EVIDÊNCIA_INSUFICIENTE** | 10 Evaluator como componente (nunca executou) · limiar numérico de densidade (H7) · eliminação de L2 (n=1 aula) |

**Hipóteses:** H2, H3, H4 aceitas (H2 e H4 com correção que decide o efeito) · **H1 refutada no remédio** (o campo proposto já existe e já colapsou) · **H5 parcialmente refutada** (o Skeptic entregou 6/6 achados válidos sem L0) · **H6 refutada por inexistência do alvo** (nunca houve agentes por tipo de entidade; o alvo real é L1→L2, com delta medido de 1 campo) · **H7 aceita na premissa, refutada na métrica** (densidade não é a restrição ativa; dispersão é).

**Pergunta central:** corrigível dentro da arquitetura, pelo critério dos três requisitos — slot de congelamento, caminho de dados para L0 e ponto de reprovação **já existem**, e num caso o código de trava já está escrito e nunca foi acionado. REPLACE se aplica ao referente do check de provenance e à origem da rubrica; **não** ao Evaluator como componente, porque ele nunca executou e substituí-lo agora seria decidir por plausibilidade — o defeito que esta auditoria passou três fases medindo.

---

---

## 6. ADENDO — material novo apareceu na pasta auditada DURANTE esta fase

Na verificação final de integridade READ-ONLY, o diff de MD5 acusou **26 arquivos novos** em `Course-to-Skill-Compiler/`, ausentes no baseline da Fase 1. **Não foram criados por mim** — meus únicos destinos de escrita nesta sessão foram `/tmp/delta/` e `Course-to-Skill-Claude/docs/`. Nenhum arquivo preexistente foi alterado: os 218 do baseline permanecem com MD5 idêntico.

**O que é:** `02_PILOTS/PILOT-001/TEST-0007/`, criado em **2026-08-10 02:18**, com os dois braços da ablação:

| Braço | ZIP | arquivos | conteúdo |
|---|---|---|---|
| `PILOT-001-TEST-0007-ARM-A` | 23.203 B | 14 | pacote completo do candidato |
| `PILOT-001-TEST-0007-ARM-B` | 12.171 B | **12** | idêntico, **menos** `knowledge/decision-rules.yaml` e `knowledge/workflows.yaml` |

**Avaliação:** implementa corretamente a especificação. `TEST-0007.baseline.configuration` pede *"Ablated runtime: usar o mesmo `SKILL.md` e contexto geral, mas ocultar `knowledge/decision-rules.yaml` e `knowledge/workflows.yaml`"* — e o diff dos dois braços dá exatamente esses 2 arquivos, nada mais. `RUNNER_PROMPT.md` é byte-idêntico nos dois braços, o que satisfaz `same_prompt_required: true`. Os demais 12 arquivos são byte-idênticos entre os braços.

**Impacto nas classificações acima:** uma linha da resposta **(c)** fica desatualizada — quando medi, não havia nenhum arquivo com `arm` no nome; agora existe pacote de braço para **TEST-0007 (ABLATION)**. Isso **não** altera o restante de (c): o braço de **TEST-0008 (SUMMARY_VS_SKILL)** continua sem pacote — `baseline-summary.md` segue apenas dentro de `judge-private/`, sem runner próprio, e permanecem os outros três impedimentos (contradição de protocolo, `"ROBOT prompt"` exigido de um baseline que não o conhece, 4 de 6 `comparison_metrics` sem critério de rubrica). Nenhuma outra classificação, hipótese ou resposta desta fase muda.

**Ressalva de método:** a ablação de ARM-B remove as regras estruturadas mas **mantém o `SKILL.md`**, que já traz o procedimento ROBOT de 9 passos e os limiares (3–5 testes, 2 h/semana) — conforme observado no ponto 11 e em H7. A ablação é, portanto, **parcial por desenho**, e a margem de 5 pontos medirá a contribuição marginal de `decision-rules.yaml` + `workflows.yaml` sobre uma base que já contém boa parte da metodologia. Isso é uma propriedade do teste, não um defeito da execução.

---

**FIM DA FASE 2.** Nenhuma arquitetura nova foi escrita, nenhum código foi escrito, nenhum arquivo original foi criado, alterado, movido ou apagado por mim.
