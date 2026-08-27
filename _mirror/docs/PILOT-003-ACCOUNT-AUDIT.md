# PILOT-003 — AUDITORIA DA CONTA MTX PELA SKILL COMPILADA

**Skill:** PILOT-003-SKILL · 835 regras · bundle 869 KB · 424.427 tokens de entrada
**Conta:** MTX IMPORTS - ATUAL 24/25 (170-554-4703) · 15/05-12/08/2026
**Protocolo:** a Skill decidiu o recorte; ambiguidade foi reportada e nao resolvida;
todo pedido inatendivel foi registrado. Nenhum conhecimento de Google Ads meu entrou.

---

> ## ⚠️ NOTA DE CORREÇÃO — anexada em 2026-08-27, corpo não reescrito
>
> O corpo abaixo carrega um erro aritmético **de uma única origem**: a soma do custo
> da conta. Todas as parcelas citadas estão certas; a soma delas não. O defeito está
> documentado em `PILOT-003-FINAL-REPORT.md`, seção *Reconciliação do ROAS*:
>
> | amarra | valor |
> |---|---|
> | sha256 do FINAL-REPORT | `cf1124bd3bd751eaca24cf15278081e7fe5118f64d817c83ee7bb1a645ea3d8c` |
> | git blob | `87f49718bdcc6c52ffece93b8439eb56cff5ae0b` |
> | commit que versionou os dois | `ed00f8b4aa3c375ce0619fd570dd02cae6d4329b` |
>
> ### O que está errado e o que é correto
>
> | # | grandeza | no corpo | **correto** | origem do correto |
> |---|---|---|---|---|
> | 1 | custo total da conta | 9.586,54 | **9.577,32** | linha `Total: Conta`, coluna `Custo` |
> | 2 | ROAS da conta | 18,02 | **18,04** | linha `Total: Conta`, coluna `Valor conv. / custo` |
> | 3 | reconciliação mensal §5.1 | R$ 3.195,51/mês | **R$ 3.192,44/mês** | 9.577,32 ÷ 90 × 30 |
> | 4 | múltiplo do break-even | 9,0× | **9,02×** | 18,04 ÷ 2,0 |
> | 5 | CPA da conta (§1.3) | R$ 125,51 | **R$ 125,40** | linha `Total: Conta`, coluna `Custo / conv.` |
>
> O item **5 não constava do defeito registrado no FINAL-REPORT** — foi encontrado ao
> anexar esta nota, tem a mesma origem única (9.586,54 ÷ 76,38 = 125,51; o CSV traz
> 125,40) e arrasta o AOV mínimo da conta na tabela §1.3 de R$ 251,02 para
> **R$ 250,80**. Os CPAs por campanha (193,10 · 157,98 · 82,17) são verbatim do CSV
> e **não** são afetados.
>
> ### O veredito não muda
>
> A diferença de custo é de **R$ 9,22 em R$ 9.577,32** — 0,096%. O múltiplo do
> break-even vai de 9,0× para 9,02×, a queda de valor que ainda sobreviveria vai de
> −88,9% para −88,91%, e a margem de segurança sobre a discrepância de R$7.730
> permanece em ~20×. **Nenhuma conclusão de §2, §3, §4, §5, §8 ou §9 se altera em
> direção**, e nenhuma muda de lado em relação a qualquer limiar da fonte.
>
> ### Por que nota e não reescrita
>
> O corpo é o output verbatim da Skill compilada e é *evidência do piloto*. Reescrevê-lo
> apagaria o defeito que o piloto foi feito para detectar — a Skill estabeleceu a
> disciplina que pegaria isso (*"custo/conv confere em todas as linhas"*), verificou as
> linhas e não verificou o total. Uma auditoria nova, com dados novos, está em curso;
> ela substitui este documento, não o corrige.

---

---

# Auditoria MTX — conclusão com os dados 1, 5, 6, 11, 12 e 14

---

## 0. O que mudou com os novos dados

| Dado | Efeito |
|---|---|
| **1 — margem 50%** | Destrava **R-0133 / WF-0133** (break-even ROAS). **Não** destrava R-0134 (break-even CPA). |
| **5 — termos de marca** | Destrava **R-0078, R-0353, R-0438, R-0446, R-0498**. Muda a leitura do maior termo de desperdício da conta. |
| **6 — V&H é distribuição exclusiva** | Reclassifica a campanha "Conversão Vance & Hines". Desativa a aplicação de **R-0074**. Ativa **R-0033**. |
| **11 — R$380k/mês, R$8.500 mkt** | Destrava **R-0522 (MER)**, **R-0022**, **R-0032**. É o achado estratégico central. |
| **12 — export sem certeza sobre REMOVIDAS** | Restringe o escopo da conclusão 3.3 da auditoria anterior. |
| **14 — lucro no primeiro pedido** | Fixa **R-0124 → R-0126** como regime operacional. Desativa R-0125. |

