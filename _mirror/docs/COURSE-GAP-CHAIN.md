# COURSE-GAP-REPORT — A CADEIA DA INFERÊNCIA

> **Retroativo e parcial.** As regras de decisão ainda não existem — a compilação evidência→Skill não rodou. Esta é a cadeia no nível da **evidência**, que é o que as regras vão herdar.

## Por que a cadeia, e não só a marca

Dizer *"17,4% do curso foi inferido pelo modelo"* lê como acusação. Pode ser generalização razoável, pode ser invenção — e quem lê não tem como julgar sem ver **o que o curso disse** e **o que o modelo concluiu além disso**.

## O número encolheu três vezes ao ser olhado de perto

| passo | PILOT-002 | % do corpus |
|---|---|---|
| rótulo `MODEL_INFERENCE` bruto | 88 | 19,6% |
| menos correções de transcrição | 50 | 11.2% |
| menos paráfrases sem distância | **32** | **7.1%** |

**7.1% do corpus do PILOT-002 é inferência do modelo com distância real da fonte.** No PILOT-001, 5 de 149 = 3.4%.

---

## PILOT-002 — *Claude Code em 60 minutos*

**32 inferências com distância real.** Cada uma: o que o curso disse, o que o modelo concluiu, e a distância.

### `EV-0018` · **2:38** · SEG-002 · PROCEDURE

> **o curso disse:** So if you want to get started with claw code here you

**2:44**

can see simply just going to Google search the clock documentation

**o modelo concluiu:** Para obter as instruções de instalação, basta fazer uma busca no Google pela documentação oficial da ferramenta

**distância:** o curso não diz que a busca serve para obter instruções de instalação nem chama a documentação de 'oficial'; o modelo inferiu de 'Google search the documentation'

### `EV-0065` · **10:24** · SEG-007 · PROCEDURE

> **o curso disse:** if you want to terminate your current clock session, simply just going to click on

**o modelo concluiu:** Para encerrar a sessão atual do Claude Code, basta clicar no ícone de lixeira na interface, o que termina a sessão.

**distância:** o curso não menciona ícone de lixeira; o modelo inferiu da frase truncada 'simply just going to click on' sobre encerrar a sessão

### `EV-0079` · **11:48** · SEG-008 · CONCEPT

> **o curso disse:** ## Understanding Permission Modes (Plan, Accept Edits, Auto, Bypass)

**o modelo concluiu:** Os modos de permissão apresentados são quatro: Plan, Accept Edits, Auto e Bypass.

**distância:** o curso não afirma que existem apenas quatro modos; o modelo inferiu do título da seção que cita Plan, Accept Edits, Auto e Bypass

### `EV-0091` · **16:18** · SEG-009 · CONSTRAINT

> **o curso disse:** based on the initial requirements that you specified. And then what's going to happen is it's going to basically

**o modelo concluiu:** O usuário precisa especificar requisitos explícitos no prompt inicial, pois são eles que servem de critério para o avaliador do loop

**distância:** o curso não diz que os requisitos são critério de um avaliador de loop nem que especificá-los é obrigatório; o modelo inferiu de 'based on the initial requirements that you specified'

### `EV-0125` · **21:13** · SEG-011 · RATIONALE

> **o curso disse:** Here you can see the plemo here is going to extract that and put into a

**21:18**

plan which is much more visual for us to see.

**o modelo concluiu:** O modo de planejamento extrai os design tokens e os coloca no plano em formato mais visual, facilitando a leitura humana.

**distância:** o curso não diz que o extraído são design tokens; o modelo inferiu do genérico 'extract that and put into a plan'

### `EV-0147` · **25:06** · SEG-013 · CONSTRAINT

> **o curso disse:** any software developer teams is they

**25:13**

have a project tracking board where they log all the bugs that they have maybe like a camman board or like a system

**25:19**

where they keep track of all the issues.

**o modelo concluiu:** O workflow assume que a equipe de desenvolvimento mantém um quadro de acompanhamento de projeto (ex.: kanban) onde todos os bugs e issues são registrados

**distância:** o curso não diz que o workflow pressupõe esse quadro; o modelo inferiu da observação geral de que equipes de desenvolvimento têm board de bugs

### `EV-0162` · **27:26** · SEG-013 · CONCEPT

