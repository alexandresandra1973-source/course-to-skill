# MS-000B ROUND 3 — CANDIDATE ADMISSION AUDIT REPORT

## 1. GATE

`HEAD` = `origin/main` = `abbf8b79fa1ec668f88e8c6ea3287406ce31b15f`. Working tree limpo (0 linhas). Architecture Freeze **17/17, 0 divergências**. `SHA256SUMS` 0 falhas em `PILOT-MS-000B`, `round-2`, `round-3`. Seis Source Packages: `selo=PASS completude=PASS`. Drive: 0 arquivos alterados. **GATE = PASS.**

## 2. A REGRA REAL DE ADMISSION

Localizador: `pilots/PILOT-MS-000B/round-3/consolidate_r3.py:123–136` (sha256 `3068922fb94194a48414420950d7bcc78159cc0c85ae8d1d728fd9188b4260e0`). Executada pelo **consolidador**, não pelo runner. É o único lugar do repositório onde os predicados existem.

```
admit(cand, ev_ids):
  para kind em (rule_candidates, workflow_candidates, anti_pattern_candidates):
    para c em cand[kind]:
      reasons = []
      se kind == workflow_candidates:
          ks = [s.order_key for s in c.steps]
          se steps vazio            → WORKFLOW_SEM_PASSOS
          senão se ks != sorted(ks) ou ks tem repetido → ORDEM_INVALIDA
          senão se len(steps) == 1  → PASSO_UNICO_DEFEITO_HERDADO
      se kind == rule_candidates e c.precedence ∈ {None, "UNDEFINED"}
                                    → PRECEDENCE_UNDEFINED_DEFEITO_HERDADO
      reasons vazio → ADMITIDO ; senão → REJEITADO
```

Duas observações mecânicas: `ev_ids` é recebido e **nunca usado** — a regra não verifica lastro em evidência; e `anti_pattern_candidates` **não tem predicado algum**, é admitido incondicionalmente.

## 3. A REGRA ESTAVA PRÉ-DECLARADA?

**Não.** Ocorrências dos quatro predicados:

| artefato | `PRECEDENCE_UNDEFINED` | `PASSO_UNICO` | `ORDEM_INVALIDA` | `WORKFLOW_SEM_PASSOS` |
|---|---|---|---|---|
| `OPENING-RECORD.md` (R3) | 0 | 0 | 0 | 0 |
| `DECISION-RECORD-MS-000B-R3.md` | 0 | 0 | 0 | 0 |
| `MS-000B-SOURCE-PACKAGE-CONTRACT-RECOVERY.md` | 0 | 0 | 0 | 0 |

O Opening Record §11 declara **quando** a admissão ocorre, **que ela não altera o pacote** (I20) e **quais campos** reporta — `received · admitted · rejected · rejection_reason · inherited_defects · kinds · source_package_ref` — e diz **"Sem threshold"**. Não enumera predicado categórico nenhum.

Cronologia por commit: `cd5cea3` (contrato + DR) → `81d6a37` (Opening Record selado) → **`abbf8b7`, que é o commit que ADICIONOU `consolidate_r3.py`**. A regra passou a existir **depois** do Opening Record selado, no mesmo commit dos resultados.

O que **foi** pré-declarado é o `D3` do Decision Record: defeitos herdados e `workflow estruturalmente inválido` seriam **medidos e reportados** no `LOCAL-COHERENCE-REPORT` — mecânico, não julgado. Isso é reporte, não portão de admissão.

## 4. `PRECEDENCE_UNDEFINED` — STATUS ARQUITETURAL

O Architecture Freeze **não trata `precedence: UNDEFINED` como defeito descartável**. Trata como estado de primeira classe:

- §8.2 (linhas 238–246): `DEFERRED_TO_RUNTIME` está na taxonomia append-only e "preserva o comportamento medido do P003: a Skill parou e **pediu** decisão. É estado de primeira classe, não perda em arbitragem automática."
- §8.1 (linha 234): "**Nenhuma resolução silenciosa.**"
- `I25` (linha 517) e §9 item 5 (linha 293): conflito não resolvido nunca é sintetizado em silêncio; exceção única, `DEFERRED_TO_RUNTIME`, "entra em `open_questions[]` **como pergunta explícita**".
- §6.1 (linha 167): o freeze **cita** `precedence: UNDEFINED` como propriedade medida do corpus P002 (139 sobre 149), não como falha.

