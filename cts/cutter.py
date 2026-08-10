"""Cutter de held-out em L0, por span (ADR-0003).

Duas funções distintas, e é importante não confundi-las:

1. `cut()` — a operação correta: segmenta L0, sorteia com semente e SELA o
   held-out ANTES de qualquer extração. Produz um lock reproduzível.

2. `retroactive_audit()` — a auditoria do que já existe: dado um corpus onde
   nenhum lock foi criado antes da modelagem, todo caso que se declara cego é
   contaminado por construção. Não há como consertar isso a posteriori — a
   própria fonte do PILOT-001 registra `created_before_modeling: false`.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, asdict
from pathlib import Path

from .vault import Vault, MARK_RE


@dataclass
class Segment:
    seg_id: str
    span: str
    mark_start: str
    mark_end: str
    chars: int


def segment_by_marks(vault: Vault, sha256: str) -> list[Segment]:
    """Segmenta um objeto de texto pelas suas marcas de tempo.

    Regra estrutural, não semântica: o cutter não julga conteúdo — se julgasse,
    já estaria fazendo extração, que é exatamente o que a ADR-0003 proíbe
    acontecer antes do corte.
    """
    text = vault.text(sha256)
    marks = [(m.group(1), m.end()) for m in MARK_RE.finditer(text)]
    segs: list[Segment] = []
    for i in range(len(marks) - 1):
        (m0, a), (m1, b) = marks[i], marks[i + 1]
        h, s = m0.split(":")
        h2, s2 = m1.split(":")
        span = (f"L0:{sha256[:12]}:t="
                f"{int(h)//60:02d}:{int(h)%60:02d}:{s}-"
                f"{int(h2)//60:02d}:{int(h2)%60:02d}:{s2}")
        segs.append(Segment(f"SEG-{i+1:04d}", span, m0, m1, b - a))
    return segs


def cut(segments: list[Segment], seed: int, rate: float) -> dict:
    """Sorteio semeado. Determinístico: mesma semente, mesmo corte."""
    rng = random.Random(seed)
    n = max(1, round(len(segments) * rate))
    holdout = sorted(rng.sample(segments, n), key=lambda s: s.seg_id)
    spans = [s.span for s in holdout]
    payload = json.dumps(spans, ensure_ascii=False, sort_keys=True).encode()
    return {
        "seed": seed,
        "rate": rate,
        "n_segments": len(segments),
        "n_holdout": len(holdout),
        "spans": spans,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "sealed": True,
    }


def train_corpus(segments: list[Segment], lock: dict) -> list[Segment]:
    held = set(lock["spans"])
    return [s for s in segments if s.span not in held]


def corpus_hash(segments: list[Segment]) -> str:
    payload = json.dumps([s.span for s in segments], sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def overlaps(span_a: str, span_b: str) -> bool:
    """Interseção temporal entre dois spans t= do mesmo objeto."""
    from .spans import Span
    A, B = Span.parse(span_a), Span.parse(span_b)
    if not A or not B or A.kind != "time" or B.kind != "time" or A.obj != B.obj:
        return False
    def sec(t: str) -> int:
        h, m, s = t.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    return sec(A.a) < sec(B.b) and sec(B.a) < sec(A.b)


def retroactive_audit(registry: dict, blind_cases: list[dict]) -> dict:
    """Audita casos que se declaram cegos contra um registry existente.

    `blind_cases`: [{case_id, declared_type, support_spans: [...]}]
    """
    status = (registry or {}).get("registry_status")
    pre = bool((registry or {}).get("created_before_modeling"))
    locked = bool((registry or {}).get("locked"))
    cases = (registry or {}).get("cases") or []

    established = status == "ACTIVE" and pre and locked and len(cases) > 0

    verdicts = []
    for c in blind_cases:
        if not established:
            verdicts.append({
                "case_id": c["case_id"],
                "declared_type": c["declared_type"],
                "verdict": "CONTAMINATED_BY_CONSTRUCTION",
                "reason": (f"registry_status={status} created_before_modeling={pre} "
                           f"locked={locked} cases={len(cases)}"),
                "support_spans": c["support_spans"],
            })
        else:
            held = {s for s in registry.get("spans", [])}
            hit = [s for s in c["support_spans"]
                   if any(overlaps(s, h) for h in held)]
            verdicts.append({
                "case_id": c["case_id"],
                "declared_type": c["declared_type"],
                "verdict": "HELD_OUT_OK" if hit else "RECALL_NOT_HELDOUT",
                "reason": "spans de suporte no lock" if hit else
                          "nenhum span de suporte pertence ao held-out",
                "support_spans": c["support_spans"],
            })
    return {"established": established, "registry_status": status,
            "created_before_modeling": pre, "locked": locked,
            "n_cases_in_registry": len(cases), "verdicts": verdicts}
