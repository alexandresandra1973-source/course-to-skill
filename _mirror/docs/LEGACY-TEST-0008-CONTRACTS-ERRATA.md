# LEGACY TEST-0008 CONTRACTS — ERRATA

**Gerado:** `2026-08-12T00:41:39+00:00` · gerador `legacy_test0008_errata.py` · **somente medição**, READ-ONLY.

Relatório gerado por script; nenhum hash foi digitado.


> ## ⛔ ERRATA — leia antes de usar qualquer um destes contratos
>
> Os **13** contratos listados aqui declaram `TEST-0008` como chave de `comparative_tests`. Eles codificam o desenho de **DUAS** condições — Skill contra resumo.
>
> **O desenho vigente é de TRÊS condições** — `FULL_SKILL`, `SUMMARY_AS_SUMMARY`, `SUMMARY_AS_SKILL` — **com DUAS comparações**:
>
> - `P = FULL_SKILL − SUMMARY_AS_SUMMARY` (primária)
> - `F = SUMMARY_AS_SKILL − SUMMARY_AS_SUMMARY` (enquadramento)
>
> O nome `SKILL_MINUS_SUMMARY` **não desambigua entre `P` e `F`**: sob o desenho novo, os dois cabem no nome. **Quem rodar a cadeia com um destes contratos mede uma comparação e não sabe qual das duas mediu.**
>
> Estes arquivos estão dentro de zips na árvore READ-ONLY e **não podem ser marcados no próprio arquivo**. Esta errata é externa e se amarra a eles por SHA-256.


## 1. Algum destes está na cadeia de algo ATIVO?

A varredura procurou o NOME de cada contrato em toda a árvore — solto e dentro de zip — e achou **27 referência(s)**, assim distribuídas:

| classe | n | contratos citados |
|---|---|---|
| análise (este projeto) | 21 | JUDGE-SCORING-CONTRACT-v0.1.3-REV2.yaml, JUDGE-SCORING-CONTRACT-v0.1.3-REV3.yaml, JUDGE-SCORING-CONTRACT-v0.1.3-REV4.yaml, JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml, JUDGE-SCORING-CONTRACT-v0.1.3.yaml, contract-canary.yaml, contract-undefined-aggregation.yaml |
| pacote v0.1.3 | 5 | JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml |
| árvore v0.1.4 | 1 | JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml |


**análise (este projeto)**

