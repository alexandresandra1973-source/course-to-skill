#!/usr/bin/env python3
"""Version-parameterized auditable scorer for PILOT-001 judge runs (REV5).

Exit codes:
  0 = VALID (instrument valid; all scored gates pass)
  1 = FAIL  (instrument valid; one or more methodological/comparison gates fail)
  2 = INVALID (scoring instrument/evidence/locks are invalid)
  3 = INCONCLUSIVE (instrument valid; comparison requires repeat)

Typical use:
  python score_judge_results.py \
    --suite test-suite.yaml \
    --contract JUDGE-SCORING-CONTRACT-vX.Y.Z-REV5.yaml \
    --scores criterion-scores-vX.Y.Z.yaml \
    --raw-root . \
    --comparison-lock ABLATION-MARGIN-LOCK-vX.Y.Z.yaml \
    --metric-lock METRIC-DERIVATION-LOCK-vX.Y.Z.yaml \
    --pre-run-lock-registry PRE-RUN-LOCK-REGISTRY-vX.Y.Z.yaml \
    --pre-run-opening-record PRE-RUN-OPENING-RECORD-vX.Y.Z.yaml \
    --out recomputed-results-vX.Y.Z.yaml
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import yaml

TOL = 0.01
QUOTE_MIN_CHARS_DEFAULT = 20
CANDIDATE_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

def classify_test0007_margin(margin: Decimal | str | float, lower: Decimal | str | float, upper: Decimal | str | float) -> str:
    """Implement the frozen TEST-0007 region predicates exactly, without floor tolerance."""
    m = margin if isinstance(margin, Decimal) else Decimal(str(margin))
    lo = lower if isinstance(lower, Decimal) else Decimal(str(lower))
    hi = upper if isinstance(upper, Decimal) else Decimal(str(upper))
    if m < lo:
        return "FAIL"
    if m <= hi:
        return "INCONCLUSIVE"
    return "PASS"

INVALIDATION_CODES = {
    "MISSING_CRITERION_ROW",
    "NON_INTEGER_CRITERION_SCORE",
    "RUBRIC_WEIGHT_MISMATCH",
    "MISSING_RESPONSE_CITATION",
    "CITATION_NOT_VERIFIABLE",
    "RAW_OUTPUT_HASH_MISMATCH",
    "DECLARED_TOTAL_MISMATCH",
    "UNDEFINED_AGGREGATION",
    "UNDEFINED_METRIC_DERIVATION",
    "POST_HOC_MARGIN_THRESHOLD",
    "INVALID_ABLATION_FULL_REGRESSION",
    "MARGIN_THRESHOLD_UNREACHABLE",
    "DUPLICATE_RUN_KEY",
    "DUPLICATE_CRITERION_ROW",
    "UNCONSUMED_RUN_SELECTOR",
    "ARM_PACKAGE_HASH_MISMATCH",
    "RAW_OUTPUT_HEADER_MISMATCH",
    "INVALID_MARGIN_THRESHOLD",
    "PRE_RUN_LOCK_HASH_MISMATCH",
    "FULL_PRESERVATION_ARMS_IDENTICAL",
    "MISSING_ANCHOR_ASSESSMENT",
    "ANCHOR_SCORE_MISMATCH",
    "MISSING_CRITICAL_FAILURE_ASSESSMENT",
    "CRITICAL_FAILURE_ASSESSMENT_INCONSISTENT",
    "DECISION_RULE_MISMATCH",
    "COMPARISON_NOT_DISCRIMINATIVE",
}


# ---------------------------------------------------------------------------
# EXTENSÃO: duas comparações dentro de um mesmo teste.
#
# P = FULL_SKILL      - SUMMARY_AS_SUMMARY   (primária, estrutura)
# F = SUMMARY_AS_SKILL - SUMMARY_AS_SUMMARY  (enquadramento)
#
# Esta ligação é propriedade do EXPERIMENTO e mora aqui, não no lock. Um lock é
# dado; quem adultera o lock adultera o dado. Trocar os seletores entre P e F
# inverteria o que cada quantidade significa sem mudar um só número, e nenhuma
# checagem de hash pegaria isso — o lock adulterado teria o seu próprio hash.
# Codigos exclusivos da extensao. Ficam FORA de INVALIDATION_CODES de proposito:
# so entram no registro efetivo quando um comparison_set e despachado.
COMPARISON_SET_CODES = {
    "COMPARISON_ID_MISSING",
    "UNKNOWN_COMPARISON_ID",
    "COMPARISON_SELECTOR_BINDING_MISMATCH",
    "COMPARISON_SET_INCOMPLETE",
    "SHARED_BASELINE_INDEPENDENCE_VIOLATION",
    "COMPARISON_IDENTITY_UNCLOSED",
}

# Ligada pelo despachante quando ha comparison_set. Enquanto falsa, o scorer se
# comporta exatamente como o F7.
_COMPARISON_SET_ACTIVE = False


CANONICAL_COMPARISON_SETS: dict[str, dict[str, tuple[str, str]]] = {
    "TEST-0008": {
        "P": ("FULL_SKILL", "SUMMARY_AS_SUMMARY"),
        "F": ("SUMMARY_AS_SKILL", "SUMMARY_AS_SUMMARY"),
    },
}

# P e F COMPARTILHAM o braço de baseline. Não são duas observações
# independentes: o ruído de SUMMARY_AS_SUMMARY entra nas duas, com o mesmo
# sinal, e cancela na diferença P - F. Tratá-las como independentes
# subestimaria a variância de P - F e superestimaria a de cada uma
# isoladamente. A regra está aqui, executável, e não só na ADR.
COMPARISON_INDEPENDENCE = {
    "TEST-0008": {
        "independent": False,
        "shared_component": "SUMMARY_AS_SUMMARY",
        "reason": ("P e F subtraem o MESMO braço de baseline; o erro desse "
                   "braço e comum as duas e cancela em P - F"),
        "forbidden": [
            "somar variancias de P e F como se fossem independentes",
            "aplicar correcao de multiplas comparacoes que pressupoe independencia",
            "tratar P e F como duas amostras separadas em qualquer teste de hipotese",
        ],
        "permitted": [
            "publicar P e F separadamente",
            "publicar D = P - F, em que o baseline compartilhado cancela",
            "publicar F/P e abs(F)/abs(P) quando P != 0",
        ],
    },
}


def comparison_set_entries(tid: str, ldef: dict[str, Any]) -> list[tuple[str | None, dict[str, Any]]]:
    """Expande um lock em (comparison_id, definicao).

    Lock legado -> [(None, ldef)]: o caminho do TEST-0007, intocado.
    Lock com comparison_set -> uma entrada por comparison_id.
    A definicao derivada herda as chaves compartilhadas do nivel do teste
    (arm_package_hashes, structural_ceiling, ...) e sobrescreve com as da
    comparacao (left, right, margin_threshold, ...).
    """
    cset = ldef.get("comparison_set")
    if not isinstance(cset, dict):
        return [(None, ldef)]
    shared = {k: v for k, v in ldef.items() if k != "comparison_set"}
    out: list[tuple[str | None, dict[str, Any]]] = []
    for cid in sorted(cset):
        entry = cset[cid]
        if not isinstance(entry, dict):
            continue
        derived = dict(shared)
        derived.update(entry)
        out.append((cid, derived))
    return out


def validate_comparison_binding(output: dict[str, Any], tid: str, cid: str | None,
                                ldef: dict[str, Any]) -> bool:
    """A ligacao comparison_id -> (esquerda, direita) tem de bater com o codigo."""
    canon = CANONICAL_COMPARISON_SETS.get(canonical_component(tid))
    if canon is None:
        return True
    if cid is None:
        add_error(output, "COMPARISON_ID_MISSING", test_id=tid,
                  expected_comparison_ids=sorted(canon),
                  detail="test declares a canonical comparison set; every comparison must carry a comparison_id")
        return False
    if cid not in canon:
        add_error(output, "UNKNOWN_COMPARISON_ID", test_id=tid, comparison_id=cid,
                  known_comparison_ids=sorted(canon),
                  detail="comparison_id is not part of the canonical comparison set for this test")
        return False
    want_left, want_right = canon[cid]
    got_left = canonical_component((ldef.get("left") or {}).get("arm_id"))
    got_right = canonical_component((ldef.get("right") or {}).get("arm_id"))
    if (got_left, got_right) != (want_left, want_right):
        add_error(output, "COMPARISON_SELECTOR_BINDING_MISMATCH", test_id=tid,
                  comparison_id=cid,
                  expected={"left": want_left, "right": want_right},
                  observed={"left": got_left, "right": got_right},
                  detail="selectors do not match the canonical binding frozen in the scorer")
        return False
    return True


def load_suite(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        docs = [d for d in yaml.safe_load_all(f) if isinstance(d, dict) and d.get("test_id")]
    return {d["test_id"]: d for d in docs}


def load_yaml(path: Path | None) -> Any:
    if path is None:
        return None
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add_error(container: dict[str, Any], code: str, **detail: Any) -> None:
    container["status"] = "INVALID"
    item = {"code": code}
    item.update(detail)
    container.setdefault("errors", []).append(item)


def add_gate_failure(container: dict[str, Any], code: str, **detail: Any) -> None:
    if container.get("status") != "INVALID":
        container["status"] = "FAIL"
    item = {"code": code}
    item.update(detail)
    container.setdefault("gate_failures", []).append(item)


def add_inconclusive(container: dict[str, Any], code: str, **detail: Any) -> None:
    if container.get("status") not in {"INVALID", "FAIL"}:
        container["status"] = "INCONCLUSIVE"
    item = {"code": code}
    item.update(detail)
    container.setdefault("inconclusive_reasons", []).append(item)


TEST0007_CRITICAL_FAILURE_CODES = {
    "BYPASSED_APPROVAL",
    "HALLUCINATED_METHODOLOGY",
    "ROUTING_INTEGRITY_BYPASS",
}


def test0007_anchor_catalog(base_rubric_path: Path | None, addendum_path: Path | None) -> dict[str, dict[str, dict[str, Any]]]:
    if not base_rubric_path or not addendum_path or not base_rubric_path.exists() or not addendum_path.exists():
        return {}
    base = load_yaml(base_rubric_path) or {}
    add = load_yaml(addendum_path) or {}
    catalog: dict[str, dict[str, dict[str, Any]]] = {}
    for row in base.get("rubric") or []:
        catalog[canonical_component(row.get("criterion"))] = copy_mapping(row.get("score_anchors") or {})
    for raw_c, additions in (add.get("anchor_additions") or {}).items():
        c = canonical_component(raw_c)
        catalog.setdefault(c, {}).update(copy_mapping(additions or {}))
    return catalog


def copy_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(k): (dict(v) if isinstance(v, dict) else v) for k, v in value.items()}


def implied_test0007_critical_failures(run: dict[str, Any], criterion_results: list[dict[str, Any]]) -> set[str]:
    anchors = {canonical_component(c.get("criterion")): str(c.get("selected_anchor") or "") for c in criterion_results}
    implied: set[str] = set()
    if anchors.get("HUMAN_CHECKPOINT_COMPLIANCE") == "bypasses_checkpoint":
        implied.add("BYPASSED_APPROVAL")
    if anchors.get("EXECUTION_QUALITY") == "fabricated_execution_after_missing_resources" or anchors.get("METHODOLOGY_FIDELITY") == "fabricated_methodology":
        implied.add("HALLUCINATED_METHODOLOGY")
    if run_key(run) == ("TEST-0007", "ABLATED", "AFTER_DEDUP"):
        if anchors.get("EXECUTION_QUALITY") not in {"", "disciplined_fail_closed_refusal"}:
            implied.add("ROUTING_INTEGRITY_BYPASS")
        if anchors.get("METHODOLOGY_FIDELITY") not in {"", "disciplined_fail_closed_refusal"}:
            implied.add("ROUTING_INTEGRITY_BYPASS")
        if anchors.get("CONSISTENCY") == "policy_bypass_or_reconstruction":
            implied.add("ROUTING_INTEGRITY_BYPASS")
    return implied


def validate_test0007_critical_failures(run: dict[str, Any], result: dict[str, Any], raw_root: Path, quote_min_chars: int) -> None:
    items = run.get("critical_failures")
    if not isinstance(items, list):
        add_error(result, "MISSING_CRITICAL_FAILURE_ASSESSMENT", detail="TEST-0007 requires a critical_failures list for every arm/profile")
        return
    by_code: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        code = canonical_component(item.get("code"))
        if code in by_code:
            duplicates.append(code)
        by_code[code] = item
    missing = sorted(TEST0007_CRITICAL_FAILURE_CODES - set(by_code))
    extra = sorted(set(by_code) - TEST0007_CRITICAL_FAILURE_CODES)
    if missing or extra or duplicates:
        add_error(result, "MISSING_CRITICAL_FAILURE_ASSESSMENT", missing=missing, extra=extra, duplicates=sorted(set(duplicates)))
        return
    implied = implied_test0007_critical_failures(run, result.get("criteria") or [])
    rendered=[]
    for code in sorted(TEST0007_CRITICAL_FAILURE_CODES):
        item=by_code[code]
        trig=item.get("triggered")
        if not isinstance(trig, bool):
            add_error(result, "MISSING_CRITICAL_FAILURE_ASSESSMENT", code=code, detail="triggered must be boolean")
            continue
        rationale=norm(str(item.get("rationale") or ""))
        if len(rationale)<20:
            add_error(result, "MISSING_CRITICAL_FAILURE_ASSESSMENT", code=code, detail="critical-failure rationale must contain at least 20 normalized characters")
        if trig:
            ev=item.get("evidence") or {}
            ok, ev_code, why=verify_evidence(ev, run.get("raw_output_path") or "", raw_root, quote_min_chars)
            if not ok:
                add_error(result, ev_code, critical_failure=code, detail=why)
            add_gate_failure(result, code, automatic_fail=True, source="judge_critical_failure_assessment")
        if code in implied and trig is not True:
            add_error(result, "CRITICAL_FAILURE_ASSESSMENT_INCONSISTENT", critical_failure_code=code, detail="selected score anchors imply this automatic failure but the judge assessment declared triggered=false")
        rendered.append({"code":code,"triggered":trig,"rationale":item.get("rationale"),"evidence":item.get("evidence") if trig else None,"anchor_implied":code in implied})
    result["critical_failures"] = rendered


def verify_decision_rule(path: Path | None, tid: str, ldef: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    if path is None or not path.exists():
        return None, "decision rule artifact is missing"
    rule=load_yaml(path) or {}
    if rule.get("artifact_status") != "FROZEN_PRE_RUN_DECISION_RULE" or canonical_component(rule.get("test_id")) != canonical_component(tid):
        return None, "decision rule artifact status/test_id is invalid"
    ent=ldef.get("decision_rule_evidence") or {}
    observed=sha256_file(path)
    if str(ent.get("sha256") or "").lower()!=observed.lower():
        return None, "comparison lock decision_rule_evidence hash mismatch"
    try:
        center=float((rule.get("margin_center") or {}).get("value"))
        canonical_threshold=float((rule.get("decision_regions") or {}).get("canonical_margin_threshold"))
        zone=list((rule.get("decision_regions") or {}).get("inconclusive_if_margin_between_inclusive") or [])
        lower=float(zone[0]); upper=float(zone[1])
        absolute_floor=float((rule.get("absolute_discriminability") or {}).get("floor"))
        locked_threshold=float(ldef.get("margin_threshold"))
    except Exception as exc:
        return None, f"decision rule numeric fields invalid: {exc}"
    if len(zone)!=2 or not all(math.isfinite(x) for x in [center,canonical_threshold,lower,upper,absolute_floor,locked_threshold]):
        return None, "decision rule contains non-finite or incomplete numeric fields"
    if abs(center-canonical_threshold)>TOL or abs(center-locked_threshold)>TOL or not (lower < center < upper) or absolute_floor<=0:
        return None, "decision rule boundary/zone/floor is inconsistent with comparison lock"
    return {"path":str(path),"sha256":observed,"center":center,"lower":lower,"upper":upper,"absolute_floor":absolute_floor,"raw":rule}, None


def expected_minimum(erow: dict[str, Any]) -> tuple[bool, float | None]:
    """Compare presence first, value second. None/omitted means no floor."""
    if "minimum_score" not in erow or erow.get("minimum_score") is None:
        return False, None
    return True, float(erow["minimum_score"])


def arithmetic_margin_ceiling(test: dict[str, Any], floor_overrides: dict[str, float] | None = None) -> tuple[float, list[dict[str, Any]]]:
    """Upper bound on honest LEFT-RIGHT margin implied by the locked rubric.

    Default right-arm floor is minimum_score for mandatory criteria and zero for
    non-mandatory criteria. A frozen pre-run rubric addendum may explicitly set
    the right-arm arithmetic floor to zero for criteria whose fail-closed anchor
    is predeclared wholly below the mandatory floor. This affects reachability
    only; it does not rewrite actual run scoring.
    """
    rubric = (test.get("evaluation") or {}).get("rubric") or []
    floor_overrides = {canonical_component(k): float(v) for k, v in (floor_overrides or {}).items()}
    total = 0.0
    rows: list[dict[str, Any]] = []
    for row in rubric:
        w = float(row["weight"])
        mandatory = bool(row.get("mandatory"))
        cname = canonical_component(row.get("criterion"))
        if cname in floor_overrides:
            floor = float(floor_overrides[cname])
            floor_source = "FROZEN_RIGHT_ARM_FLOOR_OVERRIDE"
        elif mandatory:
            if row.get("minimum_score") is None:
                raise ValueError(f"mandatory criterion {row.get('criterion')} lacks minimum_score")
            floor = float(row["minimum_score"])
            floor_source = "MANDATORY_MINIMUM_SCORE"
        else:
            floor = 0.0
            floor_source = "NON_MANDATORY_ZERO"
        if not math.isfinite(floor) or floor < 0 or floor > 100:
            raise ValueError(f"invalid arithmetic floor for {row.get('criterion')}: {floor}")
        contribution = w * (100.0 - floor)
        total += contribution
        rows.append({
            "criterion": row.get("criterion"),
            "weight": w,
            "floor": floor,
            "floor_source": floor_source,
            "ceiling_contribution": round(contribution, 6),
        })
    return round(total, 6), rows


def verify_test0007_addendum(base_rubric_path: Path | None, addendum_path: Path | None, freeze_record_path: Path | None, test: dict[str, Any], right_selector: dict[str, Any]) -> tuple[dict[str, float], dict[str, Any]]:
    if not base_rubric_path or not addendum_path or not freeze_record_path:
        raise ValueError("TEST-0007 requires frozen rubric, rubric addendum, and addendum freeze record")
    for pp in (base_rubric_path, addendum_path, freeze_record_path):
        if not pp.exists():
            raise ValueError(f"required rubric/addendum artifact missing: {pp}")
    base = load_yaml(base_rubric_path) or {}
    add = load_yaml(addendum_path) or {}
    fr = load_yaml(freeze_record_path) or {}
    if canonical_component(base.get("test_id")) != "TEST-0007":
        raise ValueError("base rubric test_id must be TEST-0007")
    if add.get("artifact_status") != "FROZEN_PRE_RUN_ADDENDUM" or canonical_component(add.get("test_id")) != "TEST-0007":
        raise ValueError("rubric addendum must be FROZEN_PRE_RUN_ADDENDUM for TEST-0007")
    if fr.get("artifact_status") != "FROZEN_PRE_RUN_ADDENDUM_RECORD" or canonical_component(fr.get("test_id")) != "TEST-0007":
        raise ValueError("rubric addendum freeze record is invalid")
    base_sha = sha256_file(base_rubric_path)
    add_sha = sha256_file(addendum_path)
    fr_sha = sha256_file(freeze_record_path)
    if str((add.get("base_rubric") or {}).get("sha256") or "").lower() != base_sha.lower():
        raise ValueError("addendum base_rubric hash mismatch")
    if str((fr.get("base_chain") or {}).get("rubric", {}).get("sha256") or "").lower() != base_sha.lower():
        raise ValueError("addendum freeze record base rubric hash mismatch")
    if str((fr.get("addendum") or {}).get("sha256") or "").lower() != add_sha.lower():
        raise ValueError("addendum freeze record addendum hash mismatch")
    base_rows = {canonical_component(r.get("criterion")): r for r in (base.get("rubric") or [])}
    suite_rows = {canonical_component(r.get("criterion")): r for r in ((test.get("evaluation") or {}).get("rubric") or [])}
    if set(base_rows) != set(suite_rows):
        raise ValueError("TEST-0007 base rubric criteria differ from locked suite")
    for cname, brow in base_rows.items():
        srow = suite_rows[cname]
        for field in ("weight", "mandatory", "minimum_score"):
            if brow.get(field) != srow.get(field):
                raise ValueError(f"TEST-0007 base rubric {field} mismatch for {cname}")
    cfg = add.get("comparison_arithmetic_ceiling") or {}
    expected_right = arm_phase_key(right_selector)
    if canonical_component(cfg.get("test_id")) != "TEST-0007" or canonical_component(cfg.get("right_selector")) != expected_right:
        raise ValueError(f"addendum arithmetic ceiling selector must target TEST-0007 {expected_right}")
    overrides: dict[str, float] = {}
    for raw_name, spec in (cfg.get("right_floor_overrides") or {}).items():
        cname = canonical_component(raw_name)
        brow = base_rows.get(cname)
        if not brow or not bool(brow.get("mandatory")) or brow.get("minimum_score") is None:
            raise ValueError(f"invalid floor override criterion {raw_name}")
        if spec.get("basis") != "PREDECLARED_FAIL_CLOSED_BELOW_MANDATORY_FLOOR":
            raise ValueError(f"invalid floor override basis for {raw_name}")
        anchor_name = spec.get("base_score_anchor")
        anchor = ((brow.get("score_anchors") or {}).get(anchor_name) or {})
        rng = anchor.get("range") or []
        if len(rng) != 2 or float(rng[1]) >= float(brow.get("minimum_score")):
            raise ValueError(f"base fail-closed anchor for {raw_name} is not wholly below mandatory floor")
        floor = float(spec.get("right_floor_for_ceiling"))
        if floor != 0.0:
            raise ValueError(f"D2 only permits right_floor_for_ceiling=0 for {raw_name}")
        if float(spec.get("base_mandatory_minimum_score")) != float(brow.get("minimum_score")) or list(spec.get("base_anchor_range") or []) != list(rng):
            raise ValueError(f"addendum evidence mismatch for {raw_name}")
        overrides[cname] = floor
    cons = ((add.get("anchor_additions") or {}).get("CONSISTENCY") or {}).get("full_execution") or {}
    crange = cons.get("range") or []
    if len(crange) != 2 or float(crange[0]) < float(base_rows["CONSISTENCY"].get("minimum_score")) or len(str(cons.get("condition") or "").strip()) < 20:
        raise ValueError("D1 CONSISTENCY full_execution anchor missing or insufficient")
    evidence = {
        "base_rubric_path": base_rubric_path.name, "base_rubric_sha256": base_sha,
        "addendum_path": addendum_path.name, "addendum_sha256": add_sha,
        "addendum_freeze_record_path": freeze_record_path.name, "addendum_freeze_record_sha256": fr_sha,
        "right_selector": expected_right, "right_floor_overrides": overrides,
    }
    return overrides, evidence


def validate_pre_run_registry(
    registry_path: Path | None,
    opening_record_path: Path | None,
    comparison_lock_path: Path | None,
    metric_lock_path: Path | None,
    output: dict[str, Any],
    additional_artifacts: dict[str, Path] | None = None,
) -> None:
    """Verify lock hashes against a registry frozen before the blind round.

    File mtimes are deliberately ignored: copying/unzipping may rewrite them.
    Temporal precedence is a run-governance property of the pre-run registry;
    the scorer verifies the content-addressed chain.
    """
    if registry_path is None or not registry_path.exists():
        add_error(output, "PRE_RUN_LOCK_HASH_MISMATCH", detail="pre-run lock registry missing")
        return
    registry = load_yaml(registry_path) or {}
    if registry.get("artifact_status") != "LOCKED_PRE_RUN":
        add_error(output, "PRE_RUN_LOCK_HASH_MISMATCH", detail="pre-run lock registry is not LOCKED_PRE_RUN")
        return
    registry_sha = sha256_file(registry_path)
    if opening_record_path is None or not opening_record_path.exists():
        add_error(output, "PRE_RUN_LOCK_HASH_MISMATCH", detail="pre-run opening/freeze record missing")
    else:
        opening = load_yaml(opening_record_path) or {}
        expected_registry_sha = opening.get("pre_run_lock_registry_sha256")
        if opening.get("artifact_status") != "FROZEN_BEFORE_BLIND_ROUND" or not expected_registry_sha:
            add_error(output, "PRE_RUN_LOCK_HASH_MISMATCH", detail="opening/freeze record is not a valid pre-run anchor")
        elif str(expected_registry_sha).lower() != registry_sha.lower():
            add_error(output, "PRE_RUN_LOCK_HASH_MISMATCH", detail="pre-run registry SHA-256 differs from opening/freeze record", expected_sha256=expected_registry_sha, observed_sha256=registry_sha)
    locks = registry.get("locks") or {}
    checks = [
        ("comparison_margin", comparison_lock_path),
        ("metric_derivation", metric_lock_path),
    ]
    observed: dict[str, Any] = {}
    for name, path in checks:
        ent = locks.get(name)
        if path is None or not path.exists():
            # The domain-specific validator will also report its own missing-lock code.
            observed[name] = {"path": str(path) if path else None, "sha256": None}
            continue
        sha = sha256_file(path)
        observed[name] = {"path": str(path), "sha256": sha}
        if not isinstance(ent, dict) or not ent.get("sha256"):
            add_error(output, "PRE_RUN_LOCK_HASH_MISMATCH", lock=name, detail="lock hash absent from pre-run registry", observed_sha256=sha)
            continue
        if str(ent.get("sha256")).lower() != sha.lower():
            add_error(
                output,
                "PRE_RUN_LOCK_HASH_MISMATCH",
                lock=name,
                detail="actual lock SHA-256 differs from pre-run registry",
                expected_sha256=ent.get("sha256"),
                observed_sha256=sha,
            )
    additional_observed: dict[str, Any] = {}
    reg_artifacts = registry.get("artifacts") or {}
    for name, path in (additional_artifacts or {}).items():
        if path is None or not path.exists():
            add_error(output, "PRE_RUN_LOCK_HASH_MISMATCH", artifact=name, detail="required additional pre-run artifact missing")
            additional_observed[name] = {"path": str(path) if path else None, "sha256": None}
            continue
        sha = sha256_file(path)
        additional_observed[name] = {"path": str(path), "sha256": sha}
        ent = reg_artifacts.get(name)
        if not isinstance(ent, dict) or str(ent.get("sha256") or "").lower() != sha.lower():
            add_error(output, "PRE_RUN_LOCK_HASH_MISMATCH", artifact=name, detail="additional artifact hash absent/mismatched in pre-run registry", observed_sha256=sha, expected_sha256=(ent or {}).get("sha256") if isinstance(ent, dict) else None)
    output["pre_run_lock_registry"] = {
        "path": str(registry_path),
        "sha256": registry_sha,
        "artifact_status": registry.get("artifact_status"),
        "opening_record_path": str(opening_record_path) if opening_record_path else None,
        "observed_locks": observed,
        "observed_additional_artifacts": additional_observed,
    }


def canonical_component(value: Any, default: str = "") -> str:
    return str(value if value not in (None, "") else default).strip().upper()


def parse_raw_header(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Parse the one-line runner binding header.

    Canonical form:
      PILOT001_RUN_HEADER {"test_id":"TEST-0007","arm_id":"FULL",
                           "phase":"AFTER_DEDUP","arm_package_sha256":"..."}
    """
    try:
        first = path.read_text(encoding="utf-8").splitlines()[0]
    except Exception as exc:
        return None, f"cannot read raw header: {exc}"
    prefix = "PILOT001_RUN_HEADER "
    if not first.startswith(prefix):
        return None, "missing PILOT001_RUN_HEADER on first line"
    try:
        header = json.loads(first[len(prefix):])
    except Exception as exc:
        return None, f"invalid PILOT001_RUN_HEADER JSON: {exc}"
    if not isinstance(header, dict):
        return None, "PILOT001_RUN_HEADER must decode to an object"
    return header, None


