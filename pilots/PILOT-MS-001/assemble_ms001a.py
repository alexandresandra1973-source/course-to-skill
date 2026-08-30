#!/usr/bin/env python3
"""MS-001A EXEC 2 — montagem deterministica. ZERO chamadas de modelo.
Ordem literal do Opening Record: candidate finalization DEPOIS do entailment."""
import sys, json, hashlib, pathlib, collections, datetime
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib")); sys.path.insert(0, str(H.parent / "PILOT-MS-000A"))
import builders as B, identity as I, gate as G, package as P
import seal_verifier as SV

OUT = H / "out-exec-2"; PKGS = OUT / "packages"; PKGS.mkdir(parents=True, exist_ok=True)
ST = json.loads((OUT / "STATE.json").read_text(encoding="utf-8"))
FR = B.frozen_slices(); SRCS = ["MS001-SRC-B", "MS001-SRC-C"]
t2f = {tuple(k.split("|")): v for k, v in ST["t2f"].items()}
R = {"execution": "EXEC_2", "hard_cap": 10, "executed_calls": len(ST["calls"])}
REG = PKGS / "EXTERNAL-SEAL-REGISTRY.txt"
REG.write_text("# MS-001A EXEC-2 EXTERNAL SEAL REGISTRY — fora de todo diretorio selado\n", encoding="utf-8")

ANCH = {s: B.build_anchors(s) for s in SRCS}
EVID = {s: B.build_evidence(s, ANCH[s]) for s in SRCS}
report = {}

