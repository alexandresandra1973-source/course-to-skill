# DECISION RECORD — auditoria da CANDIDATE ADMISSION da `ROUND 3` do `PILOT-MS-000B`

**`decision_id`:** `DR-MS-000B-R3-CANDIDATE-AUDIT-001` · **Data:** 2026-08-30
**Ator:** Alexandre Sandra · **Classe:** `GIT_NATIVE_BY_DESIGN`
**Natureza:** **ADITIVO**. Não altera, não corrige e não supersede artefato algum da Round 3.

**Base — auditoria read-only, hashes recomputados no ato deste registro:**

| artefato | sha256 | bytes |
|---|---|---|
| `MS-000B-ROUND-3-CANDIDATE-ADMISSION-AUDIT-REPORT.md` | `61e34ba0b8f43a14ed3e68dbbd94fd990eed156058536b5737ed615c18ef6f95` | 17073 |
| `round-3/consolidate_r3.py` | `3068922fb94194a48414420950d7bcc78159cc0c85ae8d1d728fd9188b4260e0` | — |
| `round-3/OPENING-RECORD.md` | `9aa050b2e01121441fbbea3da4ed6e7d3f8b389b423ca9695f3e10b217a1b302` | — |
| `round-3/out/ROUND-3-VERDICT.md` | `6260059727f29a9fe2f7afdc2df8ff60f95752d242cd955c0422448c86a8bb5c` | — |
| `round-3/out/summary.json` | `7e6ca6b13d63905337cdaf45efe3af8c997101ca9124b13014bdca9f3475f089` | — |
| `DECISION-RECORD-MS-000B-R3.md` | `29dfb0dfeff6723d6d782a714ed9318f77374d8427b48b75e06b46f94d264c48` | — |

> A auditoria que fundamenta este registro encerrou em `MS_000B_REVIEW_EVIDENCE_COMPLETE`
> e **não aplicou correção alguma**. Este Decision Record registra o que ela mediu, sem
> reinterpretar nenhum achado em direção mais favorável.

---

## D1 — A Round 3 PERMANECE ACEITA para

Nenhum destes sete pontos passa por `admit()` em ponto verificado algum. A auditoria não os
toca, e a igualdade `before == after` do hash de pacote (`package_unchanged: true` nos seis
pacotes) confirma `I20`.

1. **Source Package Contract** — 11 membros obrigatórios + `TOOLCHAIN`, completude `PASS`
   nos seis pacotes;
2. **Seal Contract** — as sete condições de `SEALED`, verificadas pelo
   `seal_verifier.py` do `PILOT-MS-000A` reutilizado sem alteração; `selo=PASS` nos seis;
3. **Package Identity** — `SOURCE_ID` / `SOURCE_CONTENT_HASH` / `SOURCE_PACKAGE_HASH`
   distintos e estáveis;
4. **Provenance** — `PROVENANCE-LEDGER`, qualificação `(source_package_hash, local_id)`
   só na travessia de fronteira, `ref_scope: SELF` interno;
5. **Compile Trace** — membro sem timestamp; timestamp operacional fora do conjunto
   canônico, no `OPERATIONAL-RUN-LOG`;
6. **Source Packages completos e selados** — completude `PASS` **e** selo `PASS`, com o
   portão de completude separado do verificador de selo;
7. **Fusion consumindo apenas Source Packages válidos** —
   `fusion_consumes_valid_only: true`, seals `PASS` verificados antes do consumo.

## D2 — A Round 3 **NÃO QUALIFICA** como prova de

1. **Candidate Admission** — foi executada e relatada, **não funcionou como portão**;
2. **Candidate → Fusion consumption** — **zero** candidatos admitidos alcançaram o
   Fusion Package;
3. **workflow transport source → fusion** — a medida de preservação era **tautológica**.

## D3 — Motivos: os oito achados, registrados sem reinterpretação

| # | divergência | natureza | evidência no audit |
|---|---|---|---|
| **D-1** | regra de admissão não pré-declarada, criada no commit dos resultados | falha de método | §3 |
| **D-2** | `PASSO_UNICO` inexistente no freeze e contraditório com o `LOCAL-COHERENCE-REPORT` pré-declarado | critério inventado | §5 |
| **D-3** | rejeitar por `precedence: UNDEFINED` contradiz `DEFERRED_TO_RUNTIME` / `I25` / "nenhuma resolução silenciosa" | contradição com o freeze | §4 |
| **D-4** | `struct_source == struct_fusion` do mesmo objeto: `preservado` não pode ser falso | instrumento cego | §8(a) |
| **D-5** | Fusion não consome candidato admitido algum; só ids rejeitados atravessam | portão desconectado | §8(b) |
| **D-6** | política de admissão entra em `fusion_id` sem entrar no conteúdo | contradição com `I26` | §11(iii) |
| **D-7** | `v1 §7.4` citado e inexistente | locator errado | §11(i) |
| **D-8** | `ev_ids` recebido e não usado; `anti_pattern` sem predicado; 2 dos 4 predicados nunca disparam | cobertura nula | §2, §10 |

