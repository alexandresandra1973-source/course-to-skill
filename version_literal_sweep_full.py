#!/usr/bin/env python3
"""FRENTE 1 — varredura COMPLETA de literais de versão em todo script executável.

Roda daqui (ext4). READ-ONLY: lê os pacotes de dentro dos zips, sem extrair para
pasta definitiva. NÃO corrige nada.

Estende a varredura do F5, que cobriu só F3-TRISTATE e F4, para REV2..REV5,
D1/D2, F3, F4, F5 e os scripts do repositório que participam da cadeia.

Classificação, no esquema do F5:
  DOCUMENTATION_OR_EXAMPLE            — docstring, comentário, linha de uso
  VERSION_SPECIFIC_CANARY_FIXTURE_PATH— caminho de fixture em runner de canário
  EXECUTABLE_VALIDATION_OR_STAMPING   — literal usado em comparação ou carimbo

Só a terceira bloqueia.
"""
from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "VERSION-LITERAL-SWEEP-FULL.yaml"
REPO = Path(__file__).parent

TREES = [DRIVE / "Course-to-Skill", DRIVE / "Course-to-Skill-Compiler"]

VERSION_RE = re.compile(r"[vV]?0\.1\.[0-9]+")

# Qual etapa da cadeia cada script executa.
STEP_OF = {
    "freeze_margin_lock.py": ("congelar", "emite o comparison/margin lock"),
    "freeze_pre_run_registry.py": ("registrar",
                                   "emite o pre-run registry e o opening record"),
    "score_judge_results.py": ("pontuar", "recomputa notas e emite o veredito"),
    "capture_raw_output.py": ("capturar", "registra a saída crua do candidato"),
    "validate_generated_skill.py": ("validar", "valida a skill gerada"),
    "VERIFY_KIT.py": ("validar", "confere o kit"),
    # scripts do repositório que participam da cadeia
    "prerun_chain_v014.py": ("congelar",
                             "monta as entradas e dirige os dois freezers"),
    "structural_ceiling_v014.py": ("relatar",
                                   "emite o STRUCTURAL-CEILING-REPORT que o "
                                   "freezer consome"),
    "structural_ceiling_v013.py": ("relatar", "idem, para a v0.1.3"),
    "pilot002_holdout.py": ("sela", "vault-seal e held-out lock do PILOT-002"),
}
CANARY_FILES = re.compile(r"canary|canario", re.I)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def string_regions(src: str) -> set[int]:
    """Linhas (1-based) que caem dentro de docstring/bloco de aspas triplas."""
    lines = src.splitlines()
    inside, delim, out = False, None, set()
    for i, ln in enumerate(lines, 1):
        j, opened_here = 0, False
        while j < len(ln):
            if not inside:
                m = re.compile(r'"""|\'\'\'').match(ln, j)
                if m:
                    inside, delim, opened_here = True, m.group(0), True
                    j = m.end()
                    continue
                if ln[j] == "#":
                    break
                j += 1
            else:
                k = ln.find(delim, j)
                if k == -1:
                    j = len(ln)
                else:
                    inside, delim = False, None
                    j = k + 3
        if inside or opened_here:
            out.add(i)
    return out


def comment_lines(src: str) -> set[int]:
    return {i for i, ln in enumerate(src.splitlines(), 1)
            if ln.lstrip().startswith("#")}


# Um literal de versão só bloqueia se for IDENTIDADE DE CANDIDATO usada em
# comparação ou carimbo. Estes são os dois padrões que o F5 nomeia:
STAMP_RE = re.compile(r"""candidate_version["']?\s*[:=]\s*["']?[vV]?0\.1\.\d""")
IDENTITY_RE = re.compile(r"expected_artifact|expected_role|arm_id\s*==|"
                         r"==\s*[\"'][^\"']*0\.1\.\d")
# schema_version NÃO é versão de candidato.
SCHEMA_RE = re.compile(r"""schema_version["']?\s*[:=]""")
# saída de prosa: relatório, print, append de linha
PROSE_RE = re.compile(r"^\s*(w\(|A\(|print\(|L\.append\(|#)")


def classify(fname: str, line_no: int, text: str, in_doc: bool,
             in_comment: bool) -> tuple[str, bool, str]:
    t = text.strip()
    if in_doc or in_comment:
        return ("DOCUMENTATION_OR_EXAMPLE", False,
                "literal dentro de docstring ou comentário")
    if t.startswith("--") or t.endswith("\\"):
        return ("DOCUMENTATION_OR_EXAMPLE", False, "linha de exemplo de uso")
    if SCHEMA_RE.search(t) and not STAMP_RE.search(t):
        return ("DOCUMENTATION_OR_EXAMPLE", False,
                "é schema_version, não versão de candidato")
    if PROSE_RE.match(t) and not (STAMP_RE.search(t) or IDENTITY_RE.search(t)):
        return ("DOCUMENTATION_OR_EXAMPLE", False,
                "texto de relatório emitido, não lógica de validação")
    if STAMP_RE.search(t):
        return ("EXECUTABLE_VALIDATION_OR_STAMPING_LITERAL", True,
                "carimba candidate_version literal em artefato de integridade")
    if IDENTITY_RE.search(t):
        return ("EXECUTABLE_VALIDATION_OR_STAMPING_LITERAL", True,
                "compara identidade de artefato contra literal de versão")
    if CANARY_FILES.search(fname):
        return ("VERSION_SPECIFIC_CANARY_FIXTURE_PATH", False,
                "caminho de fixture dentro de runner de canário")
    if re.search(r"0\.1\.\d[^\"']*\.(yaml|yml|md|zip|txt|json)", t) or "/" in t:
        return ("VERSION_SPECIFIC_CANARY_FIXTURE_PATH", False,
                "literal é caminho ou nome de arquivo versionado")
    return ("VERSION_SPECIFIC_CANARY_FIXTURE_PATH", False,
            "literal de versão sem papel de validação identificado")


