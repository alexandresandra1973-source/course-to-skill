# COURSE-GAP-REPORT — PILOT-003-v2

*Gerado da compilação evidência→Skill. Nenhum número digitado.*

## Resumo

| | |
|---|---|
| regras | 835 |
| workflows | 158 |
| passos | 601 |
| evidências consumidas | 2211 de 2463 (89.8%) |
| **regras só de inferência genuína** | **29** |
| campos UNDEFINED | 4958 |

## Campos UNDEFINED — lacuna pedagógica

Os quatro preservados por decisão. Nenhum é metadado: os quatro são perguntas que a execução faz e o curso não responde.

| campo | vezes | a pergunta que o curso não responde |
|---|---|---|
| `missing_input_action` | 1430 | o que fazer quando falta um insumo obrigatório |
| `autonomy` | 1419 | até onde o agente pode agir sozinho antes de parar |
| `iteration_limit` | 1368 | quantas vezes repetir antes de desistir |
| `precedence` | 741 | qual regra ganha quando duas se aplicam |

> **Nenhum metadado nesta lista.** O esquema é subconjunto: os 30 campos legados que eram metadado foram descartados por decisão registrada, com o motivo escrito em `ctss/schema.py`. O que sobra aqui é lacuna do curso.

---

## Regras e passos que o curso NÃO ensinou

**45** entidades se apoiam SÓ em inferência genuína. Funcionam — mas o modelo as preencheu, não o curso. Para cada uma, a cadeia:

### `R-0024` — Gate para recursos avançados de alcance

**a regra diz:** Gasto atingiu dezenas de milhares por dia e há necessidade de mais alcance → Adotar recursos avançados de alcance; abaixo desse patamar, permanecer no núcleo essencial

> **o curso disse** (6:34): relevant when you're spending tens of thousands per day and you need more reach. Until then, just stick to the core free.

**o modelo concluiu:** Recursos avançados de alcance só se tornam relevantes quando o gasto atinge dezenas de milhares por dia; até lá, ficar no núcleo essencial

**distância:** o curso não nomeia 'recursos avançados de alcance'; o modelo inferiu do trecho sobre relevância ao gastar dezenas de milhares por dia e ficar no núcleo até lá

### `S-0024` — Montar topo de funil com demand gen

**a regra diz:** Configurar demand gen com YouTube Shorts, YouTube instream e Google Display → Configurar demand gen com YouTube Shorts, YouTube instream e Google Display

> **o curso disse** (13:46): So at the top you've got demand genen, which is about YouTube shorts, YouTube instream, and

**o modelo concluiu:** O topo do funil é demand gen, composto por YouTube Shorts, YouTube instream e Google Display

**distância:** o curso não completa a lista com Google Display; o modelo inferiu do trecho cortado após 'YouTube shorts, YouTube instream, and'

### `R-0038` — Retargetear dinamicamente abandono de add to cart

**a regra diz:** UNDEFINED → Retargetear dinamicamente o usuário de volta para a homepage ou para a página de produto

> **o curso disse** (14:12): ad to cart, then they get dynamically retargeted back to the homepage or the product page. And if they already are aware of your brand, branded search and

**o modelo concluiu:** Quem abandona o add to cart deve ser retargeteado dinamicamente de volta para a homepage ou para a página de produto

**distância:** o curso não prescreve o retargeting como dever; o modelo converteu em recomendação a descrição de que quem faz add to cart é retargeteado dinamicamente

### `R-0047` — Escalar vencedores e matar perdedores

**a regra diz:** Identificação do que está funcionando e do que não está → Escalar as campanhas vencedoras e encerrar as perdedoras

> **o curso disse** (17:06): You'll very quickly be able to see results in terms of what's working, what's not. So, you scale the winners, you kill off the loom

**o modelo concluiu:** O sistema permite ver resultados rapidamente sobre o que está funcionando e o que não está, de modo que se escala os vencedores e se mata os perdedores

**distância:** o curso não fala em "sistema" que permite isso; o modelo inferiu de frase sobre ver rápido resultados, escalar vencedores e cortar perdedores

### `R-0069` — ROAS alto demais: escalar

**a regra diz:** UNDEFINED → Escalar o investimento

> **o curso disse** (22:33): sometimes

**o modelo concluiu:** Às vezes o ROAS está simplesmente alto demais e o que se precisa é escalar.

**distância:** o curso não diz que o ROAS está alto demais nem que se deve escalar; o modelo inferiu tudo da palavra solta "sometimes"

### `R-0080` — Desconfiar de ROAS alto sem segmentação

