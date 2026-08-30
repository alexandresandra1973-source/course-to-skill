#!/usr/bin/env python3
"""KILLS de mutacao sobre COPIAS dos packages reais. Os reais NAO sao modificados."""
import sys, json, pathlib, shutil, tempfile, collections
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib")); sys.path.insert(0, str(H.parent / "PILOT-MS-000A"))
import package as P
import seal_verifier as SV

SRC = H / "out-exec-2/packages/pkg-B"
REG = H / "out-exec-2/packages/EXTERNAL-SEAL-REGISTRY.txt"
BEFORE = {p.name: P.sha_file(p) for p in sorted(SRC.rglob("*")) if p.is_file()}
sph0 = P.source_package_hash(P.member_manifest(SRC))
R = []
tmp = pathlib.Path(tempfile.mkdtemp())
def kill(cid, desc, mut, expect_seal_fail=True, expect_comp_fail=False):
    d = tmp / cid; shutil.copytree(SRC, d); mut(d)
    v = SV.verify(d, external_registry=REG, toolchain_dir=d)
    c = P.completeness_gate(d)
    h = P.source_package_hash(P.member_manifest(d)) if c["verdict"] == "PASS" or True else None
    ok = ((v["verdict"] != "PASS") if expect_seal_fail else True) and \
         ((c["verdict"] == "FAIL") if expect_comp_fail else True)
    R.append({"kill": cid, "desc": desc, "seal": v["verdict"], "completeness": c["verdict"],
              "hash_changed": h != sph0, "ok": bool(ok)})

def mut_claim(d):
    L = [json.loads(x) for x in (d/"CLAIMS.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    L[0]["text"] = "MUTADO"; P.wjsonl(d/"CLAIMS.jsonl", L)
def mut_cand(d):
    o = json.loads((d/"SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
    if o["rule_candidates"]: o["rule_candidates"][0]["structure"]["action"] = "MUTADO"
    else: o["rule_candidates"] = [{"local_id": "R-9999"}]
    P.wjson(d/"SOURCE-LOCAL-CANDIDATES.json", o)
def mut_trace(d):
    L = [json.loads(x) for x in (d/"COMPILE-TRACE.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    L[0]["model_resolved"] = "outro-modelo"; P.wjsonl(d/"COMPILE-TRACE.jsonl", L)
def mut_evidence(d):
    L = [json.loads(x) for x in (d/"EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    L[0]["excerpt"] = "MUTADO"; P.wjsonl(d/"EVIDENCE.jsonl", L)
def rm_member(d): (d/"DECLARATION-SPACE-INDEX.json").unlink()
def rm_seal(d): (d/"SEAL-RECORD.yaml").unlink()

kill("PK1", "mutacao de CLAIM", mut_claim)
kill("PK2", "mutacao de CANDIDATE", mut_cand)
kill("PK3", "mutacao identity-relevant do COMPILE-TRACE", mut_trace)
kill("PK4", "mutacao de EVIDENCE", mut_evidence)
kill("PK5", "membro obrigatorio ausente", rm_member, expect_seal_fail=False, expect_comp_fail=True)
kill("PK6", "sem SEAL-RECORD", rm_seal, expect_seal_fail=True, expect_comp_fail=True)

AFTER = {p.name: P.sha_file(p) for p in sorted(SRC.rglob("*")) if p.is_file()}
intact = BEFORE == AFTER
R.append({"kill": "PK7", "desc": "package REAL nao modificado", "seal": "-", "completeness": "-",
          "hash_changed": not intact, "ok": intact})
shutil.rmtree(tmp)
for x in R:
    print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['kill']:<4} {x['desc']:<44} selo={x['seal']:<8} compl={x['completeness']:<5} hash_mudou={x['hash_changed']}")
n = sum(1 for x in R if x["ok"]); print(f"\n  {n}/{len(R)} kills PASS")
P.wjson(H/"out-exec-2/package-kills.json", R)
sys.exit(0 if n == len(R) else 2)
