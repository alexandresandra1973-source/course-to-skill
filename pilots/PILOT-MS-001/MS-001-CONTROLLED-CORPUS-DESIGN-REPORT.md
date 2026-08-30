# MS-001 — CONTROLLED CORPUS DESIGN REPORT

*Auditoria de aquisição e desenho executada em 2026-08-30 sobre
`HEAD = 09f68a0eecee2d8eff666233f4a209ea268b89c7`.
Zero chamadas de modelo, zero escritas no repositório, zero escritas no Drive.*

## 1. Gate

`HEAD` = `origin/main` = `09f68a0eecee2d8eff666233f4a209ea268b89c7` · tree limpo (0) · `MS_000B_ACCEPTED` `5e689af7…` · `MS_001_PREDESIGN_PRESERVED` `f82c6df1…` · Freeze `6d0eb7dd…` **17/17** · Identity Errata `2f8232f6…` · Drive 0 escritas. **GATE = PASS.**

Ferramentas: `yt-dlp` **ausente** — não instalei nada. Usei `youtube_transcript_api` (já na venv do projeto) e `curl`. Nenhuma ferramenta do projeto foi mutada.

## 2. Source B — profile

| campo | valor |
|---|---|
| URL canônica | `https://www.youtube.com/watch?v=dtAoZYMEzcM` |
| `video_id` | `dtAoZYMEzcM` |
| título | **Como Gerenciar Grupos de WhatsApp com Claude Code** |
| canal | **Anderson Adelino \| IA e Automações** (`@oandersonadelino`) |
| `channel_id` | `UCI5WcISxqiFfoh4mse1s-HA` |
| upload | **2026-06-24T13:52:55-07:00** |
| duração | 1.056 s (17:36) |
| categoria | Science & Technology |
| caption tracks | `en` **AUTHOR_PROVIDED** · `es` **AUTHOR_PROVIDED** · `pt` **PLATFORM_AUTO_CAPTION** |
| faixa usada | `pt` (auto) |

Timestamps declarados pelo autor: `00:00` Introdução · `00:25` Stack · `01:09` VPS com Evolution API · `05:30` Conectando o WhatsApp · `06:30` Integrando Evolution API com Claude Code · `10:32` Casos de uso.

## 3. Source C — profile

| campo | valor |
|---|---|
| URL canônica | `https://www.youtube.com/watch?v=NvrBpnbNfv4` |
| `video_id` | `NvrBpnbNfv4` |
| título | **N8N + WhatsApp: Responda Mensagens utilizando um Agente de IA!** |
| canal | **Guilherme Lazarotto - Tecnologia & Automação** (`@guilherme_laz`) |
| `channel_id` | `UCO0x-39c7EttOhmFAsngfgg` |
| upload | **2025-02-19T10:45:04-08:00** |
| duração | 824 s (13:44) |
| categoria | Education |
| caption tracks | `pt` **PLATFORM_AUTO_CAPTION** (única) |
| faixa usada | `pt` (auto) |

**O `&t=330s` do URL de B foi ignorado como boundary**, conforme instruído — auditei o vídeo inteiro e as boundaries saíram da estrutura medida.

## 4. Artefatos adquiridos + hashes

| artefato | sha256 | bytes |
|---|---|---|
| `raw/B-dtAoZYMEzcM-pt.json` | `2a6ab098868e0714e5d4bc5cebb8018216d78f0243ee890b2c531516fbda7862` | 47.164 |
| `raw/C-NvrBpnbNfv4-pt.json` | `ed967fae27146d9aa9cc45769672f751d8eb199bc6ed7564bbb5fdb4a226fab7` | 37.838 |
| `meta/B-…-meta.json` | `1ad11f59b4af7fcd…` | 2.215 |
| `meta/C-…-meta.json` | `a96b893d8660696c…` | 6.296 |
| `out/SELECTION-ALGORITHM.txt` | `1d974b5342125d77ac130c444a979cdc692e1ffda76308f0b3ac48fe471509f7` | 1.226 |
| `out/concept-matrix.json` · `out/slices.json` · `out/MANIFEST.json` | ver manifesto | — |

Tudo em `~/ms001-controlled-corpus-design/`. **Nada no Git, nada no Drive.**

## 5. Qualidade do texto

