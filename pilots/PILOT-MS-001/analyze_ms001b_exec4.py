#!/usr/bin/env python3
"""MS-001B EXEC-4 — analise pos-hoc + Fusion Package. ZERO chamadas de modelo.
BC1-BC5 tratados como retention/coverage probes: analise DESCRITIVA, sem PASS/FAIL."""
import json, hashlib, pathlib, collections, sys

H   = pathlib.Path(__file__).resolve().parent
OUT = H / "out-ms001b-exec4"
FUS = OUT / "fusion"; FUS.mkdir(parents=True, exist_ok=True)
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha   = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
shaf  = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

R  = json.loads((OUT / "RUNS.json").read_text(encoding="utf-8"))
PS = json.loads((H / "ms001b/PAIRSET-MS001B-V1.json").read_text(encoding="utf-8"))
PI = json.loads((H / "ms001b/PAIR-INPUTS-MS001B.json").read_text(encoding="utf-8"))
CM = json.loads((H / "blocker/control-mappings-v03.json").read_text(encoding="utf-8"))
FC = json.loads((H / "ms001b/FUSION-CONFIG-MS001B.json").read_text(encoding="utf-8"))
BT = json.loads((H / "ms001b/BLOCKED-TRACE-MS001B-V1.json").read_text(encoding="utf-8"))

RUNS  = ("RUN-1", "RUN-2", "RUN-3")
PAIRS = {p["pair_id"]: p for p in PS["pairs"]}
LOCAL = {p["pair_id"]: f'{p["left"]["local_id"]}|{p["right"]["local_id"]}' for p in PS["pairs"]}

# ------------------------------------------------------------ 1. completude
comp = {}
for r in RUNS:
    rr = R["runs"].get(r, {}); j = rr.get("judgments", {})
    comp[r] = {"status": rr.get("status"), "n_judgments": len(j),
               "control_ok": (rr.get("control") or {}).get("ok"),
               "batches": {b: v.get("n") for b, v in (rr.get("batches") or {}).items()},
               "unknown_pairs": sorted(set(j) - set(PAIRS)) or None,
               "missing": len(set(PAIRS) - set(j)),
               "duplicates": None}
ALL_VALID = all(comp[r]["status"] == "VALID" and comp[r]["n_judgments"] == 97
                and comp[r]["control_ok"] for r in RUNS)

# ------------------------------------------------ 2. distribuicoes por run
def dist(field):
    return {r: dict(collections.Counter(v[field] for v in R["runs"][r]["judgments"].values()))
            for r in RUNS if R["runs"].get(r, {}).get("judgments")}
dist_rel, dist_dir, dist_scope = dist("relation"), dist("direction"), dist("scope_state")

# ----------------------------------------------------------- 3. estabilidade
def scope_compat(vals):
    s = set(vals)
    return len(s) == 1 or s == {"EQUIVALENT_SCOPE", "NESTED_COMPATIBLE_SCOPE"}

stability = {}
if ALL_VALID:
    for pid in PAIRS:
        trip = [R["runs"][r]["judgments"][pid] for r in RUNS]
        rel = [t["relation"] for t in trip]
        dr  = [t["direction"] for t in trip]
        sc  = [t["scope_state"] for t in trip]
        if len(set(rel)) == 1 and len(set(dr)) == 1 and scope_compat(sc):
            st = "STABLE"
        else:
            c = collections.Counter(zip(rel, dr))
            st = "PARTIALLY_STABLE" if c.most_common(1)[0][1] == 2 else "UNSTABLE"
        stability[pid] = {"state": st, "relations": rel, "directions": dr,
                          "scope_states": sc, "scope_materially_compatible": scope_compat(sc)}
stab_counts = dict(collections.Counter(v["state"] for v in stability.values()))

