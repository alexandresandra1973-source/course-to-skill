#!/usr/bin/env python3
"""CA1-CA9 — canarios da CANDIDATE ADMISSION POLICY v0.1 e do consumo pela Fusion.
Mecanicos, offline, zero modelo. Rodam ANTES dos pacotes reais.
Matriz de expectativa declarada AQUI, antes de qualquer execucao."""
import sys, json, pathlib, tempfile
sys.path.insert(0, "lib")
import admission as A
import fusion as F

EV = {f"EV-{i:04d}" for i in range(1, 11)}
CL = {f"CL-{i:04d}" for i in range(1, 6)}
SPH = "0" * 64

# ---- fixtures sinteticas -------------------------------------------------
def rule(lid, **kw):
    d = {"local_id": lid, "name": "n", "trigger": "t", "condition": "c", "action": "a",
         "do_not": [], "precedence": "UNDEFINED", "evidence_refs": []}
    d.update(kw); return d

def step(lid, order, **kw):
    d = {"local_id": lid, "order_key": order, "name": "s", "action": "a",
         "required_inputs": [], "missing_input_action": "UNDEFINED",
         "iteration_limit": "UNDEFINED", "autonomy": "UNDEFINED", "evidence_refs": []}
    d.update(kw); return d

def wf(lid, steps, **kw):
    d = {"local_id": lid, "name": "w", "evidence_refs": [], "steps": steps}
    d.update(kw); return d

def ap(lid, **kw):
    d = {"local_id": lid, "do_not": ["nao faca"], "evidence_refs": []}
    d.update(kw); return d

CASES = [
 ("CA1", "PRECEDENCE UNDEFINED", "rule_candidates",
  rule("R-CA1", precedence="UNDEFINED"), "ADMITTED", "PRECEDENCE_UNDEFINED"),
 ("CA2", "PASSO UNICO", "workflow_candidates",
  wf("W-CA2", [step("S-1", 1)]), "ADMITTED", "PASSO_UNICO"),
 ("CA3", "SEM PASSOS", "workflow_candidates",
  wf("W-CA3", []), "REJECTED_STRUCTURAL", None),
 ("CA4", "ORDEM INVALIDA", "workflow_candidates",
  wf("W-CA4", [step("S-1", 2), step("S-2", 2)]), "REJECTED_STRUCTURAL", None),
 ("CA5", "EVIDENCE REF QUEBRADA", "rule_candidates",
  rule("R-CA5", evidence_refs=["EV-9999"]), "REJECTED_STRUCTURAL", None),
 ("CA6", "ANTI-PATTERN VALIDO", "anti_pattern_candidates",
  ap("A-CA6", evidence_refs=["EV-0001"]), "ADMITTED", None),
 ("CA7", "ANTI-PATTERN EVIDENCE QUEBRADA", "anti_pattern_candidates",
  ap("A-CA7", evidence_refs=["EV-9999"]), "REJECTED_STRUCTURAL", None),
]
# canarios extras que fecham D-8: claim_ref quebrada e claim_ref valida
CASES += [
 ("CA5b", "CLAIM REF QUEBRADA", "rule_candidates",
  rule("R-CA5b", claim_refs=["CL-9999"]), "REJECTED_STRUCTURAL", None),
 ("CA5c", "CLAIM REF VALIDA", "rule_candidates",
  rule("R-CA5c", claim_refs=["CL-0001"]), "ADMITTED", "PRECEDENCE_UNDEFINED"),
]

def run():
    res = []
    for cid, desc, kind, obj, expected, want_defect in CASES:
        r = A.admit_one(kind, obj, EV, CL, set())
        ok = r["state"] == expected
        if want_defect: ok = ok and want_defect in r["inherited_defects"]
        res.append({"canary": cid, "desc": desc, "expected": expected,
                    "obtido": r["state"], "reasons": r["reasons"],
                    "defects": r["inherited_defects"],
                    "defect_esperado": want_defect, "ok": ok})

    # ---- CA8 / CA9: consumo real, com PERSISTENCIA e RELEITURA -----------
    cand = {"rule_candidates": [rule("R-CA8", precedence="UNDEFINED")],
            "workflow_candidates": [wf("W-CA8", [step("S-1", 1)]),
                                    wf("W-CA9", [])],
            "anti_pattern_candidates": [ap("A-CA8", evidence_refs=["EV-0001"])]}
    adm = A.admit_package(cand, EV, CL, SPH)
    admitted = {r["local_id"] for r in adm if r["state"] == "ADMITTED"}
    rejected = {r["local_id"] for r in adm if r["state"] == "REJECTED_STRUCTURAL"}
    mat = F.materialize(cand, adm, SPH)
    tmp = pathlib.Path(tempfile.mkdtemp()) / "fp.json"
    F.wjson(tmp, {"admitted_candidate_refs": [[SPH, l] for l in sorted(admitted)],
                  "rejected_candidate_refs_NOT_CONSUMABLE": [[SPH, l] for l in sorted(rejected)],
                  "fusion": mat})
    back = json.loads(tmp.read_text(encoding="utf-8"))     # RELEITURA do disco
    consumable = {x["candidate_ref"]["local_id"]
                  for pop in ("rules", "workflows", "anti_patterns")
                  for x in back["fusion"][pop]}
    res.append({"canary": "CA8", "desc": "ADMITTED CONSUMPTION",
                "expected": "PRESENT_AND_CONSUMABLE",
                "obtido": "PRESENT_AND_CONSUMABLE" if admitted <= consumable else "AUSENTE",
                "detalhe": {"admitidos": sorted(admitted), "consumiveis": sorted(consumable)},
                "ok": admitted <= consumable and len(admitted) > 0})
    res.append({"canary": "CA9", "desc": "REJECTED EXCLUSION",
                "expected": "NOT_CONSUMABLE",
                "obtido": "NOT_CONSUMABLE" if not (rejected & consumable) else "VAZOU",
                "detalhe": {"rejeitados": sorted(rejected),
                            "vazaram": sorted(rejected & consumable),
                            "presentes_em_namespace_de_auditoria":
                                [x[1] for x in back["rejected_candidate_refs_NOT_CONSUMABLE"]]},
                "ok": not (rejected & consumable) and len(rejected) > 0})
    tmp.unlink()
    return res


if __name__ == "__main__":
    r = run()
    for x in r:
        print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['canary']:<5} {x['desc']:<32} "
              f"esperado={x['expected']:<20} obtido={x['obtido']}")
    F.wjson("out/canaries-r4.json", r) if pathlib.Path("out").is_dir() else None
    print("\n  CA totais:", len(r), "| PASS:", sum(1 for x in r if x["ok"]),
          "| FALHA:", sum(1 for x in r if not x["ok"]))
    sys.exit(0 if all(x["ok"] for x in r) else 2)
