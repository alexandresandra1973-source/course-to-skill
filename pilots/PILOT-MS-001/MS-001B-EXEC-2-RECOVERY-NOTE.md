# NOTA DE RECUPERAÇÃO — MS-001B Execução 2

**Data:** 2026-08-31 · **Natureza:** ADITIVA. A Execução 1 permanece preservada e **não é retomada**.

## 1. Execução 1 — status histórico

```
MS_001B_EXEC_1 = INVALID
```

Dois motivos, ambos registrados em `out-ms001b/MS-001B-EXEC-1-BLOCKED.md`
(`d88645760ca03d17019e293d3f6b77d6be0d08cac3e9bdd2a5fbc1f29f4a782f`):

1. **falha determinística de completude de batch** — `BATCH-4` devolveu 21 de 22 em
   `RUN-1` **e** `RUN-2`, omitindo o mesmo par `f5fa1fbc…`, posição 17 de 22;
2. **esgotamento externo de saldo de API** durante `RUN-3`.

**Não são classificados FAIL:** corpus · blocker · taxonomia do juiz · Source Packages.
Os controles `J1`–`J10` passaram **30/30** ao longo das três runs.

## 2. Única mudança autorizada

```
BATCH TRANSPORT / OUTPUT COMPLETENESS RECOVERY
```

**A semântica de julgamento não muda.**

### Partição v2 — subdivisão puramente posicional

`BATCH-1`, `BATCH-2` e `BATCH-3` **preservados byte-a-byte** — os três completaram
corretamente na Execução 1, e seus `batch_hash` são idênticos aos da partição original.

O antigo `BATCH-4` (22 pares, já ordenados por `pair_id`) foi subdividido em:

| batch | n | `batch_hash` |
|---|---|---|
| `BATCH-1` | 25 | `1ad77b474888e50e…` **(inalterado)** |
| `BATCH-2` | 25 | `062f9d83e6930a99…` **(inalterado)** |
| `BATCH-3` | 25 | `2fe38932be5a1c38…` **(inalterado)** |
| `BATCH-4A` | **11** | `9d881e4a4760d42e…` |
| `BATCH-4B` | **11** | `0bb0db40d486618f…` |

**Nenhuma seleção semântica. Nenhum par isolado manualmente.** A subdivisão é posicional:
primeiros 11, últimos 11. Verificado mecanicamente: união = os mesmos 22, interseção vazia,
e os cinco batches cobrem exatamente os 97 do pairset, sem duplicata e sem faltante.

O par omitido na Execução 1 caiu em `BATCH-4B`, **posição 6 de 11** — consequência da
subdivisão, não da escolha.

### Endurecimento de completude

O envelope `[USER]` passa a carregar `batch_id`, `expected_pair_count` e a lista exata de
`expected_pair_ids`, com instrução explícita de verificar antes de finalizar e de emitir
`INDETERMINATE` em vez de omitir.

**A seção `[SYSTEM]` do prompt — todas as regras semânticas — permanece BYTE-IDÊNTICA.**
Verificado programaticamente. A mudança está confinada ao envelope de transporte.

`RELATION-PROMPT-v2.txt`: `0324219d1f62bbba9578894c41599794e7563be4a3d952d787a9ee61c5c34500`

**O validador continua sendo a autoridade.** Divergência → run `INVALID`. **Não completar
automaticamente. Não pedir par faltante em retry.**

## 3. Inalterado — byte-idêntico

Source Packages B e C · corpus · seis slices · blocker v0.3 · variante V1 · pairset e
`PAIRSET_HASH` · Claims · Candidates · taxonomia · definições semânticas · `scope_state` ·
governança · política de modelo · mappings `BC1`–`BC5` · fronteira MTX · Architecture
Freeze · Identity Errata · schema de saída · controles `J1`–`J10`.

## 4. Orçamento

```
EXEC_1_CALLS = 13   EXEC_1_STATUS = INVALID/BLOCKED
EXEC_2: por run = 1 control + 5 batches = 6 · 3 runs = PLANNED 18 · HARD_CAP 18 · RETRY 0
call 19 -> MS_001B_EXEC_2_INVALID
```

**As 13 chamadas históricas NÃO entram neste cap.** O cap é por execução selada.

## 5. Judgments históricos

Os 200 `UNRELATED` da Execução 1 permanecem **auditáveis como evidência de execução
inválida**. **Não entram** em estabilidade, Fusion nem distribuição válida. A Execução 2
produz sua própria população completa.

## 6. Canários

**29/29 PASS antes de qualquer chamada:** 22 pré-modelo reexecutados + 7 de batch
(`BATCH-C1` split, `C2` cobertura, `C3` drift por remoção e por troca, `C0` 11/11 completo,
`C4` 10 de 11, `C5` 12 com duplicata, `C6` localização do par antes omitido).

## 7. Se o saldo continuar insuficiente

`HARD STOP — API CREDIT`, **sem alterar instrumento** e **sem trocar de modelo**.
