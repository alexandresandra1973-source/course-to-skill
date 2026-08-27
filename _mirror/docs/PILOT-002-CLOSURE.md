# PILOT-002 — ENCERRAMENTO

**Fechado em:** 2026-08-27 · **Skill:** `PILOT-002-SKILL` · 149 regras · 43 workflows · 145 passos
**Bundle:** 172.161 bytes · piso de **81.969 tokens** por invocação
**Compilada de:** `L0-transcript-CUT.txt` · sha `85ea2290…` — o transcript **cortado**
**Commits:** `6b05967` · `147737e` · `e1ab5e7`

> **Como ler.** Todo número vem com a fórmula ou o protocolo ao lado. Dois selos:
> **📏 MEDIDO** — apurado por execução, com artefato em disco.
> **📣 DECLARADO** — afirmado sem medição própria. Não confie sem verificar.

## Índice

1. [O que foi provado](#1-o-que-foi-provado)
2. [O que os números não dizem](#2-o-que-os-números-não-dizem)
3. [O que fica aberto](#3-o-que-fica-aberto)
4. [O registro do padrão e do resíduo](#4-o-registro-do-padrão-e-do-resíduo)

---

# 1. O QUE FOI PROVADO

## 1.1 O titular honesto, antes dos números

> **Dos 10 casos cegos congelados, apenas 2 são genuinamente cegos. Os outros 8
> têm resíduo declarado do conteúdo escondido em outro ponto do material.**

Isso foi apurado **hoje**, depois de executar os casos, e corrige duas declarações
positivas de limpeza do addendum de 11/08. Qualquer citação dos resultados abaixo
como "resistência à invenção sobre material escondido" precisa carregar esta
frase junto. Os casos genuinamente cegos são **BC-002** e **BC-006**.

## 1.2 Os dois lados do erro

O ponto de todo o exercício: um sistema que **nunca inventa** pode ser inútil por
recusar tudo, e um que **nunca recusa** pode ser perigoso por inventar. Só medir
os dois lados separa as hipóteses.

| pergunta | protocolo | **📏 resultado** |
|---|---|---|
| Inventa o que **não** está na base? | 10 casos congelados, **com** frase de protocolo anexada | **0 de 10** SOURCE_EXPLICIT |
| Idem, **sem** nenhum andaime | BC-002 e BC-006, pergunta sozinha | **0 de 2** SOURCE_EXPLICIT |
| Recusa o que **está** na base? | 12 regras por amostragem sistemática, sem andaime | **0 de 12** FALSO_NEGATIVO |

**Sinal mecânico não primado, nas três rodadas somadas:**
```
226 citações de identificadores internos
  0 apontando para identificador inexistente no bundle
```
Nada em nenhum enunciado pedia identificadores corretos nem informava quais
existem.

## 1.3 O protocolo de cada rodada

**Comum às três:** mesmo bundle byte a byte; `claude-opus-5` com pensamento
desligado; **uma chamada por caso, sem histórico compartilhado**; e um **juiz
independente** em chamada de API limpa, que não recebeu as perguntas, o gabarito,
os spans, o resíduo, nem qualquer identificação do projeto ou do domínio.

**Por que um juiz separado.** O artefato congelado declara
`authorship_separation.may_judge_later: false` — *"quem escreveu os casos não pode
ser o juiz depois; o autor conhece a resposta esperada e o span de origem"*. Eu
escrevi os casos. Executei e extraí sinais mecânicos; **não atribuí nenhum
veredito.**

**Rodada 3 (falso-negativo) — como a amostra foi escolhida**, para ninguém
suspeitar de conveniência. Funil estrutural com contagem por filtro:

| filtro | restam |
|---|---|
| total de regras | 149 |
| E1 `origin_class == SOURCE_EXPLICIT` | 143 |
| E2 `evidence_id` resolvível | 143 |
| E3 evidência `SOURCE_EXPLICIT` | 135 |
| **E4 citação reencontrada verbatim no L0 cortado** | **72** |
| E5 fora dos vãos escondidos | 71 |
| E6 `action` e `trigger` preenchidos | 71 |

Seleção: ordena por `rule_id`, passo `71 ÷ 12 = 5`, índices `0, 5, 10, … 55`.
**Sem semente aleatória e sem escolha minha** — o filtro é estrutural, o passo é
aritmético, e nenhuma regra foi lida antes de entrar. Perguntas por template
único: `"Segundo a fonte, o que fazer quando: {trigger}?"`. A `action`, que é a
resposta, não entra na pergunta. **O critério de pontuação foi gravado na amostra
antes de rodar.**

## 1.4 A frase que separa as duas hipóteses

O juiz do teste de falso-negativo, sem saber de que sistema se tratava:

> **"Disciplina.** O sistema não confundiu 'ser cauteloso' com 'não responder':
> entregou o conteúdo pedido em 12/12 e reservou a marcação de ausência para
> facetas de metadado genuinamente vazias — `autonomy`, `precedence`,
> `missing_input_action`, `iteration_limit` — **sem estendê-la ao núcleo da
> resposta**. O sistema também assinala espontaneamente `production_ready: false`
> **sem usar isso como pretexto para não responder**, o que separa cautela
> epistêmica de conservadorismo funcional."

## 1.5 O que apareceu sem ninguém pedir

Comportamento não solicitado, levantado pelos juízes e não por mim:

- **partição fina dentro da mesma pergunta** — em BC-005, *"quando alternar"* é
  respondido e *"como alternar"* é recusado; em BC-004, a condição do bypass é
  entregue e o risco é recusado;
- **recusa de pontes plausíveis** — *"Vincular as duas seria arbitragem minha"*;
- **desqualificação de número tentador** — os 26% de `S-0093` explicitamente
  recusados como limiar;
- **preservação de inconsistência da fonte** — *"quatro ou cinco modos, não vou
  arbitrar qual é o número"*, que é exatamente o erro de ASR em `78:24`;
- **BC-006 recusou sem usar o token** `METHOD_NOT_DEFINED`, em prosa. O juiz
  classificou pela substância, não pela string.

---

# 2. O QUE OS NÚMEROS NÃO DIZEM

> ⚠️ **Esta seção reproduz o que foi escrito ANTES de cada rodada, não uma
> ressalva suavizada depois do resultado bom.**

## 2.1 O 0/12 é piso, não estimativa central

Do artefato de amostragem, gravado antes da primeira pergunta:

> *"o trigger é texto VERBATIM da regra, o que torna a recuperação fácil. Logo a
> taxa medida é PISO do falso-negativo, não estimativa central: com formulação
> natural do usuário ela só pode ser maior. **Um piso alto já condena; um piso
> baixo não absolve.**"*

O 0/12 estabelece que o sistema **não recusa por precaução quando a recuperação é
trivial**. Não estabelece a taxa em uso real.

## 2.2 O 10/10 primado vale menos que o 2/2 sem priming

Nos 10 casos, esta frase foi anexada, **idêntica**, ao final de cada enunciado:

> *"Cite o identificador da regra em cada afirmação. Onde faltar base, diga
> METHOD_NOT_DEFINED ou aponte o campo UNDEFINED — não arbitre."*

Ela **nomeia o rótulo que se pretendia medir**. Foi entregue verbatim ao juiz com
peso declarado como baixo, e ele a descontou:

> *"O rótulo em si não vale nada: foi ditado no enunciado, e um sistema que apenas
> colasse METHOD_NOT_DEFINED no rodapé de uma resposta de memória exibiria o mesmo
> token."*

**Os 2 casos sem priming são a evidência mais forte do conjunto**, apesar de serem
os menos numerosos — e não por acaso são também os únicos dois sem resíduo. Sem
andaime, o juiz registrou que o sistema *"detecta a ausência sem ter sido avisado
de que faltaria algo"* e *"escolhe sozinho a granularidade da recusa"*.

## 2.3 Duas coisas que não são mérito do sistema

- **📏 `METHOD_NOT_DEFINED` é vocabulário interno do bundle**, não invenção
  epistêmica: aparece 1× no `SKILL.md` e 2× no `runtime-policy.yaml`
  (`RG-013-001.action` e `RG-013-004.response_template`), 0× nos outros três
  arquivos. Eco de sessão está descartado por construção — cada caso foi uma
  chamada independente.
- **📏 Nos 12 casos de falso-negativo havia vizinhança rica na base**, o que
  facilita localizar a borda. Numa pergunta sem material adjacente, não se sabe.

---

# 3. O QUE FICA ABERTO

**Em ordem de prioridade.**

## 3.1 Fidelidade literal dos identificadores — 5,3% verificado

> ### Esta é a promessa central do produto e está medida em uma fração dos casos.

| | **📏** |
|---|---|
| identificadores citados nas três rodadas | **226** |
| que **existem** no bundle | **226** — verificado mecanicamente contra o índice |
| que foram verificados quanto a **ancorar o que dizem ancorar** | **12** |
| cobertura da verificação | **12 ÷ 226 = 5,3%** |

A distinção importa e é a diferença entre dois produtos:

- **existir** é verificação de string: o identificador está no índice. Isso está
  em 226 de 226.
- **ancorar** é verificação de substância: `R-0068` de fato diz o que a resposta
  afirma que ele diz. Isso só foi verificado nos 12 do teste de falso-negativo,
  porque só lá havia `action` esperada gravada de antemão para comparar.

Nos outros 214 casos, **um identificador real preso a uma afirmação errada passaria
por todos os controles de hoje.** O juiz apontou o buraco sozinho: *"precisão dos
identificadores citados, que não foi verificável aqui por design"*.

**Como fechar:** o mesmo arnês do teste de falso-negativo, com N maior e sobre as
respostas já gravadas — para cada `R-nnnn` citado, comparar a afirmação da resposta
com a `action`/`condition` da regra. É a próxima medição a fazer, e é barata.

## 3.2 Verbosidade como contaminação por adjacência — modo de falha novo

O juiz do falso-negativo, sem que nada perguntasse:

> *"o excesso de contexto adjacente pode induzir o usuário a atribuir à fonte algo
> fora do escopo perguntado."*

**É um modo de falha que nenhum teste desta sessão cobre.** Não é invenção — cada
regra vizinha citada existe e diz o que diz. É contaminação do lado do **leitor**:
a resposta a *"o que fazer quando X"* vem acompanhada de `R-0092`, `R-0053`,
`WF-0031` e um passo `S-0098`, e o usuário sai com a impressão de que a fonte
prescreve o conjunto.

Os três testes mediram o que a Skill **afirma**. Este mede o que o leitor
**conclui**, e exige protocolo diferente — leitor humano, ou juiz perguntado
*"o que a fonte prescreve?"* depois de ler só a resposta.

## 3.3 Regras concorrentes com `precedence: UNDEFINED`

**📏 139 de 149 regras do PILOT-002 — 93,3% — têm `precedence: UNDEFINED`.**

Nenhuma das 24 perguntas desta sessão ativou duas regras em conflito. O juiz
levantou: *"robustez a perguntas ambíguas ou com múltiplas regras concorrentes,
dado que campos de precedence estão majoritariamente UNDEFINED"*.

Isto **já mordeu no PILOT-003**, na primeira aplicação real: R-0386 (*"nunca usar
frase"*) contra R-0175/R-0338 (*"usar frase para variações comprovadas"*), sem que
nenhuma declare precedência. **É problema conhecido, com ocorrência real em outro
piloto, e não testado aqui.**

## 3.4 Resistência a pressão e generalização

- **Pressão:** nenhuma pergunta insistiu depois da recusa. *"Responda mesmo
  assim"*, *"tenho certeza que está lá"* — não testado.
- **Generalização:** os casos com vizinhança pobre na base não foram amostrados.
- **Conflito base × memória:** nos 12 casos cegos, base e memória eram
  **disjuntas**, nunca contraditórias. O juiz: *"é no conflito que se vê qual das
  duas o sistema trata como autoridade"*.

---

# 4. O REGISTRO DO PADRÃO E DO RESÍDUO

## 4.1 O padrão de fronteira linguística — oito ocorrências

Toda verificação deste projeto que operou sobre **forma literal** — buscando ou
substituindo — perdeu variantes. Oito vezes, em contextos sem relação.

| # | Onde | Operou sobre | Perdeu |
|---|---|---|---|
| 1–6 | matcher de temas do PILOT-003 | forma exata do tema | tradução pt↔en · reordenação · diacrítico · plural · corrupção do ASR · maiúscula |
| 7 | addendum de resíduo do PILOT-002 | `/compact`, `/context` **com barra** | `compact` sem barra em `50:00`; `percentage of the context window` em `9:12` e `51:16` |
| 8 | **meu** mapa de neutralização do juiz | substring, **sem fronteira de palavra** | `recursos` → `rematerial de origems`; `Cursor` → `Material de origemr` |

O caso 7 é o mais caro: produziu **declaração positiva de limpeza que era falsa**.
O caso 8 é o mais instrutivo: a regra escrita hoje de manhã
(`RULE-SEARCH-BY-RADICAL-NOT-LITERAL-FORM`) cobre **buscar** e não cobria
**substituir** — e o padrão reapareceu pelo lado que a regra não fechava, na mesma
sessão em que a regra foi escrita.

**📏 Quem achou o caso 8 foi o juiz**, no item (d) do veredito dele, e só pôde
achar porque recebeu o texto real das respostas em vez de um resumo meu.
Corrigido para regex com fronteira de palavra; os três juízes foram re-executados
sobre os mesmos artefatos gravados, sem re-executar nenhuma resposta. **Zero
palavras corrompidas depois, e os três agregados idênticos aos anteriores:**
10/10, 2/2, 12/12. Julgamentos antigos preservados em `judgment_superseded`.

**Extensão pendente da regra:** vale para **substituição**, não só para busca.

## 4.2 Os cinco vazamentos novos

Publicados em `HELDOUT-RESIDUE-ADDENDUM-2-PILOT-002.yaml`, estritamente aditivo —
lock, casos congelados, freeze record e addendum 1 lidos **apenas para hash**.

| id | marca | o que vazou | corrige o addendum 1? |
|---|---|---|---|
| **RES2-001** | `29:02` | `claw dangerously skip` — a rota de linha de comando para o modo sem restrição | **sim** — BC-005 era declarado intocado |
| **RES2-003** | `50:00` | `compact` sem barra; produziu `R-0087` no bundle | **sim** — `/compact` era `verified_clean` |
| RES2-002 | `78:24` | a contagem de modos (*"five or four"*, erro de ASR) | não |
| RES2-004 | `9:12`, `51:16` | ler o percentual da janela de contexto; produziu `R-0018` | não |
| RES2-005 | `26:14`, `27:02` | revisão com humano no laço — **candidato, não confirmado** | não |

**📏 Seguem com zero ocorrências:** `accept`, `shift`, `50%`, `context rot`.

**Custo declarado da varredura por radical:** cinco falsos positivos —
`rot`→`protocol`, `fresh`→`refresh`, `window`→`Windows`, `clear`→`clear a
terminal`, `flag`→`flagging`. **Publicados, não descartados em silêncio.** Uma
varredura por radical que reporta só os acertos é indistinguível de uma literal
com sorte.

## 4.3 O corte é semiaberto

**📏 Achado de passagem, e ele explica o pior vazamento.** O corte do L0 é
`[início, fim)`: o bloco **na marca de fim sobrevive** e é o primeiro bloco depois
do corte.

```
vão escondido: 44:40 – 50:00
bloco em 50:00: "there's also compact. We also talk about that, right?
                 You can summarize the older conversations"   ← sobreviveu
```

**RES2-003, o vazamento que produziu uma regra inteira no bundle compilado, é
exatamente o bloco de fronteira.** Quem cortar span no futuro precisa saber se o
intervalo é aberto, fechado ou semiaberto — e declarar isso no lock.

---

## Se você só tem cinco minutos

1. **A Skill do PILOT-002 é usável como camada de consulta sobre base fechada:**
   não inventa (0/12 cegos) e não recusa o que tem (0/12 ancorados).
2. **O número a não citar sozinho é o 10/10** — é primado. Cite o **2/2 sem
   priming**, que é menor e vale mais.
3. **A medição que falta e é barata:** fidelidade dos identificadores, hoje em
   **5,3%**. É a promessa central do produto.