| medida | B | C |
|---|---|---|
| segmentos | 488 | 389 |
| segmentos vazios | **0** | **0** |
| timestamps inválidos | **0** | **0** |
| duplicados consecutivos | **0** | **0** |
| caracteres corrompidos | **0** | **0** |
| ordem temporal monotônica | **SIM** | **SIM** |
| gaps > 3 s | **0** | **0** |
| chars | 17.846 | 14.376 |
| marcadores de português | 68% dos segmentos | 66% |

Um artefato do formato, registrado e **não corrigido**: a cobertura temporal soma **199,9%** porque a auto-caption do YouTube emite spans sobrepostos (janela rolante de duas linhas). Não é defeito; o design do anchor tem de ordenar por `start` e tratar spans como sobrepostos.

Ambas: **`SOURCE_TEXT_READY_WITH_LIMITATION`** — auto-caption com erros localizados de ASR (`Reds` por *Redis*, `Cloud Code` por *Claude Code*, `messages up search` por *MESSAGES_UPSERT*, `grock` por *Groq*), timestamps e substância plenamente recuperáveis. **Nenhuma correção semântica aplicada. Nada foi corrigido no original.**

## 6. Auditoria de independência

| sinal | B | C |
|---|---|---|
| canal | Anderson Adelino | Guilherme Lazarotto |
| `channel_id` | `UCI5WcISxqiFfoh4mse1s-HA` | `UCO0x-39c7EttOhmFAsngfgg` |
| upload | 2026-06-24 | 2025-02-19 (**16 meses antes**) |
| categoria | Science & Technology | Education |
| domínio próprio | `zenithonacademy.com.br` | `guilhermelaz.com.br` |

Referências cruzadas: **nenhuma**. Nenhum menciona o `video_id`, o canal, o nome ou o domínio do outro — cada um só se auto-referencia.

Sequências textuais idênticas entre as transcrições:

| n-grama | compartilhados |
|---|---|
| 5 palavras | 2 |
| 6 palavras | **0** |
| 8 palavras | **0** |
| 10 palavras | **0** |
| 12 palavras | **0** |

Sem script comum, sem adaptação, sem tradução, sem cópia.

## 7. Recomendação de independência

# `CANDIDATE_FOR_DECLARED_INDEPENDENT`

Há evidência suficiente para **recomendar** um futuro Decision Record `B_AND_C_DECLARED_INDEPENDENT_FOR_MS_001`. Não a declaro aqui — `DECLARED_INDEPENDENT` só existe por Decision Record formal antes da execução, e inventá-la retroativamente é a condição de morte `K10`.

## 8–10. Inventário de conceitos e matriz de sobreposição

**9 conceitos `PRESENT_BOTH`** (≥3 ocorrências em cada fonte):

| conceito | B | C | estado |
|---|---|---|---|
| **Evolution API** | 24 | 11 | `PRESENT_BOTH` |
| **WhatsApp** | 13 | 8 | `PRESENT_BOTH` |
| **API/tool** | 20 | 21 | `PRESENT_BOTH` |
| **VPS/hosting** | 16 | 3 | `PRESENT_BOTH` |
| **QR/instance** | 10 | 4 | `PRESENT_BOTH` |
| **message** | 8 | 24 | `PRESENT_BOTH` |
| **conversation** | 3 | 11 | `PRESENT_BOTH` |
| **automation/orchestration** | 7 | 8 | `PRESENT_BOTH` |
| **test/validate** | 6 | 9 | `PRESENT_BOTH` |
| `24h window` · `reports` | 3 · 3 | 0 · 0 | `B_ONLY` |
| `agent` · `n8n` · `Redis` · `database` · `outbound/reply` · `docker` · `human takeover` · `long response` · `LLM provider` | 0 | 18 · 9 · 4 · 5 · 15 · 4 · 1 · 1 · 1 | `C_ONLY` |
| `webhook` · `memory/state` · `group/admin` · `grouping/buffering` · `credentials` · `prompt/system` | 1 · 2 · 60 · 1 · 2 · 1 | 6 · 6 · 1 · 1 · 12 · 6 | `INSUFFICIENT` |

**Cluster compartilhado real:** *Evolution API como ponte não-oficial para o WhatsApp, hospedada em VPS, com instância/sessão conectada e dirigida programaticamente.* B o cobre do lado **produtor** (hospedar, criar instância, escanear QR, dar a doc da API ao orquestrador); C do lado **consumidor** (webhook na sessão, `MESSAGES_UPSERT`, base64, `remoteJid`).

