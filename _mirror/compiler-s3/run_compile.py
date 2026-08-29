#!/usr/bin/env python3
"""Compilação evidência→Skill do PILOT-002. 41 chamadas, uma por segmento."""
from __future__ import annotations
import hashlib, json, os, sys, time
from pathlib import Path
import anthropic, yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ctss import assemble, emit, policy, validate, classify              # noqa: E402
from ctss.schema import PRESERVED, COURSE_CONTENT                        # noqa: E402

import os as _os
DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
# Regra: execucao longa le e escreve em ext4. O Drive so na publicacao.
CL = Path(_os.environ.get("CTSS_ROOT", str(DRIVE / "Course-to-Skill-Claude")))
import os
PILOT = os.environ.get("CTSS_PILOT", "PILOT-002-v2")
EVDIR = os.environ.get("CTSS_EVDIR", f"pilots/{PILOT}")
P2 = CL / EVDIR; OUTDIR = CL / f"pilots/{PILOT}/skill"
ARM = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
       / "FINAL_PRE_RUN_LOCK_F7_SCORER_BOUND/PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip")
MEMBER = ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4/agent-input/runtime-bundle/"
          "knowledge/runtime-policy.yaml")
T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
TRACE = T / f"compile-trace-{PILOT}.json"

SYSTEM = """Você converte EVIDÊNCIAS extraídas de um curso em regras de decisão e passos de workflow executáveis.

REGRA DURA: toda regra e todo passo cita `evidence_ids`, e só pode citar ids do lote recebido. O que não cita, não entra. Nunca use conhecimento geral para completar.

Campos sem evidência saem literalmente "UNDEFINED". Não invente `autonomy`, `precedence`, `missing_input_action` nem `iteration_limit`: se a fonte não disser, é UNDEFINED — isso é um sinal desejado, não um defeito.

CONTABILIDADE: toda evidência do lote recebe exatamente uma disposição:
- CONSUMED_BY_RULE / CONSUMED_BY_STEP — virou regra ou passo
- NON_METHODOLOGICAL — é contexto, motivação, anedota ou mercado; não é método
- GAP — é método, mas a fonte não dá o suficiente para virar executável

ÂNCORA DE WORKFLOW: só declare uma se alguma evidência NOMEAR um procedimento.

Não escreva prosa. Só a estrutura."""

SCHEMA = {"type": "object", "properties": {
  "rules": {"type": "array", "items": {"type": "object", "properties": {
      "name": {"type": "string"}, "trigger": {"type": "string"},
      "condition": {"type": "string"}, "action": {"type": "string"},
      "autonomy": {"type": "string"}, "precedence": {"type": "string"},
      "missing_input_action": {"type": "string"}, "iteration_limit": {"type": "string"},
      "do_not": {"type": "array", "items": {"type": "string"}},
      "evidence_ids": {"type": "array", "items": {"type": "string"}}},
    "required": ["name","trigger","condition","action","autonomy","precedence",
                 "missing_input_action","iteration_limit","do_not","evidence_ids"],
    "additionalProperties": False}},
  "steps": {"type": "array", "items": {"type": "object", "properties": {
      "name": {"type": "string"}, "action": {"type": "string"},
      "required_inputs": {"type": "array", "items": {"type": "string"}},
      "missing_input_action": {"type": "string"}, "iteration_limit": {"type": "string"},
      "autonomy": {"type": "string"},
      "evidence_ids": {"type": "array", "items": {"type": "string"}}},
    "required": ["name","action","required_inputs","missing_input_action",
                 "iteration_limit","autonomy","evidence_ids"],
    "additionalProperties": False}},
  "workflow_anchors": {"type": "array", "items": {"type": "object", "properties": {
      "name": {"type": "string"}, "anchor_evidence_id": {"type": "string"}},
    "required": ["name","anchor_evidence_id"], "additionalProperties": False}},
  "dispositions": {"type": "array", "items": {"type": "object", "properties": {
      "evidence_id": {"type": "string"},
      "disposition": {"type": "string", "enum": ["CONSUMED_BY_RULE","CONSUMED_BY_STEP",
                                                 "NON_METHODOLOGICAL","GAP"]}},
    "required": ["evidence_id","disposition"], "additionalProperties": False}}},
  "required": ["rules","steps","workflow_anchors","dispositions"],
  "additionalProperties": False}


