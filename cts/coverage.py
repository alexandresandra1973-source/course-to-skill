"""Mapa de cobertura de L0 — quanto da fonte foi efetivamente citado.

Mede o COMPLEMENTO: o que nenhuma evidência, nenhum caso de teste e nenhuma
rubrica alcança. Território virgem é o único lugar de onde um held-out legítimo
poderia sair (ADR-0003) — mas esta módulo NÃO corta nada. Só mede.

Reusa `spans.py` (gramática) e `vault.py` (resolução). A geometria trabalha em
segundos absolutos sobre os timestamps declarados; a resolução contra as marcas
do transcript continua sendo trabalho do G2, e as duas medidas podem discordar
(o piloto tem 1 caso: `EV-0001`, marca de fim `0:29` inexistente).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .spans import Span

MARK_RE = re.compile(r"\*\*(\d{1,3}:[0-5]\d)\*\*")


def hhmmss_to_s(t: str) -> int:
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def mark_to_s(m: str) -> int:
    a, b = m.split(":")
    return int(a) * 60 + int(b)


def fmt(s: int) -> str:
    return f"{s // 60}:{s % 60:02d}"


@dataclass
class Citation:
    start: int
    end: int
    origin: str          # "evidence" | "test-suite" | "rubric"
    ref: str


@dataclass
class Block:
    start: int
    end: int
    text: str = ""
    verdict: str = ""
    markers: dict = field(default_factory=dict)

    @property
    def dur(self) -> int:
        return self.end - self.start


def merge(cits: list[Citation]) -> list[Block]:
    """União dos intervalos citados."""
    out: list[Block] = []
    for c in sorted(cits, key=lambda x: (x.start, x.end)):
        if out and c.start <= out[-1].end:
            out[-1].end = max(out[-1].end, c.end)
        else:
            out.append(Block(c.start, c.end))
    return out


def complement(covered: list[Block], extent_start: int, extent_end: int) -> list[Block]:
    """O que sobra da fonte depois de remover tudo o que foi citado."""
    gaps: list[Block] = []
    prev = extent_start
    for b in covered:
        if b.start > prev:
            gaps.append(Block(prev, min(b.start, extent_end)))
        prev = max(prev, b.end)
    if prev < extent_end:
        gaps.append(Block(prev, extent_end))
    return [g for g in gaps if g.dur > 0]


def mark_index(text: str) -> list[tuple[int, int, int]]:
    """[(segundos, offset_inicio_da_marca, offset_fim_da_marca)] em ordem."""
    return [(mark_to_s(m.group(1)), m.start(), m.end()) for m in MARK_RE.finditer(text)]


def text_for(text: str, idx: list[tuple[int, int, int]], a: int, b: int) -> str:
    """Fala pertencente ao intervalo [a, b).

    O texto que segue uma marca pertence ao segmento que ela abre. O intervalo
    recebe, portanto, os segmentos cuja marca cai dentro dele.
    """
    parts = []
    for i, (t, s0, e0) in enumerate(idx):
        if a <= t < b:
            nxt = idx[i + 1][1] if i + 1 < len(idx) else len(text)
            parts.append(text[e0:nxt])
    return " ".join(" ".join(parts).split())


# ---------------------------------------------------------------- triagem

# Marcadores extraídos do texto REAL do PILOT-001, não inventados.
MARKERS = {
    "metodo": [
        "if you", "make sure", "don't ", "should ", "step ", "start by",
        "never ", "always ", "at least", "avoid", "the mistake",
        "go back", "run it", "review every",
    ],
    "plug": [
        "free guide", "playbook", "put together", "link in", "description",
        "highly recommend checking", "download", "check out the",
    ],
    "cta": [
        "comments", "pause this", "subscribe", "your turn", "drop your",
        "how fast you can",
    ],
    "transicao": [
        "the next question", "so now you know", "now the question",
        "in this video", "by the end", "we're going to answer",
        "that's the operating principle", "keep it in mind",
    ],
}

CANDIDATO = "CANDIDATO_HELD_OUT"
DESCARTE = "DESCARTE"


HEADING_RE = re.compile(r"^##.*$", re.M)


def strip_headings(text: str) -> str:
    """Remove títulos de seção em markdown antes da triagem.

    Correção de dado, não ajuste de limiar: `## How to Build an AI Agent Step by
    Step` é rótulo de capítulo do transcript, não fala do professor, e injeta
    marcadores de método que ninguém disse.
    """
    return HEADING_RE.sub(" ", text)


def classify(text: str) -> tuple[str, dict]:
    """Triagem MECÂNICA, não decisão. Devolve o veredito e as duas regras.

    v1 (só método): CANDIDATO se houver ao menos um marcador de método.
    v2 (vigente):   CANDIDATO só se houver método E nenhum marcador de plug ou
                    de CTA. Um bloco que vende algo ou pede engajamento não é
                    metodologia, mesmo que contenha um verbo instrucional —
                    e `intro, saudação, plug de produto` é justamente a classe
                    que a triagem tem de mandar para DESCARTE.

    Os marcadores viajam junto com o veredito para que a chamada seja revisível:
    "sem conteúdo de método" é juízo semântico e nenhum contador o substitui.
    """
    low = strip_headings(text).lower()
    found = {k: sorted({m.strip() for m in v if m in low}) for k, v in MARKERS.items()}
    v1 = CANDIDATO if found["metodo"] else DESCARTE
    v2 = (CANDIDATO if (found["metodo"] and not found["plug"] and not found["cta"])
          else DESCARTE)
    found["_regra_v1_so_metodo"] = v1
    return v2, found
