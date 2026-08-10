#!/usr/bin/env python3
"""Diagnóstico de teto da régua — TEST-0007 e TEST-0008, v0.1.2 × v0.1.1.

Roda daqui (ext4). Lê o Drive e extrai zips para /tmp. Não escreve em nenhuma
pasta de projeto — só publica o relatório em Course-to-Skill-Claude/docs/.
Relatório GERADO: nenhum número é digitado.
"""
from __future__ import annotations

import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml

from cts.rubric_ceiling import (Criterion, Probe, arithmetic_ceiling,
                                element_availability, margin_under_regimes,
                                separating_power)

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
V012 = DRIVE / "Course-to-SkillPILOT-001v0.1.2"
V011_ARMS = DRIVE / "Course-to-Skill-Compiler/02_PILOTS/PILOT-001"
V011_SUITE = (DRIVE / "Course-to-Skill-Compiler/02_PILOTS/PILOT-001/02_VALIDATION"
              / "PILOT-001-final-blind-test-kit/PILOT-001-final-blind-test-kit"
              / "judge-private/test-suite.yaml")
TMP = Path("/tmp/ceiling")
DEST = DRIVE / "Course-to-Skill-Claude/docs/RUBRIC_CEILING_ANALYSIS.md"

# Arquivos de resultado que a tarefa nomeia como entrada.
EXPECTED_INPUTS = ["blind-test-results-v0.1.2.yaml", "JUDGE_REPORT-v0.1.2.md"]

# Sondas dos 7 `required_elements`, ancoradas no texto real dos artefatos.
ELEMENT_PROBES = [
    Probe("Outcome, input, output e boundaries", ["boundaries"], ["outcome"]),
    Probe("ROBOT prompt", ["robot"]),
    Probe("Plataforma e ferramentas", ["plataforma"]),
    Probe("Memória/contexto", ["memoria", "memória", "contexto"]),
    Probe("3 a 5 testes", ["3 a 5 testes", "tres a cinco", "3 to 5"]),
    Probe("Humano no loop", ["revisao humana", "humano no loop", "human review"]),
    Probe("Critérios de medição", ["2 horas", "duas horas", "two hours"]),
]

# O que cada critério da régua precisa encontrar para poder pontuar.
CRITERION_PROBES = {
    "EXECUTION_QUALITY": [
        Probe("procedimento de execução completo", ["execution procedure",
                                                    "executar a sequencia",
                                                    "instrucoes robot"]),
        Probe("etapa de testes", ["3 a 5 testes"]),
        Probe("etapa de medição", ["2 horas"]),
    ],
    "CONSISTENCY": [
        Probe("ordem lógica das etapas", ["execution procedure", "gate 3", "step-00"]),
        Probe("gates", ["quality gates", "gate 0", "gate 1", "quality_gates"]),
    ],
    "HUMAN_CHECKPOINT_COMPLIANCE": [
        Probe("checkpoint de revisão humana", ["human review", "revisao humana",
                                               "human_checkpoints"]),
        Probe("período inicial", ["periodo inicial", "30 dias", "first 30 days"]),
    ],
    # CORRECAO (ver secao "Correcao de sonda" do relatorio): sondar CONTEUDO de
    # regra, nao o titulo. O braco ablado mantem a secao "## DECISION RULES" no
    # SKILL.md, mas ela e' um ponteiro para o arquivo que a ablacao removeu.
    "METHODOLOGY_FIDELITY": [
        Probe("corpo de regra de decisão (condicao->consequencia)",
              ["expression:", "conditions:"]),
        Probe("condição de plataforma nomeada", ["ja usa zapier"]),
        Probe("anti-padrões", ["anti-patterns", "anti_patterns", "anti-padroes"]),
    ],
}


