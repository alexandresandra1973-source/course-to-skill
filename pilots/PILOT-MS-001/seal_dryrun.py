#!/usr/bin/env python3
"""DRY-RUN de package/selo com fixtures SINTETICOS. Zero resultado experimental real.
Reusa o verificador aceito do PILOT-MS-000A. Nenhuma definicao nova de SEALED."""
import sys, json, pathlib, tempfile, shutil, hashlib
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib")); sys.path.insert(0, str(H.parent / "PILOT-MS-000A"))
import package as P
import seal_verifier as SV

R = []
def chk(c, d, exp, got, ok): R.append({"canary": c, "desc": d, "expected": exp, "got": got, "ok": bool(ok)})

def build(base, omit=None):
    d = pathlib.Path(base); (d / "L0").mkdir(parents=True, exist_ok=True); (d / "ARTIFACTS").mkdir(exist_ok=True)
    content = {"SOURCE-PROFILE.json": {"source_id": "FIXTURE", "source_content_hash": "f"*64},
               "L0/RAW-CAPTION.json": [{"start": 0.0, "duration": 1.0, "text": "fixture"}],
               "ARTIFACTS/ARTIFACT-INDEX.json": {"artifacts": [{"local_id": "ART-RAW", "entity_kind": "artifact"}]},
               "SOURCE-LOCAL-CANDIDATES.json": {"rule_candidates": [], "workflow_candidates": [], "anti_pattern_candidates": []},
               "LOCAL-COHERENCE-REPORT.json": {"kind": "MECHANICAL_ONLY", "findings": []},
               "DECLARATION-SPACE-INDEX.json": {"bounded_to": "FIXTURE"},
               "TOOLCHAIN.json": {"tool": "fixture", "version": "0"}}
    jl = {"SOURCE-ANCHORS.jsonl": [{"local_id": "AN-0001"}], "EVIDENCE.jsonl": [{"local_id": "EV-0001"}],
          "CLAIMS.jsonl": [{"local_id": "CL-0001"}], "COMPILE-TRACE.jsonl": [{"event": "FIXTURE"}]}
    for p, o in content.items():
        if p == omit: continue
        P.wjson(d / p, o)
    for p, L in jl.items():
        if p == omit: continue
        P.wjsonl(d / p, L)
    return d

tmp = pathlib.Path(tempfile.mkdtemp())
reg = tmp / "EXTERNAL-SEAL-REGISTRY.txt"; reg.write_text("# fixture registry\n", encoding="utf-8")

# --- PD1 completeness antes do selo
d1 = build(tmp / "pkg-FIX"); c = P.completeness_gate(d1)
chk("PD1", "completude antes do selo (falta SEAL-RECORD)", "FAIL/REQUIRED_MEMBER_MISSING",
    f'{c["verdict"]}:{c["missing"]}', c["verdict"] == "FAIL" and c["missing"] == ["SEAL-RECORD"])
# --- PD2 selo + completude + verificador
s = P.seal(d1, "FIXTURE", "f"*64, reg); c2 = P.completeness_gate(d1)
v = SV.verify(d1, external_registry=reg, toolchain_dir=d1)
chk("PD2", "apos selo: completude PASS e verificador PASS", "PASS/PASS",
    f'{c2["verdict"]}/{v["verdict"]}', c2["verdict"] == "PASS" and v["verdict"] == "PASS")
chk("PD3", "manifest exclui SEAL-RECORD (condicao 7)", "SEAL-RECORD ausente",
    [m["path"] for m in P.member_manifest(d1) if "SEAL" in m["path"]],
    not any("SEAL-RECORD" in m["path"] for m in P.member_manifest(d1)))
sph0 = s["source_package_hash"]
# --- PD4 mutacao de CLAIM invalida selo e identidade
d2 = tmp / "pkg-MUT-CLAIM"; shutil.copytree(d1, d2)
P.wjsonl(d2 / "CLAIMS.jsonl", [{"local_id": "CL-0001", "text": "MUTADO"}])
v2 = SV.verify(d2, external_registry=reg, toolchain_dir=d2)
chk("PD4", "mutacao de CLAIM", "selo FAIL e hash muda",
    f'{v2["verdict"]}|{P.source_package_hash(P.member_manifest(d2))!=sph0}',
    v2["verdict"] != "PASS" and P.source_package_hash(P.member_manifest(d2)) != sph0)
# --- PD5 mutacao de CANDIDATE
d3 = tmp / "pkg-MUT-CAND"; shutil.copytree(d1, d3)
P.wjson(d3 / "SOURCE-LOCAL-CANDIDATES.json", {"rule_candidates": [{"local_id": "R-0001"}], "workflow_candidates": [], "anti_pattern_candidates": []})
v3 = SV.verify(d3, external_registry=reg, toolchain_dir=d3)
chk("PD5", "mutacao de CANDIDATE", "selo FAIL e hash muda",
    f'{v3["verdict"]}|{P.source_package_hash(P.member_manifest(d3))!=sph0}',
    v3["verdict"] != "PASS" and P.source_package_hash(P.member_manifest(d3)) != sph0)
# --- PD6 mutacao identity-relevant do COMPILE-TRACE
d4 = tmp / "pkg-MUT-TRACE"; shutil.copytree(d1, d4)
P.wjsonl(d4 / "COMPILE-TRACE.jsonl", [{"event": "FIXTURE", "model_resolved": "outro"}])
v4 = SV.verify(d4, external_registry=reg, toolchain_dir=d4)
chk("PD6", "mutacao identity-relevant do COMPILE-TRACE", "selo FAIL e hash muda",
    f'{v4["verdict"]}|{P.source_package_hash(P.member_manifest(d4))!=sph0}',
    v4["verdict"] != "PASS" and P.source_package_hash(P.member_manifest(d4)) != sph0)
# --- PD7 membro obrigatorio ausente falha completude, ainda que o selo isolado nao veja
d5 = build(tmp / "pkg-MISSING", omit="DECLARATION-SPACE-INDEX.json")
P.seal(d5, "FIXTURE2", "e"*64, reg)
c5 = P.completeness_gate(d5); v5 = SV.verify(d5, external_registry=reg, toolchain_dir=d5)
chk("PD7", "membro obrigatorio ausente", "completude FAIL (selo isolado nao basta)",
    f'completude={c5["verdict"]} selo={v5["verdict"]}', c5["verdict"] == "FAIL")
# --- PD8 sem selo nao e package valido
d6 = build(tmp / "pkg-NOSEAL"); v6 = SV.verify(d6, external_registry=reg, toolchain_dir=d6)
chk("PD8", "sem SEAL-RECORD", "verificador INVALID", v6["verdict"], v6["verdict"] == "INVALID")

if __name__ == "__main__":
    for x in R: print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['canary']:<4} {x['desc']:<48} obtido={x['got']}")
    n = sum(1 for x in R if x["ok"]); print(f"\n  {n}/{len(R)} dry-run de package/selo PASS")
    pathlib.Path("out").mkdir(exist_ok=True)
    pathlib.Path("out/seal-dryrun.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.rmtree(tmp)
    sys.exit(0 if n == len(R) else 2)
