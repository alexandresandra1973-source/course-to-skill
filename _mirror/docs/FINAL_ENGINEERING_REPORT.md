# FINAL_ENGINEERING_REPORT — Course-to-Skill

**Auditoria técnica independente, Fases 1–6.** Data: 2026-08-10.
**Entradas:** `PROJECT_INVENTORY.md`, `INVENTORY_DELTA_v0.1.1.md`, `ARCHITECTURE_REVIEW.md`, `CLAUDE_ARCHITECTURE_PROPOSAL.md`, 14 ADRs, `PHASE4_SPINE_RESULT.md`, `PILOT-001-COMPARISON.md`, código em `~/course-to-skill-claude`, `BASELINE_MANIFEST_20260810.txt`.
**READ-ONLY:** 257/257 arquivos das duas pastas auditadas com sha256 idêntico ao congelamento. 0 alterados, 0 removidos, 2 adicionados pela esteira paralela.

> **Este relatório é escrito para uma decisão de investimento de tempo.** A recomendação está na §7 e não é "continue como está".

---

## 1. ARQUITETURA FINAL — a união, não a minha nem a dele

A Fase 5 mediu complementaridade, não superioridade. O placar de detecção no mesmo dataset foi **10 (v0.1.1) × 6 (proposta), 1 em comum**, e as classes de defeito são **disjuntas**: 9 dos 10 achados da v0.1.1 são semânticos ("a fonte não ensina isso"); 6 dos 6 meus são estruturais (âncora, dispersão, teto, circularidade). Nenhuma das duas arquiteturas isolada teria pegado o que a outra pegou.

A arquitetura final é a soma, com uma divisão de trabalho que a medição impõe:

```
   L0 Vault ──── Cutter ──── Rubric Author        [ Claude ]  ancoragem, corte, régua externa
        │           │             │
        └───────────┴─────────────┴──► G0 G1
                    │
              Extractor (L1)                       [ ChatGPT ] passe único, produziu 100% do conteúdo
                    │
              ┌─────┴─────┐
              │  G2  G3   │                        [ Claude ]  piso estrutural, barato, determinístico
              └─────┬─────┘   (G3 alimenta o adversário, não bloqueia sozinho)
                    │
              Adversário (L3)                      [ ChatGPT ] INSUBSTITUÍVEL — 9/9 dos achados reais
                    │  ── G4
              Packager (L4)                        [ ChatGPT ] com G5 [Claude] depois
                    │  ── G5
              G6 teto de maturidade                [ Claude ]  n≥16 calculado por Wilson
                    │
              Evaluator (L5)                       [ ChatGPT ] com rubrica de L0 [Claude]
                    │  ── G7
              SUMMARY_VS_SKILL + ABLATION          [ ChatGPT ] INSUBSTITUÍVEL — único antídoto ao resumo disfarçado
```

### 1.1 O que vem da v0.1.1, e por qual medição

