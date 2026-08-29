#!/usr/bin/env python3
"""Freeze a reachable, auditable comparison-margin lock for a parameterized PILOT-001 candidate version.

PRE-RUN instrument step. Refuses to emit LOCKED when:
- threshold is non-positive or not justified against the effective ceiling;
- threshold exceeds arithmetic/structural reachability;
- structural report content does not bind the declared ceiling to frozen arm hashes;
- comparison arm package hashes are absent/malformed;
- FULL preservation guard is undefined.

Exit codes:
  0 = lock frozen successfully
  2 = instrument invalid / lock refused
"""
from __future__ import annotations

import argparse
import hashlib
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

TOL = 0.01
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
CANDIDATE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


# ---------------------------------------------------------------------------
# EXTENSÃO: duas comparações dentro de um mesmo teste (ver scorer-v2).
# A ligação comparison_id -> (esquerda, direita) é a MESMA constante do scorer,
# repetida aqui de propósito: o freezer e o scorer têm de recusar a mesma troca
# de seletores, e um import entre os dois criaria acoplamento onde hoje há dois
# guardas independentes.
CANONICAL_COMPARISON_SETS: dict[str, dict[str, tuple[str, str]]] = {
    "TEST-0008": {
        "P": ("FULL_SKILL", "SUMMARY_AS_SUMMARY"),
        "F": ("SUMMARY_AS_SKILL", "SUMMARY_AS_SUMMARY"),
    },
}


def expand_for_freeze(comparisons_policy: dict, defs: dict, errors: list):
    """Percorre (tid, policy, comparison_id, definicao).

    Lock legado -> uma entrada com comparison_id None: o TEST-0007, intocado.
    comparison_set -> uma entrada por comparison_id, MATERIALIZADA no rascunho,
    para que cada comparacao carregue os seus proprios hashes e tetos depois de
    congelada e nenhuma dependa de heranca implicita na hora da leitura.
    """
    for tid, policy in comparisons_policy.items():
        ldef = defs.get(tid)
        canon = CANONICAL_COMPARISON_SETS.get(canonical(tid))
        cset = ldef.get("comparison_set") if isinstance(ldef, dict) else None
        if not isinstance(cset, dict):
            if canon is not None:
                errors.append({"code": "COMPARISON_ID_MISSING", "test_id": tid,
                               "expected_comparison_ids": sorted(canon),
                               "detail": "test declares a canonical comparison set; a single flat comparison is not accepted"})
                continue
            yield tid, policy, None, ldef
            continue
        if canon is None:
            errors.append({"code": "UNKNOWN_COMPARISON_ID", "test_id": tid,
                           "detail": "comparison_set given for a test with no canonical comparison set"})
            continue
        missing = sorted(set(canon) - set(cset))
        if missing:
            errors.append({"code": "COMPARISON_SET_INCOMPLETE", "test_id": tid,
                           "missing_comparison_ids": missing,
                           "detail": "every comparison of the canonical set must be frozen in the same lock"})
            continue
        shared = {k: v for k, v in ldef.items() if k != "comparison_set"}
        for cid in sorted(cset):
            entry = cset[cid]
            if not isinstance(entry, dict):
                errors.append({"code": "UNKNOWN_COMPARISON_ID", "test_id": tid,
                               "comparison_id": cid, "detail": "comparison entry is not a mapping"})
                continue
            if cid not in canon:
                errors.append({"code": "UNKNOWN_COMPARISON_ID", "test_id": tid,
                               "comparison_id": cid, "known_comparison_ids": sorted(canon),
                               "detail": "comparison_id is not part of the canonical comparison set"})
                continue
            for k, v in shared.items():
                entry.setdefault(k, v)
            want_left, want_right = canon[cid]
            got_left = canonical((entry.get("left") or {}).get("arm_id"))
            got_right = canonical((entry.get("right") or {}).get("arm_id"))
            if (got_left, got_right) != (want_left, want_right):
                errors.append({"code": "COMPARISON_SELECTOR_BINDING_MISMATCH",
                               "test_id": tid, "comparison_id": cid,
                               "expected": {"left": want_left, "right": want_right},
                               "observed": {"left": got_left, "right": got_right},
                               "detail": "selectors do not match the canonical binding frozen in the freezer"})
                continue
            yield tid, policy, cid, entry


