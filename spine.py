#!/usr/bin/env python3
"""Espinha vertical da Fase 4 — roda contra o material REAL do PILOT-001.

Executa daqui (ext4). Lê o Drive só para (a) conferir contra o baseline
congelado e (b) ingerir L0 no vault local. Nada é escrito no Drive por este
script — a publicação é separada (publish.py).

Reprovação correta é sucesso: o piloto está defeituoso por construção e a
espinha existe para dizer isso sem quebrar.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cts import cutter, dispersion
from cts.adapters import pilot001 as P
from cts.gates import g2_anchor, g3_dispersion, g5_closure, g5_origin, g6_ceiling
from cts.result import GateResult, dump, PASS, FAIL, NOT_ESTABLISHED
from cts.vault import Vault, sha256_file

HERE = Path(__file__).parent
WORK = HERE / "work"
MANIFEST = Path("/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Claude/docs"
                "/BASELINE_MANIFEST_20260810.txt")
HOLDOUT_SEED = 20260810
HOLDOUT_RATE = 0.20
THRESHOLD = 0.80


# ---------------------------------------------------------------- baseline

def check_baseline() -> dict:
    """Confere as entradas contra o manifesto congelado. Deriva é registrada,
    o manifesto NÃO é atualizado (é a referência fixa da Fase 5)."""
    expected: dict[str, tuple[str, int]] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        sha, size, _mtime, rel = line.split("  ", 3)
        expected[rel] = (sha, int(size))

    drive = Path("/mnt/g/Meu Drive/Chat GPT")
    present = {}
    for root in ("Course-to-Skill", "Course-to-Skill-Compiler"):
        for p in (drive / root).rglob("*"):
            if p.is_file():
                present[str(p.relative_to(drive))] = p

    changed, missing = [], []
    for rel, (sha, size) in expected.items():
        p = present.get(rel)
        if p is None:
            missing.append(rel)
            continue
        if p.stat().st_size != size or sha256_file(p) != sha:
            changed.append(rel)
    added = sorted(set(present) - set(expected))
    return {"in_manifest": len(expected), "present_now": len(present),
            "changed": changed, "missing": missing, "added": added}


# ---------------------------------------------------------------- vault

def build_vault() -> tuple[Vault, str, dict]:
    v = Vault(WORK / "vault")
    tr = v.ingest(P.L0_TRANSCRIPT, "text/plain")
    v.ingest(P.L0_METADATA, "application/yaml")
    frames = [v.ingest(f, "image/png") for f in P.L0_FRAMES]
    stats = {"objects": 2 + len(frames),
             "transcript_sha256": tr.sha256,
             "transcript_bytes": tr.bytes_,
             "frames": len(frames),
             "time_marks": len(v.marks(tr.sha256))}
    return v, tr.sha256, stats


# ---------------------------------------------------------------- corrida

def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    WORK.mkdir(exist_ok=True)
    base = check_baseline()
    vault, tr_sha, vstats = build_vault()
    results: list[GateResult] = []

    # ---- Cutter: operação correta (prova que o componente funciona) ----
    segs = cutter.segment_by_marks(vault, tr_sha)
    lock = cutter.cut(segs, HOLDOUT_SEED, HOLDOUT_RATE)
    train = cutter.train_corpus(segs, lock)
    lock2 = cutter.cut(segs, HOLDOUT_SEED, HOLDOUT_RATE)
    cut_ok = (lock["sha256"] == lock2["sha256"]
              and cutter.corpus_hash(train) != cutter.corpus_hash(segs)
              and len(train) + lock["n_holdout"] == len(segs))
    results.append(GateResult(
        gate="G1-cutter/functional", state=PASS if cut_ok else FAIL,
        subject=str(P.L0_TRANSCRIPT),
        evidence={"segments": len(segs), "n_holdout": lock["n_holdout"],
                  "n_train": len(train), "seed": HOLDOUT_SEED, "rate": HOLDOUT_RATE,
                  "lock_sha256": lock["sha256"],
                  "deterministic": lock["sha256"] == lock2["sha256"],
                  "corpus_hash_all": cutter.corpus_hash(segs)[:16],
                  "corpus_hash_train": cutter.corpus_hash(train)[:16]},
        note="corte semeado em L0, ANTES de qualquer extracao (ADR-0003)"))

    # ---- Cutter: auditoria retroativa do PILOT-001 ----
    import yaml
    registry = yaml.safe_load(P.HELDOUT_REGISTRY.read_text(encoding="utf-8"))
    blind = P.blind_cases(tr_sha)
    audit = cutter.retroactive_audit(registry, blind)
    contaminated = [v for v in audit["verdicts"]
                    if v["verdict"] != "HELD_OUT_OK"]
    results.append(GateResult(
        gate="G1-cutter/retroactive", state=NOT_ESTABLISHED if not audit["established"] else PASS,
        subject=str(P.HELDOUT_REGISTRY),
        evidence={"registry_status": audit["registry_status"],
                  "created_before_modeling": audit["created_before_modeling"],
                  "locked": audit["locked"],
                  "cases_in_registry": audit["n_cases_in_registry"],
                  "cases_claiming_blind": len(blind),
                  "contaminated": len(contaminated)},
        findings=audit["verdicts"],
        note="sem lock pre-extracao, todo caso que se declara cego e' "
             "contaminado por construcao (ADR-0003)"))

    # ---- G2 anchor ----
    ev = P.load_evidence()
    recs = [{"id": e["evidence_id"],
             "spans": P.evidence_spans(e, tr_sha),
             "quote": e.get("source_excerpt"),
             "claim": e.get("observation")} for e in ev]
    g2 = g2_anchor.run(vault, recs, str(P.EVIDENCE))
    results.append(g2)

    # ---- G3 dispersion ----
    dec = P.docs(P.DECISIONS_POST_AUDIT)
    fields = {
        "evidence.origin_class":      [e.get("origin_class") for e in ev],
        "evidence.status":            [e.get("status") for e in ev],
        "evidence.evidence_strength": [e.get("evidence_strength") for e in ev],
        "evidence.confidence.level":  [(e.get("confidence") or {}).get("level") for e in ev],
        "evidence.category":          [e.get("category") for e in ev],
        "decision.origin_class":      [d.get("origin_class") for d in dec],
        "decision.rationale.state":   [(d.get("rationale") or {}).get("state") for d in dec],
        "decision.promotion_level":   [d.get("promotion_level") for d in dec],
        "decision.autonomy.level":    [(d.get("autonomy") or {}).get("level") for d in dec],
        "decision.status":            [d.get("status") for d in dec],
    }
    g3 = g3_dispersion.run(fields, P.schema_domains(),
                           f"{P.EVIDENCE.name} + {P.DECISIONS_POST_AUDIT.name}")
    results.append(g3)

    # ---- G5 closure ----
    artifact_spans: list[str] = []
    for e in ev:
        artifact_spans.extend(P.evidence_spans(e, tr_sha))
    g5 = g5_closure.run(
        bundle_claims=P.bundle_claims(),
        audited_claims=P.audited_claims(),
        normalize=P.normalize_claim,
        subject=str(P.BUNDLE),
        rubric_text=P.TEST_SUITE.read_text(encoding="utf-8"),
        holdout_spans=lock["spans"],
        artifact_spans=artifact_spans)
    results.append(g5)

    # ---- G5/origin: em que camada entrou o que o adversario sinalizou ----
    import yaml as _y
    l1_dec = P.docs(P.PILOT / "analysis/decisions.yaml")
    bundle_dec = _y.safe_load(
        (P.BUNDLE / "knowledge/decision-rules.yaml").read_text(encoding="utf-8")
    )["decision_rules"]
    # SC-001 (HIGH) atribuiu ao compilador os niveis de autonomia destes ADRs:
    sc001 = ["ADR-0002", "ADR-0003", "ADR-0005", "ADR-0007", "ADR-0008"]
    g5o = g5_origin.run(l1_records=l1_dec, bundle_records=bundle_dec,
                        field_path=("autonomy", "level"), flagged_ids=sc001,
                        subject=str(P.PILOT / "analysis/decisions.yaml"))
    results.append(g5o)

    # ---- G6 ceiling ----
    n_holdout_real = len(registry.get("cases") or [])
    g6 = g6_ceiling.run(
        vault_sealed=True, g2=g2, g3=g3, g4=None, g5=g5,
        n_holdout=n_holdout_real, threshold=THRESHOLD,
        requested_level="S4_CLOSED",
        subject=str(P.BUNDLE / "manifest.yaml"),
        corpus_stats={"lessons": 1, "evidence_records": len(ev),
                      "decision_records": len(dec),
                      "decision_branches": sum(len(d.get("conditions") or []) for d in dec),
                      "transcript_time_marks": vstats["time_marks"]})
    results.append(g6)

    # também: o nível que o piloto REIVINDICA hoje
    g6b = g6_ceiling.run(
        vault_sealed=True, g2=g2, g3=g3, g4=None, g5=g5,
        n_holdout=n_holdout_real, threshold=THRESHOLD,
        requested_level="S1_ANCHORED",
        subject=str(P.BUNDLE / "manifest.yaml"),
        corpus_stats={"claimed_in_manifest": "S3_EXECUTABLE"})
    g6b.gate = "G6-ceiling/S1"
    results.append(g6b)

    out = {"started": started, "baseline": base, "vault": vstats,
           "results": [r.to_dict() for r in results]}
    (WORK / "spine_result.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    dump(results, WORK / "gates.jsonl")

    for r in results:
        print(r)
    print(f"\nbaseline: {base['in_manifest']} no manifesto | "
          f"alterados={len(base['changed'])} sumidos={len(base['missing'])} "
          f"novos={len(base['added'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