| Componente | Medição que o sustenta | Veredicto |
|---|---|---|
| **Adversário semântico (Skeptic)** | 9 achados válidos (3 HIGH + 3 MEDIUM, depois 1 HIGH + 2 MEDIUM, depois 2 LOW), **6/6 correções verificadas nos arquivos** — e produzidos **sem** acesso a L0 | **INSUBSTITUÍVEL.** O experimento da Fase 5 mostrou que G2, bem alimentado, **aprova** `max_iterations: 5` — a invenção que SC-002 reprovou. Implicação entre dois textos não é propriedade estrutural. |
| **SUMMARY_VS_SKILL com braço-baseline** | `baseline-summary.md` verificado fato a fato contra a transcrição; braços ARM-A/ARM-B montados; `required_margin_over_baseline: 5` | **INSUBSTITUÍVEL.** É o único instrumento em qualquer das duas arquiteturas que detecta "a skill é só um resumo" — o defeito que a **minha** exigência de quote verbatim incentiva (§5.1). |
| **ABLATION com paridade de arms** | ARM-A 14 arquivos × ARM-B 12 (menos `decision-rules.yaml` e `workflows.yaml`), `RUNNER_PROMPT.md` byte-idêntico | mantido — mede a contribuição marginal da camada estruturada |
| **Extractor de passe único** (decision+workflow+principle juntos) | produziu **100%** do conteúdo decisório; diff L1→bundle = **1 campo** em 8 registros | mantido. H6 caiu: já era assim e funcionou |
| **Schemas** | 44 evidências + 8 ADRs + 1 WF + 16 testes + 1 registry → **0 erros** de validação | mantidos, com 2 campos removidos e 4 sub-objetos a ganhar campo de evidência (ADR-0013) |
| **`UNDEFINED` como estado de primeira classe** | única mudança de comportamento medida no projeto: **0/8 → 7/8** ADRs e steps | mantido — é o modelo do que a R2 exige |
| **Isolamento runtime ↔ judge (§B) e lock por hash** | 6/6 SHA-256 conferem, 0 marcadores privados, 0 arquivos proibidos | mantido integralmente |
| **Escada de maturidade + `production_ready` travado** | `PRODUCTION_READY_WITHOUT_S4` funciona | mantido, estendido pelo teto por corpus |
| **Recusar inventar contagens** | `manifest.scope.*: null` com nota *"to avoid inventing coverage"* | vira norma |

### 1.2 O que vem da proposta — e o que dela morre

| Portão | Veredicto | Razão medida |
|---|---|---|
| **Vault L0 + resolução de span** (ADR-0001) | **SOBREVIVE** | é o que torna computáveis `HALLUCINATION_RATE`, G2 e o corte de held-out. 93/94 timestamps do piloto resolvem; 1 não |
| **G2 ancoragem** (ADR-0002, 0013) | **SOBREVIVE, rebaixado a piso** | pegou `quote 0/44` e 1 endereço inválido — mas **aprova** a invenção de SC-002. É piso barato, não teto |
| **Cutter de held-out em L0** (ADR-0003) | **SOBREVIVE** | 10/10 casos "cegos" contaminados por construção; determinístico e auditável por terceiro |
| **G6 teto por corpus** (ADR-0010, 0014) | **SOBREVIVE** | transforma em bloqueio o que a v0.1.1 apenas documentava. `n ≥ 16` é calculado por Wilson, não escolhido |
| **G3 dispersão** (ADR-0005, 0014) | **VIRA TRIAGEM**, não bloqueador solitário | mede dispersão, não correção: reprovaria um corpus honestamente uniforme. Seu valor é apontar ao adversário onde olhar — SC-003 é exatamente um caso de degeneração que o adversário pegou semanticamente |
| **G5 fechamento pós-compilação** (ADR-0007) | **RETIDO, SEM DISPARO** | mediu **0** no único dado real; o probe `origin` mostrou 5/5 já presentes em L1. Não é evidência de inutilidade — é ausência de evidência |
| **G5/origin** | **VIRA PROBE** | não reprova nada, localiza camada. Chamá-lo de portão inflava a contagem |
| **`confidence.score` / `confidence.level`** (ADR-0004) | **REMOVIDOS** | 1 valor distinto em 44 registros; nenhum consumidor; nenhuma ligação schema entre score e level |

**Nada meu é removido por redundância com o adversário** — mas dois itens são rebaixados (G3 → triagem, G5/origin → probe) e um fica marcado como não-provado (G5). A contagem honesta de portões bloqueantes meus cai de 6 para **4**.

---

## 2. PRINCIPAIS DECISÕES — as 14 ADRs

