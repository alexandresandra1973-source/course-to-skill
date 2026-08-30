#!/usr/bin/env python3
"""PILOT-MS-000B / ROUND 3 — runner.

HARD CAP 10. Plano: 1 judge-controls + 6 geracao + 3 entailment = 10. Margem ZERO.
Qualquer transiente que exija retry -> PILOT_MS_000B_ROUND_3_INVALID (sem retry).

Ordem BLOQUEANTE: controles mecanicos -> PC1..PC8 -> judge controls -> runs.
"""
from __future__ import annotations
import json,os,pathlib,sys,datetime,collections
HERE=pathlib.Path(__file__).parent
sys.path.insert(0,str(HERE/"lib")); sys.path.insert(0,str(HERE.parent/"round-2/lib"))
sys.path.insert(0,str(HERE.parent/"lib")); sys.path.insert(0,str(HERE.parent.parent/"PILOT-MS-000A"))
import package as P
from tokenizer import content_tokens, norm
from classifier import classify
import controls as C
import seal_verifier as SV
import package_canaries
sys.path.insert(0,str(HERE.parent/"round-2"))
import tokenizer_controls, consolidator_controls
import anthropic

OUT=HERE/"out"; OUT.mkdir(exist_ok=True)
PKGS=OUT/"packages"; REG=PKGS/"EXTERNAL-SEAL-REGISTRY.txt"
OPLOG=OUT/"OPERATIONAL-RUN-LOG.jsonl"          # timestamps FORA de todo pacote
MODEL="claude-opus-5"; THINKING={"type":"disabled"}; MAX_TOKENS=8000; HARD_CAP=10
PROMPT_VERSION="ms000b-r3-claimgen-v1"; JUDGE_VERSION="ms000b-r3-entail-v1"
BLOCK_MIN=2
CLAIMGEN_SYS=("Voce gera CLAIMS a partir de EVIDENCIAS de uma aula. Uma claim e uma asserçao "
 "normalizada, curta, autocontida, que segue INTEIRAMENTE das evidencias citadas, SEM "
 "acrescentar fato, causalidade, condicao ou generalizacao nova. Cada claim referencia >=1 "
 "local_id de evidencia DESTE pacote. NAO invente identificadores. NAO use conhecimento externo. "
 "Responda SOMENTE com JSON: {\"claims\":[{\"text\":\"...\",\"evidence_refs\":[\"EV-0001\"]}]}")
JUDGE_SYS=("Voce julga ENTAILMENT com rigor. Para cada item decida se TODA afirmacao da claim "
 "segue do conjunto de evidencias DADO, sem introduzir fato, causalidade, condicao ou "
 "generalizacao nova. Semelhanca lexical NAO e entailment. Se a evidencia dada nao trata do "
 "assunto da claim, o estado e NOT_ENTAILED. Se a evidencia toca o assunto mas e insuficiente "
 "para concluir e insuficiente para negar, o estado e INDETERMINATE. "
 "Estados: ENTAILED | NOT_ENTAILED | INDETERMINATE. "
 "Responda SOMENTE com JSON: {\"verdicts\":[{\"claim_id\":\"...\",\"state\":\"...\",\"why\":\"...\"}]}")

_n={"n":0}; _trace=collections.defaultdict(list)
def oplog(rec):
    with OPLOG.open("a",encoding="utf-8") as fh: fh.write(json.dumps(rec,ensure_ascii=False)+"\n")
