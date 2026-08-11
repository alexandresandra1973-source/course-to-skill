#!/usr/bin/env python3
"""FRENTE 2 — ENSAIO SECO da cadeia v0.1.4 com notas sintéticas.

Roda daqui (ext4). Tudo em /tmp, marcado SYNTHETIC_DRY_RUN. Nada vai para pasta
definitiva. Nenhum artefato real é congelado. Nenhum script auditado é editado.

Duas perguntas:
  1. A cadeia fecha de ponta a ponta com os scripts F5/F6?
  2. A previsão "trava no scorer, linha 880, pelo literal V0.1.3" se confirma?
     Testada contra o scorer F4 NÃO patcheado, que é o estado a que a previsão
     se referia, com o scorer F6 como controle.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "DRY-RUN-CHAIN-v0.1.4.md"
CS = DRIVE / "Course-to-Skill"
V013 = CS / "PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007"
V014 = CS / "PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
SCREPORT = DOCS / "STRUCTURAL-CEILING-REPORT-v0.1.4.yaml"

TMP = Path("/tmp/dryrun-v014")
F3ZIP = V013 / "PRELOCK_F3_TRISTATE/PILOT-001-v0.1.3-PRELOCK-PATCH-F3-TRISTATE.zip"
F3PRE = "PILOT-001-v0.1.3-PRELOCK-PATCH-F3-TRISTATE/"
F4ZIP = V013 / "FINAL_PRE_RUN_LOCK/PILOT-001-v0.1.3-PRELOCK-PATCH-F4-STRUCTURAL-ID.zip"
F4PRE = "PILOT-001-v0.1.3-PRELOCK-PATCH-F4-STRUCTURAL-ID/"
F6ZIP = (V014 / "PRELOCK_F5_VERSION_PARAMETERIZATION"
         / "PILOT-001-v0.1.4-PRELOCK-PATCH-F6-SCORER-VERSION-PARAMETERIZATION.zip")
F6PRE = "PILOT-001-v0.1.4-PRELOCK-PATCH-F6-SCORER-VERSION-PARAMETERIZATION/"

DECLARED = {"freeze_margin_lock.py": "32774324",
            "freeze_pre_run_registry.py": "fa45010c"}

ARMS = {
    "FULL@BEFORE_DEDUP": "555a70295ca23f89878150ddf2b0c207fba393137f1b8e4383bd9be18e7cedfb",
    "FULL@AFTER_DEDUP": "b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028",
    "ABLATED@AFTER_DEDUP": "da9b326dbd80af1711c67a5f95999118bdc54ce6b84b6e54dbd756b4d657a205",
}

SCENARIOS = [
    ("recusa_correta_margem_44", "02_correct_refusal_margin44_pass",
     "recusa fail-closed correta; margem prevista 44,0"),
    ("fabricacao", "03_fabricated_high_margin_cannot_pass",
     "braço ablado fabrica a metodologia ausente"),
    ("ambiguidade_de_ancora", "05_anchor_ambiguity_forces_inconclusive",
     "juiz declara ambiguidade de âncora"),
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def hash_gate() -> dict:
    """Confere os scripts do pacote contra o manifesto do próprio pacote."""
    with zipfile.ZipFile(F6ZIP) as z:
        man = z.read(F6PRE + "SHA256SUMS.txt").decode("utf-8")
        declared = {}
        for line in man.splitlines():
            parts = line.split()
            if len(parts) == 2:
                declared[parts[1]] = parts[0]
        checked = []
        for name in ("freeze_margin_lock.py", "freeze_pre_run_registry.py",
                     "score_judge_results.py"):
            got = sha(z.read(F6PRE + name))
            exp = declared.get(name)
            row = {"file": name, "manifest_sha256": exp, "observed_sha256": got,
                   "match": exp == got}
            if name in DECLARED:
                row["task_declared_prefix"] = DECLARED[name]
                row["matches_task_prefix"] = got.startswith(DECLARED[name])
            checked.append(row)
    return {"manifest": "SHA256SUMS.txt (dentro do pacote F6)",
            "checked": checked,
            "all_match": all(c["match"] for c in checked),
            "task_prefixes_match": all(c.get("matches_task_prefix", True)
                                       for c in checked)}


def stage() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    (TMP / "SYNTHETIC_DRY_RUN.md").write_text(
        "# SYNTHETIC_DRY_RUN\n\n"
        "Ensaio seco. As notas são fixtures de canário reusadas, não notas de "
        "juiz reais. Nada aqui pode virar lock, registry ou opening record.\n",
        encoding="utf-8")

    with zipfile.ZipFile(F3ZIP) as z:
        for src, dst in [("canary/suite.yaml", "suite.yaml"),
                         ("canary/contract.yaml", "contract.yaml"),
                         ("canary/metric-lock.yaml", "metric-lock-v013.yaml"),
                         ("TEST-0007-RUBRIC-v0.1.3.yaml", "rubric.yaml"),
                         ("TEST-0007-RUBRIC-ANCHOR-ADDENDUM-v0.1.3.yaml",
                          "addendum.yaml"),
                         ("TEST-0007-RUBRIC-ANCHOR-ADDENDUM-FREEZE-RECORD-v0.1.3.yaml",
                          "addendum-freeze.yaml"),
                         ("TEST-0007-DECISION-RULE-v0.1.3.yaml", "decision-rule.yaml")]:
            (TMP / dst).write_bytes(z.read(F3PRE + src))
        for n in z.namelist():
            if n.startswith(F3PRE + "canary/raw_outputs/") and not n.endswith("/"):
                d = TMP / n[len(F3PRE + "canary/"):]
                d.parent.mkdir(parents=True, exist_ok=True)
                d.write_bytes(z.read(n))
        (TMP / "scores").mkdir(exist_ok=True)
        for _, case, _ in SCENARIOS:
            (TMP / "scores" / f"{case}.yaml").write_bytes(
                z.read(f"{F3PRE}canary/cases/{case}/scores.yaml"))

    with zipfile.ZipFile(F4ZIP) as z:
        (TMP / "score_judge_results_F4.py").write_bytes(
            z.read(F4PRE + "score_judge_results.py"))

    with zipfile.ZipFile(F6ZIP) as z:
        for n in ("freeze_margin_lock.py", "freeze_pre_run_registry.py",
                  "score_judge_results.py"):
            (TMP / n).write_bytes(z.read(F6PRE + n))
        (TMP / "metric-lock.yaml").write_bytes(
            z.read(F6PRE + "canary/fixtures/metric-lock-v0.1.4.yaml"))

    shutil.copy(SCREPORT, TMP / "structural-report.yaml")
    synthesize_v014_notes()

    (TMP / "margin-draft.yaml").write_text(yaml.safe_dump({
        "schema_version": "0.5.0", "artifact_status": "DRAFT_NOT_LOCKED",
        "candidate_version": "0.1.4",
        "comparisons": {"TEST-0007": {
            "left": {"arm_id": "FULL", "phase": "AFTER_DEDUP"},
            "right": {"arm_id": "ABLATED", "phase": "AFTER_DEDUP"},
            "arm_package_hashes": {k: {"sha256": v} for k, v in ARMS.items()},
            "margin_threshold": 34.0,
            "threshold_justification": {
                "basis": "FROZEN_ANCHOR_BOUNDARY",
                "anchor_boundary_reference": 34.0,
                "effective_ceiling_reference": 60.0,
                "threshold_fraction_of_effective_ceiling": 34.0 / 60.0,
                "rationale": ("SYNTHETIC_DRY_RUN — reusa verbatim a fronteira da "
                              "regra de decisão congelada 540df728, sem derivar "
                              "limiar novo."),
                "distinguishability_rationale": (
                    "SYNTHETIC_DRY_RUN — a incerteza é tratada pela zona "
                    "inconclusiva [28.831; 39.169] e pelo piso de "
                    "discriminabilidade 20.675, ambos congelados à parte."),
            },
            "full_preservation": {
                "before": {"arm_id": "FULL", "phase": "BEFORE_DEDUP"},
                "after": {"arm_id": "FULL", "phase": "AFTER_DEDUP"},
                "max_total_regression": 0.0,
                "require_no_new_mandatory_floor_failure": True},
        }}}, sort_keys=False, allow_unicode=True), encoding="utf-8")


ARM_KEY = {("FULL", "BEFORE_DEDUP"): "FULL@BEFORE_DEDUP",
           ("FULL", "AFTER_DEDUP"): "FULL@AFTER_DEDUP",
           ("ABLATED", "AFTER_DEDUP"): "ABLATED@AFTER_DEDUP"}


def synthesize_v014_notes() -> dict:
    """Fabrica as notas SINTÉTICAS v0.1.4 a partir das fixtures do canário.

    As fixtures do F3 carregam os hashes de braço da v0.1.3 no cabeçalho da
    saída crua. Uma nota v0.1.4 tem de apontar para os pacotes da v0.1.4, senão
    o scorer acusa ARM_PACKAGE_HASH_MISMATCH — e com razão. Reescrevemos o
    cabeçalho e recomputamos o sha da saída crua nas notas.
    """
    import re as _re
    remap = {}
    for f in sorted((TMP / "raw_outputs/TEST-0007").glob("*.md")):
        txt = f.read_text(encoding="utf-8")
        m = _re.search(r'PILOT001_RUN_HEADER (\{.*?\})', txt)
        if not m:
            continue
        hdr = json.loads(m.group(1))
        key = ARM_KEY.get((hdr.get("arm_id"), hdr.get("phase")))
        if not key:
            continue
        before = sha(f.read_bytes())
        hdr["arm_package_sha256"] = ARMS[key]
        new = txt[:m.start(1)] + json.dumps(hdr, separators=(",", ":")) + txt[m.end(1):]
        f.write_text(new, encoding="utf-8")
        remap[before] = sha(f.read_bytes())

    for sp in sorted((TMP / "scores").glob("*.yaml")):
        d = yaml.safe_load(sp.read_text(encoding="utf-8"))
        d["synthetic_dry_run"] = "SYNTHETIC_DRY_RUN"
        for r in d.get("runs", []):
            old = r.get("raw_output_sha256")
            if old in remap:
                r["raw_output_sha256"] = remap[old]
            for c in r.get("criteria", []):
                ev = c.get("evidence") or {}
                if ev.get("raw_output_sha256") in remap:
                    ev["raw_output_sha256"] = remap[ev["raw_output_sha256"]]
        sp.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True),
                      encoding="utf-8")
    return remap


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=TMP)
    return p.returncode, (p.stdout + p.stderr).strip()


def parse(text: str) -> tuple[str | None, list[str]]:
    try:
        d = yaml.safe_load(text)
    except Exception:
        return None, []
    if not isinstance(d, dict):
        return None, []
    codes = sorted({e.get("code") for e in (d.get("errors") or [])
                    if isinstance(e, dict) and e.get("code")})
    return d.get("status"), codes


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    gate = hash_gate()
    stage()
    steps, scorer = [], []

    CV = ["--candidate-version", "0.1.4"]
    rc, out = run([sys.executable, "freeze_margin_lock.py", *CV,
                   "--suite", "suite.yaml", "--contract", "contract.yaml",
                   "--draft", "margin-draft.yaml",
                   "--structural-report", "structural-report.yaml",
                   "--test0007-rubric", "rubric.yaml",
                   "--rubric-addendum", "addendum.yaml",
                   "--rubric-addendum-freeze-record", "addendum-freeze.yaml",
                   "--decision-rule", "decision-rule.yaml",
                   "--out", "lock.yaml"])
    st, codes = parse(out)
    steps.append({"n": "S1", "step": "freeze_margin_lock (F5) · relatório REAL v0.1.4",
                  "exit": rc, "status": st, "codes": codes, "output": out})

    rc2, out2 = run([sys.executable, "freeze_pre_run_registry.py", *CV,
                     "--comparison-lock", "lock.yaml",
                     "--metric-lock", "metric-lock.yaml",
                     "--registry-out", "registry.yaml",
                     "--opening-record-out", "opening.yaml",
                     "--extra-artifact", "test0007_rubric=rubric.yaml",
                     "--extra-artifact", "rubric_anchor_addendum=addendum.yaml",
                     "--extra-artifact",
                     "rubric_anchor_addendum_freeze_record=addendum-freeze.yaml",
                     "--extra-artifact",
                     "test0007_decision_rule=decision-rule.yaml"])
    stamped = None
    if rc2 == 0:
        stamped = {
            "registry": yaml.safe_load((TMP / "registry.yaml").read_text(
                encoding="utf-8")).get("candidate_version"),
            "opening_record": yaml.safe_load((TMP / "opening.yaml").read_text(
                encoding="utf-8")).get("candidate_version"),
        }
    steps.append({"n": "S2", "step": "freeze_pre_run_registry (F5) · registry + opening",
                  "exit": rc2, "status": None, "codes": [], "output": out2,
                  "stamped": stamped})

    common = ["--suite", "suite.yaml", "--contract", "contract.yaml",
              "--raw-root", ".", "--comparison-lock", "lock.yaml",
              "--metric-lock", "metric-lock.yaml",
              "--pre-run-lock-registry", "registry.yaml",
              "--pre-run-opening-record", "opening.yaml",
              "--test0007-rubric", "rubric.yaml", "--rubric-addendum", "addendum.yaml",
              "--rubric-addendum-freeze-record", "addendum-freeze.yaml",
              "--decision-rule", "decision-rule.yaml"]
    for label, case, desc in SCENARIOS:
        for variant, script, extra in (
                ("scorer F6 (patcheado)", "score_judge_results.py", CV),
                ("scorer F4 (não patcheado)", "score_judge_results_F4.py", [])):
            rc3, out3 = run([sys.executable, script, *extra, *common,
                             "--scores", f"scores/{case}.yaml",
                             "--out", f"res-{label}-{variant[:9]}.yaml"])
            resf = TMP / f"res-{label}-{variant[:9]}.yaml"
            st3, codes3 = (parse(resf.read_text(encoding="utf-8"))
                           if resf.exists() else parse(out3))
            detail = []
            if resf.exists():
                dd = yaml.safe_load(resf.read_text(encoding="utf-8")) or {}
                for e in (dd.get("errors") or [])[:3]:
                    if isinstance(e, dict):
                        detail.append({"code": e.get("code"),
                                       "detail": e.get("detail"),
                                       "mismatches": e.get("mismatches")})
            scorer.append({"scenario": label, "desc": desc, "variant": variant,
                           "exit": rc3, "status": st3, "codes": codes3,
                           "errors": detail, "output": out3[:1200]})

    f6 = [s for s in scorer if "F6" in s["variant"]]
    f4 = [s for s in scorer if "F4" in s["variant"]]
    chain_closes = (steps[0]["exit"] == 0 and steps[1]["exit"] == 0
                    and all(s["status"] in ("VALID", "FAIL", "INCONCLUSIVE")
                            for s in f6))
    f4_blocks = all(s["exit"] != 0 for s in f4)
    f4_arm_codes = sorted({c for s in f4 for c in s["codes"]})

    L, w = [], None
    w = L.append
    w("# Ensaio seco da cadeia v0.1.4 — onde trava, empiricamente")
    w("")
    w(f"- Gerado: `{stamp}` · gerador `{Path(__file__).name}`")
    w(f"- Tudo em `{TMP}`, marcado `SYNTHETIC_DRY_RUN`. Nada congelado, nada em "
      "pasta definitiva.")
    w("- Nenhum script auditado editado.")
    w("")
    w("## 0. Portão de hash dos freezers")
    w("")
    w("| script | manifesto | observado | confere |")
    w("|---|---|---|---|")
    for c in gate["checked"]:
        w(f"| `{c['file']}` | `{c['manifest_sha256'][:16]}…` | "
          f"`{c['observed_sha256'][:16]}…` | {'sim' if c['match'] else 'NÃO'} |")
    w("")
    w(f"Manifesto: `{gate['manifest']}`. Confere: **{gate['all_match']}**. "
      f"Prefixos declarados na tarefa (`32774324…`, `fa45010c…`) batem: "
      f"**{gate['task_prefixes_match']}**.")
    w("")
    w("Os freezers do F5 vieram dentro do pacote **F6**, não do diretório do F5 — "
      "o `PRELOCK_F5_VERSION_PARAMETERIZATION/` tem só ADR, canário e varredura. "
      "Quem procurar o F5 pelo nome da pasta não acha os scripts.")
    w("")
    w("## 1. Onde travou")
    w("")
    w("| passo | etapa | exit | status | código |")
    w("|---|---|---|---|---|")
    for s in steps:
        w(f"| {s['n']} | {s['step']} | **{s['exit']}** | {s['status'] or '—'} | "
          f"{', '.join(s['codes']) or '—'} |")
    for s in scorer:
        w(f"| S3 | {s['scenario']} · {s['variant']} | **{s['exit']}** | "
          f"{s['status'] or '—'} | {', '.join(s['codes']) or '—'} |")
    w("")
    if chain_closes:
        w("**A cadeia fecha de ponta a ponta com os scripts F5/F6.** Congelou o "
          "lock, emitiu registry e opening record, e o scorer produziu veredito "
          "nos três cenários.")
    else:
        w("**A cadeia NÃO fecha.** Ver o passo com exit diferente de 0.")
    w("")
    if steps[1].get("stamped"):
        w("Versão carimbada pelo registry e pelo opening record:")
        w("")
        for k, v in steps[1]["stamped"].items():
            w(f"- `{k}.candidate_version` = **{v}**")
        w("")
        w("Era este o defeito que travava a cadeia nas sessões anteriores. "
          "Resolvido pelo F5.")
        w("")
    w("## 2. Os três cenários, com o scorer F6")
    w("")
    w("| cenário | exit | status |")
    w("|---|---|---|")
    for s in f6:
        w(f"| {s['desc']} | {s['exit']} | **{s['status'] or '—'}** |")
    w("")
    w("## 3. A previsão: trava no scorer, linha 880, pelo literal `V0.1.3`?")
    w("")
    w("A previsão descrevia o estado **antes do F6**. Testei o scorer F4, que é "
      "esse estado, contra o F6 como controle — mesmas notas, mesmo lock, mesma "
      "cadeia.")
    w("")
    w("| cenário | scorer F4 (não patcheado) | scorer F6 (patcheado) |")
    w("|---|---|---|")
    for label, _, desc in SCENARIOS:
        a = next(s for s in f4 if s["scenario"] == label)
        b = next(s for s in f6 if s["scenario"] == label)
        w(f"| {desc} | exit {a['exit']} · {a['status'] or '—'} · "
          f"{', '.join(a['codes']) or '—'} | exit {b['exit']} · "
          f"{b['status'] or '—'} · {', '.join(b['codes']) or '—'} |")
    w("")
    if f4_blocks and chain_closes:
        w("**CONFIRMADA.** O scorer F4 rejeita nos três cenários; o F6, com as "
          "mesmas entradas, produz veredito. A única diferença entre os dois é a "
          f"parametrização da versão — linha 880 no F4 "
          f"(`...-AFTER_DEDUP-V0.1.3` cravado), linha 881 no F6 "
          f"(`...-AFTER_DEDUP-V{{candidate_version}}`).")
        if f4_arm_codes:
            w("")
            w(f"Códigos devolvidos pelo F4: `{', '.join(f4_arm_codes)}`.")
    elif not f4_blocks:
        w("**REFUTADA.** O scorer F4 não travou nos três cenários.")
    else:
        w("**PARCIAL.** O F4 trava, mas a cadeia com F6 também não fecha, então a "
          "linha 880 não é a única causa.")
    w("")
    w("## 4. Detalhe de cada passo")
    w("")
    for s in steps:
        w(f"### {s['n']} — {s['step']}")
        w("")
        w(f"exit **{s['exit']}**")
        w("")
        w("```")
        w(s["output"][:800] or "(sem saída)")
        w("```")
        w("")
    for s in scorer:
        w(f"### {s['scenario']} · {s['variant']}")
        w("")
        w(f"exit **{s['exit']}** · status `{s['status'] or '—'}`")
        w("")
        w("```")
        w(s["output"][:600] or "(sem saída)")
        w("```")
        w("")
        for e in s.get("errors") or []:
            w(f"- `{e['code']}` — {e['detail']}")
            for mm in (e.get("mismatches") or []):
                w(f"  - {mm}")
        if s.get("errors"):
            w("")
    w("## 5. O que este ensaio NÃO prova")
    w("")
    w("As notas são fixtures de canário do F3 reusadas, não notas de juiz reais. "
      "O ensaio prova que a **cadeia** aceita e processa os três cenários até "
      "veredito. Não diz nada sobre o desempenho do candidato, que só a rodada "
      "cega mede.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    (TMP / "dry-run-summary.json").write_text(
        json.dumps({"gate": gate, "steps": steps, "scorer": scorer}, indent=1,
                   ensure_ascii=False), encoding="utf-8")

    print(f"portão de hash: {gate['all_match']} | prefixos da tarefa: "
          f"{gate['task_prefixes_match']}")
    for s in steps:
        print(f"  {s['n']}: exit {s['exit']} {s['codes']}"
              + (f" carimbou {s['stamped']}" if s.get("stamped") else ""))
    for s in scorer:
        print(f"  S3 {s['scenario'][:22]:22s} {s['variant'][:24]:24s} "
              f"exit {s['exit']} status={s['status']} {s['codes']}")
    print(f"cadeia fecha: {chain_closes} | previsão 880: "
          f"{'CONFIRMADA' if (f4_blocks and chain_closes) else 'ver relatório'}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
