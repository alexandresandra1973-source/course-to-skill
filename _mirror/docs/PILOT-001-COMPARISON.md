# PILOT-001-COMPARISON — arquitetura v0.1.1 (ChatGPT) × arquitetura proposta (Claude)

**Fase 5.** Dataset comum: PILOT-001. Baseline: `BASELINE_MANIFEST_20260810.txt` (257 arquivos, 0 alterados).
**Emendas que precederam esta fase:** [ADR-0013](adr/ADR-0013.md) e [ADR-0014](adr/ADR-0014.md).

---

## 0. HONESTIDADE DE ESCOPO — leia antes de comparar

**Não existem duas Skills para comparar.** Eu não construí Extractor nem Compiler; a Fase 4 implementou apenas a espinha de verificação (Vault, Cutter, G2, G3, G5, G6). Comparar artefato contra artefato aqui seria inventar uma simetria que não existe.

O que a arquitetura v0.1.1 tem e a minha não tem, e que isto torna incomparável por artefato:

| | v0.1.1 (ChatGPT) | proposta (Claude) |
|---|---|---|
| Skill gerada de ponta a ponta | **sim** — 14 arquivos, 8 ADRs, 1 workflow, 6 princípios | **não existe** |
| Extractor | sim, produziu 100% do conteúdo | não implementado |
| Compiler | sim | não implementado |
| Adversário | sim, com 9 achados válidos | não implementado |
| Evaluator | especificado, **nunca executou** | não implementado |
| Portões executáveis | 7 checks + VERIFY_KIT | 6 portões, 26 meta-testes |

Uma arquitetura que **produz** e uma que **verifica** não competem no mesmo eixo. Esta comparação é entre **o que cada uma promete e o que cada uma consegue provar**, e entre **o que cada uma detectou no mesmo material**. Nada além disso é sustentável com a evidência que tenho.

Segunda assimetria, que também precisa estar dita: minha taxa de "decisão com verificação" é alta em parte porque **só escrevi decisões que eu sabia como verificar**. Isso é seleção, não superioridade. A v0.1.1 escreveu regras sobre coisas difíceis de verificar — como "não inventar rationale" — e o preço foi não conseguir verificá-las. Escolher só problemas fáceis também é uma forma de errar.

---

## 1. O QUE CADA UMA PROMETE × O QUE VERIFICA MECANICAMENTE

### 1.1 Lado v0.1.1 — contado nos arquivos

| Classe de enunciado normativo | quantos | com verificação em código |
|---|---:|---:|
| Regras de hardening v0.1.1 (§A–H) | 8 | **7** |
| Proibições de alucinação (`SKILL.md` §13) | 7 | **0** |
| Estados nomeados de §13 (`METHOD_NOT_DEFINED`, `RATIONALE_NOT_EXPLICIT`, `INSUFFICIENT_EVIDENCE`, `CONTRADICTION_DETECTED`, `MISSING_REQUIRED_INPUT`) | 5 | **0** |
| HARD RULES do `lesson-analyzer` (HR-01…HR-08) | 8 | **0** |
| NON-GOALS (`SKILL.md` §29) | 8 | **0** |
| **Total** | **36** | **7 = 19%** |

Os 7 com código, e o que cada um realmente faz:

| Regra | Check | Estado real medido |
|---|---|---|
| §A held-out travado antes da modelagem | `HELD_OUT_ACTIVE_WITHOUT_PREMODEL_LOCK` | existe e funciona — **nunca acionado** (`registry_status: NOT_AVAILABLE` só gera WARN) |
| §B isolamento runtime/judge | `VERIFY_KIT.py`, nomes + marcadores | **funciona**: 6/6 SHA-256, 0 marcadores |
| §C test input closure | — | **sem código**; 4 testes violam a regra |
| §D IDs canônicos | `UNKNOWN_TOOL_IDS` + reference closure | **funciona** |
| §E provenance closure | `PROVENANCE_LOSS` | funciona, mas **auto-referencial** (compara duas saídas do mesmo produtor) |
| §F REVIEW vs APPROVAL | warning `BYPASSED_APPROVAL` | **NO-OP neste dado**: nenhuma pré-condição do ramo é satisfeita |
| §G teto de maturidade | `PRODUCTION_READY_WITHOUT_S4` | **funciona** |
| §H preflight obrigatório | o próprio script | funciona, mas **falha no runtime-bundle** que §B manda entregar |

