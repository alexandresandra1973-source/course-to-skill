#!/usr/bin/env python3
"""MS-001B — CANARIOS MECANICOS PRE-MODELO. Todos PASS antes de qualquer chamada."""
import sys, json, pathlib, hashlib, copy
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib")); sys.path.insert(0, str(H.parent / "PILOT-MS-000A"))
import relation_validate as RV, package as P
import seal_verifier as SV

R = []
def chk(c, d, exp, got, ok): R.append({"canary": c, "desc": d, "expected": exp, "got": got, "ok": bool(ok)})

PS = json.loads((H / "ms001b/PAIRSET-MS001B-V1.json").read_text(encoding="utf-8"))
PI = json.loads((H / "ms001b/PAIR-INPUTS-MS001B.json").read_text(encoding="utf-8"))
ids = [p["pair_id"] for p in PS["pairs"]]
SENT = {i: {"left": {e["evidence_id"] for e in PI[i]["left"]["evidence"]},
            "right": {e["evidence_id"] for e in PI[i]["right"]["evidence"]}} for i in ids[:3]}
def ok_j(pid, rel="UNRELATED", dr="NONE", sc="DIFFERENT_SCOPE"):
    return {"pair_id": pid, "relation": rel, "direction": dr, "scope_state": sc,
            "relation_why": "razao suficientemente longa para o schema",
            "left_evidence_refs_checked": sorted(SENT[pid]["left"]),
            "right_evidence_refs_checked": sorted(SENT[pid]["right"])}
doc = lambda js: json.dumps({"batch_id": "BATCH-1", "judgments": js})
base = [ok_j(i) for i in SENT]