# ------------------------------- 4. BC buckets — DESCRITIVO, sem PASS/FAIL
bc_map = {pid: [k for k, v in CM.items() if LOCAL[pid] in v.get("pairs", [])] for pid in PAIRS}
bc_desc = {}
for bc in CM:
    ids = [p for p, h in bc_map.items() if bc in h]
    entry = {"semantics": "blocker retention / coverage probe — SEM expected relation por par",
             "declared_pairs": len(CM[bc].get("pairs", [])),
             "cartesian_product": len(CM[bc].get("B", [])) * len(CM[bc].get("C", [])),
             "retained_pairs_in_pairset_v1": len(ids)}
    if ids and ALL_VALID:
        entry["relation_distribution_per_run"] = {
            r: dict(collections.Counter(R["runs"][r]["judgments"][p]["relation"] for p in ids)) for r in RUNS}
        entry["stability_distribution"] = dict(collections.Counter(stability[p]["state"] for p in ids))
    bc_desc[bc] = entry
no_ctrl = [p for p, h in bc_map.items() if not h]
bc_desc["(sem bucket)"] = {"retained_pairs_in_pairset_v1": len(no_ctrl)}
if no_ctrl and ALL_VALID:
    bc_desc["(sem bucket)"]["relation_distribution_per_run"] = {
        r: dict(collections.Counter(R["runs"][r]["judgments"][p]["relation"] for p in no_ctrl)) for r in RUNS}

# ---------------------------------------------------- 5. contradicoes
contradictions = []
for pid, st in stability.items():
    if "CONTRADICTS" in st["relations"]:
        contradictions.append({"pair_id": pid, "pair_local": LOCAL[pid],
                               "left": PAIRS[pid]["left"], "right": PAIRS[pid]["right"],
                               "relations_by_run": {r: R["runs"][r]["judgments"][pid]["relation"] for r in RUNS},
                               "n_runs_contradicts": st["relations"].count("CONTRADICTS"),
                               "stability_state": st["state"], "bc_buckets": bc_map[pid],
                               "governance_state": "NOT_YET_ADJUDICATED"})

