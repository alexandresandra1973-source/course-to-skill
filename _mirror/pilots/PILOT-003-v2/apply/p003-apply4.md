# AUDITORIA MTX — RODADA 3

**Skill:** PILOT-003-SKILL · `S3_EXECUTABLE` · `production_ready: false`
**Conta:** MTX IMPORTS - ATUAL 24/25 (170-554-4703) · 15/05–12/08/2026
**Escopo:** Google Ads para e-commerce — dentro do escopo de RG-013-001. Nenhum guard de parada disparou.

---

## 0. Correções aritméticas aplicadas antes de qualquer cálculo

Adoto os valores corrigidos que você forneceu. Registro o que cada um altera:

| grandeza | valor anterior | **valor usado agora** |
|---|---|---|
| custo total da conta | 9.586,54 | **9.577,32** |
| ROAS da conta | 18,02 | **18,04** |
| CPA da conta | 125,51 | **125,40** |
| reconciliação mensal | 3.195,51/mês | **3.192,44/mês** |
| múltiplo do break-even ROAS | 9,0× | **9,02×** |

CPAs por campanha (193,10 · 157,98 · 82,17) **não afetados** — verbatim do CSV.

**Observação de integridade:** o recorte B que você reenviou ainda traz `Total: Conta · custo 9586,54 · cpa 125,52`. Estou usando os valores da sua nota (9.577,32 / 125,40), conforme instruído. O recorte não foi atualizado. Registro a divergência; não a arbitro além da instrução recebida.

---

## 1. ENTREGÁVEL 1 — BREAK-EVEN CPA

### 1.1 A fórmula e os componentes

**R-0134 / WF-0134 / S-0422** — fórmula da fonte (EV-1620, EV-1621):

> `break-even CPA = AOV × % margem bruta − custos fixos de COGS`

| Componente | Valor | Status |
|---|---|---|
| AOV | **R$ 2.533,86** | ✅ dado 7 |
| % margem | **50%** | ✅ dado 1 |
| Custos fixos de COGS/pedido | **R$ 0,00** | ✅ dado 7b — declarado ZERO explicitamente |

**Nenhum componente falta.** R-0134 está executável pela primeira vez nesta auditoria.

### 1.2 O cálculo

```
break-even CPA = 2.533,86 × 0,50 − 0,00
```

> ## **BREAK-EVEN CPA = R$ 1.266,93**

### 1.3 Ressalva de substituição — mantida e agora mais relevante

A ressalva de §1.1 da rodada anterior **permanece e se aplica igualmente aqui**: o dono informou **margem de contribuição** (após produto, frete e taxa de pagamento). A fonte, em EV-1621, define margem bruta como o que resta após **COGS e entrega do produto** — não menciona taxa de pagamento.

Direção do erro:

```
margem de contribuição (50%) ≤ margem bruta pela definição da fonte
⇒ 2.533,86 × 0,50 ≤ 2.533,86 × margem_bruta_verdadeira
⇒ R$ 1.266,93 é PISO do break-even CPA verdadeiro
```

A substituição é **conservadora na direção certa**. Conclusões do tipo "CPA observado ≤ 1.266,93 ⇒ abaixo do break-even" são **seguras** — o break-even verdadeiro só pode ser maior, nunca menor. Não arbitrei nada.

### 1.4 Estabilidade do AOV — verificação contra a variação declarada

Você informou que o AOV mensal de 2026 oscila entre R$ 2.030,88 e R$ 3.361,10. Testo os extremos:

| cenário | AOV | break-even CPA |
|---|---|---|
| pior mês | R$ 2.030,88 | **R$ 1.015,44** |
| janela auditada | R$ 2.533,86 | **R$ 1.266,93** |
| melhor mês | R$ 3.361,10 | **R$ 1.680,55** |

**Mesmo no pior mês de 2026**, o break-even CPA é R$ 1.015,44. Registro isso porque a fonte não prescreve teste de sensibilidade — é aritmética sobre dado que você forneceu, e serve para mostrar que o veredito de §2 não depende da escolha da janela.

### 1.5 Verificação cruzada — R-0133 e R-0134 devem concordar

A fonte fornece duas fórmulas independentes (EV-1616 e EV-1620) sobre a mesma margem. Testo a coerência:

```
break-even ROAS  = 100 ÷ 50 = 2,0
AOV ÷ BE-ROAS    = 2.533,86 ÷ 2,0 = R$ 1.266,93  ✅ idêntico
```

As duas fórmulas da fonte **fecham exatamente** quando F=0. Isso não é uma regra da fonte; é confirmação de que apliquei ambas corretamente sobre o mesmo insumo.

### 1.6 O que a rodada anterior previu e o dado confirmou

A tabela §1.3 da rodada anterior projetou os AOVs mínimos necessários. Confronto agora com o AOV real:

| Campanha | AOV mínimo projetado | AOV real | folga |
|---|---|---|---|
| VENDAS\|PERF-MAX | R$ 386,20 | R$ 2.533,86 | **6,56×** |
| VENDAS\|ATUAL | R$ 315,96 | R$ 2.533,86 | **8,02×** |
| Conversão V&H | R$ 164,34 | R$ 2.533,86 | **15,42×** |
| **Conta** | **R$ 250,80** | **R$ 2.533,86** | **10,10×** |

A inversão da fórmula feita na rodada anterior estava correta. O AOV real supera todos os limiares por uma ordem de grandeza.

---

## 2. ENTREGÁVEL 2 — VEREDITO POR CAMPANHA CONTRA O BREAK-EVEN CPA

