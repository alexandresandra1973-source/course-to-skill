"""G5 — portão de fechamento pós-compilação (ADR-0007, ADR-0008).

Três verificações, todas ancoradas fora do artefato que examinam:

  1. COMPILER_INVENTION  claims(bundle) ⊄ claims(pós-auditoria)
  2. HOLDOUT_LEAK        artefato cita span reservado no lock
  3. RUBRIC_SELF_REFERENCE  a rubrica cita IDs internos do artefato
     (é a checagem de circularidade — ADR-0008)
"""
from __future__ import annotations

import re

from ..result import GateResult, PASS, FAIL

INTERNAL_ID = re.compile(r"\b(?:ADR|WF|EV|PR|AP|QC|TOOL|CLAIM|RULE)-\d{3,}\b")


def run(bundle_claims: dict[str, list[str]],
        audited_claims: dict[str, list[str]],
        normalize,
        subject: str,
        rubric_text: str | None = None,
        holdout_spans: list[str] | None = None,
        artifact_spans: list[str] | None = None) -> GateResult:

    audited = set()
    for v in audited_claims.values():
        audited |= {normalize(x) for x in v if normalize(x)}

    invented: list[dict] = []
    n_bundle = 0
    for f, claims in bundle_claims.items():
        for c in claims:
            nc = normalize(c)
            if not nc:
                continue
            n_bundle += 1
            if nc not in audited:
                invented.append({"file": f, "claim_head": c[:110]})

    leak = []
    if holdout_spans and artifact_spans:
        from ..cutter import overlaps
        for a in artifact_spans:
            for h in holdout_spans:
                if overlaps(a, h):
                    leak.append({"artifact_span": a, "holdout_span": h})
                    break

    rubric_ids = sorted(set(INTERNAL_ID.findall(rubric_text or "")))

    state = FAIL if (invented or leak or rubric_ids) else PASS
    return GateResult(
        gate="G5-closure",
        state=state,
        subject=subject,
        evidence={
            "bundle_claims": n_bundle,
            "audited_claims": len(audited),
            "compiler_invention_count": len(invented),
            "holdout_leak_count": len(leak),
            "rubric_internal_id_kinds": len(rubric_ids),
            "rubric_internal_id_sample": rubric_ids[:12],
            "invention_by_file": _by_file(invented),
        },
        findings=(invented[:15] + leak[:5]
                  + ([{"rubric_self_reference": rubric_ids[:20]}] if rubric_ids else [])),
        note=("normalizacao estrita de proposito (ADR-0007): comeca apertada e "
              "so afrouxa com caso documentado"),
    )


def _by_file(items: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for i in items:
        out[i["file"]] = out.get(i["file"], 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))