Não há em nenhum lugar do freeze uma instrução para rejeitar candidato por `precedence` ausente. A regra da Round 3 faz o oposto do estado congelado: descarta em silêncio o que o freeze manda carregar como pergunta.

**Origem do defeito — verificada, e a atribuição está correta:** `_mirror/pilots/PILOT-002-v2/skill/knowledge/decision-rules.yaml` (sha `4cccee56d82a2663e3b1784a67c155c007f632a1b46c1726fe50aad7321eab20`, intocado desde `378d764`) tem **149 regras, 139 com `precedence: UNDEFINED` = 93,29%** — exatamente o número que o freeze §6.1 declara. No recorte 12+13, 30/32 = 93,75%. O `UNDEFINED` é genuinamente herdado do corpus, não fabricado na Round 3. O modelo emitiu `precedence` real em 2 casos (pkg-B), provando que o campo não está morto por construção.

## 5. `PASSO_UNICO` — STATUS ARQUITETURAL

**Não existe no Architecture Freeze nem na v1.1.** Busca por `passo único / passo unico / um único passo / single step / >= 2 passos / dois passos / min_steps`: **0 ocorrências** em ambos.

Pior: o instrumento **pré-declarado** discorda do não pré-declarado. `LOCAL-COHERENCE-REPORT.json` (RUN-1/pkg-A, sha `44c992c3…`) reporta `"findings": []` — o predicado `WORKFLOW_STRUCTURALLY_INVALID` (`lib/package.py:197–202`) **não considera workflow de um passo inválido**, e seus `inherited_defects` listam apenas `N9` e `P002-HELDOUT`. Nenhum dos dois é precedência ou passo único.

Ou seja: o relatório de coerência pré-declarado diz **zero defeitos**; a regra não pré-declarada diz **34 de 49 candidatos são defeituosos**. Os dois instrumentos usam o mesmo nome — "defeito herdado" — para coisas diferentes.

No corpus P002, 15 de 43 workflows (34,88%) têm um passo.

## 6. TABELA RUN × SOURCE × KIND

Recomputada por mim a partir dos pacotes selados, não lida do relatório:

| run | src | recebidos | rule adm/rej | workflow adm/rej | anti-pattern adm/rej | admitidos | rejeitados |
|---|---|---|---|---|---|---|---|
| RUN-1 | A | 23 | **0/13** | 4/2 | 4/0 | 8 | 15 |
| RUN-1 | B | 26 | 2/17 | 2/2 | 3/0 | 7 | 19 |
| RUN-2 | A | 23 | **0/13** | 4/2 | 4/0 | 8 | 15 |
| RUN-2 | B | 26 | 2/17 | 2/2 | 3/0 | 7 | 19 |
| RUN-3 | A | 23 | **0/13** | 4/2 | 4/0 | 8 | 15 |
| RUN-3 | B | 26 | 2/17 | 2/2 | 3/0 | 7 | 19 |

Idêntico nos três runs — os candidatos são derivados deterministicamente do YAML do P002, sem chamada de modelo. **A fonte A admitiu ZERO regras nos três runs.**

## 7. O QUE A FUSION DECLAROU CONSUMIR

`fusion-package-RUN-1.json` (sha `ad7383a75c684c8305f9933015b7f21637a1ea7722998855bbcb521e9a3618b3`) carrega `candidate_admission_report` com os números acima, e `workflow_transport` com `A: 6 workflows / 19 steps`, `B: 4 / 23`, `preservado: true`.

## 8. O QUE A FUSION DE FATO CONSUMIU

Três achados mecânicos, todos verificados no artefato:

**(a) O contraditório do §7 se resolve contra o relatório.** `consolidate_r3.py:172–177` monta `workflow_transport` assim:

```python
wp[k]={"struct_source":P.sha_text(P.canon(src)),"struct_fusion":P.sha_text(P.canon(src)), ...}
wp[k]["preservado"]= wp[k]["struct_source"]==wp[k]["struct_fusion"]
```