| ADR | Decisão em uma linha | Estado |
|---|---|---|
| 0001 | Vault L0 imutável endereçado por conteúdo como único referente de verdade | **vigente** · implementada |
| 0002 | Tripla obrigatória `span` + `quote` + `claim`, com quote verbatim verificado | **vigente** · implementada · limite declarado na 0013 |
| 0003 | Corte de held-out em L0, por span, com semente, antes da extração | **vigente** · implementada |
| 0004 | Remover `confidence`; derivar `evidence_strength` de contagem de spans | **vigente** · **sem código** (derivação não implementada) |
| 0005 | Portão de degeneração por dispersão (entropia normalizada) | **emendada** pela 0014 · implementada · rebaixada a triagem pela Fase 5 |
| 0006 | Adversário mantido e promovido a portão bloqueante legível por máquina | **vigente** · **sem código** · confirmada pela Fase 5 por caminho oposto |
| 0007 | Packager como função pura com portão de fechamento pós-compilação | **emendada** pela 0013 · implementada · **candidata a revogação parcial** (ver abaixo) |
| 0008 | Rubrica escrita em L0 antes da extração, proibida de citar IDs internos | **vigente** · **parcial** (só o check de IDs) |
| 0009 | Métricas computáveis em escala única; `TOTAL_SCORE` não é portão | **vigente** · **sem código** |
| 0010 | Teto de maturidade em função do corpus (n ≥ 16 held-out, Wilson 95%) | **vigente** · implementada |
| 0011 | Consolidator rebaixado a função condicional que emite diff | **vigente** · **sem código** · sustentada por n=1 aula apenas |
| 0012 | Separar namespace de IDs do curso e do projeto | **candidata a revogação** — única ADR sem defeito medido; higiene, custo real de dois vocabulários conviverem |
| 0013 | Emenda à 0007: portão de invenção também em L0→L1, por granularidade de campo | **vigente** · **sem código** (Fase 6+) |
| 0014 | Emenda à 0005: `UNDERPOWERED` epistêmico limita o teto a `S1_ANCHORED` | **vigente** · implementada |

**Sobre a 0007 como candidata a revogação parcial:** o portão pós-Packager mediu 0 em dado real e o defeito que motivou sua criação entrou uma camada antes. Ele não deve ser removido — cobre uma etapa que o adversário não vê —, mas **não deve ser contado como defesa ativa** até disparar uma vez. Se, após a ancoragem por campo (0013) estar em produção, ele continuar em 0 por dois corpora, revogue.

---

## 3. PROBLEMAS ENCONTRADOS

### 3.1 Do projeto auditado

| # | Problema | Número |
|---|---|---|
| P1 | Verificação de proveniência fecha contra o próprio artefato | `union(EV usados) ⊆ union(EV no mapa)`, ambos escritos pelo mesmo compilador |
| P2 | Rótulos epistêmicos degenerados | 7 campos com entropia **0**; `confidence.score` com **1 valor distinto em 44** |
| P3 | Caso "cego" que é recall | TEST-0009 = `EV-0027`, fonte **08:05–08:20**; `created_before_modeling: false`, `cases: []` |
| P4 | Rubrica circular | **10/10** `evaluator_instructions` = *"avaliar contra a metodologia extraída"*; **0** referências à fonte na suíte de 37 KB; 25 IDs internos |
| P5 | Vazamento semântico do teste cego | **10/10** testes declaram `hidden_items` que estão inteiros no pacote do candidato; 2/2 `expected_questions` com match exato |
| P6 | Ancoragem textual inexistente | `source_excerpt` em **0/44**; fonte em EN, claims em PT — nenhuma verificação lexical possível |
| P7 | Contratos entre camadas não exigidos | **13** artefatos prescritos nunca produzidos, 0 ocorrências nas duas pastas |
| P8 | Validador obrigatório falha no pacote que o projeto manda entregar | `ERROR MISSING_FILE: tests/test-candidates.yaml` no `runtime-bundle` |
| P9 | Regra §C do próprio hardening violada | **4** testes, um deles sem margem de leitura (`ADR-0006` manda `STOP`, TEST-0006/0007 exigem `should_stop: false`) |
| P10 | Camada intermediária sem delta | L1→bundle alterou **1 campo** em 8 registros; Modeler entregou 7 de 11 arquivos |
| P11 | Endereço de fonte inválido | `EV-0001`, marca `0:29` ausente entre as 180 do transcript |
| P12 | Afirmações "PASS" sem predicado | das 11 do PREFLIGHT: 1 sem predicado, 1 medindo outra coisa, 1 NO-OP |

