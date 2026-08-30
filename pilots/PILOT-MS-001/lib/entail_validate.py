"""MS-001A EXEC 2 — validador do output do juiz de entailment.
Modulo SEPARADO para que lib/validate.py permaneca byte-identico ao declarado no
Opening Record da Execucao 1. A correcao e focalizada no instrumento de entailment.

Mudanca contra a v1: evidence_refs_checked exige IGUALDADE com o conjunto fornecido,
nao mais subconjunto. Codigos distintos para acrescimo, omissao e evidencia estrangeira.
"""
import json

JUDGMENTS = ("ENTAILED", "NOT_ENTAILED", "INDETERMINATE")
FIELDS = {"claim_id", "judgment", "entail_why", "evidence_refs_checked"}
LEGACY = {"temporary_claim_id", "state", "why"}


def validate(txt, source_id, sent, all_source_evidence_ids=None):
    """sent: {claim_id: set(evidence_ids enviados ao juiz para aquela claim)}
    all_source_evidence_ids: universo de EV- da PROPRIA source; ref fora dele e FOREIGN.
    Devolve (doc|None, [codigos])."""
    E = []
    try:
        d = json.loads(txt)
    except Exception:
        return None, ["E01_JSON_UNPARSEABLE"]
    if not isinstance(d, dict) or "verdicts" not in d or set(d) - {"source_id", "verdicts"}:
        return None, ["E22_JUDGE_SCHEMA_VIOLATION"]
    if d.get("source_id") != source_id:
        E.append("E15_SOURCE_ID_MISMATCH")
    if not isinstance(d["verdicts"], list) or not d["verdicts"]:
        return None, ["E22_JUDGE_SCHEMA_VIOLATION"]

    seen = []
    for v in d["verdicts"]:
        if not isinstance(v, dict):
            E.append("E22_JUDGE_SCHEMA_VIOLATION"); continue
        keys = set(v)
        if keys & LEGACY:
            E.append("E23_JUDGE_LEGACY_FORMAT")          # {temporary_claim_id,state,why}
        if keys - FIELDS:
            E.append("E04b_JUDGE_EXTRA_FIELD")
        if FIELDS - keys:
            E.append("E22_JUDGE_SCHEMA_VIOLATION"); continue
        cid = v["claim_id"]
        if cid not in sent:
            E.append("E21_UNKNOWN_CLAIM_ID"); continue
        if cid in seen:
            E.append("E24_JUDGMENT_DUPLICATED")
        seen.append(cid)
        if v["judgment"] not in JUDGMENTS:
            E.append("E25_JUDGMENT_NOT_IN_ENUM")
        if not isinstance(v["entail_why"], str) or len(v["entail_why"]) < 10:
            E.append("E22_JUDGE_SCHEMA_VIOLATION")
        chk = v["evidence_refs_checked"]
        if not isinstance(chk, list) or not chk:
            E.append("E22_JUDGE_SCHEMA_VIOLATION"); continue
        chk = set(chk)
        want = sent[cid]
        if all_source_evidence_ids is not None and (chk - all_source_evidence_ids):
            E.append("E26_FOREIGN_EVIDENCE")
        if chk - want:
            E.append("E19_JUDGE_ADDED_EVIDENCE")
        if want - chk:
            E.append("E27_JUDGE_OMITTED_EVIDENCE")
    if set(sent) - set(seen):
        E.append("E20_JUDGMENT_MISSING")
    return (d if not E else None), sorted(set(E))
