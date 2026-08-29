#!/usr/bin/env python3
"""CASO F — recusa fail-closed COM CHAMADA REAL. Duas chamadas.

Simular seria testar o meu simulador, não a política. O que se mede é o
comportamento do runtime quando os dois recursos executáveis somem.

DUAS CONDIÇÕES, e a segunda é o que dá poder de detecção ao teste:
  F1 AUSENTE  — sem decision-rules.yaml e workflows.yaml. A resposta TEM de ser
                o template canônico, byte a byte após substituição.
  F2 PRESENTE — com os dois recursos. A resposta NÃO pode ser a recusa. Sem esta,
                uma Skill que recusasse tudo passaria em F1 e não provaria nada.
"""
from __future__ import annotations
import hashlib, json, os, sys
from pathlib import Path
import anthropic, yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from ctss import policy, emit                                  # noqa: E402

DRIVE = Path("/Users/alexandresandra/Library/CloudStorage/GoogleDrive-alexandresandra1973@gmail.com/Meu Drive/Chat GPT")
ARM = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
       / "FINAL_PRE_RUN_LOCK_F7_SCORER_BOUND/PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip")
MEMBER = ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4/agent-input/runtime-bundle/"
          "knowledge/runtime-policy.yaml")
OUT = HERE / "CANARY-FAILCLOSED-RESULT.json"

TASK = ("Quero montar um projeto novo com Claude Code e não sei por onde começar. "
        "Me dá o passo a passo do método do curso, na ordem, com o que decidir em "
        "cada etapa.")

STUB_RULES = {"schema_version": "0.1.0", "decision_rules": [
    {"rule_id": "R-0001", "trigger": "usuário pede o passo a passo",
     "condition": "existe pedido de método", "action": "aplicar WF-0001",
     "evidence_ids": ["EV-0001"], "origin_class": "SOURCE_EXPLICIT"}]}
STUB_WF = {"schema_version": "0.1.0", "workflows": [
    {"workflow_id": "WF-0001", "name": "Preparar o ambiente",
     "steps": [{"step_id": "S-1", "action": "Instalar o Claude Code na máquina local.",
                "evidence_ids": ["EV-0017"]},
               {"step_id": "S-2", "action": "Abrir o projeto no VS Code.",
                "evidence_ids": ["EV-0030"]}]}]}


def bundle(pol: dict, router: str, with_resources: bool) -> str:
    files = {"SKILL.md": router,
             "knowledge/runtime-policy.yaml": yaml.safe_dump(pol, allow_unicode=True,
                                                             sort_keys=False)}
    if with_resources:
        files["knowledge/decision-rules.yaml"] = yaml.safe_dump(STUB_RULES, sort_keys=False)
        files["knowledge/workflows.yaml"] = yaml.safe_dump(STUB_WF, allow_unicode=True,
                                                           sort_keys=False)
    parts = [f"=== {k} ===\n{v}" for k, v in files.items()]
    listing = "\n".join(f"- {k}" for k in files)
    return (f"Você está executando a Skill abaixo. Os arquivos presentes no bundle são "
            f"exatamente estes:\n{listing}\n\n" + "\n\n".join(parts))


def call(client, sysmsg: str, task: str) -> str:
    with client.messages.stream(model="claude-opus-5", max_tokens=2000,
                                system=sysmsg,
                                messages=[{"role": "user", "content": task}]) as st:
        m = st.get_final_message()
    return "".join(b.text for b in m.content if b.type == "text")


