#!/usr/bin/env python3
"""MS-002 — calibracao MECANICA do blocker. ZERO chamadas de modelo.
Executa ANTES do juiz semantico. Nenhum output de juiz e usado aqui."""
import json, hashlib, pathlib, re, unicodedata, collections, itertools, sys
H = pathlib.Path(__file__).resolve().parent
P = H.parent
D = json.loads((H / "BLOCKER-DESIGN-MS002-v1.0.json").read_text(encoding="utf-8"))
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
DESIGN_HASH = hashlib.sha256((H / "BLOCKER-DESIGN-MS002-v1.0.json").read_bytes()).hexdigest()

STOP = set("""the a an and or of to in on for with is are was were be been being it its this that these
those you your we our they i me my he she his her as at by from not no if then than so do does did done
can could should would will just like get got make made use used using very really actually basically
okay yeah right now here there what when where who how why all any some more most other into out up down
over under again once only own same too don going want know see thing things lot gonna let also because
about which one but guys sort little time doing different something way stuff through cool well kind maybe
bunch first back probably pretty bit show every looks hey their work good look take day need say them think
o a os as um uma uns umas de do da dos das em no na nos nas por para com sem sobre e ou que se nao sim ja
mais menos muito pouco tem ter tenho temos vai vou vamos esta estao esse essa isso aqui ali la voce voces eu
nos ele ela eles elas meu minha seu sua entao porque como quando onde qual quais tudo todo toda todos todas
ai pra pro ne ta cara gente coisa jeito fazer pode agora tambem ser colocar nome vem mas caso legal criar
clica nosso clicar varios outro exemplo dessa ver usar sao passo outra desse nesse fica depois tiver pegar
pagina ficar pronto""".split())

def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

CONCEPTS = D["CHANNEL_A_FROZEN_CONCEPTS"]["conceitos"]
OBJECTS  = D["CHANNEL_B_NAMED_OBJECTS"]["objetos"]
MINLEN   = D["CHANNEL_C_CONTENT_TOKENS"]["min_len"]

def claim_text(c):
    q = c.get("qualifiers") or {}
    return " ".join([c["text"]] + [str(v) for v in q.values() if v])

def features(c):
    t = " " + norm(claim_text(c)) + " "
    conc = {k for k, al in CONCEPTS.items() if any(f" {norm(a)} " in t for a in al)}
    objs = {k for k, al in OBJECTS.items() if any(f" {norm(a)} " in t for a in al)}
    toks = {w for w in t.split() if len(w) >= MINLEN and w not in STOP}
    return {"concepts": sorted(conc), "objects": sorted(objs), "tokens": sorted(toks)}

VAR = {
 "V1": lambda a, b: len(a["C"] & b["C"]) >= 1,
 "V2": lambda a, b: len(a["O"] & b["O"]) >= 1,
 "V3": lambda a, b: len(a["C"] & b["C"]) >= 1 or len(a["O"] & b["O"]) >= 1,
 "V4": lambda a, b: len(a["C"] & b["C"]) >= 2 or len(a["O"] & b["O"]) >= 1,
 "V5": lambda a, b: len(a["C"] & b["C"]) >= 2 and len(a["O"] & b["O"]) >= 1,
 "V6": lambda a, b: len(a["C"] & b["C"]) >= 3 and len(a["O"] & b["O"]) >= 1,
 "V7": lambda a, b: len(a["C"] & b["C"]) >= 3 and len(a["O"] & b["O"]) >= 1 and len(a["T"] & b["T"]) >= 1,
}
ORDER = ["V1", "V3", "V4", "V2", "V5", "V6", "V7"]
CAP = D["CAPACIDADE_DO_JUIZ_DECLARADA"]["MAX_PAIRS_FOR_JUDGE"]

