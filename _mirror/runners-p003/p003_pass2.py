#!/usr/bin/env python3
"""PILOT-003 · (e) PASS 2 por segmento + portão. Compiler-v2 CONGELADO, sem alteração."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); CL = DRIVE / "Course-to-Skill-Claude"
sys.path.insert(0, str(CL/"compiler-v2")); sys.path.insert(0, str(Path(__file__).parent))
P3 = CL/"pilots/PILOT-003"; OUT = P3/"02_PASS2"
from cts import coverage as C                                   # noqa: E402
from ctsc2 import pipeline                                      # noqa: E402
from ctsc2.extractors.claude_extractor import ClaudeExtractor    # noqa: E402
from ctsc2.model import Segment                                  # noqa: E402
from ctsc2.thresholds import COVERAGE_FLOOR                      # noqa: E402
MARK = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")


def sec(t):
    q=[int(x) for x in str(t).split(":")]
    return q[0]*3600+q[1]*60+q[2] if len(q)==3 else q[0]*60+q[1]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = yaml.safe_load((P3/"00_SOURCE/SOURCE-MANIFEST.yaml").read_text(encoding="utf-8"))
    tm = yaml.safe_load((P3/"01_PASS1/temporal-map.yaml").read_text(encoding="utf-8"))
    L0 = P3/"00_SOURCE/L0-transcript.txt"
    text = L0.read_text(encoding="utf-8")
    blocks = text.split("\n\n")
    idx = [(i, sec(m.group(0).strip("*"))) for i,b in enumerate(blocks)
           if (m:=MARK.fullmatch(b.strip()))]

    def text_for(seg):
        out=[]
        for k,(i,s) in enumerate(idx):
            if seg.start_s <= s < seg.end_s:
                end = idx[k+1][0] if k+1 < len(idx) else len(blocks)
                out.extend(blocks[i:end])
        return "\n\n".join(out).strip()

    segs=[Segment(s["segment_id"], s["start_s"], s["end_s"], s["topic"], s["function"])
          for s in tm["temporal_map"]]
    print(f"L0 {meta['l0']['sha256'][:16]}… · {len(segs)} segmentos · "
          f"extensão {meta['l0']['duration_s']}s · held-out NÃO aplicado")
    ex = ClaudeExtractor(text_for)
    res = pipeline.compile_lesson(pilot_id="PILOT-003", lesson_id="PILOT-003-L01",
        l0_sha256=meta["l0"]["sha256"], extent_s=meta["l0"]["duration_s"],
        segments=segs, extractor=ex, out_dir=OUT,
        compiler_version="compiler-v2/0.2.0-frozen")
    m=res.manifest; g=m["coverage_gate"]; tot=ex.totals()
    (OUT/"EVIDENCE.jsonl").write_text("\n".join(json.dumps({
        "evidence_id":e.evidence_id,"segment_id":e.segment_id,
        "epistemic_status":e.epistemic_status,"category":e.category,"claim":e.claim,
        "source_excerpt":{"source_file":L0.name,"source_sha256":meta["l0"]["sha256"],
                          "span":{"start_s":e.start_s,"end_s":e.end_s},"quote":e.quote},
        "origin":e.origin,"iteration":e.iteration,"merged_from":e.merged_from},
        ensure_ascii=False) for e in res.evidences)+"\n", encoding="utf-8")
    print(f"\nevidências {m['evidence']['total']} · yield/segmento "
          f"{m['evidence']['aggregate_yield_per_segment']}")
    print(f"cobertura L0 {g['l0_coverage_pct']}% (piso {COVERAGE_FLOOR*100:.1f}%) · "
          f"{g['result']} · revarreduras {g['rescan_iterations']}")
    print(f"chamadas {tot['calls']} erros {tot['errors']} · "
          f"devolvidas {tot['drafts_returned']} aceitas {tot['drafts_accepted']} "
          f"rejeitadas {tot['drafts_rejected']}")
    print(f"zero-yield {m['pass2']['zero_yield_count']} · dedup "
          f"{m['deduplication']['merged_after_pass2']}")
    print(f"manifesto {res.manifest_sha256}")
    Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-pass2.json").write_text(
        json.dumps({"totals":tot,"calls":ex.trace()},ensure_ascii=False,indent=1),
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
