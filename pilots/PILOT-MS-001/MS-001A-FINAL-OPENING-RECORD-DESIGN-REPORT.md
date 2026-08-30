# PILOT-MS-001A — FINAL OPENING RECORD DESIGN REPORT

*Rodada de design read-only executada em 2026-08-30 sobre
`HEAD = aab2447e31af363b4065846589ef9d50e437d6db`.
Zero chamadas de modelo, zero escritas no repositório, zero escritas no Drive.*

## 1. Gate

`HEAD` = `origin/main` = `aab2447e31af363b4065846589ef9d50e437d6db` · tree limpo · corpus MS-001 `SHA256SUMS-CORPUS` e `SHA256SUMS-DESIGN` **0 FAILED** · Freeze **17/17** · Identity Errata `2f8232f6…` · Drive 0 escritas · instrumentos temporários **7/7 íntegros** antes da correção. **GATE = PASS.**

## 2. Correções aplicadas

Quatro, e as duas primeiras eram erros meus:

**(a) `evidence_refs = []` estava contraditório.** A v1 dizia *"`evidence_refs = []` → `NOT_ELIGIBLE`"* enquanto o schema já proibia o vazio com `minItems: 1`. Um objeto que o schema rejeita **não pode receber estado de elegibilidade — ele não existe**. Corrigido.

**(b) O plano de chamadas tinha texto ambíguo.** Escrevi *"oitava… décima primeira chamada → `INVALID`"*. Errado: **8, 9 e 10 são planejadas e válidas**; só a **11ª** é `INVALID`. Corrigido explicitamente em `CALL-PLAN-v2.txt`.

**(c) A ordem do pipeline estava errada.** Candidate finalization vinha antes do entailment. Não pode: a elegibilidade cross-source depende de quais Claims foram seladas, e isso só se sabe depois do juiz. Finalizar antes obrigaria a reabrir refs depois — a forma exata de retrofitting que `K12` proíbe.

**(d) `NOT_ELIGIBLE` não tinha caso real.** Sem `CP7`/`CP8`, o estado só existiria no canário artificial.

## 3. Semântica do schema do extractor

```
raw Claim     : evidence_refs.length >= 1   OBRIGATÓRIO
raw Candidate : evidence_refs.length >= 1   OBRIGATÓRIO
violação → E05_EMPTY_EVIDENCE_REFS → EXTRACTION_BUNDLE_INVALID
```

Ocorre na **validação de schema**, antes do Candidate Provenance Gate. O objeto **nunca entra** no conjunto válido de raw Candidates; o bundle inteiro é inválido e a rodada para. **Não é classificado `NOT_ELIGIBLE`.**

## 4. Significado de `NOT_ELIGIBLE`

Candidate **estruturalmente válido e diretamente ancorado** que não satisfaz requisito **adicional** para decisão cross-source. Caso principal no MS-001A:

```
candidate.evidence_refs    → válidas e resolvíveis        OK
candidate.claim_temp_refs  → válidas no raw bundle        OK
MAS ≥1 Claim referenciada NÃO chega a SEALED CLAIMS,
porque o entailment independente devolveu NOT_ENTAILED ou INDETERMINATE
```

O `SOURCE_LOCAL_CANDIDATE` **permanece preservado**; `cross_source_eligibility = NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION`. **Não apagar o candidate. Não transformar a Claim rejeitada em selada. Não criar ref quebrada.**

## 5. Estados da raw Claim

Após entailment: `ENTAILED` · `NOT_ENTAILED` · `INDETERMINATE`. **Somente `ENTAILED` entra no membro `CLAIMS`, com `status: SEALED`.** `NOT_ENTAILED` e `INDETERMINATE` permanecem auditáveis nos outputs e no compile trace, **fora** do conjunto selado. **Nada é apagado.**

## 6. Finalização em duas etapas

**Stage A — Identity Finalization**, antes do entailment, zero modelo: `raw claim → representação canônica normalizada → final claim_id` determinístico (`CL-nnnn`). Dá ao juiz identidade **estável**. **`final claim_id` ≠ `sealed claim`.**

**Stage B — Seal Eligibility**, depois do entailment: `ENTAILED` → membro `CLAIMS`, `SEALED`; os demais → audit-only.

## 7. Isolamento do input do juiz

Por Claim, o juiz recebe: `claim_id` · texto · `qualifiers`/`scope` · **somente as Evidence explicitamente referenciadas por aquela Claim** · os excerpts dessas Evidence · anchor metadata para auditabilidade. **E nada mais** — não recebe outra source, candidates, contexto de Fusion, Evidence não relacionada do catálogo, MTX policy nem taxonomia cross-source.

