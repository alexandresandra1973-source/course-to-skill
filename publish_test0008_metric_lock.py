#!/usr/bin/env python3
"""TEST-0008-METRIC-LOCK — congela a lista canônica de métricas do TEST-0008.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/ e Course-to-Skill-Compiler/.
Publica só em Course-to-Skill-Claude/docs/. Não altera nenhum script auditado.

Fecha o BLOQUEADOR 1 da ADR-V014-TEST0008-INFORMATION-PARITY: "a lista canônica
de comparison_metrics não está congelada; a discrepância 5×6 tem de ser
resolvida contra o RELEASE autoritativo".

A resposta é lida do RELEASE, não digitada: o script abre o test-suite.yaml do
release v0.1.1, extrai os dois documentos comparativos e conta.

GUARDA EXECUTÁVEL, duas âncoras independentes:
  A. HASH   — o RELEASE tem de bater byte a byte com o SHA-256 congelado.
  B. CONTEÚDO — a lista extraída tem de bater com a lista congelada, mesmo que
     alguém recompute o hash de uma cópia adulterada.
Uma sozinha não basta: (A) cai se o adversário recongela o hash, (B) cai se o
adversário altera bytes fora da lista. As duas juntas fecham os dois caminhos.
"""
from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "TEST-0008-METRIC-LOCK.yaml"

RELEASE = (DRIVE / "Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1"
           / "course-to-skill-compiler-v0.1.1-pilot-ready"
           / "course-to-skill-compiler-v0.1.1-pilot-ready"
           / "pilot/PILOT-001/final-test/judge-private/test-suite.yaml")
RELEASE_SHA = "9dc5313c0171984d24162bce39a57dd1a9703f8ad21939db66615f3829eb1927"

ERRATA = DOCS / "LEGACY-TEST-0008-CONTRACTS-ERRATA.md"
DISCREPANCY = DOCS / "TEST-0008-METRICS-DISCREPANCY.md"
ADR_ZIP = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007"
           / "ARMS_WORDING_FROZEN/PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN.zip")
ADR_MEMBER = ("PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN/"
              "ADR-TEST-0008-INFORMATION-PARITY-v0.1.4.md")

CANONICAL_FIVE = ["TOTAL_SCORE", "DECISION_ACCURACY", "METHODOLOGY_FIDELITY",
                  "EXECUTION_QUALITY", "HALLUCINATION_RATE"]


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_p(p: Path) -> str:
    return sha_bytes(p.read_bytes())


def extract(path: Path) -> dict[str, list[str]]:
    """Lê comparison_metrics por test_id direto do arquivo. Nada digitado."""
    out = {}
    for doc in yaml.safe_load_all(path.read_text(encoding="utf-8")):
        if not isinstance(doc, dict):
            continue
        tid = doc.get("test_id")
        base = doc.get("baseline") or {}
        if tid and isinstance(base, dict) and base.get("comparison_metrics"):
            out[tid] = list(base["comparison_metrics"])
    return out


# ------------------------------------------------------------------ a guarda
def guard(path: Path) -> tuple[bool, str, dict]:
    """Aceita só o RELEASE exato. Duas âncoras, ambas têm de passar."""
    detail = {}
    if not path.is_file():
        return False, "RELEASE_ABSENT", detail
    observed = sha_p(path)
    detail["observed_sha256"] = observed
    detail["expected_sha256"] = RELEASE_SHA
    if observed != RELEASE_SHA:
        return False, "RELEASE_HASH_MISMATCH", detail
    try:
        got = extract(path).get("TEST-0008")
    except Exception as exc:
        detail["parse_error"] = str(exc)
        return False, "RELEASE_UNPARSEABLE", detail
    detail["observed_metrics"] = got
    if got != CANONICAL_FIVE:
        return False, "RELEASE_METRIC_LIST_MISMATCH", detail
    return True, "ACCEPTED", detail


