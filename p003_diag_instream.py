#!/usr/bin/env python3
"""Diagnóstico da LACUNA DE EXTRAÇÃO do youtube instream. Zero chamadas."""
from __future__ import annotations
import json, re
from collections import Counter
from pathlib import Path
import yaml

W = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-work")
MARK = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")
TERMOS = re.compile(r"\b(instream|in-stream)\b", re.I)


def main() -> int:
    raw = (W/"00_SOURCE/L0-transcript.txt").read_text(encoding="utf-8")
    tm = yaml.safe_load((W/"01_PASS1/temporal-map.yaml").read_text(encoding="utf-8"))["temporal_map"]
    ev = [json.loads(l) for l in (W/"02_PASS2/EVIDENCE.jsonl").read_text(encoding="utf-8")
          .splitlines() if l.strip()]
    ck = {json.loads(l)["segment_id"]: json.loads(l)
          for l in (W/"02_PASS2/pass2-checkpoint.jsonl").read_text(encoding="utf-8")
          .splitlines() if l.strip()}

    # --- 1. onde estão as ocorrências em L0
    blocks = raw.split("\n\n"); cur = 0; hits = []
    for b in blocks:
        m = MARK.fullmatch(b.strip())
        if m:
            cur = int(m.group(1))*60 + int(m.group(2)); continue
        for _ in TERMOS.finditer(b):
            hits.append(cur)
    print(f"ocorrências de instream no L0: {len(hits)}")
    print(f"faixa: {min(hits)//60}:{min(hits)%60:02d} a {max(hits)//60}:{max(hits)%60:02d}")

    # --- 2. em que segmentos caem
    def seg_of(t):
        for s in tm:
            if s["start_s"] <= t < s["end_s"]:
                return s
        return None
    dist = Counter(seg_of(t)["segment_id"] for t in hits if seg_of(t))
    print(f"\nsegmentos atingidos: {len(dist)}")
    ev_by_seg = Counter(e["segment_id"] for e in ev)
    med = sum(ev_by_seg.values())/len(tm)
    print(f"média de evidências por segmento no piloto: {med:.1f}\n")
    print(f"  {'segmento':<10} {'ocorr':>5} {'evidências':>11} {'dur':>5}  tópico")
    total_ev = 0
    for sid, n in dist.most_common():
        s = next(x for x in tm if x["segment_id"] == sid)
        e = ev_by_seg.get(sid, 0); total_ev += e
        print(f"  {sid:<10} {n:>5} {e:>11} {s['duration_s']:>5}  {s['topic'][:52]}")
    # --- 3. o que o PASS 2 devolveu nesses segmentos
    print("\nAMOSTRA do que o extractor devolveu nos segmentos atingidos:")
    for sid, _ in dist.most_common(3):
        print(f"\n  [{sid}]")
        for e in [x for x in ev if x["segment_id"] == sid][:5]:
            marca = "  <-- MENCIONA" if TERMOS.search(e["claim"] + e["source_excerpt"]["quote"]) else ""
            print(f"    {e['claim'][:96]}{marca}")
    # --- 4. veredito
    n_seg = len(dist)
    ev_media_atingidos = total_ev / n_seg if n_seg else 0
    cita = sum(1 for e in ev if TERMOS.search(e["claim"] + e["source_excerpt"]["quote"]))
    print("\n" + "="*70)
    print(f"evidências nos segmentos atingidos: {total_ev} em {n_seg} segmentos "
          f"= {ev_media_atingidos:.1f}/segmento")
    print(f"média do piloto: {med:.1f}/segmento")
    print(f"evidências que CITAM instream: {cita}")
    if ev_media_atingidos >= med * 0.8:
        print("\nVEREDITO: O EXTRACTOR PULOU O TÓPICO.")
        print("  Os segmentos renderam volume NORMAL de evidência, sobre OUTROS")
        print("  assuntos. Não é falha de segmento: é seleção dentro do segmento.")
    else:
        print("\nVEREDITO: FALHA DE SEGMENTO.")
        print("  Os segmentos atingidos renderam abaixo da média do piloto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