**Prova de não-vazamento:** persistir a lista exata `claim_id → evidence payload` enviada, por chamada, e verificar mecanicamente que nenhum `EV-` do payload de B pertence ao catálogo de C, e vice-versa.

## 8. Schema de saída do entailment

`ENTAILMENT-SCHEMA-v2.json`: por Claim, `claim_id` · `judgment` · `entail_why` · `evidence_refs_checked`.

Regra mecânica: **`evidence_refs_checked` tem de ser subconjunto exato das refs já declaradas na Claim.** Superset → `E19_JUDGE_ADDED_EVIDENCE`. **O juiz não pode acrescentar Evidence.** Mais `E20` veredito ausente, `E21` claim_id desconhecido, `E22` violação de schema — todos `ENTAILMENT_OUTPUT_INVALID`.

## 9. JE1–JE4

`JE1` suportada → `ENTAILED` · `JE2` claim generaliza além da Evidence → `NOT_ENTAILED` · `JE3` Evidence fora do assunto → `NOT_ENTAILED` · `JE4` Evidence insuficiente/ambígua → `INDETERMINATE`.

`JE2` e `JE3` juntos com `JE4` provam que **`NOT_ENTAILED ≠ INDETERMINATE`** — um juiz que colapse os dois falha. Uma única chamada carrega os quatro fixtures. Falha → `MS_001A_INSTRUMENT_INVALID`.

## 10. Ordem corrigida do pipeline

```
Frozen L0 → Controlled Slice ARTIFACTS → SOURCE_ANCHORS → EVIDENCE
→ Extraction Calls → Raw outputs persisted
→ Claim Identity Finalization → Entailment Judge → SEALED CLAIM Selection
→ Candidate Finalization → Candidate Provenance/Eligibility Gate
→ Local Coherence → Compile Trace final → Required Members → Completeness
→ Member Manifest → SOURCE_PACKAGE_HASH → SEAL-RECORD → External Seal Registry
```

IDs de candidate continuam derivados do próprio `content_hash`, **jamais** do veredito do juiz nem da ordem de emissão.

## 11. Dependência de Claim

**Caso A** — `claim_refs_applicability = NOT_APPLICABLE`: nenhuma dependência exigida; provenance direta de evidence continua obrigatória; evidence válida → pode ser `ELIGIBLE`.

**Caso B** — dependência aplicável: toda `claim_temp_ref` resolve no raw bundle, mapeia para final claim_id, e **todas** as Claims requeridas têm de estar `SEALED`/`ENTAILED`. Qualquer uma `NOT_ENTAILED` ou `INDETERMINATE` → `NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION`.

## 12. Representação do `NOT_ELIGIBLE`

```
claim_refs_applicability      APPLICABLE | NOT_APPLICABLE
sealed_claim_refs[]           SOMENTE refs que existem no membro CLAIMS
claim_dependency_status       SATISFIED | UNSATISFIED_BY_ENTAILMENT | NOT_APPLICABLE
unsealed_claim_dependencies[] audit trail: final_claim_id + judgment
cross_source_eligibility      ELIGIBLE_… | NOT_ELIGIBLE_…
```

**`unsealed_claim_dependencies` não é ref para o membro `CLAIMS`** — aponta para o output/compile trace onde a raw Claim julgada está persistida. **Nenhuma ref quebrada é criada.**

## 13. `INVALID_PROVENANCE`

Reservado a defeito **estrutural real**: evidence id não resolve · evidence não alcança anchor/L0 · `claim_temp_ref` inexistente no raw bundle · typed ref inválida · source/slice incompatível. Vários já são bloqueados pelo schema — aqui são **defense-in-depth**. **`INVALID_PROVENANCE` → Source Package `FAIL`.**

## 14. CP1–CP8

| # | fixture | esperado |
|---|---|---|
| `CP1` | evidence válida, `NOT_APPLICABLE` | `ELIGIBLE` |
| `CP2` | evidence ref inexistente | `INVALID_PROVENANCE` |
| `CP3` | `evidence_refs = []` **injetado direto no gate** | **`NOT_ELIGIBLE`** + `UNREACHABLE_FROM_VALID_MS001A_EXTRACTOR_OUTPUT` |
| `CP4` | `claim_temp_ref` inexistente | `INVALID_PROVENANCE` |
| `CP5` | evidence não alcança anchor/L0 | `INVALID_PROVENANCE` |
| `CP6` | evidence válida + Claim `ENTAILED` | `ELIGIBLE` |
| `CP7` | evidence válida + Claim `NOT_ENTAILED` | **`NOT_ELIGIBLE`**, `UNSATISFIED_BY_ENTAILMENT` |
| `CP8` | evidence válida + Claim `INDETERMINATE` | **`NOT_ELIGIBLE`**, `UNSATISFIED_BY_ENTAILMENT` |

