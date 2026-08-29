# KIT DE FECHAMENTO — PILOT-004 · 14/08/2026

> [!success] PREENCHIDO EM 15/08/2026 — PILOT-004 VALIDADO NOS 4 CRITÉRIOS
> **Seção A (C2):** 4 de 5 candidatos julgados *específicos e verdadeiros*; o 5 julgado genérico.
> **Seção B (C3a):** respostas reais chegaram via a agência que administra a estrutura.
> Veredito consolidado em `PILOT-004-VEREDITO-FINAL.md`.

Para o chat de fechamento com o Alexandre. **Só leitura e formatação:** nenhuma
chamada de API foi feita para gerar nem para preencher este arquivo, e nenhum
artefato congelado ou publicado foi alterado.

Fonte dos dados: `03_SKILL/COURSE-GAP-REPORT.md`, `03_SKILL/knowledge/*.yaml`,
`00_SOURCE/L0-transcript.txt`, `00_SOURCE/GAP-CONTROLE-POSITIVO.json`,
`00_SOURCE/T8-MTX-APLICACAO-VERBATIM.md`.

---

# SEÇÃO A — C2 PARA JULGAMENTO

## O critério

> **C2 passa se ao menos UMA das alegações for específica E verdadeira** sobre
> ESTE tutorial — não uma lacuna genérica que valeria para qualquer vídeo de
> Meta Business Suite.

**Padrão de referência (PILOT-003):** *"ensina a construir do zero e nunca ensina
a olhar antes"*. É esse o nível de especificidade que faz o C2 passar: uma frase
que só é verdadeira daquele curso, e que um leitor do curso reconhece como certa.

Cinco candidatos abaixo. Cada um traz o literal da fonte para você conferir sem
depender de mim.

---

## Candidato 1 — as trilhas que a fonte manda seguir e nunca ensina

**(1) Alegação:** o curso instrui a seguir "a trilha do modelo de negócio" e não
ensina nenhuma das três trilhas que ele mesmo nomeia.

**(2) Timestamp:** 11:09 – 11:17

**(3) Literal do L0:**

> **11:09** — pegar na sua mão do básico avançado para negócio local, para vender no X1 através
>
> **11:13** — de mensagem, para fazer campanhas para venda direta também, se você é um
>
> **11:17** — infoprodutor, um afiliado. E fora isso você vai ter comunidade, alunos, suporte

**(4) O que o controle diz:** a regra `R-0026` existe na Skill
(*"Seguir a trilha de campanha correspondente ao modelo de negócio identificado"*)
e **nenhum workflow implementa qualquer uma das três trilhas**. O controle
negativo confirma o vazio ao redor: `orçamento de campanha`, `teste a/b`, `cbo`,
`público semelhante`, `lookalike` — todos ausentes do L0 **e** da Skill, zero
invenções.

**Agravante para o julgamento:** o trecho está dentro da propaganda do
treinamento pago do autor. As três trilhas são citadas como conteúdo do curso
que ele **vende**, não do vídeo gratuito.

**VEREDITO DE ALEXANDRE:** [x] específica e verdadeira · [ ] genérica · [ ] errada

---

## Candidato 2 — o WhatsApp aparece unificado sem nunca ser conectado

**(1) Alegação:** o tutorial mostra o WhatsApp respondido na caixa de entrada
unificada e ensina apenas a **verificar** perfis conectados — nunca a conectar um.

**(2) Timestamps:** 8:04 (uso) · 14:02 (verificação) · nenhum para a conexão

**(3) Literal do L0:**

> **8:04** — Messenger, no Instagram, no WhatsApp, comentários tanto no Instagram quanto no Facebook. Você consegue ver tudo por
>
> **14:02** — condição aqui de ver os seus perfis do WhatsApp que estão conectados aqui
>
> **14:06** — também para poder falar com as pessoas.