> **o curso disse:** There's three different four different stages. Understand, fix, ship, hand off

**27:34**

to the right person.

**o modelo concluiu:** O workflow fix ticket é organizado em quatro estágios: entender, corrigir, enviar e repassar à pessoa certa

**distância:** o curso não afirma serem quatro estágios de forma definitiva; o modelo inferiu de 'três diferentes quatro diferentes estágios', hesitação na fala

### `EV-0170` · **29:08** · SEG-014 · TOOL_USAGE

> **o curso disse:** Here you can see we have our plugins. So if I

**29:15**

were to enter this, you can see that currently we're in a discovery. We're can installing any plugins we want. You

**29:20**

can see that we have our front end of design plugins, which is exactly the same as this one right here.

**o modelo concluiu:** O comando /plugins abre uma tela de discovery no Claude Code onde é possível instalar plugins disponíveis, incluindo o front-end design

**distância:** o curso não menciona o comando /plugins; o modelo inferiu da menção a 'nossos plugins' e à tela de discovery para instalação

### `EV-0179` · **30:41** · SEG-014 · PROCEDURE

> **o curso disse:** once we have the front end design skill installed, you can see we can just simply just type in /reload plugins to

**30:53**

actually apply the changes.

**o modelo concluiu:** Depois de instalar a skill, é necessário executar /reload-plugins para aplicar as mudanças

**distância:** o curso não diz ser necessário nem grafa '/reload-plugins'; o modelo inferiu de 'simply just type in /reload plugins' para aplicar mudanças

### `EV-0182` · **31:27** · SEG-015 · PROCEDURE

> **o curso disse:** Now the other option you can do this is you can just specify the skill itself like using a slash

**31:32**

command using slashfront of design

**o modelo concluiu:** A segunda forma de acionar uma skill é especificá-la explicitamente via slash command (ex.: /frontend-design)

**distância:** o curso não grafa '/frontend-design' nem numera como segunda forma; o modelo inferiu de 'other option' e 'slashfront of design'

### `EV-0194` · **33:36** · SEG-016 · TOOL_USAGE

> **o curso disse:** to happen here is that claw code is going to install ining this skill onto your local machine.

**o modelo concluiu:** Ao receber o link, o agente instala a skill na máquina local do usuário.

**distância:** o curso não menciona recebimento de link; o modelo inferiu do trecho que diz apenas que o Claude Code instala a skill localmente

### `EV-0196` · **33:42** · SEG-016 · TOOL_USAGE

> **o curso disse:** /verell for something and it's going to start to use it right away.

**o modelo concluiu:** A skill instalada é invocada por um comando de barra (ex.: /vercel ...) e passa a ser usada de imediato.

**distância:** o curso não escreve '/vercel'; o modelo inferiu de '/verell for something' usado imediatamente

### `EV-0199` · **34:00** · SEG-016 · PROCEDURE

> **o curso disse:** type in first cell uh react best practice you can see that we have the skill here is showing which basically

**o modelo concluiu:** Depois do reload, ao digitar o nome da skill (Vercel React best practice) ela aparece listada, confirmando que está ativa.

**distância:** o curso não menciona reload nem confirmação de skill ativa; o modelo inferiu de digitar o nome e a skill aparecer listada

### `EV-0200` · **34:07** · SEG-016 · CONCEPT

> **o curso disse:** help you to building application here with the best performance optimizations whenever you're using react or NexJS as

**o modelo concluiu:** A função dessa skill é ajudar a construir a aplicação com as melhores otimizações de performance quando se usa React ou Next.js como framework de front-end.

**distância:** o curso não chama React/Next.js de framework de front-end; o modelo inferiu da menção a otimizações de performance ao usar React ou Next.js

### `EV-0210` · **35:46** · SEG-017 · CONCEPT

> **o curso disse:** the the package.json package log here really don't need to worry about too much. These are only

**o modelo concluiu:** O package-lock.json não precisa de atenção do desenvolvedor: é gerado automaticamente a cada instalação das dependências declaradas.

**distância:** o curso não explica geração automática a cada instalação de dependências; o modelo inferiu de 'não precisa se preocupar muito' com package.json/package-lock

### `EV-0215` · **36:48** · SEG-017 · EXAMPLE

