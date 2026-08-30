# MS-000B — SOURCE PACKAGE CONTRACT RECOVERY REPORT

**Rodada:** `PACKAGE CONTRACT RECOVERY DESIGN + MECHANICAL CANARIES` — **desenho apenas**.
**Data:** 2026-08-30 · `HEAD` = `origin/main` = `d56491fee49869481434a0e8b0eb9275131f9080`
**Zero chamadas de modelo · zero alteração no repo · relatório temporário em `~/ms000b-recovery/`.**

---

## 1. GATE — **PASS**

| verificação | resultado |
|---|---|
| `HEAD == origin/main` | `d56491fe…` · working tree limpa |
| Architecture Freeze | **17/17 membros, 0 divergências** |
| MS-000B Round 1 | 18 arquivos, **0 falhas** |
| MS-000B Round 2 | 18 arquivos, **0 falhas** |
| MS-000A Round 3 | **0 falhas** |

---

## 2. CLASSIFICAÇÃO FORMAL DA ROUND 2 — registro aditivo a criar

**`MS-000B ROUND-2 = NON_QUALIFYING_FOR_FINAL_ACCEPTANCE`** · `MS_000B_REVIEW_FAILED` ·
`MS_001 = NOT_AUTHORIZED`

Cinco motivos:

1. **Claims não eram membros do Source Package** — provado por recomputação: o hash cobre
   `{profile, anchors, items}` e nada mais.
2. **Source-local candidates não eram membros** — mesma prova.
3. **Não existia `SEAL-RECORD` de Source Package** — `find -iname '*SEAL-RECORD*'` = 0.
4. **Candidate admission não foi implementado nem medido** — zero ocorrências de
   `admission|admitted|rejected_candidate` em todo o código.
5. **Hashes incorretos citados no relatório da Round 1** — ver §13.

**Os relatórios históricos não são reescritos.** Tokenizer controls (9/9), judge controls
(5/5), consolidator controls (7/7), isolation controls e demais resultados mecânicos da
Round 2 permanecem citáveis **apenas** como **`ROUND_2_OBSERVATION`**.

---

## 3. SEPARAÇÃO FORMAL DAS TRÊS IDENTIDADES

A frase *"Source Package não deve mudar de identidade quando o prompt muda"* era ampla
demais e fica **descartada**. No lugar, três identidades distintas:

| identidade | o que endereça | muda quando | estável entre runs? |
|---|---|---|---|
| **`SOURCE_ID`** | identidade **lógica** da fonte/capítulo experimental | a fonte lógica muda | **sim, sempre** |
| **`SOURCE_CONTENT_HASH`** | os **bytes** da fonte/slice | os bytes mudam | **sim**, se os bytes não mudam |
| **`SOURCE_PACKAGE_HASH`** | o **conjunto selado** produzido por **UMA** compilação | qualquer membro muda — inclusive claims, candidates ou compile-trace | **não** — e não deve ser |

**Recompilação diferente produz `SOURCE_PACKAGE_HASH` novo. Isso é esperado e correto**,
porque `CLAIMS`, `SOURCE_LOCAL_CANDIDATES` e `COMPILE-TRACE` são membros do pacote.

> O defeito real da Round 2 **não** era o hash mudar com o prompt. Era o hash **não cobrir
> claims, candidates e trace** — e, ao mesmo tempo, **carregar `model_policy` dentro do
> `SOURCE-PROFILE`**, misturando fato de fonte com configuração de compilação. Corrigir a
> segunda metade sem a primeira teria produzido um pacote ainda mais errado: identidade
> estável sobre um conjunto incompleto.

---

## 4. `SOURCE-PROFILE` CORRIGIDO — só fatos da fonte

**CONTÉM:** `source_id` · `source_content_hash` · `lang` · `text_source_lang` · autor ·
mídia/plataforma · `chapter/source boundary` (origem da fronteira, linhas, tempos) ·
`provenance_chain` `FULL → CUT → SLICE` · `source_independence` (`KNOWN_DEPENDENT`) com
evidência · `authority` **declarada externamente** (`D37`) · escopo experimental.

**NÃO CONTÉM:** `model` · `prompt_version` · `judge_version` · `thinking` · `max_tokens` ·
`partition` · qualquer output de modelo.

