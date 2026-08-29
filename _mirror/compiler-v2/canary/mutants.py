"""Mutantes — implementações DELIBERADAMENTE quebradas.

Para que servem: um canário que passa não prova nada se ele também passaria com
a proteção ausente. Cada caso do canário roda duas vezes — contra a
implementação real, onde TEM de passar, e contra o mutante correspondente, onde
TEM de falhar. Se o mutante passa, o canário não tem poder e a suíte inteira é
reprovada.

Cada mutante encarna exatamente o modo de falha que o caso existe para pegar.
"""
from __future__ import annotations

import difflib

from ctsc2.dedup import DedupResult
from ctsc2.model import Evidence, normalize_claim


# ------------------------------------------------------------------ M1
def dedup_by_similarity(evidences: list[Evidence], threshold: float = 0.80) -> DedupResult:
    """MUTANTE do C1: funde por SEMELHANÇA lexical.

    É o conserto ingênuo: "duas evidências parecidas são a mesma". Funde as
    vizinhas legítimas da fronteira e destrói evidência válida — exatamente o
    dano que a §13 da ADR manda impedir.
    """
    kept: list[Evidence] = []
    merged: list[dict] = []
    for ev in sorted(evidences, key=lambda e: e.evidence_id):
        k = normalize_claim(ev.claim)
        hit = None
        for prev in kept:
            if difflib.SequenceMatcher(
                    None, k, normalize_claim(prev.claim)).ratio() >= threshold:
                hit = prev
                break
        if hit is None:
            kept.append(ev)
        else:
            hit.merged_from.append(ev.evidence_id)
            merged.append({"survivor": hit.evidence_id, "absorbed": ev.evidence_id,
                           "reason": f"SIMILARITY>={threshold}",
                           "survivor_segment": hit.segment_id,
                           "absorbed_segment": ev.segment_id,
                           "absorbed_iteration": ev.iteration})
    return DedupResult(kept=kept, merged=merged, examined=len(evidences))


# ------------------------------------------------------------------ M2
def dedup_identity_only(evidences: list[Evidence]) -> DedupResult:
    """MUTANTE do C2: só considera duplicata o MESMO `evidence_id`.

    Como o alocador nunca reemite ID, isto é dedup que nunca funde nada. A
    duplicata real da revarredura sobrevive e o corpus incha com repetição.
    """
    seen, kept = set(), []
    for ev in sorted(evidences, key=lambda e: e.evidence_id):
        if ev.evidence_id in seen:
            continue
        seen.add(ev.evidence_id)
        kept.append(ev)
    return DedupResult(kept=kept, merged=[], examined=len(evidences))


# ------------------------------------------------------------------ M3
def run_pass2_dropping_empty(*, tmap, extractor, ids):
    """MUTANTE do C3: omite do rastro os segmentos que não produziram nada.

    É a regressão mais fácil de cometer — filtrar o vazio "porque não interessa"
    — e é a que apaga a diferença entre o Caso 2 e o Caso 3 da §8 da ADR.
    """
    from ctsc2.extraction import Pass2Result, SegmentYield, _local_context

    res = Pass2Result()
    segs = tmap.segments
    for seg in segs:
        drafts = extractor.extract(seg, _local_context(seg, segs), 0) or []
        emitted = [Evidence(evidence_id=ids.issue(), segment_id=seg.segment_id,
                            claim=d.claim, start_s=d.start_s, end_s=d.end_s,
                            category=d.category,
                            epistemic_status=d.epistemic_status, quote=d.quote,
                            origin="PASS2", iteration=0) for d in drafts]
        res.evidences.extend(emitted)
        if not emitted:
            continue                       # <-- o defeito
        res.yields.append(SegmentYield(
            segment_id=seg.segment_id, start_s=seg.start_s, end_s=seg.end_s,
            duration_s=seg.duration, evidence_count=len(emitted),
            evidence_ids=[e.evidence_id for e in emitted],
            extraction_status="OK"))
    return res


