# PILOT-MS-000A — SEAL CANARY · RELATÓRIO

**Gerado integralmente por `run_canary.py`.** Nenhum número digitado à mão.

- Início: `2026-08-30T02:40:49.633021-03:00`
- Opening Record: `bb4427c458e21f2938ce0ee0a9d084676d0d2a681d061b686ef5481aeec281e6`
- `seal_verifier.py`: `63cfe229de85713a2717b2d9cd3cd6d49de871b10bad255284af379259dc717f`
- `identity_verifier.py`: `51aede028a9e3069faad6bdfb1912a6cada2259918a1a8cf760e8e21691f7c84`
- Julgamento: **`MECHANICAL / OFFLINE`** — zero chamadas de modelo

## 1. As fixtures negativas contêm mesmo o defeito?

| fixture | defeito presente | asserção estrutural independente |
|---|---|---|
| `HAPPY` | SIM | conjunto integro por construcao |
| `C1` | SIM | 2 selos, versoes ['1.0', '2.0'] |
| `C2` | SIM | selo byte-identico ao de C2_SET_A=True; diverge no lugar=True |
| `C3` | SIM | members[] contem o proprio selo: ['SEAL-RECORD.yaml'] |
| `C4` | SIM | declarado=0000000000000000… real=51f9de0ff7846c3b… |
| `C5` | SIM | local_ids=['EV-0001', 'EV-0002', 'EV-0001', 'EV-0002']; repetidos=True |
| `C6` | SIM | cross_refs sem source_package_hash: [{'local_id': 'EV-0001'}] |
| `CTRL-INVALID` | SIM | YAML ilegivel: ScannerError |

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

## 3. Códigos emitidos por fixture

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

## 4. C5 — as três asserções de identidade

| asserção | resultado |
|---|---|
| local ids podem repetir | OK |
| identidade nua colide | OK |
| identidade qualificada distinta | OK |

## 5. Controles do instrumento

- fixtures na matriz: **8** · executadas: **8** — nenhum teste passou por ausência de execução
- fixtures negativas sem o defeito: **0**
- resultados inesperados: **0**
- `CTRL-INVALID` devolveu `INVALID` — o verificador distingue INVALID de FAIL

## 6. Classificação

# `PILOT_MS_000A_PASS`
