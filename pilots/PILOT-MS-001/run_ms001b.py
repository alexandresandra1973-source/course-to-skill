#!/usr/bin/env python3
"""PILOT-MS-001B — 3 runs independentes. HARD CAP 15, RETRY 0."""
import sys, os, json, hashlib, pathlib, datetime, collections
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib"))
import relation_validate as RV
import anthropic
MODEL="claude-opus-5"; THINKING={"type":"disabled"}; MAX_TOKENS=8000; HARD_CAP=15
OUT=H/"out-ms001b"; RAW=OUT/"raw"; RAW.mkdir(parents=True,exist_ok=True)
PS=json.loads((H/"ms001b/PAIRSET-MS001B-V1.json").read_text(encoding="utf-8"))
PI=json.loads((H/"ms001b/PAIR-INPUTS-MS001B.json").read_text(encoding="utf-8"))
PROMPT=(H/"ms001b/RELATION-PROMPT-v1.txt").read_text(encoding="utf-8")
SCHEMA=(H/"ms001b/RELATION-SCHEMA-v1.json").read_text(encoding="utf-8")
JC=json.loads((H/"ms001b/JUDGE-CONTROLS-J1-J10.json").read_text(encoding="utf-8"))
canon=lambda o: json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(",",":"))
sha=lambda s: hashlib.sha256(s.encode()).hexdigest()
_n={"n":0}; CALLS=[]
def split(t):
    a=t.index("[SYSTEM]"); b=t.index("[USER]"); return t[a+8:b].strip(), t[b+6:].strip()
SYS,USR=split(PROMPT)
IDS=[p["pair_id"] for p in PS["pairs"]]
BATCHES={f"BATCH-{i+1}":IDS[i*25:(i+1)*25] for i in range(4)}

def call(client,run,label,system,user,meta):
    if _n["n"]>=HARD_CAP: raise SystemExit(f"HARD CAP {HARD_CAP} — MS_001B_INVALID")
    t0=datetime.datetime.now().astimezone().isoformat()
    r=client.messages.create(model=MODEL,max_tokens=MAX_TOKENS,thinking=THINKING,
                             system=system,messages=[{"role":"user","content":user}])
    _n["n"]+=1
    txt="".join(b.text for b in r.content if b.type=="text")
    (RAW/f"{run}-{label}-RAW.txt").write_text(txt,encoding="utf-8")
    (RAW/f"{run}-{label}-INPUT.json").write_text(json.dumps(
        {"system_sha256":sha(system),"user_sha256":sha(user),"meta":meta},ensure_ascii=False,indent=1),encoding="utf-8")
    rec={"call_seq":_n["n"],"run":run,"label":label,"model_requested":MODEL,"model_resolved":r.model,
         "thinking":THINKING,"max_tokens":MAX_TOKENS,"stop_reason":r.stop_reason,
         "input_sha256":sha(canon(meta)),"output_sha256":sha(txt),
         "tokens":{"input":r.usage.input_tokens,"output":r.usage.output_tokens},
         "started_at":t0,"finished_at":datetime.datetime.now().astimezone().isoformat()}
    CALLS.append(rec)
    if r.model!=MODEL: raise SystemExit(f"model_resolved={r.model} — MS_001B_INVALID")
    return txt
def jparse(t):
    t=t.strip()
    if t.startswith("```"): t=t.split("\n",1)[1].rsplit("```",1)[0]
    a,b=t.find("{"),t.rfind("}"); return t[a:b+1] if a>=0 else t
def pair_payload(pid):
    p=PI[pid]
    return {"pair_id":pid,
      "left":{"claim_ref":p["left"]["typed_ref"],"text":p["left"]["text"],
              "language":p["left"]["source_language"],"qualifiers":p["left"]["qualifiers"],
              "evidence":[{"evidence_id":e["evidence_id"],"excerpt":e["excerpt"],"anchor":e["anchor"]} for e in p["left"]["evidence"]]},
      "right":{"claim_ref":p["right"]["typed_ref"],"text":p["right"]["text"],
               "language":p["right"]["source_language"],"qualifiers":p["right"]["qualifiers"],
               "evidence":[{"evidence_id":e["evidence_id"],"excerpt":e["excerpt"],"anchor":e["anchor"]} for e in p["right"]["evidence"]]}}
def ctrl_payload():
    out=[]
    for c in JC["controls"]:
        out.append({"pair_id":sha(c["id"]).replace(sha(c["id"])[:0],""),  # placeholder abaixo
                    })
    return out

