#!/usr/bin/env python3
"""Experimento de corte: teto por chamada, causal. 4 chamadas.

Mesma versão CONGELADA do compiler-v2. Não republica piloto, não escreve em
pilots/, não toca compiler-v2/. Saída em /tmp. §12 intacta.
"""
from __future__ import annotations
import json,re,sys,yaml
from pathlib import Path
DRIVE=Path("/mnt/g/Meu Drive/Chat GPT"); CL=DRIVE/"Course-to-Skill-Claude"
sys.path.insert(0,str(CL/"compiler-v2"))
from ctsc2.extractors.claude_extractor import ClaudeExtractor
from ctsc2.model import Segment, IdAllocator, Evidence
from ctsc2.dedup import dedup
L0=CL/"pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt"
TM=CL/"pilots/PILOT-002/02_MEASUREMENTS/PASS1-TENDENCY-RERUN/temporal-map(1).yaml"
OUT=Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/cut-experiment.json")
TARGET="SEG-013"
MARK=re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")
def hh(t):
    q=[int(x) for x in str(t).split(":")]
    return q[0]*3600+q[1]*60+q[2] if len(q)==3 else q[0]*60+q[1]
txt=L0.read_text(encoding="utf-8"); blocks=txt.split("\n\n")
idx=[(i,int(m.group(1))*60+int(m.group(2))) for i,b in enumerate(blocks) if (m:=MARK.fullmatch(b.strip()))]
segs={s["segment_id"]:(hh(s["start"]),hh(s["end"]),s.get("topic",""),s.get("function","")) for s in yaml.safe_load(TM.read_text(encoding="utf-8"))["temporal_map"]}
A,B,TOP,FN=segs[TARGET]
def text_for(seg):
    out=[]
    for j,(i,s) in enumerate(idx):
        if seg.start_s<=s<seg.end_s:
            end=idx[j+1][0] if j+1<len(idx) else len(blocks)
            out.extend(blocks[i:end])
    return "\n\n".join(out).strip()
marks_in=[s for _,s in idx if A<=s<B]
print(f"{TARGET}: {A}s-{B}s ({B-A}s) · {len(marks_in)} marcas · tópico: {TOP[:60]}")
# terços por MARCA, contíguos e sem sobreposição
n=len(marks_in); c1=marks_in[n//3]; c2=marks_in[2*n//3]
parts=[(A,c1),(c1,c2),(c2,B)]
print(f"terços: {parts}  durações {[b-a for a,b in parts]}")
ctx=lambda sid: {"segment_id":sid,"position":{"index":0,"of":1},"bounds_s":[0,0],
                 "previous_segment_id":None,"next_segment_id":None,
                 "scope_rule":"Extraia SOMENTE do intervalo deste segmento."}
ex=ClaudeExtractor(text_for)
whole_seg=Segment(TARGET,A,B,TOP,FN)
print("\n--- chamada 1/4: segmento INTEIRO ---")
w=ex.extract(whole_seg,ctx(TARGET),0)
print(f"  inteiro: {len(w)} evidências · {len(text_for(whole_seg))} chars")
pres=[]
for k,(a,b) in enumerate(parts,1):
    sid=f"{TARGET}-P{k}"
    sg=Segment(sid,a,b,TOP,FN)
    print(f"--- chamada {k+1}/4: parte {k} ({a}-{b}, {b-a}s, {len(text_for(sg))} chars) ---")
    d=ex.extract(sg,ctx(sid),0)
    print(f"  parte {k}: {len(d)} evidências")
    pres.append((sid,sg,d))
ids=IdAllocator(start=1)
allp=[Evidence(evidence_id=ids.issue(),segment_id=sid,claim=x.claim,start_s=x.start_s,
      end_s=x.end_s,category=x.category,epistemic_status=x.epistemic_status,quote=x.quote)
      for sid,sg,ds in pres for x in ds]
dd=dedup(allp)
soma=len(allp); apos=len(dd.kept); inteiro=len(w)
print("\n"+"="*66)
print(f"INTEIRO                    : {inteiro}")
print(f"PARTES somadas (bruto)     : {soma}   ganho {soma/inteiro:.3f}")
print(f"PARTES após dedup          : {apos}   ganho {apos/inteiro:.3f}   (fusões {dd.n_merged})")
print("="*66)
for lbl,g in (("bruto",soma/inteiro),("após dedup",apos/inteiro)):
    r=("CONFIRMA teto (>=1.15)" if g>=1.15 else "REFUTA teto (<=1.05)" if g<=1.05 else "INCONCLUSIVO (1.05-1.15)")
    print(f"  {lbl:<12} {g:.3f} → {r}")
OUT.write_text(json.dumps({"segment":TARGET,"bounds":[A,B],"parts":parts,
 "whole":[{"claim":x.claim,"start_s":x.start_s,"end_s":x.end_s,"quote":x.quote} for x in w],
 "parts_ev":[{"seg":sid,"claim":x.claim,"start_s":x.start_s,"end_s":x.end_s,"quote":x.quote} for sid,_,ds in pres for x in ds],
 "merges":dd.merged,"totals":{"whole":inteiro,"parts_raw":soma,"parts_dedup":apos},
 "calls":ex.trace()},ensure_ascii=False,indent=1),encoding="utf-8")
print(f"\nrastro: {OUT}")
