#!/usr/bin/env python3
"""PILOT-MS-000B / ROUND 2 — runner.

Ordem BLOQUEANTE:
  1. controles mecanicos (tokenizer, consolidator)      0 chamadas
  2. controles do JUIZ (3 estados + 2 cross-source)     1 chamada
     -> se falhar, ROUND_2_INVALID e PARA ANTES de julgar claim gerada
  3. RUN-1/2/3: geracao (6) + julgamento (3)            9 chamadas
  TOTAL PLANEJADO: 10 de 24
"""
from __future__ import annotations
import json, os, pathlib, sys, datetime
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE / "lib"))
sys.path.insert(0, str(HERE.parent / "lib"))
import ms000b as M                      # slicer/packager/fusion da ROUND 1, sem alteracao
from tokenizer import content_tokens, norm
from classifier import classify
import controls as C
import tokenizer_controls, consolidator_controls
import anthropic

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
TRACE = OUT / "COMPILE-TRACE.jsonl"
MODEL="claude-opus-5"; THINKING={"type":"disabled"}; MAX_TOKENS=8000; HARD_CAP=24
PROMPT_VERSION="ms000b-r2-claimgen-v1"; JUDGE_VERSION="ms000b-r2-entail-v1"
BLOCK_MIN_SHARED=2

CLAIMGEN_SYS=("Voce gera CLAIMS a partir de EVIDENCIAS de uma aula. Uma claim e uma asserçao "
 "normalizada, curta, autocontida, que segue INTEIRAMENTE das evidencias citadas, SEM "
 "acrescentar fato, causalidade, condicao ou generalizacao nova. Cada claim referencia >=1 "
 "local_id de evidencia deste pacote. NAO invente identificadores. NAO use conhecimento externo. "
 "Responda SOMENTE com JSON: {\"claims\":[{\"text\":\"...\",\"evidence_refs\":[\"EV-0001\"]}]}")
JUDGE_SYS=("Voce julga ENTAILMENT com rigor. Para cada item decida se TODA afirmacao da claim "
 "segue do conjunto de evidencias DADO, sem introduzir fato, causalidade, condicao ou "
 "generalizacao nova. Semelhanca lexical NAO e entailment. Se a evidencia dada nao trata do "
 "assunto da claim, o estado e NOT_ENTAILED. Se a evidencia toca o assunto mas e insuficiente "
 "para concluir e insuficiente para negar, o estado e INDETERMINATE. "
 "Estados: ENTAILED | NOT_ENTAILED | INDETERMINATE. "
 "Responda SOMENTE com JSON: {\"verdicts\":[{\"claim_id\":\"...\",\"state\":\"...\",\"why\":\"...\"}]}")

_n={"n":0}
def call(client, run, source, system, user, purpose, meta):
    if _n["n"] >= HARD_CAP: raise SystemExit(f"HARD CAP {HARD_CAP} atingido")
    t0=datetime.datetime.now().astimezone().isoformat()
    r=client.messages.create(model=MODEL,max_tokens=MAX_TOKENS,thinking=THINKING,
                             system=system,messages=[{"role":"user","content":user}])
    _n["n"]+=1
    txt="".join(b.text for b in r.content if b.type=="text")
    rec={"call_seq":_n["n"],"run":run,"source":source,"purpose":purpose,
         "input_sha256":M.sha_text(M.canon(meta)),"partition":meta.get("_partition"),
         "prompt_version":meta.get("_prompt_version"),"model_requested":MODEL,
         "model_resolved":r.model,"thinking":THINKING,"max_tokens":MAX_TOKENS,
         "output_sha256":M.sha_text(txt),"stop_reason":r.stop_reason,
         "tokens":{"input":r.usage.input_tokens,"output":r.usage.output_tokens},
         "timestamp_operacional":t0,"nota_timestamp":"registro operacional; NUNCA identidade"}
    with TRACE.open("a",encoding="utf-8") as fh: fh.write(json.dumps(rec,ensure_ascii=False)+"\n")
    return txt
def jparse(t):
    t=t.strip()
    if t.startswith("```"): t=t.split("```")[1].lstrip("json").strip()
    i,j=t.find("{"),t.rfind("}"); return json.loads(t[i:j+1])

