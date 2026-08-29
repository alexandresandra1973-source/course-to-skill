# PHASE4_SPINE_RESULT — espinha vertical rodando contra o PILOT-001

**Corrida:** `2026-08-10T06:35:03.079940+00:00` · **Repositório:** `~/course-to-skill-claude` (ext4) · **Publicação:** por script, a partir de `work/spine_result.json`.

Nenhum número deste relatório foi digitado à mão: todos vêm do JSON da corrida.

**Critério da fase:** a espinha tem de reproduzir mecanicamente os defeitos que a auditoria mediu à mão. Reprovação correta é sucesso.


## 0. Baseline e deriva

- Arquivos no manifesto congelado: **257**
- Alterados: **0** · Sumidos: **0** · Novos: **2**
  - novo (esteira paralela): `Course-to-Skill-Compiler/02_PILOTS/PILOT-001/TEST-0008/PILOT-001-TEST-0008-ARM-A.zip`
  - novo (esteira paralela): `Course-to-Skill-Compiler/02_PILOTS/PILOT-001/TEST-0008/PILOT-001-TEST-0008-ARM-B.zip`

O manifesto **não** foi atualizado — é a referência fixa da Fase 5. Deriva só por adição; nenhuma entrada de leitura mudou.


## 1. O que cada portão devolveu, e contra que arquivo


### `G1-cutter/functional` → **PASS**
*Sujeito medido:* `/mnt/g/Meu Drive/Chat GPT/Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources/transcript/transcript-original-en.txt`

```
segments: 179
n_holdout: 36
n_train: 143
seed: 20260810
rate: 0.2
lock_sha256: 2361147f2943f536350386e37715ec41aae92e3e25838b0312c927c333a1a120
deterministic: True
corpus_hash_all: d1178b52f6c270e6
corpus_hash_train: c96f77d53563ac53
```
> corte semeado em L0, ANTES de qualquer extracao (ADR-0003)

### `G1-cutter/retroactive` → **NOT_ESTABLISHED**
*Sujeito medido:* `/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Compiler/02_PILOTS/PILOT-001/02_VALIDATION/PILOT-001-final-blind-test-kit/PILOT-001-final-blind-test-kit/judge-private/held-out-registry.yaml`

```
registry_status: NOT_AVAILABLE
created_before_modeling: False
locked: False
cases_in_registry: 0
cases_claiming_blind: 10
contaminated: 10
```
> sem lock pre-extracao, todo caso que se declara cego e' contaminado por construcao (ADR-0003)

### `G2-anchor` → **FAIL**
*Sujeito medido:* `/mnt/g/Meu Drive/Chat GPT/Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/analysis/evidence.jsonl`

```
records: 44
records_anchored_ok: 0
records_without_quote: 44
records_without_span: 0
records_with_unresolved_span: 1
records_quote_mismatch: 0
span_refs_total: 47
span_refs_resolved: 46
span_refs_unresolved: 1
resolution_reasons: {'OK': 46, 'END_MARK_NOT_FOUND': 1}
```
> quote ausente impede qualquer verificação lexical; span não resolvido é endereço inválido contra L0

### `G3-dispersion` → **FAIL**
*Sujeito medido:* `evidence.jsonl + decisions-revised.yaml`

```
fields_measured: 10
collapsed: 3
collapsed_epistemic_blocking: 2
near_collapsed: 1
underpowered: 5
suspect_underpowered: 4
underpowered_epistemic: 4
underpowered_fields: <4 itens>
n_missing_to_test: <4 itens>
ok: 1
theta_provisorio: 0.5
theta_status: EM_ABERTO — nao calibrado (ADR-0005)
n_min: 20
table: <10 itens>
```
> campo de valor unico carrega 0 bits e nao pode mudar o comportamento de consumidor nenhum (R2); `status` e' operacional e nao bloqueia

### `G5-closure` → **FAIL**
*Sujeito medido:* `/mnt/g/Meu Drive/Chat GPT/Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/PILOT-001-generated-skill-v0.1.1-corrected/generated-skill`

```
bundle_claims: 290
audited_claims: 264
compiler_invention_count: 0
holdout_leak_count: 23
rubric_internal_id_kinds: 25
rubric_internal_id_sample: <12 itens>
invention_by_file: {}
```
> normalizacao estrita de proposito (ADR-0007): comeca apertada e so afrouxa com caso documentado

### `G5-closure/origin` → **WARN**
*Sujeito medido:* `/mnt/g/Meu Drive/Chat GPT/Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/analysis/decisions.yaml`

