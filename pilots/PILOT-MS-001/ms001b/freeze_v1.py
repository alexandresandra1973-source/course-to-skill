#!/usr/bin/env python3
"""MS-001B — FREEZE do PAIRSET V1. Recomputa deterministicamente do zero.
Zero modelo. Reusa lib de features da v0.3 sem alteracao de desenho."""
import json, re, hashlib, pathlib, unicodedata, collections
CAL = pathlib.Path.home() / "ms001-blocker-calibration/v03"
D = json.loads((CAL / "BLOCKER-DESIGN-v0.3.json").read_text(encoding="utf-8"))
BD_HASH = hashlib.sha256((CAL / "BLOCKER-DESIGN-v0.3.json").read_bytes()).hexdigest()
PKG = pathlib.Path("/home/mtx/course-to-skill-claude/pilots/PILOT-MS-001/out-exec-2/packages")
SPH = {"B": D["population"]["left"]["source_package_hash"],
       "C": D["population"]["right"]["source_package_hash"]}
CONC = D["CHANNEL_A_FROZEN_CONCEPTS"]["conceitos"]; NAMED = D["CHANNEL_B_NAMED_OBJECTS"]["objetos"]
MINLEN = D["CHANNEL_C_CONTENT_TOKENS"]["min_len"]; PROC = set(D["CHANNEL_C_CONTENT_TOKENS"]["procedural_filter"])
TOKRE = re.compile(r"[a-z0-9à-ÿ][a-z0-9à-ÿ_-]*")
deacc = lambda w: "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn")
STOPKEY = {deacc(w) for w in D["STOPWORDS"]["lista"]}
norm = lambda t: unicodedata.normalize("NFC", t or "").casefold()
words = lambda t: TOKRE.findall(norm(t))
def ch_a(t):
    W = words(t); WD = {deacc(w) for w in W}
    return sorted({c for c, al in CONC.items()
                   if any(a in W or a in WD or any(w.startswith(a) and len(a) >= 4 for w in WD) for a in al)})
def ch_b(t):
    W = words(t); WD = {deacc(w) for w in W}
    return sorted({n for n in NAMED if n in W or n in WD})
def ch_c(t):
    return sorted({w for w in words(t) if len(w) >= MINLEN and deacc(w) not in STOPKEY})

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
        A, Bn, C = ch_a(c["text"]), ch_b(c["text"]), ch_c(c["text"])
        refs = [r["local_id"] for r in c["evidence_refs"]]
        F[t].append({"typed_ref": {"source_package_hash": SPH[t], "entity_kind": "claim", "local_id": c["local_id"]},
                     "local_id": c["local_id"], "text": c["text"], "qualifiers": c.get("qualifiers", {}),
                     "source_language": c.get("source_language", "pt"),
                     "a": A, "b": Bn, "c": C, "cnp": sorted(set(C) - PROC),
                     "evidence_refs": sorted(refs),
                     "evidence": [{"evidence_id": r, "excerpt": ev[r]["excerpt"],
                                   "anchor": {"local_id": ev[r]["source_anchor_refs"][0]["local_id"],
                                              "start_s": an[ev[r]["source_anchor_refs"][0]["local_id"]]["start_s"],
                                              "end_s": an[ev[r]["source_anchor_refs"][0]["local_id"]]["end_s"]}}
                                  for r in sorted(refs)],
                     "slice_provenance": sorted({ev[r]["slice_id"] for r in refs})})

canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
V1 = lambda p: p["n_concepts"] >= 1

ALL, RET, BLK = [], [], []
for b in F["B"]:
    for c in F["C"]:
        sa = sorted(set(b["a"]) & set(c["a"])); sb = sorted(set(b["b"]) & set(c["b"]))
        sc = sorted(set(b["c"]) & set(c["c"])); snp = sorted(set(b["cnp"]) & set(c["cnp"]))
        ft = {"shared_concepts": sa, "shared_named": sb, "shared_tokens": sc, "shared_nonprocedural": snp}
        p = {"left": b["typed_ref"], "right": c["typed_ref"],
             **ft, "n_concepts": len(sa), "n_named": len(sb), "n_nonproc": len(snp),
             "short_tokens_channel_c": sorted({w for w in sc if len(w) < 4}),
             "feature_trace_hash": sha(canon(ft)),
             "blocker_version": "v0.3", "blocker_variant": "V1",
             "blocker_design_hash": BD_HASH}
        p["pair_id"] = sha(canon({"left": b["typed_ref"], "right": c["typed_ref"],
                                  "blocker_design_hash": BD_HASH, "blocker_variant": "V1"}))
        p["retained"] = V1(p)
        p["reason_code"] = ("RETAINED_SHARED_FROZEN_CONCEPT" if p["retained"]
                            else "BLOCKED_NO_SHARED_FROZEN_CONCEPT")
        ALL.append(p); (RET if p["retained"] else BLK).append(p)

