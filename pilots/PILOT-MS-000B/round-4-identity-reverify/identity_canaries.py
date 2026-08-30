#!/usr/bin/env python3
"""ID1-ID8 — canarios da identidade tipada. Mecanicos, offline, zero modelo.
Matriz de expectativa declarada AQUI, antes de tocar os pacotes reais."""
import sys, json, pathlib, tempfile, hashlib
sys.path.insert(0, "lib")
import typedref as T, admission as A, fusion as F

EV = {f"EV-{i:04d}" for i in range(1, 11)}
CL = {f"CL-{i:04d}" for i in range(1, 6)}
SPH = "0" * 64

rule = lambda lid: {"local_id": lid, "name": "n", "trigger": "t", "condition": "c",
                    "action": "a", "do_not": ["x"], "precedence": "UNDEFINED", "evidence_refs": []}
ap   = lambda lid: {"local_id": lid, "do_not": ["x"], "evidence_refs": []}
step = lambda lid, o: {"local_id": lid, "order_key": o, "name": "s", "action": "a",
                       "required_inputs": [], "missing_input_action": "U",
                       "iteration_limit": "U", "autonomy": "U", "evidence_refs": []}
wf   = lambda lid: {"local_id": lid, "name": "w", "evidence_refs": [], "steps": [step("S-1", 1)]}


