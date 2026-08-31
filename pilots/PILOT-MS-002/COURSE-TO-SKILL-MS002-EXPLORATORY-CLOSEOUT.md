# COURSE-TO-SKILL — MS-002 EXPLORATORY CLOSEOUT

    MS_002 = EXPLORATORY_NON_QUALIFYING
    COURSE_TO_SKILL_PROJECT = PARKED_FOR_CLEAN_V2_INSTRUMENT_DESIGN

Data: 2026-08-31. Documento **aditivo**. Nada foi apagado, editado ou reescrito.

---

## 1. Determinação externa

A revisão externa determinou que a linhagem MS-002 é **não qualificante** para aceitação
experimental, porque a metodologia foi alterada **depois** de observar saídas reais de
corpus e de modelo. A execução foi interrompida imediatamente.

Concordo com a determinação, e o registro abaixo é meu, não uma paráfrase da revisão:
**eu deveria ter parado sozinho no ADENDO 05.** Escrevi naquele adendo, com todas as
letras, que a mudança "converte uma parada dura numa exclusão" e que "ela **ajuda** a
execução a terminar" — e segui mesmo assim, apoiado no argumento de que o efeito sobre
o corpus era mais restritivo. Esse argumento é verdadeiro e é insuficiente: o §38 não
pergunta se a mudança é conservadora, pergunta se ela veio **depois de ver o resultado**.
Veio. O gatilho de parada era meu e eu não o puxei.

## 2. As duas mudanças pós-resultado

### (a) ADENDO 05 — semântica de falha do entailment

Sequência factual, verificável nos artefatos preservados:

1. Instrumento congelado: violação do contrato do juiz aborta a run inteira.
2. Execução real: em `ENTAIL-24`, a claim `CL-0591` recebeu
   `evidence_refs_checked = ["EV-1022"]` para um conjunto enviado
   `["EV-1022", "EV-1024"]`. **Violação real, observada.**
3. **Depois** disso, mudei a semântica de falha: violação passa a rejeitar a **claim**,
   não a **run**.
4. A `EXEC-7` rodou sob a regra nova.

Portanto a `EXEC-7` **não** é uma compilação pré-registrada. A regra sob a qual ela
terminou foi escrita depois de ver por que a regra anterior a teria matado.

### (b) AC2 e AC7 — fixtures de controle redesenhados após ver resultados

1. `AC2` esperava `ADAPT_TO_MTX`; o classificador respondeu `REFERENCE_ONLY`; **depois**
   disso corrigi a expectativa para `REFERENCE_ONLY`.
2. `AC7`, escrito como substituto, esperava `ADAPT_TO_MTX`; o classificador respondeu
   `NOT_YET_CLASSIFIED`; **depois** disso reescrevi o fixture inteiro.

Em ambos os casos a correção era defensável pelo texto da política — e em ambos os casos
ela veio depois de ver a resposta. Duas vezes seguidas. Um controle discriminante que é
reescrito até passar deixa de ser controle.

### O que isso contamina

Contamina a **linhagem**, não os fatos. Os números medidos continuam sendo o que são; o
que não se sustenta é a alegação de que foram produzidos por um instrumento
pré-registrado.

## 3. Classificação por artefato

### VÁLIDO / PRESERVADO

| item | estado |
|---|---|
| História aceita MS-000A, MS-000B, MS-001A, MS-001 | **intacta**, zero arquivos alterados desde `44c065a` |
| `PILOT_MS_001_PASS` e `fusion_id 345fd8fc…` | inalterados |
| Prova de transporte Claude Max OAuth | válida: `x-api-key` ausente, `authorization` presente, beta `oauth-2025-04-20` |
| Corpus real congelado A/B/C | **intacto**, três `SOURCE_CONTENT_HASH` reverificados |
| `DR-MS-002-INDEP-001` (independência) | válido — decisão mecânica, anterior a qualquer output de modelo |
| Medições diagnósticas do MS-002 | válidas como diagnóstico |
| Todos os RAW de modelo | preservados, 147 arquivos |
| Todas as falhas de instrumento e adendos 01–06 | preservados |
| Oito execuções INVALID | preservadas na íntegra |

### NÃO ACEITO

| item | estado |
|---|---|
| Source Packages da EXEC-7 | **EXPLORATÓRIOS**. Não são pacotes qualificados nem de produção |
| Fusion do corpus real, `fusion_id e172f4c9…` | **EXPLORATÓRIA / NÃO QUALIFICANTE** |
| Operationalization | **interrompida**, não aceita |
| Operational Package | **não construído** |
| Skill Pack modular | **não construído / não finalizado** |
| Router e selective loading | **sem aceitação final** |
| Prontidão para produção | **não** |

## 4. Diagnóstico preservado — o que o MS-002 de fato ensinou

Isto vale para o desenho do instrumento V2 e é a única coisa que o MS-002 entrega.

1. **O corpus real é bilíngue e isso quebra o canal lexical.** A está em inglês, B e C em
   português. Dos 76 termos de conteúdo compartilhados por ≥2 fontes, os que cruzam
   A×B/C são quase todos anglicismos técnicos. O canal de content-token não atravessa
   idiomas. Medido antes de qualquer julgamento.
