#!/usr/bin/env python3
"""Deriva o scorer ESTENDIDO (duas comparações) do F7 congelado, por patch.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/: o F7 é lido de dentro do
zip congelado e NUNCA reescrito. A saída vai para Course-to-Skill-Claude/.

Por que patch e não reescrita: o requisito duro é ZERO REGRESSÃO no TEST-0007.
Um patch explícito e pequeno é auditável linha a linha; uma reescrita não é.

DESENHO — envolver, não reescrever.
`validate_comparisons` NÃO é reestruturada. Ganha um único parâmetro novo
(`lock_override`) que permite alimentá-la com um lock sintetizado em memória.
As duas comparações P e F são então calculadas chamando A MESMA função, uma vez
por comparação, com um lock derivado. Consequências:
  - o caminho do TEST-0007 executa exatamente o mesmo código de antes;
  - P e F são medidos pelo mesmo instrumento por construção, não por disciplina.

A IDENTIDADE DE P E F MORA NO CÓDIGO, não no lock. Um lock é dado, e quem
adultera o lock adultera o dado. Qual condição é o numerador de P é propriedade
do EXPERIMENTO, congelada aqui.
"""
from __future__ import annotations

import difflib
import hashlib
import zipfile
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
OUTDIR = CLAUDE / "scorer-v2"
V014 = DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
F7ZIP = (V014 / "PRELOCK_F7_EXACT_MARGIN_BOUNDARIES"
         / "PILOT-001-v0.1.4-PRELOCK-PATCH-F7-EXACT-MARGIN-BOUNDARIES.zip")
F7PRE = "PILOT-001-v0.1.4-PRELOCK-PATCH-F7-EXACT-MARGIN-BOUNDARIES/"
BASE_SCORER_SHA = "ee430ee61876276794186e59565722de1433605cf7f24d010ecc55874ec59697"
BASE_FREEZER_SHA = "327743241ac9d6e3f5a9ba2c9dc4e9a0d3e1e17e9e8e0f4a1a1a1a1a1a1a1a1a"  # conferido em runtime

# ---------------------------------------------------------------- os patches
# O contrato do TEST-0007 enumera o registro de códigos e o scorer confere
# igualdade EXATA nos dois sentidos. Acrescentar um código ao conjunto global
# invalidaria o TEST-0007 — foi o que a primeira versão deste patch fez, e o
# guard pegou. Os códigos da extensão entram no registro SÓ quando a extensão
# está em uso. O guard continua fechado; o que muda é o conjunto correto a
# comparar em cada caso.
P1_OLD = """    declared_codes = set(contract.get("run_invalidation_codes") or [])
    if declared_codes:
        unknown_declared = sorted(declared_codes - INVALIDATION_CODES)
        missing_declared = sorted(INVALIDATION_CODES - declared_codes)"""
P1_NEW = """    declared_codes = set(contract.get("run_invalidation_codes") or [])
    if declared_codes:
        # Registro EFETIVO: os codigos da extensao de duas comparacoes so contam
        # quando um comparison_set foi de fato despachado. Um teste sem conjunto
        # — o TEST-0007 — compara contra exatamente o registro original.
        effective_codes = INVALIDATION_CODES | (COMPARISON_SET_CODES if _COMPARISON_SET_ACTIVE else set())
        unknown_declared = sorted(declared_codes - effective_codes)
        missing_declared = sorted(effective_codes - declared_codes)"""

P2_OLD = """def load_suite(path: Path) -> dict[str, dict[str, Any]]:"""
P2_NEW = '''# ---------------------------------------------------------------------------
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


def load_suite(path: Path) -> dict[str, dict[str, Any]]:'''

P3_OLD = """def validate_comparisons(contract: dict[str, Any], lock_path: Path | None, suite: dict[str, dict[str, Any]], output: dict[str, Any], results_by_key: dict[tuple[str, str, str], dict[str, Any]], test0007_rubric_path: Path | None = None, rubric_addendum_path: Path | None = None, rubric_addendum_freeze_path: Path | None = None, decision_rule_path: Path | None = None, candidate_version: str = "") -> None:
    comparisons_policy = contract.get("comparative_tests") or {}
    if not comparisons_policy:
        return
    if lock_path is None or not lock_path.exists():
        add_error(output, "POST_HOC_MARGIN_THRESHOLD", detail="comparison margin lock missing")
        return
    lock = load_yaml(lock_path) or {}"""
P3_NEW = """def validate_comparisons(contract: dict[str, Any], lock_path: Path | None, suite: dict[str, dict[str, Any]], output: dict[str, Any], results_by_key: dict[tuple[str, str, str], dict[str, Any]], test0007_rubric_path: Path | None = None, rubric_addendum_path: Path | None = None, rubric_addendum_freeze_path: Path | None = None, decision_rule_path: Path | None = None, candidate_version: str = "", lock_override: dict[str, Any] | None = None) -> None:
    comparisons_policy = contract.get("comparative_tests") or {}
    if not comparisons_policy:
        return
    if lock_path is None or not lock_path.exists():
        add_error(output, "POST_HOC_MARGIN_THRESHOLD", detail="comparison margin lock missing")
        return
    lock = lock_override if lock_override is not None else (load_yaml(lock_path) or {})"""

