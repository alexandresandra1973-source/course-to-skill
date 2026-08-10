"""Resultado de portão: estado nomeado + a evidência que o sustenta.

Regra de engenharia (Fase 4): nenhum portão devolve booleano nu.
Todo retorno carrega (a) um estado nomeado, (b) os números medidos,
(c) o sujeito medido — o arquivo real de onde os números saíram.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any


# Estados possíveis de um portão. PASS/FAIL não bastam: a arquitetura
# precisa distinguir "reprovou porque mediu e estava errado" de
# "não pôde medir" — os dois têm consequências diferentes no teto (ADR-0010).
PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"
UNDERPOWERED = "UNDERPOWERED"      # base pequena demais para o teste significar algo
NOT_ESTABLISHED = "NOT_ESTABLISHED"  # o pré-requisito do teste nunca existiu
DATA_DEFECT = "DATA_DEFECT"        # a entrada está malformada — resultado legítimo, não exceção


@dataclass
class GateResult:
    gate: str
    state: str
    subject: str                      # arquivo/caminho realmente lido
    evidence: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    note: str = ""

    @property
    def blocking(self) -> bool:
        return self.state in (FAIL, DATA_DEFECT)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["blocking"] = self.blocking
        return d

    def __str__(self) -> str:
        head = f"[{self.gate}] {self.state}  subject={self.subject}"
        ev = "  ".join(f"{k}={v}" for k, v in self.evidence.items()
                       if not isinstance(v, (list, dict)))
        return f"{head}\n    {ev}" if ev else head


def dump(results: list[GateResult], path) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
