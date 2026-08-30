"""MS-001 — validacao mecanica dos outputs de modelo. Zero modelo.
Codigos de erro estaveis. Resposta invalida NUNCA e consertada a mao."""
import json, re

KINDS = ("rule_candidate", "workflow_candidate", "anti_pattern_candidate")
QK = ("scope", "condition", "platform", "stage", "audience")
CLAIM_REQ = ("temporary_claim_id", "text", "source_language", "evidence_refs",
             "qualifiers", "status")
CAND_REQ = ("temporary_candidate_id", "entity_kind", "evidence_refs",
            "claim_temp_refs", "structure", "defects")
STRUCT_REQ = {"rule_candidate": ("name", "trigger", "condition", "action", "do_not", "precedence"),
              "workflow_candidate": ("name", "steps"),
              "anti_pattern_candidate": ("do_not", "why")}
STRUCT_OPT = {"rule_candidate": ("exceptions", "prerequisites"),
              "workflow_candidate": ("exceptions", "prerequisites"),
              "anti_pattern_candidate": ("conditions",)}
STEP_REQ = ("order_key", "name", "action", "evidence_refs")
STEP_OPT = ("required_inputs", "missing_input_action")
DEFECTS = ("PRECEDENCE_UNDEFINED", "PASSO_UNICO", "SCOPE_UNSTATED")


def validate_extraction(txt, source_id, slice_id, catalog_ids):
    """Devolve (bundle|None, [codigos]). Lista vazia = valido."""
    E = []
    try:
        d = json.loads(txt)
    except Exception:
        return None, ["E01_JSON_UNPARSEABLE"]
    if not isinstance(d, dict):
        return None, ["E02_SCHEMA_VIOLATION"]
    if set(d) - {"source_id", "slice_id", "raw_claims", "raw_candidates"}:
        E.append("E03_UNKNOWN_FIELD")
    for k in ("source_id", "slice_id", "raw_claims", "raw_candidates"):
        if k not in d:
            E.append("E02_SCHEMA_VIOLATION")
    if E:
        return None, sorted(set(E))
    if d["source_id"] != source_id: E.append("E15_SOURCE_ID_MISMATCH")
    if d["slice_id"] != slice_id:   E.append("E16_SLICE_ID_MISMATCH")

    tids, xids = set(), set()
    for c in d["raw_claims"]:
        if set(c) - set(CLAIM_REQ): E.append("E03_UNKNOWN_FIELD")
        if any(k not in c for k in CLAIM_REQ): E.append("E02_SCHEMA_VIOLATION"); continue
        if not re.fullmatch(r"TC-\d{3}", c["temporary_claim_id"]): E.append("E02_SCHEMA_VIOLATION")
        if c["temporary_claim_id"] in tids: E.append("E11_DUPLICATE_TEMP_ID")
        tids.add(c["temporary_claim_id"])
        if not isinstance(c["evidence_refs"], list) or not c["evidence_refs"]:
            E.append("E05_EMPTY_EVIDENCE_REFS")
        for r in c["evidence_refs"] or []:
            if not re.fullmatch(r"EV-\d{4}", str(r)): E.append("E02_SCHEMA_VIOLATION")
            elif r not in catalog_ids: E.append("E06_EVIDENCE_REF_NOT_IN_CATALOG")
        if not isinstance(c.get("qualifiers"), dict) or set(c["qualifiers"]) - set(QK):
            E.append("E02_SCHEMA_VIOLATION")
        if c.get("status") not in ("SOURCE_EXPLICIT", "SOURCE_IMPLIED"):
            E.append("E02_SCHEMA_VIOLATION")
        if c.get("source_language") != "pt": E.append("E02_SCHEMA_VIOLATION")

    for c in d["raw_candidates"]:
        extra = set(c) - set(CAND_REQ) - {"claim_refs_applicability"}
        if extra: E.append("E03_UNKNOWN_FIELD")
        if any(k not in c for k in CAND_REQ): E.append("E02_SCHEMA_VIOLATION"); continue
        k = c["entity_kind"]
        if k not in KINDS: E.append("E04_UNKNOWN_ENTITY_KIND"); continue
        if not re.fullmatch(r"TX-\d{3}", c["temporary_candidate_id"]): E.append("E02_SCHEMA_VIOLATION")
        if c["temporary_candidate_id"] in xids: E.append("E11_DUPLICATE_TEMP_ID")
        xids.add(c["temporary_candidate_id"])
        if not c["evidence_refs"]: E.append("E05_EMPTY_EVIDENCE_REFS")
        for r in c["evidence_refs"] or []:
            if not re.fullmatch(r"EV-\d{4}", str(r)): E.append("E02_SCHEMA_VIOLATION")
            elif r not in catalog_ids: E.append("E06_EVIDENCE_REF_NOT_IN_CATALOG")
        for t in c["claim_temp_refs"] or []:
            if t not in tids: E.append("E10_CLAIM_TEMP_REF_UNRESOLVED")
        if not c["claim_temp_refs"] and "claim_refs_applicability" not in c:
            E.append("E18_CLAIM_REFS_APPLICABILITY_MISSING")
        for dd in c.get("defects") or []:
            if dd not in DEFECTS: E.append("E02_SCHEMA_VIOLATION")
        s = c["structure"]
        if not isinstance(s, dict): E.append("E17_STRUCTURE_KIND_MISMATCH"); continue
        if any(f not in s for f in STRUCT_REQ[k]): E.append("E17_STRUCTURE_KIND_MISMATCH")
        if set(s) - set(STRUCT_REQ[k]) - set(STRUCT_OPT[k]): E.append("E03_UNKNOWN_FIELD")
        if k == "workflow_candidate":
            st = s.get("steps")
            if not isinstance(st, list) or not st:
                E.append("E12_WORKFLOW_NO_STEPS")
            else:
                ks = [x.get("order_key") for x in st]
                if any(x is None for x in ks) or len(set(ks)) != len(ks) or ks != sorted(ks):
                    E.append("E13_WORKFLOW_ORDER_INVALID")
                for x in st:
                    if any(f not in x for f in STEP_REQ): E.append("E02_SCHEMA_VIOLATION")
                    if set(x) - set(STEP_REQ) - set(STEP_OPT): E.append("E03_UNKNOWN_FIELD")
                    if not x.get("evidence_refs"): E.append("E05_EMPTY_EVIDENCE_REFS")
                    for r in x.get("evidence_refs") or []:
                        if r not in catalog_ids: E.append("E06_EVIDENCE_REF_NOT_IN_CATALOG")
    return (d if not E else None), sorted(set(E))