### 3.2 OS MEUS

Registrados com o mesmo rigor. Três foram medidos contra mim pelo próprio processo.

| # | Meu erro | Como foi medido | Consequência |
|---|---|---|---|
| **M1** | **H1 refutada** — propus substituir `confidence` por escala ordinal ancorada | A escala proposta **já existia** (`evidence_strength`) e **já havia colapsado**: 37/4/3, 0 usos de 2 valores, H_norm **0,340** | Teria renomeado o problema. Corrigido: remover o campo e derivar de contagem |
| **M2** | **H5 refutada** — propus que todo estágio a jusante relesse L0 | O adversário entregou **6/6 achados válidos sem L0**; e dar L0 ao Packager criaria superfície nova de invenção pós-auditoria | Custo sem captura medida, e dano num dos estágios |
| **M3** | **H6 refutada** — propus unir decision+workflow+principle num passe | **Já era um passe só**: `lesson-analyzer.md` §10 executa PASS 3/4/5 no mesmo prompt | Eu propus como reforma algo que já existia — leitura insuficiente antes de propor |
| **M4** | **Concluí a tabela de entropia com N pequeno demais** | Chamei 7 campos de COLLAPSED; meu próprio código, aplicando `N_MIN = 20` da ADR-0005, recusa concluir em **4 deles** (N=8) | Errei o mesmo vício que auditei: concluir de base insuficiente. Corrigido pela ADR-0014 |
| **M5** | **Errei a contagem na Fase 3** | Escrevi "8 de 10 campos carregam 0 bits ou quase"; o exato é **9 de 10** não-OK (7 com H=0, 1 quase, 1 saudável) | Corrigido no `PHASE4_SPINE_RESULT.md` |
| **M6** | **Errei a contagem de órfãs na Fase 1** | Reportei 16 evidências nunca citadas; a varredura completa dá **12** | Varredura incompleta de arquivos. Corrigido na Fase 2 |
| **M7** | **G2 aprova a invenção que o adversário reprovou** | Experimento: `span` `11:29–11:33` resolve, `quote` *"Run it three to five times"* é verbatim, `claim` = `max_iterations: 5` → **G2 PASS** | Meu portão principal não alcança a classe de defeito que dominou este piloto. É o achado mais importante contra a minha arquitetura |
| **M8** | **Falso positivo do meu extrator de claims** | Acusou 1 invenção que era `manifest.skill.name` | Corrigido estreitando **escopo**, não afrouxando **limiar** — registrado porque ajustar verificação até parar de reclamar é o defeito auditado |
| **M9** | **Um rótulo meu sem consumidor** | `UNDERPOWERED` emitido por G3 e consumido por ninguém — exatamente o que a R2 proíbe | Corrigido pela ADR-0014 |
| **M10** | **Cutter sem guarda de tamanho mínimo** | Cortaria 20% de uma aula única, destruindo a única demonstração ponta a ponta (82 s, 9,1%) | **Defeito aberto**, não corrigido |

---

## 4. MELHORIAS SOBRE O ORIGINAL — só as medidas