**(4) O que o controle diz:** `whatsapp` é **COBERTO** — está no L0 e na Skill,
então não é perda do nosso pipeline. Os dois passos existentes são `S-0021`
(*"Responder na caixa de entrada... Messenger, Instagram e WhatsApp"*) e `S-0041`
(*"**verificar** os perfis do WhatsApp conectados"*). Não há passo de conexão.
O verbo da fonte é "ver que estão conectados", nunca "conectar".

**Relevância direta para a MTX:** o pedido do caso é exatamente unificar
Instagram, Facebook e **WhatsApp Business** — e é justamente o terceiro que o
curso pressupõe pronto.

**VEREDITO DE ALEXANDRE:** [x] específica e verdadeira · [ ] genérica · [ ] errada

---

## Candidato 3 — o pixel é localizado e explicitamente abandonado

**(1) Alegação:** o curso manda guardar o pixel no portfólio, mostra onde ele
fica, e então declara na própria fala que o assunto não é deste vídeo.

**(2) Timestamps:** 2:58 (manda guardar) · 14:06 – 14:17 (localiza e abandona)

**(3) Literal do L0:**

> **2:58** — suas contas de anúncio, tem que guardar seu pixel e toda a sua estrutura de anúncio. Porque que se você deixa isso
>
> **14:06** — Você vai vir aqui e vai ter suas contas do Instagram. Aqui em pixel, em fonte de
>
> **14:12** — dados, você vai ter os pixeis, né, que é muito importante quando você quer vender
>
> **14:17** — online aí, né? **Isso aqui não é o assunto esse vídeo.**

**(4) O que o controle diz:** `pixel` é **COBERTO** (no L0 e na Skill). A regra
`R-0030` registra a exclusão com a condição literal *"O tema pixel não é o
assunto deste vídeo"* e ação *"Apenas localizar/mencionar os pixels em 'fonte de
dados' e não desenvolver o assunto"*. Não é omissão silenciosa — é abandono
declarado pelo próprio autor, capturado pela compilação.

**VEREDITO DE ALEXANDRE:** [x] específica e verdadeira · [ ] genérica · [ ] errada

---

## Candidato 4 — dois pré-requisitos declarados e terceirizados no minuto final

**(1) Alegação:** criar página e criar conta de anúncio são apresentados como
necessários e remetidos para fora do vídeo, a 30 segundos do fim.

**(2) Timestamps:** 13:56 (menciona criar conta) · 14:31 – 14:41 (terceiriza)

**(3) Literal do L0:**

> **13:56** — anúncio que você tem, tá vendo? Você pode vir aqui também criar conta de anúncio por aqui, né? Você vai ter
>
> **14:31** — você entrar aqui, olhar com calma, continuar estudando os conteúdos que tem
>
> **14:35** — aqui no canal para você aprender criar página, para você às vezes aprender a criar conta de anúncio, né, e montar a

