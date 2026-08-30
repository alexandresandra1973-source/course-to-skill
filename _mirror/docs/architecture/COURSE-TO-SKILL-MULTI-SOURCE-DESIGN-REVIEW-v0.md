# COURSE-TO-SKILL MULTI-SOURCE — DESIGN REVIEW v0

**Objeto:** `COURSE-TO-SKILL MULTI-SOURCE — ARCHITECTURE PROPOSAL v0`
**Data:** 29/08/2026
**Escopo:** somente desenho. Nenhuma implementação, recompilação ou correção de N1–N9.
**Não alterado nesta rodada:** Compiler atual · `compiler-v2-v0.2.2` · `compiler-s3-v0.1.1` · `cts/` · runners · pilotos · N1–N9 · freezes · manifests · `_mirror/` · Drive · Git.
**Classificação final:** `ARCHITECTURE_REVISION_REQUIRED` (justificativa na §10).

Método: cada achado é confrontado contra estado **medido** do projeto. Onde não há medição, o achado é declarado como hipótese e rotulado.

---

## 1. ACCEPTED PRINCIPLES

Estes princípios da proposta sobrevivem à confrontação e devem ser preservados na revisão.

**A1 — Não transformar o Compiler atual em multi-source.**
Correto e é a melhor decisão do documento. O Compiler satisfaz hoje um invariante estreito e útil: uma fonte por execução. Alargá-lo transformaria multi-fonte em reescrita, invalidaria os quatro pilotos como baseline e destruiria a única classificação positiva que existe (`READY_FOR_CONTROLLED_USE` condicional para fonte única).

**A2 — Fronteira `SOURCE → COMPILE ISOLATED → SEALED SOURCE PACKAGE → FUSION`.**
A topologia está certa: isolamento por execução converte multi-fonte de problema de compilação em problema de composição. **Aceito com três correções obrigatórias** (§4, R1–R3): o nó `SEALED` não tem definição operacional, falta um estágio entre compilação e selo, e falta canal de retorno para defeito descoberto na fusão.

**A3 — Deduplicar representação não é deduplicar proveniência.**
É a regra mais importante do documento. Precisa virar invariante mecânico, não princípio escrito (§4, R7).

**A4 — Separação DETECTION / DECISION / ENFORCEMENT.**
Correta e alinhada a uma disciplina que o projeto já pagou para aprender: duas pistas de saída (`INVALID`/exit 2 para instrumento, `FAIL`/exit 1 para candidata). Detecção que decide é a mesma família de defeito.

**A5 — Proibição de `latest source wins`.**
Correta, e reforçada por medição própria: no Item 2 a ordem entre duas versões foi provada por identidade de conteúdo (sha256/blob/commit), não por `mtime` — e `mtime` está desqualificado do lado DrvFs/Drive. Uma regra de precedência temporal apoiada em metadado repetiria o erro. **Ressalva:** proibir é negativa; a positiva não está escrita (§4, R12).

**A6 — Módulos definidos por CAPACIDADE, não por fonte; lista não congelada na v0.**
Correto nos dois pontos. Congelar a lista de módulos na v0 seria decidir por plausibilidade antes de qualquer medição.

**A7 — Carregamento seletivo como requisito de viabilidade, não otimização.**
Sustentado por número medido: piso de **411.658 tokens** por invocação no P003, **~493 tokens/regra**, crescimento **linear** na duração do curso. Um corpus de dezenas de fontes não cabe. **Ressalva grave:** o desenho atual do carregamento colide com o contrato de runtime vigente (§2, C4).

**A8 — `filesystem scan ≠ corpus audit`.**
A proposta incorporou a lição corretamente. Esta revisão vai além: transforma a lição em **requisito de esquema** (§3, M6).

---

## 2. CHALLENGED PRINCIPLES

**C1 — `SEALED SOURCE PACKAGE` apoia-se na operação que o projeto tem histórico medido de errar.**

Selar é uma alegação de proveniência. Três defeitos medidos dizem que o projeto ainda não sabe selar:

- `compiler-v2-v0.2.0` tem **11/15 hashes idênticos e 4 ALTERADOS**, porque v0.2.0 e v0.2.1 **compartilham o diretório `compiler-v2/`** e os arquivos foram sobrescritos no lugar. O `ADITIVO_NAO_MUTACAO` protegeu o arquivo de **registro**, não o **conjunto selado**.
- O `compiler-v2-v0.2.2/FREEZE-RECORD.yaml` é cópia byte-idêntica do registro 0.2.0 e **falha contra o próprio diretório em que está**.
- **N1**: os três bundles declaram `compiler-s3/0.1.0` enquanto o repo é v0.1.1; `RT-CITE-001` e `questions.yaml` nunca chegaram a produto.

Consequência arquitetural: a fronteira inteira pendura-se num nó cuja definição operacional não existe. Não é objeção teórica — é o elo mais fraco *já medido* do sistema.

**C2 — O grafo trata ancoragem como aresta única, e ela são três coisas.**

Medido: `EXISTIR` 226/226 (100%) · mecânica (quote reencontrada verbatim em L0) 139/226 (**61,50%**) · substância 12/226 (**5,3%**). São três predicados diferentes sobre a mesma aresta. Enquanto `evidence → segment` for aresta única, a fusão não sabe qual delas está consumindo — e o consumidor lê 100% quando o número que importa é 5,3%.

