---
tipo: veredito-final
pilot_id: PILOT-004
data: 2026-08-15
maquina: bot-04 (MacBook Pro M4 Max)
status: VALIDADO — 4/4 criterios declarados
---

# PILOT-004 — VEREDITO FINAL

**VALIDADO NOS 4 CRITÉRIOS DECLARADOS.**

Fonte: *Como Usar o Meta Business Suite 2026 [PASSO A PASSO]*, 15:03, pt-BR, ASR
auto-gerada. `L0 sha256 607f5a98…`. Primeira fonte em português do projeto.

Os quatro critérios foram declarados **antes** do PASS 1, no
`SOURCE-MANIFEST-PILOT-004.yaml`, e não foram alterados depois.

---

## C1 — cobertura evidência→regra > 80% · **PASSA**

**83,58%** — 112 de 134 evidências consumidas por regra ou passo.

| | |
|---|---|
| regras / passos / workflows | 32 / 44 / 12 |
| `CONSUMED_BY_RULE` / `CONSUMED_BY_STEP` | 63 / 49 |
| `NON_METHODOLOGICAL` / `GAP` | 20 / 2 |
| evidências **sem** disposição | **0** |
| erros de validação / roteador | 0 / 0 |
| template fail-closed byte-a-byte | `true` |

Compilado com o **compiler-s3/0.1.0**, congelado no mesmo dia
(`FREEZE-RECORD-s3-v0.1.0.yaml`, inventário `115a3773…`), com pré-classificação
rodando **antes** de qualquer regra: `SOURCE_EXPLICIT` 119 ·
`GENUINE_INFERENCE` 9 · `TRANSCRIPTION_CORRECTION` 6.

Evidência: `T7-BLOCO3-RESULTADO.md`, `03_SKILL/COMPILATION_MANIFEST.yaml`.

## C2 — GAP-REPORT específico e verdadeiro · **PASSA**

O critério exigia **ao menos uma** alegação específica e verdadeira. Dos cinco
candidatos submetidos com literal da fonte e timestamp, **quatro** foram julgados
específicos e verdadeiros por Alexandre:

| candidato | veredito |
|---|---|
| 1 — as trilhas que a fonte manda seguir e nunca ensina (11:09–11:17) | **específica e verdadeira** |
| 2 — o WhatsApp unificado sem nunca ser conectado (8:04 / 14:02) | **específica e verdadeira** |
| 3 — o pixel localizado e explicitamente abandonado (2:58 / 14:17) | **específica e verdadeira** |
| 4 — página e conta de anúncio terceirizadas no minuto final (14:31–14:41) | **específica e verdadeira** |
| 5 — `autonomy: UNDEFINED` em 100% | genérica |

O candidato 5 era o que eu próprio havia marcado como o mais fraco em
especificidade no kit, com a ressalva escrita antes do julgamento. O veredito
confirmou a ressalva.

**Controle que sustenta o C2:** controle positivo por token **16/17 (94,1%)**,
com poder; controle negativo **12/12** ausentes do L0 e da Skill; **zero
invenções**; **zero lacuna nossa** real. Sem isso, "o curso não ensinou X"
poderia ser perda do pipeline apresentada como falha do curso.

Evidência: `KIT-FECHAMENTO-20260814.md` §A, `GAP-CONTROLE-POSITIVO.json`,
`03_SKILL/COURSE-GAP-REPORT.md`.

## C3 — aplicada ao Business Suite REAL da MTX · **PASSA (a + b)**

### Metade b — pede o dado/acesso certo

A Skill recebeu **apenas** o contexto mínimo autorizado — *empresa de peças de
moto com Instagram, Facebook e WhatsApp Business; quer gerenciar os três de forma
unificada* — sem nenhum dado de conta. Pediu **15 itens**, cada um com o caminho
na interface e a regra de origem.

O sinal mais forte: reconheceu que peças de moto **não cai** em nenhuma das três
trilhas da fonte e **pediu a classificação em vez de escolher uma** —
*"não vou classificar por você"*.

### Metade a — produz configuração/correção conferível

Respostas reais chegaram em 15/08/2026 pela **agência Click**, que administra a
estrutura Meta da MTX. Placar: **8 configurados · 2 não existem · 5 não
conferidos**.

