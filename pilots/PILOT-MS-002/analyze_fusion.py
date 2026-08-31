#!/usr/bin/env python3
"""MS-002 — Fusion Package + fusion_id + estabilidade + descritivo. ZERO modelo."""
import json, hashlib, pathlib, collections, sys
H = pathlib.Path(__file__).resolve().parent
OUT = H / "out-fusion"
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
shaf = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

R  = json.loads((OUT / "FUSION-RUNS.json").read_text(encoding="utf-8"))
PS = json.loads((H / "PAIRSET-MS002.json").read_text(encoding="utf-8"))
BD = json.loads((H / "blocker/BLOCKER-DESIGN-MS002-v1.0.json").read_text(encoding="utf-8"))
RUNS = ("RUN-1", "RUN-2", "RUN-3")
PAIRS = {p["pair_id"]: p for p in PS["pairs"]}

comp = {}
for r in RUNS:
    rr = R["runs"].get(r, {}); j = rr.get("judgments", {})
    comp[r] = {"status": rr.get("status"), "n_judgments": len(j),
               "control_ok": (rr.get("control") or {}).get("ok"),
               "unknown_pairs": sorted(set(j) - set(PAIRS)) or None,
               "missing": len(set(PAIRS) - set(j))}
ALL_VALID = all(comp[r]["status"] == "VALID" and comp[r]["n_judgments"] == len(PAIRS)
                and comp[r]["control_ok"] for r in RUNS)

def dist(f):
    return {r: dict(collections.Counter(v[f] for v in R["runs"][r]["judgments"].values()))
            for r in RUNS if R["runs"].get(r, {}).get("judgments")}

def scope_compat(v):
    s = set(v); return len(s) == 1 or s == {"EQUIVALENT_SCOPE", "NESTED_COMPATIBLE_SCOPE"}

stability = {}
if ALL_VALID:
    for pid in PAIRS:
        t = [R["runs"][r]["judgments"][pid] for r in RUNS]
        rel = [x["relation"] for x in t]; dr = [x["direction"] for x in t]; sc = [x["scope_state"] for x in t]
        if len(set(rel)) == 1 and len(set(dr)) == 1 and scope_compat(sc): st = "STABLE"
        else:
            c = collections.Counter(zip(rel, dr))
            st = "PARTIALLY_STABLE" if c.most_common(1)[0][1] == 2 else "UNSTABLE"
        stability[pid] = {"state": st, "relations": rel, "directions": dr, "scope_states": sc}
stab = dict(collections.Counter(v["state"] for v in stability.values()))

contradictions = [{"pair_id": p, "left": PAIRS[p]["left"], "right": PAIRS[p]["right"],
                   "relations_by_run": {r: R["runs"][r]["judgments"][p]["relation"] for r in RUNS},
                   "n_runs_contradicts": v["relations"].count("CONTRADICTS"),
                   "stability_state": v["state"],
                   "feature_trace": PAIRS[p]["feature_trace"],
                   "governance_state": "NOT_YET_ADJUDICATED"}
                  for p, v in stability.items() if "CONTRADICTS" in v["relations"]]

# descritivo por combinacao de fontes
SRC = {PS[f"source_package_hash_{s}"]: f"MS002-SRC-{s}" for s in "ABC"}
combo = collections.defaultdict(list)
for p, v in PAIRS.items():
    combo[f'{SRC[v["left"]["source_package_hash"]][-1]}-{SRC[v["right"]["source_package_hash"]][-1]}'].append(p)
combo_desc = {}
for k, ids in combo.items():
    e = {"n_pairs": len(ids)}
    if ALL_VALID:
        e["relation_distribution_per_run"] = {r: dict(collections.Counter(
            R["runs"][r]["judgments"][i]["relation"] for i in ids)) for r in RUNS}
        e["stability"] = dict(collections.Counter(stability[i]["state"] for i in ids))
    combo_desc[k] = e