def _tag_errors(errors: list, mark: int, cid) -> None:
    if cid is None:
        return
    for e in errors[mark:]:
        e.setdefault("comparison_id", cid)


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_suite(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        docs = [d for d in yaml.safe_load_all(f) if isinstance(d, dict) and d.get("test_id")]
    return {str(d["test_id"]).strip().upper(): d for d in docs}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def canonical(value: Any) -> str:
    return str(value or "").strip().upper()


def arm_hash_value(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("sha256")
    if value is None:
        return None
    return str(value).lower()


def selector_key(sel: dict[str, Any]) -> tuple[str, str]:
    return canonical(sel.get("arm_id") or "PRIMARY"), canonical(sel.get("phase") or "CURRENT")


def arm_phase_key(sel: dict[str, Any]) -> str:
    arm, phase = selector_key(sel)
    return f"{arm}@{phase}"


def arithmetic_ceiling(test: dict[str, Any], floor_overrides: dict[str, float] | None = None) -> tuple[float, list[dict[str, Any]]]:
    """Arithmetic upper bound for LEFT-RIGHT margin.

    Default floor is the mandatory minimum_score (or 0 for non-mandatory).
    A frozen rubric addendum may predeclare right-arm fail-closed criteria whose
    honest score can legitimately be below the mandatory floor; for reachability
    only, those criteria use an explicit right-floor override (currently 0).
    """
    rubric = (test.get("evaluation") or {}).get("rubric") or []
    floor_overrides = {canonical(k): float(v) for k, v in (floor_overrides or {}).items()}
    total = 0.0
    rows = []
    for row in rubric:
        w = float(row["weight"])
        mandatory = bool(row.get("mandatory"))
        cname = canonical(row.get("criterion"))
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
        c = w * (100.0 - floor)
        total += c
        rows.append({"criterion": row.get("criterion"), "weight": w, "floor": floor, "floor_source": floor_source, "ceiling_contribution": round(c, 6)})
    return round(total, 6), rows


def verify_test0007_addendum(base_rubric_path: Path | None, addendum_path: Path | None, freeze_record_path: Path | None, test: dict[str, Any], right_selector: dict[str, Any]) -> tuple[dict[str, float], dict[str, Any]]:
    """Verify the D1/D2 frozen addendum chain and return arithmetic floor overrides.

    The override is accepted only when the frozen base rubric itself contains the
    named fail-closed score anchor whose entire range lies below the mandatory floor.
    This prevents an addendum from inventing a lower right-arm floor post hoc.
    """
    if not base_rubric_path or not addendum_path or not freeze_record_path:
        raise ValueError("TEST-0007 requires frozen rubric, rubric addendum, and addendum freeze record before margin lock freeze")
    for pp in (base_rubric_path, addendum_path, freeze_record_path):
        if not pp.exists():
            raise ValueError(f"required rubric/addendum artifact missing: {pp}")
    base = load_yaml(base_rubric_path) or {}
    add = load_yaml(addendum_path) or {}
    fr = load_yaml(freeze_record_path) or {}
    if canonical(base.get("test_id")) != "TEST-0007":
        raise ValueError("base rubric test_id must be TEST-0007")
    if add.get("artifact_status") != "FROZEN_PRE_RUN_ADDENDUM" or canonical(add.get("test_id")) != "TEST-0007":
        raise ValueError("rubric addendum must be FROZEN_PRE_RUN_ADDENDUM for TEST-0007")
    if fr.get("artifact_status") != "FROZEN_PRE_RUN_ADDENDUM_RECORD" or canonical(fr.get("test_id")) != "TEST-0007":
        raise ValueError("rubric addendum freeze record is invalid")
    if str((add.get("base_rubric") or {}).get("sha256") or "").lower() != sha256_file(base_rubric_path).lower():
        raise ValueError("addendum base_rubric hash mismatch")
    if str((fr.get("base_chain") or {}).get("rubric", {}).get("sha256") or "").lower() != sha256_file(base_rubric_path).lower():
        raise ValueError("addendum freeze record base rubric hash mismatch")
    if str((fr.get("addendum") or {}).get("sha256") or "").lower() != sha256_file(addendum_path).lower():
        raise ValueError("addendum freeze record addendum hash mismatch")

    # Core rubric identity must match the suite used by the freezer.
    base_rows = {canonical(r.get("criterion")): r for r in (base.get("rubric") or [])}
    suite_rows = {canonical(r.get("criterion")): r for r in ((test.get("evaluation") or {}).get("rubric") or [])}
    if set(base_rows) != set(suite_rows):
        raise ValueError("TEST-0007 base rubric criteria differ from locked suite")
    for cname, brow in base_rows.items():
        srow = suite_rows[cname]
        for field in ("weight", "mandatory", "minimum_score"):
            if brow.get(field) != srow.get(field):
                raise ValueError(f"TEST-0007 base rubric {field} mismatch for {cname}")

    cfg = add.get("comparison_arithmetic_ceiling") or {}
    if canonical(cfg.get("test_id")) != "TEST-0007":
        raise ValueError("addendum arithmetic ceiling section must target TEST-0007")
    expected_right = arm_phase_key(right_selector)
    if canonical(cfg.get("right_selector")) != expected_right:
        raise ValueError(f"addendum right_selector must match comparison right arm {expected_right}")
    overrides: dict[str, float] = {}
    for raw_name, spec in (cfg.get("right_floor_overrides") or {}).items():
        cname = canonical(raw_name)
        if cname not in base_rows:
            raise ValueError(f"addendum floor override references unknown criterion {raw_name}")
        brow = base_rows[cname]
        if not bool(brow.get("mandatory")) or brow.get("minimum_score") is None:
            raise ValueError(f"floor override is only valid for mandatory criterion with minimum_score: {raw_name}")
        if spec.get("basis") != "PREDECLARED_FAIL_CLOSED_BELOW_MANDATORY_FLOOR":
            raise ValueError(f"invalid floor override basis for {raw_name}")
        anchor_name = spec.get("base_score_anchor")
        anchor = ((brow.get("score_anchors") or {}).get(anchor_name) or {})
        rng = anchor.get("range") or []
        if len(rng) != 2:
            raise ValueError(f"base score anchor missing/invalid for {raw_name}")
        floor = float(spec.get("right_floor_for_ceiling"))
        mandatory_floor = float(brow.get("minimum_score"))
        if float(rng[1]) >= mandatory_floor:
            raise ValueError(f"base fail-closed anchor for {raw_name} is not wholly below mandatory floor")
        if floor != 0.0:
            raise ValueError(f"REV5 D2 only permits explicit right_floor_for_ceiling=0 for {raw_name}")
        if float(spec.get("base_mandatory_minimum_score")) != mandatory_floor:
            raise ValueError(f"addendum mandatory floor evidence mismatch for {raw_name}")
        if list(spec.get("base_anchor_range") or []) != list(rng):
            raise ValueError(f"addendum anchor range evidence mismatch for {raw_name}")
        overrides[cname] = floor

    # D1: full execution CONSISTENCY anchor must exist in the addendum and sit above its floor.
    cons = ((add.get("anchor_additions") or {}).get("CONSISTENCY") or {}).get("full_execution") or {}
    crange = cons.get("range") or []
    if len(crange) != 2 or float(crange[0]) < float(base_rows["CONSISTENCY"].get("minimum_score")) or len(str(cons.get("condition") or "").strip()) < 20:
        raise ValueError("D1 CONSISTENCY full_execution anchor missing or insufficient")
    evidence = {
        "base_rubric_path": base_rubric_path.name,
        "base_rubric_sha256": sha256_file(base_rubric_path),
        "addendum_path": addendum_path.name,
        "addendum_sha256": sha256_file(addendum_path),
        "addendum_freeze_record_path": freeze_record_path.name,
        "addendum_freeze_record_sha256": sha256_file(freeze_record_path),
        "right_selector": expected_right,
        "right_floor_overrides": {k: v for k, v in overrides.items()},
    }
    return overrides, evidence


def validate_justification(contract: dict[str, Any], ldef: dict[str, Any], effective: float, threshold: float, decision_rule: dict[str, Any] | None = None) -> str | None:
    just = ldef.get("threshold_justification")
    if not isinstance(just, dict):
        return "threshold_justification is required"
    expected_basis = "FROZEN_ANCHOR_BOUNDARY" if decision_rule is not None else "EFFECTIVE_CEILING"
    if just.get("basis") != expected_basis:
        return f"threshold_justification.basis must be {expected_basis}"
    rationale = norm(str(just.get("rationale") or ""))
    if len(rationale) < 20:
        return "threshold_justification.rationale must contain at least 20 normalized characters"
    distinguishability = norm(str(just.get("distinguishability_rationale") or ""))
    if len(distinguishability) < 20:
        return "threshold_justification.distinguishability_rationale must contain at least 20 normalized characters"
    try:
        ref = float(just.get("effective_ceiling_reference"))
        frac = float(just.get("threshold_fraction_of_effective_ceiling"))
    except Exception:
        return "threshold justification requires numeric effective_ceiling_reference and threshold_fraction_of_effective_ceiling"
    if not math.isfinite(ref) or abs(ref - effective) > TOL:
        return "effective_ceiling_reference differs from computed effective ceiling"
    reqs = ((contract.get("comparison_lock_requirements") or {}).get("threshold_justification_required") or {})
    min_frac = float(reqs.get("minimum_fraction_of_effective_ceiling", 0.05))
    if not math.isfinite(min_frac) or min_frac <= 0 or min_frac > 1:
        return "contract minimum_fraction_of_effective_ceiling must be in (0,1]"
    if effective <= 0 or not math.isfinite(frac) or frac < min_frac - 1e-12 or frac > 1 + TOL:
        return f"threshold fraction must be >= {min_frac:g} and <= 1"
    if abs(frac - threshold / effective) > 1e-6:
        return "threshold fraction does not equal margin_threshold / effective_ceiling"
    if decision_rule is not None:
        try:
            boundary=float((decision_rule.get("margin_center") or {}).get("value"))
            declared=float(just.get("anchor_boundary_reference"))
        except Exception:
            return "FROZEN_ANCHOR_BOUNDARY justification requires numeric anchor_boundary_reference"
        if abs(boundary-threshold)>TOL or abs(declared-boundary)>TOL:
            return "anchor boundary reference does not match frozen decision rule and threshold"
    return None


def fail(code: str, **detail: Any) -> int:
    print(yaml.safe_dump({"status": "INVALID", "code": code, **detail}, sort_keys=False, allow_unicode=True))
    return 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-version", required=True, help="Candidate version without v prefix, e.g. 0.1.4")
    ap.add_argument("--suite", required=True)
    ap.add_argument("--contract", required=True)
    ap.add_argument("--draft", required=True)
    ap.add_argument("--structural-report")
    ap.add_argument("--test0007-rubric")
    ap.add_argument("--rubric-addendum")
    ap.add_argument("--rubric-addendum-freeze-record")
    ap.add_argument("--decision-rule")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    candidate_version = str(args.candidate_version).strip()
    if not CANDIDATE_VERSION.fullmatch(candidate_version):
        return fail("INVALID_CANDIDATE_VERSION", detail="--candidate-version must be X.Y.Z without a v prefix")

    suite = load_suite(Path(args.suite))
    contract = load_yaml(Path(args.contract)) or {}
    draft = load_yaml(Path(args.draft)) or {}
    report_path = Path(args.structural_report) if args.structural_report else None
    report = load_yaml(report_path) if report_path and report_path.exists() else None
    test0007_rubric_path = Path(args.test0007_rubric) if args.test0007_rubric else None
    rubric_addendum_path = Path(args.rubric_addendum) if args.rubric_addendum else None
    rubric_addendum_freeze_path = Path(args.rubric_addendum_freeze_record) if args.rubric_addendum_freeze_record else None
    decision_rule_path = Path(args.decision_rule) if args.decision_rule else None
    decision_rule = load_yaml(decision_rule_path) if decision_rule_path and decision_rule_path.exists() else None

    if str(draft.get("candidate_version") or "").strip() != candidate_version:
        return fail("CANDIDATE_VERSION_MISMATCH", detail="draft candidate_version differs from --candidate-version")
    if isinstance(report, dict) and report.get("candidate_version") is not None and str(report.get("candidate_version")).strip() != candidate_version:
        return fail("CANDIDATE_VERSION_MISMATCH", detail="structural report candidate_version differs from --candidate-version")

    if draft.get("artifact_status") not in {"TEMPLATE_ONLY_NOT_LOCKED", "DRAFT_NOT_LOCKED"}:
        return fail("POST_HOC_MARGIN_THRESHOLD", detail="draft must not already claim LOCKED status")

    comparisons_policy = contract.get("comparative_tests") or {}
    defs = draft.get("comparisons") or {}
    errors: list[dict[str, Any]] = []

    _expanded = list(expand_for_freeze(comparisons_policy, defs, errors))
    _mark, _cid_prev = len(errors), None
    for tid, policy, _cid, ldef in _expanded:
        # Marca os erros da iteracao ANTERIOR com o seu comparison_id. Feito na
        # entrada, e nao na saida, porque o corpo tem varios `continue`.
        _tag_errors(errors, _mark, _cid_prev)
        _mark, _cid_prev = len(errors), _cid
        tid_key = canonical(tid)
        test = suite.get(tid_key)
        if not isinstance(ldef, dict) or not test:
            errors.append({"code": "POST_HOC_MARGIN_THRESHOLD", "test_id": tid, "detail": "comparison definition or test missing"})
            continue
        try:
            threshold = float(ldef.get("margin_threshold"))
        except Exception:
            errors.append({"code": "INVALID_MARGIN_THRESHOLD", "test_id": tid, "detail": "margin_threshold must be set and numeric before freezing"})
            continue
        if not math.isfinite(threshold) or threshold <= 0:
            errors.append({"code": "INVALID_MARGIN_THRESHOLD", "test_id": tid, "detail": "margin_threshold must be finite and strictly positive"})
            continue

        active_decision_rule = None
        if tid_key == "TEST-0007":
            if not isinstance(decision_rule, dict) or decision_rule.get("artifact_status") != "FROZEN_PRE_RUN_DECISION_RULE" or canonical(decision_rule.get("test_id")) != "TEST-0007":
                errors.append({"code":"DECISION_RULE_MISMATCH","test_id":tid,"detail":"frozen TEST-0007 decision rule is required before margin lock freeze"})
                continue
            try:
                boundary=float((decision_rule.get("margin_center") or {}).get("value"))
            except Exception:
                errors.append({"code":"DECISION_RULE_MISMATCH","test_id":tid,"detail":"decision rule boundary is invalid"})
                continue
            if abs(boundary-threshold)>TOL:
                errors.append({"code":"DECISION_RULE_MISMATCH","test_id":tid,"detail":"draft margin_threshold differs from frozen anchor boundary","decision_rule_boundary":boundary,"draft_threshold":threshold})
                continue
            active_decision_rule=decision_rule
            ldef["decision_rule_evidence"]={"path":decision_rule_path.name,"sha256":sha256_file(decision_rule_path)}

        floor_overrides: dict[str, float] = {}
        addendum_evidence: dict[str, Any] | None = None
        if tid_key == "TEST-0007":
            try:
                floor_overrides, addendum_evidence = verify_test0007_addendum(
                    test0007_rubric_path, rubric_addendum_path, rubric_addendum_freeze_path, test, ldef.get("right") or {}
                )
            except Exception as exc:
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": f"rubric addendum/D2 ceiling basis invalid: {exc}"})
                continue
        try:
            arith, components = arithmetic_ceiling(test, floor_overrides=floor_overrides)
        except Exception as exc:
            errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": str(exc)})
            continue
        ldef["arithmetic_ceiling"] = arith
        ldef["arithmetic_ceiling_components"] = components
        if addendum_evidence is not None:
            ldef["rubric_addendum_evidence"] = addendum_evidence

        # C1: bind packages by arm_id + phase, not arm_id alone. FULL before and
        # after dedup are distinct frozen packages and both must be represented.
        arm_hashes_in = ldef.get("arm_package_hashes") or {}
        normalized_hashes = {canonical(k): arm_hash_value(v) for k, v in arm_hashes_in.items()}
        left_sel = ldef.get("left") or {}
        right_sel = ldef.get("right") or {}
        required_keys = [arm_phase_key(left_sel), arm_phase_key(right_sel)]
        guard = ldef.get("full_preservation") or {}
        if bool(policy.get("full_preservation_guard_required")):
            required_keys += [arm_phase_key(guard.get("before") or {}), arm_phase_key(guard.get("after") or {})]
        required_keys = list(dict.fromkeys(required_keys))
        bad = [k for k in required_keys if not normalized_hashes.get(k) or not HEX64.match(str(normalized_hashes.get(k)))]
        if bad:
            errors.append({"code": "ARM_PACKAGE_HASH_MISMATCH", "test_id": tid, "detail": "arm_package_hashes must contain 64-hex hashes for every arm_id@phase selector", "required_package_keys": required_keys, "missing_or_invalid": bad})
            continue
        ldef["arm_package_hashes"] = {k: {"sha256": normalized_hashes[k]} for k in required_keys}
        left_key = arm_phase_key(left_sel)
        right_key = arm_phase_key(right_sel)
        left_sha = normalized_hashes[left_key]
        right_sha = normalized_hashes[right_key]
        if bool(policy.get("full_preservation_guard_required")):
            before_key = arm_phase_key(guard.get("before") or {})
            after_key = arm_phase_key(guard.get("after") or {})
            if before_key == after_key:
                errors.append({"code": "INVALID_ABLATION_FULL_REGRESSION", "test_id": tid, "detail": "FULL preservation before/after selectors must differ by phase"})
                continue
            if normalized_hashes[before_key] == normalized_hashes[after_key]:
                errors.append({"code": "FULL_PRESERVATION_ARMS_IDENTICAL", "test_id": tid, "before_package_key": before_key, "after_package_key": after_key, "sha256": normalized_hashes[before_key], "detail": "FULL before/after package hashes are identical; deduplication did not produce distinct artifacts"})
                continue

        structural_required = bool(policy.get("structural_ceiling_required", False))
        structural = ldef.get("structural_ceiling")
        if structural_required:
            if not isinstance(report, dict):
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": "structural-ceiling report required before lock freeze"})
                continue
            if report.get("artifact_status") != "FINAL" or canonical(report.get("test_id")) != tid_key:
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": "structural report must be FINAL and match test_id"})
                continue
            try:
                structural = float(report["structural_ceiling"])
            except Exception:
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": "structural ceiling must be numeric"})
                continue
            if not math.isfinite(structural) or structural < 0:
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": "structural ceiling must be finite and non-negative"})
                continue
            report_arms = report.get("arms") or {}
            report_full_entry = report_arms.get("full_after_dedup") or {}
            report_ablated_entry = report_arms.get("ablated_after_dedup") or {}
            report_full = arm_hash_value(report_full_entry)
            report_ablated = arm_hash_value(report_ablated_entry)
            def structural_role(raw_arm_id: Any, expected_role: str) -> str:
                raw = canonical(raw_arm_id or expected_role)
                expected_artifact = canonical(
                    f"PILOT-001-TEST-0007-{expected_role}-AFTER_DEDUP-v{candidate_version}"
                )
                if raw in {expected_role, expected_artifact}:
                    return expected_role
                return raw

            report_full_key = f"{structural_role(report_full_entry.get('arm_id'), 'FULL')}@{canonical(report_full_entry.get('phase') or 'AFTER_DEDUP')}"
            report_ablated_key = f"{structural_role(report_ablated_entry.get('arm_id'), 'ABLATED')}@{canonical(report_ablated_entry.get('phase') or 'AFTER_DEDUP')}"
            if report_full_key != "FULL@AFTER_DEDUP" or report_ablated_key != "ABLATED@AFTER_DEDUP":
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": "structural report must explicitly identify FULL@AFTER_DEDUP and ABLATED@AFTER_DEDUP"})
                continue
            if not report_full or not HEX64.match(report_full) or not report_ablated or not HEX64.match(report_ablated):
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": "structural report must contain hashed phase-specific FULL and ABLATED packages"})
                continue
            if normalized_hashes.get("FULL@AFTER_DEDUP") != report_full:
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": "FULL@AFTER_DEDUP package hash in draft differs from structural report"})
                continue
            if normalized_hashes.get("ABLATED@AFTER_DEDUP") != report_ablated:
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": "ABLATED@AFTER_DEDUP package hash in draft differs from structural report"})
                continue
            ldef["structural_ceiling"] = structural
            ldef["structural_ceiling_evidence"] = {
                "report_path": report_path.name,
                "report_sha256": sha256_file(report_path),
                "arm_package_hashes": {
                    "FULL@AFTER_DEDUP": {"sha256": report_full},
                    "ABLATED@AFTER_DEDUP": {"sha256": report_ablated},
                },
                "tool": report.get("analysis_tool"),
                "tool_version_or_hash": report.get("analysis_tool_version_or_hash"),
            }
        elif structural is not None:
            try:
                structural = float(structural)
            except Exception:
                errors.append({"code": "MARGIN_THRESHOLD_UNREACHABLE", "test_id": tid, "detail": "optional structural ceiling is non-numeric"})
                continue

        effective = min(arith, structural) if structural is not None else arith
        ldef["effective_ceiling"] = round(float(effective), 6)
        if active_decision_rule is not None:
            try:
                abs_floor=float((active_decision_rule.get("absolute_discriminability") or {}).get("floor"))
                zone=list((active_decision_rule.get("decision_regions") or {}).get("inconclusive_if_margin_between_inclusive") or [])
                lower=float(zone[0]); upper=float(zone[1])
            except Exception:
                errors.append({"code":"DECISION_RULE_MISMATCH","test_id":tid,"detail":"decision rule discriminability/zone fields invalid"})
                continue
            if effective + TOL < abs_floor:
                errors.append({"code":"COMPARISON_NOT_DISCRIMINATIVE","test_id":tid,"effective_ceiling":round(float(effective),6),"absolute_discriminability_floor":abs_floor})
                continue
            ldef["decision_regions"]={"fail_below":lower,"inconclusive_inclusive":[lower,upper],"pass_above":upper,"absolute_discriminability_floor":abs_floor}
        if effective <= 0 or threshold > float(effective) + TOL:
            errors.append({
                "code": "MARGIN_THRESHOLD_UNREACHABLE",
                "test_id": tid,
                "margin_threshold": threshold,
                "arithmetic_ceiling": arith,
                "structural_ceiling": structural,
                "effective_ceiling": round(float(effective), 6),
            })
            continue

        just_error = validate_justification(contract, ldef, float(effective), threshold, active_decision_rule)
        if just_error:
            errors.append({"code": "INVALID_MARGIN_THRESHOLD", "test_id": tid, "detail": just_error})
            continue

        if bool(policy.get("full_preservation_guard_required")):
            guard = ldef.get("full_preservation") or {}
            try:
                max_reg = float(guard.get("max_total_regression"))
            except Exception:
                errors.append({"code": "INVALID_ABLATION_FULL_REGRESSION", "test_id": tid, "detail": "max_total_regression must be set and numeric before freezing"})
                continue
            if not math.isfinite(max_reg) or max_reg < 0:
                errors.append({"code": "INVALID_ABLATION_FULL_REGRESSION", "test_id": tid, "detail": "max_total_regression must be finite and non-negative"})

    _tag_errors(errors, _mark, _cid_prev)
    if errors:
        print(yaml.safe_dump({"status": "INVALID", "errors": errors}, sort_keys=False, allow_unicode=True))
        return 2

    draft["schema_version"] = "0.4.0"
    draft["artifact_status"] = "LOCKED"
    draft["locked_at_utc"] = datetime.now(timezone.utc).isoformat()
    draft.setdefault("derivation_record", {})
    draft["derivation_record"].update({
        "arithmetic_ceiling_formula": "sum(weight_i * (100 - right_floor_i)); right_floor_i = 0 for frozen predeclared right-arm fail-closed exceptions, else minimum_score if mandatory, else 0",
        "structural_ceiling_required_for": [tid for tid, p in comparisons_policy.items() if p.get("structural_ceiling_required")],
        "threshold_rule": "frozen_anchor_boundary_with_predeclared_inconclusive_zone_and_absolute_discriminability_floor",
        "comparison_sets": {
            tid: {"comparison_ids": sorted(CANONICAL_COMPARISON_SETS[canonical(tid)]),
                  "independent": False,
                  "shared_component": "SUMMARY_AS_SUMMARY",
                  "note": ("P e F subtraem o mesmo braco de baseline; nao sao duas "
                           "observacoes independentes e o instrumento nao pode "
                           "combina-las como se fossem")}
            for tid in comparisons_policy
            if canonical(tid) in CANONICAL_COMPARISON_SETS
        },
        "note": "Thresholds, phase-specific arm hashes, preservation distinctness, and reachability were validated before lock emission.",
    })
    out = Path(args.out)
    out.write_text(yaml.safe_dump(draft, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"VALID: wrote LOCKED margin artifact {out} sha256={sha256_file(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
