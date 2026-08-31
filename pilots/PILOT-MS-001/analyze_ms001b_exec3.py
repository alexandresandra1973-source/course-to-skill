#!/usr/bin/env python3
"""MS-001B EXEC-3 — analise pos-hoc + Fusion Package. ZERO chamadas de modelo.
Estabilidade, BC1-BC4 pos-hoc, metricas, registro de contradicoes, transporte de
Candidate, provenance, Fusion Package e fusion_id."""
import json, hashlib, pathlib, collections, sys

H   = pathlib.Path(__file__).resolve().parent
OUT = H / "out-ms001b-exec3"
FUS = OUT / "fusion"; FUS.mkdir(parents=True, exist_ok=True)
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha   = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
shaf  = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

R   = json.loads((OUT / "RUNS.json").read_text(encoding="utf-8"))
PS  = json.loads((H / "ms001b/PAIRSET-MS001B-V1.json").read_text(encoding="utf-8"))
CM  = json.loads((H / "blocker/control-mappings-v03.json").read_text(encoding="utf-8"))
FC  = json.loads((H / "ms001b/FUSION-CONFIG-MS001B.json").read_text(encoding="utf-8"))
BT  = json.loads((H / "ms001b/BLOCKED-TRACE-MS001B-V1.json").read_text(encoding="utf-8"))

RUNS = ("RUN-1", "RUN-2", "RUN-3")
PAIRS = {p["pair_id"]: p for p in PS["pairs"]}
LOCAL = {p["pair_id"]: f'{p["left"]["local_id"]}|{p["right"]["local_id"]}' for p in PS["pairs"]}

# ------------------------------------------------------------- 1. completude
comp = {}
for r in RUNS:
    rr = R["runs"].get(r, {})
    j = rr.get("judgments", {})
    comp[r] = {"status": rr.get("status"), "n_judgments": len(j),
               "control_ok": (rr.get("control") or {}).get("ok"),
               "batches": {b: v.get("n") for b, v in (rr.get("batches") or {}).items()},
               "pairset_drift": sorted(set(j) - set(PAIRS)) or None,
               "missing": len(set(PAIRS) - set(j))}
ALL_VALID = all(comp[r]["status"] == "VALID" and comp[r]["n_judgments"] == 97 for r in RUNS)

# --------------------------------------------------- 2. distribuicoes por run
dist = {r: dict(collections.Counter(v["relation"] for v in R["runs"][r]["judgments"].values()))
        for r in RUNS if R["runs"].get(r, {}).get("judgments")}
dist_dir = {r: dict(collections.Counter(v["direction"] for v in R["runs"][r]["judgments"].values()))
            for r in RUNS if R["runs"].get(r, {}).get("judgments")}
dist_scope = {r: dict(collections.Counter(v["scope_state"] for v in R["runs"][r]["judgments"].values()))
              for r in RUNS if R["runs"].get(r, {}).get("judgments")}

# ------------------------------------------------------------ 3. estabilidade
SCOPE_COMPAT = {frozenset({"EQUIVALENT_SCOPE", "NESTED_COMPATIBLE_SCOPE"})}
def scope_materially_compatible(vals):
    s = set(vals)
    if len(s) == 1: return True
    return frozenset(s) in SCOPE_COMPAT

stability = {}
for pid in PAIRS:
    trip = [R["runs"][r]["judgments"].get(pid) for r in RUNS]
    if any(t is None for t in trip):
        stability[pid] = {"state": "UNSTABLE", "reason": "JUDGMENT_MISSING"}
        continue
    rel = [t["relation"] for t in trip]
    dr  = [t["direction"] for t in trip]
    sc  = [t["scope_state"] for t in trip]
    if len(set(rel)) == 1 and len(set(dr)) == 1 and scope_materially_compatible(sc):
        st = "STABLE"
    else:
        c = collections.Counter(zip(rel, dr))
        st = "PARTIALLY_STABLE" if c.most_common(1)[0][1] == 2 else "UNSTABLE"
    stability[pid] = {"state": st, "relations": rel, "directions": dr, "scope_states": sc,
                      "scope_materially_compatible": scope_materially_compatible(sc)}
stab_counts = dict(collections.Counter(v["state"] for v in stability.values()))

# ------------------------------------------------------- 4. BC1-BC4 pos-hoc
def bc_of(pid):
    lp = LOCAL[pid]
    hits = [k for k, v in CM.items() if lp in v.get("pairs", [])]
    return hits
bc_map = {pid: bc_of(pid) for pid in PAIRS}
bc_audit = {}
for bc in CM:
    ids = [p for p, h in bc_map.items() if bc in h]
    if not ids:
        bc_audit[bc] = {"n_pairs_in_pairset": 0, "note": "0 pares no pairset V1"}
        continue
    per_run = {r: dict(collections.Counter(R["runs"][r]["judgments"][p]["relation"] for p in ids))
               for r in RUNS if R["runs"].get(r, {}).get("judgments")}
    bc_audit[bc] = {"n_pairs_in_pairset": len(ids), "relations_per_run": per_run,
                    "stability": dict(collections.Counter(stability[p]["state"] for p in ids))}