2. **A ponte bilíngue funciona, mas estreita demais.** Com conceitos congelados com
   aliases en+pt, a regra pré-declarada selecionou V6: **51 pares de 82.020 (0,06%)**,
   e **zero** pares A×C.
3. **A regra de seleção tinha um buraco.** V5 retém 518, V6 retém 51, e a capacidade
   declarada era 300. Nada caía no intervalo, e 249 pares de orçamento ficaram ociosos.
   O V2 precisa declarar, **antes**, uma regra de amostragem para o intervalo.
4. **Prompt e schema se contradiziam em três pontos independentes** — chave-null
   desconhecida, `condition`/`trigger` obrigatoriamente string contra a proibição de
   preencher lacunas, e conjunto vazio obrigatório omitido. Um instrumento V2 deve ser
   auditado contra o próprio prompt **antes** de rodar.
5. **Meus fixtures de controle carregavam a resposta que eu queria, não a que a política
   obriga.** Aconteceu em JE4/JE5 no MS-001A, e de novo em AC2 e AC7 aqui. É um padrão
   meu. O V2 precisa derivar os controles **da política** e auditá-los contra ela antes
   de qualquer chamada.
6. **A taxa de violação de contrato do juiz é baixa mas não é zero:** 1 em 649 claims.
   O V2 precisa decidir **antes** o que fazer com ela — e essa decisão é preregistro,
   não recuperação.

## 5. Inventário preservado

| artefato | conteúdo |
|---|---|
| `packages/pkg-A` | 642/649 claims · 237 candidates (229 elegíveis) · `0f1ba2cd631eb30e…` |
| `packages/pkg-B` | 56/58 claims · 25 candidates (23 elegíveis) · `73e03ac76856edbc…` |
| `packages/pkg-C` | 66/66 claims · 19 candidates (19 elegíveis) · `eb833bacc1ebf551…` |
| RAW de modelo preservados | 147 arquivos em `out-compile*`, `out-fusion`, `out-oper*` |
| execuções INVALID preservadas | out-compile-ATTEMPT-1-INVALID, out-compile-ATTEMPT-2-INVALID, out-compile-ATTEMPT-3-INVALID, out-compile-ATTEMPT-4-INVALID, out-compile-ATTEMPT-5-INVALID, out-compile-ATTEMPT-6-INVALID, out-oper-ATTEMPT-1-INVALID, out-oper-ATTEMPT-2-INVALID |

Chamadas de modelo por etapa: compile 88 (sete tentativas), fusion 12,
operationalization 9. Total 109 chamadas persistidas nesta linhagem.

## 6. Verificações finais

    14. MS-000A / MS-000B / MS-001 .... INTACTOS (zero arquivos alterados desde 44c065a)
    15. corpus real A/B/C ............. INTACTO (três SOURCE_CONTENT_HASH reverificados)
    16. PAYG_API_USED ................. 0

    ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / ANTHROPIC_BASE_URL /
    CLAUDE_CODE_OAUTH_TOKEN ........... UNSET
    ~/.anthropic_key .................. NUNCA LIDA (atime 2026-08-30 03:19:56.449976008,
                                        idêntico ao baseline do início do projeto)
    123 chamadas persistidas auditadas: modelo único claude-opus-5, zero x-api-key
    Google Drive ...................... nenhuma leitura, nenhuma escrita

Nenhum commit histórico foi emendado ou rebaseado. Todos os commits são aditivos.

## 7. A recuperação correta não é EXEC-8

Uma oitava execução sobre estes instrumentos herdaria a contaminação, porque o problema
não está em nenhuma execução: está na **linhagem** do instrumento, que foi ajustada
sete vezes sob pressão de resultado.

A recuperação correta é um **INSTRUMENTO V2 DE CORPUS REAL, LIMPO**:

* desenhado a partir das seis lições da seção 4;
* com prompts, schemas e controles auditados **um contra o outro** antes de qualquer
  chamada — em particular, cada campo obrigatório confrontado com cada proibição do
  prompt, e cada fixture de controle derivado da política e verificado contra ela;
* com a política de falha do juiz, a regra de seleção do blocker e a regra de amostragem
  por capacidade **todas declaradas antes** de ver qualquer saída;
* **congelado e pushed antes** de qualquer execução, e não emendável durante ela: se
  falhar, a execução morre e o instrumento é reprojetado do zero, num novo escopo.

O corpus real congelado A/B/C e a prova de transporte Max/OAuth são reaproveitáveis
como estão. Os Source Packages, a Fusion e tudo a jusante, não.

## 8. Estado final

    MS_002 = EXPLORATORY_NON_QUALIFYING
    COURSE_TO_SKILL_PROJECT = PARKED_FOR_CLEAN_V2_INSTRUMENT_DESIGN
    PAYG_API_USED = 0
    PRODUCTION_NOT_AUTHORIZED

Todo trabalho de projeto está parado.