### 1.2 Lado proposta — contado no repositório

| ADR | Tem verificação executável? | Onde |
|---|---|---|
| 0001 Vault L0 | **sim** | `cts/vault.py::resolve` |
| 0002 span + quote | **sim** | `G2-anchor` (4 modos de falha nomeados) |
| 0003 held-out em L0 | **sim** | `cts/cutter.py` (corte semeado + auditoria retroativa) |
| 0004 remover `confidence`, derivar `evidence_strength` | **não** | decisão de schema; a derivação por contagem de spans não foi implementada |
| 0005 dispersão | **sim** | `G3-dispersion` |
| 0006 adversário como portão | **não** | não implementado |
| 0007 Packager puro | **sim, mas nunca disparou** | `G5-closure` — mediu 0 no dado real |
| 0008 rubrica em L0 | **parcial** | só o check de IDs internos; o autor de rubrica não existe |
| 0009 métricas computáveis | **não** | Evaluator fora de escopo |
| 0010 teto por corpus | **sim** | `G6-ceiling` (n mínimo de Wilson calculado) |
| 0011 Consolidator condicional | **não** | não implementado |
| 0012 namespace de IDs | n/a | não requer código |
| 0013 ancoragem por campo (emenda) | **não** | escopo da Fase 6 |
| 0014 `UNDERPOWERED` trava o teto (emenda) | **sim** | `G3` + `G6`, com 3 meta-testes |

**7 completos + 1 parcial de 13 aplicáveis = 62%.** Cinco decisões minhas ainda são só texto — a mesma condição que critiquei na v0.1.1, em menor escala.

### 1.3 Leitura honesta dos dois números

19% × 62% **não é um placar**. As três diferenças que explicam o número, e só a primeira é mérito:

1. **Real:** onde a v0.1.1 escreveu proibição comportamental sem predicado ("não inventar rationale"), eu escrevi predicado estrutural ("o quote é substring do span"). Predicado estrutural é decidível; proibição comportamental não é.
2. **Seleção:** eu escolhi o que verificar depois de ver o que falhou. A v0.1.1 escreveu suas regras antes de ter o piloto.
3. **Maturidade:** a v0.1.1 tem um produto; eu tenho seis portões. As partes que ainda não escrevi são justamente onde a verificação é difícil — Extractor e Evaluator. É provável que minha taxa caia quando eu chegar lá.

---

## 2. O QUE CADA UMA DETECTOU NO MESMO MATERIAL

| Defeito no PILOT-001 | v0.1.1 detectou? | proposta detectou? |
|---|---|---|
| Governança de autonomia não ensinada pela fonte | **SIM** — SC-001, HIGH, 5 ADRs | **não** (ver §3) |
| `max_iterations: 5` inventado a partir de "3 a 5 testes" | **SIM** — SC-002, HIGH | **não** (ver §3, experimento) |
| 10 perguntas apresentadas como explícitas | **SIM** — SC-003, HIGH | **não** |
| Verificações/fallbacks de ferramenta virando política | **SIM** — SC-004, MEDIUM | **não** |
| Conceito promovido a princípio (5 blocos) | **SIM** — SC-005, MEDIUM | **não** |
| Runtime code atribuído à metodologia | **SIM** — SC-006, MEDIUM | **não** |
| `HC-002` APPROVAL onde a fonte só ensina revisão | **SIM** — SC2-001, HIGH | **não** |
| Stop conditions do compilador atribuídas à aula | **SIM** — SC2-002, MEDIUM | **não** |
| Campos de ferramenta formulados pelo compilador | **SIM** — SC2-003, MEDIUM | **não** |
| **Held-out inexistente** | **SIM** — `NOT_AVAILABLE`, `audit-decision` = `NOT_VERIFIABLE` | **SIM** — `G1/retroactive` NOT_ESTABLISHED |
| `source_excerpt` vazio em 44/44 | não | **SIM** — G2, `records_without_quote = 44/44` |
| 1 timestamp que não resolve na fonte (`EV-0001`, `0:29`) | não | **SIM** — G2, `END_MARK_NOT_FOUND` |
| 7 campos de classificação com entropia zero | não | **SIM** — G3 |
| Rubrica circular, medida | não | **SIM** — G5, 25 IDs internos na suíte |
| Nível S3 reivindicado sem base | declarado em prosa (§4 do PREFLIGHT) | **SIM** — G6 recusa, teto `S0_INGESTED`, n_min=16 |
| Invenção **no bundle compilado** | SC-001 alegou | **G5 mediu 0** — e o probe `origin` mostrou que 5/5 já estavam em L1 |

