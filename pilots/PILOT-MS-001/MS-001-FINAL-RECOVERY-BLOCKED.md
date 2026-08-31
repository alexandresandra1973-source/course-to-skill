# `MS_001_FINAL_RECOVERY_BLOCKED` — HARD STOP: API CREDIT

**Data:** 2026-08-31 · Opening Record Exec 2
`5b4f21b640d6d6463aa63ccbb4a0f518947d4c97566e3ef5ce3f5d8096c929b4`, pushed em `b82f6c0`
**antes de qualquer chamada**.

## 1. O bloqueio

```
anthropic.BadRequestError: 400 — 'Your credit balance is too low to access the
Anthropic API.'   request_id req_011Cea7qTo7tK1D7DadZmBm9
```

A falha ocorreu na **primeira chamada** da Execução 2 — o control `J1`–`J10` da `RUN-1`.

```
EXEC_2_CALLS = 0 / 18
```

**Nenhuma chamada de modelo foi efetivada na Execução 2.**

O §9 do bloco é explícito: *"Se saldo continuar insuficiente: `HARD STOP — API CREDIT` e
PARE sem alterar instrumento. Não mudar modelo."* Foi o que fiz.

## 2. Segunda ocorrência, mesma causa

| | data | request_id | ponto |
|---|---|---|---|
| Exec 1 | 2026-08-30 | `req_011Cea4mhNESy16KHH7tHgAZ` | chamada 14, `RUN-3 BATCH-3` |
| **Exec 2** | 2026-08-31 | `req_011Cea7qTo7tK1D7DadZmBm9` | **chamada 1**, `RUN-1 CONTROL` |

Na Exec 1 o saldo acabou **durante** a execução; na Exec 2 **já estava esgotado antes de
começar**. É condição externa, fora do alcance do piloto.

## 3. O que foi entregue mesmo assim — trabalho zero-modelo

A recuperação instrumental está **completa, selada e publicada**, pronta para executar no
instante em que houver saldo:

| entregue | estado |
|---|---|
| classificação `MS_001B_EXEC_1 = INVALID` | registrada, sem reescrever histórico |
| partição v2 `25/25/25/11/11` | `62c3fcca…` — `BATCH-1/2/3` byte-idênticos, `batch_hash` iguais |
| subdivisão posicional do antigo `BATCH-4` | união = os 22 originais, interseção vazia, verificado |
| endurecimento de completude | `RELATION-PROMPT-v2.txt` `0324219d…`, seção `[SYSTEM]` **byte-idêntica** |
| nota de recuperação | `ecc9546d…` |
| Opening Record Exec 2 | `5b4f21b6…`, **pushed antes de qualquer chamada** |
| canários | **29/29 PASS** — 22 pré-modelo + `BATCH-C0`–`C6` |
| orçamento | `PLANNED 18 · HARD_CAP 18 · RETRY 0`, separado das 13 da Exec 1 |

O par que a Exec 1 omitia deterministicamente — `f5fa1fbc…`, posição 17 de 22 — agora está
em `BATCH-4B`, **posição 6 de 11**, por consequência da subdivisão posicional e não por
escolha.

## 4. O que NÃO foi feito

**Nenhum instrumento foi alterado após o bloqueio.** Nenhum modelo trocado. Nenhum Fusion
Package construído — não há run válida. Nenhuma análise de estabilidade. Nenhum judgment da
Exec 1 reutilizado como válido. Nenhuma metodologia mudada.

## 5. Integridade

Source Packages B e C **byte-idênticos**, selos `PASS`, completude `PASS`. `PAIRSET_HASH`
inalterado, 97 pares. Corpus **0 FAILED**. Freeze **17/17**. Identity Errata íntegra.
Execuções anteriores preservadas com seus 13 raw. Drive **0 escritas**.

## 6. Para retomar

**Uma única condição externa: saldo de API para 18 chamadas.** Tudo o mais está pronto,
selado e publicado. A Execução 2 pode ser disparada sem nenhuma decisão adicional de
metodologia.

## 7. Classificação

# `MS_001_FINAL_RECOVERY_BLOCKED`

**`HARD STOP — API CREDIT`**
