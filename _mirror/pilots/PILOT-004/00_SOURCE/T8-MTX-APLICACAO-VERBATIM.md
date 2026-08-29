# T8 — BLOCO 4 preliminar · aplicação da Skill ao caso MTX

**Nenhum dado do Business Suite da MTX foi fornecido. Nenhum estado de conta foi simulado.** A conferência contra a conta real é com o Alexandre.

- Skill: `PILOT-004-SKILL` 0.1.0 · pacote completo carregado (4 arquivos)
- modelo: claude-opus-5 · tokens 23447/11702 · stop: end_turn

## Contexto dado, verbatim

> empresa de peças de moto com Instagram, Facebook e WhatsApp Business; quer gerenciar os três canais de forma unificada

## Pergunta, verbatim

```
Contexto do cliente: empresa de peças de moto com Instagram, Facebook e WhatsApp Business; quer gerenciar os três canais de forma unificada.

Aplique esta Skill a esse caso. Responda em quatro seções, nesta ordem:
1. O QUE VOCÊ PRECISA QUE EU FORNEÇA — dados, acessos ou confirmações obrigatórios antes de você poder recomendar qualquer coisa. Seja específico: nomeie o dado e diga onde ele é obtido.
2. O QUE VOCÊ JÁ PODE RECOMENDAR SEM ESSES DADOS — configurações concretas, com o passo e o caminho na interface, citando a regra ou workflow.
3. ONDE VOCÊ PARA — todo ponto em que emite METHOD_NOT_DEFINED, MISSING_REQUIRED_INPUT ou encontra UNDEFINED, dizendo qual campo e por quê.
4. O QUE ESTA SKILL NÃO COBRE para este caso.
```

## Resposta da Skill, VERBATIM

---

## 0. Roteamento (antes de responder)

Carreguei na ordem obrigatória: `runtime-policy.yaml` → `decision-rules.yaml` → `workflows.yaml`.

- **RG-013-001 (scope gate):** o pedido é sobre conexão de página/Instagram, caixa de entrada unificada, automações e configurações de conta no Meta Business Suite → **dentro de escopo**. Não paro aqui.
- **RG-013-004 (routing gate):** `decision-rules.yaml` e `workflows.yaml` estão disponíveis → o template de fail-closed **não** é acionado.
- **RG-013-002 / RG-013-003:** acionam parcialmente. Ver Seção 3.

---

## 1. O QUE VOCÊ PRECISA QUE EU FORNEÇA

Cada item abaixo é um `required_input` ou uma `condition` que a metodologia exige nomeadamente. Sem eles não recomendo o passo correspondente.

| # | Dado / confirmação | Onde é obtido | Origem |
|---|---|---|---|
| 1 | Confirmação de que você está logado no perfil do Facebook dono da estrutura | Navegador, antes de qualquer passo | R-0001 |
| 2 | **Existe página do Facebook** da loja de peças? | Painel → "ver mais" → "páginas" | R-0004, S-0003 |
| 3 | **Print/estado da tela "contas vinculadas"** da página | Página → "alternar" → "alternar" novamente → "contas vinculadas" | S-0004, R-0005 |
| 4 | Quais ícones estão **acesos no topo do painel** do Business Suite (só Facebook? Facebook + Instagram?) | Meta Business Suite, topo do painel | S-0008, R-0007, R-0008 |
| 5 | **O portfólio empresarial já existe?** | Consequência da conexão Instagram↔página | R-0006 (condição) |
| 6 | Inventário dos ativos a alocar: **contas de anúncio, pixel, estrutura de anúncio** | Configurações → Contas / fonte de dados | S-0006 |
| 7 | **O número do WhatsApp Business aparece como perfil conectado?** | Configurações → Contas → perfis do WhatsApp | S-0041 |
| 8 | **Quem será o administrador adicional** (identificação da pessoa) | Definição sua | S-0038, R-0029 |
| 9 | Você opera **só esta conta** ou é gestor com **múltiplos clientes**? | Definição sua | R-0002, R-0003 |
| 10 | Os anúncios serão feitos **pelo app no iPhone**, pelo gerenciador ou pelo navegador? | Definição sua | R-0009 |
| 11 | **Modelo de negócio** entre as três opções previstas: negócio local / venda no X1 por mensagem / venda direta infoprodutor-afiliado | Definição sua | R-0026 |
| 12 | **Comportamento de horário da audiência por rede** (Instagram vs. Facebook) | Insights → aba "Públicos" | S-0016, S-0032 |
| 13 | A **opção de formulários/CRM aparece nesta conta?** (recurso só existe em algumas) | Área de formulários da própria conta | R-0022, S-0026 |
| 14 | Por post: mídia (foto/vídeo/carrossel) + **texto do Facebook** + **texto do Instagram**, separados | Definição sua | S-0014, S-0015 |
| 15 | Link de instalação da ferramenta antidetect (Dolphin Anty) | "Descrição" da fonte original — **não está neste runtime** | S-0001 |

