#!/usr/bin/env python3
"""MS-001 BLOCKER v0.3 — TRES CANAIS DE FEATURE. Zero modelo, zero rede, zero embedding.
Ordem: texto normalizado -> Channel A conceitos -> Channel B objetos -> Channel C tokens."""
import json, re, hashlib, pathlib, unicodedata, collections

D = json.loads(pathlib.Path("BLOCKER-DESIGN-v0.3.json").read_text(encoding="utf-8"))
PKG = pathlib.Path("/home/mtx/course-to-skill-claude/pilots/PILOT-MS-001/out-exec-2/packages")
SPH = {"B": D["population"]["left"]["source_package_hash"],
       "C": D["population"]["right"]["source_package_hash"]}
CONC = D["CHANNEL_A_FROZEN_CONCEPTS"]["conceitos"]
NAMED = D["CHANNEL_B_NAMED_OBJECTS"]["objetos"]
MINLEN = D["CHANNEL_C_CONTENT_TOKENS"]["min_len"]
PROC = set(D["CHANNEL_C_CONTENT_TOKENS"]["procedural_filter"])
NEG = set(D["NEGATION"]["tokens"])
FUNC = set(D["FUNCTIONAL_BRIDGE_TEST"]["lista_funcional_pre_declarada"])
TOKRE = re.compile(r"[a-z0-9à-ÿ][a-z0-9à-ÿ_-]*")