Nenhum cluster foi fabricado para preencher lista.

## 11. Algoritmo de seleção

Declarado e hasheado **antes** de selecionar: `1d974b5342125d77ac130c444a979cdc692e1ffda76308f0b3ac48fe471509f7`. Janela 90 s / passo 30 s · score = nº de conceitos `PRESENT_BOTH` distintos · descarte de boilerplate por 10 marcadores · expansão até fronteira de segmento · rank por score desc, `start` asc · sem sobreposição. **A seleção não consulta relação semântica alguma.**

## 12–14. Slices candidatas e segurança de boundary

**Source B** — todas `BOUNDARY_SAFE`:

| slice | janela | score | conceitos |
|---|---|---|---|
| `SB1` | 0–90 s | **7** | API, Evolution, VPS, WhatsApp, automation, conversation, message |
| `SB2` | 150–240 s | 5 | API, Evolution, QR/instance, VPS, WhatsApp |
| `SB3` | 270–360 s | 6 | + test/validate |
| `SB4` | 570–660 s | 6 | API, Evolution, QR/instance, VPS, WhatsApp, test |
| `SB5` | 660–750 s | 2 | Evolution, automation |
| `SB6` | 960–1050 s | 3 | API, message, test |

**Source C** — todas `BOUNDARY_SAFE`:

| slice | janela | score | conceitos |
|---|---|---|---|
| `SC1` | 30–120 s | 3 | API, VPS, conversation |
| `SC2` | 120–210 s | **7** | API, Evolution, QR/instance, WhatsApp, automation, message, test |
| `SC3` | 210–300 s | 5 | API, QR/instance, conversation, message, test |
| `SC4` | 300–390 s | 3 | API, conversation, message |
| `SC5` | 450–540 s | 4 | API, automation, conversation, message |
| `SC6` | 660–750 s | **7** | API, Evolution, VPS, WhatsApp, automation, message, test |

Nenhuma começa ou termina no meio de um raciocínio — o filtro de conector de continuidade não disparou em nenhuma das doze.

## 15–16. Opções de tamanho e microcorpus recomendado

| config | dur B | dur C | chars B | chars C | sub-blocos | pares brutos |
|---|---|---|---|---|---|---|
| 2+2 | 180 s | 180 s | 3.188 | 3.136 | 12 | 36 |
| **3+3** | **270 s** | **270 s** | **4.716** | **4.619** | **18** | **81** |
| 4+4 | 360 s | 360 s | 6.086 | 6.270 | 24 | 144 |

**Recomendado: 3+3** — `SB1`, `SB2`, `SB3` × `SC1`, `SC2`, `SC3`. É o menor conjunto que cobre os nove conceitos `PRESENT_BOTH` e ainda inclui as duas slices de score 7 do cluster central. ~9,3k chars mantém o risco de explosão de all-pairs sob controle sem sacrificar diversidade.

## 17. Genuine overlap (S1) — **presente**

`SB2`/`SB3` × `SC2`: criação e configuração da instância/sessão Evolution API para o WhatsApp, com chave de API e verificação. Ambos substantivos, não menção.

## 18. Scope difference (S2) — **presente**

**Direção do fluxo.** B: *"criar vários grupos em massa, mudar foto de perfil, mudando a descrição, adicionando pessoas, enviando…"* — outbound/administrativo. C: *"responder as mensagens que chegam no seu WhatsApp"* — inbound/reply. O contador confirma: `outbound/reply` = 0 em B, 15 em C; `group/admin` = 60 em B, 1 em C.

## 19. Specialization (S4) — **presente**

Orquestrador: B usa **Claude Code** lendo a documentação da Evolution API e chamando-a direto; C usa **n8n** com webhook, nodes comunitários e agente. Mesma API, camadas de orquestração diferentes.

## 20. True conflict — **`TRUE_CONFLICT_CANDIDATE_FOUND`**

Candidato real, não fabricado, sobre **onde rodar a Evolution API**:

- **B** [~60–90 s]: *"Ele precisa ser hospedado em algum lugar… você precisa hospedar em uma VPS para ele ficar lá 24 horas por dia funcionando."*
- **C** [~22 s]: *"se você ainda não tem a Evolution e o n8n configurados na sua VPS… ou baixe aí na descrição o meu script para rodar localmente."*

