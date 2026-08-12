#!/usr/bin/env python3
"""Rodada COMPLETA do PILOT-002 com o compiler-v2. Mesma versão congelada.

READ-ONLY sobre `Course-to-Skill/`. Escreve só em
`Course-to-Skill-Claude/pilots/PILOT-002-v2/`.

REGRA DURA DE ENTRADA: só o L0 CORTADO. O íntegro é PROIBIDO e o script nem
conhece o caminho dele.
"""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
V2 = CLAUDE / "compiler-v2"
sys.path.insert(0, str(V2)); sys.path.insert(0, str(Path(__file__).parent))

P2 = CLAUDE / "pilots/PILOT-002"
L0_CUT = P2 / "00_SOURCE/L0-transcript-CUT.txt"
TMAP = P2 / "02_MEASUREMENTS/PASS1-TENDENCY-RERUN/temporal-map(1).yaml"
OUTDIR = CLAUDE / "pilots/PILOT-002-v2"
TRACE = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/pilot002-v2-trace.json")

EXPECTED_L0 = "85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29"
EXPECTED_TMAP = "87372638248d92b886768f265b253330f4939accc0a6a0bb74cb08fdf329fa38"
EXPECTED_BYTES, EXPECTED_MARKS, EXPECTED_SEGS = 96246, 733, 41
HOLDOUT_LOCK = [(715, 908), (2680, 3000)]
EXTENT = 4384

from cts import coverage as C
from ctsc2 import pipeline
from ctsc2.extractors.claude_extractor import ClaudeExtractor
from ctsc2.model import Segment
from ctsc2.thresholds import COVERAGE_FLOOR

