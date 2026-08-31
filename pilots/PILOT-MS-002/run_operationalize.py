#!/usr/bin/env python3
"""MS-002 — OPERATIONALIZATION. Camada SEPARADA da Fusion.
Classifica unidades operacionais source-local contra a MTX-POLICY. Fail-closed.
NUNCA escreve de volta em Source Package nem em Fusion.
Transporte Claude Max OAuth. PAYG PROIBIDA. Uso: run_operationalize.py [--dry] [--cap=N]"""
import json, hashlib, pathlib, sys, collections, warnings
warnings.filterwarnings("ignore")
import jsonschema
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib"))
import transport as T

DRY = "--dry" in sys.argv
CAP = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--cap=")), 20))
OUT = H / ("out-oper-dry" if DRY else "out-oper"); (OUT / "raw").mkdir(parents=True, exist_ok=True)
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
shaf = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

POLICY = (H / "operationalization/MTX-POLICY-v1.json").read_text(encoding="utf-8")
SCHEMA = (H / "instruments/APPLICABILITY-SCHEMA-v1.json").read_text(encoding="utf-8")
SCH = json.loads(SCHEMA)
AC = json.loads((H / "instruments/APPLICABILITY-CONTROLS-AC-v1.json").read_text(encoding="utf-8"))
SYS, USR = T.split_prompt((H / "instruments/APPLICABILITY-PROMPT-v1.txt").read_text(encoding="utf-8"))
SYSF = OUT / "APPLICABILITY-SYSTEM.frozen.txt"; SYSF.write_text(SYS, encoding="utf-8")
BUDGET = T.Budget(cap=CAP)
BATCH = 20

def load_units():
    """Unidades operacionais = Candidates ELIGIBLE das tres fontes, com provenance."""
    units, index = [], {}
    for s in "ABC":
        pkg = H / "packages" / f"pkg-{s}"
        seal = [l for l in (pkg / "SEAL-RECORD.yaml").read_text(encoding="utf-8").splitlines()
                if l.startswith("source_package_hash: ")][0].split(": ", 1)[1].strip()
        cands = json.loads((pkg / "SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
        for bucket, lst in cands.items():
            for c in lst:
                if c["cross_source_eligibility"] != "ELIGIBLE_FOR_CROSS_SOURCE_DECISION":
                    continue
                uid = f'{c["source_id"]}|{c["local_id"]}'
                u = {"unit_id": uid, "entity_kind": c["entity_kind"], "source_id": c["source_id"],
                     "structure": c["structure"], "defects": c["defects"],
                     "evidence_refs": c["evidence_refs"]}
                units.append(u)
                index[uid] = {"typed_ref": {"source_package_hash": seal, "entity_kind": c["entity_kind"],
                                            "local_id": c["local_id"]},
                              "evidence_refs": c["evidence_refs"],
                              "claim_dependencies": c["claim_dependencies"],
                              "sealed_claim_refs": c["sealed_claim_refs"],
                              "source_id": c["source_id"]}
    return units, index

def build_user(bid, units):
    return (USR.replace("{BATCH_ID}", bid).replace("{EXPECTED_COUNT}", str(len(units)))
               .replace("{EXPECTED_IDS}", json.dumps([u["unit_id"] for u in units], ensure_ascii=False, indent=1))
               .replace("{MTX_POLICY_JSON}", POLICY)
               .replace("{UNITS_JSON}", json.dumps(units, ensure_ascii=False, indent=1))
               .replace("{JSON_SCHEMA}", SCHEMA))

def ac_control():
    units = [c["unit"] for c in AC["controls"]]
    txt, _ = T.call(BUDGET, SYSF, build_user("BATCH-1", units), OUT / "raw", "AC")
    d = json.loads(T.jparse(txt)); jsonschema.validate(d, SCH)
    got = {x["unit_id"]: x for x in d["decisions"]}
    res = {}
    for c in AC["controls"]:
        g = got.get(c["unit"]["unit_id"]); e = c["expect"]; ok = g is not None
        if ok and "applicability" in e: ok &= g["applicability"] == e["applicability"]
        if ok and "applicability_in" in e: ok &= g["applicability"] in e["applicability_in"]
        if ok and "channels_include" in e: ok &= e["channels_include"] in g["channels"]
        if ok and "mtx_derived" in e: ok &= g["mtx_derived"] == e["mtx_derived"]
        if ok and e.get("adaptations_nonempty"): ok &= bool(g["adaptations"])
        res[c["id"]] = {"ok": bool(ok), "got": g["applicability"] if g else None}
    return res

def main():
    T.guard_env()
    units, index = load_units()
    print(f"MS-002 operationalization · unidades ELIGIBLE={len(units)} · cap={CAP} · dry={DRY}")
    batches = {f"BATCH-{i+1}": units[i*BATCH:(i+1)*BATCH] for i in range((len(units)+BATCH-1)//BATCH)}
    if DRY:
        for bid, u in batches.items():
            (OUT / "raw" / f"{bid}-USER.txt").write_text(build_user(bid, u), encoding="utf-8")
        print(f"  {len(batches)} batches montados (dry)"); return 0
    print("  controle AC (aplicabilidade)...")
    ac = ac_control()
    print("   ", {k: ("OK" if v["ok"] else f"FALHA({v['got']})") for k, v in ac.items()})
    if not all(v["ok"] for v in ac.values()):
        raise SystemExit("MS_002_APPLICABILITY_INSTRUMENT_INVALID")
    decisions = {}
    for bid, u in batches.items():
        txt, _ = T.call(BUDGET, SYSF, build_user(bid, u), OUT / "raw", bid)
        d = json.loads(T.jparse(txt)); jsonschema.validate(d, SCH)
        if d["batch_id"] != bid: raise SystemExit(f"O01_BATCH_ID_MISMATCH {bid}")
        got = {x["unit_id"]: x for x in d["decisions"]}
        want = {x["unit_id"] for x in u}
        if set(got) != want: raise SystemExit(f"O02_UNIT_SET_MISMATCH em {bid}")
        for k, v in got.items():
            if v["mtx_derived"] and not (v.get("derivation") or "").strip():
                raise SystemExit(f"O03_MTX_DERIVED_WITHOUT_DERIVATION em {k}")
            decisions[k] = v
        print(f"  {bid}: {len(got)} decisoes OK")
    dist = collections.Counter(v["applicability"] for v in decisions.values())
    state = {"stage": "OPERATIONALIZATION", "policy_hash": shaf(H / "operationalization/MTX-POLICY-v1.json"),
             "controls_AC": ac, "n_units": len(units), "distribution": dict(dist),
             "decisions": decisions, "unit_index": index,
             "calls": BUDGET.calls, "executed_calls": BUDGET.n,
             "transport": "CLAUDE_CODE_MAX_OAUTH_PRINT_MODE", "payg_api_used": 0}
    (OUT / "APPLICABILITY-DECISIONS.json").write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  distribuicao: {dict(dist)}")
    print(f"  chamadas: {BUDGET.n}/{CAP}")

if __name__ == "__main__":
    sys.exit(main())
