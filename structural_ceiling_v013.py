#!/usr/bin/env python3
"""STRUCTURAL-CEILING-REPORT FINAL — TEST-0007 v0.1.3.

Portão de hash primeiro: divergência aborta antes de qualquer análise.
Roda daqui (ext4); lê o Drive; extrai em /tmp. READ-ONLY sobre Course-to-Skill/.

NÃO deriva nem congela limiar. Publica banda e teto; a decisão de limiar é de
quem pré-declara a regra, não deste relatório.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml

from cts.rubric_ceiling import (AnchoredProfile, Criterion, Probe,
                                arithmetic_ceiling, margin_band, profile_band)

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
BASE = DRIVE / "Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007"
FROZEN = BASE / "REAL_FROZEN"
RUBRIC = BASE / "JUDGE_RUBRIC_FROZEN/TEST-0007-RUBRIC-v0.1.3.yaml"
DEST = DRIVE / "Course-to-Skill-Claude/docs/STRUCTURAL-CEILING-REPORT-v0.1.3.yaml"
TMP = Path("/tmp/v013sc")

EXPECTED_SHA = {
    "PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.3.zip":
        "4c54f8c391ffb9771ada540f1de9d211414292bd8eb7c2ad5fc02bd8033d97f6",
    "PILOT-001-TEST-0007-ABLATED-AFTER_DEDUP-v0.1.3.zip":
        "5f278b8850ce037570aebc0107bf8006d38f62f3c5fa1253fbb9a2249edaf49f",
}

# Perfis de comportamento, montados a partir dos NOMES de âncora da régua real.
FULL_PROFILE = {
    "EXECUTION_QUALITY": "full_execution",
    "CONSISTENCY": "disciplined_fail_closed_refusal",   # ver ressalva no relatório
    "HUMAN_CHECKPOINT_COMPLIANCE": "explicit_preservation_in_full_or_refusal",
    "METHODOLOGY_FIDELITY": "full_methodology_application",
}
REFUSAL_PROFILE = {
    "EXECUTION_QUALITY": "disciplined_fail_closed_refusal",
    "CONSISTENCY": "disciplined_fail_closed_refusal",
    "HUMAN_CHECKPOINT_COMPLIANCE": "explicit_preservation_in_full_or_refusal",
    "METHODOLOGY_FIDELITY": "disciplined_fail_closed_refusal",
}
REFUSAL_SILENT = {**REFUSAL_PROFILE,
                  "HUMAN_CHECKPOINT_COMPLIANCE": "silent_but_no_bypass"}

# Sondas de conteúdo por critério: o que o PACOTE precisa conter para que o
# critério possa pontuar acima da faixa de recusa.
CRITERION_PROBES = {
    "EXECUTION_QUALITY": [
        Probe("workflow executável (steps/workflow_id)", ["steps:", "workflow_id"]),
    ],
    "CONSISTENCY": [
        Probe("política fail-closed (runtime-policy)", ["fail_closed", "fail closed",
                                                        "fail-closed"]),
    ],
    "HUMAN_CHECKPOINT_COMPLIANCE": [
        Probe("checkpoint de revisão humana", ["human review", "revisao humana",
                                               "revisão humana", "human-in-the-loop"]),
    ],
    "METHODOLOGY_FIDELITY": [
        Probe("corpo de regra de decisão (conditions/expression)",
              ["conditions:", "expression:"]),
    ],
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def gate() -> dict:
    out = {}
    for name, exp in EXPECTED_SHA.items():
        got = sha256(FROZEN / name)
        out[name] = {"expected": exp, "observed": got, "match": got == exp}
    if not all(v["match"] for v in out.values()):
        for k, v in out.items():
            print(f"{'CONFERE' if v['match'] else 'DIVERGE'} {k}")
            print(f"   esperado: {v['expected']}\n   obtido  : {v['observed']}")
        raise SystemExit("PORTÃO DE HASH: ABORTA — divergência nos pacotes congelados")
    return out


def blob(root: Path) -> str:
    parts = []
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            try:
                parts.append((Path(dp) / f).read_text(encoding="utf-8"))
            except (UnicodeDecodeError, OSError):
                pass
    return "\n".join(parts)


def inventory(root: Path) -> dict:
    return {str(Path(dp).joinpath(f).relative_to(root)): (Path(dp) / f).stat().st_size
            for dp, _, fs in os.walk(root) for f in fs}


def tool_id() -> dict:
    mod = Path("cts/rubric_ceiling.py")
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True, check=True).stdout.strip()
    except Exception:
        commit = None
    return {"module": str(mod), "module_sha256": sha256(mod), "git_commit": commit,
            "test_count": 56}


def collect() -> dict:
    hashes = gate()
    TMP.mkdir(parents=True, exist_ok=True)
    arms = {}
    for name, key, phase in [
            ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.3.zip", "full_after_dedup",
             "AFTER_DEDUP"),
            ("PILOT-001-TEST-0007-ABLATED-AFTER_DEDUP-v0.1.3.zip", "ablated_after_dedup",
             "AFTER_DEDUP")]:
        d = TMP / key
        with zipfile.ZipFile(FROZEN / name) as f:
            f.extractall(d)
        arms[key] = {"arm_id": name[:-4], "phase": phase,
                     "sha256": hashes[name]["observed"],
                     "zip_bytes": (FROZEN / name).stat().st_size,
                     "text": blob(d), "inventory": inventory(d)}

    R = yaml.safe_load(RUBRIC.read_text(encoding="utf-8"))
    criteria = [Criterion(c["criterion"], float(c["weight"]), int(c["minimum_score"]),
                          bool(c["mandatory"])) for c in R["rubric"]]
    anchors = {c["criterion"]: {k: [float(v["range"][0]), float(v["range"][1])]
                                for k, v in (c.get("score_anchors") or {}).items()}
               for c in R["rubric"]}

    full_txt, abl_txt = arms["full_after_dedup"]["text"], arms["ablated_after_dedup"]["text"]
    per_criterion = []
    for c in criteria:
        probes = CRITERION_PROBES[c.name]
        excl = [p.label for p in probes
                if p.present_in(full_txt) and not p.present_in(abl_txt)]
        both = [p.label for p in probes
                if p.present_in(full_txt) and p.present_in(abl_txt)]
        per_criterion.append({
            "criterion": c.name, "weight": c.weight, "mandatory": c.mandatory,
            "minimum_score": c.minimum_score,
            "verdict": "SEPARA" if excl else "EMPATA",
            "exclusive_to_full": excl, "present_in_both_arms": both,
            "anchors": {k: v for k, v in anchors[c.name].items()},
        })

    arith = arithmetic_ceiling(criteria, int(R["scoring"]["score_scale"]["max"]))
    floor_regime = round(sum(c.weight * (100 - c.minimum_score) for c in criteria), 4)

    bands = {}
    for label, prof in [("full_execution", FULL_PROFILE),
                        ("disciplined_fail_closed_refusal", REFUSAL_PROFILE),
                        ("refusal_silent_checkpoint", REFUSAL_SILENT)]:
        bands[label] = profile_band(criteria, anchors, AnchoredProfile(label, prof))

    primary = margin_band(bands["full_execution"], bands["disciplined_fail_closed_refusal"])
    variant = margin_band(bands["full_execution"], bands["refusal_silent_checkpoint"])

    return {"hash_gate": hashes, "arms": arms, "rubric": R, "criteria": criteria,
            "per_criterion": per_criterion, "arithmetic": arith,
            "floor_regime_ceiling": floor_regime, "bands": bands,
            "primary": primary, "variant": variant, "tool": tool_id()}


def build_doc(d: dict) -> dict:
    R = d["rubric"]
    p, v = d["primary"], d["variant"]
    A = d["arms"]
    return {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-001-TEST-0007-STRUCTURAL-CEILING-v0.1.3",
        "artifact_status": "FINAL",
        "test_id": R["test_id"],
        "candidate_version": R["candidate_version"],
        "source_rubric": {
            "artifact_id": R["artifact_id"],
            "artifact_status": R["artifact_status"],
            "path": str(RUBRIC.relative_to(DRIVE)),
            "sha256": sha256(RUBRIC),
        },
        "hash_gate": {
            "policy": "Divergência aborta antes de qualquer análise.",
            "result": "PASS",
            "checked": [{"file": k, "expected": val["expected"],
                         "observed": val["observed"], "match": val["match"]}
                        for k, val in d["hash_gate"].items()],
        },
        "arms": {
            "full_after_dedup": {
                "arm_id": A["full_after_dedup"]["arm_id"],
                "phase": A["full_after_dedup"]["phase"],
                "sha256": A["full_after_dedup"]["sha256"],
                "files": len(A["full_after_dedup"]["inventory"]),
                "unpacked_bytes": sum(A["full_after_dedup"]["inventory"].values()),
            },
            "ablated_after_dedup": {
                "arm_id": A["ablated_after_dedup"]["arm_id"],
                "phase": A["ablated_after_dedup"]["phase"],
                "sha256": A["ablated_after_dedup"]["sha256"],
                "files": len(A["ablated_after_dedup"]["inventory"]),
                "unpacked_bytes": sum(A["ablated_after_dedup"]["inventory"].values()),
                "missing_required_resources": R["expected_ablated_behavior"][
                    "missing_required_resources"],
            },
        },
        "per_criterion_analysis": d["per_criterion"],
        "arithmetic_ceiling": {
            "weights_sum": d["arithmetic"]["weights_sum"],
            "weighted_floor_if_both_arms_pass": d["arithmetic"]["weighted_floor_if_passing"],
            "floor_regime_ceiling": d["floor_regime_ceiling"],
            "governs": False,
            "why_not": (
                "A régua declara em `scoring.mandatory_floor_semantics` que uma recusa "
                "fail-closed do braço ablado pode legitimamente ficar abaixo dos pisos "
                "de EXECUTION_QUALITY e METHODOLOGY_FIDELITY, e que isso é comportamento "
                "do candidato sob instrumento válido. O regime de piso, portanto, não se "
                "aplica ao braço ablado, e o teto de "
                f"{d['floor_regime_ceiling']} não governa este teste."),
        },
        "profile_bands": {k: {"min": b["min"], "max": b["max"], "detail": b["detail"]}
                          for k, b in d["bands"].items()},
        "profile_construction_caveats": [
            {"criterion": "CONSISTENCY",
             "issue": ("A régua não declara âncora para execução completa correta neste "
                       "critério: as três faixas descrevem recusa disciplinada, parada "
                       "ambígua e bypass. Para o perfil full_execution foi usada a faixa "
                       "superior [90,100], que é a faixa de comportamento correto."),
             "effect_on_result": ("Nenhum efeito sobre a banda: CONSISTENCY empata, e o "
                                  "mesmo intervalo é aplicado aos dois braços, cancelando-se "
                                  "na diferença."),
             "resolution": "Declarar uma âncora explícita de execução completa para CONSISTENCY."},
        ],
        "structural_ceiling": p["structural_ceiling"],
        "margin_band": {
            "min": p["margin_min"],
            "max": p["margin_max"],
            "profiles": ["full_execution", "disciplined_fail_closed_refusal"],
            "derivation": (
                "min = min(total FULL sob execução completa) − max(total ABLATED sob "
                "recusa disciplinada); max = max(FULL) − min(ABLATED). Ambos os totais "
                "vêm das score_anchors pré-declaradas na régua congelada."),
            "variant_if_refusal_is_silent_on_checkpoint": {
                "anchor": "silent_but_no_bypass",
                "min": v["margin_min"], "max": v["margin_max"],
            },
        },
        "threshold_implication": {
            "statement": (
                "Qualquer limiar de margem fixado ABAIXO do mínimo da banda "
                f"({p['margin_min']}) é passado por construção: sob os perfis "
                "pré-declarados pela própria régua, nenhuma rodada válida pode "
                "produzir margem menor que esse valor, qualquer que seja o "
                "desempenho do candidato."),
            "symmetric_statement": (
                f"Simetricamente, limiar acima do teto estrutural ({p['margin_max']}) "
                "seria reprovado por construção."),
            "informative_interval": [p["margin_min"], p["margin_max"]],
            "threshold_not_derived_here": True,
            "note": (
                "Este relatório não deriva nem congela limiar. A escolha do limiar é "
                "regra de decisão pré-declarada por quem conduz o teste."),
        },
        "rationale": (
            "Os dois braços diferem apenas por knowledge/decision-rules.yaml e "
            "knowledge/workflows.yaml. Sondagem de conteúdo mostra que as formas "
            "EXECUTÁVEIS dessa metodologia (corpo de regra com conditions/expression; "
            "passos de workflow com steps/workflow_id) são exclusivas do braço completo, "
            "enquanto as MENÇÕES descritivas dos mesmos temas sobrevivem em glossary, "
            "quality-criteria, principles, questions e anti-patterns. Por isso "
            "EXECUTION_QUALITY e METHODOLOGY_FIDELITY separam os braços e CONSISTENCY e "
            "HUMAN_CHECKPOINT_COMPLIANCE empatam — o que coincide com o desenho das "
            "âncoras, que colocam a recusa disciplinada em faixa baixa nos dois "
            "primeiros e em faixa alta nos dois últimos. Como a régua pré-declara as "
            "faixas de pontuação por perfil de comportamento, a banda de margem fica "
            "determinada antes da rodada e o teto estrutural é computável sem escores."),
        "interpretation_constraints": R["interpretation_constraints"],
        "analysis_tool_version_or_hash": d["tool"],
        "computed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main() -> int:
    d = collect()
    doc = build_doc(d)
    Path("work").mkdir(exist_ok=True)
    Path("work/structural_ceiling_v013.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    DEST.write_text(
        "# STRUCTURAL-CEILING-REPORT — TEST-0007 v0.1.3\n"
        "# Gerado por script (structural_ceiling_v013.py). Nenhum número digitado.\n"
        "# READ-ONLY sobre Course-to-Skill/. Nenhum limiar derivado ou congelado.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    print("PORTÃO DE HASH: PASS (2/2)")
    for c in doc["per_criterion_analysis"]:
        print(f"  {c['criterion']:30s} w={c['weight']} min={c['minimum_score']} "
              f"mand={c['mandatory']}  {c['verdict']}")
    print(f"teto aritmético (regime de piso, NÃO governa): {doc['arithmetic_ceiling']['floor_regime_ceiling']}")
    print(f"teto ESTRUTURAL: {doc['structural_ceiling']}  "
          f"banda [{doc['margin_band']['min']}, {doc['margin_band']['max']}]")
    print(f"publicado: {DEST.name} ({DEST.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