> **o curso disse:** is one of the dependency we're going to ignore every time we're going to commit it or in this case add it to our

**o modelo concluiu:** node_modules é um exemplo de dependência listada no .gitignore, ignorada a cada commit/adição ao controle de versão.

**distância:** o curso não nomeia node_modules nem o arquivo .gitignore aqui; o modelo inferiu de "uma das dependências que vamos ignorar sempre que fizermos commit"

### `EV-0234` · **39:13** · SEG-018 · EXAMPLE

> **o curso disse:** slashtier list and that's going to be slashtier list right here which is this page right here okay and this is the

**o modelo concluiu:** A homepage renderiza a rota /tier-list, que corresponde à página exibida no navegador.

**distância:** o curso não diz que a homepage renderiza essa rota; o modelo inferiu de "/tier-list, que é esta página aqui"

### `EV-0256` · **42:55** · SEG-020 · PRINCIPLE

> **o curso disse:** And let's say if you want to

**43:01**

make it universal for all the AI agent frameworks, then you're going to add that inside of the AI, sorry, the agents

**43:06**

file right here.

**o modelo concluiu:** Para tornar um system prompt universal para todos os frameworks de agentes de IA, coloque-o no arquivo agents.md

**distância:** o curso não diz extensão .md nem "system prompt"; o modelo inferiu de "adicionar dentro do arquivo agents" para ser universal a todos os frameworks

### `EV-0266` · **50:06** · SEG-022 · CONCEPT

> **o curso disse:** those are shortcuts that clock has built in, right? There's also the MCP.

**o modelo concluiu:** Os comandos acessíveis via barra são atalhos que o Claude Code já traz embutidos

**distância:** o curso não diz que são acessados por barra; o modelo inferiu de "são atalhos que o Claude já traz embutidos"

### `EV-0312` · **58:02** · SEG-025 · EXAMPLE

> **o curso disse:** So what we have

**58:08**

committed here you can see uh 133 files here in one initial commits. So the entire NexJS applications the images the

**58:16**

playrs for the evaluations and also the documentations.

**o modelo concluiu:** O commit inicial do projeto incluiu 133 arquivos: a aplicação Next.js, imagens, arquivos de avaliação (evals) e a documentação

**distância:** o curso não diz "arquivos de avaliação (evals)"; o modelo interpretou assim o trecho "playrs for the evaluations" no commit de 133 arquivos

### `EV-0313` · **58:21** · SEG-025 · PRINCIPLE

> **o curso disse:** things that we I have

**58:21**

exclude here you can see is the existing ignore no modules the NexJS so like I

**58:27**

said before right those are the things that are not really relevant for our projects so those dot folders and also

**58:33**

no module here are not going to be relevant

**o modelo concluiu:** node_modules e as pastas dot do Next.js foram excluídas do commit via gitignore porque não são relevantes para o projeto

**distância:** o curso não atribui a exclusão ao gitignore nem chama as dot folders de Next.js; o modelo inferiu de "o ignore existente, no modules, o NextJS... não relevantes"

### `EV-0315` · **58:39** · SEG-025 · TOOL_USAGE

> **o curso disse:** and you can see that if we were to look at the color for those fog

**58:44**

explore you can see these are all grayed out right and the ones that are committed are not grayed out. Okay, so

**58:51**

the grade out ones are be part of the get commits. So they will not be committed if there's any changes that

**58:57**

are inside of that folder.

**o modelo concluiu:** No file explorer do editor, arquivos e pastas acinzentados são os ignorados pelo git e não serão commitados, enquanto os não acinzentados fazem parte do commit

**distância:** o curso não diz que acinzentado significa "ignorado pelo git"; o modelo inferiu de "os acinzentados não serão commitados"

### `EV-0316` · **58:57** · SEG-025 · QUALITY_CRITERION

> **o curso disse:** And you can see there's no MV file here or CQ

**59:02**

queries exist anywhere in the folder. So nothing sensitive went up.

**o modelo concluiu:** Após o commit, verifica-se que nenhum arquivo .env nem queries SQL foram enviados, confirmando que nada sensível subiu para o controle de versão

**distância:** o curso não fala de envio ao controle de versão nem de momento pós-commit; o modelo inferiu de "não há .env nem queries SQL na pasta; nada sensível subiu"