**O que os novos dados NÃO mudaram:** as conclusões 3.1 a 3.8 da auditoria anterior permanecem todas de pé. Nenhuma foi revertida pela margem. Explico em 2.3 por que a lucratividade confirmada não desbloqueia a escala.

---

## 1. Unit economics — o que foi possível calcular

### 1.1 Break-even ROAS — **CALCULADO** — R-0133 / WF-0133 / S-0421

Fórmula da fonte (EV-1616): `100 ÷ % de margem bruta`.

**Ressalva de substituição declarada:** o dono informou **margem de contribuição** (50%: após produto, frete e taxa de pagamento), não margem bruta. A fonte, em EV-1621, define margem bruta como o que resta após **COGS e entrega do produto** — não menciona taxa de pagamento. Logo:

> margem de contribuição (50%) ≤ margem bruta pela definição da fonte
> ⇒ `100 ÷ 50 = 2,0` **≥** o break-even ROAS "verdadeiro" pela definição da fonte

A substituição é **conservadora na direção certa**. Conclusões do tipo "ROAS > 2,0 ⇒ acima do break-even" são seguras. Não arbitrei nada.

> ### **BREAK-EVEN ROAS = 2,0**

### 1.2 Break-even CPA — **BLOQUEADO** — R-0134 / WF-0134

Fórmula da fonte (EV-1620): `AOV × % margem bruta − custos fixos de COGS`.

| Componente | Status |
|---|---|
| % margem | 50% ✅ |
| **AOV** | ❌ **UNDEFINED** — não informado |
| **Custos fixos de COGS por pedido** | ❌ **UNDEFINED** — o dono declarou explicitamente que não separou |

**Não substituo AOV por "valor por conversão" (R$2.261,46).** Esse número é valor atribuído ÷ conversões fracionárias sob atribuição data-driven (R-0191), não valor de pedido. Usá-lo seria arbitrar.

**Consequência hierárquica — R-0523:** a fonte declara o break-even CPA como o KPI **mais importante**, com o break-even ROAS sendo "apenas informativo/interessante", e `precedence: "Break-even CPA prevalece sobre break-even ROAS; ROAS é irrelevante em comparação"`. Portanto: **o KPI primário da metodologia está indisponível.** Tudo que segue baseado em ROAS opera no KPI que a própria fonte classifica como secundário.

### 1.3 O que dá para fazer sem AOV — inversão da fórmula

Em vez de arbitrar AOV, **resolvo a fórmula para ele**. Condição de aprovação: `CPA_observado ≤ 0,50 × AOV − F`, onde F = custo fixo de COGS por pedido.

⇒ `AOV mínimo = 2 × (CPA_observado + F)`

| Campanha | CPA observado | **AOV mínimo para passar** (F = 0) | Ajuste |
|---|---|---|---|
| VENDAS\|PERF-MAX | R$ 193,10 | **R$ 386,20** | + 2F |
| VENDAS\|ATUAL | R$ 157,98 | **R$ 315,96** | + 2F |
| Conversão V&H | R$ 82,17 | **R$ 164,34** | + 2F |
| **Conta** | **R$ 125,51** | **R$ 251,02** | + 2F |

**Isto é o que falta para fechar a auditoria de CPA, e o dono responde em uma linha:** qual o AOV do site e qual o custo fixo por pedido (embalagem, picking, etiqueta). Sem isso, R-0134 fica em **UNDEFINED** e **R-0524** (origin: GENUINE_INFERENCE) bloqueia escala por um terceiro caminho independente.

---

## 2. Veredito por campanha contra o break-even

### 2.1 Todas as três campanhas estão acima do break-even ROAS — R-0526

| Campanha | ROAS | BE ROAS | Múltiplo | Valor necessário p/ BE | **Queda de valor que ainda sobreviveria** |
|---|---|---|---|---|---|
| VENDAS\|PERF-MAX | 7,62 | 2,0 | **3,8×** | R$ 5.599,78 | **−73,7%** |
| VENDAS\|ATUAL | 34,19 | 2,0 | **17,1×** | R$ 7.056,64 | **−94,2%** |
| Conversão V&H | 9,47 | 2,0 | **4,7×** | R$ 6.498,22 | **−78,9%** |
| **Conta** | **18,02** | **2,0** | **9,0×** | **R$ 19.173,08** | **−88,9%** |

### 2.2 A ressalva de R$7.730 não derruba a conclusão — quantificado

A ressalva aberta (R-0130: não presumir que o rastreamento herdado está correto) permanece **formalmente não resolvida** — ninguém viu a tela das ações de conversão, e R-0377 (uma única conversão primária) / R-0199 (add-to-cart e begin-checkout como *secondary observe only*) seguem **não verificados**.

