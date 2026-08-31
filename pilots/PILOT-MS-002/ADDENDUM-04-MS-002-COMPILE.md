# ADENDO 04 — OPENING RECORD MS-002 COMPILE

Aditivo. Data: 2026-08-31.

## Tentativa 4 — preservada como INVALID

    MS_002_COMPILE_ATTEMPT_4 = INVALID
    razão: X07_NORMALIZER_NOT_SCHEMA_AWARE

**O defeito é da minha ferramenta de recuperação, não do instrumento nem do modelo.**

Preservada em `out-compile-ATTEMPT-4-INVALID/`. A extração da fonte A foi **inteiramente
bem-sucedida**: 19 de 19 slices, 649 claims, 237 candidates, todas validadas. A falha
veio na primeira chamada de entailment.

## Diagnóstico

O normalizador do ADENDO 03 aplicava a lista de defaults **sem consultar o schema
alvo**. A lista inclui `$.raw_claims` e `$.raw_candidates`, que existem no schema de
extração. Ao validar um documento de **entailment**, o normalizador injetava essas duas
chaves num documento que declara `additionalProperties: false` e só conhece `source_id`
e `verdicts`. O resultado:

    ValidationError: Additional properties are not allowed
                     ('raw_candidates', 'raw_claims' were unexpected)

O documento do modelo estava correto. Quem o corrompeu foi o meu normalizador.

## Correção — normalizador schema-aware

    _declares(schema, path)  ->  True apenas se ESTE schema declara a propriedade

Nenhum default é inserido para propriedade que o schema alvo não declare. A inserção
discriminada de `structure.do_not` também passou a exigir que o schema declare
`raw_candidates[].structure`. Teste de regressão registrado na execução: um documento de
entailment atravessa o normalizador e sai com exatamente `source_id` e `verdicts`; um
documento de extração continua recebendo `defects: []` e `do_not: []` no ramo `rule`.

## Reaproveitamento da extração de A — declarado

A tentativa 4 gastou 21 chamadas para produzir as 19 slices de A, todas válidas. Descartá-las
por um bug meu, que **provadamente não tocou a extração**, seria desperdiçar franquia do
plano sem ganho metodológico.

Evidência de que o bug não tocou a extração: em documentos de extração, `raw_claims` e
`raw_candidates` **sempre vieram presentes**, então a inserção nunca disparou. O log da
tentativa 4 registra exatamente 10 normalizações, **todas** de `defects`, e nenhuma de
`raw_claims`/`raw_candidates`.

Por isso a execução 5 usa `--resume=out-compile-ATTEMPT-4-INVALID`, que:

* relê os RAW persistidos, **não** o estado interno da tentativa 4;
* **revalida cada bundle do zero** sob o validador corrigido, incluindo
  `X01_SLICE_MISMATCH`, `X02_INVENTED_EVIDENCE` e `X03_DANGLING_CLAIM_REF`;
* aborta se qualquer bundle falhar;
* marca cada bundle reaproveitado como `RESUMED_AND_REVALIDATED` no trace.

O que **não** é reaproveitado: controles EC e JE (reexecutados), entailment (nunca
concluiu), fontes B e C (extraídas do zero), e qualquer coisa das tentativas 1, 2 ou 3.

### Diferença em relação aos adendos anteriores

Nos adendos 01, 02 e 03 o **instrumento de extração mudou**, então os bundles anteriores
tinham sido produzidos sob instrumento superado e foram descartados. Aqui o instrumento
de extração é byte-idêntico: `EXTRACTION-PROMPT-v3` e `EXTRACTION-SCHEMA-v4` inalterados.
Só o validador mudou — e o reaproveitamento passa pelo validador novo.

## Inalterado

Corpus congelado · camada L0 · prompts de extração e entailment · schemas · fixtures EC e
JE · transporte Route B · proibição de PAYG · regra e lista fechada do ADENDO 03.
