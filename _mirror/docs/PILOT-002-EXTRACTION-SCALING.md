# PILOT-002 — EXTRACTION SCALING

**Gerado:** `2026-08-11T23:47:59+00:00` · gerador `pilot002_extraction_scaling.py` · **somente medição**, READ-ONLY.

Relatório gerado por script; nenhum número foi digitado.


**A pergunta:** o PILOT-002 produziu 44 evidências — exatamente o mesmo número do PILOT-001 — sobre uma fonte 4,8× maior, cobrindo 37,2% contra 73,5%. Isto é **truncamento** (o extractor parou por orçamento) ou **seleção** (escolheu por saliência até um alvo implícito)? As duas hipóteses fazem previsões diferentes sobre a FORMA da distribuição, e é a forma que este relatório mede.


## 0. Insumos

| insumo | sha256 | extensão | registros |
|---|---|---|---|
| PILOT-002 · L0 cortado | `85ea229011a989ea…` | 4384s | 44 evidências |
| PILOT-002 · EVIDENCE | `a23c837d37cbc9e6…` | — | — |
| PILOT-001 · evidence.jsonl | `2eb266b1fa1c965b…` | 905s | 44 evidências |

> Os 44 registros do PILOT-001 têm timestamp; nenhum ficou fora.


> **Eixo do PILOT-002.** As duas janelas de held-out foram removidas e o que sobra foi remapeado sobre um eixo contínuo de 0–4384s. Sem isso, uma faixa de 5 minutos que contivesse um corte teria menos conteúdo real que as outras e a densidade sairia distorcida por artefato de medição. O tempo de vídeo original viaja na coluna à direita.


## 1. Distribuição temporal do PILOT-002 — faixas de 5 minutos

| faixa (corpus) | faixa (vídeo) | n |  | por 5min | evidências |
|---|---|---|---|---|---|
| 0:00–5:00 | 0:00–5:00 | 3 | ███ | 3.0 | E001, E002, E003 |
| 5:00–10:00 | 5:00–10:00 | 2 | ██ | 2.0 | E004, E005 |
| 10:00–15:00 | 10:00–18:13 | 3 | ███ | 3.0 | E006, E007, E008 |
| 15:00–20:00 | 18:13–23:13 | 2 | ██ | 2.0 | E009, E010 |
| 20:00–25:00 | 23:13–28:13 | 3 | ███ | 3.0 | E011, E012, E013 |
| 25:00–30:00 | 28:13–33:13 | 4 | ████ | 4.0 | E014, E015, E016, E017 |
| 30:00–35:00 | 33:13–38:13 | 4 | ████ | 4.0 | E018, E019, E020, E021 |
| 35:00–40:00 | 38:13–43:13 | 2 | ██ | 2.0 | E022, E023 |
| 40:00–45:00 | 43:13–53:33 | 5 | █████ | 5.0 | E024, E025, E026, E027, E028 |
| 45:00–50:00 | 53:33–58:33 | 3 | ███ | 3.0 | E029, E030, E031 |
| 50:00–55:00 | 58:33–63:33 | 4 | ████ | 4.0 | E032, E033, E034, E035 |
| 55:00–60:00 | 63:33–68:33 | 2 | ██ | 2.0 | E036, E037 |
| 60:00–65:00 | 68:33–73:33 | 4 | ████ | 4.0 | E038, E039, E040, E041 |
| 65:00–70:00 | 73:33–78:33 | 2 | ██ | 2.0 | E042, E043 |
| 70:00–73:04 | 78:33–81:37 | 1 | █ | 1.6 | E044 |

**Total: 44 evidências em 15 faixas de 5 minutos.** Faixas vazias: **0**. Máximo numa faixa: 5 · mínimo: 1. Nenhuma faixa ficou sem evidência, inclusive a última.


> A cauda **não** está vazia. Se o extractor tivesse parado por orçamento, o fim da fonte seria o primeiro lugar a esvaziar, e é justamente lá que está `E044`, a 70:00 do corpus (78:33 de vídeo). A hipótese de truncamento morre aqui; o resto da seção mede o quanto.


### 1.1 A forma, em números