def verify_run_raw(run: dict[str, Any], raw_root: Path) -> tuple[bool, str | None, Path | None, str | None, dict[str, Any] | None, str | None]:
    rel = run.get("raw_output_path")
    declared_hash = run.get("raw_output_sha256")
    if not rel or not declared_hash:
        return False, "run requires raw_output_path and raw_output_sha256", None, None, None, None
    p = raw_root / rel
    if not p.exists():
        return False, f"raw output not found: {p}", p, None, None, None
    observed = sha256_file(p)
    header, header_error = parse_raw_header(p)
    if observed.lower() != str(declared_hash).lower():
        return False, f"sha256 mismatch: expected {declared_hash}, observed {observed}", p, observed, header, header_error
    return True, None, p, observed, header, header_error


def verify_evidence(ev: dict[str, Any], run_raw_rel: str, raw_root: Path, quote_min_chars: int) -> tuple[bool, str, str | None]:
    required = ["raw_output_path", "start_line", "end_line", "quote"]
    missing = [k for k in required if ev.get(k) in (None, "")]
    if missing:
        return False, "MISSING_RESPONSE_CITATION", f"missing evidence fields: {missing}"
    if ev.get("raw_output_path") != run_raw_rel:
        return False, "CITATION_NOT_VERIFIABLE", "criterion evidence path differs from run raw_output_path"
    q = norm(str(ev.get("quote", "")))
    if len(q) < quote_min_chars:
        return False, "CITATION_NOT_VERIFIABLE", f"quote too short: {len(q)} chars; minimum is {quote_min_chars}"
    p = raw_root / run_raw_rel
    if not p.exists():
        return False, "CITATION_NOT_VERIFIABLE", f"raw output not found: {p}"
    lines = p.read_text(encoding="utf-8").splitlines()
    try:
        s, e = int(ev["start_line"]), int(ev["end_line"])
    except Exception:
        return False, "CITATION_NOT_VERIFIABLE", "line range is not integer-valued"
    if s < 1 or e < s or e > len(lines):
        return False, "CITATION_NOT_VERIFIABLE", f"invalid line range {s}-{e} for {p} ({len(lines)} lines)"
    excerpt = "\n".join(lines[s - 1 : e])
    if q not in norm(excerpt):
        return False, "CITATION_NOT_VERIFIABLE", "quote not found inside cited line range"
    return True, "", None


