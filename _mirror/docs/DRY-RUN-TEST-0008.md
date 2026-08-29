# Ensaio seco da maquinaria do TEST-0008

- Gerado: `2026-08-11T04:57:12+00:00` · gerador `dry_run_test0008.py`
- Notas **sintéticas**, marcadas `SYNTHETIC_DRY_RUN`, em `/tmp/dryrun-0008`.
- Nenhuma condição executada, nenhuma Skill compilada, nada congelado, nada em pasta definitiva.
- Aritmética exata (`Fraction`), como na prova de alcançabilidade.

## 1. As duas comparações, sobre notas sintéticas

`P = FULL_SKILL − SUMMARY_AS_SUMMARY` (primária) · `F = SUMMARY_AS_SKILL − SUMMARY_AS_SUMMARY` (enquadramento)

| regime | FULL | SaSummary | SaSkill | P | F | \|F\| | F/P | \|F\|/\|P\| | mesma direção |
|---|---|---|---|---|---|---|---|---|---|
| **R1** — framing pequeno em relação a P | 93 | 53 | 54.6 | **40** | **1.6** | 1.6 | 0.04 | 0.04 | sim |
| **R2** — framing fração material de P | 93 | 53 | 66.8 | **40** | **13.8** | 13.8 | 0.345 | 0.345 | sim |
| **R3** — framing da ordem de P | 93 | 53 | 90.4 | **40** | **37.4** | 37.4 | 0.935 | 0.935 | sim |
| **R4** — framing em direção OPOSTA a P | 93 | 53 | 46.6 | **40** | **-6.4** | 6.4 | -0.16 | 0.16 | **não** |

As cinco quantidades que o ADR manda publicar — `F`, `P`, `|F|`, `|P|`, `F/P` e `|F|/|P|` — são todas computáveis com o que existe. **A aritmética não é o gargalo.**

## 2. As três leituras pré-declaradas

| regime | leitura que o ADR manda aplicar |
|---|---|
| **R1** F/P = 0.04 | enquadramento não explica o resultado primário; P pode sustentar a alegação de valor estrutural |
| **R2** F/P = 0.345 | publicar a parcela de enquadramento e qualificar proporcionalmente a alegação |
| **R3** F/P = 0.935 | resultado primário só é interpretável como efeito de enquadramento; **não sustenta a premissa** |
| **R4** F/P = -0.16 | direção oposta: publicar a direção; não explica vantagem da Skill, mas entra na sensibilidade |

> **O que este ensaio NÃO consegue fazer.** Ele mostra em que regime cada conjunto de notas cai *se* os pontos de corte já existissem. Eles não existem. "Pequeno", "fração material" e "da ordem de" são rótulos qualitativos até alguém congelar números — e o ADR exige que esses números venham da variância medida sob a régua final do 0008, proibindo herdar o `w` do 0007. Atribuí os regimes acima por construção das notas, não por regra vigente.

## 3. O que a maquinaria exige e NÃO existe

**13 de 14 itens ausentes.**

| item | por que é exigido |
|---|---|
| **rubrica do TEST-0008 CONGELADA** | sem régua congelada não há critério, peso nem piso |
| **addendum de âncora do TEST-0008** | as âncoras por perfil de comportamento, como o 0007 tem |
| **lista canônica de comparison_metrics congelada** | bloqueador 1 do ADR: a discrepância 5×6 tem de ser resolvida antes |
| **variância do avaliador do TEST-0008** | sem ela não há largura de incerteza própria; o ADR proíbe herdar o w do 0007 |
| **bandas de interpretação F/P, numéricas e congeladas** | os três regimes precisam de pontos de corte numéricos, da variância |
| **teto estrutural do TEST-0008** | o que a régua do 0008 consegue separar, antes da rodada |
| **regra de decisão do TEST-0008** | limiar, zona inconclusiva e piso de discriminabilidade próprios |
| **pacotes congelados das três condições** | hashes dos três pacotes, como os três braços do 0007 |
| **addendum de saída do juiz para o 0008** | campos obrigatórios: selected_anchor, anchor_ambiguity |
| **instruções de rodada cega do 0008** | o que anexar e em que ordem |
| **margin lock, registry e opening record do 0008** | a cadeia pré-run, que no 0007 já fecha |
| **suporte a DUAS comparações no mesmo teste** | o 0008 precisa de P e F; o modelo de dados expressa um par só |
| **suporte a TRÊS condições** | o modelo atual é par esquerda/direita mais preservação antes/depois |

Existem:

- contrato de pontuação cobrindo o 0008 — `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK.zip :: PILOT-001-v0.1.3-REVISION-PACK/JUDGE-SCORING-CONTRACT-v0.1.3.yaml`

### A entrada legada do 0008, que existe e não serve

Encontrei **13** contrato(s) antigo(s) com `TEST-0008` declarado em `comparative_tests`:

- `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK.zip :: PILOT-001-v0.1.3-REVISION-PACK/JUDGE-SCORING-CONTRACT-v0.1.3.yaml`
  - `comparison`: `SKILL_MINUS_SUMMARY`
  - `margin_threshold`: `PRELOCKED_IN_TEST_SUITE_OR_COMPARISON_LOCK`
- `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV2.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV2/canary/contract-undefined-aggregation.yaml`
  - `full_preservation_guard_required`: `False`
- `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV2.zip :: PILOT-001-v0.1.3-REVISION-PACK-REV2/canary/contract-canary.yaml`
  - `full_preservation_guard_required`: `False`

Isso é pior que ausência, e por isso vale destaque. A entrada declara **uma** comparação, `SKILL_MINUS_SUMMARY`, e um limiar adiado. Ela codifica o desenho de **duas** condições — Skill contra resumo — que o ADR de paridade de informação substituiu por **três** condições e **duas** comparações. `SKILL_MINUS_SUMMARY` não desambigua entre `P` (FULL − SUMMARY_AS_SUMMARY) e `F` (SUMMARY_AS_SKILL − SUMMARY_AS_SUMMARY): sob o desenho novo, os dois cabem no nome.

Quem rodar a cadeia com esse contrato sem reler o ADR vai medir uma comparação só e não vai saber qual das duas mediu.

### Os dois que não são falta de arquivo, e sim de forma

1. **Uma comparação por teste.** No contrato, `comparative_tests` é um mapa `test_id → política`, com um único par `left`/`right`. O 0008 precisa de **duas** comparações sobre o mesmo teste, `P` e `F`. Não é preencher campo: é estender o modelo de dados.
2. **Duas condições por comparação, três no teste.** O modelo atual é par esquerda/direita mais preservação antes/depois — desenhado para ablação. As três condições do 0008 não cabem nesse formato sem mudança.

E `TEST-0008` não aparece em nenhum dos scripts da cadeia: nem no freezer, nem no registry, nem no scorer.

## 4. Quanto falta, honestamente

A cadeia do 0007 fecha hoje. A do 0008 não está a um patch de distância: faltam artefatos de conteúdo (régua congelada, âncoras, variância, bandas, teto, regra de decisão, pacotes das três condições) **e** mudança de forma no contrato e nos scripts para caber duas comparações e três condições.

A ordem importa e está no ADR: a lista canônica de `comparison_metrics` precisa ser resolvida primeiro — é o bloqueador 1 — porque régua, âncoras e derivação de métrica dependem dela. Depois vem a variância, e só então as bandas numéricas.

Nada aqui foi congelado. Nenhuma conversa cega foi aberta.