**Placar de detecção: v0.1.1 = 10 · proposta = 6 · em comum = 1** (held-out).

E a diferença mais importante não está no que cada uma detectou, mas no que fez com a detecção: **a v0.1.1 detectou o held-out inexistente e registrou honestamente; não bloqueou.** Compilou a S3 assim mesmo. Meu G6 recusa. Mesma detecção, consequência diferente — e a consequência é a arquitetura.

---

## 3. ONDE MEUS PORTÕES TERIAM IMPEDIDO — E ONDE NÃO

### 3.1 Teriam impedido

| Defeito | Portão | Como |
|---|---|---|
| Rótulo `BLIND_EVALUATION` em caso de recall | `G1/retroactive` | sem lock pré-extração, 10/10 casos que se declaram cegos são contaminados por construção |
| Rubrica derivada do artefato | `G5` | 25 IDs internos na suíte → FAIL |
| Reivindicação de S3/S4 sem base | `G6` | teto `S0_INGESTED`, `n_holdout=0`, `n_min=16` |
| Proveniência sem citação | `G2` | 44/44 sem quote → o pipeline para antes de compilar |
| Endereço de fonte inválido | `G2` | `EV-0001`, marca `0:29` ausente entre as 180 |

Ressalva: G2 teria parado o pipeline logo na extração. Isso impede **tudo** a jusante — mas por parada, não por diagnóstico. Parar cedo não é o mesmo que entender o defeito.

### 3.2 NÃO teriam impedido — com o experimento que prova

O caso mais limpo é **SC-002**. O adversário reprovou `max_iterations: 5` porque *"a fonte não diz que o ciclo de correção pode repetir no máximo cinco vezes"*. Rodei o experimento: peguei o trecho real da fonte e ancorei corretamente a regra inventada.

Fonte em `11:29–11:33`, verbatim:
> *"break it, fix it. Run it three to five times. Every time it produces something off brand or"*

Registro construído — span que resolve, quote verbatim, claim inventada:
```
span  : L0:068b4998c160:t=00:11:29-00:11:33      → resolve: True
quote : "break it, fix it. Run it three to five times. …"   → substring exata
claim : "O ciclo de correção pode repetir no máximo cinco vezes (max_iterations: 5)."
```
```
>>> G2 sobre a regra que SC-002 reprovou, bem ancorada:  PASS   (1/1 ancoradas)
```

**G2 aprova a invenção que o adversário reprovou.** A citação existe, resolve e é literal; o que não existe é a implicação entre "rode de 3 a 5 vezes" e "no máximo 5 iterações do ciclo de correção". G2 mede presença de âncora. Não mede se a afirmação cabe dentro dela.

O mesmo vale, por construção, para os outros oito achados: SC-001, SC-003, SC-004, SC-005, SC-006, SC2-001, SC2-002, SC2-003 são todos "a fonte não ensina isso" — nenhum é falha de endereço, de citação, de dispersão ou de conjunto.

**Dos 9 achados do adversário, meus portões estruturais pegam 0.** Eles param o build por outro motivo. Se o extrator tivesse feito o trabalho de citação corretamente, os 9 defeitos continuariam lá e todos os meus portões passariam.

E há um falso positivo meu que a v0.1.1 não tem: **G3 mede dispersão, não correção.** Um corpus em que o professor de fato só declara conteúdo explícito reprovaria em G3 por ser honesto. Distinguir "colapsado porque degenerado" de "colapsado porque a fonte é uniforme" não é decidível estruturalmente.

---

## 4. A PERGUNTA CENTRAL — o que o ChatGPT pegou que eu não pego

### 4.1 Resposta

**São complementares, e a fronteira é precisa e demonstrável.**

Meus portões são predicados **decidíveis sobre (artefato, L0)** que não exigem entender nenhum dos dois:
- este endereço resolve? (comparação de índice)
- esta string está naquele intervalo? (substring)
- esta distribuição tem quantos bits? (contagem)
- este conjunto está contido naquele? (containment)
- este número passa deste limiar? (aritmética)