**(4) O que o controle diz:** virou `S-0044` (*"continuar estudando os conteúdos
do canal para aprender a criar página"*) — um passo cuja ação é sair do curso.
Reforça o Candidato 1: a mesma estrutura de "o método está no outro conteúdo".

**Tensão a notar no julgamento:** `R-0004` do próprio runtime diz que **sem
página do Facebook não há acesso aos recursos do Business Suite**. Ou seja, o
tutorial declara um pré-requisito duro e não o ensina.

**VEREDITO DE ALEXANDRE:** [x] específica e verdadeira · [ ] genérica · [ ] errada

---

## Candidato 5 — nada neste curso autoriza execução autônoma

**(1) Alegação:** `autonomy` é `UNDEFINED` em **100%** das regras e passos — o
curso nunca diz até onde alguém pode agir sem conferir.

**(2) Timestamp:** não aplicável — é ausência medida sobre a fonte inteira
(0:00 – 15:03), não um trecho.

**(3) Literal do L0:** não há. É exatamente esse o ponto: nenhuma passagem do
tutorial estabelece limite de autonomia. Contagem conferida nos artefatos:

| campo | regras | passos |
|---|---|---|
| `autonomy` | **32/32** | **44/44** |
| `iteration_limit` | 32/32 | 44/44 |
| `missing_input_action` | 32/32 | 44/44 |
| `precedence` | 31/32 | — |

A única exceção em todo o pacote é `R-0001`, cujo `precedence` diz *"Precede o
passo a passo de acesso ao Meta Business Suite"*.

**(4) O que o controle diz:** o controle por token não alcança este candidato —
ele mede presença de vocabulário, e aqui a alegação é sobre ausência de campo
estrutural. A verificação é a contagem acima, direta nos YAML publicados.

**Ressalva honesta:** este é o candidato **mais fraco em especificidade**. Um
tutorial de demonstração de tela dificilmente definiria autonomia, então a
alegação pode valer para qualquer vídeo do gênero — o que é o teste que o C2
aplica. Incluído por completude, não por convicção.

**VEREDITO DE ALEXANDRE:** [ ] específica e verdadeira · [x] genérica · [ ] errada

---

### Nota de método sobre a Seção A

Os candidatos 1, 2 e 4 compartilham uma forma: **a fonte nomeia um método e o
coloca fora de si mesma.** Se você julgar que isso é uma única alegação em três
manifestações, o C2 se decide por ela. Se julgar que são três independentes, C2
passa se qualquer uma passar. A decisão de agrupar ou não é sua — não agrupei
para não fazer a escolha no seu lugar.

---
---

# SEÇÃO B — C3a · CHECKLIST PARA A CONTA REAL

Os **15 pedidos** que a Skill fez ao caso MTX, sem receber nenhum dado.
Verbatim em `T8-MTX-APLICACAO-VERBATIM.md`.

Ordenados **do mais rápido de conferir ao mais lento**: primeiro o que você
responde de cabeça, depois o que exige uma tela, depois várias, depois decisão de
negócio, e por último o que exige ler dado acumulado.

> [!note] RESPOSTAS REAIS — 15/08/2026
> Vieram da **agência Click**, que administra a estrutura Meta da MTX.
> Placar: **8 configurados · 2 não existem · 5 não conferidos**.
> O item **11** é a correção conferível que decide o C3a.

Caso, como foi dado à Skill: *empresa de peças de moto com Instagram, Facebook e
WhatsApp Business; quer gerenciar os três canais de forma unificada.*

---

### 1. Sessão do Facebook ativa
**Pediu:** confirmação de que você está logado no perfil do Facebook que
administra a empresa.
**Caminho:** sessão ativa em `facebook.com`, no navegador que será usado.
**Regra:** `R-0001` (precede todo o passo a passo de acesso).
**ESTADO REAL:** [x] existe/configurado · [ ] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** estrutura **operada pela agência Click**. Sessão e acesso são da agência, não da MTX.

### 2. Gestão de múltiplos clientes
**Pediu:** você opera esta conta como gestor, com outros clientes na mesma
máquina/navegador?
**Caminho:** resposta direta — não precisa abrir nada.
**Regra:** `R-0002` (ambiente separado por cliente, para não cruzar dados).
**ESTADO REAL:** [x] existe/configurado · [ ] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** sim — a estrutura é operada por agência, com outros clientes. `R-0002` (ambiente separado) passa a valer para a agência, não para a MTX.

### 3. Histórico de anúncios na estrutura
**Pediu:** já foram feitos anúncios nesta estrutura?
**Caminho:** resposta direta.
**Regra:** `R-0023` (decide entre anunciar pelo Business Suite ou pelo
Gerenciador de Anúncios).
**ESTADO REAL:** [x] existe/configurado · [ ] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** anúncios **existiram em 2023/24**, nada novo desde. Mídia paga hoje concentrada no **Google Ads**, fora do escopo desta Skill.

### 4. Anúncio pelo app no iPhone
**Pediu:** haverá criação de anúncio pelo aplicativo em iPhone?
**Caminho:** resposta direta.
**Regra:** `R-0009` (a fonte alerta que o custo pode subir ~30%).
**ESTADO REAL:** [ ] existe/configurado · [ ] não existe · [x] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **NÃO RESPONDIDO** neste retorno. Não bloqueia o critério — `R-0009` só afeta custo se houver criação de anúncio pelo app.

### 5. Ícones no topo do painel — o critério de conformidade da fonte
**Pediu:** aparecem **os dois** ícones acesos (página do Facebook e Instagram),
ou só o do Facebook?
**Caminho:** topo do painel do Meta Business Suite.
**Regra:** `S-0008`, avaliado por `R-0007` / `R-0008` (só Facebook aceso = o
Instagram é tratado como perfil abandonado).
**ESTADO REAL:** [x] existe/configurado · [ ] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **dois ícones ativos** → CONFIGURADO. É o critério de conformidade da própria fonte (`R-0007`/`R-0008`).

### 6. Página do Facebook da empresa
**Pediu:** existência e nome da página.
**Caminho:** painel → *ver mais* → *Páginas*.
**Regra:** `S-0003`, exigido por `R-0004` (sem página não há acesso aos recursos
— requisito, não preferência).
**ESTADO REAL:** [x] existe/configurado · [ ] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **CONFIGURADO por implicação**, não por leitura direta: o item 10 confirma portfólio com *página vinculada* e o item 8 confirma Instagram conectado **à página**. Ambos pressupõem a página existente.

### 7. Formulários / CRM gratuito disponível na conta
**Pediu:** a opção de formulários aparece nesta conta?
**Caminho:** área de formulários no painel.
**Regra:** `R-0022` (a fonte declara que o recurso só existe em algumas contas —
por isso é verificação, não pressuposto).
**ESTADO REAL:** [ ] existe/configurado · [x] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** CRM/formulários da Meta **NÃO utilizados**. O inbox é respondido **internamente pela equipe MTX**. `R-0022` resolvido: o recurso não entra na operação.

### 8. Tela "contas vinculadas" — Instagram conectado à página
**Pediu:** o Instagram da empresa já aparece conectado?
**Caminho:** página → *alternar* → *alternar* → *contas vinculadas*.
**Regra:** `S-0004`, com `R-0005` (é essa conexão que faz nascer o portfólio
empresarial).
**ESTADO REAL:** [x] existe/configurado · [ ] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **Instagram conectado à página** → CONFIGURADO.

### 9. Perfis de WhatsApp conectados
**Pediu:** quais perfis de WhatsApp já estão conectados à estrutura.
**Caminho:** área de contas → perfis do WhatsApp.
**Regra:** `S-0041`.
**Atenção:** se a resposta for "não existe", a Skill **para aqui** — ela não tem
passo de como conectar (Candidato 2 da Seção A). Este é o item que mais
provavelmente trava a metade a do C3.
**ESTADO REAL:** [x] existe/configurado · [ ] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **WhatsApp conectado como número principal** → CONFIGURADO. A lacuna do Candidato 2 da Seção A **não afeta a MTX**: a conexão já existe, e o passo que a fonte não ensina não é necessário aqui.

### 10. Portfólio empresarial e ativos dentro dele
**Pediu:** existe portfólio empresarial? Se existe, quais ativos estão dentro:
contas de anúncio, pixel, estrutura de anúncio.
**Caminho:** portfólio empresarial / seção *Contas* do Gerenciador.
**Regra:** `S-0039`, `S-0040`, avaliado por `R-0006` (não deixar a estrutura
isolada fora do portfólio, nem mantê-la na conta pessoal).
**ESTADO REAL:** [x] existe/configurado · [ ] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** portfólio empresarial **próprio** existe — `mtximports_` — com página vinculada. Veio da gestão anterior e é administrado pela agência.

### 11. Administrador adicional de contingência
**Pediu:** quem será cadastrado como administrador adicional, identificado.
**Caminho:** *Configurações* → *Usuários* → *Pessoas*.
**Regra:** `S-0037` → `S-0038`, por `R-0029`. A fonte trata como o de maior risco
se ficar para depois: em restrição a nível de perfil, perde-se página, Instagram
e contas de anúncio de uma vez.
**ESTADO REAL:** [ ] existe/configurado · [x] não existe · [ ] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **NÃO EXISTE administrador da MTX.** Só a agência mais o perfil pessoal do contato como backup. → **CORREÇÃO CONFERÍVEL ENCONTRADA**: cadastrar administrador da MTX (`S-0038`, por `R-0029`). Correção **já solicitada por Alexandre à agência**.

### 12. Modelo de negócio, entre os três que a fonte reconhece
**Pediu:** negócio local, venda no X1 por mensagem, ou venda direta
infoprodutor/afiliado.
**Caminho:** declaração sua — a Skill **se recusou a classificar** peças de moto
por conta própria.
**Regra:** `R-0026`.
**Atenção:** qualquer que seja a resposta, a trilha correspondente **não existe**
no runtime (Candidato 1 da Seção A). O pedido é legítimo; o que vem depois dele
é `METHOD_NOT_DEFINED`.
**ESTADO REAL:** [ ] existe/configurado · [ ] não existe · [x] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **PENDENTE-ALEXANDRE.** Não bloqueia o critério.

### 13. Output esperado da operação unificada
**Pediu:** o que a operação deve produzir ao final — conversa respondida, lead
etiquetado, orçamento enviado, venda fechada.
**Caminho:** decisão sua. A Skill declarou que não inventa.
**Regra:** guard `RG-013-003` (contrato de configuração). É neste campo que ela
emite `MISSING_REQUIRED_INPUT`.
**ESTADO REAL:** [ ] existe/configurado · [ ] não existe · [x] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **PENDENTE-ALEXANDRE.** Não bloqueia o critério.

### 14. Boundaries do atendimento
**Pediu:** o que a automação **nunca** deve fazer ou responder, horário de
atendimento humano, e quando escalar para pessoa.
**Caminho:** decisão sua.
**Regra:** guard `RG-013-003`.
**ESTADO REAL:** [ ] existe/configurado · [ ] não existe · [x] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **PENDENTE-ALEXANDRE.** Não bloqueia o critério.

### 15. Comportamento da audiência por rede
**Pediu:** quando cada rede entrega — para decidir horários de postagem
diferentes em Facebook e Instagram.
**Caminho:** *Insights* → *Públicos*, e visão geral de desempenho de conteúdo.
**Regra:** `S-0031`, `S-0032`, `S-0035`, exigido por `S-0016` / `R-0014`.
**Por que é o último:** exige ler dado acumulado, não uma tela. O exemplo da
fonte (Facebook de manhã, Instagram à tarde) é explicitamente **condicionado** a
essa leitura — não é regra fixa a copiar.
**ESTADO REAL:** [ ] existe/configurado · [ ] não existe · [x] não encontrei
**RESPOSTA REAL (15/08/2026, via agência Click):** **não conferido** — exige leitura de dado acumulado. Não bloqueia o critério.

---

### Como ler o resultado da Seção B

A metade **b** do C3 já está satisfeita: a Skill pediu dado nomeado, com caminho
e origem, e recusou-se a classificar o negócio da MTX por conta própria.

A metade **a** se decide aqui. Ela passa se, com as respostas acima, sair **ao
menos uma configuração ou correção conferível** na conta real — por exemplo, o
item 5 revelar que só o ícone do Facebook está aceso (correção: conectar o
Instagram, `S-0005`), ou o item 11 revelar que não há administrador adicional
(correção: cadastrar, `S-0038`).

Os itens **9 e 12** são os que provavelmente vão bater em `METHOD_NOT_DEFINED`.
Bater neles **não reprova** o C3a — pedir o dado certo e parar onde a fonte não
ensina é o comportamento desejado, e é o oposto do modo de falha do C4.