**Consequência mensurável, e é o teste `PC4`:** o `SOURCE-PROFILE` de um mesmo source passa
a ser **byte-idêntico entre runs** quando os fatos da fonte não mudam. Na Round 2 ele não
era: mudou de `31df720f…` para `115ae350…` **apenas** porque `ms000b-claimgen-v1` virou
`ms000b-r2-claimgen-v1`, com `CHAPTER_SLICE`, `items` e `anchors` byte-idênticos.

## 5. `COMPILE-TRACE` CORRIGIDO — recebe tudo que saiu do profile

Passa a carregar, além do que a Round 2 já registrava: `model` requisitado e **resolvido** ·
`thinking` · `max_tokens` · `prompt_version` · `judge_version` · **partição de chamadas**
(`I19`) · `input_sha256` · `output_sha256` · `stop_reason` · tokens · checkpoints ·
timestamp **operacional apenas, nunca identidade**.

`D11` congela `COMPILE-TRACE` como membro **obrigatório**. Ele é membro do pacote — logo
entra no `SOURCE_PACKAGE_HASH`, e é por isso que uma recompilação muda o hash.

---

## 6. LIFECYCLE COMPLETO DA ROUND 3

**Por `RUN × SOURCE`, nesta ordem — o selo é o ÚLTIMO passo:**

```
source bytes (slice, derivado do CUT selado)
  → SOURCE_ANCHORS / EVIDENCE
    → claim generation
      → ENTAILED_BY
        → SEALED CLAIMS
          → SOURCE_LOCAL_CANDIDATES
            → COMPILE-TRACE final
              → LOCAL-COHERENCE-REPORT
                → DECLARATION-SPACE-INDEX
                  → PACKAGE ASSEMBLY
                    → VALIDATE
                      → SEAL
                        → SOURCE PACKAGE
```

**Só depois, por RUN:**

```
SOURCE PACKAGE A  +  SOURCE PACKAGE B
  → candidate admission
    → blocking
      → relation detection
        → fusion
          → FUSION PACKAGE
```

**Round 3 terá conceitualmente até `3 runs × 2 sources = 6 Source Packages`.**

> **Regra, não expectativa digitada:** conjuntos de membros diferentes **devem** produzir
> package hashes diferentes; conjuntos byte-equivalentes **podem** produzir o mesmo
> content-address. Como as claims variaram entre runs na Round 2, **seis hashes distintos é
> a consequência provável** — mas é consequência dos membros, **não condição de PASS**.
> Se dois runs produzirem claims byte-idênticas e o hash coincidir, isso é correto.

---

## 7. MEMBER SET — literal, da v1 §4.1, sem invenção nem remoção

| # | membro | papel |
|---|---|---|
| 1 | `SOURCE-PROFILE` | fatos da fonte (§4) |
| 2 | `L0` / `CHAPTER-SLICE` + provenance | fonte imutável endereçada por conteúdo |
| 3 | `ARTIFACTS` | derivados do L0 (mapa temporal do trecho) |
| 4 | `SOURCE_ANCHORS` | locators de primeira classe |
| 5 | `EVIDENCE` | asserções com âncora |
| 6 | **`CLAIMS`** seladas | unidades normalizadas de comparação |
| 7 | **`SOURCE_LOCAL_CANDIDATES`** | `rule` · `workflow` · `anti_pattern` |
| 8 | **`COMPILE-TRACE`** | chamadas, modelo resolvido, **partição** |
| 9 | **`LOCAL-COHERENCE-REPORT`** | contradições **internas** à fonte, antes da fusão |
| 10 | **`DECLARATION-SPACE-INDEX`** | onde vivem as declarações sobre este pacote |
| 11 | **`SEAL-RECORD`** | o selo, pelas sete condições |

Os cinco em negrito **não existiam** na Round 2.

### 7.1 · A circularidade que precisa ser resolvida — achado desta rodada

`I4` congela: *"Todo identificador citado em **qualquer produto** é qualificado
`(source_package_hash, local_id)`"*. Mas se `CLAIMS` são **membros** do pacote e cada claim
carrega o `source_package_hash`, **o hash depende de si mesmo**.