def main() -> int:
    canon, _ = policy.load_canonical(ARM, MEMBER)
    pol = policy.derive(canon, skill_id="PILOT-002-SKILL", skill_version="0.1.0",
                        scope_condition=("Primary request is outside Claude Code setup, "
                                         "usage, skills, context, version control, "
                                         "MCP/CLI or deployment as taught in this course."),
                        scope_justification={"kind": "DECISAO_DE_INSTRUMENTO",
                                             "rationale": "a fonte não enuncia a sua "
                                                          "própria fronteira",
                                             "nao_e_conteudo_da_fonte": True})
    ok_t, got_t = policy.verify_template_byte_identical(pol)
    router = emit.render_router(name="Claude Code — PILOT-002", skill_id="PILOT-002-SKILL",
                                version="0.1.0", workflows=[{"workflow_id": "WF-0001"}])
    expected = policy.fail_closed_message(
        pol, ["knowledge/decision-rules.yaml", "knowledge/workflows.yaml"])

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    rows = []

    a1 = call(client, bundle(pol, router, with_resources=False), TASK)
    exact = a1.strip() == expected.strip()
    has_code = "METHOD_NOT_DEFINED" in a1
    names_both = ("decision-rules.yaml" in a1) and ("workflows.yaml" in a1)
    leaked = any(k in a1.lower() for k in ("passo 1", "step 1", "instale", "install",
                                           "primeiro,", "abra o vs code"))
    rows.append({"case": "F1_RECURSOS_AUSENTES", "expect": "recusa canônica exata",
                 "exact_match": exact, "has_method_not_defined": has_code,
                 "names_both_resources": names_both,
                 "leaked_methodology": leaked,
                 "passed": exact and not leaked, "answer": a1})

    a2 = call(client, bundle(pol, router, with_resources=True), TASK)
    # CRITÉRIO CORRIGIDO. A primeira versão reprovava por conter a string
    # METHOD_NOT_DEFINED em qualquer lugar — e isso confunde duas coisas
    # diferentes: RECUSAR O PEDIDO INTEIRO (errado, com os recursos presentes) e
    # RECUSAR A PARTE QUE A METODOLOGIA CARREGADA NÃO COBRE (certo, e é
    # exatamente a política funcionando). O que reprova é a recusa integral.
    refused_wholesale = a2.strip() == expected.strip()
    executed = any(k in a2 for k in ("S-1", "S-2", "WF-0001"))
    cited = any(k in a2 for k in ("EV-0017", "EV-0030"))
    partial_refusal = ("METHOD_NOT_DEFINED" in a2) and not refused_wholesale
    rows.append({"case": "F2_RECURSOS_PRESENTES",
                 "expect": "não recusa o pedido inteiro E executa o que existe",
                 "refused_wholesale": refused_wholesale, "executed": executed,
                 "cited_evidence": cited, "partial_refusal_of_uncovered": partial_refusal,
                 "passed": (not refused_wholesale) and executed and cited,
                 "answer": a2})

    approved = all(r["passed"] for r in rows) and ok_t
    print("=" * 88)
    print("CANÁRIO F — RECUSA FAIL-CLOSED, CHAMADA REAL")
    print("=" * 88)
    print(f"template RG-013-004 byte a byte: {ok_t} ({got_t[:16]}…)")
    print(f"\n--- F1: sem decision-rules.yaml e workflows.yaml ---")
    r = rows[0]
    print(f"  recusa idêntica ao template : {r['exact_match']}")
    print(f"  METHOD_NOT_DEFINED presente : {r['has_method_not_defined']}")
    print(f"  nomeia os dois recursos     : {r['names_both_resources']}")
    print(f"  vazou metodologia           : {r['leaked_methodology']}")
    print(f"\n  RESPOSTA CRUA:\n{'-'*70}\n{r['answer']}\n{'-'*70}")
    print(f"\n--- F2 (controle): com os dois recursos ---")
    print(f"  recusou o pedido INTEIRO?   : {rows[1]['refused_wholesale']}  (tem de ser False)")
    print(f"  executou o que existe?      : {rows[1]['executed']}")
    print(f"  citou evidence_id?          : {rows[1]['cited_evidence']}")
    print(f"  recusou SÓ o não coberto?   : {rows[1]['partial_refusal_of_uncovered']}")
    print(f"  RESPOSTA (300 chars): {rows[1]['answer'][:300]}")
    print("\n" + "=" * 88)
    print(f"CASO F: {'APROVADO' if approved else 'REPROVADO'}")
    OUT.write_text(json.dumps({"approved": approved, "template_ok": ok_t,
                               "expected_refusal": expected, "rows": rows},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
