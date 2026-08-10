"""G6 — teto de maturidade em função do corpus (ADR-0010).

Escada:
  S0 INGESTED   G0 (vault selado)
  S1 ANCHORED   G2
  S2 MODELED    G3
  S3 AUDITED    G4        (fora do escopo da fatia vertical: não avaliado)
  S4 CLOSED     G5
  S5 VALIDATED  G7 e n_holdout >= n_min_wilson(limiar)

n mínimo é CALCULADO, não escolhido: para acerto observado de 100% o limite
inferior de Wilson a 95% vale n/(n+z^2). O menor n com LB >= 0.80 é 16.
"""
from __future__ import annotations

import math

from ..result import GateResult, PASS, FAIL

Z = 1.96
LADDER = ["S0_INGESTED", "S1_ANCHORED", "S2_MODELED",
          "S3_AUDITED", "S4_CLOSED", "S5_VALIDATED"]


def wilson_lower_perfect(n: int, z: float = Z) -> float:
    """LB de Wilson 95% quando p_chapeu = 1."""
    return n / (n + z * z) if n > 0 else 0.0


def min_n_for(threshold: float, z: float = Z) -> int:
    n = 1
    while wilson_lower_perfect(n, z) < threshold:
        n += 1
        if n > 10000:
            break
    return n


def run(*, vault_sealed: bool, g2, g3, g4, g5,
        n_holdout: int, threshold: float, requested_level: str,
        subject: str, corpus_stats: dict) -> GateResult:

    n_min = min_n_for(threshold)
    lb = wilson_lower_perfect(n_holdout)

    reached, reasons = "NONE", []

    def note(level, ok, why):
        reasons.append({"level": level, "reached": ok, "why": why})
        return ok

    if note("S0_INGESTED", vault_sealed, "vault selado" if vault_sealed
            else "vault nao selado"):
        reached = "S0_INGESTED"
        if note("S1_ANCHORED", g2 is not None and g2.state == "PASS",
                f"G2={getattr(g2,'state','AUSENTE')} "
                f"({getattr(g2,'evidence',{}).get('records_anchored_ok','?')}/"
                f"{getattr(g2,'evidence',{}).get('records','?')} ancoradas)"):
            reached = "S1_ANCHORED"
            if note("S2_MODELED", g3 is not None and g3.state in ("PASS", "WARN"),
                    f"G3={getattr(g3,'state','AUSENTE')} "
                    f"({getattr(g3,'evidence',{}).get('collapsed_epistemic_blocking','?')}"
                    " campos epistemicos colapsados)"):
                reached = "S2_MODELED"
                if note("S3_AUDITED", g4 is not None and g4.state == "PASS",
                        "G4 fora do escopo da fatia vertical (Adversario nao implementado)"):
                    reached = "S3_AUDITED"
                    if note("S4_CLOSED", g5 is not None and g5.state == "PASS",
                            f"G5={getattr(g5,'state','AUSENTE')}"):
                        reached = "S4_CLOSED"
                        if note("S5_VALIDATED", n_holdout >= n_min,
                                f"n_holdout={n_holdout} < n_min={n_min}"):
                            reached = "S5_VALIDATED"
            else:
                reasons.append({"level": "S3_AUDITED", "reached": False,
                                "why": "nao avaliado: S2 nao alcancado"})
        else:
            for lv in ("S2_MODELED", "S3_AUDITED", "S4_CLOSED", "S5_VALIDATED"):
                reasons.append({"level": lv, "reached": False,
                                "why": "nao avaliado: S1 nao alcancado"})

    granted = LADDER.index(reached) if reached in LADDER else -1
    asked = LADDER.index(requested_level) if requested_level in LADDER else -1
    state = PASS if asked <= granted else FAIL

    return GateResult(
        gate="G6-ceiling",
        state=state,
        subject=subject,
        evidence={
            "requested_level": requested_level,
            "ceiling_reached": reached,
            "n_holdout": n_holdout,
            "threshold": threshold,
            "n_min_wilson_95": n_min,
            "wilson_lb_at_n_holdout": round(lb, 4),
            "production_ready_allowed": reached == "S5_VALIDATED",
            "corpus": corpus_stats,
            "ladder": reasons,
        },
        findings=[r for r in reasons if not r["reached"]],
        note=(f"n minimo calculado, nao escolhido: menor n com LB de Wilson 95% "
              f">= {threshold} e' {n_min} (LB={wilson_lower_perfect(n_min):.4f})"),
    )
