#!/usr/bin/env python3
"""PILOT-003 · PASS 2 com CHECKPOINT POR SEGMENTO e retomada. Tudo em ext4.

Dois consertos, depois de uma execução de ~5h ter sido perdida inteira:

1. CHECKPOINT: cada segmento é gravado em JSONL no instante em que fecha. Uma
   queda custa UMA chamada, não a rodada. A retomada lê o checkpoint e pula o
   que já existe.
2. FORA DO DRIVE: insumos copiados para ext4 e conferidos por hash no início;
   nada é lido nem escrito no Drive durante a execução. O Drive é tocado só na
   publicação, por outro script.

O compiler-v2 CONGELADO não é alterado: reuso o mesmo ClaudeExtractor e a mesma
regra de aceitação. O que muda é o laço em volta, que nunca foi congelado.
"""
from __future__ import annotations
import hashlib, json, os, re, sys, time
from pathlib import Path
import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); CL = DRIVE / "Course-to-Skill-Claude"
sys.path.insert(0, str(CL / "compiler-v2"))
W = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-work")
CKPT = W / "02_PASS2/pass2-checkpoint.jsonl"
EXPECT = {"L0": "04fda222febbaeece075f0096274ae8be00a7eedd5582006dd99d6ccc465e192",
          "tmap": "2c09e3ce74afce8c721e4a26205a31dbb2f4c7e0f5162cf8c190c7981dcf3d06"}
MARK = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")

from ctsc2.extractors.claude_extractor import ClaudeExtractor      # noqa: E402
from ctsc2.model import Segment, IdAllocator, Evidence             # noqa: E402
from ctsc2.dedup import dedup                                      # noqa: E402
from ctsc2.coverage_gate import measure                            # noqa: E402
from ctsc2.thresholds import COVERAGE_FLOOR                        # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sec(t):
    q = [int(x) for x in str(t).split(":")]
    return q[0]*3600+q[1]*60+q[2] if len(q) == 3 else q[0]*60+q[1]