Os achados do adversário são todos da forma **"a afirmação A excede o que a fonte S sustenta"** — uma relação de implicação entre dois textos. Implicação não é propriedade estrutural: não se computa de hash, offset ou frequência. O experimento de §3.2 é a prova operacional — a mesma tripla `span`+`quote`+`claim` passa em G2 com uma claim correta e com uma claim inventada, porque G2 não olha para a relação entre elas.

**Nenhuma quantidade de ancoragem fecha essa lacuna.** É por isso que a ADR-0013 declara o limite em vez de prometer que a ancoragem por campo o resolve.

### 4.2 Qual classe de defeito só o adversário alcança

| Classe | Exemplo medido | Por que é inalcançável estruturalmente |
|---|---|---|
| **Sobre-extensão** — a claim vai além do que o quote sustenta | SC-002 (`3 a 5 testes` → `max_iterations: 5`) | requer avaliar implicação entre dois enunciados |
| **Promoção de categoria** — conceito virando regra decisória | SC-005 (5 blocos, `CONCEPT` → princípio) | requer julgar se aquilo *controla decisão* |
| **Atribuição indevida** — política do compilador atribuída ao professor | SC2-002 (`TOOL_UNAVAILABLE` como ensinamento) | requer saber quem é o autor de uma ideia |
| **Falsa explicitude** — derivação apresentada como declaração | SC-003 (10 perguntas) | requer comparar forma da fonte com forma da claim |
| **Deriva semântica de rótulo** — REVIEW ≠ APPROVAL | SC2-001 | requer entender que os dois termos não são intercambiáveis naquele contexto |

Isto **confirma a ADR-0006 pelo caminho oposto ao que ela foi escrita**: eu mantive o adversário porque ele tinha valor medido; agora sei *por que* ele é insubstituível — ele ocupa a única classe de defeito que a verificação estrutural não alcança, e essa classe contém **9 dos 9** achados reais deste piloto.

### 4.3 Portões meus que são redundantes ou mal posicionados — marcados

Uma comparação em que eu venço em tudo é comparação mal feita. Três revisões:

| Portão | Veredito | Razão medida |
|---|---|---|
| `G5-closure/origin` | **REBAIXAR a probe** | não reprova nada; localiza camada. Chamá-lo de portão inflava a contagem. Já registrado na ADR-0013. |
| `G3-dispersion` | **REPOSICIONAR como triagem do adversário**, não bloqueador independente | SC-003 é um caso de degeneração que o adversário pegou **semanticamente** (10 perguntas rotuladas explícitas). G3 pega o mesmo padrão **estatisticamente e barato**. O valor de G3 não é bloquear sozinho — é apontar ao adversário onde olhar. E, como bloqueador solitário, tem o falso positivo do §3.2. |
| `G5-closure` (invenção) | **RETIDO, SEM DISPARO** | mediu 0 no único dado real disponível, e o probe mostra que a invenção entrou antes. Não é evidência de inutilidade — é ausência de evidência. Fica marcado assim até disparar uma vez. |

---

## 5. RISCOS QUE A MINHA ARQUITETURA INTRODUZ E A DO CHATGPT NÃO TEM

### 5.1 Custo do vault

| Item | Medido |
|---|---|
| Transcrição do PILOT-001 | 20.174 B |
| 3 frames PNG | 907.473 B |
| Bundle atual | ~68,5 KB |
| Vault desta aula | ~927 KB — **13× o bundle** |

Endereçamento por conteúdo duplica o material de fonte. Para uma aula de texto é irrelevante; para um curso de 40 aulas com vídeo, é escala de GB. **EM ABERTO:** se L0 guarda a mídia ou só a transcrição + hashes de frame. **Decide:** o primeiro corpus real com vídeo; se o custo inviabilizar, a garantia de imutabilidade cai para "hash sem cópia", que é mais fraca — o objeto pode sumir.

### 5.2 Custo de `span` + `quote` obrigatórios

44 evidências em 14,75 min de aula = **~3 recortes verbatim por minuto de fonte**. Para 40 aulas: ~1.800 recortes. É trabalho de extração que a v0.1.1 não paga — e ela não paga porque não verifica.

### 5.3 O risco mais sério: citar demais e modelar de menos

**O usuário nomeou este e ele está correto.** A forma mais barata de passar em G2 é fazer `claim` ≈ tradução do `quote`. Isso dá ancoragem perfeita e metodologia zero — e **a minha arquitetura não tem nenhuma métrica contra isso**.

