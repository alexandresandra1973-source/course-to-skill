#!/usr/bin/env python3
"""ROUND 3 — canarios PC1..PC8 do PACKAGE CONTRACT. Zero chamadas de modelo.

Todos sobre FIXTURES SINTETICAS. Reutilizam o seal_verifier.py do MS-000A SEM
alteracao — nao se cria uma segunda definicao de selo.
Todos tem de passar ANTES da primeira chamada de modelo.
"""
from __future__ import annotations
import json,sys,pathlib,shutil,tempfile,collections
HERE=pathlib.Path(__file__).parent
sys.path.insert(0,str(HERE/"lib")); sys.path.insert(0,str(HERE.parent.parent/"PILOT-MS-000A"))
import package as P
import seal_verifier as SV

def fake_claims(n=3):
    return [{"local_id":f"CL-{i:04d}","text":f"synthetic claim {i}",
             "evidence_refs":[{"ref_scope":"SELF","local_id":"EV-0001"}],
             "entailed_by":"ENTAILED"} for i in range(1,n+1)]
def fake_cands():
    return {"rule_candidates":[{"local_id":"R-9001","name":"syn","trigger":"t","condition":"c",
              "action":"a","do_not":[],"evidence_refs":[{"ref_scope":"SELF","local_id":"EV-0001"}]}],
            "workflow_candidates":[{"local_id":"WF-9001","name":"syn wf",
              "evidence_refs":[{"ref_scope":"SELF","local_id":"EV-0001"}],
              "steps":[{"local_id":"S-1","order_key":1,"name":"a","action":"x","evidence_refs":[]},
                       {"local_id":"S-2","order_key":2,"name":"b","action":"y","evidence_refs":[]}]}],
            "anti_pattern_candidates":[]}
def fake_trace():
    return [{"run":"FX","source":"A","purpose":"CLAIM_GENERATION","input_sha256":"a"*64,
             "partition":"1 chamada por (source,run)","prompt_version":"fx-v1",
             "model_requested":"claude-opus-5","model_resolved":"claude-opus-5",
             "thinking":{"type":"disabled"},"max_tokens":8000,"output_sha256":"b"*64,
             "stop_reason":"end_turn","tokens":{"input":1,"output":1}}]

def build_fixture(root,key="A",skip=()):
    cut=P.CUT.read_text(encoding="utf-8")
    d=root/f"pkg-{key}"; d.mkdir(parents=True,exist_ok=True)
    m=P.build_content_members(key,cut,d)
    if "CLAIMS" not in skip: P.wjsonl(d/"CLAIMS.jsonl",fake_claims())
    if "CANDIDATES" not in skip: P.wjson(d/"SOURCE-LOCAL-CANDIDATES.json",fake_cands())
    if "TRACE" not in skip: P.wjsonl(d/"COMPILE-TRACE.jsonl",fake_trace())
    P.write_toolchain(d)
    if "CLAIMS" not in skip and "CANDIDATES" not in skip: P.local_coherence(d)
    P.declaration_space_index(d,P.SOURCES[key]["source_id"],m["content_hash"])
    return d,m

def sealed_fixture(root,key="A"):
    d,m=build_fixture(root,key)
    reg=root/"EXTERNAL-SEAL-REGISTRY.txt"
    s=P.seal(d,P.SOURCES[key]["source_id"],m["content_hash"],reg)
    return d,m,s,reg

