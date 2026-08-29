# Cadeia pré-run da v0.1.4 — o que fechou e o que recusou

- Gerado: `2026-08-11T04:00:54+00:00` · gerador `prerun_chain_v014.py`
- READ-ONLY sobre `Course-to-Skill/`. Nenhum script auditado foi editado.
- **Nada foi congelado.**

## 1. Portão dos freezers

| freezer | pacote de origem | bytes | sha256 | confere |
|---|---|---|---|---|
| `freeze_margin_lock.py` | `PILOT-001-v0.1.3-PRELOCK-PATCH-F4-STRUCTURAL-ID.zip` | 27303 | `09a742c237a7a7aa…` | sim |
| `freeze_pre_run_registry.py` | `PILOT-001-v0.1.3-PRELOCK-PATCH-F3-TRISTATE.zip` | 3979 | `80ff9c070e0692ed…` | sim |

Ambos conferem contra o manifesto do próprio pacote.

## 2. Árvore v0.1.4

Criada em `docs/v0.1.4/06_COMPARISON_ARMS/TEST-0007`.

**Os artefatos v0.1.4 hoje moram indevidamente sob `v0.1.3/`.** O pacote `PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN.zip` está em `Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007/ARMS_WORDING_FROZEN/`. Esta árvore não corrige isso — `Course-to-Skill/` é read-only nesta sessão. Mover é decisão do Alexandre.

## 3. Cadeia de lock — RECUSADA, em dois pontos independentes

### 3.1 `freeze_margin_lock.py` → exit 2

```
status: INVALID
errors:
- code: MARGIN_THRESHOLD_UNREACHABLE
  test_id: TEST-0007
  detail: structural report must explicitly identify FULL@AFTER_DEDUP and ABLATED@AFTER_DEDUP
```

**Causa isolada.** Rodei o mesmo freezer mudando **apenas** o `arm_id` dos dois braços no relatório estrutural, numa cópia descartável em `/tmp` — o relatório publicado não foi tocado:

| campo | no relatório publicado | no diagnóstico |
|---|---|---|
| `arms.full_after_dedup.arm_id` | `PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4` | `FULL` |
| `arms.ablated_after_dedup.arm_id` | `PILOT-001-TEST-0007-ABLATED-AFTER_DEDUP-v0.1.4` | `ABLATED` |

Resultado: exit 0 — **congelaria**.

Ou seja, tudo o mais passa: limiar 34,0, teto 60,0, hashes dos braços, regra de decisão. O que barra é uma **amarração de versão** dentro do freezer: a função `structural_role` aceita só o papel genérico (`FULL`, `ABLATED`) ou o nome de artefato **da v0.1.3** (`PILOT-001-TEST-0007-…-AFTER_DEDUP-V0.1.3`), cravado no código. O nome da v0.1.4 não está na lista.

Isso é justamente a área que o patch F4 (`STRUCTURAL-ARM-ID-NORMALIZATION`) endereçou — e que não foi estendida para a 0.1.4.

### 3.2 `freeze_pre_run_registry.py` → exit 0

Sondado sobre o lock do diagnóstico, só para ver o que ele carimbaria:

```
VALID: registry=3cfa62f2f97ee69830b62f8df9b5f2d631fc7e9ab257db3ba8457b3ccace226b opening_record=4540d07d71f585204594e0e4955ce3180fde751e6d504741eb8035ad3f42117c
ANCHOR_FIRST_MESSAGE: PRE-RUN-OPENING-RECORD SHA-256: 4540d07d71f585204594e0e4955ce3180fde751e6d504741eb8035ad3f42117c
```

| campo | valor carimbado |
|---|---|
| `registry_candidate_version` | **0.1.3** |
| `opening_candidate_version` | **0.1.3** |

**Este é o segundo bloqueio, e é o decisivo.** O freezer tem `candidate_version` **fixo em `'0.1.3'`** no código. Congelar a cadeia agora gravaria, dentro do registry e do opening record — artefatos que existem justamente para provar integridade — a afirmação falsa de que a rodada é 0.1.3.

### 3.3 Decisão

**Não congelei.** Havia dois caminhos e recusei os dois:

1. **Editar os freezers** para aceitar 0.1.4 — quebra a premissa de usar "os scripts já auditados". A correção precisa vir como patch auditado, não como edição de madrugada.
2. **Ajustar a entrada** para o formato que o validador da v0.1.3 aceita — resolveria o 3.1, mas não o 3.2, e o registry continuaria carimbando 0.1.3. Congelar um artefato de integridade com a versão errada é pior do que não congelar.

## 4. BLIND_RUN_READY

Publicada em `docs/v0.1.4/06_COMPARISON_ARMS/TEST-0007/BLIND_RUN_READY`:

- `ANCHOR-LINES.md` — 665 B · `4b9ee60904b895cf…`
- `CANDIDATE-ATTACHMENTS.md` — 1571 B · `6ac55e85e1da7d8f…`
- `JUDGE-ATTACHMENTS.md` — 1351 B · `edc929fa7f2fafbd…`
- `JUDGE-BLIND-RUN-INSTRUCTIONS-v0.1.4.md` — 2799 B · `56420146fe414b08…`
- `README-ABERTURA.md` — 631 B · `507828189ec6461f…`
- `SHA256SUMS.txt` — 678 B · `e4b81a22fea03e00…`

As instruções do juiz da v0.1.4 foram **derivadas** da v0.1.3 (origem sha256 `d62046601f170ec6…`), com o cabeçalho declarando que é derivada e não original. Alterações: título: 'TEST-0007 v0.1.3' → 'TEST-0007 v0.1.4'; mais a tabela de hashes da rodada v0.1.4.

Os nomes de arquivo da régua e dos addenda continuam `v0.1.3` de propósito: esses artefatos não foram reemitidos, e renomeá-los apontaria para arquivos que não existem.

**A segunda linha de âncora está bloqueada.** A do juiz é o hash do opening record, e o opening record não existe.