# descritivo por conceito compartilhado (retention probe, NAO ground truth)
conc = collections.defaultdict(list)
for p, v in PAIRS.items():
    for c in v["feature_trace"]["shared_concepts"]: conc[c].append(p)
conc_desc = {c: {"n_pairs": len(ids), "semantics": "retention/coverage probe — SEM expected relation",
                 **({"relation_distribution_run1": dict(collections.Counter(
                     R["runs"]["RUN-1"]["judgments"][i]["relation"] for i in ids))} if ALL_VALID else {})}
             for c, ids in sorted(conc.items(), key=lambda kv: -len(kv[1]))}

cand = {}
for s in "ABC":
    pkg = H / "packages" / f"pkg-{s}"
    seal = [l for l in (pkg / "SEAL-RECORD.yaml").read_text(encoding="utf-8").splitlines()
            if l.startswith("source_package_hash: ")][0].split(": ", 1)[1].strip()
    d = json.loads((pkg / "SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
    el, ne = [], []
    for b, lst in d.items():
        for c in lst:
            ref = {"source_package_hash": seal, "entity_kind": c["entity_kind"], "local_id": c["local_id"]}
            (el if c["cross_source_eligibility"] == "ELIGIBLE_FOR_CROSS_SOURCE_DECISION" else ne).append(ref)
    cand[s] = {"eligible": el, "not_eligible": ne}

prov = {f"source_package_hash_{s}": PS[f"source_package_hash_{s}"] for s in "ABC"}
prov.update({"blocker_design_hash": PS["blocker_design_hash"], "blocker_version": "v1.0",
             "blocker_variant": PS["blocker_variant"],
             "capacity_limited_sample": PS["capacity_limited_sample"],
             "pairset_hash": PS["PAIRSET_HASH"], "pairset_n": len(PAIRS), "population": PS["population"],
             "relation_taxonomy_hash": shaf(H / "instruments/RELATION-TAXONOMY-MS002-v1.txt"),
             "relation_prompt_hash": shaf(H / "instruments/RELATION-PROMPT-MS002-v1.txt"),
             "relation_schema_hash": shaf(H / "instruments/RELATION-SCHEMA-MS002-v1.json"),
             "judge_controls_hash": shaf(H / "instruments/JUDGE-CONTROLS-J1-J10.json"),
             "model_policy_hash": shaf(H / "lib/transport.py"),
             "validator_hash": shaf(H / "lib/relation_validate.py"),
             "independence_decision_record": "DR-MS-002-INDEP-001",
             "model_transport": "CLAUDE_CODE_MAX_OAUTH_PRINT_MODE",
             "claude_code_version": "2.1.251", "payg_api_used": 0})

fusion = fusion_id = None
if ALL_VALID:
    jbr = {r: R["runs"][r]["judgments"] for r in RUNS}
    fin = {"source_package_hash_A": prov["source_package_hash_A"],
           "source_package_hash_B": prov["source_package_hash_B"],
           "source_package_hash_C": prov["source_package_hash_C"],
           "blocker_design_hash": prov["blocker_design_hash"], "blocker_variant": prov["blocker_variant"],
           "pairset_hash": prov["pairset_hash"], "relation_taxonomy_hash": prov["relation_taxonomy_hash"],
           "relation_prompt_hash": prov["relation_prompt_hash"], "relation_schema_hash": prov["relation_schema_hash"],
           "judge_model_policy_hash": prov["model_policy_hash"],
           "relation_outputs_hash": sha(canon(jbr))}
    fusion_id = sha(canon(fin))
    fusion = {"fusion_id": fusion_id, "fusion_id_inputs": fin, "mtx_policy_hash": None,
              **{f"source_package_hash_{s}": prov[f"source_package_hash_{s}"] for s in "ABC"},
              "blocker": {"design_hash": prov["blocker_design_hash"], "version": "v1.0",
                          "selected_variant": prov["blocker_variant"],
                          "capacity_limited_sample": PS["capacity_limited_sample"],
                          "semantics": "BLOCKER_RETENTION != SEMANTIC_RELATION"},
              "pairset_hash": prov["pairset_hash"], "pairset": PS["pairs"],
              "blocked_trace": json.loads((H / "blocker/BLOCKED-TRACE-MS002.json").read_text(encoding="utf-8")),
              "judgments_by_run": jbr,
              "relation_stability_state": {p: v["state"] for p, v in stability.items()},
              "governance_state": {p: "NOT_YET_ADJUDICATED" for p in PAIRS},
              "eligible_candidate_refs": {s: cand[s]["eligible"] for s in "ABC"},
              "not_transported_candidate_refs": {s: cand[s]["not_eligible"] for s in "ABC"},
              "provenance_ledger": prov,
              "unresolved_relation_states": {
                  "unstable": sorted(p for p, v in stability.items() if v["state"] == "UNSTABLE"),
                  "partially_stable": sorted(p for p, v in stability.items() if v["state"] == "PARTIALLY_STABLE"),
                  "contradicts_open": [c["pair_id"] for c in contradictions]},
              "open_questions": [
                  "Nenhuma arbitragem de maioria: PARTIALLY_STABLE e UNSTABLE ficam registrados, nao resolvidos.",
                  "Toda relation permanece NOT_YET_ADJUDICATED; nenhuma precedence derivada.",
                  "O pairset e limitado pela capacidade declarada do juiz; NAO e cobertura cross-source exaustiva.",
                  "O CHANNEL C do blocker nao atravessa a fronteira ingles/portugues; a ponte e o CHANNEL A bilingue."],
              "zero_operationalization": True, "zero_mtx_policy": True}
    (OUT / "FUSION-PACKAGE-MS002.json").write_text(canon(fusion) + "\n", encoding="utf-8")

kills = {"PAIRSET_DRIFT": any(comp[r]["unknown_pairs"] for r in RUNS),
         "PACKAGE_DRIFT": False, "SILENT_MAJORITY": False,
         "MTX_IN_FUSION": bool(fusion and "mtx_policy_hash" in fusion["fusion_id_inputs"]),
         "HARD_CAP_EXCEEDED": False,
         "MODEL_DRIFT": any(c["model_resolved"] != "claude-opus-5" for c in R["calls"]),
         "PAYG_API_USED": any(c["payg"] for c in R["calls"]),
         "POST_RESULT_TUNING": False}
trace = {"stage": "FUSION", "all_runs_valid": ALL_VALID, "completeness": comp,
         "relation_distribution": dist("relation"), "direction_distribution": dist("direction"),
         "scope_distribution": dist("scope_state"), "stability_counts": stab, "stability": stability,
         "combo_descriptive": combo_desc, "concept_descriptive": conc_desc,
         "contradiction_registry": contradictions,
         "candidate_transport": {s: {"n_eligible": len(cand[s]["eligible"]),
                                     "n_not_eligible": len(cand[s]["not_eligible"])} for s in "ABC"},
         "provenance_ledger": prov, "kills": kills, "fusion_id": fusion_id,
         "executed_calls": R["executed_calls"],
         "calls_summary": {"n": len(R["calls"]),
                           "models": sorted({c["model_resolved"] for c in R["calls"]}),
                           "thinking_tokens_all_zero": all(c["thinking_tokens"] == 0 for c in R["calls"]),
                           "auth_paths": sorted({c["auth_path"] for c in R["calls"]})}}
(OUT / "FUSION-TRACE-MS002.json").write_text(json.dumps(trace, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"  all_runs_valid={ALL_VALID}")
for r in RUNS: print(f"    {r}: {comp[r]['n_judgments']}/{len(PAIRS)} status={comp[r]['status']} control_ok={comp[r]['control_ok']}")
print(f"  distribuicao: {dist('relation')}")
print(f"  estabilidade: {stab}")
print(f"  contradicoes: {len(contradictions)}")
print(f"  por combo: { {k: v['n_pairs'] for k, v in combo_desc.items()} }")
print(f"  kills: {kills}")
print(f"  fusion_id = {fusion_id}")