A Round 2 já colocava `qualified_refs` com o package hash **dentro** de cada claim — o que
não quebrou nada só porque as claims **não eram** membros.

**Resolução, fiel ao texto congelado:** `E6` fala em *"identidade **global**"* e `I4` em
*"citado em qualquer **produto**"*. A qualificação é exigida **onde há travessia de
pacote** — no `FUSION PACKAGE` e a jusante. **Dentro** do Source Package, `local_id` nu é
correto: o contexto é o próprio pacote. As claims membros citam `evidence_refs` por
`local_id`; o **Fusion Package** as cita qualificadas.

Isso resolve a circularidade **sem** afrouxar `I4`, e precisa estar escrito no Opening
Record da Round 3.

---

## 8. ALGORITMO PROPOSTO DE `SOURCE_PACKAGE_HASH`

**O algoritmo atual `{profile, anchors, items}` é descartado.**

**O Source Package passa a ser um DIRETÓRIO**, não um blob JSON — porque é assim que o
`seal_verifier.py` do MS-000A, já `READY_FOR_EXPERIMENTAL_USE`, opera
(`verify(seal_dir, external_registry, toolchain_dir)`). **Não se cria uma segunda definição
de selo.**

```
round-3/run-1/pkg-A/
    SOURCE-PROFILE.json
    CHAPTER-SLICE.txt
    ARTIFACTS/temporal-map.json
    SOURCE-ANCHORS.jsonl
    EVIDENCE.jsonl
    CLAIMS.jsonl
    SOURCE-LOCAL-CANDIDATES.json
    COMPILE-TRACE.jsonl
    LOCAL-COHERENCE-REPORT.json
    DECLARATION-SPACE-INDEX.json
    TOOLCHAIN.txt
    SEAL-RECORD.yaml          ← NÃO se lista em members[]
round-3/EXTERNAL-SEAL-REGISTRY.txt   ← fora de TODOS os diretórios selados
```

**Definição:**

1. **`member_manifest`** = lista de `(caminho_relativo, sha256)` de **todos** os membros
   **exceto o `SEAL-RECORD`**, ordenada por `caminho_relativo` sob `LC_ALL=C`.
2. **Representação canônica** = `json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False)`,
   UTF-8 — a mesma já usada e validada.
3. **`member_manifest_hash`** = `sha256(canon(member_manifest))`.
4. **`SOURCE_PACKAGE_HASH` := `member_manifest_hash`.** É o content-address do conjunto
   selado. Um membro muda ⇒ o sha do membro muda ⇒ o manifesto muda ⇒ o package hash muda.
5. O **`SEAL-RECORD`** declara: `member_manifest`, `source_package_hash`, `source_id`,
   `source_content_hash`, e `producer` como **referência a `TOOLCHAIN` com hash próprio**
   (condição 5), sem depender de rede, relógio ou `mtime` (condição 6).
6. **`seal_record_hash`** = `sha256` do arquivo do selo, registrado no
   `EXTERNAL-SEAL-REGISTRY.txt`, **fora** do diretório selado (condição 2).

## 9. RELAÇÃO ENTRE OS TRÊS HASHES

```
member_manifest_hash  ≡  SOURCE_PACKAGE_HASH      (mesmo valor, um nome canônico)
        ⊂ conteúdo do
SEAL-RECORD  →  seal_record_hash  →  registrado no EXTERNAL-SEAL-REGISTRY
```

- `seal_record_hash ≠ source_package_hash` **por construção** — o selo contém mais que o
  manifesto (produtor, metadados).
- **Auto-referência evitada:** o `SEAL-RECORD` não consta de `members[]`. É a condição 7, e
  é exatamente o canário `C3` do MS-000A, que provou ser **insatisfazível por construção**
  gravar o próprio hash dentro de si.
- `SOURCE_ID` e `SOURCE_CONTENT_HASH` vivem no `SOURCE-PROFILE`, que **é** membro — logo
  são cobertos pelo package hash, mas **não** são o package hash.

---

## 10. PLANO `PC1`–`PC8` — canários mecânicos, zero modelo

Todos sobre **fixtures sintéticas**, antes de qualquer chamada. Reutilizam o
`seal_verifier.py` do MS-000A **sem alteração**.

