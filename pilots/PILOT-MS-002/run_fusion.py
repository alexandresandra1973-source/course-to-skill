#!/usr/bin/env python3
"""MS-002 — FUSION multi-source A/B/C. Tres runs independentes, isolamento por processo.
Transporte Claude Max OAuth. PAYG PROIBIDA. Uso: run_fusion.py [--dry] [--cap=N]"""
import json, hashlib, pathlib, sys, collections, warnings
warnings.filterwarnings("ignore")
import jsonschema
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib"))
import transport as T
import relation_validate as RV

DRY = "--dry" in sys.argv
CAP = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--cap=")), 45))
OUT = H / ("out-fusion-dry" if DRY else "out-fusion"); (OUT / "raw").mkdir(parents=True, exist_ok=True)
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
shaf = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

PS = json.loads((H / "PAIRSET-MS002.json").read_text(encoding="utf-8"))
SCHEMA = (H / "instruments/RELATION-SCHEMA-MS002-v1.json").read_text(encoding="utf-8")
SCH = json.loads(SCHEMA)
JC = json.loads((H / "instruments/JUDGE-CONTROLS-J1-J10.json").read_text(encoding="utf-8"))
SYS, USR = T.split_prompt((H / "instruments/RELATION-PROMPT-MS002-v1.txt").read_text(encoding="utf-8"))
SYSF = OUT / "RELATION-SYSTEM.frozen.txt"; SYSF.write_text(SYS, encoding="utf-8")
BUDGET = T.Budget(cap=CAP)
BATCH = 25

