"""Gramática de span L0 e resolução contra o vault (ADR-0001, ADR-0002).

Formatos:
    L0:<sha12>:c=<ini>-<fim>                  texto, offsets de caractere
    L0:<sha12>:t=<hh:mm:ss>-<hh:mm:ss>        mídia temporal
    L0:<sha12>:frame=<sha12>                  quadro/imagem

Resolver um span devolve bytes OU um motivo nomeado de não-resolução.
Não-resolução é resultado, não exceção: a entrada do piloto tem um span
que não resolve por construção e a espinha existe para dizer isso.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

SPAN_RE = re.compile(
    r"^L0:(?P<obj>[0-9a-f]{12}):"
    r"(?:c=(?P<c0>\d+)-(?P<c1>\d+)"
    r"|t=(?P<t0>\d{1,3}:[0-5]\d:[0-5]\d)-(?P<t1>\d{1,3}:[0-5]\d:[0-5]\d)"
    r"|frame=(?P<frame>[0-9a-f]{12}))$"
)


@dataclass(frozen=True)
class Span:
    raw: str
    obj: str
    kind: str          # "char" | "time" | "frame"
    a: str | int | None
    b: str | int | None

    @staticmethod
    def parse(raw: str) -> "Span | None":
        m = SPAN_RE.match(raw or "")
        if not m:
            return None
        g = m.groupdict()
        if g["c0"] is not None:
            return Span(raw, g["obj"], "char", int(g["c0"]), int(g["c1"]))
        if g["t0"] is not None:
            return Span(raw, g["obj"], "time", g["t0"], g["t1"])
        return Span(raw, g["obj"], "frame", g["frame"], None)


@dataclass
class Resolution:
    span: str
    ok: bool
    reason: str          # OK | MALFORMED_SPAN | OBJECT_NOT_IN_VAULT |
                         # START_MARK_NOT_FOUND | END_MARK_NOT_FOUND |
                         # EMPTY_RANGE | RANGE_OUT_OF_BOUNDS | UNSUPPORTED_KIND
    text: str = ""
    detail: str = ""


def hhmmss_to_mark(ts: str) -> str:
    """Converte 00:08:05 para a forma em que a marca aparece no transcript: '8:05'."""
    h, m, s = ts.split(":")
    return f"{int(h) * 60 + int(m)}:{s}"
