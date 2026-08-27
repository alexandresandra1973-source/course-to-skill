# PILOT-003 — ENCERRAMENTO

**Fechado em:** 2026-08-27 · **Curso:** *(2026) Ecommerce Google Ads Free Course* `c6qEURhNsYw` · 3h50m57s
**Conta:** MTX IMPORTS - ATUAL 24/25 (170-554-4703) · janela 15/05–12/08/2026 (90 dias)
**Commits:** `ed00f8b` (piloto completo) · `8becb52` (rodada 4)

> **Como ler este documento.** Ele existe para você voltar em uma semana ou um mês
> sem reconstruir nada. Todo número vem com a fórmula ao lado. Dois selos aparecem
> ao longo do texto:
>
> **📏 MEDIDO** — apurado por execução, com artefato em disco e fórmula reproduzível.
> **📣 DECLARADO** — informado por alguém, ou afirmado sem medição. Não confie sem verificar.

## Índice

1. [O que foi provado](#1-o-que-foi-provado)
2. [Frente de negócio — dono: Alexandre](#2-frente-de-negócio--dono-alexandre)
3. [Frente de produto — dono: o compilador](#3-frente-de-produto--dono-o-compilador)
4. [Dívida técnica e risco](#4-dívida-técnica-e-risco)
5. [Estado dos arquivos](#5-estado-dos-arquivos)

---

# 1. O QUE FOI PROVADO

## 1.1 Os quatro critérios

| # | Critério | Veredito | Base |
|---|---|---|---|
| 1 | Cobertura > 80% | ✅ **PASSA** | **📏 89,8%** de cobertura evidência→regra |
| 2 | Achado específico e verdadeiro sobre o curso | ✅ **PASSA** | `negative keyword` aparece **3 vezes em 3h50m**; a conta confirma **0 termos negativados em 24.795 linhas** |
| 3a | Conclusão específica dos dados que tem | ✅ **PASSA** | PMax não qualifica (R-0430): exige US$50–100/dia e 30–50 conv/mês, realizado R$31,11/dia e 4,83 conv/mês |
| 3b | Pede dado que não foi dado | ✅ **PASSA** | 14 pedidos explícitos, cada um com a regra que o exige |
| 4 | Modo de falha (conselho genérico) | ✅ **NÃO CAIU** | toda conclusão cita identificador de regra e número da conta |

**📏 Densidade:** `2.463 ÷ 13.857 s = 0,1777 ev/s` — a mais alta dos três pilotos, sobre corpus 15,3× maior que o PILOT-001.

## 1.2 O break-even CPA — o resultado central da rodada 4

Nas três primeiras rodadas o KPI que a fonte declara **primário** estava indisponível: faltava o AOV. Toda a auditoria rodava no KPI que R-0523 chama de *"irrelevante em comparação"*. Com o AOV, R-0134 executou.

**Rota 1 — R-0134, fórmula direta da fonte (EV-1620):**
```
break-even CPA = AOV × % margem − custos fixos de COGS
               = 2.533,86 × 0,50 − 0,00
               = R$ 1.266,93
```

**Rota 2 — R-0133 (EV-1616) combinada com o AOV:**
```
break-even ROAS = 100 ÷ 50 = 2,0
AOV ÷ BE-ROAS   = 2.533,86 ÷ 2,0 = R$ 1.266,93
```

> ⚠️ **As duas rotas não são independentes, e isso importa.** Ambas consomem a mesma
> margem de 50%, e com custos fixos em zero são algebricamente equivalentes
> (`AOV × m ≡ AOV ÷ (100/m)`). O acordo entre elas **confirma aplicação correta das
> duas fórmulas da fonte, não confirma o valor**. A própria Skill registrou isso sem
> ser perguntada. Não trate como dupla confirmação.

**📏 Vereditos** (critério: CPA observado ≤ 1.266,93):

| Campanha | CPA | fórmula da folga | Folga |
|---|---|---|---|
| VENDAS\|PERF-MAX | 193,10 | `1.266,93 ÷ 193,10` | **6,56×** ✅ |
| VENDAS\|ATUAL | 157,98 | `1.266,93 ÷ 157,98` | **8,02×** ✅ |
| Conversão V&H | 82,17 | `1.266,93 ÷ 82,17` | **15,42×** ✅ |
| **Conta** | **125,40** | `1.266,93 ÷ 125,40` | **10,10×** ✅ |

**Robustez, conferida em três cenários:**

- pior AOV de 2026 → `2.030,88 × 0,50 = 1.015,44` → folgas de 5,26× a 12,36×, **nenhuma linha muda de lado**;
- só as 48 compras da tela de Metas → `9.577,32 ÷ 48 = 199,53` → folga `1.266,93 ÷ 199,53 = **6,35×**`, ainda passa;
- para a conta cair ao break-even, `1 − (9.577,32 ÷ 1.266,93) ÷ 76,38 = **90,1%**` das conversões teriam de ser espúrias.

## 1.3 O que a Skill achou sozinha

Quatro coisas que ninguém tinha achado e que não vieram de pergunta:

1. **O maior termo de desperdício da conta é o nome da marca.** `mtx` — R$58,46, 41 cliques, **zero** conversões, item nº 1 da lista de desperdício. Só ficou visível quando os termos de marca foram fornecidos.
2. **Três colunas quebradas nos recortes**, detectadas por reconciliação aritmética, com recusa a raciocinar sobre dados corrompidos. Recusou-se também a julgar antes do break-even (R-0517) e corrigiu um erro próprio entre etapas.
3. **Antecipou por escrito a inversão que a rodada 4 confirmou.** Com o denominador quebrado, escreveu: *"Se o site for, digamos, metade do faturamento, o Google já estaria em ~30% e o gatilho seria R-0054 — conclusão oposta."* Com o dado real, foi exatamente o que ocorreu.

## 1.4 O limite honesto — o que este piloto NÃO estabelece

> ⚠️ **Leia esta seção antes de citar qualquer número acima em contexto comercial.**

- **Não é teste de resistência à invenção.** O held-out **não foi aplicado** aqui — o ground truth é externo (uma conta viva). Nenhum número deste piloto é comparável aos de resistência dos PILOT-001 e 002.
- **Não é validação da metodologia do curso.** Prova que a Skill aplica a fonte com fidelidade, não que a fonte esteja certa.
- **Não é execução cega.** Eu montei os recortes e conduzi as quatro rodadas; um terceiro não reproduziu isso. **Curso único, conta única — N=1 nos dois lados.**
- **📏 A auditoria de PMax está formalmente incompleta:** 75,7% do gasto é opaco sem o script de R-0444. E a Skill continua **📣 `S3_EXECUTABLE`, `production_ready: false`**, por declaração dela própria.

---

# 2. FRENTE DE NEGÓCIO — dono: Alexandre

**Esta frente não precisa de mais nenhuma rodada da Skill.** Está decidida; o que falta é execução.

## 2.1 A conta é lucrativa pelo KPI que decide

**📏** CPA de R$125,40 contra break-even de R$1.266,93 — folga de 10,10×. Três de três campanhas aprovadas, em todos os cenários testados. Isso está resolvido e não muda com dado novo.

## 2.2 Os dois bloqueios que restam antes de escalar

Eram três. **R-0524 caiu** — exigia break-even CPA calculado, e agora ele existe. Restam dois, ambos com precedência textual na fonte:

| Regra | Precedência declarada na fonte | Condição na MTX |
|---|---|---|
| **R-0072** | *"Precede qualquer decisão de aumento de verba"* | **📏** Fundação ausente: sem branded search, sem branded shopping, sem Shopping padrão |
| **R-0092** | *"Precede a regra de aumento de orçamento"* | **📏** V&H **−73%** no período, sendo a campanha de melhor CPA da conta (82,17 contra 125,40 da conta) |

A fonte **não diz "não escale"** — diz *"estruturar a conta primeiro e escalar depois"* (R-0072) e *"corrigir o vazamento antes de aumentar mais o orçamento"* (R-0092). **É ordem de execução, não proibição.** O dinheiro está lá; a sequência é que está invertida.

```
estruturar (R-0072) → corrigir o vazamento da V&H (R-0092) → escalar (R-0527, R-0532)
```

**📏 Nenhum dos dois depende de dado que a MTX não tenha em mãos.**

## 2.3 A inversão do diagnóstico de canal

Este é o achado que mudou de direção quando o faturamento do site foi separado dos demais canais.

```
Google atribuído/mês = 172.730,01 ÷ 90 × 30 = R$ 57.576,67
```

| Denominador | Share | Regra que dispara | Diagnóstico |
|---|---|---|---|
| todos os canais — `57.576,67 ÷ 525.000` | **11,0%** | R-0032 | abaixo de 20–30% → ampliar o Google |
| **apenas o site** — `57.576,67 ÷ 149.892` | **38,4%** | **R-0054** | acima de 20–30% → **subperformance dos outros canais** |

R-0032 refere-se textualmente ao *dashboard de receita (Shopify / Triple Whale / Northbeam)* — dashboards de DTC, que medem o site. A leitura ancorada no texto é a do site, e ela dispara **R-0054**, cujo `do_not` é explícito: *"Não concluir que o problema é o Google estar sobreperformando."*

```
receita fora do site = 525.000 − 149.892 = R$ 375.108/mês  →  375.108 ÷ 525.000 = 71,4%
```

**📏 71,4% da receita da empresa não tem mídia paga identificada.**

> ⚠️ **METHOD_NOT_DEFINED.** A fonte cobre alocação **dentro** do Google Ads (R-0079: 80–90% em tráfego frio; R-0095: 3–8% em marca). Ela **não** define como distribuir verba **entre** site, Mercado Livre e balcão. O gatilho de R-0054 está registrado; o caminho não. Nem a Skill nem eu arbitramos isso.

**📣 Ressalva sobre os R$525.000:** valor declarado pelo dono, sem medição independente. Ele **corrigiu** o R$380.000 informado antes — e a correção piorou todas as proporções:

| Medida | fórmula | com 380k | **com 525k** |
|---|---|---|---|
| MER | `receita ÷ marketing` | 44,7 | **61,8** |
| Marketing / receita | `8.500 ÷ receita` | 2,24% | **1,62%** |
| Mídia Google / receita | `3.192,44 ÷ receita` | 0,92% | **0,61%** |

**📏 A empresa investe 0,61% da receita em mídia no Google.** R-0022 aplica-se integralmente: mensagem excelente com volume baixo → *"reconhecer que o gasto é insuficiente"*.

## 2.4 A ação de dois minutos que fecha três ressalvas

> ## **Abrir a tela das ações de conversão do Google Ads.**

Subiu de #8 para #3 nas recomendações — o maior movimento da reordenação — porque passou a resolver três coisas em vez de uma:

| O que fecha | Regra |
|---|---|
| A ambiguidade **48 compras vs 76,38 conversões** — única via | R-0130, R-0377 |
| A discrepância de **R$7.730** (4,5%), aberta desde a rodada 1 | R-0130 |
| Os **41 cliques em `mtx` com zero conversão** | R-0130, R-0113 |

Verificar quatro coisas na tela: **R-0377** (uma única ação primária), **R-0187** (purchase como *account default goal*), **R-0199** (add to cart, begin checkout e checkout page view como *secondary, observe only*), **R-0190** (janelas 90/30/30).

**Custo: uma tela.** É o item de melhor relação resultado/esforço em toda a auditoria.

## 2.5 As duas ações imediatas de marca

**📏 R$102,86 = 1,07% do custo da conta** — **piso, não medida**: os recortes trazem só as listas top-N de 24.795 linhas.

1. **Excluir `mtx imports` (R$30,47 / 1,00 conv) e `mtx importadora` (R$4,91 / 0) da VENDAS|PERF-MAX** — R-0498 é a **única regra da fonte com urgência declarada**: *"excluir o termo de marca imediatamente"*.
2. **Mover `mtx` (R$58,46 / 41 cliques / 0 conv) e `loja mtx` (R$9,02 / 5 / 0) para campanha de marca dedicada** — R-0078 prescreve campanha própria, **não** negativar e esquecer.

> ⚠️ **METHOD_NOT_DEFINED.** A fonte não define como tratar termo de marca simultaneamente obrigatório proteger (R-0073) e candidato a remoção por zero conversão (R-0393). Recomendação da Skill: `[mtx]` em exata sob monitoramento diário, decisão em 30 dias.

---

# 3. FRENTE DE PRODUTO — dono: o compilador

**Esta é a frente que decide se o Course-to-Skill vira ferramenta ou continua experimento.**

## 3.1 O piso de 411.658 tokens

**📏 Medido por `count_tokens` em `claude-opus-5`, o mesmo modelo da invocação:**

| medida | tokens |
|---|---|
| **bundle isolado — o piso** | **411.658** |
| overhead de mensagem mínima | 7 |
| payload da rodada 4 | 24.513 |
| invocação completa | 436.171 |

**Caracteres:** bundle 869.045 · system prompt montado 869.405 (`= 869.045 + 204 de preâmbulo + 156 de separadores`) · bytes 880.321.

> ⚠️ **Os números 415.478 e 424.427, que circularam nos relatórios anteriores como
> "custo da Skill", estavam errados de escopo.** Eram `input_tokens` de invocações
> inteiras — bundle **mais** o payload daquela rodada específica. **O número a citar
> é 411.658.**

**O que o piso implica:**

```
835 regras  ← curso de 3h50   → 411.658 tokens
regra por hora ≈ 835 ÷ 3,85 ≈ 217
curso de 20 h ≈ 217 × 20 ≈ 4.340 regras ≈ 5,2 × o bundle atual ≈ 2,1 M tokens
```

**📣 A projeção de 20 horas é extrapolação linear, não medição** — nada garante que a densidade se mantenha. Mas mesmo com folga generosa, **o bundle não caberia com margem em nenhuma janela de contexto de hoje.** E o custo é **fixo e independente da pergunta**: uma consulta de uma linha paga os mesmos 411.658 tokens que a auditoria completa.

## 3.2 A estrutura que não escala

| Sintoma | **📏 Medido** |
|---|---|
| DISPATCH ocupa quase todo o SKILL.md | **167 de 196 linhas = 85,2%** |
| Workflows de passo único | **40 de 158 = 25,3%** |
| Regras sem precedência declarada | **741 de 835 = 88,7%** |

Um quarto dos workflows tem um passo só — não são workflows, são regras com cerimônia em volta. E o `precedence: UNDEFINED` **já mordeu na primeira aplicação real**: R-0386 (*"nunca usar frase"*) contra R-0175/R-0338 (*"usar frase para variações comprovadas"*), sem nenhuma das duas declarar precedência.

> **Carregamento seletivo — só as regras da família roteada — deixou de ser
> otimização e passou a ser requisito de viabilidade.**

Uma coisa que **não** aconteceu, e registro porque previ o contrário: eu esperava que o DISPATCH ilegível contaminasse a aplicação. **Não contaminou.** A Skill roteou corretamente para WF-0022, WF-0002, WF-0105 e WF-0177. Errei na direção pessimista.

## 3.3 Os 10 casos cegos do PILOT-002

> ⚠️ **Correção de premissa, apurada em disco nesta sessão.** A formulação que vínhamos
> usando — *"o PILOT-002 nunca foi recompilado, os casos esperam uma Skill"* — **não
> confere.** `PILOT-002-v2/skill/` **existe**, com **📏 149 regras**, compilado em
> 2026-08-12 11:36, depois do commit do arnês evidência→Skill (`bdf4345`, 04:13 do
> mesmo dia).

**O que é verdade:** **📏 os 10 casos cegos BC-001 a BC-010 nunca foram executados contra ela.** Nenhum artefato de resultado existe em disco, nem no repo nem no Drive. Eles foram escritos e congelados **antes** de existir Skill — a regra de anterioridade em `heldout_blind_cases.py` — e continuam intactos nesse estado.

**A Skill existe. A execução é que falta** — a diferença entre "não temos o instrumento" e "temos o instrumento e não medimos". A segunda é muito mais barata: 10 casos contra 149 regras, ordem de grandeza menor que os 835 do PILOT-003.

**📏 Existe também material de PILOT-004 no Drive** (`00_SOURCE` a `03_SKILL`, de 13–14/08), posterior ao último commit e **fora do git**. Não foi tocado nesta sessão.

---

# 4. DÍVIDA TÉCNICA E RISCO

## 4.1 Já mordeu — o alias `claude-opus-5` mudou de comportamento

**📏 Medido nesta sessão.** Entre 12/08 e 27/08 o snapshot por trás do alias passou a **ligar pensamento estendido por conta própria** em prompts complexos, e esses tokens consomem o `max_tokens`.

**O que aconteceu:** a primeira execução da rodada 4 gastou os 32.000 tokens inteiros dentro de um bloco `thinking`, devolveu **zero texto** e **saiu com exit code 0**. O artefato de 0 byte passou por execução bem-sucedida.

```
prompt complexo, snapshot atual  → blocos: ['thinking', 'text']
thinking={'type':'disabled'}     → blocos: ['text']
```

**Consequências permanentes:**

- **📏 As etapas 1–3 do PILOT-003 não são reproduzíveis hoje com o mesmo comando.** Mesmo alias, comportamento diferente.
- **📏 Nenhum artefato das rodadas 1–3 registra qual snapshot atendeu.** Isso não é recuperável.

**Correção aplicada** (`p003_apply_step4.py`): `thinking={"type": "disabled"}` explícito, para preservar comparabilidade com as etapas anteriores; `blocos` e `model_resolvido` gravados no artefato; **exit code 1 se a resposta vier vazia**.

**Regra que fica:** *fixe o snapshot ou grave o `model` resolvido que a API devolve — o alias é uma variável de ambiente, não uma constante.*

## 4.2 Já mordeu — hash confirma, não reconstrói

A regra estava escrita desde 12/08 (`RULE-HASH-DOES-NOT-RECONSTRUCT.md`) e **mordeu de novo nesta sessão**, num lugar diferente do previsto.

**📏 O que se perdeu com o `/tmp` limpo em 14 dias:**

| artefato | recuperável? | como |
|---|---|---|
| `p003-recortes.json` | ✅ sim | reconstruído dos CSVs; confere com o relatório (1.099 termos / R$2.325,35; `mtx` a R$58,46) |
| respostas das rodadas 1 e 2 | ❌ **não** | perdidas em definitivo |
| resposta da rodada 3 | ✅ sim | é o corpo do `PILOT-003-ACCOUNT-AUDIT.md` |

O que salvou os recortes foi os CSVs de origem estarem no Drive. **O que salvou a rodada 3 foi ela ter virado documento.** As rodadas 1 e 2 não viraram, e não voltam.

**Correção aplicada:** artefatos agora em `_mirror/pilots/PILOT-003-v2/apply/`, dentro do git. Nada de intermediário volta para `/tmp`.

## 4.3 Ainda não mordeu — o ramo de revarredura nunca executou

**📏 Três pilotos, três portões satisfeitos na primeira passada** — cobertura 90,61% · 82,39% · 78,86% contra piso de 73,5%, **zero revarreduras**. O caminho de revarredura dirigida **nunca rodou sobre dados reais**: é código não exercitado no caminho crítico. O PILOT-003 foi o mais baixo e ainda ficou 5,36 pontos acima do piso. **O próximo curso mais difícil aciona esse ramo pela primeira vez, em produção.**

## 4.4 O padrão que mais apareceu — erro de escopo

**Três ocorrências, dois autores, mesma forma:** numerador de um escopo contra denominador de outro.

| # | Autor | O erro | Correto |
|---|---|---|---|
| 1 | a Skill | `9.586,54` em vez de `9.577,32` na soma do custo → ROAS 18,02, CPA 125,51 | **18,04 · 125,40** |
| 2 | Alexandre | R$3.598/conv usando 48 compras como denominador contra AOV do site | os dois divisores são legítimos; **a pergunta não fecha** |
| 3 | a Skill | `76,38 × 1.266,93 = 96.767` apresentado como gasto **mensal** | **📏 `÷ 90 × 30 = R$ 32.256/mês`** |

O caso 1 é o mesmo mecanismo do ROAS 34,19 já documentado (coluna da campanha contra total da conta). O caso 3 é **regressão**: na rodada 3 a Skill fez o cálculo análogo no ROAS **corretamente** (`172.730,01 ÷ 2,0 ÷ 90 × 30 = R$28.788/mês`).

> ### A guarda estrutural que falta
>
> Nos três casos existia um invariante interno ao próprio documento que teria pego o erro,
> e em nenhum ele foi verificado:
>
> - caso 1 — *"custo/conv confere em todas as linhas"*: a Skill **estabeleceu essa disciplina**, verificou as linhas e **não verificou o total**;
> - caso 3 — a folga de escala **tem de ser idêntica** à folga de CPA. A Skill publicou `10,10×` e, três parágrafos depois, `~30×`. **O documento se contradiz sozinho.**
>
> **A guarda não é "conferir contas". É exigir que toda razão declarada apareça duas
> vezes por caminhos diferentes e que as duas batam** — e falhar alto quando não batem.
> Nenhuma das três ocorrências sobreviveria a isso.

## 4.5 Defeito conhecido, não corrigido no artefato

O caso 3 acima está **publicado com o número errado** em `p003-apply4.md`, §5 item 13:
mídia sustentável ao BE CPA como `R$ 96.767/mês` (correto: **R$ 32.256/mês**) e folga
`~30×` (correto: **10,10×**); sob 48 compras, `R$ 60.813/mês · ~19×` (correto:
**R$ 20.271/mês · 6,35×**).

**Não corrigido de propósito.** O artefato é a saída verbatim da Skill e é evidência do
piloto; reescrevê-lo apagaria o defeito que o piloto serve para detectar. Mesmo
tratamento no `PILOT-003-ACCOUNT-AUDIT.md`: corpo intacto, nota de correção no topo
amarrada por `sha256`, `git blob` e commit ao `FINAL-REPORT`.

**⚠️ Nenhum veredito muda por causa desses defeitos** — a folga correta de 10,10×
continua larga. Mas **não cite os números publicados; cite os corrigidos.**

---

# 5. ESTADO DOS ARQUIVOS

Tudo sob `_mirror/`, exceto os scripts na raiz.

| caminho | o que é |
|---|---|
| `docs/PILOT-003-FINAL-REPORT.md` | os quatro critérios, reconciliação do ROAS |
| `docs/PILOT-003-ACCOUNT-AUDIT.md` | auditoria da rodada 3 + nota de correção no topo |
| `pilots/PILOT-003-v2/skill/` | bundle: 835 regras · 601 passos · 158 workflows |
| `pilots/PILOT-003-v2/apply/p003-apply4.md` | saída da rodada 4 (38.193 chars) |
| `pilots/PILOT-003-v2/apply/p003-medicao-tokens.json` | a medição de 411.658 |
| `p003_apply_step4.py` · `heldout_blind_cases.py` | harness da rodada 4 · os 10 casos congelados |

**Fora do git:** material de PILOT-004 no Drive (13–14/08).

## Se você só tem cinco minutos

1. **Negócio:** abra a tela das ações de conversão (§2.4). Fecha três ressalvas, custa uma tela.
2. **Produto:** carregamento seletivo (§3.2). Sem ele não há curso de 20 horas.
3. **Barato e parado:** rodar os 10 casos cegos contra a Skill do PILOT-002, que **já existe** (§3.3).