**C3 — `Claim` como "unidade semântica central" é rótulo largo demais e cria risco de perda de proveniência.**

Ver §3/M1 e §4/R7. Claim serve como unidade de **comparação**. Se virar unidade de **proveniência** ou de **emissão**, o projeto perde o único elo verificável que tem (evidência↔span) e passa a fundir paráfrases.

**C4 — Carregamento seletivo contradiz o contrato de runtime vigente. A proposta não viu.**

Medido: o `SKILL.md` traz `## LOAD ORDER — MANDATORY` (carrega tudo, sempre) e `required_executable_resources` obrigatórios, com `fail_closed_on_missing_executable_resource: true`. Esse contrato é o que fez o braço ablado do TEST-0007 **recusar contratualmente** a tarefa — comportamento medido e registrado.

Sob carregamento seletivo, todo módulo não carregado é, pelo contrato atual, recurso ausente → **recusa**. Ou o Skill Pack novo opera sob contrato diferente (e então não é comparável a nenhum piloto), ou o carregamento seletivo não funciona. **Não há terceira opção, e a decisão não está no documento.**

**C5 — Precedência `scope-aware` foi desenhada para um corpus que não existe.**

Medido: `precedence: UNDEFINED` em **93,3% (P002) · 88,7% (P003) · 96,9% (P004)**. Nenhum piloto tem material para derivar escopo. Uma política que exige escopo será inaplicável no caso dominante, e o modo de falha previsível é o sistema **inventar escopo para poder decidir** — que é o defeito original auditado neste projeto (preencher lacuna com plausível). A política tem de ser desenhada para o caso dominante: sem escopo declarado, precedência é indeterminada e o conflito escala.

**C6 — A taxonomia de 7 relações mistura dois eixos ortogonais.**

`EXACT_DUPLICATE` e `SEMANTIC_DUPLICATE` são sobre **representação**. `CORROBORATES`, `COMPLEMENTS`, `SPECIALIZES`, `CONTRADICTS` são sobre **conteúdo**. `UNRELATED` é ausência de ambos. Um par pode ser semanticamente duplicado **e** corroborante; como rótulo único, a taxonomia força escolha falsa e perde informação (§4, R8).

**C7 — `UNRESOLVED` faz o trabalho de dois estados.**

"Ainda não adjudicado" ≠ "adjudicado e indecidível". O projeto já pagou por essa distinção uma vez (INVALID × FAIL). Sem separá-la, backlog e impossibilidade viram o mesmo número (§4, R9).

**C8 — A classificação pareada é quadrática e `n` é instável.**

Da escala medida do P003 (2.463 evidências → 835 regras), a faixa plausível de claims por fonte é 835–2.463. Pares intra-fonte: C(835,2)=**348.195**; C(2.463,2)=**3.031.953**. Duas fontes nessa escala (intra A + intra B + cruzados): piso **1.393.615**, teto **12.130.275**. A 100 tokens por par — preço otimista — o piso dá ~139 milhões de tokens por fusão, ~340× o piso de invocação da Skill do P003.

Cresce onde dói: com `k` fontes, pares ≈ C(k,2)·n² + k·C(n,2). No piso: 2 fontes 1,39M · 3 fontes 3,14M · 5 fontes 8,71M — **6,25× mais caro exatamente na direção que o caminho existe para habilitar.**

E `n` não é propriedade da fonte: o teto por chamada **medido** diz que o mesmo texto em 3 chamadas rende **1,5×** mais que em 1. Se `n` varia 1,5×, `n²` varia **2,25×**. Não se pré-declara limiar sobre população cujo tamanho se move com o particionamento das chamadas — e limiar pré-declarado é regra não negociável desta frente.

**C9 — A fusão é tratada como operação em lote; com dezenas de fontes ela é incremental por necessidade.**

Adicionar a fonte `n+1` custa O(n) comparações, não O(1). Sem cache de decisões chaveado por par de hashes, o custo de manutenção cresce sem teto e a fusão deixa de ser reexecutável.

---

## 3. MISSING ARCHITECTURAL ELEMENTS

**M1 — `SPAN` como entidade de primeira classe, com arestas tipadas.**
Substituir a aresta única por três: `LOCATED_IN` (o span existe) · `QUOTED_FROM` (quote reencontrável verbatim, em língua da fonte) · `SUPPORTED_BY` (a substância sustenta a asserção). Sem isso, 100% / 61,50% / 5,3% continuam colapsando num campo só.

**M2 — `LANGUAGE` como campo obrigatório, e campo em LÍNGUA DA FONTE ao lado do traduzido.**
Existe `PENDENCY-SOURCE-LANGUAGE-FIELD` e **zero campo de língua no schema**. Em fonte única isso degradou medição (falhas medidas de PT×EN). Em multi-fonte produz **falsa deduplicação e falsa contradição diretamente**: duas claims traduzidas para o mesmo idioma parecem mais próximas do que a origem autoriza. É bloqueante, não cosmético.

**M3 — `SCOPE` / `ASSERTION CONTEXT` como objeto endereçável e comparável.**
Se precedência é scope-aware e `CONTEXT_SPLIT` é estado de conflito, escopo precisa suportar as relações *igual · disjunto · contém · sobrepõe*. String livre não computa nenhuma delas.

