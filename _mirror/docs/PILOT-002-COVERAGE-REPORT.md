# PILOT-002 — COVERAGE REPORT

**Gerado:** `2026-08-11T23:36:43+00:00` · gerador `pilot002_coverage_report.py` · **somente medição**, READ-ONLY.

Relatório gerado por script; nenhum número foi digitado. Mesmo formato do `L0_COVERAGE_MAP` do PILOT-001, para os dois corpora ficarem comparáveis.


## 0. Portão de hash

| arquivo | esperado | obtido | autoridade da expectativa | veredito |
|---|---|---|---|---|
| `Course-to-Skill-Claude/pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt` | `85ea229011a989ea…` | `85ea229011a989ea…` | informada na tarefa | **CONFERE** |
| `Course-to-Skill-Claude/pilots/PILOT-002/01_COMPILED-SKILL/v0.1.0/EVIDENCE(1).jsonl` | `a23c837d37cbc9e6…` | `a23c837d37cbc9e6…` | `SHA256SUMS(2).txt` do próprio pacote, linha `EVIDENCE.jsonl` | **CONFERE** |

> O arquivo em disco chama-se `EVIDENCE(1).jsonl`, não `EVIDENCE.jsonl` — renomeação de download do Drive. O conteúdo é o canônico: o hash bate com a linha `EVIDENCE.jsonl` do `SHA256SUMS(2).txt` publicado no próprio pacote. A expectativa do EVIDENCE **não foi informada na tarefa**; a autoridade usada está declarada na tabela.


Os dois portões passam. A medição prossegue.


## 1. Entrada e geometria

| item | valor |
|---|---|
| sha256 do L0 cortado | `85ea229011a989ea…` |
| bytes / linhas / marcas | 96246 / 2956 / 733 |
| duração nominal do vídeo | 81:37 = 4897s |
| held-out removido (lock G1) | 513s |
| **extensão do corpus de treino** | **73:04 = 4384s** |
| soma dos segmentos retidos | 4384s |
| geometria fecha | **SIM** |
| última marca | 81:35 |
| evidências | 44 |
| citações (segmento × evidência) | 282 |
| `source_file` único | sim |
| `source_sha256` declarado bate com o arquivo | **sim** |

> **Tradução de gramática.** O PILOT-001 endereça L0 por tempo; o PILOT-002 endereça por **linha** (`#L9-L19`). Para reportar segundos, cada faixa de linhas foi traduzida para os segmentos de marca que ela toca. Nos dois pontos de corte a marca seguinte está a 200s e 326s de distância — esse salto é o buraco do held-out, não fala, e o segmento de fronteira termina no início declarado do corte. A soma dos segmentos retidos (4384s) fecha com a extensão declarada (4384s), que é a checagem de que a tradução não inventou nem perdeu tempo.


## 2. Cobertura de L0 pelas 44 evidências

| métrica | valor |
|---|---|
| extensão do corpus de treino | 73:04 (4384s) |
| **coberto** | **27:10 (1630s) — 37.2%** |
| **virgem** | **45:54 (2754s) — 62.8%** |
| blocos cobertos contíguos | 35 |
| **blocos virgens contíguos** | **37** |
| **maior bloco virgem** | **220s** (26:32–30:12) |
| blocos virgens ≥ 60s | 15 |
| coberto + virgem = extensão | sim |

### 2.1 Lado a lado com o PILOT-001

| piloto | coberto | extensão | cobertura |
|---|---|---|---|
| PILOT-001 | 665s | 905s | **73.5%** |
| PILOT-002 | 1630s | 4384s | **37.2%** |

**Diferença: -36.3 pontos percentuais.** 
O PILOT-002 cobre proporcionalmente **menos** da sua fonte que o PILOT-001, sobre um corpus quase cinco vezes maior.


> As duas medidas usam o mesmo denominador conceitual (extensão da fonte disponível) e o mesmo numerador (união dos spans citados pelas evidências de L1). A comparação é legítima nesse nível. O que **não** é comparável é a granularidade: o PILOT-001 cita por timestamp, e o PILOT-002 cita por faixa de linhas, que é mais grossa — uma citação de linha arrasta o segmento de marca inteiro. Isso empurra a cobertura do PILOT-002 para **cima**, não para baixo.


### 2.2 Os 15 maiores blocos virgens (≥ 60s)