def main():
    claims, pkghash = {}, {}
    for s in "ABC":
        pkg = P / "packages" / f"pkg-{s}"
        seal = dict(l.split(": ", 1) for l in (pkg / "SEAL-RECORD.yaml").read_text(encoding="utf-8").splitlines()
                    if l.startswith("source_package_hash: "))
        pkghash[s] = seal["source_package_hash"].strip()
        rows = [json.loads(l) for l in (pkg / "CLAIMS.jsonl").read_text(encoding="utf-8").splitlines()]
        claims[s] = rows
        print(f"  fonte {s}: {len(rows)} claims SEALED · package {pkghash[s][:16]}…")
    feats = {s: {c["local_id"]: features(c) for c in claims[s]} for s in "ABC"}
    F = {s: {k: {"C": set(v["concepts"]), "O": set(v["objects"]), "T": set(v["tokens"])}
             for k, v in feats[s].items()} for s in "ABC"}

    pairs, metrics = [], {}
    combos = [("A", "B"), ("A", "C"), ("B", "C")]
    pop = 0
    for l, r in combos:
        pop += len(claims[l]) * len(claims[r])
    print(f"  populacao cross-source total: {pop} pares")

    allpairs = []
    for l, r in combos:
        for cl in claims[l]:
            for cr in claims[r]:
                a, b = F[l][cl["local_id"]], F[r][cr["local_id"]]
                allpairs.append({"lsrc": l, "rsrc": r, "l": cl["local_id"], "r": cr["local_id"],
                                 "nc": len(a["C"] & b["C"]), "no": len(a["O"] & b["O"]),
                                 "nt": len(a["T"] & b["T"]),
                                 "shared_concepts": sorted(a["C"] & b["C"]),
                                 "shared_objects": sorted(a["O"] & b["O"])})
    for v in ORDER:
        f = VAR[v]
        keep = [p for p in allpairs
                if f({"C": set(p["shared_concepts"]) or set(), "O": set(p["shared_objects"]) or set(),
                      "T": set(range(p["nt"]))},
                     {"C": set(p["shared_concepts"]) or set(), "O": set(p["shared_objects"]) or set(),
                      "T": set(range(p["nt"]))})]
        per = collections.Counter(f'{p["lsrc"]}-{p["rsrc"]}' for p in keep)
        metrics[v] = {"retained": len(keep), "retention_rate": round(len(keep) / pop, 6),
                      "per_combo": dict(per), "fits_capacity": len(keep) <= CAP}
        print(f"  {v}: retidos={len(keep):>6} ({len(keep)/pop*100:5.2f}%)  por combo={dict(per)}  cabe={len(keep)<=CAP}")

    sel = next((v for v in ORDER if metrics[v]["fits_capacity"]), None)
    sampled = False
    if sel is None:
        sel = ORDER[-1]; sampled = True
    f = VAR[sel]
    keep = [p for p in allpairs
            if f({"C": set(p["shared_concepts"]), "O": set(p["shared_objects"]), "T": set(range(p["nt"]))},
                 {"C": set(p["shared_concepts"]), "O": set(p["shared_objects"]), "T": set(range(p["nt"]))})]
    for p in keep:
        lref = {"source_package_hash": pkghash[p["lsrc"]], "entity_kind": "claim", "local_id": p["l"]}
        rref = {"source_package_hash": pkghash[p["rsrc"]], "entity_kind": "claim", "local_id": p["r"]}
        p["left"], p["right"] = lref, rref
        p["pair_id"] = sha(canon({"left": lref, "right": rref}))
    keep.sort(key=lambda p: (-p["nc"], -p["no"], p["pair_id"]))
    if sampled:
        keep = keep[:CAP]
    pairset = {"blocker_version": "v1.0", "blocker_variant": sel,
               "blocker_design_hash": DESIGN_HASH,
               "selection_rule": D["REGRA_DE_SELECAO"]["regra"],
               "capacity_limited_sample": sampled,
               "source_package_hash_A": pkghash["A"], "source_package_hash_B": pkghash["B"],
               "source_package_hash_C": pkghash["C"],
               "population": pop, "n_pairs": len(keep),
               "pairs": [{"pair_id": p["pair_id"], "left": p["left"], "right": p["right"],
                          "blocker_variant": sel, "blocker_design_hash": DESIGN_HASH,
                          "feature_trace": {"shared_concepts": p["shared_concepts"],
                                            "shared_objects": p["shared_objects"],
                                            "n_shared_content_tokens": p["nt"]}} for p in keep]}
    pairset["PAIRSET_HASH"] = sha(canon([p["pair_id"] for p in pairset["pairs"]]))
    (H / "VARIANT-METRICS-MS002.json").write_text(json.dumps(
        {"design_hash": DESIGN_HASH, "population": pop, "capacity": CAP,
         "order": ORDER, "metrics": metrics, "selected": sel,
         "capacity_limited_sample": sampled,
         "cross_language_note": "V1..V7 medidos por combo; A-B e A-C atravessam a fronteira ingles/portugues"},
        ensure_ascii=False, indent=1), encoding="utf-8")
    (P / "PAIRSET-MS002.json").write_text(json.dumps(pairset, ensure_ascii=False, indent=1), encoding="utf-8")
    blocked = [p for p in allpairs if p["pair_id"] not in {x["pair_id"] for x in keep}] if False else None
    (H / "BLOCKED-TRACE-MS002.json").write_text(json.dumps(
        {"population": pop, "retained": len(keep), "blocked": pop - len(keep),
         "variant": sel, "reason_code": "BELOW_VARIANT_THRESHOLD",
         "note": "traco agregado; o traco por par retido esta em PAIRSET-MS002.json/feature_trace"},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  VARIANTE SELECIONADA: {sel} · pares={len(keep)} · amostra_limitada={sampled}")
    print(f"  PAIRSET_HASH = {pairset['PAIRSET_HASH']}")
    per = collections.Counter(f'{p["lsrc"]}-{p["rsrc"]}' for p in keep)
    print(f"  por combo: {dict(per)}")

if __name__ == "__main__":
    main()
