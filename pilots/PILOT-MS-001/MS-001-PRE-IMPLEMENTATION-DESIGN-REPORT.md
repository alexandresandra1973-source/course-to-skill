# PILOT-MS-001 — PRE-IMPLEMENTATION DESIGN REPORT

*Auditoria e desenho read-only executados em 2026-08-30 sobre
`HEAD = e12dfcda902e574272ab0826bcd32e85685bc9fb`.
Zero chamadas de modelo, zero escritas no repositório, zero escritas no Drive.
Todas as medições são reproduzíveis sobre o acervo preservado.*

## 1. Gate

`HEAD` = `origin/main` = `e12dfcda902e574272ab0826bcd32e85685bc9fb` (**confere com o esperado**) · tree limpo (0) · MS-000A accepted `abcfa0ac…` · MS-000B accepted `5e689af7…` · Freeze original `6d0eb7dd…` **17/17** · Identity Errata `2f8232f6…` · seis Source Packages **6/6 PASS** · Drive 0 escritas. **GATE = PASS.**

## 2. Estado herdado

MS-000A e MS-000B aceitos. Arquitetura congelada com errata de identidade. A limitação herdada — `CANDIDATE_DIRECT_PROVENANCE_NOT_YET_QUALIFIED` — é o portão que esta rodada tinha de resolver antes de qualquer desenho.

## 3. Corpus pool audit

Seis pilotos preservados. Quatro L0 no espelho. Inventário medido:

| fonte | autoridade | idioma | assunto | L0 | evidence | rules | workflows | steps |
|---|---|---|---|---|---|---|---|---|
| **P001-v2** | — | — | agentes/Slack | **AUSENTE** (`068b4998…` não preservado) | 149 | **0** | **0** | **0** |
| **P002-v2** | curso Claude Code, ex-eng. Amazon/Microsoft | en → claims pt | Claude Code | `43b58271…` (107 KB) + CUT | 448 | 149 | 43 | 145 |
| **P003-v2** | YouTube `c6qEURhNsYw`, *Ecommerce Google Ads Free Course* | en → claims pt | Google Ads e-commerce | `04fda222…` (369 KB, 3:50:57) | 2.463 | 835 | 158 | 601 |
| **P004** | YouTube `GNOHB166vWY`, **Filipe Detrey**, *Meta Business Suite 2026* | pt-BR | Meta Business Suite | `607f5a98…` (19,6 KB, 15:03) | 134 | 32 | 12 | 44 |

**P001 está fora**: seu L0 não está preservado — a cadeia não pode terminar — e não tem candidates. Existe ainda `PILOT-004/p001v2-remac` (175 evidences), uma recompilação de P001 em outra máquina: **`KNOWN_DEPENDENT`** com P001, útil como fixture de dependência, nunca como segunda fonte.

## 4. Source independence

Sinais mecânicos de dependência entre **P003 × P004**, buscados e **não encontrados**: `video_id` distintos e não citados entre si (`c6qEURhNsYw` aparece 0× em P004; `GNOHB166vWY` 0× em P003) · canais distintos (`Detrey` 0× em P003) · idiomas distintos (en vs pt-BR) · plataformas distintas · datas distintas · máquinas de selagem distintas (Lenovo vs bot-04, divergência já declarada no `SOURCE-MANIFEST-PILOT-004`).

Estado proposto: **`DECLARED_INDEPENDENT`**, sustentado por esse feixe de evidência explícita — sujeito a declaração formal no Opening Record, porque nenhum artefato hoje **declara** a independência; ela é inferida da evidência. Enquanto não declarada, o estado correto é `UNKNOWN`, e **`UNKNOWN ≠ INDEPENDENT`**.

## 5. Candidate Provenance contract — **a limitação herdada está resolvida**

Este é o achado central da rodada, e ele inverte o diagnóstico do MS-000B.

O corpus histórico **sempre teve** lastro de candidate. `decision_rules`, `workflows` e `steps` carregam `evidence_ids` e `segment_ids`. E `EVIDENCE.source_excerpt` **é** o `SOURCE_ANCHOR`: `{source_file, source_sha256, span{start_s,end_s}, quote}`.

Cadeia medida, sem chamada de modelo:

| fonte | objeto | com `evidence_ids` | refs resolvem | anchor completo | quote no L0 por sha256 |
|---|---|---|---|---|---|
| P002-v2 | rules 149 | 149 | **149/149** | **149/149** | 139 (93,29%) |
| | workflows 43 | 42 | 42/42 | 42/42 | 37 (86,05%) |
| | steps 145 | 145 | 145/145 | 145/145 | 138 (95,17%) |
| P003-v2 | rules 835 | 835 | **835/835** | **835/835** | 796 (95,33%) |
| | workflows 158 | 157 | 157/157 | 157/157 | 153 (96,84%) |
| | steps 601 | 601 | 601/601 | 601/601 | 577 (96,01%) |
| P004 | rules 32 | 32 | **32/32** | **32/32** | 32 (100%) |
| | workflows 12 | 11 | 11/11 | 11/11 | 11 (91,67%) |
| | steps 44 | 44 | 44/44 | 44/44 | 44 (100%) |

**100% das refs resolvem. 100% alcançam anchor completo.** A taxa de quote-no-L0 (86–100%) é consistente com o baseline `REPRODUCED_FROM` já medido, 2921/3045 = 95,93%, aqui com casamento mais estrito.

> **O `evidence_refs = []` do MS-000B foi defeito do meu empacotador**, não do corpus. `run_round3.py` reconstruía o candidate a partir do YAML e gravava `"evidence_refs": []` literal, descartando o `evidence_ids` que já existia. `CANDIDATE_DIRECT_PROVENANCE_NOT_YET_QUALIFIED` é **satisfazível hoje**, sem corpus novo.

Contrato do portão: `ELIGIBLE_FOR_CROSS_SOURCE_DECISION` · `NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION` · `INVALID_PROVENANCE`. Regra dura: **conjunto vazio não passa por vacuidade** — é `NOT_ELIGIBLE`, nunca `ELIGIBLE`.

## 6. Canários CP1–CP6

Desenháveis, com **caso real não sintético disponível** (CP1/CP6): qualquer das 1.016 rules com cadeia completa serve. CP2/CP4 (ref inexistente), CP3 (vazias) e CP5 (evidence sem anchor) são sintéticos, plantados fora do corpus real.

## 7. Unidade de comparação

`CLAIM` primária, congelado. Duas camadas separadas: **Claim Relation Layer** (substância normalizada) e **Candidate Transport / Assembly Layer** (sequência, condições, exceções, pré-requisitos, defeitos, proveniência). Não se confundem — foi o que a Round 4 do MS-000B já executou corretamente.

## 8–12. Taxonomia, eixos, conflito, escopo

Desenháveis: taxonomia experimental `IDENTICAL · CORROBORATES · SPECIALIZES · CONTRADICTS · SUPERSEDES · UNRELATED · INDETERMINATE`, com `PRESUPPOSES` aberto; eixos A (semântico) e B (governança) separados, `CONTRADICTS` sem implicar quem vence; portão de escopo com o canário obrigatório de vocabulário igual + escopos incompatíveis → **não** `IDENTICAL`.

O corpus até oferece o caso perfeito de falso conflito: P003 *"Exceção ao anti-padrão de PMAX…"* × P004 *"Anti-padrão: deixar a estrutura fora do portfólio…"* — compartilham `anti · padrão · conta · estrutura`, e são sobre plataformas diferentes.

## 13. Pair blocker — **onde o corpus falha**

Espaço de pares P003 × P004 = 2.463 × 134 = **330.042**. Sobrevivência por tokens de conteúdo compartilhados:

| par | brutos | `k≥2` | `k≥3` | `k≥4` | `k≥5` |
|---|---|---|---|---|---|
| P002 × P003 | 1.103.424 | 1.523 | 37 | **0** | 0 |
| P002 × P004 | 60.032 | 171 | 5 | **0** | 0 |
| **P003 × P004** | 330.042 | 1.198 | 68 | **3** | **0** |

Os três sobreviventes em `k≥4`, inspecionados um a um: um é **meta-discurso** (*"objetivo declarado… é mostrar…"*), sem substância; um é o falso-conflito de anti-padrão em plataformas distintas; um é sobre "quem está começando", com objetos diferentes.

**Nenhum par do acervo preservado sustenta uma camada de relação semântica.** Três pares — dos quais um é ruído — não permitem medir distribuição de relações, taxa de `INDETERMINATE`, recall do blocker em controles positivos reais, nem conflito algum. E cair em blocking semântico por embeddings não resolve: embeddings estão **explicitamente não congelados** (§21 do Freeze), seriam instrumento não testado, e trocar um blocker medível por um não medível para salvar o corpus é escolher método pelo resultado — proibido pelo §25.