Mas dá para medir o tamanho do erro necessário para inverter o veredito:

- Discrepância conhecida: **4,5%** (R$7.730 em R$172.730)
- Erro necessário para a conta cair ao break-even: **88,9%**
- Margem de segurança: **~20× a discrepância observada**

Mesmo no cenário mais pessimista compatível com R-0130 — todas as quatro ações de conversão (purchase, add to cart, begin checkout, page view) marcadas como primárias, inflando a contagem — seria preciso que **89% do valor reportado fosse espúrio**. A conclusão "acima do break-even ROAS" é **robusta à incerteza de medição conhecida**. A verificação segue obrigatória (R-0130), mas não é pré-requisito para as decisões de 3 e 4 abaixo.

### 2.3 E mesmo assim: **não aumentar orçamento agora** — R-0072 e R-0092, ambas com precedência declarada

Este é o ponto que a margem **não** mudou, e é importante que fique explícito.

R-0526 diz: ROAS consistentemente acima do break-even → aumentar orçamento. R-0519 vai além: campanha muito abaixo do break-even e claramente escalável → `autonomy: "Obrigatório escalar"`. R-0069: ROAS alto demais → escalar. Três regras apontando para escala.

Contra elas, **três bloqueios com precedência textual na fonte**:

| Regra | Precedência declarada | Condição na MTX |
|---|---|---|
| **R-0072** | *"Precede qualquer decisão de aumento de verba e a adição de YouTube/cold search"* | Fundação ausente (§3.3 anterior): sem branded search, sem branded shopping, sem Shopping padrão |
| **R-0092** | *"Precede a regra de aumento de orçamento"* | Desempenho em queda (impressões −37%, conversões −18%, valor −25%, V&H −73%) |
| **R-0524** | Calcular break-even CPA **antes** de escalar | AOV e F em UNDEFINED |

**Veredito:** a fonte não diz "não escale" — R-0072 diz `"estruturar a conta primeiro e escalar depois"` e R-0092 diz `"corrigir o vazamento antes de aumentar mais o orçamento"`. É uma **ordem de execução**, não uma proibição. O dinheiro está lá para ser gasto; a sequência é que está invertida.

---

## 3. Contaminação de marca — o achado que os termos de marca liberaram

### 3.1 Marca está dentro das três campanhas de prospecção — R-0078 / R-0353 / R-0438 / R-0446

Varredura dos recortes contra a lista de marca (`mtx imports`, `mtx`, `mtximports`, `mtx motoparts`, `MTX Parts`, `mtximports.com.br`, `mtxparts.com.br`):

| Termo | Campanha | Custo | Cliques | Conv. | Regra violada |
|---|---|---|---|---|---|
| **mtx** | VENDAS\|ATUAL | R$ 58,46 | 41 | **0** | R-0078, R-0353 |
| **mtx imports** | VENDAS\|PERF-MAX | R$ 30,47 | — | 1,00 | **R-0498, R-0446, R-0438** |
| loja mtx | Conversão V&H | R$ 9,02 | 5 | 0 | R-0078, R-0353 |
| mtx importadora | VENDAS\|PERF-MAX | R$ 4,91 | — | 0 | R-0446, R-0438 |
| **Identificado** | | **R$ 102,86** | | **1,00** | = **1,07% do custo da conta** |

> ⚠️ **R$102,86 é piso, não medida.** Os recortes B, C e D contêm apenas as listas top-N. O relatório completo tem 24.795 linhas. A contaminação real de marca é **≥ 1,07%** do gasto, e não posso estimar quanto maior sem o export completo filtrado pelos sete termos de marca.

### 3.2 O maior termo de desperdício da conta é o nome da marca

**"mtx" — R$58,46, 41 cliques, ZERO conversões.** É o item nº 1 da lista de desperdício (C_desperdicio) e agora sabe-se que é termo de marca.

Duas leituras, ambas graves, e não tenho dado para escolher entre elas:

1. **Rastreamento quebrado** — 41 cliques do segmento de intenção mais alta que existe (R-0318, R-0320, R-0326) sem uma única conversão registrada é anômalo. Reforça R-0130.
2. **"mtx" em ampla está captando tráfego alheio** — a string tem outros donos no mundo. Sem os termos de pesquisa completos (o recorte G veio com a coluna de palavra-chave quebrada), não dá para confirmar.

**METHOD_NOT_DEFINED:** a fonte não define como tratar um termo de marca que é simultaneamente (a) obrigatório proteger sob R-0073/R-0341 e (b) candidato a remoção sob R-0393 por zero conversão com volume de cliques. R-0337 diz que o conjunto exato de marca "basta"; R-0393 diz para remover. Não arbitro. **Lançar `[mtx]` em exata dentro da campanha de marca sob monitoramento diário**, com decisão em 30 dias.