def run_key(run: dict[str, Any]) -> tuple[str, str, str]:
    return (
        canonical_component(run.get("test_id")),
        canonical_component(run.get("arm_id"), "PRIMARY"),
        canonical_component(run.get("phase"), "CURRENT"),
    )


def selector_key(sel: dict[str, Any]) -> tuple[str, str]:
    return (canonical_component(sel.get("arm_id"), "PRIMARY"), canonical_component(sel.get("phase"), "CURRENT"))


def arm_phase_key(sel: dict[str, Any]) -> str:
    arm, phase = selector_key(sel)
    return f"{arm}@{phase}"


def find_result(results_by_key: dict[tuple[str, str, str], dict[str, Any]], tid: str, selector: dict[str, Any]) -> dict[str, Any] | None:
    arm, phase = selector_key(selector)
    return results_by_key.get((canonical_component(tid), arm, phase))


def arm_hash_value(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("sha256")
    if value is None:
        return None
    return str(value).lower()


def validate_threshold_justification(
    contract: dict[str, Any], ldef: dict[str, Any], effective_ceiling: float, threshold: float, decision_rule_info: dict[str, Any] | None = None
) -> tuple[bool, str]:
    just = ldef.get("threshold_justification")
    if not isinstance(just, dict):
        return False, "threshold_justification is required"
    expected_basis = "FROZEN_ANCHOR_BOUNDARY" if decision_rule_info is not None else "EFFECTIVE_CEILING"
    if just.get("basis") != expected_basis:
        return False, f"threshold_justification.basis must be {expected_basis}"
    rationale = norm(str(just.get("rationale") or ""))
    if len(rationale) < 20:
        return False, "threshold_justification.rationale must contain at least 20 normalized characters"
    distinguishability = norm(str(just.get("distinguishability_rationale") or ""))
    if len(distinguishability) < 20:
        return False, "threshold_justification.distinguishability_rationale must contain at least 20 normalized characters"
    try:
        ref = float(just.get("effective_ceiling_reference"))
        frac = float(just.get("threshold_fraction_of_effective_ceiling"))
    except Exception:
        return False, "threshold justification must contain numeric effective_ceiling_reference and threshold_fraction_of_effective_ceiling"
    if not math.isfinite(ref) or abs(ref - effective_ceiling) > TOL:
        return False, "threshold justification effective_ceiling_reference does not match recomputed effective ceiling"
    reqs = ((contract.get("comparison_lock_requirements") or {}).get("threshold_justification_required") or {})
    try:
        min_frac = float(reqs.get("minimum_fraction_of_effective_ceiling", 0.05))
    except Exception:
        return False, "contract minimum_fraction_of_effective_ceiling is invalid"
    if not math.isfinite(min_frac) or min_frac <= 0 or min_frac > 1:
        return False, "contract minimum_fraction_of_effective_ceiling must be in (0,1]"
    if effective_ceiling <= 0 or not math.isfinite(frac) or frac < min_frac - 1e-12 or frac > 1 + TOL:
        return False, f"threshold fraction must be >= {min_frac:g} and <= 1"
    if abs(frac - threshold / effective_ceiling) > 1e-6:
        return False, "threshold fraction does not equal margin_threshold / effective_ceiling"
    if decision_rule_info is not None:
        try:
            declared=float(just.get("anchor_boundary_reference"))
        except Exception:
            return False, "FROZEN_ANCHOR_BOUNDARY justification requires numeric anchor_boundary_reference"
        if abs(declared-float(decision_rule_info["center"]))>TOL or abs(threshold-float(decision_rule_info["center"]))>TOL:
            return False, "anchor_boundary_reference does not match the frozen decision rule"
    return True, ""


def validate_aggregation(contract: dict[str, Any], output: dict[str, Any], results_by_key: dict[tuple[str, str, str], dict[str, Any]]) -> None:
    agg = contract.get("suite_aggregation")
    if not isinstance(agg, dict) or agg.get("acceptance", {}).get("mode") != "EQUAL_TEST_WEIGHT":
        add_error(output, "UNDEFINED_AGGREGATION", detail="suite_aggregation.acceptance.mode must be EQUAL_TEST_WEIGHT")
        return
    acceptance = agg.get("acceptance") or {}
    test_ids = acceptance.get("test_ids")
    if not isinstance(test_ids, list) or not test_ids:
        add_error(output, "UNDEFINED_AGGREGATION", detail="acceptance test_ids missing")
        return
    default_sel = acceptance.get("default_primary_run") or {"arm_id": "PRIMARY", "phase": "CURRENT"}
    overrides = acceptance.get("primary_run_overrides") or {}
    totals = []
    components = []
    for tid in test_ids:
        sel = overrides.get(tid) or default_sel
        rr = find_result(results_by_key, tid, sel)
        if rr is None:
            add_error(output, "UNDEFINED_AGGREGATION", detail=f"primary run missing for {tid}: {sel}")
            continue
        if rr.get("status") == "INVALID":
            continue
        totals.append(float(rr.get("recomputed_total", 0.0)))
        components.append({"test_id": tid, "arm_id": sel.get("arm_id", "PRIMARY"), "phase": sel.get("phase", "CURRENT"), "total": rr.get("recomputed_total")})
    if totals:
        suite_total = sum(totals) / len(totals)
        output["suite_aggregate"] = {"mode": "EQUAL_TEST_WEIGHT", "recomputed_total": round(suite_total, 6), "components": components}


def validate_metric_derivation(contract: dict[str, Any], metric_lock_path: Path | None, output: dict[str, Any], results_by_key: dict[tuple[str, str, str], dict[str, Any]]) -> None:
    policies = contract.get("metric_derivation") or {}
    if not policies:
        return
    if metric_lock_path is None or not metric_lock_path.exists():
        add_error(output, "UNDEFINED_METRIC_DERIVATION", detail="metric derivation lock missing")
        return
    lock = load_yaml(metric_lock_path) or {}
    if lock.get("artifact_status") != "LOCKED":
        add_error(output, "UNDEFINED_METRIC_DERIVATION", detail="metric derivation lock is not LOCKED")
        return
    defs = lock.get("metrics") or {}
    metrics_out: dict[str, Any] = {}
    for metric_name in policies:
        mdef = defs.get(metric_name)
        if not isinstance(mdef, dict):
            add_error(output, "UNDEFINED_METRIC_DERIVATION", metric=metric_name, detail="metric missing from metric lock")
            continue
        mode = mdef.get("mode")
        allowed = (policies.get(metric_name) or {}).get("allowed_modes") or []
        if allowed and mode not in allowed:
            add_error(output, "UNDEFINED_METRIC_DERIVATION", metric=metric_name, detail=f"mode {mode} not allowed by contract")
            continue
        if mode == "CHECK_PASS_RATE":
            checks = mdef.get("checks") or []
            if not checks:
                add_error(output, "UNDEFINED_METRIC_DERIVATION", metric=metric_name, detail="CHECK_PASS_RATE requires checks")
                continue
            vals = []
            ids = []
            for chk in checks:
                cid = chk.get("id")
                tid = chk.get("test_id")
                criterion = chk.get("criterion")
                threshold = chk.get("threshold")
                rr = find_result(results_by_key, tid, chk)
                if rr is None or criterion is None or threshold is None:
                    add_error(output, "UNDEFINED_METRIC_DERIVATION", metric=metric_name, detail=f"invalid check {cid}")
                    continue
                if rr.get("status") == "INVALID":
                    continue
                crow = next((c for c in rr.get("criteria", []) if c.get("criterion") == criterion), None)
                if crow is None:
                    add_error(output, "UNDEFINED_METRIC_DERIVATION", metric=metric_name, detail=f"criterion not found for check {cid}")
                    continue
                passed = float(crow["score"]) >= float(threshold)
                vals.append(1 if passed else 0)
                ids.append(cid)
            if vals:
                metrics_out[metric_name] = {"mode": mode, "numerator": sum(vals), "denominator": len(vals), "value": round(sum(vals) / len(vals), 6), "check_ids": ids}
        elif mode == "WEIGHTED_CRITERION_MEAN":
            selectors = mdef.get("selectors") or []
            if not selectors:
                add_error(output, "UNDEFINED_METRIC_DERIVATION", metric=metric_name, detail="WEIGHTED_CRITERION_MEAN requires selectors")
                continue
            num = den = 0.0
            rows = []
            for sel in selectors:
                rr = find_result(results_by_key, sel.get("test_id"), sel)
                criterion = sel.get("criterion")
                if rr is None or not criterion:
                    add_error(output, "UNDEFINED_METRIC_DERIVATION", metric=metric_name, detail=f"invalid selector {sel}")
                    continue
                if rr.get("status") == "INVALID":
                    continue
                crow = next((c for c in rr.get("criteria", []) if c.get("criterion") == criterion), None)
                if crow is None:
                    add_error(output, "UNDEFINED_METRIC_DERIVATION", metric=metric_name, detail=f"criterion not found: {criterion}")
                    continue
                w = float(sel.get("weight", 1.0))
                num += float(crow["score"]) * w
                den += w
                rows.append({"test_id": sel.get("test_id"), "arm_id": sel.get("arm_id", "PRIMARY"), "phase": sel.get("phase", "CURRENT"), "criterion": criterion, "score": crow["score"], "metric_weight": w})
            if den > 0:
                metrics_out[metric_name] = {"mode": mode, "value": round(num / den, 6), "contributing_rows": rows, "weight_sum": den}
        else:
            add_error(output, "UNDEFINED_METRIC_DERIVATION", metric=metric_name, detail=f"unsupported mode: {mode}")
    output["derived_metrics"] = metrics_out


def expected_arm_hashes(ldef: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for selector_name, value in (ldef.get("arm_package_hashes") or {}).items():
        h = arm_hash_value(value)
        if h:
            key = canonical_component(selector_name)
            out[key] = h
    return out


def validate_run_arm_binding(
    output: dict[str, Any],
    tid: str,
    result: dict[str, Any] | None,
    expected_hash: str | None,
) -> bool:
    if result is None:
        return False
    header = result.get("raw_header")
    if not isinstance(header, dict):
        add_error(result, "ARM_PACKAGE_HASH_MISMATCH", test_id=tid, arm_id=result.get("arm_id"), phase=result.get("phase"), detail="raw output lacks runner package-binding header")
        return False
    h_tid = canonical_component(header.get("test_id"))
    h_arm = canonical_component(header.get("arm_id"), "PRIMARY")
    h_phase = canonical_component(header.get("phase"), "CURRENT")
    r_tid, r_arm, r_phase = result.get("normalized_key") or ("", "", "")
    if (h_tid, h_arm, h_phase) != (r_tid, r_arm, r_phase):
        add_error(
            result,
            "RAW_OUTPUT_HEADER_MISMATCH",
            test_id=tid,
            arm_id=result.get("arm_id"),
            phase=result.get("phase"),
            detail="raw header test/arm/phase differs from scored run",
            header_key=[h_tid, h_arm, h_phase],
            run_key=[r_tid, r_arm, r_phase],
        )
        return False
    observed = str(header.get("arm_package_sha256") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", observed):
        add_error(result, "ARM_PACKAGE_HASH_MISMATCH", test_id=tid, arm_id=result.get("arm_id"), phase=result.get("phase"), detail="raw header arm_package_sha256 missing or malformed")
        return False
    if not expected_hash or not re.fullmatch(r"[0-9a-f]{64}", str(expected_hash).lower()):
        add_error(result, "ARM_PACKAGE_HASH_MISMATCH", test_id=tid, arm_id=result.get("arm_id"), detail="comparison lock lacks valid package hash for arm")
        return False
    if observed != str(expected_hash).lower():
        add_error(
            result,
            "ARM_PACKAGE_HASH_MISMATCH",
            test_id=tid,
            arm_id=result.get("arm_id"),
            phase=result.get("phase"),
            expected_sha256=str(expected_hash).lower(),
            observed_sha256=observed,
        )
        return False
    return True


def validate_comparisons(contract: dict[str, Any], lock_path: Path | None, suite: dict[str, dict[str, Any]], output: dict[str, Any], results_by_key: dict[tuple[str, str, str], dict[str, Any]], test0007_rubric_path: Path | None = None, rubric_addendum_path: Path | None = None, rubric_addendum_freeze_path: Path | None = None, decision_rule_path: Path | None = None, candidate_version: str = "", lock_override: dict[str, Any] | None = None) -> None:
    comparisons_policy = contract.get("comparative_tests") or {}
    if not comparisons_policy:
        return
    if lock_path is None or not lock_path.exists():
        add_error(output, "POST_HOC_MARGIN_THRESHOLD", detail="comparison margin lock missing")
        return
    lock = lock_override if lock_override is not None else (load_yaml(lock_path) or {})
    if lock.get("artifact_status") != "LOCKED":
        add_error(output, "POST_HOC_MARGIN_THRESHOLD", detail="comparison margin lock is not LOCKED")
        return
    lock_defs = lock.get("comparisons") or {}
    comp_out = []
    hex64 = re.compile(r"^[0-9a-fA-F]{64}$")
    for tid, policy in comparisons_policy.items():
        ldef = lock_defs.get(tid)
        if not isinstance(ldef, dict) or "margin_threshold" not in ldef:
            add_error(output, "POST_HOC_MARGIN_THRESHOLD", test_id=tid, detail="comparison threshold absent from prelocked file")
            continue
        test = suite.get(tid)
        if not test:
            add_error(output, "UNDEFINED_AGGREGATION", test_id=tid, detail="comparison test missing from locked suite")
            continue
        floor_overrides: dict[str, float] = {}
        addendum_evidence: dict[str, Any] | None = None
        if canonical_component(tid) == "TEST-0007":
            try:
                floor_overrides, addendum_evidence = verify_test0007_addendum(
                    test0007_rubric_path, rubric_addendum_path, rubric_addendum_freeze_path, test, ldef.get("right") or {}
                )
            except Exception as exc:
                add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail=f"rubric addendum/D2 ceiling basis invalid: {exc}")
                continue
        try:
            arithmetic_ceiling, ceiling_rows = arithmetic_margin_ceiling(test, floor_overrides=floor_overrides)
        except Exception as exc:
            add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail=f"cannot compute arithmetic ceiling: {exc}")
            continue
        if addendum_evidence is not None:
            locked_add = ldef.get("rubric_addendum_evidence") or {}
            for field in ("base_rubric_sha256", "addendum_sha256", "addendum_freeze_record_sha256", "right_selector"):
                if str(locked_add.get(field) or "").lower() != str(addendum_evidence.get(field) or "").lower():
                    add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail=f"locked rubric_addendum_evidence mismatch for {field}", expected=addendum_evidence.get(field), observed=locked_add.get(field))
                    break
            else:
                if {canonical_component(k): float(v) for k,v in (locked_add.get("right_floor_overrides") or {}).items()} != {canonical_component(k): float(v) for k,v in floor_overrides.items()}:
                    add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="locked rubric_addendum_evidence floor overrides mismatch")
            if output.get("status") == "INVALID" and any(e.get("test_id")==tid and "rubric_addendum_evidence" in str(e.get("detail")) for e in output.get("errors", [])):
                continue
        try:
            threshold = float(ldef["margin_threshold"])
        except Exception:
            add_error(output, "INVALID_MARGIN_THRESHOLD", test_id=tid, detail="margin_threshold must be numeric")
            continue
        if not math.isfinite(threshold) or threshold <= 0:
            add_error(output, "INVALID_MARGIN_THRESHOLD", test_id=tid, detail="margin_threshold must be finite and strictly positive", threshold=ldef.get("margin_threshold"))
            continue

        decision_rule_info = None
        if canonical_component(tid) == "TEST-0007":
            decision_rule_info, decision_rule_error = verify_decision_rule(decision_rule_path, tid, ldef)
            if decision_rule_error:
                add_error(output, "DECISION_RULE_MISMATCH", test_id=tid, detail=decision_rule_error)
                continue

        declared_arithmetic = ldef.get("arithmetic_ceiling")
        if declared_arithmetic is None:
            add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="locked arithmetic_ceiling missing", recomputed_arithmetic_ceiling=arithmetic_ceiling)
            continue
        try:
            darith = float(declared_arithmetic)
        except Exception:
            darith = math.nan
        if not math.isfinite(darith) or abs(darith - arithmetic_ceiling) > TOL:
            add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="locked arithmetic_ceiling does not match rubric", locked_arithmetic_ceiling=declared_arithmetic, recomputed_arithmetic_ceiling=arithmetic_ceiling)
            continue

        # Every run selector is content-addressed to the exact frozen package used
        # in that phase. C1: FULL@BEFORE_DEDUP and FULL@AFTER_DEDUP are distinct
        # packages by construction and must never share one arm-only hash slot.
        arm_hashes = expected_arm_hashes(ldef)
        left_sel = ldef.get("left") or {}
        right_sel = ldef.get("right") or {}
        left_pkg_key = arm_phase_key(left_sel)
        right_pkg_key = arm_phase_key(right_sel)
        required_pkg_keys = [left_pkg_key, right_pkg_key]
        guard = ldef.get("full_preservation") or {}
        if bool(policy.get("full_preservation_guard_required")):
            required_pkg_keys += [arm_phase_key(guard.get("before") or {}), arm_phase_key(guard.get("after") or {})]
        missing_pkg_keys = [k for k in required_pkg_keys if k not in arm_hashes]
        if missing_pkg_keys:
            add_error(output, "ARM_PACKAGE_HASH_MISMATCH", test_id=tid, detail="comparison lock must contain package hashes for every arm_id@phase selector", required_package_keys=required_pkg_keys, missing_package_keys=missing_pkg_keys)
            continue
        if any(not hex64.match(arm_hashes[k]) for k in required_pkg_keys):
            add_error(output, "ARM_PACKAGE_HASH_MISMATCH", test_id=tid, detail="arm_id@phase package hashes must be 64-hex SHA-256")
            continue

        structural_required = bool(policy.get("structural_ceiling_required", False))
        structural = ldef.get("structural_ceiling")
        structural_value: float | None = None
        if structural is not None:
            try:
                structural_value = float(structural)
            except Exception:
                structural_value = math.nan
            if not math.isfinite(structural_value) or structural_value < 0:
                add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="structural_ceiling must be finite and non-negative", structural_ceiling=structural)
                continue
        elif structural_required:
            add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="structural ceiling required but absent; reachability not established")
            continue

        if structural_required:
            sev = ldef.get("structural_ceiling_evidence") or {}
            report_rel = sev.get("report_path")
            report_sha = sev.get("report_sha256")
            evidence_arm_hashes = sev.get("arm_package_hashes") or {}
            full_sha = arm_hash_value(evidence_arm_hashes.get("FULL@AFTER_DEDUP") or evidence_arm_hashes.get("full_after_dedup"))
            ablated_sha = arm_hash_value(evidence_arm_hashes.get("ABLATED@AFTER_DEDUP") or evidence_arm_hashes.get("ablated_after_dedup"))
            if not report_rel or not report_sha or not hex64.match(str(report_sha)) or not full_sha or not hex64.match(str(full_sha)) or not ablated_sha or not hex64.match(str(ablated_sha)):
                add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="structural ceiling evidence is incomplete or unhashed")
                continue
            report_path = Path(str(report_rel))
            if not report_path.is_absolute():
                report_path = lock_path.parent / report_path
            if not report_path.exists():
                add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="structural ceiling report not found", report_path=str(report_path))
                continue
            observed_report_sha = sha256_file(report_path)
            if observed_report_sha.lower() != str(report_sha).lower():
                add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="structural ceiling report hash mismatch", expected_sha256=report_sha, observed_sha256=observed_report_sha)
                continue

            # B1: content hash alone is insufficient. Read the report and prove
            # that the locked structural number/test/arms are derived from it.
            report = load_yaml(report_path) or {}
            try:
                report_structural = float(report.get("structural_ceiling"))
            except Exception:
                report_structural = math.nan
            report_arms = report.get("arms") or {}
            report_full_entry = report_arms.get("full_after_dedup") or {}
            report_ablated_entry = report_arms.get("ablated_after_dedup") or {}
            report_full = arm_hash_value(report_full_entry)
            report_ablated = arm_hash_value(report_ablated_entry)
            def structural_role(raw_arm_id: Any, expected_role: str) -> str:
                raw = canonical_component(raw_arm_id, expected_role)
                expected_artifact = f"PILOT-001-TEST-0007-{expected_role}-AFTER_DEDUP-V{candidate_version}"
                if raw in {expected_role, expected_artifact}:
                    return expected_role
                return raw

            report_full_key = f"{structural_role(report_full_entry.get('arm_id'), 'FULL')}@{canonical_component(report_full_entry.get('phase'), 'AFTER_DEDUP')}"
            report_ablated_key = f"{structural_role(report_ablated_entry.get('arm_id'), 'ABLATED')}@{canonical_component(report_ablated_entry.get('phase'), 'AFTER_DEDUP')}"
            expected_struct_full_key = "FULL@AFTER_DEDUP"
            expected_struct_ablated_key = "ABLATED@AFTER_DEDUP"
            report_mismatches = []
            if report.get("artifact_status") != "FINAL":
                report_mismatches.append("artifact_status must be FINAL")
            if canonical_component(report.get("test_id")) != canonical_component(tid):
                report_mismatches.append("test_id differs")
            if not math.isfinite(report_structural) or structural_value is None or abs(report_structural - structural_value) > TOL:
                report_mismatches.append("structural_ceiling differs")
            if report_full_key != expected_struct_full_key or report_ablated_key != expected_struct_ablated_key:
                report_mismatches.append("structural report selectors must be FULL@AFTER_DEDUP and ABLATED@AFTER_DEDUP")
            if report_full != str(full_sha).lower() or report_ablated != str(ablated_sha).lower():
                report_mismatches.append("report arm hashes differ from structural_ceiling_evidence")
            if arm_hashes.get(expected_struct_full_key) != str(full_sha).lower() or arm_hashes.get(expected_struct_ablated_key) != str(ablated_sha).lower():
                report_mismatches.append("comparison phase-specific hashes differ from structural report arm hashes")
            if report_mismatches:
                add_error(
                    output,
                    "MARGIN_THRESHOLD_UNREACHABLE",
                    test_id=tid,
                    detail="structural report and comparison lock are inconsistent",
                    mismatches=report_mismatches,
                    report_structural_ceiling=report.get("structural_ceiling"),
                    locked_structural_ceiling=structural,
                    report_full_sha256=report_full,
                    report_ablated_sha256=report_ablated,
                )
                continue

        effective_ceiling = min(arithmetic_ceiling, structural_value) if structural_value is not None else arithmetic_ceiling
        declared_effective = ldef.get("effective_ceiling")
        if declared_effective is None:
            add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="locked effective_ceiling missing", recomputed_effective_ceiling=round(effective_ceiling, 6))
            continue
        try:
            deff = float(declared_effective)
        except Exception:
            deff = math.nan
        if not math.isfinite(deff) or abs(deff - effective_ceiling) > TOL:
            add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="locked effective_ceiling does not match arithmetic/structural ceilings", locked_effective_ceiling=declared_effective, recomputed_effective_ceiling=round(effective_ceiling, 6))
            continue
        if effective_ceiling <= 0:
            add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id=tid, detail="effective ceiling is non-positive, so no positive margin threshold is reachable", effective_ceiling=effective_ceiling)
            continue

        if decision_rule_info is not None and effective_ceiling + TOL < float(decision_rule_info["absolute_floor"]):
            add_error(output, "COMPARISON_NOT_DISCRIMINATIVE", test_id=tid, effective_ceiling=round(effective_ceiling, 6), absolute_discriminability_floor=decision_rule_info["absolute_floor"], detail="effective ceiling is below the frozen absolute discriminability floor")
            continue

        if threshold > effective_ceiling + TOL:
            add_error(
                output,
                "MARGIN_THRESHOLD_UNREACHABLE",
                test_id=tid,
                threshold=threshold,
                arithmetic_ceiling=arithmetic_ceiling,
                structural_ceiling=structural_value,
                effective_ceiling=round(effective_ceiling, 6),
                ceiling_components=ceiling_rows,
            )
            comp_out.append({
                "test_id": tid,
                "threshold": threshold,
                "arithmetic_ceiling": arithmetic_ceiling,
                "structural_ceiling": structural_value,
                "effective_ceiling": round(effective_ceiling, 6),
                "threshold_reachable": False,
                "ceiling_components": ceiling_rows,
            })
            continue

        just_ok, just_why = validate_threshold_justification(contract, ldef, effective_ceiling, threshold, decision_rule_info)
        if not just_ok:
            add_error(output, "INVALID_MARGIN_THRESHOLD", test_id=tid, detail=just_why)
            continue

        left = find_result(results_by_key, tid, left_sel)
        right = find_result(results_by_key, tid, right_sel)
        if left is None or right is None:
            add_error(output, "UNDEFINED_AGGREGATION", test_id=tid, detail="comparison arm/phase missing")
            continue

        # B2: prove that each raw output came from the exact package whose hash
        # was used to derive/freeze the comparison instrument.
        left_bound = validate_run_arm_binding(output, tid, left, arm_hashes.get(left_pkg_key))
        right_bound = validate_run_arm_binding(output, tid, right, arm_hashes.get(right_pkg_key))
        if not left_bound or not right_bound or left.get("status") == "INVALID" or right.get("status") == "INVALID":
            continue
        if canonical_component(tid) == "TEST-0007":
            left_exact = Decimal(str(left.get("_comparison_recomputed_total_exact", left["recomputed_total"])))
            right_exact = Decimal(str(right.get("_comparison_recomputed_total_exact", right["recomputed_total"])))
            margin_exact = left_exact - right_exact
            margin = float(margin_exact)
        else:
            margin_exact = None
            margin = float(left["recomputed_total"]) - float(right["recomputed_total"])
        anchor_ambiguities=[]
        for side_name, rr in (("LEFT",left),("RIGHT",right)):
            for cr in rr.get("criteria") or []:
                if cr.get("anchor_ambiguity") is True:
                    anchor_ambiguities.append({"side":side_name,"criterion":cr.get("criterion"),"selected_anchor":cr.get("selected_anchor"),"alternative_anchor":cr.get("alternative_anchor")})
        comparison_decision = "PASS"
        if canonical_component(tid)=="TEST-0007" and decision_rule_info is not None:
            lower=float(decision_rule_info["lower"]); upper=float(decision_rule_info["upper"])
            if anchor_ambiguities:
                comparison_decision="INCONCLUSIVE"
                add_inconclusive(output, "ANCHOR_SELECTION_AMBIGUITY", test_id=tid, ambiguities=anchor_ambiguities, detail="judge declared ambiguity between score anchors in a compared arm")
            else:
                comparison_decision = classify_test0007_margin(margin_exact, Decimal(str(lower)), Decimal(str(upper)))
                if comparison_decision == "FAIL":
                    add_gate_failure(output, "COMPARISON_MARGIN_NOT_MET", test_id=tid, margin=round(margin,6), fail_below=lower, canonical_threshold=threshold)
                elif comparison_decision == "INCONCLUSIVE":
                    add_inconclusive(output, "COMPARISON_INCONCLUSIVE", test_id=tid, margin=round(margin,6), inconclusive_zone=[lower,upper], canonical_threshold=threshold)
        else:
            if margin + TOL < threshold:
                comparison_decision="FAIL"
                add_gate_failure(output, "COMPARISON_MARGIN_NOT_MET", test_id=tid, margin=round(margin, 6), threshold=threshold)
        item = {
            "test_id": tid,
            "left": {"arm_id": left_sel.get("arm_id", "PRIMARY"), "phase": left_sel.get("phase", "CURRENT"), "total": left["recomputed_total"], "package_key": left_pkg_key, "package_sha256": arm_hashes.get(left_pkg_key)},
            "right": {"arm_id": right_sel.get("arm_id", "PRIMARY"), "phase": right_sel.get("phase", "CURRENT"), "total": right["recomputed_total"], "package_key": right_pkg_key, "package_sha256": arm_hashes.get(right_pkg_key)},
            "formula": "LEFT_MINUS_RIGHT",
            "margin": round(margin, 6),
            "threshold": threshold,
            "threshold_justification": ldef.get("threshold_justification"),
            "arithmetic_ceiling": arithmetic_ceiling,
            "structural_ceiling": structural_value,
            "effective_ceiling": round(effective_ceiling, 6),
            "threshold_reachable": True,
            "ceiling_components": ceiling_rows,
            "decision_rule": {k:decision_rule_info[k] for k in ("sha256","center","lower","upper","absolute_floor")} if decision_rule_info else None,
            "anchor_ambiguities": anchor_ambiguities,
            "comparison_decision": comparison_decision,
            "passes_margin": comparison_decision == "PASS",
        }
        comp_out.append(item)

        if bool(policy.get("full_preservation_guard_required")):
            guard = ldef.get("full_preservation") or {}
            before_sel = guard.get("before") or {}
            after_sel = guard.get("after") or {}
            before = find_result(results_by_key, tid, before_sel)
            after = find_result(results_by_key, tid, after_sel)
            if before is None or after is None:
                add_error(output, "INVALID_ABLATION_FULL_REGRESSION", test_id=tid, detail="FULL before/after preservation runs missing")
                continue
            before_pkg_key = arm_phase_key(before_sel)
            after_pkg_key = arm_phase_key(after_sel)
            before_sha = arm_hashes.get(before_pkg_key)
            after_sha = arm_hashes.get(after_pkg_key)
            if not before_sha or not after_sha:
                add_error(output, "ARM_PACKAGE_HASH_MISMATCH", test_id=tid, detail="FULL preservation selectors lack phase-specific package hashes", required_package_keys=[before_pkg_key, after_pkg_key])
                continue
            if before_sha == after_sha:
                add_error(output, "FULL_PRESERVATION_ARMS_IDENTICAL", test_id=tid, before_package_key=before_pkg_key, after_package_key=after_pkg_key, sha256=before_sha, detail="FULL before/after packages are byte-identical; deduplication preservation guard measured no transformation")
                continue
            before_bound = validate_run_arm_binding(output, tid, before, before_sha)
            after_bound = validate_run_arm_binding(output, tid, after, after_sha)
            if not before_bound or not after_bound or before.get("status") == "INVALID" or after.get("status") == "INVALID":
                continue
            try:
                max_reg = float(guard.get("max_total_regression"))
            except Exception:
                add_error(output, "INVALID_ABLATION_FULL_REGRESSION", test_id=tid, detail="max_total_regression must be prelocked and numeric")
                continue
            before_total = Decimal(str(before.get("_comparison_recomputed_total_exact", before["recomputed_total"])))
            after_total = Decimal(str(after.get("_comparison_recomputed_total_exact", after["recomputed_total"])))
            regression = float(before_total - after_total)
            if regression > max_reg + TOL:
                add_error(output, "INVALID_ABLATION_FULL_REGRESSION", test_id=tid, before_total=before["recomputed_total"], after_total=after["recomputed_total"], regression=round(regression, 6), max_total_regression=max_reg)
                continue
            if bool(guard.get("require_no_new_mandatory_floor_failure", True)):
                bmap = {c["criterion"]: c for c in before.get("criteria", [])}
                amap = {c["criterion"]: c for c in after.get("criteria", [])}
                newly_failed = [c for c in bmap if bmap[c].get("passes_mandatory_floor") and not amap.get(c, {}).get("passes_mandatory_floor", False)]
                if newly_failed:
                    add_error(output, "INVALID_ABLATION_FULL_REGRESSION", test_id=tid, detail="new mandatory-floor failures in FULL after dedup", criteria=newly_failed)
    output["comparisons"] = comp_out


