#!/usr/bin/env python3
"""Rodada COMPLETA do PILOT-001 com o compiler-v2.

Roda daqui (ext4). READ-ONLY sobre `Course-to-Skill/`: lê L0 e o temporal-map.
Escreve só em `Course-to-Skill-Claude/pilots/PILOT-001-v2/`.

PASS 1 → temporal-map persistido e hasheado → PASS 2 por segmento → dedup →
portão de cobertura → revarredura dirigida se preciso → COMPILATION_MANIFEST.

RESSALVA SOBRE O PASS 1, que o relatório repete: o PASS 1 NÃO é re-executado
por modelo. Os segmentos vêm do `temporal-map.yaml` histórico. Logo a contagem
de 9 é herdada, não medida, e esta rodada NÃO responde à pergunta de
estabilidade do PASS 1 da §12 da ADR.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
V2 = CLAUDE / "compiler-v2"
sys.path.insert(0, str(V2))
sys.path.insert(0, str(Path(__file__).parent))

P1 = DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
TMAP = P1 / "analysis/temporal-map.yaml"
L0 = P1 / "sources/transcript/transcript-original-en.txt"
META = P1 / "sources/metadata/source-metadata.yaml"
OUTDIR = CLAUDE / "pilots/PILOT-001-v2"
TRACE = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/pilot001-v2-trace.json")

from cts import coverage as C                                    # noqa: E402
from ctsc2 import pipeline                                       # noqa: E402
from ctsc2.extractors.claude_extractor import ClaudeExtractor     # noqa: E402
from ctsc2.model import Segment                                   # noqa: E402
from ctsc2.thresholds import (COVERAGE_FLOOR, HISTORICAL,          # noqa: E402
                              PASS1_BAND_INCLUSIVE, pass1_in_band)

MARK = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")
COMPILER_VERSION = "compiler-v2/0.2.0-frozen"


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hhmmss(t: str) -> int:
    q = [int(x) for x in t.split(":")]
    return q[0] * 3600 + q[1] * 60 + q[2] if len(q) == 3 else q[0] * 60 + q[1]


def slicer(text: str):
    blocks = text.split("\n\n")
    idx = [(i, int(m.group(1)) * 60 + int(m.group(2)))
           for i, b in enumerate(blocks) if (m := MARK.fullmatch(b.strip()))]

    def text_for(seg: Segment) -> str:
        out = []
        for k, (i, s) in enumerate(idx):
            if seg.start_s <= s < seg.end_s:
                end = idx[k + 1][0] if k + 1 < len(idx) else len(blocks)
                out.extend(blocks[i:end])
        return "\n\n".join(out).strip()
    return text_for


def main() -> int:
    tm = yaml.safe_load(TMAP.read_text(encoding="utf-8"))
    segs = [Segment(s["segment_id"], hhmmss(s["start"]), hhmmss(s["end"]),
                    s.get("topic", ""), s.get("function", ""))
            for s in tm["temporal_map"]]
    meta = yaml.safe_load(META.read_text(encoding="utf-8"))
    extent = hhmmss(meta["source"]["duration"])
    text = L0.read_text(encoding="utf-8")
    text_for = slicer(text)

    print("=" * 78)
    print("PILOT-001 — RODADA COMPLETA COM COMPILER-V2")
    print("=" * 78)
    print(f"L0           : sha256 {sha_p(L0)[:16]}… · extensão {extent}s")
    print(f"temporal-map : sha256 {sha_p(TMAP)[:16]}… · {len(segs)} segmentos")
    print(f"saída        : {OUTDIR.relative_to(DRIVE)}")
    print(f"PASS 1 herdado do mapa histórico — NÃO re-executado por modelo.\n")

    ex = ClaudeExtractor(text_for)
    res = pipeline.compile_lesson(
        pilot_id="PILOT-001", lesson_id="PILOT-001-L01",
        l0_sha256=sha_p(L0), extent_s=extent, segments=segs,
        extractor=ex, out_dir=OUTDIR, compiler_version=COMPILER_VERSION)

    m = res.manifest
    tot = ex.totals()
    n = len(segs)

    # evidências finais em JSONL, para auditoria
    (OUTDIR / "EVIDENCE.jsonl").write_text(
        "\n".join(json.dumps({
            "evidence_id": e.evidence_id, "segment_id": e.segment_id,
            "epistemic_status": e.epistemic_status, "category": e.category,
            "claim": e.claim,
            "source_excerpt": {"source_file": L0.name, "source_sha256": sha_p(L0),
                               "span": {"start_s": e.start_s, "end_s": e.end_s},
                               "quote": e.quote},
            "origin": e.origin, "iteration": e.iteration,
            "merged_from": e.merged_from,
        }, ensure_ascii=False) for e in res.evidences) + "\n", encoding="utf-8")
    TRACE.write_text(json.dumps({"totals": tot, "calls": ex.trace()},
                                ensure_ascii=False, indent=1), encoding="utf-8")

    g = m["coverage_gate"]
    p2 = m["pass2"]
    # união declarada por segmento
    ud = sum(b.dur for b in C.merge(
        [C.Citation(e.start_s, e.end_s, "d", e.evidence_id) for e in res.evidences]))

    print("--- 1. PASS 1 ---")
    print(f"segmentos            : {n} · banda {PASS1_BAND_INCLUSIVE} · "
          f"dentro: {pass1_in_band(n)}")
    print(f"histórico            : {HISTORICAL['segments']}")
    print(f"temporal-map sha256  : {m['pass1']['temporal_map_sha256'][:16]}…")
    print(f"persistido antes PASS2: {m['pass1']['persisted_before_pass2']}")
    print("  RESSALVA: herdado, não re-executado — não testa variância do PASS 1")

    print("\n--- 2. evidências e yield ---")
    ev_total = m["evidence"]["total"]
    print(f"total                : {ev_total}   (histórico {HISTORICAL['evidence']})")
    print(f"yield por segmento   : {m['evidence']['aggregate_yield_per_segment']}"
          f"   (histórico {HISTORICAL['yield_per_segment']})")
    print(f"comparação de yield válida (banda): "
          f"{m['evidence']['yield_comparison_valid']}")

    print("\n--- 3. cobertura ---")
    print(f"cobertura L0         : {g['l0_coverage_pct']}%   piso "
          f"{COVERAGE_FLOOR*100:.1f}% ({g['comparison']})")
    print(f"coberto/extensão     : {g['covered_s']}s / {g['extent_s']}s")
    print(f"união DECLARADA      : {ud}s  ·  por segmento: {ud/n:.1f}s")

    print("\n--- 4. portão ---")
    print(f"resultado            : {g['result']} ({g['stop_reason']})")
    print(f"iterações            : {g['rescan_iterations']}")
    for it in g["iterations"]:
        print(f"  #{it['iteration']}: {it['coverage_before']:.4f} → "
              f"{it['coverage_after']:.4f} · +{it['evidence_added']} · "
              f"alvos {it['targeted_segments']}")

    print("\n--- 5. rejeições e rótulos ---")
    rej = {}
    for c in ex.calls:
        for r in c.rejected:
            rej[r["reason"]] = rej.get(r["reason"], 0) + 1
    print(f"devolvidas={tot['drafts_returned']} aceitas={tot['drafts_accepted']} "
          f"rejeitadas={tot['drafts_rejected']}")
    for k, v in sorted(rej.items()):
        print(f"  {k}: {v}")
    if not rej:
        print("  nenhuma")
    mi = sum(1 for e in res.evidences if e.epistemic_status == "MODEL_INFERENCE")
    print(f"MODEL_INFERENCE      : {mi} de {ev_total}")
    print(f"avisos claim×literal : {tot['warnings']}")
    print(f"recuperadas pela normalização: {tot['recovered_by_normalization']}")
    print(f"dedup: {m['deduplication']['merged_after_pass2']} + "
          f"{m['deduplication']['merged_inside_gate']} + "
          f"{m['deduplication']['merged_after_rescan']} fusões")
    print(f"segmentos com yield zero: {p2['zero_yield_count']} "
          f"{p2['segments_with_zero_yield']}")

    print("\n--- 6. custo ---")
    print(f"chamadas             : {tot['calls']} (erros {tot['errors']})")
    print(f"tokens entrada       : {tot['input_tokens']}")
    print(f"tokens saída         : {tot['output_tokens']}")
    print(f"cache read/write     : {tot['cache_read_input_tokens']}/"
          f"{tot['cache_creation_input_tokens']}")
    print(f"latência total       : {tot['latency_s']}s")

    print(f"\nmanifesto: {res.manifest_path.name} sha256 {res.manifest_sha256[:16]}…")
    print(f"rastro por chamada: {TRACE}")
    print("\nNENHUM número acima foi interpretado. A leitura vem do revisor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
