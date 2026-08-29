"""Tipos do compilador v2 e o contrato do extractor.

O extractor é um PONTO DE INJEÇÃO. Esta implementação não chama modelo nenhum e
não compila piloto nenhum: quem injeta decide se o extractor é o prompt real
(`prompts/lesson-analyzer-v2.md`) ou uma fixture de canário.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from typing import Protocol


# ---------------------------------------------------------------- segmento
@dataclass(frozen=True)
class Segment:
    segment_id: str
    start_s: int
    end_s: int
    topic: str = ""
    function: str = ""

    @property
    def duration(self) -> int:
        return self.end_s - self.start_s


# ---------------------------------------------------------------- evidência
@dataclass
class Evidence:
    """Uma unidade atômica. `evidence_id` é atribuído pelo alocador global."""
    evidence_id: str
    segment_id: str
    claim: str
    start_s: int
    end_s: int
    category: str = "CONCEPT"
    epistemic_status: str = "SOURCE_EXPLICIT"
    quote: str = ""
    origin: str = "PASS2"          # PASS2 | RESCAN
    iteration: int = 0
    merged_from: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvidenceDraft:
    """O que o extractor devolve: sem ID. O ID é do compilador, não do modelo.

    Isto não é detalhe de estilo. Se o extractor numerasse, cada chamada por
    segmento começaria do zero e a unicidade global (§9.3 da ADR) morreria.
    """
    claim: str
    start_s: int
    end_s: int
    category: str = "CONCEPT"
    epistemic_status: str = "SOURCE_EXPLICIT"
    quote: str = ""


class Extractor(Protocol):
    """PASS 2, escopo de UM segmento.

    `context` carrega só o mínimo local declarado na §5 Decisão A; nunca a aula
    inteira. `iteration` é 0 no PASS 2 e ≥1 nas revarreduras dirigidas.
    """

    def extract(self, segment: Segment, context: dict,
                iteration: int) -> list[EvidenceDraft]:
        ...


# ---------------------------------------------------------------- IDs
class IdAllocator:
    """IDs globalmente únicos e sequenciais ENTRE chamadas por segmento.

    Monotônico por construção: o contador nunca recua, nem entre segmentos nem
    entre iterações de revarredura. Reemitir um ID já usado é erro, não aviso.
    """

    def __init__(self, prefix: str = "EV", width: int = 4, start: int = 1):
        self.prefix, self.width, self._next = prefix, width, start
        self._issued: set[str] = set()

    def issue(self) -> str:
        eid = f"{self.prefix}-{self._next:0{self.width}d}"
        if eid in self._issued:                       # inalcançável por construção
            raise RuntimeError(f"ID reemitido: {eid}")
        self._issued.add(eid)
        self._next += 1
        return eid

    @property
    def count(self) -> int:
        return len(self._issued)

    def is_sequential(self) -> bool:
        nums = sorted(int(e.split("-")[1]) for e in self._issued)
        return nums == list(range(nums[0], nums[0] + len(nums))) if nums else True


# ---------------------------------------------------------------- normalização
_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)


def normalize_claim(s: str) -> str:
    """Normalização ESTRITA, igual em espírito à da ADR-0007 do projeto.

    Estrita de propósito: ela decide identidade de conteúdo na deduplicação, e
    afrouxar aqui é exatamente o modo de falha que o canário de fronteira
    existe para pegar.
    """
    s = _PUNCT.sub("", _WS.sub(" ", (s or "").lower())).strip()
    return s


def claim_key(claim: str) -> str:
    return hashlib.sha256(normalize_claim(claim).encode("utf-8")).hexdigest()
