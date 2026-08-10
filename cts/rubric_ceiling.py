"""Teto da régua: quanta margem um teste comparativo pode produzir.

A margem de um teste A×B é limitada por duas coisas independentes:

  1. TETO ARITMÉTICO — se ambos os braços precisam passar em todos os critérios
     obrigatórios, cada um fica preso entre o piso ponderado (Σ w·min) e o máximo
     da escala. A margem máxima é a diferença entre os dois.

  2. TETO EVIDENCIAL — um critério só separa dois braços se aquilo que ele mede
     estiver em um e não no outro. Critério cujo conteúdo sobrevive à ablação não
     tem poder de separação, qualquer que seja o peso.

O segundo é o que costuma decidir, e é invisível para quem só olha a soma dos
pesos. Este módulo mede os dois e NÃO precisa dos escores — é propriedade do
instrumento, não do resultado.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).lower()


@dataclass
class Criterion:
    name: str
    weight: float
    minimum_score: int
    mandatory: bool


@dataclass
class Probe:
    """Um item exigido pela régua e como detectá-lo no texto de um braço."""
    label: str
    any_of: list[str]
    all_of: list[str] = field(default_factory=list)

    def present_in(self, text: str) -> bool:
        t = norm(text)
        ok_any = any(norm(x) in t for x in self.any_of) if self.any_of else True
        ok_all = all(norm(x) in t for x in self.all_of) if self.all_of else True
        return ok_any and ok_all


def weighted_floor(criteria: list[Criterion], mandatory_only: bool = True) -> float:
    """Menor total possível para um braço que passa em todos os obrigatórios."""
    return round(sum(c.weight * c.minimum_score
                     for c in criteria if c.mandatory or not mandatory_only), 4)


def arithmetic_ceiling(criteria: list[Criterion], scale_max: int) -> dict:
    floor = weighted_floor(criteria)
    return {
        "weights_sum": round(sum(c.weight for c in criteria), 4),
        "weighted_floor_if_passing": floor,
        "scale_max": scale_max,
        "headroom_above_floor": round(scale_max - floor, 4),
        "max_margin_if_both_arms_pass": round(scale_max - floor, 4),
        "max_margin_if_baseline_unconstrained": round(scale_max - 0, 4),
    }


def margin_under_regimes(criteria: list[Criterion], sep_rows: list[dict],
                         scale_max: int) -> dict:
    """Margem máxima disponível, nos dois regimes possíveis para o braço comparado.

    Regime PISO: o braço comparado também respeita os mínimos obrigatórios.
    Cada critério que separa contribui, no máximo, w * (max - min).
    Regime LIVRE: o braço comparado não precisa passar; contribui w * max.

    A distinção decide o teste: se a margem exigida só é alcançável no regime
    LIVRE, o teste só "vence" quando o braço comparado REPROVA — não basta ele
    ser pior.
    """
    by_name = {c.name: c for c in criteria}
    sep = [r["criterion"] for r in sep_rows if r["status"] == "SEPARA"]
    piso = sum(by_name[n].weight * (scale_max - by_name[n].minimum_score) for n in sep)
    livre = sum(by_name[n].weight * scale_max for n in sep)
    return {"separating_criteria": sep,
            "max_margin_regime_piso": round(piso, 4),
            "max_margin_regime_livre": round(livre, 4)}


def separating_power(criteria: list[Criterion],
                     criterion_probes: dict[str, list[Probe]],
                     arm_a_text: str, arm_b_text: str) -> dict:
    """Quanto peso da régua consegue, de fato, separar os dois braços."""
    rows, sep_w, tie_w, unmapped_w = [], 0.0, 0.0, 0.0
    for c in criteria:
        probes = criterion_probes.get(c.name)
        if not probes:
            rows.append({"criterion": c.name, "weight": c.weight,
                         "status": "NAO_MAPEADO", "exclusive_to_A": None})
            unmapped_w += c.weight
            continue
        excl = [p.label for p in probes
                if p.present_in(arm_a_text) and not p.present_in(arm_b_text)]
        both = [p.label for p in probes
                if p.present_in(arm_a_text) and p.present_in(arm_b_text)]
        if excl:
            sep_w += c.weight
            status = "SEPARA"
        else:
            tie_w += c.weight
            status = "EMPATA"
        rows.append({"criterion": c.name, "weight": c.weight, "status": status,
                     "exclusive_to_A": excl, "in_both_arms": both})
    return {
        "rows": rows,
        "separating_weight": round(sep_w, 4),
        "tying_weight": round(tie_w, 4),
        "unmapped_weight": round(unmapped_w, 4),
        "max_margin_from_separating_criteria": round(sep_w * 100, 4),
    }


def element_availability(probes: list[Probe], arms: dict[str, str]) -> list[dict]:
    return [{"element": p.label,
             **{a: p.present_in(t) for a, t in arms.items()}} for p in probes]