MARK = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")
def sha_p(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def hh(t):
    q=[int(x) for x in str(t).split(":")]
    return q[0]*3600+q[1]*60+q[2] if len(q)==3 else q[0]*60+q[1]
def fmt(s): return f"{s//60}:{s%60:02d}"

def slicer(text):
    blocks=text.split("\n\n")
    idx=[(i,int(m.group(1))*60+int(m.group(2))) for i,b in enumerate(blocks) if (m:=MARK.fullmatch(b.strip()))]
    def text_for(seg):
        out=[]
        for k,(i,s) in enumerate(idx):
            if seg.start_s<=s<seg.end_s:
                end=idx[k+1][0] if k+1<len(idx) else len(blocks)
                out.extend(blocks[i:end])
        return "\n\n".join(out).strip()
    return text_for

def main():
    # ---------------- PORTÃO DE ENTRADA, antes de qualquer coisa
    print("="*78); print("PILOT-002 — RODADA COMPLETA COM COMPILER-V2"); print("="*78)
    s0=sha_p(L0_CUT); nb=L0_CUT.stat().st_size
    txt=L0_CUT.read_text(encoding="utf-8"); nm=len(MARK.findall(txt))
    st=sha_p(TMAP)
    ok=True
    for lbl,got,exp in (("L0 sha256",s0,EXPECTED_L0),("L0 bytes",nb,EXPECTED_BYTES),
                        ("L0 marcas",nm,EXPECTED_MARKS),("tmap sha256",st,EXPECTED_TMAP)):
        good=(got==exp); ok&=good
        g=str(got)[:16]+"…" if isinstance(got,str) else got
        e=str(exp)[:16]+"…" if isinstance(exp,str) else exp
        print(f"  {lbl:<14} {g!s:<20} esperado {e!s:<20} {'OK' if good else 'DIVERGE'}")
    d=yaml.safe_load(TMAP.read_text(encoding="utf-8"))
    segs=[Segment(s["segment_id"],hh(s["start"]),hh(s["end"]),s.get("topic",""),s.get("function",""))
          for s in d["temporal_map"]]
    print(f"  {'segmentos':<14} {len(segs):<20} esperado {EXPECTED_SEGS:<20} "
          f"{'OK' if len(segs)==EXPECTED_SEGS else 'DIVERGE'}")
    ok&=len(segs)==EXPECTED_SEGS
    if not ok:
        print("\nPORTÃO DE ENTRADA REPROVADO — nada foi executado."); return 2
    print(f"  L0 íntegro: NÃO REFERENCIADO por este script (proibido)\n")

    ex=ClaudeExtractor(slicer(txt))
    res=pipeline.compile_lesson(pilot_id="PILOT-002",lesson_id="PILOT-002-L01",
        l0_sha256=s0,extent_s=EXTENT,segments=segs,extractor=ex,out_dir=OUTDIR,
        compiler_version="compiler-v2/0.2.0-frozen",holdout=HOLDOUT_LOCK)
    m=res.manifest; tot=ex.totals(); n=len(segs)

    (OUTDIR/"EVIDENCE.jsonl").write_text("\n".join(json.dumps({
        "evidence_id":e.evidence_id,"segment_id":e.segment_id,
        "epistemic_status":e.epistemic_status,"category":e.category,"claim":e.claim,
        "source_excerpt":{"source_file":L0_CUT.name,"source_sha256":s0,
            "span":{"start_s":e.start_s,"end_s":e.end_s},"quote":e.quote},
        "origin":e.origin,"iteration":e.iteration,"merged_from":e.merged_from},
        ensure_ascii=False) for e in res.evidences)+"\n",encoding="utf-8")
    TRACE.write_text(json.dumps({"totals":tot,"calls":ex.trace()},ensure_ascii=False,indent=1),encoding="utf-8")

    g=m["coverage_gate"]; p2=m["pass2"]
    ud=sum(b.dur for b in C.merge([C.Citation(e.start_s,e.end_s,"d",e.evidence_id) for e in res.evidences]))
    print("--- 1. evidências e yield ---")
    print(f"total              : {m['evidence']['total']}   (44 na rodada antiga)")
    print(f"yield por segmento : {m['evidence']['aggregate_yield_per_segment']}   (1.07 antiga)")
    print("\n--- 3. cobertura ---")
    print(f"cobertura L0       : {g['l0_coverage_pct']}%   piso {COVERAGE_FLOOR*100:.1f}%")
    print(f"coberto/extensão   : {g['covered_s']}s / {g['extent_s']}s")
    print(f"união DECLARADA    : {ud}s · por segmento {ud/n:.1f}s")
    print("\n--- 5. portão ---")
    print(f"resultado          : {g['result']} ({g['stop_reason']}) · iterações {g['rescan_iterations']}")
    for it in g["iterations"]:
        print(f"  #{it['iteration']}: {it['coverage_before']:.4f} → {it['coverage_after']:.4f} "
              f"· +{it['evidence_added']} · {len(it['targeted_segments'])} alvos")
    print("\n--- 6. rótulos e rejeições ---")
    rej={}
    for c in ex.calls:
        for r in c.rejected: rej[r["reason"]]=rej.get(r["reason"],0)+1
    print(f"devolvidas={tot['drafts_returned']} aceitas={tot['drafts_accepted']} rejeitadas={tot['drafts_rejected']}")
    for k,v in sorted(rej.items()): print(f"  {k}: {v}")
    if not rej: print("  nenhuma")
    mi=sum(1 for e in res.evidences if e.epistemic_status=="MODEL_INFERENCE")
    print(f"MODEL_INFERENCE    : {mi} de {m['evidence']['total']}")
    print(f"yield zero         : {p2['zero_yield_count']} {p2['segments_with_zero_yield'][:8]}")
    print(f"dedup              : {m['deduplication']['merged_after_pass2']}+"
          f"{m['deduplication']['merged_inside_gate']}+{m['deduplication']['merged_after_rescan']}")
    print("\n--- 7. custo ---")
    print(f"chamadas={tot['calls']} erros={tot['errors']} entrada={tot['input_tokens']} "
          f"saída={tot['output_tokens']}")
    print(f"cache r/w={tot['cache_read_input_tokens']}/{tot['cache_creation_input_tokens']} "
          f"latência={tot['latency_s']}s")
    print(f"\nmanifesto sha256 {res.manifest_sha256[:16]}…")
    return 0

if __name__=="__main__": raise SystemExit(main())
