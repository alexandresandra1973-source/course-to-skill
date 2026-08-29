# Lista enumerada de decisão — PILOT-002 (L0 CORTADO)

- Gerado: `2026-08-11T04:33:57+00:00` · gerador `decision_structure_pilot002.py`
- Fonte: `Course-to-Skill-Claude/pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt` · sha256 `85ea229011a989ea…`
- **É o corpus CORTADO**, o que a Skill vai receber — não o L0 íntegro.
- Mesmas categorias e mesmos critérios da calibração do PILOT-001.

## Método, e o que nele é chamada de julgamento

1. Extração mecânica: 194 candidatos (mesmas regex do medidor).
2. Duas classes separadas por **regra declarada**, derivadas da leitura desta fonte: narração de demonstração de tela (57) e CTA (9).
3. Resíduo de **128** itens, lido à mão. Dele saem as estruturas.

> **Categoria nova, declarada.** O PILOT-001 não precisou de `DEMONSTRACAO_DE_TELA`. O PILOT-002 é um tutorial de ferramenta gravado com a tela: *"if I were to open this"*, *"if I want to delete"* são narração do que o dedo está fazendo, não regra. Acrescentar a categoria é chamada de julgamento minha, e é o que separa este corpus do outro.

> **O que NÃO foi feito.** Não classifiquei os 128 itens do resíduo um a um numa tabela como fiz com os 49 do PILOT-001. Li todos e ancorei à mão os que pertencem a estrutura, que são os que decidem. Os demais são passo linear, definição ou narração; estão publicados abaixo sem categoria individual. Dizer o contrário seria inventar trabalho manual.

## 1. Estruturas de decisão no corpus de treino

**4 tabelas multi-ramo · 3 portões simples.**

### T1 — CLI × MCP · tabela multi-ramo

| # | marca | trecho que disparou |
|---|---|---|
| 104 | `—` | Which one should you really use? |
| 105 | `—` | So let's say if you want to save tokens that using CLI here is the best option but if you're using MCP that ba |

- economizar token / velocidade → CLI
- segurança, controlar quantas ferramentas o agente acessa, ambiente de time → MCP

### T2 — onde rodar: terminal × IDE · tabela multi-ramo

| # | marca | trecho que disparou |
|---|---|---|
| 6 | `—` | So the first option we have is use our claw code instead of a desktop app. |
| 7 | `—` | But if you are technical and you want to get more control, explore all the functionality the clock really offe |
| 8 | `—` | So that's why my recommendation is using a IDE which stands for integrated development environment which means |
| 108 | `—` | So if you really want to experience all the functionality that clock really offers then clock terminal here is |
| 127 | `—` | But my preference here for beginners, if you want to start small, starting simple, start a minimal, then VS Co |

- técnico, quer controle e toda a funcionalidade → terminal
- iniciante, quer começar pequeno → VS Code
- recomendação geral do autor → IDE

> **Chamada de julgamento.** O autor dá recomendação e preferência em pontos diferentes do curso, sem uma tabela única. Tratei como uma estrutura só porque as condições são mutuamente exclusivas e cobrem o mesmo eixo; quem preferir pode contar como duas.

### T3 — onde colocar o system prompt: CLAUDE.md × AGENTS.md · tabela multi-ramo

| # | marca | trecho que disparou |
|---|---|---|
| 68 | `—` | Let's say if you want to add a system prompt here specifically for claw code then you're going to add it insid |
| 69 | `—` | And let's say if you want to make it universal for all the AI agent frameworks, then you're going to add that  |
| 72 | `43:24` | If you're using cloud code, then it's going to sync that in your AI agents. |

- só para o claw code → CLAUDE.md
- universal para todos os frameworks de agente → AGENTS.md

### T4 — plano e orçamento · tabela multi-ramo

| # | marca | trecho que disparou |
|---|---|---|
| 118 | `—` | Now my honest take for this is that if you're a beginner who are just learning started learning claw code, the |
| 119 | `—` | But if you're trying to use this every single day, I'm gonna be upfront with you here that it's not going to b |
| 120 | `—` | If you want to stay under this budget and you don't want to upgrade anymore, what you can do here is you can c |
| 121 | `76:39` | One is local model if your computer is really strong. |

- iniciante aprendendo → o plano atual basta
- uso diário → não basta, precisa subir de plano
- quer ficar no orçamento → modelo local, se a máquina aguentar

> **Chamada de julgamento.** Três ramos com condição, mas ditos em tom de opinião ("my honest take"), não como regra do método. Contei como tabela; quem exigir regra normativa contaria como conselho.