**M4 — `SOURCE PROFILE` declarado externamente.**
Fatos da fonte (data de publicação **da fonte**, versão do produto ensinado, autor, língua), não julgamento de qualidade. Sem isso, precedência não tem insumo e reentra por `latest-wins` disfarçado. Deve ser **externo à fonte**: fonte que declara a própria autoridade é auto-referência — mesma família do N5 (o `files:` do manifesto do P002 lista a si mesmo e diverge).

**M5 — `COMPILE-TRACE` como membro obrigatório do Source Package.**
Medido: **compile-trace NÃO EXISTE de nenhum piloto**, e o PASS 1 vive nos runners, fora de qualquer FREEZE-RECORD. Se o pacote não carrega o traço, a fusão recebe conclusões sem poder auditar como foram produzidas — e herda opacidade que hoje é local.

**M6 — `DECLARATION SPACE` declarado, incluindo mensagem de commit.**
A taxonomia que governa o espelho — `GIT_NATIVE_BY_DESIGN`, os 14 arquivos, a direção D2 (Drive→Git), a proibição de `--delete` — **não existe em arquivo nenhum: vive só na mensagem do commit `378d764`**. Qualquer auditor que varra arquivos não a encontra. Requisito: o Source Package declara **onde** suas declarações vivem (ADR · manifest · errata · freeze record · mensagem de commit), e o auditor de corpus varre todos esses espaços, com controle positivo por espaço.

**M7 — Terceiro pacote: `SKILL PACK ≠ FUSION PACKAGE`.**
Fusion Package é o resultado da deliberação (claims, relações, decisões, conflitos abertos). Skill Pack é o artefato de consumo. Colapsá-los faz o consumidor carregar deliberação e reintroduz o problema de orçamento. Três níveis, três selos: `SOURCE PACKAGE → FUSION PACKAGE → SKILL PACK`.

**M8 — Estágio de blocagem não-gerador antes de qualquer classificação pareada.**
Nenhum par chega a um modelo sem passar por filtro barato de candidatura. **Ressalva honesta:** blocagem é matcher mecânico, e matcher mecânico já falhou **8 vezes** neste projeto (acento · PT×EN · filtro ao montar e não ao procurar · campo `function` · português sem diacrítico · ordem e adjacência · busca por forma literal · varredura que não alcança mensagem de commit). Portanto o blocador entra como **instrumento medido**, com recall pré-declarado e controle positivo — jamais como otimização silenciosa.

**M9 — Modelo incremental de fusão + política de invalidação em cascata.**
Cache de relação chaveado por `(hash_A, hash_B, versão_do_juiz)`. E política declarada para quando uma fonte é recompilada: quais relações morrem, o que é recomputado, o que fica marcado stale. Sem isso o sistema fica permanentemente desatualizado ou permanentemente recomputando.

**M10 — Estado de retorno `SOURCE_PACKAGE_DEFECT_FOUND_IN_FUSION`.**
A fronteira é unidirecional no papel e bidirecional na prática: a fusão vai descobrir defeitos que pertencem à fonte. Sem canal de retorno explícito, a tentação é consertar no fundidor — que é exatamente a contaminação que a fronteira existe para impedir. A fusão **para**, reporta, e a recompilação da fonte é ato separado com selo novo.

---

## 4. REQUIRED CHANGES

**R1 — Definir `SEALED` operacionalmente, sobre o CONJUNTO.**
Manifesto de membros com hash + contagem + **proibição de membros extras**; selo auto-verificável no diretório em que vive (defeito exato do v0.2.2); **proibição de compartilhar diretório entre versões seladas** (defeito exato do v0.2.0/v0.2.1). Verificador próprio, com canário cujas fixtures reproduzem esses dois defeitos e **TÊM de falhar**.

**R2 — Nomear o estágio faltante e fixar o conteúdo mínimo do Source Package.**
`L0 selado + temporal-map + EVIDENCE + CLAIMS SELADAS + bundle + COMPILE-TRACE + manifesto de membros + declaration space`.

**R3 — Adicionar `SOURCE_PACKAGE_DEFECT_FOUND_IN_FUSION` (M10).**

**R4 — Identidade global por qualificação, nunca por renumeração.**
Medido: **N9** (`evidence_id` colide — os três pilotos numeram de EV-0001) e **N4** (`artifact_id: PILOT-002-SKILL-COMPILATION-MANIFEST` nos **três** manifests). A colisão está em **dois níveis do grafo**. Solução compatível com "não alterar": id global = par `(source_package_hash, local_id)`, atribuído no **envelope** do pacote, fora do artefato. Renumerar pilotos existentes fica **proibido** — violaria freeze e reescreveria histórico.

**R5 — Tipar a aresta de ancoragem (M1) e declarar qual tipo cada consumidor usa.**

**R6 — Tornar `lang` obrigatório e manter campo em língua da fonte (M2).**

**R7 — `Claim` rebaixada a unidade de COMPARAÇÃO, com três travas.**
(a) `claim.evidence_refs` é conjunto não vazio; fusão sobre claims é **união** de refs, nunca escolha — a regra de ouro vira invariante mecânico.
(b) Toda claim carrega ao menos uma `anchor_quote` verbatim em língua da fonte, com span. Claim sem quote nasce marcada e **não pode entrar em DECISION de contradição** — só em DETECTION.
(c) **As claims são seladas dentro do Source Package.** A fusão **nunca regenera claim**. Sem isso, a variância medida de 1,5× do extractor entra na fusão e nada acima dela é reprodutível.

