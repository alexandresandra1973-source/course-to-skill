# ADENDO 01 — OPENING RECORD MS-002 COMPILE

Aditivo. Não altera o Opening Record original. Data: 2026-08-31.

## Tentativa 1 — preservada como INVALID

    MS_002_COMPILE_ATTEMPT_1 = INVALID
    razão: X04_EXTRA_FIELD_IN_EXTRACTION_BUNDLE

Preservada integralmente em `out-compile-ATTEMPT-1-INVALID/`, com os RAW, os STDOUT e os
resultados dos controles. Nenhum output foi editado.

O que aconteceu: os controles passaram (EC 7/7, JE 5/5) e a fonte C compilou por inteiro
(61 claims, 60 seladas, 24 candidates). Na primeira slice de A, o schema estrito rejeitou
o bundle porque **um** candidate de sete trazia uma chave extra:

    "temporary_claim_id_placeholder": null

Todos os campos obrigatórios estavam presentes e corretos, incluindo
`claim_temp_refs: ["TC-026"]`. A chave excedente carregava valor literalmente `null`.

## Diagnóstico

`additionalProperties: false` fez o que devia: falhou fechado. Mas o defeito é
**instrumental**, não semântico — uma chave de valor nulo não carrega informação. Deixar
o pipeline morrer nisso, em 1 de 19 slices da fonte maior, seria desproporcional; e
afrouxar `additionalProperties` destruiria o contrato.

## Recuperação autorizada — normalização determinística pré-validação

Classe: **parser determinístico** (recuperação instrumental autorizada).

    strip_null_unknown(doc, schema)

Remove **exclusivamente** chaves desconhecidas cujo valor é literalmente `null`, em
qualquer profundidade, apenas onde o schema declara `additionalProperties: false`.

O que **continua** falhando fechado, sem exceção:

* chave desconhecida com valor **não-null** → `ValidationError`;
* campo obrigatório ausente → `ValidationError`;
* valor fora de enum, padrão ou tipo → `ValidationError`;
* `X01_SLICE_MISMATCH`, `X02_INVENTED_EVIDENCE`, `X03_DANGLING_CLAIM_REF`,
  `E01_ENTAIL_SET_MISMATCH`, `E02_EVIDENCE_SET_MISMATCH`, `INVALID_PROVENANCE > 0`.

Nenhum valor é alterado. Nenhum campo obrigatório é preenchido. Nenhuma correção
semântica é feita. **Toda** remoção é registrada, com caminho completo, em
`COMPILE-STATE.json → addendum_01_stripped_null_unknown_keys`, e impressa no log.

## Execução 2

Recompila as três fontes do zero, para que A, B e C compartilhem um único
`TOOLCHAIN.json`. Nenhum resultado da tentativa 1 é reutilizado — nem os controles, nem
a fonte C já selada. Os controles EC e JE são reexecutados.

## Inalterado

Corpus congelado · `SOURCE_CONTENT_HASH` de A/B/C · camada L0 · prompts de extração e de
entailment · schemas · fixtures dos controles EC e JE · transporte Route B ·
proibição de PAYG.
