"""Pré-classificação das evidências. RODA ANTES DE QUALQUER REGRA SER FORMADA.

Sem isto o avaliador penaliza o curso pelo que o ASR estragou: no L0 do
PILOT-002, 133 de 146 menções (91,1%) ao produto central estão corrompidas.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

sys.path.insert(0, "/home/mtx/course-to-skill-claude")
from scan_source_corruption import lost_negation, corrupted_name      # noqa: E402
from detector_recall_fix import corrupted_name_lower                  # noqa: E402

# Aliases DECLARADOS por medição, não por similaridade. Cada um é um nome
# central do curso que o ASR corrompe sistematicamente, e a corrupção é severa
# demais para casar por similaridade (claude~claw = 0,60; roas~rows = 0,50).
#   PILOT-002: 133 de 146 menções (91,1%) a "Claude" corrompidas.
#   PILOT-003: 11 de 12 menções (91,7%) a "ROAS" saem como "rows"/"roads".
ALIAS = {"Claude": re.compile(r"\b(clawed|claw|clod|cloud|clawd|clode|clot)\b", re.I),
         "ROAS": re.compile(r"\b(rows|roads|row)\b", re.I)}
PATH2_REJECTED = {("Explorer", "explore"), ("Termos", "terms"),
                  ("Agentes", "Agents"), ("Agentes", "agents")}


def classify(r: dict, paraphrase_ids: set[str]) -> tuple[str, str | None]:
    if r["epistemic_status"] == "SOURCE_EXPLICIT":
        return "SOURCE_EXPLICIT", None
    claim, quote = r["claim"], r["source_excerpt"]["quote"]
    d = lost_negation(claim, quote) or corrupted_name(claim, quote)
    if d:
        return "TRANSCRIPTION_CORRECTION", f"P1:{d['tipo']}"
    d2 = corrupted_name_lower(claim, quote)
    if d2 and (d2["nome_na_claim"], d2["quase_igual_na_quote"]) not in PATH2_REJECTED:
        return "TRANSCRIPTION_CORRECTION", f"P2:{d2['tipo']}"
    for name, rx in ALIAS.items():
        if name.lower() in claim.lower() and rx.search(quote) \
           and name.lower() not in quote.lower():
            return "TRANSCRIPTION_CORRECTION", f"P3:ALIAS:{name}"
    if r["evidence_id"] in paraphrase_ids:
        return "PARAPHRASE", "P4:sem distância medida da citação"
    return "GENUINE_INFERENCE", None


def classify_all(rows: list[dict], paraphrase_ids: set[str]) -> dict:
    out = {}
    for r in rows:
        cls, why = classify(r, paraphrase_ids)
        out[r["evidence_id"]] = {"origin_class": cls, "why": why}
    return out