def scan_source(tree: str, fname: str, src: str) -> list[dict]:
    docs = string_regions(src)
    coms = comment_lines(src)
    out = []
    for i, ln in enumerate(src.splitlines(), 1):
        if not VERSION_RE.search(ln):
            continue
        cls, blocking, why = classify(fname, i, ln, i in docs, i in coms)
        rec = {"source_tree": tree, "file": fname, "line": i,
               "text": ln.strip()[:220],
               "versions_seen": sorted(set(VERSION_RE.findall(ln))),
               "classification": cls, "blocking_class_candidate": blocking,
               "why": why}
        if blocking:
            step, what = STEP_OF.get(fname, ("desconhecida", "papel não mapeado"))
            vers = sorted({v.lstrip("vV") for v in VERSION_RE.findall(ln)})
            rec["breaks_step"] = step
            rec["step_does"] = what
            rec["literal_version"] = vers
            rec["breaks_when"] = (
                f"quebra a etapa `{step}` em qualquer rodada cuja versão de "
                f"candidato não seja {', '.join(vers)}")
        out.append(rec)
    return out


def collect() -> tuple[list[dict], list[dict]]:
    findings, inventory = [], []

    for tree in TREES:
        for z in sorted(tree.rglob("*.zip")):
            try:
                zf = zipfile.ZipFile(z)
            except zipfile.BadZipFile:
                continue
            with zf:
                for n in zf.namelist():
                    if not n.endswith(".py"):
                        continue
                    b = zf.read(n)
                    fname = n.split("/")[-1]
                    label = z.stem.replace("PILOT-001-v0.1.3-", "") \
                                  .replace("PILOT-001-", "")
                    inventory.append({"source_tree": label, "file": fname,
                                      "container": str(z.relative_to(DRIVE)),
                                      "sha256": sha(b), "bytes": len(b)})
                    findings += scan_source(label, fname,
                                            b.decode("utf-8", "replace"))

    # .py soltos nas árvores read-only (fora de zip)
    for tree in TREES:
        for p in sorted(tree.rglob("*.py")):
            if not p.is_file():
                continue
            b = p.read_bytes()
            inventory.append({"source_tree": f"LOOSE:{tree.name}",
                              "file": p.name,
                              "container": str(p.relative_to(DRIVE)),
                              "sha256": sha(b), "bytes": len(b)})
            findings += scan_source(f"LOOSE:{tree.name}", p.name,
                                    b.decode("utf-8", "replace"))

    # scripts do repositório que participam da cadeia
    chain_repo = ["structural_ceiling_v014.py", "prerun_chain_v014.py",
                  "structural_ceiling_v013.py", "pilot002_holdout.py",
                  "source_density.py", "density_calibration.py",
                  "judge_package_verify.py", "rubric_ceiling_report.py",
                  "coverage_map.py", "publish.py", "spine.py"]
    for name in chain_repo:
        p = REPO / name
        if not p.exists():
            continue
        b = p.read_bytes()
        inventory.append({"source_tree": "REPO", "file": name,
                          "container": "course-to-skill-claude (ext4)",
                          "sha256": sha(b), "bytes": len(b)})
        findings += scan_source("REPO", name, b.decode("utf-8", "replace"))
    for p in sorted((REPO / "cts").glob("*.py")):
        b = p.read_bytes()
        inventory.append({"source_tree": "REPO_CTS", "file": f"cts/{p.name}",
                          "container": "course-to-skill-claude (ext4)",
                          "sha256": sha(b), "bytes": len(b)})
        findings += scan_source("REPO_CTS", f"cts/{p.name}",
                                b.decode("utf-8", "replace"))
    return findings, inventory