def main() -> int:
    rows = [json.loads(l) for l in (P2/"EVIDENCE.jsonl").read_text(encoding="utf-8")
            .splitlines() if l.strip()]
    tm = yaml.safe_load((Path(os.environ.get("CTSS_TMAP", str(P2/"temporal-map.yaml")))).read_text(encoding="utf-8"))["temporal_map"]
    para = set()
    dl = json.loads((T/f"distance-lines-{PILOT}.json").read_text(encoding="utf-8"))["lines"]
    for k, v in dl.items():
        if v.startswith("sem distância"):
            para.add(k)
    cls = classify.classify_all(rows, para)
    from collections import Counter
    dist = Counter(c["origin_class"] for c in cls.values())
    print("PRÉ-CLASSIFICAÇÃO (antes de qualquer regra):")
    for k, v in dist.most_common():
        tag = "conteúdo do curso" if k in COURSE_CONTENT else "NÃO é conteúdo do curso"
        print(f"  {k:<26} {v:>3}  ({tag})")
    print()

    by_seg = {}
    for r in rows:
        by_seg.setdefault(r["segment_id"], []).append(r)
    span = {r["evidence_id"]: (r["source_excerpt"]["span"]["start_s"],
                               r["source_excerpt"]["span"]["end_s"]) for r in rows}
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    rules, steps, anchors, disp, calls = [], [], [], {}, []
    rid = sid = wid = 0
    t0 = time.time()
    for i, s in enumerate(tm, 1):
        seg = s["segment_id"]; evs = by_seg.get(seg, [])
        if not evs:
            continue
        payload = (f"SEGMENTO {seg} · {s['start']}–{s['end']} · tópico: {s['topic']}\n"
                   f"função: {s.get('function')}\n\nEVIDÊNCIAS ({len(evs)}):\n" +
                   "\n".join(
                       f"[{e['evidence_id']}] ({e['category']}/"
                       f"{cls[e['evidence_id']]['origin_class']}) {e['claim']}\n"
                       f"    citação: {e['source_excerpt']['quote']}" for e in evs))
        st = time.time()
        with client.messages.stream(model="claude-opus-5", max_tokens=8000,
                                    system=SYSTEM,
                                    messages=[{"role":"user","content":payload}],
                                    output_config={"format":{"type":"json_schema",
                                                             "schema":SCHEMA}}) as stream:
            m = stream.get_final_message()
        d = json.loads("".join(b.text for b in m.content if b.type == "text"))
        known = {e["evidence_id"] for e in evs}
        for r in d["rules"]:
            rid += 1; r["rule_id"] = f"R-{rid:04d}"
            r["segment_ids"] = [seg]
            r["evidence_ids"] = [x for x in r["evidence_ids"] if x in known]
            oc = {cls[x]["origin_class"] for x in r["evidence_ids"]}
            r["origin_class"] = ("GENUINE_INFERENCE" if oc == {"GENUINE_INFERENCE"}
                                 else "SOURCE_EXPLICIT")
            rules.append(r)
        for p in d["steps"]:
            sid += 1; p["step_id"] = f"S-{sid:04d}"
            p["segment_ids"] = [seg]; p["workflow_id"] = None; p["order_key"] = 0
            p["evidence_ids"] = [x for x in p["evidence_ids"] if x in known]
            oc = {cls[x]["origin_class"] for x in p["evidence_ids"]}
            p["origin_class"] = ("GENUINE_INFERENCE" if oc == {"GENUINE_INFERENCE"}
                                 else "SOURCE_EXPLICIT")
            steps.append(p)
        for a in d["workflow_anchors"]:
            if a["anchor_evidence_id"] in known:
                wid += 1
                anchors.append({"workflow_id": f"WF-{wid:04d}", "name": a["name"],
                                "anchor_evidence_id": a["anchor_evidence_id"]})
        for x in d["dispositions"]:
            if x["evidence_id"] in known:
                disp[x["evidence_id"]] = x["disposition"]
        miss = known - set(disp)
        calls.append({"segment": seg, "n_ev": len(evs), "rules": len(d["rules"]),
                      "steps": len(d["steps"]), "anchors": len(d["workflow_anchors"]),
                      "undisposed": sorted(miss), "latency_s": round(time.time()-st,1),
                      "in": m.usage.input_tokens, "out": m.usage.output_tokens})
        print(f"  [{i:>2}/41] {seg} ev={len(evs):>2} → regras {len(d['rules'])} "
              f"passos {len(d['steps'])} âncoras {len(d['workflow_anchors'])}"
              f"{'  SEM DISPOSIÇÃO: '+str(sorted(miss)) if miss else ''}")
    TRACE.write_text(json.dumps({"calls": calls, "rules": rules, "steps": steps,
                                 "anchors": anchors, "dispositions": disp,
                                 "classes": cls, "elapsed_s": round(time.time()-t0,1)},
                                ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n41 chamadas em {round(time.time()-t0)}s · regras {len(rules)} · "
          f"passos {len(steps)} · âncoras {len(anchors)}")
    print(f"tokens entrada {sum(c['in'] for c in calls)} saída {sum(c['out'] for c in calls)}")
    print(f"rastro: {TRACE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