| contrato | referenciado em | caminho interno |
|---|---|---|
| `JUDGE-SCORING-CONTRACT-v0.1.3.yaml` | `Course-to-Skill-Claude/docs/DRY-RUN-TEST-0008.md` | — |
| `contract-canary.yaml` | `Course-to-Skill-Claude/docs/DRY-RUN-TEST-0008.md` | — |
| `contract-undefined-aggregation.yaml` | `Course-to-Skill-Claude/docs/DRY-RUN-TEST-0008.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV2.yaml` | `Course-to-Skill-Claude/docs/LEGACY-TEST-0008-CONTRACTS-ERRATA.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV3.yaml` | `Course-to-Skill-Claude/docs/LEGACY-TEST-0008-CONTRACTS-ERRATA.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV4.yaml` | `Course-to-Skill-Claude/docs/LEGACY-TEST-0008-CONTRACTS-ERRATA.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `Course-to-Skill-Claude/docs/LEGACY-TEST-0008-CONTRACTS-ERRATA.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3.yaml` | `Course-to-Skill-Claude/docs/LEGACY-TEST-0008-CONTRACTS-ERRATA.md` | — |
| `contract-canary.yaml` | `Course-to-Skill-Claude/docs/LEGACY-TEST-0008-CONTRACTS-ERRATA.md` | — |
| `contract-undefined-aggregation.yaml` | `Course-to-Skill-Claude/docs/LEGACY-TEST-0008-CONTRACTS-ERRATA.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV2.yaml` | `Course-to-Skill-Claude/docs/TEST-0008-METRICS-DISCREPANCY.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV3.yaml` | `Course-to-Skill-Claude/docs/TEST-0008-METRICS-DISCREPANCY.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV4.yaml` | `Course-to-Skill-Claude/docs/TEST-0008-METRICS-DISCREPANCY.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `Course-to-Skill-Claude/docs/TEST-0008-METRICS-DISCREPANCY.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3.yaml` | `Course-to-Skill-Claude/docs/TEST-0008-METRICS-DISCREPANCY.md` | — |
| `contract-canary.yaml` | `Course-to-Skill-Claude/docs/TEST-0008-METRICS-DISCREPANCY.md` | — |
| `contract-undefined-aggregation.yaml` | `Course-to-Skill-Claude/docs/TEST-0008-METRICS-DISCREPANCY.md` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV2.yaml` | `Course-to-Skill-Claude/docs/VERSION-LITERAL-SWEEP-FULL.yaml` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV3.yaml` | `Course-to-Skill-Claude/docs/VERSION-LITERAL-SWEEP-FULL.yaml` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV4.yaml` | `Course-to-Skill-Claude/docs/VERSION-LITERAL-SWEEP-FULL.yaml` | — |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `Course-to-Skill-Claude/docs/VERSION-LITERAL-SWEEP-FULL.yaml` | — |


**pacote v0.1.3**

| contrato | referenciado em | caminho interno |
|---|---|---|
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PRELOCK_D1_D2/PILOT-001-v0.1.3-PRELOCK-PATCH-D1-D2.zip` | `PILOT-001-v0.1.3-PRELOCK-PATCH-D1-D2/score_judge_results.py` |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PRELOCK_D1_D2/PILOT-001-v0.1.3-PRELOCK-PATCH-D1-D2.zip` | `PILOT-001-v0.1.3-PRELOCK-PATCH-D1-D2/JUDGE-SCORING-CONTRACT-ADDENDUM-D1-D2-v0.1.3.yaml` |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007/FINAL_PRE_RUN_LOCK/PILOT-001-v0.1.3-PRELOCK-PATCH-F4-STRUCTURAL-ID.zip` | `PILOT-001-v0.1.3-PRELOCK-PATCH-F4-STRUCTURAL-ID/score_judge_results.py` |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007/PRELOCK_F3_TRISTATE/PILOT-001-v0.1.3-PRELOCK-PATCH-F3-TRISTATE.zip` | `PILOT-001-v0.1.3-PRELOCK-PATCH-F3-TRISTATE/score_judge_results.py` |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007/PRELOCK_F4_STRUCTURAL_ID/PILOT-001-v0.1.3-PRELOCK-PATCH-F4-STRUCTURAL-ID (1).zip` | `PILOT-001-v0.1.3-PRELOCK-PATCH-F4-STRUCTURAL-ID/score_judge_results.py` |


**árvore v0.1.4**

