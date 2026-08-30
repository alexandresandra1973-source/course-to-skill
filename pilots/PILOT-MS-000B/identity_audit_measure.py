#!/usr/bin/env python3
"""QUALIFIED IDENTITY NAMESPACE AUDIT — instrumento de medicao.
MECANICO, OFFLINE, READ-ONLY, zero chamadas de modelo.
Emite identity-measurements.json; a errata e o relatorio LEEM esse arquivo.
Nenhum numero e digitado a mao em documento algum."""
import json, sys, pathlib, collections, hashlib

HERE = pathlib.Path(__file__).resolve().parent
R3 = HERE / "round-3"
R4 = HERE / "round-4"
sys.path.insert(0, str(R3))
from lib import package as P

PKGS = R3 / "out/packages"
RUNS = ("RUN-1", "RUN-2", "RUN-3")
SRC = ("A", "B")

# entity_kind CANONICO — nome de schema, nao rotulo de exibicao
KINDS = ("artifact", "source_anchor", "evidence", "claim", "rule_candidate",
         "workflow_candidate", "workflow_step", "anti_pattern_candidate")


def jl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def entities(d):
    """Todo objeto enderecavel com identificador local, com seu entity_kind canonico."""
    E = []
    for a in json.loads((d / "ARTIFACTS/ARTIFACT-INDEX.json").read_text(encoding="utf-8"))["artifacts"]:
        E.append(("artifact", a["local_id"]))
    for x in jl(d / "SOURCE-ANCHORS.jsonl"): E.append(("source_anchor", x["local_id"]))
    for x in jl(d / "EVIDENCE.jsonl"):       E.append(("evidence", x["local_id"]))
    for x in jl(d / "CLAIMS.jsonl"):         E.append(("claim", x["local_id"]))
    c = json.loads((d / "SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
    for r in c["rule_candidates"]:         E.append(("rule_candidate", r["local_id"]))
    for w in c["workflow_candidates"]:
        E.append(("workflow_candidate", w["local_id"]))
        for s in w["steps"]: E.append(("workflow_step", s["local_id"]))
    for a in c["anti_pattern_candidates"]: E.append(("anti_pattern_candidate", a["local_id"]))
    return E


def main():
    M = {"instrument": "identity_audit_measure.py", "model_calls": 0,
         "entity_kinds_canonical": list(KINDS)}

    pkgs, ents = {}, {}
    for run in RUNS:
        for k in SRC:
            d = PKGS / run / f"pkg-{k}"
            sph = P.source_package_hash(P.member_manifest(d))
            pkgs[f"{run}/{k}"] = sph
            ents[f"{run}/{k}"] = entities(d)
    M["source_package_hashes"] = pkgs

    # ---- 1. inventario -------------------------------------------------
    inv = {}
    for pk, E in ents.items():
        c = collections.Counter(k for k, _ in E)
        inv[pk] = {"by_kind": {k: c[k] for k in KINDS}, "total": len(E)}
    M["inventory"] = inv
    M["total_addressable_objects"] = sum(v["total"] for v in inv.values())

    # ---- 2. unicidade sob a 2-tupla congelada --------------------------
    col2, n2, q2 = [], 0, 0
    for pk, E in ents.items():
        sph = pkgs[pk]
        byid = collections.defaultdict(list)
        for k, i in E: byid[i].append(k)
        n2 += len(E); q2 += len(byid)
        for i, ks in sorted(byid.items()):
            if len(ks) > 1:
                col2.append({"package": pk, "source_package_hash": sph, "local_id": i,
                             "kinds": sorted(ks), "n": len(ks),
                             "type": "SAME_KIND" if len(set(ks)) == 1 else "CROSS_KIND"})
    M["two_tuple"] = {"objects": n2, "distinct_tuples": q2, "collisions": n2 - q2,
                      "collision_list": col2,
                      "cross_kind": sum(1 for c in col2 if c["type"] == "CROSS_KIND"),
                      "same_kind": sum(1 for c in col2 if c["type"] == "SAME_KIND")}

    # ---- 3. unicidade sob a 3-tupla tipada -----------------------------
    n3 = q3 = 0; col3 = []
    for pk, E in ents.items():
        c = collections.Counter(E); n3 += len(E); q3 += len(c)
        col3 += [{"package": pk, "kind": k, "local_id": i, "n": v}
                 for (k, i), v in c.items() if v > 1]
    M["three_tuple"] = {"objects": n3, "distinct_tuples": q3, "collisions": n3 - q3,
                        "collision_list": col3, "same_kind": len(col3), "cross_kind": 0}
    M["verdict_typed"] = ("TYPED_QUALIFICATION_IS_UNIQUE" if n3 == q3
                          else "TYPED_QUALIFICATION_STILL_COLLIDES")

    # ---- 4. sobreposicao lexical entre kinds ---------------------------
    byk = collections.defaultdict(set)
    for E in ents.values():
        for k, i in E: byk[k].add(i)
    M["lexical_overlap"] = {f"{a}|{b}": len(byk[a] & byk[b])
                            for ai, a in enumerate(KINDS) for b in KINDS[ai + 1:]
                            if byk[a] & byk[b]}
    M["kind_set_sizes"] = {k: len(byk[k]) for k in KINDS}

    # ---- 5. a mesma tupla como consumivel E nao-consumivel na R4 -------
    both = []
    for run in RUNS:
        fp = json.loads((R4 / f"out/fusion/fusion-package-R4-{run}.json").read_text(encoding="utf-8"))
        a = {tuple(x) for x in fp["admitted_candidate_refs"]}
        r = {tuple(x) for x in fp["rejected_candidate_refs_NOT_CONSUMABLE"]}
        both += [{"run": run, "source_package_hash": t[0], "local_id": t[1]} for t in sorted(a & r)]
    M["r4_tuple_in_both_admitted_and_rejected"] = {"n": len(both), "cases": both}

    # ---- 6. refs persistidas da R4 ambiguas em isolamento ---------------
    colide = collections.defaultdict(set)
    for c in col2: colide[c["source_package_hash"]].add(c["local_id"])
    tot = amb = 0
    for run in RUNS:
        fp = json.loads((R4 / f"out/fusion/fusion-package-R4-{run}.json").read_text(encoding="utf-8"))
        for f in ("admitted_candidate_refs", "rejected_candidate_refs_NOT_CONSUMABLE"):
            for s, l in fp[f]: tot += 1; amb += l in colide[s]
        for pop in ("rules", "workflows", "anti_patterns"):
            for it in fp["fusion"][pop]:
                r = it["candidate_ref"]; tot += 1
                amb += r["local_id"] in colide[r["source_package_hash"]]
        for car in fp["candidate_admission_report"].values():
            for x in car["records"]:
                s, l = x["qualified_ref"]; tot += 1; amb += l in colide[s]
    M["r4_persisted_refs"] = {"total": tot, "ambiguous_in_isolation": amb,
                              "pct": round(amb / tot * 100, 2) if tot else 0.0}

    # ---- 7. artefatos citados ------------------------------------------
    def sh(p):
        p = pathlib.Path(p)
        return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    M["cited_artifacts"] = {
        "round-4/ROUND-4-EXEC-1-INVALID.md": sh(R4 / "ROUND-4-EXEC-1-INVALID.md"),
        "round-4/OPENING-RECORD.md": sh(R4 / "OPENING-RECORD.md"),
        "round-4/OPENING-RECORD-ADDENDUM-EXEC-2.md": sh(R4 / "OPENING-RECORD-ADDENDUM-EXEC-2.md"),
        "round-4/out/ROUND-4-VERDICT.md": sh(R4 / "out/ROUND-4-VERDICT.md"),
        "round-3/run_round3.py": sh(R3 / "run_round3.py"),
        "architecture/COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-FREEZE.md":
            sh(HERE.parent.parent / "_mirror/docs/architecture/COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-FREEZE.md"),
    }
    out = HERE / "out-identity-audit"
    out.mkdir(exist_ok=True)
    (out / "identity-measurements.json").write_text(
        json.dumps(M, sort_keys=True, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  objetos={M['total_addressable_objects']} "
          f"| 2-tupla: {M['two_tuple']['distinct_tuples']} distintas, "
          f"{M['two_tuple']['collisions']} colisoes "
          f"(cross={M['two_tuple']['cross_kind']}, same={M['two_tuple']['same_kind']})")
    print(f"  3-tupla: {M['three_tuple']['distinct_tuples']} distintas, "
          f"{M['three_tuple']['collisions']} colisoes -> {M['verdict_typed']}")
    print(f"  R4: {M['r4_tuple_in_both_admitted_and_rejected']['n']} tuplas em admitted E rejected; "
          f"{M['r4_persisted_refs']['ambiguous_in_isolation']}/{M['r4_persisted_refs']['total']} "
          f"refs ambiguas ({M['r4_persisted_refs']['pct']}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
