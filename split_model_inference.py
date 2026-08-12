#!/usr/bin/env python3
"""Separa MODEL_INFERENCE em CORRECAO_DE_TRANSCRICAO e INFERENCIA_GENUINA.

Zero chamadas. Reusa o detector de corrupção já construído e calibrado
(capitalização + similaridade >= 0.60 + negação incorporada).

Consequência para o produto: regra que se apoia SÓ em inferência genuína é
LACUNA DO CURSO, mesmo funcionando — o modelo preencheu, o curso não ensinou.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from scan_source_corruption import lost_negation, corrupted_name

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
OUT = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/mi-split.json")


def split(p: Path, label: str) -> dict:
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    mi = [r for r in rows if r["epistemic_status"] == "MODEL_INFERENCE"]
    corr, genu = [], []
    for r in mi:
        q = r["source_excerpt"]["quote"]
        d = lost_negation(r["claim"], q) or corrupted_name(r["claim"], q)
        (corr if d else genu).append({"evidence_id": r["evidence_id"],
                                      "segment_id": r["segment_id"],
                                      "category": r["category"],
                                      "detector": (d or {}).get("tipo"),
                                      "claim": r["claim"][:110]})
    print(f"\n=== {label} ===")
    print(f"  total {len(rows)} · MODEL_INFERENCE {len(mi)} ({100*len(mi)/len(rows):.1f}%)")
    print(f"    CORRECAO_DE_TRANSCRICAO : {len(corr):>3}  → conta como conteúdo do curso")
    print(f"    INFERENCIA_GENUINA      : {len(genu):>3}  → NÃO é conteúdo do curso")
    import collections
    print(f"  genuína por categoria: "
          f"{dict(collections.Counter(g['category'] for g in genu).most_common(6))}")
    print("  exemplos de CORREÇÃO:")
    for c in corr[:4]:
        print(f"    [{c['evidence_id']}] {c['detector']}: {c['claim'][:88]}")
    print("  exemplos de INFERÊNCIA GENUÍNA:")
    for g in genu[:4]:
        print(f"    [{g['evidence_id']}] {g['claim'][:88]}")
    return {"total": len(rows), "model_inference": len(mi),
            "correcao_de_transcricao": len(corr), "inferencia_genuina": len(genu),
            "correcao_ids": [c["evidence_id"] for c in corr],
            "genuina_ids": [g["evidence_id"] for g in genu],
            "detalhe_correcao": corr, "detalhe_genuina": genu}


res = {}
for pid, lbl in (("PILOT-001-v2", "PILOT-001-v2"), ("PILOT-002-v2", "PILOT-002-v2")):
    p = DRIVE / f"Course-to-Skill-Claude/pilots/{pid}/EVIDENCE.jsonl"
    if p.is_file():
        res[pid] = split(p, lbl)
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n{OUT}")
