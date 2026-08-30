"""TYPED REFERENCE SCHEMA v1 — a errata de identidade, em codigo.

GLOBAL_OBJECT_IDENTITY = (source_package_hash, entity_kind, local_id)
A referencia resolve SOZINHA. Nao depende de prefixo lexical, campo irmao,
conhecimento externo nem heuristica do consumidor.
"""
SCHEMA_VERSION = "typed-ref-v1"

# entity_kind CANONICO (errata secao 2). A esquerda, a chave do container JSON.
CONTAINER_TO_KIND = {
    "rule_candidates":         "rule_candidate",
    "workflow_candidates":     "workflow_candidate",
    "anti_pattern_candidates": "anti_pattern_candidate",
}
CANONICAL_KINDS = ("artifact", "source_anchor", "evidence", "claim", "rule_candidate",
                   "workflow_candidate", "workflow_step", "anti_pattern_candidate")

# campos cujo kind de destino e determinado pelo schema (errata secao 4)
SCHEMA_IMPLIED = {
    "claim.evidence_refs":        "evidence",
    "evidence.anchor_ref":        "source_anchor",
    "source_anchor.artifact_ref": "artifact",
}


def tref(source_package_hash, entity_kind, local_id):
    """Constroi uma referencia tipada. Recusa kind nao canonico."""
    if entity_kind not in CANONICAL_KINDS:
        raise ValueError(f"entity_kind nao canonico: {entity_kind!r}")
    return {"source_package_hash": source_package_hash,
            "entity_kind": entity_kind, "local_id": local_id}


def is_typed(ref):
    return (isinstance(ref, dict)
            and {"source_package_hash", "entity_kind", "local_id"} <= set(ref)
            and ref.get("entity_kind") in CANONICAL_KINDS)


def resolve(ref, index):
    """index: {(sph, entity_kind, local_id): objeto}. Retorna estado + alvos."""
    if not is_typed(ref):
        return {"state": "INVALID_REF", "n": 0, "targets": []}
    key = (ref["source_package_hash"], ref["entity_kind"], ref["local_id"])
    hit = [k for k in index if k == key]
    return {"state": "RESOLVED" if len(hit) == 1 else
            ("UNRESOLVED" if not hit else "AMBIGUOUS_REF"),
            "n": len(hit), "targets": hit}


def resolve_untyped(sph, local_id, index):
    """A forma congelada ANTIGA. Existe so para o canario ID4 demonstrar a ambiguidade."""
    hit = [k for k in index if k[0] == sph and k[2] == local_id]
    return {"state": "RESOLVED" if len(hit) == 1 else
            ("UNRESOLVED" if not hit else "AMBIGUOUS_REF"),
            "n": len(hit), "targets": hit}


def resolve_self(field_path, ref, index, sph):
    """SELF ref: valida sem entity_kind SOMENTE com kind schema-implied."""
    if "entity_kind" in ref:
        k = ref["entity_kind"]
        if k not in CANONICAL_KINDS:
            return {"state": "INVALID_REF", "why": "entity_kind nao canonico"}
    elif field_path in SCHEMA_IMPLIED:
        k = SCHEMA_IMPLIED[field_path]
    else:
        return {"state": "INVALID_REF",
                "why": "SELF generica: schema nao determina o kind do alvo e entity_kind ausente"}
    r = resolve(tref(sph, k, ref["local_id"]), index)
    r["entity_kind_source"] = "explicit" if "entity_kind" in ref else "schema-implied"
    r["entity_kind"] = k
    return r
