# MS-001B — NOTA DE RECUPERAÇÃO PARA A EXECUÇÃO 4

Data: 2026-08-31. Duas correções autorizadas por decisão externa, ambas **aditivas**.

## DEF-1 — corrigido

`ms001b/RELATION-SCHEMA-v2.json`, aditivo. `RELATION-SCHEMA-v1.json` preservado.

Diff completo em relação ao v1 — duas linhas, nenhuma delas semântica:

    - "title": "MS-001B RELATION JUDGMENT v1"
    + "title": "MS-001B RELATION JUDGMENT v2"

    - "batch_id": {"type": "string", "pattern": "^BATCH-[1-4]$"}
    + "batch_id": {"type": "string", "enum": ["BATCH-1","BATCH-2","BATCH-3","BATCH-4A","BATCH-4B"]}

Enum explícita da partição ativa, preferida à regex genérica. Todo o resto do
documento — `judgments`, relações, direções, scopes, `relation_why`, igualdade de
evidence, tabelas de compatibilidade mecânica — é byte-idêntico.

    RELATION-SCHEMA-v1.json  35c5814841711d4c92b9dc7e869b01902405bd40944a48720ad2d3f4c4db1973
    RELATION-SCHEMA-v2.json  62f37d6d889c923d88505a6d4b6d3cee09f7a0a74d9bd55b6bf217ea7a2c5fba

Canários RS1–RS11: **11/11 PASS** (`schema_canaries_v2.py`), sem modelo. Destaque:

* **RS4** — `BATCH-4` agora FALHA, por não pertencer à partição ativa.
* **RS6** — o payload real emitido pela EXEC-3 no BATCH-4A, com `batch_id` corrigido
  para `BATCH-4A`, valida sob o schema v2. Confirma que o defeito era exclusivamente
  o rótulo, e que os 11 julgamentos daquela chamada eram estruturalmente corretos.
* **RS9** — verificação mecânica de que v2 difere de v1 somente em `title` e `batch_id`.

O validador `lib/relation_validate.py` permanece **inalterado**: ele nunca leu o
`pattern` do schema; comparava, e continua comparando, o `batch_id` com o rótulo
literal do batch.

## DEF-2 — corrigido declarativamente

`ERRATA-MS001B-BLOCKER-CONTROL-SEMANTICS.md`. Nenhum dado alterado. BC1–BC5 passam a
ser classificados como **blocker retention / coverage probes**, sem expected relation
por par; J1–J10 permanecem o único controle semântico discriminante.

    BC_BUCKET_MEMBERSHIP  !=  EXPECTED_SEMANTIC_RELATION
    BLOCKER RETAINS A PAIR   não implica   SEMANTIC RELATION EXISTS

## EXEC-3 — preservada como INVALID

    MS_001B_EXEC_3 = INVALID
    razão primária: RELATION_SCHEMA_BATCH_ID_MISMATCH

Os 86 julgamentos válidos antes da falha e os controles J1–J10 PASS permanecem
auditáveis em `out-ms001b-exec3/`, mas **não** entram em estabilidade, distribuição
final, Fusion ou veredito de aceitação. Nenhum judgment da EXEC-3 é reutilizado.

## Inalterado

Corpus · Source Packages · Claims · Candidates · blocker v0.3 · feature model · V1 ·
pairset de 97 pares · `PAIRSET_HASH` · taxonomia · definições semânticas · semântica de
scope · SYSTEM do prompt semântico · J1–J10 · família de modelo · transporte Max/OAuth ·
política de estabilidade · semântica de Fusion · `lib/relation_validate.py`.