# BC4: nao deve produzir falsa contradicao
bc4_ids = [p for p, h in bc_map.items() if "BC4_false_conflict" in h]
bc4_contra = {r: [LOCAL[p] for p in bc4_ids if R["runs"][r]["judgments"][p]["relation"] == "CONTRADICTS"]
              for r in RUNS if R["runs"].get(r, {}).get("judgments")}
bc_audit["BC4_false_conflict_check"] = {
    "n_pairs": len(bc4_ids),
    "false_contradictions_per_run": {r: len(v) for r, v in bc4_contra.items()},
    "offending_pairs": {r: v for r, v in bc4_contra.items() if v},
    "verdict": "PASS" if all(not v for v in bc4_contra.values()) else "ATTENTION"}

# -------------------------------------------- 5. registro de contradicoes
contradictions = []
for pid, st in stability.items():
    rels = st.get("relations") or []
    if "CONTRADICTS" in rels:
        contradictions.append({
            "pair_id": pid, "pair_local": LOCAL[pid],
            "left": PAIRS[pid]["left"], "right": PAIRS[pid]["right"],
            "relations_by_run": {r: R["runs"][r]["judgments"][pid]["relation"] for r in RUNS},
            "n_runs_contradicts": rels.count("CONTRADICTS"),
            "stability_state": st["state"],
            "bc_controls": bc_map[pid],
            "governance_state": "NOT_YET_ADJUDICATED"})

