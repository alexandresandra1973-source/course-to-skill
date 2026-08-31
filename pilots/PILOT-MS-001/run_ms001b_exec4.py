#!/usr/bin/env python3
"""PILOT-MS-001B — EXEC-4. ROUTE B. Transporte: processo `claude -p` novo por chamada,
OAuth Claude Max. ZERO Anthropic PAYG API. Semantica identica ao run_ms001b.py:
mesmo prompt, mesmo schema, mesma particao v2, mesmos controles, mesmo validador.
HARD CAP 18, RETRY 0.  Uso: run_ms001b_routeB.py [--dry]
"""
import sys, os, json, hashlib, pathlib, datetime, collections, subprocess, shutil
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib"))
import relation_validate as RV

MODEL   = "claude-opus-5"
HARD_CAP= 18
DRY     = "--dry" in sys.argv
OUT     = H / ("out-ms001b-exec4-dry" if DRY else "out-ms001b-exec4")
RAW     = OUT / "raw"; RAW.mkdir(parents=True, exist_ok=True)

PS     = json.loads((H/"ms001b/PAIRSET-MS001B-V1.json").read_text(encoding="utf-8"))
PI     = json.loads((H/"ms001b/PAIR-INPUTS-MS001B.json").read_text(encoding="utf-8"))
PROMPT = (H/"ms001b/RELATION-PROMPT-v2.txt").read_text(encoding="utf-8")
SCHEMA = (H/"ms001b/RELATION-SCHEMA-v2.json").read_text(encoding="utf-8")
JC     = json.loads((H/"ms001b/JUDGE-CONTROLS-J1-J10.json").read_text(encoding="utf-8"))

canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha   = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
_n    = {"n": 0}
CALLS = []

def split(t):
    a = t.index("[SYSTEM]"); b = t.index("[USER]")
    return t[a+8:b].strip(), t[b+6:].strip()
SYS, USR = split(PROMPT)
IDS = [p["pair_id"] for p in PS["pairs"]]
BATCHES = {"BATCH-1": IDS[0:25], "BATCH-2": IDS[25:50], "BATCH-3": IDS[50:75],
           "BATCH-4A": IDS[75:86], "BATCH-4B": IDS[86:97]}

# ---------------------------------------------------------------- transporte
CLAUDE = shutil.which("claude") or "/home/mtx/.local/bin/claude"
SYSFILE = OUT / "SYSTEM.frozen.txt"
SYSFILE.write_text(SYS, encoding="utf-8")

FLAGS = ["-p", "--model", MODEL,
         "--system-prompt-file", str(SYSFILE),
         "--tools", "",
         "--disable-slash-commands", "--strict-mcp-config",
         "--no-session-persistence", "--permission-mode", "dontAsk",
         "--setting-sources", "",
         "--settings", '{"alwaysThinkingEnabled":false}',
         "--output-format", "json"]

FORBIDDEN_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
                 "CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CODE_USE_BEDROCK",
                 "CLAUDE_CODE_USE_VERTEX", "AWS_BEARER_TOKEN_BEDROCK")

def guard_env():
    bad = [v for v in FORBIDDEN_ENV if os.environ.get(v)]
    if bad:
        raise SystemExit(f"HARD STOP — variavel proibida definida: {bad}")
    if "--bare" in FLAGS:
        raise SystemExit("HARD STOP — --bare proibido")