def main():
    key=pathlib.Path(os.path.expanduser("~/.anthropic_key")).read_text().strip()
    client=anthropic.Anthropic(api_key=key)
    R={"pilot":"PILOT-MS-001B","hard_cap":HARD_CAP,"pairset_hash":PS["PAIRSET_HASH"],"runs":{}}
    # controles: pair_id sintetico deterministico
    CP=[{"pair_id":sha("CTRL-"+c["id"]),"left":{"claim_ref":{"source_package_hash":"0"*64,"entity_kind":"claim","local_id":"CL-9000"},
          "text":c["left"]["text"],"language":"pt","qualifiers":c["left"]["qualifiers"],
          "evidence":[{"evidence_id":e["evidence_id"],"excerpt":e["excerpt"],"anchor":{"local_id":"AN-9000","start_s":0,"end_s":1}} for e in c["left"]["evidence"]]},
         "right":{"claim_ref":{"source_package_hash":"f"*64,"entity_kind":"claim","local_id":"CL-9100"},
          "text":c["right"]["text"],"language":"pt","qualifiers":c["right"]["qualifiers"],
          "evidence":[{"evidence_id":e["evidence_id"],"excerpt":e["excerpt"],"anchor":{"local_id":"AN-9100","start_s":0,"end_s":1}} for e in c["right"]["evidence"]]},
         "_id":c["id"],"_expect":c["expect"]} for c in JC["controls"]]
    CSENT={x["pair_id"]:{"left":{e["evidence_id"] for e in x["left"]["evidence"]},
                         "right":{e["evidence_id"] for e in x["right"]["evidence"]}} for x in CP}
    for run in ("RUN-1","RUN-2","RUN-3"):
        rr={"control":None,"batches":{},"judgments":{},"status":None}
        u=USR.replace("{BATCH_ID}","BATCH-1").replace("{PAIRS_JSON}",
             json.dumps([{k:v for k,v in x.items() if not k.startswith("_")} for x in CP],ensure_ascii=False,indent=1)).replace("{JSON_SCHEMA}",SCHEMA)
        txt=call(client,run,"CONTROL",SYS,u,{"controls":[c["_id"] for c in CP]})
        doc,errs=RV.validate(jparse(txt),"BATCH-1",CSENT)
        if doc is None:
            rr["status"]="INVALID"; rr["control"]={"schema_errors":errs}
            R["runs"][run]=rr; print(f"  {run} CONTROL schema INVALIDO: {errs}"); continue
        got={v["pair_id"]:v for v in doc["judgments"]}
        det=[]
        for c in CP:
            g=got[c["pair_id"]]; e=c["_expect"]; ok=True
            if "relation" in e: ok &= g["relation"]==e["relation"]
            if "relation_not" in e: ok &= g["relation"]!=e["relation_not"]
            if "direction" in e: ok &= g["direction"]==e["direction"]
            if "scope_state" in e: ok &= g["scope_state"]==e["scope_state"]
            det.append({"id":c["_id"],"expect":e,"got":{k:g[k] for k in ("relation","direction","scope_state")},"ok":bool(ok)})
        cok=all(x["ok"] for x in det)
        rr["control"]={"detail":det,"ok":cok}
        for x in det: print(f"  {run} {x['id']:<4} {'OK ' if x['ok'] else 'FALHA'} obtido={x['got']['relation']}/{x['got']['direction']}/{x['got']['scope_state']}")
        if not cok:
            rr["status"]="INVALID"; R["runs"][run]=rr
            print(f"  {run}: controle FALHOU — batches NAO queimados"); continue
        for bid,ids in BATCHES.items():
            sent={i:{"left":{e["evidence_id"] for e in PI[i]["left"]["evidence"]},
                     "right":{e["evidence_id"] for e in PI[i]["right"]["evidence"]}} for i in ids}
            u=USR.replace("{BATCH_ID}",bid).replace("{PAIRS_JSON}",
                 json.dumps([pair_payload(i) for i in ids],ensure_ascii=False,indent=1)).replace("{JSON_SCHEMA}",SCHEMA)
            txt=call(client,run,bid,SYS,u,{"batch":bid,"pair_ids":ids})
            doc,errs=RV.validate(jparse(txt),bid,sent)
            if doc is None:
                rr["status"]="INVALID"; rr["batches"][bid]={"errors":errs}
                print(f"  {run} {bid} INVALIDO: {errs}"); break
            for v in doc["judgments"]: rr["judgments"][v["pair_id"]]=v
            rr["batches"][bid]={"n":len(doc["judgments"]),"errors":[]}
            print(f"  {run} {bid}: {len(doc['judgments'])} judgments OK")
        if rr["status"]!="INVALID":
            rr["status"]="VALID" if len(rr["judgments"])==97 else "INVALID"
            if len(rr["judgments"])!=97: rr["motivo"]=f"{len(rr['judgments'])}/97 julgados"
        R["runs"][run]=rr
        d=collections.Counter(v["relation"] for v in rr["judgments"].values())
        print(f"  {run} [{rr['status']}]: {dict(d)}\n")
    R["calls"]=CALLS; R["executed_calls"]=_n["n"]
    (OUT/"RUNS.json").write_text(json.dumps(R,ensure_ascii=False,indent=1),encoding="utf-8")
    print(f"  chamadas: {_n['n']}/{HARD_CAP}")
    return 0
if __name__=="__main__": sys.exit(main())