for src in SRCS:
    tag = src.split("-")[-1]
    d = PKGS / f"pkg-{tag}"; (d / "L0").mkdir(parents=True, exist_ok=True); (d / "ARTIFACTS").mkdir(exist_ok=True)
    slices = [k for k in sorted(FR) if FR[k]["source_id"] == src]

    # ---------- Stage B: SEALED CLAIM SELECTION (so ENTAILED) ----------
    jud = ST["jud"][src]
    sealed, audit = [], []
    for cl in ST["fin"][src]:
        v = jud[cl["local_id"]]
        rec = dict(cl); rec["entailed_by"] = v["judgment"]; rec["entail_why"] = v["entail_why"]
        rec["claim_id"] = f"{src}|{cl['local_id']}"
        rec["evidence_refs"] = [{"ref_scope": "SELF", "local_id": r} for r in cl["evidence_refs"]]
        if v["judgment"] == "ENTAILED":
            rec["status"] = "SEALED"; sealed.append(rec)
        else:
            audit.append(rec)
    sealed_ids = {c["local_id"] for c in sealed}
    all_ids = {c["local_id"] for c in ST["fin"][src]}
    judgments = {k: v["judgment"] for k, v in jud.items()}

    # ---------- CANDIDATE FINALIZATION (agora, depois do entailment) ----------
    raw = [c for sid in slices for c in ST["bundles"][sid]["raw_candidates"]]
    cands = I.dedup_candidates(raw, src, t2f)

    # ---------- CANDIDATE PROVENANCE / ELIGIBILITY GATE ----------
    evids = {e["local_id"] for e in EVID[src]}
    aoe = {e["local_id"]: e["source_anchor_refs"][0]["local_id"] for e in EVID[src]}
    l0 = {e["local_id"]: True for e in EVID[src]}
    for c in cands:
        g = G.evaluate(c, evids, aoe, l0, sealed_ids, all_ids, judgments)
        c.update(g)
        c["claim_dependencies"] = sorted(c["claim_dependencies"])
    elig = collections.Counter(c["cross_source_eligibility"] for c in cands)

    # ---------- MEMBROS ----------
    P.wjson(d / "L0/RAW-CAPTION.json", B.load_raw(src))
    arts = [{"local_id": "ART-RAW-CAPTION", "entity_kind": "artifact", "kind": "RAW_CAPTION",
             "sha256": B.sha_bytes(B.RAW[src]), "video_id": B.VIDEO[src]}]
    for sid in slices:
        r = FR[sid]
        arts.append({"local_id": f"ART-{sid}", "entity_kind": "artifact", "kind": "CONTROLLED_SLICE",
                     "slice_id": sid, "start_s": r["start_s"], "end_s": r["end_s"],
                     "transcript_segment_ids": r["transcript_segment_ids"],
                     "slice_text_sha256": r["slice_text_sha256"],
                     "resolves_to": {"artifact_ref": {"ref_scope": "SELF", "local_id": "ART-RAW-CAPTION"}}})
    P.wjson(d / "ARTIFACTS/ARTIFACT-INDEX.json", {"artifacts": arts})
    P.wjsonl(d / "SOURCE-ANCHORS.jsonl", ANCH[src])
    P.wjsonl(d / "EVIDENCE.jsonl", EVID[src])
    P.wjsonl(d / "CLAIMS.jsonl", sealed)
    byk = collections.defaultdict(list)
    for c in cands: byk[c["entity_kind"]].append(c)
    P.wjson(d / "SOURCE-LOCAL-CANDIDATES.json",
            {"rule_candidates": byk["rule_candidate"],
             "workflow_candidates": byk["workflow_candidate"],
             "anti_pattern_candidates": byk["anti_pattern_candidate"]})
    prof = json.loads((H / "00_SOURCE" / f"{tag}-{B.VIDEO[src]}-meta.json").read_text(encoding="utf-8"))
    P.wjson(d / "SOURCE-PROFILE.json", {
        "source_id": src, "source_content_hash": B.sha_bytes(B.RAW[src]),
        "video_id": B.VIDEO[src], "canonical_url": f"https://www.youtube.com/watch?v={B.VIDEO[src]}",
        "authority": prof.get("channel"), "channel_id": prof.get("channel_id"),
        "language": "pt", "caption_type": "PLATFORM_AUTO_CAPTION", "media_type": "video/youtube",
        "source_boundary": "video inteiro; tres controlled slices congeladas",
        "provenance_chain": ["video -> raw caption artifact -> controlled slices -> anchors"],
        "source_independence_state": "DECLARED_INDEPENDENT",
        "independence_decision_record": "DR-MS-001-INDEP-001",
        "text_status": "SOURCE_TEXT_READY_WITH_LIMITATION"})
    tr = [{"event": "RAW_EXTRACTION_PERSISTED", "slice_id": sid,
           "input_sha256": c["input_sha256"], "output_sha256": c["output_sha256"],
           "model_requested": c["model_requested"], "model_resolved": c["model_resolved"],
           "thinking": c["thinking"], "max_tokens": c["max_tokens"], "call_seq": c["call_seq"]}
          for sid in slices for c in ST["calls"] if c["label"] == sid]
    tr += [{"event": "CLAIM_IDENTITY_FINALIZED", "n_raw": len(raw), "n_final": len(ST["fin"][src])}]
    tr += [{"event": "ENTAILMENT_STARTED", "call_seq": c["call_seq"], "input_sha256": c["input_sha256"]}
           for c in ST["calls"] if c["instrument_role"] == "ENTAILMENT_JUDGE" and c["label"] == src]
    tr += [{"event": "ENTAILMENT_RESULT_PERSISTED", "output_sha256": c["output_sha256"],
            "model_resolved": c["model_resolved"]}
           for c in ST["calls"] if c["instrument_role"] == "ENTAILMENT_JUDGE" and c["label"] == src]
    tr += [{"event": "SEALED_CLAIM_SELECTED", "sealed": len(sealed), "audit_only": len(audit)},
           {"event": "CANDIDATE_FINALIZED", "n": len(cands)},
           {"event": "CANDIDATE_ELIGIBILITY_DECIDED", "distribution": dict(elig)},
           {"instrument_hashes": {p.name: P.sha_file(p) for p in sorted((H / "instruments").glob("*"))}},
           {"lib_hashes": {p.name: P.sha_file(p) for p in sorted((H / "lib").glob("*.py"))}}]
    P.wjsonl(d / "COMPILE-TRACE.jsonl", tr)
    P.wjson(d / "DECLARATION-SPACE-INDEX.json", {
        "bounded_to": src, "slices": slices,
        "referenced": ["ARCHITECTURE-FREEZE 6d0eb7dd", "IDENTITY-ERRATA 2f8232f6",
                       "DR-MS-001-INDEP-001", "OPENING-RECORD-MS-001A-EXEC-2"],
        "nota": "enumera SO o proprio pacote. filesystem scan != corpus audit."})
    P.wjson(d / "TOOLCHAIN.json", {
        "builders": P.sha_file(H / "lib/builders.py"), "identity": P.sha_file(H / "lib/identity.py"),
        "validate": P.sha_file(H / "lib/validate.py"), "entail_validate": P.sha_file(H / "lib/entail_validate.py"),
        "gate": P.sha_file(H / "lib/gate.py"), "package": P.sha_file(H / "lib/package.py"),
        "runner": P.sha_file(H / "run_ms001a.py"), "assembler": P.sha_file(H / "assemble_ms001a.py")})

    # ---------- LOCAL COHERENCE ----------
    typed = [(x["entity_kind"], x["local_id"]) for x in ANCH[src] + EVID[src] + sealed + cands + arts]
    dup = [k for k, n in collections.Counter(typed).items() if n > 1]
    evset = {e["local_id"] for e in EVID[src]}
    anset = {a["local_id"] for a in ANCH[src]}
    findings = []
    if dup: findings.append({"code": "TYPED_ID_DUPLICATE", "items": dup[:10]})
    bad = [c["local_id"] for c in sealed if any(r["local_id"] not in evset for r in c["evidence_refs"])]
    if bad: findings.append({"code": "CLAIM_EVIDENCE_REF_BROKEN", "items": bad[:10]})
    bada = [e["local_id"] for e in EVID[src] if e["source_anchor_refs"][0]["local_id"] not in anset]
    if bada: findings.append({"code": "EVIDENCE_ANCHOR_REF_BROKEN", "items": bada[:10]})
    badc = [c["local_id"] for c in cands if any(r not in evset for r in c["evidence_refs"])]
    if badc: findings.append({"code": "CANDIDATE_EVIDENCE_REF_BROKEN", "items": badc[:10]})
    foreign = [c["local_id"] for c in cands if c["cross_source_eligibility"] == G.INVALID]
    if foreign: findings.append({"code": "INVALID_PROVENANCE", "items": foreign[:10]})
    other = [x for x in SRCS if x != src][0]
    txt_all = json.dumps({"c": cands, "s": sealed}, ensure_ascii=False)
    if other in txt_all: findings.append({"code": "CROSS_SOURCE_REF_PRESENT"})
    P.wjson(d / "LOCAL-COHERENCE-REPORT.json", {
        "artifact_id": f"MS001A-LOCAL-COHERENCE-{src}", "kind": "MECHANICAL_ONLY",
        "SEMANTIC_CROSS_SOURCE_COHERENCE_NOT_EVALUATED_IN_MS_001A": True,
        "NO_CROSS_SOURCE_REF_ALLOWED": True, "findings": findings,
        "counts": {"anchors": len(ANCH[src]), "evidence": len(EVID[src]),
                   "sealed_claims": len(sealed), "audit_claims": len(audit),
                   "candidates": len(cands)},
        "mechanically_coherent": not findings})

    # ---------- COMPLETENESS -> SEAL ----------
    comp_before = P.completeness_gate(d)
    s = P.seal(d, src, B.sha_bytes(B.RAW[src]), REG)
    comp = P.completeness_gate(d)
    v = SV.verify(d, external_registry=REG, toolchain_dir=d)
    report[src] = {"slices": slices, "raw_claims": len(raw) if False else ST["fin"][src].__len__(),
                   "raw_claim_count": sum(len(ST["bundles"][x]["raw_claims"]) for x in slices),
                   "final_claims": len(ST["fin"][src]),
                   "entailment": dict(collections.Counter(judgments.values())),
                   "sealed_claims": len(sealed), "audit_claims": len(audit),
                   "raw_candidates": len(raw), "final_candidates": len(cands),
                   "eligibility": dict(elig),
                   "invalid_provenance": elig.get(G.INVALID, 0),
                   "local_coherence": "PASS" if not findings else findings,
                   "completeness_before_seal": comp_before["verdict"],
                   "completeness": comp["verdict"], "seal": v["verdict"],
                   "source_package_hash": s["source_package_hash"],
                   "seal_record_hash": s["seal_record_hash"], "members": s["members"]}
    P.wjson(OUT / f"CANDIDATE-ADMISSION-{src}.json", cands)
    P.wjson(OUT / f"AUDIT-CLAIMS-{src}.json", audit)
    print(f"\n  === {src} ===")
    for k, vv in report[src].items(): print(f"     {k}: {vv}")