### 3.3 R-0498 é a única ação com urgência declarada na fonte

> **R-0498 — Eliminar imediatamente conversões de marca vindas pelos search terms**
> Trigger: identificação de conversões de marca nos search terms da PMAX. Action: **excluir o termo de marca imediatamente.**

"mtx imports" está com **1,00 conversão** dentro da VENDAS|PERF-MAX. **R-0499** define o critério de conclusão: marca só está totalmente excluída quando **não há nenhum termo de marca na lista de convertedores**. A conta **falha** esse critério hoje.

Consequências em cadeia:
- **R-0080** (GENUINE_INFERENCE): ROAS 18,02 sem segmentação → tratar como **possivelmente inflado por tráfego de marca**. Condição plenamente satisfeita.
- **R-0797**: proibido reivindicar conversões de marca como tráfego frio. Hoje, por construção, é o que a conta faz.
- **R-0356**: risco de lances altíssimos em termos de marca sob smart bidding embutido em prospecção. **Estratégias de lance de VENDAS|ATUAL e V&H = UNDEFINED** (pedido 3/4 não atendido) → não posso avaliar a magnitude.

---

## 4. Vance & Hines — reclassificação (dado 6)

### 4.1 O que a resposta 6 corrige

V&H é **marca distribuída com exclusividade pela MTX no Brasil desde 2011**. Isso significa:

- **R-0074 NÃO se aplica.** A campanha "Conversão Vance & Hines" **não** é campanha de concorrente. A proibição de `do_not: "Rodar campanhas competitivas em campanha própria"` está fora de escopo aqui. Registro isso porque era uma leitura possível e errada.
- **R-0227 se aplica ao feed:** produto de revenda → campo `brand` = Vance & Hines, não MTX.
- **R-0033 se aplica com força:** *trigger* "existe demanda de busca pelo produto ou pela marca"; *action* "ativar Google Ads para garantir que quem busca compre da marca, e não de concorrente, Amazon ou revendedor". Como a MTX detém exclusividade contratual no Brasil, **toda busca por V&H no Brasil pertence à MTX por contrato**, e qualquer clique perdido para marketplace ou revendedor paralelo é receita que já era da empresa.

### 4.2 O que a fonte NÃO resolve

> **METHOD_NOT_DEFINED — classificação de marca de terceiro sob distribuição exclusiva.**
>
> A fonte segmenta o mundo em *branded* (nome próprio da marca — R-0073, R-0315, R-0341) e *non-branded / cold* (R-0079: 80–90% do orçamento). Ela **não define** onde entra a marca de um terceiro que o anunciante distribui com exclusividade.
>
> Isso importa materialmente: se V&H contar como *branded*, a campanha cai sob o teto de **R-0095 (3–8%, máx. 10%)** e a conta está gastando **33,9%** — violação grosseira. Se contar como *non-branded product-level* (**R-0017**: "começar a maior parte do marketing no Google pelas buscas em nível de produto, por serem as mais fáceis de converter"), 33,9% é alocação correta e até conservadora.
>
> **Não arbitro.** Registro que a classificação decide se a maior campanha em conversões da conta está em conformidade ou em violação de teto.

### 4.3 Desempenho da V&H — o que é decidível

| Métrica | V&H | Conta | Leitura |
|---|---|---|---|
| CPA | **R$ 82,17** | R$ 125,51 | **melhor CPA da conta** |
| Conv./dia | **0,439** | 0,849 | **52% de todas as conversões** |
| Valor/conv. | R$ 778,50 | R$ 2.261,46 | menor ticket atribuído |
| ROAS | 9,47 | 18,02 | 4,7× break-even |
| Variação no período | **−73%** | — | **maior queda da conta** |

**R-0092** dispara aqui com nome e sobrenome: a campanha de melhor CPA da conta caiu 73%. Esse é *o* vazamento cuja correção precede o aumento de orçamento. **Causa raiz = UNDEFINED** — exigiria parcela de impressão (pedido 2), relatório de produtos (pedido 9) ou o script de PMax (pedido 13), nenhum atendido.

---

## 5. A escala da operação — o achado estratégico (dado 11)

### 5.1 MER — R-0522 / S-0418 / R-0013

| Medida | Valor |
|---|---|
| Receita mensal (site + ML + balcão) | R$ 380.000 |
| Marketing total/mês | R$ 8.500 |
| **MER** | **44,7** |
| Marketing como % da receita | **2,24%** |
| Mídia Google como % da receita | **0,92%** |