**R8 — Taxonomia em dois eixos, com direção explícita.**
`representation: {IDENTICAL, EQUIVALENT, DISTINCT}` × `content_relation: {CORROBORATES, COMPLEMENTS, SPECIALIZES, CONTRADICTS, SUPERSEDES, UNRELATED, INDETERMINATE}`.
Acréscimos e porquês:
- `SPECIALIZES` é **direcional** — direção é campo, não convenção de ordem do par; do contrário a relação depende da ordem de varredura e a fusão deixa de ser reprodutível.
- `SUPERSEDES` — contradição em que a supersessão está sinalizada **no conteúdo** (não em metadado). Sem categoria própria, `CONTRADICTS` vira balde e a decisão reentra por `latest-wins`.
- `INDETERMINATE` ≠ `UNRELATED`. `UNRELATED` é afirmação; `INDETERMINATE` é ausência de poder. Sem essa separação, todo par não decidido cai em `UNRELATED` e a informação some em silêncio. É a mesma lição do `METHOD_NOT_DEFINED`, que já funcionou.
- Equivalência atravessando tradução é registrada no eixo de representação **com marca de tradução**, nunca como `EQUIVALENT` limpo.
- Falso acordo (mesma superfície, escopo diferente) precisa de estado explícito.

**R9 — Estados de conflito revisados.**
`NOT_YET_ADJUDICATED` · `UNDECIDABLE_BY_DESIGN` · `CONTEXT_SPLIT` · `BOTH_VALID` · `PRECEDENCE_DECIDED` · **`ESCALATED_TO_HUMAN`** · **`DEFERRED_TO_RUNTIME`** · `MISSING_REQUIRED_INPUT` · `CLAIM_REJECTED`.
- `ESCALATED_TO_HUMAN` com dono e **pergunta formulada**. É o comportamento que **funcionou de verdade**: no P003 a `precedence: UNDEFINED` mordeu (R-0386 contra a regra de frase), a Skill **parou e pediu decisão**. É o ativo do sistema; a proposta não tem estado para ele.
- `DEFERRED_TO_RUNTIME` para conflito que só resolve com contexto do usuário — o caso "marca de terceiro sob distribuição exclusiva" do P003 é exatamente isso. Implica que o Skill Pack carregue conflitos abertos **como perguntas**, não como regras.
- `CLAIM_REJECTED` com travas: motivo enumerado obrigatório · evidência preservada · rejeição **aditiva e reversível**, nunca remoção · **proibido rejeitar por não-ancoragem isolada** (rejeitaria 94,7% do corpus por construção).

**R10 — Blocagem obrigatória antes da classificação pareada (M8), com recall pré-declarado.**

**R11 — Medir a variância do juiz de relações ANTES de fixar qualquer limiar.**
Teste-reteste nunca foi feito neste projeto, e a lição do teto degenerado já está paga: com teto de 3,0 e piso **relativo** de 5%, limiar "válido" pode estar dentro do ruído. Um classificador de relações sem variância medida produz limiares indistinguíveis de ruído.

**R12 — Escrever a política positiva de precedência, dimensionada para o caso dominante.**
Sem escopo declarado (88,7–96,9% hoje) → `INDETERMINATE` + escalada. Precedência ordena por **(escopo, dimensão)**, nunca globalmente: ordenação global de fontes é `latest-wins` com outro nome, trocando data por autoridade.

**R13 — Resolver o contrato de carregamento (C4) antes de qualquer código de Skill Pack.**

**R14 — L3 (proveniência) deixa de ser nível de carregamento e vira obrigação de resolubilidade.**
Módulos por capacidade agregam claims de várias fontes; logo o módulo não tem proveniência única. Se L1 for carregável sem L3, o consumidor consome material multi-fonte sem saber de onde veio. L3 sempre resolvível sob demanda, e toda saída cita o que usou.

**R15 — Grafo de dependência entre módulos é DAG, verificado por script, com canário que planta ciclo e TEM de falhar.**

**R16 — Runner próprio para o caminho novo.**
Medido: os campos do portão nos manifests do P003/P004 foram escritos pelos **runners**, não pelo `coverage_gate` selado; o PASS 1 vive nos runners e fora de qualquer freeze. Reusar runners herda ambiguidade de autoria. Runner novo, versionado, sem compartilhar diretório com nada selado, modelo fixado em `claude-sonnet-5`.

---

## 5. DECISIONS TO FREEZE BEFORE IMPLEMENTATION

Em ordem de dependência lógica. Nenhuma linha de código antes de D1–D6.

