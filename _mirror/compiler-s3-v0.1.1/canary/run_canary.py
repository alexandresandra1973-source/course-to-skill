#!/usr/bin/env python3
"""CANÁRIO do compilador evidência→Skill.

Regra da casa: cada caso roda contra o real (TEM de passar) E contra uma fixture
adulterada (TEM de reprovar). Fixture adulterada que passa = sem poder de
detecção = suíte reprovada.

O caso F é o único com CHAMADA REAL: a recusa fail-closed é comportamento de
runtime e simular seria testar o meu simulador, não a política.
"""
from __future__ import annotations
import hashlib, json, os, sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from ctss import validate, policy, emit, assemble          # noqa: E402
from ctss.schema import PRESERVED                          # noqa: E402

DRIVE = Path("/Users/alexandresandra/Library/CloudStorage/GoogleDrive-alexandresandra1973@gmail.com/Meu Drive/Chat GPT")
ARM = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
       / "FINAL_PRE_RUN_LOCK_F7_SCORER_BOUND/PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip")
MEMBER = ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4/agent-input/runtime-bundle/"
          "knowledge/runtime-policy.yaml")
EV = DRIVE / "Course-to-Skill-Claude/pilots/PILOT-002-v2/EVIDENCE.jsonl"

ROWS = []


def rec(case, sub, expect, got, ok, note=""):
    ROWS.append({"case": case, "sub": sub, "expect": expect, "got": got,
                 "passed": ok, "note": note})


def good_rule(eids):
    return {"rule_id": "R-0001", "name": "regra boa", "trigger": "t", "condition": "c",
            "action": "a", "autonomy": "UNDEFINED", "precedence": "UNDEFINED",
            "missing_input_action": "ASK_USER", "iteration_limit": "UNDEFINED",
            "do_not": [], "evidence_ids": eids, "origin_class": "SOURCE_EXPLICIT",
            "segment_ids": ["SEG-001"]}