### `EV-0375` · **69:42** · SEG-030 · PROCEDURE

> **o curso disse:** Once you connected log into your versell then

**o modelo concluiu:** Depois de conectar o MCP, faça login na sua conta da Vercel antes de seguir.

**distância:** o curso não diz que a conexão é de MCP; o modelo inferiu de "once you connected, log into your Vercel"

### `EV-0391` · **72:16** · SEG-031 · CONCEPT

> **o curso disse:** MTPs is kind of like tools, right? You want to connect it to your tools like Slack or Jira or sales, whatever

**72:22**

tools you want to have clock access to to be able to use it. Then that's what MTP is for.

**o modelo concluiu:** MCPs são as ferramentas: servem para conectar Claude Code a sistemas externos como Slack, Jira ou Salesforce, dando-lhe acesso para usá-los

**distância:** o curso não menciona Claude Code nem Salesforce; o modelo inferiu de "tools like Slack or Jira or sales" e do contexto

### `EV-0399` · **73:42** · SEG-032 · PRINCIPLE

> **o curso disse:** So if you really want to experience all

**o modelo concluiu:** Para experimentar todas as funcionalidades do Claude Code, deve-se preferir o uso no terminal em vez da versão desktop

**distância:** o curso não compara terminal e desktop na citação; o modelo inferiu da frase truncada "if you really want to experience all"

### `EV-0422` · **77:04** · SEG-036 · EXAMPLE

> **o curso disse:** and maybe using uh opus here

**77:04**

for maybe like uh go or gro whatever model that you find online

**o modelo concluiu:** O Opus também pode ser substituído por outro modelo de terceiros (ex.: GLM ou Grok) encontrado online.

**distância:** o curso não nomeia GLM/Grok nem "terceiros"; o modelo inferiu dos termos truncados "go or gro... model that you find online"

### `EV-0432` · **78:24** · SEG-038 · PRINCIPLE

> **o curso disse:** Setting the right permission mode here is going to help you to make sure that when clock is going to run, it's going

**o modelo concluiu:** Definir o modo de permissão correto é o mecanismo que garante a segurança da execução do Claude na máquina do usuário

**distância:** o curso não afirma ser o mecanismo que garante segurança na máquina; o modelo inferiu de "help you to make sure when Claude runs"

### `EV-0442` · **79:40** · SEG-040 · EXAMPLE

> **o curso disse:** released you know before they only use have the sonic model but now they have

**79:46**

opus model they have obus 4.8 eight maybe fable 5 there's so many model has released and there's so many changes in

**o modelo concluiu:** Como exemplo de mudança rápida, cita a evolução dos modelos: antes só havia o Sonnet, depois vieram os modelos Opus (incluindo versões como 4.5) e muitos outros lançamentos

**distância:** o curso não cita Opus 4.5 nem rotula como mudança rápida; o modelo inferiu de "obus 4.8 eight maybe fable 5"

### `EV-0443` · **79:46** · SEG-040 · PRINCIPLE

> **o curso disse:** there's so many changes in

**o modelo concluiu:** Apesar das muitas mudanças no Claude Code, o material fundamental permanece o mesmo

**distância:** o curso não diz que o fundamental permanece igual no Claude Code; o modelo inferiu de "there's so many changes in"

### `EV-0445` · **80:04** · SEG-040 · PRINCIPLE

> **o curso disse:** fundamentals right you still need to know this before you actually know or try to learn about like altra code or

**80:10**

try to learn dynamic workflow building loops right you still need to know the foundation before you actually know

**o modelo concluiu:** É necessário dominar os fundamentos antes de tentar aprender recursos avançados como o Agent SDK, construção de workflows dinâmicos e loops

**distância:** o curso não menciona "Agent SDK"; o modelo inferiu de "altra code" na transcrição, mantendo apenas workflows dinâmicos e loops como avançados

### `EV-0447` · **81:25** · SEG-041 · PRINCIPLE

> **o curso disse:** There's so many things that we haven't gone over yet. So that's why in my next coming video, I'm going to

**o modelo concluiu:** O domínio da ferramenta é tratado como uma progressão em níveis: o conteúdo introdutório é seguido por material intermediário destinado a subir de nível

**distância:** o curso não estrutura níveis introdutório/intermediário nem promete "subir de nível"; o modelo inferiu de "há muita coisa não abordada" e menção a próximo vídeo