def child_env():
    e = dict(os.environ)
    for v in FORBIDDEN_ENV:
        e.pop(v, None)
    e["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
    return e

def transport(user_text, run, label):
    """Uma invocacao fresh de `claude -p`. Retorna (texto, registro)."""
    uf = RAW / f"{run}-{label}-USER.txt"
    uf.write_text(user_text, encoding="utf-8")
    t0 = datetime.datetime.now().astimezone().isoformat()
    p = subprocess.run([CLAUDE] + FLAGS, input=user_text, capture_output=True,
                       text=True, env=child_env(), cwd=str(OUT), timeout=1800)
    t1 = datetime.datetime.now().astimezone().isoformat()
    (RAW / f"{run}-{label}-STDOUT.json").write_text(p.stdout, encoding="utf-8")
    if p.stderr:
        (RAW / f"{run}-{label}-STDERR.txt").write_text(p.stderr, encoding="utf-8")
    if p.returncode != 0:
        raise SystemExit(f"HARD STOP — exit {p.returncode} em {run}/{label}: {p.stderr[:400]}")
    d = json.loads(p.stdout)
    if d.get("is_error"):
        raise SystemExit(f"HARD STOP — is_error em {run}/{label}: {str(d.get('result'))[:400]}")
    txt = d["result"]
    (RAW / f"{run}-{label}-RAW.txt").write_text(txt, encoding="utf-8")
    models = list(d.get("modelUsage", {}).keys())
    if models != [MODEL]:
        raise SystemExit(f"model_resolved={models} != [{MODEL}] — MS_001B_INVALID")
    rec = {"model_resolved": models[0], "stop_reason": d.get("stop_reason"),
           "usage": {k: d["usage"].get(k) for k in
                     ("input_tokens", "output_tokens", "cache_read_input_tokens",
                      "cache_creation_input_tokens", "service_tier")},
           "thinking_tokens": d["usage"].get("output_tokens_details", {}).get("thinking_tokens"),
           "num_turns": d.get("num_turns"), "session_id": d.get("session_id"),
           "exit_code": p.returncode, "started_at": t0, "finished_at": t1,
           "cost_estimate_usd_list_price": d.get("total_cost_usd")}
    return txt, rec

def call(run, label, user_text, meta):
    if _n["n"] >= HARD_CAP:
        raise SystemExit(f"HARD CAP {HARD_CAP} — MS_001B_INVALID")
    if DRY:
        (RAW / f"{run}-{label}-USER.txt").write_text(user_text, encoding="utf-8")
        rec = {"dry": True}
        txt = ""
    else:
        txt, rec = transport(user_text, run, label)
    _n["n"] += 1
    rec.update({"call_seq": _n["n"], "run": run, "label": label,
                "model_requested": MODEL,
                "system_sha256": sha(SYS), "user_sha256": sha(user_text),
                "user_bytes": len(user_text.encode("utf-8")),
                "input_sha256": sha(canon(meta)), "output_sha256": sha(txt)})
    (RAW / f"{run}-{label}-INPUT.json").write_text(json.dumps(
        {"system_sha256": sha(SYS), "user_sha256": sha(user_text), "meta": meta},
        ensure_ascii=False, indent=1), encoding="utf-8")
    CALLS.append(rec)
    return txt

def jparse(t):
    t = t.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0]
    a, b = t.find("{"), t.rfind("}")
    return t[a:b+1] if a >= 0 else t

def pair_payload(pid):
    p = PI[pid]
    return {"pair_id": pid,
            "left": {"claim_ref": p["left"]["typed_ref"], "text": p["left"]["text"],
                     "language": p["left"]["source_language"], "qualifiers": p["left"]["qualifiers"],
                     "evidence": [{"evidence_id": e["evidence_id"], "excerpt": e["excerpt"],
                                   "anchor": e["anchor"]} for e in p["left"]["evidence"]]},
            "right": {"claim_ref": p["right"]["typed_ref"], "text": p["right"]["text"],
                      "language": p["right"]["source_language"], "qualifiers": p["right"]["qualifiers"],
                      "evidence": [{"evidence_id": e["evidence_id"], "excerpt": e["excerpt"],
                                    "anchor": e["anchor"]} for e in p["right"]["evidence"]]}}

def build_user(batch_id, ids_or_payloads, payloads):
    return (USR.replace("{BATCH_ID}", batch_id)
               .replace("{EXPECTED_COUNT}", str(len(payloads)))
               .replace("{EXPECTED_IDS}", json.dumps(ids_or_payloads, ensure_ascii=False, indent=1))
               .replace("{PAIRS_JSON}", json.dumps(payloads, ensure_ascii=False, indent=1))
               .replace("{JSON_SCHEMA}", SCHEMA))

