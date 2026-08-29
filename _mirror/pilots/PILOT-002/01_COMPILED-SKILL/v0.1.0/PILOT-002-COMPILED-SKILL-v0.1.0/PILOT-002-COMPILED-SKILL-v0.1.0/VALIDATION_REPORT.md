# PILOT-002 Compilation Validation Report

## Input gate

- SHA-256: `85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29` — PASS
- Bytes: `96246` — PASS
- Timestamp marks: `733` — PASS
- Full L0 used: `NO`
- TEST-0008 artifacts produced: `0`

## Evidence gate

- Evidence records: `44`
- Records with non-empty `source_excerpt`: `44`
- Quotes resolving exactly to declared source spans: `44`
- Epistemic distribution:
  - SOURCE_EXPLICIT: `39`
  - MODEL_INFERENCE: `5`
  - GENERAL_KNOWLEDGE: `0`
- `confidence.score` fields emitted: `0`

## UNDEFINED gate

The following source-derived operational-governance defaults remain `UNDEFINED` because the cut does not teach a complete default rule:

1. `autonomy`
2. `precedence`
3. `missing_input_action`
4. `iteration_limit`

Total `UNDEFINED` fields: `4`.

## Cut-gap handling

- `11:48 -> 15:08`: not reconstructed.
- `44:34 -> 50:00`: not reconstructed.

## Validation method

For every JSONL evidence record, the compiler re-sliced `L0-transcript-CUT.txt` by the declared `start_line`/`end_line` and required exact equality with `source_excerpt.quote`. Any mismatch would abort compilation.
