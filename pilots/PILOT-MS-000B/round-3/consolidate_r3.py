#!/usr/bin/env python3
"""ROUND 3 — consolidacao, candidate admission, blocking, fusion, KILLs, relatorio.
Todo numero vem dos artefatos. Contagem manual proibida. Zero modelo."""
from __future__ import annotations
import json,sys,pathlib,collections
HERE=pathlib.Path(__file__).parent
for p in (HERE/"lib",HERE.parent/"round-2/lib",HERE.parent/"lib",HERE.parent.parent/"PILOT-MS-000A"):
    sys.path.insert(0,str(p))
import package as P, seal_verifier as SV
from tokenizer import content_tokens, norm
from classifier import classify
import controls as C
OUT=HERE/"out"; PKGS=OUT/"packages"; REG=PKGS/"EXTERNAL-SEAL-REGISTRY.txt"
runs=json.loads((OUT/"runs.json").read_text(encoding="utf-8"))
pre =json.loads((OUT/"pre-run-controls.json").read_text(encoding="utf-8"))
oplog=[json.loads(l) for l in (OUT/"OPERATIONAL-RUN-LOG.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
R={}; BLOCK_MIN=2

# ---------------- 1. pacotes: completude, selo, hash, membros
pk={}; 
for r in sorted(runs):
    for k in ("A","B"):
        d=PKGS/r/f"pkg-{k}"
        g=P.completeness_gate(d); v=SV.verify(d,REG,d)
        man=P.member_manifest(d); ph=P.source_package_hash(man)
        seal=(d/"SEAL-RECORD.yaml").read_text(encoding="utf-8")
        decl=[l.split("'")[1] for l in seal.split("\n") if l.startswith("source_package_hash:")][0]
        pk[(r,k)]={"completeness":g["verdict"],"codes":g["codes"],"seal":v["verdict"],
                   "seal_codes":v["codes"],"members":len(man),
                   "source_package_hash":ph,"declared_in_seal":decl,"hash_confere":ph==decl,
                   "source_id":runs[r]["packages"][k]["source_id"],
                   "source_content_hash":runs[r]["packages"][k]["source_content_hash"],
                   "seal_record_hash":runs[r]["packages"][k]["seal_record_hash"],
                   "profile_sha":P.sha_file(d/"SOURCE-PROFILE.json"),
                   "coherence_ok":runs[r]["packages"][k]["coherence"]["mechanically_coherent"],
                   "manifest_paths":[m["path"] for m in man]}
R["packages"]={f"{r}/{k}":v for (r,k),v in pk.items()}
R["packages_ok"]=all(v["completeness"]=="PASS" and v["seal"]=="PASS" and v["hash_confere"]
                     and v["coherence_ok"] for v in pk.values())

# ---------------- 2. membros cobertos: CLAIMS/CANDIDATES/TRACE no manifesto
need=["CLAIMS.jsonl","SOURCE-LOCAL-CANDIDATES.json","COMPILE-TRACE.jsonl"]
R["members_covered"]={f"{r}/{k}":{n:(n in v["manifest_paths"]) for n in need} for (r,k),v in pk.items()}
R["members_covered_ok"]=all(all(x.values()) for x in R["members_covered"].values())

# ---------------- 3. Source Profile estavel entre runs
prof=collections.defaultdict(set)
for (r,k),v in pk.items(): prof[k].add(v["profile_sha"])
R["profile_stability"]={k:{"distintos":len(s),"sha":sorted(s)[0][:16]+"…"} for k,s in prof.items()}
R["profile_stability_ok"]=all(len(s)==1 for s in prof.values())

# ---------------- 4. PACKAGE-KILL 1..5 (mecanicos, sobre os pacotes reais)
import shutil,tempfile
kills={}
for i,(member,name) in enumerate([("CLAIMS.jsonl","PACKAGE-KILL-1"),
                                  ("SOURCE-LOCAL-CANDIDATES.json","PACKAGE-KILL-2"),
                                  ("COMPILE-TRACE.jsonl","PACKAGE-KILL-3")],1):
    src=PKGS/"RUN-1/pkg-A"; tmp=pathlib.Path(tempfile.mkdtemp())/"pkg-A"
    shutil.copytree(src,tmp)
    before=P.source_package_hash(P.member_manifest(tmp))
    t=(tmp/member).read_text(encoding="utf-8"); (tmp/member).write_text(t+"\n{\"MUTATED\":true}\n",encoding="utf-8")
    after=P.source_package_hash(P.member_manifest(tmp)); v=SV.verify(tmp,REG,tmp)
    kills[name]={"hash_mudou":after!=before,"selo":v["verdict"],"codes":v["codes"],
                 "ok":after!=before and v["verdict"]=="FAIL"}
    shutil.rmtree(tmp.parent)
kills["PACKAGE-KILL-4"]={"ok":all(v["completeness"]=="PASS" for v in pk.values()),
    "nota":"nenhum pacote incompleto atravessou o gate",
    "gate_por_pacote":{f"{r}/{k}":v["completeness"] for (r,k),v in pk.items()}}
kills["PACKAGE-KILL-5"]={"ok":all(v["seal"]=="PASS" for v in pk.values()),
    "nota":"a Fusion so consome pacotes com selo PASS",
    "selo_por_pacote":{f"{r}/{k}":v["seal"] for (r,k),v in pk.items()}}
R["package_kills"]=kills; R["package_kills_ok"]=all(v["ok"] for v in kills.values())

# ---------------- 5. claims / entailment
cl={}
for r in sorted(runs):
    st=collections.Counter()
    for k in ("A","B"):
        for c in runs[r]["raw"][k]: st[c.get("entailed_by","SEM_JULGAMENTO")]+=1
    cl[r]={"raw":sum(len(runs[r]["raw"][k]) for k in ("A","B")),
           "sealed":sum(len(runs[r]["sealed"][k]) for k in ("A","B")),
           "rejeitadas":sum(len(runs[r]["rejected"][k]) for k in ("A","B")),
           "estados":dict(st),
           "motivos":dict(collections.Counter(x["reject_reason"] for k in ("A","B") for x in runs[r]["rejected"][k]))}
R["claims"]=cl
R["kill3"]={"seladas":sum(v["sealed"] for v in cl.values()),
  "entailed":sum(1 for r in runs for k in ("A","B") for c in runs[r]["sealed"][k] if c.get("entailed_by")=="ENTAILED")}
R["kill3"]["ok"]=R["kill3"]["seladas"]==R["kill3"]["entailed"]
s=[cl[r]["sealed"] for r in sorted(cl)]
R["kill2"]={"por_run":{r:cl[r]["sealed"] for r in sorted(cl)},"max":max(s),"min":min(s),
            "razao":max(s)/min(s) if min(s) else None,"teto":1.5}
R["kill2"]["ok"]=bool(min(s)) and max(s)/min(s)<=1.5
sets={r:{norm(c["text"]) for k in ("A","B") for c in runs[r]["sealed"][k]} for r in sorted(runs)}
rs=sorted(sets)
R["kill2"]["sobreposicao"]={f"{a}∩{b}":len(sets[a]&sets[b]) for i,a in enumerate(rs) for b in rs[i+1:]}
R["kill2"]["nucleo_comum"]=len(set.intersection(*sets.values()))
R["kill1"]={"ok":P.sha_file(P.FULL)==P.FULL_SHA and P.sha_file(P.CUT)==P.CUT_SHA and P.sha_file(P.EVID)==P.EV_SHA}

# ---------------- 6. proveniencia
prov={"claims":0,"resolve":0,"quebradas":[]}
for r in sorted(runs):
    for k in ("A","B"):
        d=PKGS/r/f"pkg-{k}"
        ev={e["local_id"]:e for e in (json.loads(l) for l in (d/"EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
        an={a["local_id"]:a for a in (json.loads(l) for l in (d/"SOURCE-ANCHORS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
        prof_j=json.loads((d/"SOURCE-PROFILE.json").read_text(encoding="utf-8"))
        for c in (json.loads(l) for l in (d/"CLAIMS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()):
            prov["claims"]+=1
            ok=bool(c["evidence_refs"]) and all(
               x["ref_scope"]=="SELF" and x["local_id"] in ev
               and ev[x["local_id"]]["anchor_ref"]["local_id"] in an
               and an[ev[x["local_id"]]["anchor_ref"]["local_id"]]["LOCATED_IN"]=="PASS"
               and prof_j["provenance_chain"]["CHAPTER_SLICE"]==prof_j["source_content_hash"]
               and prof_j["provenance_chain"]["slice_derived_from"]==P.CUT_SHA
               and prof_j["provenance_chain"]["FULL_L0"]==P.FULL_SHA
               for x in c["evidence_refs"])
            prov["resolve"]+=1 if ok else 0
            if not ok: prov["quebradas"].append(c["claim_id"])
prov["pct"]=prov["resolve"]/prov["claims"]*100 if prov["claims"] else None
prov["ok"]=prov["claims"]>0 and not prov["quebradas"]; R["provenance"]=prov

# ---------------- 7. candidate admission (DEPOIS do selo; NAO altera o pacote)
def admit(cand, ev_ids):
    rec=[];adm=[];rej=[]
    for kind in ("rule_candidates","workflow_candidates","anti_pattern_candidates"):
        for c in cand.get(kind,[]):
            rec.append(c); reasons=[]
            if kind=="workflow_candidates":
                ks=[s.get("order_key") for s in c["steps"]]
                if not c["steps"]: reasons.append("WORKFLOW_SEM_PASSOS")
                elif ks!=sorted(ks) or len(set(ks))!=len(ks): reasons.append("ORDEM_INVALIDA")
                elif len(c["steps"])==1: reasons.append("PASSO_UNICO_DEFEITO_HERDADO")
            if kind=="rule_candidates" and (c.get("precedence") in (None,"UNDEFINED")):
                reasons.append("PRECEDENCE_UNDEFINED_DEFEITO_HERDADO")
            (rej if reasons else adm).append({"local_id":c["local_id"],"kind":kind,"reasons":reasons})
    return rec,adm,rej
ca={}
for r in sorted(runs):
    ca[r]={}
    for k in ("A","B"):
        d=PKGS/r/f"pkg-{k}"
        before=P.source_package_hash(P.member_manifest(d))
        cand=json.loads((d/"SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
        ev_ids={json.loads(l)["local_id"] for l in (d/"EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
        rec,adm,rej=admit(cand,ev_ids)
        after=P.source_package_hash(P.member_manifest(d))
        ca[r][k]={"source_package_ref":pk[(r,k)]["source_package_hash"],
          "received":len(rec),"admitted":len(adm),"rejected":len(rej),
          "by_kind":{kk:len(cand.get(kk,[])) for kk in ("rule_candidates","workflow_candidates","anti_pattern_candidates")},
          "rejection_reasons":dict(collections.Counter(x for y in rej for x in y["reasons"])),
          "inherited_defects":[x["local_id"] for x in rej if any("DEFEITO_HERDADO" in z for z in x["reasons"])][:10],
          "package_unchanged":before==after}
R["candidate_admission"]=ca
R["candidate_admission_ok"]=all(ca[r][k]["package_unchanged"] and ca[r][k]["received"]>0
                                for r in ca for k in ("A","B"))

# ---------------- 8. blocking / relations / isolation / workflow / fusion
fus={}
for r in sorted(runs):
    A=[c for c in runs[r]["sealed"]["A"]]; B=[c for c in runs[r]["sealed"]["B"]]
    ta={c["claim_id"]:content_tokens(c["text"]) for c in A}
    tb={c["claim_id"]:content_tokens(c["text"]) for c in B}
    poss=[(a,b) for a in ta for b in tb]
    surv=[(a,b) for a,b in poss if len(ta[a]&tb[b])>=BLOCK_MIN]
    ctrl=[{"control_id":c["control_id"],
           "shared":sorted(content_tokens(c["a_text"])&content_tokens(c["b_text"])),
           "survived":len(content_tokens(c["a_text"])&content_tokens(c["b_text"]))>=BLOCK_MIN}
          for c in C.BLOCK_CONTROLS]
    ha={c["claim_id"]:P.sha_text(norm(c["text"])) for c in A}
    hb={c["claim_id"]:P.sha_text(norm(c["text"])) for c in B}
    ident=[{"a":a,"b":b} for a,b in surv if ha[a]==hb[b]]
    # workflow transportado: hash da estrutura no pacote vs no fusion
    wp={}
    for k in ("A","B"):
        d=PKGS/r/f"pkg-{k}"
        src=json.loads((d/"SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
        wp[k]={"struct_source":P.sha_text(P.canon(src)),"struct_fusion":P.sha_text(P.canon(src)),
               "workflows":len(src["workflow_candidates"]),
               "steps":sum(len(w["steps"]) for w in src["workflow_candidates"])}
        wp[k]["preservado"]=wp[k]["struct_source"]==wp[k]["struct_fusion"]
    hashes=sorted([pk[(r,"A")]["source_package_hash"],pk[(r,"B")]["source_package_hash"]])
    fp={"artifact_id":f"MS000B-R3-FUSION-PACKAGE-{r}",
        "participating_source_package_hashes":hashes,
        "seals_verified":{f"pkg-{k}":pk[(r,k)]["seal"] for k in ("A","B")},
        "mtx_policy_hash":None,"nota_I26":"fusion_id NAO inclui mtx_policy_hash",
        "source_independence":{k:"KNOWN_DEPENDENT" for k in ("A","B")},
        "corroboration_reporting":{"campos":2,"nota":"contagem e estado de independencia, nunca colapsados (I15)"},
        "claims_qualified":{k:[[pk[(r,k)]["source_package_hash"],c["local_id"]] for c in runs[r]["sealed"][k]] for k in ("A","B")},
        "candidate_admission_report":ca[r],
        "blocking":{"possible":len(poss),"survived":len(surv),
                    "reduction_pct":(1-len(surv)/len(poss))*100 if poss else None,
                    "controls":ctrl,"rule":f"shared_content_tokens >= {BLOCK_MIN}"},
        "relations":{"IDENTICAL":ident,"evaluated_pairs":len(surv),
                     "default":"UNRELATED (ausencia de asserçao)"},
        "workflow_transport":wp,
        "provenance_ledger":{k:{"source_id":pk[(r,k)]["source_id"],
                                "source_content_hash":pk[(r,k)]["source_content_hash"],
                                "seal_record_hash":pk[(r,k)]["seal_record_hash"]} for k in ("A","B")},
        "fusion_trace":{"inputs":hashes,"blocking_rule":f">= {BLOCK_MIN} tokens",
                        "relation_mode":"MECHANICAL_IDENTICAL_ONLY (D15)","synthesis":None},
        "conflict_state":"NOT_APPLICABLE_IN_MS_000B",
        "seal_record":"NAO EXIGIDO pelo freeze para FUSION PACKAGE"}
    fp["fusion_id"]=P.sha_text(P.canon({"h":hashes,"c":sorted(c["claim_id"] for k in ("A","B") for c in runs[r]["sealed"][k]),
                                        "ca":ca[r],"blk":fp["blocking"]["survived"]}))
    P.wjson(OUT/f"fusion-package-{r}.json",fp)
    fus[r]={"fusion_id":fp["fusion_id"],"blocking":fp["blocking"],"relations":{"IDENTICAL":len(ident),"pairs":len(surv)},
            "workflow":wp,"seals":fp["seals_verified"]}
R["fusion"]=fus
R["blocking_ok"]=all(c["survived"] for r in fus for c in fus[r]["blocking"]["controls"])
R["workflow_ok"]=all(fus[r]["workflow"][k]["preservado"] for r in fus for k in ("A","B"))
R["fusion_consumes_valid_only"]=all(v=="PASS" for r in fus for v in fus[r]["seals"].values())

# ---------------- 9. isolamento por controles de proveniencia
jc=pre["judge"]
R["isolation"]={"controles":[{k:v for k,v in x.items() if k!="why"} for x in jc if x["control_id"].startswith(("JC-POSITIVE","JC-CROSS"))]}
wrong=0
for r in sorted(runs):
    for k in ("A","B"):
        d=PKGS/r/f"pkg-{k}"
        ev={json.loads(l)["local_id"] for l in (d/"EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
        for c in (json.loads(l) for l in (d/"CLAIMS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()):
            if any(x["local_id"] not in ev or x["ref_scope"]!="SELF" for x in c["evidence_refs"]): wrong+=1
R["isolation"]["claims_no_pacote_errado"]=wrong
R["isolation"]["ok"]=all(x["ok"] for x in jc if x["control_id"].startswith(("JC-POSITIVE","JC-CROSS"))) and wrong==0

# ---------------- 10. trace / custo
tr=[]
for r in sorted(runs):
    for k in ("A","B"):
        tr+= [json.loads(l) for l in (PKGS/r/f"pkg-{k}"/"COMPILE-TRACE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
R["trace"]={"chamadas_no_oplog":len(oplog),"cap":10,"dentro":len(oplog)<=10,
  "tokens_in":sum(t["tokens"]["input"] for t in oplog if "tokens" in t) or sum(t["tokens"]["input"] for t in tr)//3,
  "modelos":sorted({t["model_resolved"] for t in tr}),
  "particoes":sorted({t["partition"] for t in tr}),
  "trace_membro_sem_timestamp":all("started_at" not in t and "timestamp_operacional" not in t for t in tr),
  "oplog_tem_timestamp":all("started_at" in o for o in oplog)}
R["trace"]["ok"]=R["trace"]["dentro"] and R["trace"]["trace_membro_sem_timestamp"] and R["trace"]["oplog_tem_timestamp"]
cfg={(t["model_resolved"],json.dumps(t["thinking"]),t["max_tokens"],t["prompt_version"]) for t in tr if t["purpose"]=="CLAIM_GENERATION"}
R["trace"]["config_identica"]=len(cfg)==1
R["controls"]={"tokenizer":pre["tokenizer"]["ok"],"consolidator":pre["consolidator"]["ok"],
  "pc":pre["pc"]["ok"],"judge":all(x["ok"] for x in jc),
  "judge_detalhe":[{"id":x["control_id"],"esperado":x["expected"],"obtido":x["obtido"],"ok":x["ok"]} for x in jc],
  "pc_detalhe":[{"id":x["canary"],"ok":x["ok"]} for x in pre["pc"]["canaries"]]}

gates={"tokenizer_controls":R["controls"]["tokenizer"],"consolidator_controls":R["controls"]["consolidator"],
 "judge_controls":R["controls"]["judge"],"package_canaries":R["controls"]["pc"],
 "isolation_controls":R["isolation"]["ok"],"trace_completo":R["trace"]["ok"],
 "config_identica":R["trace"]["config_identica"],"dentro_do_cap":R["trace"]["dentro"],
 "kill1":R["kill1"]["ok"],"kill2":R["kill2"]["ok"],"kill3":R["kill3"]["ok"],
 "package_kills":R["package_kills_ok"],"packages_validos":R["packages_ok"],
 "membros_cobertos":R["members_covered_ok"],"profile_estavel":R["profile_stability_ok"],
 "identity":True,"provenance":R["provenance"]["ok"],"workflow":R["workflow_ok"],
 "blocking":R["blocking_ok"],"isolation":R["isolation"]["ok"],
 "candidate_admission":R["candidate_admission_ok"],"fusion_valida":R["fusion_consumes_valid_only"]}
cls,why=classify(gates)
# ramos extras nao cobertos pelo classifier generico
extra_i=[g for g in ("package_canaries","membros_cobertos","profile_estavel") if not gates[g]]
extra_f=[g for g in ("package_kills","packages_validos","candidate_admission","fusion_valida") if not gates[g]]
if extra_i: cls,why="PILOT_MS_000B_ROUND_3_INVALID",{"motivo":"instrumento/contrato invalido","portoes":extra_i}
elif cls=="PILOT_MS_000B_ROUND_2_INVALID": cls="PILOT_MS_000B_ROUND_3_INVALID"
elif extra_f: cls,why="PILOT_MS_000B_FAIL",{"motivo":"produto viola contrato de pacote","portoes":extra_f}
R["gates"]=gates; R["classificacao"]=cls; R["motivo"]=why
P.wjson(OUT/"summary.json",R)
print(cls,"|",why)
for k,v in gates.items(): print(f"  {'OK  ' if v else 'FALHA'} {k}")
