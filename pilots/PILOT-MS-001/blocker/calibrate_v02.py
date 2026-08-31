#!/usr/bin/env python3
"""MS-001 — CLAIM BLOCKER CALIBRATION, PHASE B. Zero modelo, zero rede, zero embedding.
Implementa EXATAMENTE o BLOCKER-DESIGN-v0.2.json, ja congelado por hash."""
import json, re, hashlib, pathlib, unicodedata, collections, itertools

D = json.loads(pathlib.Path("BLOCKER-DESIGN-v0.2.json").read_text(encoding="utf-8"))
PKG = pathlib.Path("/home/mtx/course-to-skill-claude/pilots/PILOT-MS-001/out-exec-2/packages")
SPH = {"B": D["population"]["left"]["source_package_hash"],
       "C": D["population"]["right"]["source_package_hash"]}
STOP = set(D["stopwords_pt"])
PROC = set(D["PROCEDURAL_LOW_INFORMATION_TOKENS"]["lista"])
CONC = D["FROZEN_CONCEPTS"]["conceitos"]
NAMED = set(D["NAMED_OBJECTS"]["lista"])
TOKRE = re.compile(r"[a-z0-9à-ÿ][a-z0-9à-ÿ_-]*")


def norm(t):
    return unicodedata.normalize("NFC", t or "").casefold()


def toks(t):
    return [w for w in TOKRE.findall(norm(t)) if len(w) >= D["tokenizer"]["min_len"] and w not in STOP]