def main():
    guard_env()
    CP = [{"pair_id": sha("CTRL-" + c["id"]),
           "left": {"claim_ref": {"source_package_hash": "0"*64, "entity_kind": "claim", "local_id": "CL-9000"},
                    "text": c["left"]["text"], "language": "pt", "qualifiers": c["left"]["qualifiers"],
                    "evidence": [{"evidence_id": e["evidence_id"], "excerpt": e["excerpt"],
                                  "anchor": {"local_id": "AN-9000", "start_s": 0, "end_s": 1}}
                                 for e in c["left"]["evidence"]]},
           "right": {"claim_ref": {"source_package_hash": "f"*64, "entity_kind": "claim", "local_id": "CL-9100"},
                     "text": c["right"]["text"], "language": "pt", "qualifiers": c["right"]["qualifiers"],
                     "evidence": [{"evidence_id": e["evidence_id"], "excerpt": e["excerpt"],
                                   "anchor": {"local_id": "AN-9100", "start_s": 0, "end_s": 1}}
                                  for e in c["right"]["evidence"]]},
           "_id": c["id"], "_expect": c["expect"]} for c in JC["controls"]]
    CSENT = {x["pair_id"]: {"left": {e["evidence_id"] for e in x["left"]["evidence"]},
                            "right": {e["evidence_id"] for e in x["right"]["evidence"]}} for x in CP}
    R = {"pilot": "PILOT-MS-001B", "execution": "EXEC-4",
         "transport": "CLAUDE_CODE_MAX_OAUTH_PRINT_MODE", "payg_api_used": 0,
         "hard_cap": HARD_CAP, "pairset_hash": PS["PAIRSET_HASH"], "runs": {}}

    for run in ("RUN-1", "RUN-2", "RUN-3"):
        rr = {"control": None, "batches": {}, "judgments": {}, "status": None}
        cids = [x["pair_id"] for x in CP]
        u = build_user("BATCH-1", cids, [{k: v for k, v in x.items() if not k.startswith("_")} for x in CP])
        txt = call(run, "CONTROL", u, {"controls": [c["_id"] for c in CP]})
        if DRY:
            R["runs"][run] = rr
            for bid, ids in BATCHES.items():
                call(run, bid, build_user(bid, ids, [pair_payload(i) for i in ids]),
                     {"batch": bid, "pair_ids": ids})
            continue
        doc, errs = RV.validate(jparse(txt), "BATCH-1", CSENT)
        if doc is None:
            rr["status"] = "INVALID"; rr["control"] = {"schema_errors": errs}
            R["runs"][run] = rr; print(f"  {run} CONTROL schema INVALIDO: {errs}"); continue
        got = {v["pair_id"]: v for v in doc["judgments"]}
        det = []
        for c in CP:
            g = got[c["pair_id"]]; e = c["_expect"]; ok = True
            if "relation" in e: ok &= g["relation"] == e["relation"]
            if "relation_not" in e: ok &= g["relation"] != e["relation_not"]
            if "direction" in e: ok &= g["direction"] == e["direction"]
            if "scope_state" in e: ok &= g["scope_state"] == e["scope_state"]
            det.append({"id": c["_id"], "expect": e,
                        "got": {k: g[k] for k in ("relation", "direction", "scope_state")}, "ok": bool(ok)})
        cok = all(x["ok"] for x in det)
        rr["control"] = {"detail": det, "ok": cok}
        for x in det:
            print(f"  {run} {x['id']:<4} {'OK ' if x['ok'] else 'FALHA'} "
                  f"obtido={x['got']['relation']}/{x['got']['direction']}/{x['got']['scope_state']}")
        if not cok:
            rr["status"] = "INVALID"; R["runs"][run] = rr
            print(f"  {run}: controle FALHOU — batches NAO queimados"); continue
        for bid, ids in BATCHES.items():
            sent = {i: {"left": {e["evidence_id"] for e in PI[i]["left"]["evidence"]},
                        "right": {e["evidence_id"] for e in PI[i]["right"]["evidence"]}} for i in ids}
            txt = call(run, bid, build_user(bid, ids, [pair_payload(i) for i in ids]),
                       {"batch": bid, "pair_ids": ids})
            doc, errs = RV.validate(jparse(txt), bid, sent)
            if doc is None:
                rr["status"] = "INVALID"; rr["batches"][bid] = {"errors": errs}
                print(f"  {run} {bid} INVALIDO: {errs}"); break
            for v in doc["judgments"]:
                rr["judgments"][v["pair_id"]] = v
            rr["batches"][bid] = {"n": len(doc["judgments"]), "errors": []}
            print(f"  {run} {bid}: {len(doc['judgments'])} judgments OK")
        if rr["status"] != "INVALID":
            rr["status"] = "VALID" if len(rr["judgments"]) == 97 else "INVALID"
            if len(rr["judgments"]) != 97:
                rr["motivo"] = f"{len(rr['judgments'])}/97 julgados"
        R["runs"][run] = rr
        d = collections.Counter(v["relation"] for v in rr["judgments"].values())
        print(f"  {run} [{rr['status']}]: {dict(d)}\n")

    R["calls"] = CALLS; R["executed_calls"] = _n["n"]
    (OUT / "RUNS.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  chamadas: {_n['n']}/{HARD_CAP}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