RET.sort(key=lambda p: p["pair_id"]); BLK.sort(key=lambda p: p["pair_id"])
PAIRSET = [{k: p[k] for k in ("pair_id", "left", "right", "blocker_version", "blocker_variant",
                              "blocker_design_hash", "feature_trace_hash")} for p in RET]
PAIRSET_HASH = sha(canon([{"pair_id": x["pair_id"], "left": x["left"], "right": x["right"]} for x in PAIRSET]))

pathlib.Path("PAIRSET-MS001B-V1.json").write_text(json.dumps(
    {"blocker_version": "v0.3", "blocker_variant": "V1", "blocker_design_hash": BD_HASH,
     "source_package_hash_B": SPH["B"], "source_package_hash_C": SPH["C"],
     "pair_direction": "B -> C", "n_pairs": len(PAIRSET),
     "PAIRSET_HASH": PAIRSET_HASH, "pairs": PAIRSET}, ensure_ascii=False, indent=1), encoding="utf-8")
pathlib.Path("BLOCKED-TRACE-MS001B-V1.json").write_text(json.dumps(
    [{k: p[k] for k in ("pair_id","left","right","shared_concepts","shared_named","shared_nonprocedural",
                        "reason_code","feature_trace_hash")} for p in BLK], ensure_ascii=False, indent=1), encoding="utf-8")
pathlib.Path("PAIR-INPUTS-MS001B.json").write_text(json.dumps(
    {p["pair_id"]: {
        "left": {"typed_ref": p["left"], "text": next(x for x in F["B"] if x["local_id"]==p["left"]["local_id"])["text"],
                 "source_language": "pt",
                 "qualifiers": next(x for x in F["B"] if x["local_id"]==p["left"]["local_id"])["qualifiers"],
                 "source": "B",
                 "evidence": next(x for x in F["B"] if x["local_id"]==p["left"]["local_id"])["evidence"]},
        "right": {"typed_ref": p["right"], "text": next(x for x in F["C"] if x["local_id"]==p["right"]["local_id"])["text"],
                  "source_language": "pt",
                  "qualifiers": next(x for x in F["C"] if x["local_id"]==p["right"]["local_id"])["qualifiers"],
                  "source": "C",
                  "evidence": next(x for x in F["C"] if x["local_id"]==p["right"]["local_id"])["evidence"]}}
     for p in RET}, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"=== RECOMPUTACAO DETERMINISTICA DE V1 ===")
print(f"  pares brutos     : {len(ALL)}   (esperado 1080)")
print(f"  retidos          : {len(RET)}   (esperado 97)")
print(f"  bloqueados       : {len(BLK)}   (esperado 983)")
print(f"  reducao          : {100*(1-len(RET)/len(ALL)):.2f}%   (esperado 91.02%)")
print(f"  cobertura B      : {len({p['left']['local_id'] for p in RET})}/30   (esperado 22)")
print(f"  cobertura C      : {len({p['right']['local_id'] for p in RET})}/36   (esperado 16)")
leak = sorted({w for p in RET for w in p["short_tokens_channel_c"]})
print(f"  short-token leak : {leak or 'NENHUM'}")
print(f"\n  PAIRSET_HASH     : {PAIRSET_HASH}")
print(f"  blocker_design   : {BD_HASH}")
ok = (len(ALL)==1080 and len(RET)==97 and len(BLK)==983 and not leak)
print(f"\n  {'REPRODUZ' if ok else 'NAO REPRODUZ -> BLOCKER_FREEZE_INVALID'}")

M = json.loads((CAL / "control-mappings-v03.json").read_text(encoding="utf-8"))
rk = {f"{p['left']['local_id']}|{p['right']['local_id']}" for p in RET}
print(f"\n=== BC1-BC5 sob V1 congelada ===")
for k, m in M.items():
    r = [x for x in m["pairs"] if x in rk]
    eb = m["esperado"].startswith("BLOCK")
    st = "BLOCK" if not r else "RETAIN"
    print(f"  {k:<24} {len(r):>3}/{len(m['pairs']):>3} retidos -> {st:<7} "
          f"{'PASS' if ((len(r)==0) if eb else (len(r)>=1)) else 'FALHA'}")
