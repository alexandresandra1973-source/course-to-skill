"""CANDIDATE ADMISSION POLICY v0.2 — implementacao mecanica, offline, zero modelo.

DIFERENCA UNICA E NORMATIVA contra a v0.1: a unicidade de local_id passa a ser
verificada por (entity_kind, local_id) DENTRO do package, e nao package-wide.
Tudo o mais e semanticamente equivalente. Nenhuma regra nova de qualidade.

Predicados de rejeicao sao EXAUSTIVOS e vem da policy pre-declarada. Nada aqui
rejeita por PRECEDENCE_UNDEFINED, por PASSO_UNICO ou por evidence_refs vazio.
"""
import json, hashlib
import typedref as T

POLICY_VERSION = "v0.2"

REQUIRED = {
    "rule_candidates":         ["local_id", "name", "trigger", "condition", "action"],
    "workflow_candidates":     ["local_id", "name", "steps"],
    "anti_pattern_candidates": ["local_id", "do_not"],
}
REQUIRED_STEP = ["local_id", "order_key", "action"]

REJECTION_PREDICATES = ["LOCAL_ID_INVALIDO", "REQUIRED_FIELD_AUSENTE", "WORKFLOW_SEM_PASSOS",
                        "ORDEM_INVALIDA", "EVIDENCE_REF_QUEBRADA", "CLAIM_REF_QUEBRADA"]


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def struct_hash(o):
    return sha_text(canon(o))


def _refs(x):
    """Extrai os local_id de uma lista de refs que pode ser [str] ou [{local_id:...}]."""
    out = []
    for r in (x or []):
        out.append(r if isinstance(r, str) else r.get("local_id"))
    return out


def _ev_check(obj, ev_ids):
    """EV-RESOLVABILITY: toda ref PRESENTE tem de resolver. Vazio satisfaz vacuamente."""
    got = _refs(obj.get("evidence_refs"))
    broken = [r for r in got if r not in ev_ids]
    return {"refs": got, "n": len(got), "broken": broken,
            "resolvable": not broken,
            "empty": len(got) == 0}


def _claim_check(obj, claim_ids):
    """CLAIM-RESOLVABILITY. Campo ausente => NOT_APPLICABLE, nunca PASS silencioso."""
    if "claim_refs" not in obj:
        return {"state": "NOT_APPLICABLE", "refs": [], "broken": [], "resolvable": True}
    got = _refs(obj.get("claim_refs"))
    broken = [r for r in got if r not in claim_ids]
    return {"state": "PRESENT", "refs": got, "broken": broken, "resolvable": not broken}


def admit_one(kind, c, ev_ids, claim_ids, seen_ids):
    """Retorna o registro de admissao de UM candidate. Mecanico e total."""
    reasons, defects = [], []

    lid = c.get("local_id")
    # v0.2: a colisao so e defeito DENTRO do mesmo entity_kind
    if not isinstance(lid, str) or not lid.strip() or (kind, lid) in seen_ids:
        reasons.append("LOCAL_ID_INVALIDO")

    for f in REQUIRED[kind]:
        v = c.get(f)
        if f not in c or v is None or (isinstance(v, (str, list)) and len(v) == 0):
            reasons.append("REQUIRED_FIELD_AUSENTE")
            break

    if kind == "workflow_candidates":
        steps = c.get("steps") or []
        if not steps:
            reasons.append("WORKFLOW_SEM_PASSOS")
        else:
            ks = [s.get("order_key") for s in steps]
            if any(k is None for k in ks) or len(set(ks)) != len(ks) or ks != sorted(ks):
                reasons.append("ORDEM_INVALIDA")
            for s in steps:
                if any(f not in s or s.get(f) in (None, "") for f in REQUIRED_STEP):
                    reasons.append("REQUIRED_FIELD_AUSENTE")
                    break
            if len(steps) == 1:
                defects.append("PASSO_UNICO")

    if kind == "rule_candidates" and c.get("precedence") in (None, "UNDEFINED"):
        defects.append("PRECEDENCE_UNDEFINED")

    ev = _ev_check(c, ev_ids)
    if not ev["resolvable"]:
        reasons.append("EVIDENCE_REF_QUEBRADA")
    if ev["empty"]:
        defects.append("EVIDENCE_REFS_EMPTY_INHERITED_FROM_R3_PACKAGING")

    for s in (c.get("steps") or []):
        sev = _ev_check(s, ev_ids)
        if not sev["resolvable"] and "EVIDENCE_REF_QUEBRADA" not in reasons:
            reasons.append("EVIDENCE_REF_QUEBRADA")

    cr = _claim_check(c, claim_ids)
    if not cr["resolvable"]:
        reasons.append("CLAIM_REF_QUEBRADA")

    reasons = sorted(set(reasons))
    return {
        "local_id": lid, "kind": kind,
        "state": "REJECTED_STRUCTURAL" if reasons else "ADMITTED",
        "reasons": reasons,
        "inherited_defects": sorted(set(defects)),
        "evidence_validation": {"n_refs": ev["n"], "broken": ev["broken"],
                                "resolvable": ev["resolvable"], "empty": ev["empty"]},
        "claim_validation": cr,
    }


def admit_package(cand, ev_ids, claim_ids, source_package_hash):
    """Aplica a policy a um Source Package inteiro. Nunca escreve no pacote."""
    recs, seen = [], set()
    for kind in ("rule_candidates", "workflow_candidates", "anti_pattern_candidates"):
        for c in cand.get(kind, []):
            r = admit_one(kind, c, ev_ids, claim_ids, seen)
            if isinstance(c.get("local_id"), str):
                seen.add((kind, c["local_id"]))
            # v0.2: ref TIPADA, que resolve sozinha (errata secao 5)
            r["entity_kind"] = T.CONTAINER_TO_KIND[kind]
            r["qualified_ref"] = T.tref(source_package_hash, r["entity_kind"], r["local_id"])
            r["source_package_hash"] = source_package_hash
            recs.append(r)
    return recs