| Melhoria | Número |
|---|---|
| Referente externo imutável para verificação | 93/94 timestamps resolvem contra L0; o 1 que não resolve é detectado (`EV-0001`, `END_MARK_NOT_FOUND`) |
| Ancoragem textual verificável | de `source_excerpt` **0/44 sem verificação possível** para substring byte-exata verificada |
| Held-out com consequência | de `cases: []` documentado em prosa para **10/10** casos marcados `CONTAMINATED_BY_CONSTRUCTION` e build bloqueado |
| Circularidade medida | **25** IDs internos na rubrica → FAIL; antes, 0 checks |
| Teto de maturidade calculado | `n ≥ 16` derivado de Wilson 95% (LB `n/(n+3,84)`), não escolhido; PILOT-001 recusado em `S0_INGESTED` |
| Degeneração detectável | 7 campos com H=0 quantificados; `category` poupado (H_norm **0,864**) |
| Enunciados com verificação executável | **19% → 62%** (7/36 vs 8/13 aplicáveis) — com viés de seleção declarado |
| Portão publica número, não veredicto | 100% dos `GateResult` carregam estado nomeado + evidência medida; **0** booleanos nus |
| Meta-testes | **26**, cada portão com fixture que dispara e que passa, incluindo o caso real `EV-0001` |
| Atribuição de camada corrigida | SC-001 atribuía ao Compiler; medido: **5/5 já em L1, 0 entre L1 e bundle** |

---

## 5. LIMITAÇÕES E DÍVIDA TÉCNICA

### 5.1 O incentivo perverso do quote verbatim — a limitação mais séria

A forma mais barata de passar em G2 é fazer `claim` ≈ tradução do `quote`. Isso dá ancoragem perfeita e metodologia zero.

Linha de base medida (razão palavras da claim / palavras do span da fonte, 43 evidências resolvíveis):

| | valor |
|---|---|
| mediana | **0,373** |
| média | 0,416 |
| mínimo | 0,072 (`EV-0011`) |
| **máximo** | **0,944** (`EV-0015`) |
| claims ≤ 50% da fonte | 31 de 43 |

`EV-0015`, razão 0,944 — fonte: *"Without tools, your agent is just a chatbot with a fancy hat."* → claim: *"O professor afirma que, sem ferramentas, o agente permanece essencialmente um chatbot sem capacidade prática de agir."* **Isso é tradução, não modelagem, e passaria em G2 com nota máxima.**

**A arquitetura que estou propondo cria esse incentivo e não traz o antídoto. A arquitetura que auditei traz** — `SUMMARY_VS_SKILL` foi desenhado exatamente contra "resumo disfarçado de skill", antes de o problema existir. É a razão nº 1 pela qual a união é obrigatória e não uma cortesia.

### 5.2 Dívida técnica declarada

| Item | Estado |
|---|---|
| 5 das 14 ADRs sem código (0004, 0006, 0009, 0011, 0013) | dívida assumida |
| Extractor e Evaluator não implementados | é onde a verificação é difícil; minha taxa de 62% deve cair quando eu chegar lá |
| `N_MIN = 20` e `θ = 0,50` **não calibrados** | precisam de **2 corpora de qualidade conhecida** — um curso longo não resolve, é um corpus só |
| Custo do vault | 927 KB para uma aula, **13× o bundle**. Para 40 aulas com vídeo, escala de GB |
| G3 reprova corpus honestamente uniforme | falso positivo sem solução estrutural |
| Cutter sem corpus mínimo | M10, aberto |
| Sem CI, sem empacotamento, sem CLI | a espinha roda por script; 1.761 linhas, 26 testes |

### 5.3 EM ABERTO que sobraram

1. **θ de `NEAR_COLLAPSED`** — intervalo conhecido: entre 0,340 e 0,864. Decide: 2 corpora de qualidade conhecida.
2. **Se o Consolidator se paga em escala de módulo** — decide: `|diff(E, N)|` em ≥5 aulas.
3. **Detecção mecânica de "a claim excede a quote"** — decide: conjunto rotulado de pares claim/quote com julgamento humano de exagero. **A Fase 5 sugere que a resposta é não**, e que isso é território permanente do adversário.
4. **Granularidade do corte de held-out** (span · ramo · caso) — decide: rodar as três no mesmo corpus.
5. **Se `GENERAL_KNOWLEDGE` deve existir** — 0 usos em 44; campo morto ou não exercitado.
6. **Se o candidato consegue citar span por afirmação** — de que depende `HALLUCINATION_RATE`.
7. **Se rubrica não-circular é escrevível na prática** — decide: 2 autores independentes, mesmo L0, concordância nos `expected_label`.
8. **Métrica de divergência claim↔quote** (§5.1) — sem limiar; qualquer número hoje seria chute.

