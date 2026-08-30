"""MS-001 — IDENTIDADE E DEDUP. ID-DERIVATION-v3: IDENTITY != PROVENANCE.
Mecanico, offline, zero modelo."""
import json, hashlib, re, unicodedata, collections

QUALIFIER_KEYS = ("scope", "condition", "platform", "stage", "audience")
KIND_PREFIX = {"claim": "CL", "rule_candidate": "R", "workflow_candidate": "WF",
               "anti_pattern_candidate": "AP", "workflow_step": "S"}
# listas cuja ORDEM NAO e semantica -> ordenadas na identidade
UNORDERED = ("do_not", "exceptions", "prerequisites", "required_inputs", "conditions")


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def norm(t):
    """NFC -> casefold -> colapsa whitespace -> remove pontuacao periferica.
    Preserva estrutura interna: numeros, hifens internos, siglas."""
    if t is None:
        return None
    t = unicodedata.normalize("NFC", str(t)).casefold()
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"^[\s\.,;:!?\"'()\[\]]+|[\s\.,;:!?\"'()\[\]]+$", "", t)


def qualifiers_canon(q):
    q = q or {}
    return {k: norm(q.get(k)) for k in QUALIFIER_KEYS}


# ---------------------------------------------------------------- CLAIM
def claim_semantic_key(source_id, text, source_language, qualifiers):
    """NAO contem evidence_refs, entailment, ordem de emissao, slice nem status."""
    return sha(canon({"source_id": source_id, "normalized_text": norm(text),
                      "source_language": source_language,
                      "qualifiers": qualifiers_canon(qualifiers)}))


# ------------------------------------------------------------ CANDIDATE
def _nl(v):
    return [norm(x) for x in (v or [])]


def structure_canon(kind, s):
    """SOMENTE campos operacionais. precedence ENTRA (muda o que a regra diz).
    defects NAO entram (sao anotacao/medicao)."""
    if kind == "rule_candidate":
        return {"name": norm(s.get("name")), "trigger": norm(s.get("trigger")),
                "condition": norm(s.get("condition")), "action": norm(s.get("action")),
                "do_not": sorted(_nl(s.get("do_not"))),
                "precedence": norm(s.get("precedence")),
                "exceptions": sorted(_nl(s.get("exceptions"))),
                "prerequisites": sorted(_nl(s.get("prerequisites")))}
    if kind == "workflow_candidate":
        steps = sorted(s.get("steps") or [], key=lambda x: x.get("order_key", 0))
        return {"name": norm(s.get("name")),
                "steps": [{"order_key": st.get("order_key"), "name": norm(st.get("name")),
                           "action": norm(st.get("action")),
                           "required_inputs": sorted(_nl(st.get("required_inputs"))),
                           "missing_input_action": norm(st.get("missing_input_action"))}
                          for st in steps],           # ORDEM PRESERVADA: e semantica
                "exceptions": sorted(_nl(s.get("exceptions"))),
                "prerequisites": sorted(_nl(s.get("prerequisites")))}
    if kind == "anti_pattern_candidate":
        return {"do_not": sorted(_nl(s.get("do_not"))), "why": norm(s.get("why")),
                "conditions": sorted(_nl(s.get("conditions")))}
    raise ValueError(f"entity_kind desconhecido: {kind!r}")


def candidate_structural_key(source_id, entity_kind, structure):
    """NAO contem evidence_refs, claim refs, eligibility, verdict, merged_from, defects."""
    return sha(canon({"source_id": source_id, "entity_kind": entity_kind,
                      "structure": structure_canon(entity_kind, structure)}))


# ------------------------------------------------------- DEDUP + ID FINAL
def dedup_claims(raw, source_id):
    """DEDUP ANTES do id final. Uniao de evidence_refs. merged_from preservado."""
    g = collections.OrderedDict()
    for r in raw:
        k = claim_semantic_key(source_id, r["text"], r["source_language"], r.get("qualifiers"))
        if k not in g:
            g[k] = {"semantic_key": k, "text": r["text"],
                    "source_language": r["source_language"],
                    "qualifiers": r.get("qualifiers") or {},
                    "evidence_refs": set(), "merged_from": [], "status_raw": set()}
        g[k]["evidence_refs"] |= set(r["evidence_refs"])
        g[k]["merged_from"].append({"slice_id": r["_slice_id"],
                                    "temporary_claim_id": r["temporary_claim_id"]})
        g[k]["status_raw"].add(r.get("status", ""))
    out = []
    for i, k in enumerate(sorted(g), 1):
        c = g[k]
        out.append({"local_id": f"CL-{i:04d}", "entity_kind": "claim",
                    "semantic_key": k, "text": c["text"],
                    "source_language": c["source_language"], "qualifiers": c["qualifiers"],
                    "evidence_refs": sorted(c["evidence_refs"]),
                    "merged_from": sorted(c["merged_from"],
                                          key=lambda x: (x["slice_id"], x["temporary_claim_id"])),
                    "status_raw": sorted(x for x in c["status_raw"] if x)})
    return out


def dedup_candidates(raw, source_id, temp2final):
    """Mesma disciplina. claim_temp_refs mapeadas para final ids ANTES da uniao."""
    g = collections.OrderedDict()
    for r in raw:
        kind = r["entity_kind"]
        k = candidate_structural_key(source_id, kind, r["structure"])
        gk = (kind, k)
        if gk not in g:
            g[gk] = {"structural_key": k, "entity_kind": kind, "structure": r["structure"],
                     "evidence_refs": set(), "claim_deps": set(), "defects": set(),
                     "merged_from": [], "applicability": set()}
        e = g[gk]
        e["evidence_refs"] |= set(r["evidence_refs"])
        e["defects"] |= set(r.get("defects") or [])
        e["applicability"].add(r.get("claim_refs_applicability")
                               or ("APPLICABLE" if r.get("claim_temp_refs") else "NOT_APPLICABLE"))
        for t in (r.get("claim_temp_refs") or []):
            e["claim_deps"].add(temp2final[(r["_slice_id"], t)])
        e["merged_from"].append({"slice_id": r["_slice_id"],
                                 "temporary_candidate_id": r["temporary_candidate_id"]})
    out = []
    ctr = collections.Counter()
    for kind, k in sorted(g, key=lambda x: (x[0], x[1])):
        e = g[(kind, k)]
        ctr[kind] += 1
        app = "APPLICABLE" if "APPLICABLE" in e["applicability"] else "NOT_APPLICABLE"
        st = e["structure"]
        if kind == "workflow_candidate":
            st = dict(st)
            st["steps"] = [dict(x, local_id=f"S-{j:04d}") for j, x in
                           enumerate(sorted(st["steps"], key=lambda y: y["order_key"]), 1)]
        out.append({"local_id": f"{KIND_PREFIX[kind]}-{ctr[kind]:04d}", "entity_kind": kind,
                    "structural_key": k, "structure": st,
                    "evidence_refs": sorted(e["evidence_refs"]),
                    "claim_refs_applicability": app,
                    "claim_dependencies": sorted(e["claim_deps"]),
                    "defects": sorted(e["defects"]),
                    "merged_from": sorted(e["merged_from"],
                                          key=lambda x: (x["slice_id"], x["temporary_candidate_id"]))})
    return out
