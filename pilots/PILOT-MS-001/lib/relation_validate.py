"""MS-001B — validador do output do juiz de relacao. Zero modelo."""
import json
REL = ("IDENTICAL","CORROBORATES","SPECIALIZES","CONTRADICTS","SUPERSEDES","UNRELATED","INDETERMINATE")
DIR = ("NONE","LEFT_TO_RIGHT","RIGHT_TO_LEFT")
SCOPE = ("EQUIVALENT_SCOPE","NESTED_COMPATIBLE_SCOPE","DIFFERENT_SCOPE","AMBIGUOUS_SCOPE")
FIELDS = {"pair_id","relation","direction","scope_state","relation_why",
          "left_evidence_refs_checked","right_evidence_refs_checked"}
DIR_OK = {"IDENTICAL":{"NONE"},"CORROBORATES":{"NONE"},"CONTRADICTS":{"NONE"},
          "UNRELATED":{"NONE"},"INDETERMINATE":{"NONE"},
          "SPECIALIZES":{"LEFT_TO_RIGHT","RIGHT_TO_LEFT"},
          "SUPERSEDES":{"LEFT_TO_RIGHT","RIGHT_TO_LEFT"}}
SCOPE_OK = {"IDENTICAL":{"EQUIVALENT_SCOPE"},
            "SPECIALIZES":{"NESTED_COMPATIBLE_SCOPE","EQUIVALENT_SCOPE"},
            "CONTRADICTS":{"EQUIVALENT_SCOPE","NESTED_COMPATIBLE_SCOPE"}}
FORBIDDEN = {"precedence","winner","mtx_policy","mtx_policy_hash","authority","governance_state"}


def validate(txt, batch_id, sent):
    """sent: {pair_id: {"left": set(EV), "right": set(EV)}}"""
    E = []
    try:
        d = json.loads(txt)
    except Exception:
        return None, ["R01_JSON_UNPARSEABLE"]
    if not isinstance(d, dict) or set(d) - {"batch_id","judgments"} or "judgments" not in d:
        return None, ["R02_SCHEMA_VIOLATION"]
    if d.get("batch_id") != batch_id: E.append("R03_BATCH_ID_MISMATCH")
    if not isinstance(d["judgments"], list) or not d["judgments"]:
        return None, ["R02_SCHEMA_VIOLATION"]
    seen = []
    for v in d["judgments"]:
        if not isinstance(v, dict): E.append("R02_SCHEMA_VIOLATION"); continue
        k = set(v)
        if k & FORBIDDEN: E.append("R12_FORBIDDEN_FIELD")
        if k - FIELDS: E.append("R04_EXTRA_FIELD")
        if FIELDS - k: E.append("R02_SCHEMA_VIOLATION"); continue
        pid = v["pair_id"]
        if pid not in sent: E.append("R05_UNKNOWN_PAIR"); continue
        if pid in seen: E.append("R06_DUPLICATE_PAIR")
        seen.append(pid)
        r, dr, sc = v["relation"], v["direction"], v["scope_state"]
        if r not in REL: E.append("R07_INVALID_RELATION"); continue
        if dr not in DIR: E.append("R08_INVALID_DIRECTION")
        elif dr not in DIR_OK[r]: E.append("R09_DIRECTION_INCOMPATIBLE")
        if sc not in SCOPE: E.append("R10_INVALID_SCOPE")
        elif r in SCOPE_OK and sc not in SCOPE_OK[r]: E.append("R11_SCOPE_INCOMPATIBLE")
        if not isinstance(v["relation_why"], str) or len(v["relation_why"]) < 15:
            E.append("R02_SCHEMA_VIOLATION")
        for side, key in (("left","left_evidence_refs_checked"), ("right","right_evidence_refs_checked")):
            got = set(v[key] or [])
            want = sent[pid][side]
            if not got: E.append("R02_SCHEMA_VIOLATION"); continue
            if got - want: E.append(f"R13_EVIDENCE_ADDED_{side.upper()}")
            if want - got: E.append(f"R14_EVIDENCE_OMITTED_{side.upper()}")
    if set(sent) - set(seen): E.append("R15_PAIR_MISSING")
    return (d if not E else None), sorted(set(E))
