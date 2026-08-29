# COURSE-GAP-REPORT — PILOT-002

*Gerado da compilação evidência→Skill. Nenhum número digitado.*

## Resumo

| | |
|---|---|
| regras | 149 |
| workflows | 43 |
| passos | 145 |
| evidências consumidas | 386 de 448 (86.2%) |
| **regras só de inferência genuína** | **6** |
| campos UNDEFINED | 1000 |

## Campos UNDEFINED — lacuna pedagógica

Os quatro preservados por decisão. Nenhum é metadado: os quatro são perguntas que a execução faz e o curso não responde.

| campo | vezes | a pergunta que o curso não responde |
|---|---|---|
| `missing_input_action` | 292 | o que fazer quando falta um insumo obrigatório |
| `iteration_limit` | 288 | quantas vezes repetir antes de desistir |
| `autonomy` | 281 | até onde o agente pode agir sozinho antes de parar |
| `precedence` | 139 | qual regra ganha quando duas se aplicam |

> **Nenhum metadado nesta lista.** O esquema é subconjunto: os 30 campos legados que eram metadado foram descartados por decisão registrada, com o motivo escrito em `ctss/schema.py`. O que sobra aqui é lacuna do curso.

---

## Regras e passos que o curso NÃO ensinou

**12** entidades se apoiam SÓ em inferência genuína. Funcionam — mas o modelo as preencheu, não o curso. Para cada uma, a cadeia:

### `S-0004` — Localizar a documentação oficial

**a regra diz:** Fazer uma busca no Google pela documentação da ferramenta para obter as instruções de instalação → Fazer uma busca no Google pela documentação da ferramenta para obter as instruções de instalação

> **o curso disse** (2:38): So if you want to get started with claw code here you

**2:44**

can see simply just going to Google search the clock documentation

**o modelo concluiu:** Para obter as instruções de instalação, basta fazer uma busca no Google pela documentação oficial da ferramenta

**distância:** o curso não diz que a busca serve para obter instruções de instalação nem chama a documentação de 'oficial'; o modelo inferiu de 'Google search the documentation'

### `S-0053` — Pré-requisito: quadro de acompanhamento de tickets

**a regra diz:** Manter um quadro de acompanhamento de projeto (ex.: kanban) ou sistema onde todos os bugs e issues são registrados → Manter um quadro de acompanhamento de projeto (ex.: kanban) ou sistema onde todos os bugs e issues são registrados

> **o curso disse** (25:06): any software developer teams is they

**25:13**

have a project tracking board where they log all the bugs that they have maybe like a camman board or like a system

**25:19**

where they keep track of all the issues.

**o modelo concluiu:** O workflow assume que a equipe de desenvolvimento mantém um quadro de acompanhamento de projeto (ex.: kanban) onde todos os bugs e issues são registrados

**distância:** o curso não diz que o workflow pressupõe esse quadro; o modelo inferiu da observação geral de que equipes de desenvolvimento têm board de bugs

### `S-0066` — Abrir tela de discovery de plugins

**a regra diz:** Executar o comando /plugins para entrar na tela de discovery, onde os plugins disponíveis (incluindo front end design) podem ser instalados → Executar o comando /plugins para entrar na tela de discovery, onde os plugins disponíveis (incluindo front end design) podem ser instalados

> **o curso disse** (29:08): Here you can see we have our plugins. So if I

**29:15**

were to enter this, you can see that currently we're in a discovery. We're can installing any plugins we want. You

**29:20**

can see that we have our front end of design plugins, which is exactly the same as this one right here.

**o modelo concluiu:** O comando /plugins abre uma tela de discovery no Claude Code onde é possível instalar plugins disponíveis, incluindo o front-end design

**distância:** o curso não menciona o comando /plugins; o modelo inferiu da menção a 'nossos plugins' e à tela de discovery para instalação

### `R-0054` — Recarregar plugins após instalar skill

**a regra diz:** UNDEFINED → Digitar /reload-plugins na sessão do Claude Code para aplicar as mudanças

> **o curso disse** (30:41): once we have the front end design skill installed, you can see we can just simply just type in /reload plugins to

**30:53**

actually apply the changes.

**o modelo concluiu:** Depois de instalar a skill, é necessário executar /reload-plugins para aplicar as mudanças

**distância:** o curso não diz ser necessário nem grafa '/reload-plugins'; o modelo inferiu de 'simply just type in /reload plugins' para aplicar mudanças

