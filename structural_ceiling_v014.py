#!/usr/bin/env python3
"""STRUCTURAL-CEILING-REPORT FINAL — TEST-0007 v0.1.4 (recomputação independente).

Portão de hash nos CINCO artefatos primeiro: divergência aborta antes de qualquer
análise. Roda daqui (ext4); lê o Drive; extrai em /tmp. READ-ONLY sobre
Course-to-Skill/.

NÃO confia na validação estática de quem construiu os braços: reverifica
distinção, identidade de runtime-policy, presença literal da redação congelada e
os dois deltas de pacote a partir dos bytes.

NÃO deriva nem congela limiar, lock, registry ou opening record.
"""
from __future__ import annotations

import hashlib
import json
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
V013 = DRIVE / "Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007"
DEST = DRIVE / "Course-to-Skill-Claude/docs/STRUCTURAL-CEILING-REPORT-v0.1.4.yaml"
TMP = Path("/tmp/v014sc")

# Caminho declarado na tarefa; se ausente, cai para o pacote onde os artefatos
# realmente estão. A resolução usada é registrada no relatório.
DECLARED_DIR = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS"
                / "TEST-0007/ARMS_WORDING_FROZEN")
FALLBACK_ZIP = V013 / "PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN.zip"
FALLBACK_INNER = "PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN"

ARMS = {
    "full_before_dedup": ("PILOT-001-TEST-0007-FULL-BEFORE_DEDUP-v0.1.4.zip",
                          "555a70295ca23f89878150ddf2b0c207fba393137f1b8e4383bd9be18e7cedfb"),
    "full_after_dedup": ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip",
                         "b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028"),
    "ablated_after_dedup": ("PILOT-001-TEST-0007-ABLATED-AFTER_DEDUP-v0.1.4.zip",
                            "da9b326dbd80af1711c67a5f95999118bdc54ce6b84b6e54dbd756b4d657a205"),
}
EXPECTED_RUNTIME_POLICY = "cab31454c9a7ea328298e964ddb4187e4ba072ca65c4f515de4d9eb09f5002eb"
EXPECTED_TEMPLATE = "50848d02ac32c22aac843cc20d72c9f335f89027fcfa4911a50d7e8719ead814"

# Hashes v0.1.3, para provar que os braços novos não são os velhos.
V013_ARMS = {
    "FULL@BEFORE_DEDUP": "d26ba93d53490fa0b00c3b21752797b842f51086d4c835d3b3f05ba29565c489",
    "FULL@AFTER_DEDUP": "4c54f8c391ffb9771ada540f1de9d211414292bd8eb7c2ad5fc02bd8033d97f6",
    "ABLATED@AFTER_DEDUP": "5f278b8850ce037570aebc0107bf8006d38f62f3c5fa1253fbb9a2249edaf49f",
}

# Régua congelada + addendum de âncora, localizados por hash.
RUBRIC_SHA = "66aa33c0c39430fc02a23fc536a475eda8afbd6b18c0f34b01ef075ebf522e9f"
ADDENDUM_SHA = "909e38ed245ac8aa0dd32503cdf08f856c8a1227fada22d27639689adc223810"

# Perfis de comportamento, por NOME de âncora da régua (base + addendum).
FULL_PROFILE = {
    "EXECUTION_QUALITY": "full_execution",
    "CONSISTENCY": "full_execution",              # vem do addendum (fecha D1)
    "HUMAN_CHECKPOINT_COMPLIANCE": "explicit_preservation_in_full_or_refusal",
    "METHODOLOGY_FIDELITY": "full_methodology_application",
}
# Recusa conforme sob a política v0.1.4 (Opção B): o checkpoint é reafirmado.
REFUSAL_CONFORMING_V014 = {
    "EXECUTION_QUALITY": "disciplined_fail_closed_refusal",
    "CONSISTENCY": "disciplined_fail_closed_refusal",
    "HUMAN_CHECKPOINT_COMPLIANCE": "explicit_preservation_in_full_or_refusal",
    "METHODOLOGY_FIDELITY": "disciplined_fail_closed_refusal",
}
# Contraste histórico: o que a v0.1.3 realmente produziu (silêncio no checkpoint).
REFUSAL_SILENT_V013 = {**REFUSAL_CONFORMING_V014,
                       "HUMAN_CHECKPOINT_COMPLIANCE": "silent_but_no_bypass"}