**Regra aplicada:** R-0528 (`ROAS ou CPA cai para além do break-even → pausar, ajustar ou otimizar`) e R-0527 (`CPA em tendência abaixo do break-even → aumentar os lances para capturar mais volume`). Critério de aprovação: **CPA observado ≤ R$ 1.266,93**.

| Campanha | CPA observado | BE CPA | **Veredito** | Folga | Quanto o CPA poderia subir |
|---|---|---|---|---|---|
| VENDAS\|PERF-MAX | R$ 193,10 | R$ 1.266,93 | ✅ **PASSA** | **6,56×** | **+556%** |
| VENDAS\|ATUAL | R$ 157,98 | R$ 1.266,93 | ✅ **PASSA** | **8,02×** | **+702%** |
| Conversão V&H | R$ 82,17 | R$ 1.266,93 | ✅ **PASSA** | **15,42×** | **+1.442%** |
| **Conta** | **R$ 125,40** | **R$ 1.266,93** | ✅ **PASSA** | **10,10×** | **+910%** |

### 2.1 Robustez contra o pior mês

Sob o AOV mínimo de 2026 (R$ 2.030,88 → BE CPA R$ 1.015,44), as quatro linhas continuam passando com folgas de 5,26× a 12,36×. **Nenhuma campanha muda de lado em nenhum cenário de AOV observado em 2026.**

### 2.2 Robustez contra a ressalva de R$ 7.730 — R-0130

A discrepância de 4,5% entre CSV (R$172.730,01) e telas (~R$165.000) é do lado do **valor de conversão**, não do custo. O CPA usa **custo ÷ conversões** — não usa valor. Logo:

> A ressalva de R$7.730 **não toca o cálculo de CPA**.

O que **tocaria** o CPA é inflação na **contagem de conversões** (76,38). Meço o tamanho do erro necessário:

```
Para a conta atingir o BE CPA de R$ 1.266,93 com custo 9.577,32:
conversões_máximas = 9.577,32 ÷ 1.266,93 = 7,56

Conversões reportadas: 76,38
⇒ 90,1% das conversões reportadas teriam de ser espúrias.
```

Mesmo no cenário mais pessimista compatível com R-0130 — as quatro ações de conversão (purchase, add to cart, begin checkout, page view) todas marcadas como primárias, inflando a contagem — seria preciso que **9 em cada 10 conversões fossem falsas**. A conta registra **48 compras na tela de Metas**; 48 ÷ 9.577,32 = **CPA de R$ 199,53**, que continua passando com folga de **6,35×**.

> **Conclusão sob R-0130:** mesmo usando exclusivamente as 48 compras confirmadas na tela de Metas — descartando integralmente as 76,38 conversões do CSV — o veredito de aprovação **não muda**. Esta é a leitura mais conservadora possível do dado disponível.

### 2.3 O que este veredito NÃO autoriza — R-0072, R-0092

**R-0527** diz: CPA abaixo do break-even → aumentar lances. **R-0519** vai além: campanha muito abaixo do break-even e claramente escalável → `autonomy: "Obrigatório escalar"`. Agora, pela primeira vez, essas regras disparam sobre o **KPI primário**, não sobre o secundário.

Contra elas, os mesmos **dois bloqueios com precedência textual**:

| Regra | Precedência declarada na fonte | Condição na MTX |
|---|---|---|
| **R-0072** | *"Precede qualquer decisão de aumento de verba e a adição de YouTube/cold search"* | Fundação ausente: sem branded search, sem branded shopping, sem Shopping padrão |
| **R-0092** | *"Precede a regra de aumento de orçamento"* | Desempenho em queda (V&H −73%; impressões −37%; conversões −18%; valor −25%) |

**R-0524 caiu.** Era o terceiro bloqueio ("não escalar sem break-even CPA calculado") e está **resolvido** — o break-even CPA agora existe. Restam dois.

---

## 3. ENTREGÁVEL 3 — O QUE MUDA COM O KPI PRIMÁRIO DISPONÍVEL

**R-0523** declara: *break-even CPA é o KPI mais importante; break-even ROAS é apenas informativo/interessante*, com `precedence: "Break-even CPA prevalece sobre break-even ROAS; ROAS é irrelevante em comparação"` e `do_not: "Não usar o ROAS como métrica decisória principal em detrimento do break-even CPA"`.

Toda a auditoria anterior rodou no KPI que a fonte chama de irrelevante. Agora rodo no primário.

### 3.1 O que se CONFIRMA

| Conclusão anterior | Base anterior | Base agora | Estado |
|---|---|---|---|
| Todas as campanhas acima do break-even | R-0526 (ROAS) — KPI secundário | **R-0527 (CPA) — KPI primário** | ✅ **CONFIRMADA no KPI que decide** |
| Conta lucrativa | ROAS 18,04 vs 2,0 | **CPA 125,40 vs 1.266,93** | ✅ **CONFIRMADA** |
| V&H tem o melhor CPA da conta | comparação intra-conta | **folga de 15,42× no BE CPA** | ✅ **CONFIRMADA e ampliada** |
| Ressalva de R$7.730 não é determinante | margem ~20× no ROAS | **CPA não usa valor; 48 compras ainda passam** | ✅ **CONFIRMADA por caminho independente** |
| Não escalar agora | R-0072 + R-0092 + R-0524 | **R-0072 + R-0092** (R-0524 caiu) | ✅ **CONFIRMADA, com um bloqueio a menos** |
| MER 44,7 = volume insuficiente | R-0022 | recalculado em §3.3 | ✅ **CONFIRMADA e reforçada** |
| Marca contaminando prospecção | R-0078, R-0353, R-0498 | inalterado | ✅ **CONFIRMADA — nenhum dado novo tocou** |