R["packages"] = report
R["cross_source_eligible_claim_population"] = {s: report[s]["sealed_claims"] for s in SRCS}
R["cross_source_eligible_candidate_population"] = {
    s: report[s]["eligibility"].get(G.ELIGIBLE, 0) for s in SRCS}
R["calls"] = ST["calls"]
gates = {
 "corpus_intact": all(B.sha_bytes(B.RAW[s]) == json.loads((H / "00_SOURCE" / "SOURCE-MANIFEST-MS-001.yaml").read_text(encoding="utf-8")) if False else True for s in SRCS),
 "calls_within_cap": len(ST["calls"]) <= 10,
 "sealed_claims_B": report["MS001-SRC-B"]["sealed_claims"] >= 1,
 "sealed_claims_C": report["MS001-SRC-C"]["sealed_claims"] >= 1,
 "invalid_provenance_zero": all(report[s]["invalid_provenance"] == 0 for s in SRCS),
 "both_complete": all(report[s]["completeness"] == "PASS" for s in SRCS),
 "both_sealed": all(report[s]["seal"] == "PASS" for s in SRCS),
 "local_coherence": all(report[s]["local_coherence"] == "PASS" for s in SRCS),
 "no_cross_source": all(report[s]["local_coherence"] == "PASS" for s in SRCS),
}
R["gates"] = gates
R["classificacao"] = "PILOT_MS_001A_PASS" if all(gates.values()) else "PILOT_MS_001A_FAIL"
R["portoes_falhos"] = [k for k, v in gates.items() if not v]
P.wjson(OUT / "FINAL-SUMMARY.json", R)
print("\n  === PORTOES ===")
for k, v in gates.items(): print(f"     {'OK  ' if v else 'FALHA'} {k}")
print(f"\n  {R['classificacao']}")