**Reconciliação de custo:** R$9.586,54 ÷ 90 dias × 30 = **R$3.195,51/mês** vs R$3.500 declarados. Desvio de 8,7%, dentro de variação normal. **O lado do custo bate.** Isso corrobora a integridade do CSV no campo custo — que já era o campo que fechava entre CSV e telas.

### 5.2 A leitura correta de um MER de 44,7 — R-0022

R-0522 diz que MER alto indica esforços sustentáveis e eficientes. Verdade, mas incompleta. **R-0013** define o marketing efficiency ratio como a única métrica que importa; **R-0022** define o que fazer quando ele é alto demais:

> **R-0022** — trigger: "Mensagem de marketing avaliada como excelente e volume de tráfego baixo"; condition: "Mensagem ótima combinada com volume baixo (gasto insuficiente)"; action: **"Reconhecer que o gasto é insuficiente e que o crescimento está limitado nesse teto; aumentar o volume/gasto"**; do_not: *"Não manter volume baixo e esperar crescimento além do teto."*

**MER 44,7 com 2,24% de investimento em marketing não é uma conta eficiente. É uma empresa que quase não faz marketing.** A eficiência é artefato do volume mínimo.

**R-0005** (fórmula da escala): `mensagem × volume = crescimento`. Mensagem: ROAS 9× break-even. Volume: 0,92% da receita. **O fator limitante é inequivocamente o volume.**

### 5.3 Dimensionamento do espaço não explorado — R-0058 / R-0126

Sob **R-0126** (regime escolhido — lucro no primeiro pedido), o limite operacional é: **não ultrapassar o break-even**. Isso significa que a conta pode deixar o ROAS cair de 18,02 até 2,0 **e continuar cumprindo a instrução do dono**.

**R-0058** diz exatamente isso: *"escalar até o ponto em que a aquisição fica em break even ou levemente lucrativa na primeira compra, em vez de perseguir ROAS alto isoladamente"*, com `do_not: "Não focar em ROAS alto isoladamente"`.

Para dimensionar (**não é previsão** — a fonte não prescreve modelagem de retornos decrescentes, e eles existem): ao ROAS de break-even, o mesmo valor de conversão sustentaria **R$28.788/mês de mídia** contra R$3.195/mês hoje. **A folga nominal é de ~9×.** O caminho até lá é regido por **R-0532** (incrementos de 10–20%, `do_not: "Não fazer aumentos bruscos"`) e **R-0091** (escalar em etapas conforme estabilidade dos KPIs) — não por um salto.

### 5.4 Diagnóstico de share — R-0032, com denominador quebrado

Google atribuído: R$172.730 ÷ 90 × 30 = **R$57.577/mês** = **15,2% de R$380.000**.

**R-0032** dispara: abaixo de 20–30% → espaço não explorado, ampliar uso do Google.

> ⚠️ **Denominador UNDEFINED.** R-0032 refere-se ao dashboard de receita (Shopify/Triple Whale/Northbeam) — dashboards de DTC. Os R$380.000 incluem **Mercado Livre e balcão**. A receita apenas do site não foi informada.
>
> Se o site for, digamos, metade do faturamento, o Google já estaria em ~30% e o gatilho seria **R-0054** (Google acima de 20–30% → diagnosticar **subperformance dos outros canais**, não sobreperformance do Google) — conclusão oposta.
>
> **Não arbitro a divisão.** Falta: receita mensal apenas do site.

### 5.5 Mercado Livre — fora de escopo, mas registrado

A existência de canal Mercado Livre é diretamente relevante a **R-0033** (`do_not: "Não deixar a busca de marca/produto sem cobertura no Google"` — proteger contra Amazon, revendedores e concorrentes). Com V&H exclusiva e sem campanha de marca ativa, buscas por "vance hines" e por "mtx" no Google podem estar sendo capturadas por listagens de marketplace — inclusive as da própria MTX, com margem inferior à do site. **Não tenho dado de SERP para confirmar** e a fonte não cobre canibalização entre site próprio e marketplace próprio → fora de escopo desta Skill.

---

## 6. Limitação imposta pelo dado 12

**Escopo restrito, conforme instruído.** A conclusão §3.3 da auditoria anterior ("nenhuma campanha de marca operou no período") passa a ser enunciada assim:

> **Válido com certeza para campanhas ATIVAS e PAUSADAS:** o relatório de termos de pesquisa cobre o período e contém exatamente três campanhas em 24.795 linhas.
>
> **Não excluído:** uma campanha de marca REMOVIDA antes ou durante o período, caso o relatório de termos tenha herdado filtro que suprime itens removidos.

**Isso não altera nenhuma conclusão operacional.** R-0073 exige campanha de marca **em operação** protegendo o termo. Campanha removida ou pausada é funcionalmente idêntica a campanha inexistente para efeito de proteção de marca. E os dados de §3.1 provam positivamente que tráfego de marca está sendo servido pelas campanhas de prospecção — o que só ocorre se não há campanha de marca capturando-o.