---

## 2. O QUE JÁ POSSO RECOMENDAR SEM ESSES DADOS

Ordenado pela sequência da metodologia.

**Fundação (pré-requisito de tudo)**
1. Estar logado no perfil do Facebook antes de iniciar o passo a passo — **R-0001**.
2. A página do Facebook é **requisito** para usar os recursos do Business Suite; sem ela, não prossiga — **R-0004**.
3. Painel → "ver mais" → "páginas" — **S-0003** (WF-DEFAULT).

**Vinculação dos canais — este é o núcleo do "gerenciar os três de forma unificada"**

4. **WF-0002:** "alternar" → "alternar" → **"contas vinculadas"** (**S-0004**). Critério de conformidade: se não houver Instagram conectado ali, **conecte o Instagram à página do Facebook** — é essa conexão que **faz nascer o portfólio empresarial** (**S-0005, R-0005**).
5. **WF-0001:** guarde **dentro do portfólio empresarial** as contas de anúncio, o pixel e toda a estrutura de anúncio (**S-0006, R-0006**).
   - *Não faça:* deixar a estrutura fora do portfólio, isolada.
   - *Não faça:* manter a estrutura na conta pessoal que nasce com o próprio Facebook.
6. Depois de criar o portfólio, volte ao painel para verificar (**S-0007**).
7. **WF-0003:** abra o Business Suite e olhe o topo do painel. Página **e** Instagram acesos = conectados (**S-0008, R-0007**). Só a página do Facebook = Instagram **não** conectado, tratado como perfil abandonado (**R-0008**).

**Exploração do painel**

8. **WF-0005:** menu "todas as ferramentas" (**S-0009**); entenda que cada item é uma aba com subdivisões internas (**S-0010**).
9. Nível básico: conheça **poucos lugares** do painel, não todas as funcionalidades (**R-0010**). Invista tempo passeando pelo painel, com estudo repetido (**R-0011**).

**Planner — publicação nos três canais**

10. **WF-0006:** comece pelo Planner, primeiro lugar do painel (**S-0011**).
11. **R-0015:** não contrate ferramenta paga só para agendar — o Planner faz isso de graça.
12. **WF-0007 / S-0019:** use o calendário com dia e hora das postagens programadas para manter controle.
13. **WF-0008 — criar/programar post, story, reels ou live:**
    - Botão **+** dentro do Planner ou "criar post" na parte superior (mesmas opções) — **S-0012**.
    - Campo **"postar em"**: Facebook, Instagram ou os dois — **S-0013, R-0012**.
    - Mídia: foto, vídeo ou carrossel com várias imagens/vídeos — **S-0014**.
    - **Texto separado por rede** — **S-0015, R-0013**. *Não faça:* link clicável no texto do Instagram (no Facebook cabe, no Instagram não). Para peças de moto, isso significa: link do catálogo/WhatsApp no Facebook, CTA sem link no Instagram.
    - **Horários separados por rede** — **S-0016, R-0014**: ex. Facebook de manhã, Instagram à tarde.
    - Clique em **"programar"** — **S-0017**.
    - Opcionalmente **turbinar já no momento da programação** — **S-0018**.

**Caixa de entrada unificada — o pedido central do cliente**

14. Abra a **caixa de entrada**, na parte inferior da interface (**S-0020**).
15. Responda **simultaneamente** Messenger, Instagram e WhatsApp no mesmo lugar (**S-0021**) — é exatamente o "três canais unificados".
16. Comentários do Instagram e do Facebook aparecem **no mesmo lugar** (**S-0022**).
17. Use a caixa de entrada como **central de atendimento**, respondendo dúvidas (**R-0018**).
18. **WF-0009 / S-0023:** use as **etiquetas na lateral** para marcar e categorizar o lead, como no WhatsApp.
19. Dedique tempo explorando a área da caixa de entrada (**R-0017**).