| contrato | referenciado em | caminho interno |
|---|---|---|
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007/PRELOCK_F5_VERSION_PARAMETERIZATION/VERSION-LITERAL-SWEEP-v0.1.4.yaml` | — |


### 1.1 A checagem decisiva: o contrato que a cadeia ATIVA consome

Referência por nome não basta — o que importa é se a cadeia em uso carrega um contrato que traga `TEST-0008` como chave. O sucessor do contrato de julgamento na v0.1.4 é este:

| pacote | contrato | chaves de comparative_tests | contém TEST-0008? |
|---|---|---|---|
| `Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007/FINAL_PRE_RUN_LOCK_F7/PILOT-001-v0.1.4-FINAL-PRE-RUN-LOCK-F7.zip` | `JUDGE-SCORING-CONTRACT-TEST-0007-v0.1.4-F7.yaml` | `TEST-0007` | **não** |
| `Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007/FINAL_PRE_RUN_LOCK_F7_SCORER_BOUND/PILOT-001-v0.1.4-FINAL-PRE-RUN-LOCK-F7-SCORER-BOUND.zip` | `JUDGE-SCORING-CONTRACT-TEST-0007-v0.1.4-F7.yaml` | `TEST-0007` | **não** |
| `Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007/JUDGE_BLIND_RUN/PILOT-001-v0.1.4-TEST-0007-JUDGE-BLIND-RUN.zip` | `JUDGE-SCORING-CONTRACT-TEST-0007-v0.1.4-F7.yaml` | `TEST-0007` | **não** |
| `Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007/PRELOCK_F7_EXACT_MARGIN_BOUNDARIES/PILOT-001-v0.1.4-PRELOCK-PATCH-F7-EXACT-MARGIN-BOUNDARIES.zip` | `JUDGE-SCORING-CONTRACT-TEST-0007-v0.1.4-F7.yaml` | `TEST-0007` | **não** |

**SHA-256 do contrato ativo:** `fa5d203b700d56d232eb436689077731c921cbdabb0ae4af5a57d9e7e01c3977` (idêntico nos 4 pacotes acima).


### Veredito

**NÃO há achado grave.** Nenhum dos 13 está na cadeia de execução de artefato ativo, e a prova é positiva, não apenas ausência de evidência:


1. **O sucessor ativo dropou a entrada.** `JUDGE-SCORING-CONTRACT-TEST-0007-v0.1.4-F7.yaml` declara `comparative_tests` com **apenas `TEST-0007`**. A entrada `TEST-0008` que os contratos v0.1.3 carregavam **já foi removida** na geração corrente, inclusive no pacote `JUDGE_BLIND_RUN` e no `FINAL_PRE_RUN_LOCK_F7_SCORER_BOUND`.

2. **Todos os 13 vivem em pacotes da v0.1.3** — `00_REVISION_INPUT/` e os prelocks do TEST-0007 — e nenhum existe como arquivo solto.

3. **O pacote de blind run ativo não contém contrato nenhum**: só instruções, âncoras, anexos e `SHA256SUMS.txt`.


### 1.2 A ressalva que sobra, e ela é real

Duas referências merecem registro porque são caminhos vivos até um dos contratos desta errata:

| artefato | como referencia | natureza |
|---|---|---|
| `JUDGE-SCORING-CONTRACT-ADDENDUM-D1-D2-v0.1.3.yaml` | declara `base_contract: JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | dependência declarada — o addendum se apoia num dos 13 |
| `score_judge_results.py` | linha de uso `--contract JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | invocação documentada do scorer, copiável |

> Os dois vivem dentro dos pacotes de prelock da v0.1.3 (`PRELOCK_D1_D2`, `PRELOCK_F3_TRISTATE`, `PRELOCK_F4_STRUCTURAL_ID`). O `VERSION-LITERAL-SWEEP-v0.1.4.yaml`, já na árvore v0.1.4, cataloga a linha do scorer e a classifica como `DOCUMENTATION_OR_EXAMPLE` com `blocking_class_candidate: false` — ou seja, o próprio projeto já a examinou e a considerou não bloqueante.


> **Por que isso não vira grave:** o scorer da v0.1.3 e seus addenda não são a cadeia em uso; a v0.1.4 tem contrato próprio, sem `TEST-0008`. **Por que ainda assim importa:** a linha `--contract …REV5.yaml` é copiável, e quem a copiar puxa um contrato que traz a entrada aposentada. É ponteiro quente, não incêndio.


## 2. Correção de premissa: não são 13 declarando o desenho velho

A varredura por identidade encontra **13** contratos com `TEST-0008` como chave. Mas eles não são homogêneos:

| classe | n | o que significa |
|---|---|---|
| declaram `comparison: SKILL_MINUS_SUMMARY` | 5 | **codificam o desenho de duas condições** |
| declaram `TEST-0008` sem `comparison` nenhum | 8 | fixtures de canário: só um flag de guarda |

**Só 5 dos 13 declaram `SKILL_MINUS_SUMMARY`.** Os outros 8 são contratos de canário que trazem `TEST-0008` como chave com apenas `full_preservation_guard_required` (e, em quatro deles, `structural_ceiling_required`). Eles **não declaram comparação nenhuma**, logo não codificam o desenho de duas condições — o problema deles é outro e menor: mencionam um teste que a cadeia não implementa.


> Registro a diferença porque ela muda o que precisa ser aposentado. A errata forte vale para os 5; os 8 restantes entram como contexto.


## 3. Os 13 contratos

### 3.1 Os que declaram o desenho aposentado

| # | zip | caminho interno | comparison | margin_threshold |
|---|---|---|---|---|
| 1 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV2.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV2/JUDGE-SCORING-CONTRACT-v0.1.3-REV2.yaml` | `SKILL_MINUS_SUMMARY` | `FROM_ABLATION_MARGIN_LOCK` |
| 2 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV3.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV3/JUDGE-SCORING-CONTRACT-v0.1.3-REV3.yaml` | `SKILL_MINUS_SUMMARY` | `FROM_ABLATION_MARGIN_LOCK` |
| 3 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV4.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV4/JUDGE-SCORING-CONTRACT-v0.1.3-REV4.yaml` | `SKILL_MINUS_SUMMARY` | `FROM_ABLATION_MARGIN_LOCK` |
| 4 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV5.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV5/JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `SKILL_MINUS_SUMMARY` | `FROM_ABLATION_MARGIN_LOCK` |
| 5 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK.zip` | `PILOT-001-v0.1.3-REVISION-PACK/JUDGE-SCORING-CONTRACT-v0.1.3.yaml` | `SKILL_MINUS_SUMMARY` | `PRELOCKED_IN_TEST_SUITE_OR_COMPARISON_LOCK` |

| arquivo | SHA-256 do YAML interno | bytes |
|---|---|---|
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV2.yaml` | `5539db445bb8cea412c9be4e7cafd8d8a4b02597e2f5e166c2ea95f2f6979ab5` | 4333 |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV3.yaml` | `84c676677b91fc207877971562ab6763be6c1cd6d0536d7ca28f2d10725d3ca9` | 5893 |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV4.yaml` | `4363ff5480367edecef4131a078145af04d3f054d6d7dc2ecda549f572dfdb29` | 7947 |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | `2ebfe5c89b5c6aad935d2831bd6f16156e0f1c85353908c93563c2f0db9a1157` | 8687 |
| `JUDGE-SCORING-CONTRACT-v0.1.3.yaml` | `012cea748141478f7969bc107a479540e1b73c19218492783535bbf96ca385e6` | 2846 |

