"""Deduplicação entre segmentos e entre iterações de revarredura.

O PROBLEMA QUE ESTE MÓDULO RESOLVE, E O QUE ELE SE RECUSA A FAZER
-----------------------------------------------------------------
A extração por segmento cria dois riscos opostos, e um conserto ingênuo troca
um pelo outro:

  RISCO 1 — duplicata real. A revarredura dirigida visita de novo um bloco já
            coberto e reemite a MESMA evidência. Tem de fundir (§9.7 da ADR).

  RISCO 2 — vizinhas distintas na fronteira. Dois segmentos adjacentes contêm
            duas unidades atômicas DIFERENTES, com parecença lexical alta
            porque falam do mesmo assunto. Fundir é destruir evidência válida
            (§13, canário de fronteira).

A REGRA ADOTADA: identidade de conteúdo, NUNCA semelhança.
Duas evidências são a mesma se, e somente se, a claim normalizada é IDÊNTICA.
Proximidade de span, sobreposição temporal e similaridade lexical **não**
fundem nada por si.

Por que não usar similaridade com limiar: qualquer limiar que funda "parecidas"
funde as vizinhas legítimas do RISCO 2, e o limiar que as preserva não funde
quase nada do RISCO 1. Não há ponto de corte que sirva aos dois. Identidade
exata sobre texto normalizado resolve o RISCO 1 completamente — porque uma
revarredura que reemite a mesma unidade reemite o mesmo texto — sem tocar no
RISCO 2. O canário prova as duas metades.
"""
from __future__ import annotations

from dataclasses import dataclass

from .model import Evidence, normalize_claim


@dataclass
class DedupResult:
    kept: list[Evidence]
    merged: list[dict]          # {"survivor": id, "absorbed": id, "reason": ...}
    examined: int

    @property
    def n_merged(self) -> int:
        return len(self.merged)


def dedup(evidences: list[Evidence]) -> DedupResult:
    """Funde só identidade exata de claim normalizada. Ordem estável.

    O sobrevivente é o de menor ID — o primeiro emitido. Isso mantém a
    proveniência no segmento que primeiro encontrou a unidade, que é o que a
    §9.4 pede (rastreabilidade ao segmento de origem).
    """
    by_key: dict[str, Evidence] = {}
    kept: list[Evidence] = []
    merged: list[dict] = []

    for ev in sorted(evidences, key=lambda e: e.evidence_id):
        k = normalize_claim(ev.claim)
        if not k:
            kept.append(ev)                    # claim vazia não é identidade
            continue
        prev = by_key.get(k)
        if prev is None:
            by_key[k] = ev
            kept.append(ev)
            continue
        # Duplicata real: mesma afirmação, reemitida.
        prev.merged_from.append(ev.evidence_id)
        merged.append({
            "survivor": prev.evidence_id,
            "absorbed": ev.evidence_id,
            "reason": "IDENTICAL_NORMALIZED_CLAIM",
            "survivor_segment": prev.segment_id,
            "absorbed_segment": ev.segment_id,
            "absorbed_iteration": ev.iteration,
        })

    return DedupResult(kept=kept, merged=merged, examined=len(evidences))


def boundary_report(evidences: list[Evidence]) -> list[dict]:
    """Pares de segmentos adjacentes que sobreviveram lado a lado.

    Não é portão: é observabilidade. Serve para o auditor ver que a fronteira
    manteve unidades distintas em vez de as ter colapsado silenciosamente.
    """
    out = []
    ordered = sorted(evidences, key=lambda e: (e.start_s, e.evidence_id))
    for a, b in zip(ordered, ordered[1:]):
        if a.segment_id != b.segment_id and normalize_claim(a.claim) != normalize_claim(b.claim):
            out.append({
                "left": a.evidence_id, "left_segment": a.segment_id,
                "right": b.evidence_id, "right_segment": b.segment_id,
                "gap_s": b.start_s - a.end_s,
                "both_survived": True,
            })
    return out