def main():
    if TRACE.exists(): TRACE.unlink()
    # ---------- 1. controles mecanicos, BLOQUEANTES
    tk=tokenizer_controls.run(); cs=consolidator_controls.run()
    print(f"  tokenizer controls: {'PASS' if tk['ok'] else 'FAIL'} | consolidator controls: {'PASS' if cs['ok'] else 'FAIL'}")
    if not (tk["ok"] and cs["ok"]):
        (OUT/"ROUND-2-INVALID.json").write_text(json.dumps({"classificacao":"PILOT_MS_000B_ROUND_2_INVALID",
            "motivo":"controles mecanicos falharam","tokenizer":tk,"consolidator":cs},ensure_ascii=False,indent=2),encoding="utf-8")
        return 2

    key=os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raw=(pathlib.Path.home()/".anthropic_key").read_text(encoding="utf-8")
        key=(raw.split("=",1)[1] if "=" in raw else raw).strip().strip('"\'')
    client=anthropic.Anthropic(api_key=key)
    started=datetime.datetime.now().astimezone().isoformat()

    cut=M.CUT.read_text(encoding="utf-8")
    assert M.sha(M.CUT)==M.CUT_SHA and M.sha(M.FULL)==M.FULL_SHA and M.sha(M.EVID)==M.EV_SHA
    policy={"model":MODEL,"thinking":THINKING,"max_tokens":MAX_TOKENS,
            "prompt_version":PROMPT_VERSION,"judge_version":JUDGE_VERSION}
    pkgs,bodies,cands={},{},{}
    for k in ("A","B"):
        pkgs[k],bodies[k]=M.build_package(k,cut,policy); cands[k]=M.source_local_candidates(k)
    (OUT/"source-packages.json").write_text(json.dumps(pkgs,ensure_ascii=False,indent=2),encoding="utf-8")

    # ---------- 2. controles do JUIZ, BLOQUEANTES, ANTES de qualquer claim gerada
    jc=C.judge_controls(pkgs)
    items=[{"claim_id":c["control_id"],"claim":c["claim"],"evidence":c["evidence"]} for c in jc]
    txt=call(client,"CONTROLS","A+B",JUDGE_SYS,json.dumps(items,ensure_ascii=False),
             "JUDGE_CONTROLS",{"_partition":"1 chamada; os 5 controles do juiz",
                               "_prompt_version":JUDGE_VERSION,"items":items})
    got={v["claim_id"]:v for v in jparse(txt).get("verdicts",[])}
    res=[]
    for c in jc:
        g=got.get(c["control_id"],{"state":"<ausente>","why":""})
        res.append({**{k:v for k,v in c.items() if k!="evidence"},
                    "obtido":g["state"],"why":g.get("why",""),
                    "ok":g["state"]==c["expected"],"n_evidencias":len(c["evidence"])})
    jok=all(x["ok"] for x in res)
    (OUT/"judge-controls.json").write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding="utf-8")
    for x in res: print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['control_id']:<18} esperado={x['expected']:<16} obtido={x['obtido']}")
    if not jok:
        (OUT/"ROUND-2-INVALID.json").write_text(json.dumps({"classificacao":"PILOT_MS_000B_ROUND_2_INVALID",
            "motivo":"juiz nao demonstrou poder discriminante","judge_controls":res,
            "chamadas":_n["n"]},ensure_ascii=False,indent=2),encoding="utf-8")
        print("  -> ROUND_2_INVALID: PARANDO ANTES de julgar claims geradas")
        return 2

    # ---------- 3. RUN-1/2/3
    runs={}
    for run in ("RUN-1","RUN-2","RUN-3"):
        raw,sealed,rejected={},{},{}
        for k in ("A","B"):
            ev=[{"local_id":i["local_id"],"quote":i["quote"],"epistemic_status":i["epistemic_status"]} for i in pkgs[k]["items"]]
            meta={"_partition":f"1 chamada por (source,run); todas as {len(ev)} evidencias do pacote {k}",
                  "_prompt_version":PROMPT_VERSION,"source_package_hash":pkgs[k]["source_package_hash"],"evidence":ev}
            user=(f"Pacote {k} — capitulo {pkgs[k]['profile']['chapter_n']}: {pkgs[k]['profile']['chapter_titulo']}\n\n"
                  "EVIDENCIAS:\n"+json.dumps(ev,ensure_ascii=False,indent=1))
            txt=call(client,run,k,CLAIMGEN_SYS,user,"CLAIM_GENERATION",meta)
            valid={i["local_id"] for i in pkgs[k]["items"]}
            rl,rj=[],[]
            for n,c in enumerate(jparse(txt).get("claims",[]),1):
                cid=f"{run}-{k}-CL-{n:04d}"
                refs=[r for r in (c.get("evidence_refs") or []) if r in valid]
                rec={"claim_id":cid,"package":k,"text":(c.get("text") or "").strip(),"evidence_refs":refs,
                     "qualified_refs":[[pkgs[k]["source_package_hash"],r] for r in refs]}
                rl.append(rec)
                if not rec["text"]: rj.append({**rec,"reject_reason":"TEXTO_VAZIO"})
                elif not refs: rj.append({**rec,"reject_reason":"EVIDENCE_REFS_VAZIO_OU_INEXISTENTE"})
            raw[k]=rl; rejected[k]=rj
        cand=[c for k in ("A","B") for c in raw[k] if c["claim_id"] not in {r["claim_id"] for r in rejected[k]}]
        items=[{"claim_id":c["claim_id"],"claim":c["text"],
                "evidence":[i["quote"] for i in pkgs[c["package"]]["items"] if i["local_id"] in c["evidence_refs"]]} for c in cand]
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
        # blocagem com tokenizador CORRIGIDO
        ta={c["claim_id"]:content_tokens(c["text"]) for c in sealed["A"]}
        tb={c["claim_id"]:content_tokens(c["text"]) for c in sealed["B"]}
        possible=[(a,b) for a in ta for b in tb]
        surv=[(a,b) for a,b in possible if len(ta[a]&tb[b])>=BLOCK_MIN_SHARED]
        ctrl=[{"control_id":c["control_id"],
               "shared":sorted(content_tokens(c["a_text"])&content_tokens(c["b_text"])),
               "survived":len(content_tokens(c["a_text"])&content_tokens(c["b_text"]))>=BLOCK_MIN_SHARED}
              for c in C.BLOCK_CONTROLS]
        blk={"possible":len(possible),"survived":len(surv),
             "reduction_pct":(1-len(surv)/len(possible))*100 if possible else None,
             "controls":ctrl,"rule":f"shared_content_tokens >= {BLOCK_MIN_SHARED}"}
        rel=M.relations_mechanical(sealed["A"],sealed["B"],surv)
        wp={k:{"struct_source":M.struct_hash(cands[k]),"struct_fusion":M.struct_hash(cands[k]),
               "preservado":True,"workflows":len(cands[k]["workflow_candidates"]),
               "steps":sum(len(w["steps"]) for w in cands[k]["workflow_candidates"])} for k in ("A","B")}
        fus=M.fusion_package(pkgs["A"],pkgs["B"],sealed["A"],sealed["B"],cands["A"],cands["B"],rel,{**blk,"pairs":surv})
        for k in ("A","B"):
            wp[k]["struct_fusion"]=M.struct_hash(fus["transported_candidates"][k])
            wp[k]["preservado"]=wp[k]["struct_source"]==wp[k]["struct_fusion"]
        # verifica que nenhuma claim selada esta no pacote errado
        wrongpkg=[c["claim_id"] for k in ("A","B") for c in sealed[k]
                  if any(r not in {i["local_id"] for i in pkgs[k]["items"]} for r in c["evidence_refs"])]
        runs[run]={"raw":raw,"rejected":rejected,"sealed":sealed,"blocking":blk,"relations":rel,
                   "workflow_preservation":wp,"fusion_id":fus["fusion_id"],"claims_no_pacote_errado":wrongpkg}
        (OUT/f"fusion-package-{run}.json").write_text(json.dumps(fus,ensure_ascii=False,indent=2),encoding="utf-8")
        st={}
        for k in ("A","B"):
            for c in raw[k]: st[c.get("entailed_by","-")]=st.get(c.get("entailed_by","-"),0)+1
        print(f"  {run}: raw A={len(raw['A'])} B={len(raw['B'])} | sealed A={len(sealed['A'])} B={len(sealed['B'])} "
              f"| estados={st} | pares {blk['survived']}/{blk['possible']} | chamadas={_n['n']}")
    (OUT/"runs.json").write_text(json.dumps(runs,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUT/"pre-run-controls.json").write_text(json.dumps({"tokenizer":tk,"consolidator":cs,"judge":res},ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"  TOTAL de chamadas: {_n['n']} de {HARD_CAP}")
    return 0

if __name__=="__main__": sys.exit(main())