```
field: autonomy.level
records: 8
flagged_by_adversary: 5
already_present_in_L1: 5
introduced_between_L1_and_bundle: 0
table: <8 itens>
```
> se o conteudo sinalizado ja estava em L1, a atribuicao do achado ao Compiler esta na camada errada

### `G6-ceiling` → **FAIL**
*Sujeito medido:* `/mnt/g/Meu Drive/Chat GPT/Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/PILOT-001-generated-skill-v0.1.1-corrected/generated-skill/manifest.yaml`

```
requested_level: S4_CLOSED
ceiling_reached: S0_INGESTED
n_holdout: 0
threshold: 0.8
n_min_wilson_95: 16
wilson_lb_at_n_holdout: 0.0
production_ready_allowed: False
corpus: {'lessons': 1, 'evidence_records': 44, 'decision_records': 8, 'decision_branches': 14, 'transcript_time_marks': 180}
ladder: <6 itens>
```
> n minimo calculado, nao escolhido: menor n com LB de Wilson 95% >= 0.8 e' 16 (LB=0.8064)

### `G6-ceiling/S1` → **FAIL**
*Sujeito medido:* `/mnt/g/Meu Drive/Chat GPT/Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/PILOT-001-generated-skill-v0.1.1-corrected/generated-skill/manifest.yaml`

```
requested_level: S1_ANCHORED
ceiling_reached: S0_INGESTED
n_holdout: 0
threshold: 0.8
n_min_wilson_95: 16
wilson_lb_at_n_holdout: 0.0
production_ready_allowed: False
corpus: {'claimed_in_manifest': 'S3_EXECUTABLE'}
ladder: <6 itens>
```
> n minimo calculado, nao escolhido: menor n com LB de Wilson 95% >= 0.8 e' 16 (LB=0.8064)

## 2. Tabela de dispersão medida (G3)

| campo | N | k | distintos | H (bits) | H_norm | estado |
|---|---|---|---|---|---|---|
| decision.origin_class | 8 | 2 | 1 | 0.0 | 0.0 | SUSPECT_UNDERPOWERED |
| decision.promotion_level | 8 | 3 | 1 | 0.0 | 0.0 | SUSPECT_UNDERPOWERED |
| decision.rationale.state | 8 | 4 | 1 | 0.0 | 0.0 | SUSPECT_UNDERPOWERED |
| decision.status | 8 | 5 | 1 | 0.0 | 0.0 | SUSPECT_UNDERPOWERED |
| evidence.confidence.level | 44 | 3 | 1 | 0.0 | 0.0 | COLLAPSED |
| evidence.origin_class | 44 | 3 | 1 | 0.0 | 0.0 | COLLAPSED |
| evidence.status | 44 | 5 | 1 | 0.0 | 0.0 | COLLAPSED |
| decision.autonomy.level | 8 | 4 | 2 | 0.5436 | 0.2718 | UNDERPOWERED |
| evidence.evidence_strength | 44 | 5 | 3 | 0.7889 | 0.3397 | NEAR_COLLAPSED |
| evidence.category | 44 | 14 | 12 | 3.2907 | 0.8643 | OK |

## 3. Diff: esperado pela auditoria × medido pelo código

| veredito | o que a auditoria esperava | o que o código mediu |
|---|---|---|
| ✅ CONFIRMA | G2 reprova por quote 0/44 | state=FAIL sem_quote=44/44 ancoradas_ok=0 |
| ✅ CONFIRMA | G2 acusa o span de EV-0001 que não resolve | span_refs 46/47 resolvem; motivos={'OK': 46, 'END_MARK_NOT_FOUND': 1} |
| ✅ CONFIRMA | G3 poupa `category` | H_norm=0.8643 state=OK |
| ✅ CONFIRMA | G3 acusa os campos de entropia zero | campos com H_norm=0: 7; classificados COLLAPSED: 3; UNDERPOWERED: 5 |
| ✅ CONFIRMA | Cutter marca TEST-0009 como contaminado | CONTAMINATED_BY_CONSTRUCTION; spans=['L0:068b4998c160:t=00:07:19-00:07:42', 'L0:068b4998c160:t=00:07:42-00:07:56', 'L0:068b4998c160:t=00:07:56-00:08:10', 'L0:068b4998c160:t=00:08:05-00:08:20', 'L0:068b4998c160:t=00:08:20-00:08:59'] |
| ✅ CONFIRMA | G6 recusa S4 | pedido=S4_CLOSED teto=S0_INGESTED n_holdout=0 n_min=16 |
| ✅ CONFIRMA | G6 recusa S1 | pedido=S1_ANCHORED teto=S0_INGESTED corpus={'lessons': 1, 'evidence_records': 44, 'decision_records': 8, 'decision_branches': 14, 'transcript_time_marks': 180} |