Os dois hashes vêm do **mesmo objeto `src`**. `preservado: true` é **tautológico** — não pode ser falso. E `workflows: 6 / steps: 19` conta **todos** os `workflow_candidates` da fonte, **incluindo os 2 rejeitados**. Não é medida de transporte; é a contagem do pacote de origem espelhada duas vezes.

**(b) A Fusion não consumiu candidato nenhum — nem admitido.** `claims_qualified` (`consolidate_r3.py:183`) é construído de `runs[r]["sealed"][k]`, o conjunto de **claims** selados: 38 (A) + 43 (B) = 81 pares `(source_package_hash, CL-xxxx)`. Varredura de `local_id` de candidato dentro do JSON da Fusion:

- `local_id` **admitidos** presentes no Fusion Package: **0** (`WF-0035, WF-0037, WF-0038, WF-0039` — nenhum aparece)
- `local_id` **rejeitados** presentes: **10** (`R-0095…R-0104`), e só porque `inherited_defects[:10]` os lista como defeito.

Os únicos ids de candidato que atravessaram para a Fusion são **rejeitados**, transportados como defeito. Blocagem, relações `IDENTICAL` e isolamento operam sobre claims, não sobre candidatos.

**(c) Nenhum portão depende do resultado da admissão.** `consolidate_r3.py:152–153`: `candidate_admission_ok = all(package_unchanged and received > 0)`. Admitidos e rejeitados **não entram em portão algum**. `PILOT_MS_000B_PASS` sairia idêntico com 49 admitidos ou 49 rejeitados.

## 9. ADMISSION FOI PORTÃO OU RELATÓRIO?

**Relatório.** Não filtrou nada, não bloqueou nada, não alimentou portão. A única consequência material é a do item 11.

## 10. IMPACTO QUANTITATIVO

| recorte | recebidos | admitidos | rejeitados | % rejeitada |
|---|---|---|---|---|
| pkg-A (por run) | 23 | 8 | 15 | **65,22%** |
| pkg-B (por run) | 26 | 7 | 19 | **73,08%** |
| agregado (por run) | 49 | 15 | 34 | **69,39%** |
| **só `rule_candidates`** | 32 | **2** | 30 | **93,75%** |

Motivos: `PRECEDENCE_UNDEFINED_DEFEITO_HERDADO` 13 (A) + 17 (B) = 30; `PASSO_UNICO_DEFEITO_HERDADO` 2 + 2 = 4. `ORDEM_INVALIDA` e `WORKFLOW_SEM_PASSOS`: 0 disparos — dois dos quatro predicados nunca foram exercitados.

Se a regra tivesse valido como filtro real, a Round 3 teria descartado **93,75% das regras** de um corpus cujo defeito o freeze manda **preservar como pergunta**.

## 11. BASELINE vs POLÍTICA vs `v1 §7.4`

Três divergências:

**(i) `v1 §7.4` não existe.** O Opening Record §11 justifica "Sem threshold" citando "v1 §7.4". Na v1.1 (Drive, read-only) a §7 tem apenas §7.1, §7.2 e §7.3. Não há §7.4 na v1.1 nem na v1.2. O locator está errado; o conteúdo equivalente é o freeze §21 (linhas 574–575): "thresholds ainda não medidos — incluindo … **os limiares do portão de admissão de candidatos**".

**(ii) "Sem threshold" é verdade literal e falsa material.** Nenhum limiar **numérico** foi usado. Mas quatro predicados **categóricos** decidiram admissão, e um predicado categórico é uma política de admissão tanto quanto um número. `I18` (linha 510): "Nenhum limiar entra em uso sem ter sido **pré-declarado** antes da rodada que o consome". Sob a leitura literal (limiar = número) `I18` não foi violada; sob a leitura funcional (limiar = critério que decide entrada) ela foi. O Opening Record fechou a porta dos números e deixou a categórica aberta sem declarar.