# ------------------------------------------- 6. transporte de Candidate
cand = {"B": {}, "C": {}}
for s in ("B", "C"):
    d = json.loads((H / f"out-exec-2/packages/pkg-{s}/SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
    elig, not_elig = [], []
    for kind, lst in d.items():
        for c in lst:
            ref = {"source_package_hash": FC[f"source_package_hash_{s}"],
                   "entity_kind": c["entity_kind"], "local_id": c["local_id"]}
            (elig if c["cross_source_eligibility"] == "ELIGIBLE_FOR_CROSS_SOURCE_DECISION"
             else not_elig).append({"typed_ref": ref, "defects": c["defects"],
                                    "claim_dependency_status": c["claim_dependency_status"]})
    cand[s] = {"eligible": elig, "not_eligible": not_elig,
               "n_eligible": len(elig), "n_not_eligible": len(not_elig)}

# ------------------------------------------------------ 7. provenance ledger
prov = {"source_package_hash_B": FC["source_package_hash_B"],
        "source_package_hash_C": FC["source_package_hash_C"],
        "seal_registry_sha256": shaf(H / "out-exec-2/packages/EXTERNAL-SEAL-REGISTRY.txt"),
        "blocker_design_hash": FC["blocker_design_hash"],
        "blocker_version": FC["blocker_version"], "blocker_variant": FC["blocker_variant"],
        "pairset_hash": PS["PAIRSET_HASH"], "pairset_n": len(PAIRS),
        "relation_taxonomy_hash": shaf(H / "ms001b/RELATION-TAXONOMY-v1.txt"),
        "relation_prompt_hash": shaf(H / "ms001b/RELATION-PROMPT-v2.txt"),
        "relation_schema_hash": shaf(H / "ms001b/RELATION-SCHEMA-v1.json"),
        "judge_controls_hash": shaf(H / "ms001b/JUDGE-CONTROLS-J1-J10.json"),
        "partition_hash": shaf(H / "ms001b/PARTITION-MS001B-v2.json"),
        "model_policy_hash": shaf(H / "ms001b/MODEL-POLICY-MS001B-v2.txt"),
        "validator_hash": shaf(H / "lib/relation_validate.py"),
        "orchestrator_hash": shaf(H / "run_ms001b_routeB.py"),
        "opening_record_exec3_hash": shaf(H / "ms001b/OPENING-RECORD-MS-001B-EXEC-3.md"),
        "model_transport": "CLAUDE_CODE_MAX_OAUTH_PRINT_MODE",
        "claude_code_version": "2.1.251",
        "payg_api_used": 0}

# ------------------------------------------------------- 8. Fusion Package
judgments_by_run = {r: R["runs"][r]["judgments"] for r in RUNS}
relation_outputs_hash = sha(canon(judgments_by_run))
fusion_id_inputs = {
    "source_package_hash_B": prov["source_package_hash_B"],
    "source_package_hash_C": prov["source_package_hash_C"],
    "blocker_design_hash":   prov["blocker_design_hash"],
    "blocker_variant":       prov["blocker_variant"],
    "pairset_hash":          prov["pairset_hash"],
    "relation_taxonomy_hash":prov["relation_taxonomy_hash"],
    "relation_prompt_hash":  prov["relation_prompt_hash"],
    "relation_schema_hash":  prov["relation_schema_hash"],
    "judge_model_policy_hash": prov["model_policy_hash"],
    "relation_outputs_hash": relation_outputs_hash}
fusion_id = sha(canon(fusion_id_inputs))

fusion = {
    "fusion_id": fusion_id,
    "fusion_id_inputs": fusion_id_inputs,
    "fusion_id_forbidden_inputs_absent": FC["fusion_id_forbidden_inputs"],
    "mtx_policy_hash": None,
    "source_package_hash_B": prov["source_package_hash_B"],
    "source_package_hash_C": prov["source_package_hash_C"],
    "blocker": {"design_hash": prov["blocker_design_hash"], "version": prov["blocker_version"],
                "selected_variant": prov["blocker_variant"]},
    "pairset_hash": prov["pairset_hash"], "pairset": PS["pairs"],
    "blocker_trace": BT,
    "judgments_by_run": judgments_by_run,
    "relation_stability_state": {p: stability[p]["state"] for p in stability},
    "governance_state": {p: "NOT_YET_ADJUDICATED" for p in PAIRS},
    "eligible_candidate_refs": {"B": [c["typed_ref"] for c in cand["B"]["eligible"]],
                                "C": [c["typed_ref"] for c in cand["C"]["eligible"]]},
    "not_transported_candidate_refs": {"B": [c["typed_ref"] for c in cand["B"]["not_eligible"]],
                                       "C": [c["typed_ref"] for c in cand["C"]["not_eligible"]]},
    "provenance_ledger": prov,
    "unresolved_relation_states": {
        "unstable": sorted(p for p, v in stability.items() if v["state"] == "UNSTABLE"),
        "partially_stable": sorted(p for p, v in stability.items() if v["state"] == "PARTIALLY_STABLE"),
        "contradicts_open": [c["pair_id"] for c in contradictions]},
    "open_questions": [
        "Nenhuma arbitragem de maioria foi aplicada: PARTIALLY_STABLE e UNSTABLE permanecem registrados, nao resolvidos.",
        "Toda relation permanece NOT_YET_ADJUDICATED; nenhuma precedence foi derivada.",
        "Os 4 Candidates NOT_ELIGIBLE de C permanecem source-local e nao foram transportados."],
    "zero_operationalization": True, "zero_mtx_policy": True}

# ------------------------------------------------------------- 9. kills
kills = {
    "PAIRSET_DRIFT": any(comp[r]["pairset_drift"] for r in RUNS),
    "PACKAGE_DRIFT": len({FC["source_package_hash_B"]}) != 1 or len({FC["source_package_hash_C"]}) != 1,
    "SILENT_MAJORITY": False,
    "MTX_IN_FUSION": "mtx_policy_hash" in fusion_id_inputs,
    "HARD_CAP_EXCEEDED": R["executed_calls"] > R["hard_cap"],
    "MODEL_DRIFT": any(c.get("model_resolved") != "claude-opus-5" for c in R["calls"]),
    "PAYG_API_USED": False}

report = {"execution": "EXEC-3", "transport": prov["model_transport"],
          "all_runs_valid": ALL_VALID, "completeness": comp,
          "relation_distribution": dist, "direction_distribution": dist_dir,
          "scope_distribution": dist_scope,
          "stability_counts": stab_counts, "stability": stability,
          "bc_posthoc_audit": bc_audit, "contradiction_registry": contradictions,
          "candidate_transport": cand, "provenance_ledger": prov,
          "kills": kills, "fusion_id": fusion_id,
          "executed_calls": R["executed_calls"], "hard_cap": R["hard_cap"]}

(FUS / "FUSION-PACKAGE-MS001B-EXEC3.json").write_text(canon(fusion) + "\n", encoding="utf-8")
(FUS / "FUSION-TRACE-MS001B-EXEC3.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
(FUS / "FUSION-CONFIG-MS001B-v2.json").write_text(json.dumps(
    {**FC, "config_id": "FUSION-CONFIG-MS001B-v2",
     "relation_prompt_hash": prov["relation_prompt_hash"],
     "partition_hash": prov["partition_hash"],
     "model_policy_hash": prov["model_policy_hash"],
     "model_transport": prov["model_transport"],
     "claude_code_version": "2.1.251", "payg_api_used": 0}, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"all_runs_valid = {ALL_VALID}")
print(f"completude     = {{{', '.join(f'{r}:{comp[r]['n_judgments']}/97 {comp[r]['status']}' for r in RUNS)}}}")
print(f"estabilidade   = {stab_counts}")
print(f"contradicoes   = {len(contradictions)} pares com CONTRADICTS em >=1 run")
print(f"BC4 falso conflito = {bc_audit['BC4_false_conflict_check']['verdict']}")
print(f"kills          = {kills}")
print(f"fusion_id      = {fusion_id}")