| início | fim | dur | triagem mecânica | trecho |
|---|---|---|---|---|
| 26:32 | 30:12 | 220s | CANDIDATO_HELD_OUT | of it like GitHub is kind of like Google cloud or one drive kind of keeping track of all the version of your a… |
| 38:38 | 41:41 | 183s | DESCARTE | of like Lego pieces. You piece them all together into bigger applications. So this why that's why we have comp… |
| 56:04 | 59:02 | 178s | CANDIDATO_HELD_OUT | to revert back to changes that are being worked on maybe like June 18th right if I were to scroll down maybe l… |
| 18:58 | 21:51 | 173s | DESCARTE | front-end framework here that will basically help you to building applications which we will talk a little mor… |
| 65:00 | 67:46 | 166s | CANDIDATO_HELD_OUT | on the web or connecting to maybe like Stripe or PayPal or people to connect to Slack or Jira whichever softwa… |
| 5:49 | 8:33 | 164s | CANDIDATO_HELD_OUT | going to give a name for that folder and just going to click on create. And then here we're just going to clic… |
| 32:23 | 35:06 | 163s | CANDIDATO_HELD_OUT | grid or canvas or something. But you can see that we have still the functionality working, right? I can still … |
| 72:59 | 75:33 | 154s | CANDIDATO_HELD_OUT | think of like agents as the agents that we're going to you know do the executions and each agent here can have… |
| 0:34 | 2:49 | 135s | DESCARTE | curriculum covers how to connect remote tools using the model context protocol, integrate version control with… |
| 8:55 | 11:05 | 130s | CANDIDATO_HELD_OUT | have. So if I were to say hi for example and what's going to happen here is that it's going to do some thinkin… |
| 79:27 | 81:37 | 130s | CANDIDATO_HELD_OUT | because I made videos on claw code for over more than a year now. Okay, since it was released last year, I sta… |
| 76:14 | 78:17 | 123s | DESCARTE | are just learning started learning claw code, then that's more than enough. But if you're trying to use this e… |
| 59:27 | 60:58 | 91s | DESCARTE | it is. But master branch basically means that this is the current branch that we're in and we only have this o… |
| 62:42 | 63:53 | 71s | CANDIDATO_HELD_OUT | claw code all right so by now you pretty much have all the basics down for how to use claw code the next thing… |
| 36:18 | 37:28 | 70s | CANDIDATO_HELD_OUT | package.json, those dependencies, it's going to creating all those no module here inside of it. So all the lib… |

> A triagem é a de `cts/coverage.py`, cujos marcadores foram extraídos do PILOT-001 (curso de marketing). Sobre um curso de ferramenta de programação ela é **indicativa, não calibrada** — vale para comparar formato, não para decidir held-out.


## 3. As 4 estruturas multi-ramo

A pergunta é se a estrutura que justifica a fonte entrou na Skill. Checagem em dois níveis: a evidência **alcança** as linhas da tabela, e as *claims* dessas evidências **nomeiam cada ramo**. O segundo nível é mecânico (o termo aparece ou não) e serve para tornar a chamada revisível, não para substituí-la.

| tabela | âncora (linhas) | evidência que alcança o núcleo | coberta | ramos nomeados |
|---|---|---|---|---|
| CLI × MCP | L2213–2574 | `E037`, `E038` | **SIM** | 3/3 |
| escopos de instalação de Skill | L1105–1127 | `E014` | **SIM** | 2/3 |
| .claude/ × agents/ | L1563–1660 | `E023` | **SIM** | 3/3 |
| escolha de IDE | L145–286 | `E003` | **SIM** | 3/3 |


