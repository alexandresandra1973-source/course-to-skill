# OPENING RECORD — ADENDO PARA A **EXECUÇÃO 2** DA ROUND 4

**Selado e pushed ANTES da re-execução.** Data: 2026-08-30.

**Opening Record base, que permanece integralmente normativo e NÃO é alterado:**
`OPENING-RECORD.md` sha256 `fff9e05aac9fe89b135b23d57560ad87780e3231f25c53b98f1d5557516b3726`,
selado em `3b44084d1c66070efe26b92ca6280b54f1407df4`.

**Execução 1:** `PILOT_MS_000B_ROUND_4_INVALID`, registrada em
`ROUND-4-EXEC-1-INVALID.md` (`c98082b5d7739475d8042f2b602fd45f645909d76f50044fbd3ab175056a8b01`), com as saídas preservadas em
`out-invalid-exec-1/`. Nada dela é apagado.

---

## 1. O FATO NOVO, DESCOBERTO NA EXECUÇÃO 1

> Nos seis Source Packages da Round 3, **`local_id` não é único dentro do pacote**:
> `anti_pattern_candidates` reusam o `local_id` da rule de origem. Em `RUN-1/pkg-A`,
> `R-0095`, `R-0098`, `R-0101` e `R-0102` nomeiam simultaneamente uma rule e um
> anti-pattern.

Consequência arquitetural, registrada e **não corrigida** nesta rodada:
**`(source_package_hash, local_id)` — a qualificação que o Architecture Freeze manda usar na
travessia de fronteira — é ambígua nestes pacotes.** Defeito herdado do empacotador da
Round 3, da mesma família de `evidence_refs: []`.

## 2. O QUE MUDA — E É SÓ ISSO

**Dois verificadores** de `run_round4.py` passam a indexar por
`(source_package_hash, kind, local_id)` em vez de `local_id` sozinho:

1. o detector de vazamento (`rejected_nao_consumidos`);
2. a busca do registro de admissão nos canários reais (`real_passo_unico`,
   `real_precedence_undefined`).

`run_round4.py` novo sha256: `e6e2cc9eb2fb554c676814ca2ed878fab36e4dccda631e5cef8ea35ed6afb629`.

## 3. O QUE **NÃO** MUDA — BYTE-IDÊNTICO

| artefato | sha256 | estado |
|---|---|---|
| `CANDIDATE-ADMISSION-POLICY-v0.1.json` | `64c2feaeebf1ac62c559031f1918741a35856fb1115b5b10e7707a1e922a75c9` | **inalterado** |
| `FUSION-CONFIG-R4.json` | `cc34c4834a54291c2db822463bacf1f40c3ed3bf0179a34e83b542a115fcfe79` | **inalterado** |
| `lib/admission.py` | `88d74f22251b8cb996ea458a7c451ae1b9db48162d9739094f9ce1c7ab4b0e27` | **inalterado** |
| `lib/fusion.py` | `5c03d3f694548ae9843240b979cfeadec91d90417dfc1bd323a183b23efe24b1` | **inalterado** |
| `canaries_r4.py` | `24ce2311a22c1ff8484a508e501ff2b2a054343261539474ae2d2f72afdd1f5a` | **inalterado** |
| `i26_canary.py` | `889369305b2bf3dca29cb2a5fea547aca96d0f87bc71a285e3072d5c2f65406f` | **inalterado** |

**Nenhum predicado, nenhum critério, nenhum limiar, nenhuma estrutura declarada muda.**
`admitted_candidate_refs` e `rejected_candidate_refs_NOT_CONSUMABLE` continuam qualificados
como o item 9 do Opening Record declarou: `(source_package_hash, local_id)`. O `kind` usado
na **verificação** é lido do relatório de admissão já persistido no próprio arquivo.

## 4. `LOCAL_ID_INVALIDO` NÃO É AFROUXADO

O predicado foi pré-declarado como *"`local_id` válido (não vazio, string, **único no
pacote**)"* e disparou sobre uma colisão real, rejeitando **21 anti-patterns**.

> **A policy não é alterada por causa desse número.** Mudá-la depois de ver o resultado
> seria repetir exatamente o achado `D-1` da Round 3 — a regra nascendo depois da medição.

O resultado esperado da execução 2 **inclui** essas 21 rejeições. Elas são
`REJECTED_STRUCTURAL` legítimas, e a população de anti-patterns admitidos no corpus real
será **zero**. Isso é medida, não falha do instrumento.

## 5. LIMITAÇÃO ADICIONAL DECLARADA AGORA

`ANTI_PATTERN_ADMISSION_NOT_EXERCISABLE_ON_R3_CORPUS` — nenhum anti-pattern do corpus real
pode ser admitido, porque todos colidem em `local_id`. `CA6` (anti-pattern válido →
`ADMITTED`) e `CA7` (evidence quebrada → `REJECTED_STRUCTURAL`) continuam provando o
comportamento **sinteticamente**; o corpus real **não exercita** a admissão de anti-pattern.
Segue a mesma disciplina de `EVIDENCE_LASTRO_NON_EMPTINESS_NOT_TESTABLE_ON_R3_CORPUS`.

## 6. CRITÉRIOS INALTERADOS

`PASS` / `FAIL` / `INVALID` continuam exatamente como o item 14 do Opening Record base
declarou, `INVALID` precedendo `FAIL`. Nenhuma contagem esperada de admitidos ou rejeitados
é declarada — quantidade não é threshold. **Zero chamadas de modelo.**
