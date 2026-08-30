"""MS-001 — CANDIDATE PROVENANCE / ELIGIBILITY GATE. Zero modelo.
PROVENANCE-STATES-v2: vazio nunca chega aqui pelo caminho valido; se chegar
(injecao direta), e NOT_ELIGIBLE + UNREACHABLE_FROM_VALID_MS001A_EXTRACTOR_OUTPUT."""

ELIGIBLE = "ELIGIBLE_FOR_CROSS_SOURCE_DECISION"
NOT_ELIGIBLE = "NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION"
INVALID = "INVALID_PROVENANCE"
UNREACHABLE = "UNREACHABLE_FROM_VALID_MS001A_EXTRACTOR_OUTPUT"


def evaluate(cand, evidence_ids, anchor_of_evidence, l0_reachable, sealed_claim_ids,
             all_final_claim_ids, judgments):
    """judgments: {final_claim_id: ENTAILED|NOT_ENTAILED|INDETERMINATE}"""
    marks = []
    refs = cand.get("evidence_refs") or []

    # --- defense in depth: vazio injetado direto no gate
    if not refs:
        return {"cross_source_eligibility": NOT_ELIGIBLE, "markers": [UNREACHABLE],
                "claim_dependency_status": "NOT_APPLICABLE",
                "sealed_claim_refs": [], "unsealed_claim_dependencies": [],
                "provenance_detail": {"reason": "EMPTY_EVIDENCE_REFS_AT_GATE"}}

    # --- defeito estrutural real
    broken = [r for r in refs if r not in evidence_ids]
    if broken:
        return {"cross_source_eligibility": INVALID, "markers": ["EVIDENCE_REF_UNRESOLVED"],
                "claim_dependency_status": "NOT_APPLICABLE",
                "sealed_claim_refs": [], "unsealed_claim_dependencies": [],
                "provenance_detail": {"broken_evidence_refs": broken}}
    no_anchor = [r for r in refs if not anchor_of_evidence.get(r)]
    if no_anchor:
        return {"cross_source_eligibility": INVALID, "markers": ["EVIDENCE_WITHOUT_ANCHOR"],
                "claim_dependency_status": "NOT_APPLICABLE",
                "sealed_claim_refs": [], "unsealed_claim_dependencies": [],
                "provenance_detail": {"evidence_without_anchor": no_anchor}}
    no_l0 = [r for r in refs if not l0_reachable.get(r)]
    if no_l0:
        return {"cross_source_eligibility": INVALID, "markers": ["ANCHOR_NOT_REACHING_L0"],
                "claim_dependency_status": "NOT_APPLICABLE",
                "sealed_claim_refs": [], "unsealed_claim_dependencies": [],
                "provenance_detail": {"anchor_not_reaching_l0": no_l0}}

    deps = cand.get("claim_dependencies") or []
    app = cand.get("claim_refs_applicability", "NOT_APPLICABLE")

    unknown = [d for d in deps if d not in all_final_claim_ids]
    if unknown:
        return {"cross_source_eligibility": INVALID, "markers": ["CLAIM_REF_UNRESOLVED"],
                "claim_dependency_status": "NOT_APPLICABLE",
                "sealed_claim_refs": [], "unsealed_claim_dependencies": [],
                "provenance_detail": {"unresolved_claim_refs": unknown}}

    if app == "NOT_APPLICABLE" or not deps:
        return {"cross_source_eligibility": ELIGIBLE, "markers": marks,
                "claim_dependency_status": "NOT_APPLICABLE",
                "sealed_claim_refs": [], "unsealed_claim_dependencies": [],
                "provenance_detail": {"direct_evidence_ok": True}}

    sealed = [d for d in deps if d in sealed_claim_ids]
    unsealed = [{"final_claim_id": d, "judgment": judgments.get(d, "UNKNOWN")}
                for d in deps if d not in sealed_claim_ids]
    if unsealed:
        return {"cross_source_eligibility": NOT_ELIGIBLE,
                "markers": ["CLAIM_DEPENDENCY_NOT_SEALED"],
                "claim_dependency_status": "UNSATISFIED_BY_ENTAILMENT",
                "sealed_claim_refs": sorted(sealed),
                "unsealed_claim_dependencies": sorted(unsealed, key=lambda x: x["final_claim_id"]),
                "provenance_detail": {"direct_evidence_ok": True}}
    return {"cross_source_eligibility": ELIGIBLE, "markers": marks,
            "claim_dependency_status": "SATISFIED",
            "sealed_claim_refs": sorted(sealed), "unsealed_claim_dependencies": [],
            "provenance_detail": {"direct_evidence_ok": True}}