**a regra diz:** Prospecção e proteção de marca não estão segmentadas → Tratar o ROAS aparentemente alto como possivelmente inflado por tráfego de marca

> **o curso disse** (24:33): And if you don't segment your prospecting and brand

**o modelo concluiu:** Sem segmentar prospecção e proteção de marca, o ROAS pode parecer alto mas será tráfego de marca

**distância:** o curso não diz que o ROAS parecerá alto por tráfego de marca; o modelo inferiu de frase cortada sobre não segmentar prospecção e marca

### `R-0093` — Lances inteligentes como alavanca de eficiência

**a regra diz:** UNDEFINED → Usar de forma inteligente lances por target ROAS e target CPA

> **o curso disse** (28:23): And with Google ads specifically, it comes from smart use of target rorow as

**o modelo concluiu:** No Google Ads, a eficiência vem do uso inteligente de lances por target ROAS e target CPA

**distância:** o curso não cita target CPA nem chama isso de eficiência; o modelo inferiu de menção ao uso inteligente de target ROAS

### `S-0059` — Introduzir YouTube e Demand Gen após esgotar Search, Shopping e PMax

**a regra diz:** Depois de esgotar o potencial de Search, Shopping e Performance Max, introduzir YouTube e Demand Gen para escalar além do limite de volume de busca já atingido → Depois de esgotar o potencial de Search, Shopping e Performance Max, introduzir YouTube e Demand Gen para escalar além do limite de volume de busca já atingido

> **o curso disse** (30:03): search, shopping, performance max, introduce YouTube, introduce demand genen, and you're able to scale past the search volume limit that you've hit.

**o modelo concluiu:** Depois de esgotar o potencial de Search, Shopping e Performance Max, introduzir YouTube e Demand Gen permite escalar além do limite de volume de busca já atingido

**distância:** o curso não diz que Search, Shopping e PMax foram esgotados antes; o modelo inferiu da lista de canais e do limite de volume de busca

### `R-0169` — Query convertedora vira keyword exato/frase

**a regra diz:** A query converteu em Shopping/PMax → Transformar a query em palavra-chave de correspondência exata e de frase em campanha de search

> **o curso disse** (49:45): You

then turn those converting queries into exact and phrase matching keywords instead of search campaigns.

**o modelo concluiu:** As queries que convertem devem ser convertidas em palavras-chave de correspondência exata e de frase em campanhas de search

**distância:** o curso diz "instead of search campaigns"; o modelo inverteu para dentro de campanhas de search

### `R-0189` — Contagem: cada conversão

**a regra diz:** UNDEFINED → Selecionar contar cada conversão (every single one)

> **o curso disse** (55:21): Count. You want to

**o modelo concluiu:** Na contagem (count), deve-se contar cada conversão (every single one).

**distância:** o curso não diz contar cada conversão; o modelo inferiu de "Count. You want to", frase interrompida

### `S-0133` — Criar ação begin checkout

**a regra diz:** Criar a terceira ação begin checkout com o mesmo processo, removendo das metas padrão, nomeando e configurando valor e contagem → Criar a terceira ação begin checkout com o mesmo processo, removendo das metas padrão, nomeando e configurando valor e contagem

> **o curso disse** (55:58): Now we need to add a begin checkout. Same process here. Get rid of it in count goals. Name it once it's named value count.

**o modelo concluiu:** A terceira ação é begin checkout, criada com o mesmo processo e removida das metas padrão da conta.

**distância:** o curso não indica que begin checkout seja a terceira ação; o modelo inferiu da sequência descrita ("Now we need to add")

### `S-0169` — Montar a composição do título

**a regra diz:** Compor o título incluindo as palavras-chave de maior volume, detalhes do produto (cor, tamanho), as palavras-chave de segundo maior volume, múltiplos ângulos e USPs, e o nome da marca → Compor o título incluindo as palavras-chave de maior volume, detalhes do produto (cor, tamanho), as palavras-chave de segundo maior volume, múltiplos ângulos e USPs, e o nome da marca

> **o curso disse** (67:42): 150 characters which has your highest volume keywords, any details around the product. to color, size, your second highest volume keywords, angles and

**o modelo concluiu:** A composição do título deve conter: as palavras-chave de maior volume, detalhes do produto (como cor e tamanho), as palavras-chave de segundo maior volume, múltiplos ângulos e USPs, e o nome da marca.

**distância:** o curso não cita nome da marca nem limite de 150 caracteres como composição completa; o modelo inferiu da lista de elementos citada

