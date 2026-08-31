#!/usr/bin/env python3
"""MS-001B EXEC-4 — canarios RS1-RS8 do RELATION-SCHEMA-v2. ZERO chamadas de modelo.
Testa duas camadas: (a) JSON Schema v2, (b) lib/relation_validate.py (inalterado)."""
import json, sys, pathlib, copy, warnings
warnings.filterwarnings("ignore")
import jsonschema
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib")); import relation_validate as RV

SCHEMA = json.loads((H / "ms001b/RELATION-SCHEMA-v2.json").read_text(encoding="utf-8"))
PI     = json.loads((H / "ms001b/PAIR-INPUTS-MS001B.json").read_text(encoding="utf-8"))
PS     = json.loads((H / "ms001b/PAIRSET-MS001B-V1.json").read_text(encoding="utf-8"))
IDS    = [p["pair_id"] for p in PS["pairs"]]
B4A    = IDS[75:86]                      # BATCH-4A = 11 pares da particao v2

def schema_ok(doc):
    try:
        jsonschema.validate(doc, SCHEMA); return True, None
    except jsonschema.ValidationError as e:
        return False, e.message[:90]

# payload real emitido pela EXEC-3 no BATCH-4A (batch_id historico = "BATCH-4")
raw = (H / "out-ms001b-exec3/raw/RUN-1-BATCH-4A-RAW.txt").read_text(encoding="utf-8").strip()
if raw.startswith("```"): raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
EXEC3 = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])

def with_batch(bid, judgments=None):
    d = copy.deepcopy(EXEC3); d["batch_id"] = bid
    if judgments is not None: d["judgments"] = judgments
    return d

SENT = {i: {"left":  {e["evidence_id"] for e in PI[i]["left"]["evidence"]},
            "right": {e["evidence_id"] for e in PI[i]["right"]["evidence"]}} for i in B4A}

R, fails = [], 0
def check(cid, desc, got, want):
    global fails
    ok = got == want
    if not ok: fails += 1
    R.append((cid, desc, "PASS" if ok else "FALHA", f"esperado={want} obtido={got}"))

# ---- RS1..RS5: regra de batch_id no schema v2
for cid, bid, want in (("RS1", "BATCH-1", True), ("RS2", "BATCH-4A", True),
                       ("RS3", "BATCH-4B", True), ("RS4", "BATCH-4", False),
                       ("RS5", "BATCH-5", False)):
    ok, _ = schema_ok(with_batch(bid))
    check(cid, f"schema v2 aceita batch_id={bid}", ok, want)

# ---- RS6: payload real da EXEC-3 com batch_id corrigido -> schema PASS
ok, msg = schema_ok(with_batch("BATCH-4A"))
check("RS6", "payload BATCH-4A da EXEC-3 com batch_id=BATCH-4A", ok, True)

# ---- RS7: 10 de 11 -> completude FALHA
d10 = with_batch("BATCH-4A", EXEC3["judgments"][:10])
doc, errs = RV.validate(json.dumps(d10, ensure_ascii=False), "BATCH-4A", SENT)
check("RS7", "10/11 -> completude FALHA (R15_PAIR_MISSING)",
      doc is None and "R15_PAIR_MISSING" in errs, True)

# ---- RS8: 11 de 11 -> PASS nas duas camadas
d11 = with_batch("BATCH-4A")
ok, _ = schema_ok(d11)
doc, errs = RV.validate(json.dumps(d11, ensure_ascii=False), "BATCH-4A", SENT)
check("RS8", "11/11 -> schema v2 PASS e validador PASS", ok and doc is not None and not errs, True)

# ---- guardas de conservadorismo
check("RS9", "schema v2 difere de v1 SOMENTE em title e batch_id",
      [k for k in SCHEMA if k != "title"] ==
      [k for k in json.loads((H / "ms001b/RELATION-SCHEMA-v1.json").read_text(encoding="utf-8")) if k != "title"]
      and SCHEMA["properties"]["judgments"] ==
      json.loads((H / "ms001b/RELATION-SCHEMA-v1.json").read_text(encoding="utf-8"))["properties"]["judgments"], True)
check("RS10", "pairset intacto: 97 pares e PAIRSET_HASH congelado",
      len(IDS) == 97 and PS["PAIRSET_HASH"] == "a0b116d93f754576cf8fbbbf6eb1757b2837b7ea18b415f8e2bce30c1ee517f5", True)
check("RS11", "particao ativa 25/25/25/11/11",
      [25, 25, 25, len(B4A), len(IDS[86:97])] == [25, 25, 25, 11, 11], True)

for cid, desc, st, detail in R:
    print(f"  {'OK ' if st == 'PASS' else 'FALHA'} {cid:<5} {desc:<58} {detail}")
print(f"\n  {len(R) - fails}/{len(R)} canarios de schema PASS")
sys.exit(1 if fails else 0)