def run(pkg_states_before=None, pkg_states_after=None):
    res = []

    # ---- ID1: mesmo local_id em kinds diferentes -> ambos validos e DISTINTOS
    cand = {"rule_candidates": [rule("R-0095")], "workflow_candidates": [],
            "anti_pattern_candidates": [ap("R-0095")]}
    recs = A.admit_package(cand, EV, CL, SPH)
    states = {r["entity_kind"]: r["state"] for r in recs}
    refs = [r["qualified_ref"] for r in recs]
    ok = (len(recs) == 2 and all(v == "ADMITTED" for v in states.values())
          and refs[0] != refs[1] and len({json.dumps(r, sort_keys=True) for r in refs}) == 2)
    res.append({"canary": "ID1", "desc": "CROSS-KIND DUPLICATE",
                "expected": "ambos validos e distintos", "obtido": states,
                "refs_distintas": refs[0] != refs[1], "ok": ok})

    # ---- ID2: mesmo (kind, local_id) duas vezes -> INVALID_IDENTITY
    cand = {"rule_candidates": [rule("R-0095"), rule("R-0095")],
            "workflow_candidates": [], "anti_pattern_candidates": []}
    recs = A.admit_package(cand, EV, CL, SPH)
    ok = (recs[0]["state"] == "ADMITTED" and recs[1]["state"] == "REJECTED_STRUCTURAL"
          and "LOCAL_ID_INVALIDO" in recs[1]["reasons"])
    res.append({"canary": "ID2", "desc": "SAME-KIND DUPLICATE",
                "expected": "REJECTED / INVALID_IDENTITY",
                "obtido": [r["state"] for r in recs], "reasons": recs[1]["reasons"], "ok": ok})

    # ---- indice tipado com a colisao real
    index = {(SPH, "rule_candidate", "R-0095"): "obj-rule",
             (SPH, "anti_pattern_candidate", "R-0095"): "obj-antipattern",
             (SPH, "evidence", "EV-0001"): "obj-ev",
             (SPH, "source_anchor", "AN-0001"): "obj-an",
             (SPH, "artifact", "ART-SLICE"): "obj-art"}

    # ---- ID3: typed ref resolve EXATAMENTE um objeto
    r1 = T.resolve(T.tref(SPH, "rule_candidate", "R-0095"), index)
    r2 = T.resolve(T.tref(SPH, "anti_pattern_candidate", "R-0095"), index)
    ok = (r1["state"] == "RESOLVED" and r1["n"] == 1 and r2["state"] == "RESOLVED"
          and r2["n"] == 1 and r1["targets"] != r2["targets"])
    res.append({"canary": "ID3", "desc": "TYPED RESOLUTION", "expected": "RESOLVED n=1",
                "obtido": {"rule": [r1["state"], r1["n"]], "anti_pattern": [r2["state"], r2["n"]]},
                "ok": ok})

    # ---- ID4: a tupla ANTIGA sobre o mesmo package -> AMBIGUOUS_REF
    u = T.resolve_untyped(SPH, "R-0095", index)
    res.append({"canary": "ID4", "desc": "OLD TUPLE AMBIGUITY", "expected": "AMBIGUOUS_REF",
                "obtido": u["state"], "n_alvos": u["n"], "ok": u["state"] == "AMBIGUOUS_REF"})

    # ---- ID5: admitted ∩ rejected = ∅ num package que SATISFAZ a unicidade congelada.
    # Fixture: colisao CROSS-KIND real (rule R-0095 + anti_pattern R-0095) mais um
    # workflow estruturalmente invalido, que da o lado rejeitado sem violar o invariante.
    def disjoint(cand):
        recs = A.admit_package(cand, EV, CL, SPH)
        adm = [r["qualified_ref"] for r in recs if r["state"] == "ADMITTED"]
        rej = [r["qualified_ref"] for r in recs if r["state"] != "ADMITTED"]
        tmp = pathlib.Path(tempfile.mkdtemp()) / "fp.json"
        F.wjson(tmp, {"admitted_candidate_refs": adm,
                      "rejected_candidate_refs_NOT_CONSUMABLE": rej})
        back = json.loads(tmp.read_text(encoding="utf-8"))     # RELEITURA do disco
        ka = {json.dumps(x, sort_keys=True) for x in back["admitted_candidate_refs"]}
        kr = {json.dumps(x, sort_keys=True) for x in back["rejected_candidate_refs_NOT_CONSUMABLE"]}
        tmp.unlink()
        return ka, kr
    bad_wf = {"local_id": "WF-BAD", "name": "w", "evidence_refs": [], "steps": []}
    ka, kr = disjoint({"rule_candidates": [rule("R-0095")],
                       "workflow_candidates": [wf("WF-1"), bad_wf],
                       "anti_pattern_candidates": [ap("R-0095")]})
    res.append({"canary": "ID5", "desc": "ADMITTED/REJECTED DISJOINT",
                "expected": "intersecao vazia", "obtido": len(ka & kr),
                "n_admitted": len(ka), "n_rejected": len(kr),
                "nota": "package satisfaz (entity_kind, local_id) unico, como a errata exige",
                "ok": not (ka & kr) and len(kr) > 0 and len(ka) > 0})

    # ---- ID5b: LIMITE DECLARADO do modelo de identidade.
    # Se o package VIOLA a unicidade same-kind, a 3-tupla NAO restaura disjuncao —
    # dois objetos distintos partilham a mesma GLOBAL_OBJECT_IDENTITY por construcao.
    # E por isso que a errata secao 3 congela a unicidade same-kind como MUST, e por
    # isso que ID2 e o portao que a faz valer. Registrado, nao contornado.
    ka2, kr2 = disjoint({"rule_candidates": [rule("R-0095"), rule("R-0095")],
                         "workflow_candidates": [], "anti_pattern_candidates": []})
    res.append({"canary": "ID5b", "desc": "SAME-KIND DUP QUEBRA DISJUNCAO",
                "expected": "intersecao NAO vazia — limite declarado",
                "obtido": len(ka2 & kr2),
                "nota": "a identidade tipada nao discrimina duplicata same-kind; a unicidade "
                        "congelada e a defesa, e ID2 e quem a aplica",
                "ok": len(ka2 & kr2) > 0})

    # ---- ID6: SELF ref schema-implied resolve
    s6 = T.resolve_self("claim.evidence_refs", {"ref_scope": "SELF", "local_id": "EV-0001"},
                        index, SPH)
    ok = s6["state"] == "RESOLVED" and s6["entity_kind_source"] == "schema-implied"
    res.append({"canary": "ID6", "desc": "SCHEMA-IMPLIED SELF", "expected": "RESOLVED",
                "obtido": s6["state"], "kind_implicado": s6.get("entity_kind"), "ok": ok})

    # ---- ID7: SELF generica, sem kind determinado -> INVALID_REF
    s7 = T.resolve_self("candidate.generic_refs", {"ref_scope": "SELF", "local_id": "R-0095"},
                        index, SPH)
    res.append({"canary": "ID7", "desc": "GENERIC SELF WITHOUT KIND", "expected": "INVALID_REF",
                "obtido": s7["state"], "why": s7.get("why"), "ok": s7["state"] == "INVALID_REF"})

    # ---- ID8: nenhuma mutacao nos Source Packages
    if pkg_states_before is None:
        res.append({"canary": "ID8", "desc": "NO SOURCE PACKAGE MUTATION",
                    "expected": "6/6 intactos", "obtido": "NAO AVALIADO nesta invocacao",
                    "ok": None})
    else:
        ok = pkg_states_before == pkg_states_after
        res.append({"canary": "ID8", "desc": "NO SOURCE PACKAGE MUTATION",
                    "expected": "6/6 intactos",
                    "obtido": "IDENTICOS" if ok else "MUTADOS", "ok": ok})
    return res


if __name__ == "__main__":
    r = run()
    for x in r:
        m = "OK  " if x["ok"] else ("----" if x["ok"] is None else "FALHA")
        print(f"  {m} {x['canary']:<4} {x['desc']:<28} esperado={str(x['expected']):<28} obtido={x['obtido']}")
    aval = [x for x in r if x["ok"] is not None]
    print(f"\n  avaliados: {len(aval)} | PASS: {sum(1 for x in aval if x['ok'])}")
    sys.exit(0 if all(x["ok"] for x in aval) else 2)