**CLI × MCP** — COBERTA  
núcleo em L2409–2481 (onde a fonte pergunta 'what's the difference between CLI or MCP? Which one should you really use?' e responde).  
evidência que alcança a âncora: `E036`, `E037`, `E038`, `E039`, `E040`.  

| ramo | nomeado na claim |
|---|---|
| ramo CLI | sim |
| ramo MCP | sim |
| critério de escolha | sim |


**escopos de instalação de Skill** — COBERTA  
núcleo em L1109–1121 (as opções oferecidas pelo instalador, em 30:18–30:35).  
evidência que alcança a âncora: `E014`, `E015`.  

| ramo | nomeado na claim |
|---|---|
| escopo de usuário / global | sim |
| projeto, compartilhado | sim |
| projeto, só para você | **não** |


**.claude/ × agents/** — COBERTA  
núcleo em L1583–1612 (onde a fonte contrasta 'universal for all the AI agent frameworks' com 'only specific for claw code only').  
evidência que alcança a âncora: `E023`, `E024`.  

| ramo | nomeado na claim |
|---|---|
| agents/ universal | sim |
| .claude/ específico | sim |
| fonte da verdade / referência | sim |


**escolha de IDE** — COBERTA  
núcleo em L169–185 (a seção dedicada 'Choosing an IDE & Installing VS Code'; o FAQ ('do I need cursor to use it?') reafirma em L2839–2867).  
evidência que alcança a âncora: `E003`, `E004`.  
âncora secundária L2839–2870: `E043`, `E044`.

| ramo | nomeado na claim |
|---|---|
| VS Code | sim |
| alternativas de IDE | sim |
| terminal puro | sim |


> **Nenhuma das 4 tabelas ficou fora.** Todas têm evidência alcançando o núcleo. Não há achado grave no critério pedido.


> **Ressalva, num nível abaixo do achado grave:** 1 tabela(s) têm evidência mas a *claim* não nomeia todos os ramos — **escopos de instalação de Skill** (falta: projeto, só para você). A faixa de linhas citada **cobre** o ramo; o que não o alcança é o texto da afirmação. Isso é compressão na redação da evidência, não ausência de fonte.


## 4. Os 5 MODEL_INFERENCE

| id | linhas | tempo | claim |
|---|---|---|---|
| `E008` | L563–585 | 16:48–17:29 | For a /goal workflow, planning requirements and expectations before execution is the source-supported sequence; treating this as a recommended workflow is a compilation inference from the demonstrated order. |
| `E010` | L763–785 | 21:51–22:34 | When source assets are available, localizing them before the build can reduce guessing; this is generalized from the demonstrated asset-pull refinement. |
| `E017` | L1177–1191 | 31:55–32:23 | The source shows a skill asking clarification questions for a redesign, but does not establish a universal missing-input policy; therefore that example must not be promoted into a default missing_input_action. |
| `E040` | L2541–2569 | 71:05–71:52 | Before a destructive remote deletion, the example checks the account projects, identifies the exact target, and preserves unrelated projects; compiling this into an exact-target verification safeguard is an inference from the demonstrated behavior. |
| `E043` | L2827–2841 | 78:17–78:48 | The cut states that permission-mode choice affects safety but omits the actual permission-mode definitions between 11:48 and 15:08; therefore the compilation must not reconstruct a default permission policy. |

**Interseção com as 4 tabelas multi-ramo: nenhuma.**


Leitura do conjunto: **não são as decisões condicionais.** As quatro estruturas de decisão do curso — CLI × MCP, escopos de Skill, `.claude/` × `agents/`, escolha de IDE — estão **todas** em evidência `SOURCE_EXPLICIT`. Nenhuma delas se apoia numa inferência.


O que os 5 são, um a um, está na tabela acima; o padrão é este: **quatro dos cinco são marcadores de contenção, não de conteúdo.** `E017`, `E040` e `E043` dizem explicitamente o que a compilação **não pode** fazer — não promover um exemplo a `missing_input_action` padrão, não generalizar uma verificação de alvo, não reconstruir política de permissão a partir do que foi cortado. `E008` marca que tratar a ordem demonstrada como workflow recomendado é inferência. Só `E010` é generalização de procedimento periférico (localizar assets antes do build).


Ou seja: o compilador usou a categoria `MODEL_INFERENCE` sobretudo para **declarar limite**, e não para carregar decisão. Isso é coerente com o `COMPILATION_MANIFEST`, que lista `missing_input_action` entre os 4 campos não definidos — exatamente o campo que `E017` se recusa a preencher.


## 5. Held-out: nenhuma evidência cita span cortado

Duas janelas foram conferidas, porque não são a mesma coisa:

| janela | intervalo | o que é | resultado |
|---|---|---|---|
| janelas do lock (G1) | 11:55–15:08, 44:40–50:00 | o corte declarado | **0 violação(ões)** |
| janelas pedidas na conferência | 11:48–15:08, 44:34–50:00 | alinhadas à marca que ABRE cada corte | **0 violação(ões)** |

**CONFIRMADO: nenhuma das 44 evidências cita span dentro de qualquer das duas janelas, nem na leitura estrita do lock nem na leitura mais larga pedida.**


> As duas janelas diferem no início: o lock declara 11:55 e 44:40, e o corte removeu os segmentos INTEIROS que as contêm, cujas marcas abrem em 11:48 e 44:34. As marcas 11:48 e 44:34 **sobrevivem** no corpus de treino. Conferir só a janela do lock deixaria 13s de fronteira sem checar; por isso as duas foram medidas.


### 5.1 Menção textual, que não é citação

| id | status | claim |
|---|---|---|
| `E043` | MODEL_INFERENCE | The cut states that permission-mode choice affects safety but omits the actual permission-mode definitions between 11:48 and 15:08; therefore the compilation must not reconstruct a default permission policy. |

> Isto **não é violação e é importante não confundir**: a evidência acima *escreve* o intervalo do held-out no texto da afirmação, mas o span que ela cita fica fora dele. É o oposto de vazamento — é o registro de que o material está ausente, que é justamente o que se espera de uma compilação honesta sobre corpus cortado. O que a checagem proíbe é citar span dentro da janela, e isso não acontece.


## 6. Todas as 44 evidências

| id | tipo | linhas | tempo | segs | claim |
|---|---|---|---|---|---|
| `E001` | SOUR | L9–19 | 0:07–0:34 | 4 | The course is presented for absolute beginners and states no previous technical or devel… |
| `E002` | SOUR | L119–133 | 2:49–3:17 | 5 | Installation is demonstrated from the Claude Code quick-start documentation using the re… |
| `E003` | SOUR | L169–185 | 4:02–4:30 | 5 | The instructor recommends an IDE, specifically VS Code in the demonstration, to combine … |
| `E004` | SOUR | L221–241 | 5:16–5:49 | 6 | Projects are kept in an opened/created folder so project files remain organized and file… |
| `E005` | SOUR | L361–373 | 8:33–8:55 | 4 | A Claude Code session is started from the VS Code terminal by typing claude. |
| `E006` | SOUR | L465–481 | 11:05–11:36 | 5 | A previous Claude Code session can be resumed using /resume. |
| `E007` | SOUR | L527–561 | 15:51–16:53 | 10 | The /goal command is described as allowing autonomous execution in a loop, with an evalu… |
| `E008` | MODE | L563–585 | 16:48–17:29 | 7 | For a /goal workflow, planning requirements and expectations before execution is the sou… |
| `E009` | SOUR | L619–647 | 18:10–18:58 | 8 | In the demonstrated planning flow, Claude asks the user questions about implementation d… |
| `E010` | MODE | L763–785 | 21:51–22:34 | 7 | When source assets are available, localizing them before the build can reduce guessing; … |
| `E011` | SOUR | L831–845 | 23:33–24:02 | 5 | A development-server link shown in the example is local-only and cannot be accessed by a… |
| `E012` | SOUR | L873–889 | 24:29–25:00 | 5 | A skill is described as a reusable workflow, guide, or SOP that instructs Claude Code or… |
| `E013` | SOUR | L901–951 | 25:13–26:32 | 14 | The fix-ticket example packages a multi-step bug-fix pipeline into a reusable workflow, … |
| `E014` | SOUR | L1105–1127 | 30:12–30:53 | 7 | The skill installer offers scope choices including user/global scope and project scope f… |
| `E015` | SOUR | L1125–1141 | 30:41–31:11 | 5 | After installing a plugin/skill in the example, /reload plugins is used to apply the cha… |
| `E016` | SOUR | L1149–1171 | 31:16–31:55 | 7 | A skill can be triggered through natural-language instruction or by specifying the skill… |
| `E017` | MODE | L1177–1191 | 31:55–32:23 | 5 | The source shows a skill asking clarification questions for a redesign, but does not est… |
| `E018` | SOUR | L1305–1317 | 35:06–35:29 | 4 | Markdown files are described as documentation/written documentation. |
| `E019` | SOUR | L1325–1337 | 35:35–35:59 | 4 | package.json is described as containing dependency lists and commands the application re… |
| `E020` | SOUR | L1341–1351 | 35:59–36:18 | 3 | The public folder is described as holding public assets such as logos and images. |
| `E021` | SOUR | L1403–1421 | 37:28–38:03 | 6 | The eval folder is described as created by /goal to evaluate whether requirements are me… |
| `E022` | SOUR | L1419–1445 | 37:52–38:38 | 8 | The components folder is described as containing reusable smaller application components… |
| `E023` | SOUR | L1575–1607 | 41:41–42:36 | 9 | The .agents location is presented as the source of truth for universal agent skills, whi… |
| `E024` | SOUR | L1615–1657 | 42:43–43:53 | 12 | AGENTS.md and CLAUDE.md are described as system-prompt locations, with AGENTS.md for uni… |
| `E025` | SOUR | L1697–1705 | 50:00–50:17 | 3 | /compact is described as summarizing older conversations. |
| `E026` | SOUR | L1713–1723 | 50:23–50:46 | 4 | /model is used to change the active model. |
| `E027` | SOUR | L1757–1771 | 51:28–51:59 | 5 | Rewind is described as restoring both code and conversation to a previous checkpoint. |
| `E028` | SOUR | L1793–1823 | 52:23–53:17 | 9 | Plugins can be managed/uninstalled, and an installed skill can be removed by deleting it… |
| `E029` | SOUR | L1847–1873 | 53:41–54:30 | 8 | For project version control, the instructor recommends GitHub as a simple/free option an… |
| `E030` | SOUR | L1871–1893 | 54:19–55:00 | 7 | GitHub commit history is presented as a version tree where individual commits can be ins… |
| `E031` | SOUR | L1919–1937 | 55:29–56:04 | 6 | Branches are described as allowing separate lines of change such as beta or version-two … |
| `E032` | SOUR | L2063–2075 | 59:02–59:27 | 4 | The example explicitly avoids committing sensitive information to cloud version control. |
| `E033` | SOUR | L2139–2153 | 60:58–61:29 | 5 | The demonstrated VS Code flow stages changes, commits them, and syncs/pushes them to Git… |
| `E034` | SOUR | L2175–2191 | 61:52–62:19 | 5 | GitHub collaborators can be added to work on the same repository, and version control ca… |
| `E035` | SOUR | L2195–2207 | 62:19–62:42 | 4 | A specific Git commit can be reverted by giving its commit ID to Claude Code and asking … |
| `E036` | SOUR | L2261–2295 | 63:53–65:00 | 10 | MCP is defined as Model Context Protocol connecting AI agents with external tools, with … |
| `E037` | SOUR | L2409–2431 | 67:46–68:30 | 7 | CLI is described as terminal-based command execution, while MCP provides a standardized … |
| `E038` | SOUR | L2459–2481 | 69:07–69:42 | 6 | The instructor recommends CLI for speed/token efficiency and MCP for security, team acce… |
| `E039` | SOUR | L2485–2505 | 69:42–70:18 | 6 | The deployment example creates a new Vercel project through the connected CLI after logi… |
| `E040` | MODE | L2541–2569 | 71:05–71:52 | 8 | Before a destructive remote deletion, the example checks the account projects, identifie… |
| `E041` | SOUR | L2579–2615 | 71:58–72:59 | 10 | The FAQ distinguishes skills as repeatable SOP/workflows, MCPs as tools/connectors, and … |
| `E042` | SOUR | L2719–2741 | 75:33–76:14 | 7 | For a maintained or long-term project where rollback matters, version control with Git/G… |
| `E043` | MODE | L2827–2841 | 78:17–78:48 | 5 | The cut states that permission-mode choice affects safety but omits the actual permissio… |
| `E044` | SOUR | L2839–2867 | 78:37–79:27 | 8 | Cursor is not required; VS Code or another IDE with a terminal can be used to run Claude… |

## 7. Blocos cobertos, para conferência

| início | fim | duração |
|---|---|---|
| 0:07 | 0:34 | 27s |
| 2:49 | 3:17 | 28s |
| 4:02 | 4:30 | 28s |
| 5:16 | 5:49 | 33s |
| 8:33 | 8:55 | 22s |
| 11:05 | 11:36 | 31s |
| 15:51 | 17:29 | 98s |
| 18:10 | 18:58 | 48s |
| 21:51 | 22:34 | 43s |
| 23:33 | 24:02 | 29s |
| 24:29 | 25:00 | 31s |
| 25:13 | 26:32 | 79s |
| 30:12 | 31:11 | 59s |
| 31:16 | 32:23 | 67s |
| 35:06 | 35:29 | 23s |
| 35:35 | 36:18 | 43s |
| 37:28 | 38:38 | 70s |
| 41:41 | 42:36 | 55s |
| 42:43 | 43:53 | 70s |
| 50:00 | 50:17 | 17s |
| 50:23 | 50:46 | 23s |
| 51:28 | 51:59 | 31s |
| 52:23 | 53:17 | 54s |
| 53:41 | 55:00 | 79s |
| 55:29 | 56:04 | 35s |
| 59:02 | 59:27 | 25s |
| 60:58 | 61:29 | 31s |
| 61:52 | 62:42 | 50s |
| 63:53 | 65:00 | 67s |
| 67:46 | 68:30 | 44s |
| 69:07 | 70:18 | 71s |
| 71:05 | 71:52 | 47s |
| 71:58 | 72:59 | 61s |
| 75:33 | 76:14 | 41s |
| 78:17 | 79:27 | 70s |

---

**Escopo:** somente medição. Nada foi cortado, nenhuma evidência foi reescrita, nenhum arquivo de `pilots/`, `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado. O único arquivo escrito é este relatório.