| # | Decisão | Depende de | Por quê é bloqueante |
|---|---|---|---|
| D1 | Definição operacional de `SEALED` + verificador + canário (R1) | — | A fronteira inteira apoia neste nó, e há 3 defeitos de selo medidos |
| D2 | Identidade global `(source_package_hash, local_id)`; proibição de renumerar (R4) | D1 | Colisão medida em 2 níveis (N9, N4); é pré-condição do formato |
| D3 | Conteúdo mínimo do Source Package, incluindo compile-trace e claims seladas (R2, R7c) | D1, D2 | Define o formato emitido e a reprodutibilidade da fusão |
| D4 | `lang` + campo em língua da fonte (R6) | D3 | Sem ele, falsa dedup e falsa contradição por construção |
| D5 | Claim aditiva ou substitutiva na emissão | D3 | Decide se o piso de 411.658 tokens sobe ou desce |
| D6 | Blocagem não-geradora existe, com recall pré-declarado (R10) | D5 | Diferença entre implementável e não (C8) |
| D7 | Taxonomia em dois eixos, direção, `INDETERMINATE`, `SUPERSEDES` (R8) | D4 | Define o schema de relação |
| D8 | Estados de conflito revisados e travas do `CLAIM_REJECTED` (R9) | D7 | Define o schema de decisão |
| D9 | Política positiva de precedência para o caso dominante (R12) | D7, D8 | Substituto de `latest-wins`; hoje só existe a proibição |
| D10 | Contrato de carregamento do Skill Pack × `LOAD ORDER — MANDATORY` (R13) | — | Contaminação direta do runtime atual |
| D11 | Instrumento de ancoragem: arestas tipadas, rubrica, amostra, limiar, dimensão de fonte (R5) | D2 | Sem ele não se mede se a mudança funcionou |
| D12 | Teste-reteste do juiz de relações e limiar de variância (R11) | D7 | Limiar sem variância medida é indistinguível de ruído |
| D13 | Modelo incremental de fusão + invalidação em cascata (M9) | D3 | Só aparece com dezenas de fontes, e aí é tarde |
| D14 | Declaration space, incluindo mensagem de commit (M6) | D3 | Precedente medido: taxonomia do espelho só existe em commit |
| D15 | Teto de orçamento por rodada; modelo fixado `claude-sonnet-5` (R16) | — | Política de custo de 19/08 + ocorrência "Advising using Fable 5" de 29/08 |

**Explicitamente NÃO congelar agora:** a lista de módulos (correto na proposta) e a **lista final de relações** — a taxonomia entra como *candidata*, sujeita a poda pelo piloto. Relação que não se consegue plantar de forma plausível não merece existir.

---

## 6. PILOT-MS-001 REVIEW

### 6.1 Veredito

`PILOT-MS-001` é o experimento certo para **DETECTION e para a taxonomia**. Não é o próximo experimento certo para a **arquitetura**, por duas razões:

1. **Não toca o elo mais fraco.** O nó `SEALED` é onde há três defeitos medidos, e o microcorpus não o exercita.
2. **Testa duas coisas novas ao mesmo tempo.** Corpus multi-aula **nunca foi testado** (os quatro pilotos são vídeo único com timeline contínua). `PILOT-MS-001` salta direto para duas fontes independentes, misturando *manuseio multi-documento* com *arbitragem entre autoridades*. Quando falhar, não se saberá qual dos dois falhou.

### 6.2 Sequência recomendada

**PILOT-MS-000A — SEAL CANARY.** Sem corpus novo, sem chamada de modelo. Fixtures que reproduzem os defeitos já conhecidos e que **TÊM de falhar**: (a) duas versões compartilhando diretório com sobrescrita no lugar; (b) FREEZE-RECORD que não valida contra o diretório em que vive; (c) manifesto que se auto-referencia (N5); (d) bundle cujo carimbo de produtor diverge do produtor real (N1). Se o selo novo não pega os quatro, nada acima dele vale. Custo próximo de zero.

**PILOT-MS-000B — MULTI-AULA, MESMO AUTOR.** Duas aulas sequenciais do mesmo curso. Exercita Source Package, identidade qualificada, blocagem, fusão e Skill Pack **sem** o problema de DECISION (precedência natural pela ordem). Isola encanamento de arbitragem e fecha o buraco real: corpus multi-aula nunca testado.

**PILOT-MS-001 — DUAS MICROFONTES PLANTADAS.** Só depois, com as adições abaixo.

### 6.3 O plantio proposto está incompleto

O documento planta 9 itens (1 duplicata semântica · 1 corroboração · 1 complemento · 1 especialização · 1 contradição real · 1 contradição aparente · 1 exclusivo A · 1 exclusivo B · 1 anti-pattern). Cobre **5 das 7 relações**. Faltam:

1. **`UNRELATED` — controle negativo.** É a adição mais importante do pilot. Sem ele, um classificador que responde "relacionado" a tudo tira 9/9.
2. **`EXACT_DUPLICATE`** — sem fixture, a categoria é asserção.
3. **Falso ACORDO** (mesma superfície, substância diferente). O plantio tem contradição aparente; falta o espelho — e, com 8 falhas medidas de casamento por forma, é o modo de falha mais provável.
4. **A colisão de id, plantada de propósito.** As duas fontes numeram de `EV-0001` internamente. Se o microcorpus não reproduz a colisão, não testa o mecanismo medido quebrado.
5. **Par cujo resultado correto é `INDETERMINATE`** — canário no sentido da casa: fixture que TEM de falhar se o sistema devolver rótulo confiante. É o teste direto da proibição de `latest-wins`: o que ele faz **em vez** disso, e se o artefato tem estado para isso.
6. **Supersessão legítima sinalizada NO TEXTO**, não em metadado — coerente com o Item 2, onde a ordem saiu de identidade de conteúdo.
7. **Duas fontes em línguas diferentes dizendo o mesmo** — testa M2/R6 diretamente.
8. **Duas escalas** (ex.: ~30 e ~60 claims). **Mede** o expoente de crescimento em vez de assumi-lo, e responde C8 pelo preço de um microcorpus em vez de um P003.

### 6.4 Critérios de parada, pré-declarados