| medida | valor | como ler |
|---|---|---|
| centroide (0 = início, 1 = fim) | **0.501** | 0,500 se uniforme; < 0,4 se carregado no início |
| primeira metade × segunda metade | **22 × 22** | equilíbrio se seleção; desequilíbrio forte se truncamento |
| inclinação da densidade (por faixa) | **-0.069** | negativa e consistente se truncamento |
| Spearman (faixa × densidade) | **-0.289** | ≤ −0,5 indica queda monotônica |
| qui-quadrado vs uniforme (gl=14) | **3.0** | crítico 23.68 (p=0,05) · 29.14 (p=0,01) |
| coeficiente de variação da densidade | 0.375 | — |

### VEREDITO PILOT-002: **SELEÇÃO**

Sem queda monotônica e com as duas metades equilibradas — a assinatura de escolha por saliência até um alvo.


### 1.2 Uniforme DEMAIS — a cauda inferior do qui-quadrado

O teste habitual pergunta se a distribuição é irregular demais para ser uniforme. Aqui ela falha na direção oposta, e isso diz mais:

| item | valor |
|---|---|
| estatística observada (PILOT-002) | **3.0** |
| valor esperado sob sorteio realmente aleatório | 14 (= graus de liberdade) |
| crítico da cauda inferior, p=0,05 | 6.57 |
| crítico da cauda inferior, p=0,01 | 4.66 |

**A estatística fica abaixo até do crítico de 1% da cauda inferior.** As 44 evidências estão distribuídas de forma **mais regular do que o acaso produziria**. Sorteio uniforme geraria aglomerações e vazios que aqui não existem: a contagem por faixa oscila entre 1 e 5 e nunca chega a zero.


Isso não é compatível com 'o extractor pegou o que era saliente e por acaso deu 44'. É compatível com **cota por trecho**: um número aproximadamente fixo de evidências por unidade de transcript, independentemente do que havia ali.


### 1.3 A ordem dos IDs — passada linear única

| piloto | inversões | pares comparados | ordem de ID = ordem da fonte |
|---|---|---|---|
| PILOT-002 | 0 | 946 | **SIM** |
| PILOT-001 | 0 | 946 | **SIM** |

**Zero inversões nos dois pilotos.** `E001…E044` e `EV-0001…EV-0044` aparecem na fonte exatamente na ordem em que foram numerados. O extractor percorreu o transcript **uma vez, do início ao fim**, emitindo à medida que avançava — não varreu tudo para depois escolher os melhores achados.


Junto com a §1.2, isso fecha o mecanismo: **passada linear única com cota aproximadamente constante por trecho.** O total de 44 não é um alvo numérico que alguém digitou; é o que essa cota produz — e como a cota é por trecho e não por segundo, ela devolve um número parecido para fontes de tamanhos muito diferentes.


## 2. O mesmo, no PILOT-001 — faixas proporcionais

Para comparar fontes de tamanhos diferentes (905s contra 4384s), as faixas são **proporcionais**: 15 faixas de 1/15 da fonte cada. No PILOT-002 isso dá 292s por faixa (≈ os 5 minutos pedidos); no PILOT-001, 60s.

| faixa | P001 tempo | n |  | P002 tempo | n |  |
|---|---|---|---|---|---|---|
| 1/15 | 0:00–1:00 | 1 | █ | 0:00–4:52 | 3 | ███ |
| 2/15 | 1:00–2:01 | 4 | ████ | 4:52–9:45 | 2 | ██ |
| 3/15 | 2:01–3:01 | 5 | █████ | 9:45–14:37 | 3 | ███ |
| 4/15 | 3:01–4:01 | 0 | · | 14:37–19:29 | 2 | ██ |
| 5/15 | 4:01–5:02 | 5 | █████ | 19:29–24:21 | 3 | ███ |
| 6/15 | 5:02–6:02 | 4 | ████ | 24:21–29:14 | 4 | ████ |
| 7/15 | 6:02–7:02 | 3 | ███ | 29:14–34:06 | 3 | ███ |
| 8/15 | 7:02–8:03 | 3 | ███ | 34:06–38:58 | 3 | ███ |
| 9/15 | 8:03–9:03 | 3 | ███ | 38:58–43:50 | 4 | ████ |
| 10/15 | 9:03–10:03 | 4 | ████ | 43:50–48:43 | 4 | ████ |
| 11/15 | 10:03–11:04 | 3 | ███ | 48:43–53:35 | 3 | ███ |
| 12/15 | 11:04–12:04 | 3 | ███ | 53:35–58:27 | 2 | ██ |
| 13/15 | 12:04–13:04 | 4 | ████ | 58:27–63:19 | 4 | ████ |
| 14/15 | 13:04–14:05 | 2 | ██ | 63:19–68:12 | 2 | ██ |
| 15/15 | 14:05–15:05 | 0 | · | 68:12–73:04 | 2 | ██ |