def main() -> int:
    # ---- portão: insumos em ext4, conferidos
    l0p = W/"00_SOURCE/L0-transcript.txt"; tmp = W/"01_PASS1/temporal-map.yaml"
    for p, k in ((l0p, "L0"), (tmp, "tmap")):
        g = sha(p)
        if g != EXPECT[k]:
            print(f"ABORTA: {k} em ext4 não confere ({g})"); return 2
    print(f"insumos em ext4 conferidos · L0 {EXPECT['L0'][:16]}… · "
          f"tmap {EXPECT['tmap'][:16]}…")
    print(f"Drive NÃO é tocado nesta execução.")

    meta = yaml.safe_load((W/"00_SOURCE/SOURCE-MANIFEST.yaml").read_text(encoding="utf-8"))
    tm = yaml.safe_load(tmp.read_text(encoding="utf-8"))
    extent = meta["l0"]["duration_s"]
    text = l0p.read_text(encoding="utf-8"); blocks = text.split("\n\n")
    idx = [(i, sec(m.group(0).strip("*"))) for i, b in enumerate(blocks)
           if (m := MARK.fullmatch(b.strip()))]

    def text_for(seg):
        out = []
        for k, (i, s) in enumerate(idx):
            if seg.start_s <= s < seg.end_s:
                end = idx[k+1][0] if k+1 < len(idx) else len(blocks)
                out.extend(blocks[i:end])
        return "\n\n".join(out).strip()

    segs = [Segment(s["segment_id"], s["start_s"], s["end_s"], s["topic"], s["function"])
            for s in tm["temporal_map"]]

    # ---- retomada
    done = {}
    if CKPT.exists():
        for line in CKPT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line); done[r["segment_id"]] = r
        print(f"RETOMADA: {len(done)} segmentos já no checkpoint, "
              f"{len(segs)-len(done)} a fazer")
    else:
        CKPT.parent.mkdir(parents=True, exist_ok=True)
        print(f"execução nova: {len(segs)} segmentos")

    ex = ClaudeExtractor(text_for)
    ctx = lambda s, i: {"segment_id": s.segment_id, "position": {"index": i, "of": len(segs)},
                        "bounds_s": [s.start_s, s.end_s],
                        "previous_segment_id": segs[i-1].segment_id if i else None,
                        "next_segment_id": segs[i+1].segment_id if i+1 < len(segs) else None,
                        "scope_rule": "Extraia SOMENTE do intervalo deste segmento."}
    t0 = time.time(); errs = 0
    for i, s in enumerate(segs):
        if s.segment_id in done:
            continue
        st = time.time()
        try:
            drafts = ex.extract(s, ctx(s, i), 0)
        except Exception as e:
            errs += 1
            print(f"  [{i+1:>3}/{len(segs)}] {s.segment_id} ERRO: {type(e).__name__}: {e}")
            continue
        rec = {"segment_id": s.segment_id, "start_s": s.start_s, "end_s": s.end_s,
               "drafts": [{"claim": d.claim, "start_s": d.start_s, "end_s": d.end_s,
                           "category": d.category, "epistemic_status": d.epistemic_status,
                           "quote": d.quote} for d in drafts],
               "n": len(drafts), "latency_s": round(time.time()-st, 1),
               "call": ex.calls[-1].__dict__ if hasattr(ex, "calls") and ex.calls else None}
        with CKPT.open("a", encoding="utf-8") as f:      # grava JÁ, uma linha por segmento
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            f.flush(); os.fsync(f.fileno())
        done[s.segment_id] = rec
        el = time.time()-t0; fez = len([1 for x in segs if x.segment_id in done])
        print(f"  [{i+1:>3}/{len(segs)}] {s.segment_id} → {len(drafts):>2} ev "
              f"({round(time.time()-st)}s) · média {el/max(1,fez-len(done)+fez):.0f}s", flush=True)

    # ---- montagem a partir do checkpoint
    ids = IdAllocator(start=1); evs = []
    for s in segs:
        r = done.get(s.segment_id)
        if not r:
            continue
        for d in r["drafts"]:
            evs.append(Evidence(evidence_id=ids.issue(), segment_id=s.segment_id,
                                claim=d["claim"], start_s=d["start_s"], end_s=d["end_s"],
                                category=d["category"],
                                epistemic_status=d["epistemic_status"], quote=d["quote"]))
    dd = dedup(evs)
    cov = measure(dd.kept, extent, [])
    out = W/"02_PASS2"
    (out/"EVIDENCE.jsonl").write_text("\n".join(json.dumps({
        "evidence_id": e.evidence_id, "segment_id": e.segment_id,
        "epistemic_status": e.epistemic_status, "category": e.category, "claim": e.claim,
        "source_excerpt": {"source_file": "L0-transcript.txt",
                           "source_sha256": EXPECT["L0"],
                           "span": {"start_s": e.start_s, "end_s": e.end_s}, "quote": e.quote},
        "origin": "PASS2", "iteration": 0, "merged_from": e.merged_from},
        ensure_ascii=False) for e in dd.kept)+"\n", encoding="utf-8")
    zero = [s.segment_id for s in segs if not done.get(s.segment_id, {}).get("n")]
    man = {"pilot_id": "PILOT-003", "compiler_version": "compiler-v2/0.2.0-frozen",
           "runner": "p003_pass2_ckpt.py (checkpoint por segmento, ext4)",
           "input": {"l0_sha256": EXPECT["L0"], "temporal_map_sha256": EXPECT["tmap"],
                     "extent_s": extent, "held_out_applied": False},
           "pass2": {"execution_mode": "PER_SEGMENT", "invocations": len(done),
                     "segments": len(segs), "errors": errs,
                     "zero_yield_count": len(zero), "segments_with_zero_yield": zero},
           "evidence": {"total": len(dd.kept),
                        "aggregate_yield_per_segment": round(len(dd.kept)/len(segs), 4)},
           "deduplication": {"rule": "IDENTICAL_NORMALIZED_CLAIM", "merged": dd.n_merged},
           "coverage_gate": {"covered_s": cov.covered_s, "extent_s": extent,
                             "l0_coverage_pct": round(100*cov.coverage, 2),
                             "threshold": COVERAGE_FLOOR,
                             "result": "SATISFIED" if cov.coverage > COVERAGE_FLOOR else "NOT_SATISFIED"}}
    (out/"COMPILATION_MANIFEST.yaml").write_text(
        yaml.safe_dump(man, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    print(f"\nevidências {len(dd.kept)} · yield/seg {len(dd.kept)/len(segs):.2f} · "
          f"dedup {dd.n_merged}")
    print(f"cobertura {100*cov.coverage:.2f}% (piso {COVERAGE_FLOOR*100:.1f}%) · "
          f"{man['coverage_gate']['result']}")
    print(f"chamadas {len(done)} · erros {errs} · zero-yield {len(zero)} · "
          f"{round(time.time()-t0)}s")
    print(f"manifesto PASS2 pronto em ext4: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