| arquivo | artifact_id | chaves sob TEST-0008 | outros testes |
|---|---|---|---|
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV2.yaml` | **não declara** | `comparison`, `full_preservation_guard_required`, `margin_threshold` | TEST-0007 |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV3.yaml` | **não declara** | `comparison`, `full_preservation_guard_required`, `margin_threshold`, `structural_ceiling_required` | TEST-0007 |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV4.yaml` | **não declara** | `comparison`, `full_preservation_guard_required`, `margin_threshold`, `structural_ceiling_required` | TEST-0007 |
| `JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml` | **não declara** | `comparison`, `full_preservation_guard_required`, `margin_threshold`, `structural_ceiling_required` | TEST-0007 |
| `JUDGE-SCORING-CONTRACT-v0.1.3.yaml` | **não declara** | `comparison`, `margin_threshold` | TEST-0007 |

### 3.2 Os que declaram `TEST-0008` sem comparação

| # | zip | caminho interno | chaves sob TEST-0008 | SHA-256 |
|---|---|---|---|---|
| 1 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV2.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV2/canary/contract-undefined-aggregation.yaml` | `full_preservation_guard_required` | `2be74ea049822b84…` |
| 2 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV2.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV2/canary/contract-canary.yaml` | `full_preservation_guard_required` | `0933f27ce7e9fae0…` |
| 3 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV3.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV3/canary/contract-undefined-aggregation.yaml` | `full_preservation_guard_required`, `structural_ceiling_required` | `4f69f70c7532cf8f…` |
| 4 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV3.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV3/canary/contract-canary.yaml` | `full_preservation_guard_required`, `structural_ceiling_required` | `af80d1ea660f52f5…` |
| 5 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV4.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV4/canary/contract-undefined-aggregation.yaml` | `full_preservation_guard_required`, `structural_ceiling_required` | `ad8e771c1741ae24…` |
| 6 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV4.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV4/canary/contract-canary.yaml` | `full_preservation_guard_required`, `structural_ceiling_required` | `638bc4285a10455e…` |
| 7 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV5.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV5/canary/contract-undefined-aggregation.yaml` | `full_preservation_guard_required`, `structural_ceiling_required` | `1abcc8986a480cb8…` |
| 8 | `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV5.zip` | `PILOT-001-v0.1.3-REVISION-PACK-REV5/canary/contract-canary.yaml` | `full_preservation_guard_required`, `structural_ceiling_required` | `a2a16dcad6ec38dc…` |