**(iii) `I26` — a única consequência material, e ela é real.** `fusion_id` inclui `ca[r]`, o relatório de admissão (`consolidate_r3.py:199`). Verificado por recomputação: `fusion_id` RUN-1 = `a2d311414029c28f90aadef25421c7e6402af8e1fd3fcce048745eb8ac6f9527`, reproduz o artefato. Sob a política contrafactual "admitir tudo", mantendo hashes de pacote, claims e blocagem constantes: `f8b9b6dd81a40002e942c4b8e899728339eb2fb1623847af1ac0712f5cda01b1` — **mudou**.

`I26` exige que a mesma fusão sob duas políticas produza saída **byte-idêntica**. A regra de admissão é, funcionalmente, política MTX; ela **entrou na identidade da Fusion** enquanto **não entrou no conteúdo** dela. É a combinação errada nas duas pontas.

## 12. CLASSIFICAÇÃO DA DIVERGÊNCIA

Não é uma coisa só. Separando por natureza:

| # | divergência | natureza | evidência |
|---|---|---|---|
| D-1 | regra de admissão não pré-declarada, criada no commit dos resultados | **falha de método** | §3 |
| D-2 | `PASSO_UNICO` inexistente no freeze e contraditório com o `LOCAL-COHERENCE-REPORT` pré-declarado | **critério inventado** | §5 |
| D-3 | rejeitar por `precedence: UNDEFINED` contradiz `DEFERRED_TO_RUNTIME` / `I25` / "nenhuma resolução silenciosa" | **contradição com o freeze** | §4 |
| D-4 | `struct_source == struct_fusion` do mesmo objeto: `preservado` não pode ser falso | **instrumento cego** | §8(a) |
| D-5 | Fusion não consome candidato admitido algum; só ids rejeitados atravessam | **portão desconectado** | §8(b) |
| D-6 | política de admissão entra em `fusion_id` sem entrar no conteúdo | **contradição com `I26`** | §11(iii) |
| D-7 | `v1 §7.4` citado e inexistente | **locator errado** | §11(i) |
| D-8 | `ev_ids` recebido e não usado; `anti_pattern` sem predicado; 2 dos 4 predicados nunca disparam | **cobertura nula** | §2, §10 |

Nenhuma delas é defeito de produto do Source Package Contract. **Todas são de instrumento e de método.** Por isso não convertem o `STRUCTURAL_PASS` provisório em `FAIL` — a taxonomia da própria Round 3 diz que instrumento quebrado não reprova produto, `INVALID` precede `FAIL`.

Mas D-1 + D-6 juntas atingem o que a Round 3 **entregou como resultado**: a Fusion consumiu apenas pacotes completos e selados, o que está demonstrado e permanece de pé; a camada de admissão, porém, nunca foi testada — foi executada, relatada e ignorada, e ainda assim carimbou a identidade da Fusion.

## 13. É NECESSÁRIO RERODAR?

**Não para reprovar o que foi aceito.** Os sete pontos que o bloco já dá como demonstrados — Source Package Contract, Seal Contract, Package Identity, Provenance, Compile Trace, transporte DESIGN C, Fusion consumindo só pacote completo e selado — não dependem de `admit()` em nenhum ponto verificado. `candidate_admission_ok` não olha admitidos nem rejeitados; a classificação `PILOT_MS_000B_PASS` é invariante sob qualquer política de admissão.

**Sim, e apenas isto, para o que ficou por medir:** a camada `SOURCE_LOCAL_CANDIDATE → FUSION` **não foi medida na Round 3**. Zero candidatos admitidos alcançaram a Fusion; `preservado` não podia ser falso; dois predicados nunca dispararam. Uma rodada futura que queira medir isso precisa, antes de qualquer execução avaliativa, (a) pré-declarar os predicados no Opening Record, (b) declarar o status arquitetural de `precedence: UNDEFINED` — descarte ou `open_questions[]` — porque o freeze hoje diz `open_questions[]`, (c) medir transporte com origem e destino **distintos**, e (d) decidir se política de admissão pode tocar `fusion_id` sob `I26`.

Isso é escopo de rodada nova. Não é correção desta.

## 14. NÃO CORRIGIDO

