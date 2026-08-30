# DECISION RECORD — escopo da `ROUND 3` do `PILOT-MS-000B`

**`decision_id`:** `DR-MS-000B-R3-001` · **Data:** 2026-08-30 · **Ator:** Alexandre Sandra
**Base:** `MS-000B-SOURCE-PACKAGE-CONTRACT-RECOVERY.md`
(`abf859543db17fd7d9b82c40a056342db85923f8e94aaeb44365d03452c99faa`)
**Classe:** `GIT_NATIVE_BY_DESIGN`

> **O objetivo da Round 3 não é repetir um PASS.** É testar pela primeira vez o
> `SOURCE PACKAGE` que o Architecture Freeze realmente congelou.

---

## D1 — Corpus
`PILOT-002` capítulos **12** e **13**, mesmos `FULL`/`CUT`/`SLICE` já medidos.
`SOURCE = chapter` continua **`PILOT_MS_000B_ONLY`** e **não vira contrato de produção**.

## D2 — Independência
Ambos **`KNOWN_DEPENDENT`**.

## D3 — `LOCAL-COHERENCE-REPORT`: **MECÂNICO**, não julgado
Mede integridade referencial · `local_id` duplicados · anchors/evidence quebrados · claims
sem evidência · candidates com refs quebradas · workflow estruturalmente inválido ·
defeitos herdados · membros obrigatórios.

> **`SEMANTIC_COHERENCE_NOT_EVALUATED_IN_MS_000B`** — registrado dentro do próprio relatório.
> **Isto não é "semantic coherence PASS".**

## D4 — `DECLARATION-SPACE-INDEX`: **bounded por pacote**
Enumera só o próprio pacote · linhagem `FULL → CUT → SLICE` · Architecture Freeze e Decision
Records diretamente referenciados · commits citados por esses artefatos.
**Nenhum pacote vira auditoria de todo o Git/Drive.**
`filesystem scan ≠ corpus audit` permanece verdadeiro **globalmente**.

## D5 — `ARTIFACTS`
`ARTIFACT-INDEX` explícito · chapter slice como artefato membro · derivados source-local
necessários. `CUT`/`FULL` resolvidos **por proveniência e hash**, sem duplicar bytes grandes.
**Nenhum pacote depende de caminho mutável.**

## D6 — Modelo e partição
`claude-opus-5` · `THINKING = {"type":"disabled"}` · mesma partição experimental.
Versões de prompt sobem para `ms000b-r3-*` — mudança **estritamente necessária** ao novo
Package Contract e **pré-declarada** no Opening Record.

## D7 — Orçamento
**Plano = 10. Hard cap = 10. Margem zero.**
Confrontado **antes** do Opening Record: 1 judge-controls + 6 geração + 3 entailment = **10**.
**Nenhuma chamada extra depois do Opening Record.**
**Transiente que exija retry ⇒ `PILOT_MS_000B_ROUND_3_INVALID`.** Não se excede o cap.

## D8 — Timestamp não é identidade
O `COMPILE-TRACE` **membro** carrega só campos identity-relevant.
Timestamps vão para o **`OPERATIONAL-RUN-LOG`, fora de todo pacote**.
**Dois pacotes byte-equivalentes não podem ter hashes diferentes por terem rodado em
segundos distintos.**