> **o curso disse** (68:16): They got the make of the actual product itself. Apple Watch band is the high volume keyword that we're targeting. We've got all the sizes, got

**o modelo concluiu:** Exemplo de título otimizado: inclui o 'make' do produto, a palavra-chave de alto volume ('Apple Watch band'), todos os tamanhos, e USPs combinados com a palavra-chave de alto volume, como '100% cotton' e livre de ftalatos.

**distância:** o curso não cita '100% cotton', livre de ftalatos nem USPs combinados; o modelo inferiu de make, keyword e tamanhos

### `R-0229` — ID e SKU imutáveis

**a regra diz:** Sempre → Manter ID e SKU inalterados; importar o ID do data feed via ferramenta (DataFeedWatch) ou diretamente do Shopify, o que ocorre automaticamente após vincular o GMC à conta Shopify

> **o curso disse** (71:57): You always want to make sure you're never changing the ID or the

**o modelo concluiu:** Nunca altere o ID nem o SKU do produto, pois isso quebra muitas coisas no funcionamento.

**distância:** o curso não menciona SKU nem que isso quebra coisas; o modelo inferiu de "nunca mude o ID"

> **o curso disse** (72:04): Have it just be imported from your data feed through some process of data feed watch or

**o modelo concluiu:** O ID deve ser importado do data feed, via ferramenta como DataFeedWatch ou diretamente do Shopify, o que ocorre automaticamente após vincular o GMC à conta Shopify.

**distância:** o curso não menciona Shopify nem automatismo após vincular GMC; o modelo inferiu de "importado do feed via DataFeedWatch"

### `R-0363` — Exceção: grupo único em campanha de branding

**a regra diz:** Trata-se de campanha de branding → É aceitável colocar todos os produtos em um único grupo e dar lance nos termos de marca; pode funcionar melhor

> **o curso disse** (116:36): But because it's a branding campaign, you can just have all your products in one group and just build on your branded

**o modelo concluiu:** Como exceção, em campanha de branding é aceitável colocar todos os produtos em um único grupo e dar lance nos termos de marca — isso pode funcionar melhor.

**distância:** o curso não ensina que isso é exceção e 'pode funcionar melhor'; o modelo inferiu da fala de que em campanha de branding basta um grupo com todos os produtos

### `R-0413` — Custo por conversão acima da taxa de conversão

**a regra diz:** Termo tem taxa de conversão menor mas é mais congruente com a oferta → Avaliar o termo pelo custo por conversão, que pode ser menor apesar da taxa de conversão inferior

> **o curso disse** (130:30): And even though this has a lower

**o modelo concluiu:** Um termo pode ter taxa de conversão menor e ainda assim ter custo por conversão menor, por ser mais congruente com a oferta

**distância:** o curso não afirma custo por conversão menor por maior congruência com a oferta; o modelo inferiu da frase truncada 'even though this has a lower'

### `S-0331` — Projetar resultado anual a partir dos dados do teste

**a regra diz:** Extrapolar os dados de 3 semanas para o ano: ~50.000 impressões/ano, aplicar CTR de 10% para obter ~5.000 visitantes à página, com CPC de $0,32 → Extrapolar os dados de 3 semanas para o ano: ~50.000 impressões/ano, aplicar CTR de 10% para obter ~5.000 visitantes à página, com CPC de $0,32

> **o curso disse** (131:10): this is only the course of the last 3 weeks. Over the course of the year, you're going to get like 50,000

**o modelo concluiu:** Projeta-se resultado anual extrapolando os dados de 3 semanas: ~50.000 impressões por ano, a 10% de CTR, gerando ~5.000 visitantes à página a $0,32 de CPC

**distância:** o curso não menciona CTR de 10%, 5.000 visitantes nem CPC de $0,32; o modelo inferiu da projeção de 50.000 anuais a partir de 3 semanas

### `R-0450` — Descartar o canal quando o CPA de break-even não é sustentável

**a regra diz:** Mesmo com a campanha configurada corretamente, o negócio não consegue sustentar o nível de CPA da plataforma → Não anunciar nesse canal

> **o curso disse** (140:25): But even if you set it up right and you can sustain that level of CPA, then there's probably just no point in advertising on that channel in the first place.

**o modelo concluiu:** Se, mesmo com a configuração correta, o negócio não consegue sustentar o nível de CPA da plataforma, então não faz sentido anunciar nesse canal

**distância:** o curso diz o oposto literal ('even if you can sustain'); o modelo inferiu a negação 'não consegue sustentar' para dar sentido à frase

