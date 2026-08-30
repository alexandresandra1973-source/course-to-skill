#!/usr/bin/env python3
"""MS-000B — TARGETED IDENTITY REWRITE AND REVERIFY.
NAO e Round 5. MECANICO, OFFLINE, ZERO CHAMADAS DE MODELO.
Le os seis Source Packages selados da Round 3 como READ-ONLY. Nunca escreve neles."""
import sys, json, hashlib, pathlib, collections

HERE = pathlib.Path(__file__).resolve().parent
MS = HERE.parent
R3 = MS / "round-3"
R4 = MS / "round-4"
sys.path.insert(0, str(HERE / "lib"))
sys.path.insert(0, str(R3))
sys.path.insert(0, str(MS.parent / "PILOT-MS-000A"))
import typedref as T, admission as A, fusion as F
from lib import package as P
import seal_verifier as SV

PKGS = R3 / "out/packages"
REG = PKGS / "EXTERNAL-SEAL-REGISTRY.txt"
OUT = HERE / "out"
FUSDIR = OUT / "fusion"
RUNS = ("RUN-1", "RUN-2", "RUN-3")
SRC = ("A", "B")
ERRATA = MS.parent.parent / "_mirror/docs/architecture/ARCHITECTURE-FREEZE-ERRATA-IDENTITY-QUALIFICATION-v1.md"
MODEL_CALLS = 0


