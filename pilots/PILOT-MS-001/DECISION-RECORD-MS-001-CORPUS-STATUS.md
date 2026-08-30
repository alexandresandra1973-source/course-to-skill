# DECISION RECORD — status de corpus e de desenho do `PILOT-MS-001`

**`decision_id`:** `DR-MS-001-CORPUS-001` · **Data:** 2026-08-30
**Ator:** Design Review externa · **Classe:** `GIT_NATIVE_BY_DESIGN` · **Natureza:** **ADITIVA**

| base | sha256 |
|---|---|
| `MS-001-PRE-IMPLEMENTATION-DESIGN-REPORT.md` | `f82c6df14e4544bdb4df270499ee3a9ebd59fc2090b0421f1db866a089870ea7` |
| `ADDENDUM-MS-000B-CANDIDATE-PROVENANCE-CAUSE.md` | `e0be4ef6696e2540f1389d72135ce8b6bdc4dae489bd0f836b08d029628fbc14` |
| `DECISION-RECORD-MS-000B-FINAL-ACCEPTANCE.md` | `5e689af702a2c043adfa6be63e864465dc3d579dff2f2066787456c3fb13d4d8` |

---

## D1 — O corpus preservado **não serve**

# `EXISTING_PRESERVED_CORPUS = NOT_SUITABLE_FOR_MS_001`

Razões **medidas**, não impressões:

1. **P001 sem L0 utilizável** — o L0 `068b4998…` (`transcript-original-en.txt`) não está
   preservado no espelho; a cadeia não pode terminar. E `PILOT-001-v2` não tem candidates.
2. **P002 / P003 / P004 tratam de assuntos majoritariamente distintos** — Claude Code,
   Google Ads para e-commerce, e Meta Business Suite.
3. **P003 × P004 é o melhor par existente**, e ainda assim insuficiente.
4. **Sobreposição lexical não implica comparabilidade.** Claims curtas de P004 pontuam 1,00
   contra o vocabulário de P003 apenas por presença de termos — é a mesma armadilha que a
   Round 2 do MS-000B já proibiu como prova.
5. **Os pares sobreviventes não fornecem substância suficiente.** Sobrevivência por tokens
   de conteúdo compartilhados:

| par | brutos | `k≥2` | `k≥3` | `k≥4` | `k≥5` |
|---|---|---|---|---|---|
| P002 × P003 | 1.103.424 | 1.523 | 37 | **0** | 0 |
| P002 × P004 | 60.032 | 171 | 5 | **0** | 0 |
| P003 × P004 | 330.042 | 1.198 | 68 | **3** | **0** |

Dos três sobreviventes em `k≥4`, um é meta-discurso sem substância. Sobram **dois**.

Com isso é impossível medir: **relation distribution** · **real positive blocker recall** ·
**true conflict** · **avaliação significativa de specialization / corroboration**.

> **Isto não é falha arquitetural.** A arquitetura está pronta e a proveniência de candidate
> está resolvida. É o material que não foi montado para esta pergunta: o acervo é um corpus
> de **avaliação de curso**, com assuntos deliberadamente disjuntos.

# `CONTROLLED_CORPUS_REQUIRED`

## D2 — Independência: precisão exigida

**P003 × P004 permanece `UNKNOWN`.**

Não é promovido a `DECLARED_INDEPENDENT`. Sinais de dependência foram buscados
mecanicamente e não encontrados — mas **ausência de evidência de dependência ≠ declaração de
independência**, e `UNKNOWN ≠ INDEPENDENT` é regra congelada.

> Correção registrada: o Pre-Implementation Design Report propôs `DECLARED_INDEPENDENT`
> "sujeito a declaração formal". Essa proposta é **rejeitada**. O estado é `UNKNOWN`, e
> promovê-lo exigiria uma declaração externa que hoje não existe em artefato algum.
> É exatamente a condição de morte `K10` — tratar `UNKNOWN` como independente.

## D3 — Proveniência de candidate: causa esclarecida, portão mantido

A causa de `CANDIDATE_DIRECT_PROVENANCE_NOT_YET_QUALIFIED` é
`MS_000B_ROUND_3_PACKAGER_PROVENANCE_LOSS`, registrada em
`ADD-MS-000B-PROVENANCE-001`. `PILOT_LIMITATION != CORPUS_LIMITATION`.

O portão **continua obrigatório**: `CANDIDATE_PROVENANCE_GATE_REQUIRED_IN_MS_001`. O MS-001
prova a cadeia no **novo** Source Package contract; não a herda por inferência.

## D4 — Corpus novo: **hipótese**, não seleção

Registrado **apenas como hipótese de desenho futura**:

| par | conteúdo |
|---|---|
| **B** | `Claude Code + Evolution API + WhatsApp` |
| **C** | `n8n + Evolution API + Redis + agente` |

Razão do interesse: sobreposição **esperada** em Evolution API · WhatsApp · webhook/mensagens
de entrada · automação · fluxo de resposta · orquestração.

Estado:

```
NOT_YET_AUDITED
NOT_YET_SELECTED
NOT_YET_DECLARED_INDEPENDENT
```

**B e C não foram inspecionados nem compilados neste registro.** O bloco A
(Nick Saraev / Claude Code Marketing Full Course) permanece igualmente reservado. A
sobreposição citada é **expectativa declarada**, não medição — e vira medição obrigatória
antes de qualquer seleção.

## D5 — Status

# `MS_001_DESIGN_READY_FOR_CONTROLLED_CORPUS_DESIGN`

# `MS_001_EXECUTION_NOT_AUTHORIZED`

Todos os thresholds permanecem **OPEN**. Nenhum Opening Record é escrito enquanto o corpus
não estiver decidido — escrever agora seria fixar método com decisões abertas.
