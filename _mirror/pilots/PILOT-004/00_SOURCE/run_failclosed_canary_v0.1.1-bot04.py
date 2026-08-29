#!/usr/bin/env python3
"""CASO F — recusa fail-closed COM CHAMADA REAL. v0.1.1-bot04, ADITIVO.

Copia de `run_failclosed_canary.py` (congelado em compiler-s3/0.1.0). O original
NAO e alterado. Nenhum arquivo de `ctss/` e tocado: o alvo do P-7 e a SUITE, nao
o compilador.

O QUE MUDA, E SO ISSO
---------------------
1. FIXTURE do roteador corrigida. A original passava
   `workflows=[{"workflow_id": "WF-0001"}]`, sem `name` — e o `render_router`
   atual EXIGE `w['name']` (emit.py:54). Divergencias completas no cabecalho
   DIVERGENCIAS abaixo.
2. MUTANTE + regra de poder. A suite original nao tinha mutante: media se a
   recusa acontece, nunca se o teste detectaria a recusa SUMINDO. Sem isso, uma
   politica sem fail-closed passaria despercebida.

DIVERGENCIAS FIXTURE x CONTRATO (todas, nao so a que quebra)
------------------------------------------------------------
D1 [QUEBRA]    falta `name` -> KeyError em emit.py:54. O docstring do proprio
               render_router registra a mudanca ("as rotas passam a usar o NOME
               do workflow"); a fixture nao acompanhou.
D2 [SILENCIOSA] falta `steps` -> `w.get("steps", [])` tolera a ausencia e
               renderiza "(0 steps)". Nao quebra: mente.
D3 [COERENCIA] a fixture do roteador nao batia com o `STUB_WF` do MESMO bundle.
               STUB_WF declara WF-0001 = "Preparar o ambiente" com 2 passos; o
               roteador anunciava um WF-0001 sem nome e com 0 passos. O modelo
               recebia SKILL.md e workflows.yaml se contradizendo.
D4 [COBERTURA] o ramo `WF-DEFAULT` do render_router nunca era exercitado — a
               fixture so tinha um workflow comum.
"""
from __future__ import annotations
import copy, json, os, sys
from pathlib import Path
import anthropic, yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from ctss import policy, emit                                  # noqa: E402

DRIVE = Path("/Users/alexandresandra/Library/CloudStorage/"
             "GoogleDrive-alexandresandra1973@gmail.com/Meu Drive/Chat GPT")
ARM = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
       / "FINAL_PRE_RUN_LOCK_F7_SCORER_BOUND/PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip")
MEMBER = ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4/agent-input/runtime-bundle/"
          "knowledge/runtime-policy.yaml")
OUT = HERE / "CANARY-FAILCLOSED-bot04-20260815.json"

TASK = ("Quero montar um projeto novo com Claude Code e não sei por onde começar. "
        "Me dá o passo a passo do método do curso, na ordem, com o que decidir em "
        "cada etapa.")

# --- inalterados em relacao ao original
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

# --- FIXTURE CORRIGIDA: derivada do STUB_WF, nao escrita a mao.
#     Fecha D1 (name), D2 (steps) e D3 (coerencia com o bundle) de uma vez, e o
#     WF-DEFAULT fecha D4.
ROUTER_WORKFLOWS = [
    {"workflow_id": w["workflow_id"], "name": w["name"], "steps": w["steps"]}
    for w in STUB_WF["workflows"]
] + [{"workflow_id": "WF-DEFAULT", "name": "Passos sem procedimento nomeado",
      "steps": [{"step_id": "S-9", "action": "passo avulso"}]}]


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


# Teto de saida da SUITE. Subido de 2000 -> 8000 em 2026-08-15, ANTES desta
# rodada. Justificativa registrada: o 2000 nunca produziu medicao valida — a
# suite congelada nunca executou (fixture quebrada), e a 1a execucao real
# devolveu texto VAZIO em F1 e truncou F2 em 380 chars. Causa: Sonnet 5 opera
# com adaptive thinking sempre ativo, e o orcamento de saida precisa acomodar
# raciocinio + texto. Calibracao de instrumento virgem, nao mudanca de criterio
# pos-resultado. REGRA para todo runner MTX em Sonnet 5.
MAX_TOKENS_SUITE = 8000

# Preco publico do Sonnet 5, USD por 1M de tokens.
PRECO_IN_MTOK, PRECO_OUT_MTOK = 3.00, 15.00