---

## 6. AVALIAÇÃO DE PRONTIDÃO — dois veredictos

### 6.a O PILOT-001 como Skill: **PROTOTYPE**

Não é PILOT. "PILOT" implica ter sido rodado contra casos; **ele nunca foi executado**.

| Critério | Medido |
|---|---|
| Testes comportamentais executados | **0** — as 9 métricas em `null`, nenhum arquivo de resultado |
| Casos held-out | **0** (`cases: []`) |
| Proveniência verificável | **0/44** com citação; `evidence.jsonl` não viaja no pacote |
| Teto pela minha escada | `S0_INGESTED` — não alcança nem S1 |
| Achados do adversário corrigidos | 6/6 verificados nos arquivos — mas **nunca validados comportamentalmente** |
| Autoavaliação do próprio projeto | `S3_EXECUTABLE`, `production_ready: false`, `NOT_YET_VALIDATED` |

**Está a uma tarde de virar PILOT.** Os braços ARM-A/ARM-B do TEST-0007 e TEST-0008 já estão montados, o lock confere por SHA-256 e o protocolo está escrito. Falta executar.

### 6.b A ferramenta (compilador + espinha) como software: **PROTOTYPE**

| Lado | Evidência |
|---|---|
| **Compilador v0.1.1** | 5 prompts (7.387 linhas), 5 schemas com 0 erros de validação, 1 validador com 7 checks + VERIFY_KIT. Mas: **13** artefatos prescritos nunca produzidos, o validador **falha** no pacote que a própria regra manda entregar, 0 testes automatizados, 0 CI |
| **Espinha** | 1.761 linhas, 6 portões, **26 meta-testes**, executada contra dado real, resultado publicado por script. Mas: sem Extractor, sem Evaluator, sem CLI, sem CI, **1 dataset**, 5 de 14 ADRs sem código |

Há artefatos de qualidade **BETA** dentro de um sistema **PROTOTYPE** — os schemas (0 erros em 5 famílias de registro), a integridade do kit de teste (6/6 hashes, hash de árvore) e os 26 meta-testes. Isso é mérito real e não muda o veredicto do conjunto: **nenhuma das duas metades foi validada contra a coisa que promete fazer.**

Ambos os veredictos são **PROTOTYPE**, e escrevo PROTOTYPE.

---

## 7. PRÓXIMOS PASSOS — ordenados por razão custo/informação

### 🥇 PASSO 1 — Rodar o teste cego que já está montado

| | |
|---|---|
| **O que decide** | Se a camada de conhecimento estruturado (`decision-rules.yaml` + `workflows.yaml`) acrescenta algo sobre (a) o mesmo `SKILL.md` sem ela e (b) um resumo fiel de 216 palavras |
| **Custo** | Uma tarde. **Os arms já existem**: TEST-0007 ARM-A/ARM-B (criados 02:18) e TEST-0008 ARM-A/ARM-B (02:31); `RUNNER_PROMPT.md` byte-idêntico entre braços; suíte travada por SHA-256 |
| **Fica sabido** | Se a premissa central do projeto se sustenta |

**Este é o menor experimento que ainda pode invalidar o projeto inteiro.** A premissa é: *um curso pode ser compilado em regras de decisão executáveis que superam um bom resumo.* Se o braço-skill não superar o braço-resumo, a premissa é falsa para este corpus — e nenhuma melhoria de arquitetura conserta uma premissa falsa. É a única coisa nesta lista que pode dizer "pare".

**O que exatamente muda se der empate:**