def deacc(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn")


def concepts(tk):
    """hit se algum token, com ou sem acento, casa com um alias congelado (prefixo)."""
    out = set()
    flat = set(tk) | {deacc(w) for w in tk}
    for c, al in CONC.items():
        if any(any(w == a or w.startswith(a) for w in flat) for a in al):
            out.add(c)
    return out


def named(tk):
    flat = set(tk) | {deacc(w) for w in tk}
    return {n for n in NAMED if any(w == n or w.startswith(n) for w in flat)}


# ---------------------------------------------------------------- features
F = {}
for t in ("B", "C"):
    d = PKG / f"pkg-{t}"
    cl = [json.loads(l) for l in (d / "CLAIMS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    ev = {json.loads(l)["local_id"]: json.loads(l)
          for l in (d / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    an = {json.loads(l)["local_id"]: json.loads(l)
          for l in (d / "SOURCE-ANCHORS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    F[t] = []
    for c in cl:
        tk = toks(c["text"])
        q = [w for k, v in (c.get("qualifiers") or {}).items() if v for w in toks(v)]
        refs = [r["local_id"] for r in c["evidence_refs"]]
        slices = sorted({ev[r]["slice_id"] for r in refs if r in ev})
        prov = all(r in ev and ev[r]["source_anchor_refs"][0]["local_id"] in an and
                   an[ev[r]["source_anchor_refs"][0]["local_id"]]["transcript_segment_ids"] for r in refs)
        F[t].append({
            "typed_ref": {"source_package_hash": SPH[t], "entity_kind": "claim", "local_id": c["local_id"]},
            "local_id": c["local_id"], "text": c["text"], "normalized_text": norm(c["text"]),
            "content_tokens": sorted(set(tk)),
            "nonprocedural_tokens": sorted(set(tk) - PROC),
            "frozen_concepts": sorted(concepts(tk)), "named_objects": sorted(named(tk)),
            "qualifier_tokens": sorted(set(q)), "slice_provenance": slices,
            "evidence_refs": sorted(refs), "provenance_resolves": prov,
            "feature_hash": hashlib.sha256(json.dumps(
                {"t": sorted(set(tk)), "c": sorted(concepts(tk))}, sort_keys=True).encode()).hexdigest()[:16]})
json.dump(F, open("features-v02.json", "w"), ensure_ascii=False, indent=1)

# ------------------------------------------------------- provenance gate (§22)
bad = [f["local_id"] for t in F for f in F[t] if not f["provenance_resolves"]]
PROV_OK = not bad

# ---------------------------------------------------------------- pares
PAIRS = []
for b in F["B"]:
    for c in F["C"]:
        sc = sorted(set(b["frozen_concepts"]) & set(c["frozen_concepts"]))
        st = sorted(set(b["content_tokens"]) & set(c["content_tokens"]))
        snp = sorted(set(b["nonprocedural_tokens"]) & set(c["nonprocedural_tokens"]))
        sn = sorted(set(b["named_objects"]) & set(c["named_objects"]))
        PAIRS.append({"pair_key": f"{b['local_id']}|{c['local_id']}",
                      "left": b["typed_ref"], "right": c["typed_ref"],
                      "shared_concepts": sc, "shared_tokens": st,
                      "shared_nonprocedural": snp, "shared_named": sn,
                      "n_concepts": len(sc), "n_tokens": len(st),
                      "n_nonproc": len(snp), "n_named": len(sn),
                      "only_procedural": bool(st) and not snp,
                      "score": len(sc) * 10 + len(snp),
                      "feature_hashes": [b["feature_hash"], c["feature_hash"]],
                      "_b": b, "_c": c})
PAIRS.sort(key=lambda p: p["pair_key"])

VAR = {
 "V1": lambda p: p["n_concepts"] >= 1,
 "V2": lambda p: p["n_concepts"] >= 1 and p["n_nonproc"] >= 1,
 "V3": lambda p: p["n_concepts"] >= 1 and p["n_nonproc"] >= 2,
 "V4": lambda p: p["n_concepts"] >= 2,
 "V5": lambda p: p["n_named"] >= 1 or (p["n_concepts"] >= 1 and p["n_nonproc"] >= 1),
 "V6": lambda p: p["n_concepts"] >= 2 and p["n_nonproc"] >= 1,
}

# ------------------------------------------ mapeamento MECANICO dos controles
CT = D["control_mapping_algorithm"]["controles"]
def cand(side, slices, terms):
    out = []
    for f in F[side]:
        if not (set(f["slice_provenance"]) & set(slices)): continue
        flat = set(f["content_tokens"]) | {deacc(w) for w in f["content_tokens"]}
        if any(any(w == t or w.startswith(t) for w in flat) for t in terms):
            out.append(f["local_id"])
    return sorted(out)

MAP = {}
for k, spec in CT.items():
    tb = spec.get("termos_B") or spec.get("termos", [])
    tc = spec.get("termos_C") or spec.get("termos", [])
    cb = cand("B", spec["slices_B"], tb); cc = cand("C", spec["slices_C"], tc)
    MAP[k] = {"B": cb, "C": cc, "pairs": [f"{x}|{y}" for x in cb for y in cc],
              "esperado": spec["esperado"], "mapeavel": bool(cb and cc)}
json.dump(MAP, open("control-mappings-v02.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- metricas
IDX = {p["pair_key"]: p for p in PAIRS}
MET = {}
for v, fn in VAR.items():
    ret = [p for p in PAIRS if fn(p)]
    rk = {p["pair_key"] for p in ret}
    ctl = {}
    for k, m in MAP.items():
        if not m["mapeavel"]:
            ctl[k] = {"status": "NAO_MAPEAVEL", "n_pairs": 0, "retained": 0}
            continue
        r = [x for x in m["pairs"] if x in rk]
        exp_block = m["esperado"].startswith("BLOCK")
        ctl[k] = {"n_pairs": len(m["pairs"]), "retained": len(r),
                  "status": ("BLOCK" if not r else "RETAIN"),
                  "ok": (len(r) == 0) if exp_block else (len(r) >= 1)}
    MET[v] = {"raw": len(PAIRS), "retained": len(ret), "blocked": len(PAIRS) - len(ret),
              "reduction_pct": round(100 * (1 - len(ret) / len(PAIRS)), 2),
              "controls": ctl,
              "retained_only_procedural": sum(1 for p in ret if p["only_procedural"]),
              "dist_concepts": dict(collections.Counter(p["n_concepts"] for p in ret)),
              "dist_nonproc": dict(collections.Counter(min(p["n_nonproc"], 6) for p in ret)),
              "judge_calls_b20": -(-len(ret) // 20), "judge_calls_b25": -(-len(ret) // 25)}

# ------------------------------------------------- regra de selecao congelada
ORDER = ["V1", "V5", "V2", "V4", "V3", "V6"]
def sat(v):
    c = MET[v]["controls"]
    pos = all(c[k].get("ok") for k in ("BC1_genuine_overlap", "BC2_scope_difference",
                                       "BC3_specialization", "BC4_false_conflict"))
    neg = c["BC5_unrelated"].get("ok", False)
    return pos and neg and MET[v]["retained"] < 1080
ok = [v for v in ORDER if sat(v)]
chosen = min(ok, key=lambda v: (ORDER.index(v) * -1, MET[v]["retained"])) if ok else None
if ok:
    chosen = sorted(ok, key=lambda v: (-ORDER.index(v), MET[v]["retained"]))[0]

json.dump({"metrics": MET, "satisfying": ok, "chosen": chosen,
           "provenance_all_resolve": PROV_OK, "provenance_failures": bad},
          open("variant-metrics-v02.json", "w"), ensure_ascii=False, indent=1)
json.dump([{k: v for k, v in p.items() if not k.startswith("_")} for p in PAIRS],
          open("pair-traces-v02.json", "w"), ensure_ascii=False, indent=1)

print(f"=== provenance de todas as {sum(len(F[t]) for t in F)} claims resolve ate L0: {PROV_OK}")
print(f"\n=== MAPEAMENTO MECANICO DOS CONTROLES ===")
for k, m in MAP.items():
    print(f"  {k:<24} B={len(m['B']):>2} C={len(m['C']):>2} pares={len(m['pairs']):>4} mapeavel={m['mapeavel']}")
print(f"\n=== METRICAS POR VARIANTE (1080 pares brutos) ===")
print(f"  {'var':<4} {'retidos':>8} {'reducao':>9} {'so-proc':>8}  BC1 BC2 BC3 BC4 BC5  {'calls/20':>9} {'calls/25':>9}")
for v in ORDER:
    m = MET[v]; c = m["controls"]
    f = lambda k: ("OK " if c[k].get("ok") else "XX ")
    print(f"  {v:<4} {m['retained']:>8} {m['reduction_pct']:>8.2f}% {m['retained_only_procedural']:>8}  "
          f"{f('BC1_genuine_overlap')}{f('BC2_scope_difference')}{f('BC3_specialization')}"
          f"{f('BC4_false_conflict')}{f('BC5_unrelated')} {m['judge_calls_b20']:>9} {m['judge_calls_b25']:>9}")
print(f"\n  satisfazem a regra: {ok}")
print(f"  ESCOLHIDA: {chosen}")