### G1 — precisa de controle de versão? · portão simples

| # | marca | trecho que disparou |
|---|---|---|
| 86 | `—` | Because let's say if you have mult multiple team members working on in the same projects or let's say if you r |
| 87 | `—` | And if you actually want to set up version controls, the simplest and the most cheapest way that you can do th |

- time compartilhando projeto, ou risco de perder trabalho → Git/GitHub

### G2 — repositório privado × público · portão simples

| # | marca | trecho que disparou |
|---|---|---|
| 93 | `57:28` | You can actually change that to public if you want to. |

- quer expor → público; padrão → privado

> **Chamada de julgamento.** Um ramo só, dito de passagem durante a demonstração. Está no limite entre portão e comentário.

### G3 — trocar de modelo · portão simples

| # | marca | trecho que disparou |
|---|---|---|
| 76 | `—` | You can if you want to switch to most powerful model like the Fable 5 model, you can also do that. |
| 78 | `—` | But if you want to change the model, simply just going to type in /model here. |

- quer o modelo mais forte → `/model`

## 2. Decisão levantada e não entregue

### D1 — CLI desktop app × VS Code

- `—` — And then the fourth one we have is is should we use CLI desktop app or VS code?
- `—` — So there's actually a chapter in my video here talk about you know should we use CLI or should we use desktop app right 

> A pergunta é feita na FAQ e o autor remete a outro capítulo do vídeo em vez de responder. Não entra como estrutura: o corpus levanta a decisão sem entregá-la.

## 3. O corte levou as duas seções mais densas

| faixa | itens | segundos | itens/min |
|---|---|---|---|
| held-out (as duas seções) | 43 | 513 | **5.03** |
| corpus de treino | 234 | 4384 | **3.2** |

As faixas retiradas têm **1.57×** a densidade de candidatos do que sobrou. Não é acidente: *Understanding Permission Modes* é uma tabela de quatro modos e *Managing Your Context Window* é a seção de gestão de recurso. O held-out foi escolhido por span declarado, antes de qualquer extração — e calhou de levar justamente o material mais decisório.

**Consequência que precisa ficar registrada:** o corpus de treino do PILOT-002 é mais fino que a fonte. Comparar PILOT-002 com PILOT-001 pelo corpus de treino compara o que a Skill recebe, que é o certo para decidir se a Skill consegue aprender — mas subestima a fonte.

## 4. Lado a lado, em estruturas

| | PILOT-001 | PILOT-002 (cortado) |
|---|---|---|
| duração | 15.08 min | 73.07 min |
| candidatos mecânicos | 49 | 194 |
| **tabelas multi-ramo** | **1** | **4** |
| **portões simples** | **3** | **3** |
| estruturas ao todo | 5 | 7 |
| decisões levantadas e não entregues | 0 | 1 |

A comparação é em estrutura, não em contagem de regex — o medidor está suprimido desde a calibração, e o número de candidatos aparece acima só como referência de volume.

**Leitura honesta do quadro.** O PILOT-002 tem mais estruturas que o PILOT-001 (7 contra 5) e mais tabelas multi-ramo (4 contra 1), em 4.8× a duração. Por estrutura por minuto os dois são parecidos; o PILOT-002 ganha em volume absoluto, não em densidade. E parte do que ele tinha de mais denso foi para o held-out.

Nenhum veredito de qualificação é emitido aqui. Esta lista é a entrada para essa decisão, que é do Alexandre.

## 5. Resíduo lido, sem categoria individual

Os 128 itens do resíduo, com marca de tempo. Os que pertencem a estrutura estão marcados.