def run():
    R=[]
    def add(cid,ok,detail): R.append({"canary":cid,"ok":bool(ok),"detail":detail})

    # ---- PC1/PC2/PC3: mutacao de membro -> hash muda E selo falha
    for cid,member,mut in (("PC1","CLAIMS.jsonl","claims"),
                           ("PC2","SOURCE-LOCAL-CANDIDATES.json","candidates"),
                           ("PC3","COMPILE-TRACE.jsonl","compile-trace")):
        root=pathlib.Path(tempfile.mkdtemp()); d,m,s,reg=sealed_fixture(root)
        sid_before=json.loads((d/"SOURCE-PROFILE.json").read_text(encoding="utf-8"))["source_id"]
        v0=SV.verify(d,reg,d)
        txt=(d/member).read_text(encoding="utf-8")
        (d/member).write_text(txt.replace("synthetic claim 1","MUTATED claim 1")
                                 .replace('"R-9001"','"R-9999"')
                                 .replace('"claude-opus-5"','"MUTATED-MODEL"',1),encoding="utf-8")
        ph_after=P.source_package_hash(P.member_manifest(d))
        v1=SV.verify(d,reg,d)
        sid_after=json.loads((d/"SOURCE-PROFILE.json").read_text(encoding="utf-8"))["source_id"]
        ok=(v0["verdict"]=="PASS" and ph_after!=s["source_package_hash"] and v1["verdict"]=="FAIL"
            and "MEMBER_HASH_MISMATCH" in v1["codes"] and "DOES_NOT_VALIDATE_IN_PLACE" in v1["codes"])
        det={"selo_antes":v0["verdict"],"hash_mudou":ph_after!=s["source_package_hash"],
             "selo_depois":v1["verdict"],"codigos":v1["codes"],"membro":mut}
        if cid=="PC3":
            det["source_id_estavel"]=(sid_before==sid_after); ok=ok and sid_before==sid_after
        add(cid,ok,det); shutil.rmtree(root)

    # ---- PC4: SOURCE-PROFILE byte-identico entre "runs"
    r1=pathlib.Path(tempfile.mkdtemp()); r2=pathlib.Path(tempfile.mkdtemp())
    d1,_=build_fixture(r1); d2,_=build_fixture(r2)
    p1=P.sha_file(d1/"SOURCE-PROFILE.json"); p2=P.sha_file(d2/"SOURCE-PROFILE.json")
    prof=json.loads((d1/"SOURCE-PROFILE.json").read_text(encoding="utf-8"))
    forbidden=[k for k in ("model","prompt_version","judge_version","thinking","max_tokens",
                           "partition","model_policy") if k in prof]
    add("PC4",p1==p2 and not forbidden,
        {"profile_sha_run1":p1[:16]+"…","profile_sha_run2":p2[:16]+"…","identico":p1==p2,
         "campos_proibidos_no_profile":forbidden})
    shutil.rmtree(r1); shutil.rmtree(r2)

    # ---- PC5/PC6/PC7: membro obrigatorio ausente -> COMPLETENESS GATE
    for cid,skip,member in (("PC5",("CLAIMS",),"CLAIMS"),
                            ("PC6",("CANDIDATES",),"SOURCE_LOCAL_CANDIDATES"),
                            ("PC7",("TRACE",),"COMPILE-TRACE")):
        root=pathlib.Path(tempfile.mkdtemp()); d,m=build_fixture(root,skip=skip)
        g=P.completeness_gate(d)
        # o SELO nao detecta: o membro nunca entrou no manifesto
        reg=root/"EXTERNAL-SEAL-REGISTRY.txt"
        P.seal(d,P.SOURCES["A"]["source_id"],m["content_hash"],reg)
        v=SV.verify(d,reg,d)
        ok=(g["verdict"]=="FAIL" and "REQUIRED_MEMBER_MISSING" in g["codes"]
            and any(x["member"]==member for x in g["missing"]))
        add(cid,ok,{"gate":g["verdict"],"codigos":g["codes"],
                    "ausente":[x["member"] for x in g["missing"]],
                    "selo_isolado_diria":v["verdict"],
                    "licao":"o selo NAO detecta membro que nunca entrou no manifesto"})
        shutil.rmtree(root)

    # ---- PC8: sem SEAL-RECORD -> INVALID_PACKAGE (pre-declarado)
    root=pathlib.Path(tempfile.mkdtemp()); d,m=build_fixture(root)
    reg=root/"EXTERNAL-SEAL-REGISTRY.txt"; reg.write_text("",encoding="utf-8")
    v=SV.verify(d,reg,d); g=P.completeness_gate(d)
    ok=(v["verdict"]=="INVALID" and "SEAL_RECORD_MISSING" in v["codes"]
        and g["verdict"]=="FAIL" and "REQUIRED_MEMBER_MISSING" in g["codes"])
    add("PC8",ok,{"seal_verifier":v["verdict"],"codigos_selo":v["codes"],
                  "completeness":g["verdict"],
                  "estado_pre_declarado":"INVALID_PACKAGE",
                  "nota":"nao e defeito semantico da fonte; e objeto nao avaliavel como Source Package"})
    shutil.rmtree(root)
    return {"canaries":R,"ok":all(x["ok"] for x in R)}

if __name__=="__main__":
    R=run()
    for x in R["canaries"]:
        print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['canary']}  {json.dumps(x['detail'],ensure_ascii=False)[:150]}")
    print(f"\n  PC1-PC8: {'PASS' if R['ok'] else 'FAIL'}")
    sys.exit(0 if R["ok"] else 2)