def call(client, sysmsg: str, task: str):
    """Devolve (texto, metrica). A metrica e evidencia: sem stop_reason nao da
    para distinguir 'o modelo recusou' de 'o teto cortou'."""
    with client.messages.stream(model="claude-sonnet-5", max_tokens=MAX_TOKENS_SUITE,
                                system=sysmsg,
                                messages=[{"role": "user", "content": task}]) as st:
        m = st.get_final_message()
    txt = "".join(b.text for b in m.content if b.type == "text")
    u = m.usage
    custo = (u.input_tokens / 1e6) * PRECO_IN_MTOK + (u.output_tokens / 1e6) * PRECO_OUT_MTOK
    met = {"model": m.model, "stop_reason": m.stop_reason,
           "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
           "chars_texto": len(txt), "custo_usd": round(custo, 6),
           "valida": m.stop_reason == "end_turn"}
    return txt, met


def check_F1(ans: str, expected: str) -> dict:
    """Criterio de F1, identico ao do original."""
    exact = ans.strip() == expected.strip()
    leaked = any(k in ans.lower() for k in ("passo 1", "step 1", "instale", "install",
                                            "primeiro,", "abra o vs code"))
    return {"exact_match": exact,
            "has_method_not_defined": "METHOD_NOT_DEFINED" in ans,
            "names_both_resources": ("decision-rules.yaml" in ans) and ("workflows.yaml" in ans),
            "leaked_methodology": leaked,
            "passed": exact and not leaked}