def call(client,run,source,system,user,purpose,meta):
    if _n["n"]>=HARD_CAP: raise SystemExit(f"HARD CAP {HARD_CAP} — abortando")
    t0=datetime.datetime.now().astimezone().isoformat()
    r=client.messages.create(model=MODEL,max_tokens=MAX_TOKENS,thinking=THINKING,
                             system=system,messages=[{"role":"user","content":user}])
    _n["n"]+=1
    txt="".join(b.text for b in r.content if b.type=="text")
    # membro do pacote: SO identity-relevant. Sem timestamp.
    ident={"run":run,"source":source,"purpose":purpose,
           "input_sha256":P.sha_text(P.canon(meta)),"partition":meta.get("_partition"),
           "prompt_version":meta.get("_prompt_version"),"model_requested":MODEL,
           "model_resolved":r.model,"thinking":THINKING,"max_tokens":MAX_TOKENS,
           "output_sha256":P.sha_text(txt),"stop_reason":r.stop_reason,
           "tokens":{"input":r.usage.input_tokens,"output":r.usage.output_tokens}}
    _trace[(run,source)].append(ident)
    oplog({"call_seq":_n["n"],**{k:ident[k] for k in ("run","source","purpose")},
           "started_at":t0,"finished_at":datetime.datetime.now().astimezone().isoformat(),
           "nota":"timestamp operacional: registro, NUNCA identidade; FORA do member set"})
    return txt
def jparse(t):
    t=t.strip()
    if t.startswith("```"): t=t.split("```")[1].lstrip("json").strip()
    i,j=t.find("{"),t.rfind("}"); return json.loads(t[i:j+1])

def cands_selflocal(key):
    import yaml
    s=P.SOURCES[key]
    tm=yaml.safe_load(P.TMAP.read_text(encoding="utf-8"))["temporal_map"]
    st={x["segment_id"]:x.get("start_s") for x in tm}
    wf=yaml.safe_load(P.WF.read_text(encoding="utf-8")); dr=yaml.safe_load(P.DR.read_text(encoding="utf-8"))
    def inch(ids):
        ts=[st[x] for x in (ids or []) if x in st and st[x] is not None]
        return bool(ts) and s["t_ini"]<=min(ts)<=s["t_fim"]
    sb=collections.defaultdict(list)
    for x in wf["steps"]: sb[x["workflow_id"]].append(x)
    W=[]
    for w in wf["workflows"]:
        ss=sorted(sb[w["workflow_id"]],key=lambda x:x.get("order_key",0))
        if not ss or not inch(ss[0].get("segment_ids")): continue
        W.append({"local_id":w["workflow_id"],"name":w["name"],"evidence_refs":[],
                  "steps":[{"local_id":x["step_id"],"order_key":i+1,"name":x.get("name"),
                            "action":x.get("action"),"required_inputs":x.get("required_inputs"),
                            "missing_input_action":x.get("missing_input_action"),
                            "iteration_limit":x.get("iteration_limit"),"autonomy":x.get("autonomy"),
                            "evidence_refs":[]} for i,x in enumerate(ss)]})
    R=[{"local_id":r["rule_id"],"name":r.get("name"),"trigger":r.get("trigger"),
        "condition":r.get("condition"),"action":r.get("action"),"do_not":r.get("do_not") or [],
        "precedence":r.get("precedence"),"evidence_refs":[]}
       for r in dr["decision_rules"] if inch(r.get("segment_ids"))]
    A=[{"local_id":r["local_id"],"do_not":r["do_not"],"evidence_refs":[]} for r in R if r["do_not"]]
    return {"rule_candidates":R,"workflow_candidates":W,"anti_pattern_candidates":A}

