#!/usr/bin/env python3
"""CANÁRIO da extensão de duas comparações. Tudo em /tmp. Zero chamadas.

Regra da casa: todo verificador entra com canário cujas fixtures TÊM de falhar.
Aqui cada caso roda contra o instrumento real (tem de passar) E contra um
mutante ou uma fixture adulterada (tem de reprovar). Fixture adulterada que
passa = o verificador não tem poder de detecção = a suíte inteira reprova.

Sete casos, os sete exigidos pelo revisor.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
SV2 = DRIVE / "Course-to-Skill-Claude/scorer-v2"
W = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/t0008")
LAB = W / "canary8"
REPRO = W / "repro"
OFFICIAL = W / "official/TEST-0007-OFFICIAL-SCORER-RESULT-v0.1.4.yaml"

# ---- notas escolhidas para que a identidade seja verificável e não trivial
TOTALS = {"FULL_SKILL": 92.0, "SUMMARY_AS_SUMMARY": 74.0, "SUMMARY_AS_SKILL": 80.0}
SCORES = {  # criterion -> (weight, minimum, {arm: score})
    "EXECUTION_QUALITY":           (0.4, 85, {"FULL_SKILL": 95, "SUMMARY_AS_SUMMARY": 70, "SUMMARY_AS_SKILL": 80}),
    "CONSISTENCY":                 (0.2, 80, {"FULL_SKILL": 90, "SUMMARY_AS_SUMMARY": 75, "SUMMARY_AS_SKILL": 80}),
    "HUMAN_CHECKPOINT_COMPLIANCE": (0.2, 90, {"FULL_SKILL": 95, "SUMMARY_AS_SUMMARY": 80, "SUMMARY_AS_SKILL": 80}),
    "METHODOLOGY_FIDELITY":        (0.2, 85, {"FULL_SKILL": 85, "SUMMARY_AS_SUMMARY": 75, "SUMMARY_AS_SKILL": 80}),
}
CEILING = sum(w * (100 - m) for w, m, _ in SCORES.values())   # 15.0
THRESHOLD = 5.0
PKG = {a: hashlib.sha256(f"CANARY-PACKAGE-{a}".encode()).hexdigest() for a in TOTALS}

BASE_CODES = ["MISSING_CRITERION_ROW", "NON_INTEGER_CRITERION_SCORE", "RUBRIC_WEIGHT_MISMATCH",
              "MISSING_RESPONSE_CITATION", "CITATION_NOT_VERIFIABLE", "RAW_OUTPUT_HASH_MISMATCH",
              "DECLARED_TOTAL_MISMATCH", "UNDEFINED_AGGREGATION", "UNDEFINED_METRIC_DERIVATION",
              "POST_HOC_MARGIN_THRESHOLD", "INVALID_ABLATION_FULL_REGRESSION",
              "MARGIN_THRESHOLD_UNREACHABLE", "DUPLICATE_RUN_KEY", "DUPLICATE_CRITERION_ROW",
              "UNCONSUMED_RUN_SELECTOR", "ARM_PACKAGE_HASH_MISMATCH", "RAW_OUTPUT_HEADER_MISMATCH",
              "INVALID_MARGIN_THRESHOLD", "PRE_RUN_LOCK_HASH_MISMATCH",
              "FULL_PRESERVATION_ARMS_IDENTICAL", "MISSING_ANCHOR_ASSESSMENT",
              "ANCHOR_SCORE_MISMATCH", "MISSING_CRITICAL_FAILURE_ASSESSMENT",
              "CRITICAL_FAILURE_ASSESSMENT_INCONSISTENT", "DECISION_RULE_MISMATCH",
              "COMPARISON_NOT_DISCRIMINATIVE"]
EXT_CODES = ["COMPARISON_ID_MISSING", "UNKNOWN_COMPARISON_ID",
             "COMPARISON_SELECTOR_BINDING_MISMATCH", "COMPARISON_SET_INCOMPLETE",
             "SHARED_BASELINE_INDEPENDENCE_VIOLATION", "COMPARISON_IDENTITY_UNCLOSED"]

QUOTE = ("O agente executa o workflow completo e mantem a revisao humana "
         "inicial antes de qualquer publicacao externa.")


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ------------------------------------------------------------------ fixtures
def build(lab: Path) -> None:
    if lab.exists():
        shutil.rmtree(lab)
    (lab / "raw_outputs/TEST-0008").mkdir(parents=True)

    for arm in TOTALS:
        hdr = json.dumps({"test_id": "TEST-0008", "arm_id": arm, "phase": "CURRENT",
                          "arm_package_sha256": PKG[arm]}, separators=(",", ":"))
        (lab / f"raw_outputs/TEST-0008/{arm}.md").write_text(
            f"PILOT001_RUN_HEADER {hdr}\n"
            f"## Resposta da condicao {arm}\n\n{QUOTE}\n\n"
            f"Fim da resposta.\n", encoding="utf-8")

    (lab / "suite.yaml").write_text(yaml.safe_dump({
        "schema_version": "0.1.0", "test_id": "TEST-0008",
        "name": "Summary vs Skill — CANARIO, rubrica de fixture",
        "evaluation": {
            "rubric": [{"criterion": c, "weight": w, "mandatory": True,
                        "minimum_score": m, "description": f"fixture {c}"}
                       for c, (w, m, _) in SCORES.items()],
            "scoring_method": "WEIGHTED_SUM", "score_scale": {"min": 0, "max": 100}},
    }, sort_keys=False, allow_unicode=True), encoding="utf-8")

    (lab / "contract.yaml").write_text(yaml.safe_dump({
        "schema_version": "0.7.0",
        "contract_id": "CANARY-TEST-0008-TWO-COMPARISONS",
        "artifact_status": "CANARY_FIXTURE_NOT_A_LOCK",
        "candidate_version": "0.1.4", "scope": ["TEST-0008"],
        "raw_output_requirements": {"minimum_quote_chars": 20,
                                    "runner_header_required_for_comparison_runs": True,
                                    "runner_header_format": "PILOT001_RUN_HEADER {json-object}"},
        "suite_aggregation": {"acceptance": {
            "mode": "EQUAL_TEST_WEIGHT", "test_ids": ["TEST-0008"],
            "default_primary_run": {"arm_id": "PRIMARY", "phase": "CURRENT"},
            "primary_run_overrides": {"TEST-0008": {"arm_id": "FULL_SKILL", "phase": "CURRENT"}}}},
        "metric_derivation": {},
        "comparative_tests": {"TEST-0008": {
            "comparison": "COMPARISON_SET_P_AND_F",
            "margin_threshold": "FROM_COMPARISON_LOCK",
            "full_preservation_guard_required": False,
            "structural_ceiling_required": False}},
        "comparison_lock_requirements": {"threshold_justification_required": {
            "minimum_fraction_of_effective_ceiling": 0.05}},
        "run_invalidation_codes": BASE_CODES + EXT_CODES,
    }, sort_keys=False, allow_unicode=True), encoding="utf-8")

    runs = []
    for arm, total in TOTALS.items():
        rel = f"raw_outputs/TEST-0008/{arm}.md"
        crits = []
        for c, (w, m, per) in SCORES.items():
            crits.append({"criterion": c, "score": per[arm], "weight": w,
                          "mandatory": True, "minimum_score": m,
                          "weighted_points": round(w * per[arm], 6),
                          "evidence": {"raw_output_path": rel, "start_line": 4,
                                       "end_line": 4, "quote": QUOTE}})
        runs.append({"test_id": "TEST-0008", "arm_id": arm, "phase": "CURRENT",
                     "raw_output_path": rel,
                     "raw_output_sha256": sha_p(lab / rel),
                     "declared_total": total, "criteria": crits})
    (lab / "scores.yaml").write_text(yaml.safe_dump({"runs": runs}, sort_keys=False,
                                                    allow_unicode=True), encoding="utf-8")


def comparison_entry(left: str, right: str) -> dict:
    return {"left": {"arm_id": left, "phase": "CURRENT"},
            "right": {"arm_id": right, "phase": "CURRENT"},
            "margin_threshold": THRESHOLD,
            "arithmetic_ceiling": CEILING, "effective_ceiling": CEILING,
            "threshold_justification": {
                "basis": "EFFECTIVE_CEILING",
                "rationale": ("limiar fixado como fracao do teto efetivo antes de "
                              "qualquer nota ser vista"),
                "distinguishability_rationale": ("a fracao escolhida separa efeito "
                                                 "real de ruido de avaliador"),
                "effective_ceiling_reference": CEILING,
                "threshold_fraction_of_effective_ceiling": THRESHOLD / CEILING}}


def draft(pairs: dict[str, tuple[str, str]] | None, flat: tuple[str, str] | None = None) -> dict:
    shared = {"arm_package_hashes": {f"{a}@CURRENT": {"sha256": PKG[a]} for a in TOTALS}}
    if flat is not None:
        d = dict(shared); d.update(comparison_entry(*flat))
        return {"schema_version": "0.4.0", "artifact_status": "DRAFT_NOT_LOCKED",
                "candidate_version": "0.1.4", "comparisons": {"TEST-0008": d}}
    d = dict(shared)
    d["comparison_set"] = {cid: comparison_entry(l, r) for cid, (l, r) in pairs.items()}
    return {"schema_version": "0.4.0", "artifact_status": "DRAFT_NOT_LOCKED",
            "candidate_version": "0.1.4", "comparisons": {"TEST-0008": d}}


# ------------------------------------------------------------------ execução
def freeze(lab: Path, drf: dict, tag: str, freezer: Path) -> tuple[int, str, Path]:
    dp = lab / f"draft-{tag}.yaml"
    dp.write_text(yaml.safe_dump(drf, sort_keys=False, allow_unicode=True), encoding="utf-8")
    out = lab / f"lock-{tag}.yaml"
    r = subprocess.run([sys.executable, str(freezer), "--candidate-version", "0.1.4",
                        "--suite", str(lab / "suite.yaml"), "--contract", str(lab / "contract.yaml"),
                        "--draft", str(dp), "--out", str(out)],
                       capture_output=True, text=True, cwd=lab)
    return r.returncode, r.stdout + r.stderr, out


def pre_run_anchors(lab: Path, lock: Path, tag: str) -> tuple[Path, Path, Path]:
    """Registro pre-run + registro de abertura, amarrados ao lock deste caso.

    O scorer exige a cadeia toda. Numa fixture de canario ela e construida em
    volta do lock do caso; o que se testa aqui e a extensao, nao a governanca de
    congelamento, que ja tem os seus proprios verificadores.
    """
    ml = lab / "metric-lock.yaml"
    ml.write_text(yaml.safe_dump({"schema_version": "0.1.0",
                                  "artifact_status": "LOCKED",
                                  "candidate_version": "0.1.4",
                                  "metrics": {}}, sort_keys=False), encoding="utf-8")
    reg = lab / f"registry-{tag}.yaml"
    reg.write_text(yaml.safe_dump({
        "schema_version": "0.1.0", "artifact_status": "LOCKED_PRE_RUN",
        "candidate_version": "0.1.4",
        "locks": {"comparison_margin": {"sha256": sha_p(lock)},
                  "metric_derivation": {"sha256": sha_p(ml)}},
    }, sort_keys=False), encoding="utf-8")
    op = lab / f"opening-{tag}.yaml"
    op.write_text(yaml.safe_dump({
        "schema_version": "0.1.0", "artifact_status": "FROZEN_BEFORE_BLIND_ROUND",
        "candidate_version": "0.1.4",
        "pre_run_lock_registry_sha256": sha_p(reg),
    }, sort_keys=False), encoding="utf-8")
    return reg, op, ml


def score(lab: Path, lock: Path, tag: str, scorer: Path) -> tuple[int, dict, str]:
    out = lab / f"result-{tag}.yaml"
    reg, op, ml = pre_run_anchors(lab, lock, tag)
    r = subprocess.run([sys.executable, str(scorer), "--candidate-version", "0.1.4",
                        "--suite", "suite.yaml", "--contract", "contract.yaml",
                        "--scores", "scores.yaml", "--raw-root", ".",
                        "--comparison-lock", str(lock), "--metric-lock", str(ml),
                        "--pre-run-lock-registry", str(reg),
                        "--pre-run-opening-record", str(op), "--out", str(out)],
                       capture_output=True, text=True, cwd=lab)
    doc = yaml.safe_load(out.read_text(encoding="utf-8")) if out.exists() else {}
    return r.returncode, doc, r.stdout + r.stderr


def codes(doc: dict) -> set[str]:
    return {e.get("code") for e in (doc.get("errors") or [])}


def mutant(scorer: Path, name: str, old: str, new: str) -> Path:
    s = scorer.read_text(encoding="utf-8")
    assert s.count(old) == 1, f"mutante {name}: âncora não é única"
    p = scorer.parent / f"MUTANT-{name}.py"
    p.write_text(s.replace(old, new), encoding="utf-8")
    return p


def main() -> int:
    LAB.mkdir(parents=True, exist_ok=True)
    build(LAB)
    scorer = LAB / "score_judge_results.py"
    freezer = LAB / "freeze_margin_lock.py"
    shutil.copy(SV2 / "score_judge_results.py", scorer)
    shutil.copy(SV2 / "freeze_margin_lock.py", freezer)

    P_F = {"P": ("FULL_SKILL", "SUMMARY_AS_SUMMARY"),
           "F": ("SUMMARY_AS_SKILL", "SUMMARY_AS_SUMMARY")}
    rows: list[dict] = []

    def rec(case, sub, expect, got, ok, note=""):
        rows.append({"case": case, "sub": sub, "expect": expect, "got": got,
                     "passed": ok, "note": note})

    # ---------- referência: congela e pontua o conjunto correto
    rc, log, lock = freeze(LAB, draft(P_F), "ok", freezer)
    if rc != 0:
        print("FREEZER REPROVOU no caso correto:\n", log)
        return 3
    rc, doc, _ = score(LAB, lock, "ok", scorer)
    comps = {c.get("comparison_id"): c for c in (doc.get("comparisons") or [])}

    # K1 — P e F na MESMA execução
    ok1 = set(comps) == {"P", "F"} and doc["status"] in ("VALID", "FAIL", "INCONCLUSIVE")
    rec("K1_P_E_F_NA_MESMA_EXECUCAO", "real", "P e F presentes",
        sorted(comps), ok1)
    rc2, log2, _ = freeze(LAB, draft({"P": P_F["P"]}), "soP", freezer)
    ok1m = rc2 != 0 and "COMPARISON_SET_INCOMPLETE" in log2
    rec("K1_P_E_F_NA_MESMA_EXECUCAO", "fixture só com P", "REJEITA",
        "COMPARISON_SET_INCOMPLETE" if ok1m else log2.strip()[:60], ok1m)

    # K2 — pares corretos, cada um lendo as SUAS duas condições
    want = {"P": ("FULL_SKILL", "SUMMARY_AS_SUMMARY", 18.0),
            "F": ("SUMMARY_AS_SKILL", "SUMMARY_AS_SUMMARY", 6.0)}
    got2 = {cid: (c["left"]["arm_id"], c["right"]["arm_id"], c["margin"])
            for cid, c in comps.items()}
    ok2 = got2 == want
    rec("K2_PARES_CORRETOS", "real", str(want), str(got2), ok2)
    totals_ok = all(abs(comps[cid]["left"]["total"] - TOTALS[want[cid][0]]) < 1e-9
                    and abs(comps[cid]["right"]["total"] - TOTALS[want[cid][1]]) < 1e-9
                    for cid in want)
    rec("K2_PARES_CORRETOS", "totais lidos das condições certas",
        "cada lado lê a sua condição", "sim" if totals_ok else "NÃO", totals_ok)

    # K3 — troca de selector entre P e F
    swapped = {"P": ("SUMMARY_AS_SKILL", "SUMMARY_AS_SUMMARY"),
               "F": ("FULL_SKILL", "SUMMARY_AS_SUMMARY")}
    rc3, log3, lock3 = freeze(LAB, draft(swapped), "swap", freezer)
    ok3f = rc3 != 0 and "COMPARISON_SELECTOR_BINDING_MISMATCH" in log3
    rec("K3_TROCA_DE_SELECTOR", "freezer", "REJEITA",
        "COMPARISON_SELECTOR_BINDING_MISMATCH" if ok3f else log3.strip()[:60], ok3f)
    # o scorer tem de recusar sozinho, mesmo se um lock trocado chegar pronto
    forged = draft(swapped); forged["artifact_status"] = "LOCKED"
    fp = LAB / "lock-swap-forjado.yaml"
    fp.write_text(yaml.safe_dump(forged, sort_keys=False, allow_unicode=True), encoding="utf-8")
    _, doc3, _ = score(LAB, fp, "swap", scorer)
    ok3s = "COMPARISON_SELECTOR_BINDING_MISMATCH" in codes(doc3)
    rec("K3_TROCA_DE_SELECTOR", "scorer, lock forjado já LOCKED", "REJEITA",
        sorted(codes(doc3))[:2], ok3s,
        "o lock forjado tem hash próprio; só a ligação no código o pega")

    # K4 — comparison_id ausente ou desconhecido
    rc4a, log4a, _ = freeze(LAB, draft(None, flat=("FULL_SKILL", "SUMMARY_AS_SUMMARY")),
                            "flat", freezer)
    ok4a = rc4a != 0 and "COMPARISON_ID_MISSING" in log4a
    rec("K4_COMPARISON_ID", "ausente (lock plano)", "REJEITA",
        "COMPARISON_ID_MISSING" if ok4a else log4a.strip()[:60], ok4a)
    unknown = dict(P_F); unknown["X"] = ("FULL_SKILL", "SUMMARY_AS_SUMMARY")
    rc4b, log4b, _ = freeze(LAB, draft(unknown), "unknown", freezer)
    ok4b = rc4b != 0 and "UNKNOWN_COMPARISON_ID" in log4b
    rec("K4_COMPARISON_ID", "desconhecido ('X')", "REJEITA",
        "UNKNOWN_COMPARISON_ID" if ok4b else log4b.strip()[:60], ok4b)

    # K5 — terceira condição CONSUMIDA, sem acusar órfã
    ok5 = "UNCONSUMED_RUN_SELECTOR" not in codes(doc)
    rec("K5_TERCEIRA_CONDICAO_CONSUMIDA", "real",
        "sem UNCONSUMED_RUN_SELECTOR",
        "limpo" if ok5 else sorted(codes(doc)), ok5)
    mut5 = mutant(scorer, "consumo-legado",
                  "            for _cid, _d in comparison_set_entries(tid, ldef):",
                  "            for _cid, _d in [(None, ldef)]:")
    _, doc5, _ = score(LAB, lock, "mut5", mut5)
    got5 = [e for e in (doc5.get("errors") or [])
            if e.get("code") == "UNCONSUMED_RUN_SELECTOR"]
    ok5m = any(e.get("arm_id") == "SUMMARY_AS_SKILL" for e in got5)
    rec("K5_TERCEIRA_CONDICAO_CONSUMIDA", "mutante sem a expansão",
        "ACUSA SUMMARY_AS_SKILL como órfã",
        [e.get("arm_id") for e in got5] or "nada", ok5m,
        "prova que a expansão do consumo tem poder de detecção")

    # K6 — identidade D = m(FULL) − m(SUMMARY_AS_SKILL) = P − F
    ident = (doc.get("comparison_identities") or [{}])[0]
    ok6 = bool(ident.get("closes")) and abs(ident.get("d_direct", -1) - 12.0) < 1e-9 \
        and abs(ident.get("d_from_p_minus_f", -1) - 12.0) < 1e-9
    rec("K6_IDENTIDADE_D_IGUAL_P_MENOS_F", "real",
        "fecha: 92−80 = 18−6 = 12",
        f"D={ident.get('d_direct')} P−F={ident.get('d_from_p_minus_f')} "
        f"fecha={ident.get('closes')}", ok6)
    # mutante: erro de SELEÇÃO DE CONDIÇÃO em F (subtrai FULL em vez do baseline)
    mut6 = mutant(scorer, "selecao-de-condicao",
                  '        "F": ("SUMMARY_AS_SKILL", "SUMMARY_AS_SUMMARY"),',
                  '        "F": ("SUMMARY_AS_SKILL", "FULL_SKILL"),')
    bad_pairs = {"P": ("FULL_SKILL", "SUMMARY_AS_SUMMARY"),
                 "F": ("SUMMARY_AS_SKILL", "FULL_SKILL")}
    bad = draft(bad_pairs); bad["artifact_status"] = "LOCKED"
    bp = LAB / "lock-selecao-errada.yaml"
    bp.write_text(yaml.safe_dump(bad, sort_keys=False, allow_unicode=True), encoding="utf-8")
    _, doc6, _ = score(LAB, bp, "mut6", mut6)
    id6 = (doc6.get("comparison_identities") or [{}])[0]
    ok6m = ("COMPARISON_IDENTITY_UNCLOSED" in codes(doc6)) and not id6.get("closes", True)
    rec("K6_IDENTIDADE_D_IGUAL_P_MENOS_F", "mutante: F subtrai FULL_SKILL",
        "REJEITA (identidade não fecha)",
        f"D={id6.get('d_direct')} P−F={id6.get('d_from_p_minus_f')} "
        f"{'UNCLOSED' if ok6m else 'passou'}", ok6m)

    # não-independência registrada no artefato
    dep = (doc.get("comparison_dependence") or [{}])[0]
    okd = dep.get("independent") is False and dep.get("shared_component") == "SUMMARY_AS_SUMMARY"
    rec("K6b_NAO_INDEPENDENCIA", "registrada na saída, não só na ADR",
        "independent=False, shared=SUMMARY_AS_SUMMARY",
        f"independent={dep.get('independent')} shared={dep.get('shared_component')}", okd)
    indep = yaml.safe_load((LAB / "contract.yaml").read_text(encoding="utf-8"))
    indep["comparative_tests"]["TEST-0008"]["treat_comparisons_as_independent"] = True
    (LAB / "contract.yaml").write_text(yaml.safe_dump(indep, sort_keys=False,
                                                      allow_unicode=True), encoding="utf-8")
    _, docI, _ = score(LAB, lock, "indep", scorer)
    okI = "SHARED_BASELINE_INDEPENDENCE_VIOLATION" in codes(docI)
    rec("K6b_NAO_INDEPENDENCIA", "contrato pede tratamento independente", "REJEITA",
        "SHARED_BASELINE_INDEPENDENCE_VIOLATION" if okI else sorted(codes(docI))[:2], okI)
    build_contract_restore = yaml.safe_load((LAB / "contract.yaml").read_text(encoding="utf-8"))
    build_contract_restore["comparative_tests"]["TEST-0008"].pop("treat_comparisons_as_independent")
    (LAB / "contract.yaml").write_text(yaml.safe_dump(build_contract_restore, sort_keys=False,
                                                      allow_unicode=True), encoding="utf-8")

    # K7 — ZERO REGRESSÃO no TEST-0007
    r7 = subprocess.run([sys.executable, str(SV2 / "score_judge_results.py"),
                         "--candidate-version", "0.1.4",
                         "--suite", "TEST-0007-LOCK-SUITE-v0.1.4.yaml",
                         "--contract", "JUDGE-SCORING-CONTRACT-TEST-0007-v0.1.4-F7.yaml",
                         "--scores", "scores.yaml", "--raw-root", ".",
                         "--comparison-lock", "ABLATION-MARGIN-LOCK-v0.1.4.yaml",
                         "--metric-lock", "METRIC-DERIVATION-LOCK-v0.1.4.yaml",
                         "--pre-run-lock-registry", "PRE-RUN-LOCK-REGISTRY-v0.1.4.yaml",
                         "--pre-run-opening-record", "PRE-RUN-OPENING-RECORD-v0.1.4.yaml",
                         "--test0007-rubric", "TEST-0007-RUBRIC-v0.1.3.yaml",
                         "--rubric-addendum", "TEST-0007-RUBRIC-ANCHOR-ADDENDUM-v0.1.3.yaml",
                         "--rubric-addendum-freeze-record",
                         "TEST-0007-RUBRIC-ANCHOR-ADDENDUM-FREEZE-RECORD-v0.1.3.yaml",
                         "--decision-rule", "TEST-0007-DECISION-RULE-v0.1.4.yaml",
                         "--out", "OUT_CANARY7.yaml"],
                        capture_output=True, text=True, cwd=REPRO)

    def canon(p: Path) -> str:
        def nz(o):
            if isinstance(o, dict):
                return {k: (Path(str(v)).name if k in ("path", "opening_record_path") and v else nz(v))
                        for k, v in o.items()}
            if isinstance(o, list):
                return [nz(x) for x in o]
            return o
        return json.dumps(nz(yaml.safe_load(p.read_text(encoding="utf-8"))),
                          sort_keys=True, ensure_ascii=False)

    a = canon(OFFICIAL); b = canon(REPRO / "OUT_CANARY7.yaml")
    ha = hashlib.sha256(a.encode()).hexdigest(); hb = hashlib.sha256(b.encode()).hexdigest()
    ok7 = (a == b) and r7.returncode == 0
    rec("K7_ZERO_REGRESSAO_TEST_0007", "resultado oficial v0.1.4",
        f"canônico {ha[:16]}…", f"canônico {hb[:16]}…", ok7,
        "margem 44,0 · PASS · reproduzido idêntico")
    d7 = yaml.safe_load((REPRO / "OUT_CANARY7.yaml").read_text(encoding="utf-8"))
    ok7b = (d7["status"] == "VALID" and len(d7["comparisons"]) == 1
            and "comparison_id" not in d7["comparisons"][0]
            and "comparison_dependence" not in d7 and "comparison_identities" not in d7)
    rec("K7_ZERO_REGRESSAO_TEST_0007", "nenhum campo novo vaza para o legado",
        "sem comparison_id / dependence / identities",
        "limpo" if ok7b else "VAZOU", ok7b)

    # ---------------------------------------------------------------- relatório
    approved = all(r["passed"] for r in rows)
    print("=" * 96)
    print("CANÁRIO — EXTENSÃO DE DUAS COMPARAÇÕES (P e F)")
    print("=" * 96)
    cur = None
    for r in rows:
        if r["case"] != cur:
            cur = r["case"]; print(f"\n{cur}")
        print(f"   {'ok ' if r['passed'] else 'FALHOU'} {r['sub']:<42} "
              f"espera {r['expect']}")
        print(f"       obteve: {r['got']}")
        if r["note"]:
            print(f"       {r['note']}")
    print("\n" + "=" * 96)
    print(f"VEREDITO: {'APROVADO' if approved else 'REPROVADO'}  "
          f"({sum(r['passed'] for r in rows)}/{len(rows)})")
    print("=" * 96)
    (LAB / "CANARY-RESULT.json").write_text(
        json.dumps({"approved": approved, "cases": rows,
                    "test0007_canonical_official": ha,
                    "test0007_canonical_extended": hb},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