| # | marca | item | estrutura |
|---|---|---|---|
| 1 | `—` | And the prerequisite for this video is you don't need to be a developer or technical person here to follow alo |  |
| 2 | `2:26` | With that being said, if you're interested, let's get into the video. |  |
| 3 | `—` | So if you want to get started with claw code here you can see simply just going to Google search the clock doc |  |
| 4 | `—` | So simply just going to do the command spacebar if you're using Mac and you can see that we have our terminal  |  |
| 5 | `—` | So simply just going to choose the first one terminal and once we have that open we're just going to paste wha |  |
| 6 | `—` | So the first option we have is use our claw code instead of a desktop app. | T2 |
| 7 | `—` | But if you are technical and you want to get more control, explore all the functionality the clock really offe | T2 |
| 8 | `—` | So that's why my recommendation is using a IDE which stands for integrated development environment which means | T2 |
| 9 | `—` | But if you're using Windows, then it's going to says download for Windows. |  |
| 10 | `—` | So, for example, if you do like command minus, it will just minimize the code, right? |  |
| 11 | `—` | And if you want to do command plus, it will just zoom in a bit more for your current Visual Studio code. |  |
| 12 | `—` | And the reason why we want to open a folder here is because we want to creating our own projects and we want t |  |
| 13 | `—` | And if I were delete this and open it again, you can see that high is still there. |  |
| 14 | `7:13` | Simply you can choose whichever themes you want. |  |
| 15 | `7:33` | So it doesn't have to stick to the black background if you don't want to. |  |
| 16 | `7:45` | So if we were click on this toggle panel icon you can see we have our open our terminal here. |  |
| 17 | `—` | If you want to get the keyboard shortcut that's going to be control back quote and or back tick or if you were |  |
| 18 | `—` | So if you want to uh minimize this, if you want to actually minimize it, you can scroll or in this case minimi |  |
| 19 | `—` | So if you want to see the claw code or in this case start your clock code session simply just going to type in |  |
| 20 | `—` | So what we can do now is if you want to delete the file like I said just going to do uh click on this right or |  |
| 21 | `—` | And really quickly, if you want to terminate your current clock session, simply just going to click on this tr |  |
| 22 | `10:37` | If you're using Mac, just do control C two times and it's going to terminate it. |  |
| 23 | `—` | And if you want to resume the previous session that we just have, just type in slashres, right? |  |
| 24 | `—` | So make sure to add a slash and type in resume. |  |
| 25 | `11:36` | Or let's say if you want to resume that session, simply just going to do the same thing. |  |
| 26 | `—` | So if we do the slash command and just type in goal and what this slash command does in claw code is allows AI |  |
| 27 | `—` | And then what's going to happen is it's going to basically evaluate it and let's say if it doesn't match with  |  |
| 28 | `—` | So now to use this instead of a claw code, the first thing first we're going to do here is to gather all the r |  |
| 29 | `—` | Here is the static HTML page using some technical terms that you probably never heard of it. |  |
| 30 | `—` | So it doesn't really matter which option you choose. |  |
| 31 | `18:52` | I'm just going to choose the first one here. |  |
| 32 | `—` | You can also scroll down here to see exactly what the file structure look like if you choose the second option |  |
| 33 | `—` | So I'm just going to choose the most popular which is the first option for now. |  |
| 34 | `19:16` | And once we're going to choose that option, the next question is the email gate. |  |
| 35 | `—` | So should we keep just the pure client tool or should we also including the email gate. |  |
| 36 | `—` | So in this case we're just going to choose the first option here just to skip uh skip the gates just keep it m |  |
| 37 | `19:36` | The third one here is what content should the top tier uh list use. |  |
| 38 | `—` | So in this case, should we be able to make it just functional or should we make it like pixel perfect, right? |  |
| 39 | `—` | the it might it must match with exactly like what we have in the screenshots and it must be having the same fo |  |
| 40 | `—` | So don't need to worry about that if you're not really technical. |  |
| 41 | `—` | So let's say if you're not really satisfied with the plan here, you want to actually, you know, make some modi |  |
| 42 | `—` | Everything are all the same except this time we are going to pull in the latest images first. |  |
| 43 | `—` | So, if you were to send this link to someone else or a friend, they won't be able to access that. |  |
| 44 | `—` | So now you know exactly how we can use the permission mode instead of claw code and also using the /go. |  |
| 45 | `—` | It doesn't matter if it's claw code or any other large range model. |  |
| 46 | `—` | Then we're going to have our QA which is our playright browser automation here to actually open the browser op |  |
| 47 | `—` | If we can then it's going to spin up multiple agent here to do research on this entire ticket. |  |
| 48 | `26:03` | Now don't worry about multiple agent here in a second. |  |
| 49 | `—` | And then the next step here you can see we have our QA which is using the same playright browser automation he |  |
| 50 | `—` | So what we're going to do here, if you want to select this, we're just going to click on spacebar. |  |
| 51 | `—` | And if you want to view all the skills that are available like how we can be able to find skills online, simpl |  |
| 52 | `—` | So if you're using codeex or if you're using openclaw or any other AI agent here, you can use this skills.sh h |  |
| 53 | `—` | U so if you scroll down here, you can see the second option, the most second popular option here is the front  |  |
| 54 | `—` | So I'm going to choose the second option here which will basically install it for all the collaborators uh col |  |
| 55 | `—` | And like I said, if you want to install more skills, simply head over to your skills.sh and you can see there' |  |
| 56 | `—` | So the next time when you run it, you simply just type in /verell for something and it's going to start to use |  |
| 57 | `—` | And if I were scroll down here, you can see this is project is already installed. |  |
| 58 | `—` | That's going to be the dependence uh the the package.json package log here really don't need to worry about to |  |
| 59 | `—` | These are only things that is going to be generated uh every time when we're actually going to install everyth |  |
| 60 | `—` | And furthermore, if you want to scroll up here, you can see that we have a couple folders here. |  |
| 61 | `—` | So what no modules does is every time when you're installing those dependencies from our package.json, those d |  |
| 62 | `—` | That's why you can see instead of the git ignore file, get ignore is basically like things that the version co |  |
| 63 | `—` | You can see just just think of it like a bunch of um libraries that we're not going to use in our application, |  |
| 64 | `37:05` | So you don't really need to touch that. |  |
| 65 | `—` | So library you can think of it like anything that uh we're trying to write like for example like a comment um  |  |
| 66 | `—` | And then furthermore, if you want to close all those tabs, simply just going to click on rightclick and click  |  |
| 67 | `39:48` | You can see there's also some folder here that start with a dot in front of it. |  |
| 68 | `—` | Let's say if you want to add a system prompt here specifically for claw code then you're going to add it insid | T3 |
| 69 | `—` | And let's say if you want to make it universal for all the AI agent frameworks, then you're going to add that  | T3 |
| 70 | `—` | Every time when you send a prompts, it's going to look at the system prompts for AI agents. |  |
| 71 | `—` | So whatever your rules that you put here instead of the agents MD or the claw MD, right? |  |
| 72 | `43:24` | If you're using cloud code, then it's going to sync that in your AI agents. | T3 |
| 73 | `—` | So things like that and also there's some file configuration file that you don't really need to care at the mo |  |
| 74 | `44:17` | There's also different folders we have gone over and also the folder that start with dot. |  |
| 75 | `—` | So pretty much those are the file structures that we have and now you know exactly what the structure look lik |  |
| 76 | `—` | You can if you want to switch to most powerful model like the Fable 5 model, you can also do that. | G3 |
| 77 | `50:17` | So if you do like model here. |  |
| 78 | `—` | But if you want to change the model, simply just going to type in /model here. | G3 |
| 79 | `—` | Uh furthermore, if you want to actually go down, there's also skills and custom commands. |  |
| 80 | `—` | Okay, so you can pretty much see that we can be able to use the slash command here to basically use the built- |  |
| 81 | `—` | And if you were to type in this, you can also explore all kinds of plugins that we have inside of our discover |  |
| 82 | `—` | And if you want to actually learn more about it, you can just click on enter and just try learning more about  |  |
| 83 | `—` | And the other way you can do this is if you want to uninstall a skill that you have already installed, you can |  |
| 84 | `—` | If I don't want a skill, I can just right click on that folder and just going to click on delete and it's goin |  |
| 85 | `—` | Okay, that's how you can delete a skill or deleting a plugins here instead of your clock code session. |  |
| 86 | `—` | Because let's say if you have mult multiple team members working on in the same projects or let's say if you r | G1 |
| 87 | `—` | And if you actually want to set up version controls, the simplest and the most cheapest way that you can do th | G1 |
| 88 | `54:36` | For example if we were go down this is the oldest version that we have. |  |
| 89 | `—` | So let's say if you have like the one change that actually consistent in single branch. |  |
| 90 | `—` | If you want to you know create a different change like maybe like a beta version or like a version two of that |  |
| 91 | `—` | So, currently I don't have any um folder or in this case a repository inside of GitHub for this project yet. |  |
| 92 | `57:17` | So, let's try to take a look to see if it's actually able to do that. |  |
| 93 | `57:28` | You can actually change that to public if you want to. | G2 |
| 94 | `—` | So, that's exactly what it means when creating a private repository. |  |
| 95 | `—` | things that we I have exclude here you can see is the existing ignore no modules the NexJS so like I said befo |  |
| 96 | `—` | So they will not be committed if there's any changes that are inside of that folder. |  |
| 97 | `—` | So nothing are being added into the version control because we don't want to commit any sensitive information  |  |
| 98 | `61:52` | And if you actually want to add in more users, simply just going to go to the repositories that you have. |  |
| 99 | `—` | For example, let's say you're currently using Jira to manage your project board or let's say you're currently  |  |
| 100 | `—` | But the point here is that it doesn't matter if it's MCP or CLI. |  |
| 101 | `—` | Or let's say if you're using goh high level a lot, you can see that go high level also has their MCP, right? |  |
| 102 | `—` | Or let's say if you're currently using Verscell right for deploying your application and you're scared to runn |  |
| 103 | `—` | So I'm just going to ask that inside of my current application but if you don't have one simply just going to  |  |
| 104 | `—` | Which one should you really use? | T1 |
| 105 | `—` | So let's say if you want to save tokens that using CLI here is the best option but if you're using MCP that ba | T1 |
| 106 | `—` | Now if you don't have that connected simply just copy that documentation link paste the claw code and let it c |  |
| 107 | `—` | Your workflows that you want to repeatably do it every single time when you're using clock code. |  |
| 108 | `—` | So if you really want to experience all the functionality that clock really offers then clock terminal here is | T2 |
| 109 | `—` | If you're using claude then you're using claw code. |  |
| 110 | `74:00` | If you're using codeex then you're using GBT. |  |
| 111 | `—` | If you're using Gemini then you're using Gemini CLI or anti-gravities right? |  |
| 112 | `74:20` | But if you're talking about the frameworks here like the these uh claw code is a framework. |  |
| 113 | `—` | So there's so many videos on there um you can actually follow but personally I think that if you're talk about |  |
| 114 | `—` | And then the fourth one we have is is should we use CLI desktop app or VS code? | D1 |
| 115 | `—` | So there's actually a chapter in my video here talk about you know should we use CLI or should we use desktop  | D1 |
| 116 | `75:58` | And somehow that we don't have a version to roll back. |  |
| 117 | `76:03` | So you don't really need to pay anything here to actually use it. |  |
| 118 | `—` | Now my honest take for this is that if you're a beginner who are just learning started learning claw code, the | T4 |
| 119 | `—` | But if you're trying to use this every single day, I'm gonna be upfront with you here that it's not going to b | T4 |
| 120 | `—` | If you want to stay under this budget and you don't want to upgrade anymore, what you can do here is you can c | T4 |
| 121 | `76:39` | One is local model if your computer is really strong. | T4 |
| 122 | `—` | That's how you can be able to actually have claw code to stay in your right budget when you're running. |  |
| 123 | `—` | And if you actually want to go even further, what you can do here is that I do have video talk about how you c |  |
| 124 | `—` | Let's say if you're always getting like, oh, 100% usage. |  |
| 125 | `—` | Setting the right permission mode here is going to help you to make sure that when clock is going to run, it's |  |
| 126 | `—` | know uh you can use cursor you can use anti-gravity you can use vs code those are all idees okay but you don't |  |
| 127 | `—` | But my preference here for beginners, if you want to start small, starting simple, start a minimal, then VS Co | T2 |
| 128 | `—` | I don't think it's going to be outdated in a month or in a year. |  |