def main() -> int:
    findings, inventory = collect()
    blocking = [f for f in findings if f["blocking_class_candidate"]]

    by_class = {}
    for f in findings:
        by_class[f["classification"]] = by_class.get(f["classification"], 0) + 1

    # deduplicação por (arquivo, linha, texto): o mesmo script aparece em vários
    # pacotes; o defeito é o mesmo, o alcance é que muda.
    uniq = {}
    for f in blocking:
        k = (f["file"], f["text"])
        uniq.setdefault(k, {"file": f["file"], "text": f["text"],
                            "breaks_step": f.get("breaks_step"),
                            "step_does": f.get("step_does"),
                            "literal_version": f.get("literal_version"),
                            "breaks_when": f.get("breaks_when"),
                            "seen_in": []})
        uniq[k]["seen_in"].append({"source_tree": f["source_tree"],
                                   "line": f["line"]})

    covered_by_f5 = {"F3_TRISTATE", "F4_STRUCTURAL_ID",
                     "PRELOCK-PATCH-F3-TRISTATE", "PRELOCK-PATCH-F4-STRUCTURAL-ID"}
    new_vs_f5 = [d for d in uniq.values()
                 if not all(s["source_tree"] in covered_by_f5 for s in d["seen_in"])]

    # CALIBRAÇÃO: nos dois pacotes que o F5 já varreu, esta varredura tem de
    # reproduzir exatamente os bloqueantes que o F5 publicou. Divergiu, o
    # classificador não é confiável nos pacotes ainda não varridos.
    f5_expected = {
        ("PRELOCK-PATCH-F3-TRISTATE", "freeze_pre_run_registry.py", 53),
        ("PRELOCK-PATCH-F3-TRISTATE", "freeze_pre_run_registry.py", 69),
        ("PRELOCK-PATCH-F4-STRUCTURAL-ID", "freeze_margin_lock.py", 381),
        ("PRELOCK-PATCH-F4-STRUCTURAL-ID", "score_judge_results.py", 880),
    }
    f5_trees = {"PRELOCK-PATCH-F3-TRISTATE", "PRELOCK-PATCH-F4-STRUCTURAL-ID"}
    mine = {(f["source_tree"], f["file"], f["line"]) for f in blocking
            if f["source_tree"] in f5_trees}
    calibration = {
        "why": ("O classificador é conferido contra os vereditos já publicados "
                "pelo F5 nos dois pacotes que ele varreu. Sem isso, não há como "
                "saber se os achados nos pacotes novos são reais."),
        "f5_blocking_expected": sorted(f"{a}:{b}:{c}" for a, b, c in f5_expected),
        "this_sweep_found": sorted(f"{a}:{b}:{c}" for a, b, c in mine),
        "missed": sorted(f"{a}:{b}:{c}" for a, b, c in (f5_expected - mine)),
        "extra": sorted(f"{a}:{b}:{c}" for a, b, c in (mine - f5_expected)),
        "agrees_with_f5": mine == f5_expected,
    }

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-001-VERSION-LITERAL-SWEEP-FULL-v0.1.4",
        "calibration_against_f5": calibration,
        "artifact_status": "STATIC_SWEEP_NO_FIX_APPLIED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "extends": "PILOT-001-F5-VERSION-LITERAL-SWEEP-v0.1.4",
        "why": ("A varredura do F5 cobriu só F3-TRISTATE e F4. Um literal cravado "
                "em script não varrido queima a rodada cega, e conversa cega não "
                "se repete."),
        "scope": {
            "packages_scanned": sorted({i["source_tree"] for i in inventory}),
            "python_files_scanned": len(inventory),
            "distinct_scripts": len({i["file"] for i in inventory}),
        },
        "rule": ("Literal de validação/identidade/carimbo em código executável é "
                 "candidato a defeito de classe. Docstring, exemplo de uso e "
                 "caminho de fixture de canário não são."),
        "classification_counts": by_class,
        "totals": {
            "occurrences": len(findings),
            "blocking_occurrences": len(blocking),
            "blocking_distinct_defects": len(uniq),
            "blocking_distinct_defects_outside_f5_scope": len(new_vs_f5),
        },
        "blocking_defects": sorted(uniq.values(), key=lambda d: d["file"]),
        "blocking_defects_outside_f5_scope": new_vs_f5,
        "inventory": sorted(inventory, key=lambda i: (i["source_tree"], i["file"])),
        "findings": findings,
        "no_fix_applied": True,
        "note": ("Nada foi corrigido. Nenhum script auditado foi editado. Esta "
                 "varredura é estática: não prova que um literal bloqueante "
                 "dispara numa rodada concreta, só que ele está em posição de "
                 "disparar. A confirmação empírica é o ensaio seco."),
    }

    OUT.write_text(
        "# VERSION-LITERAL-SWEEP-FULL — todos os pacotes\n"
        "# Gerado por script. READ-ONLY. Nada corrigido.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"pacotes: {len(doc['scope']['packages_scanned'])} | "
          f"arquivos .py: {len(inventory)} | ocorrências: {len(findings)}")
    for k, v in sorted(by_class.items()):
        print(f"  {k}: {v}")
    print(f"calibração contra o F5: "
          f"{'CONFERE' if calibration['agrees_with_f5'] else 'DIVERGE'}"
          f" (faltou={calibration['missed']} sobrou={calibration['extra']})")
    print(f"defeitos bloqueantes distintos: {len(uniq)} "
          f"(fora do escopo do F5: {len(new_vs_f5)})")
    for d in sorted(uniq.values(), key=lambda x: x["file"]):
        trees = ", ".join(sorted({s['source_tree'] for s in d['seen_in']}))
        print(f"  [{d['breaks_step']}] {d['file']} — {trees}")
        print(f"      {d['text'][:100]}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