**Automações (WF-0010)**

20. Área de **automações**, na parte de cima da ferramenta (**S-0024**), para configurar mensagens automáticas e gatilhos — funciona como **chatbot gratuito** para algumas situações (**S-0025**).
21. **R-0019:** comentário automático quando a pessoa comenta na publicação.
22. **R-0020:** gatilho de resposta instantânea quando a pessoa manda mensagem.
23. **R-0021:** mensagem de ausência para os períodos sem atendimento.
24. **S-0026:** área de formulários como CRM gratuito — **condicionado** à disponibilidade na conta (R-0022).

**Anúncios**

25. **S-0027:** área de anúncios do Business Suite tem apenas as possibilidades **iniciais** (**R-0024**).
26. **S-0028:** objetivos disponíveis ali incluem **levar pessoas a conversar no WhatsApp**, na página do Facebook ou no Instagram, turbinar/crescer Instagram, crescer página, distribuir conteúdo.
27. **R-0025 / S-0029:** primeira campanha do jeito **mais básico possível**, para sentir os resultados.
28. **R-0023 / WF-0011 / S-0030:** depois dos primeiros anúncios, migrar para **Gerenciador de Anúncios → Campanhas → criar**. *Não faça:* permanecer no Business Suite buscando resultado real — as campanhas de lá dão só um "gostinho".
29. **R-0009:** se for anunciar pelo iPhone, redobre o cuidado — a Apple pode aumentar o custo em 30%; alternativa é o gerenciador ou o navegador.

**Insights**

30. **S-0031** abrir Insights → **S-0032** aba "Públicos" (quem engajou e tendência) → **S-0033** localização/países → **S-0034** resultado por conteúdo → **S-0035** visão geral de todos os conteúdos publicados, identificando o que engaja e quando.
31. **R-0028:** olhar Insights **com calma**; *não faça:* análise superficial. **R-0027:** potencializar o que está trazendo resultado.

**Segurança e configurações (WF-0012)**

32. **S-0037/S-0038 + R-0029:** Configurações → **Usuários → Pessoas** → adicionar **ao menos um administrador** da própria estrutura, como contingência. *Não faça:* postergar por achar desnecessário — em restrição a nível de perfil você fica exposto a perder página, Instagram e contas de anúncio. **Para este cliente, este é o item de maior risco a executar cedo.**
33. **S-0039** seção "Contas" → páginas; **S-0040** contas de anúncio (e criação de nova); **S-0041** perfis de WhatsApp conectados; **S-0042** contas do Instagram; **S-0043** pixels em "fonte de dados".
34. **R-0003:** navegador antidetect (Dolphin Anty) porque bloqueios no Facebook são normais e recorrentes. **R-0002 / S-0002:** se houver múltiplos clientes, **um ambiente (linha) por cliente**; *não faça:* cruzar dados no Meta.
35. **R-0031 / R-0032 / S-0044:** aprofundar o estudo; critério de avaliação da estrutura = "ter resultado".

---

## 3. ONDE EU PARO

**MISSING_REQUIRED_INPUT — RG-013-003 (build-contract completeness gate)**
O pedido é de configuração. O contrato exige `outcome, input, output, boundaries`. Você forneceu **outcome** ("gerenciar os três canais de forma unificada"), mas **input, output e boundaries estão ausentes**. A ação do guard manda perguntar apenas o primeiro campo faltante usando `knowledge/questions.yaml` — **esse arquivo não está no bundle de runtime**, e o `ADR-0004` citado pelo guard não existe em `decision-rules.yaml`. Consequência: **não vou inventar o enunciado canônico da pergunta**. Emito o stop e nomeio o campo faltante: **`input`**.
*Observação de instrumento:* o guard RG-013-003 fala em "montar um agente" — vocabulário do compilador, não do curso. Registro a incompatibilidade em vez de reinterpretá-la.

**RG-013-002 (outcome-before-routing)** — avaliado e **não acionado**: existe outcome explícito. Mas o `Q-0001` que ele referenciaria também é inacessível; se você tivesse trazido só "quero automatizar posts", eu pararia sem conseguir emitir a pergunta prescrita.