### 3.1 Divergência real, escondida numa linha que passou

A **medição** bate: **7** campos com entropia zero. A **classificação** não: o código chama de `COLLAPSED` apenas **3** deles e manda os outros **0** para `UNDERPOWERED`.

Motivo: a ADR-0005 exige `N ≥ 20` para concluir, e os campos de decisão têm N=8. A tabela das Fases 1–3 foi calculada **sem** essa guarda, que só passou a existir na ADR-0005. O código está certo pela minha própria regra; a tabela anterior concluiu com base pequena demais.

Campos que a auditoria chamou de COLLAPSED e o código recusa concluir:

| campo | N | distintos | H_norm | estado pelo código |
|---|---|---|---|---|

**Correção de medida das fases anteriores.** A Fase 3 escreveu *"8 de 10 campos carregam 0 bits ou quase"*. O número exato é: **7** com H=0, **1** quase-colapsados, **1** saudável — ou seja **9 de 10** não-OK, não 8.


## 3.2 Achados novos (não vistos pela auditoria manual)

| # | achado |
|---|---|
| N1 | O bundle corrigido **não** inventa: `compiler_invention_count = 0` sobre 290 afirmações da camada de conhecimento, contra 264 pós-auditoria. G5 confirma que o empacotador é função pura **nesta versão**. |
| N2 | **SC-001 atribuiu o defeito à camada errada.** Dos 5 ADRs que o adversário disse terem recebido autonomia *"adicionada pelo compilador"*, **5 já tinham o valor em `analysis/decisions.yaml` (L1)** e **0** entraram entre L1 e o bundle. O achado era correto em substância (não ensinado pela fonte) e errado em atribuição — consertar o Compiler não teria impedido nada. |
| N3 | **G3 é estruturalmente cego à camada de decisão em corpus de uma aula.** 0 dos 10 campos caem em `UNDERPOWERED` só por N=8 < 20. O problema de tamanho de corpus contamina o portão de dispersão, não só o held-out — a ADR-0005 precisa dizer o que `UNDERPOWERED` faz com o teto, e hoje não diz. |
| N4 | **Vazamento contrafactual = 23.** Com um corte legítimo de 20% (semente 20260810), essa é a quantidade de citações de span dos artefatos que cairia dentro do held-out. Não é defeito do piloto — é a medida, só possível agora, de quanto o artefato depende de um quinto aleatório da fonte. |
| N5 | **Falso positivo do meu próprio extrator de claims.** A primeira corrida acusou 1 invenção que era `manifest.skill.name` (*"HubSpot AI Agent Builder — PILOT-001"*). Corrigi estreitando o **escopo** (manifest e audit são metadado por contrato, não camada de conhecimento), não afrouxando o **limiar**. Registrado porque ajustar verificação até parar de reclamar é exatamente o defeito auditado. |

## 4. Casos que se declaram cegos (Cutter retroativo)

| caso | tipo declarado | veredito | spans de suporte |
|---|---|---|---|
| TEST-0001 | DECISION_REPRODUCTION | CONTAMINATED_BY_CONSTRUCTION | 2 |
| TEST-0002 | MISSING_INPUT | CONTAMINATED_BY_CONSTRUCTION | 2 |
| TEST-0003 | COUNTERFACTUAL | CONTAMINATED_BY_CONSTRUCTION | 5 |
| TEST-0004 | ANTI_PATTERN | CONTAMINATED_BY_CONSTRUCTION | 3 |
| TEST-0005 | DECISION_REPRODUCTION | CONTAMINATED_BY_CONSTRUCTION | 2 |
| TEST-0006 | EXECUTION | CONTAMINATED_BY_CONSTRUCTION | 7 |
| TEST-0007 | ABLATION | CONTAMINATED_BY_CONSTRUCTION | 7 |
| TEST-0008 | SUMMARY_VS_SKILL | CONTAMINATED_BY_CONSTRUCTION | 7 |
| TEST-0009 | BLIND_EVALUATION | CONTAMINATED_BY_CONSTRUCTION | 5 |
| TEST-0010 | EDGE_CASE | CONTAMINATED_BY_CONSTRUCTION | 0 |

## 5. Como rodar

```bash
cd ~/course-to-skill-claude
python3 spine.py      # roda a espinha
python3 run_tests.py  # meta-testes dos portões
python3 publish.py    # publica este relatório
```