## 14–19. Source Package, Fusion Package, identidade, coerência, incremental

Todos desenháveis e sem bloqueio arquitetural. O Source Package do MS-001 **não pode copiar o R3**: tem de **preservar** `evidence_ids`/`claim_refs` na construção do candidate, criando a proveniência **antes** de qualquer resultado cross-source. Identidade tipada `(source_package_hash, entity_kind, local_id)` obrigatória, com os quatro canários; nunca índice por `local_id` nu — defeito que reincidiu três vezes no meu próprio código. `fusion inputs = source_package_hashes + fusion_config_hash + semantic policy hashes`, com `mtx_policy_hash` fora.

## 20–22. Métricas, runs, orçamento

Métricas propostas sem threshold, separando **medição** de **aceitação**. Runs: **1 run instrumental + 3 runs avaliativas apenas na camada de julgamento semântico** — é o único ponto não determinístico; admissão, proveniência e transporte são mecânicos e não precisam de repetição. Orçamento: calculável, mas **sem sentido calcular sobre 3 pares**.

## 23. KILL conditions

`K1`–`K10` desenháveis, todas com fixture pré-execução. `K10` — tratar `UNKNOWN` como independente — é a que este próprio relatório quase acionou ao propor `DECLARED_INDEPENDENT` sem declaração formal existente.

## 24. Primary corpus pair

**Nenhum recomendado.** O melhor candidato — **P003-v2 × P004** — passa em independência e em Candidate Provenance, e falha no que importa: substância comparável. 3 pares em `k≥4`, 0 em `k≥5`.

## 25. Backup pair

Nenhum. P002 × P003 e P002 × P004 dão **0 pares** em `k≥4`.

## 26–27. Decisões abertas e thresholds

Fechadas: unidade de comparação · contrato de Candidate Provenance · identidade tipada · separação das duas camadas · separação dos dois eixos · forma do Fusion Package · identidade incremental · KILLs.

**Abertas por falta de corpus, não por falta de arquitetura:** qual par · estado de independência formalmente declarado · parâmetro do blocker · orçamento de chamadas · número de runs avaliativas · se `C3 TRUE CONFLICT` existe em corpus real.

Todos os thresholds permanecem `OPEN` — nenhum foi fixado aqui.

## 28. Zero model calls · 29. Zero repo writes · 30. Drive read-only

Nenhuma chamada. `git status --porcelain` = **0 linhas, 0 arquivos novos**, 0 commits desde `e12dfcda`. Freeze 17/17 e `SHA256SUMS` 0 FAILED depois da auditoria. Drive: 0 escritas. Nenhum arquivo temporário criado.

## 31. Classificação final

# `MS_001_NEEDS_NEW_CONTROLLED_CORPUS`

Arquitetura pronta. Proveniência de candidate **resolvida** e medida em 100%. Corpus preservado **não atende**.

---

**O que recomendo, sem executar nada.**

O acervo preservado é um corpus de **avaliação de curso** — três cursos sobre assuntos disjuntos, escolhidos justamente para não se sobreporem. Ele nunca foi montado para testar fusão multi-fonte, e a medição mostra isso sem ambiguidade.

O corpus reservado dos blocos A/B/C é a resposta óbvia — B (*Claude Code + Evolution API + WhatsApp*) e C (*n8n + Evolution API + Redis + agente*) compartilham Evolution API e automação de mensagens, que é exatamente substância sobreposta entre autoridades distintas. Mas ele **continua proibido**, e não o toquei nem para inspecionar.

Duas coisas que valem ser persistidas antes do próximo gate, e que **apenas recomendo** — não commitei:

1. **Uma errata ao MS-000B**, registrando que `CANDIDATE_DIRECT_PROVENANCE_NOT_YET_QUALIFIED` tinha causa no empacotador da Round 3, não no corpus, com as medições de 100% de resolução. A limitação está registrada hoje de forma que sugere insuficiência do corpus; a medição diz outra coisa.
2. **O inventário do pool de corpus**, com os números de sobrevivência de pares, para que a escolha do corpus do MS-001 seja decidida contra medida e não contra impressão.

**PARADO.** MS-001 não iniciado.