def deacc(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn")


# chave de stopword: casefold + accent-insensitive (unica correcao mecanica declarada)
STOPKEY = {deacc(w) for w in D["STOPWORDS"]["lista"]}


def norm(t):
    return unicodedata.normalize("NFC", t or "").casefold()


def all_words(t):
    return TOKRE.findall(norm(t))


# ---------------- CHANNEL A: conceitos, sobre o TEXTO NORMALIZADO, sem min_len
def ch_a(text):
    W = all_words(text); WD = {deacc(w) for w in W}
    hits, ev = set(), {}
    for c, al in CONC.items():
        m = [a for a in al if a in W or a in WD or any(w.startswith(a) and len(a) >= 4 for w in WD)]
        if m: hits.add(c); ev[c] = sorted(set(m))
    return sorted(hits), ev


# ---------------- CHANNEL B: objetos nomeados, sem min_len
def ch_b(text):
    W = all_words(text); WD = {deacc(w) for w in W}
    return sorted({n for n in NAMED if n in W or n in WD})


# ---------------- CHANNEL C: tokens genericos, min_len=4, stopword accent-insensitive
def ch_c(text):
    out = []
    for w in all_words(text):
        if len(w) < MINLEN: continue
        if deacc(w) in STOPKEY: continue
        out.append(w)
    return sorted(set(out))


def negation_tokens(text):
    return sorted({w for w in all_words(text) if deacc(w) in NEG})


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
        A, Aev = ch_a(c["text"]); Bn = ch_b(c["text"]); C = ch_c(c["text"])
        refs = [r["local_id"] for r in c["evidence_refs"]]
        prov = all(r in ev and ev[r]["source_anchor_refs"][0]["local_id"] in an for r in refs)
        F[t].append({"typed_ref": {"source_package_hash": SPH[t], "entity_kind": "claim",
                                   "local_id": c["local_id"]},
                     "local_id": c["local_id"], "text": c["text"],
                     "channel_a_concepts": A, "channel_a_evidence": Aev,
                     "channel_b_named": Bn,
                     "channel_c_tokens": C,
                     "channel_c_nonprocedural": sorted(set(C) - PROC),
                     "negation_tokens": negation_tokens(c["text"]),
                     "slice_provenance": sorted({ev[r]["slice_id"] for r in refs if r in ev}),
                     "evidence_refs": sorted(refs), "provenance_resolves": prov})
json.dump(F, open("features-v03.json", "w"), ensure_ascii=False, indent=1)
PROV_OK = all(f["provenance_resolves"] for t in F for f in F[t])

PAIRS = []
for b in F["B"]:
    for c in F["C"]:
        sa = sorted(set(b["channel_a_concepts"]) & set(c["channel_a_concepts"]))
        sb = sorted(set(b["channel_b_named"]) & set(c["channel_b_named"]))
        sc = sorted(set(b["channel_c_tokens"]) & set(c["channel_c_tokens"]))
        snp = sorted(set(b["channel_c_nonprocedural"]) & set(c["channel_c_nonprocedural"]))
        short = sorted({w for w in sc if len(w) < 4})            # deve ser VAZIO
        PAIRS.append({"pair_key": f"{b['local_id']}|{c['local_id']}",
                      "left": b["typed_ref"], "right": c["typed_ref"],
                      "shared_concepts": sa, "shared_named": sb,
                      "shared_tokens": sc, "shared_nonprocedural": snp,
                      "short_tokens_channel_c": short,
                      "n_concepts": len(sa), "n_named": len(sb),
                      "n_tokens": len(sc), "n_nonproc": len(snp),
                      "only_procedural": bool(sc) and not snp,
                      "score": len(sa) * 10 + len(sb) * 5 + len(snp)})
PAIRS.sort(key=lambda p: p["pair_key"])

VAR = {"V1": lambda p: p["n_concepts"] >= 1,
       "V2": lambda p: p["n_concepts"] >= 1 and p["n_nonproc"] >= 1,
       "V3": lambda p: p["n_concepts"] >= 1 and p["n_nonproc"] >= 2,
       "V4": lambda p: p["n_concepts"] >= 2,
       "V5": lambda p: p["n_named"] >= 1 or (p["n_concepts"] >= 1 and p["n_nonproc"] >= 1),
       "V6": lambda p: p["n_concepts"] >= 2 and p["n_nonproc"] >= 1}

CT = D["control_mapping_algorithm"]["controles"]
def cand(side, slices, terms):
    out = []
    for f in F[side]:
        if not (set(f["slice_provenance"]) & set(slices)): continue
        W = set(all_words(f["text"])); WD = {deacc(w) for w in W}
        if any(t in W or t in WD or any(w.startswith(t) and len(t) >= 4 for w in WD) for t in terms):
            out.append(f["local_id"])
    return sorted(out)
MAP = {}
for k, sp in CT.items():
    tb = sp.get("termos_B") or sp.get("termos", []); tc = sp.get("termos_C") or sp.get("termos", [])
    cb = cand("B", sp["slices_B"], tb); cc = cand("C", sp["slices_C"], tc)
    MAP[k] = {"B": cb, "C": cc, "pairs": [f"{x}|{y}" for x in cb for y in cc],
              "esperado": sp["esperado"], "mapeavel": bool(cb and cc)}
json.dump(MAP, open("control-mappings-v03.json", "w"), ensure_ascii=False, indent=1)

def bridge(p):
    if p["n_concepts"] or p["n_named"]: return "CONCEPT_OR_OBJECT_SUPPORTED"
    real = [w for w in p["shared_nonprocedural"] if deacc(w) not in FUNC]
    return "GENERIC_CONTENT_SUPPORTED" if real else "FUNCTIONAL_OR_LOW_INFORMATION_SUSPECT"

MET = {}
for v, fn in VAR.items():
    ret = [p for p in PAIRS if fn(p)]; rk = {p["pair_key"] for p in ret}
    ctl = {}
    for k, m in MAP.items():
        r = [x for x in m["pairs"] if x in rk]
        eb = m["esperado"].startswith("BLOCK")
        ctl[k] = {"n_pairs": len(m["pairs"]), "retained": len(r),
                  "ok": (len(r) == 0) if eb else (len(r) >= 1)}
    br = collections.Counter(bridge(p) for p in ret)
    leak = sorted({w for p in ret for w in p["short_tokens_channel_c"]})
    MET[v] = {"raw": 1080, "retained": len(ret), "blocked": 1080 - len(ret),
              "reduction_pct": round(100 * (1 - len(ret) / 1080), 2), "controls": ctl,
              "coverage_B": len({p["left"]["local_id"] for p in ret}),
              "coverage_C": len({p["right"]["local_id"] for p in ret}),
              "dist_concepts": dict(collections.Counter(p["n_concepts"] for p in ret)),
              "dist_named": dict(collections.Counter(p["n_named"] for p in ret)),
              "dist_tokens": dict(collections.Counter(min(p["n_nonproc"], 6) for p in ret)),
              "functional_bridge": dict(br), "short_token_leak": leak,
              "retained_only_procedural": sum(1 for p in ret if p["only_procedural"]),
              "judge_b20": -(-len(ret) // 20), "judge_b25": -(-len(ret) // 25)}

ORDER = ["V1", "V5", "V2", "V4", "V3", "V6"]
def sat(v):
    c = MET[v]["controls"]
    return (all(c[k]["ok"] for k in ("BC1_genuine_overlap", "BC2_scope_difference",
                                     "BC3_specialization", "BC4_false_conflict"))
            and c["BC5_unrelated"]["ok"] and MET[v]["retained"] < 1080)
ok = [v for v in ORDER if sat(v)]
chosen = sorted(ok, key=lambda v: (-ORDER.index(v), MET[v]["retained"]))[0] if ok else None
GLOBAL_LEAK = sorted({w for p in PAIRS for w in p["short_tokens_channel_c"]})

json.dump({"metrics": MET, "satisfying": ok, "chosen": chosen,
           "provenance_all_resolve": PROV_OK, "global_short_token_leak": GLOBAL_LEAK},
          open("variant-metrics-v03.json", "w"), ensure_ascii=False, indent=1)
json.dump(PAIRS, open("pair-traces-v03.json", "w"), ensure_ascii=False, indent=1)

print(f"=== provenance resolve: {PROV_OK}")
print(f"=== SHORT-TOKEN AUDIT: tokens <4 no Channel C em QUALQUER par: {GLOBAL_LEAK or 'NENHUM'}")
print(f"    -> {'FEATURE_CHANNEL_LEAK' if GLOBAL_LEAK else 'SEM VAZAMENTO DE CANAL'}")
print(f"\n=== MAPEAMENTOS ===")
for k, m in MAP.items(): print(f"  {k:<24} B={len(m['B']):>2} C={len(m['C']):>2} pares={len(m['pairs']):>3}")
print(f"\n=== METRICAS v0.3 (1080 pares) ===")
print(f"  {'var':<4} {'ret':>5} {'reducao':>9} {'covB':>5} {'covC':>5}  BC1 BC2 BC3 BC4 BC5  {'CONC':>5} {'GEN':>4} {'SUSP':>5}")
for v in ORDER:
    m = MET[v]; c = m["controls"]; f = lambda k: "OK " if c[k]["ok"] else "XX "
    b = m["functional_bridge"]
    print(f"  {v:<4} {m['retained']:>5} {m['reduction_pct']:>8.2f}% {m['coverage_B']:>4}/30 {m['coverage_C']:>4}/36  "
          f"{f('BC1_genuine_overlap')}{f('BC2_scope_difference')}{f('BC3_specialization')}"
          f"{f('BC4_false_conflict')}{f('BC5_unrelated')} "
          f"{b.get('CONCEPT_OR_OBJECT_SUPPORTED',0):>5} {b.get('GENERIC_CONTENT_SUPPORTED',0):>4} "
          f"{b.get('FUNCTIONAL_OR_LOW_INFORMATION_SUSPECT',0):>5}")
print(f"\n  satisfazem: {ok}")
print(f"  ESCOLHIDA: {chosen}")