---

## 7. O que continua bloqueado

| # | Pedido não atendido | Regra/workflow que fica inexecutável |
|---|---|---|
| 2 | Parcela de impressão | **R-0128** — a fonte ordena as métricas como `impression share > CPC > CTR > taxa de conversão > nº de conversões`. **A métrica de prioridade nº 1 da metodologia está ausente.** Também bloqueia R-0089 (alvo 50–60%), R-0127 (diagnóstico por IS baixo), R-0343/R-0365 (ajuste de lance por IS) |
| 3, 4 | Estratégias de lance e orçamentos por campanha | R-0084, R-0150, R-0151, R-0152, R-0356, R-0364, R-0534–R-0537 |
| 7, 8 | Tela de ações de conversão / GMC | **R-0130 permanece sem resolução**; R-0377, R-0199, R-0187, R-0192. **Status do GMC = UNDEFINED → R-0433 (Shopping obrigatório) é inexecutável até verificar** |
| 9 | Relatório de produtos | R-0094, R-0460–R-0464, R-0504, WF-0116, WF-0123, WF-0124 |
| 10 | Assets | R-0505, R-0125, WF-0125 |
| 13 | Script de PMax | **R-0444** — `do_not: "Depender apenas dos recursos nativos de insight do Google"`. **75,7% do gasto da PMax permanece opaco.** A auditoria de PMax está formalmente incompleta |
| — | Landing pages / URLs | Recorte I corrompido. R-0115, R-0400, R-0508–R-0514, WF-0114, WF-0129. **Único item recuperável com re-export, sem novo dado do cliente** |
| — | Atribuição de terceiros | **R-0443** — Triple Whale/Northbeam como fonte da verdade. Ausente. Com três canais de venda (site + ML + balcão), o risco de EV-1368 (PMax reivindicando vendas de outros canais) é **real e não mensurável** |
| — | CPA de novo cliente | **R-0521** — *"o KPI mais importante que você deveria acompanhar sempre"*. Ausente. **R-0090** (aumento mensal condicionado a aquisição estável) é inexecutável |

---

## 8. Recomendações — da mais específica à mais genérica

---

### **1. Excluir hoje `mtx imports` e `mtx importadora` da VENDAS|PERF-MAX**
**R-0498** (única regra da fonte com urgência declarada: *"excluir o termo de marca imediatamente"*), **R-0446**, **R-0438**.
Valores: R$30,47 / 1,00 conversão e R$4,91 / 0. Critério de conclusão em **R-0499**: nenhum termo de marca na lista de convertedores da PMax.
Caminho: campanha PMax → Search themes / exclusões → adicionar os 7 termos de marca como exclusão de marca.

### **2. Retirar `mtx` (R$58,46 / 41 cliques / 0 conv) e `loja mtx` (R$9,02 / 5 cliques / 0 conv) das campanhas de prospecção**
**R-0078** (`do_not: "Manter termos de marca dentro da campanha de prospecção"`, `do_not: "Desperdiçar budget em pessoas que iriam converter de qualquer forma"`), **R-0353**.
**A ação é mover para campanha de marca dedicada, não negativar e esquecer** — R-0078 prescreve segmentação em campanha própria com orçamento próprio.

### **3. Criar a campanha de busca de marca — WF-0094 / WF-0095**
**R-0073** (*"primeiro elemento fundacional"*), **R-0341**, **R-0316** (começar cedo para o Google reconhecer o dono oficial e conceder ad rank superior).

| Parâmetro | Valor | Regra |
|---|---|---|
| Tipo / objetivo | Search / Sales | S-0268, S-0269 |
| Ação de conversão | **apenas** purchase | S-0268, R-0377 |
| Estratégia de lance | Target Impression Share → **absolute top of page**, alvo **95%** | **R-0328, R-0346, S-0271** |
| Proibido | conversões, valor de conversão, maximizar conversões | **R-0330** |
| Redes | Search apenas, Display **off** | S-0273 |
| Localização | Brasil, **"presença"** — nunca "presença ou interesse" | **R-0334**, S-0274 |
| Palavras-chave | **exata apenas**: `[mtx imports]` `[mtx]` `[mtximports]` `[mtx motoparts]` `[mtx parts]` `[mtximports.com.br]` `[mtxparts.com.br]` | **R-0337** |
| Otimizar p/ novos clientes | **OFF** | **R-0332** |
| Exclusão de marca | nenhuma | **R-0336** |
| Programação de anúncios | nenhuma | **R-0335** |
| Excluir lista de clientes | sim (export Shopify) | **R-0367**, WF-0102 |
| Anúncio | "MTX Imports — Site Oficial" + oferta *no-brainer* + sitelinks para coleções/bestsellers | **R-0342, R-0310, R-0312** |