Nenhum arquivo alterado. Nenhum Opening Record, Candidate Admission Report, Fusion Package ou FINAL REPORT tocado. Nenhuma errata, nenhum Decision Record, nenhum commit, nenhum rerun, nenhuma chamada de modelo. `git status --porcelain` permanece com 0 linhas; `HEAD` permanece `abbf8b79`.

## 15. ARTEFATOS LIDOS — hashes recomputados agora

| artefato | sha256 |
|---|---|
| `round-3/consolidate_r3.py` | `3068922fb94194a48414420950d7bcc78159cc0c85ae8d1d728fd9188b4260e0` |
| `round-3/OPENING-RECORD.md` | `9aa050b2e01121441fbbea3da4ed6e7d3f8b389b423ca9695f3e10b217a1b302` |
| `round-3/out/ROUND-3-VERDICT.md` | `6260059727f29a9fe2f7afdc2df8ff60f95752d242cd955c0422448c86a8bb5c` |
| `round-3/out/summary.json` | `7e6ca6b13d63905337cdaf45efe3af8c997101ca9124b13014bdca9f3475f089` |
| `round-3/out/fusion-package-RUN-1.json` | `ad7383a75c684c8305f9933015b7f21637a1ea7722998855bbcb521e9a3618b3` |
| `DECISION-RECORD-MS-000B-R3.md` | `29dfb0dfeff6723d6d782a714ed9318f77374d8427b48b75e06b46f94d264c48` |
| `RUN-1/pkg-A/LOCAL-COHERENCE-REPORT.json` | `44c992c372aa6a261e476636c542f2ca9f6160f2c538be45121938509604d280` |
| `_mirror/…/PILOT-002-v2/skill/knowledge/decision-rules.yaml` | `4cccee56d82a2663e3b1784a67c155c007f632a1b46c1726fe50aad7321eab20` |
| `_mirror/…/PILOT-002-v2/skill/knowledge/workflows.yaml` | `d7df9646fa4e5524b050cb5394c3728ff41951736c99c0a13341c08f25c52899` |

## 16. O QUE PERMANECE DEMONSTRADO

Os sete itens que o bloco lista como aceitos permanecem aceitos. Nada nesta auditoria os toca: nenhum deles passa por `admit()`, e a igualdade `before == after` do hash de pacote (`package_unchanged: true` nos seis pacotes) confirma `I20` — a admissão não escreveu no selado.

## 17. O QUE NÃO FOI DEMONSTRADO E ERA CRIDO DEMONSTRADO

Três coisas:
1. que a admissão de candidatos foi um **portão** — foi relatório;
2. que o **workflow foi preservado** na travessia — a medida é tautológica;
3. que a Fusion **consumiu candidatos** — consumiu claims; candidato admitido nenhum chegou lá.

## 18. NÚMERO QUE NÃO PODE SER REUTILIZADO COMO BASELINE

`15/49 = 30,61%` de admissão e `34/49 = 69,39%` de rejeição **não são baseline de qualidade de candidato**. São a projeção de dois predicados não pré-declarados sobre um corpus cujo `precedence: UNDEFINED` (139/149 = 93,29% no P002) é propriedade conhecida e preservada. O mesmo se aplica a `2/32 = 6,25%` de regras admitidas. Registrar como medida de corpus, nunca como limiar, nunca como baseline de portão — pelo mesmo motivo pelo qual `139/226` foi invalidado: numerador e denominador não compartilham referente com a coisa que o número aparenta medir.

## 19. CLASSIFICAÇÃO FINAL DESTA RODADA DE REVISÃO

# `MS_000B_REVIEW_EVIDENCE_COMPLETE`

Todas as treze seções executadas com evidência mecânica; nenhuma pergunta ficou sem resposta por falta de acesso; nenhuma correção aplicada.

---

**Uma nota de honestidade sobre autoria.** As oito divergências acima são minhas — `consolidate_r3.py`, o `admit()`, o `struct_fusion` tautológico e o `ca[r]` dentro do `fusion_id` foram todos escritos por mim na Round 3, depois de o Opening Record já estar selado. O `STRUCTURAL_PASS` provisório sobrevive porque o produto que ele nomeia não depende dessa camada — mas o `PILOT_MS_000B_PASS` que o `summary.json` registra afirma um portão de admissão que, medido, não é portão.
