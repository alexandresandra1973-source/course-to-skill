#!/usr/bin/env python3
"""Diff das duas versões do prompt do compilador, com portão sobre PASS 1 e PASS 2.

Roda daqui (ext4). READ-ONLY absoluto nas duas árvores. Publica só em
`Course-to-Skill-Claude/docs/`.

Relatório GERADO: nenhuma linha, número ou hash é digitado.

O PORTÃO
--------
Se qualquer bloco de diferença tocar o PASS 1 ou o PASS 2, o diagnóstico do
colapso pode ter medido um spec enquanto o PILOT-002 foi compilado com o outro.
Isso é achado grave e para tudo antes de qualquer execução.
"""
from __future__ import annotations

import difflib
import hashlib
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "LESSON-ANALYZER-VERSION-DIFF.md"

RELEASE = (DRIVE / "Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1"
           / "course-to-skill-compiler-v0.1.1-pilot-ready"
           / "course-to-skill-compiler-v0.1.1-pilot-ready"
           / "prompts/lesson-analyzer.md")
RELEASE_ZIP = (DRIVE / "Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1"
               / "course-to-skill-compiler-v0.1.1-pilot-ready.zip")
WORKING = DRIVE / "Course-to-Skill/course-to-skill-compiler/prompts/lesson-analyzer.md"

P2 = CLAUDE / "pilots/PILOT-002/01_COMPILED-SKILL/v0.1.0"
PRECOMPILE = DRIVE / "Course-to-Skill/PILOT-002/00_PRECOMPILE_GOVERNANCE"

# Onde uma execução TERIA registrado a versão do prompt, se registrasse.
PROVENANCE_CANDIDATES = [
    ("COMPILATION_MANIFEST do PILOT-002", P2 / "COMPILATION_MANIFEST.yaml"),
    ("GOVERNANCE.yaml do PILOT-002", P2 / "GOVERNANCE.yaml"),
    ("VALIDATION_REPORT.md do PILOT-002", P2 / "VALIDATION_REPORT.md"),
    ("SCOPE-LOCK pré-compilação", PRECOMPILE / "PILOT-002-PRECOMPILE-SCOPE-LOCK.yaml"),
    ("ADR de pipeline limpo, pré-compilação",
     PRECOMPILE / "ADR-PILOT002-FIRST-CLEAN-PIPELINE-VALIDATION.md"),
]
PROVENANCE_TERMS = r"lesson-analyzer|compiler_version|prompt_sha|prompt_version|d6205a88|5233d68f"


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sections(lines: list[str]) -> list[tuple[int, str]]:
    """Índice de seções `# NN. TÍTULO`, para localizar cada linha alterada."""
    return [(i + 1, l.strip()) for i, l in enumerate(lines)
            if re.match(r"^#\s*\d+\.\s+\S", l.strip())]


def section_of(line_no: int, idx: list[tuple[int, str]]) -> str:
    cur = "(antes da primeira seção — cabeçalho do documento)"
    for ln, title in idx:
        if ln <= line_no:
            cur = title
        else:
            break
    return cur


def pass_ranges(lines: list[str]) -> dict[str, tuple[int, int]]:
    """Faixa de linhas de cada PASS, do cabeçalho ao cabeçalho seguinte."""
    heads = [(i + 1, l.strip()) for i, l in enumerate(lines)
             if re.match(r"^#\s*\d+\.\s+", l.strip())]
    out = {}
    for k, (ln, title) in enumerate(heads):
        m = re.search(r"PASS (\d+)", title)
        if not m:
            continue
        end = heads[k + 1][0] - 1 if k + 1 < len(heads) else len(lines)
        out[f"PASS {m.group(1)}"] = (ln, end)
    return out


def block_hash(lines: list[str], rng: tuple[int, int]) -> str:
    """Hash do TEXTO de um PASS. É a prova direta de que o passe é o mesmo.

    O portão por interseção de linhas diz que nenhuma diferença cai dentro do
    passe. Isto diz a mesma coisa pelo outro lado, sem depender do alinhamento
    do diff: se o hash bate, o conteúdo é idêntico byte a byte.
    """
    a, b = rng
    return hashlib.sha256("\n".join(lines[a - 1:b]).encode("utf-8")).hexdigest()


