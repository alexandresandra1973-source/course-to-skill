#!/usr/bin/env python3
"""Densidade é informação nova ou redundância? Medição, sem chamada de modelo.

Roda daqui (ext4). READ-ONLY. Imprime; publica só se `--publish`.

A dedup do compilador casa CLAIM NORMALIZADA — critério sintático. Duas claims
com redação diferente sobre o mesmo conteúdo passam intactas pelas duas. Zero
fusões, portanto, não é resposta: mede que ninguém repetiu palavra por palavra,
não que ninguém repetiu conteúdo.

O que este script mede, e o que ele se recusa a decidir:
  - MEDE multiplicidade por segundo, fator de sobreposição e os pontos de pico;
  - IMPRIME as claims sobrepostas inteiras nos picos;
  - NÃO julga se elas dizem a mesma coisa. Isso é semântica, e a chamada é do
    revisor.
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cts import coverage as C                                    # noqa: E402

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
EV1 = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
       / "analysis/evidence.jsonl")
EV2 = DRIVE / "Course-to-Skill-Claude/pilots/PILOT-001-v2/EVIDENCE.jsonl"
EXTENT = 905
TOP = 5
EXCLUSION = 20      # segundos suprimidos ao redor de um pico já reportado


def hh(t: str) -> int:
    q = [int(x) for x in t.split(":")]
    return q[0] * 3600 + q[1] * 60 + q[2] if len(q) == 3 else q[0] * 60 + q[1]


def fmt(s: int) -> str:
    return f"{s // 60}:{s % 60:02d}"


def load_hist() -> list[dict]:
    out = []
    for r in [json.loads(l) for l in EV1.read_text(encoding="utf-8").splitlines()
              if l.strip()]:
        for ref in (r.get("source_refs") or []):
            ts = ref.get("timestamp") or {}
            if ts.get("start") and ts.get("end"):
                out.append({"id": r["evidence_id"], "a": hh(ts["start"]),
                            "b": hh(ts["end"]),
                            "claim": r.get("observation") or ""})
    return out


def load_v2() -> list[dict]:
    return [{"id": x["evidence_id"],
             "a": x["source_excerpt"]["span"]["start_s"],
             "b": x["source_excerpt"]["span"]["end_s"],
             "claim": x["claim"], "quote": x["source_excerpt"]["quote"],
             "seg": x["segment_id"], "status": x["epistemic_status"]}
            for x in [json.loads(l) for l in
                      EV2.read_text(encoding="utf-8").splitlines() if l.strip()]]


def multiplicity(spans: list[dict]) -> list[int]:
    m = [0] * (EXTENT + 1)
    for s in spans:
        for t in range(max(0, s["a"]), min(EXTENT, s["b"])):
            m[t] += 1
    return m


def overlap_factor(spans: list[dict]) -> tuple[int, int, float]:
    soma = sum(s["b"] - s["a"] for s in spans)
    uni = sum(b.dur for b in C.merge(
        [C.Citation(s["a"], s["b"], "x", s["id"]) for s in spans]))
    return soma, uni, (soma / uni if uni else 0.0)


def report(label: str, spans: list[dict]) -> dict:
    m = multiplicity(spans)
    cov = [x for x in m if x > 0]
    soma, uni, fac = overlap_factor(spans)
    dist = Counter(m)
    print(f"\n### {label} — {len(spans)} spans")
    print(f"  soma dos spans : {soma}s")
    print(f"  união          : {uni}s")
    print(f"  FATOR DE SOBREPOSIÇÃO: {fac:.2f}×")
    print(f"  segundos cobertos: {len(cov)} de {EXTENT}")
    print(f"  multiplicidade nos segundos cobertos: mediana "
          f"{statistics.median(cov):.0f} · média {statistics.mean(cov):.2f} · "
          f"máx {max(cov)}")
    print(f"  distribuição (multiplicidade → segundos):")
    for k in sorted(dist):
        bar = "█" * min(40, dist[k] // 8) or "·"
        print(f"    {k:>2}× {dist[k]:>4}s {bar}")
    return {"m": m, "soma": soma, "uniao": uni, "fator": fac}


def peaks(m: list[int], spans: list[dict], n: int = TOP) -> list[dict]:
    work = list(m)
    out = []
    for _ in range(n):
        top = max(work)
        if top <= 1:
            break
        t = work.index(top)
        here = [s for s in spans if s["a"] <= t < s["b"]]
        out.append({"t": t, "mult": top, "spans": here})
        for k in range(max(0, t - EXCLUSION), min(len(work), t + EXCLUSION + 1)):
            work[k] = 0
    return out


def main() -> int:
    hist, v2 = load_hist(), load_v2()

    print("=" * 84)
    print("DENSIDADE: INFORMAÇÃO NOVA OU REDUNDÂNCIA?")
    print("=" * 84)
    h = report("HISTÓRICO (44 evidências, compilador antigo)", hist)
    v = report("V2 (149 evidências, compiler-v2)", v2)

    print("\n" + "=" * 84)
    print("MUDANÇA DE REGIME")
    print("=" * 84)
    print(f"  fator de sobreposição : {h['fator']:.2f}× → {v['fator']:.2f}×")
    print(f"  união                 : {h['uniao']}s → {v['uniao']}s "
          f"(+{v['uniao'] - h['uniao']}s)")
    print(f"  spans                 : {len(hist)} → {len(v2)} "
          f"(+{len(v2) - len(hist)})")
    novo = (v['uniao'] - h['uniao']) / max(1, len(v2) - len(hist))
    print(f"  território NOVO por span novo: {novo:.2f}s")
    print(f"  território por span no histórico: {h['uniao']/len(hist):.2f}s")

    print("\n" + "=" * 84)
    print(f"OS {TOP} PONTOS DE MAIOR MULTIPLICIDADE — CLAIMS INTEIRAS")
    print("=" * 84)
    print("As claims abaixo reivindicam o MESMO segundo de L0. Afirmam coisas")
    print("DIFERENTES (atomicidade correta) ou a MESMA coisa (redundância)?")
    print("A medição não decide isso. A leitura é do revisor.\n")
    for i, p in enumerate(peaks(v["m"], v2), 1):
        print(f"--- pico {i}: {fmt(p['t'])} ({p['t']}s) · multiplicidade "
              f"{p['mult']} ---")
        for s in sorted(p["spans"], key=lambda x: (x["a"], x["id"])):
            print(f"  [{s['id']}] {fmt(s['a'])}–{fmt(s['b'])} · {s['seg']} · "
                  f"{s['status']}")
            print(f"      claim: {s['claim']}")
            print(f"      quote: {s['quote'][:150]}"
                  f"{'…' if len(s['quote']) > 150 else ''}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