**METHOD_NOT_DEFINED — trilhas de campanha (R-0026)**
A regra manda "seguir a trilha correspondente ao modelo de negócio" (negócio local / X1 por mensagem / infoprodutor-afiliado). **Nenhuma dessas trilhas existe como workflow neste runtime.** Para peças de moto eu poderia palpitar entre "negócio local" e "X1 por mensagem" — **não vou**. Estrutura de campanha, público, orçamento e criativo ficam sem método.

**METHOD_NOT_DEFINED — conexão do WhatsApp Business**
O runtime só tem **S-0041: verificar** perfis de WhatsApp conectados. **Não existe passo de como conectar** o número. O canal WhatsApp entra na caixa de entrada unificada (S-0021) pressupondo conexão já feita — o "como" é lacuna da fonte.

**METHOD_NOT_DEFINED — criação de página e de conta de anúncio**
S-0044 remete explicitamente a "continuar estudando os conteúdos do canal para aprender a criar página e criar conta de anúncio". Fora deste runtime.

**UNDEFINED sistemático — campos vazios em toda a base**
- `missing_input_action: UNDEFINED` em **todos** os 44 steps e **todas** as 32 regras → não há método definido para o que fazer quando um input obrigatório falta. Por isso a Seção 1 é bloqueio, não sugestão.
- `iteration_limit: UNDEFINED` em todos → não há critério de quantas tentativas/revisões.
- `autonomy: UNDEFINED` em todos → **nenhum passo autoriza execução autônoma**. Tudo é orientação para operador humano.
- `precedence: UNDEFINED` em quase todas as regras (exceto R-0001) → se duas regras conflitarem, não há desempate definido.
- `condition: UNDEFINED` em R-0011, R-0017, R-0018, R-0019, R-0020, R-0021, R-0032 → automações de comentário, resposta instantânea e ausência não têm condição de disparo especificada além do gatilho bruto.

**Recursos ausentes**
- Link de instalação da ferramenta antidetect (S-0001) — existia "na descrição" da fonte; não está aqui.
- `knowledge/questions.yaml` — ausente (ver acima).

**Lacuna estrutural declarada**
S-0001, S-0002 e S-0003 caem em **WF-DEFAULT**: a fonte não nomeia procedimento que os agrupe. É ausência declarada, não invenção.

**Fora de escopo por decisão da própria fonte**
R-0030: **pixel não é tratado**. S-0043 apenas localiza os pixels em "fonte de dados" e para ali.

---

## 4. O QUE ESTA SKILL NÃO COBRE PARA ESTE CASO

1. **Pixel, eventos, Conversions API, rastreamento de conversão** — excluído explicitamente (R-0030).
2. **Como conectar o WhatsApp Business** ao portfólio/Business Suite; WhatsApp Business API, catálogo do WhatsApp, respostas rápidas nativas do app, múltiplos atendentes no mesmo número.
3. **Como criar a página do Facebook e a conta de anúncio** — remetido para fora (S-0044).
4. **Estrutura real de campanha para venda de peças**: segmentação, públicos semelhantes/personalizados, orçamento, criativos, testes A/B, escala. As "trilhas por modelo de negócio" são citadas e não definidas (R-0026).
5. **Métricas de performance de anúncio** (CPA, ROAS, CTR, frequência). Insights, aqui, cobre público, localização, engajamento e resultado por conteúdo — não a leitura de campanha paga.
6. **E-commerce**: catálogo de produtos, Loja do Facebook/Instagram, Shopping, integração com site ou ERP de peças — nada disso aparece na fonte.
7. **Recuperação de conta/página bloqueada ou restrita.** A fonte trata bloqueio só preventivamente (R-0002, R-0003, R-0029) — não há procedimento de recurso/apelação.
8. **Operação de atendimento**: SLA, divisão de fila entre atendentes, scripts de venda, integração com CRM externo. Só existe o CRM condicional via formulários (R-0022).
9. **Qualquer nível de autonomia executável.** Com `autonomy: UNDEFINED` em 100% dos steps e regras, esta Skill orienta um operador humano — não executa nem decide sozinha, e nenhum checkpoint humano aplicável pode ser removido.

**Próximo passo:** responda o item **1 da Seção 1** (login) e os itens **2, 3 e 4** (existência da página, tela de contas vinculadas, ícones no topo). Com esses quatro eu destravo WF-0002 → WF-0001 → WF-0003 na sequência correta. O item **8** (administrador adicional, R-0029) pode ser decidido em paralelo e é o de maior risco se ficar parado.
