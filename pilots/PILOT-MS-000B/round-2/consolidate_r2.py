#!/usr/bin/env python3
"""ROUND 2 — consolidacao. Todo numero vem dos artefatos; contagem manual proibida."""
from __future__ import annotations
import json, pathlib, sys, hashlib, collections
HERE=pathlib.Path(__file__).parent
sys.path.insert(0,str(HERE/"lib")); sys.path.insert(0,str(HERE.parent/"lib"))
import ms000b as M
from tokenizer import content_tokens, norm
from classifier import classify
import controls as C
OUT=HERE/"out"
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

runs=json.loads((OUT/"runs.json").read_text(encoding="utf-8"))
pkgs=json.loads((OUT/"source-packages.json").read_text(encoding="utf-8"))
pre =json.loads((OUT/"pre-run-controls.json").read_text(encoding="utf-8"))
trace=[json.loads(l) for l in (OUT/"COMPILE-TRACE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
R={}

R["kill1"]={"esperado":{"FULL":M.FULL_SHA,"CUT":M.CUT_SHA,"EVIDENCE":M.EV_SHA},
            "real":{"FULL":sha(M.FULL),"CUT":sha(M.CUT),"EVIDENCE":sha(M.EVID)}}
R["kill1"]["ok"]=R["kill1"]["esperado"]==R["kill1"]["real"]

ids=collections.Counter(); qual=set()
for k in ("A","B"):
    for it in pkgs[k]["items"]:
        ids[it["local_id"]]+=1; qual.add((pkgs[k]["source_package_hash"],it["local_id"]))
naked=sum(1 for r in runs for k in ("A","B") for c in runs[r]["sealed"][k]
          for q in c["qualified_refs"] if not q[0] or len(q)!=2)
wrong=sum(len(runs[r]["claims_no_pacote_errado"]) for r in runs)
R["identity"]={"local_ids_total":sum(ids.values()),"colisoes_nuas":sum(1 for n in ids.values() if n>1),
               "qualificadas_distintas":len(qual),"refs_cross_package_nuas":naked,
               "pkg_A":pkgs["A"]["source_package_hash"],"pkg_B":pkgs["B"]["source_package_hash"],
               "hashes_distintos":pkgs["A"]["source_package_hash"]!=pkgs["B"]["source_package_hash"],
               "claims_no_pacote_errado":wrong}
R["identity"]["ok"]=(R["identity"]["colisoes_nuas"]>0 and len(qual)==sum(ids.values())
                     and R["identity"]["hashes_distintos"] and naked==0 and wrong==0)

prov={"claims":0,"resolve":0,"quebradas":[]}
for r in runs:
    for k in ("A","B"):
        valid={i["local_id"]:i for i in pkgs[k]["items"]}; anc={a["anchor_id"]:a for a in pkgs[k]["anchors"]}
        for c in runs[r]["sealed"][k]:
            prov["claims"]+=1
            ok=bool(c["evidence_refs"]) and all(
               x in valid and valid[x]["anchor_id"] in anc
               and anc[valid[x]["anchor_id"]]["LOCATED_IN"]=="PASS"
               and anc[valid[x]["anchor_id"]]["slice_sha256"]==pkgs[k]["profile"]["provenance_chain"]["CHAPTER_SLICE"]
               and pkgs[k]["profile"]["provenance_chain"]["slice_derived_from"]==M.CUT_SHA
               for x in c["evidence_refs"])
            prov["resolve"]+=1 if ok else 0
            if not ok: prov["quebradas"].append(c["claim_id"])
prov["pct"]=prov["resolve"]/prov["claims"]*100 if prov["claims"] else None
prov["ok"]=prov["claims"]>0 and not prov["quebradas"]; R["provenance"]=prov

cl={}
for r in sorted(runs):
    d=runs[r]; st=collections.Counter()
    for k in ("A","B"):
        for c in d["raw"][k]: st[c.get("entailed_by","SEM_JULGAMENTO")]+=1
    cl[r]={"raw":sum(len(d["raw"][k]) for k in ("A","B")),
           "sealed":sum(len(d["sealed"][k]) for k in ("A","B")),
           "rejeitadas":sum(len(d["rejected"][k]) for k in ("A","B")),
           "estados":dict(st),
           "motivos":dict(collections.Counter(x["reject_reason"] for k in ("A","B") for x in d["rejected"][k]))}
R["claims"]=cl
R["kill3"]={"seladas":sum(v["sealed"] for v in cl.values()),
            "seladas_entailed":sum(1 for r in runs for k in ("A","B") for c in runs[r]["sealed"][k] if c.get("entailed_by")=="ENTAILED")}
R["kill3"]["ok"]=R["kill3"]["seladas"]==R["kill3"]["seladas_entailed"]

s=[cl[r]["sealed"] for r in sorted(cl)]
R["kill2"]={"por_run":{r:cl[r]["sealed"] for r in sorted(cl)},"max":max(s),"min":min(s),
            "razao":max(s)/min(s) if min(s) else None,"teto":1.5}
R["kill2"]["ok"]=bool(min(s)) and max(s)/min(s)<=1.5
sets={r:{norm(c["text"]) for k in ("A","B") for c in runs[r]["sealed"][k]} for r in sorted(runs)}
rs=sorted(sets)
R["kill2"]["sobreposicao"]={f"{a}∩{b}":len(sets[a]&sets[b]) for i,a in enumerate(rs) for b in rs[i+1:]}
R["kill2"]["nucleo_comum"]=len(set.intersection(*sets.values())) if len(sets)==3 else None

wp={r:runs[r]["workflow_preservation"] for r in runs}
R["workflow"]={"por_run":wp,"ok":all(wp[r][k]["preservado"] for r in wp for k in ("A","B"))}
R["blocking"]={"por_run":{r:{kk:vv for kk,vv in runs[r]["blocking"].items() if kk!="pairs"} for r in runs},
               "regra":runs[rs[0]]["blocking"]["rule"]}
R["blocking"]["controles_ok"]=all(c["survived"] for r in runs for c in runs[r]["blocking"]["controls"])
R["blocking"]["ok"]=R["blocking"]["controles_ok"]
R["relations"]={r:{"identical":len(runs[r]["relations"]["identical"]),
                   "pares_avaliados":runs[r]["relations"]["evaluated_pairs"]} for r in runs}

jc=pre["judge"]
R["isolation"]={"controles":[{k:v for k,v in x.items() if k!="why"} for x in jc if x["control_id"].startswith(("JC-POSITIVE","JC-CROSS"))],
                "claims_no_pacote_errado":wrong,"refs_nuas":naked}
R["isolation"]["ok"]=(all(x["ok"] for x in jc if x["control_id"].startswith(("JC-POSITIVE","JC-CROSS")))
                      and wrong==0 and naked==0)
R["controls"]={"tokenizer":pre["tokenizer"]["ok"],"consolidator":pre["consolidator"]["ok"],
               "judge":all(x["ok"] for x in jc),"judge_detalhe":[{"control_id":x["control_id"],
               "esperado":x["expected"],"obtido":x["obtido"],"ok":x["ok"]} for x in jc]}
esp=1+len(runs)*3
R["trace"]={"registradas":len(trace),"esperadas":esp,"cap":24,"dentro":len(trace)<=24,
            "tokens_in":sum(t["tokens"]["input"] for t in trace),
            "tokens_out":sum(t["tokens"]["output"] for t in trace),
            "modelos":sorted({t["model_resolved"] for t in trace}),
            "particoes":sorted({t["partition"] for t in trace}),
            "completo":all(all(t.get(f) for f in ("run","source","purpose","input_sha256","partition",
                "prompt_version","model_resolved","output_sha256")) for t in trace)}
R["trace"]["ok"]=R["trace"]["registradas"]==esp and R["trace"]["dentro"] and R["trace"]["completo"]
cfg={(t["model_resolved"],json.dumps(t["thinking"]),t["max_tokens"],t["prompt_version"])
     for t in trace if t["purpose"]=="CLAIM_GENERATION"}
R["trace"]["config_identica"]=len(cfg)==1

gates={"tokenizer_controls":R["controls"]["tokenizer"],"consolidator_controls":R["controls"]["consolidator"],
       "judge_controls":R["controls"]["judge"],"isolation_controls":R["isolation"]["ok"],
       "trace_completo":R["trace"]["ok"],"config_identica":R["trace"]["config_identica"],
       "dentro_do_cap":R["trace"]["dentro"],"kill1":R["kill1"]["ok"],"kill2":R["kill2"]["ok"],
       "kill3":R["kill3"]["ok"],"identity":R["identity"]["ok"],"provenance":R["provenance"]["ok"],
       "workflow":R["workflow"]["ok"],"blocking":R["blocking"]["ok"],"isolation":R["isolation"]["ok"]}
cls,why=classify(gates); R["gates"]=gates; R["classificacao"]=cls; R["motivo"]=why
(OUT/"summary.json").write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding="utf-8")
print(cls, "|", why)
for k,v in gates.items(): print(f"  {'OK  ' if v else 'FALHA'} {k}")
