#!/usr/bin/env python3
"""BATCH-C1..C5 — canarios da particao v2 e da completude. Zero modelo."""
import sys, json, pathlib, hashlib, copy
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib"))
import relation_validate as RV
PS = json.loads((H/"ms001b/PAIRSET-MS001B-V1.json").read_text(encoding="utf-8"))
PI = json.loads((H/"ms001b/PAIR-INPUTS-MS001B.json").read_text(encoding="utf-8"))
P2 = json.loads((H/"ms001b/PARTITION-MS001B-v2.json").read_text(encoding="utf-8"))
IDS = [p["pair_id"] for p in PS["pairs"]]; old4 = IDS[75:]
B = {"BATCH-1":IDS[0:25],"BATCH-2":IDS[25:50],"BATCH-3":IDS[50:75],
     "BATCH-4A":old4[:11],"BATCH-4B":old4[11:]}
canon = lambda o: json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(",",":"))
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
R=[]
def chk(c,d,exp,got,ok): R.append({"canary":c,"desc":d,"expected":exp,"got":got,"ok":bool(ok)})

# BATCH-C1: split 11+11 do antigo BATCH-4
u = B["BATCH-4A"]+B["BATCH-4B"]; i = set(B["BATCH-4A"]) & set(B["BATCH-4B"])
chk("BATCH-C1","split 11+11 do antigo BATCH-4","uniao == 22 originais, intersecao vazia",
    f"uniao={len(u)} igual={sorted(u)==sorted(old4)} intersecao={len(i)}",
    sorted(u)==sorted(old4) and not i and len(B["BATCH-4A"])==11 and len(B["BATCH-4B"])==11)
# BATCH-C2: os cinco batches cobrem 97 sem duplicata
allp=[x for k in B for x in B[k]]
chk("BATCH-C2","cinco batches cobrem 97","97 distintos, zero duplicata, zero faltante",
    f"total={len(allp)} distintos={len(set(allp))} == pairset={sorted(set(allp))==sorted(IDS)}",
    len(allp)==97 and len(set(allp))==97 and sorted(set(allp))==sorted(IDS))
# BATCH-C3: drift detectado
ph=sha(canon([{"pair_id":x["pair_id"],"left":x["left"],"right":x["right"]} for x in PS["pairs"]]))
d1=sha(canon([{"pair_id":x["pair_id"],"left":x["left"],"right":x["right"]} for x in PS["pairs"][:-1]]))
mut=copy.deepcopy(PS["pairs"]); mut[0]["right"]["local_id"]="CL-9999"
d2=sha(canon([{"pair_id":x["pair_id"],"left":x["left"],"right":x["right"]} for x in mut]))
chk("BATCH-C3","PAIRSET_DRIFT por remocao e por troca","hash muda nos dois casos",
    f"remocao={d1!=ph} troca={d2!=ph} original_confere={ph==PS['PAIRSET_HASH']}",
    d1!=ph and d2!=ph and ph==PS["PAIRSET_HASH"])
# BATCH-C4 / C5: validador sobre 4A
ids=B["BATCH-4A"]
SENT={i:{"left":{e["evidence_id"] for e in PI[i]["left"]["evidence"]},
         "right":{e["evidence_id"] for e in PI[i]["right"]["evidence"]}} for i in ids}
mk=lambda pid: {"pair_id":pid,"relation":"UNRELATED","direction":"NONE","scope_state":"DIFFERENT_SCOPE",
                "relation_why":"razao suficientemente longa para o schema",
                "left_evidence_refs_checked":sorted(SENT[pid]["left"]),
                "right_evidence_refs_checked":sorted(SENT[pid]["right"])}
doc=lambda js: json.dumps({"batch_id":"BATCH-4A","judgments":js})
full=[mk(i) for i in ids]
_,e0=RV.validate(doc(full),"BATCH-4A",SENT)
chk("BATCH-C0","11/11 completo","sem erro",e0,not e0)
_,e4=RV.validate(doc(full[:10]),"BATCH-4A",SENT)
chk("BATCH-C4","output 10 de 11","R15_PAIR_MISSING",e4,"R15_PAIR_MISSING" in e4)
_,e5=RV.validate(doc(full+[mk(ids[0])]),"BATCH-4A",SENT)
chk("BATCH-C5","output 12 de 11 com duplicata","R06_DUPLICATE_PAIR",e5,"R06_DUPLICATE_PAIR" in e5)
# o par que foi omitido na exec-1 esta em qual batch novo?
miss="f5fa1fbc0bbb6b892845b967"
tgt=[k for k,v in B.items() if any(x.startswith(miss[:16]) for x in v)]
pos=[v.index([x for x in v if x.startswith(miss[:16])][0])+1 for k,v in B.items() if k in tgt]
chk("BATCH-C6","o par omitido na exec-1 agora esta em batch menor",f"em {tgt} posicao {pos} de 11",
    f"{tgt} pos={pos}", bool(tgt) and pos and pos[0]<=11)

if __name__=="__main__":
    for x in R: print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['canary']:<10} {x['desc']:<44} {x['got']}")
    n=sum(1 for x in R if x["ok"]); print(f"\n  {n}/{len(R)} canarios de batch PASS")
    (H/"out-ms001b-exec2").mkdir(exist_ok=True)
    (H/"out-ms001b-exec2/batch-canaries.json").write_text(json.dumps(R,ensure_ascii=False,indent=1),encoding="utf-8")
    sys.exit(0 if n==len(R) else 2)