Mesmo objeto (Evolution API), mesma condição (colocá-la em operação). Se resolve para `CONTRADICTS` ou para `SPECIALIZES` — B falando de produção 24 h, C de desenvolvimento local — é exatamente o julgamento que o MS-001 existe para fazer. **Não classifico aqui.**

## 21. Controle de falso conflito — **presente**

**"chave de API"** com objetos diferentes: em B é a *global API key da Evolution API*; em C é a *chave do Groq/OpenAI*. Vocabulário idêntico, objetos incompatíveis. Candidato a `DO_NOT_CONTRADICT`.

## 22. Controle unrelated — **presente**

Pares com **0 termos compartilhados** e substância dos dois lados: B *"os tipos de servidores, dois, quatro, oito…"* × C *"os campos: quem mandou, a instância que recebeu…"*. Dentro do microcorpus recomendado.

**S6 versão/supersessão:** apenas 1 marcador temporal em C, 0 em B. `NOT_AVAILABLE` — não exigido, não fabricado.

## 23. Design de `SOURCE_ANCHOR`

```
SOURCE_ANCHOR
  source_id                 # MS001-SRC-B / MS001-SRC-C
  artifact_hash             # sha256 do JSON de caption
  video_id                  # dtAoZYMEzcM / NvrBpnbNfv4
  start_s, end_s            # spans SOBREPOSTOS por design da auto-caption
  quote                     # verbatim do artefato
  transcript_segment_ids    # índices no array original, preservados
```

Os offsets nativos do caption são preservados. Ordenação por `start`; a sobreposição de spans é propriedade do formato, registrada, não corrigida.

## 24. Design de Candidate Provenance

```
candidate → evidence_refs → SOURCE_ANCHOR → transcript artifact → source/video
candidate → claim_refs    → evidence
```

**Regra dura, herdada do defeito da Round 3:** o compilador **não pode descartar** os `evidence_ids` de origem. Candidate com evidence vazio é `NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION` — conjunto vazio nunca passa por vacuidade.

## 25. Fronteira de recurso externo

Todos `EXTERNAL_RESOURCE_REFERENCED`, **nenhum seguido ou baixado**:

| fonte | recurso | decisão |
|---|---|---|
| B | VPS HostGator (afiliado) · curso Zenithon · grupo gratuito | `OUT_OF_CORPUS` |
| C | curso N8N Fácil · VPS Hostinger/Contabo · grupo WhatsApp com **workflow JSON + script Docker** · Groq · OpenAI | `OUT_OF_CORPUS` |
| C | **vídeo anterior** com o setup de Evolution + n8n na VPS | `REFERENCED_EXTERNAL_RESOURCE_NOT_IN_CORPUS` |

O último merece destaque: **C aponta o próprio setup de Evolution API para um vídeo anterior.** Isso reduz o lado C do cluster de setup. C continua autossuficiente para o que ensina — webhook, mapeamento, agente, memória — e a sobreposição com B se dá do lado **consumidor** da API, que está em C. Registro como **limitação**, não como bloqueio.

## 26. Viabilidade do blocker

Sobre 4+4 slices, 24 sub-blocos de ~30 s como proxy de unidade de claim:

| `k` | pares sobreviventes de 144 | redução |
|---|---|---|
| 2 | 99 | 31,25% |
| 3 | 57 | 60,42% |
| 4 | 31 | 78,47% |
| **5** | **10** | **93,06%** |
| 6 | 6 | 95,83% |
| 7 | 2 | 98,61% |

**Ressalva que preciso fazer com clareza:** o topo do ranking é dominado por **registro procedural** — `clica`, `coloca`, `criar`, `nome`, `configurações`, `gerar`, `teste`. São o vocabulário comum de tutorial gravado em tela, não substância; o par de score 7 casa *"criar uma instância do WhatsApp"* com *"criar uma chave de API do Groq"*, que não são comparáveis.

Isso **não** condena o blocker: ele operará sobre **Claims** normalizadas, não sobre transcrição bruta, e a camada de claim elimina esse registro — é visível nos pilotos históricos, cujas claims leem *"O pixel é muito importante para quem quer vender online"*, sem `clica aqui`. Mas as Claims **ainda não existem**, e gerá-las está proibido nesta rodada.

**Veredito honesto: blocker plausível, não demonstrado.** A demonstração é o primeiro portão da próxima etapa.