# ---------------------------------------------------- payloads dos pares
CL, EV = {}, {}
for s in "ABC":
    pkg = H / "packages" / f"pkg-{s}"
    for l in (pkg / "CLAIMS.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(l); CL[(s, c["local_id"])] = c
    for l in (pkg / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines():
        e = json.loads(l); EV[(s, e["local_id"])] = e
SRC_OF = {PS[f"source_package_hash_{s}"]: s for s in "ABC"}

def side(ref):
    s = SRC_OF[ref["source_package_hash"]]
    c = CL[(s, ref["local_id"])]
    return {"claim_ref": ref, "text": c["text"], "language": c["source_language"],
            "qualifiers": c["qualifiers"],
            "evidence": [{"evidence_id": r["local_id"],
                          "excerpt": EV[(s, r["local_id"])]["excerpt"],
                          "anchor": {"local_id": EV[(s, r["local_id"])]["source_anchor_refs"][0]["local_id"],
                                     "start_s": 0, "end_s": 1}} for r in c["evidence_refs"]]}

PAIRS = {p["pair_id"]: p for p in PS["pairs"]}
IDS = [p["pair_id"] for p in PS["pairs"]]
BATCHES = {f"BATCH-{i+1}": IDS[i*BATCH:(i+1)*BATCH] for i in range((len(IDS)+BATCH-1)//BATCH)}
SENT = {pid: {"left": {e["evidence_id"] for e in side(PAIRS[pid]["left"])["evidence"]},
              "right": {e["evidence_id"] for e in side(PAIRS[pid]["right"])["evidence"]}} for pid in IDS}

def build_user(bid, ids, payloads):
    return (USR.replace("{BATCH_ID}", bid).replace("{EXPECTED_COUNT}", str(len(payloads)))
               .replace("{EXPECTED_IDS}", json.dumps(ids, ensure_ascii=False, indent=1))
               .replace("{PAIRS_JSON}", json.dumps(payloads, ensure_ascii=False, indent=1))
               .replace("{JSON_SCHEMA}", SCHEMA))

CP = [{"pair_id": sha("CTRL-" + c["id"]),
       "left": {"claim_ref": {"source_package_hash": "0"*64, "entity_kind": "claim", "local_id": "CL-9000"},
                "text": c["left"]["text"], "language": "pt", "qualifiers": c["left"]["qualifiers"],
                "evidence": [{"evidence_id": e["evidence_id"], "excerpt": e["excerpt"],
                              "anchor": {"local_id": "AN-9000", "start_s": 0, "end_s": 1}} for e in c["left"]["evidence"]]},
       "right": {"claim_ref": {"source_package_hash": "f"*64, "entity_kind": "claim", "local_id": "CL-9100"},
                 "text": c["right"]["text"], "language": "pt", "qualifiers": c["right"]["qualifiers"],
                 "evidence": [{"evidence_id": e["evidence_id"], "excerpt": e["excerpt"],
                               "anchor": {"local_id": "AN-9100", "start_s": 0, "end_s": 1}} for e in c["right"]["evidence"]]},
       "_id": c["id"], "_expect": c["expect"]} for c in JC["controls"]]
CSENT = {x["pair_id"]: {"left": {e["evidence_id"] for e in x["left"]["evidence"]},
                        "right": {e["evidence_id"] for e in x["right"]["evidence"]}} for x in CP}

def main():
    T.guard_env()
    print(f"MS-002 fusion · pares={len(IDS)} · batches={len(BATCHES)} · cap={CAP} · dry={DRY}")
    R = {"pilot": "PILOT-MS-002", "stage": "FUSION",
         "transport": "CLAUDE_CODE_MAX_OAUTH_PRINT_MODE", "payg_api_used": 0,
         "pairset_hash": PS["PAIRSET_HASH"], "n_pairs": len(IDS),
         "blocker_variant": PS["blocker_variant"], "runs": {}}
    for run in ("RUN-1", "RUN-2", "RUN-3"):
        rr = {"control": None, "batches": {}, "judgments": {}, "status": None}
        cids = [x["pair_id"] for x in CP]
        u = build_user("BATCH-1", cids, [{k: v for k, v in x.items() if not k.startswith("_")} for x in CP])
        if DRY:
            (OUT / "raw" / f"{run}-CONTROL-USER.txt").write_text(u, encoding="utf-8")
            for bid, ids in BATCHES.items():
                (OUT / "raw" / f"{run}-{bid}-USER.txt").write_text(
                    build_user(bid, ids, [{"pair_id": i, "left": side(PAIRS[i]["left"]),
                                           "right": side(PAIRS[i]["right"])} for i in ids]), encoding="utf-8")
            R["runs"][run] = rr; continue
        txt, _ = T.call(BUDGET, SYSF, u, OUT / "raw", f"{run}-CONTROL")
        doc, errs = RV.validate(T.jparse(txt), "BATCH-1", CSENT)
        if doc is None:
            rr["status"] = "INVALID"; rr["control"] = {"schema_errors": errs}
            R["runs"][run] = rr; print(f"  {run} CONTROL INVALIDO: {errs}"); continue
        jsonschema.validate(json.loads(T.jparse(txt)), SCH)
        got = {v["pair_id"]: v for v in doc["judgments"]}
        det = []
        for c in CP:
            g = got[c["pair_id"]]; e = c["_expect"]; ok = True
            if "relation" in e: ok &= g["relation"] == e["relation"]
            if "relation_not" in e: ok &= g["relation"] != e["relation_not"]
            if "direction" in e: ok &= g["direction"] == e["direction"]
            if "scope_state" in e: ok &= g["scope_state"] == e["scope_state"]
            det.append({"id": c["_id"], "ok": bool(ok),
                        "got": {k: g[k] for k in ("relation", "direction", "scope_state")}})
        cok = all(x["ok"] for x in det)
        rr["control"] = {"detail": det, "ok": cok}
        print(f"  {run} CONTROL J1-J10: {sum(x['ok'] for x in det)}/10")
        if not cok:
            rr["status"] = "INVALID"; R["runs"][run] = rr
            print(f"  {run}: controle FALHOU — batches NAO queimados"); continue
        for bid, ids in BATCHES.items():
            payload = [{"pair_id": i, "left": side(PAIRS[i]["left"]), "right": side(PAIRS[i]["right"])} for i in ids]
            txt, _ = T.call(BUDGET, SYSF, build_user(bid, ids, payload), OUT / "raw", f"{run}-{bid}")
            sent = {i: SENT[i] for i in ids}
            doc, errs = RV.validate(T.jparse(txt), bid, sent)
            if doc is None:
                rr["status"] = "INVALID"; rr["batches"][bid] = {"errors": errs}
                print(f"  {run} {bid} INVALIDO: {errs}"); break
            jsonschema.validate(json.loads(T.jparse(txt)), SCH)
            for v in doc["judgments"]: rr["judgments"][v["pair_id"]] = v
            rr["batches"][bid] = {"n": len(doc["judgments"])}
            print(f"  {run} {bid}: {len(doc['judgments'])} judgments OK")
        if rr["status"] != "INVALID":
            rr["status"] = "VALID" if len(rr["judgments"]) == len(IDS) else "INVALID"
        R["runs"][run] = rr
        d = collections.Counter(v["relation"] for v in rr["judgments"].values())
        print(f"  {run} [{rr['status']}]: {dict(d)}\n")
    R["calls"] = BUDGET.calls; R["executed_calls"] = BUDGET.n
    (OUT / "FUSION-RUNS.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  chamadas: {BUDGET.n}/{CAP}")

if __name__ == "__main__":
    sys.exit(main())