- **Empate em n=1 caso é inconclusivo.** TEST-0008 tem **1** `input_case`. Uma proporção sobre 1 item é 0 ou 1; não há inferência possível. O honesto é: empate → escalar para n≥16, não concluir.
- **Mas empate sob a rubrica atual é pior do que parece.** A rubrica é derivada do artefato (10/10 `evaluator_instructions`) e exige `"ROBOT prompt"` em `required_elements` — elemento que o baseline não menciona e a fonte menciona em `9:52`. **A régua está inclinada a favor da skill.** Empatar com o polegar na balança é sinal negativo, não neutro.
- **Se der derrota**, a leitura é forte mesmo em n=1: um resumo de 216 palavras batendo um pipeline de 5 estágios é evidência direta contra a premissa.
- **Redução de escopo que isso dispararia:** parar de construir o compilador e manter **a espinha de verificação como ferramenta de proveniência para metodologia escrita por humano**. Isso continua valendo — G2, o Cutter e G6 não dependem de a extração automática funcionar. É um produto menor, mais barato e defensável.

### 🥈 PASSO 2 — Reescrever a rubrica a partir de L0 e reexecutar

| | |
|---|---|
| **O que decide** | Se o resultado do Passo 1 é real ou artefato da régua circular |
| **Custo** | Menor que o Passo 1: escrever `expected_label` e `allowed_spans` para os 10 casos, lendo só a transcrição. Verificação já existe (grep de IDs internos, hoje acusa 25) |
| **Fica sabido** | Se o veredicto do teste cego sobrevive à remoção do viés. E, de quebra, **se rubrica não-circular é escrevível na prática** — o EM ABERTO nº 7 |

Sem este passo, qualquer número do Passo 1 é contestável. Com ele, o Passo 1 vira evidência.

### 🥉 PASSO 3 — Ancoragem por campo em uma aula só (ADR-0013)

| | |
|---|---|
| **O que decide** | Se a extração consegue produzir `span`+`quote` por campo sem virar transcrição — e qual é a razão claim/quote resultante contra a linha de base **0,373 / máx 0,944** |
| **Custo** | Uma aula reprocessada, ~44 recortes verbatim; mais os 4 sub-objetos do schema que precisam ganhar campo de evidência (`autonomy`, `precedence`, `missing_input_action`, `input_requirement`) |
| **Fica sabido** | Se a exigência de quote é praticável, e se o incentivo perverso da §5.1 se materializa. Se a razão subir para perto de 1, **a ancoragem está produzindo tradução** — e a ADR-0002 precisa de contrapeso antes de escalar |

### Depois disso — corpus de 5–8 aulas

| | |
|---|---|
| **O que custa** | Medido no piloto: **~77 min de ponta a ponta por aula** (L0 → 3 passadas de adversário → bundle), fora o retrabalho de ferramenta. Para 6 aulas: **~8 h de pipeline**, mais revisão humana das passadas de adversário |
| **O que destrava** | `N ≥ 20` para a camada de decisão sair de `UNDERPOWERED` → **3 aulas**. `n_holdout ≥ 16` para S5 → **5 aulas** a 25% de reserva, **6** a 20%, **8** a 15% |
| **O que NÃO destrava** | **θ e `N_MIN` continuam sem calibração** — isso exige **dois corpora de qualidade conhecida**, não um corpus maior. Seis aulas do mesmo curso são um corpus só |

Este passo vem **depois** dos três primeiros porque custa 8 h e destrava capacidade estatística, não decisão. Gastar 8 h antes de saber se a premissa se sustenta é a ordem errada.

### 7.4 A arquitetura serve para metodologia que NÃO está em curso?

Hipótese avaliada, não requisito. **Resposta: serve pela metade, e as metades que faltam são estruturais, não de esforço.**

O que transfere sem mudança:
- **Endereçamento de span** funciona em qualquer texto: mensagem de chat (`msg_id` + offset), célula de planilha (`aba!R1C1`), parágrafo de documento. Não é específico de vídeo.
- **G2, G6, o Cutter e o teto por corpus** não dependem de a fonte ser uma aula.
- **O adversário** é o componente mais transferível: "isto é o que a fonte sustenta?" é a mesma pergunta.

O que quebra, e por quê:

| Premissa da arquitetura | O que acontece fora de um curso | O que teria que mudar |
|---|---|---|
| **L0 é imutável** (ADR-0001) | Conversa cresce, planilha é editada diariamente, documento tem revisões. Endereçamento por conteúdo faz **cada edição quebrar todos os spans** | L0 **versionado** em vez de imutável: span endereça `(objeto, versão)`, e mudança na fonte marca claims dependentes como `STALE` em vez de quebrá-las. É alteração real na ADR-0001 |
| **Uma fonte autoritativa por afirmação** | A mesma decisão aparece num thread, num doc, e é **contradita pelo que a planilha faz** | `contradiction` existe no schema e foi usada **0/44** — caminho nunca exercitado. Teria de virar primeira classe, com resolução explícita |
| **Held-out por corte aleatório de span** | Um corte de 20% pode remover **o único lugar** onde a decisão está registrada. O corte assume redundância que a prática dispersa não tem | Corte por **instância de decisão com suporte independente verificado** — o que exige indexar antes de cortar, e isso é quase circular |
| **A fonte *ensina*** | Fora de curso não há ensino, há **comportamento**. A evidência é o que foi feito, não o que foi dito | O adversário muda de pergunta: de *"a fonte ensina isso?"* para *"é isto que eles de fato fazem?"* — o que exige evidência comportamental (logs, resultados). O schema lista as modalidades (`EXAMPLE_FILE`, `OTHER`), o pipeline nunca as exercitou |

**Veredicto da hipótese:** a espinha de verificação transfere; o pipeline de extração não, sem as quatro mudanças acima. E há um sinal favorável que não deve ser ignorado: **fora de curso o corpus tende a ser muito maior** — anos de decisões dispersas contêm ordens de grandeza mais instâncias decisórias do que 15 minutos de aula. Os dois gargalos medidos aqui (`N ≥ 20` e `n_holdout ≥ 16`) desaparecem. O que era o problema mais duro do caso-curso deixa de ser problema.

**Não recomendo perseguir isso agora.** É hipótese com fundamento, e persegui-la antes do Passo 1 seria trocar uma premissa não testada por outra.

---

## 8. RECOMENDAÇÃO HONESTA

**Continue — mas não escreva mais nenhuma linha de arquitetura antes de rodar o Passo 1.**

O que sustenta continuar: os schemas funcionam (0 erros em 5 famílias de registro); o adversário funciona e é insubstituível (6/6 correções verificadas); a espinha funciona e reproduziu mecanicamente 4 de 4 defeitos que a auditoria mediu à mão; e a união das duas arquiteturas cobre classes de defeito disjuntas que nenhuma das duas cobria sozinha.

O que sustenta a cautela: **nada neste projeto foi validado contra o que ele promete fazer.** Cinco fases de auditoria, 14 ADRs, 1.761 linhas de código, e o número de testes comportamentais executados continua sendo **zero**. Toda a discussão de arquitetura — a minha inclusive — está sendo conduzida sobre uma premissa que ninguém mediu.

**A recomendação concreta é uma redução de escopo temporária:** congele a arquitetura como está, rode o teste cego, reescreva a rubrica a partir de L0, rode de novo. Três passos, custo somado abaixo de dois dias. Se a skill superar o resumo, o investimento no compilador está justificado e a lista de dívida técnica da §5 vira um plano de trabalho. Se empatar sob uma régua já inclinada a favor dela, ou perder, o caminho honesto é reduzir o escopo à espinha de verificação — que continua valendo por si e custa uma fração.

O maior risco deste projeto não é técnico. É o de continuar refinando um compilador cuja premissa nunca foi testada, com a auditoria dando a impressão de progresso. Esta auditoria mediu muita coisa; ela **não** mediu se a ideia funciona. Só o Passo 1 mede.

---

**FIM DA AUDITORIA.** Fases 1–6 concluídas. Nenhum arquivo de `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado em nenhuma fase: 257/257 conferem contra `BASELINE_MANIFEST_20260810.txt`.