## 27. Volume de pares estimado

Com 3+3 slices e a densidade de claims dos pilotos históricos (~16,6 evidences/segmento em P003; ~5–6 claims por 90 s de conteúdo denso): estimo **40–70 claims por fonte**, logo **1.600–4.900 pares brutos**. Sob blocker a 90–95% de redução: **80–490 pares candidatos**. Intervalo largo de propósito — o fator dominante é a densidade real de claims, que só a compilação revela.

## 28. Orçamento preliminar do juiz semântico

Não chamei modelo. Estimativa, com os fatores que a alteram:

| item | estimativa |
|---|---|
| geração de Claims | 1 chamada por (fonte × slice) = **6** |
| controles do juiz (positivo, negativo, indeterminado, cross-source) | **2–3** |
| julgamento de pares, lotes de 20–25 | **4–20** (depende do volume acima) |
| 3 runs avaliativas só na camada de julgamento | **×3** apenas sobre o julgamento |
| **total preliminar** | **~20–70 chamadas** |

Fatores que mudam o orçamento: densidade real de claims · parâmetro final do blocker · tamanho do lote · se as 3 runs cobrem só o juiz ou também a geração. **Nenhum threshold é fixado.**

## 29. Recomendação de `SOURCE_CONTENT_HASH`

`SOURCE_ID` (lógico, estável) ≠ `SOURCE_CONTENT_HASH` (bytes). Recomendo como base do `SOURCE_CONTENT_HASH` o **artefato de caption original serializado canonicamente** — `raw/{tag}-{video_id}-pt.json`, com `start`/`duration`/`text` por segmento, JSON ordenado — cujos hashes já estão fixados acima. Razões: é o byte real de que toda Evidence deriva; é reproduzível por reaquisição; e não depende de normalização, que é passo derivado e versionável à parte. **URL não é identidade de conteúdo** — o vídeo pode ser editado, re-legendado ou removido sob o mesmo URL.

Risco registrado: a auto-caption do YouTube **pode mudar** sem aviso. Congelar o artefato agora é o que torna a rodada reproduzível.

## 30. Decisões abertas

Par de slices definitivo dentro do conjunto recomendado · parâmetro `k` do blocker · densidade de claims · volume real de pares · orçamento final · modelo/config/prompt do juiz · declaração formal de independência · se a taxonomia mantém as sete labels.

## 31–33. Zero modelo · zero repo writes · Drive read-only

Nenhuma chamada de modelo. `git status --porcelain` = **0 linhas**; `HEAD` inalterado em `09f68a0e`. Drive: **0 escritas**. **Source A / Nick Saraev não foi inspecionada.** Nenhuma outra fonte usada para complementar B ou C. Nada compilado.

## 34. Classificação final

# `MS_001_BC_CORPUS_READY_FOR_SOURCE_PACKAGE_DESIGN`

Contra os doze critérios do §26: dez atendidos, dois com ressalva declarada — *overlap não é só boilerplate* (a substância é real, mas o registro procedural contamina o blocker lexical bruto) e *blocker parece viável* (plausível, não demonstrado, porque exige Claims). Nenhum recurso externo obrigatório está faltando; o vídeo anterior de C é referência, não pré-requisito para o que C ensina.

---

**Três coisas que a próxima etapa precisa tratar como portão, não como detalhe.**

**(a) O blocker é o risco vivo.** O corpus preservado morreu exatamente aí. Aqui a estrutura é diferente — as duas fontes falam da *mesma API*, não de plataformas vizinhas — mas isso é argumento, não medida. Primeiro portão do Source Package design: gerar Claims e **medir a sobrevivência de pares sobre elas**. Se colapsar como P003×P004, o corpus cai junto.

**(b) `CANDIDATE_FOR_DECLARED_INDEPENDENT` não é `DECLARED_INDEPENDENT`.** A evidência é forte — zero n-gramas de 6+, zero referências cruzadas, 16 meses de distância — e continua sendo ausência de evidência de dependência. A promoção exige Decision Record formal antes da execução.

**(c) O artefato precisa ser congelado agora.** As duas transcrições estão hasheadas na área temporária, fora do Git. Auto-caption do YouTube muda sem aviso; se a próxima etapa reabrir a aquisição, pode pegar bytes diferentes e invalidar tudo o que este relatório mediu.

**PARADO.** Não compilei. MS-001 não iniciado.
