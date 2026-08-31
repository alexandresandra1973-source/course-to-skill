# OPENING RECORD — PILOT-MS-002 — FUSION MULTI-SOURCE A/B/C

Selado e pushed **ANTES** de qualquer chamada semântica de Fusion. Data: 2026-08-31.

## 1. Entrada — três Source Packages selados

| source_id | claims seladas | candidates (elegíveis) | `source_package_hash` |
|---|---|---|---|
| MS002-SRC-A | 642 / 649 | 237 (229) | `0f1ba2cd631eb30e46c899a7fd5984be240a50e4616fd71cd56815698cb7e8dc` |
| MS002-SRC-B | 56 / 58 | 25 (23) | `73e03ac76856edbc6adb25717ed9a6ece285a94d63921a6ad6a508dd9bfe0889` |
| MS002-SRC-C | 66 / 66 | 19 (19) | `eb833bacc1ebf5517c1757cc1c13f0d2bfc2185d5595621286a7f236bb3bf0df` |

`INVALID_PROVENANCE = 0` nos três. Registro externo em
`packages/EXTERNAL-SEAL-REGISTRY.txt`.

## 2. Blocker — calibração mecânica, antes do juiz

`BLOCKER-DESIGN-MS002-v1.0`, hash
`7b8b7fd954c13997c16066c41aae091630ded25f5dd9abf5323d70849c0a8d45`,
declarado **antes** de qualquer medição. População cross-source: **82.020 pares**
(A×B 35.952, A×C 42.372, B×C 3.696). Nenhum par intra-fonte.

| variante | retidos | taxa | A-B | A-C | B-C | cabe em 300? |
|---|---|---|---|---|---|---|
| V1 (≥1 conceito) | 20.292 | 24,74% | 7.055 | 11.472 | 1.765 | não |
| V3 (≥1 conceito OU ≥1 objeto) | 24.261 | 29,58% | 10.975 | 11.521 | 1.765 | não |
| V4 (≥2 conceitos OU ≥1 objeto) | 8.545 | 10,42% | 6.049 | 1.858 | 638 | não |
| V2 (≥1 objeto) | 6.174 | 7,53% | 5.552 | 135 | 487 | não |
| V5 (≥2 conceitos E ≥1 objeto) | 518 | 0,63% | 223 | 32 | 263 | não |
| **V6 (≥3 conceitos E ≥1 objeto)** | **51** | **0,06%** | **12** | **0** | **39** | **sim** |
| V7 (V6 E ≥1 content token) | 50 | 0,06% | 11 | 0 | 39 | sim |

    VARIANTE SELECIONADA: V6 · 51 pares · PAIRSET_HASH 62293fb3544c313cb7aee8c13b34a7d4ba2dfcc2598b9ace9472e8883121c159
    capacity_limited_sample = false

A seleção seguiu **exatamente** a regra pré-declarada: a variante menos estrita cuja
contagem cabe na capacidade declarada de 300 pares, na ordem V1, V3, V4, V2, V5, V6, V7.

## 3. Limitações que registro agora, não depois

**(a) 249 pares de capacidade ficaram sem uso.** V5 retém 518 e V6 retém 51; nada cai
entre 51 e 300. A regra declarada só previa amostragem determinística **se nenhuma
variante coubesse**, e V6 coube. Honrar a regra custou orçamento ocioso. Mudar a regra
agora, depois de ver as contagens, seria exatamente o tuning pós-resultado que o §38
proíbe — então não mudo. Registro como defeito de desenho da regra, a corrigir num
desenho futuro, **não** nesta execução.

**(b) A×C retém zero pares em V6.** Isto é o problema bilíngue declarado no desenho do
blocker se manifestando: A está em inglês, C em português, e o par A-C não acumula três
conceitos congelados compartilhados **mais** um objeto nomeado compartilhado. As três
fontes ainda participam da Fusion — A por A-B, C por B-C — mas **não existe julgamento
semântico direto entre A e C** nesta execução.

**(c) 51 de 82.020 é 0,06% de cobertura.** Esta Fusion demonstra o pipeline e a
classificação auditável; ela **não** é cobertura cross-source exaustiva, e nada aqui
deve ser lido como tal.

`BLOCKER_RETENTION != SEMANTIC_RELATION`: a retenção mede alcance lexical e conceitual,
nunca existência de relação.

## 4. Taxonomia e convenção de direção

Sete labels, herdados sem alteração semântica do MS-001B. `PRESUPPOSES` permanece
`OPEN / NOT_REQUIRED`. Para três fontes, LEFT e RIGHT são fixados pela **ordem
lexicográfica do `source_id`**: A<B<C. Determinístico, invariante entre runs.

## 5. Governança

Nenhuma relation produz precedence automaticamente. Todo par nasce
`governance_state = NOT_YET_ADJUDICATED` e assim permanece. Precedence nunca é derivada
de data, autor, seguidores, canal, modelo ou confiança informal.

## 6. Execução

    partição: 51 pares em 3 batches (25 / 25 / 1)
    3 runs independentes · cada run: 1 controle J1-J10 + 3 batches = 4 chamadas
    total 12 chamadas · isolamento por processo fresh

Controle falho → run `INVALID`, batches **não** queimados.

## 7. Transporte

    MODEL_TRANSPORT = CLAUDE_CODE_MAX_OAUTH_PRINT_MODE · claude-opus-5 · Claude Code 2.1.251
    PAYG PROIBIDA. Guard de ambiente aborta se qualquer variavel proibida estiver definida.
    Limite do plano -> MS_PROJECT_PAUSED_MAX_PLAN_LIMIT, nunca fallback para API.

## 8. Fora de escopo

Nenhuma Operationalization, nenhuma política MTX, nenhum Skill Pack nesta etapa.
`mtx_policy_hash` é **proibido** como input identitário da Fusion.