**Orçamento:** R-0340 fixa **US$25/dia** como teto justificado por *"a campanha de marca nunca gasta todo esse valor"* — a fonte **não define conversão cambial** (UNDEFINED). O limite que efetivamente vincula aqui é **R-0095**: **3–8% do investimento mensal = R$105–280/mês**, teto duro 10% = R$350/mês, sobre os R$3.500 declarados.

**Ponto de atenção declarado:** `[mtx]` já demonstrou 41 cliques com zero conversão. Lançar sob monitoramento diário, decisão em 30 dias (ver METHOD_NOT_DEFINED em §3.2).

### **4. Verificar o Google Merchant Center antes de qualquer campanha de Shopping**
**Status = UNDEFINED.** Sem GMC saudável não existe nem Shopping de marca nem Shopping padrão — ou seja, **duas das três peças fundacionais dependem deste único item**.
**R-0237** (checklist proativo de 34 itens, `do_not: "Não esperar um problema/suspensão para agir"`), **WF-0069**. Itens de maior risco para distribuidor de peças importadas: **R-0207** (política de devolução espelhada exatamente), **R-0206** (envio em modo manual no GMC, não sincronizado com Shopify), **R-0235** (`do_not: nunca editar preço/disponibilidade dentro do GMC`), **R-0230** (GTIN — crítico em peças com código de barras de fabricante), **R-0254** (envio sincronizado).

### **5. Subir Shopping padrão — a maior lacuna de receita da conta**
**R-0433** (*"Estar presente em shopping"* — obrigatório para e-commerce), **R-0018** e **R-0037**: shopping representa **60–80% de todo o volume de Google Ads em e-commerce** e é *"de onde vem a maior parte da receita gerada em e-commerce no Google Ads"*.

**Tradução direta:** a MTX opera hoje sobre **20–40% do canal**. Um distribuidor de peças com SKU, código de barras e catálogo é o caso de uso canônico de Shopping. **R-0041 / R-0138 / R-0542**: combinar PMax com standard shopping para cobrir integralmente o placement.

### **6. Subir Shopping de marca — WF-0099**
**R-0349** (toda marca roda branded shopping; o custo é *"um dos custos de fazer negócio no Google Ads"*), **R-0350** (ocupar o máximo acima da dobra), **R-0347/R-0348** (excluir **todos** os termos não-marca), **R-0359** Manual CPC, **R-0360** prioridade alta, **R-0361** presença apenas, **R-0364** (`do_not: "Automatizar os lances em campanhas de branding — complete no"`).
Depende de 4.

### **7. Fornecer AOV do site e custo fixo de COGS por pedido**
Destrava **R-0134 / WF-0134** e, com ele, **R-0523** (o KPI que a fonte declara primário) e **R-0524** (terceiro bloqueio à escala).
Limiar de decisão pronto na tabela §1.3: com F=0, a conta passa se **AOV ≥ R$251,02**; cada campanha tem seu próprio limiar. **Uma linha de resposta fecha o item.**

### **8. Abrir a tela das ações de conversão**
**R-0130** (`do_not: "Assumir que o rastreamento de conversão herdado está correto"` — *"a maioria das agências e freelancers erra essa configuração"*).
Verificar: **R-0377** (uma única primária), **R-0187** (purchase como account default goal), **R-0199** (add to cart, begin checkout e checkout page view como *secondary, observe only*), **R-0190** (janelas 90/30/30), **R-0191** (atribuição data-driven).
Resolve a ressalva dos R$7.730 e explica os 41 cliques em `mtx` sem conversão.

### **9. Instaurar a cadência operacional — WF-0020 / WF-0121**
**R-0104** (`do_not: "Não montar, publicar e esquecer a conta"`), **R-0496** (search term insights da PMax = *"a única tarefa a fazer todos os dias dentro da PMAX"*), **S-0046** (termos diariamente), **R-0106** (não testar é anti-padrão de mercado).
Estado atual: **180 linhas tocadas em 24.795 = 0,73%**, zero negativações em 90 dias. É set-and-forget caracterizado.

### **10. Promover os 7 termos convertedores para correspondência exata**
**R-0394**, **R-0174**, **R-0169**, WF-0105 (S-0321).
`fuel pak 4`, `harley davidson lojas`, `sissy bar road glide 2025`, `motobox`, `capacete harley davidson`, `vance & hines backslash 450`.
**R-0386**: o estado-alvo é mistura de exata e ampla; hoje são **100% ampla**. **R-0176**: broad fora de contexto de teste é proibido. A fase de descoberta está aberta há 90 dias sem nunca ter sido fechada.