| caminho interno | SHA-256 completo |
|---|---|
| `PILOT-001-v0.1.3-REVISION-PACK-REV2/canary/contract-undefined-aggregation.yaml` | `2be74ea049822b8497e101433bfb1b1f27da2f92babc605f0688756eca3eee49` |
| `PILOT-001-v0.1.3-REVISION-PACK-REV2/canary/contract-canary.yaml` | `0933f27ce7e9fae0b0361a81d4f07603b6d490717bbb26b707e1375c8371ec22` |
| `PILOT-001-v0.1.3-REVISION-PACK-REV3/canary/contract-undefined-aggregation.yaml` | `4f69f70c7532cf8f9f3f8083804012dbc961838baf0fb2a2f9ef17e79d039786` |
| `PILOT-001-v0.1.3-REVISION-PACK-REV3/canary/contract-canary.yaml` | `af80d1ea660f52f5f8d485ea559602722096db0b3f7eb76e50e8feba64b2bb28` |
| `PILOT-001-v0.1.3-REVISION-PACK-REV4/canary/contract-undefined-aggregation.yaml` | `ad8e771c1741ae24c7f538dd872491cf228b9399d25b3b38dea0da0926d0eddf` |
| `PILOT-001-v0.1.3-REVISION-PACK-REV4/canary/contract-canary.yaml` | `638bc4285a10455ec58eef4f684d8f5af69c5bd617106e1ae2ec05cdcc743fef` |
| `PILOT-001-v0.1.3-REVISION-PACK-REV5/canary/contract-undefined-aggregation.yaml` | `1abcc8986a480cb88abaae4586188a1285491be0e0f94127ffb476b2779f55db` |
| `PILOT-001-v0.1.3-REVISION-PACK-REV5/canary/contract-canary.yaml` | `a2a16dcad6ec38dc49320fd273f93a34343ad060b1b394b6b1a1d52aae4c1635` |

### 3.3 SHA-256 dos zips que os contêm

Os contratos não podem ser marcados; os pacotes que os carregam ficam amarrados aqui, para que a errata continue válida mesmo que alguém reempacote.

| zip | SHA-256 do zip |
|---|---|
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV2.zip` | `e2cd2174b12ec97998971102e333e9ca8577500bef1e30aa14c91d6fc64b0a23` |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV3.zip` | `c5536d9717bd92b9e1e6e5edb1501e3a8b4011b71d555f996735f87e72d05271` |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV4.zip` | `92598cc49cecc11dd21f7bd54666360c9316f9125186ea4e5c29ba93731d6ca2` |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK-REV5.zip` | `9dc6643bc28a7f97cea051bb1c49bd559d763104adf8875f9cbaa4a8d655762c` |
| `Course-to-Skill/PILOT-001/v0.1.3/00_REVISION_INPUT/PILOT-001-v0.1.3-REVISION-PACK.zip` | `4a6c88915b714bd2512444094d30ab25422c76d5098f5b355a16afc2d9effa72` |

## 4. Amarração ao desenho que os substitui