**PASS** — todas as relações plantadas recuperadas na taxa declarada · `UNRELATED` e `INDETERMINATE` não confundidos entre si · canários falharam como desenhado · **duas execuções independentes produzem conjuntos de claims dentro da tolerância declarada** (reaproveita a forma do protocolo de dois clones do N6, que já provou ter poder) · zero número digitado à mão · relatório gerado por script.

**KILL** — ancoragem mecânica cai abaixo de 61,50% · variância do conjunto de claims em 3 rodadas excede o 1,5× medido do extractor · crescimento entre as duas escalas sai quadrático sem blocador · variância do juiz de relações (R11) maior que a menor separação entre categorias.

**ORÇAMENTO** — teto absoluto de chamadas e tokens declarado antes, que **interrompe** a rodada.

**Trava:** o pilot **não pode passar por ser pequeno**. A extrapolação de escala é critério de aprovação, não trabalho posterior.

---

## 7. REGRESSION / ISOLATION RISKS

Pontos em que a arquitetura, como escrita, ainda contaminaria ou exigiria alterar o pipeline atual.

**I1 — `source_id` no EVIDENCE (ALTO).** As chaves reais do `EVIDENCE.jsonl` não têm dimensão de fonte. Adicionar dimensão ao schema altera o compilador e invalida os pilotos como baseline. **Único caminho compatível com "não alterar": atribuir `source_id` no envelope do pacote**, fora do artefato (R4).

**I2 — Tentação de "consertar" N9/N4 por renumeração (ALTO).** Violaria freeze e reescreveria histórico. Regra explícita: **nunca renumerar; sempre qualificar.**

**I3 — Camada de claim rodando sobre pilotos selados (ALTO).** Gerar claims a partir do EVIDENCE dos pilotos cria artefato novo dentro do escopo de um freeze. Tem de nascer como pacote **aditivo, com selo próprio**, referenciando o piloto por hash — nunca dentro dele. É a aplicação do `ADITIVO_NAO_MUTACAO` no nível do conjunto, que é justamente onde ele já falhou.

**I4 — Carregamento seletivo × contrato fail-closed (ALTO).** Ver C4/R13. Mexer no contrato muda o comportamento medido dos pilotos — foi exatamente o mecanismo do TEST-0007.

**I5 — Reuso de runners (MÉDIO).** PASS 1 vive nos runners, fora de freeze; campos do portão do P003/P004 escritos pelos runners e não pelo `coverage_gate` selado. Reusar herda ambiguidade de autoria (R16).

**I6 — Compartilhamento de diretório entre pacotes selados (MÉDIO-ALTO).** Defeito já materializado no v0.2.0/v0.2.1. Multi-fonte multiplica diretórios; a política tem de **proibir** o compartilhamento, não só registrar o freeze.

**I7 — Revarredura do portão (MÉDIO).** Medido: **nunca executou em nenhum piloto**; a margem do portão de cobertura caiu de 17,1 para 5,4 pontos ao longo dos três. Um corpus multi-fonte é maior que qualquer piloto e provavelmente aciona pela primeira vez maquinaria testada só por canário. Declarar antes o que acontece quando ela dispara.

**I8 — Workflows de passo único e DISPATCH (MÉDIO).** 25–35% dos workflows têm passo único, defeito diagnosticado e nunca consertado; o DISPATCH ocupava 90% do `SKILL.md` do P003. Fundir corpora sem consertar isso multiplica ruído no roteador — e o roteador é o novo ponto único de falha.

---

## 8. OPEN QUESTIONS

**Q1 — Claim é aditiva ou substitutiva na emissão?** Se aditiva, o piso de 411.658 tokens sobe e o Skill Pack fica pior. Se substitutiva (regra vira vista derivada de claims), pode cair. Não decidido no documento.

**Q2 — Existe blocador barato e confiável neste domínio?** É a pergunta que decide se o caminho é implementável. Recall do blocador é mensurável no `PILOT-MS-001` com pares plantados — mas se o único blocador viável for lexical, ele é da família que já falhou 8 vezes.

**Q3 — Escopo é derivável, ou só declarável?** Com `precedence: UNDEFINED` em ~90%, a hipótese de trabalho tem de ser "só declarável". Se for, quem declara, e quando?

**Q4 — O que a fusão faz com claim não ancorada em substância?** Se 94,7% não têm ancoragem substantiva, rejeitá-las esvazia o corpus e aceitá-las faz a precedência arbitrar ruído. Não há resposta boa no documento; é decisão de produto.

**Q5 — Skill Pack roteia por capacidade — e quando o roteamento erra?** Hoje, carregando tudo, roteamento errado ainda pode achar a regra. Com carregamento seletivo, roteamento errado significa **a regra existe e nunca é vista**, e a saída fica indistinguível de "o corpus não cobre" — a mesma classe de risco de produto já nomeada (medição quebrada produz o mesmo texto que achado verdadeiro). Qual é a métrica de recall de roteamento e seu controle positivo?

**Q6 — Autoridade da fonte é declarada ou derivada?** Se derivada da qualidade das claims dela, fecha ciclo: precedência decide entre claims, claims determinam autoridade, autoridade decide precedência. Tem de ser declarada externamente e congelada antes da fusão.

**Q7 — Qual é o critério de aposentadoria de uma fonte?** Com dezenas de fontes, algumas ficam obsoletas. Remover viola preservação; manter degrada a fusão. Provável resposta: marcação aditiva (`SUPERSEDED_BY`), nunca remoção — mas não está escrito.