**`CP3`:** `NOT_ELIGIBLE` com marcador obrigatório. O canário existe para provar que o **gate** nunca aceita vacuidade mesmo se o schema falhar; classificá-lo `INVALID_PROVENANCE` confundiria *defeito estrutural do produto* com *defesa em profundidade exercitada*.

## 15. Semântica do membro `CLAIMS`

Nomenclatura **literal**, conferida no `CLAIMS.jsonl` selado do MS-000B: `local_id` · `claim_id` · `text` · `evidence_refs` · **`entailed_by`** · **`entail_why`**. Campos novos do MS-001, **aditivos**: `source_language` · `qualifiers` · `content_hash` · `status: "SEALED"`.

## 16. Ordem de montagem

A de §10, literal.

## 17. Plano de chamadas

```
call 1     EXTRACTOR MODEL CONTROL   EC1-EC6
call 2     ENTAILMENT JUDGE CONTROL  JE1-JE4
call 3-8   seis extrações
call 9     entailment de MS001-SRC-B
call 10    entailment de MS001-SRC-C

PLANNED = 10 | HARD_CAP = 10 | RETRY = 0 | executed_calls <= 10
SOMENTE a call 11 é MS_001A_INVALID
```

**Término antecipado:** se a rodada terminar por `INVALID` ou `FAIL`, as chamadas restantes **não precisam ser queimadas**.

## 18. Caso de borda — zero claims

```
ZERO_RAW_CLAIMS → SOURCE_PACKAGE_FAIL
```

**PARE sem gastar a call 9 ou 10 correspondente.**

## 19. EC ≠ JE

`EC` valida o **gerador**; `JE` valida o **juiz**. O extractor **nunca** auto-certifica `ENTAILED`. O juiz **nunca** cria Claim, **nunca** cria Evidence, **nunca** vê a outra source. `INSTRUMENT_ROLE` diferente, prompt/input independentes. É o que `I29` exige.

## 20. Política de modelo

`requested = claude-opus-5` · `thinking = disabled` · `max_tokens = 8000` · `temperature` omitida/default · SDK `anthropic 0.121.0` · credencial em `~/.anthropic_key`.

**A primeira call real — o EC control — é também a verificação de resolução.** `resolved_model != claude-opus-5` → `MS_001A_INSTRUMENT_INVALID`. **Nenhuma substituição silenciosa.**

## 21. Persistência do bruto

Para cada call de 1 a 10: **raw bytes/JSON antes de qualquer processamento**, mais parsed, validação, hash de entrada e saída. Para o entailment, a lista exata `claim_id → evidence payload enviado`.

## 22. Compile Trace

`RAW_EXTRACTION_PERSISTED` → `CLAIM_IDENTITY_FINALIZED` → `ENTAILMENT_STARTED` → `ENTAILMENT_RESULT_PERSISTED` → `SEALED_CLAIM_SELECTED` → `CANDIDATE_FINALIZED` → `CANDIDATE_ELIGIBILITY_DECIDED`. Timestamp operacional **fora** da representação canônica.

## 23. PASS sobre Claims

Obrigatório: **≥ 1 SEALED Claim em B e ≥ 1 em C**. Medir `raw_claims`, `ENTAILED`, `NOT_ENTAILED`, `INDETERMINATE`. **Nenhum threshold de taxa.**

## 24. PASS sobre Candidates

**Obrigatório: `INVALID_PROVENANCE == 0`.** Medir total, `ELIGIBLE`, `NOT_ELIGIBLE`. **Nenhum eligibility-rate threshold.**

## 25. População futura do blocker

`CROSS_SOURCE_ELIGIBLE_CLAIM_POPULATION` e `CROSS_SOURCE_ELIGIBLE_CANDIDATE_POPULATION`. Blocker **não é executado** e nenhum threshold seu entra no Opening Record (`K13`).

## 26. Hashes dos instrumentos

Registrados no manifesto de `~/ms001a-opening-design/`, todos verificados 17/17.

## 27–29. Zero modelo · zero repo writes · Drive read-only

**Nenhuma chamada de modelo.** `HEAD` inalterado. Drive: **0 escritas**.

## 30. Classificação

# `MS_001A_READY_FOR_OPENING_RECORD`

---

**A correção que mais importa, dita sem rodeio.** As duas inconsistências apontadas eram minhas, e a primeira era estrutural: eu tinha um estado de elegibilidade atribuído a um objeto que o schema já rejeitava. Isso deixava `NOT_ELIGIBLE` sem caso real no pipeline. Com `CP7` e `CP8`, o estado passa a ter origem legítima.

E a reordenação do pipeline não é ajuste de conveniência: finalizar candidate antes do juiz obrigaria a reabrir suas refs depois de saber o resultado, que é exatamente o retrofitting que `K12` existe para pegar.