def main():
    for f in (OPLOG,): 
        if f.exists(): f.unlink()
    if PKGS.exists():
        import shutil; shutil.rmtree(PKGS)
    PKGS.mkdir(parents=True); REG.write_text("# EXTERNAL SEAL REGISTRY — fora de todo diretorio selado\n",encoding="utf-8")

    # 1. controles mecanicos + PC1..PC8, BLOQUEANTES
    tk=tokenizer_controls.run(); cs=consolidator_controls.run(); pc=package_canaries.run()
    print(f"  tokenizer {'PASS' if tk['ok'] else 'FAIL'} | consolidator {'PASS' if cs['ok'] else 'FAIL'} | PC1-PC8 {'PASS' if pc['ok'] else 'FAIL'}")
    if not (tk["ok"] and cs["ok"] and pc["ok"]):
        P.wjson(OUT/"ROUND-3-INVALID.json",{"classificacao":"PILOT_MS_000B_ROUND_3_INVALID",
            "motivo":"controles mecanicos/PC falharam","tokenizer":tk,"consolidator":cs,"pc":pc}); return 2

    key=os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raw=(pathlib.Path.home()/".anthropic_key").read_text(encoding="utf-8")
        key=(raw.split("=",1)[1] if "=" in raw else raw).strip().strip('"\'')
    client=anthropic.Anthropic(api_key=key)
    cut=P.CUT.read_text(encoding="utf-8")
    assert P.sha_file(P.CUT)==P.CUT_SHA and P.sha_file(P.FULL)==P.FULL_SHA and P.sha_file(P.EVID)==P.EV_SHA

    # 2. judge controls (chamada 1/10) — usa os pacotes provisorios so para as quotes
    tmp=PKGS/"_ctrl"; base={}
    for k in ("A","B"): base[k]=P.build_content_members(k,cut,tmp/f"pkg-{k}")
    pk_for_ctrl={k:{"items":[{"local_id":e["local_id"],"quote":e["quote"]} for e in base[k]["evidence"]]} for k in ("A","B")}
    jc=C.judge_controls(pk_for_ctrl)
    items=[{"claim_id":c["control_id"],"claim":c["claim"],"evidence":c["evidence"]} for c in jc]
    txt=call(client,"CONTROLS","A+B",JUDGE_SYS,json.dumps(items,ensure_ascii=False),"JUDGE_CONTROLS",
             {"_partition":"1 chamada; os 5 controles do juiz","_prompt_version":JUDGE_VERSION,"items":items})
    got={v["claim_id"]:v for v in jparse(txt).get("verdicts",[])}
    res=[{**{a:b for a,b in c.items() if a!="evidence"},"obtido":got.get(c["control_id"],{}).get("state","<ausente>"),
          "why":got.get(c["control_id"],{}).get("why",""),
          "ok":got.get(c["control_id"],{}).get("state")==c["expected"]} for c in jc]
    P.wjson(OUT/"judge-controls.json",res)
    for x in res: print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['control_id']:<18} esperado={x['expected']:<16} obtido={x['obtido']}")
    if not all(x["ok"] for x in res):
        P.wjson(OUT/"ROUND-3-INVALID.json",{"classificacao":"PILOT_MS_000B_ROUND_3_INVALID",
            "motivo":"juiz nao demonstrou poder discriminante","judge_controls":res,"chamadas":_n["n"]}); return 2
    import shutil; shutil.rmtree(tmp)

    # 3. RUN-1/2/3
    runs={}
    for run in ("RUN-1","RUN-2","RUN-3"):
        _trace.clear(); pkgres={}; raw={}; rejected={}; sealed={}
        mats={}
        for k in ("A","B"):
            d=PKGS/run/f"pkg-{k}"; mats[k]=P.build_content_members(k,cut,d)
            ev=[{"local_id":e["local_id"],"quote":e["quote"],"epistemic_status":e["epistemic_status"]}
                for e in mats[k]["evidence"]]
            meta={"_partition":f"1 chamada por (source,run); todas as {len(ev)} evidencias do pacote {k}",
                  "_prompt_version":PROMPT_VERSION,"source_id":P.SOURCES[k]["source_id"],
                  "source_content_hash":mats[k]["content_hash"],"evidence":ev}
            user=(f"Pacote {k} — capitulo {P.SOURCES[k]['chapter_n']}: {P.SOURCES[k]['titulo']}\n\n"
                  "EVIDENCIAS:\n"+json.dumps(ev,ensure_ascii=False,indent=1))
            txt=call(client,run,k,CLAIMGEN_SYS,user,"CLAIM_GENERATION",meta)
            valid={e["local_id"] for e in mats[k]["evidence"]}
            rl,rj=[],[]
            for i,c in enumerate(jparse(txt).get("claims",[]),1):
                lid=f"CL-{i:04d}"
                refs=[{"ref_scope":"SELF","local_id":r} for r in (c.get("evidence_refs") or []) if r in valid]
                rec={"local_id":lid,"claim_id":f"{run}-{k}-{lid}","text":(c.get("text") or "").strip(),
                     "evidence_refs":refs}
                rl.append(rec)
                if not rec["text"]: rj.append({**rec,"reject_reason":"TEXTO_VAZIO"})
                elif not refs: rj.append({**rec,"reject_reason":"EVIDENCE_REFS_VAZIO_OU_INEXISTENTE"})
            raw[k]=rl; rejected[k]=rj
        cand=[c for k in ("A","B") for c in raw[k] if c["claim_id"] not in {r["claim_id"] for r in rejected[k]}]
        items=[{"claim_id":c["claim_id"],"claim":c["text"],
                "evidence":[e["quote"] for e in mats[c["claim_id"].split("-")[2]]["evidence"]
                            if e["local_id"] in {r["local_id"] for r in c["evidence_refs"]}]} for c in cand]
        meta={"_partition":f"1 chamada por run; TODAS as {len(items)} claims candidatas",
              "_prompt_version":JUDGE_VERSION,"items":items}
        txt=call(client,run,"A+B",JUDGE_SYS,json.dumps(items,ensure_ascii=False),"ENTAILED_BY_JUDGMENT",meta)
        verd={v["claim_id"]:v for v in jparse(txt).get("verdicts",[])}
        by={c["claim_id"] for c in cand}
        for k in ("A","B"):
            s=[]
            for c in raw[k]:
                if c["claim_id"] not in by: continue
                v=verd.get(c["claim_id"],{"state":"INDETERMINATE","why":"sem veredito"})
                c["entailed_by"]=v["state"]; c["entail_why"]=v.get("why","")
                if v["state"]=="ENTAILED": s.append(c)
                else: rejected[k].append({**c,"reject_reason":f"ENTAILED_BY={v['state']}"})
            sealed[k]=s
        # --- montar, verificar completude, selar
        for k in ("A","B"):
            d=PKGS/run/f"pkg-{k}"
            P.write_generated_members(d,sealed[k],cands_selflocal(k),
                                      _trace[(run,k)]+[t for t in _trace[(run,"A+B")]])
            P.local_coherence(d)
            P.declaration_space_index(d,P.SOURCES[k]["source_id"],mats[k]["content_hash"])
            P.write_toolchain(d)
            g=P.completeness_gate(d)
            if g["verdict"]!="PASS" and g["codes"]!=["REQUIRED_MEMBER_MISSING"]:
                pass
            # o SEAL-RECORD ainda nao existe; a completude final e apos selar
            s=P.seal(d,P.SOURCES[k]["source_id"],mats[k]["content_hash"],REG)
            g2=P.completeness_gate(d); v=SV.verify(d,REG,d)
            pkgres[k]={"dir":str(d.relative_to(OUT)),"source_id":P.SOURCES[k]["source_id"],
                       "source_content_hash":mats[k]["content_hash"],
                       "source_package_hash":s["source_package_hash"],
                       "member_manifest_hash":s["member_manifest_hash"],
                       "seal_record_hash":s["seal_record_hash"],"members_count":s["members_count"],
                       "completeness":g2,"seal":{"verdict":v["verdict"],"codes":v["codes"]},
                       "profile_sha":P.sha_file(d/"SOURCE-PROFILE.json"),
                       "coherence":json.loads((d/"LOCAL-COHERENCE-REPORT.json").read_text(encoding="utf-8"))}
        runs[run]={"raw":raw,"rejected":rejected,"sealed":sealed,"packages":pkgres,
                   "candidates":{k:cands_selflocal(k) for k in ("A","B")}}
        print(f"  {run}: sealed A={len(sealed['A'])} B={len(sealed['B'])} | "
              f"pkgA={pkgres['A']['source_package_hash'][:12]}… pkgB={pkgres['B']['source_package_hash'][:12]}… | "
              f"selo A={pkgres['A']['seal']['verdict']} B={pkgres['B']['seal']['verdict']} | chamadas={_n['n']}")
    P.wjson(OUT/"runs.json",runs)
    P.wjson(OUT/"pre-run-controls.json",{"tokenizer":tk,"consolidator":cs,"pc":pc,"judge":res})
    print(f"  TOTAL de chamadas: {_n['n']} de {HARD_CAP}")
    return 0

if __name__=="__main__": sys.exit(main())
