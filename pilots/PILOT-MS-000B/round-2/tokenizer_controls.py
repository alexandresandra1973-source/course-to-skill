#!/usr/bin/env python3
"""ROUND 2 — controles MECANICOS do tokenizador, PRE-DECLARADOS.

O blocker so entra na avaliacao depois que estes controles passarem.
Zero chamadas de modelo.
"""
from __future__ import annotations
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent / "lib"))
from tokenizer import content_tokens

# --- POSITIVE EQUIVALENCE: formas que DEVEM produzir o mesmo token
POSITIVE = [
    ("PEQ-01", ["github", "github.", "github,", "(github)", "github:", "github;", "'github'"], "github"),
    ("PEQ-02", ["repository", "repository.", "repository,", "[repository]"], "repository"),
    ("PEQ-03", ["commit", "commit!", "commit?", "\"commit\""], "commit"),
    ("PEQ-04", ["remote", "remote.", "«remote»"], "remote"),
]
# --- NEGATIVE: formas distintas que NAO podem colapsar indevidamente
NEGATIVE = [
    ("NEG-01", "knowledge/decision-rules.yaml", "decision-rules", "caminho nao colapsa no nome do arquivo"),
    ("NEG-02", "--dangerously-skip-permissions", "permissions", "opcao completa nao colapsa no radical"),
    ("NEG-03", "claude.md", "claude", "nome de arquivo com extensao nao colapsa no radical"),
    ("NEG-04", "v0.2.1", "v0", "versao interna preservada"),
    ("NEG-05", "github.com", "github", "dominio nao colapsa no nome"),
]

def run():
    R = {"positive": [], "negative": []}
    for cid, forms, expect in POSITIVE:
        got = [sorted(content_tokens(f)) for f in forms]
        ok = all(g == [expect] for g in got)
        R["positive"].append({"control_id": cid, "formas": forms, "esperado": expect,
                              "obtido": got, "ok": ok})
    for cid, a, b, why in NEGATIVE:
        ta, tb = content_tokens(a), content_tokens(b)
        ok = ta != tb                      # nao podem ser a MESMA identidade
        R["negative"].append({"control_id": cid, "a": a, "b": b, "tokens_a": sorted(ta),
                              "tokens_b": sorted(tb), "porque": why, "ok": ok})
    R["ok"] = all(x["ok"] for x in R["positive"]) and all(x["ok"] for x in R["negative"])
    return R

if __name__ == "__main__":
    R = run()
    for x in R["positive"]:
        print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['control_id']} equivalencia -> {x['esperado']!r} : {x['obtido']}")
    for x in R["negative"]:
        print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['control_id']} {x['a']!r} != {x['b']!r} ({x['porque']})")
    print(f"\n  tokenizer controls: {'PASS' if R['ok'] else 'FAIL'}")
    sys.exit(0 if R["ok"] else 2)