### `R-0058` — Acionar skill por slash command

**a regra diz:** A skill possui um slash command correspondente (ex.: /frontend-design) → Invocar a skill diretamente via slash command

> **o curso disse** (31:27): Now the other option you can do this is you can just specify the skill itself like using a slash

**31:32**

command using slashfront of design

**o modelo concluiu:** A segunda forma de acionar uma skill é especificá-la explicitamente via slash command (ex.: /frontend-design)

**distância:** o curso não grafa '/frontend-design' nem numera como segunda forma; o modelo inferiu de 'other option' e 'slashfront of design'

### `S-0076` — Agente instala a skill localmente

**a regra diz:** O agente processa o link e instala a skill na máquina local do usuário → O agente processa o link e instala a skill na máquina local do usuário

> **o curso disse** (33:36): to happen here is that claw code is going to install ining this skill onto your local machine.

**o modelo concluiu:** Ao receber o link, o agente instala a skill na máquina local do usuário.

**distância:** o curso não menciona recebimento de link; o modelo inferiu do trecho que diz apenas que o Claude Code instala a skill localmente

### `R-0066` — Ignorar package-lock.json

**a regra diz:** Arquivo é package-lock.json, gerado automaticamente a cada instalação das dependências declaradas → Não se preocupar com ele; não exige atenção do desenvolvedor

> **o curso disse** (35:46): the the package.json package log here really don't need to worry about too much. These are only

**o modelo concluiu:** O package-lock.json não precisa de atenção do desenvolvedor: é gerado automaticamente a cada instalação das dependências declaradas.

**distância:** o curso não explica geração automática a cada instalação de dependências; o modelo inferiu de 'não precisa se preocupar muito' com package.json/package-lock

### `S-0083` — Conferir a rota renderizada no navegador

**a regra diz:** Verificar que a homepage renderiza a rota /tier-list e conferir a página correspondente exibida no navegador → Verificar que a homepage renderiza a rota /tier-list e conferir a página correspondente exibida no navegador

> **o curso disse** (39:13): slashtier list and that's going to be slashtier list right here which is this page right here okay and this is the

**o modelo concluiu:** A homepage renderiza a rota /tier-list, que corresponde à página exibida no navegador.

**distância:** o curso não diz que a homepage renderiza essa rota; o modelo inferiu de "/tier-list, que é esta página aqui"

### `S-0114` — Revisar conteúdo do commit inicial

**a regra diz:** Verificar os arquivos incluídos no commit inicial (aplicação, imagens, evals, documentação) e os itens excluídos pelo gitignore → Verificar os arquivos incluídos no commit inicial (aplicação, imagens, evals, documentação) e os itens excluídos pelo gitignore

> **o curso disse** (58:02): So what we have

**58:08**

committed here you can see uh 133 files here in one initial commits. So the entire NexJS applications the images the

**58:16**

playrs for the evaluations and also the documentations.

**o modelo concluiu:** O commit inicial do projeto incluiu 133 arquivos: a aplicação Next.js, imagens, arquivos de avaliação (evals) e a documentação

**distância:** o curso não diz "arquivos de avaliação (evals)"; o modelo interpretou assim o trecho "playrs for the evaluations" no commit de 133 arquivos

> **o curso disse** (58:21): things that we I have

**58:21**

exclude here you can see is the existing ignore no modules the NexJS so like I

**58:27**

said before right those are the things that are not really relevant for our projects so those dot folders and also

**58:33**

no module here are not going to be relevant

**o modelo concluiu:** node_modules e as pastas dot do Next.js foram excluídas do commit via gitignore porque não são relevantes para o projeto

**distância:** o curso não atribui a exclusão ao gitignore nem chama as dot folders de Next.js; o modelo inferiu de "o ignore existente, no modules, o NextJS... não relevantes"

> **o curso disse** (58:39): and you can see that if we were to look at the color for those fog

**58:44**

explore you can see these are all grayed out right and the ones that are committed are not grayed out. Okay, so

**58:51**

the grade out ones are be part of the get commits. So they will not be committed if there's any changes that

**58:57**

are inside of that folder.

**o modelo concluiu:** No file explorer do editor, arquivos e pastas acinzentados são os ignorados pelo git e não serão commitados, enquanto os não acinzentados fazem parte do commit

**distância:** o curso não diz que acinzentado significa "ignorado pelo git"; o modelo inferiu de "os acinzentados não serão commitados"

### `R-0103` — Ler estado de ignore pelo file explorer