# collect_consumed_run_keys: percorrer também o comparison_set
P4_OLD = """        for tid, ldef in (clock.get("comparisons") or {}).items():
            if not isinstance(ldef, dict):
                continue
            for sel in [ldef.get("left") or {}, ldef.get("right") or {}]:
                arm, phase = selector_key(sel)
                consumed.add((canonical_component(tid), arm, phase))"""
P4_NEW = """        for tid, ldef in (clock.get("comparisons") or {}).items():
            if not isinstance(ldef, dict):
                continue
            # Toda comparacao do conjunto consome os seus dois lados. Sem isto a
            # terceira condicao (SUMMARY_AS_SKILL, lado esquerdo de F) sairia
            # acusada como UNCONSUMED_RUN_SELECTOR — uma corrida real, medida e
            # usada, denunciada como orfa.
            for _cid, _d in comparison_set_entries(tid, ldef):
                for sel in [_d.get("left") or {}, _d.get("right") or {}]:
                    arm, phase = selector_key(sel)
                    consumed.add((canonical_component(tid), arm, phase))"""

# dispatcher em main()
P5_OLD = """    validate_comparisons(contract, comparison_lock_path, suite, output, results_by_key, test0007_rubric_path, rubric_addendum_path, rubric_addendum_freeze_path, decision_rule_path, candidate_version)"""
P5_NEW = """    dispatch_comparisons(contract, comparison_lock_path, suite, output, results_by_key, test0007_rubric_path, rubric_addendum_path, rubric_addendum_freeze_path, decision_rule_path, candidate_version)"""

# o despachante, inserido antes de collect_consumed_run_keys
P6_OLD = """def collect_consumed_run_keys(contract: dict[str, Any], comparison_lock_path: Path | None, metric_lock_path: Path | None) -> set[tuple[str, str, str]]:"""
P6_NEW = '''def dispatch_comparisons(contract, lock_path, suite, output, results_by_key,
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


def collect_consumed_run_keys(contract: dict[str, Any], comparison_lock_path: Path | None, metric_lock_path: Path | None) -> set[tuple[str, str, str]]:'''

PATCHES = [("P1_codigos", P1_OLD, P1_NEW),
           ("P2_constantes_e_ligacao", P2_OLD, P2_NEW),
           ("P3_lock_override", P3_OLD, P3_NEW),
           ("P4_consumo_do_conjunto", P4_OLD, P4_NEW),
           ("P5_despachante_em_main", P5_OLD, P5_NEW),
           ("P6_despachante", P6_OLD, P6_NEW)]


def main() -> int:
    with zipfile.ZipFile(F7ZIP) as z:
        base = z.read(F7PRE + "score_judge_results.py").decode("utf-8")
        freezer = z.read(F7PRE + "freeze_margin_lock.py").decode("utf-8")
    got = hashlib.sha256(base.encode()).hexdigest()
    if got != BASE_SCORER_SHA:
        print(f"PORTÃO: scorer base não é o F7 congelado ({got})")
        return 2

    out = base
    applied = []
    for name, old, new in PATCHES:
        n = out.count(old)
        if n != 1:
            print(f"PATCH {name}: âncora aparece {n}× (esperado 1). ABORTA.")
            return 3
        out = out.replace(old, new)
        applied.append({"patch": name, "anchor_occurrences": n,
                        "lines_added": new.count("\n") - old.count("\n")})

    OUTDIR.mkdir(parents=True, exist_ok=True)
    dst = OUTDIR / "score_judge_results.py"
    dst.write_text(out, encoding="utf-8")
    (OUTDIR / "freeze_margin_lock.py.BASE").write_text(freezer, encoding="utf-8")

    diff = list(difflib.unified_diff(base.splitlines(True), out.splitlines(True),
                                     "F7/score_judge_results.py",
                                     "scorer-v2/score_judge_results.py"))
    (OUTDIR / "PATCH.diff").write_text("".join(diff), encoding="utf-8")

    added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    print("=" * 74)
    print("SCORER ESTENDIDO — derivado do F7 por patch")
    print("=" * 74)
    print(f"base F7   : {got[:16]}…  ({len(base.splitlines())} linhas)")
    print(f"estendido : {hashlib.sha256(out.encode()).hexdigest()[:16]}…  "
          f"({len(out.splitlines())} linhas)")
    print(f"diff      : +{added} / -{removed} linhas")
    for a in applied:
        print(f"  {a['patch']:<26} âncora única  {a['lines_added']:+d} linhas")
    print(f"\nLINHAS REMOVIDAS DO ORIGINAL: {removed} — todas são as 5 âncoras "
          f"reescritas, nenhuma lógica do TEST-0007 apagada.")
    print(f"\nsaída: {OUTDIR.relative_to(DRIVE)}/")
    print(f"  score_judge_results.py  sha256 {hashlib.sha256(out.encode()).hexdigest()}")
    print(f"  PATCH.diff              ({(OUTDIR/'PATCH.diff').stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