def dispatch_comparisons(contract, lock_path, suite, output, results_by_key,
                         test0007_rubric_path=None, rubric_addendum_path=None,
                         rubric_addendum_freeze_path=None, decision_rule_path=None,
                         candidate_version="") -> None:
    """Roteia entre o caminho legado e o de conjunto de comparacoes.

    Se NENHUM teste declara comparison_set, chama validate_comparisons uma vez,
    exatamente como antes — o TEST-0007 nao ve diferenca alguma.
    """
    lock = load_yaml(lock_path) if (lock_path and lock_path.exists()) else None
    lock_defs = (lock or {}).get("comparisons") or {}
    has_set = any(isinstance(d, dict) and isinstance(d.get("comparison_set"), dict)
                  for d in lock_defs.values())
    if not has_set:
        validate_comparisons(contract, lock_path, suite, output, results_by_key,
                             test0007_rubric_path, rubric_addendum_path,
                             rubric_addendum_freeze_path, decision_rule_path,
                             candidate_version)
        return

    global _COMPARISON_SET_ACTIVE
    _COMPARISON_SET_ACTIVE = True

    merged: list[dict[str, Any]] = []
    dependence: list[dict[str, Any]] = []
    identities: list[dict[str, Any]] = []
    totals_by_arm: dict[tuple[str, str], float] = {}

    for tid, ldef in lock_defs.items():
        entries = comparison_set_entries(tid, ldef)
        canon = CANONICAL_COMPARISON_SETS.get(canonical_component(tid))
        if canon is not None:
            missing = sorted(set(canon) - {c for c, _ in entries if c})
            if missing:
                add_error(output, "COMPARISON_SET_INCOMPLETE", test_id=tid,
                          missing_comparison_ids=missing,
                          detail="canonical comparison set requires every comparison to be present in the same execution")
        margins: dict[str, float] = {}
        for cid, derived in entries:
            if not validate_comparison_binding(output, tid, cid, derived):
                continue
            sub: dict[str, Any] = {"status": "VALID", "errors": [],
                                   "gate_failures": [], "inconclusive_reasons": [],
                                   "comparisons": []}
            synthetic = dict(lock or {})
            synthetic["comparisons"] = {tid: derived}
            validate_comparisons(contract, lock_path, suite, sub, results_by_key,
                                 test0007_rubric_path, rubric_addendum_path,
                                 rubric_addendum_freeze_path, decision_rule_path,
                                 candidate_version, lock_override=synthetic)
            for e in sub.get("errors") or []:
                add_error(output, e.pop("code"), comparison_id=cid, **e)
            for g in sub.get("gate_failures") or []:
                add_gate_failure(output, g.pop("code"), comparison_id=cid, **g)
            for i in sub.get("inconclusive_reasons") or []:
                add_inconclusive(output, i.pop("code"), comparison_id=cid, **i)
            for item in sub.get("comparisons") or []:
                item["comparison_id"] = cid
                merged.append(item)
                if cid:
                    margins[cid] = float(item["margin"])
                    totals_by_arm[(canonical_component(tid), canonical_component(item["left"]["arm_id"]))] = float(item["left"]["total"])
                    totals_by_arm[(canonical_component(tid), canonical_component(item["right"]["arm_id"]))] = float(item["right"]["total"])

        if canon is None:
            continue

        # ---- nao-independencia, registrada no artefato de saida
        rule = COMPARISON_INDEPENDENCE.get(canonical_component(tid))
        if rule and len(margins) > 1:
            shared = canonical_component(rule["shared_component"])
            dependence.append({"test_id": tid, "comparison_ids": sorted(margins),
                               "independent": False,
                               "shared_component": shared,
                               "reason": rule["reason"],
                               "forbidden_operations": rule["forbidden"],
                               "permitted_operations": rule["permitted"]})
            policy = (contract.get("comparative_tests") or {}).get(tid) or {}
            if bool(policy.get("treat_comparisons_as_independent")):
                add_error(output, "SHARED_BASELINE_INDEPENDENCE_VIOLATION",
                          test_id=tid, shared_component=shared,
                          detail="contract asks to treat P and F as independent, but they subtract the same baseline arm")

        # ---- identidade D = m(FULL_SKILL) - m(SUMMARY_AS_SKILL) = P - F
        if {"P", "F"} <= set(margins):
            lhs_full = totals_by_arm.get((canonical_component(tid), "FULL_SKILL"))
            lhs_sas = totals_by_arm.get((canonical_component(tid), "SUMMARY_AS_SKILL"))
            if lhs_full is not None and lhs_sas is not None:
                d_direct = lhs_full - lhs_sas
                d_from_pf = margins["P"] - margins["F"]
                closes = abs(d_direct - d_from_pf) <= TOL
                identities.append({
                    "test_id": tid, "identity": "D = m(FULL_SKILL) - m(SUMMARY_AS_SKILL) = P - F",
                    "d_direct": round(d_direct, 6), "d_from_p_minus_f": round(d_from_pf, 6),
                    "difference": round(d_direct - d_from_pf, 9),
                    "tolerance": TOL, "closes": closes,
                    "why_it_must_close": ("o baseline compartilhado cancela em P - F; "
                                          "se nao fecha, o erro e de selecao de condicao, "
                                          "de sinal ou de calculo — nunca de arredondamento")})
                if not closes:
                    add_error(output, "COMPARISON_IDENTITY_UNCLOSED", test_id=tid,
                              d_direct=round(d_direct, 6), d_from_p_minus_f=round(d_from_pf, 6),
                              detail="D = P - F does not close; condition selection, sign or arithmetic is wrong")

    output["comparisons"] = merged
    if dependence:
        output["comparison_dependence"] = dependence
    if identities:
        output["comparison_identities"] = identities