**a regra diz:** Arquivos/pastas exibidos acinzentados no file explorer do editor → Interpretar acinzentado como ignorado pelo git (não será commitado) e não acinzentado como parte do commit

> **o curso disse** (58:39): and you can see that if we were to look at the color for those fog

**58:44**

explore you can see these are all grayed out right and the ones that are committed are not grayed out. Okay, so

**58:51**

the grade out ones are be part of the get commits. So they will not be committed if there's any changes that

**58:57**

are inside of that folder.

**o modelo concluiu:** No file explorer do editor, arquivos e pastas acinzentados são os ignorados pelo git e não serão commitados, enquanto os não acinzentados fazem parte do commit

**distância:** o curso não diz que acinzentado significa "ignorado pelo git"; o modelo inferiu de "os acinzentados não serão commitados"

### `R-0128` — Escolher MCP para conexão com sistema externo

**a regra diz:** O objetivo é conectar Claude Code à ferramenta para poder usá-la → Usar um MCP como mecanismo de conexão à ferramenta

> **o curso disse** (72:16): MTPs is kind of like tools, right? You want to connect it to your tools like Slack or Jira or sales, whatever

**72:22**

tools you want to have clock access to to be able to use it. Then that's what MTP is for.

**o modelo concluiu:** MCPs são as ferramentas: servem para conectar Claude Code a sistemas externos como Slack, Jira ou Salesforce, dando-lhe acesso para usá-los

**distância:** o curso não menciona Claude Code nem Salesforce; o modelo inferiu de "tools like Slack or Jira or sales" e do contexto

### `R-0148` — Dominar fundamentos antes de recursos avançados

**a regra diz:** Fundamentos ainda não dominados → Aprender/consolidar os fundamentos antes de avançar para os recursos avançados

> **o curso disse** (80:04): fundamentals right you still need to know this before you actually know or try to learn about like altra code or

**80:10**

try to learn dynamic workflow building loops right you still need to know the foundation before you actually know

**o modelo concluiu:** É necessário dominar os fundamentos antes de tentar aprender recursos avançados como o Agent SDK, construção de workflows dinâmicos e loops

**distância:** o curso não menciona "Agent SDK"; o modelo inferiu de "altra code" na transcrição, mantendo apenas workflows dinâmicos e loops como avançados

---

## Evidência não consumida

| disposição | n | significado |
|---|---|---|
| NON_METHODOLOGICAL | 48 | contexto, motivação, mercado — não é método |
| GAP | 15 | é método, mas a fonte não dá o suficiente |

### Método que a fonte menciona sem especificar

| onde | o que o curso disse |
|---|---|
| **0:14** | O currículo cobre fundamentos da plataforma: configurar o ambiente, gerenciar estruturas de arquivos de projet |
| **0:27** | O currículo cobre conexão de ferramentas remotas usando o Model Context Protocol |
| **0:39** | O currículo cobre integração de controle de versão com GitHub e deploy das aplicações construídas |
| **1:30** | O curso explora as estruturas de arquivo geradas pelo Claude Code |
| **1:36** | O curso aborda o arquivo CLAUDE.md, contexto, slash commands e uso de git para controle de versão dos projetos |
| **1:43** | O curso trata de conectar Claude Code a MCPs e ferramentas CLI ligadas a aplicações de uso diário como Jira e  |
| **11:48** | Os modos de permissão apresentados são quatro: Plan, Accept Edits, Auto e Bypass. |
| **44:34** | Depois de tratar skills, goals e permission mode, o próximo elemento a ser examinado na configuração é o conte |
| **75:20** | Uma das perguntas frequentes tratadas é qual interface usar: CLI, aplicativo desktop ou VS Code. |
| **75:27** | O autor indica que existe um capítulo dedicado no vídeo que discute a escolha entre CLI e aplicativo desktop. |
| **77:40** | Skills podem ser usadas como mecanismo para economizar tokens ao usar Claude Code (tema de conteúdo futuro do  |
| **77:52** | Perder contexto é tratada como uma dúvida recorrente do público, e a resposta oferecida é controlar o uso de c |
| **77:59** | O sintoma prático do problema de contexto é descrito como chegar sempre a 100% de uso, e isso é apresentado co |
| **79:08** | O instrutor declara ter uma preferência específica recomendada para iniciantes que querem começar pequeno |
| **81:10** | Existem tópicos avançados de Claude Code que ficam fora de um tutorial introdutório: agents, skills, framework |

