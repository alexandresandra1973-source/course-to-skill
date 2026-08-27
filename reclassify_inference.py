#!/usr/bin/env python3
"""Reclassificação de MODEL_INFERENCE com as duas âncoras que faltavam.

CAMINHO 1 (já existia): quase-igual CAPITALIZADO, similaridade >= 0.60.
CAMINHO 2 (novo): quase-igual MINÚSCULO, similaridade >= 0.78 — mais estreito,
  para compensar a âncora de capitalização perdida. Pega Playwright/playright,
  Vercel/Verscell, Codex/codeex, Sonnet/sonet, Anthropic/Enthropic.
CAMINHO 3 (novo, ALIAS DECLARADO): 'Claude' ↔ claw/clawed/cloud/clod/clot.
  NÃO é limiar de similaridade — 'claude'↔'claw' dá 0,60 e cairia junto com
  lixo. É FATO MEDIDO: no L0 cortado, 133 de 146 menções (91,1%) ao produto
  central do curso estão corrompidas, e só 13 dizem 'claude'. Um alias assim é
  declarável porque a medição o sustenta, não porque a similaridade o permite.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from scan_source_corruption import lost_negation, corrupted_name
from detector_recall_fix import corrupted_name_lower

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
ALIAS = {"Claude": re.compile(r"\b(clawed|claw|clod|cloud|clawd|clode|clot)\b", re.I),
         "ROAS": re.compile(r"\b(rows|roads|row)\b", re.I)}
# Falsos positivos do caminho 2, revisados à mão e EXCLUÍDOS por nome: são
# tradução (pt↔en), não corrupção do ASR.
PATH2_REJECTED = {("Explorer", "explore"), ("Termos", "terms"), ("Agentes", "Agents"),
                  ("Agentes", "agents")}


def classify(r: dict):
    claim, quote = r["claim"], r["source_excerpt"]["quote"]
    d = lost_negation(claim, quote) or corrupted_name(claim, quote)
    if d:
        return "TRANSCRIPTION_CORRECTION", d["tipo"], 1
    d2 = corrupted_name_lower(claim, quote)
    if d2 and (d2["nome_na_claim"], d2["quase_igual_na_quote"]) not in PATH2_REJECTED:
        return "TRANSCRIPTION_CORRECTION", d2["tipo"], 2
    for name, rx in ALIAS.items():
        if name.lower() in claim.lower() and rx.search(quote) and name.lower() not in quote.lower():
            return "TRANSCRIPTION_CORRECTION", f"ALIAS_DECLARADO:{name}", 3
    return "GENUINE_INFERENCE", None, None


out = {}
import os
PIDS = os.environ.get("CTSS_PIDS", "PILOT-001-v2,PILOT-002-v2").split(",")
for pid in PIDS:
    p = DRIVE / f"Course-to-Skill-Claude/pilots/{os.environ.get('CTSS_EVSUB', pid)}/EVIDENCE.jsonl"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    mi = [r for r in rows if r["epistemic_status"] == "MODEL_INFERENCE"]
    corr, gen, by_path = [], [], {}
    for r in mi:
        cls, why, path = classify(r)
        item = {"evidence_id": r["evidence_id"], "segment_id": r["segment_id"],
                "category": r["category"], "why": why, "path": path,
                "claim": r["claim"], "quote": r["source_excerpt"]["quote"],
                "start_s": r["source_excerpt"]["span"]["start_s"]}
        if cls == "TRANSCRIPTION_CORRECTION":
            corr.append(item); by_path[path] = by_path.get(path, 0) + 1
        else:
            gen.append(item)
    out[pid] = {"total": len(rows), "model_inference": len(mi),
                "transcription_correction": len(corr), "genuine_inference": len(gen),
                "by_path": by_path,
                "genuine_pct_of_corpus": round(100*len(gen)/len(rows), 1),
                "correcao": corr, "genuina": gen}
    print(f"\n=== {pid} ===")
    print(f"  {len(rows)} evidências · MODEL_INFERENCE {len(mi)}")
    print(f"    CORREÇÃO DE TRANSCRIÇÃO : {len(corr):>3}  por caminho {by_path}")
    print(f"    INFERÊNCIA GENUÍNA      : {len(gen):>3}  "
          f"= {100*len(gen)/len(rows):.1f}% do corpus")

(T/os.environ.get("CTSS_SPLIT","mi-split-v2.json")).write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                  encoding="utf-8")
for k,v in out.items(): print(f"\n{k}: genuina {v['genuine_pct_of_corpus']}% do corpus")