### **11. Negativar os 1.099 termos com zero conversão (R$2.325,35 = 76,8% do gasto divulgado)**
**R-0393**, **R-0497**, **R-0171**.
> **METHOD_NOT_DEFINED reiterado:** a fonte não define piso de cliques ou gasto que separa "evidentemente não performando" (R-0393) de "volume insuficiente para concluir" (**R-0389**, que proíbe concluir a partir de gasto muito baixo). Não arbitro. Aplicação segura: começar pelos termos com maior custo E maior contagem de cliques, onde as duas regras não conflitam.

### **12. Re-exportar o relatório de landing pages (recorte I)**
Único item bloqueado por falha técnica minha, não por falta de dado do cliente. Destrava **R-0115** (congruência anúncio↔página), **R-0400**, **R-0508** a **R-0514**, WF-0114, WF-0129.
Relevante porque **R-0113** manda dirigir a investigação para a página quando as métricas de anúncio estão boas e a conversão não vem — exatamente o padrão de `mtx`.

### **13. Rodar o script de PMax de Mike Rhodes**
**R-0444** (*"padrão-ouro para analisar e auditar PMax"*, `do_not: "Depender apenas dos recursos nativos de insight do Google"`), WF-0120, WF-0137.
**75,7% do gasto da PMax é opaco.** Sem isso, a PMax não pode ser auditada — apenas desqualificada estruturalmente, o que já foi feito (§3.1 anterior: **R-0430** falha em gasto/dia e conversões/mês; **R-0044** falha no gate de 1 conv/dia por 30 dias).

### **14. Só depois de 1–6 e 9: escalar em incrementos de 10–20%**
**R-0532** (incrementos controlados; `do_not: "Não fazer aumentos bruscos"`), **R-0091** (etapas conforme estabilidade), **R-0136/R-0538** (cortar rápido, escalar devagar), **R-0090** (aumento mensal condicionado a aquisição de novos clientes e ROAS blended estáveis — **hoje inexecutável, R-0521 sem dado**).
Alvo de alocação: **80–90% em tráfego frio** (**R-0079**), marca em **3–8%** (**R-0095**).
Teto operacional sob **R-0126**: nunca ultrapassar o break-even — ROAS ≥ 2,0.

### **15. Genérico: o problema da MTX não é eficiência, é tamanho**
**R-0022**, **R-0005**, **R-0013**, **R-0058**.
ROAS a 9× o break-even com 0,92% da receita em mídia significa que a conta está sendo administrada para preservar um número, não para adquirir clientes. **R-0051** define o critério de sucesso: *"Avaliar o sucesso pela eficiência na aquisição de clientes... e não por receita ou vendas isoladas"*, com `do_not: "Não usar receita como critério de sucesso"`.

**R-0056** ressalva o limite: o Google é primariamente captura de demanda (**R-0055**) e depende das fontes que geram essa demanda. Com R$5.000/mês de agência produzindo conteúdo e vídeo, existe geração de demanda — mas **R-0052** vale: *"Não pensar em Google Ads como único motor de crescimento do negócio"*.

---

## 9. Veredito

**A conta é lucrativa e estruturalmente incompleta. Os dois fatos são independentes e ambos são verdadeiros.**

- **Lucrativa:** 18,02 de ROAS contra 2,0 de break-even, com margem de erro de 20× sobre a única discrepância de medição conhecida. **R-0526** aprovaria escala nas três campanhas.
- **Incompleta:** sem busca de marca, sem shopping de marca, sem shopping padrão — três elementos que **R-0073, R-0349 e R-0433** classificam como fundacionais ou obrigatórios. Marca vazando para dentro das três campanhas de prospecção. Zero negativações em 90 dias. PMax rodando 6× abaixo do seu gate de habilitação (**R-0044**).
- **Subdimensionada:** 0,92% da receita em mídia. **R-0022** aplica-se integralmente.

**A sequência é: estruturar (R-0072) → corrigir o vazamento da V&H (R-0092) → calcular o break-even CPA (R-0524) → escalar (R-0526, R-0519).** As três primeiras não são opcionais e nenhuma delas depende de dado que a MTX não tenha em mãos.

**Ressalvas que permanecem abertas ao fim desta auditoria:** R-0130 (configuração das ações de conversão não vista — quantificada e não determinante, mas não resolvida); R-0128 (parcela de impressão, métrica nº 1 da hierarquia da fonte, ausente); R-0444 (75,7% da PMax opaco); R-0443 (sem atribuição de terceiros, com três canais de venda concorrendo pelo crédito); R-0521 (CPA de novo cliente, KPI declarado como o mais importante, indisponível); classificação de V&H sob distribuição exclusiva (METHOD_NOT_DEFINED); denominador de receita para R-0032 (site vs. total).