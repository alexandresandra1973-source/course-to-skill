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

---

## Tentativa 2 — preservada como INVALID

    MS_002_APPLICABILITY_ATTEMPT_2 = INVALID
    razão: AC7_FIXTURE_USES_UNLISTED_CHANNEL

    AC1 OK · AC2 OK · AC3 OK · AC4 OK · AC5 OK · AC6 OK · AC7 FALHA(NOT_YET_CLASSIFIED)

O AC2 corrigido passou. O AC7 que eu havia acabado de escrever falhou — e, de novo, o
modelo estava certo e o fixture errado.

O AC7 da tentativa 2 descrevia publicar **vídeo longo horizontal no YouTube**. A
`MTX-POLICY-v1` **não lista YouTube** em canal algum: nem prioritário, nem secundário.
O prompt do classificador manda, nessa situação, usar `NOT_YET_CLASSIFIED`:

    NOT_YET_CLASSIFIED
      FAIL-CLOSED. Use quando a unidade nao traz informacao suficiente para decidir, ou
      quando decidir exigiria inventar contexto que a unidade nao da. NA DUVIDA, USE ESTA.

Esperar que o modelo mapeasse YouTube para Instagram por conta própria era pedir
exatamente a invenção que a regra 2 do mesmo prompt proíbe. **Eu escrevi um fixture que
exigia violar o instrumento para passar.**

### AC7 refeito — dentro de canal prioritário

A unidade agora é uma regra de publicar a dica diária **no feed do Instagram** como post
de **texto puro, sem imagem e sem vídeo**. Sob a política:

* Instagram é rank 1 — logo, não é `REFERENCE_ONLY` nem `REJECT`;
* a substância (publicar a dica diária no Instagram) se aplica — logo, não é `NOT_YET_CLASSIFIED`;
* a forma **precisa** mudar, porque a política diz "especialmente vídeos e imagens" e
  porque o canal não veicula texto puro — logo, não é `DIRECT_USE`.

Resta `ADAPT_TO_MTX`, com adaptação concreta e não inventiva: renderizar a dica como
imagem ou vídeo. A classe esperada decorre da política, sem depender de nada que o
modelo tenha respondido.

### Registro honesto

Este é o **segundo** fixture meu, seguido, cuja expectativa não era sustentada pelas
regras do próprio instrumento — depois do AC2 e, antes dele, do mesmo padrão em JE4/JE5
no MS-001A. O padrão é meu, não do modelo: ao escrever controles, embuti o que eu
queria que a resposta fosse em vez do que a política obriga. Registro isso porque é
informação de auditoria, não ruído.

Nenhuma classificação real foi produzida em nenhuma das duas tentativas: o portão
bloqueou na primeira chamada das duas vezes. Não há resultado de corpus a que ajustar.