chk("RC00","output valido de referencia",None, RV.validate(doc(base),"BATCH-1",SENT)[1], not RV.validate(doc(base),"BATCH-1",SENT)[1])
chk("RC01","JSON invalido","R01_JSON_UNPARSEABLE", RV.validate("{x","BATCH-1",SENT)[1], "R01_JSON_UNPARSEABLE" in RV.validate("{x","BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0]["lixo"]=1
chk("RC02","campo extra","R04_EXTRA_FIELD", RV.validate(doc(b),"BATCH-1",SENT)[1], "R04_EXTRA_FIELD" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0]["pair_id"]="f"*64
chk("RC03","par desconhecido","R05_UNKNOWN_PAIR", RV.validate(doc(b),"BATCH-1",SENT)[1], "R05_UNKNOWN_PAIR" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base)+[copy.deepcopy(base[0])]
chk("RC04","par duplicado","R06_DUPLICATE_PAIR", RV.validate(doc(b),"BATCH-1",SENT)[1], "R06_DUPLICATE_PAIR" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base)[:2]
chk("RC05","par omitido","R15_PAIR_MISSING", RV.validate(doc(b),"BATCH-1",SENT)[1], "R15_PAIR_MISSING" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0]["relation"]="TALVEZ"
chk("RC06","relation invalida","R07_INVALID_RELATION", RV.validate(doc(b),"BATCH-1",SENT)[1], "R07_INVALID_RELATION" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0]["direction"]="ESQUERDA"
chk("RC07","direction invalida","R08_INVALID_DIRECTION", RV.validate(doc(b),"BATCH-1",SENT)[1], "R08_INVALID_DIRECTION" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0].update({"relation":"IDENTICAL","direction":"LEFT_TO_RIGHT","scope_state":"EQUIVALENT_SCOPE"})
chk("RC08","direction incompativel com relation","R09_DIRECTION_INCOMPATIBLE", RV.validate(doc(b),"BATCH-1",SENT)[1], "R09_DIRECTION_INCOMPATIBLE" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0]["scope_state"]="QUALQUER"
chk("RC09","scope_state invalido","R10_INVALID_SCOPE", RV.validate(doc(b),"BATCH-1",SENT)[1], "R10_INVALID_SCOPE" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0].update({"relation":"IDENTICAL","direction":"NONE","scope_state":"DIFFERENT_SCOPE"})
chk("RC10","IDENTICAL com DIFFERENT_SCOPE","R11_SCOPE_INCOMPATIBLE", RV.validate(doc(b),"BATCH-1",SENT)[1], "R11_SCOPE_INCOMPATIBLE" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0]["left_evidence_refs_checked"]=sorted(SENT[b[0]["pair_id"]]["left"])+["EV-9999"]
chk("RC11","evidence acrescentada","R13_EVIDENCE_ADDED_LEFT", RV.validate(doc(b),"BATCH-1",SENT)[1], "R13_EVIDENCE_ADDED_LEFT" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0]["right_evidence_refs_checked"]=sorted(SENT[b[0]["pair_id"]]["right"])[:1] if len(SENT[b[0]["pair_id"]]["right"])>1 else ["EV-0001"]
r=RV.validate(doc(b),"BATCH-1",SENT)[1]
chk("RC12","evidence omitida/estrangeira","R14 ou R13", r, ("R14_EVIDENCE_OMITTED_RIGHT" in r or "R13_EVIDENCE_ADDED_RIGHT" in r))
b=copy.deepcopy(base); b[0]["precedence"]="B"
chk("RC13","injecao de precedence","R12_FORBIDDEN_FIELD", RV.validate(doc(b),"BATCH-1",SENT)[1], "R12_FORBIDDEN_FIELD" in RV.validate(doc(b),"BATCH-1",SENT)[1])
b=copy.deepcopy(base); b[0]["mtx_policy_hash"]="0"*64
chk("RC14","injecao de MTX policy","R12_FORBIDDEN_FIELD", RV.validate(doc(b),"BATCH-1",SENT)[1], "R12_FORBIDDEN_FIELD" in RV.validate(doc(b),"BATCH-1",SENT)[1])
# pairset drift + typed ref + package drift
canon=lambda o: json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(",",":"))
sha=lambda s: hashlib.sha256(s.encode()).hexdigest()
ph=sha(canon([{"pair_id":x["pair_id"],"left":x["left"],"right":x["right"]} for x in PS["pairs"]]))
chk("RC15","PAIRSET_HASH reproduz","igual", ph==PS["PAIRSET_HASH"], ph==PS["PAIRSET_HASH"])
drift=sha(canon([{"pair_id":x["pair_id"],"left":x["left"],"right":x["right"]} for x in PS["pairs"][:-1]]))
chk("RC16","PAIRSET_DRIFT detectado","hash muda", drift!=PS["PAIRSET_HASH"], drift!=PS["PAIRSET_HASH"])
untyped=[p for p in PS["pairs"] if not all(k in p["left"] and k in p["right"] for k in ("source_package_hash","entity_kind","local_id"))]
chk("RC17","zero ref nao tipada","0 refs nuas", len(untyped), not untyped)
reg=H/"out-exec-2/packages/EXTERNAL-SEAL-REGISTRY.txt"
E={"B":"a0a73dde03410d5c744129bf8ba635815a678dbf5ce46cd124e6a31f8f67dc1f","C":"5959b4ea1e8b91f570c17d61d03c4f2b6d00698801056a72a53c8e02b5a1d6c2"}
drifted=[t for t,e in E.items() if P.source_package_hash(P.member_manifest(H/f"out-exec-2/packages/pkg-{t}"))!=e]
chk("RC18","Source Package hash drift","nenhum", drifted, not drifted)
seals=[SV.verify(H/f"out-exec-2/packages/pkg-{t}",external_registry=reg,toolchain_dir=H/f"out-exec-2/packages/pkg-{t}")["verdict"] for t in "BC"]
chk("RC19","selos PASS","PASS PASS", seals, all(s=="PASS" for s in seals))
chk("RC20","97 pares exatos","97", len(PS["pairs"]), len(PS["pairs"])==97)
prov=all(PI[i][s]["evidence"] and all(e.get("anchor",{}).get("local_id") for e in PI[i][s]["evidence"]) for i in ids for s in ("left","right"))
chk("RC21","provenance de todos os 97 pares resolve a anchor","True", prov, prov)

if __name__ == "__main__":
    for x in R: print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['canary']:<6} {x['desc']:<42} esperado={str(x['expected'])[:34]}")
    n=sum(1 for x in R if x["ok"]); print(f"\n  {n}/{len(R)} canarios pre-modelo PASS")
    (H/"out-ms001b").mkdir(exist_ok=True)
    (H/"out-ms001b/premodel-canaries.json").write_text(json.dumps(R,ensure_ascii=False,indent=1),encoding="utf-8")
    sys.exit(0 if n==len(R) else 2)
