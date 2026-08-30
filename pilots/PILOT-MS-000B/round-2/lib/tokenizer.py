#!/usr/bin/env python3
"""ROUND 2 — CORRECAO 1: tokenizador.

Defeito da ROUND 1: o padrao admitia '.' dentro do token, entao pontuacao terminal
grudava na palavra (github. != github).

Correcao por PROPRIEDADE, nao por ajuste ao resultado: pontuacao PERIFERICA e
removida; estrutura INTERNA de tokens tecnicos e preservada.
"""
from __future__ import annotations
import re, unicodedata

WS   = re.compile(r"\s+")
CAND = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-_/\.:]*")
# pontuacao periferica: removida das PONTAS apenas
PERIPH = ".,;:!?)]}\"'`»…"
PERIPH_L = "([{\"'`«"

STOP = set("""a an the of to in on for with and or is are was were be been being this that these those
it its as at by from into over under after before while when where how what which who whom your you
we our they their he she his her i me my do does did done can could should would may might must will
shall not no nor if then than so such very just also only own same too s t don now there here all
any both each few more most other some get got go going make made use used using want need like
here's there's let's you're we're it's that's here we you i""".split())

def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").casefold()
    return WS.sub(" ", s).strip()

def strip_periph(t: str) -> str:
    """Remove pontuacao das PONTAS. Preserva o interior: caminhos, opcoes, versoes."""
    while t and t[0] in PERIPH_L: t = t[1:]
    while t and t[-1] in PERIPH:  t = t[:-1]
    return t

def content_tokens(s: str) -> set:
    out = set()
    for raw in CAND.findall(norm(s)):
        t = strip_periph(raw)
        if len(t) < 3 or t in STOP or t.isdigit(): continue
        out.add(t)
    return out
