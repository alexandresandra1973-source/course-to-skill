"""FUSION — IDENTITY REVERIFY. Consumo real com referencias TIPADAS.

Toda candidate_ref persistida carrega source_package_hash + entity_kind + local_id
DENTRO da propria ref (errata secao 5). Nunca a 2-tupla.

Regra central desta rodada: origem e destino sao objetos PERSISTIDOS DIFERENTES.
A origem e lida do Source Package selado; o destino e lido de volta do arquivo do
Fusion Package ja gravado em disco. Nunca duas referencias ao mesmo objeto em memoria.
"""
import json, hashlib, pathlib
import typedref as T

CONSUMPTION_VERSION = "identity-reverify-candidate-consumption-v1"
TRANSPORT_VERSION = "identity-reverify-workflow-transport-v1"


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def wjson(p, o):
    pathlib.Path(p).write_text(json.dumps(o, sort_keys=True, ensure_ascii=False, indent=1),
                               encoding="utf-8")


# ---------------------------------------------------------------- projecoes
# A projecao estrutural e a MESMA funcao aplicada aos dois lados. E o que torna a
# comparacao real: se a materializacao perder um step, mudar ordem, ou alterar um
# campo, os hashes divergem.

def rule_structure(r):
    return {"local_id": r.get("local_id"), "name": r.get("name"), "trigger": r.get("trigger"),
            "condition": r.get("condition"), "action": r.get("action"),
            "do_not": r.get("do_not") or [], "precedence": r.get("precedence"),
            "evidence_refs": r.get("evidence_refs") or [],
            "claim_refs": r.get("claim_refs") or []}


def step_structure(s):
    return {"local_id": s.get("local_id"), "order_key": s.get("order_key"),
            "name": s.get("name"), "action": s.get("action"),
            "required_inputs": s.get("required_inputs"),
            "missing_input_action": s.get("missing_input_action"),
            "iteration_limit": s.get("iteration_limit"), "autonomy": s.get("autonomy"),
            "evidence_refs": s.get("evidence_refs") or [],
            "claim_refs": s.get("claim_refs") or []}


def workflow_structure(w):
    return {"local_id": w.get("local_id"), "name": w.get("name"),
            "evidence_refs": w.get("evidence_refs") or [],
            "claim_refs": w.get("claim_refs") or [],
            "steps": [step_structure(s) for s in (w.get("steps") or [])]}


def anti_pattern_structure(a):
    return {"local_id": a.get("local_id"), "do_not": a.get("do_not") or [],
            "evidence_refs": a.get("evidence_refs") or [],
            "claim_refs": a.get("claim_refs") or []}


STRUCT = {"rule_candidates": rule_structure,
          "workflow_candidates": workflow_structure,
          "anti_pattern_candidates": anti_pattern_structure}

POP = {"rule_candidates": "rules",
       "workflow_candidates": "workflows",
       "anti_pattern_candidates": "anti_patterns"}


def materialize(cand_by_kind, admission, sph):
    """Constroi as populacoes da Fusion SOMENTE a partir de candidates ADMITIDOS."""
    adm = {r["local_id"]: r for r in admission if r["state"] == "ADMITTED"}
    out = {"rules": [], "workflows": [], "anti_patterns": []}
    for kind, pop in POP.items():
        for c in cand_by_kind.get(kind, []):
            lid = c.get("local_id")
            if lid not in adm or adm[lid]["kind"] != kind:
                continue
            st = STRUCT[kind](c)
            ek = T.CONTAINER_TO_KIND[kind]
            out[pop].append({
                "fusion_local_id": f"F-{pop.upper()[:2]}-{ek}-{lid}",
                "candidate_ref": T.tref(sph, ek, lid),
                "entity_kind": ek,
                "kind": kind,
                "structure": st,
                "inherited_defects": adm[lid]["inherited_defects"],
                "transformation": None,
                "adjudication": None,
            })
    return out


def fusion_id(source_package_hashes, fusion_config_hash, admission_report_hash,
              admitted_set_hash, outputs_hash, identity_errata_hash):
    """I26: mtx_policy_hash NAO entra. A Candidate Admission Policy entra, via
    FUSION-CONFIG, porque e configuracao estrutural da propria Fusion."""
    return sha_text(canon({
        "source_package_hashes": sorted(source_package_hashes),
        "fusion_config_hash": fusion_config_hash,
        "candidate_admission_report_hash": admission_report_hash,
        "admitted_candidate_set_hash": admitted_set_hash,
        "outputs_hash": outputs_hash,
        "identity_errata_hash": identity_errata_hash,
    }))