| medida | PILOT-001 | PILOT-002 |
|---|---|---|
| registros na geometria | 44 | 44 |
| extensão da fonte | 905s | 4384s |
| evidências por 1000s de fonte | **48.6** | **10.0** |
| faixas vazias | 2 | 1 |
| centroide | 0.474 | 0.501 |
| 1ª metade × 2ª metade | 24 × 20 | 22 × 22 |
| inclinação da densidade | -0.320 | -0.069 |
| Spearman | -0.285 | -0.289 |
| qui-quadrado (gl=14) | 11.9 | 3.0 |
| **veredito** | **SELEÇÃO** | **SELEÇÃO** |

**A densidade de extração caiu de 48.6 para 10.0 evidências por 1000s — fator 4.84×.** É esse o número que explica o 44 repetido: o extractor não escalou com a fonte.


## 3. Tamanho do span citado

Se o PILOT-002 cita spans maiores, ele compensa volume com granularidade e a leitura muda — não é 'extraiu menos', é 'extraiu mais grosso'.

| piloto | média | mediana | min–max | IQR | soma |
|---|---|---|---|---|---|
| PILOT-001 (timestamp declarado) | 17.8s | 15.0s | 5–74s | 10–20s | 785s |
| PILOT-002 (span de linha → tempo) | 38.2s | 35.0s | 17–79s | 28–47s | 1680s |

**O span médio do PILOT-002 é 2.14× o do PILOT-001; a mediana, 2.33×.**


Em linhas de transcript, sem passar por tempo:

| piloto | linhas (média) | linhas (mediana) | min–max |
|---|---|---|---|
| PILOT-002 | 21.6 | 20.0 | 9–51 |

> **Ressalva de medida.** O PILOT-001 declara o span em timestamp e a medida é direta. O PILOT-002 declara em faixa de linhas, e converter para tempo obriga a encostar nas marcas que a faixa toca — o que **infla** o span medido. A comparação de tamanho é, portanto, um **teto** para o PILOT-002, não um valor exato. Se ainda assim o span do PILOT-002 sair maior, a conclusão se sustenta; se sair menor, sai menor com folga.


Soma dos spans do PILOT-002: **1680s**; união: **1630s**. A diferença de **50s** é sobreposição entre evidências vizinhas (`E014`/`E015`, `E021`/`E022`, `E029`/`E030`, `E043`/`E044` e outras citam faixas que se cruzam).


## 4. Os 15 blocos virgens ≥ 60s — o que ficou de fora

| faixa (vídeo) | dur | seção do curso | trecho |
|---|---|---|---|
| 26:32–30:12 | 220s | Installing and Triggering Claude Skills | of it like GitHub is kind of like Google cloud or one drive kind of keeping track of all the version of your application right or in this case store t… |
| 38:38–41:41 | 183s | Exploring File Structures and Directories | of like Lego pieces. You piece them all together into bigger applications. So this why that's why we have components folder here which contains all th… |
| 56:04–59:02 | 178s | Managing Version Control with GitHub | to revert back to changes that are being worked on maybe like June 18th right if I were to scroll down maybe like there's some changes that were done … |
| 18:58–21:51 | 173s | Understanding Permission Modes (Plan, Accept Edits, Auto, Bypass) | front-end framework here that will basically help you to building applications which we will talk a little more about in our channel and also our scho… |
| 65:00–67:46 | 166s | Connecting Tools & Deploying Apps via MCP and CLI | on the web or connecting to maybe like Stripe or PayPal or people to connect to Slack or Jira whichever softwares or apps you're using day-to-day you … |
| 5:49–8:33 | 164s | Choosing an IDE & Installing VS Code; Customizing VS Code Themes; Starting and Managing a Claude Code Session | going to give a name for that folder and just going to click on create. And then here we're just going to click on open. And now you can see we're ope… |
| 32:23–35:06 | 163s | Installing and Triggering Claude Skills; Exploring File Structures and Directories | grid or canvas or something. But you can see that we have still the functionality working, right? I can still be able to drag that on onto a specific … |
| 72:59–75:33 | 154s | Frequently Asked Questions (FAQ) | think of like agents as the agents that we're going to you know do the executions and each agent here can have his skill has his own skills how many s… |
| 0:34–2:49 | 135s | Introduction & Course Overview; Installing Claude Code on Your Local Machine | curriculum covers how to connect remote tools using the model context protocol, integrate version control with GitHub, and successfully deploy your bu… |
| 8:55–11:05 | 130s | Starting and Managing a Claude Code Session | have. So if I were to say hi for example and what's going to happen here is that it's going to do some thinking and now you can see it says hi Eric ho… |
| 79:27–81:37 | 130s | Frequently Asked Questions (FAQ) | because I made videos on claw code for over more than a year now. Okay, since it was released last year, I started making video on this and the stuff … |
| 76:14–78:17 | 123s | Frequently Asked Questions (FAQ) | are just learning started learning claw code, then that's more than enough. But if you're trying to use this every single day, I'm gonna be upfront wi… |
| 59:27–60:58 | 91s | Managing Version Control with GitHub | it is. But master branch basically means that this is the current branch that we're in and we only have this one branch and that's the source of truth… |
| 62:42–63:53 | 71s | Managing Version Control with GitHub; Connecting Tools & Deploying Apps via MCP and CLI | claw code all right so by now you pretty much have all the basics down for how to use claw code the next thing we're going ## Connecting Tools & Deplo… |
| 36:18–37:28 | 70s | Exploring File Structures and Directories | package.json, those dependencies, it's going to creating all those no module here inside of it. So all the libraries that install it's going to store … |

