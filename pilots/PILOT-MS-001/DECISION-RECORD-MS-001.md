# DECISION RECORD — MS-001

    PILOT_MS_001_PASS
    MS_001_ACCEPTED_FOR_EXPERIMENTAL_MULTI_SOURCE_FUSION
    MODEL_TRANSPORT = CLAUDE_MAX_OAUTH
    PAYG_API_USED = 0

Data: 2026-08-31. Execução válida: **EXEC-4**.
`fusion_id = 345fd8fc6d5fbdf5d164ddd290aef3cd6a2d4c7d451e722b392cd0f024c08306`

---

## Decisão

O PILOT-MS-001 é aceito para fusão multi-source **experimental**. O pipeline produziu,
sob transporte de plano Claude Max e sem qualquer gasto pay-as-you-go, três runs
independentes e completas, com controle semântico discriminante aprovado em todas,
estabilidade total entre runs, identidade tipada e provenance íntegras, e um Fusion
Package auditável com identidade determinística.

## O que foi provado

* **Pipeline multi-source auditável.** Dois Source Packages selados e byte-idênticos,
  um blocker determinístico, 97 pares tipados, um juiz semântico isolado por processo,
  validação mecânica fail-closed e uma identidade de fusão reproduzível.
* **Classificação auditável.** Todo julgamento é rastreável do par tipado até a âncora
  de evidência, com o raw preservado byte a byte e o hash do input e do output por
  chamada.
* **Transporte de assinatura.** O experimento roda inteiro na franquia Claude Max, com
  isolamento por processo mais forte que o do transporte original, e com prova de
  nível de transporte de que nenhuma chamada passou pelo Console pay-as-you-go.

## O que NÃO foi provado, e não se alega

O corpus não exibiu sobreposição semântica entre as duas fontes: os 97 pares admitidos
pelo blocker foram julgados `UNRELATED` nas três runs. Isso é **resultado válido**, não
falha — o objetivo declarado era provar o pipeline e a classificação auditável, não
fabricar sobreposição.

Em particular, **não** se alega: que o juiz foi exercitado em relações não triviais
sobre corpus real; que o blocker seleciona pares semanticamente relacionados; nem que
BC1–BC5 medem correção semântica. O único exercício discriminante das sete relações são
os controles sintéticos J1–J10, aprovados 10/10 em cada uma das três runs.

## Correções incorporadas

* **DEF-1** — `RELATION-SCHEMA-v2.json`, aditivo. Única mudança semântica: `batch_id`
  passa de `pattern ^BATCH-[1-4]$` para enum explícita da partição ativa. Ver
  `MS-001B-EXEC-4-RECOVERY-NOTE.md`.
* **DEF-2** — `ERRATA-MS001B-BLOCKER-CONTROL-SEMANTICS.md`, declarativa. BC1–BC5
  reclassificados como retention/coverage probes.
  `BC_BUCKET_MEMBERSHIP != EXPECTED_SEMANTIC_RELATION`.

Nenhum dado foi ajustado ao resultado. `POST_RESULT_TUNING = false`.

## Preservado sem alteração

Corpus · Source Packages (`a0a73dde…`, `5959b4ea…`) · Claims · Candidates ·
blocker v0.3 (`BLOCKER_FEATURE_MODEL_QUALIFIED`) · feature model · V1 · 97 pares ·
`PAIRSET_HASH a0b116d9…` · taxonomia · definições semânticas · semântica de scope ·
SYSTEM do prompt (`37dc0211…`, idêntico ao da EXEC-1) · J1–J10 · família de modelo ·
política de estabilidade · semântica de Fusion · `lib/relation_validate.py`.

Execuções históricas EXEC-1, EXEC-2 e EXEC-3 preservadas integralmente. Nenhum judgment
da EXEC-3 reutilizado.

## Escopo explicitamente não autorizado

Não iniciar: Operationalization · Operational Package · Router · Skill Pack · Source A ·
MTX policy · N1–N9 · produção. A aceitação é para fusão **experimental**, e não autoriza
produção.