**A correção conferível é o item 11:**

> **NÃO EXISTE administrador da MTX** na estrutura. Só a agência, mais o perfil
> pessoal do contato como backup.

A Skill havia pedido exatamente isso, por `S-0037 → S-0038`, com base em
`R-0029` — a regra que a fonte enuncia como a de maior risco se ficar para
depois: em restrição a nível de perfil, perde-se página, Instagram e contas de
anúncio de uma vez. **Correção já solicitada por Alexandre à agência.**

Uma correção conferível basta para o critério. As demais respostas ou
confirmaram conformidade (ícones ativos, Instagram conectado, WhatsApp como
número principal, portfólio próprio `mtximports_` com página vinculada) ou
resolveram regras condicionais (`R-0022`: CRM/formulários da Meta não utilizados,
inbox respondido internamente pela equipe MTX).

**Achado colateral:** a lacuna do Candidato 2 — o curso nunca ensina a conectar o
WhatsApp — **não afeta a MTX**, porque o número principal já está conectado. A
lacuna do curso é real e continua real; ela apenas não morde neste caso.

Evidência: `KIT-FECHAMENTO-20260814.md` §B, `T8-MTX-APLICACAO-VERBATIM.md`.

## C4 — modo de falha (só conselho genérico) · **NÃO ACIONADO**

O critério declarava falha se a saída fosse conselho genérico do tipo *"conecte
suas contas, poste com frequência"*. Não foi o caso:

- toda recomendação vem com **passo, caminho na interface e id** de regra ou
  workflow (`S-0004: alternar → alternar → contas vinculadas`);
- traz **proibições** da fonte, não só sugestões — não deixar a estrutura fora do
  portfólio, não usar link clicável no texto do Instagram;
- traz **decisão fechada e justificada** — não contratar ferramenta paga de
  agendamento, porque o Planner faz de graça (`R-0015`);
- **recusa** onde a fonte não ensina, em vez de completar com conhecimento geral:
  `MISSING_REQUIRED_INPUT` nomeando o campo (`input`) e `METHOD_NOT_DEFINED` em
  quatro pontos específicos.

---

# Objetivo secundário — PRIMEIRA FONTE EM PORTUGUÊS · **FECHADO**

A hipótese declarada antes do PASS 1: *as 6 ocorrências de falha de medição do
PILOT-003 eram falha de tradução PT×EN*.

**Sustentada, e por uma margem maior do que a hipótese previa.**

| | P001-v2 (EN) | P003-v2 (EN) | **P004 (PT)** |
|---|---|---|---|
| quotes com marcador de inglês | 66% | 78% | **0%** |
| classe A — travessia PT×EN | estrutural | estrutural | **0** |

Nos dois pilotos de fonte inglesa, **toda evidência é uma travessia por
construção**: quote em inglês, claim em português. As 6 do P003 não eram um
defeito ocasional — eram a fração em que a forma normal de operação produziu erro
visível.

E nada tomou o lugar da travessia. Com o P001-v2 **reprocessado nesta mesma
máquina**, no mesmo runner e extractor, para gerar o baseline que não existia:

| | PT (P004) | EN (P001v2-remac) |
|---|---|---|
| classe C por evidência | **40,30%** | 45,14% |
| **aceitos só após normalização** | **0** | **108 (62%)** |
| rejeições / citações fabricadas aceitas | 0 / 0 | 0 / 0 |

Os 40% do português **não eram degradação** — o inglês está ~5 pontos acima. E a
diferença que mais importa é a última linha: em português as 134 citações
casaram literalmente de primeira; em inglês, 62% só passaram depois da
normalização de formato.

Evidência: `M4C-BASELINE-EN-vs-PT.md`, `REGUA-M1-M4-RESULTADO.md`.

---

# Achado de governança

O piloto encontrou, sem procurar, um problema que não é do curso nem da Skill:

> **A MTX não tem administrador próprio na sua própria estrutura Meta.**
> Só a agência, mais o perfil pessoal de um contato como backup.

Vale registrar o que isso significa em termos de risco, porque é a mesma lógica
que a `R-0029` enuncia: em restrição a nível de perfil, ou em ruptura com a
agência, a MTX perderia de uma vez a página, o Instagram e as contas de anúncio —
sem caminho próprio de recuperação. O portfólio `mtximports_` é da MTX, mas
administrado por terceiro, e veio da gestão anterior.

