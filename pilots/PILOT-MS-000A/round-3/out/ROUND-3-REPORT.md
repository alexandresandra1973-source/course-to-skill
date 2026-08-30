# PILOT-MS-000A / ROUND 3 — RELATÓRIO

**Gerado integralmente por `round-3/run_canary.py`.** Nenhum número digitado à mão.

- Início: `2026-08-30T02:55:17.540527-03:00`
- Opening Record da ROUND 3: `a11fff651aca8797aa39aaca928fa4f06744478fdd29f8501c16979885c3be45`
- `seal_verifier.py`: `63cfe229de85713a2717b2d9cd3cd6d49de871b10bad255284af379259dc717f` — **reutilizado sem alteração**
- `identity_verifier.py`: `51aede028a9e3069faad6bdfb1912a6cada2259918a1a8cf760e8e21691f7c84` — **reutilizado sem alteração**
- Julgamento: **`MECHANICAL / OFFLINE`** — zero chamadas de modelo

## 1. Portão pré-execução — prova estrutural do defeito

**8/8 fixtures com o defeito provado mecanicamente, antes de o verificador rodar.**

| fixture | prova |
|---|---|
| `HAPPY` | 3 membros listados == 3 em disco, hashes conferem, sem auto-referencia, produtor confere |
| `C1` | 2 selos no mesmo diretorio, versoes ['1.0', '2.0'] |
| `C2` | selo byte-identico ao de C2_SET_A=True; diverge em C2 nos membros ['alpha.txt']; confere em C2_SET_A=True |
| `C3` | members[] lista o proprio selo (['SEAL-RECORD.yaml']); hash declarado a02949da707c7851… != real f9b8192c11aaa76c… -> insatisfazivel por construcao |
| `C4` | declarado sintaticamente sha256 valido=True; declarado == sha256 REAL de TOOLCHAIN-B=True; diverge do produtor presente TOOLCHAIN-A=True (A=a1f4415b782a71d3… B=a2f565aabd1d09b0…) -> identidade divergente, NAO dado malformado |
| `C5` | local_ids=['EV-0001', 'EV-0002', 'EV-0001', 'EV-0002'] (nus colidem); qualificadas distintas=4==4; 2 package hashes distintos |
| `C6` | cross_refs sem source_package_hash: [{'local_id': 'EV-0001'}] |
| `CTRL-INVALID` | YAML ilegivel: ScannerError |

## 2. Matriz esperado × observado

| fixture | classe | esperado | observado | veredito | código esperado presente | resultado |
|---|---|---|---|---|---|---|
| `HAPPY` | `SEAL_INTEGRITY` | `PASS` | `PASS` | OK | OK | **ESPERADO** |
| `C1` | `SEAL_INTEGRITY` | `FAIL` | `FAIL` | OK | OK | **ESPERADO** |
| `C2` | `SEAL_INTEGRITY` | `FAIL` | `FAIL` | OK | OK | **ESPERADO** |
| `C3` | `SEAL_INTEGRITY` | `FAIL` | `FAIL` | OK | OK | **ESPERADO** |
| `C4` | `SEAL_INTEGRITY` | `FAIL` | `FAIL` | OK | OK | **ESPERADO** |
| `C5` | `PACKAGE_IDENTITY` | `FAIL` | `FAIL` | OK | OK | **ESPERADO** |
| `C6` | `PACKAGE_IDENTITY` | `FAIL` | `FAIL` | OK | OK | **ESPERADO** |
| `CTRL-INVALID` | `SEAL_INTEGRITY` | `INVALID` | `INVALID` | OK | OK | **ESPERADO** |

## 3. Códigos emitidos

| fixture | esperado | observado |
|---|---|---|
| `HAPPY` | — | — |
| `C1` | `SHARED_MUTABLE_DIRECTORY` | `SHARED_MUTABLE_DIRECTORY` |
| `C2` | `DOES_NOT_VALIDATE_IN_PLACE` | `DOES_NOT_VALIDATE_IN_PLACE`, `MEMBER_HASH_MISMATCH` |
| `C3` | `SEAL_SELF_REFERENCE` | `DOES_NOT_VALIDATE_IN_PLACE`, `MEMBER_HASH_MISMATCH`, `MEMBER_SET_MISMATCH`, `SEAL_SELF_REFERENCE` |
| `C4` | `PRODUCER_IDENTITY_MISMATCH` | `PRODUCER_IDENTITY_MISMATCH` |
| `C5` | `GLOBAL_ID_COLLISION` | `GLOBAL_ID_COLLISION` |
| `C6` | `NAKED_LOCAL_ID` | `NAKED_LOCAL_ID` |
| `CTRL-INVALID` | `SEAL_RECORD_UNPARSEABLE` | `SEAL_RECORD_UNPARSEABLE` |

## 4. C4 — a correção desta rodada

- produtor declarado: `a2f565aabd1d09b086137a7cc066cce50aff27e23e4f3567b7cf74377f0df520`
- produtor real no caminho: `a1f4415b782a71d344b94fa087372247ab2de12886643037dfc37c66f8fe8ce3`
- código emitido: `PRODUCER_IDENTITY_MISMATCH`
- disparou por identidade divergente, **não** por formato inválido: SIM

## 5. C5 — as três asserções

| asserção | resultado |
|---|---|
| local ids podem repetir | OK |
| identidade nua colide | OK |
| identidade qualificada distinta | OK |

## 6. Controles do instrumento

- na matriz **8** · executadas **8** — nenhum teste passou por ausência de execução
- resultados inesperados: **0**
- defeitos que escaparam: **0**
- `CTRL-INVALID` → `INVALID` — distingue INVALID de FAIL

## 7. Classificação

# `PILOT_MS_000A_PASS`