| # | mutação | resultado obrigatório | código esperado |
|---|---|---|---|
| **PC1** | alterar uma `CLAIM` membro | package hash **muda** **e** selo **falha** | `MEMBER_HASH_MISMATCH` + `DOES_NOT_VALIDATE_IN_PLACE` |
| **PC2** | alterar um `SOURCE_LOCAL_CANDIDATE` | idem | idem |
| **PC3** | alterar `model`/`prompt`/`output_sha256` no `COMPILE-TRACE` | idem — **e `SOURCE_ID` NÃO muda** | idem + asserção de estabilidade do `source_id` |
| **PC4** | mover `model`/`prompt`/`judge` do profile para o trace | `SOURCE-PROFILE` **byte-idêntico entre runs** com os mesmos fatos de fonte | igualdade de sha do profile |
| **PC5** | montar pacote **sem** `CLAIMS` | **FAIL** de completude | `REQUIRED_MEMBER_MISSING` |
| **PC6** | sem `SOURCE_LOCAL_CANDIDATES` | **FAIL** | `REQUIRED_MEMBER_MISSING` |
| **PC7** | sem `COMPILE-TRACE` | **FAIL** | `REQUIRED_MEMBER_MISSING` |
| **PC8** | sem `SEAL-RECORD` | **não é Source Package válido** | verificador devolve **`INVALID`** / `SEAL_RECORD_MISSING` |

### Dois pontos de precisão, aprendidos no MS-000A

**(a) `PC5`–`PC7` não são detectáveis pelo selo.** Se o membro falta **no disco e no
manifesto**, o selo valida perfeitamente — o conjunto é só menor. Detectar exige um
**instrumento distinto**: um **gate de completude** que confronte o manifesto contra a
**lista dos 11 membros obrigatórios**. Sem ele, `PC5`–`PC7` passariam silenciosamente.

**(b) `PC8` devolve `INVALID`, não `FAIL`.** O verificador do MS-000A retorna
`INVALID`/`SEAL_RECORD_MISSING` — "não consigo avaliar", não "detectei defeito". Ambos
significam *não é Source Package válido*, e o Opening Record da Round 3 deve declarar essa
distinção em vez de colapsá-la.

---

## 11. `CANDIDATE ADMISSION` — contrato e estágio

**Estágio:** **depois** do Source Package selado, **antes** de a Fusion consumir candidatos.
**A admissão NÃO altera o Source Package** — `I20`: fusão que encontra defeito em pacote
selado **para e reporta, nunca corrige**.

**Saída própria: `CANDIDATE-ADMISSION-REPORT`**, membro do Fusion Package (v1 §7.3), com,
por `source_package_ref`:

`candidates_received` · `admitted` · `rejected` · `reason_per_rejection` ·
`inherited_defects` · `kind` ∈ {`rule`, `workflow`, `anti_pattern`}.

**Nenhum threshold nesta rodada.** v1 §7.4 congela o **portão como contrato** e diz
explicitamente que **os limiares saem medidos do `PILOT-MS-000B`**. A Round 3 **mede o
baseline**; quem congela número é uma decisão posterior.

**Baseline conhecido da Round 2, citável só como `ROUND_2_OBSERVATION`:**
pacote A 6 workflow / 13 rule / 4 anti-pattern · pacote B 4 / 19 / 3.

---

## 12. `FUSION PACKAGE` — contrato aplicável

**O freeze NÃO exige selo do Fusion Package.** A tabela dos quatro produtos o define como
**"derivado, recomputável"**, endereçado por `fusion_id` — *"selado uma vez"* é o
`OPERATIONAL PACKAGE`, que o MS-000B **não produz**.

Membros aplicáveis (v1 §7.3), restritos ao que o MS-000B precisa:

`FUSED-CLAIMS` · `WORKFLOWS` transportados · `ANTI-PATTERNS` · `RELATION-SET` ·
`CONFLICT-SETS` · `DECISION-RECORDS` · **`CANDIDATE-ADMISSION-REPORT`** ·
`PROVENANCE-LEDGER` · **`FUSION-TRACE`**, mais referência aos **dois** `SOURCE_PACKAGE_HASH`
daquela run e os resultados de **blocking**.

