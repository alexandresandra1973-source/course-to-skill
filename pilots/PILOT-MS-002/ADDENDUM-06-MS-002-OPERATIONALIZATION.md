# ADENDO 06 — OPERATIONALIZATION MS-002

Aditivo. Data: 2026-08-31.

## Tentativa 1 — preservada como INVALID

    MS_002_APPLICABILITY_ATTEMPT_1 = INVALID
    razão: AC_FIXTURE_CONTRADICTS_POLICY

Preservada em `out-oper-ATTEMPT-1-INVALID/`. O portão de controle bloqueou a execução
antes de qualquer classificação real, como devia. Resultado:

    AC1 OK · AC2 FALHA(REFERENCE_ONLY) · AC3 OK · AC4 OK · AC5 OK · AC6 OK

## Diagnóstico — o fixture estava errado, não o modelo

`AC2` apresentava uma sequência de nutrição por **email** em cinco toques e esperava
`ADAPT_TO_MTX`. O classificador respondeu `REFERENCE_ONLY`.

A `MTX-POLICY-v1`, congelada antes de qualquer classificação, diz:

    secondary_channels:
      channels: [email, sms, voz]
      default_treatment: REFERENCE_ONLY
      excecao: "podem receber DIRECT_USE ou ADAPT_TO_MTX quando o material operacional
                atender uma necessidade especifica declarada e rastreada"

O fixture AC2 é email puro e **não declara necessidade específica alguma**. Pela política,
`REFERENCE_ONLY` é a resposta **correta**. A expectativa do fixture contradizia a política
que o próprio instrumento carrega no prompt.

Este é o mesmo padrão que a errata JE4/JE5 do MS-001A registrou: o juiz estava certo e o
fixture é que testava a fronteira errada.

## Correção

**Justificada pelo texto da política, não pela resposta observada.** Qualquer leitor da
`MTX-POLICY-v1` chega ao mesmo veredito sem nunca ver o output do modelo.

1. **AC2** passa a esperar `REFERENCE_ONLY`, com `channels_include: email`. A nota de
   correção fica registrada dentro do próprio fixture.
2. **AC7**, novo, restaura o poder discriminante de `ADAPT_TO_MTX` testando o caso que
   AC2 deveria ter testado: um workflow de **vídeo longo horizontal para YouTube**, cuja
   substância se aplica mas cujo formato exige adaptação ao canal **prioritário**.
   Esperado: `ADAPT_TO_MTX`, com `adaptations` não vazio e `instagram` entre os canais.

O portão passa a exigir os **sete** exatos. Nenhuma classe perdeu cobertura:
`DIRECT_USE` (AC1), `ADAPT_TO_MTX` (AC7), `REFERENCE_ONLY` (AC2, AC3), `REJECT` (AC4),
`NOT_YET_CLASSIFIED` (AC5), e o caso de anti-padrão em canal prioritário (AC6).

## Por que isto não é tuning para aprovação

Relabelar AC2 para bater com a resposta do modelo, e parar aí, seria tuning. Por isso
**AC7 foi acrescentado**: a fronteira que AC2 pretendia testar continua sendo testada, e
agora com um fixture que de fato a instancia. O portão ficou **mais** exigente — sete
controles em vez de seis —, não menos.

Nenhuma classificação real havia sido produzida quando isto foi decidido: o portão
bloqueou na primeira chamada. Não há resultado de corpus a que ajustar.

## Inalterado

`MTX-POLICY-v1` (byte-idêntica) · prompt de aplicabilidade · schema de aplicabilidade ·
AC1, AC3, AC4, AC5, AC6 · Source Packages · Fusion · transporte · proibição de PAYG.
