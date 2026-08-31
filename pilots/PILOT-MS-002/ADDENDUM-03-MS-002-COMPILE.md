# ADENDO 03 — OPENING RECORD MS-002 COMPILE

Aditivo. Data: 2026-08-31.

## Tentativa 3 — preservada como INVALID

    MS_002_COMPILE_ATTEMPT_3 = INVALID
    razão: X06_REQUIRED_EMPTY_SET_OMITTED

Preservada em `out-compile-ATTEMPT-3-INVALID/`. Controles EC 7/7 e JE 5/5 passaram e
SL-A-01 a SL-A-04 compilaram (23, 45, 49 e 33 claims) — o schema v4 do ADENDO 02
resolveu o que devia. A falha veio em SL-A-05: dois candidates de doze **omitiram**
`defects`, que é `required`. Omitir significa "nenhum defeito".

## Por que este adendo é diferente dos dois anteriores

Os adendos 01 e 02 corrigiram um campo cada, cada um descoberto por uma falha. Três
falhas da mesma classe são um padrão, e continuar remendando campo a campo seria, na
prática, calibrar o instrumento contra os resultados — precisamente o que o §38 proíbe.

Então, em vez de corrigir `defects`, **auditei o schema inteiro de uma vez** contra a
classe do defeito e declarei a regra que a governa, com lista fechada.

### Regra declarada

> Um campo obrigatório cujo valor é "o conjunto de X", e para o qual **o conjunto vazio
> é legítimo e não carrega informação**, recebe o valor vazio quando ausente. Ausente e
> vazio são indistinguíveis para esses campos.

### Lista fechada — normalizada

| caminho | valor inserido quando ausente |
|---|---|
| `$.raw_claims` | `[]` — o prompt declara arrays vazios como resposta válida |
| `$.raw_candidates` | `[]` — idem |
| `$.raw_candidates[].claim_temp_refs` | `[]` |
| `$.raw_candidates[].defects` | `[]` |
| `$.raw_candidates[].structure.do_not` | `[]` **somente no ramo `rule`** |
| `$.raw_claims[].qualifiers` | `{}` — todos os sub-campos já são nulos-admissíveis |

A inserção de `do_not` é **discriminada pelo ramo**: aplica-se só quando a estrutura tem
`action` e não tem `steps` nem `why`. No ramo `workflow` o campo não existe no schema; no
ramo `anti_pattern` ele exige `minItems: 1` e continua exigindo — um anti-padrão sem
"não fazer" continua falhando fechado, como deve.

### Lista fechada — deliberadamente NÃO normalizada

| campo | por quê |
|---|---|
| `evidence_refs` (claims e candidates) | provenance. `minItems: 1` intacto. Inegociável. |
| `structure.steps` | workflow sem passo não é workflow |
| `anti_pattern.do_not` | anti-padrão sem "não fazer" não é anti-padrão |
| `text`, `action`, `name`, `entity_kind`, ids temporários, `status`, `source_language` | carregam informação; ausência não é neutra |
| `additionalProperties: false` | contrato estrito preservado em todos os ramos |

Toda inserção é registrada com caminho completo em
`COMPILE-STATE.json → addendum_03_defaulted_empty_sets` e impressa no log.

## Verificação retroativa

O normalizador foi rodado contra **os 12 bundles já produzidos nas três tentativas**
(A e C, todos preservados). Resultado: os 12 validam, com `evidence_refs` intactos em
todos. O volume total de normalização nesses 12 bundles é: **1** remoção de chave-null
(ADENDO 01) e **2** inserções de `defects: []` (ADENDO 03). Nenhuma outra.

## Autoavaliação contra o §38 — post-result tuning

O §38 manda parar se o PASS só for alcançável mudando limiar, pairset, rótulo, output
esperado ou critério de aplicabilidade **depois de ver resultados**. Registro por que
isto não é esse caso:

* nenhum limiar foi movido — o blocker ainda não rodou;
* nenhum pairset existe ainda;
* nenhum rótulo ou output esperado mudou — os controles EC e JE seguem byte-idênticos e
  passaram nas três tentativas;
* nenhum critério de aplicabilidade foi tocado;
* **nenhum resultado semântico foi observado ao decidir**: a decisão saiu de ler o schema
  contra o prompt, não de olhar as claims produzidas;
* a mudança não altera o que conta como resposta **certa** — altera o que o instrumento
  aceita como **forma** de uma resposta que já era certa;
* provenance e completude, os dois contratos que de fato governam a validade, ficaram
  intocados.

O que mudou é ceremônia de serialização. O que não mudou é o que o experimento mede.

## Execução 4

Recompila as três fontes do zero. Nada das tentativas 1, 2 ou 3 é reutilizado.
Controles EC e JE reexecutados.

## Inalterado

Corpus congelado · `SOURCE_CONTENT_HASH` · camada L0 · prompt de extração · prompt e
schema de entailment · `EXTRACTION-SCHEMA-v4.json` · fixtures EC e JE · transporte
Route B · proibição de PAYG.