Medi a linha de base no PILOT-001 (razão entre palavras da claim e palavras do span da fonte, 43 evidências resolvíveis):

| | valor |
|---|---|
| mediana | **0,373** |
| média | 0,416 |
| mínimo | 0,072 (`EV-0011`) |
| máximo | **0,944** (`EV-0015`) |
| claims ≤ 50% da fonte | 31 de 43 |
| claims maiores que a fonte | 0 |

O extremo superior é ilustrativo. `EV-0015`, razão 0,944:
> **fonte:** *"Without tools, your agent is just a chatbot with a fancy hat."*
> **claim:** *"O professor afirma que, sem ferramentas, o agente permanece essencialmente um chatbot sem capacidade prática de agir."*

Isso é tradução, não modelagem. E passaria em G2 com nota máxima.

**E aqui a v0.1.1 está à minha frente:** ela tem um instrumento contra exatamente esse modo de falha — `evaluator.md` §12 **SUMMARY_VS_SKILL**, com braço-baseline, `required_margin_over_baseline` e `baseline-summary.md`. Foi desenhado para detectar uma Skill que é só um resumo. **Minha arquitetura cria o incentivo para esse defeito e não traz o antídoto; a arquitetura que estou comparando trouxe o antídoto antes de ter o problema.**

Contramedida proposta, **não implementada** e registrada como EM ABERTO: métrica de divergência claim↔quote no nível do corpus (mediana da razão, ou sobreposição de tokens após tradução), com piso — se as claims são cópias das quotes, o extrator está transcrevendo. **Decide:** dois corpora, um com extração conhecidamente boa e um com transcrição disfarçada. Não tenho os dois; qualquer limiar hoje seria chute.

### 5.4 Outros riscos que introduzo

| Risco | Estado |
|---|---|
| G3 reprova corpus honestamente uniforme (falso positivo) | reconhecido, sem solução estrutural — pertence ao adversário |
| Cutter sem guarda de tamanho mínimo: cortaria 20% de uma aula única, destruindo a única demonstração ponta a ponta (82 s, 9,1%) | **defeito aberto** — o cutter deveria recusar cortar abaixo de um corpus mínimo, e hoje não recusa |
| `N_MIN = 20` e `θ = 0,50` continuam **não calibrados** | declarado desde a ADR-0005; a ADR-0014 decidiu a consequência, não o valor |
| 5 das 14 ADRs ainda sem código | o mesmo defeito que critiquei, em escala menor |

---

## 6. SÍNTESE

| Eixo | v0.1.1 (ChatGPT) | proposta (Claude) |
|---|---|---|
| Enunciados com verificação executável | 7 de 36 (19%) | 8 de 13 (62%) — com viés de seleção declarado |
| Defeitos detectados no PILOT-001 | **10** | 6 |
| Achados semânticos ("a fonte não ensina isso") | **9** | **0** |
| Achados estruturais (âncora, dispersão, teto, circularidade) | 1 | **6** |
| Detectou e **bloqueou** o held-out inexistente | detectou, **não bloqueou** | detecta e bloqueia |
| Antídoto contra "resumo disfarçado de skill" | **tem** (SUMMARY_VS_SKILL) | **não tem** |
| Produto entregue | Skill completa, S3, com kit de teste travado | 6 portões e 26 meta-testes |

**Conclusão que a evidência sustenta:** as duas arquiteturas cobrem classes disjuntas de defeito e nenhuma substitui a outra. O adversário da v0.1.1 pegou 9 defeitos reais que a verificação estrutural não alcança nem em princípio — e o experimento de §3.2 mostra que meu portão principal **aprova** o defeito que o adversário reprovou. Meus portões pegam 6 defeitos que o adversário não viu e, mais importante, transformam em bloqueio o que a v0.1.1 apenas documentava.

A arquitetura correta é a soma: portões estruturais como piso barato e determinístico, adversário como camada semântica insubstituível, e ambos alimentando o mesmo teto de maturidade. Foi o que a ADR-0006 decidiu manter — e esta comparação mostra que a decisão estava certa por uma razão mais forte do que a que eu tinha quando a escrevi.

---

**FIM DA FASE 5.** Nenhum código foi ajustado para melhorar o resultado desta comparação — a única alteração de código foi a ADR-0014, que torna o portão **mais estrito**. Nenhum arquivo de `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado.