### `R-0513` — Critério de manutenção de URLs de melhor desempenho

**a regra diz:** URL está entre as de melhor desempenho → Manter aberta ao tráfego; excluir qualquer URL que possa diluir os resultados

> **o curso disse** (156:25): Keep your

**o modelo concluiu:** O critério geral é manter as URLs de melhor desempenho abertas ao tráfego e excluir qualquer coisa que possa diluir os resultados

**distância:** o curso não enuncia critério sobre URLs de melhor desempenho e exclusão de diluidoras; o modelo inferiu do fragmento 'Keep your'

### `R-0522` — Leitura do MER como sinal de sustentabilidade

**a regra diz:** MER alto → Interpretar como indicação de que os esforços de marketing são sustentáveis e eficientes

> **o curso disse** (159:50): A high me shows your marketing efforts are

**o modelo concluiu:** Um MER alto indica que os esforços de marketing são sustentáveis e eficientes.

**distância:** o curso não ensina que MER alto indica sustentabilidade e eficiência; o modelo inferiu de frase truncada 'a high MER mostra que seus esforços de marketing são'

### `R-0524` — Bloqueio de escala sem break-even CPA conhecido

**a regra diz:** O break-even CPA não foi calculado/não é conhecido → Não escalar; calcular primeiro o break-even CPA

> **o curso disse** (160:10): If you don't

**o modelo concluiu:** Sem conhecer o break-even CPA é impossível escalar em Google Ads, Facebook Ads ou qualquer canal

**distância:** o curso não menciona Google Ads, Facebook Ads ou impossibilidade de escalar; o modelo inferiu de fragmento 'If you don't'

### `S-0420` — Definir o significado operacional do break-even CPA

**a regra diz:** Estabelecer o break-even CPA como o valor máximo que se pode gastar para adquirir um cliente sem perder dinheiro, seja na primeira compra ou considerando a razão com o LTV → Estabelecer o break-even CPA como o valor máximo que se pode gastar para adquirir um cliente sem perder dinheiro, seja na primeira compra ou considerando a razão com o LTV

> **o curso disse** (160:10): This is the maximum you can spend to acquire a customer without losing money whether on first purchase or even an encounter to LTB ratio.

**o modelo concluiu:** Break-even CPA é definido como o valor máximo que se pode gastar para adquirir um cliente sem perder dinheiro, seja na primeira compra ou considerando a razão com o LTV

**distância:** o curso não nomeia esse conceito como break-even CPA na citação; o modelo inferiu de definição de gasto máximo sem perder dinheiro

### `S-0423` — Usar a planilha de cálculo

**a regra diz:** Utilizar a planilha disponibilizada para o cálculo, cujo link está na descrição, como alternativa ao cálculo manual → Utilizar a planilha disponibilizada para o cálculo, cujo link está na descrição, como alternativa ao cálculo manual

> **o curso disse** (160:25): Again, there's a spreadsheet for

**o modelo concluiu:** Existe uma planilha para esse cálculo, com link na descrição

**distância:** o curso não menciona link na descrição; o modelo inferiu de 'existe uma planilha para'

### `S-0427` — Monitorar MER global

**a regra diz:** Como passo final, monitorar o MER como métrica de eficiência global do negócio, englobando Meta Ads, TikTok, orgânico, Klaviyo (e-mail) e Google → Como passo final, monitorar o MER como métrica de eficiência global do negócio, englobando Meta Ads, TikTok, orgânico, Klaviyo (e-mail) e Google

> **o curso disse** (161:48): And then finally, you want to monitor me for overall

**o modelo concluiu:** O passo final é monitorar o MER como métrica de eficiência global do negócio.

**distância:** o curso não ensina que o MER é métrica de eficiência global do negócio; o modelo inferiu de 'monitor me for overall' no fim

> **o curso disse** (161:54): This is including your meta ads, your Tik Tok, your organic, your clavio, and your Google.

**o modelo concluiu:** O cálculo de eficiência global deve englobar todas as fontes: Meta Ads, TikTok, orgânico, Klaviyo (e-mail) e Google.

**distância:** o curso não ensina que essa lista compõe o cálculo de eficiência global nem que Klaviyo é e-mail; o modelo inferiu da simples enumeração de canais

### `R-0537` — Subgasto (<80%) com performance ruim → afrouxar alvo

**a regra diz:** Performance está ruim (underperforming) → Reduzir o tROAS ou o tCPA para ampliar o alcance e gerar mais volume

> **o curso disse** (163:12): daily budget and underperforming, you want to lower the Tro ads or TCPA to widen reach and prove more volume.

