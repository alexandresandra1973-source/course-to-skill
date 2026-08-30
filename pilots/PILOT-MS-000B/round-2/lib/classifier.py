#!/usr/bin/env python3
"""ROUND 2 — CORRECAO 4: classificador com TRES classes.

Defeito da ROUND 1: o consolidador tinha so PASS|FAIL e nao implementava o ramo
INVALID que o Opening Record declarava.

Regra:
  INVALID  instrumento ou metodologia invalidos  -> tem PRECEDENCIA sobre FAIL,
           porque um instrumento quebrado nao pode reprovar o produto
  KILL     violacao de KILL-1/2/3 com instrumento valido
  FAIL     instrumento valido, produto/corpus viola criterio
  PASS     tudo valido
"""
from __future__ import annotations

INSTRUMENT_GATES = ("tokenizer_controls", "isolation_controls", "judge_controls",
                    "consolidator_controls", "trace_completo", "config_identica",
                    "dentro_do_cap")
KILL_GATES       = ("kill1", "kill2", "kill3")
PRODUCT_GATES    = ("identity", "provenance", "workflow", "blocking", "isolation")

def classify(gates: dict):
    bad_i = [g for g in INSTRUMENT_GATES if g in gates and not gates[g]]
    if bad_i:
        return "PILOT_MS_000B_ROUND_2_INVALID", {"motivo": "instrumento/metodologia invalidos",
                                                 "portoes": bad_i}
    bad_k = [g for g in KILL_GATES if g in gates and not gates[g]]
    if bad_k:
        return "PILOT_MS_000B_FAIL", {"motivo": "KILL violado com instrumento valido",
                                      "portoes": bad_k}
    bad_p = [g for g in PRODUCT_GATES if g in gates and not gates[g]]
    if bad_p:
        return "PILOT_MS_000B_FAIL", {"motivo": "instrumento valido; produto/corpus viola criterio",
                                      "portoes": bad_p}
    return "PILOT_MS_000B_PASS", {"motivo": "todos os portoes validos", "portoes": []}