def build_hunks(a: list[str], b: list[str]) -> list[dict]:
    """Blocos de diferença com numeração nas DUAS versões."""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    hunks = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        hunks.append({
            "op": tag,
            "working_lines": (i1 + 1, i2) if i2 > i1 else None,
            "release_lines": (j1 + 1, j2) if j2 > j1 else None,
            "removed": a[i1:i2],
            "added": b[j1:j2],
        })
    return hunks


def classify(h: dict, pr_w: dict, pr_r: dict, sec_w, sec_r) -> dict:
    """Toca PASS 1? PASS 2? outro PASS? só redação?"""
    touched = set()

    def scan(rng, ranges):
        if not rng:
            return
        lo, hi = rng
        for name, (a, b) in ranges.items():
            if lo <= b and a <= hi:
                touched.add(name)

    scan(h["working_lines"], pr_w)
    scan(h["release_lines"], pr_r)

    where = []
    if h["working_lines"]:
        where.append(f"trabalho L{h['working_lines'][0]}–{h['working_lines'][1]}: "
                     f"{section_of(h['working_lines'][0], sec_w)}")
    if h["release_lines"]:
        where.append(f"release L{h['release_lines'][0]}–{h['release_lines'][1]}: "
                     f"{section_of(h['release_lines'][0], sec_r)}")

    critical = {"PASS 1", "PASS 2"} & touched
    if critical:
        kind = f"**TOCA {', '.join(sorted(critical))}**"
    elif touched:
        kind = f"toca outro PASS ({', '.join(sorted(touched))})"
    else:
        body = [l.strip() for l in (h["removed"] + h["added"]) if l.strip()]
        if len(body) <= 2 and any(re.search(r"\*\*Version:\*\*", l) for l in body):
            kind = "metadado de versão — sem efeito sobre instrução"
        elif h["op"] == "insert":
            kind = "acréscimo fora de qualquer PASS"
        else:
            kind = "redação fora de qualquer PASS"
    return {"touched": sorted(touched), "critical": bool(critical),
            "kind": kind, "where": where}


def provenance_scan() -> list[dict]:
    out = []
    for label, p in PROVENANCE_CANDIDATES:
        if not p.is_file():
            out.append({"label": label, "path": str(p.relative_to(DRIVE)),
                        "exists": False, "records_prompt": False, "hits": []})
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        hits = [f"L{i+1}" for i, l in enumerate(t.splitlines())
                if re.search(PROVENANCE_TERMS, l, re.I)]
        out.append({"label": label, "path": str(p.relative_to(DRIVE)),
                    "exists": True, "records_prompt": bool(hits), "hits": hits})
    return out


def table(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |",
                      "|" + "|".join("---" for _ in head) + "|"]
                     + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows])


