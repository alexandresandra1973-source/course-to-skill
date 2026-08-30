#!/usr/bin/env python3
"""Constroi as duas fixtures de controle. NAO mede nada.

Positivo: quote copiada VERBATIM de um trecho real do L0 do P002.
Negativo: a MESMA quote com uma alteracao deliberada.
As duas vivem FORA da populacao (nenhum evidence_id real e usado).
"""
import json, pathlib, hashlib

REPO = pathlib.Path("/home/mtx/course-to-skill-claude")
L0 = REPO / "_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt"
raw = L0.read_text(encoding="utf-8")

# trecho real, recortado por offset fixo de bytes de texto (deterministico)
start = raw.index("This course is designed")
snippet = raw[start:start + 96]                       # verbatim, sem tocar

positivo = snippet
negativo = snippet.replace("designed", "ENGINEERED_XQZ")   # alteracao deliberada
assert negativo != positivo, "fixture negativa nao foi alterada"

cases = [
    {"fixture_id": "FX-POS-001", "l0": str(L0), "quote": positivo,
     "expect": "PASS",
     "porque": "quote copiada verbatim de trecho real do L0 do P002"},
    {"fixture_id": "FX-NEG-001", "l0": str(L0), "quote": negativo,
     "expect": "FAIL",
     "porque": "mesma quote com 'designed' -> 'ENGINEERED_XQZ'; nao existe no L0"},
]
out = pathlib.Path(__file__).parent / "fixtures" / "fixture-cases.json"
out.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("fixtures escritas:", out)
print("  L0 usado :", L0)
print("  L0 sha256:", hashlib.sha256(L0.read_bytes()).hexdigest())
for c in cases:
    print(f"  {c['fixture_id']}  expect={c['expect']}  quote[:60]={c['quote'][:60]!r}")