**o modelo concluiu:** Se você gasta menos de 80% do orçamento diário e a performance está ruim, reduza o tROAS ou o tCPA para ampliar o alcance e gerar mais volume.

**distância:** o curso não cita o limiar de 80% do orçamento diário; o modelo inferiu de gastar abaixo do orçamento com baixa performance e baixar tROAS/tCPA

### `R-0549` — Rastrear ROAS de novos clientes separadamente

**a regra diz:** UNDEFINED → Acompanhar o ROAS de novos clientes como métrica separada do ROAS geral da conta

> **o curso disse** (166:30): 1.19x new customer rorowaz

**o modelo concluiu:** O ROAS de novos clientes é acompanhado como métrica separada do ROAS geral da conta (1,19x de ROAS de novo cliente contra 1,29x geral no caso).

**distância:** o curso não diz que é métrica separada acompanhada nem compara com o ROAS geral; o modelo inferiu do número isolado 1,19x de novo cliente

### `R-0575` — CTA para varejo quando há presença em varejo

**a regra diz:** Há um bom CTA direcionando ao varejo → Usar CTA direcionando ao varejo, esperando aumento em vendas no varejo, em DTC e na conversão no Meta

> **o curso disse** (173:41): have a good CTA to retail and you're in retail, that also increases and then your DC also increases as well as the conversion on your metas.

**o modelo concluiu:** Com um bom CTA direcionando ao varejo, e estando presente no varejo, as vendas no varejo aumentam, o DTC aumenta e a conversão no Meta também

**distância:** o curso não especifica que são vendas no varejo que sobem; o modelo inferiu de 'you're in retail, that also increases'

### `R-0589` — Alternativa de mecanismo de conversão à página de produto

**a regra diz:** UNDEFINED → Usar outro mecanismo de conversão como destino: advertorial, listicle, VSL ou quiz funnel

> **o curso disse** (177:42): mechanism, advertorial, listical, VSSL, quizfunnel.

**o modelo concluiu:** Como alternativa à página de produto, pode-se usar outro mecanismo de conversão: advertorial, listicle, VSL ou quiz funnel.

**distância:** o curso não apresenta esses formatos como alternativa à página de produto; o modelo inferiu da lista 'mechanism, advertorial, listicle, VSL, quiz funnel'

### `S-0455` — Teste rápido de criativos por volume

**a regra diz:** Direcionar muitos cliques e volume para cada criativo para descobrir rapidamente quais funcionam, garantindo que a configuração esteja correta → Direcionar muitos cliques e volume para cada criativo para descobrir rapidamente quais funcionam, garantindo que a configuração esteja correta

> **o curso disse** (178:47): And you're able to test really quickly which creatives do well by putting in a

**o modelo concluiu:** É possível testar rapidamente quais criativos funcionam ao direcionar muitos cliques e volume para cada criativo, se a configuração estiver correta

**distância:** o curso não ensina que basta direcionar muitos cliques e volume por criativo com a configuração correta; o modelo inferiu de menção a testar criativos rapidamente

> **o curso disse** (178:34): Have lots of volume so you get a lot of clicks very

**o modelo concluiu:** Shorts têm muito volume e geram cliques muito baratos, da ordem de 1 a 2 centavos

**distância:** o curso não cita Shorts nem cliques de 1 a 2 centavos; o modelo inferiu de 'lots of volume so you get a lot of clicks'

### `R-0612` — Exceção de autenticidade do fundador

**a regra diz:** O conteúdo vem do fundador e portanto é percebido como autêntico → Aceitar que o criativo ainda pode funcionar apesar da baixa produção

> **o curso disse** (182:06): it's authentic because it's from the founder.

**o modelo concluiu:** Anúncio gerado por IA com legendas ruins ainda pode funcionar por ser autêntico quando vem do fundador

**distância:** o curso não ensina que anúncio gerado por IA com legendas ruins funciona; o modelo inferiu de "é autêntico porque vem do fundador"

### `S-0463` — CTA final forte

**a regra diz:** Encerrar o anúncio com um CTA forte → Encerrar o anúncio com um CTA forte

> **o curso disse** (182:34): And then you

**182:41**

need a strong ad as stock CTA

**o modelo concluiu:** O anúncio precisa terminar com um CTA forte

**distância:** o curso não diz que o CTA deve vir no fim do anúncio; o modelo inferiu de "precisa de um CTA forte"

### `R-0661` — Avaliar view rate contra benchmark por placement

**a regra diz:** View rate em 10% no Shorts ou 20% em instream → Considerar o view rate como bom