Duas observações de método:

1. **A Skill não sabia disso.** Ela pediu o dado por regra da fonte, e o dado
   revelou a lacuna. É a diferença entre uma Skill que responde e uma que
   pergunta a coisa certa.
2. **A correção é execução de Alexandre com a agência.** Nenhuma ação foi tomada
   na conta Meta por este piloto, e nenhuma será.

---

# Pendências abertas

Nenhuma delas invalida o veredito. Todas estão nomeadas para não virarem
silêncio.

## Do piloto

| id | pendência |
|---|---|
| **P-5** | causa das **175 × 149** evidências no reprocessamento do P001-v2 — extractor sem contraparte conferível (`R1_ABERTO_SEM_CONTRAPARTE`) ou variação normal do modelo. Não separável com o que está publicado. |
| **P-6** | **13 segmentos fora da banda 7–11**. Segui porque a banda é faixa de comparabilidade com `variance_flag`, não piso de portão. Consequência: **M2 é diagnóstico, não comparação**. |
| **P-7** | fixture do **canário fail-closed do compiler-s3 desatualizada** (`KeyError: 'name'` em `emit.py:54`). A proteção fail-closed **não é exercitada por teste**, e o resultado guardado não é reproduzível. |
| **P-8** | `knowledge/questions.yaml`, `Q-0001` e `ADR-0004` **referenciados e ausentes** no runtime emitido — no P004 **e** no P003-v2. Dois guards prescrevem uma pergunta que o pacote não contém. Defeito do compiler-s3. |
| **P-9** | **gerador do `distance-lines`** ausente. Sem ele o caminho **P4 (PARAPHRASE)** fica indisponível para todo piloto novo — no P004 rodou com `paraphrase_ids` vazio, declarado. |

## Do caso MTX

| item | estado |
|---|---|
| **4** — anúncio pelo app no iPhone (`R-0009`) | não respondido; não bloqueia |
| **12** — modelo de negócio entre as três trilhas (`R-0026`) | **PENDENTE-ALEXANDRE** |
| **13** — output esperado da operação unificada | **PENDENTE-ALEXANDRE** |
| **14** — boundaries do atendimento | **PENDENTE-ALEXANDRE** |
| **15** — comportamento da audiência por rede | não conferido; exige leitura de dado acumulado |

Sobre o **12**: qualquer que seja a resposta, a trilha correspondente **não
existe** no runtime — é o Candidato 1 da Seção A. O pedido é legítimo; o que vem
depois dele é `METHOD_NOT_DEFINED`.

## Ressalva de escala, declarada antes do PASS 1

A fonte tem 15:03 contra 3:50:57 do PILOT-003 — cerca de 1/15 do corpus. Isso foi
registrado no `SOURCE-MANIFEST` **antes** de qualquer execução, com a previsão de
que C1 ficaria mais fácil e C4 mais provável de acionar num corpus pequeno. C1
passou com folga de 3,58 pontos e C4 não acionou. A ressalva permanece válida
para leitura comparativa entre pilotos.

---

# Custo

| fase | chamadas |
|---|---|
| PASS 1 | 1 |
| PASS 2 | 13 |
| Baseline EN (P001-v2 remac) | 9 |
| Compilação evidência→Skill | 13 |
| Aplicação ao caso MTX | 2 |
| Canário fail-closed do s3 (quebrou antes da chamada) | 0 |
| **TOTAL** | **38** |

Estimativa declarada antes do PASS 1: 8–11 chamadas para PASS 1+2. Real: 14 — a
diferença veio do PASS 1 render 13 segmentos em vez dos 7–10 projetados.

---

# Fecho

O PILOT-004 valida os quatro critérios declarados e fecha o objetivo secundário.
O que ele **não** prova é o que as pendências dizem: a comparabilidade retroativa
com o P003 segue com uma incerteza nomeada, o caminho P4 da pré-classificação não
rodou, e a proteção fail-closed do compilador de Skill não está sob teste.

Nenhuma ação foi tomada na conta Meta da MTX. A correção de administrador é
execução de Alexandre com a agência.