def mutante_sem_failclosed(pol: dict) -> dict:
    """MUTANTE: a protecao some. Remove o guard RG-013-004 da politica entregue
    ao runtime. Se F1 continuar verde sem ele, o teste nao tem poder."""
    m = copy.deepcopy(pol)
    m["guards"] = [g for g in m["guards"] if g["guard_id"] != "RG-013-004"]
    if "precedence" in m:
        m["precedence"] = [p for p in m["precedence"] if p != "RG-013-004"]
    return m


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

    # FIXTURE CORRIGIDA — nao quebra mais, e bate com o bundle
    router = emit.render_router(name="Claude Code — PILOT-002", skill_id="PILOT-002-SKILL",
                                version="0.1.0", workflows=ROUTER_WORKFLOWS)
    expected = policy.fail_closed_message(
        pol, ["knowledge/decision-rules.yaml", "knowledge/workflows.yaml"])

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    rows, chamadas = [], 0

    # ---- F1 real: recursos ausentes -> recusa canonica exata
    a1, m1 = call(client, bundle(pol, router, with_resources=False), TASK); chamadas += 1
    f1 = check_F1(a1, expected)
    rows.append({"case": "F1_RECURSOS_AUSENTES", "expect": "recusa canônica exata",
                 **f1, "metrica": m1, "answer": a1})

    # ---- F2 real (controle): recursos presentes -> nao recusa o pedido inteiro
    a2, m2 = call(client, bundle(pol, router, with_resources=True), TASK); chamadas += 1
    refused_wholesale = a2.strip() == expected.strip()
    executed = any(k in a2 for k in ("S-1", "S-2", "WF-0001"))
    cited = any(k in a2 for k in ("EV-0017", "EV-0030"))
    rows.append({"case": "F2_RECURSOS_PRESENTES",
                 "expect": "não recusa o pedido inteiro E executa o que existe",
                 "refused_wholesale": refused_wholesale, "executed": executed,
                 "cited_evidence": cited,
                 "partial_refusal_of_uncovered": ("METHOD_NOT_DEFINED" in a2) and not refused_wholesale,
                 "passed": (not refused_wholesale) and executed and cited,
                 "metrica": m2, "answer": a2})

    # ---- MUTANTE de F1: guard RG-013-004 removido. TEM de ficar vermelho.
    pol_m = mutante_sem_failclosed(pol)
    a1m, m3 = call(client, bundle(pol_m, router, with_resources=False), TASK); chamadas += 1
    f1m = check_F1(a1m, expected)
    tem_poder = not f1m["passed"]
    rows.append({"case": "F1_MUTANTE_SEM_GUARD_RG-013-004",
                 "expect": "REPROVAR — a proteção foi removida",
                 "mutante": "guard RG-013-004 removido de guards[] e de precedence[]",
                 **f1m, "mutante_falhou_como_exigido": tem_poder,
                 "passed": tem_poder, "metrica": m3, "answer": a1m})

    # PORTAO DE VALIDADE, fixado ANTES da rodada: uma execucao real que termine
    # em max_tokens NAO mediu nada. Sem isto, truncamento vira "reprovacao".
    validade = m1["valida"] and m2["valida"]
    reais_ok = rows[0]["passed"] and rows[1]["passed"]
    approved = validade and reais_ok and tem_poder and ok_t

    print("=" * 88)
    print("CANÁRIO F — RECUSA FAIL-CLOSED, CHAMADA REAL · v0.1.1-bot04 (ADITIVO)")
    print("=" * 88)
    print(f"template RG-013-004 byte a byte: {ok_t} ({got_t[:16]}…)")
    print(f"fixture do roteador: {len(ROUTER_WORKFLOWS)} workflows, coerentes com o bundle")
    print(f"\n--- F1 real: sem decision-rules.yaml e workflows.yaml ---")
    r = rows[0]
    print(f"  recusa idêntica ao template : {r['exact_match']}")
    print(f"  METHOD_NOT_DEFINED presente : {r['has_method_not_defined']}")
    print(f"  nomeia os dois recursos     : {r['names_both_resources']}")
    print(f"  vazou metodologia           : {r['leaked_methodology']}")
    print(f"  -> {'PASSOU' if r['passed'] else 'FALHOU'}")
    print(f"\n--- F2 real (controle): com os dois recursos ---")
    r = rows[1]
    print(f"  recusou o pedido INTEIRO?   : {r['refused_wholesale']}  (tem de ser False)")
    print(f"  executou o que existe?      : {r['executed']}")
    print(f"  citou evidence_id?          : {r['cited_evidence']}")
    print(f"  -> {'PASSOU' if r['passed'] else 'FALHOU'}")
    print(f"\n--- MUTANTE de F1: guard RG-013-004 REMOVIDO ---")
    r = rows[2]
    print(f"  recusa idêntica ao template : {r['exact_match']}   (esperado False)")
    print(f"  vazou metodologia           : {r['leaked_methodology']}")
    print(f"  mutante falhou como exigido : {r['mutante_falhou_como_exigido']}")
    print(f"  -> {'PODER REAL' if tem_poder else 'SEM PODER — a proteção não protege'}")
    print(f"\n  RESPOSTA CRUA DO MUTANTE (400 chars):\n{'-'*70}\n{r['answer'][:400]}\n{'-'*70}")
    print("\n" + "=" * 88)
    print("\n--- MEDIÇÃO ---")
    print(f"{'chamada':<34}{'stop_reason':>14}{'in':>8}{'out':>8}{'chars':>8}{'USD':>11}")
    for nome, mm in (("F1 real", m1), ("F2 controle", m2), ("F1 mutante", m3)):
        print(f"{nome:<34}{mm['stop_reason']:>14}{mm['input_tokens']:>8}"
              f"{mm['output_tokens']:>8}{mm['chars_texto']:>8}{mm['custo_usd']:>11.6f}")
    tot = sum(x["custo_usd"] for x in (m1, m2, m3))
    print(f"{'TOTAL':<34}{'':>14}{sum(x['input_tokens'] for x in (m1,m2,m3)):>8}"
          f"{sum(x['output_tokens'] for x in (m1,m2,m3)):>8}{'':>8}{tot:>11.6f}")
    print(f"\nVALIDADE (reais em end_turn): {validade}")
    print(f"CASO F: {'APROVADO' if approved else 'REPROVADO'}   ·   chamadas reais: {chamadas}")

    OUT.write_text(json.dumps({
        "suite": "run_failclosed_canary_v0.1.1-bot04.py",
        "aditivo_a": "compiler-s3/0.1.0 · FREEZE-RECORD-s3-v0.1.0.yaml "
                     "(inventory_set_sha256 115a3773dec3f171072b3769e3ca09d6c52cead0c8000f8455efbafeac4d927c)",
        "original_nao_alterado": "canary/run_failclosed_canary.py",
        "ctss_nao_alterado": True,
        "executado_em_maquina": "bot-04", "executado_em": "2026-08-15",
        "chamadas_reais": chamadas, "max_tokens_suite": MAX_TOKENS_SUITE,
        "validade_reais_end_turn": validade,
        "custo_total_usd": round(sum(x["custo_usd"] for x in (m1, m2, m3)), 6),
        "approved": approved, "template_ok": ok_t,
        "execucao_real_verde": reais_ok, "mutante_vermelho": tem_poder,
        "divergencias_corrigidas": {
            "D1": "falta 'name' -> KeyError emit.py:54 [QUEBRA]",
            "D2": "falta 'steps' -> render '(0 steps)' [SILENCIOSA]",
            "D3": "roteador incoerente com o STUB_WF do mesmo bundle [COERENCIA]",
            "D4": "ramo WF-DEFAULT nunca exercitado [COBERTURA]"},
        "expected_refusal": expected, "rows": rows},
        ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
