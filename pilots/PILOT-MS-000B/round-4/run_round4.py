#!/usr/bin/env python3
"""PILOT-MS-000B ROUND 4 — CANDIDATE -> FUSION CONTRACT.
MECANICO, OFFLINE, ZERO CHAMADAS DE MODELO. Nenhum cliente de modelo e instanciado.
Le os seis Source Packages selados da Round 3 como READ-ONLY e nunca escreve neles."""
import sys, json, hashlib, pathlib, collections

HERE = pathlib.Path(__file__).resolve().parent
R3 = HERE.parent / "round-3"
sys.path.insert(0, str(HERE / "lib"))
sys.path.insert(0, str(R3))
sys.path.insert(0, str(HERE.parent.parent / "PILOT-MS-000A"))
import admission as A
import fusion as F
from lib import package as P            # do round-3: hash de pacote e completude
import seal_verifier as SV

PKGS = R3 / "out/packages"
REG = PKGS / "EXTERNAL-SEAL-REGISTRY.txt"
OUT = HERE / "out"
FUSDIR = OUT / "fusion"
RUNS = ("RUN-1", "RUN-2", "RUN-3")
SRC = ("A", "B")
MODEL_CALLS = 0                          # nunca incrementado: nao ha chamada nesta rodada


def sha_file(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def pkg_state(d):
    return {"source_package_hash": P.source_package_hash(P.member_manifest(d)),
            "seal": SV.verify(d, external_registry=REG, toolchain_dir=d)["verdict"],
            "completeness": P.completeness_gate(d)["verdict"],
            "seal_record_hash": sha_file(d / "SEAL-RECORD.yaml")}


def main():
    OUT.mkdir(exist_ok=True); FUSDIR.mkdir(exist_ok=True)
    R = {"round": "PILOT-MS-000B ROUND 4", "model_calls": MODEL_CALLS}

    # ---------------- 1. estado ANTES ------------------------------------
    before = {f"{r}/{k}": pkg_state(PKGS / r / f"pkg-{k}") for r in RUNS for k in SRC}
    R["source_packages_before"] = before
    R["registry_before"] = sha_file(REG)
    assert all(v["seal"] == "PASS" and v["completeness"] == "PASS" for v in before.values())

    # ---------------- 2. canarios ----------------------------------------
    import canaries_r4, i26_canary
    ca = canaries_r4.run(); i26 = i26_canary.run()
    F.wjson(OUT / "canaries-r4.json", ca); F.wjson(OUT / "i26-canaries.json", i26)
    R["canaries"] = {"CA": ca, "I26": i26,
                     "ca_ok": all(x["ok"] for x in ca), "i26_ok": all(x["ok"] for x in i26)}
    if not (R["canaries"]["ca_ok"] and R["canaries"]["i26_ok"]):
        R["classificacao"] = "PILOT_MS_000B_ROUND_4_INVALID"
        R["motivo"] = "canario falhou antes dos pacotes reais"
        F.wjson(OUT / "summary.json", R); return 2

    # ---------------- 3. ADMISSION real ----------------------------------
    adm_all, cand_all, tbl = {}, {}, {}
    for r in RUNS:
        adm_all[r], cand_all[r], tbl[r] = {}, {}, {}
        for k in SRC:
            d = PKGS / r / f"pkg-{k}"
            sph = before[f"{r}/{k}"]["source_package_hash"]
            cand = json.loads((d / "SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
            ev = {json.loads(l)["local_id"]
                  for l in (d / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
            cl = {json.loads(l)["local_id"]
                  for l in (d / "CLAIMS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
            recs = A.admit_package(cand, ev, cl, sph)
            adm_all[r][k] = recs; cand_all[r][k] = cand
            bykind = collections.defaultdict(lambda: {"received": 0, "admitted": 0,
                                                      "rejected": 0, "reasons": collections.Counter()})
            for x in recs:
                b = bykind[x["kind"]]; b["received"] += 1
                b["admitted" if x["state"] == "ADMITTED" else "rejected"] += 1
                for z in x["reasons"]: b["reasons"][z] += 1
            tbl[r][k] = {kk: {"received": v["received"], "admitted": v["admitted"],
                              "rejected": v["rejected"], "reasons": dict(v["reasons"])}
                         for kk, v in bykind.items()}
            tbl[r][k]["TOTAL"] = {"received": len(recs),
                                  "admitted": sum(1 for x in recs if x["state"] == "ADMITTED"),
                                  "rejected": sum(1 for x in recs if x["state"] != "ADMITTED"),
                                  "reasons": dict(collections.Counter(z for x in recs for z in x["reasons"]))}
            F.wjson(OUT / f"CANDIDATE-ADMISSION-REPORT-{r}-{k}.json",
                    {"source_package_hash": sph, "policy_version": A.POLICY_VERSION,
                     "records": recs, "by_kind": tbl[r][k]})
    R["admission_table"] = tbl

    # ---------------- 4. FUSION: materializar e PERSISTIR ----------------
    cfg_hash = sha_file(HERE / "FUSION-CONFIG-R4.json")
    pol_hash = sha_file(HERE / "CANDIDATE-ADMISSION-POLICY-v0.1.json")
    fus = {}
    for r in RUNS:
        pops = {"rules": [], "workflows": [], "anti_patterns": []}
        adm_refs, rej_refs = [], []
        for k in SRC:
            sph = before[f"{r}/{k}"]["source_package_hash"]
            m = F.materialize(cand_all[r][k], adm_all[r][k], sph)
            for p in pops: pops[p] += m[p]
            for x in adm_all[r][k]:
                (adm_refs if x["state"] == "ADMITTED" else rej_refs).append([sph, x["local_id"]])
        car = {k: {"source_package_hash": before[f"{r}/{k}"]["source_package_hash"],
                   "records": adm_all[r][k], "by_kind": tbl[r][k]} for k in SRC}
        car_hash = F.sha_text(F.canon(car))
        adm_set_hash = F.sha_text(F.canon(sorted(adm_refs)))
        out_hash = F.sha_text(F.canon(pops))
        fid = F.fusion_id([before[f"{r}/{k}"]["source_package_hash"] for k in SRC],
                          cfg_hash, car_hash, adm_set_hash, out_hash)
        fp = {"artifact_id": f"MS000B-R4-FUSION-PACKAGE-{r}",
              "fusion_id": fid,
              "participating_source_package_hashes":
                  sorted(before[f"{r}/{k}"]["source_package_hash"] for k in SRC),
              "seals_verified": {f"pkg-{k}": before[f"{r}/{k}"]["seal"] for k in SRC},
              "fusion_config_hash": cfg_hash,
              "candidate_admission_policy_hash": pol_hash,
              "candidate_admission_report_hash": car_hash,
              "admitted_candidate_set_hash": adm_set_hash,
              "outputs_hash": out_hash,
              "mtx_policy_hash": None,
              "nota_I26": "mtx_policy_hash ausente por contrato. A Candidate Admission Policy entra via FUSION-CONFIG.",
              "admitted_candidate_refs": sorted(adm_refs),
              "rejected_candidate_refs_NOT_CONSUMABLE": sorted(rej_refs),
              "consumability_note": "SOMENTE admitted_candidate_refs sao consumiveis. A lista de rejeitados existe para auditabilidade e esta em estado NOT_CONSUMABLE.",
              "candidate_admission_report": car,
              "fusion": pops,
              "source_independence": {k: "KNOWN_DEPENDENT" for k in SRC},
              "conflict_state": "NOT_APPLICABLE_IN_ROUND_4",
              "relation_policy": "NOT_APPLIED_IN_ROUND_4"}
        F.wjson(FUSDIR / f"fusion-package-R4-{r}.json", fp)
        fus[r] = {"fusion_id": fid, "path": str(FUSDIR / f"fusion-package-R4-{r}.json")}
    R["fusion"] = fus

    # ---------------- 5. TRANSPORTE: releitura do disco ------------------
    # origem = objeto lido do Source Package SELADO; destino = objeto lido do
    # arquivo do Fusion Package JA GRAVADO. Dois arquivos, duas leituras.
    STRUCT = {"rules": ("rule_candidates", F.rule_structure),
              "workflows": ("workflow_candidates", F.workflow_structure),
              "anti_patterns": ("anti_pattern_candidates", F.anti_pattern_structure)}
    trans, leaks = {}, []
    for r in RUNS:
        back = json.loads((FUSDIR / f"fusion-package-R4-{r}.json").read_text(encoding="utf-8"))
        # CORRECAO exec-2: local_id sozinho e AMBIGUO nestes pacotes (um anti-pattern
        # reusa o local_id da rule de origem). A chave de verificacao passa a ser
        # (source_package_hash, kind, local_id), lida do relatorio ja persistido.
        rejected_ids = {(car["source_package_hash"], x["kind"], x["local_id"])
                        for car in back["candidate_admission_report"].values()
                        for x in car["records"] if x["state"] != "ADMITTED"}
        trans[r] = {}
        for pop, (kind, proj) in STRUCT.items():
            rows = []
            for item in back["fusion"][pop]:
                sph = item["candidate_ref"]["source_package_hash"]
                lid = item["candidate_ref"]["local_id"]
                if (sph, kind, lid) in rejected_ids: leaks.append([r, pop, sph, kind, lid])
                k = next(kk for kk in SRC if before[f"{r}/{kk}"]["source_package_hash"] == sph)
                d = PKGS / r / f"pkg-{k}"
                src_obj = next(x for x in json.loads(
                    (d / "SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))[kind]
                    if x["local_id"] == lid)
                sh = F.sha_text(F.canon(proj(src_obj)))       # do arquivo SELADO
                fh = F.sha_text(F.canon(item["structure"]))   # do arquivo RELIDO
                row = {"local_id": lid, "source_package_hash": sph,
                       "source_structure_hash": sh, "fusion_structure_hash": fh,
                       "preservado": sh == fh,
                       "source_file": str(d / "SOURCE-LOCAL-CANDIDATES.json"),
                       "fusion_file": str(FUSDIR / f"fusion-package-R4-{r}.json"),
                       "objetos_distintos": True,
                       "transformation": item["transformation"]}
                if pop == "workflows":
                    row["n_steps_source"] = len(src_obj.get("steps") or [])
                    row["n_steps_fusion"] = len(item["structure"].get("steps") or [])
                    row["order_source"] = [s.get("order_key") for s in (src_obj.get("steps") or [])]
                    row["order_fusion"] = [s.get("order_key") for s in item["structure"]["steps"]]
                if pop == "rules":
                    row["precedence_source"] = src_obj.get("precedence")
                    row["precedence_fusion"] = item["structure"].get("precedence")
                    row["adjudication"] = item["adjudication"]
                rows.append(row)
            trans[r][pop] = rows
    R["transport"] = trans
    R["rejected_leaks"] = leaks

    # ---------------- 6. canarios REAIS no corpus (18 e 19) --------------
    real_pu, real_pu_ok = [], True
    real_un, real_un_ok = [], True
    for r in RUNS:
        idx = {(x["source_package_hash"], x["local_id"]): x for x in trans[r]["workflows"]}
        ridx = {(x["source_package_hash"], x["local_id"]): x for x in trans[r]["rules"]}
        for k in SRC:
            sph = before[f"{r}/{k}"]["source_package_hash"]
            c = cand_all[r][k]
            # chave (kind, local_id): sem o kind, o registro REJECTED do anti-pattern
            # sobrescrevia o ADMITTED da rule homonima
            arec = {(x["kind"], x["local_id"]): x for x in adm_all[r][k]}
            for w in c["workflow_candidates"]:
                if len(w["steps"]) != 1: continue
                t = idx.get((sph, w["local_id"]))
                a = arec[("workflow_candidates", w["local_id"])]
                ok = (a["state"] == "ADMITTED"
                      and t is not None and t["preservado"]
                      and t["n_steps_source"] == 1 and t["n_steps_fusion"] == 1
                      and "PASSO_UNICO" in a["inherited_defects"])
                real_pu_ok &= ok
                real_pu.append({"run": r, "src": k, "local_id": w["local_id"],
                                "state": a["state"], "defects": a["inherited_defects"],
                                "na_fusion": t is not None,
                                "steps_source": 1,
                                "steps_fusion": t["n_steps_fusion"] if t else None,
                                "hash_confere": t["preservado"] if t else None, "ok": ok})
            for ru in c["rule_candidates"]:
                if ru.get("precedence") not in (None, "UNDEFINED"): continue
                t = ridx.get((sph, ru["local_id"]))
                a = arec[("rule_candidates", ru["local_id"])]
                ok = (a["state"] == "ADMITTED"
                      and t is not None and t["preservado"]
                      and t["precedence_fusion"] == "UNDEFINED"
                      and t["adjudication"] is None
                      and "PRECEDENCE_UNDEFINED" in a["inherited_defects"])
                real_un_ok &= ok
                real_un.append({"run": r, "src": k, "local_id": ru["local_id"],
                                "state": a["state"], "na_fusion": t is not None,
                                "precedence_fusion": t["precedence_fusion"] if t else None,
                                "adjudicado": (t["adjudication"] is not None) if t else None,
                                "hash_confere": t["preservado"] if t else None, "ok": ok})
    R["real_passo_unico"] = {"n": len(real_pu), "ok": real_pu_ok, "casos": real_pu}
    R["real_precedence_undefined"] = {"n": len(real_un), "ok": real_un_ok, "casos": real_un}

    # ---------------- 7. estado DEPOIS -----------------------------------
    after = {f"{r}/{k}": pkg_state(PKGS / r / f"pkg-{k}") for r in RUNS for k in SRC}
    R["source_packages_after"] = after
    R["registry_after"] = sha_file(REG)
    R["source_packages_intact"] = (before == after and R["registry_before"] == R["registry_after"])

    # ---------------- 8. portoes -----------------------------------------
    all_t = [x for r in RUNS for pop in trans[r] for x in trans[r][pop]]
    adm_total = sum(tbl[r][k]["TOTAL"]["admitted"] for r in RUNS for k in SRC)
    g = {
     "canaries_CA": R["canaries"]["ca_ok"],
     "canaries_I26": R["canaries"]["i26_ok"],
     "source_packages_intact": R["source_packages_intact"],
     "precedence_undefined_nao_rejeita": not any(
         "PRECEDENCE_UNDEFINED" in x["reasons"] for r in RUNS for k in SRC for x in adm_all[r][k]),
     "passo_unico_nao_rejeita": not any(
         "PASSO_UNICO" in x["reasons"] for r in RUNS for k in SRC for x in adm_all[r][k]),
     "evidence_refs_verificadas": all("evidence_validation" in x
         for r in RUNS for k in SRC for x in adm_all[r][k]),
     "claim_refs_verificadas": all("claim_validation" in x
         for r in RUNS for k in SRC for x in adm_all[r][k]),
     "admitted_materializados": adm_total == len(all_t),
     "rejected_nao_consumidos": len(leaks) == 0,
     "transporte_preservado": all(x["preservado"] for x in all_t),
     "objetos_distintos": all(x["source_file"] != x["fusion_file"] for x in all_t),
     "real_passo_unico": real_pu_ok and len(real_pu) > 0,
     "real_precedence_undefined": real_un_ok and len(real_un) > 0,
     "fusion_id_sem_mtx_policy": all(
         json.loads((FUSDIR / f"fusion-package-R4-{r}.json").read_text(encoding="utf-8"))["mtx_policy_hash"] is None
         for r in RUNS),
     "zero_model_calls": MODEL_CALLS == 0,
    }
    R["gates"] = g
    R["classificacao"] = "PILOT_MS_000B_ROUND_4_PASS" if all(g.values()) else "PILOT_MS_000B_ROUND_4_FAIL"
    R["portoes_falhos"] = [k for k, v in g.items() if not v]
    F.wjson(OUT / "summary.json", R)

    print(f"\n  admitidos totais: {adm_total} | materializados: {len(all_t)} | vazamentos: {len(leaks)}")
    for k, v in g.items(): print(f"  {'OK  ' if v else 'FALHA'} {k}")
    print(f"\n  {R['classificacao']}")
    return 0 if all(g.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