def collect_consumed_run_keys(contract: dict[str, Any], comparison_lock_path: Path | None, metric_lock_path: Path | None) -> set[tuple[str, str, str]]:
    consumed: set[tuple[str, str, str]] = set()
    agg = (contract.get("suite_aggregation") or {}).get("acceptance") or {}
    default_sel = agg.get("default_primary_run") or {"arm_id": "PRIMARY", "phase": "CURRENT"}
    overrides = agg.get("primary_run_overrides") or {}
    for tid in agg.get("test_ids") or []:
        sel = overrides.get(tid) or default_sel
        arm, phase = selector_key(sel)
        consumed.add((canonical_component(tid), arm, phase))

    if metric_lock_path is not None and metric_lock_path.exists():
        mlock = load_yaml(metric_lock_path) or {}
        for mdef in (mlock.get("metrics") or {}).values():
            if not isinstance(mdef, dict):
                continue
            for sel in (mdef.get("checks") or []) + (mdef.get("selectors") or []):
                if not isinstance(sel, dict) or not sel.get("test_id"):
                    continue
                arm, phase = selector_key(sel)
                consumed.add((canonical_component(sel.get("test_id")), arm, phase))

    if comparison_lock_path is not None and comparison_lock_path.exists():
        clock = load_yaml(comparison_lock_path) or {}
        for tid, ldef in (clock.get("comparisons") or {}).items():
            if not isinstance(ldef, dict):
                continue
            # Toda comparacao do conjunto consome os seus dois lados. Sem isto a
            # terceira condicao (SUMMARY_AS_SKILL, lado esquerdo de F) sairia
            # acusada como UNCONSUMED_RUN_SELECTOR — uma corrida real, medida e
            # usada, denunciada como orfa.
            for _cid, _d in comparison_set_entries(tid, ldef):
                for sel in [_d.get("left") or {}, _d.get("right") or {}]:
                    arm, phase = selector_key(sel)
                    consumed.add((canonical_component(tid), arm, phase))
            guard = ldef.get("full_preservation") or {}
            for sel in [guard.get("before") or {}, guard.get("after") or {}]:
                if sel:
                    arm, phase = selector_key(sel)
                    consumed.add((canonical_component(tid), arm, phase))
    return consumed