def sha_file(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def key(r): return (r["source_package_hash"], r["entity_kind"], r["local_id"])


def pkg_state(d):
    return {"source_package_hash": P.source_package_hash(P.member_manifest(d)),
            "seal": SV.verify(d, external_registry=REG, toolchain_dir=d)["verdict"],
            "completeness": P.completeness_gate(d)["verdict"],
            "seal_record_hash": sha_file(d / "SEAL-RECORD.yaml")}


def walk_refs(o, path=""):
    """Toda ref persistida: distingue tipada de 2-tupla nua."""
    if isinstance(o, dict):
        if {"source_package_hash", "local_id"} <= set(o):
            yield (path, o, T.is_typed(o))
        for k, v in o.items(): yield from walk_refs(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        if len(o) == 2 and all(isinstance(x, str) for x in o) and len(o[0]) == 64:
            yield (path, o, False)          # 2-tupla nua
        for x in o: yield from walk_refs(x, path)


def main():
    OUT.mkdir(exist_ok=True); FUSDIR.mkdir(exist_ok=True)
    R = {"operation": "TARGETED_IDENTITY_REWRITE_AND_REVERIFY", "model_calls": MODEL_CALLS,
         "not_a_round": True, "policy_version": A.POLICY_VERSION,
         "typed_reference_schema_version": T.SCHEMA_VERSION}

    # ---- 1. ANTES ------------------------------------------------------
    before = {f"{r}/{k}": pkg_state(PKGS / r / f"pkg-{k}") for r in RUNS for k in SRC}
    R["source_packages_before"] = before
    R["registry_before"] = sha_file(REG)

    # ---- 2. canarios de identidade + I26 --------------------------------
    import identity_canaries, i26_canary
    idc = identity_canaries.run()
    i26 = i26_canary.run()
    R["identity_canaries"] = idc; R["i26_canaries"] = i26

    # ---- 3. ADMISSION v0.2 ----------------------------------------------
    adm_all, cand_all, tbl = {}, {}, {}
    for r in RUNS:
        adm_all[r], cand_all[r], tbl[r] = {}, {}, {}
        for k in SRC:
            d = PKGS / r / f"pkg-{k}"
            sph = before[f"{r}/{k}"]["source_package_hash"]
            cand = json.loads((d / "SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
            ev = {json.loads(l)["local_id"] for l in (d / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
            cl = {json.loads(l)["local_id"] for l in (d / "CLAIMS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
            recs = A.admit_package(cand, ev, cl, sph)
            adm_all[r][k] = recs; cand_all[r][k] = cand
            bk = collections.defaultdict(lambda: {"received": 0, "admitted": 0, "rejected": 0,
                                                  "reasons": collections.Counter()})
            for x in recs:
                b = bk[x["entity_kind"]]; b["received"] += 1
                b["admitted" if x["state"] == "ADMITTED" else "rejected"] += 1
                for z in x["reasons"]: b["reasons"][z] += 1
            tbl[r][k] = {kk: {"received": v["received"], "admitted": v["admitted"],
                              "rejected": v["rejected"], "reasons": dict(v["reasons"])}
                         for kk, v in bk.items()}
            tbl[r][k]["TOTAL"] = {"received": len(recs),
                "admitted": sum(1 for x in recs if x["state"] == "ADMITTED"),
                "rejected": sum(1 for x in recs if x["state"] != "ADMITTED"),
                "reasons": dict(collections.Counter(z for x in recs for z in x["reasons"]))}
            F.wjson(OUT / f"CANDIDATE-ADMISSION-REPORT-{r}-{k}.json",
                    {"source_package_hash": sph, "policy_version": A.POLICY_VERSION,
                     "typed_reference_schema_version": T.SCHEMA_VERSION,
                     "records": recs, "by_kind": tbl[r][k]})
    R["admission_table"] = tbl

    # ---- 4. FUSION com refs TIPADAS -------------------------------------
    cfg_hash = sha_file(HERE / "FUSION-CONFIG-IDENTITY-REVERIFY.json")
    pol_hash = sha_file(HERE / "CANDIDATE-ADMISSION-POLICY-v0.2.json")
    err_hash = sha_file(ERRATA)
    fus = {}
    for r in RUNS:
        pops = {"rules": [], "workflows": [], "anti_patterns": []}
        adm_refs, rej_refs, prov = [], [], []
        for k in SRC:
            sph = before[f"{r}/{k}"]["source_package_hash"]
            m = F.materialize(cand_all[r][k], adm_all[r][k], sph)
            for p in pops: pops[p] += m[p]
            for x in adm_all[r][k]:
                (adm_refs if x["state"] == "ADMITTED" else rej_refs).append(x["qualified_ref"])
                if x["state"] == "ADMITTED":
                    prov.append({"element_ref": x["qualified_ref"],
                                 "source_id": json.loads((PKGS / r / f"pkg-{k}" / "SOURCE-PROFILE.json").read_text(encoding="utf-8"))["source_id"],
                                 "source_package_hash": sph,
                                 "seal_record_hash": before[f"{r}/{k}"]["seal_record_hash"],
                                 "lineage": "candidate_refs"})
        car = {k: {"source_package_hash": before[f"{r}/{k}"]["source_package_hash"],
                   "records": adm_all[r][k], "by_kind": tbl[r][k]} for k in SRC}
        car_h = F.sha_text(F.canon(car))
        set_h = F.sha_text(F.canon(sorted(adm_refs, key=lambda x: (x["source_package_hash"], x["entity_kind"], x["local_id"]))))
        out_h = F.sha_text(F.canon(pops))
        fid = F.fusion_id([before[f"{r}/{k}"]["source_package_hash"] for k in SRC],
                          cfg_hash, car_h, set_h, out_h, err_hash)
        srt = lambda L: sorted(L, key=lambda x: (x["source_package_hash"], x["entity_kind"], x["local_id"]))
        fp = {"artifact_id": f"MS000B-IDENTITY-REVERIFY-FUSION-PACKAGE-{r}",
              "fusion_id": fid,
              "identity_model": "GLOBAL_OBJECT_IDENTITY = (source_package_hash, entity_kind, local_id)",
              "identity_errata_hash": err_hash,
              "typed_reference_schema_version": T.SCHEMA_VERSION,
              "candidate_admission_policy_version": A.POLICY_VERSION,
              "candidate_admission_policy_hash": pol_hash,
              "fusion_config_hash": cfg_hash,
              "participating_source_package_hashes":
                  sorted(before[f"{r}/{k}"]["source_package_hash"] for k in SRC),
              "seals_verified": {f"pkg-{k}": before[f"{r}/{k}"]["seal"] for k in SRC},
              "candidate_admission_report_hash": car_h,
              "admitted_candidate_set_hash": set_h, "outputs_hash": out_h,
              "mtx_policy_hash": None,
              "nota_I26": "mtx_policy_hash ausente por contrato; a Candidate Admission Policy entra via FUSION-CONFIG",
              "admitted_candidate_refs": srt(adm_refs),
              "rejected_candidate_refs_NOT_CONSUMABLE": srt(rej_refs),
              "consumability_note": "SOMENTE admitted_candidate_refs sao consumiveis; a lista de rejeitados existe para auditabilidade, em estado NOT_CONSUMABLE",
              "candidate_admission_report": car, "fusion": pops,
              "provenance_ledger": prov,
              "source_independence": {k: "KNOWN_DEPENDENT" for k in SRC},
              "conflict_state": "NOT_APPLICABLE", "relation_policy": "NOT_APPLIED"}
        F.wjson(FUSDIR / f"fusion-package-IDENTITY-{r}.json", fp)
        fus[r] = {"fusion_id": fid}
    R["fusion"] = fus

    # ---- 5. TRANSPORTE: releitura do disco -------------------------------
    STRUCT = {"rules": ("rule_candidates", F.rule_structure),
              "workflows": ("workflow_candidates", F.workflow_structure),
              "anti_patterns": ("anti_pattern_candidates", F.anti_pattern_structure)}
    trans, leaks, untyped = {}, [], []
    for r in RUNS:
        back = json.loads((FUSDIR / f"fusion-package-IDENTITY-{r}.json").read_text(encoding="utf-8"))
        rejk = {key(x) for x in back["rejected_candidate_refs_NOT_CONSUMABLE"]}
        untyped += [[r, p] for p, o, ok in walk_refs(back) if not ok]
        trans[r] = {}
        for pop, (kind, proj) in STRUCT.items():
            rows = []
            for item in back["fusion"][pop]:
                ref = item["candidate_ref"]
                if key(ref) in rejk: leaks.append([r, pop, ref])
                k = next(kk for kk in SRC if before[f"{r}/{kk}"]["source_package_hash"] == ref["source_package_hash"])
                d = PKGS / r / f"pkg-{k}"
                src = next(x for x in json.loads((d / "SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))[kind]
                           if x["local_id"] == ref["local_id"])
                sh = F.sha_text(F.canon(proj(src)))       # do arquivo SELADO
                fh = F.sha_text(F.canon(item["structure"]))  # do arquivo RELIDO
                row = {"ref": ref, "source_structure_hash": sh, "fusion_structure_hash": fh,
                       "preservado": sh == fh, "transformation": item["transformation"],
                       "source_file": str(d / "SOURCE-LOCAL-CANDIDATES.json"),
                       "fusion_file": str(FUSDIR / f"fusion-package-IDENTITY-{r}.json")}
                if pop == "workflows":
                    row["n_steps_source"] = len(src.get("steps") or [])
                    row["n_steps_fusion"] = len(item["structure"].get("steps") or [])
                if pop == "rules":
                    row["precedence_source"] = src.get("precedence")
                    row["precedence_fusion"] = item["structure"].get("precedence")
                    row["adjudication"] = item["adjudication"]
                rows.append(row)
            trans[r][pop] = rows
    R["transport"] = trans; R["rejected_leaks"] = leaks; R["untyped_refs"] = untyped

    # ---- 6. disjuncao e ambiguidade sobre o PERSISTIDO -------------------
    dis, ambig = [], []
    idx_all = set()
    for r in RUNS:
        for k in SRC:
            sph = before[f"{r}/{k}"]["source_package_hash"]
            for x in adm_all[r][k]: idx_all.add(key(x["qualified_ref"]))
    for r in RUNS:
        back = json.loads((FUSDIR / f"fusion-package-IDENTITY-{r}.json").read_text(encoding="utf-8"))
        a = {key(x) for x in back["admitted_candidate_refs"]}
        b = {key(x) for x in back["rejected_candidate_refs_NOT_CONSUMABLE"]}
        dis.append({"run": r, "n_admitted": len(a), "n_rejected": len(b),
                    "intersecao": len(a & b), "disjuntos": not (a & b)})
        for p, o, ok in walk_refs(back):
            if ok:
                res = T.resolve(o, {kk: 1 for kk in idx_all})
                if res["state"] == "AMBIGUOUS_REF": ambig.append([r, p, o])
    R["disjointness"] = dis; R["ambiguous_refs"] = ambig

    # ---- 7. canarios reais no corpus ------------------------------------
    real = {"passo_unico": [], "precedence_undefined": [], "anti_pattern": []}
    for r in RUNS:
        widx = {key(x["ref"]): x for x in trans[r]["workflows"]}
        ridx = {key(x["ref"]): x for x in trans[r]["rules"]}
        aidx = {key(x["ref"]): x for x in trans[r]["anti_patterns"]}
        for k in SRC:
            sph = before[f"{r}/{k}"]["source_package_hash"]
            arec = {(x["entity_kind"], x["local_id"]): x for x in adm_all[r][k]}
            c = cand_all[r][k]
            for w in c["workflow_candidates"]:
                if len(w["steps"]) != 1: continue
                a = arec[("workflow_candidate", w["local_id"])]
                t = widx.get((sph, "workflow_candidate", w["local_id"]))
                real["passo_unico"].append({"run": r, "src": k, "local_id": w["local_id"],
                    "state": a["state"], "defects": a["inherited_defects"],
                    "steps_fusion": t["n_steps_fusion"] if t else None,
                    "hash": t["preservado"] if t else None,
                    "ok": a["state"] == "ADMITTED" and t and t["preservado"]
                          and t["n_steps_fusion"] == 1 and "PASSO_UNICO" in a["inherited_defects"]})
            for ru in c["rule_candidates"]:
                if ru.get("precedence") not in (None, "UNDEFINED"): continue
                a = arec[("rule_candidate", ru["local_id"])]
                t = ridx.get((sph, "rule_candidate", ru["local_id"]))
                real["precedence_undefined"].append({"run": r, "src": k, "local_id": ru["local_id"],
                    "state": a["state"], "precedence_fusion": t["precedence_fusion"] if t else None,
                    "adjudicado": (t["adjudication"] is not None) if t else None,
                    "hash": t["preservado"] if t else None,
                    "ok": a["state"] == "ADMITTED" and t and t["preservado"]
                          and t["precedence_fusion"] == "UNDEFINED" and t["adjudication"] is None})
            for ap in c["anti_pattern_candidates"]:
                a = arec[("anti_pattern_candidate", ap["local_id"])]
                t = aidx.get((sph, "anti_pattern_candidate", ap["local_id"]))
                real["anti_pattern"].append({"run": r, "src": k, "local_id": ap["local_id"],
                    "state": a["state"], "reasons": a["reasons"],
                    "na_fusion": t is not None, "hash": t["preservado"] if t else None,
                    "ref": a["qualified_ref"],
                    "ok": (a["state"] == "ADMITTED" and t and t["preservado"])
                          or (a["state"] != "ADMITTED" and t is None)})
    R["real_canaries"] = {kk: {"n": len(v), "ok": all(x["ok"] for x in v) and len(v) > 0,
                               "casos": v} for kk, v in real.items()}

    # ---- 8. DEPOIS -------------------------------------------------------
    after = {f"{r}/{k}": pkg_state(PKGS / r / f"pkg-{k}") for r in RUNS for k in SRC}
    R["source_packages_after"] = after
    R["registry_after"] = sha_file(REG)
    R["source_packages_intact"] = before == after and R["registry_before"] == R["registry_after"]

    idc8 = identity_canaries.run(before, after)
    R["identity_canaries"] = idc8
    F.wjson(OUT / "identity-canaries.json", idc8)
    F.wjson(OUT / "i26-canaries.json", i26)

    # ---- 9. portoes ------------------------------------------------------
    allt = [x for r in RUNS for p in trans[r] for x in trans[r][p]]
    admn = sum(tbl[r][k]["TOTAL"]["admitted"] for r in RUNS for k in SRC)
    g = {
     "errata_registrada": ERRATA.is_file(),
     "identity_canaries_ID1_ID8": all(x["ok"] for x in idc8),
     "i26": all(x["ok"] for x in i26),
     "source_packages_intact": R["source_packages_intact"],
     "typed_qualification_zero_collisions": not R["ambiguous_refs"],
     "todas_refs_derivadas_tipadas": not untyped,
     "admitted_rejected_disjuntos": all(d["disjuntos"] for d in dis),
     "admitted_materializados": admn == len(allt),
     "rejected_nao_consumidos": not leaks,
     "transporte_preservado": all(x["preservado"] for x in allt),
     "objetos_distintos": all(x["source_file"] != x["fusion_file"] for x in allt),
     "real_passo_unico": R["real_canaries"]["passo_unico"]["ok"],
     "real_precedence_undefined": R["real_canaries"]["precedence_undefined"]["ok"],
     "anti_pattern_outcome_medido": R["real_canaries"]["anti_pattern"]["ok"],
     "fusion_id_sem_mtx_policy": all(
        json.loads((FUSDIR / f"fusion-package-IDENTITY-{r}.json").read_text(encoding="utf-8"))["mtx_policy_hash"] is None
        for r in RUNS),
     "zero_model_calls": MODEL_CALLS == 0,
    }
    R["gates"] = g
    R["classificacao"] = ("MS_000B_TYPED_IDENTITY_REVERIFY_PASS" if all(g.values())
                          else "MS_000B_TYPED_IDENTITY_REVERIFY_FAIL")
    R["portoes_falhos"] = [k for k, v in g.items() if not v]
    F.wjson(OUT / "summary.json", R)
    print(f"\n  admitidos={admn} materializados={len(allt)} vazamentos={len(leaks)} "
          f"refs_nao_tipadas={len(untyped)} refs_ambiguas={len(R['ambiguous_refs'])}")
    for k, v in g.items(): print(f"  {'OK  ' if v else 'FALHA'} {k}")
    print(f"\n  {R['classificacao']}")
    return 0 if all(g.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
