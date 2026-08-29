"""Emissão MECÂNICA do roteador, do gap report e dos manifests. Zero chamadas."""
from __future__ import annotations
import json

ROUTER = """# {name}

**Skill ID:** `{skill_id}`  **Version:** `{version}`  **Maturity:** `S3_EXECUTABLE`  **Production Ready:** `false`

## ROLE OF THIS FILE

Runtime entrypoint and router only. Executable methodology is intentionally stored in structured resources rather than duplicated here.

## LOAD ORDER — MANDATORY

Before every answer, load/apply in this order:

1. `knowledge/runtime-policy.yaml`
2. `knowledge/decision-rules.yaml` when a methodology decision is required
3. `knowledge/workflows.yaml` when building/configuring

## DISPATCH

{dispatch}

## FAIL CLOSED

`METHOD_NOT_DEFINED` and `MISSING_REQUIRED_INPUT` are hard runtime stops when emitted by the routed policy. Do not bypass them with general knowledge.

If an executable decision/workflow resource required for the current request is unavailable, do not reconstruct it from this entrypoint, memory, or general knowledge; use the fail-closed behavior in `knowledge/runtime-policy.yaml`.

## RESPONSE DISCIPLINE

Preserve explicit user boundaries; never invent missing required inputs; distinguish source methodology from generic implementation suggestions.

## PILOT LIMITATION

Single-course pilot. Until an independent blind run succeeds, this runtime remains `S3_EXECUTABLE`, `production_ready: false`.
"""


def render_router(*, name: str, skill_id: str, version: str, workflows: list) -> str:
    """Rotas geradas do índice. Nenhuma condição, nenhuma ação: só destino.

    A primeira versão listava `WF-0001 … WF-0045` — 43 linhas de identificador
    opaco. Um roteador que lista IDs não roteia: quem lê não tem por onde casar
    um pedido. As rotas passam a usar o NOME do workflow, que vem da evidência
    que o ancora, e o ID vai junto como destino.
    """
    lines = ["- Methodology decision request → `knowledge/decision-rules.yaml`.", "",
             "Build/configure requests route by topic to `knowledge/workflows.yaml`:"]
    for w in sorted(workflows, key=lambda x: x["workflow_id"]):
        if w["workflow_id"] == "WF-DEFAULT":
            continue
        lines.append(f"- *{w['name']}* → `{w['workflow_id']}`"
                     f" ({len(w.get('steps', []))} steps)")
    if any(w["workflow_id"] == "WF-DEFAULT" for w in workflows):
        d = next(w for w in workflows if w["workflow_id"] == "WF-DEFAULT")
        lines += ["", f"- Steps the source does not group under any named procedure "
                      f"→ `WF-DEFAULT` ({len(d.get('steps', []))} steps).", ""]
    lines.append("- Out-of-scope request: obey the scope guard in "
                 "`knowledge/runtime-policy.yaml`.")
    return ROUTER.format(name=name, skill_id=skill_id, version=version,
                         dispatch="\n".join(lines))


def collect_gaps(rules, steps, dispositions, evidence, origin_by_evidence,
                 rule_is_course_gap) -> list[dict]:
    """Toda lacuna vira linha com id estável, tipo, span e timestamp."""
    gaps = []
    span = {e["evidence_id"]: (e["source_excerpt"]["span"]["start_s"],
                               e["source_excerpt"]["span"]["end_s"]) for e in evidence}

    def ts(a):
        return f"{a//60}:{a%60:02d}"

    for ent in list(rules) + list(steps):
        eid = ent.get("rule_id") or ent.get("step_id")
        for f in ("autonomy", "precedence", "missing_input_action", "iteration_limit"):
            if ent.get(f) == "UNDEFINED":
                sp = [span[e] for e in ent["evidence_ids"] if e in span]
                a = min(s[0] for s in sp) if sp else 0
                gaps.append({"gap_id": f"GAP-{eid}-{f}", "kind": "UNDEFINED_FIELD",
                             "entity": eid, "field": f, "at_s": a, "timestamp": ts(a),
                             "evidence_ids": ent["evidence_ids"]})
        if rule_is_course_gap(ent, origin_by_evidence):
            sp = [span[e] for e in ent["evidence_ids"] if e in span]
            a = min(s[0] for s in sp) if sp else 0
            gaps.append({"gap_id": f"GAP-{eid}-ONLY-INFERENCE",
                         "kind": "RULE_ONLY_FROM_GENUINE_INFERENCE",
                         "entity": eid, "field": None, "at_s": a, "timestamp": ts(a),
                         "evidence_ids": ent["evidence_ids"],
                         "detail": ("a regra funciona, mas o curso não a ensinou: "
                                    "toda evidência que a sustenta é inferência do "
                                    "modelo")})
    for e, d in dispositions.items():
        if d == "GAP":
            a = span.get(e, (0, 0))[0]
            gaps.append({"gap_id": f"GAP-{e}", "kind": "EVIDENCE_UNDERSPECIFIED",
                         "entity": e, "field": None, "at_s": a, "timestamp": ts(a),
                         "evidence_ids": [e]})
    return sorted(gaps, key=lambda g: (g["at_s"], g["gap_id"]))


def render_gap_report(gaps: list[dict], header: str) -> str:
    L = [header, "", "| lacuna | tipo | onde na aula | origem |", "|---|---|---|---|"]
    for g in gaps:
        L.append(f"| `{g['gap_id']}` | {g['kind']} | **{g['timestamp']}** | "
                 f"{', '.join(g['evidence_ids'][:3])} |")
    return "\n".join(L) + "\n"
