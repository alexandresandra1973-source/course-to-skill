"""G3 — portão de degeneração por dispersão (ADR-0005)."""
from __future__ import annotations

from ..dispersion import measure, FieldDispersion, THETA_PROVISORIO, N_MIN
from ..result import GateResult, PASS, FAIL, WARN, UNDERPOWERED

# Campos epistêmicos entram no portão. `status` é operacional (ciclo de vida do
# registro), então é medido e reportado mas NÃO bloqueia — ADR-0005.
EPISTEMIC = {
    "evidence.origin_class", "evidence.evidence_strength",
    "evidence.confidence.level", "evidence.category",
    "decision.origin_class", "decision.rationale.state",
    "decision.promotion_level", "decision.autonomy.level",
}


def run(fields: dict[str, list], domains: dict[str, int], subject: str,
        theta: float = THETA_PROVISORIO) -> GateResult:
    measured: list[FieldDispersion] = []
    for name, values in fields.items():
        k = domains.get(name)
        if not k:
            continue
        measured.append(measure(name, values, k, theta=theta))

    collapsed = [m for m in measured if m.state == "COLLAPSED"]
    near = [m for m in measured if m.state == "NEAR_COLLAPSED"]
    under = [m for m in measured if m.state == "UNDERPOWERED"]
    okf = [m for m in measured if m.state == "OK"]

    blocking = [m for m in collapsed if m.field in EPISTEMIC]
    if blocking:
        state = FAIL
    elif near:
        state = WARN
    elif under and not okf:
        state = UNDERPOWERED
    else:
        state = PASS

    return GateResult(
        gate="G3-dispersion",
        state=state,
        subject=subject,
        evidence={
            "fields_measured": len(measured),
            "collapsed": len(collapsed),
            "collapsed_epistemic_blocking": len(blocking),
            "near_collapsed": len(near),
            "underpowered": len(under),
            "ok": len(okf),
            "theta_provisorio": theta,
            "theta_status": "EM_ABERTO — nao calibrado (ADR-0005)",
            "n_min": N_MIN,
            "table": [
                {"field": m.field, "n": m.n, "k": m.k, "distinct": m.distinct,
                 "H_bits": m.entropy_bits, "H_norm": m.h_norm,
                 "state": m.state, "counts": m.counts}
                for m in sorted(measured, key=lambda x: (x.h_norm, x.field))
            ],
        },
        findings=[{"field": m.field, "state": m.state, "H_norm": m.h_norm,
                   "distinct": m.distinct, "n": m.n,
                   "blocking": m.field in EPISTEMIC and m.state == "COLLAPSED"}
                  for m in measured if m.state in ("COLLAPSED", "NEAR_COLLAPSED")],
        note=("campo de valor unico carrega 0 bits e nao pode mudar o "
              "comportamento de consumidor nenhum (R2); `status` e' operacional "
              "e nao bloqueia"),
    )
