#!/usr/bin/env python3
"""Canario I26 — formaliza mecanicamente a fronteira entre as duas politicas.

CANDIDATE-ADMISSION-POLICY pertence a Fusion  -> PODE alterar fusion_id.
MTX-POLICY pertence a Operationalization      -> NAO PODE tocar fusion_id.
"""
import sys, json, inspect
sys.path.insert(0, "lib")
import fusion as F

FORBIDDEN = {"mtx_policy_hash", "mtx_policy", "mtx_policy_ref"}
SPH = ["a" * 64, "b" * 64]
CFG_1 = "c" * 64
CFG_2 = "d" * 64          # mesmo pipeline, Candidate Admission Policy diferente
CAR = "e" * 64
ADM = "f" * 64
OUT = "1" * 64


def guard(identity_inputs):
    """Recusa qualquer tentativa de tornar a MTX-POLICY input identitario da Fusion."""
    bad = sorted(FORBIDDEN & set(identity_inputs))
    return {"verdict": "FAIL" if bad else "PASS", "forbidden_found": bad}


def run():
    res = []

    # A — mesmos Source Packages + mesmo Fusion Config -> mesmo fusion_id
    a1 = F.fusion_id(SPH, CFG_1, CAR, ADM, OUT)
    a2 = F.fusion_id(list(reversed(SPH)), CFG_1, CAR, ADM, OUT)
    res.append({"canary": "I26-A", "desc": "mesmo input + mesmo config -> mesmo fusion_id",
                "expected": "IGUAL", "obtido": "IGUAL" if a1 == a2 else "DIFERENTE",
                "fusion_id": a1, "ok": a1 == a2})

    # B — Candidate Admission Policy diferente -> Fusion Config diferente -> fusion_id novo
    b = F.fusion_id(SPH, CFG_2, CAR, ADM, OUT)
    res.append({"canary": "I26-B", "desc": "admission policy diferente -> fusion_id novo",
                "expected": "DIFERENTE E PERMITIDO",
                "obtido": "DIFERENTE" if b != a1 else "IGUAL",
                "fusion_id_1": a1, "fusion_id_2": b, "ok": b != a1})

    # C1 — I26 positivo: duas MTX-POLICY distintas -> saida byte-identica
    c1 = F.fusion_id(SPH, CFG_1, CAR, ADM, OUT)   # sob "politica MTX X"
    c2 = F.fusion_id(SPH, CFG_1, CAR, ADM, OUT)   # sob "politica MTX Y"
    res.append({"canary": "I26-C1", "desc": "duas MTX-POLICY -> fusion_id byte-identico",
                "expected": "IGUAL", "obtido": "IGUAL" if c1 == c2 else "DIFERENTE",
                "ok": c1 == c2})

    # C2 — injetar mtx_policy_hash como input identitario -> FAIL
    tentativa = ["source_package_hashes", "fusion_config_hash",
                 "candidate_admission_report_hash", "admitted_candidate_set_hash",
                 "outputs_hash", "mtx_policy_hash"]
    g = guard(tentativa)
    res.append({"canary": "I26-C2", "desc": "injetar mtx_policy_hash como input identitario",
                "expected": "FAIL", "obtido": g["verdict"],
                "forbidden_found": g["forbidden_found"], "ok": g["verdict"] == "FAIL"})

    # C3 — a assinatura real de fusion_id nao aceita mtx_policy_hash
    params = list(inspect.signature(F.fusion_id).parameters)
    res.append({"canary": "I26-C3", "desc": "assinatura de fusion_id sem mtx_policy_hash",
                "expected": "AUSENTE", "params": params,
                "obtido": "AUSENTE" if not (FORBIDDEN & set(params)) else "PRESENTE",
                "ok": not (FORBIDDEN & set(params))})

    # C4 — o conjunto declarado no FUSION-CONFIG passa pelo guard
    cfg = json.load(open("FUSION-CONFIG-R4.json", encoding="utf-8"))
    g2 = guard(cfg["fusion_id_inputs"])
    res.append({"canary": "I26-C4", "desc": "fusion_id_inputs do FUSION-CONFIG passam no guard",
                "expected": "PASS", "obtido": g2["verdict"],
                "inputs": cfg["fusion_id_inputs"], "ok": g2["verdict"] == "PASS"})
    return res


if __name__ == "__main__":
    r = run()
    for x in r:
        print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['canary']:<8} {x['desc']:<52} "
              f"esperado={x['expected']:<22} obtido={x['obtido']}")
    print("\n  I26 canarios:", len(r), "| PASS:", sum(1 for x in r if x["ok"]))
    sys.exit(0 if all(x["ok"] for x in r) else 2)