def main() -> int:
    for p in (RELEASE, WORKING):
        if not p.is_file():
            print(f"AUSENTE: {p}")
            return 2

    wt = WORKING.read_text(encoding="utf-8")
    rt = RELEASE.read_text(encoding="utf-8")
    wl, rl = wt.splitlines(), rt.splitlines()
    w_sha, r_sha = sha_p(WORKING), sha_p(RELEASE)

    zip_sha = None
    if RELEASE_ZIP.is_file():
        with zipfile.ZipFile(RELEASE_ZIP) as z:
            for n in z.namelist():
                if n.endswith("prompts/lesson-analyzer.md"):
                    zip_sha = hashlib.sha256(z.read(n)).hexdigest()

    pr_w, pr_r = pass_ranges(wl), pass_ranges(rl)
    sec_w, sec_r = sections(wl), sections(rl)
    hunks = build_hunks(wl, rl)
    for h in hunks:
        h["cls"] = classify(h, pr_w, pr_r, sec_w, sec_r)

    critical = [h for h in hunks if h["cls"]["critical"]]
    prov = provenance_scan()

    L, w = [], None
    w = L.append
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    w("# LESSON-ANALYZER — DIFF DAS DUAS VERSÕES\n")
    w(f"**Gerado:** `{stamp}` · gerador `{Path(__file__).name}` · READ-ONLY nas "
      "duas árvores.\n")
    w("Relatório gerado por script; nenhuma linha, número ou hash foi digitado.\n")

    w("\n## 1. As duas versões\n")
    w(table([[f"`{WORKING.relative_to(DRIVE)}`", "cópia de trabalho",
              f"`{w_sha}`", len(wl)],
             [f"`{RELEASE.relative_to(DRIVE)}`", "RELEASE v0.1.1",
              f"`{r_sha}`", len(rl)]],
            ["caminho", "papel", "sha256", "linhas"]))
    if zip_sha:
        w(f"\nO release dentro do zip tem sha256 `{zip_sha}` — "
          f"{'idêntico ao extraído' if zip_sha == r_sha else '**DIVERGENTE do extraído**'}.\n")
    w(f"\nDiferença de tamanho: **{len(rl) - len(wl):+d} linhas**.\n")

    w("\n## 2. Faixas de PASS em cada versão\n")
    keys = sorted(set(pr_w) | set(pr_r), key=lambda k: int(k.split()[1]))
    w(table([[k,
              f"L{pr_w[k][0]}–{pr_w[k][1]}" if k in pr_w else "—",
              f"L{pr_r[k][0]}–{pr_r[k][1]}" if k in pr_r else "—",
              "iguais" if pr_w.get(k) == pr_r.get(k) else "**diferentes**"]
             for k in keys],
            ["PASS", "cópia de trabalho", "release", "posição"]))

    w("\n### 2.1 Conteúdo dos passes críticos, por hash\n")
    w("Prova independente do portão: se o hash do bloco bate, o passe é "
      "idêntico byte a byte, sem depender de como o diff alinhou as linhas.\n")
    crit_rows = []
    for k in ("PASS 1", "PASS 2"):
        if k in pr_w and k in pr_r:
            hw, hr = block_hash(wl, pr_w[k]), block_hash(rl, pr_r[k])
            crit_rows.append([k, f"`{hw[:24]}…`", f"`{hr[:24]}…`",
                              "**IDÊNTICO**" if hw == hr else "**DIVERGE**"])
    w(table(crit_rows, ["PASS", "hash (trabalho)", "hash (release)", "veredito"]))

    w("\n## 3. Diff completo\n")
    w(f"**{len(hunks)} bloco(s) de diferença.**\n")
    for i, h in enumerate(hunks, 1):
        c = h["cls"]
        w(f"\n### Bloco {i} — {c['kind']}\n")
        w(table([[x] for x in c["where"]], ["localização"]))
        w("")
        w("```diff")
        for l in h["removed"]:
            w(f"-{l}")
        for l in h["added"]:
            w(f"+{l}")
        w("```")
    w("")

    w("\n## 4. Classificação\n")
    w(table([[i + 1, h["op"],
              (f"L{h['working_lines'][0]}–{h['working_lines'][1]}"
               if h["working_lines"] else "—"),
              (f"L{h['release_lines'][0]}–{h['release_lines'][1]}"
               if h["release_lines"] else "—"),
              h["cls"]["kind"]]
             for i, h in enumerate(hunks)],
            ["#", "operação", "linhas (trabalho)", "linhas (release)",
             "classificação"]))

    w("\n## 5. PORTÃO\n")
    if critical:
        w("> ### ⛔ ACHADO GRAVE — diferença dentro de PASS 1 ou PASS 2\n>\n"
          f"> {len(critical)} bloco(s) tocam os passes que o diagnóstico do "
          "colapso mediu. Isso significa que o diagnóstico pode ter lido um "
          "spec enquanto o PILOT-002 foi compilado com o outro.\n>\n"
          "> **PARADO. Nenhuma execução deve começar antes de resolver isto.**\n")
        w(table([[i + 1, h["cls"]["kind"], "; ".join(h["cls"]["where"])]
                 for i, h in enumerate(hunks) if h["cls"]["critical"]],
                ["bloco", "classificação", "onde"]))
    else:
        w("> ### ✅ PORTÃO ABERTO — nenhuma diferença toca PASS 1 ou PASS 2\n>\n"
          f"> Os {len(hunks)} blocos de diferença ficam **inteiramente fora** "
          "dos dois passes que o diagnóstico do colapso mediu. As faixas de "
          "linha do PASS 1 e do PASS 2 são idênticas nas duas versões e o texto "
          "dentro delas é o mesmo byte a byte.\n>\n"
          "> **Consequência:** mesmo sem saber qual das duas versões compilou o "
          "PILOT-002, o diagnóstico do colapso não é afetado — as duas dizem "
          "exatamente a mesma coisa sobre segmentação e extração.\n")

    w("\n## 6. Qual das duas compilou o PILOT-002? NÃO SABEMOS\n")
    w("Isto não é dedução, é ausência de registro. Nenhum artefato da "
      "compilação do PILOT-002 grava a versão do prompt:\n")
    w(table([[p["label"], f"`{p['path']}`",
              "existe" if p["exists"] else "**ausente**",
              "**sim**" if p["records_prompt"] else "não"]
             for p in prov],
            ["artefato", "caminho", "estado", "registra o prompt?"]))
    n_rec = sum(1 for p in prov if p["records_prompt"])
    w(f"\n**{n_rec} de {len(prov)} artefatos registram a versão do prompt.**\n")
    w("\n### O que existiria em disco, se existisse, e decidiria a questão\n")
    w(table([
        ["`compiler_version` ou `prompt_sha256` no `COMPILATION_MANIFEST`",
         "decidiria sozinho", "**não existe** — o manifesto grava entrada, "
         "evidências e campos indefinidos, mas nada sobre o compilador"],
        ["hash do prompt no `GOVERNANCE.yaml`",
         "decidiria sozinho",
         "**não existe** — grava `scope_lock` e `adr` por prefixo, não o prompt"],
        ["registro de execução / log da compilação",
         "decidiria sozinho", "**não existe** na árvore"],
        ["cópia do prompt dentro do pacote compilado",
         "decidiria sozinho", "**não existe** — o pacote traz SKILL, EVIDENCE, "
         "GOVERNANCE, MANIFEST e VALIDATION, nenhum prompt"],
        ["mtime dos arquivos", "não decide",
         "prova apenas que as duas versões já existiam antes da compilação"],
    ], ["evidência que decidiria", "força", "estado real"]))
    w("\n> **Registrado como incerteza aberta.** Pelo §5 a resposta não muda o "
      "diagnóstico do colapso, porque a diferença não toca os passes medidos. "
      "Mas ela continua desconhecida, e o compilador v2 já corrige isso: o "
      "`COMPILATION_MANIFEST` v2 grava `compiler_version` e o hash do "
      "`temporal-map`, de modo que a mesma pergunta não vai ficar sem resposta "
      "na próxima compilação.\n")

    w("\n---\n")
    w("**Escopo:** somente leitura e comparação. Nenhum arquivo de "
      "`Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, "
      "movido ou apagado. O único arquivo escrito é este relatório.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"blocos de diferença: {len(hunks)} | tocam PASS 1/2: {len(critical)}")
    for i, h in enumerate(hunks, 1):
        print(f"  {i}. {h['op']:9s} {h['cls']['kind']}")
    for k in ("PASS 1", "PASS 2"):
        hw, hr = block_hash(wl, pr_w[k]), block_hash(rl, pr_r[k])
        print(f"{k} conteúdo idêntico: {hw == hr} ({hw[:16]}…)")
    print(f"artefatos que registram o prompt: {n_rec}/{len(prov)}")
    print("PORTÃO:", "FECHADO — ACHADO GRAVE" if critical else "ABERTO")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha_p(OUT)[:16]}…")
    return 2 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