### 18 classificadas como inferência que são paráfrase

Marcadas `MODEL_INFERENCE` pelo extrator, mas sem distância da fonte — tradução ou reordenação. **Não são lacuna do curso.**

| evidência | onde | por quê |
|---|---|---|
| `EV-0008` | 1:06 | a afirmação é paráfrase da citação (apenas normaliza 'Clawo' para Claude Code) |
| `EV-0012` | 1:43 | a afirmação é paráfrase da citação |
| `EV-0013` | 1:56 | a afirmação é paráfrase da citação |
| `EV-0022` | 3:05 | a afirmação é paráfrase da citação |
| `EV-0061` | 9:41 | a afirmação é paráfrase da citação |
| `EV-0073` | 11:05 | a afirmação é paráfrase da citação |
| `EV-0158` | 26:56 | a afirmação é paráfrase da citação |
| `EV-0212` | 36:18 | a afirmação é paráfrase da citação |
| `EV-0213` | 36:24 | a afirmação é paráfrase da citação |
| `EV-0318` | 59:02 | a afirmação é paráfrase da citação |

---

## PILOT-001 — *How to Build Your First AI Agent*

**5 inferências com distância real.** Cada uma: o que o curso disse, o que o modelo concluiu, e a distância.

### `EV-0014` · **1:09** · SEG-002 · EXAMPLE

> **o curso disse:** sits in one dock

**o modelo concluiu:** Exemplo de fragmentação: a estratégia fica em um documento separado

**distância:** o curso não ensina que se trata da estratégia nem que isso exemplifica fragmentação; o modelo inferiu de "sits in one dock", que só menciona algo num único documento

### `EV-0023` · **1:44** · SEG-002 · CONCEPT

> **o curso disse:** Our good friend Kevin Hudson from

**o modelo concluiu:** O reframe é atribuído a Kevin Hudson, da Futurepedia

**distância:** o curso não ensina que Kevin Hudson é da Futurepedia nem que ele propôs o reframe; o modelo inferiu de "Our good friend Kevin Hudson from", frase incompleta

### `EV-0070` · **6:28** · SEG-005 · EXAMPLE

> **o curso disse:** A blog becomes a length post, an X thread, a short  script, and an email newsletter.

**o modelo concluiu:** Exemplo de cascata: um blog se torna um post de LinkedIn, uma thread no X, um roteiro curto e uma newsletter por email

**distância:** o curso não ensina que o post é do LinkedIn; o modelo inferiu de "a length post", sem plataforma nomeada

### `EV-0087` · **8:00** · SEG-006 · TOOL_USAGE

> **o curso disse:** There's a free tier, so you can try before  you commit.

**o modelo concluiu:** O Gumloop tem uma camada gratuita, permitindo testar antes de se comprometer

**distância:** o curso não ensina que a camada gratuita é do Gumloop; o modelo inferiu de "There's a free tier", sem produto nomeado na citação

### `EV-0113` · **11:01** · SEG-007 · TOOL_USAGE

> **o curso disse:** And Claude, you  add knowledge documents directly to the project.

**o modelo concluiu:** No Claude, a memória é fornecida adicionando documentos de conhecimento diretamente ao projeto

**distância:** o curso não ensina que isso constitui "memória"; o modelo inferiu de adicionar documentos de conhecimento ao projeto no Claude

### 2 classificadas como inferência que são paráfrase

Marcadas `MODEL_INFERENCE` pelo extrator, mas sem distância da fonte — tradução ou reordenação. **Não são lacuna do curso.**

| evidência | onde | por quê |
|---|---|---|
| `EV-0021` | 1:35 | a afirmação é paráfrase da citação |
| `EV-0086` | 7:56 | a afirmação é paráfrase da citação |

---

## Como ler isto quando as regras existirem

Cada regra de decisão vai citar `evidence_id`. Uma regra cujas evidências sejam **todas** desta lista é **lacuna do curso**: funciona, mas o curso não a ensinou — o modelo preencheu. É a diferença entre avaliar o curso e avaliar o modelo.

*Gerado por script. As linhas de distância vieram de 6 chamadas em lotes de 12, com contabilidade dura: 57/57 evidências voltaram com linha.*
