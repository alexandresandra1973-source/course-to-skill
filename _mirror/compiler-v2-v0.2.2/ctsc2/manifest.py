"""COMPILATION_MANIFEST estendido — §6.2 da ADR.

Registra o que permite diagnosticar regressão de densidade quantitativamente:
contagem de segmentos, evidências por segmento (inclusive zero), cobertura de
L0, limiar, resultado do portão, iterações de revarredura e hash do
temporal-map.

Este módulo NÃO decide aceitação. Ele registra. A decisão de aceitação do
PILOT-001 corrigido é do §9 da ADR e acontece na execução, que não é feita
aqui.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from . import thresholds as T
from .coverage_gate import CoverageResult, GateResult
from .extraction import Pass2Result
from .temporal_map import TemporalMapHandle


def build(*, pilot_id: str, compiler_version: str, tmap: TemporalMapHandle,
          pass2: Pass2Result, gate: GateResult, cov: CoverageResult,
          dedup_report: dict, l0_sha256: str,
          final_evidences: int) -> dict:
    yields = [y.to_dict() for y in pass2.yields]
    counts = [y["evidence_count"] for y in yields]
    n_seg = tmap.segment_count

    doc = {
        "schema_version": "0.2.0",
        "artifact_id": f"{pilot_id}-COMPILATION-MANIFEST",
        "pilot_id": pilot_id,
        "compiler_version": compiler_version,
        "compiler_architecture": (
            "PASS 1 → temporal-map.yaml persistido e hasheado → "
            "PASS 2[SEG-001] … PASS 2[SEG-N] → portão de cobertura/saturação "
            "→ revarredura dirigida se necessário"),

        "input": {"l0_sha256": l0_sha256},

        # ---------------------------------------------------------- PASS 1
        "pass1": {
            "segment_count": n_seg,
            "temporal_map_path": str(tmap.path.name),
            "temporal_map_sha256": tmap.sha256,
            "persisted_before_pass2": True,
            "historical_reference_segments": T.HISTORICAL["segments"],
            "comparability_band_inclusive": list(T.PASS1_BAND_INCLUSIVE),
            "in_comparability_band": T.pass1_in_band(n_seg),
            "variance_flag": (None if T.pass1_in_band(n_seg)
                              else T.PASS1_VARIANCE_FLAG),
        },

        # ---------------------------------------------------------- PASS 2
        "pass2": {
            "execution_mode": "PER_SEGMENT",
            "monolithic_sweep_used": False,
            "invocations": n_seg,
            "evidence_from_pass2": pass2.total,
            "segments_with_zero_yield": pass2.zero_yield_segments,
            "zero_yield_count": len(pass2.zero_yield_segments),
            "min_yield": min(counts) if counts else 0,
            "max_yield": max(counts) if counts else 0,
            "per_segment_yield": yields,
        },

        # ------------------------------------------------------- dedup
        "deduplication": dedup_report,

        # ------------------------------------------------------- portão
        "coverage_gate": {
            "metric": cov.metric,
            "metric_module_sha256": cov.module_hashes,
            "extent_s": cov.extent_s,
            "covered_s": cov.covered_s,
            "l0_coverage": round(cov.coverage, 6),
            "l0_coverage_pct": round(100 * cov.coverage, 2),
            "threshold": T.COVERAGE_FLOOR,
            "comparison": T.COVERAGE_COMPARISON,
            "threshold_frozen_before_run": True,
            "result": "SATISFIED" if gate.satisfied else "NOT_SATISFIED",
            "stop_reason": gate.stop_reason,
            "rescan_iterations": gate.n_iterations,
            "max_rescan_iterations": T.MAX_RESCAN_ITERATIONS,
            "iterations": [
                {"iteration": it.iteration,
                 "coverage_before": round(it.coverage_before, 6),
                 "targeted_segments": it.targeted_segments,
                 "evidence_added": it.evidence_added,
                 "coverage_after": round(it.coverage_after, 6),
                 "stopped_reason": it.stopped_reason}
                for it in gate.iterations],
        },

        # ------------------------------------------------------- totais
        "evidence": {
            "total": final_evidences,
            "aggregate_yield_per_segment": (round(final_evidences / n_seg, 4)
                                            if n_seg else 0),
            "historical_reference_total": T.HISTORICAL["evidence"],
            "historical_reference_yield": T.HISTORICAL["yield_per_segment"],
            "yield_comparison_valid": T.pass1_in_band(n_seg),
            "yield_comparison_note": (
                "Comparação de yield contra 4,89 só vale com PASS 1 dentro de "
                "7–11 segmentos (§12). Fora da banda, yield é diagnóstico."),
        },

        # ------------------------------------------------------- proibições
        "no_quota_declaration": {
            "count_target": None,
            "min_per_segment": None,
            "proportional_to_time": False,
            "statement": ("Nenhum alvo de contagem existe nesta implementação. "
                          "Os ~200 da ADR são diagnóstico, nunca cota (§10)."),
        },
        "frozen_thresholds": T.FROZEN,
    }
    return doc


def persist(doc: dict, out_dir: Path) -> tuple[Path, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "COMPILATION_MANIFEST.yaml"
    blob = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False,
                          width=100).encode("utf-8")
    p.write_bytes(blob)
    return p, hashlib.sha256(blob).hexdigest()
