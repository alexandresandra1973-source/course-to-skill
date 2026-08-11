#!/usr/bin/env python3
"""FRENTE 1 — cadeia pré-run da v0.1.4: árvore, freezers auditados, BLIND_RUN_READY.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/: os freezers são EXTRAÍDOS
para /tmp e conferidos contra o manifesto do pacote de origem antes de rodar.
Nenhum script auditado é editado.

Se um freezer recusar, o relatório registra a recusa com o erro literal. Não se
contorna validador auditado nem se congela artefato com campo falso.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
CS = DRIVE / "Course-to-Skill"
V013 = CS / "PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007"

TREE = DOCS / "v0.1.4/06_COMPARISON_ARMS/TEST-0007"
LOCKDIR = TREE / "PRE_RUN_LOCK"
BRR = TREE / "BLIND_RUN_READY"
OLD_BRR = DOCS / "BLIND_RUN_READY-v0.1.4"
REPORT = DOCS / "PRE-RUN-CHAIN-v0.1.4.md"

TMP = Path("/tmp/v014chain")
SCRATCH = TMP / "work"

FREEZERS = {
    "freeze_margin_lock.py": (
        V013 / "FINAL_PRE_RUN_LOCK/PILOT-001-v0.1.3-PRELOCK-PATCH-F4-STRUCTURAL-ID.zip",
        "PILOT-001-v0.1.3-PRELOCK-PATCH-F4-STRUCTURAL-ID/", "F4-SHA256SUMS.txt"),
    "freeze_pre_run_registry.py": (
        V013 / "PRELOCK_F3_TRISTATE/PILOT-001-v0.1.3-PRELOCK-PATCH-F3-TRISTATE.zip",
        "PILOT-001-v0.1.3-PRELOCK-PATCH-F3-TRISTATE/", "SHA256SUMS.txt"),
}
F3ZIP = FREEZERS["freeze_pre_run_registry.py"][0]
F3PRE = FREEZERS["freeze_pre_run_registry.py"][1]

ARMS = {
    "FULL@BEFORE_DEDUP": ("PILOT-001-TEST-0007-FULL-BEFORE_DEDUP-v0.1.4.zip",
                          "555a70295ca23f89878150ddf2b0c207fba393137f1b8e4383bd9be18e7cedfb"),
    "FULL@AFTER_DEDUP": ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip",
                         "b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028"),
    "ABLATED@AFTER_DEDUP": ("PILOT-001-TEST-0007-ABLATED-AFTER_DEDUP-v0.1.4.zip",
                            "da9b326dbd80af1711c67a5f95999118bdc54ce6b84b6e54dbd756b4d657a205"),
}
JUDGE_REFS = {
    "TEST-0007-RUBRIC-v0.1.3.yaml":
        "66aa33c0c39430fc02a23fc536a475eda8afbd6b18c0f34b01ef075ebf522e9f",
    "TEST-0007-RUBRIC-ANCHOR-ADDENDUM-v0.1.3.yaml":
        "909e38ed245ac8aa0dd32503cdf08f856c8a1227fada22d27639689adc223810",
    "TEST-0007-DECISION-RULE-v0.1.3.yaml":
        "540df7283405aba5dfd2569511e8e11ad42015f55876b39284b3c8c61d160856",
}
SCREPORT = DOCS / "STRUCTURAL-CEILING-REPORT-v0.1.4.yaml"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def zread(z: Path, inner: str) -> bytes:
    with zipfile.ZipFile(z) as f:
        return f.read(inner)


def locate(want: str) -> str | None:
    for p in sorted(CS.rglob("*")):
        if not p.is_file():
            continue
        try:
            if sha(p.read_bytes()) == want:
                return str(p.relative_to(DRIVE))
            if p.suffix.lower() == ".zip":
                with zipfile.ZipFile(p) as z:
                    for n in z.namelist():
                        if not n.endswith("/") and sha(z.read(n)) == want:
                            return f"{p.relative_to(DRIVE)} :: {n}"
        except (OSError, zipfile.BadZipFile):
            continue
    return None


# ---------------------------------------------------------------- 1. freezers
def extract_freezers() -> tuple[dict, bool]:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, (z, pref, manifest) in FREEZERS.items():
        blob = zread(z, pref + name)
        man = zread(z, pref + manifest).decode("utf-8", "replace")
        got = sha(blob)
        declared = next((l.split()[0] for l in man.splitlines()
                         if l.strip().endswith(name)), None)
        ok = declared == got
        if ok:
            (TMP / name).write_bytes(blob)
        out[name] = {"source_package": str(z.relative_to(DRIVE)),
                     "manifest": manifest, "bytes": len(blob),
                     "declared_sha256": declared, "observed_sha256": got,
                     "match": ok}
    return out, all(v["match"] for v in out.values())


# ------------------------------------------------------------ 3. cadeia lock
def prepare_inputs() -> None:
    for src, dst in [("canary/suite.yaml", "suite.yaml"),
                     ("canary/contract.yaml", "contract.yaml"),
                     ("canary/metric-lock.yaml", "metric-lock.yaml"),
                     ("TEST-0007-RUBRIC-v0.1.3.yaml", "rubric.yaml"),
                     ("TEST-0007-RUBRIC-ANCHOR-ADDENDUM-v0.1.3.yaml", "addendum.yaml"),
                     ("TEST-0007-RUBRIC-ANCHOR-ADDENDUM-FREEZE-RECORD-v0.1.3.yaml",
                      "addendum-freeze.yaml"),
                     ("TEST-0007-DECISION-RULE-v0.1.3.yaml", "decision-rule.yaml")]:
        (SCRATCH / dst).write_bytes(zread(F3ZIP, F3PRE + src))
    shutil.copy(SCREPORT, SCRATCH / "structural-report.yaml")
    (SCRATCH / "margin-draft.yaml").write_text(yaml.safe_dump({
        "schema_version": "0.5.0", "artifact_status": "DRAFT_NOT_LOCKED",
        "candidate_version": "0.1.4",
        "comparisons": {"TEST-0007": {
            "left": {"arm_id": "FULL", "phase": "AFTER_DEDUP"},
            "right": {"arm_id": "ABLATED", "phase": "AFTER_DEDUP"},
            "arm_package_hashes": {k: {"sha256": h} for k, (_, h) in ARMS.items()},
            "margin_threshold": 34.0,
            "threshold_justification": {
                "basis": "FROZEN_ANCHOR_BOUNDARY",
                "anchor_boundary_reference": 34.0,
                "effective_ceiling_reference": 60.0,
                "threshold_fraction_of_effective_ceiling": 34.0 / 60.0,
                "rationale": ("Reusado verbatim da regra de decisão congelada "
                              "540df728…; nenhum limiar derivado aqui."),
                "distinguishability_rationale": ("Zona inconclusiva [28.831; 39.169] "
                                                 "e piso 4w 20.675 são congelados à "
                                                 "parte."),
            },
            "full_preservation": {
                "before": {"arm_id": "FULL", "phase": "BEFORE_DEDUP"},
                "after": {"arm_id": "FULL", "phase": "AFTER_DEDUP"},
                "max_total_regression": 0.0,
                "require_no_new_mandatory_floor_failure": True},
        }}}, sort_keys=False, allow_unicode=True), encoding="utf-8")


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=SCRATCH)
    return p.returncode, (p.stdout + p.stderr).strip()


def try_chain() -> dict:
    prepare_inputs()
    rc, out = run([sys.executable, str(TMP / "freeze_margin_lock.py"),
                   "--suite", "suite.yaml", "--contract", "contract.yaml",
                   "--draft", "margin-draft.yaml",
                   "--structural-report", "structural-report.yaml",
                   "--test0007-rubric", "rubric.yaml",
                   "--rubric-addendum", "addendum.yaml",
                   "--rubric-addendum-freeze-record", "addendum-freeze.yaml",
                   "--decision-rule", "decision-rule.yaml",
                   "--out", "comparison-lock.yaml"])
    step1 = {"step": "freeze_margin_lock.py", "exit_code": rc, "output": out,
             "frozen": rc == 0}

    # Diagnóstico: isolar a causa sem editar o freezer nem republicar o relatório.
    diag = None
    if rc != 0:
        d = yaml.safe_load((SCRATCH / "structural-report.yaml").read_text(encoding="utf-8"))
        before = {k: d["arms"][k]["arm_id"] for k in ("full_after_dedup",
                                                      "ablated_after_dedup")}
        d["arms"]["full_after_dedup"]["arm_id"] = "FULL"
        d["arms"]["ablated_after_dedup"]["arm_id"] = "ABLATED"
        (SCRATCH / "diag-report.yaml").write_text(
            yaml.safe_dump(d, sort_keys=False, allow_unicode=True), encoding="utf-8")
        rc2, out2 = run([sys.executable, str(TMP / "freeze_margin_lock.py"),
                         "--suite", "suite.yaml", "--contract", "contract.yaml",
                         "--draft", "margin-draft.yaml",
                         "--structural-report", "diag-report.yaml",
                         "--test0007-rubric", "rubric.yaml",
                         "--rubric-addendum", "addendum.yaml",
                         "--rubric-addendum-freeze-record", "addendum-freeze.yaml",
                         "--decision-rule", "decision-rule.yaml",
                         "--out", "diag-lock.yaml"])
        diag = {"changed_only": before, "changed_to": {"full_after_dedup": "FULL",
                                                       "ablated_after_dedup": "ABLATED"},
                "exit_code": rc2, "output": out2, "would_freeze": rc2 == 0,
                "written_to": "/tmp (descartável) — o relatório publicado NÃO foi tocado"}

    # O registry stampa candidate_version fixo; medir isso é o que decide.
    step2 = None
    if diag and diag["would_freeze"]:
        rc3, out3 = run([sys.executable, str(TMP / "freeze_pre_run_registry.py"),
                         "--comparison-lock", "diag-lock.yaml",
                         "--metric-lock", "metric-lock.yaml",
                         "--registry-out", "diag-registry.yaml",
                         "--opening-record-out", "diag-opening.yaml"])
        stamped = None
        if rc3 == 0:
            r = yaml.safe_load((SCRATCH / "diag-registry.yaml").read_text(encoding="utf-8"))
            o = yaml.safe_load((SCRATCH / "diag-opening.yaml").read_text(encoding="utf-8"))
            stamped = {"registry_candidate_version": r.get("candidate_version"),
                       "opening_candidate_version": o.get("candidate_version")}
        step2 = {"step": "freeze_pre_run_registry.py (diagnóstico)", "exit_code": rc3,
                 "output": out3, "stamped": stamped}
    return {"margin_lock": step1, "arm_id_diagnostic": diag, "registry_probe": step2}


# ------------------------------------------------ 4. instruções do juiz v0.1.4
def derive_judge_instructions() -> tuple[str, dict]:
    z = V013 / "PILOT-001-v0.1.3-TEST-0007-JUDGE-BLIND-RUN.zip"
    inner = "PILOT-001-v0.1.3-TEST-0007-JUDGE-BLIND-RUN/JUDGE-BLIND-RUN-INSTRUCTIONS.md"
    orig = zread(z, inner).decode("utf-8")
    changes = []
    body = orig
    if "TEST-0007 v0.1.3" in body:
        body = body.replace("TEST-0007 v0.1.3", "TEST-0007 v0.1.4")
        changes.append("título: 'TEST-0007 v0.1.3' → 'TEST-0007 v0.1.4'")
    header = (
        "<!-- ARTEFATO DERIVADO, NÃO ORIGINAL.\n"
        f"     Origem: {inner} (sha256 {sha(orig.encode())})\n"
        "     Derivado por script a partir da versão v0.1.3. Alterações:\n"
        + "".join(f"       - {c}\n" for c in changes)
        + "       - acrescentada a tabela de hashes dos artefatos da rodada v0.1.4\n"
        "     Os nomes de arquivo da régua e dos addenda SEGUEM v0.1.3 de propósito:\n"
        "     esses artefatos não foram reemitidos e continuam sendo os da v0.1.3.\n"
        "     NÃO congelado. Precisa de revisão antes de virar artefato de rodada. -->\n\n")
    table = ("\n## Artefatos desta rodada (v0.1.4)\n\n"
             "| artefato | sha256 |\n|---|---|\n"
             + "".join(f"| `{ARMS[k][0]}` | `{ARMS[k][1]}` |\n" for k in ARMS)
             + "".join(f"| `{k}` | `{v}` |\n" for k, v in JUDGE_REFS.items())
             + f"| `{SCREPORT.name}` | `{sha(SCREPORT.read_bytes())}` |\n")
    derived = header + body.rstrip() + "\n" + table
    return derived, {"origin_inner": inner, "origin_sha256": sha(orig.encode()),
                     "changes": changes, "derived": True, "frozen": False}


def build_brr(chain: dict, judge_md: str, judge_meta: dict) -> None:
    BRR.mkdir(parents=True, exist_ok=True)
    arm_loc = {k: locate(h) for k, (_, h) in ARMS.items()}
    judge_loc = {k: locate(v) for k, v in JUDGE_REFS.items()}

    (BRR / "JUDGE-BLIND-RUN-INSTRUCTIONS-v0.1.4.md").write_text(judge_md,
                                                                encoding="utf-8")
    (BRR / "CANDIDATE-ATTACHMENTS.md").write_text(
        "# Conversa CANDIDATA — o que anexar\n\n"
        "Uma conversa NOVA por braço. Nunca dois braços na mesma conversa.\n\n"
        "| ordem | braço | anexar | sha256 |\n|---|---|---|---|\n"
        + "".join(f"| {i} | `{k}` | `{ARMS[k][0]}` | `{ARMS[k][1]}` |\n"
                 for i, k in enumerate(ARMS, 1))
        + "\nOrigem (referenciada, não copiada):\n\n"
        + "".join(f"- `{k}` → `{arm_loc[k]}`\n" for k in ARMS)
        + "\nAnexar só `agent-input/runtime-bundle/` como Skill e seguir\n"
          "`agent-input/RUNNER_PROMPT.md`. Nada de régua, testes ou judge-private.\n",
        encoding="utf-8")

    (BRR / "JUDGE-ATTACHMENTS.md").write_text(
        "# Conversa JUIZ — o que anexar\n\n"
        "Conversa nova, sem contexto prévio de PILOT-001. Anexar as três saídas\n"
        "cruas das conversas candidatas, mais:\n\n"
        "| artefato | sha256 | origem |\n|---|---|---|\n"
        + "".join(f"| `{k}` | `{v}` | `{judge_loc[k]}` |\n"
                 for k, v in JUDGE_REFS.items())
        + f"| `JUDGE-BLIND-RUN-INSTRUCTIONS-v0.1.4.md` | "
          f"`{sha(judge_md.encode())}` | derivado nesta pasta |\n"
        + "\nO arquivo de instruções é **derivado** da v0.1.3 e **não está "
          "congelado**. Ver o cabeçalho dele.\n",
        encoding="utf-8")

    frozen = chain["margin_lock"]["frozen"]
    anchor2 = ("PRE-RUN-OPENING-RECORD SHA-256: <sha do opening record>"
               if not frozen else "ver opening-record")
    (BRR / "ANCHOR-LINES.md").write_text(
        "# Linhas de âncora — PRIMEIRA mensagem\n\n"
        "## 1. Conversa CANDIDATA\n\n"
        "Cole o conteúdo integral de `agent-input/RUNNER_PROMPT.md` do pacote, sem\n"
        "editar. Ele exige esta resposta, que é a âncora de confirmação:\n\n"
        "```\nPILOT-001 v0.1.4 runtime loaded — ready for blind cases.\n```\n\n"
        "Resposta diferente disso = conversa suja. Descarte e abra outra.\n\n"
        "## 2. Conversa JUIZ\n\n"
        "A âncora do juiz é o hash do opening record, no formato que o próprio\n"
        "`freeze_pre_run_registry.py` imprime:\n\n"
        f"```\n{anchor2}\n```\n\n"
        + ("**BLOQUEADA.** O opening record não foi congelado — ver "
           "`PRE-RUN-CHAIN-v0.1.4.md`. Sem ele não há hash para colar.\n"
           if not frozen else ""),
        encoding="utf-8")

    readme = (
        "# Abertura da rodada cega — TEST-0007 v0.1.4\n"
        "\n"
        "**NÃO ABRA AINDA.** A cadeia pré-run não fechou: ver\n"
        "`PRE-RUN-CHAIN-v0.1.4.md`. Sem opening record não há âncora do juiz.\n"
        "\n"
        "Quando liberado, nesta ordem:\n"
        "\n"
        "1. Abra 3 conversas candidatas novas, uma por braço: BEFORE, AFTER,\n"
        "   ABLATED (`CANDIDATE-ATTACHMENTS.md`).\n"
        "2. Cole o `RUNNER_PROMPT.md` como primeira mensagem e confira a âncora\n"
        "   (`ANCHOR-LINES.md`).\n"
        "3. Dê o caso de teste. Salve a saída crua de cada conversa.\n"
        "4. Abra 1 conversa de juiz nova. Anexe as 3 saídas e o que está em\n"
        "   `JUDGE-ATTACHMENTS.md`.\n"
        "5. Confira tudo contra `SHA256SUMS.txt` antes de começar.\n")
    if len(readme.splitlines()) > 15:
        raise SystemExit("README-ABERTURA.md passou de 15 linhas")
    (BRR / "README-ABERTURA.md").write_text(readme, encoding="utf-8")

    files = sorted(p for p in BRR.iterdir()
                   if p.is_file() and p.name != "SHA256SUMS.txt")
    (BRR / "SHA256SUMS.txt").write_text(
        f"# BLIND_RUN_READY v0.1.4 — {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
        "# Hashes dos arquivos DESTA pasta. Os pacotes de braço são referenciados,\n"
        "# não copiados; os hashes deles estão em CANDIDATE-ATTACHMENTS.md.\n"
        + "".join(f"{sha(p.read_bytes())}  {p.stat().st_size}  {p.name}\n"
                 for p in files), encoding="utf-8")


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    TMP.mkdir(parents=True, exist_ok=True)

    fz, fz_ok = extract_freezers()
    if not fz_ok:
        print("PORTÃO DOS FREEZERS: DIVERGE — FRENTE 1 abortada")
        for k, v in fz.items():
            print(f"  {k}: declarado={v['declared_sha256']} obtido={v['observed_sha256']}")
        return 2
    print(f"portão dos freezers: PASS ({len(fz)}/{len(fz)})")

    TREE.mkdir(parents=True, exist_ok=True)
    LOCKDIR.mkdir(parents=True, exist_ok=True)

    chain = try_chain()
    judge_md, judge_meta = derive_judge_instructions()
    build_brr(chain, judge_md, judge_meta)

    if OLD_BRR.is_dir():
        (OLD_BRR / "SUPERSEDED.md").write_text(
            "# Pasta superada\n\n"
            f"Substituída por `docs/{BRR.relative_to(DOCS)}`, que tem as instruções\n"
            "do juiz derivadas e as duas linhas de âncora. Nada foi apagado aqui.\n",
            encoding="utf-8")

    ml = chain["margin_lock"]
    diag = chain["arm_id_diagnostic"]
    reg = chain["registry_probe"]

    L, w = [], None
    w = L.append
    w("# Cadeia pré-run da v0.1.4 — o que fechou e o que recusou")
    w("")
    w(f"- Gerado: `{stamp}` · gerador `{Path(__file__).name}`")
    w("- READ-ONLY sobre `Course-to-Skill/`. Nenhum script auditado foi editado.")
    w("- **Nada foi congelado.**")
    w("")
    w("## 1. Portão dos freezers")
    w("")
    w("| freezer | pacote de origem | bytes | sha256 | confere |")
    w("|---|---|---|---|---|")
    for k, v in fz.items():
        w(f"| `{k}` | `{Path(v['source_package']).name}` | {v['bytes']} | "
          f"`{v['observed_sha256'][:16]}…` | {'sim' if v['match'] else 'NÃO'} |")
    w("")
    w("Ambos conferem contra o manifesto do próprio pacote.")
    w("")
    w("## 2. Árvore v0.1.4")
    w("")
    w(f"Criada em `docs/{TREE.relative_to(DOCS)}`.")
    w("")
    w("**Os artefatos v0.1.4 hoje moram indevidamente sob `v0.1.3/`.** O pacote "
      "`PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN.zip` está em "
      "`Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007/"
      "ARMS_WORDING_FROZEN/`. Esta árvore não corrige isso — `Course-to-Skill/` é "
      "read-only nesta sessão. Mover é decisão do Alexandre.")
    w("")
    w("## 3. Cadeia de lock — RECUSADA, em dois pontos independentes")
    w("")
    w(f"### 3.1 `freeze_margin_lock.py` → exit {ml['exit_code']}")
    w("")
    w("```")
    w(ml["output"])
    w("```")
    w("")
    if diag:
        w("**Causa isolada.** Rodei o mesmo freezer mudando **apenas** o `arm_id` "
          "dos dois braços no relatório estrutural, numa cópia descartável em "
          "`/tmp` — o relatório publicado não foi tocado:")
        w("")
        w("| campo | no relatório publicado | no diagnóstico |")
        w("|---|---|---|")
        for k in diag["changed_only"]:
            w(f"| `arms.{k}.arm_id` | `{diag['changed_only'][k]}` | "
              f"`{diag['changed_to'][k]}` |")
        w("")
        w(f"Resultado: exit {diag['exit_code']} — "
          f"**{'congelaria' if diag['would_freeze'] else 'ainda recusaria'}**.")
        w("")
        w("Ou seja, tudo o mais passa: limiar 34,0, teto 60,0, hashes dos braços, "
          "regra de decisão. O que barra é uma **amarração de versão** dentro do "
          "freezer: a função `structural_role` aceita só o papel genérico (`FULL`, "
          "`ABLATED`) ou o nome de artefato **da v0.1.3** "
          "(`PILOT-001-TEST-0007-…-AFTER_DEDUP-V0.1.3`), cravado no código. O nome "
          "da v0.1.4 não está na lista.")
        w("")
        w("Isso é justamente a área que o patch F4 "
          "(`STRUCTURAL-ARM-ID-NORMALIZATION`) endereçou — e que não foi estendida "
          "para a 0.1.4.")
        w("")
    if reg:
        w(f"### 3.2 `freeze_pre_run_registry.py` → exit {reg['exit_code']}")
        w("")
        w("Sondado sobre o lock do diagnóstico, só para ver o que ele carimbaria:")
        w("")
        w("```")
        w(reg["output"])
        w("```")
        w("")
        if reg["stamped"]:
            w("| campo | valor carimbado |")
            w("|---|---|")
            for k, v in reg["stamped"].items():
                w(f"| `{k}` | **{v}** |")
            w("")
            w("**Este é o segundo bloqueio, e é o decisivo.** O freezer tem "
              "`candidate_version` **fixo em `'0.1.3'`** no código. Congelar a "
              "cadeia agora gravaria, dentro do registry e do opening record — "
              "artefatos que existem justamente para provar integridade — a "
              "afirmação falsa de que a rodada é 0.1.3.")
            w("")
    w("### 3.3 Decisão")
    w("")
    w("**Não congelei.** Havia dois caminhos e recusei os dois:")
    w("")
    w("1. **Editar os freezers** para aceitar 0.1.4 — quebra a premissa de usar "
      "\"os scripts já auditados\". A correção precisa vir como patch auditado, "
      "não como edição de madrugada.")
    w("2. **Ajustar a entrada** para o formato que o validador da v0.1.3 aceita — "
      "resolveria o 3.1, mas não o 3.2, e o registry continuaria carimbando 0.1.3. "
      "Congelar um artefato de integridade com a versão errada é pior do que não "
      "congelar.")
    w("")
    w("## 4. BLIND_RUN_READY")
    w("")
    w(f"Publicada em `docs/{BRR.relative_to(DOCS)}`:")
    w("")
    for p in sorted(BRR.iterdir()):
        w(f"- `{p.name}` — {p.stat().st_size} B · `{sha(p.read_bytes())[:16]}…`")
    w("")
    w("As instruções do juiz da v0.1.4 foram **derivadas** da v0.1.3 "
      f"(origem sha256 `{judge_meta['origin_sha256'][:16]}…`), com o cabeçalho "
      "declarando que é derivada e não original. Alterações: "
      + ("; ".join(judge_meta["changes"]) or "nenhuma no corpo")
      + "; mais a tabela de hashes da rodada v0.1.4.")
    w("")
    w("Os nomes de arquivo da régua e dos addenda continuam `v0.1.3` de propósito: "
      "esses artefatos não foram reemitidos, e renomeá-los apontaria para arquivos "
      "que não existem.")
    w("")
    w("**A segunda linha de âncora está bloqueada.** A do juiz é o hash do opening "
      "record, e o opening record não existe.")
    w("")

    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"margin lock: exit {ml['exit_code']} ({'congelado' if ml['frozen'] else 'RECUSADO'})")
    if diag:
        print(f"  diagnóstico arm_id: exit {diag['exit_code']} "
              f"({'congelaria' if diag['would_freeze'] else 'recusaria'})")
    if reg and reg["stamped"]:
        print(f"  registry carimbaria candidate_version="
              f"{reg['stamped']['registry_candidate_version']}")
    print(f"publicado: {REPORT.name} ({REPORT.stat().st_size} B)")
    print(f"pasta: {BRR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
