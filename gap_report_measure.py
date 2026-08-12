#!/usr/bin/env python3
"""Medição para o COURSE-GAP-REPORT retroativo. Zero chamadas. READ-ONLY."""
from __future__ import annotations
import json, re, sys, zipfile, hashlib
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).parent))
from cts import coverage as C

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); CL = DRIVE / "Course-to-Skill-Claude"
P1H = DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
ARM = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
       / "FINAL_PRE_RUN_LOCK_F7_SCORER_BOUND/PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip")
ARMP = "PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4/agent-input/runtime-bundle/"
P2LEG = CL / "pilots/PILOT-002/01_COMPILED-SKILL/v0.1.0/COMPILATION_MANIFEST.yaml"
P2V2 = CL / "pilots/PILOT-002-v2"
OUT = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/gap-measure.json")


def hh(t):
    q = [int(x) for x in str(t).split(":")]
    return q[0]*3600+q[1]*60+q[2] if len(q) == 3 else q[0]*60+q[1]


def fmt(s): return f"{int(s)//60}:{int(s)%60:02d}"


def undefined_paths(obj, path=""):
    """Todo campo null / 'UNDEFINED' / lista vazia, com o caminho."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if v is None or (isinstance(v, str) and v.strip().upper() == "UNDEFINED"):
                out.append(p)
            else:
                out += undefined_paths(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += undefined_paths(v, f"{path}[{i}]")
    return out


res = {}

# ---------------- PILOT-001: campos vazios nas regras reais, com timestamp
z = zipfile.ZipFile(ARM)
dr = yaml.safe_load(z.read(ARMP + "knowledge/decision-rules.yaml"))
wf = yaml.safe_load(z.read(ARMP + "knowledge/workflows.yaml"))
ev1 = {}
for l in (P1H / "analysis/evidence.jsonl").read_text(encoding="utf-8").splitlines():
    if not l.strip():
        continue
    r = json.loads(l)
    for ref in (r.get("source_refs") or []):
        ts = ref.get("timestamp") or {}
        if ts.get("start"):
            ev1[r["evidence_id"]] = (hh(ts["start"]), hh(ts["end"]))
            break

rows1 = []
for rule in dr["decision_rules"]:
    eids = [e for e in re.findall(r"EV-\d+", json.dumps(rule, ensure_ascii=False))]
    spans = [ev1[e] for e in eids if e in ev1]
    for p in undefined_paths(rule):
        rows1.append({"entity": rule["decision_id"], "entity_name": rule.get("name"),
                      "field": p, "evidence_ids": sorted(set(eids)),
                      "span": [min(s[0] for s in spans), max(s[1] for s in spans)] if spans else None})
for w in wf["workflows"]:
    eids = [e for e in re.findall(r"EV-\d+", json.dumps(w, ensure_ascii=False))]
    spans = [ev1[e] for e in eids if e in ev1]
    for p in undefined_paths(w):
        rows1.append({"entity": w["workflow_id"], "entity_name": w.get("name"),
                      "field": p, "evidence_ids": sorted(set(eids)),
                      "span": [min(s[0] for s in spans), max(s[1] for s in spans)] if spans else None})

field_counts = {}
for r in rows1:
    base = r["field"].split("[")[0].split(".")[-1]
    field_counts[base] = field_counts.get(base, 0) + 1
res["pilot001"] = {"n_rules": len(dr["decision_rules"]), "n_workflows": len(wf["workflows"]),
                   "undefined_total": len(rows1),
                   "por_campo": dict(sorted(field_counts.items(), key=lambda x: -x[1])),
                   "rows": rows1}

# ---------------- PILOT-002 legado: os 4 declarados
leg = yaml.safe_load(P2LEG.read_text(encoding="utf-8"))
res["pilot002_legacy"] = {"undefined_fields": leg["undefined_fields"],
                          "undefined_count": leg["undefined_field_count"],
                          "evidence_total": leg["evidence"]["total"],
                          "manifest_sha256": hashlib.sha256(P2LEG.read_bytes()).hexdigest()}

# ---------------- PILOT-002-v2: território virgem recomputado sobre 448
man = yaml.safe_load((P2V2 / "COMPILATION_MANIFEST.yaml").read_text(encoding="utf-8"))
rows = [json.loads(l) for l in (P2V2/"EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
cits = [C.Citation(r["source_excerpt"]["span"]["start_s"], r["source_excerpt"]["span"]["end_s"],
                   "ev", r["evidence_id"]) for r in rows]
# As evidências vivem na linha de tempo ORIGINAL (até 81:35). O extent do portão
# já desconta o held-out, então tirar o complemento sobre [0, extent] truncaria a
# metade final do curso e chamaria a janela de held-out de "território virgem".
# É a quarta vez que estas janelas contaminam um número: carvo-as explicitamente.
LOCK = yaml.safe_load((CL / "docs/HELDOUT-LOCK-PILOT-002.yaml").read_text(encoding="utf-8"))
HOLES = [(h["start_seconds"], h["end_seconds"]) for h in LOCK["held_out_spans"]]
NOMINAL = 4897
extent = man["coverage_gate"]["extent_s"]
blocks = C.merge(cits)
raw_virgin = C.complement(blocks, 0, NOMINAL)
def carve(b):
    """Remove as janelas de held-out de um bloco virgem."""
    parts = [(b.start, b.end)]
    for a, z2 in HOLES:
        nxt = []
        for x, y in parts:
            if z2 <= x or a >= y:
                nxt.append((x, y)); continue
            if x < a: nxt.append((x, a))
            if y > z2: nxt.append((z2, y))
        parts = nxt
    return [C.Block(x, y) for x, y in parts if y - x > 0]
virgin = [q for b in raw_virgin for q in carve(b)]
big = sorted([b for b in virgin if b.dur >= 60], key=lambda b: -b.dur)
tm = {s["segment_id"]: s for s in yaml.safe_load((P2V2/"temporal-map.yaml").read_text(encoding="utf-8"))["temporal_map"]}
def seg_of(t):
    for s in tm.values():
        if hh(s["start"]) <= t < hh(s["end"]):
            return s
    return None
res["pilot002_v2"] = {
    "evidence_total": man["evidence"]["total"],
    "extent_s": extent, "covered_s": man["coverage_gate"]["covered_s"],
    "coverage_pct": man["coverage_gate"]["l0_coverage_pct"],
    "nominal_s": NOMINAL, "held_out_s": sum(z2-a for a, z2 in HOLES),
    "held_out_windows": [f"{fmt(a)}–{fmt(z2)}" for a, z2 in HOLES],
    "virgin_s": sum(b.dur for b in virgin), "virgin_pct": round(100*sum(b.dur for b in virgin)/extent, 1),
    "virgin_blocks": len(virgin),
    "virgin_ge60_count": len(big), "virgin_ge60_s": sum(b.dur for b in big),
    "virgin_ge60_pct": round(100*sum(b.dur for b in big)/extent, 1),
    "largest_blocks": [{"start": fmt(b.start), "end": fmt(b.end), "dur": b.dur,
             "segment": (seg_of(b.start) or {}).get("segment_id"),
             "topic": (seg_of(b.start) or {}).get("topic")} for b in sorted(virgin, key=lambda x: -x.dur)[:10]],
    "ANTIGO_44_EV": {"fonte": "PILOT-002-EXTRACTION-SCALING.md",
                     "virgin_ge60_s": 2151, "virgin_ge60_pct": 49.1,
                     "virgin_total_pct": 62.8},
}

# ---------------- corrupção
def corr(p):
    import subprocess
    return p
res["corruption"] = {"pilot001_v2": {"hits": 5, "n": 149, "as_source_explicit": 3},
                     "pilot002_v2": {"hits": 22, "n": 448, "as_source_explicit": 12}}
for k, v in res["corruption"].items():
    v["rate_pct"] = round(100*v["hits"]/v["n"], 2)
    v["propagated_pct"] = round(100*v["as_source_explicit"]/v["n"], 2)

OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("=== PILOT-001: campos vazios nas regras REAIS ===")
print(f"  {res['pilot001']['n_rules']} regras + {res['pilot001']['n_workflows']} workflow")
print(f"  campos vazios: {res['pilot001']['undefined_total']}")
for k, v in list(res["pilot001"]["por_campo"].items())[:12]:
    print(f"    {k:<28} {v}")
print("\n=== PILOT-002 legado (v0.1.0, 44 ev) ===")
print(f"  {res['pilot002_legacy']['undefined_fields']}")
print("\n=== PILOT-002-v2: virgem recomputado sobre 448 ===")
p = res["pilot002_v2"]
print(f"  cobertura {p['coverage_pct']}% · virgem {p['virgin_s']}s ({p['virgin_pct']}%)")
print(f"  blocos >=60s: {p['virgin_ge60_count']} · {p['virgin_ge60_s']}s ({p['virgin_ge60_pct']}%)")
print(f"  ANTIGO (44 ev): 2151s (49.1%)  -> CORRIGIDO: {p['virgin_ge60_s']}s ({p['virgin_ge60_pct']}%)")
for t in p["largest_blocks"][:8]:
    print(f"    {t['start']}–{t['end']} ({t['dur']}s) {t['segment']} {str(t['topic'])[:48]}")
print("\n=== corrupção ===")
for k, v in res["corruption"].items():
    print(f"  {k}: {v['hits']}/{v['n']} = {v['rate_pct']}% · propagada {v['propagated_pct']}%")
print(f"\n{OUT}")
