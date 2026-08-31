# OPENING RECORD — PILOT-MS-002 — COMPILAÇÃO DOS SOURCE PACKAGES REAIS

Selado e pushed **ANTES** de qualquer chamada semântica. Data: 2026-08-31.

## 1. Escopo

Compilar, **isoladamente**, três Source Packages a partir do corpus real congelado em
`SOURCE-MANIFEST-MS-002.json`. O PILOT-MS-001 permanece intocado: MS-002 é escopo novo.

## 2. Corpus congelado

| source_id | vídeo | autor | idioma | segmentos | chars | SOURCE_CONTENT_HASH |
|---|---|---|---|---|---|---|
| MS002-SRC-A | `yulWjh3rq28` | Nick Saraev | en | 11250 | 415478 | `2880a4c3996f5abc…` |
| MS002-SRC-B | `dtAoZYMEzcM` | Anderson Adelino | pt | 488 | 17846 | `2a6ab098868e0714…` |
| MS002-SRC-C | `NvrBpnbNfv4` | Guilherme Lazarotto | pt | 389 | 14376 | `ed967fae27146d9a…` |

Independência: `DR-MS-002-INDEP-001`, `DECLARED_INDEPENDENT` para os três pares.

## 3. Isolamento de fonte

Cada fonte é compilada sozinha. O extrator de A **nunca** vê B ou C, e assim por diante.
O prompt do extrator declara explicitamente que não existe "a outra fonte". Nenhuma
chamada recebe material de mais de uma fonte.

## 4. Camada L0 — mecânica, zero modelo

Cobertura **integral**, verificada por asserção: 11250/11250, 488/488, 389/389 segmentos.

| fonte | segmentos por unidade | unidades | slices |
|---|---|---|---|
| A | 10 | 1125 | 19 |
| B | 4 | 122 | 3 |
| C | 4 | 98 | 3 |

Evidence existe **antes** de qualquer extração. O extrator recebe um catálogo fechado e
não pode citar id fora dele.

## 5. Pipeline

    RAW SOURCE → ARTIFACTS → SOURCE_ANCHORS → EVIDENCE → SOURCE-LOCAL EXTRACTION
    → RAW OUTPUT PERSISTENCE → CLAIM IDENTITY → INDEPENDENT ENTAILMENT → SEALED CLAIMS
    → CANDIDATE FINALIZATION → CANDIDATE PROVENANCE → LOCAL COHERENCE → COMPLETENESS
    → SOURCE_PACKAGE_HASH → SEAL-RECORD → EXTERNAL REGISTRY

Identidade tipada: `(source_package_hash, entity_kind, local_id)`. Nunca indexar por
`local_id` nu.

## 6. Controles discriminantes — antes de qualquer output real

* **EC1–EC6** (extrator): claim suportada · armadilha não suportada · provenance de
  candidate · link de claim · ausência de candidate para fato não operacional ·
  preservação de qualificador de escopo. Mais `EC0`: nenhum id de Evidence inventado.
* **JE1–JE5** (entailment): ENTAILED · generalização não suportada · objeto diferente ·
  questão declarada em aberto (INDETERMINATE) · mesmo objeto porém silencioso
  (NOT_ENTAILED). JE5 prova mecanicamente que **silêncio ≠ INDETERMINATE**.

Qualquer falha: `MS_002_INSTRUMENT_INVALID`, nenhuma chamada real começa.

## 7. Fail-closed mecânico

`X01_SLICE_MISMATCH` · `X02_INVENTED_EVIDENCE` · `X03_DANGLING_CLAIM_REF` ·
`E01_ENTAIL_SET_MISMATCH` · `E02_EVIDENCE_SET_MISMATCH` · `INVALID_PROVENANCE > 0`
impedem a selagem. Zero reparo manual. Zero correção semântica de output.

## 8. Transporte

    MODEL_TRANSPORT = CLAUDE_CODE_MAX_OAUTH_PRINT_MODE · claude-opus-5 · Claude Code 2.1.251
    processo `claude -p` novo por chamada · --tools "" · sem --continue/--resume
    PAYG PROIBIDA: sem ANTHROPIC_API_KEY, sem ~/.anthropic_key, sem --bare, sem Console API

Guard de ambiente aborta se qualquer variável proibida estiver definida. Limite do plano →
`MS_PROJECT_PAUSED_MAX_PLAN_LIMIT`, nunca fallback para API.

## 9. Claim e Candidate

Toda Claim: `evidence_refs` não vazias e julgada independentemente **antes** de entrar em
`CLAIMS.jsonl`. Só `ENTAILED` sela. Todo Candidate: provenance direta de Evidence,
dependência de Claim quando aplicável, e estado de elegibilidade próprio. Um Candidate
pode permanecer source-local como `NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION` — isso é
resultado válido, não defeito. `INVALID_PROVENANCE` deve ser **zero** para selar.

Tipos first-class preservados: `rule_candidate`, `workflow_candidate`,
`anti_pattern_candidate`. Anti-pattern não é anotação descartável.

## 10. Fora de escopo nesta etapa

Nenhuma comparação cross-source. Nenhuma Fusion. Nenhuma Operationalization. Nenhuma
política MTX. Nenhum Skill Pack.