### D3.1 — os pontos que este registro fixa nominalmente

- **A admission rule surgiu DEPOIS do Opening Record.** Cronologia por commit:
  `cd5cea3` (contrato + DR) → `81d6a37` (Opening Record **selado**) → `abbf8b7`, que é o
  commit que **adicionou** `consolidate_r3.py`. Os quatro predicados têm **0 ocorrências**
  no Opening Record R3, no `DECISION-RECORD-MS-000B-R3.md` e no
  `MS-000B-SOURCE-PACKAGE-CONTRACT-RECOVERY.md`.
- **`PRECEDENCE_UNDEFINED` NÃO é rejeição automática.** O Architecture Freeze o trata como
  estado de primeira classe: `DEFERRED_TO_RUNTIME` "preserva o comportamento medido do
  P003: a Skill parou e **pediu** decisão"; `I25` e §9(5) mandam entrar em
  `open_questions[]` **como pergunta explícita**; §8.1 proíbe resolução silenciosa. O freeze
  §6.1 **cita** `precedence: UNDEFINED` como propriedade medida do corpus P002
  (139 de 149 = 93,29%), não como falha. A origem herdada está verificada e correta —
  o defeito é do corpus; a **rejeição** é que não é normativa.
- **`PASSO_UNICO` NÃO é rejeição normativa.** 0 ocorrências no Architecture Freeze e na
  v1.1 para `passo único / passo unico / um único passo / single step / >= 2 passos /
  dois passos / min_steps`. O instrumento **pré-declarado** (`LOCAL-COHERENCE-REPORT`,
  `D3` do DR-MS-000B-R3-001) reporta `"findings": []` e **não** considera workflow de um
  passo estruturalmente inválido. Os dois instrumentos usam o nome "defeito herdado" para
  coisas diferentes; só um deles foi pré-declarado.
- **A workflow preservation medida era tautológica.** `struct_source` e `struct_fusion`
  são calculados do **mesmo objeto `src`**; `preservado` não pode ser falso. As contagens
  `A: 6 workflows / 19 steps` e `B: 4 / 23` são do pacote de origem e **incluem os
  rejeitados**.
- **A Fusion não consumiu candidates admitidos.** `claims_qualified` vem dos **claims**
  selados (38 A + 43 B = 81 pares qualificados). Varredura de `local_id` de candidato no
  Fusion Package: **0** admitidos presentes; **10** rejeitados presentes, e apenas porque
  `inherited_defects[:10]` os lista como defeito.
- **A admission não funcionou como portão.**
  `candidate_admission_ok = all(package_unchanged and received > 0)`. Admitidos e
  rejeitados **não entram em portão algum**; `PILOT_MS_000B_PASS` sairia idêntico com 49
  admitidos ou 49 rejeitados.
- **O locator `v1 §7.4` estava errado.** A §7 da v1.1 tem apenas §7.1, §7.2 e §7.3; não há
  §7.4 na v1.1 nem na v1.2. O conteúdo equivalente é o freeze §21: "thresholds ainda não
  medidos — incluindo … os limiares do portão de admissão de candidatos".
- **`evidence_refs` não eram realmente verificadas pela função de admission.** `admit()`
  recebe `ev_ids` e **nunca o usa**; `anti_pattern_candidates` não tem predicado algum e é
  admitido incondicionalmente; `ORDEM_INVALIDA` e `WORKFLOW_SEM_PASSOS` tiveram
  **0 disparos**.

### D3.2 — natureza dos oito

Nenhum é defeito de produto do Source Package Contract. **Todos são de instrumento e de
método.** Por isso não convertem o `STRUCTURAL_PASS` em `FAIL`: instrumento quebrado não
reprova produto, e `INVALID` precede `FAIL`. Isto é registro, não atenuação — `D-1` e
`D-6` juntas atingem o que a Round 3 entregou como resultado, e é exatamente por isso que
`D2` acima retira três itens do conjunto do que foi provado.

## D4 — CLASSIFICAÇÃO FORMAL