**15 blocos, 2151s no total — 49.1% do corpus de treino.**


Agregado por seção do curso:

| seção | segundos virgens |
|---|---|
| Exploring File Structures and Directories | 416s |
| Frequently Asked Questions (FAQ) | 407s |
| Installing and Triggering Claude Skills | 383s |
| Managing Version Control with GitHub | 340s |
| Starting and Managing a Claude Code Session | 294s |
| Connecting Tools & Deploying Apps via MCP and CLI | 237s |
| Understanding Permission Modes (Plan, Accept Edits, Auto, Bypass) | 173s |
| Choosing an IDE & Installing VS Code | 164s |
| Customizing VS Code Themes | 164s |
| Introduction & Course Overview | 135s |
| Installing Claude Code on Your Local Machine | 135s |

> **Duas ressalvas de leitura desta tabela.**

>

> 1. A soma das linhas (2848s) é MAIOR que o total de blocos virgens (2151s) porque um bloco que atravessa duas seções é contado nas duas. A tabela mostra em que seções o vazio aparece, não uma partição.

>

> 2. A linha **Understanding Permission Modes** é artefato, não achado. O conteúdo dessa seção foi retirado pelo held-out; o que sobrou foi o TÍTULO, que é o resíduo já declarado no lock. Sem conteúdo próprio, o título passa a nomear o intervalo até o título seguinte, e absorve o material que vinha DEPOIS do corte. O trecho listado em 18:58–21:51 fala de framework de front-end, não de modos de permissão. Nenhum segundo de modo de permissão está nesta tabela — eles não estão no corpus de treino.


## 5. Leitura

1. **A forma da distribuição do PILOT-002 é `SELEÇÃO`** — sem queda monotônica e com as duas metades equilibradas — a assinatura de escolha por saliência até um alvo.

2. **O PILOT-001 mede `SELEÇÃO`** pelos mesmos critérios. O padrão é o mesmo nas duas fontes, o que afasta a explicação 'a fonte do PILOT-002 é diferente' e joga a causa para o extractor.

3. **A densidade caiu 4.84×** enquanto o total ficou congelado em 44. Um extractor que escalasse com a fonte teria produzido cerca de **213** evidências para cobrir o PILOT-002 na mesma proporção do PILOT-001.

4. **O span médio do PILOT-002 é 2.14× o do PILOT-001** (e esse número é teto). A granularidade mais grossa compensa parte do volume: o extractor cita menos vezes, mas cada citação carrega mais fonte.

5. **O mecanismo, nomeado:** passada linear única (zero inversões de ordem) com cota aproximadamente constante por trecho (qui-quadrado 3.0, abaixo do crítico inferior de 1%). O 44 não foi escolhido; foi o que essa cota devolveu. Como a cota é por trecho e não por segundo de fonte, ela produz um total parecido para fontes de tamanhos muito diferentes — que é exatamente o sintoma.


---

**Escopo:** somente medição. Nenhuma evidência foi reescrita, nenhum arquivo de `pilots/`, `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado. O único arquivo escrito é este relatório.