## 6. Separados por regra declarada

### Narração de demonstração de tela (57)

- `—` — And once you download it here, you can see if I were to open it, here is what it looks like.
- `—` — And currently, you can see if I want to see all the files here, I can simply just going to click on 
- `—` — So if I want to create a folder or create a files here inside of this folder I can do to say okay we
- `—` — And if I want to delete it, simply just going to click on this file and just going to do a command d
- `—` — So that way if you want to create any files here like for example this is a um let's say this is jus
- `—` — So if I were to say hi for example and what's going to happen here is that it's going to do some thi
- `—` — So now if I were to give this prompt to claude and what now cla can do that's different compared to 
- `—` — So now if I want to clear a terminal, simply just going to do clear.
- `—` — And if I want to type in clot or start cloud again, simply type in cloud again.
- `11:24` — So if I want to resume that session, simply just going to click on return or enter.
- `—` — So if I were to open the sidebar and I go to the public, you can see these are all the SVGs for all 
- `—` — So, if I were to copy that link and just going to navigate to a browser and I'm just going to paste 
- `—` — So if I were to enter this, you can see that currently we're in a discovery.
- `—` — So now if I type in front end design, you can see we have our front end design skill inside of our c
- `—` — If I were to say a prompt for example uh you can see if I were to say hey I want to trigger this in 
- … mais 42

### CTA (9)

- `—` — I'll make sure to put the timestamps in the description below so you can actually check it out.
- `25:31` — But if you want to see the actual video, you can check out this video right here.
- `—` — Make sure to comment down below for this video.
- `—` — And if you want to get in more about like how you can actually have your Google workspace to connect
- `77:52` — So make sure to subscribe to this channel and I'll make sure to let you know once that video is rele
- `—` — Uh if you do find those questions here and answer here helpful, make sure to comment down below.
- `—` — And if you have more question here, make sure to comment down below and I'll make sure to answer tha
- `—` — And if you do found value in this video and you actually want to go even further and master AI agent
- `—` — And if you want to get a full video course on how you can actually build a master claw code, I do ha

