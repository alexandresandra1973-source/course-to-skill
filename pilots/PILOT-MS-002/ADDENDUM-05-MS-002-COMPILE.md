# ADENDO 05 — OPENING RECORD MS-002 COMPILE

Aditivo. Data: 2026-08-31.

## Tentativa 5 — preservada como INVALID

    MS_002_COMPILE_ATTEMPT_5 = INVALID
    razão: E02_EVIDENCE_SET_MISMATCH (abortou a run inteira)

Preservada em `out-compile-ATTEMPT-5-INVALID/`. O resume do ADENDO 04 funcionou: 19
bundles de A revalidados. O entailment de A avançou até `ENTAIL-23` — **575 de 649
claims julgadas sem uma única violação** — e abortou em `ENTAIL-24`.

## Diagnóstico

Numa claim, `CL-0591`, o juiz devolveu `evidence_refs_checked = ["EV-1022"]` quando o
conjunto enviado era `["EV-1022", "EV-1024"]`. A regra 6 do prompt de entailment é
explícita:

> Voce verificou EXATAMENTE as Evidence fornecidas para aquela Claim, nem mais nem
> menos, e as lista em `evidence_refs_checked`.

**O juiz violou o contrato.** Isto não é defeito de instrumento e não é corrigível: o
instrumento está certo, e o fail-closed detectou o que devia detectar.

Taxa observada: **1 em 600 claims julgadas** (0,17%). Os controles JE1–JE5 passaram 5/5
na mesma execução, então o poder discriminante do juiz está estabelecido.

## O que muda — e o que não muda

O defeito não é o que o validador detectou, é **o que ele faz em seguida**: abortar a
compilação inteira das três fontes por causa de um veredito ruim em uma claim é
desproporcional e não torna o corpus mais confiável.

    ANTES:  violação de contrato  ->  a RUN inteira é INVALID
    AGORA:  violação de contrato  ->  a CLAIM é REJEITADA

Nada é reparado. Nada é reinterpretado. O veredito é **recusado** e descartado; a claim
recebe `status = REJECTED_ENTAILMENT_CONTRACT_VIOLATION` e **não entra** em
`CLAIMS.jsonl`. O veredito descartado é registrado com o conjunto enviado, o conjunto
devolvido e o julgamento que foi jogado fora, em
`COMPILE-STATE.json → addendum_05_rejected_entailment_contract_violations`.

### Guard de taxa — pré-declarado

    E02_MAX_RATE = 0.01

Se a taxa de vereditos recusados passar de 1% das claims de uma fonte, o instrumento
não está discriminando e a execução aborta com `MS_002_INVALID`. O limite é uma ordem de
grandeza acima da taxa observada e uma ordem de grandeza abaixo de qualquer taxa que
sugerisse falha sistemática.

### Registro honesto do efeito

Esta mudança converte uma parada dura numa exclusão. Ela **ajuda** a execução a
terminar, e por isso registro explicitamente por que não é tuning para aprovação:

* a claim afetada é **excluída**, não aceita — o efeito no corpus é mais restritivo, não menos;
* nenhum output foi reinterpretado, nenhum julgamento foi corrigido;
* `E01` (conjunto de claim_ids diferente do enviado) **continua** sendo aborto duro:
  é falha de completude, classe diferente;
* a contagem de recusas é reportada no relatório final, não escondida;
* o guard de taxa foi declarado **antes** de rodar, e é ele que decide se o instrumento
  ainda vale.

## Resume de entailment

A execução 6 reaproveita, além dos bundles de extração de A, os **23 batches de
entailment já concluídos** da tentativa 5, relendo os RAW persistidos e revalidando cada
verdict do zero sob o validador corrigido — mesmo tratamento do ADENDO 04. O batch 24 em
diante é chamado de novo. Nada do estado interno é reaproveitado.

## Inalterado

Corpus congelado · camada L0 · prompts de extração e entailment (**byte-idênticos**) ·
schemas · fixtures EC e JE · transporte Route B · proibição de PAYG · normalizador
schema-aware · regra e lista fechada do ADENDO 03.
