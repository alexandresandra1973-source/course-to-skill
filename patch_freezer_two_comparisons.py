#!/usr/bin/env python3
"""Deriva o freeze_margin_lock ESTENDIDO do F7 congelado, por patch.

Mesmo desenho do scorer: âncoras únicas, diff auditável, corpo do laço de
validação INTOCADO. O que muda é o que o laço percorre.
"""
from __future__ import annotations

import difflib
import hashlib
import zipfile
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
OUTDIR = DRIVE / "Course-to-Skill-Claude/scorer-v2"
F7ZIP = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
         / "PRELOCK_F7_EXACT_MARGIN_BOUNDARIES"
         / "PILOT-001-v0.1.4-PRELOCK-PATCH-F7-EXACT-MARGIN-BOUNDARIES.zip")
F7PRE = "PILOT-001-v0.1.4-PRELOCK-PATCH-F7-EXACT-MARGIN-BOUNDARIES/"
BASE_SHA = "327743241ac9aa6d1ba2e35a3ee16dbd4e2e1e5b6d1c0e2d3a4b5c6d7e8f9a0b"

Q1_OLD = '''def load_yaml(path: Path) -> Any:'''
Q1_NEW = '''# ---------------------------------------------------------------------------
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


def load_yaml(path: Path) -> Any:'''

Q2_OLD = """    for tid, policy in comparisons_policy.items():
        tid_key = canonical(tid)
        ldef = defs.get(tid)
        test = suite.get(tid_key)"""
Q2_NEW = """    _expanded = list(expand_for_freeze(comparisons_policy, defs, errors))
    _mark, _cid_prev = len(errors), None
    for tid, policy, _cid, ldef in _expanded:
        # Marca os erros da iteracao ANTERIOR com o seu comparison_id. Feito na
        # entrada, e nao na saida, porque o corpo tem varios `continue`.
        _tag_errors(errors, _mark, _cid_prev)
        _mark, _cid_prev = len(errors), _cid
        tid_key = canonical(tid)
        test = suite.get(tid_key)"""

Q3_OLD = """    if errors:
        print(yaml.safe_dump({"status": "INVALID", "errors": errors}, sort_keys=False, allow_unicode=True))
        return 2"""
Q3_NEW = """    _tag_errors(errors, _mark, _cid_prev)
    if errors:
        print(yaml.safe_dump({"status": "INVALID", "errors": errors}, sort_keys=False, allow_unicode=True))
        return 2"""

Q4_OLD = """        "threshold_rule": "frozen_anchor_boundary_with_predeclared_inconclusive_zone_and_absolute_discriminability_floor","""
Q4_NEW = """        "threshold_rule": "frozen_anchor_boundary_with_predeclared_inconclusive_zone_and_absolute_discriminability_floor",
        "comparison_sets": {
            tid: {"comparison_ids": sorted(CANONICAL_COMPARISON_SETS[canonical(tid)]),
                  "independent": False,
                  "shared_component": "SUMMARY_AS_SUMMARY",
                  "note": ("P e F subtraem o mesmo braco de baseline; nao sao duas "
                           "observacoes independentes e o instrumento nao pode "
                           "combina-las como se fossem")}
            for tid in comparisons_policy
            if canonical(tid) in CANONICAL_COMPARISON_SETS
        },"""

PATCHES = [("Q1_expansao", Q1_OLD, Q1_NEW),
           ("Q2_laco", Q2_OLD, Q2_NEW),
           ("Q3_marcacao_final", Q3_OLD, Q3_NEW),
           ("Q4_registro_de_derivacao", Q4_OLD, Q4_NEW)]


def main() -> int:
    with zipfile.ZipFile(F7ZIP) as z:
        base = z.read(F7PRE + "freeze_margin_lock.py").decode("utf-8")
    print(f"base freeze_margin_lock: {hashlib.sha256(base.encode()).hexdigest()}")

    out = base
    for name, old, new in PATCHES:
        n = out.count(old)
        if n != 1:
            print(f"PATCH {name}: âncora aparece {n}× (esperado 1). ABORTA.")
            return 3
        out = out.replace(old, new)
        print(f"  {name:<26} âncora única  "
              f"{new.count(chr(10)) - old.count(chr(10)):+d} linhas")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "freeze_margin_lock.py").write_text(out, encoding="utf-8")
    diff = list(difflib.unified_diff(base.splitlines(True), out.splitlines(True),
                                     "F7/freeze_margin_lock.py",
                                     "scorer-v2/freeze_margin_lock.py"))
    (OUTDIR / "PATCH-freezer.diff").write_text("".join(diff), encoding="utf-8")
    (OUTDIR / "freeze_margin_lock.py.BASE").unlink(missing_ok=True)
    added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    print(f"\ndiff: +{added} / -{removed}")
    print(f"estendido sha256: {hashlib.sha256(out.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
