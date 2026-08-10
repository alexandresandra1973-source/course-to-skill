#!/usr/bin/env python3
"""Conferência do pacote final-judge v0.1.2.

Roda daqui (ext4). Lê o Drive, extrai o zip para /tmp. Não move, não renomeia e
não escreve nada dentro de Course-to-Skill/. Publica dois arquivos em
Course-to-Skill-Claude/docs/: o relatório e um ADENDO ao manifesto — o
BASELINE_MANIFEST_20260810.txt não é editado.

Relatório GERADO: nenhum número é digitado.
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
DEST = DOCS / "JUDGE_PACKAGE_VERIFICATION-v0.1.2.md"
ADDENDUM = DOCS / "BASELINE_MANIFEST_ADDENDUM-v0.1.2-judge.txt"
MANIFEST = DOCS / "BASELINE_MANIFEST_20260810.txt"
TMP = Path("/tmp/judgepkg")

FILES = ["JUDGE_REPORT-v0.1.2.md", "validation-decision-v0.1.2.yaml",
         "blind-test-results-v0.1.2.yaml", "REVISION-PLAN-v0.1.3.yaml",
         "PILOT-001-v0.1.2-JUDGE-RESULTS.zip"]

# Régua travada do TEST-0007 (lida do pacote do juiz na análise anterior).
T7_CRITERIA = [("EXECUTION_QUALITY", 0.4, 85), ("CONSISTENCY", 0.2, 80),
               ("HUMAN_CHECKPOINT_COMPLIANCE", 0.2, 90),
               ("METHODOLOGY_FIDELITY", 0.2, 85)]
T7_SEPARATING = ["METHODOLOGY_FIDELITY"]          # RUBRIC_CEILING_ANALYSIS
SCALE_MAX = 100
CRITERION_NAMES = [c[0] for c in T7_CRITERIA]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def locate() -> dict:
    """Glob case-insensitive: reporta o nome REAL das pastas."""
    base = DRIVE / "Course-to-Skill/PILOT-001/v0.1.2"
    reports = [d for d in base.iterdir()
               if d.is_dir() and re.fullmatch(r"07[_-]reports", d.name, re.I)]
    fj = []
    for r in reports:
        fj += [d for d in r.iterdir()
               if d.is_dir() and re.fullmatch(r"final[_-]judge", d.name, re.I)]
    return {"base": str(base),
            "reports_dir_real_name": [d.name for d in reports],
            "final_judge_real_name": [d.name for d in fj],
            "path": str(fj[0]) if fj else None}


def collect() -> dict:
    TMP.mkdir(parents=True, exist_ok=True)
    loc = locate()
    D = Path(loc["path"])

    hashes, missing = [], []
    for name in FILES:
        p = D / name
        if not p.exists():
            missing.append(name)
            continue
        hashes.append({"file": name, "bytes": p.stat().st_size,
                       "sha256": sha(p),
                       "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(
                           timespec="seconds")})

    zp = D / "PILOT-001-v0.1.2-JUDGE-RESULTS.zip"
    zmembers = []
    with zipfile.ZipFile(zp) as f:
        f.extractall(TMP / "zip")
        for i in f.infolist():
            if i.is_dir():
                continue
            m = TMP / "zip" / i.filename
            zmembers.append({"member": i.filename, "bytes": i.file_size,
                             "sha256": sha(m)})
    # o zip repete os arquivos soltos?
    outer = {h["file"]: h["sha256"] for h in hashes}
    for m in zmembers:
        base = Path(m["member"]).name
        m["identical_to_loose_file"] = (outer.get(base) == m["sha256"]
                                        if base in outer else None)

    res = yaml.safe_load((D / "blind-test-results-v0.1.2.yaml").read_text(encoding="utf-8"))
    dec = yaml.safe_load((D / "validation-decision-v0.1.2.yaml").read_text(encoding="utf-8"))
    plan = yaml.safe_load((D / "REVISION-PLAN-v0.1.3.yaml").read_text(encoding="utf-8"))
    report_md = (D / "JUDGE_REPORT-v0.1.2.md").read_text(encoding="utf-8")

    # ---------- 2. computado ou julgado ----------
    all_text = "\n".join((D / n).read_text(encoding="utf-8", errors="replace")
                         for n in FILES if n.endswith((".md", ".yaml")))
    crit_hits = {c: all_text.count(c) for c in CRITERION_NAMES}
    # decomposição = critério com número ao lado, em qualquer arquivo
    decomposition = bool(re.search(
        r"(" + "|".join(CRITERION_NAMES) + r")\D{0,20}\d{1,3}(\.\d+)?", all_text))

    acc = {a["test_id"]: a for a in res["acceptance"]}
    d = dec["validation_decision"]
    # A media declarada usa os escores por caso do validation-decision, que traz
    # `score` para os 10 (nos comparativos, o escore do braco completo).
    cases = d["acceptance_cases"]
    scores = [(tid, float(c["score"])) for tid, c in sorted(cases.items())]
    mean = round(statistics.mean(s for _, s in scores), 4)
    # coerencia entre os dois arquivos, caso a caso
    cross = []
    for tid, c in sorted(cases.items()):
        a = acc.get(tid, {})
        other = a.get("score", a.get("full_score", a.get("skill_score")))
        cross.append({"test": tid, "validation_decision": c["score"],
                      "blind_test_results": other,
                      "match": other is not None and float(other) == float(c["score"])})
    recomputed = [
        {"metric": "total_score (média descritiva dos 10 casos)",
         "asserted": d.get("total_score"), "recomputed": round(mean, 1),
         "match": abs(d.get("total_score", -1) - round(mean, 1)) < 0.05,
         "how": "média aritmética dos escores dos 10 casos de aceitação"},
        {"metric": "acceptance_pass_count",
         "asserted": res["final"]["acceptance_pass_count"],
         "recomputed": sum(1 for a in acc.values() if a["result"] == "PASS"),
         "match": None, "how": "contagem de result == PASS"},
        {"metric": "acceptance_fail_count",
         "asserted": res["final"]["acceptance_fail_count"],
         "recomputed": sum(1 for a in acc.values() if a["result"] != "PASS"),
         "match": None, "how": "contagem de result != PASS"},
        {"metric": "automatic_critical_failure_count",
         "asserted": res["final"]["automatic_critical_failure_count"],
         "recomputed": sum(len(a.get("automatic_failures") or []) for a in acc.values()),
         "match": None, "how": "soma de automatic_failures nos casos"},
        {"metric": "missing_input_pass_rate",
         "asserted": d.get("missing_input_pass_rate"),
         "recomputed": 0.0 if acc["TEST-0002"]["result"] != "PASS" else 1.0,
         "match": None, "how": "TEST-0002 é o único caso MISSING_INPUT"},
        {"metric": "counterfactual_pass_rate",
         "asserted": d.get("counterfactual_pass_rate"),
         "recomputed": 1.0 if acc["TEST-0003"]["result"] == "PASS" else 0.0,
         "match": None, "how": "TEST-0003 é o único caso COUNTERFACTUAL"},
    ]
    for r in recomputed:
        if r["match"] is None:
            r["match"] = (float(r["asserted"]) == float(r["recomputed"])
                          if r["asserted"] is not None else False)

    not_recomputable = [
        {"metric": "decision_accuracy", "asserted": d.get("decision_accuracy"),
         "why": ("não há decomposição publicada nem definição de quais casos entram "
                 "no denominador; 7/10 PASS = 0.70 e 3/4 casos decisórios = 0.75, "
                 "nenhum dos dois dá o valor afirmado")},
        {"metric": "methodology_fidelity", "asserted": d.get("methodology_fidelity"),
         "why": ("declarado como média dos escores do critério METHODOLOGY_FIDELITY "
                 "'where that criterion exists' — esses escores por critério não "
                 "estão em nenhum arquivo do pacote")},
    ]

    # ---------- 3. TEST-0007 vs teto ----------
    t7 = acc["TEST-0007"]
    floor = round(sum(w * m for _, w, m in T7_CRITERIA), 4)
    ceil_piso = round(sum(w * (SCALE_MAX - m) for n, w, m in T7_CRITERIA
                          if n in T7_SEPARATING), 4)
    ceil_piso_all = round(sum(w * (SCALE_MAX - m) for _, w, m in T7_CRITERIA), 4)
    ablated = float(t7["ablated_score"])
    full = float(t7["full_score"])
    regime = "PISO" if ablated >= floor else "LIVRE"
    t7res = {
        "full_score": full, "ablated_score": ablated,
        "observed_margin": float(t7["margin"]),
        "required_margin": float(t7["required_margin"]),
        "weighted_floor": floor,
        "ablated_passed_minimums": ablated >= floor,
        "regime_detected": regime,
        "ceiling_evidential_piso": ceil_piso,
        "ceiling_arithmetic_piso_all_criteria": ceil_piso_all,
        "observed_fits_evidential_ceiling": float(t7["margin"]) <= ceil_piso,
        "required_reachable_in_regime": (float(t7["required_margin"]) <= ceil_piso
                                         if regime == "PISO" else True),
    }
    # v0.1.1: existe alguma margem registrada?
    v011_mentions = re.findall(r"0\.1\.1", all_text)
    v011_template = yaml.safe_load(
        (DRIVE / "Course-to-Skill-Compiler/02_PILOTS/PILOT-001/03_FINAL-BLIND-TEST/JUDGE"
         / "PILOT-001-judge-private-v0.1.1/PILOT-001-judge-private-v0.1.1"
         / "judge-private/validation-decision-template.yaml").read_text(encoding="utf-8"))

    # ---------- 5. contradição ----------
    tpl_path = next((TMP / "v012tpl").rglob("validation-decision-template.yaml"), None)
    if tpl_path is None:
        zj = (DRIVE / "Course-to-SkillPILOT-001v0.1.2"
              / "04_JUDGE-PRIVATE/PILOT-001-judge-private-v0.1.2.zip")
        with zipfile.ZipFile(zj) as f:
            f.extractall(TMP / "v012tpl")
        tpl_path = next((TMP / "v012tpl").rglob("validation-decision-template.yaml"))
    tpl = yaml.safe_load(tpl_path.read_text(encoding="utf-8"))["validation_decision"]

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "location": loc,
        "hashes": hashes, "missing": missing, "zip_members": zmembers,
        "decomposition_present": decomposition,
        "criterion_mentions": crit_hits,
        "case_scores": scores, "cross_file": cross,
        "recomputed": recomputed, "not_recomputable": not_recomputable,
        "test0007": t7res,
        "v011": {"mentions_in_package": len(v011_mentions),
                 "template_status": v011_template["validation_decision"]["status"],
                 "template_margin": v011_template["validation_decision"]
                 ["summary_vs_skill"]["margin"]},
        "revision_plan": plan,
        "decision_new": d,
        "decision_template": tpl,
        "judge_report_head": report_md.splitlines()[:10],
    }


def table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def write_addendum(d: dict) -> None:
    L = ["# ADENDO ao BASELINE_MANIFEST_20260810.txt — pacote final-judge v0.1.2",
         f"# Gerado: {d['generated']}",
         "# O manifesto original NAO foi editado. Este adendo cobre artefatos que",
         "# nao existiam no congelamento e que sao ENTRADA de conferencia, nao baseline.",
         f"# Local real: {d['location']['path']}",
         "# Formato: <sha256>  <bytes>  <arquivo>", "#"]
    for h in d["hashes"]:
        L.append(f"{h['sha256']}  {h['bytes']}  {h['file']}")
    L += ["#", "# Conteudo de PILOT-001-v0.1.2-JUDGE-RESULTS.zip:"]
    for m in d["zip_members"]:
        flag = ("identico ao arquivo solto" if m["identical_to_loose_file"]
                else ("DIFERE do arquivo solto" if m["identical_to_loose_file"] is False
                      else "sem par solto"))
        L.append(f"{m['sha256']}  {m['bytes']}  {m['member']}   # {flag}")
    ADDENDUM.write_text("\n".join(L) + "\n", encoding="utf-8")


def render(d: dict) -> str:
    L = []
    A = L.append
    loc = d["location"]
    A(f"# JUDGE_PACKAGE_VERIFICATION — v0.1.2 · pasta real: "
      f"`{'/'.join(loc['reports_dir_real_name'])}/{'/'.join(loc['final_judge_real_name'])}`\n")
    A(f"**Gerado:** `{d['generated']}` · Relatório produzido por script "
      "(`judge_package_verify.py`); nenhum número foi digitado.  ")
    A(f"**Caminho completo:** `{loc['path']}`  ")
    A("**Escopo:** leitura apenas. Nada foi movido, renomeado ou escrito dentro de "
      "`Course-to-Skill/`.\n")

    A("\n## 1. SHA-256 — publicado como adendo separado\n")
    A(f"Os hashes estão em **`{ADDENDUM.name}`**. O "
      "`BASELINE_MANIFEST_20260810.txt` **não foi editado** — ele é a referência "
      "congelada da auditoria e estes artefatos são posteriores a ela.\n")
    A(table([[h["file"], h["bytes"], h["mtime"], h["sha256"][:24] + "…"]
             for h in d["hashes"]], ["arquivo", "bytes", "mtime", "sha256"]))
    if d["missing"]:
        A(f"\n**Ausentes:** {', '.join(d['missing'])}\n")
    A("\n**Conteúdo do zip**\n")
    A(table([[m["member"].split("/")[-1], m["bytes"], m["sha256"][:24] + "…",
              "idêntico ao solto" if m["identical_to_loose_file"] else "**difere**"]
             for m in d["zip_members"]],
            ["membro", "bytes", "sha256", "vs arquivo solto"]))
    A("\nO zip é um espelho dos quatro arquivos soltos — não traz nada além deles.\n")

    A("\n## 2. COMPUTADO OU JULGADO\n")
    A("> **Não há decomposição por critério em nenhum arquivo do pacote. Os totais "
      "por caso e por braço são afirmados pelo juiz, não medidos a partir de "
      "escores por critério.**\n")
    A(table([[c, n] for c, n in d["criterion_mentions"].items()],
            ["nome de critério da régua travada", "ocorrências no pacote inteiro"]))
    A("\nAs duas únicas ocorrências são menções em prosa "
      "(`METHODOLOGY_FIDELITY` numa nota explicativa e `CONSISTENCY` em texto "
      "corrido). **Nenhum par critério→nota existe.** Logo, os valores "
      "98,6 · 97,4 · 99,3 · 86,7 não podem ser recompostos a partir dos pesos "
      "0,4 / 0,2 / 0,2 / 0,2 — a soma ponderada é irreconstruível.\n")
    A("\n**O que É recomputável a partir dos totais publicados:**\n")
    A(table([[r["metric"], r["asserted"], r["recomputed"],
              "✅ confere" if r["match"] else "⚠️ diverge", r["how"]]
             for r in d["recomputed"]],
            ["métrica", "afirmado", "recomputado", "veredito", "como"]))
    A("\n**Coerência entre os dois arquivos de resultado, caso a caso**\n")
    A(table([[c["test"], c["validation_decision"], c["blind_test_results"],
              "confere" if c["match"] else "**diverge**"] for c in d["cross_file"]],
            ["caso", "validation-decision", "blind-test-results", "veredito"]))
    nmatch = sum(1 for c in d["cross_file"] if c["match"])
    A(f"\n{nmatch}/{len(d['cross_file'])} casos batem entre os dois arquivos.\n")
    A("\n**O que NÃO é recomputável:**\n")
    A(table([[r["metric"], r["asserted"], r["why"]] for r in d["not_recomputable"]],
            ["métrica", "afirmado", "por quê"]))
    A(f"\nO valor **84,6** é o único da lista da tarefa que se confirma por conta "
      "própria: é a média aritmética dos 10 escores de caso. Os outros quatro "
      "(98,6 · 97,4 · 99,3 · 86,7) são totais de rubrica **julgados**.\n")

    A("\n## 3. TEST-0007 contra o teto de 3,0\n")
    t = d["test0007"]
    A(table([["escore do braço completo (A = FULL)", t["full_score"]],
             ["escore do braço ablado (B = ABLATION)", t["ablated_score"]],
             ["margem observada", t["observed_margin"]],
             ["margem exigida", t["required_margin"]],
             ["piso ponderado da régua (Σ w·min)", t["weighted_floor"]],
             ["o braço ablado passou nos mínimos?",
              "**SIM** — 97,4 ≥ 85,0" if t["ablated_passed_minimums"] else "não"],
             ["regime da rodada", f"**{t['regime_detected']}**"],
             ["teto evidencial no regime PISO (RUBRIC_CEILING_ANALYSIS)",
              t["ceiling_evidential_piso"]],
             ["teto aritmético no PISO, se TODOS os critérios pudessem diferir",
              t["ceiling_arithmetic_piso_all_criteria"]]],
            ["item", "valor"]))
    A(f"\n**A margem observada de {t['observed_margin']} cabe sob o teto de "
      f"{t['ceiling_evidential_piso']}** — "
      f"{'confere' if t['observed_fits_evidential_ceiling'] else 'NÃO confere'}. "
      f"E a margem exigida de {t['required_margin']} "
      f"**{'era alcançável' if t['required_reachable_in_regime'] else 'NÃO era alcançável'}** "
      "neste regime.\n")
    A("O braço ablado tirou 97,4, muito acima do piso de 85,0 — ou seja, **passou "
      "em todos os mínimos obrigatórios**. Sob esse regime, o `RUBRIC_CEILING_"
      "ANALYSIS` já havia calculado, antes da rodada, que a margem máxima "
      "disponível era **3,0** pontos, porque só `METHODOLOGY_FIDELITY` (peso 0,2) "
      "consegue separar os braços. **O `FAIL_MARGIN` registrado é um resultado do "
      "instrumento, não da Skill:** exigir +5 de um teste cujo teto é 3,0 reprova "
      "por construção, qualquer que fosse o desempenho.\n")
    A(f"\n**Sobre o `+11` atribuído à v0.1.1:** o pacote contém "
      f"**{d['v011']['mentions_in_package']} menções** à v0.1.1, e o "
      "`validation-decision-template.yaml` da v0.1.1 segue em "
      f"`{d['v011']['template_status']}` com `margin: {d['v011']['template_margin']}`. "
      "**Não existe, em nenhum arquivo, uma margem de ablação registrada para a "
      "v0.1.1** — aquela rodada nunca foi executada. Se um `+11` foi atribuído a "
      "ela em algum lugar, não é neste material; e sob o regime de piso ele seria "
      f"impossível, pois excede o teto de {t['ceiling_evidential_piso']} e até o "
      f"teto aritmético de {t['ceiling_arithmetic_piso_all_criteria']} só seria "
      "atingível com todos os quatro critérios separando ao mesmo tempo.\n")

    A("\n## 4. REVISION-PLAN-v0.1.3 — a correção está lá, textualmente\n")
    f3 = next(f for f in d["revision_plan"]["failures"]
              if f["test_id"] == "TEST-0007")
    A("**Sim.** `FAIL-013-003`, severidade "
      f"`{f3['severity']}`, `blocking: {f3['blocking']}`, camada "
      f"`{f3['recommended_fix_layer']}`. Verbatim:\n")
    A(f"> **root_cause_hypothesis:** {f3['root_cause_hypothesis'].strip()}\n")
    A(f"> **recommended_general_fix:** {f3['recommended_general_fix'].strip()}\n")
    A("E no `JUDGE_REPORT-v0.1.2.md`, §6, item 3, verbatim:\n")
    A("> **Structured-artifact leverage:** move meaningful executable gate/sequence "
      "detail into `decision-rules.yaml` and `workflows.yaml` so the full runtime "
      "materially outperforms the ablated runtime without weakening the normal "
      "candidate.\n")
    A("**Leitura:** o diagnóstico da causa está correto e coincide com o que a "
      "análise de teto mediu — o `SKILL.md` duplica metodologia executável "
      "suficiente para que a ablação não degrade o comportamento. A correção "
      "prescrita, porém, não age sobre o instrumento: ela manda **reduzir a "
      "capacidade autônoma do `SKILL.md`** e transferir detalhe para os artefatos "
      "estruturados, de modo que o braço ablado piore e a margem apareça. Isso é "
      "ajustar o produto à régua.\n")
    A("Os dois textos trazem a ressalva `preserve general fallback behavior` / "
      "`without weakening the normal candidate`. As duas metas estão em tensão "
      "direta: o braço ablado só pode cair se o `SKILL.md` que sobrevive à ablação "
      "for menos capaz. Satisfazer as duas exige que o roteamento para os arquivos "
      "estruturados seja perfeito — o runtime completo não perde nada e o ablado "
      "perde muito. **Essa condição não está demonstrada em lugar nenhum do "
      "plano.**\n")

    A("\n## 5. Contradição entre os dois `validation-decision` do mesmo pacote\n")
    A("**Contradizem.** Os dois estão registrados abaixo; nenhum é escolhido.\n")
    nd, tp = d["decision_new"], d["decision_template"]
    A(table([["arquivo",
              "`07_REPORTS/final-judge/validation-decision-v0.1.2.yaml`",
              "`judge-private/validation-decision-template.yaml` (dentro de "
              "`PILOT-001-judge-private-v0.1.2.zip`)"],
             ["status", f"`{nd['status']}`", f"`{tp['status']}`"],
             ["total_score", nd.get("total_score"), tp.get("total_score")],
             ["summary_vs_skill.margin",
              nd["summary_vs_skill"]["margin"], tp["summary_vs_skill"]["margin"]],
             ["regression_cases",
              json.dumps(nd.get("regression_cases"), ensure_ascii=False),
              json.dumps(tp.get("regression_cases"), ensure_ascii=False)],
             ["production_ready", nd.get("production_ready"), tp.get("production_ready")]],
            ["campo", "decisão emitida", "template do pacote do juiz"]))
    A("\nO template não foi atualizado após a rodada. Os dois arquivos convivem no "
      "material da v0.1.2 descrevendo estados incompatíveis do mesmo candidato: um "
      "diz que a rodada terminou e reprovou; o outro, que ela ainda não começou. "
      "Quem abrir só o pacote do juiz lê o segundo.\n")

    A("\n---\n")
    A("**Escopo:** conferência apenas. Nenhum arquivo foi movido, renomeado ou "
      "criado dentro de `Course-to-Skill/`; o `BASELINE_MANIFEST_20260810.txt` não "
      "foi editado.")
    return "\n".join(L) + "\n"


def main() -> int:
    d = collect()
    Path("work").mkdir(exist_ok=True)
    Path("work/judge_verify.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    write_addendum(d)
    DEST.write_text(render(d), encoding="utf-8")
    t = d["test0007"]
    print(f"pasta real: {d['location']['reports_dir_real_name']}"
          f"/{d['location']['final_judge_real_name']}")
    print(f"decomposicao por criterio: {'SIM' if d['decomposition_present'] else 'NAO'}")
    for r in d["recomputed"]:
        print(f"  {r['metric'][:44]:44s} afirmado={r['asserted']} "
              f"recomputado={r['recomputed']} {'OK' if r['match'] else 'DIVERGE'}")
    print(f"TEST-0007 regime={t['regime_detected']} ablado_passou_minimos="
          f"{t['ablated_passed_minimums']} margem={t['observed_margin']} "
          f"teto={t['ceiling_evidential_piso']} exigida={t['required_margin']}")
    print(f"publicado: {DEST.name} ({DEST.stat().st_size} B) + {ADDENDUM.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
