# ADENDO 02 — OPENING RECORD MS-002 COMPILE

Aditivo. Data: 2026-08-31.

## Tentativa 2 — preservada como INVALID

    MS_002_COMPILE_ATTEMPT_2 = INVALID
    razão: X05_SCHEMA_FORCES_INVENTION

Preservada em `out-compile-ATTEMPT-2-INVALID/`. Controles EC 7/7 e JE 5/5 passaram;
SL-A-01 e SL-A-02 compilaram (29 e 45 claims). A falha veio em SL-A-03. O normalizador
do ADENDO 01 funcionou como esperado e não é a causa aqui.

## Diagnóstico — contradição interna do instrumento

`EXTRACTION-SCHEMA-v3.json`, ramo `rule_candidate`:

    "trigger":    {"type": "string"}
    "condition":  {"type": "string"}
    "precedence": {"type": ["string", "null"]}

O prompt do extrator, regra 8, diz:

> **NAO complete lacunas com conhecimento externo, com o que voce sabe sobre a
> ferramenta, nem com o que seria "boa pratica".**

Em SL-A-03 o modelo encontrou uma regra cuja fonte **não enuncia condição**. Emitiu
`"condition": null` — a leitura fiel. O schema rejeitou.

O instrumento pedia duas coisas incompatíveis: não inventar, e nunca emitir nulo. Só
havia duas saídas para o modelo: inventar uma condição (violando o prompt) ou falhar
(violando o schema). `precedence` já reconhecia exatamente esse caso e admitia `null`;
`trigger` e `condition` não. A assimetria era o defeito.

Este é o mesmo padrão do DEF-1 do MS-001B: prompt e schema, na mesma mensagem, exigindo
coisas contraditórias.

## Correção — `EXTRACTION-SCHEMA-v4.json`, aditiva

`v3` preservado. Diff completo, verificado mecanicamente:

    - "title": "SOURCE-LOCAL-EXTRACTION-BUNDLE v3"
    + "title": "SOURCE-LOCAL-EXTRACTION-BUNDLE v4"
    rule_candidate.trigger    : {"type":"string"} -> {"type":["string","null"]}
    rule_candidate.condition  : {"type":"string"} -> {"type":["string","null"]}

Verificação mecânica registrada na execução: **nenhum outro campo do schema mudou**.

### Escolha deliberada: o que NÃO foi afrouxado

| campo | mantido | por quê |
|---|---|---|
| `evidence_refs` (claims e candidates) | `minItems: 1` | provenance é inegociável |
| `workflow.steps` | `minItems: 1` | workflow sem passo não é workflow |
| `anti_pattern.do_not` | `minItems: 1` | anti-padrão sem "não fazer" não é anti-padrão |
| `rule.action`, `rule.name` | `string` | a ação **é** a regra; sempre presente |
| `additionalProperties` | `false` | contrato estrito preservado em todos os ramos |

Só `trigger` e `condition` mudaram, e apenas para o mesmo tratamento que `precedence`
já tinha. Nenhum critério de correção semântica foi alterado: `null` significa "a fonte
não enuncia", que é mais fiel do que uma string inventada.

## Por que isto não é tuning pós-resultado

A mudança não altera o que conta como resposta **certa**; altera o que o instrumento
permite **expressar**. Antes, a leitura fiel era inexprimível. Nenhum output foi
reinterpretado, nenhum limiar foi movido para obter aprovação, e nenhum resultado
semântico foi observado ao decidir — a decisão veio de ler o prompt contra o schema.

## Execução 3

Recompila as três fontes do zero, com `EXTRACTION-SCHEMA-v4.json`. Nada das tentativas 1
ou 2 é reutilizado. Controles EC e JE reexecutados.

## Inalterado

Corpus congelado · `SOURCE_CONTENT_HASH` · camada L0 · prompts de extração e entailment ·
schema de entailment · fixtures EC e JE · transporte Route B · proibição de PAYG ·
normalizador do ADENDO 01.