**Q8 — O Fusion Package é descartável ou histórico?** Se descartável, precisa ser reconstruível por hash do conjunto de entrada. Se histórico, entra na disciplina de selo e o volume cresce com C(k,2).

---

## 9. ARQUITETURA REVISADA PROPOSTA

Alterações mínimas sobre a v0. O núcleo é preservado.

### 9.1 Fronteira (5 nós, não 4)

```
SOURCE
  → COMPILE ISOLATED            (uma fonte por execução, Compiler atual intocado)
  → PACKAGE ASSEMBLY            [NOVO] monta o conjunto: L0 + temporal-map +
                                 EVIDENCE + CLAIMS + bundle + COMPILE-TRACE +
                                 declaration space + manifesto de membros
  → SEAL                        [DEFINIDO] selo sobre o CONJUNTO, auto-verificável
                                 no lugar, sem diretório compartilhado
  → FUSION                      (opera só sobre pacotes selados; nunca regenera claim)

  ⟵ SOURCE_PACKAGE_DEFECT_FOUND_IN_FUSION   [NOVO] canal de retorno: fusão PARA,
                                             recompilação é ato separado com selo novo
```

### 9.2 Grafo revisado

```
source
  → source_profile            [NOVO, externo]
  → artifact
  → segment
  → span                      [NOVO, primeira classe]
  → evidence      --{LOCATED_IN | QUOTED_FROM | SUPPORTED_BY}--> span   [arestas tipadas]
  → claim                     [união de evidence_refs; anchor_quote obrigatória;
                               lang + texto em língua da fonte; SELADA no pacote]
  → rule / workflow / anti-pattern
  → module                    [por capacidade; L3 sempre resolvível]
  → skill pack
```

### 9.3 Três pacotes, três selos

| Pacote | Natureza | Endereçamento | Autoridade |
|---|---|---|---|
| `SOURCE PACKAGE` | imutável | hash do conjunto | **autoritativo** sobre conteúdo de fonte |
| `FUSION PACKAGE` | derivado, recomputável | hash + `source_set` ordenado de hashes | autoritativo só sobre **relações e decisões** |
| `SKILL PACK` | artefato de consumo | hash + `fusion_package_hash` | **não autoritativo**; toda saída resolve para trás |

### 9.4 Relação em dois eixos

```
representation : IDENTICAL | EQUIVALENT | DISTINCT     (+ flag translated_comparison)
content        : CORROBORATES | COMPLEMENTS | SPECIALIZES(direção) |
                 CONTRADICTS | SUPERSEDES | UNRELATED | INDETERMINATE
```

### 9.5 Conflito

```
NOT_YET_ADJUDICATED | UNDECIDABLE_BY_DESIGN | CONTEXT_SPLIT | BOTH_VALID |
PRECEDENCE_DECIDED  | ESCALATED_TO_HUMAN    | DEFERRED_TO_RUNTIME |
MISSING_REQUIRED_INPUT | CLAIM_REJECTED (aditivo, reversível, motivo enumerado)
```

### 9.6 Pipeline de relação (obrigatório)

```
claims seladas → BLOCAGEM não-geradora (recall pré-declarado, controle positivo)
              → DETECTION (classifica só candidatos)
              → DECISION  (precedência por (escopo, dimensão); sem escopo → INDETERMINATE + escalada)
              → ENFORCEMENT
```

---

## 10. CLASSIFICAÇÃO FINAL

### `ARCHITECTURE_REVISION_REQUIRED`

Não é rejeição. O núcleo está certo e deve ser preservado: a fronteira com isolamento, a claim como unidade de comparação, a separação DETECTION/DECISION/ENFORCEMENT, a proibição de `latest-wins`, os módulos por capacidade e a regra de ouro sobre proveniência. A revisão é de **completude e definição**, não de direção.

A classificação é `ARCHITECTURE_REVISION_REQUIRED` por **quatro achados bloqueantes**, cada um verificável contra estado medido:

**1. O nó `SEALED` não tem definição operacional, e há três defeitos de selo já medidos.**
`compiler-v2-v0.2.0` com 4 arquivos alterados por diretório compartilhado · `FREEZE-RECORD` do v0.2.2 que falha contra o próprio diretório · N1 (bundles declarando `compiler-s3/0.1.0`). A fronteira inteira apoia num nó indefinido cuja operação o projeto tem histórico de errar.

**2. O carregamento seletivo do Skill Pack contradiz o contrato de runtime vigente.**
`## LOAD ORDER — MANDATORY` + `fail_closed_on_missing_executable_resource: true` implicam recusa diante de recurso não carregado. Ou o pacote novo opera sob contrato diferente — e deixa de ser comparável aos pilotos — ou o carregamento seletivo não funciona. **É contaminação direta do pipeline atual e a proposta não a percebeu.**

**3. A identidade colide em dois níveis do grafo e o desenho não tem esquema de identidade global.**
N9 (`evidence_id`) e N4 (`artifact_id` idêntico nos três manifests). Sem qualificação por pacote, toda aresta cruzando fontes aponta para o objeto errado **sem erro visível** — o mecanismo exato pelo qual multi-fonte quebra, já medido.

