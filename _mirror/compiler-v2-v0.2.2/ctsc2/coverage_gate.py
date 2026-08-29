"""Decisão B — portão de cobertura/saturação DEPOIS do PASS 2, com revarredura dirigida.

A métrica é a de `cts/coverage.py`, e o módulo é PINADO por hash: se ele mudar,
a métrica mudou, e a trava de comparabilidade da §12 da ADR (dois pilotos só se
comparam sob o mesmo comportamento de compilador) deixa de valer. O portão
falha alto nesse caso, em vez de medir com régua diferente e não avisar.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .dedup import dedup
from .model import Evidence, Segment
from .thresholds import GatePolicy, PINNED_METRIC_MODULES, COVERAGE_METRIC

_DEFAULT_CTS_ROOTS = [
    Path("/home/mtx/course-to-skill-claude"),
    Path(__file__).resolve().parents[3] / "course-to-skill-claude",
]


def _cts_root() -> Path:
    env = os.environ.get("CTS_ROOT")
    cands = [Path(env)] if env else []
    cands += _DEFAULT_CTS_ROOTS
    for c in cands:
        if (c / "cts" / "coverage.py").is_file():
            return c
    raise RuntimeError(
        "cts/coverage.py não encontrado. Defina CTS_ROOT para a raiz que "
        f"contém cts/. Procurado em: {[str(c) for c in cands]}")


def load_coverage_module() -> tuple[object, dict[str, str]]:
    """Importa `cts.coverage` e devolve os hashes dos módulos que definem a métrica."""
    root = _cts_root()
    hashes = {}
    for rel in PINNED_METRIC_MODULES:
        p = root / rel
        if not p.is_file():
            raise RuntimeError(f"módulo da métrica ausente: {rel}")
        hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from cts import coverage as C          # noqa: E402
    return C, hashes


@dataclass
class CoverageResult:
    covered_s: int
    extent_s: int
    uncovered_blocks: list[dict]
    metric: dict
    module_hashes: dict[str, str]

    @property
    def coverage(self) -> float:
        return self.covered_s / self.extent_s if self.extent_s else 0.0


@dataclass
class GateIteration:
    iteration: int
    coverage_before: float
    targeted_segments: list[str]
    evidence_added: int
    coverage_after: float
    stopped_reason: str = ""


@dataclass
class GateResult:
    satisfied: bool
    final_coverage: float
    floor: float
    comparison: str
    iterations: list[GateIteration] = field(default_factory=list)
    stop_reason: str = ""
    # Fusões feitas DENTRO do portão, entre iterações de revarredura. Precisam
    # subir para o manifesto: uma duplicata fundida aqui e não reportada some
    # do rastro de auditoria, que é o que a §9.7 da ADR exige enxergar.
    merges: list[dict] = field(default_factory=list)

    @property
    def n_iterations(self) -> int:
        return len(self.iterations)


def measure(evidences: list[Evidence], extent_s: int,
            holdout: list[tuple[int, int]] | None = None) -> CoverageResult:
    """Cobertura de L0 pela união dos spans citados. Held-out fora dos dois lados."""
    C, hashes = load_coverage_module()
    holes = sorted(holdout or [])

    cits = [C.Citation(int(e.start_s), int(e.end_s), "evidence", e.evidence_id)
            for e in evidences]
    covered = C.merge(cits) if cits else []

    # remove held-out do coberto: o que foi cortado não conta como coberto
    def carve(blocks):
        out = []
        for b in blocks:
            pieces = [(b.start, b.end)]
            for h0, h1 in holes:
                nxt = []
                for p0, p1 in pieces:
                    if h1 <= p0 or h0 >= p1:
                        nxt.append((p0, p1))
                        continue
                    if p0 < h0:
                        nxt.append((p0, h0))
                    if h1 < p1:
                        nxt.append((h1, p1))
                pieces = nxt
            out += [C.Block(a, b_) for a, b_ in pieces if b_ > a]
        return out

    covered = carve(covered)
    covered_s = sum(b.dur for b in covered)

    full = C.merge(cits + [C.Citation(a, b, "holdout", "H") for a, b in holes])
    gaps = C.complement(full, 0, extent_s + sum(b - a for a, b in holes))
    blocks = [{"start_s": g.start, "end_s": g.end, "dur_s": g.dur} for g in gaps]

    return CoverageResult(covered_s=covered_s, extent_s=extent_s,
                          uncovered_blocks=blocks, metric=dict(COVERAGE_METRIC),
                          module_hashes=hashes)


def segments_for_blocks(blocks: list[dict], segments: list[Segment]) -> list[str]:
    """Segmentos que intersectam blocos descobertos — o alvo da revarredura.

    A revarredura é DIRIGIDA: só volta aos segmentos que tocam território não
    coberto. Revarrer tudo seria a varredura monolítica que a Decisão A proíbe.
    """
    out = []
    for s in segments:
        if any(b["start_s"] < s.end_s and s.start_s < b["end_s"] for b in blocks):
            out.append(s.segment_id)
    return out


def run_gate(*, evidences: list[Evidence], segments: list[Segment], extent_s: int,
             rescan, policy: GatePolicy,
             holdout: list[tuple[int, int]] | None = None) -> tuple[GateResult, list[Evidence]]:
    """Mede, e enquanto não satisfizer, revarre os blocos descobertos.

    `rescan(segment_ids, iteration) -> list[Evidence]` já vem com IDs alocados
    pelo mesmo alocador global do PASS 2, e o resultado passa por dedup fora
    daqui. Este módulo não emite evidência e não numera nada.
    """
    cur = list(evidences)
    cov = measure(cur, extent_s, holdout)
    res = GateResult(satisfied=policy.satisfied(cov.coverage),
                     final_coverage=cov.coverage, floor=policy.coverage_floor,
                     comparison="strictly_greater")
    if res.satisfied:
        res.stop_reason = "THRESHOLD_SATISFIED_WITHOUT_RESCAN"
        return res, cur

    for i in range(1, policy.max_iterations + 1):
        before = cov.coverage
        targets = segments_for_blocks(cov.uncovered_blocks, segments)
        added = rescan(targets, i) or []
        merged = dedup(cur + list(added))
        gained = len(merged.kept) - len(cur)
        cur = merged.kept
        res.merges.extend(merged.merged)
        cov = measure(cur, extent_s, holdout)
        it = GateIteration(iteration=i, coverage_before=before,
                           targeted_segments=targets, evidence_added=gained,
                           coverage_after=cov.coverage)
        res.iterations.append(it)

        if policy.satisfied(cov.coverage):
            it.stopped_reason = "THRESHOLD_SATISFIED"
            res.satisfied = True
            res.stop_reason = "THRESHOLD_SATISFIED_AFTER_RESCAN"
            break
        if policy.stop_on_zero_progress and gained == 0:
            it.stopped_reason = "ZERO_PROGRESS"
            res.stop_reason = "STOPPED_ZERO_PROGRESS"
            break
    else:
        res.stop_reason = "STOPPED_MAX_ITERATIONS"

    res.final_coverage = cov.coverage
    return res, cur