# ------------------------------------------------------------------ M4
def run_gate_always_satisfied(*, evidences, segments, extent_s, rescan, policy,
                              holdout=None):
    """MUTANTE do C4: o portão declara satisfeito sem medir. Nunca revarre."""
    from ctsc2.coverage_gate import GateResult, measure
    cov = measure(evidences, extent_s, holdout)
    return GateResult(satisfied=True, final_coverage=cov.coverage,
                      floor=policy.coverage_floor, comparison="strictly_greater",
                      stop_reason="MUTANT_ALWAYS_SATISFIED"), list(evidences)


# ------------------------------------------------------------------ M5
def run_gate_always_rescans(*, evidences, segments, extent_s, rescan, policy,
                            holdout=None):
    """MUTANTE do C5: revarre sempre, mesmo com a cobertura acima do piso.

    Desperdiça trabalho e, pior, reabre segmentos já saturados — o caminho mais
    curto para reintroduzir duplicata.
    """
    from ctsc2.coverage_gate import GateIteration, GateResult, measure
    from ctsc2.dedup import dedup

    cur = list(evidences)
    cov = measure(cur, extent_s, holdout)
    before = cov.coverage
    added = rescan([s.segment_id for s in segments], 1) or []
    cur = dedup(cur + list(added)).kept
    cov = measure(cur, extent_s, holdout)
    res = GateResult(satisfied=True, final_coverage=cov.coverage,
                     floor=policy.coverage_floor, comparison="strictly_greater",
                     stop_reason="MUTANT_ALWAYS_RESCANS")
    res.iterations.append(GateIteration(
        iteration=1, coverage_before=before,
        targeted_segments=[s.segment_id for s in segments],
        evidence_added=len(added), coverage_after=cov.coverage))
    return res, cur


# ------------------------------------------------------------------ M6
def quote_matches_fuzzy(qn: str, tn: str, threshold: float = 0.80) -> bool:
    """MUTANTE do C6: casa por SEMELHANÇA em vez de substring exata.

    É o afrouxamento que a tarefa proíbe por nome. Ele recupera as citações
    legítimas — e também aceita a fabricada, que é o dano. O caso C6 existe para
    que essa troca seja detectada e não celebrada como conserto.
    """
    if not qn:
        return False
    best = 0.0
    step = max(1, len(qn) // 4)
    for i in range(0, max(1, len(tn) - len(qn) + 1), step):
        window = tn[i:i + len(qn)]
        best = max(best, difflib.SequenceMatcher(None, window, qn).ratio())
        if best >= threshold:
            return True
    return best >= threshold


# `dedup` é importada em três módulos; trocar só uma ligação deixaria o
# caminho real intacto e o mutante passaria por não ter sido aplicado — falso
# "canário sem poder". Todos os pontos de ligação entram na lista.
DEDUP_BINDINGS = ("ctsc2.dedup.dedup", "ctsc2.pipeline.dedup",
                  "ctsc2.coverage_gate.dedup")

MUTANTS = {
    "C1_boundary_distinct": (DEDUP_BINDINGS, dedup_by_similarity,
                             "dedup por semelhança lexical (limiar 0,80)"),
    "C2_true_duplicate": (DEDUP_BINDINGS, dedup_identity_only,
                          "dedup só por evidence_id — nunca funde"),
    "C3_zero_yield_visible": (("ctsc2.pipeline.run_pass2",), run_pass2_dropping_empty,
                              "rastro omite segmento de yield zero"),
    "C4_below_threshold_rescans": (("ctsc2.pipeline.run_gate",),
                                   run_gate_always_satisfied,
                                   "portão sempre satisfeito — nunca revarre"),
    "C5_above_threshold_stops": (("ctsc2.pipeline.run_gate",), run_gate_always_rescans,
                                 "portão sempre revarre — ignora o piso"),
    "C6_quote_normalization": (("ctsc2.extractors.claude_extractor.quote_matches",),
                               quote_matches_fuzzy,
                               "casamento difuso por semelhança (limiar 0,80)"),
}