### 3.2 O que se INVERTE

**Uma inversão, e é de status epistêmico, não de direção.**

> **Toda a rodada anterior operava sob autoinvalidação declarada.** §1.2 dizia: *"o KPI primário da metodologia está indisponível. Tudo que segue baseado em ROAS opera no KPI que a própria fonte classifica como secundário."*
>
> Sob R-0523, aquilo era uma auditoria construída sobre a métrica que a fonte manda **não** usar como decisória.
>
> **Isso se inverte agora.** As conclusões de aprovação passam de *provisórias sob KPI desqualificado* para **firmes sob o KPI que a fonte declara primário**. A direção não mudou; a autoridade da conclusão mudou.

**Nenhuma conclusão mudou de lado.** Nenhuma campanha que passava passou a falhar, nem o contrário. Registro isso explicitamente porque era o resultado possível que exigiria reescrever a auditoria.

### 3.3 O que muda por causa da CORREÇÃO de R$380k → R$525k

**Recalculo tudo que dependia do denominador.**

| Medida | com R$380.000 | **com R$525.000** | Δ |
|---|---|---|---|
| **MER** (R-0522 / S-0418) | 44,7 | **61,8** | +38% |
| Marketing como % da receita | 2,24% | **1,62%** | −28% |
| Mídia Google como % da receita | 0,92% | **0,61%** | −34% |
| **Share do Google na receita** (R-0032) | 15,2% | **11,0%** | −28% |

**O que MUDA:**

- **Todos os números de proporção pioram.** A empresa é maior do que se pensava e investe proporcionalmente **menos** em marketing.
- **R-0022** dispara com mais força, não menos: `action: "Reconhecer que o gasto é insuficiente e que o crescimento está limitado nesse teto; aumentar o volume/gasto"`. Com 1,62% da receita em marketing e 0,61% em mídia Google, o diagnóstico de volume insuficiente é **mais** agudo.
- **R-0032** continua disparando na mesma direção (Google < 20–30% → espaço não explorado), agora com margem maior: 11,0% contra 15,2%.

**O que NÃO MUDA:**

- **Nada do lado da conta de anúncios.** ROAS, CPA, break-evens, veredito por campanha, contaminação de marca, ausência de fundação — nenhum desses números tem R$380.000 no denominador. São todos internos à conta.
- **A direção de R-0022 e R-0032.** Ambas já apontavam para "gastar mais"; continuam apontando, com mais força.
- **A reconciliação de custo** (R$3.192,44/mês vs R$3.500 declarados) — não usa faturamento.
- **A sequência R-0072 → R-0092 → escalar.** Bloqueios estruturais, independentes do faturamento.

### 3.4 §5.4 RESOLVIDO — o denominador quebrado agora fecha

A rodada anterior deixou §5.4 aberto: *"Não arbitro a divisão. Falta: receita mensal apenas do site."* Você forneceu.

```
Receita mensal do site (média maio–julho): R$ 149.892
Google atribuído/mês: R$ 172.730,01 ÷ 90 × 30 = R$ 57.576,67
Share do Google sobre o site: 38,4%
```

**Isto inverte a regra que dispara.**

| Denominador | Share | Regra | Diagnóstico |
|---|---|---|---|
| Todos os canais (R$525.000) | **11,0%** | **R-0032** | abaixo de 20–30% → espaço não explorado, ampliar Google |
| **Apenas o site (R$149.892)** | **38,4%** | **R-0054** | acima de 20–30% → **subperformance dos outros canais**, não sobreperformance do Google |

**R-0054** (`do_not: "Não concluir que o problema é o Google estar sobreperformando"`) diz: quando o Google excede 20–30%, diagnosticar como **subperformance dos demais canais** e tratar como espaço para escalar os outros.

> ### **A rodada anterior antecipou exatamente este cenário e ele se confirmou.**
> §5.4 dizia: *"Se o site for, digamos, metade do faturamento, o Google já estaria em ~30% e o gatilho seria R-0054 — conclusão oposta."* O site é 28,6% do faturamento total e o Google é 38,4% do site.

**Qual denominador vale?** **R-0032** refere-se explicitamente ao *"dashboard de receita (Shopify, Triple Whale ou Northbeam)"* — dashboards de DTC, que medem o site. A leitura textualmente ancorada é a do site.

**Mas as duas regras coexistem sem contradição operacional**, e é isso que importa:

- **R-0054** diz: os outros canais estão subperformando → escalar os outros canais. Mercado Livre + balcão = R$375.108/mês (71,4% da receita) com **zero** mídia paga identificada.
- **R-0022** diz: mensagem excelente + volume baixo → aumentar volume. 1,62% da receita em marketing.
- **R-0052** (`do_not: "Não pensar em Google Ads como único motor de crescimento do negócio"`) e **R-0053** (teto de ~20–30% do Google sobre a receita da marca em escala).

**Convergência:** todas apontam para o mesmo lugar — **o Google não está subperformando; o resto do negócio está subinvestido em marketing.** O gasto de R$3.192/mês está concentrado no canal que já responde por 38,4% do site enquanto 71,4% da receita da empresa não tem mídia paga.

> **METHOD_NOT_DEFINED — alocação de verba entre canais de venda.** A fonte cobre alocação **dentro** do Google Ads (R-0079: 80–90% em tráfego frio; R-0095: 3–8% em marca) e enquadra o Google no ecossistema de marketing (R-0012, R-0034, R-0052, R-0056). Ela **não** define como distribuir orçamento entre site próprio, marketplace e balcão. Registro que R-0054 aponta para "escalar os outros canais" e que a fonte não diz como. Não arbitro.