> **o curso disse** (189:30): If you're at 10% on shorts and 20% on Instagram,

**o modelo concluiu:** Benchmark de view rate considerado bom: 10% em Shorts e 20% em instream.

**distância:** o curso não identifica a métrica como view rate boa nem diz que 20% é instream (fala Instagram); o modelo inferiu dos números citados

### `R-0683` — Obter dados de atribuição via Triple

**a regra diz:** Modelo de atribuição em uso definido → Usar a ferramenta Triple (Triple Whale) para obter os dados conforme o modelo de atribuição utilizado

> **o curso disse** (192:39): Triple will be able to get all of

**o modelo concluiu:** A ferramenta Triple (Triple Whale) consegue fornecer todos esses dados conforme o modelo de atribuição que você estiver usando.

**distância:** o curso não menciona modelo de atribuição nem Triple Whale; o modelo inferiu de 'Triple conseguirá obter todos os'

### `R-0693` — Diagnóstico inicial por métricas ruins

**a regra diz:** UNDEFINED → Iniciar o diagnóstico examinando view rate baixo e CTR baixo

> **o curso disse** (194:31): So if you have poor metrics, so pure view rate, poor CTR, no

**o modelo concluiu:** O diagnóstico de métricas ruins começa examinando view rate e CTR baixos

**distância:** o curso não apresenta isso como início de um diagnóstico; o modelo inferiu de 'se você tem métricas ruins, view rate e CTR ruins'

### `S-0511` — Examinar view rate e CTR

**a regra diz:** Diante de métricas ruins, examinar view rate e CTR baixos como ponto de partida do diagnóstico → Diante de métricas ruins, examinar view rate e CTR baixos como ponto de partida do diagnóstico

> **o curso disse** (194:31): So if you have poor metrics, so pure view rate, poor CTR, no

**o modelo concluiu:** O diagnóstico de métricas ruins começa examinando view rate e CTR baixos

**distância:** o curso não apresenta isso como início de um diagnóstico; o modelo inferiu de 'se você tem métricas ruins, view rate e CTR ruins'

### `R-0707` — Lucratividade no primeiro pedido com recompra de 30 dias aumenta segurança para escalar

**a regra diz:** A conta é lucrativa no primeiro pedido e o produto é recomprado a cada ~30 dias (LTV subsequente muito alto) → Tratar a conta como mais segura para escalar

> **o curso disse** (196:45): CPA to be first order profitable. So, we are first order profitable on a product which people buy every single 30 days. And because we know our LTB is cracked

**o modelo concluiu:** Ser lucrativo no primeiro pedido em um produto recomprado a cada 30 dias torna a conta ainda mais segura para escalar, porque o LTV subsequente é muito alto.

**distância:** o curso não afirma que isso torna a conta mais segura para escalar nem que o LTV é altíssimo; o modelo inferiu de 'LTB is cracked'

### `S-0528` — Montar blocos iniciais da landing page

**a regra diz:** Estruturar a página em sequência longa de blocos: seção above the fold, todos os diferentes produtos, resultados de laboratório, FAQs, banners, passos simples, diferenciação, prova social, linhas de tempo e jornadas, pesquisas e estudos → Estruturar a página em sequência longa de blocos: seção above the fold, todos os diferentes produtos, resultados de laboratório, FAQs, banners, passos simples, diferenciação, prova social, linhas de tempo e jornadas, pesquisas e estudos

> **o curso disse** (197:24): So, it's got the above the poll section, all the different products, lab results, FAQs,

**o modelo concluiu:** A landing page é composta por uma sequência longa de blocos: seção above the fold, todos os diferentes produtos, resultados de laboratório, FAQs, banners, passos simples, diferenciação, prova social, linhas de tempo e jornadas, pesquisas e estudos.

**distância:** o curso não lista banners, passos simples, diferenciação, prova social, timelines nem pesquisas; a citação cita apenas above the fold, produtos, lab results e FAQs

### `R-0723` — Espera de 25 dias antes do e-mail de estoque no post-purchase

**a regra diz:** UNDEFINED → Aplicar espera (weight) de 25 dias com foco em incentivar o cliente a estocar o produto (stocking up)

> **o curso disse** (198:51): there's a free email deep post purchase flow with a 25-day weight in terms of stocking up and a replenishment email on top of that post purchase as well.

**o modelo concluiu:** O post-purchase flow tem três e-mails, com uma espera de 25 dias focada em incentivar o cliente a estocar o produto