def main() -> int:
    evidence = [json.loads(l) for l in EV.read_text(encoding="utf-8").splitlines() if l.strip()]
    known = {e["evidence_id"] for e in evidence}
    e0 = evidence[0]["evidence_id"]

    # ---------------- A: regra sem evidence_id
    rec("A_REGRA_SEM_EVIDENCE_ID", "regra real", "aceita",
        validate.validate_entity(good_rule([e0]), "rule", known) or "limpa",
        not validate.validate_entity(good_rule([e0]), "rule", known))
    bad = good_rule([])
    errs = validate.validate_entity(bad, "rule", known)
    rec("A_REGRA_SEM_EVIDENCE_ID", "fixture sem evidence_ids", "REJEITA",
        [e["code"] for e in errs], any(e["code"] == "RULE_WITHOUT_EVIDENCE" for e in errs))

    # ---------------- B: evidence_id inexistente
    bad = good_rule(["EV-9999"])
    errs = validate.validate_entity(bad, "rule", known)
    rec("B_EVIDENCE_ID_INEXISTENTE", "fixture citando EV-9999", "REJEITA",
        [e["code"] for e in errs], any(e["code"] == "EVIDENCE_ID_UNKNOWN" for e in errs))

    # ---------------- C: SKILL.md com regra executável
    wfs = [{"workflow_id": "WF-0001", "name": "instalar", "steps": ["S-1"]}]
    args = dict(name="X", skill_id="S", version="0.1.0", workflows=wfs)
    router = emit.render_router(**args)
    expected = emit.render_router(**args)          # reconstrucao independente
    rec("C_SKILL_MD_ROTEADOR", "roteador reconstruivel do template", "aceito",
        validate.validate_router(router, expected=expected) or "limpo",
        not validate.validate_router(router, expected=expected),
        "gerado por script, nunca ve modelo: a propriedade e ESTRUTURAL")
    inj = ("\n\nSe o usuario nao definiu o outcome, pergunte primeiro qual e o "
           "resultado desejado.\n")
    tampered = router.replace("## DISPATCH", "## DISPATCH" + inj, 1)
    errs = validate.validate_router(tampered, expected=expected)
    rec("C_SKILL_MD_ROTEADOR", "fixture com regra colada no corpo", "REJEITA",
        [e["code"] for e in errs],
        any(e["code"] == "SKILL_MD_CONTAINS_RULE" for e in errs))
    errs2 = validate.validate_router("", dispatch_lines=[
        "- Se o outcome nao estiver definido, pergunte antes de rotear."])
    rec("C_SKILL_MD_ROTEADOR", "varredura do bloco DISPATCH (2a ancora)", "REJEITA",
        [e["code"] for e in errs2], bool(errs2),
        "segunda ancora, caso alguem regenere com template adulterado")
    ok_clean = not validate.validate_router("", dispatch_lines=[
        "- Methodology decision request: apply knowledge/decision-rules.yaml."])
    rec("C_SKILL_MD_ROTEADOR", "rota legitima nao e acusada", "aceita",
        "limpa" if ok_clean else "FALSO POSITIVO", ok_clean)

    # ---------------- D: campo sem evidência que não sai UNDEFINED
    bad = good_rule([e0]); bad["precedence"] = None
    errs = validate.validate_entity(bad, "rule", known)
    rec("D_CAMPO_NAO_UNDEFINED", "fixture com precedence=None", "REJEITA",
        [e["code"] for e in errs], any(e["code"] == "FIELD_NOT_UNDEFINED" for e in errs),
        f"os quatro preservados por decisão: {PRESERVED}")
    disp = {e["evidence_id"]: "NON_METHODOLOGICAL" for e in evidence}
    rec("D_CONTABILIDADE_EXAUSTIVA", "todas as 448 com disposição", "aceita",
        validate.validate_accounting(known, disp) or "limpa",
        not validate.validate_accounting(known, disp))
    d2 = dict(disp); d2.pop(e0)
    errs = validate.validate_accounting(known, d2)
    rec("D_CONTABILIDADE_EXAUSTIVA", "fixture com uma evidência sem disposição",
        "REJEITA", [e["code"] for e in errs],
        any(e["code"] == "EVIDENCE_WITHOUT_DISPOSITION" for e in errs))

    # ---------------- E: lacuna ausente do gap report
    r = good_rule([e0])
    gaps = emit.collect_gaps([r], [], {e0: "CONSUMED_BY_RULE"}, evidence,
                             {e0: "SOURCE_EXPLICIT"}, validate.rule_is_course_gap)
    report = emit.render_gap_report(gaps, "# gaps")
    rec("E_LACUNA_NO_GAP_REPORT", f"{len(gaps)} lacunas medidas, todas no relatório",
        "aceito", validate.validate_gap_report(report, gaps) or "limpo",
        not validate.validate_gap_report(report, gaps))
    trimmed = "\n".join(l for l in report.splitlines() if gaps[0]["gap_id"] not in l)
    errs = validate.validate_gap_report(trimmed, gaps)
    rec("E_LACUNA_NO_GAP_REPORT", "fixture com uma lacuna suprimida", "REJEITA",
        [e["code"] for e in errs], any(e["code"] == "GAP_NOT_REPORTED" for e in errs))
    # regra apoiada só em inferência genuína vira lacuna
    only_inf = validate.rule_is_course_gap(r, {e0: "GENUINE_INFERENCE"})
    mixed = validate.rule_is_course_gap(good_rule([e0, evidence[1]["evidence_id"]]),
                                        {e0: "GENUINE_INFERENCE",
                                         evidence[1]["evidence_id"]: "SOURCE_EXPLICIT"})
    rec("E_REGRA_SO_DE_INFERENCIA", "só inferência genuína → LACUNA", "True/False",
        f"só-inferência={only_inf} · mista={mixed}", only_inf and not mixed,
        "é a diferença entre avaliar o curso e avaliar o modelo")

    # ---------------- policy derivada
    canon, sha = policy.load_canonical(ARM, MEMBER)
    p = policy.derive(canon, skill_id="PILOT-002-SKILL", skill_version="0.1.0",
                      scope_condition="Primary request is outside Claude Code setup, "
                                      "usage, skills, context, version control, MCP/CLI "
                                      "or deployment as taught in this course.",
                      scope_justification={
                          "kind": "DECISAO_DE_INSTRUMENTO",
                          "rationale": ("o escopo delimita o que a Skill aceita responder; "
                                        "a fonte não enuncia a sua própria fronteira, "
                                        "então isto é decisão de instrumento e não "
                                        "conteúdo do curso"),
                          "nao_e_conteudo_da_fonte": True})
    ok_t, got_t = policy.verify_template_byte_identical(p)
    rec("P_TEMPLATE_BYTE_IDENTICO", "RG-013-004 na policy derivada",
        policy.CANONICAL_TEMPLATE_SHA[:16] + "…", got_t[:16] + "…", ok_t,
        "parametrizar o escopo não pode tocar a redação da recusa")
    try:
        policy.derive(canon, skill_id="X", skill_version="1", scope_condition="algo",
                      scope_justification={})
        silent_ok = False
    except ValueError:
        silent_ok = True
    rec("P_ESCOPO_EXIGE_JUSTIFICATIVA", "fixture sem justificativa", "REJEITA",
        "ValueError" if silent_ok else "PASSOU", silent_ok,
        "silêncio não serve: é o único texto escrito à mão")

    (HERE / "derived-runtime-policy.yaml").write_text(
        yaml.safe_dump(p, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")

    approved = all(r["passed"] for r in ROWS)
    print("=" * 92)
    print("CANÁRIO — COMPILADOR EVIDÊNCIA → SKILL (casos estáticos)")
    print("=" * 92)
    cur = None
    for r in ROWS:
        if r["case"] != cur:
            cur = r["case"]; print(f"\n{cur}")
        print(f"   {'ok ' if r['passed'] else 'FALHOU'} {r['sub']:<44} espera {r['expect']}")
        print(f"       obteve: {r['got']}")
        if r["note"]:
            print(f"       {r['note']}")
    print("\n" + "=" * 92)
    print(f"ESTÁTICOS: {'APROVADO' if approved else 'REPROVADO'} "
          f"({sum(r['passed'] for r in ROWS)}/{len(ROWS)})")
    print("Falta o caso F — recusa fail-closed COM CHAMADA REAL: run_failclosed_canary.py")
    (HERE / "CANARY-STATIC-RESULT.json").write_text(
        json.dumps({"approved": approved, "cases": ROWS}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    return 0 if approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