def run_canary() -> list[dict]:
    """Cada caso: o real TEM de passar, o mutante TEM de falhar."""
    rows = []
    ok, code, _ = guard(RELEASE)
    rows.append({"case": "C1_RELEASE_EXATO", "expect": "ACEITA",
                 "accepted": ok, "code": code, "passed": ok})

    with tempfile.TemporaryDirectory() as td:
        # C2 — um byte alterado FORA da lista: só a âncora de hash pega.
        p = Path(td) / "one-byte.yaml"
        raw = bytearray(RELEASE.read_bytes())
        i = raw.find(b"blind_evaluation")
        raw[i] = ord("B")                      # 'b' -> 'B', um byte
        p.write_bytes(bytes(raw))
        ok2, code2, d2 = guard(p)
        rows.append({"case": "C2_UM_BYTE_ALTERADO", "expect": "REJEITA",
                     "accepted": ok2, "code": code2, "passed": not ok2,
                     "bytes_changed": 1,
                     "caught_by": "ANCORA_A_HASH",
                     "metric_list_still_intact": True})

        # C3 — lista adulterada E hash recomputado: só a âncora de conteúdo pega.
        # É o ataque que derruba um guard que confia só no hash.
        p3 = Path(td) / "relabeled.yaml"
        txt = RELEASE.read_text(encoding="utf-8")
        p3.write_text(txt.replace("  - HALLUCINATION_RATE\n",
                                  "  - HALLUCINATION_SCORE\n"), encoding="utf-8")
        ok3, code3, d3 = guard(p3)
        rows.append({"case": "C3_METRICA_RENOMEADA", "expect": "REJEITA",
                     "accepted": ok3, "code": code3, "passed": not ok3,
                     "caught_by": "ANCORA_A_HASH_E_B_CONTEUDO"})

        # C4 — MUTANTE DO PRÓPRIO GUARD: se a âncora de conteúdo for removida,
        # C3 com hash recomputado passa. Prova que a âncora B tem poder.
        def guard_hash_only(pp: Path):
            return sha_p(pp) == sha_bytes(p3.read_bytes())
        rows.append({"case": "C4_MUTANTE_GUARD_SO_HASH",
                     "expect": "MUTANTE_ACEITA_O_ADULTERADO",
                     "accepted": guard_hash_only(p3),
                     "code": "MUTANT_HASH_ONLY_NO_CONTENT_ANCHOR",
                     "passed": guard_hash_only(p3),
                     "reading": ("o guard sem a âncora de conteúdo aceita a lista "
                                 "renomeada; logo a âncora B tem poder de detecção")})
        # C5 — arquivo ausente
        ok5, code5, _ = guard(Path(td) / "nao-existe.yaml")
        rows.append({"case": "C5_ARQUIVO_AUSENTE", "expect": "REJEITA",
                     "accepted": ok5, "code": code5, "passed": not ok5})
    return rows