### 3.5 O que continua INDETERMINADO

| Item | Regra bloqueada | Por quê |
|---|---|---|
| **Parcela de impressão** | **R-0128** — hierarquia declarada: `impression share > CPC > CTR > taxa de conversão > nº de conversões` | Pedido 2 não atendido. **A métrica nº 1 da hierarquia da fonte segue ausente.** Também bloqueia R-0089, R-0127, R-0343, R-0365 |
| **CPA de novo cliente** | **R-0521** — *"o KPI mais importante que você deveria acompanhar sempre"* | **Não confundir com o break-even CPA.** R-0134 calcula o *limiar*; R-0521 exige o *CPA de cliente NOVO especificamente*. Requer separação novo vs. recorrente (R-0779, tag de primeiro pedido) — não existe na conta. **R-0090** (aumento mensal condicionado a aquisição estável) segue inexecutável |
| **Estratégias de lance e orçamentos** | R-0084, R-0150, R-0151, R-0152, R-0356, R-0364, R-0534–R-0537 | Pedidos 3 e 4 não atendidos |
| **Ações de conversão (tela)** | R-0130, R-0377, R-0199, R-0187, R-0192 | Pedido 4 não atendido — ver §4 |
| **Status do GMC** | R-0433 (Shopping obrigatório) inexecutável até verificar | Pedido 8 não atendido |
| **Relatório de produtos** | R-0094, R-0460–R-0464, R-0504, WF-0116, WF-0123, WF-0124 | Pedido 9 |
| **Assets** | R-0505, R-0125, WF-0125 | Pedido 10 |
| **Script de PMax** | **R-0444** — `do_not: "Depender apenas dos recursos nativos de insight do Google"` | Pedido 13. **75,7% do gasto da PMax opaco.** Auditoria de PMax formalmente incompleta |
| **Atribuição de terceiros** | **R-0443** — Triple Whale/Northbeam como fonte da verdade | Com **três** canais de venda concorrendo pelo crédito, EV-1368 (PMax reivindicando vendas de outros canais) é risco real e não mensurável. **Agravado** pela correção: R$375.108/mês fora do site |
| **Landing pages** | R-0115, R-0400, R-0508–R-0514, WF-0114, WF-0129 | Recorte I corrompido (`url: "(vazio)"`, 400,27 conv em 502 linhas). Único item recuperável por re-export |
| **Classificação de V&H** | METHOD_NOT_DEFINED (§4.2 da rodada anterior) | A fonte não define marca de terceiro sob distribuição exclusiva. Decide se 33,9% do gasto viola R-0095 ou cumpre R-0017 |

---

## 4. ENTREGÁVEL 4 — 48 COMPRAS vs 76,38 CONVERSÕES

### 4.1 O que é DECIDÍVEL com o que existe

Você trouxe um terceiro número que a rodada anterior não tinha: o **AOV real de R$ 2.533,86**, medido no site, sobre 161 pedidos finalizados. Isso permite testar as duas hipóteses contra um referencial externo à conta de anúncios.

| Divisor | Valor por unidade | vs AOV real (R$ 2.533,86) | Desvio |
|---|---|---|---|
| ÷ 48 compras | **R$ 3.598,54** | 1,42× o AOV | **+42,0%** |
| ÷ 76,38 conversões | **R$ 2.261,46** | 0,89× o AOV | **−10,8%** |

**Conclusão decidível:** o valor por **conversão** (R$2.261,46) fica **10,8% abaixo** do AOV real. O valor por **compra** (R$3.598,54) fica **42,0% acima**.

**R-0562** (critério de sucesso do gasto em criativos) e **R-0673** (`do_not: "Não usar um número de CPA/CAC universal como referência"` — avaliar contra as unit economics próprias) estabelecem o princípio de julgar contra o dado próprio do negócio. Aplico: o AOV do site é o dado próprio. Um desvio de −10,8% é compatível com ruído de atribuição, mix de produtos e recorte temporal. Um desvio de **+42,0%** exigiria que os pedidos atribuídos ao Google fossem sistematicamente 42% maiores que a média do site.

**Verificação cruzada — a contagem de pedidos:**

```
Pedidos finalizados no site na janela: 161
Compras na tela de Metas: 48       → 29,8% dos pedidos do site
Conversões no CSV: 76,38            → 47,4% dos pedidos do site
```

Ambos os números cabem dentro de 161. Nenhum dos dois é aritmeticamente impossível. **A contagem de pedidos não desempata.**

**Verificação cruzada — o valor total:**

```
Receita do site na janela: R$ 407.951,51
Valor de conversão atribuído: R$ 172.730,01  → 42,3% da receita do site
```

Também cabe. Também não desempata.

### 4.2 O que a divergência 48 vs 76,38 significa estruturalmente

76,38 − 48 = **28,38** — e 28,38 é fracionário.

**R-0191** estabelece atribuição **data-driven** como configuração. Sob atribuição data-driven, uma única conversão pode ser fracionada entre múltiplos pontos de contato, gerando contagens não-inteiras. **Isso explica a fração**, mas não explica sozinho a diferença de 59% entre os dois números.

**R-0192 / R-0199** estabelecem que add to cart, begin checkout e product view devem ser **`secondary, observe only`**, e **R-0187** que apenas purchase é `account default goal`. **R-0377** exige **uma única ação de conversão primária**.

Duas leituras compatíveis com o dado, e **não tenho como escolher entre elas**:

| # | Leitura | O que implicaria | Regra |
|---|---|---|---|
| **A** | "Compras" na tela de Metas conta eventos discretos; "conversões" no CSV conta atribuição fracionada da mesma ação | Configuração **conforme** R-0377. Valor/conversão (R$2.261,46) é a leitura correta e bate com o AOV | R-0191 |
| **B** | Múltiplas ações estão marcadas como primárias e todas carregam valor | Configuração **em violação** de R-0377 e R-0199. Ambos os divisores estariam contaminados | R-0130 |

**A leitura A é mais compatível com o AOV real** (desvio de −10,8% contra +42,0%). Mas compatibilidade não é prova.

### 4.3 O que EXIGE o pedido #4 — e é o único que resolve

> **A pergunta que você faz — "qual dos dois é o valor por PEDIDO" — depende de saber quais ações de conversão carregam valor. Isso é exatamente o pedido #4 e não há substituto.**

**R-0130** é a regra que governa esta situação: `condition: "A maioria das agências e freelancers erra essa configuração"`, `action: "Tratar a configuração como suspeita e verificar o rastreamento de conversão"`, `do_not: "Assumir que o rastreamento de conversão herdado está correto"`.

A fonte manda **verificar**, não inferir. E a verificação é uma tela.

> ### **METHOD_NOT_DEFINED — desambiguação de contagem de conversão sem acesso à configuração**
>
> A fonte fornece o **estado-alvo** da configuração (R-0187, R-0190, R-0191, R-0192, R-0199, R-0377) e manda **verificá-lo** (R-0130). Ela **não** fornece procedimento para inferir a configuração a partir das saídas agregadas quando a tela não está disponível.
>
> Não arbitro qual divisor é o correto.

### 4.4 O que é seguro fazer sem resolver a ambiguidade

**Uma coisa importante: a ambiguidade não bloqueia nenhum veredito desta auditoria.**

| Uso | Depende do divisor? | Estado |
|---|---|---|
| **CPA por campanha** | ❌ Não — CPA é custo ÷ conversões, e ambos os divisores foram testados em §2.2 | ✅ Decidido |
| **Veredito contra BE CPA** | ❌ Não — passa com 76,38 (folga 10,10×) e passa com 48 (folga 6,35×) | ✅ Decidido |
| **Break-even CPA** | ❌ Não — usa AOV do site, medido fora da conta de anúncios | ✅ Decidido |
| **Break-even ROAS** | ❌ Não — usa margem, não conversões | ✅ Decidido |
| **Valor por pedido atribuído** | ✅ **Sim** | ❌ **INDETERMINADO** |
| **R-0521 (CPA de novo cliente)** | ✅ Sim, e mais | ❌ Bloqueado independentemente — exige separação novo/recorrente |

**Registro:** ao adotar as 48 compras — a leitura mais conservadora — o CPA da conta vai a R$ 199,53 e continua aprovado. Foi assim que blindei §2.2. A ambiguidade está **quantificada e contida**; segue **não resolvida**.

---

## 5. ENTREGÁVEL 5 — RECOMENDAÇÕES REORDENADAS

Ordem: **da mais específica para a mais genérica**, conforme solicitado. Marco cada mudança de posição e a razão.

---

### **1. Excluir hoje `mtx imports` e `mtx importadora` da VENDAS|PERF-MAX**
🔁 **MANTÉM A POSIÇÃO 1**
**R-0498** — única regra da fonte com urgência declarada: `action: "excluir o termo de marca imediatamente"`. Também **R-0446**, **R-0438**.
Valores: R$30,47 / 1,00 conversão e R$4,91 / 0 conversões. Critério de conclusão em **R-0499**: nenhum termo de marca na lista de convertedores da PMax. A conta falha esse critério hoje.
**Por que não se move:** é a única regra com "imediatamente" no texto. Nenhum dado novo tocou nela.

### **2. Retirar `mtx` (R$58,46 / 41 cliques / 0 conv) e `loja mtx` (R$9,02 / 5 cliques / 0 conv) das campanhas de prospecção**
🔁 **MANTÉM A POSIÇÃO 2**
**R-0078** (`do_not: "Manter termos de marca dentro da campanha de prospecção"`, `do_not: "Desperdiçar budget em pessoas que iriam converter de qualquer forma"`), **R-0353**.
Ação é **mover para campanha de marca dedicada**, não negativar e esquecer — R-0078 prescreve segmentação em campanha própria com orçamento próprio.
**METHOD_NOT_DEFINED reiterado (§3.2 anterior):** a fonte não define como tratar termo de marca simultaneamente obrigatório de proteger (R-0073/R-0341) e candidato a remoção por zero conversão (R-0393). Lançar `[mtx]` em exata sob monitoramento diário, decisão em 30 dias.

### **3. Abrir a tela das ações de conversão** ⬆️
⬆️ **SOBE DE #8 PARA #3 — MAIOR MOVIMENTO DESTA REORDENAÇÃO**
**R-0130** (`do_not: "Assumir que o rastreamento de conversão herdado está correto"`).
**Por que subiu cinco posições:** na rodada anterior este item resolvia **uma** ressalva (os R$7.730). Agora resolve **três**, e uma delas é a pergunta que você fez no Bloco 3:

| O que resolve | Regra |
|---|---|
| A ambiguidade 48 vs 76,38 — **a única forma de fechá-la** (§4.3) | R-0130, R-0377 |
| A ressalva dos R$7.730 (4,5%), aberta desde a rodada 1 | R-0130 |
| Os 41 cliques em `mtx` sem conversão (§3.2 anterior) | R-0130, R-0113 |