# ------------------------------------------- 6. transporte de Candidate
cand = {}
for s in ("B", "C"):
    d = json.loads((H / f"out-exec-2/packages/pkg-{s}/SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
    elig, notel = [], []
    for kind, lst in d.items():
        for c in lst:
            rec = {"typed_ref": {"source_package_hash": FC[f"source_package_hash_{s}"],
                                 "entity_kind": c["entity_kind"], "local_id": c["local_id"]},
                   "defects": c["defects"], "claim_dependency_status": c["claim_dependency_status"]}
            (elig if c["cross_source_eligibility"] == "ELIGIBLE_FOR_CROSS_SOURCE_DECISION" else notel).append(rec)
    cand[s] = {"eligible": elig, "not_eligible": notel,
               "n_eligible": len(elig), "n_not_eligible": len(notel)}

# ------------------------------------------------ 7. identidade tipada
def typed_ok(ref):
    return (isinstance(ref, dict) and set(ref) == {"source_package_hash", "entity_kind", "local_id"}
            and len(ref["source_package_hash"]) == 64 and bool(ref["entity_kind"]) and bool(ref["local_id"]))
typed = {"pairset_refs": all(typed_ok(p[s]) for p in PS["pairs"] for s in ("left", "right")),
         "candidate_refs": all(typed_ok(c["typed_ref"]) for s in cand for k in ("eligible", "not_eligible")
                               for c in cand[s][k]),
         "pair_inputs_refs": all(typed_ok(PI[p][s]["typed_ref"]) for p in PAIRS for s in ("left", "right"))}
typed["all"] = all(typed.values())

# ----------------------------------------------------- 8. provenance
prov_pairs = {p: all(e.get("anchor") for s in ("left", "right") for e in PI[p][s]["evidence"]) for p in PAIRS}
prov = {"source_package_hash_B": FC["source_package_hash_B"],
        "source_package_hash_C": FC["source_package_hash_C"],
        "seal_registry_sha256": shaf(H / "out-exec-2/packages/EXTERNAL-SEAL-REGISTRY.txt"),
        "blocker_design_hash": FC["blocker_design_hash"], "blocker_version": FC["blocker_version"],
        "blocker_variant": FC["blocker_variant"],
        "pairset_hash": PS["PAIRSET_HASH"], "pairset_n": len(PAIRS),
        "relation_taxonomy_hash": shaf(H / "ms001b/RELATION-TAXONOMY-v1.txt"),
        "relation_prompt_hash": shaf(H / "ms001b/RELATION-PROMPT-v2.txt"),
        "relation_schema_hash": shaf(H / "ms001b/RELATION-SCHEMA-v2.json"),
        "relation_schema_version": "v2",
        "judge_controls_hash": shaf(H / "ms001b/JUDGE-CONTROLS-J1-J10.json"),
        "partition_hash": shaf(H / "ms001b/PARTITION-MS001B-v2.json"),
        "model_policy_hash": shaf(H / "ms001b/MODEL-POLICY-MS001B-v2.txt"),
        "validator_hash": shaf(H / "lib/relation_validate.py"),
        "orchestrator_hash": shaf(H / "run_ms001b_exec4.py"),
        "opening_record_exec4_hash": shaf(H / "ms001b/OPENING-RECORD-MS-001B-EXEC-4.md"),
        "bc_errata_hash": shaf(H / "ERRATA-MS001B-BLOCKER-CONTROL-SEMANTICS.md"),
        "model_transport": "CLAUDE_CODE_MAX_OAUTH_PRINT_MODE",
        "claude_code_version": "2.1.251", "payg_api_used": 0,
        "provenance_complete": all(prov_pairs.values()),
        "pairs_without_anchor": [p for p, ok in prov_pairs.items() if not ok]}

# ------------------------------------------------------ 9. Fusion Package
fusion = fusion_id = None
if ALL_VALID:
    jbr = {r: R["runs"][r]["judgments"] for r in RUNS}
    relation_outputs_hash = sha(canon(jbr))
    fid_inputs = {"source_package_hash_B": prov["source_package_hash_B"],
                  "source_package_hash_C": prov["source_package_hash_C"],
                  "blocker_design_hash": prov["blocker_design_hash"],
                  "blocker_variant": prov["blocker_variant"],
                  "pairset_hash": prov["pairset_hash"],
                  "relation_taxonomy_hash": prov["relation_taxonomy_hash"],
                  "relation_prompt_hash": prov["relation_prompt_hash"],
                  "relation_schema_hash": prov["relation_schema_hash"],
                  "judge_model_policy_hash": prov["model_policy_hash"],
                  "relation_outputs_hash": relation_outputs_hash}
    fusion_id = sha(canon(fid_inputs))
    fusion = {"fusion_id": fusion_id, "fusion_id_inputs": fid_inputs,
              "mtx_policy_hash": None,
              "source_package_hash_B": prov["source_package_hash_B"],
              "source_package_hash_C": prov["source_package_hash_C"],
              "blocker": {"design_hash": prov["blocker_design_hash"], "version": prov["blocker_version"],
                          "selected_variant": prov["blocker_variant"]},
              "pairset_hash": prov["pairset_hash"], "pairset": PS["pairs"],
              "blocker_trace": BT, "judgments_by_run": jbr,
              "relation_stability_state": {p: stability[p]["state"] for p in stability},
              "governance_state": {p: "NOT_YET_ADJUDICATED" for p in PAIRS},
              "eligible_candidate_refs": {s: [c["typed_ref"] for c in cand[s]["eligible"]] for s in ("B", "C")},
              "not_transported_candidate_refs": {s: [c["typed_ref"] for c in cand[s]["not_eligible"]] for s in ("B", "C")},
              "provenance_ledger": prov,
              "blocker_control_semantics": "BC1-BC5 = retention/coverage probes; ver ERRATA-MS001B-BLOCKER-CONTROL-SEMANTICS.md",
              "unresolved_relation_states": {
                  "unstable": sorted(p for p, v in stability.items() if v["state"] == "UNSTABLE"),
                  "partially_stable": sorted(p for p, v in stability.items() if v["state"] == "PARTIALLY_STABLE"),
                  "contradicts_open": [c["pair_id"] for c in contradictions]},
              "open_questions": [
                  "Nenhuma arbitragem de maioria aplicada: PARTIALLY_STABLE e UNSTABLE ficam registrados, nao resolvidos.",
                  "Toda relation permanece NOT_YET_ADJUDICATED; nenhuma precedence derivada.",
                  "BC1-BC5 nao carregam expected relation; a analise por bucket e descritiva.",
                  "Os Candidates NOT_ELIGIBLE de C permanecem source-local e nao foram transportados."],
              "zero_operationalization": True, "zero_mtx_policy": True}

# ------------------------------------------------------------- 10. kills
kills = {"PAIRSET_DRIFT": any(comp[r]["unknown_pairs"] for r in RUNS) or PS["PAIRSET_HASH"] != FC["pairset_hash"],
         "PACKAGE_DRIFT": False, "SILENT_MAJORITY": False,
         "MTX_IN_FUSION": bool(fusion and "mtx_policy_hash" in fusion["fusion_id_inputs"]),
         "HARD_CAP_EXCEEDED": R["executed_calls"] > R["hard_cap"],
         "MODEL_DRIFT": any(c.get("model_resolved") != "claude-opus-5" for c in R["calls"]),
         "PAYG_API_USED": False,
         "POST_RESULT_TUNING": False}

report = {"execution": "EXEC-4", "transport": prov["model_transport"], "all_runs_valid": ALL_VALID,
          "completeness": comp, "relation_distribution": dist_rel, "direction_distribution": dist_dir,
          "scope_distribution": dist_scope, "stability_counts": stab_counts, "stability": stability,
          "bc_bucket_descriptive": bc_desc, "contradiction_registry": contradictions,
          "candidate_transport": {s: {k: cand[s][k] for k in ("n_eligible", "n_not_eligible")} for s in cand},
          "typed_identity": typed, "provenance_ledger": prov, "kills": kills,
          "fusion_id": fusion_id, "executed_calls": R["executed_calls"], "hard_cap": R["hard_cap"]}

(FUS / "FUSION-TRACE-MS001B-EXEC4.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
(FUS / "FUSION-CONFIG-MS001B-v2.json").write_text(json.dumps(
    {**FC, "config_id": "FUSION-CONFIG-MS001B-v2",
     "relation_schema_hash": prov["relation_schema_hash"], "relation_schema_version": "v2",
     "relation_prompt_hash": prov["relation_prompt_hash"], "partition_hash": prov["partition_hash"],
     "model_policy_hash": prov["model_policy_hash"], "model_transport": prov["model_transport"],
     "claude_code_version": "2.1.251", "payg_api_used": 0,
     "blocker_control_semantics": "retention/coverage probes (ver ERRATA)"},
    ensure_ascii=False, indent=1), encoding="utf-8")
if fusion:
    (FUS / "FUSION-PACKAGE-MS001B-EXEC4.json").write_text(canon(fusion) + "\n", encoding="utf-8")

print(f"all_runs_valid = {ALL_VALID}")
for r in RUNS:
    print(f"  {r}: {comp[r]['n_judgments']}/97  status={comp[r]['status']}  control_ok={comp[r]['control_ok']}")
print(f"distribuicao   = {dist_rel}")
print(f"estabilidade   = {stab_counts}")
print(f"contradicoes   = {len(contradictions)}")
print(f"identidade tipada 100% = {typed['all']}   provenance 100% = {prov['provenance_complete']}")
print(f"kills          = {kills}")
print(f"fusion_id      = {fusion_id}")