**4. Sem campo de língua e sem aresta de ancoragem tipada, a fusão produz falsa deduplicação e falsa contradição.**
São os dois modos de falha que a arquitetura existe para evitar. Falha aqui é pior que o estado atual: hoje uma regra não ancorada fica visivelmente não ancorada e a Skill para com `UNDEFINED`; sob fusão, ela vira decisão de precedência — **confiantemente errada**.

Nenhum dos quatro exige mudar direção. Os quatro exigem escrever o que ainda não está escrito. Fechadas as decisões D1–D6 da §5 e rodado o `PILOT-MS-000A` (custo próximo de zero), a proposta é recandidatável a `READY_TO_FREEZE_ARCHITECTURE`.

---

**FIM DA REVISÃO. Nenhuma implementação foi realizada nesta rodada.**

---

# ADENDO A — QUATRO LACUNAS DA PRÓPRIA REVISÃO

**Forma aditiva, sem mutação do corpo acima** — disciplina já adotada no projeto (emenda por aditivo, nunca reescrita).

Método: em vez de confiar em leitura, o corpo acima foi **enumerado** por busca de radical antes de escrever este adendo. O que já estava coberto **não** é repetido aqui — inclusive a decomposição da aresta de ancoragem em três predicados (§3), o DAG de módulos com canário que planta ciclo (R15), a circularidade autoridade↔precedência (Q6) e os pilotos `MS-000A` / `MS-000B`, que continuam valendo como escritos.

## A.1 — Falta a relação que DERIVA o grafo de dependências

R15 exige que a dependência entre módulos seja DAG **verificado**. Nada no eixo `content` da §9.4 a **produz**. Hoje a dependência é **afirmada** por quem monta o módulo e depois checada — o que faz da composição de módulo um juízo não registrado.

**Acrescentar ao eixo `content`:** `PRESUPPOSES` — a claim de B só faz sentido se a de A valer. Não é corroboração (não afirma o mesmo), não é especialização (não estreita o mesmo escopo), não é complemento (não é paralela). É a única relação capaz de **derivar** a aresta de dependência a partir do corpus em vez de postulá-la. Sem ela, `required_modules` no manifesto é opinião com verificação de aciclicidade em cima.

## A.2 — O fork que nenhuma das duas versões desta revisão decidiu

A §9.1 coloca o **bundle** dentro de `PACKAGE ASSEMBLY`, o que implica que **regras viajam dentro do Source Package**. A consequência não foi examinada e é estrutural:

- **Desenho A — regras viajam.** A fusão opera sobre regras já derivadas; claim é índice de casamento. Custo: dedup em nível de regra e risco imediato sobre a regra de ouro (proveniência preservada). **E fonte única continua sendo um caminho separado, mantido para sempre em paralelo ao multi-fonte.**
- **Desenho B — o Source Package para nas claims.** Regras, workflows e anti-patterns são **sempre** saída de FUSÃO, inclusive para k=1. **Fonte única vira caso degenerado de multi-source: um pipeline, não dois.** O estágio de regras do compilador atual é **reutilizado** como componente de fusão — reuso, não modificação, e portanto não viola o isolamento.

**Recomendação: Desenho B.** Resolve de uma vez a dupla verdade, o custo permanente de manter dois caminhos e boa parte do risco de contaminação. **Decisão bloqueante: entra na lista da §5.**

## A.3 — Critério de morte pré-registrado para a camada de claim

A §3 decompôs a ancoragem em três predicados, o que é a leitura certa. Falta a **previsão falsificável** que decide se a camada entra:

> Uma claim é reescrita normalizada — **paráfrase**. Paráfrase é exatamente a operação que destrói recuperabilidade verbatim, que é o que o predicado `QUOTED_FROM` (139/226 = 61,50%) mede.
>
> **Previsão a congelar ANTES de qualquer rodada: a camada de claim derruba `QUOTED_FROM` abaixo de 61,50% sem levantar `SUPPORTED_BY` acima de 5,3%.**

Se a previsão se confirmar, a camada não entra na forma proposta. É barata, é pré-declarável e ataca a justificativa da camada em vez do seu funcionamento — que é onde a decisão de produto realmente está.

**Corolário de enquadramento:** a camada de claim **não pode ser justificada como melhoria de ancoragem** em nenhuma hipótese. Acrescentar salto na cadeia `L0 → evidence → claim → rule` tem, no melhor caso, efeito neutro sobre substância. A camada só se defende como mecanismo de **resolução de conflito**. São objetivos distintos e devem ser medidos separadamente.

## A.4 — Corroboração entre fontes correlacionadas

Cursos copiam cursos. `CORROBORATES` entre duas fontes que copiaram uma terceira **não é corroboração independente**. Se contagem de corroboração alimentar qualquer peso, prioridade ou ordem de módulo, o viés é sistemático e cresce com o corpus — aparece só com dezenas de fontes, que é onde ninguém quer descobri-lo.

**Mínimo viável:** `source_independence` **declarado manualmente** no `source_profile`, nunca inferido. Sinal mecânico auxiliar aceitável: sobreposição verbatim entre fontes — com a ressalva permanente de que é matcher, e matcher já falhou 8 vezes neste projeto, logo entra com controle positivo.

---

**A classificação `ARCHITECTURE_REVISION_REQUIRED` não muda com este adendo — ela fica mais firme:** A.2 é um fork estrutural não decidido, e A.1 é uma entidade de relação ausente sem a qual o grafo de módulos não é derivável do corpus.

**FIM DO ADENDO A. Nada implementado.**