| artefato do desenho vigente | caminho | SHA-256 |
|---|---|---|
| desenho de três condições, montado | `Course-to-Skill-Claude/docs/TEST-0008-CONDITIONS-v0.1.4` | `c029eacb659b4bd2be077ec17464b9442f3b3b50a4e80ac70d9a98c59eb78baf` |
| procedência do baseline, com os SHA-256 das três condições | `Course-to-Skill-Claude/docs/BASELINE-PROVENANCE-v0.1.4.yaml` | `4cf74c31e53d7d875d897214d682335e5472664eb08a9d6bff4125036736437e` |
| ensaio seco que define P e F e lista o que falta | `Course-to-Skill-Claude/docs/DRY-RUN-TEST-0008.md` | `6d75f9bc6b69358cc59efc19446d47aa4720af67e192a38f8aa0cfa66bf41d97` |
| apuração da discrepância 5×6 das métricas | `Course-to-Skill-Claude/docs/TEST-0008-METRICS-DISCREPANCY.md` | `f7780d6891f398d12a5fa68918afd80f14219896f55708910fd79a9fd1197e05` |
| rascunho de rubrica do TEST-0008 (NÃO congelado) | `Course-to-Skill-Claude/docs/TEST-0008-RUBRIC-DRAFT-v0.1.4.yaml` | `a6c27d8268db06eed72afa84fa39f33c51c9ada31ffb12164d4326f5fa76e00b` |

> Diretórios são amarrados pelo hash da lista ordenada de `(caminho, sha256)` dos seus membros, não pelo conteúdo concatenado.


### 4.1 As duas âncoras pedidas que NÃO existem

A tarefa pediu amarração ao **ADR do TEST-0008** e ao **metric lock `caffc7ba…`**. Procurei os dois e nenhum existe. Registro em vez de fabricar a amarração:

| âncora pedida | como foi procurada | resultado |
|---|---|---|
| ADR do TEST-0008 / ADR de paridade de informação | arquivo em docs/adr/ que trate do TEST-0008 ou das três condições | **NÃO ENCONTRADO** |
| metric lock `caffc7ba…` | arquivo cujo SHA-256 comece com caffc7ba, ou documento que cite a string | **NÃO ENCONTRADO** |

- **ADR do TEST-0008:** `docs/adr/` tem 14 ADRs (ADR-0001 a ADR-0014) e **nenhum** menciona `TEST-0008`, `SUMMARY_AS_SKILL` ou paridade de informação. O "ADR de paridade de informação" é citado em prosa no `DRY-RUN-TEST-0008.md` e no `BASELINE-PROVENANCE-v0.1.4.yaml` — **mas não existe como arquivo, e nunca recebeu número**. O desenho de três condições vive hoje só na prosa desses dois documentos e na pasta de condições montadas.

- **Metric lock `caffc7ba…`:** varri a árvore inteira por literal (inclusive dentro de zips) e por SHA-256 de arquivo. **Zero acertos.** Nenhum arquivo tem esse hash e nenhum documento cita essa string.


> **Consequência para esta errata.** Ela se amarra ao que existe (§4) e declara ausente o que não existe. Um leitor que precise da autoridade formal do desenho de três condições **não vai encontrá-la**: o desenho vigente não tem ADR numerado nem lock de métrica. Isso é, por si, um achado — a errata aposenta um desenho velho apontando para um desenho novo que ainda não foi formalizado.


## 5. O que fazer com um destes contratos

| uso | veredito |
|---|---|
| rodar a cadeia do TEST-0008 com ele | **NÃO** — mede `P` ou `F` sem dizer qual |
| usá-lo como referência histórica do desenho de duas condições | sim, é para isso que esta errata o preserva |
| copiar a linha `--contract …REV5.yaml` de exemplo | **NÃO** — herda o desenho aposentado |
| editar o contrato para o desenho novo | impossível sem escrever na árvore READ-ONLY; e o modelo de dados não comporta duas comparações por teste |

> O `DRY-RUN-TEST-0008.md` já registrou que a mudança necessária não é preencher campo: `comparative_tests` é um mapa `test_id → política` com um único par `left`/`right`, e o TEST-0008 precisa de duas comparações sobre três condições. **Estender o modelo de dados é pré-requisito**, e nenhum contrato desta lista pode ser consertado no lugar.


---

**Escopo:** somente medição. Nenhum contrato foi editado, movido, copiado ou reempacotado. Nenhum arquivo de `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi tocado. O único arquivo escrito é este relatório, em `Course-to-Skill-Claude/docs/`.
