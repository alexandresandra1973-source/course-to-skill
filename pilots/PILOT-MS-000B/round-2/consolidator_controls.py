#!/usr/bin/env python3
"""ROUND 2 — controles do CLASSIFICADOR com fixtures sinteticas. Zero modelo.

Se nao distinguir FAIL de INVALID, a Round 2 NAO abre.
"""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "lib"))
from classifier import classify, INSTRUMENT_GATES, KILL_GATES, PRODUCT_GATES

ALL_OK = {g: True for g in INSTRUMENT_GATES + KILL_GATES + PRODUCT_GATES}
FIXTURES = [
  ("FX-PASS",    ALL_OK,                                     "PILOT_MS_000B_PASS"),
  ("FX-FAIL",    {**ALL_OK, "isolation": False},              "PILOT_MS_000B_FAIL"),
  ("FX-FAIL-2",  {**ALL_OK, "provenance": False},             "PILOT_MS_000B_FAIL"),
  ("FX-KILL",    {**ALL_OK, "kill3": False},                  "PILOT_MS_000B_FAIL"),
  ("FX-INVALID", {**ALL_OK, "judge_controls": False},         "PILOT_MS_000B_ROUND_2_INVALID"),
  ("FX-INVALID-2",{**ALL_OK, "tokenizer_controls": False},    "PILOT_MS_000B_ROUND_2_INVALID"),
  # PRECEDENCIA: instrumento quebrado E produto quebrado -> INVALID, nunca FAIL
  ("FX-PRECED",  {**ALL_OK, "judge_controls": False, "isolation": False},
                                                              "PILOT_MS_000B_ROUND_2_INVALID"),
]
def run():
    R=[]
    for cid, gates, esperado in FIXTURES:
        got,_ = classify(gates)
        R.append({"fixture": cid, "esperado": esperado, "obtido": got, "ok": got == esperado})
    return {"fixtures": R, "ok": all(x["ok"] for x in R)}

if __name__ == "__main__":
    R = run()
    for x in R["fixtures"]:
        print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['fixture']:<12} esperado={x['esperado']:<32} obtido={x['obtido']}")
    print(f"\n  consolidator controls: {'PASS' if R['ok'] else 'FAIL'}")
    sys.exit(0 if R["ok"] else 2)
