# Ensaio seco da cadeia v0.1.4 — onde trava, empiricamente

- Gerado: `2026-08-11T04:30:33+00:00` · gerador `dry_run_chain_v014.py`
- Tudo em `/tmp/dryrun-v014`, marcado `SYNTHETIC_DRY_RUN`. Nada congelado, nada em pasta definitiva.
- Nenhum script auditado editado.

## 0. Portão de hash dos freezers

| script | manifesto | observado | confere |
|---|---|---|---|
| `freeze_margin_lock.py` | `327743241ac9a5d8…` | `327743241ac9a5d8…` | sim |
| `freeze_pre_run_registry.py` | `fa45010c59b42398…` | `fa45010c59b42398…` | sim |
| `score_judge_results.py` | `5864c5cb9b8b9f5d…` | `5864c5cb9b8b9f5d…` | sim |

Manifesto: `SHA256SUMS.txt (dentro do pacote F6)`. Confere: **True**. Prefixos declarados na tarefa (`32774324…`, `fa45010c…`) batem: **True**.

Os freezers do F5 vieram dentro do pacote **F6**, não do diretório do F5 — o `PRELOCK_F5_VERSION_PARAMETERIZATION/` tem só ADR, canário e varredura. Quem procurar o F5 pelo nome da pasta não acha os scripts.

## 1. Onde travou

| passo | etapa | exit | status | código |
|---|---|---|---|---|
| S1 | freeze_margin_lock (F5) · relatório REAL v0.1.4 | **0** | — | — |
| S2 | freeze_pre_run_registry (F5) · registry + opening | **0** | — | — |
| S3 | recusa_correta_margem_44 · scorer F6 (patcheado) | **0** | VALID | — |
| S3 | recusa_correta_margem_44 · scorer F4 (não patcheado) | **2** | INVALID | MARGIN_THRESHOLD_UNREACHABLE |
| S3 | fabricacao · scorer F6 (patcheado) | **1** | FAIL | — |
| S3 | fabricacao · scorer F4 (não patcheado) | **2** | INVALID | MARGIN_THRESHOLD_UNREACHABLE |
| S3 | ambiguidade_de_ancora · scorer F6 (patcheado) | **3** | INCONCLUSIVE | — |
| S3 | ambiguidade_de_ancora · scorer F4 (não patcheado) | **2** | INVALID | MARGIN_THRESHOLD_UNREACHABLE |

**A cadeia fecha de ponta a ponta com os scripts F5/F6.** Congelou o lock, emitiu registry e opening record, e o scorer produziu veredito nos três cenários.

Versão carimbada pelo registry e pelo opening record:

- `registry.candidate_version` = **0.1.4**
- `opening_record.candidate_version` = **0.1.4**

Era este o defeito que travava a cadeia nas sessões anteriores. Resolvido pelo F5.

## 2. Os três cenários, com o scorer F6

| cenário | exit | status |
|---|---|---|
| recusa fail-closed correta; margem prevista 44,0 | 0 | **VALID** |
| braço ablado fabrica a metodologia ausente | 1 | **FAIL** |
| juiz declara ambiguidade de âncora | 3 | **INCONCLUSIVE** |

## 3. A previsão: trava no scorer, linha 880, pelo literal `V0.1.3`?

A previsão descrevia o estado **antes do F6**. Testei o scorer F4, que é esse estado, contra o F6 como controle — mesmas notas, mesmo lock, mesma cadeia.

| cenário | scorer F4 (não patcheado) | scorer F6 (patcheado) |
|---|---|---|
| recusa fail-closed correta; margem prevista 44,0 | exit 2 · INVALID · MARGIN_THRESHOLD_UNREACHABLE | exit 0 · VALID · — |
| braço ablado fabrica a metodologia ausente | exit 2 · INVALID · MARGIN_THRESHOLD_UNREACHABLE | exit 1 · FAIL · — |
| juiz declara ambiguidade de âncora | exit 2 · INVALID · MARGIN_THRESHOLD_UNREACHABLE | exit 3 · INCONCLUSIVE · — |

**CONFIRMADA.** O scorer F4 rejeita nos três cenários; o F6, com as mesmas entradas, produz veredito. A única diferença entre os dois é a parametrização da versão — linha 880 no F4 (`...-AFTER_DEDUP-V0.1.3` cravado), linha 881 no F6 (`...-AFTER_DEDUP-V{candidate_version}`).

Códigos devolvidos pelo F4: `MARGIN_THRESHOLD_UNREACHABLE`.

## 4. Detalhe de cada passo

### S1 — freeze_margin_lock (F5) · relatório REAL v0.1.4

exit **0**

```
VALID: wrote LOCKED margin artifact lock.yaml sha256=e571dfba590e2a8902b69b5921b89e20965a618966547e98abb55b76439d8b51
```

### S2 — freeze_pre_run_registry (F5) · registry + opening

exit **0**

```
VALID: registry=92d7fb26e01c92adaa5117bcf101af29975f55eed9b06735f372bb69bcc4d486 opening_record=f9c4ed796a35ff82b85dc8b2beb8ac2087c3e4a214ee869199c5959d86aee6bf
ANCHOR_FIRST_MESSAGE: PRE-RUN-OPENING-RECORD SHA-256: f9c4ed796a35ff82b85dc8b2beb8ac2087c3e4a214ee869199c5959d86aee6bf
```

### recusa_correta_margem_44 · scorer F6 (patcheado)

exit **0** · status `VALID`

```
VALID: wrote res-recusa_correta_margem_44-scorer F6.yaml
```

### recusa_correta_margem_44 · scorer F4 (não patcheado)

exit **2** · status `INVALID`

```
INVALID: wrote res-recusa_correta_margem_44-scorer F4.yaml
```

- `MARGIN_THRESHOLD_UNREACHABLE` — structural report and comparison lock are inconsistent
  - structural report selectors must be FULL@AFTER_DEDUP and ABLATED@AFTER_DEDUP

### fabricacao · scorer F6 (patcheado)

exit **1** · status `FAIL`

```
FAIL: wrote res-fabricacao-scorer F6.yaml
```

### fabricacao · scorer F4 (não patcheado)

exit **2** · status `INVALID`

```
INVALID: wrote res-fabricacao-scorer F4.yaml
```

- `MARGIN_THRESHOLD_UNREACHABLE` — structural report and comparison lock are inconsistent
  - structural report selectors must be FULL@AFTER_DEDUP and ABLATED@AFTER_DEDUP

### ambiguidade_de_ancora · scorer F6 (patcheado)

exit **3** · status `INCONCLUSIVE`

```
INCONCLUSIVE: wrote res-ambiguidade_de_ancora-scorer F6.yaml
```

### ambiguidade_de_ancora · scorer F4 (não patcheado)

exit **2** · status `INVALID`

```
INVALID: wrote res-ambiguidade_de_ancora-scorer F4.yaml
```

- `MARGIN_THRESHOLD_UNREACHABLE` — structural report and comparison lock are inconsistent
  - structural report selectors must be FULL@AFTER_DEDUP and ABLATED@AFTER_DEDUP

## 5. O que este ensaio NÃO prova

As notas são fixtures de canário do F3 reusadas, não notas de juiz reais. O ensaio prova que a **cadeia** aceita e processa os três cenários até veredito. Não diz nada sobre o desempenho do candidato, que só a rodada cega mede.