`fusion_id` por **conjunto ordenado de hashes**, **sem `mtx_policy_hash`** (`D13`, `I26`).
**`OPERATIONAL-RULES` não é produzido** — exigiria operacionalização, fora de escopo.
**Zero Operational Package. Zero Skill Pack.**

---

## 13. ERRATA — hashes da Round 1

**Registro aditivo, sem modificar o relatório antigo.**

| | citado no relatório e em `ROUND-1-CLASSIFICATION.md` | **valor real do artefato** |
|---|---|---|
| pacote A | `4290b88f…` | **`31df720fa727867912dfe16b6c7c36fa9d10524b4f99d4482919f3276bf33ab2`** |
| pacote B | `5c32b8ed…` | **`40a786072bd3faac832be876a62d082c17995ca5cd4b3e393041fb0d74e57f8e`** |

Confirmado por duas fontes independentes: `out/source-packages.json` e os
`qualified_refs` de todas as claims da Round 1.

**Origem do erro, reproduzida:** `4290b88f…` é o hash do **dry-run**, computado com um
`model_policy` simplificado (`{'model':..., 'thinking':'disabled'}`). Eu citei o número do
dry-run em vez de ler o artefato da execução. Reprodução: com a policy real da Round 1 o
mesmo código devolve `31df720f…`.

**Lição que entra no Opening Record da Round 3:** todo hash citado em relatório é **lido do
artefato persistido**, nunca de execução exploratória — é a disciplina que a v1.2 já
aplicou às erratas de localizador.

---

## 14. REUTILIZÁVEL DA ROUND 2 — só código, após revalidação

| instrumento | condição para reuso |
|---|---|
| `tokenizer.py` | controles **9/9** revalidados |
| judge controls | **5/5** revalidados (consome **1 chamada**) |
| `classifier.py` | **7/7** fixtures, `INVALID` precede `FAIL` |
| isolation controls `ISO-A`/`ISO-B` | exclusividade revalidada mecanicamente |
| blocker + `BLK-CTRL-01/02` | controles sobrevivendo com ≥ 2 tokens |
| `seal_verifier.py` do MS-000A | **sem alteração** — é o selo canônico |

**Nenhum resultado avaliativo é carregado.**

## 15. O QUE **DEVE** SER RERODADO

Tudo: Opening Record novo · três runs novos · claims novas · **Source Packages novos, agora
com os 11 membros e selo** · candidate admission (**primeira medição real**) · blocking ·
relações · Fusion Packages novos · métricas novas.

## 16. DECISÕES AINDA ABERTAS — só Alexandre fecha

1. **`LOCAL-COHERENCE-REPORT`**: qual detector de contradição interna? Mecânico (contradição
   direta entre claims da mesma fonte) ou julgado? Se julgado, **consome chamadas** e o
   orçamento muda.
2. **`DECLARATION-SPACE-INDEX`**: o freeze deixa a **enumeração de repos/refs** explicitamente
   **não congelada**. Qual escopo para o MS-000B?
3. **`ARTIFACTS`**: basta o recorte do mapa temporal, ou exige artefato próprio?
4. **Orçamento**: 6 pacotes × (geração + entailment) + controles. Estimativa **≈ 10–13
   chamadas**, dentro do cap de 24 — **confirmar o cap**.
5. **Corpus**: mantém capítulos 12+13, ou a Round 3 é oportunidade de trocar?
6. **Onde vive a Round 3**: `pilots/PILOT-MS-000B/round-3/`, mantendo Rounds 1 e 2 intactas.

---

## 17. CLASSIFICAÇÃO

# `MS_000B_ROUND_3_READY_FOR_IMPLEMENTATION`

O contrato está recuperado e confrontado literalmente com o freeze e a v1 §4.1: as três
identidades separadas, o profile limpo, o trace recebendo o que saiu dele, o lifecycle com o
selo por último, os 11 membros, o algoritmo de hash sobre o conjunto realmente selado
reutilizando o selo já comprovado do MS-000A, os oito canários com os dois pontos de
precisão, o estágio e a saída da admissão, e o contrato do Fusion Package.

**Condicionado às seis decisões da §16.** Nenhuma linha de código foi escrita.