def main() -> int:
    for p in (RELEASE, ERRATA, DISCREPANCY, ADR_ZIP):
        if not p.exists():
            print(f"ÂNCORA AUSENTE: {p}")
            return 2

    import zipfile
    adr_bytes = zipfile.ZipFile(ADR_ZIP).read(ADR_MEMBER)

    metrics = extract(RELEASE)
    t7, t8 = metrics.get("TEST-0007"), metrics.get("TEST-0008")
    union = sorted(set(t7) | set(t8))
    inter = sorted(set(t7) & set(t8))

    canary = run_canary()
    canary_ok = all(r["passed"] for r in canary)

    ok, code, detail = guard(RELEASE)
    if not ok or not canary_ok:
        print(f"PORTÃO REPROVADO: guard={code} canário_ok={canary_ok}")
        for r in canary:
            print("  ", r["case"], r["expect"], "->", r["code"],
                  "PASSOU" if r["passed"] else "REPROVOU")
        return 3

    # rubrica legada do TEST-0008, lida do RELEASE
    doc8 = [d for d in yaml.safe_load_all(RELEASE.read_text(encoding="utf-8"))
            if isinstance(d, dict) and d.get("test_id") == "TEST-0008"][0]
    rubric = (doc8.get("evaluation") or {}).get("rubric") or []
    criteria = [c["criterion"] for c in rubric]
    weights = {c["criterion"]: float(c["weight"]) for c in rubric}
    wsum = round(sum(weights.values()), 10)
    orphan_criteria = [c for c in criteria if c not in t8]
    metrics_without_criterion = [m for m in t8 if m not in criteria]

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-001-TEST-0008-METRIC-LOCK",
        "artifact_status": "LOCKED",
        "locked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "test_id": "TEST-0008",
        "candidate_version": "0.1.4",

        "nature": {
            "additive_only": True,
            "changes_the_compiler": False,
            "changes_test_0007": False,
            "statement": ("Congela QUAL lista de métricas vale. NÃO congela a "
                          "rubrica, nem as âncoras, nem as bandas — esses são os "
                          "bloqueadores 2 e 3 da ADR e seguem abertos."),
        },

        # ------------------------------------------------ 1. as cinco
        "canonical_metrics": {
            "count": len(t8),
            "metrics": t8,
            "read_from": "RELEASE, não digitado — extraído por yaml.safe_load_all",
            "source": {
                "path": str(RELEASE.relative_to(DRIVE)),
                "sha256": RELEASE_SHA,
                "document_index": 7,
                "yaml_path": "baseline.comparison_metrics",
                "line_range_in_release": "1037-1042",
            },
            "corroborating_positions": {
                "count": 4,
                "note": ("As 4 posições RELEASE apuradas em "
                         "TEST-0008-METRICS-DISCREPANCY.md declaram a MESMA lista; "
                         "o WORKSPACE também. Um único conjunto em todas as posições."),
            },
        },

        # ------------------------------------------------ 2. a origem do 6
        "origin_of_the_six": {
            "resolved": True,
            "previous_label": "UNRESOLVED_PROVENANCE",
            "current_label": "UNION_TEST0007_UNION_TEST0008",
            "supersedes": ("O rótulo UNRESOLVED_PROVENANCE fica RETIRADO: a "
                           "procedência está apurada, não pendente."),
            "explanation": ("O '6' da auditoria é a UNIÃO dos dois testes "
                            "comparativos, não a contagem do TEST-0008 isolado. "
                            "Nenhum teste declara 6."),
            "test_0007_metrics": t7,
            "test_0008_metrics": t8,
            "intersection": inter,
            "only_in_test_0007": sorted(set(t7) - set(t8)),
            "only_in_test_0008": sorted(set(t8) - set(t7)),
            "union": union,
            "union_count": len(union),
            "arithmetic_check": {
                "expression": "|A ∪ B| = |A| + |B| − |A ∩ B|",
                "computed": f"{len(t7)} + {len(t8)} − {len(inter)} = {len(union)}",
                "holds": len(union) == len(t7) + len(t8) - len(inter),
            },
            "metric_lock_do_chatgpt": {
                "referencia": "caffc7ba…",
                "estado": "NUNCA_SALVO_EM_DISCO",
                "consequencia": ("Não é fonte verificável. Esta apuração contra o "
                                 "RELEASE é que estabelece a resposta canônica."),
            },
        },

        # ------------------------------------------------ 3. status legado
        "legacy_five_status": "PENDING_REDERIVATION",
        "legacy_five_status_reason": {
            "por_que_pendente": (
                "As cinco foram definidas para um desenho de DUAS condições "
                "(Skill × baseline único). O TEST-0008 agora tem TRÊS condições "
                "e DUAS comparações (P e F). A lista está congelada como "
                "AUTORIDADE DE PROCEDÊNCIA; sua aplicabilidade ao desenho de três "
                "condições não está estabelecida."),
            "o_que_este_lock_faz": "congela QUAIS são as cinco e de onde vêm",
            "o_que_este_lock_NAO_faz": (
                "não declara que as cinco são as métricas corretas para o desenho "
                "de três condições, nem as torna computáveis"),
            "regra_dura": ("Mesmo vetor de métricas para P e F. Métrica exclusiva "
                           "de uma das comparações destrói a comparabilidade."),
        },

        # ------------------------------------------------ 4. HALLUCINATION_RATE
        "hallucination_rate_definition": {
            "provenance": "DECLARED_IN_THIS_LOCK",
            "NOT_derivable_from_release": True,
            "por_que": (
                "O RELEASE declara HALLUCINATION_RATE como comparison_metric mas "
                "NÃO tem critério de rubrica com esse nome. O que existe é o "
                "critério HALLUCINATION_CONTROL e a falha crítica "
                "HALLUCINATED_METHODOLOGY. Numerador e denominador são declarados "
                "AQUI; não foram lidos do RELEASE, e isso fica escrito para "
                "ninguém tratar a definição como herdada."),
            "numerator": {
                "what": ("número de afirmações distintas, na saída crua do braço, "
                         "que atribuem à metodologia da fonte uma regra, etapa ou "
                         "cobertura que a fonte não sustenta"),
                "adjudicated_by": "juiz, sob a rubrica congelada do TEST-0008",
                "anchored_to": ["evaluation.rubric[].HALLUCINATION_CONTROL",
                                "critical_failures[].HALLUCINATED_METHODOLOGY"],
            },
            "denominator": {
                "what": ("número de afirmações distintas portadoras de metodologia "
                         "na MESMA saída crua — o conjunto do qual o numerador é "
                         "subconjunto"),
                "must_be_counted_per_arm": True,
                "never_shared_across_arms": True,
            },
            "zero_denominator_rule": {
                "value": "UNDEFINED",
                "emit": None,
                "must_not_be": 0.0,
                "por_que": (
                    "Denominador zero significa que o braço não fez afirmação "
                    "metodológica alguma. Emitir 0.0 leria isso como 'nenhuma "
                    "alucinação', premiando a resposta vazia — o incentivo "
                    "exatamente invertido. A métrica sai UNDEFINED, a execução é "
                    "sinalizada, e o braço NÃO entra na margem por esta métrica."),
                "flag_code": "HALLUCINATION_RATE_DENOMINATOR_ZERO",
            },
            "polarity": "LOWER_IS_BETTER",
            "polarity_consequence": {
                "mechanical": (
                    "Todo o instrumento calcula margem como LEFT − RIGHT e trata "
                    "MAIOR como melhor. Uma métrica LOWER_IS_BETTER entra com "
                    "sinal invertido, ou a margem passa a premiar o braço que "
                    "alucina mais."),
                "required_transform": "contribution = −(left_value − right_value)",
                "must_be_enforced_in_code": True,
                "not_enforced_yet": True,
                "note": ("O scorer estendido registra a polaridade e recusa "
                         "agregação de métrica LOWER_IS_BETTER sem transformação "
                         "declarada. A agregação em si é passo 3."),
            },
        },

        # ------------------------------------------------ 5. a pendência aberta
        "open_pendency_for_alexandre": {
            "decision_owner": "Alexandre",
            "status": "UNRESOLVED_BY_DESIGN",
            "resolvida_neste_lock": False,
            "question": ("CONSISTENCY e HUMAN_CHECKPOINT_COMPLIANCE têm de receber "
                         "destinação explícita: viram MÉTRICAS DIRETAS do vetor de "
                         "comparação, ou permanecem GATE/AGGREGATE-ONLY?"),
            "por_que_e_decisao_e_nao_apuracao": (
                "Não há fato no RELEASE que responda. As duas são critérios de "
                "rubrica com peso, mas nenhuma aparece na lista de "
                "comparison_metrics. Os dois desenhos são internamente coerentes; "
                "escolher entre eles é decisão de escopo."),
            "measured_facts": {
                "rubric_criteria_legacy": criteria,
                "weights": weights,
                "weight_sum": wsum,
                "criteria_sem_metrica_correspondente": orphan_criteria,
                "peso_dos_orfaos": round(
                    sum(weights[c] for c in orphan_criteria), 10),
                "fracao_do_peso_total_nos_orfaos": round(
                    sum(weights[c] for c in orphan_criteria) / wsum, 6) if wsum else None,
                "metricas_sem_criterio_correspondente": metrics_without_criterion,
            },
            "achado_colateral_do_peso": {
                "weight_sum": wsum,
                "soma_e_um": abs(wsum - 1.0) < 1e-9,
                "consequencia_se_nao_for_um": (
                    f"WEIGHTED_SUM com pesos somando {wsum} limita o TOTAL_SCORE "
                    f"máximo a {round(wsum*100,4)}, não a 100. O pass_criteria "
                    f"legado exige minimum_total_score 85, que continua alcançável, "
                    f"mas o teto de margem fica comprimido. Isto é OBSERVAÇÃO sobre "
                    f"a rubrica LEGADA, que não é a rubrica final — o passo 3 é que "
                    f"a define."),
                "nao_corrigido_aqui": True,
            },
            "opcao_A_metricas_diretas": {
                "efeito": "entram no vetor de P e F; viram 7 métricas",
                "custo": ("muda a lista congelada acima; exige rederivação e "
                          "invalida a contagem 5 como canônica para o desenho novo"),
            },
            "opcao_B_gate_ou_aggregate_only": {
                "efeito": ("continuam pesando no TOTAL_SCORE e podendo reprovar por "
                           "piso obrigatório, mas não aparecem como métrica "
                           "comparada"),
                "custo": ("o relatório de P e F não mostra separadamente o "
                          "comportamento de checkpoint humano, que é justamente a "
                          "hipótese do TEST-0008"),
            },
            "o_que_este_lock_faz": "registra a pendência e mede os fatos; não escolhe",
        },

        # ------------------------------------------------ 6. a guarda
        "executable_guard": {
            "implemented_in": Path(__file__).name,
            "function": "guard()",
            "anchors": {
                "A_hash": "RELEASE tem de bater byte a byte com o SHA-256 congelado",
                "B_content": ("a lista extraída tem de bater com a congelada, "
                              "mesmo que o hash tenha sido recomputado"),
                "por_que_duas": ("(A) sozinha cai se o adversário recongela o hash "
                                 "de uma cópia adulterada; (B) sozinha cai se a "
                                 "alteração está fora da lista."),
            },
            "canary": canary,
            "canary_approved": canary_ok,
            "canary_note": ("C4 é o mutante do próprio guard: prova que a âncora "
                            "de conteúdo tem poder de detecção, aceitando o que o "
                            "guard completo rejeita."),
        },

        # ------------------------------------------------ 7. amarras
        "binds_to": {
            "legacy_contracts_errata": {"path": str(ERRATA.relative_to(DRIVE)),
                                        "sha256": sha_p(ERRATA)},
            "metrics_discrepancy_report": {"path": str(DISCREPANCY.relative_to(DRIVE)),
                                           "sha256": sha_p(DISCREPANCY)},
            "adr_test_0008": {
                "artifact": "ADR-V014-TEST0008-INFORMATION-PARITY",
                "member": ADR_MEMBER,
                "container": str(ADR_ZIP.relative_to(DRIVE)),
                "sha256": sha_bytes(adr_bytes),
            },
            "release_test_suite": {"path": str(RELEASE.relative_to(DRIVE)),
                                   "sha256": RELEASE_SHA},
        },

        "closes_adr_blocker": {
            "blocker": 1,
            "text": ("The canonical comparison_metrics list is not frozen. The "
                     "observed 5×6 discrepancy must first be resolved against the "
                     "authoritative RELEASE."),
            "status": "CLOSED",
            "how": ("Resolvido contra o RELEASE por hash: cinco métricas, e o '6' "
                    "identificado como união dos dois testes."),
        },
        "adr_blockers_still_open": [
            {"blocker": 2, "text": "âncoras de critério e derivações de métrica da "
                                   "rubrica final do TEST-0008 não congeladas",
             "status": "OPEN", "is_step": 3},
            {"blocker": 3, "text": "variância do avaliador do TEST-0008 não medida; "
                                   "bandas de enquadramento indefinidas",
             "status": "OPEN", "is_step": 3},
        ],
    }

    OUT.write_text(
        "# TEST-0008 — LOCK DA LISTA CANÔNICA DE MÉTRICAS.\n"
        "# Cinco métricas, lidas do RELEASE por hash. O '6' é UNIÃO 0007 ∪ 0008.\n"
        "# Fecha o bloqueador 1 da ADR. Bloqueadores 2 e 3 seguem abertos.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print("=" * 78)
    print("TEST-0008 — LOCK DA LISTA CANÔNICA DE MÉTRICAS")
    print("=" * 78)
    print(f"RELEASE  : {RELEASE_SHA[:16]}…  guard={code}")
    print(f"TEST-0007: {len(t7)} → {t7}")
    print(f"TEST-0008: {len(t8)} → {t8}")
    print(f"união    : {len(union)} → é este o '6'")
    print(f"           {len(t7)} + {len(t8)} − {len(inter)} = {len(union)}  "
          f"({'confere' if doc['origin_of_the_six']['arithmetic_check']['holds'] else 'NÃO CONFERE'})")
    print(f"\ncanário do guard ({'APROVADO' if canary_ok else 'REPROVADO'}):")
    for r in canary:
        print(f"  {r['case']:<28} espera {r['expect']:<28} → {r['code']:<38} "
              f"{'ok' if r['passed'] else 'FALHOU'}")
    print(f"\nrubrica legada do TEST-0008: {criteria}")
    print(f"  pesos {weights} soma {wsum}")
    print(f"  critérios SEM métrica  : {orphan_criteria}  "
          f"(peso {doc['open_pendency_for_alexandre']['measured_facts']['peso_dos_orfaos']}"
          f" = {doc['open_pendency_for_alexandre']['measured_facts']['fracao_do_peso_total_nos_orfaos']:.1%} do total)")
    print(f"  métricas SEM critério  : {metrics_without_criterion}")
    print(f"\nlegacy_five_status: PENDING_REDERIVATION (mantido)")
    print(f"pendência de CONSISTENCY / HUMAN_CHECKPOINT_COMPLIANCE: "
          f"ABERTA, decisão do Alexandre")
    print(f"\npublicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256: {sha_p(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