**distância:** o curso não diz que o fluxo tem três e-mails; o modelo inferiu de 'free email deep post purchase flow' mais a menção ao e-mail de reposição adicional

### `S-0536` — Montar post-purchase flow com três e-mails

**a regra diz:** Construir o post-purchase flow com três e-mails, incluindo a espera de 25 dias voltada ao stocking up → Construir o post-purchase flow com três e-mails, incluindo a espera de 25 dias voltada ao stocking up

> **o curso disse** (198:51): there's a free email deep post purchase flow with a 25-day weight in terms of stocking up and a replenishment email on top of that post purchase as well.

**o modelo concluiu:** O post-purchase flow tem três e-mails, com uma espera de 25 dias focada em incentivar o cliente a estocar o produto

**distância:** o curso não diz que o fluxo tem três e-mails; o modelo inferiu de 'free email deep post purchase flow' mais a menção ao e-mail de reposição adicional

### `R-0727` — Condicionar existência de shopping campaign ao status do Merchant Center

**a regra diz:** A conta de Merchant Center (GMT) ainda não foi banida → Esperar/considerar a existência de uma shopping campaign na estrutura; se banida, a shopping campaign não estará presente

> **o curso disse** (200:10): If your GMT isn't banned yet, then you're going to have a shopping campaign.

**o modelo concluiu:** A presença de campanha de shopping depende de a conta do Merchant Center ainda não ter sido banida (o literal fala de 'GMT' banido).

**distância:** o curso não define GMT como conta do Merchant Center; o modelo inferiu de 'if your GMT isn't banned yet, you're going to have a shopping campaign'

### `R-0747` — Sinal de anti-padrão em contas herdadas de agência

**a regra diz:** Há overspend histórico em brand e search impression share muito ruim → Tratar como anti-padrão e revisar a campanha de brand

> **o curso disse** (204:45): really mess heavy brands, they may had an agency run their stuff. They've overspent on brand. You take a look at it, the search impression share is

**o modelo concluiu:** Anti-padrão observado: marcas grandes cujas contas foram geridas por agência gastaram demais em brand e ainda assim têm search impression share muito ruim

**distância:** o curso não qualifica as marcas como grandes nem completa que o impression share é muito ruim; o modelo inferiu de fala truncada sobre agência e overspend

### `S-0566` — 3. Testar mecanismos na ordem definida

**a regra diz:** Testar os mecanismos de conversão nesta ordem: sales page aprimorada, advertorial, quiz funnel, VSL → Testar os mecanismos de conversão nesta ordem: sales page aprimorada, advertorial, quiz funnel, VSL

> **o curso disse** (213:06): their dry aviator or quiz funnel let's call them BSL in this order you want optimize your CRO iterating the creators from awareness

**o modelo concluiu:** A sequência de mecanismos de conversão a testar é: sales page aprimorada, depois advertorial, depois quiz funnel, depois VSL, nessa ordem.

**distância:** o curso não lista 'sales page aprimorada' como primeiro passo nem nomeia VSL; o modelo inferiu de 'dry aviator or quiz funnel... BSL in this order'

### `S-0585` — Cobrir todas as etapas do funil do mecanismo

**a regra diz:** Atuar em media buying, pre-sale pages, página de produto, checkout e aftersell, visando aumentar AOV, reduzir CAC e adquirir novos clientes → Atuar em media buying, pre-sale pages, página de produto, checkout e aftersell, visando aumentar AOV, reduzir CAC e adquirir novos clientes

> **o curso disse** (223:12): media buying, the pre-sale pages, the actual product page itself, the order, the afterell to increase AOV, to drop CAC to acquire new customers and to be

**o modelo concluiu:** O mecanismo abrange media buying, pre-sale pages, a própria página de produto, o checkout e o aftersell, com objetivos de aumentar AOV, reduzir CAC e adquirir novos clientes

**distância:** o curso não fala em checkout; o modelo inferiu de 'the order' na lista de etapas do mecanismo

### `S-0594` — Transformar PMax em motor de LTV

**a regra diz:** Construir o front end para adquirir e o back end para retiner, transformando a campanha PMax em motor de LTV → Construir o front end para adquirir e o back end para retiner, transformando a campanha PMax em motor de LTV

> **o curso disse** (227:48): And we transformed the PMAX campaign into our LTV engine. We built the front end to quad and back end

**o modelo concluiu:** A campanha PMax foi transformada em um motor de LTV: front end construído para adquirir e back end para retiner.

**distância:** o curso não ensina que o front end serve para adquirir e o back end para reter; o modelo inferiu de "front end to quad and back end", frase truncada