Verificar: **R-0377** (uma única primária), **R-0187** (purchase como account default goal), **R-0199** (add to cart, begin checkout e checkout page view como *secondary, observe only*), **R-0190** (janelas 90/30/30), **R-0191** (atribuição data-driven).
**Custo de execução: uma tela.**

### **4. Criar a campanha de busca de marca — WF-0094 / WF-0095**
🔁 **MANTÉM A POSIÇÃO** (era #3, desce uma casa apenas porque #3 subiu)
**R-0073** (*"primeiro elemento fundacional"*), **R-0341**, **R-0316**.

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

**Orçamento — recalculado com a correção:** R-0340 fixa US$25/dia, mas a fonte **não define conversão cambial** (UNDEFINED). O limite vinculante é **R-0095**: 3–8% do investimento mensal. Sobre R$3.500 declarados = **R$105–280/mês**, teto duro 10% = R$350/mês. *O faturamento corrigido não altera este número — R-0095 tem o investimento em mídia no denominador, não a receita.*

### **5. Verificar o Google Merchant Center**
🔁 **MANTÉM A POSIÇÃO 5** (era #4, desce uma casa)
**Status = UNDEFINED.** Sem GMC saudável não existe Shopping de marca nem Shopping padrão — **duas das três peças fundacionais dependem deste único item**.
**R-0237** (checklist proativo de 34 itens, `do_not: "Não esperar um problema/suspensão para agir"`), **WF-0069**. Itens de maior risco para distribuidor de peças importadas: **R-0207** (política de devolução espelhada exatamente), **R-0206** (envio em modo manual no GMC, não sincronizado com Shopify), **R-0235** (`do_not: nunca editar preço/disponibilidade dentro do GMC`), **R-0230** (GTIN — crítico em peças com código de barras de fabricante), **R-0254** (envio sincronizado).

### **6. Subir Shopping padrão**
🔁 **MANTÉM A POSIÇÃO 6** (era #5)
**R-0433** (*"Estar presente em shopping"* — obrigatório para e-commerce), **R-0018** e **R-0037**: shopping representa **60–80% de todo o volume de Google Ads em e-commerce**.
**Tradução direta:** a MTX opera hoje sobre **20–40% do canal**. **R-0041 / R-0138 / R-0542**: combinar PMax com standard shopping para cobrir integralmente o placement.

### **7. Subir Shopping de marca — WF-0099**
🔁 **MANTÉM A POSIÇÃO 7** (era #6)
**R-0349** (o custo é *"um dos custos de fazer negócio no Google Ads"*), **R-0350**, **R-0347/R-0348** (excluir **todos** os termos não-marca), **R-0359** Manual CPC, **R-0360** prioridade alta, **R-0361** presença apenas, **R-0364** (`do_not: "Automatizar os lances em campanhas de branding — complete no"`).
Depende de #5.

### **8. Instaurar a cadência operacional — WF-0020 / WF-0121** ⬆️
⬆️ **SOBE DE #9 PARA #8**
**R-0104** (`do_not: "Não montar, publicar e esquecer a conta"`), **R-0496** (search term insights da PMax = *"a única tarefa a fazer todos os dias dentro da PMAX"*), **S-0046**, **R-0106**.
Estado: **180 linhas tocadas em 24.795 = 0,73%**, zero negativações em 90 dias.
**Por que subiu:** o item que ocupava #7 (fornecer AOV e custo fixo) **foi cumprido e sai da lista** — ver §5.1.

### **9. Promover os 7 termos convertedores para correspondência exata** ⬆️
⬆️ **SOBE DE #10 PARA #9**
**R-0394**, **R-0174**, **R-0169**, WF-0105 (S-0321).
`fuel pak 4`, `harley davidson lojas`, `sissy bar road glide 2025`, `motobox`, `capacete harley davidson`, `vance & hines backslash 450`.
**R-0386**: estado-alvo é mistura de exata e ampla; hoje **100% ampla**. **R-0176**: broad fora de contexto de teste é proibido. Fase de descoberta aberta há 90 dias sem nunca ter sido fechada.

### **10. Negativar os 1.099 termos com zero conversão (R$2.325,35)** ⬆️
⬆️ **SOBE DE #11 PARA #10**
**R-0393**, **R-0497**, **R-0171**.
> **METHOD_NOT_DEFINED reiterado:** a fonte não define piso de cliques ou gasto que separa "evidentemente não performando" (R-0393) de "volume insuficiente para concluir" (**R-0389**). Não arbitro. Aplicação segura: começar pelos termos com maior custo **E** maior contagem de cliques, onde as duas regras não conflitam.
> **Nota sobre percentual:** o denominador de "76,8% do gasto divulgado" era R$3.026,50 (Total: Termos de pesquisa). Sobre o custo total corrigido da conta (R$9.577,32), R$2.325,35 = **24,3%**. Uso o percentual sobre o total da conta por ser o denominador auditável.

### **11. Re-exportar o relatório de landing pages** ⬆️
⬆️ **SOBE DE #12 PARA #11**
Único item bloqueado por falha técnica minha, não por falta de dado do cliente. Recorte I chegou com `url: "(vazio)"` e 400,27 conversões em 502 linhas — inutilizável.
Destrava **R-0115** (congruência anúncio↔página), **R-0400**, **R-0508**–**R-0514**, WF-0114, WF-0129.
Relevante porque **R-0113** manda dirigir a investigação para a página quando as métricas de anúncio estão boas e a conversão não vem — exatamente o padrão de `mtx`.

### **12. Rodar o script de PMax de Mike Rhodes** ⬆️
⬆️ **SOBE DE #13 PARA #12**
**R-0444** (*"padrão-ouro para analisar e auditar PMax"*, `do_not: "Depender apenas dos recursos nativos de insight do Google"`), WF-0120, WF-0137.
**75,7% do gasto da PMax é opaco.** Sem isso a PMax não pode ser auditada — apenas desqualificada estruturalmente, o que já foi feito (**R-0430** falha em gasto/dia e conversões/mês; **R-0044** falha no gate de 1 conv/dia por 30 dias).

### **13. Só depois de 1–8: escalar em incrementos de 10–20%**
🔁 **MANTÉM A POSIÇÃO RELATIVA** (era #14, sobe uma casa)
**R-0532** (`do_not: "Não fazer aumentos bruscos"`), **R-0091**, **R-0136/R-0538** (cortar rápido, escalar devagar), **R-0090** (condicionado a aquisição estável — **hoje inexecutável, R-0521 sem dado**).
Alvo de alocação: **80–90% em tráfego frio** (**R-0079**), marca em **3–8%** (**R-0095**).
**Teto operacional — recalculado com o KPI primário:** sob **R-0126** (lucro no primeiro pedido), o limite é o break-even. Agora expresso no KPI que decide:

> **CPA da conta pode subir de R$ 125,40 até R$ 1.266,93** e continuar cumprindo a instrução do dono (R-0126).
> **Folga de 10,10×.**

**Dimensionamento (não é previsão — a fonte não prescreve modelagem de retornos decrescentes, e eles existem):** ao BE CPA, as mesmas 76,38 conversões sustentariam **R$96.767/mês de mídia** contra R$3.192,44/mês hoje. **Folga nominal de ~30×.** Sob a leitura conservadora de 48 compras: **R$60.813/mês**, folga de ~19×. O caminho é regido por R-0532 e R-0091 — em etapas, nunca em salto.

### **14. Genérico: o problema da MTX não é eficiência, é tamanho** ⬆️
⬆️ **SOBE DE #15 PARA #14 — e o argumento ficou mais forte com a correção**
**R-0022**, **R-0005**, **R-0013**, **R-0058**.

| Medida | corrigida |
|---|---|
| MER | **61,8** |
| Marketing / receita | **1,62%** |
| Mídia Google / receita | **0,61%** |

**R-0005** (fórmula da escala): `mensagem × volume = crescimento`. Mensagem: CPA a 10,10× de folga sobre o break-even. Volume: **0,61% da receita**. **O fator limitante é inequivocamente o volume**, e a correção de R$380k→R$525k tornou o desequilíbrio **28% mais agudo**.

**R-0051** define o critério de sucesso: *"Avaliar o sucesso pela eficiência na aquisição de clientes... e não por receita ou vendas isoladas"*, `do_not: "Não usar receita como critério de sucesso"`. **R-0058**: `do_not: "Não focar em ROAS alto isoladamente"`. Um CPA de R$125,40 contra um teto de R$1.266,93 é uma conta administrada para preservar um número.

### **15. NOVO — Diagnosticar a subperformance dos canais fora do site** 🆕
🆕 **ENTRA NA LISTA — item que não existia na rodada anterior**
**R-0054** — Google a **38,4% da receita do site** dispara: `action: "Diagnosticar como subperformance dos outros canais (não sobreperformance do Google) e tratar isso como espaço para escalar os demais canais"`, `do_not: "Não concluir que o problema é o Google estar sobreperformando"`.
**Por que é novo:** só existe porque §5.4 foi resolvido — a rodada anterior tinha o denominador quebrado e registrou textualmente que esta era a conclusão oposta possível.
**Por que é o mais genérico da lista:** R$375.108/mês (71,4% da receita) em Mercado Livre e balcão, sem mídia paga identificada. **R-0052** (`do_not: "Não pensar em Google Ads como único motor de crescimento"`), **R-0056** (Google depende das fontes que geram demanda), **R-0053** (teto de ~20–30% do Google sobre a receita em escala).
> **METHOD_NOT_DEFINED (§3.4):** a fonte não define alocação de verba **entre** canais de venda. Registro o gatilho de R-0054 e paro. Não arbitro.

---

### 5.1 Itens que SAEM da lista

| Item anterior | Estado |
|---|---|
| **#7 — Fornecer AOV do site e custo fixo de COGS por pedido** | ✅ **CUMPRIDO.** Dados 7 e 7b. Destravou R-0134, resolveu R-0523 e derrubou R-0524. **Este documento é o resultado.** |

### 5.2 Resumo das mudanças de posição

| Movimento | Item | Razão |
|---|---|---|
| ⬆️ **#8 → #3** | Tela das ações de conversão | Passou a resolver **três** ressalvas, incluindo a pergunta do Bloco 3. Única via para fechar 48 vs 76,38 |
| ✅ **#7 → removido** | AOV e custo fixo | Cumprido |
| ⬆️ **+1 cada** | Itens #9 a #15 anteriores | Consequência da remoção do #7 |
| 🆕 **novo #15** | Subperformance dos outros canais | §5.4 resolvido inverteu R-0032 para R-0054 |
| 🔁 **#1, #2** | Contaminação de marca | Nenhum dado novo tocou. R-0498 mantém a urgência declarada |

---

## 6. VEREDITO

**A conta é lucrativa pelo KPI que a fonte declara primário, e estruturalmente incompleta. Os dois fatos são independentes e ambos verdadeiros.**

### 6.1 Lucrativa — agora no KPI que decide

| | |
|---|---|
| Break-even CPA (**R-0134**) | **R$ 1.266,93** |
| CPA da conta | **R$ 125,40** |
| **Folga** | **10,10×** |
| Sob a leitura conservadora (48 compras) | CPA R$ 199,53 · folga **6,35×** |
| Sob o pior AOV de 2026 (R$2.030,88) | BE CPA R$1.015,44 · folga **8,10×** |
| **Campanhas aprovadas** | **3 de 3, em todos os cenários** |

**R-0523** está satisfeita: o KPI primário existe, foi calculado pela fórmula da fonte, e as quatro linhas passam. A rodada anterior operava sob autoinvalidação; esta não.

### 6.2 Incompleta — inalterado

Sem busca de marca, sem shopping de marca, sem shopping padrão — três elementos que **R-0073**, **R-0349** e **R-0433** classificam como fundacionais ou obrigatórios. Marca vazando para dentro das três campanhas de prospecção (**R-0498**, **R-0078**). Zero negativações em 90 dias (**R-0104**). PMax rodando 6× abaixo do gate de habilitação (**R-0044**, **R-0430**).

### 6.3 Subdimensionada — pior do que se pensava

**0,61%** da receita em mídia Google. **1,62%** em marketing total. **R-0022** aplica-se integralmente e a correção de faturamento tornou o diagnóstico **28% mais agudo**.

### 6.4 A sequência

```
estruturar (R-0072)
  → corrigir o vazamento da V&H (R-0092)
    → escalar (R-0527, R-0519, R-0532)
```

**R-0524 foi removida da sequência** — o break-even CPA existe. Restam dois bloqueios, ambos com precedência textual na fonte, e nenhum deles depende de dado que a MTX não tenha em mãos.

### 6.5 Ressalvas abertas ao fim desta auditoria

| Ressalva | Regra | Estado |
|---|---|---|
| **48 compras vs 76,38 conversões** | R-0130, R-0377 | ⚠️ **Quantificada, contida, NÃO resolvida.** Não bloqueia nenhum veredito (§4.4). Exige o pedido #4 |
| Discrepância de R$7.730 (4,5%) | R-0130 | ⚠️ Aberta desde a rodada 1. Não toca o cálculo de CPA (§2.2) |
| Configuração das ações de conversão | R-0130, R-0377, R-0199 | ⚠️ Não vista. **Recomendação #3** |
| Parcela de impressão | **R-0128** | ⚠️ **Métrica nº 1 da hierarquia da fonte, ausente** |
| CPA de **novo cliente** | **R-0521** | ⚠️ *"O KPI mais importante que você deveria acompanhar sempre"* — indisponível. Distinto do break-even CPA |
| 75,7% da PMax opaco | **R-0444** | ⚠️ Auditoria de PMax formalmente incompleta |
| Sem atribuição de terceiros | **R-0443** | ⚠️ **Agravada pela correção** — R$375.108/mês fora do site concorrendo pelo crédito |
| Classificação de V&H | METHOD_NOT_DEFINED | ⚠️ Decide se 33,9% do gasto viola R-0095 ou cumpre R-0017 |
| Alocação entre canais de venda | METHOD_NOT_DEFINED | ⚠️ **Nova.** R-0054 aponta para escalar os outros canais; a fonte não diz como |
| Divergência no recorte B | — | ⚠️ Recorte reenviado mantém 9.586,54 / 125,52; usei 9.577,32 / 125,40 conforme instruído |

---

## 7. DADOS QUE PRECISO E NÃO TENHO

Registro completo, conforme protocolo.

| # | Dado | Regra/workflow bloqueado | Custo de obtenção |
|---|---|---|---|
| **4** | **Tela das ações de conversão** — quais são primárias, quais carregam valor | **R-0130, R-0377, R-0187, R-0190, R-0191, R-0192, R-0199** — **e a pergunta do Bloco 3** | **Uma tela** |
| 2 | Parcela de impressão por campanha | **R-0128** (métrica nº 1), R-0089, R-0127, R-0343, R-0365 | Uma coluna no relatório |
| 3 | Estratégias de lance por campanha | R-0084, R-0150, R-0151, R-0152, R-0356, R-0364 | Uma tela |
| — | Orçamentos por campanha | R-0534–R-0537 | Uma tela |
| 8 | Status do Google Merchant Center | **R-0433** inexecutável; WF-0069, R-0237 | Uma tela |
| 9 | Relatório de produtos | R-0094, R-0460–R-0464, R-0504, WF-0116, WF-0123, WF-0124 | Um export |
| 10 | Relatório de assets | R-0505, R-0125, WF-0125 | Um export |
| 13 | Script de PMax (Mike Rhodes) | **R-0444** — 75,7% do gasto opaco | Instalar e rodar |
| — | Re-export de landing pages | R-0115, R-0400, R-0508–R-0514 | **Falha minha** — recorte I corrompido |
| — | CPA de **novo cliente** (separado de recorrente) | **R-0521**, R-0090, R-0779 | Exige tag de primeiro pedido (**WF-0173**) — não existe hoje |
| — | Atribuição de terceiros (Triple Whale / Northbeam) | **R-0443** | Implementação |
| — | Classificação de V&H sob distribuição exclusiva | METHOD_NOT_DEFINED — fora do alcance da fonte | Não resolvível com dado |
| — | Alocação de verba entre site / ML / balcão | METHOD_NOT_DEFINED — fora do alcance da fonte | Não resolvível com dado |

---

**Limitação do piloto:** esta Skill permanece `S3_EXECUTABLE`, `production_ready: false`. Piloto de curso único; até que uma execução cega independente seja bem-sucedida, os vereditos aqui refletem a metodologia compilada de uma única fonte e não substituem julgamento independente.