"""Orquestração do compilador v2.

`PASS 1 → temporal-map persistido e hasheado → PASS 2 por segmento →
 dedup → portão de cobertura → revarredura dirigida → dedup → manifesto`

Esta função NÃO chama modelo. O `extractor` é injetado. Nenhum piloto é
compilado por este módulo; ele é a máquina, não a execução.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import manifest as M
from .coverage_gate import measure, run_gate
from .dedup import boundary_report, dedup
from .extraction import make_rescanner, run_pass2
from .model import Evidence, Extractor, IdAllocator, Segment
from .temporal_map import write_and_seal
from .thresholds import GatePolicy


@dataclass
class CompileResult:
    evidences: list[Evidence]
    manifest: dict
    manifest_path: Path
    manifest_sha256: str
    temporal_map_sha256: str
    gate_satisfied: bool
    coverage: float


def compile_lesson(*, pilot_id: str, lesson_id: str, l0_sha256: str,
                   extent_s: int, segments: list[Segment], extractor: Extractor,
                   out_dir: Path, compiler_version: str,
                   holdout: list[tuple[int, int]] | None = None,
                   policy: GatePolicy | None = None,
                   id_start: int = 1) -> CompileResult:
    policy = policy or GatePolicy()
    out_dir = Path(out_dir)

    # PASS 1 — persistido e hasheado ANTES do PASS 2 (§6.1)
    tmap = write_and_seal(segments, out_dir, pilot_id=pilot_id,
                          lesson_id=lesson_id, l0_sha256=l0_sha256,
                          extent_s=extent_s)

    # PASS 2 — por segmento (Decisão A)
    ids = IdAllocator(start=id_start)
    p2 = run_pass2(tmap=tmap, extractor=extractor, ids=ids)

    d1 = dedup(p2.evidences)
    cur = d1.kept

    # Portão + revarredura dirigida (Decisão B)
    rescan = make_rescanner(tmap=tmap, extractor=extractor, ids=ids, result=p2)
    gate, cur = run_gate(evidences=cur, segments=tmap.segments,
                         extent_s=extent_s, rescan=rescan, policy=policy,
                         holdout=holdout)

    d2 = dedup(cur)
    cur = d2.kept
    cov = measure(cur, extent_s, holdout)

    dedup_report = {
        "rule": "IDENTICAL_NORMALIZED_CLAIM",
        "similarity_merging_used": False,
        "rationale": ("Similaridade fundiria vizinhas distintas na fronteira "
                      "entre segmentos; identidade exata resolve duplicata de "
                      "revarredura sem esse dano."),
        "merged_after_pass2": d1.n_merged,
        "merged_inside_gate": len(gate.merges),
        "merged_after_rescan": d2.n_merged,
        "merges": d1.merged + gate.merges + d2.merged,
        "adjacent_distinct_pairs_preserved": len(boundary_report(cur)),
    }

    doc = M.build(pilot_id=pilot_id, compiler_version=compiler_version,
                  tmap=tmap, pass2=p2, gate=gate, cov=cov,
                  dedup_report=dedup_report, l0_sha256=l0_sha256,
                  final_evidences=len(cur))
    mpath, msha = M.persist(doc, out_dir)

    if not ids.is_sequential():
        raise RuntimeError("IDs não ficaram sequenciais (§9.3)")

    return CompileResult(evidences=cur, manifest=doc, manifest_path=mpath,
                         manifest_sha256=msha, temporal_map_sha256=tmap.sha256,
                         gate_satisfied=gate.satisfied, coverage=cov.coverage)