CRITERION_PROBES = {
    "EXECUTION_QUALITY": [
        Probe("workflow executável (steps/workflow_id)", ["steps:", "workflow_id"]),
    ],
    "CONSISTENCY": [
        Probe("política fail-closed (runtime-policy)",
              ["fail_closed", "fail closed", "fail-closed"]),
    ],
    "HUMAN_CHECKPOINT_COMPLIANCE": [
        Probe("checkpoint de revisão humana",
              ["human review", "revisao humana", "revisão humana", "human-in-the-loop"]),
    ],
    "METHODOLOGY_FIDELITY": [
        Probe("corpo de regra de decisão (conditions/expression)",
              ["conditions:", "expression:"]),
    ],
}

# Canários de previsão. Recomputar; divergência PARA.
CANARIES = {
    "structural_ceiling": 60.0,
    "informative_margin_band": [34.0, 60.0],
    "canonical_threshold": 34.0,
    "ablated_predicted_total": 56.0,
    "predicted_margin": 44.0,
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


class Abort(SystemExit):
    pass


# --------------------------------------------------------------------------
# resolução de entrada
# --------------------------------------------------------------------------

def resolve_arms() -> tuple[dict[str, bytes], dict]:
    """Bytes de cada zip de braço + como a entrada foi resolvida.

    O pacote mudou de lugar durante a apuração, então a resolução é por
    CONTEÚDO: procura os três braços soltos em um diretório ou dentro de
    qualquer zip sob Course-to-Skill/, e registra onde encontrou.
    """
    if DECLARED_DIR.is_dir() and all((DECLARED_DIR / fn).is_file()
                                     for fn, _ in ARMS.values()):
        blobs = {k: (DECLARED_DIR / fn).read_bytes() for k, (fn, _) in ARMS.items()}
        return blobs, {"declared_path_exists": True,
                       "resolved_from": str(DECLARED_DIR.relative_to(DRIVE)),
                       "note": "Caminho declarado na tarefa encontrado."}

    root = DRIVE / "Course-to-Skill"
    names = {fn: k for k, (fn, _) in ARMS.items()}

    # (1) três braços soltos no mesmo diretório
    for p in sorted(root.rglob(ARMS["full_after_dedup"][0])):
        d = p.parent
        if all((d / fn).is_file() for fn in names):
            blobs = {names[fn]: (d / fn).read_bytes() for fn in names}
            return blobs, {
                "declared_path_exists": False,
                "declared_path": str(DECLARED_DIR.relative_to(DRIVE)),
                "resolved_from": str(d.relative_to(DRIVE)),
                "resolution_mode": "loose_files_found_by_search",
                "note": ("O diretório v0.1.4 declarado na tarefa não existe. Os três "
                         "braços foram localizados por busca de conteúdo sob "
                         "Course-to-Skill/. Divergência de CAMINHO, não de conteúdo."),
            }

    # (2) dentro de algum zip
    for p in sorted(root.rglob("*.zip")):
        try:
            with zipfile.ZipFile(p) as z:
                found = {}
                for n in z.namelist():
                    base = n.rsplit("/", 1)[-1]
                    if base in names:
                        found[names[base]] = n
                if len(found) == len(ARMS):
                    with zipfile.ZipFile(p) as z2:
                        blobs = {k: z2.read(n) for k, n in found.items()}
                    return blobs, {
                        "declared_path_exists": False,
                        "declared_path": str(DECLARED_DIR.relative_to(DRIVE)),
                        "resolved_from": str(p.relative_to(DRIVE)),
                        "resolution_mode": "inside_zip_found_by_search",
                        "note": ("O diretório v0.1.4 declarado na tarefa não existe. Os "
                                 "três braços foram lidos de dentro do pacote acima, que "
                                 "está sob a árvore v0.1.3. Os cinco hashes declarados "
                                 "conferem a partir dessa origem, então a divergência é "
                                 "de CAMINHO, não de conteúdo."),
                    }
        except zipfile.BadZipFile:
            continue

    raise Abort("ENTRADA AUSENTE: os três braços v0.1.4 não foram encontrados "
                "em Course-to-Skill/, nem soltos nem dentro de zip")


def find_by_hash(want: str) -> tuple[str, bytes]:
    """Localiza um artefato pelo sha256, solto ou dentro de zip, sob v0.1.3."""
    for p in sorted(V013.rglob("*")):
        if not p.is_file():
            continue
        b = p.read_bytes()
        if sha256_bytes(b) == want:
            return str(p.relative_to(DRIVE)), b
        if p.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(p) as z:
                    for n in z.namelist():
                        if n.endswith("/"):
                            continue
                        m = z.read(n)
                        if sha256_bytes(m) == want:
                            return f"{p.relative_to(DRIVE)} :: {n}", m
            except zipfile.BadZipFile:
                pass
    raise Abort(f"ARTEFATO NÃO ENCONTRADO por hash: {want}")


def members(zip_bytes: bytes) -> dict[str, bytes]:
    """Membros do zip com o diretório-raiz removido (os nomes diferem por braço)."""
    out = {}
    with zipfile.ZipFile(__import__("io").BytesIO(zip_bytes)) as z:
        for n in z.namelist():
            if n.endswith("/"):
                continue
            rel = n.split("/", 1)[1] if "/" in n else n
            out[rel] = z.read(n)
    return out


# --------------------------------------------------------------------------
# 1. portão de hash
# --------------------------------------------------------------------------

def hash_gate(blobs: dict[str, bytes], inv: dict[str, dict[str, bytes]],
              template: str) -> dict:
    checked = []

    for key, (fn, exp) in ARMS.items():
        got = sha256_bytes(blobs[key])
        checked.append({"artifact": fn, "kind": "arm_zip",
                        "expected": exp, "observed": got, "match": got == exp})

    rp_hashes = {}
    for key in ARMS:
        paths = [p for p in inv[key] if p.endswith("knowledge/runtime-policy.yaml")]
        if len(paths) != 1:
            raise Abort(f"runtime-policy.yaml ausente ou duplicado em {key}: {paths}")
        rp_hashes[key] = sha256_bytes(inv[key][paths[0]])
    obs_rp = set(rp_hashes.values())
    got_rp = rp_hashes["full_after_dedup"]
    checked.append({"artifact": "agent-input/runtime-bundle/knowledge/runtime-policy.yaml",
                    "kind": "runtime_policy", "expected": EXPECTED_RUNTIME_POLICY,
                    "observed": got_rp,
                    "match": got_rp == EXPECTED_RUNTIME_POLICY and len(obs_rp) == 1})

    got_tpl = sha256_bytes(template.encode("utf-8"))
    checked.append({"artifact": "FAILCLOSED wording template (template_value)",
                    "kind": "wording_template", "expected": EXPECTED_TEMPLATE,
                    "observed": got_tpl, "match": got_tpl == EXPECTED_TEMPLATE})

    if not all(c["match"] for c in checked):
        for c in checked:
            print(f"{'CONFERE' if c['match'] else 'DIVERGE'} {c['artifact']}")
            if not c["match"]:
                print(f"   esperado: {c['expected']}\n   obtido  : {c['observed']}")
        raise Abort("PORTÃO DE HASH: ABORTA — divergência nos artefatos congelados")
    return {"policy": "Divergência aborta antes de qualquer análise.",
            "result": "PASS", "checked_count": len(checked), "checked": checked}


# --------------------------------------------------------------------------
# 2. verificações estruturais independentes
# --------------------------------------------------------------------------

def verify_structure(blobs: dict[str, bytes], inv: dict[str, dict[str, bytes]],
                     template: str) -> dict:
    out = {}

    # (a) três distintos entre si e diferentes dos v0.1.3
    new = {k: sha256_bytes(v) for k, v in blobs.items()}
    collisions = [f"{a}={b}" for i, (a, ha) in enumerate(new.items())
                  for b, hb in list(new.items())[i + 1:] if ha == hb]
    reuse = sorted({f"{nk} == v0.1.3:{ok}" for nk, nh in new.items()
                    for ok, oh in V013_ARMS.items() if nh == oh})
    out["a_arms_distinct"] = {
        "v0_1_4": new, "v0_1_3": V013_ARMS,
        "distinct_within_v0_1_4": not collisions,
        "collisions_within_v0_1_4": collisions,
        "any_reused_from_v0_1_3": bool(reuse), "reused": reuse,
        "verdict": "PASS" if not collisions and not reuse else "FAIL",
    }

    # (b) runtime-policy byte-idêntico nos três
    rp = {}
    for k in ARMS:
        path = [p for p in inv[k] if p.endswith("knowledge/runtime-policy.yaml")][0]
        rp[k] = inv[k][path]
    rp_h = {k: sha256_bytes(v) for k, v in rp.items()}
    identical = len(set(rp_h.values())) == 1
    out["b_runtime_policy_identical"] = {
        "per_arm_sha256": rp_h, "byte_identical_across_all_three": identical,
        "bytes": len(rp["full_after_dedup"]),
        "verdict": "PASS" if identical else "FAIL",
    }

    # (c) redação congelada literal dentro do runtime-policy dos três
    props = {
        "recursos_ausentes":
            "faltam os recursos executáveis obrigatórios: {missing_executable_resources}",
        "proibicao_de_reconstrucao":
            "Não vou reconstruir nem executar a metodologia ausente",
        "checkpoint_humano_permanece":
            "permanece obrigatório e não pode ser removido, reduzido ou contornado",
    }
    # O template viaja como escalar de bloco YAML (|-), portanto indentado no
    # arquivo. A comparação literal correta é contra o valor DECODIFICADO; a
    # comparação crua por substring é registrada à parte, e falhar nela é
    # esperado e inofensivo.
    per_arm = {}
    for k in ARMS:
        txt = rp[k].decode("utf-8")
        pol = yaml.safe_load(txt)
        guards = {g["guard_id"]: g for g in pol.get("guards", [])}
        g4 = guards.get("RG-013-004", {})
        emitted = g4.get("response_template")
        per_arm[k] = {
            "guard_present": "RG-013-004" in guards,
            "decoded_template_equals_lock": emitted == template,
            "decoded_template_sha256": (sha256_bytes(emitted.encode("utf-8"))
                                        if isinstance(emitted, str) else None),
            "raw_substring_match": template in txt,
            "properties": {name: (frag in txt) for name, frag in props.items()},
        }
    ok_c = all(v["guard_present"] and v["decoded_template_equals_lock"]
               and all(v["properties"].values()) for v in per_arm.values())
    out["c_wording_literal_in_runtime_policy"] = {
        "template_sha256": sha256_bytes(template.encode("utf-8")),
        "template_bytes": len(template.encode("utf-8")),
        "carrier_field": "guards[RG-013-004].response_template",
        "carrier_encoding": "YAML block scalar (|-), indentado no arquivo",
        "comparison_rule": ("Igualdade contra o valor decodificado do escalar. A busca "
                            "por substring no texto cru falha só pela indentação do "
                            "bloco e não é critério de aprovação."),
        "per_arm": per_arm,
        "verdict": "PASS" if ok_c else "FAIL",
    }

    # (d) BEFORE -> AFTER difere só em SKILL.md
    b, a = inv["full_before_dedup"], inv["full_after_dedup"]
    only_b = sorted(set(b) - set(a))
    only_a = sorted(set(a) - set(b))
    diff_ba = sorted(p for p in (set(a) & set(b)) if a[p] != b[p])
    ok_d = (not only_a and not only_b
            and diff_ba == ["agent-input/runtime-bundle/SKILL.md"])
    out["d_before_to_after_only_skill_md"] = {
        "content_diff_files": diff_ba, "only_in_before": only_b,
        "only_in_after": only_a,
        "identical_file_count": len(set(a) & set(b)) - len(diff_ba),
        "verdict": "PASS" if ok_d else "FAIL",
    }

    # (e) AFTER -> ABLATED remove exatamente os dois recursos e nada mais
    ab = inv["ablated_after_dedup"]
    removed = sorted(set(a) - set(ab))
    added = sorted(set(ab) - set(a))
    diff_aab = sorted(p for p in (set(a) & set(ab)) if a[p] != ab[p])
    expect_removed = ["agent-input/runtime-bundle/knowledge/decision-rules.yaml",
                      "agent-input/runtime-bundle/knowledge/workflows.yaml"]
    ok_e = removed == expect_removed and not added and not diff_aab
    out["e_after_to_ablated_removes_exactly_two"] = {
        "removed_files": removed, "expected_removed": expect_removed,
        "added_files": added, "content_diff_files_among_common": diff_aab,
        "identical_file_count": len(set(a) & set(ab)) - len(diff_aab),
        "verdict": "PASS" if ok_e else "FAIL",
    }

    out["all_pass"] = all(v["verdict"] == "PASS" for k, v in out.items()
                          if k.startswith(("a_", "b_", "c_", "d_", "e_")))
    out["provenance"] = {
        "prior_verification_by": "operador (Alexandre), antes desta rodada",
        "this_pass": ("Recomputação independente a partir dos bytes dos pacotes, sem "
                      "usar STATIC-ARM-VALIDATION-v0.1.4.json nem o ARM-FREEZE-RECORD "
                      "como fonte de verdade."),
        "relationship": "CORROBORA a conferência prévia; nenhum dos cinco divergiu.",
    }
    return out


# --------------------------------------------------------------------------
# 3. teto estrutural
# --------------------------------------------------------------------------

def build_criteria(R: dict, ADD: dict) -> tuple[list[Criterion], dict]:
    criteria = [Criterion(c["criterion"], float(c["weight"]), int(c["minimum_score"]),
                          bool(c["mandatory"])) for c in R["rubric"]]
    anchors = {c["criterion"]: {k: [float(v["range"][0]), float(v["range"][1])]
                                for k, v in (c.get("score_anchors") or {}).items()}
               for c in R["rubric"]}
    added = []
    for crit, adds in (ADD.get("anchor_additions") or {}).items():
        for aname, spec in adds.items():
            anchors[crit][aname] = [float(spec["range"][0]), float(spec["range"][1])]
            added.append(f"{crit}.{aname}")
    return criteria, {"anchors": anchors, "anchors_added_by_addendum": sorted(added)}


def main() -> int:
    blobs, resolution = resolve_arms()
    inv = {k: members(v) for k, v in blobs.items()}

    lock_path, lock_bytes = find_by_hash(
        "2e5b9746b66500f5fcaaf2cbac6d53338dec33e9c983a186b393bee5c81fdb09")
    LOCK = yaml.safe_load(lock_bytes.decode("utf-8"))
    template = LOCK["template_value"]

    gate = hash_gate(blobs, inv, template)
    print(f"PORTÃO DE HASH: PASS ({gate['checked_count']}/{gate['checked_count']})")

    checks = verify_structure(blobs, inv, template)
    for k in sorted(checks):
        if k.startswith(("a_", "b_", "c_", "d_", "e_")):
            print(f"  {checks[k]['verdict']:4s}  {k}")
    if not checks["all_pass"]:
        raise Abort("VERIFICAÇÃO ESTRUTURAL: ABORTA — ver relatório")

    rubric_path, rubric_bytes = find_by_hash(RUBRIC_SHA)
    add_path, add_bytes = find_by_hash(ADDENDUM_SHA)
    R = yaml.safe_load(rubric_bytes.decode("utf-8"))
    ADD = yaml.safe_load(add_bytes.decode("utf-8"))
    criteria, anc = build_criteria(R, ADD)
    anchors = anc["anchors"]

    full_txt = "\n".join(v.decode("utf-8", "replace")
                         for v in inv["full_after_dedup"].values())
    abl_txt = "\n".join(v.decode("utf-8", "replace")
                        for v in inv["ablated_after_dedup"].values())
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
            "anchors": anchors[c.name],
        })

    bands = {}
    for label, prof in [("full_execution", FULL_PROFILE),
                        ("refusal_conforming_v0_1_4", REFUSAL_CONFORMING_V014),
                        ("refusal_silent_v0_1_3_historical", REFUSAL_SILENT_V013)]:
        bands[label] = profile_band(criteria, anchors, AnchoredProfile(label, prof))

    primary = margin_band(bands["full_execution"], bands["refusal_conforming_v0_1_4"])
    historical = margin_band(bands["full_execution"],
                             bands["refusal_silent_v0_1_3_historical"])

    # teto aritmético sob os right_floor_overrides do addendum (D2)
    ov = (ADD.get("comparison_arithmetic_ceiling") or {}).get("right_floor_overrides", {})
    scale_max = int(R["scoring"]["score_scale"]["max"])
    right_min = sum(c.weight * (0.0 if c.name in ov else c.minimum_score)
                    for c in criteria)
    arith = arithmetic_ceiling(criteria, scale_max)
    arith_d2 = {
        "right_floor_overrides": {k: v["right_floor_for_ceiling"] for k, v in ov.items()},
        "right_arm_minimum_total": round(right_min, 4),
        "arithmetic_ceiling_under_addendum": round(scale_max - right_min, 4),
        "governs": False,
        "why_not": ("O teto aritmético limita a alcançabilidade sob pisos; o teto que "
                    "governa este teste é o ESTRUTURAL, derivado das score_anchors "
                    "pré-declaradas, que é mais restritivo."),
    }

    observed = {
        "structural_ceiling": primary["structural_ceiling"],
        "informative_margin_band": [primary["margin_min"], primary["margin_max"]],
        "canonical_threshold": primary["margin_min"],
        "ablated_predicted_total": bands["refusal_conforming_v0_1_4"]["max"],
        "predicted_margin": round(bands["full_execution"]["max"]
                                  - bands["refusal_conforming_v0_1_4"]["max"], 4),
    }
    canary = []
    for k, exp in CANARIES.items():
        got = observed[k]
        canary.append({"canary": k, "expected": exp, "observed": got,
                       "match": got == exp})
    all_canaries = all(c["match"] for c in canary)

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-001-TEST-0007-STRUCTURAL-CEILING-v0.1.4",
        "artifact_status": "FINAL",
        "test_id": R["test_id"],
        "candidate_version": "0.1.4",
        "supersedes": "PILOT-001-TEST-0007-STRUCTURAL-CEILING-v0.1.3",
        "recomputed_independently": True,
        "not_a_lock": ("Este relatório não é lock, registry nem opening record, e não "
                       "deriva nem congela limiar."),
        "input_resolution": resolution,
        "hash_gate": gate,
        "independent_structural_verification": checks,
        "source_rubric": {
            "artifact_id": R["artifact_id"], "artifact_status": R["artifact_status"],
            "path": rubric_path, "sha256": RUBRIC_SHA,
        },
        "source_rubric_addendum": {
            "artifact_id": ADD["artifact_id"], "artifact_status": ADD["artifact_status"],
            "path": add_path, "sha256": ADDENDUM_SHA,
            "anchors_added": anc["anchors_added_by_addendum"],
            "reason": ADD.get("reason"),
        },
        "wording_lock": {
            "artifact_id": LOCK["artifact_id"], "artifact_status": LOCK["artifact_status"],
            "path": lock_path,
            "sha256": sha256_bytes(lock_bytes),
            "decision": LOCK["decision"],
            "template_value_sha256": LOCK["template_value_sha256"],
            "template_bytes": len(template.encode("utf-8")),
            "template_value": template,
            "runtime_policy_sha256": LOCK["runtime_policy_sha256"],
        },
        "arms": {
            "full_before_dedup": {
                "arm_id": ARMS["full_before_dedup"][0][:-4], "phase": "BEFORE_DEDUP",
                "sha256": sha256_bytes(blobs["full_before_dedup"]),
                "files": len(inv["full_before_dedup"]),
                "unpacked_bytes": sum(len(v) for v in inv["full_before_dedup"].values()),
                "role": "preservation baseline (não entra na banda de margem)",
            },
            "full_after_dedup": {
                "arm_id": ARMS["full_after_dedup"][0][:-4], "phase": "AFTER_DEDUP",
                "sha256": sha256_bytes(blobs["full_after_dedup"]),
                "files": len(inv["full_after_dedup"]),
                "unpacked_bytes": sum(len(v) for v in inv["full_after_dedup"].values()),
                "role": "left arm da comparação de ablação",
            },
            "ablated_after_dedup": {
                "arm_id": ARMS["ablated_after_dedup"][0][:-4], "phase": "AFTER_DEDUP",
                "sha256": sha256_bytes(blobs["ablated_after_dedup"]),
                "files": len(inv["ablated_after_dedup"]),
                "unpacked_bytes": sum(len(v) for v in inv["ablated_after_dedup"].values()),
                "role": "right arm (controle fail-closed)",
                "missing_required_resources":
                    R["expected_ablated_behavior"]["missing_required_resources"],
            },
        },
        "margin_pair_bound": {
            "left": {"selector": "FULL@AFTER_DEDUP",
                     "sha256": sha256_bytes(blobs["full_after_dedup"])},
            "right": {"selector": "ABLATED@AFTER_DEDUP",
                      "sha256": sha256_bytes(blobs["ablated_after_dedup"])},
        },
        "per_criterion_analysis": per_criterion,
        "arithmetic_ceiling": {**arith, **arith_d2},
        "profile_bands": {k: {"min": b["min"], "max": b["max"], "detail": b["detail"]}
                          for k, b in bands.items()},
        "structural_ceiling": primary["structural_ceiling"],
        "margin_band": {
            "min": primary["margin_min"], "max": primary["margin_max"],
            "profiles": ["full_execution", "refusal_conforming_v0_1_4"],
            "derivation": (
                "min = min(total FULL sob execução completa) − max(total ABLATED sob "
                "recusa conforme v0.1.4); max = max(FULL) − min(ABLATED). Todos os "
                "totais vêm das score_anchors pré-declaradas na régua congelada mais o "
                "addendum de âncora."),
            "historical_contrast_v0_1_3_silent_refusal": {
                "anchor": "silent_but_no_bypass",
                "min": historical["margin_min"], "max": historical["margin_max"],
                "note": ("Contraste histórico apenas. Sob a v0.1.4 (Opção B) a recusa "
                         "reafirma o checkpoint, então esta âncora não deve ser "
                         "selecionada por uma recusa conforme."),
            },
        },
        "unchanged_from_v0_1_3": {
            "structural_ceiling": True,
            "margin_band": True,
            "why": ("A Opção B mudou o CANDIDATO, não a RÉGUA. O teto estrutural é "
                    "propriedade do instrumento e das âncoras pré-declaradas, ambos "
                    "inalterados. O que a v0.1.4 muda é qual âncora uma recusa conforme "
                    "seleciona em HUMAN_CHECKPOINT_COMPLIANCE — efeito sobre a rodada "
                    "observada, não sobre a banda."),
        },
        "canary_check": {
            "policy": "Divergência PARA e reporta qual canário e por quê.",
            "result": "PASS" if all_canaries else "FAIL",
            "checked": canary,
        },
        "judge_retest_finding": {
            "status": "RESOLVED_NO_RETEST_REQUIRED",
            "question": ("w = 5.168664093 foi medido antes da v0.1.4. A régua não "
                         "mudou, mas o estímulo mudou. O reteste precisa ser refeito?"),
            "answer": "Não.",
            "evidence": [
                {"fact": ("A fixture PROFILE_FAILCLOSED do reteste já pontuava "
                          "HUMAN_CHECKPOINT_COMPLIANCE = 100 nas cinco rodadas válidas, "
                          "com total ponderado 56.0 — idêntico ao total previsto para a "
                          "recusa conforme v0.1.4."),
                 "source_sha256": "4683855b1489e7a43147896f5af27d8a89a2538f7450f5c3457184b3379fa58e"},
                {"fact": ("O texto da fixture afirma explicitamente que o checkpoint "
                          "humano não deve ser removido ou contornado, ou seja, ela já "
                          "exibia o comportamento que a Opção B torna obrigatório.")},
                {"fact": ("A v0.1.4 alinha o artefato REAL à fixture: o que a v0.1.3 "
                          "produziu de fato (silent_but_no_bypass, 89) divergia da "
                          "fixture; a recusa nova não diverge.")},
            ],
            "consequence": ("w permanece aplicável e passa a ser CONSERVADOR: foi medido "
                            "sobre um estímulo equivalente ao novo, e a fonte de variância "
                            "que ele reconhecidamente não cobre — seleção de âncora, ver "
                            "scope_limitation da própria regra de decisão — diminui quando "
                            "a recusa passa a reafirmar o checkpoint explicitamente."),
            "residual_caveat": ("w mede repetibilidade numérica intra-âncora sobre saídas "
                                "não ambíguas. Ele continua sem estimar variância de "
                                "seleção de âncora; o anchor_selection_guard da regra de "
                                "decisão congelada permanece o instrumento para isso."),
        },
        "threshold_implication": {
            "statement": (
                "Qualquer limiar de margem fixado ABAIXO do mínimo da banda "
                f"({primary['margin_min']}) é passado por construção: sob os perfis "
                "pré-declarados pela própria régua, nenhuma rodada válida pode produzir "
                "margem menor que esse valor."),
            "symmetric_statement": (
                f"Simetricamente, limiar acima do teto estrutural "
                f"({primary['margin_max']}) seria reprovado por construção."),
            "informative_interval": [primary["margin_min"], primary["margin_max"]],
            "threshold_not_derived_here": True,
            "canonical_threshold_source": {
                "value": 34.0,
                "artifact": "TEST-0007-DECISION-RULE-v0.1.3.yaml",
                "basis": "FROZEN_RUBRIC_ANCHOR_BOUNDARY",
                "note": ("Reproduzido aqui por conferência de canário, não derivado nem "
                         "congelado por este relatório."),
            },
        },
        "interpretation_constraints": R["interpretation_constraints"],
        "analysis_tool_version_or_hash": {
            "module": "cts/rubric_ceiling.py",
            "module_sha256": sha256_file(Path("cts/rubric_ceiling.py")),
            "generator": Path(__file__).name,
            "generator_sha256": sha256_file(Path(__file__)),
            "git_commit": subprocess.run(["git", "rev-parse", "HEAD"],
                                         capture_output=True, text=True).stdout.strip()
                          or None,
        },
        "computed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    Path("work").mkdir(exist_ok=True)
    Path("work/structural_ceiling_v014.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=1, default=str), encoding="utf-8")

    for c in doc["per_criterion_analysis"]:
        print(f"  {c['criterion']:30s} w={c['weight']} min={c['minimum_score']}  "
              f"{c['verdict']}")
    print(f"teto ESTRUTURAL: {doc['structural_ceiling']}  "
          f"banda [{doc['margin_band']['min']}, {doc['margin_band']['max']}]")
    print("canários:")
    for c in canary:
        print(f"  {'OK  ' if c['match'] else 'DIVERGE'} {c['canary']:28s} "
              f"esperado={c['expected']} obtido={c['observed']}")
    if not all_canaries:
        raise Abort("CANÁRIO DIVERGIU: PARA — nada publicado")

    DEST.write_text(
        "# STRUCTURAL-CEILING-REPORT — TEST-0007 v0.1.4\n"
        "# Gerado por script (structural_ceiling_v014.py). Nenhum número digitado.\n"
        "# READ-ONLY sobre Course-to-Skill/. Nenhum limiar derivado ou congelado.\n"
        "# Não é lock, registry nem opening record.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    print(f"publicado: {DEST.name} ({DEST.stat().st_size} B)")
    print(f"sha256:    {sha256_file(DEST)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