def validate_entailment(txt, source_id, claim_refs_map):
    """claim_refs_map: {claim_id: set(evidence_refs declaradas)}."""
    E = []
    try:
        d = json.loads(txt)
    except Exception:
        return None, ["E01_JSON_UNPARSEABLE"]
    if not isinstance(d, dict) or set(d) - {"source_id", "verdicts"} or "verdicts" not in d:
        return None, ["E22_JUDGE_SCHEMA_VIOLATION"]
    if d.get("source_id") != source_id: E.append("E15_SOURCE_ID_MISMATCH")
    seen = set()
    for v in d["verdicts"]:
        if set(v) - {"claim_id", "judgment", "entail_why", "evidence_refs_checked"}:
            E.append("E22_JUDGE_SCHEMA_VIOLATION"); continue
        cid = v.get("claim_id")
        if cid not in claim_refs_map: E.append("E21_UNKNOWN_CLAIM_ID"); continue
        seen.add(cid)
        if v.get("judgment") not in ("ENTAILED", "NOT_ENTAILED", "INDETERMINATE"):
            E.append("E22_JUDGE_SCHEMA_VIOLATION")
        if not isinstance(v.get("entail_why"), str) or len(v["entail_why"]) < 10:
            E.append("E22_JUDGE_SCHEMA_VIOLATION")
        chk = set(v.get("evidence_refs_checked") or [])
        if not chk: E.append("E22_JUDGE_SCHEMA_VIOLATION")
        if chk - claim_refs_map[cid]: E.append("E19_JUDGE_ADDED_EVIDENCE")
    if set(claim_refs_map) - seen: E.append("E20_JUDGMENT_MISSING")
    return (d if not E else None), sorted(set(E))
