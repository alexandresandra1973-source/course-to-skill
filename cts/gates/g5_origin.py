"""G5/origin — localiza EM QUE CAMADA uma afirmação entrou (extensão de ADR-0007).

G5 responde "o bundle inventou?". Este probe responde a pergunta seguinte, que
o portão sozinho não alcança: se o bundle é subconjunto do pós-auditoria, onde
a invenção que o adversário encontrou realmente entrou?

Existe porque a auditoria manual (SC-001) atribuiu ao Compiler um conteúdo que
o diff L1→L3 mostra já presente na saída do Extractor. Atribuir o defeito à
camada errada leva a consertar a camada errada.
"""
from __future__ import annotations

from ..result import GateResult, PASS, WARN


def run(*, l1_records: list[dict], bundle_records: list[dict],
        field_path: tuple[str, ...], flagged_ids: list[str],
        subject: str) -> GateResult:
    def get(rec, path):
        node = rec
        for p in path:
            if not isinstance(node, dict):
                return None
            node = node.get(p)
        return node

    l1 = {r.get("decision_id"): r for r in l1_records}
    bd = {r.get("decision_id"): r for r in bundle_records}

    rows = []
    for did in sorted(set(l1) | set(bd)):
        rows.append({
            "id": did,
            "l1": get(l1.get(did, {}), field_path),
            "bundle": get(bd.get(did, {}), field_path),
            "flagged_by_adversary": did in flagged_ids,
        })

    present_in_l1 = [r for r in rows if r["flagged_by_adversary"] and r["l1"] not in (None, "UNDEFINED")]
    introduced_by_compiler = [r for r in rows
                              if r["flagged_by_adversary"] and r["l1"] in (None, "UNDEFINED")
                              and r["bundle"] not in (None, "UNDEFINED")]

    state = WARN if present_in_l1 and not introduced_by_compiler else PASS
    return GateResult(
        gate="G5-closure/origin",
        state=state,
        subject=subject,
        evidence={
            "field": ".".join(field_path),
            "records": len(rows),
            "flagged_by_adversary": len(flagged_ids),
            "already_present_in_L1": len(present_in_l1),
            "introduced_between_L1_and_bundle": len(introduced_by_compiler),
            "table": rows,
        },
        findings=present_in_l1,
        note=("se o conteudo sinalizado ja estava em L1, a atribuicao do achado "
              "ao Compiler esta na camada errada"),
    )