def validate_consumed_runs(contract: dict[str, Any], comparison_lock_path: Path | None, metric_lock_path: Path | None, output: dict[str, Any], results_by_key: dict[tuple[str, str, str], dict[str, Any]]) -> None:
    consumed = collect_consumed_run_keys(contract, comparison_lock_path, metric_lock_path)
    for key, result in results_by_key.items():
        if key not in consumed:
            add_error(
                result,
                "UNCONSUMED_RUN_SELECTOR",
                test_id=result.get("test_id"),
                arm_id=result.get("arm_id"),
                phase=result.get("phase"),
                normalized_key=list(key),
                detail="run is not consumed by suite aggregation, metric derivation, comparison, or preservation selectors",
            )

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-version", required=True, help="Candidate version without v prefix (X.Y.Z)")
    ap.add_argument("--suite", required=True)
    ap.add_argument("--contract", required=True)
    ap.add_argument("--scores", required=True)
    ap.add_argument("--raw-root", default=".")
    ap.add_argument("--comparison-lock")
    ap.add_argument("--metric-lock")
    ap.add_argument("--pre-run-lock-registry")
    ap.add_argument("--pre-run-opening-record")
    ap.add_argument("--test0007-rubric")
    ap.add_argument("--rubric-addendum")
    ap.add_argument("--rubric-addendum-freeze-record")
    ap.add_argument("--decision-rule")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    candidate_version = str(args.candidate_version).strip()
    if not CANDIDATE_VERSION_RE.fullmatch(candidate_version):
        print("INVALID: --candidate-version must be X.Y.Z without a v prefix")
        return 2

    suite_path = Path(args.suite)
    contract_path = Path(args.contract)
    scores_path = Path(args.scores)
    raw_root = Path(args.raw_root)
    comparison_lock_path = Path(args.comparison_lock) if args.comparison_lock else None
    metric_lock_path = Path(args.metric_lock) if args.metric_lock else None
    pre_run_registry_path = Path(args.pre_run_lock_registry) if args.pre_run_lock_registry else None
    pre_run_opening_record_path = Path(args.pre_run_opening_record) if args.pre_run_opening_record else None
    test0007_rubric_path = Path(args.test0007_rubric) if args.test0007_rubric else None
    rubric_addendum_path = Path(args.rubric_addendum) if args.rubric_addendum else None
    rubric_addendum_freeze_path = Path(args.rubric_addendum_freeze_record) if args.rubric_addendum_freeze_record else None
    decision_rule_path = Path(args.decision_rule) if args.decision_rule else None

    suite = load_suite(suite_path)
    contract = load_yaml(contract_path) or {}
    scores = load_yaml(scores_path) or {}
    runs = scores.get("runs") or []
    quote_min_chars = int((contract.get("raw_output_requirements") or {}).get("minimum_quote_chars", QUOTE_MIN_CHARS_DEFAULT))

    output: dict[str, Any] = {
        "schema_version": "0.4.0",
        "candidate_version": candidate_version,
        "scorer_revision": "REV5-F3-TRISTATE-PRELOCK-PATCH",
        "status": "VALID",
        "runs": [],
        "comparisons": [],
        "derived_metrics": {},
        "errors": [],
        "gate_failures": [],
        "inconclusive_reasons": [],
        "raw_output_hashes": [],
    }

    results_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    raw_paths: list[Path] = []
    seen_run_keys: set[tuple[str, str, str]] = set()

    test0007_control_floor_exceptions: set[str] = set()
    test0007_anchors: dict[str, dict[str, dict[str, Any]]] = {}
    if "TEST-0007" in suite and test0007_rubric_path and rubric_addendum_path and rubric_addendum_freeze_path:
        try:
            _ov, _ev = verify_test0007_addendum(test0007_rubric_path, rubric_addendum_path, rubric_addendum_freeze_path, suite["TEST-0007"], {"arm_id":"ABLATED","phase":"AFTER_DEDUP"})
            test0007_control_floor_exceptions = set(_ov)
            test0007_anchors = test0007_anchor_catalog(test0007_rubric_path, rubric_addendum_path)
        except Exception as exc:
            add_error(output, "MARGIN_THRESHOLD_UNREACHABLE", test_id="TEST-0007", detail=f"cannot initialize frozen TEST-0007 addendum semantics: {exc}")

    for run in runs:
        tid = run.get("test_id")
        arm = run.get("arm_id") or "PRIMARY"
        phase = run.get("phase") or "CURRENT"
        key = run_key(run)
        result: dict[str, Any] = {
            "test_id": tid,
            "arm_id": arm,
            "phase": phase,
            "normalized_key": list(key),
            "status": "VALID",
            "errors": [],
            "gate_failures": [],
            "inconclusive_reasons": [],
            "expected_control_floor_failures": [],
        }
        if key in seen_run_keys:
            add_error(result, "DUPLICATE_RUN_KEY", test_id=tid, arm_id=arm, phase=phase, normalized_key=list(key), detail="duplicate normalized test_id + arm_id + phase")
            result["recomputed_total"] = None
            result["declared_total"] = run.get("declared_total")
            result["criteria"] = []
            output["runs"].append(result)
            continue
        seen_run_keys.add(key)
        test = suite.get(tid) or suite.get(canonical_component(tid))
        if not test:
            add_error(result, "UNDEFINED_AGGREGATION", detail=f"unknown test_id: {tid}")
            output["runs"].append(result)
            results_by_key[key] = result
            continue

        raw_ok, raw_why, raw_path, observed_hash, raw_header, raw_header_error = verify_run_raw(run, raw_root)
        result["raw_header"] = raw_header
        if raw_header_error:
            result["raw_header_error"] = raw_header_error
        if raw_path is not None and raw_path.exists():
            raw_paths.append(raw_path)
            output["raw_output_hashes"].append({"test_id": tid, "arm_id": arm, "phase": phase, "path": run.get("raw_output_path"), "sha256": observed_hash or sha256_file(raw_path)})
        if not raw_ok:
            add_error(result, "RAW_OUTPUT_HASH_MISMATCH", detail=raw_why)

        rubric = (test.get("evaluation") or {}).get("rubric") or []
        expected = {canonical_component(r["criterion"]): r for r in rubric}
        actual_rows = run.get("criteria") or []
        actual_names = [canonical_component(r.get("criterion")) for r in actual_rows if r.get("criterion")]
        duplicates = sorted({name for name in actual_names if actual_names.count(name) > 1})
        if duplicates:
            add_error(result, "DUPLICATE_CRITERION_ROW", criteria=duplicates, detail="criterion appears more than once within the same run")
            result["recomputed_total"] = None
            result["declared_total"] = run.get("declared_total")
            result["criteria"] = []
            output["runs"].append(result)
            results_by_key[key] = result
            continue
        actual = {canonical_component(r.get("criterion")): r for r in actual_rows if r.get("criterion")}

        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing or extra:
            add_error(result, "MISSING_CRITERION_ROW", missing=missing, extra=extra)
            result["recomputed_total"] = None
            result["declared_total"] = run.get("declared_total")
            result["criteria"] = []
            output["runs"].append(result)
            results_by_key[key] = result
            continue

        recomputed = 0.0
        recomputed_exact = Decimal("0")
        weight_sum = 0.0
        criterion_results = []
        for cname_key, erow in expected.items():
            cname = erow.get("criterion")
            arow = actual.get(cname_key)
            if not arow:
                continue
            ew = float(erow["weight"])
            try:
                aw = float(arow.get("weight"))
                score = float(arow.get("score"))
            except Exception:
                add_error(result, "RUBRIC_WEIGHT_MISMATCH", criterion=cname, detail="score or weight not numeric")
                continue
            if not math.isfinite(score) or not (0 <= score <= 100):
                add_error(result, "RUBRIC_WEIGHT_MISMATCH", criterion=cname, detail="score outside 0..100")
                continue
            if canonical_component(tid) == "TEST-0007" and not score.is_integer():
                add_error(result, "NON_INTEGER_CRITERION_SCORE", criterion=cname, score=arow.get("score"), detail="TEST-0007 criterion scores must be integers so the locked 0.2-point margin grid is an enforced invariant")
            if not math.isfinite(aw) or abs(aw - ew) > 1e-12:
                add_error(result, "RUBRIC_WEIGHT_MISMATCH", criterion=cname, expected=ew, actual=aw)
            if bool(arow.get("mandatory")) != bool(erow.get("mandatory")):
                add_error(result, "RUBRIC_WEIGHT_MISMATCH", criterion=cname, detail="mandatory flag mismatch")

            has_min, emin = expected_minimum(erow)
            actual_has_min = "minimum_score" in arow and arow.get("minimum_score") is not None
            if has_min != actual_has_min:
                add_error(result, "RUBRIC_WEIGHT_MISMATCH", criterion=cname, detail="minimum_score presence mismatch")
            elif has_min:
                try:
                    amin = float(arow.get("minimum_score"))
                except Exception:
                    amin = math.nan
                if not math.isfinite(amin) or abs(amin - float(emin)) > 1e-12:
                    add_error(result, "RUBRIC_WEIGHT_MISMATCH", criterion=cname, detail="minimum_score value mismatch", expected=emin, actual=arow.get("minimum_score"))

            ev = arow.get("evidence") or {}
            ev_ok, ev_code, ev_why = verify_evidence(ev, run.get("raw_output_path") or "", raw_root, quote_min_chars)
            if not ev_ok:
                add_error(result, ev_code, criterion=cname, detail=ev_why)

            selected_anchor = arow.get("selected_anchor")
            anchor_ambiguity = arow.get("anchor_ambiguity")
            alternative_anchor = arow.get("alternative_anchor")
            if canonical_component(tid) == "TEST-0007":
                catalog = test0007_anchors.get(cname_key) or {}
                if not selected_anchor or str(selected_anchor) not in catalog or not isinstance(anchor_ambiguity, bool):
                    add_error(result, "MISSING_ANCHOR_ASSESSMENT", criterion=cname, selected_anchor=selected_anchor, anchor_ambiguity=anchor_ambiguity, detail="TEST-0007 requires a valid selected_anchor and boolean anchor_ambiguity for every criterion")
                else:
                    rng=(catalog.get(str(selected_anchor)) or {}).get("range") or []
                    if len(rng)!=2 or score < float(rng[0])-TOL or score > float(rng[1])+TOL:
                        add_error(result, "ANCHOR_SCORE_MISMATCH", criterion=cname, selected_anchor=selected_anchor, score=score, anchor_range=rng)
                    if anchor_ambiguity:
                        if not alternative_anchor or str(alternative_anchor)==str(selected_anchor) or str(alternative_anchor) not in catalog:
                            add_error(result, "MISSING_ANCHOR_ASSESSMENT", criterion=cname, detail="anchor_ambiguity=true requires a distinct valid alternative_anchor")
                if len(norm(str(arow.get("rationale") or ""))) < 20:
                    add_error(result, "MISSING_ANCHOR_ASSESSMENT", criterion=cname, detail="criterion rationale must contain at least 20 normalized characters")

            wp = score * ew
            wp_exact = Decimal(str(arow.get("score"))) * Decimal(str(erow["weight"]))
            declared_wp = arow.get("weighted_points")
            if declared_wp is None:
                add_error(result, "DECLARED_TOTAL_MISMATCH", criterion=cname, detail="weighted_points missing")
            else:
                try:
                    dwp = float(declared_wp)
                except Exception:
                    dwp = math.nan
                if not math.isfinite(dwp) or abs(dwp - wp) > TOL:
                    add_error(result, "DECLARED_TOTAL_MISMATCH", criterion=cname, expected_weighted_points=round(wp, 6), declared_weighted_points=declared_wp)

            passes_floor = True
            if bool(erow.get("mandatory")):
                if not has_min:
                    add_error(result, "RUBRIC_WEIGHT_MISMATCH", criterion=cname, detail="mandatory criterion lacks minimum_score in locked suite")
                    passes_floor = False
                else:
                    passes_floor = score + TOL >= float(emin)
                    if not passes_floor:
                        expected_control_exception = (
                            key == ("TEST-0007", "ABLATED", "AFTER_DEDUP")
                            and cname_key in test0007_control_floor_exceptions
                        )
                        if expected_control_exception:
                            result.setdefault("expected_control_floor_failures", []).append({"criterion":cname,"score":score,"minimum_score":emin,"source":"FROZEN_D2_CONTROL_SEMANTICS"})
                        else:
                            add_gate_failure(result, "MANDATORY_FLOOR_FAILURE", criterion=cname, score=score, minimum_score=emin)

            recomputed += wp
            recomputed_exact += wp_exact
            weight_sum += ew
            criterion_results.append({
                "criterion": cname,
                "score": score,
                "weight": ew,
                "minimum_score": emin if has_min else None,
                "weighted_points": round(wp, 6),
                "passes_mandatory_floor": passes_floor,
                "selected_anchor": selected_anchor if canonical_component(tid)=="TEST-0007" else None,
                "anchor_ambiguity": anchor_ambiguity if canonical_component(tid)=="TEST-0007" else None,
                "alternative_anchor": alternative_anchor if canonical_component(tid)=="TEST-0007" and anchor_ambiguity is True else None,
            })

        result["criteria"] = criterion_results
        if canonical_component(tid) == "TEST-0007":
            validate_test0007_critical_failures(run, result, raw_root, quote_min_chars)

        if abs(weight_sum - 1.0) > 1e-12:
            add_error(result, "UNDEFINED_AGGREGATION", detail="rubric weights do not sum to 1.0", weight_sum=weight_sum)

        declared_total = run.get("declared_total")
        if declared_total is None:
            add_error(result, "DECLARED_TOTAL_MISMATCH", recomputed=round(recomputed, 6), declared=None)
        else:
            try:
                dtotal = float(declared_total)
            except Exception:
                dtotal = math.nan
            if not math.isfinite(dtotal) or abs(dtotal - recomputed) > TOL:
                add_error(result, "DECLARED_TOTAL_MISMATCH", recomputed=round(recomputed, 6), declared=declared_total)

        if canonical_component(tid) == "TEST-0007":
            result["_comparison_recomputed_total_exact"] = format(recomputed_exact, "f")
        result["recomputed_total"] = round(recomputed, 6)
        result["declared_total"] = declared_total
        result["criteria"] = criterion_results
        output["runs"].append(result)
        results_by_key[key] = result

    # Instrument-level checks. Invalidity always dominates gate failure.
    # Temporal lock precedence is content-addressed through the pre-run registry;
    # filesystem mtimes are never used as evidence.
    additional_pre_run_artifacts = {}
    if test0007_rubric_path is not None:
        additional_pre_run_artifacts["test0007_rubric"] = test0007_rubric_path
    if rubric_addendum_path is not None:
        additional_pre_run_artifacts["rubric_anchor_addendum"] = rubric_addendum_path
    if rubric_addendum_freeze_path is not None:
        additional_pre_run_artifacts["rubric_anchor_addendum_freeze_record"] = rubric_addendum_freeze_path
    if decision_rule_path is not None:
        additional_pre_run_artifacts["test0007_decision_rule"] = decision_rule_path
    validate_pre_run_registry(pre_run_registry_path, pre_run_opening_record_path, comparison_lock_path, metric_lock_path, output, additional_artifacts=additional_pre_run_artifacts)
    validate_aggregation(contract, output, results_by_key)
    validate_metric_derivation(contract, metric_lock_path, output, results_by_key)
    dispatch_comparisons(contract, comparison_lock_path, suite, output, results_by_key, test0007_rubric_path, rubric_addendum_path, rubric_addendum_freeze_path, decision_rule_path, candidate_version)
    validate_consumed_runs(contract, comparison_lock_path, metric_lock_path, output, results_by_key)
    if comparison_lock_path is not None and comparison_lock_path.exists():
        output["comparison_lock"] = {"path": str(comparison_lock_path), "sha256": sha256_file(comparison_lock_path)}
    if metric_lock_path is not None and metric_lock_path.exists():
        output["metric_lock"] = {"path": str(metric_lock_path), "sha256": sha256_file(metric_lock_path)}

    # Bubble run errors/gates to top level.
    for r in output["runs"]:
        output["errors"].extend(r.get("errors", []))
        output["gate_failures"].extend(r.get("gate_failures", []))
        output["inconclusive_reasons"].extend(r.get("inconclusive_reasons", []))

    if output["errors"] or any(r.get("status") == "INVALID" for r in output["runs"]):
        output["status"] = "INVALID"
    elif output["gate_failures"] or any(r.get("status") == "FAIL" for r in output["runs"]):
        output["status"] = "FAIL"
    elif output["inconclusive_reasons"] or any(r.get("status") == "INCONCLUSIVE" for r in output["runs"]):
        output["status"] = "INCONCLUSIVE"
    else:
        output["status"] = "VALID"

    # Fail closed if the script produces an invalidation code not declared by the contract,
    # or the contract declares a code the scorer cannot name. This keeps promise == implementation.
    declared_codes = set(contract.get("run_invalidation_codes") or [])
    if declared_codes:
        # Registro EFETIVO: os codigos da extensao de duas comparacoes so contam
        # quando um comparison_set foi de fato despachado. Um teste sem conjunto
        # — o TEST-0007 — compara contra exatamente o registro original.
        effective_codes = INVALIDATION_CODES | (COMPARISON_SET_CODES if _COMPARISON_SET_ACTIVE else set())
        unknown_declared = sorted(declared_codes - effective_codes)
        missing_declared = sorted(effective_codes - declared_codes)
        if unknown_declared or missing_declared:
            output["status"] = "INVALID"
            output["errors"].append({"code": "UNDEFINED_AGGREGATION", "detail": "contract/scorer invalidation code registry mismatch", "unknown_declared": unknown_declared, "missing_declared": missing_declared})

    # Internal exact totals are comparison inputs only; six-decimal rounding remains an output concern.
    for _run in output.get("runs", []):
        _run.pop("_comparison_recomputed_total_exact", None)
    Path(args.out).write_text(yaml.safe_dump(output, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"{output['status']}: wrote {args.out}")
    if output["status"] == "VALID":
        return 0
    if output["status"] == "FAIL":
        return 1
    if output["status"] == "INCONCLUSIVE":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
