# Google Ads para E-commerce — PILOT-003

**Skill ID:** `PILOT-003-SKILL`  **Version:** `0.1.0`  **Maturity:** `S3_EXECUTABLE`  **Production Ready:** `false`

## ROLE OF THIS FILE

Runtime entrypoint and router only. Executable methodology is intentionally stored in structured resources rather than duplicated here.

## LOAD ORDER — MANDATORY

Before every answer, load/apply in this order:

1. `knowledge/runtime-policy.yaml`
2. `knowledge/decision-rules.yaml` when a methodology decision is required
3. `knowledge/workflows.yaml` when building/configuring

## DISPATCH

- Methodology decision request → `knowledge/decision-rules.yaml`.

Build/configure requests route by topic to `knowledge/workflows.yaml`:
- *conversion tracking setup* → `WF-0001` (3 steps)
- *systematic checklist* → `WF-0002` (3 steps)
- *Marketing efficiency ratio* → `WF-0003` (3 steps)
- *Fórmula para escalar no Google (mensagem × volume = crescimento)* → `WF-0005` (3 steps)
- *seção de pesquisa de palavras-chave (keyword research section)* → `WF-0006` (5 steps)
- *cold customer magnet* → `WF-0007` (9 steps)
- *Cold customer magnet Google ad system* → `WF-0008` (2 steps)
- *Três estágios de crescimento da estratégia de Google Ads* → `WF-0009` (3 steps)
- *Framework das sete áreas de escala em Google Ads* → `WF-0011` (7 steps)
- *break even rise and break even CPA scaling philosophy* → `WF-0012` (1 steps)
- *Shopping campaigns* → `WF-0014` (1 steps)
- *Performance Max campaign* → `WF-0015` (2 steps)
- *Campaign segmentation* → `WF-0016` (2 steps)
- *Scripts de palavras-chave negativas* → `WF-0017` (1 steps)
- *Poda manual com relatórios de termos de busca* → `WF-0018` (2 steps)
- *Ações diárias, semanais e mensais de escala* → `WF-0020` (6 steps)
- *Weekly GMC optimizations* → `WF-0021` (1 steps)
- *Full account review* → `WF-0022` (3 steps)
- *Full funnel approach (abordagem de funil completo) para escalar Google Ads* → `WF-0023` (1 steps)
- *AB test semanal de search campaigns e product feeds* → `WF-0025` (2 steps)
- *Conversion rate optimization (CRO) e account level optimization / split testing* → `WF-0026` (3 steps)
- *Os nove focos para escalar uma marca de e-commerce no Google Ads* → `WF-0027` (3 steps)
- *unit economics* → `WF-0028` (1 steps)
- *Goals and KPIs (definidos antes do Google Ads)* → `WF-0029` (1 steps)
- *LTV play vs. first order profitable* → `WF-0030` (2 steps)
- *Conversion tracking (rastreamento de conversão)* → `WF-0031` (1 steps)
- *Campaign structure (estrutura de campanha)* → `WF-0032` (4 steps)
- *Sétimo fator do framework: targeting (segmentação)* → `WF-0033` (2 steps)
- *Penúltimo ponto do framework: escrever anúncios congruentes* → `WF-0035` (1 steps)
- *Factor #8: creative (search, shopping, YouTube)* → `WF-0036` (8 steps)
- *Keyword research (abordagem moderna: broad match + search term reports)* → `WF-0038` (6 steps)
- *Nove áreas de foco para escalar uma marca com Google Ads* → `WF-0039` (3 steps)
- *Loop de retroalimentação de palavras-chave (keyword flywheel)* → `WF-0040` (6 steps)
- *Método 1: começar amplo e deixar o Google otimizar* → `WF-0041` (1 steps)
- *Método 2: pesquisa tradicional de palavras-chave* → `WF-0042` (4 steps)
- *Step two: using shopping and PMax campaigns to inform your search* → `WF-0043` (6 steps)
- *Step three — structuring your keywords for search and shopping campaigns* → `WF-0044` (4 steps)
- *profitable feedback loop (flywheel data-driven: shopping/PMax → keywords → search)* → `WF-0045` (6 steps)
- *Enhanced conversion tracking setup para loja e-commerce Shopify (do zero ao completo)* → `WF-0046` (1 steps)
- *Setup de Google Ads dynamic remarketing e Google Analytics 4* → `WF-0048` (5 steps)
- *Criação das quatro ações de conversão no Google Ads* → `WF-0049` (5 steps)
- *Adição de tags às ações de conversão via Google Tag Manager* → `WF-0050` (2 steps)
- *Import Container (Google Tag Manager)* → `WF-0051` (7 steps)
- *Submit → Publish → Continue (publicação do workspace)* → `WF-0052` (4 steps)
- *Google tag manager code for customer event* → `WF-0053` (5 steps)
- *Fase 1 — Foundational account and business setup (otimização do Merchant Center)* → `WF-0055` (5 steps)
- *Fase dois: shipping, returns and tax configuration* → `WF-0056` (2 steps)
- *Fase de saúde e otimização do feed de produtos* → `WF-0057` (1 steps)
- *Auditar os feeds (audit your feeds)* → `WF-0058` (1 steps)
- *Diagnosticar e corrigir problemas no feed (products > needs attention)* → `WF-0059` (1 steps)
- *Fase quatro: enhancing trust and visibility* → `WF-0060` (3 steps)
- *Shopping experience scorecard* → `WF-0061` (1 steps)
- *Ongoing maintenance* → `WF-0063` (2 steps)
- *product feed optimization* → `WF-0064` (3 steps)
- *Fórmula de título de produto* → `WF-0065` (3 steps)
- *Otimização de feed de produtos no GMC* → `WF-0066` (10 steps)
- *Preencher atributos detalhados para filtragem e relevância* → `WF-0067` (5 steps)
- *Checklist step-by-step de prevenção de suspensão do GMC (34 itens, 8 categorias, com frequências)* → `WF-0069` (8 steps)
- *Checklist de pagamento e checkout* → `WF-0070` (17 steps)
- *Legal compliance (bloco de três itens do checklist)* → `WF-0071` (12 steps)
- *internal AI workflow (Demand Capture) para gerar copy de Google Ads* → `WF-0073` (6 steps)
- *Pesquisa de marca (brand research) — primeiro passo do workflow* → `WF-0075` (2 steps)
- *Ordem de prompt engineering: role → contexto → tarefa → exemplos → constraints → output* → `WF-0076` (3 steps)
- *Auditoria abrangente do site/página de produto* → `WF-0077` (4 steps)
- *copy research framework* → `WF-0079` (1 steps)
- *tools > deep research (Gemini)* → `WF-0080` (2 steps)
- *field audit of the brand* → `WF-0081` (1 steps)
- *deep research* → `WF-0082` (1 steps)
- *brand context profile* → `WF-0083` (1 steps)
- *custom avatar JSON file* → `WF-0084` (2 steps)
- *full context profile* → `WF-0085` (2 steps)
- *deep research* → `WF-0086` (2 steps)
- *Criação dos três perfis de contexto* → `WF-0087` (1 steps)
- *Workflow de geração dos ativos de Google Ads a partir dos JSONs* → `WF-0088` (7 steps)
- *Workflow para replicar os brand JSON context profiles* → `WF-0089` (1 steps)
- *branded search campaign* → `WF-0090` (3 steps)
- *Campanha de busca de marca (brand search campaign)* → `WF-0093` (4 steps)
- *Campanha de busca de marca (search brand)* → `WF-0094` (7 steps)
- *Campanha de marca (branded campaign) no Google Ads* → `WF-0095` (6 steps)
- *Branded search campaign* → `WF-0096` (3 steps)
- *Branded shopping campaign (campanha de shopping de marca)* → `WF-0097` (2 steps)
- *Branded shopping campaign* → `WF-0098` (3 steps)
- *Criação da campanha de shopping de marca (branded shopping campaign)* → `WF-0099` (10 steps)
- *Tools > Bulk actions > Scripts* → `WF-0100` (2 steps)
- *Exclusão de audiência de clientes existentes nas campanhas de marca* → `WF-0102` (5 steps)
- *Treinamento completo de otimização do Google Merchant Center* → `WF-0103` (2 steps)
- *Setup da search campaign (começar pelo setup/settings)* → `WF-0104` (6 steps)
- *Relatório de termos de busca* → `WF-0105` (8 steps)
- *search term report* → `WF-0107` (4 steps)
- *dynamic keyword insertion* → `WF-0108` (8 steps)
- *Fase um / Fase dois da estratégia de cold search* → `WF-0109` (2 steps)
- *Dynamic Search Ads sobre content farm* → `WF-0110` (2 steps)
- *Abordagem de funil completo em Google Ads (topo, meio, fundo)* → `WF-0111` (1 steps)
- *Configurar, escalar e otimizar campanhas Performance Max* → `WF-0112` (9 steps)
- *Auditoria de landing pages/posicionamentos da PMax* → `WF-0114` (5 steps)
- *E-commerce growth engine with Google Ads* → `WF-0115` (3 steps)
- *Princípio de Pareto na seleção de produtos* → `WF-0116` (3 steps)
- *Zombie asset groups* → `WF-0117` (4 steps)
- *Criação de campanha Performance Max* → `WF-0118` (13 steps)
- *Asset group creation* → `WF-0119` (10 steps)
- *PMax script (auditoria de conta PMax)* → `WF-0120` (7 steps)
- *Check diário dos search term insights na campanha PMAX* → `WF-0121` (6 steps)
- *Verificação semanal de gasto em nível de produto (product level spend)* → `WF-0123` (1 steps)
- *Exclusão semanal de SKUs de baixo desempenho (excluding poor performing SKUs)* → `WF-0124` (1 steps)
- *Melhoria semanal de assets de baixo desempenho (improve low performing assets)* → `WF-0125` (1 steps)
- *PMAX campaigns placement (report editor)* → `WF-0127` (1 steps)
- *Exclude some URLs* → `WF-0128` (1 steps)
- *pages report (relatório de páginas) semanal* → `WF-0129` (2 steps)
- *atualização mensal de search themes* → `WF-0130` (3 steps)
- *atualização da lista de clientes (first-party data)* → `WF-0131` (5 steps)
- *Sistema de sinalização verde/amarelo/vermelho com ratios para escala* → `WF-0132` (6 steps)
- *Break even ROAS (100 dividido pela margem bruta)* → `WF-0133` (2 steps)
- *Break even CPA (AOV × margem bruta − custos fixos de COGS)* → `WF-0134` (5 steps)
- *Ajuste semanal de orçamento baseado nos KPIs* → `WF-0135` (2 steps)
- *Cut fast, scale slow* → `WF-0136` (1 steps)
- *Micro script (Google Ads script para insights de Performance Max)* → `WF-0137` (1 steps)
- *Combinar PMax com standard shopping* → `WF-0138` (1 steps)
- *Escalonamento horizontal por localização via duplicação de campanha PMax* → `WF-0139` (10 steps)
- *Vantagem 2 do YouTube: reutilizar criativos (Meta winners → YouTube in-stream/Shorts)* → `WF-0140` (3 steps)
- *Curva de oferta e demanda em termos de quantidade de anunciantes por placement, problema/solução/CTA e produto* → `WF-0142` (2 steps)
- *Entender onde YouTube ads se encaixa no funil do Google Ads* → `WF-0143` (1 steps)
- *Diagrama/framework de funil de campanhas Google Ads* → `WF-0144` (8 steps)
- *Movie trailer style hook* → `WF-0145` (1 steps)
- *Fórmula de estrutura a ser usada em todo anúncio* → `WF-0146` (6 steps)
- *Funil de YouTube Ads (criativos → placements → funil)* → `WF-0147` (1 steps)
- *8 figure ecom YouTube ads swipe file* → `WF-0148` (2 steps)
- *new campaign (criação de campanha Demand Gen)* → `WF-0149` (16 steps)
- *hook tests* → `WF-0150` (1 steps)
- *Asset optimization* → `WF-0151` (5 steps)
- *Review a campaign / publish campaign* → `WF-0152` (1 steps)
- *Winning ad group* → `WF-0153` (7 steps)
- *Ordem de diagnóstico: view rate e depois CTR* → `WF-0154` (7 steps)
- *more, better, new* → `WF-0156` (4 steps)
- *traffic scaling* → `WF-0157` (4 steps)
- *CTR testing* → `WF-0158` (2 steps)
- *morally obligated to scale ad creative* → `WF-0159` (2 steps)
- *Estrutura de uma campanha CBO com ad groups de teste e de vencedores* → `WF-0161` (4 steps)
- *Optimized targeting* → `WF-0163` (10 steps)
- *welcome flow* → `WF-0164` (3 steps)
- *email popup* → `WF-0165` (1 steps)
- *post-purchase flow* → `WF-0167` (3 steps)
- *Auditoria da conta de Google Ads e dos MetaFunnels* → `WF-0168` (2 steps)
- *Auditoria de conta de Google Ads de marca* → `WF-0169` (3 steps)
- *Páginas de pré-venda, páginas educacionais, advertoriais e listicles* → `WF-0170` (2 steps)
- *Target impression share em posição absoluta no topo para campanhas de busca de marca* → `WF-0171` (11 steps)
- *Ordem dos mecanismos de conversão ('Use these in order')* → `WF-0172` (5 steps)
- *New customer conversion tag (setup técnico 2025)* → `WF-0173` (1 steps)
- *CRO mobile-optimized* → `WF-0174` (3 steps)
- *Playbook (seguir em ordem)* → `WF-0175` (8 steps)
- *Game plan: Passo um — segmentação de campanhas branded e unbranded* → `WF-0176` (1 steps)
- *Primeiro passo de execução — exclusão de termos de marca das campanhas relevantes* → `WF-0177` (7 steps)
- *Estabelecer o baseline de campanhas e, como primeiro passo seguinte, reconstruir a página de produto* → `WF-0178` (3 steps)
- *Full cold traffic conversion mechanism (mecanismo completo de conversão de tráfego frio)* → `WF-0179` (3 steps)
- *Reworking the funnel with evidence, clarity, and differentiation* → `WF-0180` (5 steps)
- *LTV engine (PMax transformado em motor de LTV)* → `WF-0181` (7 steps)
- *Mecanismo de tráfego + mecanismo de conversão* → `WF-0182` (2 steps)
- *Cold customer traffic funnel* → `WF-0183` (1 steps)

- Steps the source does not group under any named procedure → `WF-DEFAULT` (1 steps).

- Out-of-scope request: obey the scope guard in `knowledge/runtime-policy.yaml`.

## FAIL CLOSED

`METHOD_NOT_DEFINED` and `MISSING_REQUIRED_INPUT` are hard runtime stops when emitted by the routed policy. Do not bypass them with general knowledge.

If an executable decision/workflow resource required for the current request is unavailable, do not reconstruct it from this entrypoint, memory, or general knowledge; use the fail-closed behavior in `knowledge/runtime-policy.yaml`.

## RESPONSE DISCIPLINE

Preserve explicit user boundaries; never invent missing required inputs; distinguish source methodology from generic implementation suggestions.

## PILOT LIMITATION

Single-course pilot. Until an independent blind run succeeds, this runtime remains `S3_EXECUTABLE`, `production_ready: false`.