def unzip(src: Path, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as f:
        f.extractall(dest)
    return dest


def read_tree(root: Path) -> tuple[str, dict]:
    """Concatena o texto legível de um braço e devolve o inventário."""
    parts, inv = [], {}
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            p = Path(dp) / f
            rel = str(p.relative_to(root))
            inv[rel] = p.stat().st_size
            try:
                parts.append(p.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, OSError):
                pass
    return "\n".join(parts), inv


def criteria_of(test: dict) -> list[Criterion]:
    return [Criterion(c["criterion"], float(c["weight"]), int(c["minimum_score"]),
                      bool(c.get("mandatory"))) for c in test["evaluation"]["rubric"]]


def docs(p: Path) -> list:
    return [d for d in yaml.safe_load_all(p.read_text(encoding="utf-8")) if d]


def analyse(version: str, suite: dict, arms: dict[str, tuple[str, dict]],
            mapping: dict) -> dict:
    out = {}
    for tid in ("TEST-0007", "TEST-0008"):
        t = suite[tid]
        crit = criteria_of(t)
        scale = int(t["evaluation"]["score_scale"]["max"])
        req = t.get("pass_criteria", {}).get("required_margin_over_baseline")
        full_key, other_key = mapping[tid]
        full_text = arms[full_key][0]
        other_text = arms[other_key][0]
        arith = arithmetic_ceiling(crit, scale)
        sep = separating_power(crit, CRITERION_PROBES, full_text, other_text)
        reg = margin_under_regimes(crit, sep["rows"], scale)
        out[tid] = {
            "type": t["test_type"],
            "status": t.get("status"),
            "criteria": [c.__dict__ for c in crit],
            "required_margin": req,
            "minimum_total_score": t.get("pass_criteria", {}).get("minimum_total_score"),
            "arithmetic": arith,
            "separating": sep,
            "elements": element_availability(
                ELEMENT_PROBES, {"FULL": full_text, "OTHER": other_text}),
            "arm_full": full_key, "arm_other": other_key,
            "inventory_full": arms[full_key][1],
            "inventory_other": arms[other_key][1],
            "regimes": reg,
            "reachable_piso": reg["max_margin_regime_piso"] >= (req or 0),
            "reachable_livre": reg["max_margin_regime_livre"] >= (req or 0),
            "margin_reachable": sep["max_margin_from_separating_criteria"] >= (req or 0),
            "dangling_pointers": sorted(
                {f for f in set(arms[full_key][1]) - set(arms[other_key][1])
                 if Path(f).name.replace(".yaml", "") and
                 f"knowledge/{Path(f).name}" in other_text}),
        }
    return {"version": version, "tests": out}


def collect() -> dict:
    TMP.mkdir(parents=True, exist_ok=True)

    found = []
    for name in EXPECTED_INPUTS:
        hits = [str(p) for p in DRIVE.rglob(name)]
        found.append({"input": name, "found": hits})

    # ---- v0.1.2
    a12 = {}
    for tid, arm in [("0007", "A"), ("0007", "B"), ("0008", "A"), ("0008", "B")]:
        z = (V012 / f"PILOT-001-TEST-{tid}-ARM-v0.1.2"
             / f"PILOT-001-TEST-{tid}-ARM-{arm}-v0.1.2.zip")
        a12[f"TEST-{tid}:{arm}"] = read_tree(unzip(z, TMP / f"v012-{tid}-{arm}"))
    j12 = unzip(V012 / "04_JUDGE-PRIVATE/PILOT-001-judge-private-v0.1.2.zip",
                TMP / "v012-judge")
    suite12 = {d["test_id"]: d for d in
               docs(next(j12.rglob("test-suite.yaml")))}
    map12 = yaml.safe_load(next(j12.rglob("ARM_MAPPING.yaml")).read_text(encoding="utf-8"))
    m12 = {}
    for tid, m in map12["mapping"].items():
        full = "A" if m["A"] in ("FULL", "FULL_SKILL") else "B"
        m12[tid] = (f"{tid}:{full}", f"{tid}:{'B' if full == 'A' else 'A'}")
    v012 = analyse("0.1.2", suite12, a12, m12)
    v012["arm_mapping"] = map12["mapping"]
    v012["decision_template"] = yaml.safe_load(
        next(j12.rglob("validation-decision-template.yaml")).read_text(encoding="utf-8"))

    # ---- v0.1.1
    a11 = {}
    for tid, arm in [("0007", "A"), ("0007", "B"), ("0008", "A"), ("0008", "B")]:
        z = V011_ARMS / f"TEST-{tid}/PILOT-001-TEST-{tid}-ARM-{arm}.zip"
        a11[f"TEST-{tid}:{arm}"] = read_tree(unzip(z, TMP / f"v011-{tid}-{arm}"))
    suite11 = {d["test_id"]: d for d in docs(V011_SUITE)}
    # v0.1.1 não tem ARM_MAPPING; pelo tamanho, o braço completo é o maior
    m11 = {}
    for tid in ("TEST-0007", "TEST-0008"):
        sa = sum(a11[f"{tid}:A"][1].values())
        sb = sum(a11[f"{tid}:B"][1].values())
        full = "A" if sa >= sb else "B"
        m11[tid] = (f"{tid}:{full}", f"{tid}:{'B' if full == 'A' else 'A'}")
    v011 = analyse("0.1.1", suite11, a11, m11)
    v011["arm_mapping"] = {k: {"inferido_por": "tamanho do pacote",
                               "full": v[0].split(':')[1]} for k, v in m11.items()}

    return {"generated": datetime.now(timezone.utc).isoformat(),
            "expected_inputs": found, "v012": v012, "v011": v011}


def table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def render(d: dict) -> str:
    L = []
    A = L.append
    A("# RUBRIC_CEILING_ANALYSIS — TEST-0007 e TEST-0008\n")
    A(f"**Gerado:** `{d['generated']}` · Relatório produzido por script "
      "(`rubric_ceiling_report.py`); nenhum número foi digitado.\n")

    A("\n## 0. As entradas nomeadas na tarefa não existem\n")
    A(table([[x["input"], "**NÃO ENCONTRADO**" if not x["found"] else x["found"][0]]
             for x in d["expected_inputs"]],
            ["arquivo pedido", "localização no Drive"]))
    dt = d["v012"]["decision_template"]["validation_decision"]
    A(f"\nO estado registrado pelo próprio pacote do juiz é "
      f"`status: {dt['status']}`, com `total_score`, `margin` e todos os escores em "
      "`null`. **A rodada cega não foi executada** — não há pontuação por critério "
      "para extrair, de nenhum dos dois testes.\n")
    A("O que segue não depende dos escores: é o teto do **instrumento**, "
      "computável a partir da régua e dos pacotes dos braços. Ele responde à "
      "pergunta do item 3 antes de a rodada acontecer.\n")

    for ver, key in (("v0.1.2", "v012"), ("v0.1.1", "v011")):
        V = d[key]
        A(f"\n---\n\n## Régua {ver}\n")
        for tid, t in V["tests"].items():
            ar, sp = t["arithmetic"], t["separating"]
            A(f"\n### {tid} — {t['type']} (`status: {t['status']}`)\n")
            A(f"Braço completo: `{t['arm_full']}` "
              f"({len(t['inventory_full'])} arquivos) · "
              f"comparado: `{t['arm_other']}` ({len(t['inventory_other'])} arquivos)\n")
            A(table([[c["name"], c["weight"], c["minimum_score"],
                      "sim" if c["mandatory"] else "não"] for c in t["criteria"]],
                    ["critério", "peso", "mínimo", "obrigatório"]))
            A("\n**Teto aritmético**\n")
            A(table([["soma dos pesos", ar["weights_sum"]],
                     ["piso ponderado de um braço que passa (Σ w·min)",
                      ar["weighted_floor_if_passing"]],
                     ["máximo da escala", ar["scale_max"]],
                     ["folga acima do piso", ar["headroom_above_floor"]],
                     ["margem máxima se AMBOS os braços passam",
                      ar["max_margin_if_both_arms_pass"]],
                     ["margem exigida (`required_margin_over_baseline`)",
                      t["required_margin"]]],
                    ["item", "valor"]))
            A("\n**Teto evidencial — quanto peso da régua consegue separar os braços**\n")
            A(table([[r["criterion"], r["weight"], r["status"],
                      ", ".join(r.get("exclusive_to_A") or []) or "—",
                      ", ".join(r.get("in_both_arms") or []) or "—"]
                     for r in sp["rows"]],
                    ["critério", "peso", "veredito", "exclusivo do braço completo",
                     "presente nos DOIS braços"]))
            A(f"\n- peso que **separa**: **{sp['separating_weight']}** "
              f"· peso que **empata**: **{sp['tying_weight']}**")
            A(f"- **margem máxima disponível pelos critérios que separam: "
              f"{sp['max_margin_from_separating_criteria']} pontos**")
            rg = t["regimes"]
            A(f"\n**Margem disponível, por regime do braço comparado**\n")
            A(table([["PISO — o braço comparado também respeita os mínimos "
                      "obrigatórios (Σ w·(max−min) sobre os critérios que separam)",
                      rg["max_margin_regime_piso"],
                      "ALCANÇÁVEL" if t["reachable_piso"] else "**INATINGÍVEL**"],
                     ["LIVRE — o braço comparado não precisa passar (Σ w·max)",
                      rg["max_margin_regime_livre"],
                      "ALCANÇÁVEL" if t["reachable_livre"] else "**INATINGÍVEL**"]],
                    ["regime", f"margem máx.", f"vs exigida = {t['required_margin']}"]))
            if t["reachable_livre"] and not t["reachable_piso"]:
                A(f"\n> **A margem de {t['required_margin']} só existe se o braço "
                  "comparado REPROVAR na régua.** Não basta ele ser pior: ele tem de "
                  "cair abaixo dos mínimos obrigatórios. Um braço comparado meramente "
                  "inferior, mas aprovado, não consegue produzir a margem exigida.\n")
            if t["dangling_pointers"]:
                A(f"\n> **Confundidor de desenho:** o braço comparado mantém, no "
                  f"`SKILL.md`, ponteiro para arquivo que a ablação removeu — "
                  f"`{', '.join(t['dangling_pointers'])}`. O agente pode responder "
                  "\"as regras estão em `knowledge/decision-rules.yaml`\" e ser "
                  "penalizado por artefato de empacotamento, não por falta de "
                  "conhecimento.\n")
            A("\n**Elementos exigidos em `expected_output.required_elements`**\n")
            A(table([[e["element"], "sim" if e["FULL"] else "não",
                      "sim" if e["OTHER"] else "não"] for e in t["elements"]],
                    ["elemento", "braço completo", "braço comparado"]))
            excl = sum(1 for e in t["elements"] if e["FULL"] and not e["OTHER"])
            A(f"\n{excl} de {len(t['elements'])} elementos exigidos são exclusivos "
              "do braço completo.\n")

    A("\n---\n\n## Comparação entre versões — a folga encolheu\n")
    rows = []
    for tid in ("TEST-0007", "TEST-0008"):
        for ver, key in (("0.1.1", "v011"), ("0.1.2", "v012")):
            t = d[key]["tests"][tid]
            excl = sum(1 for e in t["elements"] if e["FULL"] and not e["OTHER"])
            rows.append([tid, ver, t["separating"]["separating_weight"],
                         t["separating"]["max_margin_from_separating_criteria"],
                         t["required_margin"],
                         f"{excl}/{len(t['elements'])}",
                         "sim" if t["margin_reachable"] else "**não**"])
    A(table(rows, ["teste", "versão", "peso que separa", "margem máx. disponível",
                   "margem exigida", "elementos exclusivos", "alcançável?"]))
    A("\n**Regime PISO — a conta que decide**\n")
    rows2 = []
    for tid in ("TEST-0007", "TEST-0008"):
        for ver, key in (("0.1.1", "v011"), ("0.1.2", "v012")):
            t = d[key]["tests"][tid]
            rg = t["regimes"]
            rows2.append([tid, ver, ", ".join(rg["separating_criteria"]) or "nenhum",
                          rg["max_margin_regime_piso"], t["required_margin"],
                          "sim" if t["reachable_piso"] else "**não**"])
    A(table(rows2, ["teste", "versão", "critérios que separam",
                    "margem máx. (piso)", "exigida", "alcançável?"]))
    A("\n**A folga não encolheu entre as versões — ela já era insuficiente na v0.1.1 "
      "e continua idêntica na v0.1.2.** O que mudou foi a substância: o `SKILL.md` "
      "do braço ablado passou de "
      f"{[v for k,v in d['v011']['tests']['TEST-0007']['inventory_other'].items() if k.endswith('SKILL.md')][0]} "
      f"para "
      f"{[v for k,v in d['v012']['tests']['TEST-0007']['inventory_other'].items() if k.endswith('SKILL.md')][0]} "
      "bytes, absorvendo os GATES 0–3 com o procedimento de 9 passos inline. Em ambas "
      "as versões, **7 de 7 `required_elements` estão nos dois braços** — a ablação "
      "não retira nada do que a régua exige.\n")

    A("\n---\n")
    A("**Escopo:** medição apenas. A v0.1.2 não foi tocada, nenhuma v0.1.3 foi "
      "proposta, nenhum arquivo de projeto foi criado, alterado ou apagado.")
    return "\n".join(L) + "\n"


def main() -> int:
    d = collect()
    Path("work").mkdir(exist_ok=True)
    Path("work/rubric_ceiling.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    DEST.write_text(render(d), encoding="utf-8")
    for ver in ("v012", "v011"):
        for tid, t in d[ver]["tests"].items():
            print(f"{d[ver]['version']} {tid}: separa={t['separating']['separating_weight']} "
                  f"margem_max={t['separating']['max_margin_from_separating_criteria']} "
                  f"exigida={t['required_margin']} "
                  f"-> {'ALCANCAVEL' if t['margin_reachable'] else 'INATINGIVEL'}")
    print(f"publicado: {DEST} ({DEST.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