### `R-0832` — Escalar o criativo aprovado mesmo com histórico fraco no Meta

**a regra diz:** Esse criativo teve performance fraca no Meta → Escalar esse criativo no Google mesmo assim

> **o curso disse** (229:04): running on meta only works on Google right now. We're scaling that one and that wasn't doing really well.

**o modelo concluiu:** De todo o lote de anúncios que rodam no Meta, apenas um funciona no Google atualmente; é justamente esse que está sendo escalado, mesmo tendo performance fraca no Meta.

**distância:** o curso não ensina que se trata de um lote de anúncios do Meta com desempenho fraco lá; o modelo inferiu de "only works on Google" e "wasn't doing really well"

### `R-0835` — Diversificar concentração de mídia via funil de YouTube

**a regra diz:** UNDEFINED → Construir um funil de campanha no YouTube para a marca

> **o curso disse** (229:58): They were running 95%

**o modelo concluiu:** Caso de outra marca: ela estava com 95% do investimento concentrado no Meta e a agência construiu um funil de campanha no YouTube para ela.

**distância:** o curso não ensina que os 95% eram investimento em Meta de outra marca com funil de YouTube criado; o modelo inferiu de "They were running 95%"

> **o curso disse** (230:05): on Meta. We've now built a YouTube campaign funnel for them. Just the ads of Media B. We're already at 2 hours on YouTube and their break even is like 1.2

**o modelo concluiu:** Nesse caso, o funil de YouTube já entrega ROAS de 2 enquanto o break-even da marca é 1,2–1,3, o que abre folga para escalar de forma muito agressiva.

**distância:** o curso não ensina break-even de 1,3 nem folga para escalar agressivamente; o modelo inferiu de ROAS 2 no YouTube e break-even 1,2

---

## Evidência não consumida

| disposição | n | significado |
|---|---|---|
| NON_METHODOLOGICAL | 229 | contexto, motivação, mercado — não é método |
| GAP | 23 | é método, mas a fonte não dá o suficiente |

### Método que a fonte menciona sem especificar

| onde | o que o curso disse |
|---|---|
| **0:33** | KPIs devem ser entendidos de uma forma avançada específica para e-commerce, e não no nível básico ensinado nos |
| **29:23** | O Google funciona melhor quando tem demanda para capturar |
| **32:24** | Nove pontos são apresentados como o conjunto completo de focos para escalar uma marca de e-commerce no Google  |
| **53:39** | O objetivo declarado do procedimento é levar o aluno de nenhum rastreamento de conversão até rastreamento de c |
| **53:59** | A configuração completa de rastreamento consiste em quatro tags: purchase, add to cart, product view e begin c |
| **54:06** | Além das tags de conversão, a configuração inclui remarketing dinâmico do Google Ads e Google Analytics 4. |
| **59:50** | O processo apresentado para o Merchant Center é o SOP interno usado na Demand Capture para "bulletproof" a con |
| **65:46** | Deve-se verificar quais avaliações foram reprovadas ou têm problemas, distinguindo umas das outras |
| **81:47** | O período de devolução deve estar atualizado conforme as melhores práticas de mercado. |
| **131:31** | Otimizações adicionais de COGS e de back end foram feitas na campanha, mas não foram detalhadas na demonstraçã |
| **141:13** | PMAX pode ser escalado agressivamente; o autor cita uma conta PMAX com orçamento de 20 mil por dia |
| **141:20** | PMAX preenche uma lacuna específica do funil dentro do motor de crescimento de e-commerce com Google Ads |
| **143:10** | Um dos maiores erros em PMAX é deixá-la desperdiçar orçamento em produtos que não vão vender ou que não são ge |
| **148:09** | Será necessário fazer outras ações além das exclusões de marca para eliminar os termos de marca, apresentadas  |
| **158:45** | O que o curso entrega são razões (ratios) e um sistema de sinalização verde/amarelo/vermelho para decidir como |
| **170:36** | A vantagem seguinte é a arbitragem de CPM: os CPMs de anúncios no YouTube são extremamente baixos |
| **183:41** | Os tópicos considerados componentes do domínio de Google Ads para e-commerce incluem: básico de Google Ads, pe |
| **188:06** | Após a configuração da campanha, há seis KPIs e métricas que precisam ser acompanhados. |
| **195:14** | Os demais anúncios do conjunto ainda não atingiram o patamar dos vencedores, mas estão subindo em performance. |
| **201:53** | O gap dessas marcas é não saber traduzir criativos e landing pages já existentes para o YouTube, onde funciona |

