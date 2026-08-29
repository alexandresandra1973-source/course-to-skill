"""Montagem MECÂNICA. Zero chamadas de modelo — e é essa a garantia.

Ordem dos passos: por `min(start_s)` das evidências citadas. Um curso é linear;
a ordem em que ensina é a ordem das marcas. Qualquer reordenação seria
conhecimento do modelo entrando pela porta dos fundos.

Dedup: condição+ação normalizadas IDÊNTICAS. Nunca similaridade.

Workflows: existem só se alguma evidência os NOMEAR como procedimento
(âncora). Passos ligam-se à âncora anterior mais próxima em ordem temporal.
Sem âncora, caem num workflow padrão DECLARADO.
"""
from __future__ import annotations
import re

DEFAULT_WORKFLOW = "WF-DEFAULT"


def norm(s: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", (s or "").lower()).split())


def order_key(entity: dict, span_by_evidence: dict) -> int:
    spans = [span_by_evidence[e][0] for e in entity.get("evidence_ids", [])
             if e in span_by_evidence]
    return min(spans) if spans else 10**9


def dedup(entities: list[dict], keyfields: tuple[str, ...]) -> tuple[list, list]:
    seen, kept, merged = {}, [], []
    for e in entities:
        k = tuple(norm(str(e.get(f, ""))) for f in keyfields)
        if k in seen:
            tgt = seen[k]
            tgt["evidence_ids"] = sorted(set(tgt["evidence_ids"]) | set(e["evidence_ids"]))
            tgt["segment_ids"] = sorted(set(tgt.get("segment_ids", [])) |
                                        set(e.get("segment_ids", [])))
            merged.append({"kept": tgt.get("rule_id") or tgt.get("step_id"),
                           "dropped": e.get("rule_id") or e.get("step_id"),
                           "rule": "IDENTICAL_NORMALIZED"})
        else:
            seen[k] = e
            kept.append(e)
    return kept, merged


def assign_workflows(steps: list[dict], anchors: list[dict],
                     span_by_evidence: dict) -> tuple[list[dict], dict]:
    """Âncora = evidência que NOMEIA um procedimento. Ligação por ordem temporal."""
    anc = sorted(anchors, key=lambda a: span_by_evidence.get(a["anchor_evidence_id"],
                                                             (10**9,))[0])
    for s in steps:
        s["order_key"] = order_key(s, span_by_evidence)
    steps.sort(key=lambda s: s["order_key"])
    used = {}
    for s in steps:
        prev = [a for a in anc
                if span_by_evidence.get(a["anchor_evidence_id"], (10**9,))[0] <= s["order_key"]]
        wid = prev[-1]["workflow_id"] if prev else DEFAULT_WORKFLOW
        s["workflow_id"] = wid
        used.setdefault(wid, []).append(s["step_id"])
    wfs = []
    for a in anc:
        if a["workflow_id"] in used:
            wfs.append({"workflow_id": a["workflow_id"], "name": a["name"],
                        "anchor_evidence_id": a["anchor_evidence_id"],
                        "steps": used[a["workflow_id"]],
                        "evidence_ids": [a["anchor_evidence_id"]]})
    if DEFAULT_WORKFLOW in used:
        wfs.append({"workflow_id": DEFAULT_WORKFLOW,
                    "name": "Passos sem âncora de procedimento na fonte",
                    "anchor_evidence_id": None,
                    "steps": used[DEFAULT_WORKFLOW], "evidence_ids": [],
                    "DECLARADO": ("workflow padrão: a fonte não nomeia procedimento "
                                  "que os agrupe. Não é invenção do compilador — é "
                                  "ausência declarada, e vai ao COURSE-GAP-REPORT.")})
    return wfs, used