```
MS_000B_ROUND_3_STRUCTURAL_PASS
CANDIDATE_TO_FUSION_LAYER = NON_QUALIFYING_IN_ROUND_3
```

**`PILOT_MS_000B_ACCEPTED` NÃO é declarado nesta data.** A aceitação final do piloto
permanece **aberta** e depende da rodada descrita em `D6`.

> Observação de custódia: `round-3/out/summary.json` registra
> `classificacao: PILOT_MS_000B_PASS`. Esse artefato **não é alterado** — é histórico e
> permanece byte-idêntico. Este Decision Record é a declaração aditiva de que aquele
> `PASS` cobre os sete itens de `D1` e **não** cobre os três de `D2`.

## D5 — NÚMEROS PROIBIDOS COMO BASELINE

Ficam registrados como `NOT_VALID_AS_CANDIDATE_ADMISSION_QUALITY_BASELINE`:

| número | o que aparenta medir | o que de fato é |
|---|---|---|
| `15/49 = 30,61%` | taxa de admissão de candidatos | projeção de dois predicados **não pré-declarados** sobre o corpus P002 |
| `34/49 = 69,39%` | taxa de rejeição de candidatos | idem |
| `2/32 = 6,25%` | qualidade das `rule_candidates` | idem, sobre um corpus cujo `precedence: UNDEFINED` (139/149 = 93,29%) é propriedade **conhecida e deliberadamente preservada** |

**Permanecem permitidos** apenas como observação histórica da execução daquela heurística.

**É PROIBIDO** que qualquer um dos três vire:
- **threshold** de portão;
- **medida de qualidade do corpus**;
- **política futura**;
- **baseline do portão de admissão**.

Mesmo motivo pelo qual `139/226 = 61,50%` foi invalidado no freeze §6.1: numerador e
denominador não compartilham referente com a coisa que o número aparenta medir.

## D6 — RERUN NECESSÁRIO: escopo

```
TARGETED_POST_PACKAGE_RERUN_REQUIRED
```

E **não** `FULL_MS_000B_RERUN_REQUIRED`.

**Mede exclusivamente:**

```
SOURCE_LOCAL_CANDIDATE  →  CANDIDATE ADMISSION  →  FUSION
```

**Insumo:** os **seis Source Packages selados da Round 3**, reutilizados **como estão**,
sem reabrir, sem reselar, sem regravar. `I20` continua valendo: a rodada não escreve em
camada selada.

**Zero nova geração de Claims é necessária.** Os claims da Round 3 já estão selados dentro
dos pacotes e não são objeto desta medição.

**Precondições que a rodada tem de satisfazer ANTES de qualquer execução avaliativa**
(derivadas dos oito achados, não inventadas aqui):

1. **pré-declarar os predicados de admissão** no Opening Record, nominalmente, por hash
   selado — fecha `D-1` e `D-8`;
2. **declarar o status arquitetural de `precedence: UNDEFINED`** — descarte **ou**
   `open_questions[]`. O freeze hoje diz `open_questions[]` — fecha `D-3`;
3. **decidir o status de `PASSO_UNICO`** — hoje não é normativo em lugar nenhum —
   fecha `D-2`;
4. **medir transporte com origem e destino distintos**, de modo que `preservado` **possa**
   ser falso — fecha `D-4`;
5. **fazer a admissão alimentar consumo real da Fusion**, ou declarar explicitamente que
   não alimenta — fecha `D-5`;
6. **decidir se política de admissão pode tocar `fusion_id`** sob `I26`
   (mesma fusão sob duas políticas → saída byte-idêntica) — fecha `D-6`;
7. **corrigir o locator** do fundamento de "sem threshold" para o freeze §21 —
   fecha `D-7`.

**Nenhum limiar numérico entra nessa rodada sem pré-declaração** (`I18`), e nenhum dos três
números de `D5` pode ser usado para calibrá-la.

## D7 — NÃO REESCREVER HISTÓRICO

Não foram alterados, e permanecem byte-idênticos: `round-3/OPENING-RECORD.md` ·
`round-3/consolidate_r3.py` · `round-3/out/fusion-package-RUN-{1,2,3}.json` ·
`round-3/out/ROUND-3-VERDICT.md` · `round-3/out/summary.json` · `round-3/out/runs.json` ·
os seis Source Packages e seus `SEAL-RECORD.yaml` · `EXTERNAL-SEAL-REGISTRY.txt` ·
todos os artefatos das Rounds 1 e 2 · o Architecture Freeze e seu `FREEZE-RECORD` ·
`_mirror/` · `cts/` · N1–N9.

Este registro é **inteiramente aditivo**.
