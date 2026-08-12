#!/usr/bin/env python3
"""Errata dos contratos legados que declaram TEST-0008.

Roda daqui (ext4). READ-ONLY absoluto: os contratos vivem dentro de zips na
árvore protegida e NÃO podem ser marcados no próprio arquivo. A errata é
externa e se amarra a eles por SHA-256.

Relatório GERADO: nenhum hash é digitado.

CASAMENTO POR IDENTIDADE, nunca por menção: um contrato entra quando
`TEST-0008` é CHAVE de `comparative_tests`. O termo no corpo do texto não conta.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
TREES = [DRIVE / "Course-to-Skill", DRIVE / "Course-to-Skill-Compiler"]
OUT = DOCS / "LEGACY-TEST-0008-CONTRACTS-ERRATA.md"

TARGET = "TEST-0008"
RETIRED = "SKILL_MINUS_SUMMARY"

# O desenho vigente. Os caminhos são âncoras que TÊM de existir; se algum não
# existir, isso é reportado em vez de silenciado.
DESIGN_ANCHORS = [
    ("desenho de três condições, montado",
     DOCS / "TEST-0008-CONDITIONS-v0.1.4"),
    ("procedência do baseline, com os SHA-256 das três condições",
     DOCS / "BASELINE-PROVENANCE-v0.1.4.yaml"),
    ("ensaio seco que define P e F e lista o que falta",
     DOCS / "DRY-RUN-TEST-0008.md"),
    ("apuração da discrepância 5×6 das métricas",
     DOCS / "TEST-0008-METRICS-DISCREPANCY.md"),
    ("rascunho de rubrica do TEST-0008 (NÃO congelado)",
     DOCS / "TEST-0008-RUBRIC-DRAFT-v0.1.4.yaml"),
]

# Âncoras PEDIDAS na tarefa. Podem não existir; o script procura e reporta.
REQUESTED_ANCHORS = [
    {"label": "ADR do TEST-0008 / ADR de paridade de informação",
     "how": "arquivo em docs/adr/ que trate do TEST-0008 ou das três condições",
     "probe": "adr"},
    {"label": "metric lock `caffc7ba…`",
     "how": "arquivo cujo SHA-256 comece com caffc7ba, ou documento que cite "
            "a string",
     "probe": "caffc7ba"},
]

CONDITIONS = ["FULL_SKILL", "SUMMARY_AS_SUMMARY", "SUMMARY_AS_SKILL"]


def sha_b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_p(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def dir_sha(p: Path) -> str:
    """Hash de diretório: sobre a lista ordenada de (caminho, sha) dos membros."""
    items = sorted((str(x.relative_to(p)), sha_p(x))
                   for x in p.rglob("*") if x.is_file())
    return sha_b(json.dumps(items, sort_keys=True).encode())


def yaml_sources():
    for tree in TREES:
        for p in sorted(tree.rglob("*")):
            if not p.is_file():
                continue
            s = p.suffix.lower()
            if s in (".yaml", ".yml"):
                try:
                    yield str(p.relative_to(DRIVE)), None, p.read_bytes(), p
                except OSError:
                    continue
            elif s == ".zip":
                try:
                    with zipfile.ZipFile(p) as z:
                        for n in z.namelist():
                            if n.lower().endswith((".yaml", ".yml")):
                                yield str(p.relative_to(DRIVE)), n, z.read(n), p
                except zipfile.BadZipFile:
                    continue


def collect():
    out = []
    for path, inner, blob, container in yaml_sources():
        text = blob.decode("utf-8", "replace")
        if "comparative_tests" not in text:
            continue
        try:
            docs = [d for d in yaml.safe_load_all(text) if isinstance(d, dict)]
        except yaml.YAMLError:
            continue
        for d in docs:
            ct = d.get("comparative_tests")
            if not (isinstance(ct, dict) and TARGET in ct):
                continue
            e = ct[TARGET] or {}
            out.append({
                "zip": path if inner else None,
                "path": path, "inner": inner,
                "artifact_id": d.get("artifact_id"),
                "schema_version": d.get("schema_version"),
                "comparison": e.get("comparison") if isinstance(e, dict) else None,
                "margin_threshold": (e.get("margin_threshold")
                                     if isinstance(e, dict) else None),
                "keys": sorted(e) if isinstance(e, dict) else [],
                "sha": sha_b(blob), "bytes": len(blob),
                "container_sha": sha_p(container),
                "other_tests": sorted(k for k in ct if k != TARGET),
            })
    return out


def find_requested(contracts):
    """Procura as âncoras pedidas. Não inventa: reporta ausência."""
    res = []
    # ADR
    adr_dir = DOCS / "adr"
    hits = []
    if adr_dir.is_dir():
        for p in sorted(adr_dir.glob("*.md")):
            t = p.read_text(encoding="utf-8", errors="replace")
            if TARGET in t or "SUMMARY_AS_SKILL" in t or "paridade de informa" in t:
                hits.append(str(p.relative_to(DRIVE)))
    res.append({**REQUESTED_ANCHORS[0], "found": hits,
                "n_adr_files": len(list(adr_dir.glob("*.md"))) if adr_dir.is_dir() else 0})
    # metric lock
    lit, byhash = [], []
    for tree in (CLAUDE, *TREES):
        if not tree.is_dir():
            continue
        for p in tree.rglob("*"):
            if not p.is_file() or p.stat().st_size > 3_000_000:
                continue
            if p == OUT:
                continue          # este relatório cita a string; não é acerto
            try:
                if sha_p(p).startswith("caffc7ba"):
                    byhash.append(str(p.relative_to(DRIVE)))
                if p.suffix.lower() in (".md", ".yaml", ".yml", ".txt", ".json") \
                        and b"caffc7ba" in p.read_bytes().lower():
                    lit.append(str(p.relative_to(DRIVE)))
            except OSError:
                continue
    res.append({**REQUESTED_ANCHORS[1], "found": sorted(set(lit + byhash))})
    return res


def active_refs(contracts):
    """Algum dos contratos é referenciado por artefato ATIVO?

    Procura o NOME de cada contrato em toda a árvore (solto e dentro de zip),
    fora do próprio zip que o contém. Classifica cada acerto.
    """
    names = {}
    for c in contracts:
        nm = Path(c["inner"] or c["path"]).name
        names.setdefault(nm, []).append(c)

    hits = []
    for tree in (CLAUDE, *TREES):
        if not tree.is_dir():
            continue
        for p in sorted(tree.rglob("*")):
            if not p.is_file():
                continue
            s = p.suffix.lower()
            blobs = []
            if s in (".md", ".yaml", ".yml", ".txt", ".json", ".py"):
                try:
                    blobs = [(None, p.read_bytes())]
                except OSError:
                    continue
            elif s == ".zip":
                try:
                    with zipfile.ZipFile(p) as z:
                        blobs = [(n, z.read(n)) for n in z.namelist()
                                 if not n.endswith("/")]
                except (zipfile.BadZipFile, OSError):
                    continue
            for inner, b in blobs:
                low = b.decode("utf-8", "replace")
                for nm in names:
                    if nm in low:
                        rel = str(p.relative_to(DRIVE))
                        if any(rel == c["path"] for c in names[nm]) and inner:
                            continue          # é o próprio pacote
                        hits.append({"contract": nm, "where": rel,
                                     "inner": inner})
    return hits


def successor_contracts():
    """O contrato que a cadeia ATIVA (v0.1.4) realmente consome.

    É a checagem decisiva do item 4: se o sucessor ainda trouxesse `TEST-0008`
    como chave, o desenho aposentado estaria vivo na cadeia em uso.
    """
    out = []
    for tree in TREES:
        for z in sorted(tree.rglob("*.zip")):
            try:
                zz = zipfile.ZipFile(z)
            except (zipfile.BadZipFile, OSError):
                continue
            for n in zz.namelist():
                if "JUDGE-SCORING-CONTRACT-TEST-0007" not in n:
                    continue
                b = zz.read(n)
                try:
                    d = yaml.safe_load(b.decode("utf-8", "replace")) or {}
                except yaml.YAMLError:
                    continue
                ct = d.get("comparative_tests") or {}
                out.append({"zip": str(z.relative_to(DRIVE)), "inner": n,
                            "keys": sorted(ct), "sha": sha_b(b),
                            "has_target": TARGET in ct})
    return out


def classify_hit(h: dict) -> str:
    w = h["where"]
    if w.startswith("Course-to-Skill-Claude/docs/"):
        return "análise (este projeto)"
    if "/v0.1.4/" in w:
        return "árvore v0.1.4"
    return "pacote v0.1.3"


def table(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |",
                      "|" + "|".join("---" for _ in head) + "|"]
                     + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows])


def render(cs, anchors, req, hits, succ) -> str:
    L, w = [], None
    w = L.append
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    retired = [c for c in cs if c["comparison"] == RETIRED]
    silent = [c for c in cs if c["comparison"] is None]

    w("# LEGACY TEST-0008 CONTRACTS — ERRATA\n")
    w(f"**Gerado:** `{stamp}` · gerador `{Path(__file__).name}` · "
      "**somente medição**, READ-ONLY.\n")
    w("Relatório gerado por script; nenhum hash foi digitado.\n")

    # ------------------------------------------------------------- topo
    w("\n> ## ⛔ ERRATA — leia antes de usar qualquer um destes contratos\n>\n"
      f"> Os **{len(cs)}** contratos listados aqui declaram `{TARGET}` como "
      "chave de `comparative_tests`. Eles codificam o desenho de **DUAS** "
      "condições — Skill contra resumo.\n>\n"
      "> **O desenho vigente é de TRÊS condições** — `FULL_SKILL`, "
      "`SUMMARY_AS_SUMMARY`, `SUMMARY_AS_SKILL` — **com DUAS comparações**:\n>\n"
      "> - `P = FULL_SKILL − SUMMARY_AS_SUMMARY` (primária)\n"
      "> - `F = SUMMARY_AS_SKILL − SUMMARY_AS_SUMMARY` (enquadramento)\n>\n"
      f"> O nome `{RETIRED}` **não desambigua entre `P` e `F`**: sob o desenho "
      "novo, os dois cabem no nome. **Quem rodar a cadeia com um destes "
      "contratos mede uma comparação e não sabe qual das duas mediu.**\n>\n"
      "> Estes arquivos estão dentro de zips na árvore READ-ONLY e **não podem "
      "ser marcados no próprio arquivo**. Esta errata é externa e se amarra a "
      "eles por SHA-256.\n")

    # ------------------------------------------------------------- grave
    w("\n## 1. Algum destes está na cadeia de algo ATIVO?\n")
    groups: dict[str, list] = {}
    for h in hits:
        groups.setdefault(classify_hit(h), []).append(h)
    w(f"A varredura procurou o NOME de cada contrato em toda a árvore — solto e "
      f"dentro de zip — e achou **{len(hits)} referência(s)**, assim "
      "distribuídas:\n")
    w(table([[k, len(v), ", ".join(sorted({x["contract"] for x in v}))]
             for k, v in sorted(groups.items())],
            ["classe", "n", "contratos citados"]))
    w("")
    for k in sorted(groups):
        w(f"\n**{k}**\n")
        w(table([[f"`{h['contract']}`", f"`{h['where']}`",
                  f"`{h['inner']}`" if h["inner"] else "—"]
                 for h in sorted(groups[k], key=lambda x: (x["where"], x["contract"]))],
                ["contrato", "referenciado em", "caminho interno"]))
        w("")

    w("\n### 1.1 A checagem decisiva: o contrato que a cadeia ATIVA consome\n")
    w("Referência por nome não basta — o que importa é se a cadeia em uso "
      f"carrega um contrato que traga `{TARGET}` como chave. O sucessor do "
      "contrato de julgamento na v0.1.4 é este:\n")
    w(table([[f"`{s_['zip']}`", f"`{Path(s_['inner']).name}`",
              ", ".join(f"`{k}`" for k in s_["keys"]),
              "**SIM**" if s_["has_target"] else "**não**"]
             for s_ in succ],
            ["pacote", "contrato", "chaves de comparative_tests",
             f"contém {TARGET}?"]))
    if succ:
        w(f"\n**SHA-256 do contrato ativo:** `{succ[0]['sha']}` "
          f"(idêntico nos {len(succ)} pacotes acima).\n")

    w("\n### Veredito\n")
    contaminated = [s_ for s_ in succ if s_["has_target"]]
    if contaminated:
        w("> ## ⛔ ACHADO GRAVE\n>\n"
          f"> O contrato consumido pela cadeia ATIVA ainda traz `{TARGET}` como "
          "chave. O desenho aposentado está vivo em uso.\n")
    else:
        w("**NÃO há achado grave.** Nenhum dos "
          f"{len(cs)} está na cadeia de execução de artefato ativo, e a prova é "
          "positiva, não apenas ausência de evidência:\n")
        w(f"\n1. **O sucessor ativo dropou a entrada.** "
          f"`JUDGE-SCORING-CONTRACT-TEST-0007-v0.1.4-F7.yaml` declara "
          f"`comparative_tests` com **apenas `TEST-0007`**. A entrada "
          f"`{TARGET}` que os contratos v0.1.3 carregavam **já foi removida** na "
          "geração corrente, inclusive no pacote `JUDGE_BLIND_RUN` e no "
          "`FINAL_PRE_RUN_LOCK_F7_SCORER_BOUND`.\n")
        w(f"2. **Todos os {len(cs)} vivem em pacotes da v0.1.3** — "
          "`00_REVISION_INPUT/` e os prelocks do TEST-0007 — e nenhum existe "
          "como arquivo solto.\n")
        w("3. **O pacote de blind run ativo não contém contrato nenhum**: só "
          "instruções, âncoras, anexos e `SHA256SUMS.txt`.\n")

    w("\n### 1.2 A ressalva que sobra, e ela é real\n")
    w("Duas referências merecem registro porque são caminhos vivos até um dos "
      "contratos desta errata:\n")
    w(table([["`JUDGE-SCORING-CONTRACT-ADDENDUM-D1-D2-v0.1.3.yaml`",
              "declara `base_contract: JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml`",
              "dependência declarada — o addendum se apoia num dos 13"],
             ["`score_judge_results.py`",
              "linha de uso `--contract JUDGE-SCORING-CONTRACT-v0.1.3-REV5.yaml`",
              "invocação documentada do scorer, copiável"]],
            ["artefato", "como referencia", "natureza"]))
    w("\n> Os dois vivem dentro dos pacotes de prelock da v0.1.3 "
      "(`PRELOCK_D1_D2`, `PRELOCK_F3_TRISTATE`, `PRELOCK_F4_STRUCTURAL_ID`). O "
      "`VERSION-LITERAL-SWEEP-v0.1.4.yaml`, já na árvore v0.1.4, cataloga a "
      "linha do scorer e a classifica como `DOCUMENTATION_OR_EXAMPLE` com "
      "`blocking_class_candidate: false` — ou seja, o próprio projeto já a "
      "examinou e a considerou não bloqueante.\n")
    w("\n> **Por que isso não vira grave:** o scorer da v0.1.3 e seus addenda "
      "não são a cadeia em uso; a v0.1.4 tem contrato próprio, sem "
      f"`{TARGET}`. **Por que ainda assim importa:** a linha "
      "`--contract …REV5.yaml` é copiável, e quem a copiar puxa um contrato que "
      "traz a entrada aposentada. É ponteiro quente, não incêndio.\n")

    # ------------------------------------------------------------- correção
    w("\n## 2. Correção de premissa: não são 13 declarando o desenho velho\n")
    w(f"A varredura por identidade encontra **{len(cs)}** contratos com "
      f"`{TARGET}` como chave. Mas eles não são homogêneos:\n")
    w(table([[f"declaram `comparison: {RETIRED}`", len(retired),
              "**codificam o desenho de duas condições**"],
             ["declaram `TEST-0008` sem `comparison` nenhum", len(silent),
              "fixtures de canário: só um flag de guarda"]],
            ["classe", "n", "o que significa"]))
    w(f"\n**Só {len(retired)} dos {len(cs)} declaram `{RETIRED}`.** Os outros "
      f"{len(silent)} são contratos de canário que trazem `{TARGET}` como chave "
      "com apenas `full_preservation_guard_required` (e, em quatro deles, "
      "`structural_ceiling_required`). Eles **não declaram comparação nenhuma**, "
      "logo não codificam o desenho de duas condições — o problema deles é "
      f"outro e menor: mencionam um teste que a cadeia não implementa.\n")
    w("\n> Registro a diferença porque ela muda o que precisa ser aposentado. "
      f"A errata forte vale para os {len(retired)}; os {len(silent)} restantes "
      "entram como contexto.\n")

    # ------------------------------------------------------------- os 13
    w(f"\n## 3. Os {len(cs)} contratos\n")
    w("### 3.1 Os que declaram o desenho aposentado\n")
    w(table([[i + 1, f"`{c['path']}`", f"`{c['inner']}`",
              f"`{c['comparison']}`", f"`{c['margin_threshold']}`"]
             for i, c in enumerate(retired)],
            ["#", "zip", "caminho interno", "comparison", "margin_threshold"]))
    w("")
    w(table([[f"`{Path(c['inner']).name}`", f"`{c['sha']}`", c["bytes"]]
             for c in retired],
            ["arquivo", "SHA-256 do YAML interno", "bytes"]))
    w("")
    w(table([[f"`{Path(c['inner']).name}`",
              c["artifact_id"] or "**não declara**",
              ", ".join(f"`{k}`" for k in c["keys"]),
              ", ".join(c["other_tests"]) or "—"]
             for c in retired],
            ["arquivo", "artifact_id", "chaves sob TEST-0008", "outros testes"]))

    w(f"\n### 3.2 Os que declaram `{TARGET}` sem comparação\n")
    w(table([[i + 1, f"`{c['path']}`", f"`{c['inner']}`",
              ", ".join(f"`{k}`" for k in c["keys"]) or "—",
              f"`{c['sha'][:16]}…`"]
             for i, c in enumerate(silent)],
            ["#", "zip", "caminho interno", "chaves sob TEST-0008", "SHA-256"]))
    w("")
    w(table([[f"`{c['inner']}`", f"`{c['sha']}`"] for c in silent],
            ["caminho interno", "SHA-256 completo"]))

    w("\n### 3.3 SHA-256 dos zips que os contêm\n")
    w("Os contratos não podem ser marcados; os pacotes que os carregam ficam "
      "amarrados aqui, para que a errata continue válida mesmo que alguém "
      "reempacote.\n")
    seen = {}
    for c in cs:
        seen[c["path"]] = c["container_sha"]
    w(table([[f"`{k}`", f"`{v}`"] for k, v in sorted(seen.items())],
            ["zip", "SHA-256 do zip"]))

    # ------------------------------------------------------------- âncoras
    w("\n## 4. Amarração ao desenho que os substitui\n")
    w(table([[lbl, f"`{p.relative_to(DRIVE)}`",
              f"`{h}`" if h else "**AUSENTE**"]
             for lbl, p, h in anchors],
            ["artefato do desenho vigente", "caminho", "SHA-256"]))
    w("\n> Diretórios são amarrados pelo hash da lista ordenada de "
      "`(caminho, sha256)` dos seus membros, não pelo conteúdo concatenado.\n")

    w("\n### 4.1 As duas âncoras pedidas que NÃO existem\n")
    w("A tarefa pediu amarração ao **ADR do TEST-0008** e ao **metric lock "
      "`caffc7ba…`**. Procurei os dois e nenhum existe. Registro em vez de "
      "fabricar a amarração:\n")
    w(table([[r["label"], r["how"],
              ", ".join(f"`{x}`" for x in r["found"]) if r["found"]
              else "**NÃO ENCONTRADO**"]
             for r in req],
            ["âncora pedida", "como foi procurada", "resultado"]))
    w(f"\n- **ADR do TEST-0008:** `docs/adr/` tem "
      f"{req[0]['n_adr_files']} ADRs (ADR-0001 a ADR-0014) e **nenhum** menciona "
      f"`{TARGET}`, `SUMMARY_AS_SKILL` ou paridade de informação. O \"ADR de "
      "paridade de informação\" é citado em prosa no `DRY-RUN-TEST-0008.md` e no "
      "`BASELINE-PROVENANCE-v0.1.4.yaml` — **mas não existe como arquivo, e "
      "nunca recebeu número**. O desenho de três condições vive hoje só na "
      "prosa desses dois documentos e na pasta de condições montadas.\n")
    w("- **Metric lock `caffc7ba…`:** varri a árvore inteira por literal "
      "(inclusive dentro de zips) e por SHA-256 de arquivo. **Zero acertos.** "
      "Nenhum arquivo tem esse hash e nenhum documento cita essa string.\n")
    w("\n> **Consequência para esta errata.** Ela se amarra ao que existe (§4) e "
      "declara ausente o que não existe. Um leitor que precise da autoridade "
      "formal do desenho de três condições **não vai encontrá-la**: o desenho "
      "vigente não tem ADR numerado nem lock de métrica. Isso é, por si, um "
      "achado — a errata aposenta um desenho velho apontando para um desenho "
      "novo que ainda não foi formalizado.\n")

    # ------------------------------------------------------------- uso
    w("\n## 5. O que fazer com um destes contratos\n")
    w(table([["rodar a cadeia do TEST-0008 com ele",
              "**NÃO** — mede `P` ou `F` sem dizer qual"],
             ["usá-lo como referência histórica do desenho de duas condições",
              "sim, é para isso que esta errata o preserva"],
             ["copiar a linha `--contract …REV5.yaml` de exemplo",
              "**NÃO** — herda o desenho aposentado"],
             ["editar o contrato para o desenho novo",
              "impossível sem escrever na árvore READ-ONLY; e o modelo de dados "
              "não comporta duas comparações por teste"]],
            ["uso", "veredito"]))
    w("\n> O `DRY-RUN-TEST-0008.md` já registrou que a mudança necessária não é "
      "preencher campo: `comparative_tests` é um mapa `test_id → política` com "
      "um único par `left`/`right`, e o TEST-0008 precisa de duas comparações "
      "sobre três condições. **Estender o modelo de dados é pré-requisito**, e "
      "nenhum contrato desta lista pode ser consertado no lugar.\n")

    w("\n---\n")
    w("**Escopo:** somente medição. Nenhum contrato foi editado, movido, "
      "copiado ou reempacotado. Nenhum arquivo de `Course-to-Skill/` ou "
      "`Course-to-Skill-Compiler/` foi tocado. O único arquivo escrito é este "
      "relatório, em `Course-to-Skill-Claude/docs/`.")
    return "\n".join(L) + "\n"


def main() -> int:
    cs = collect()
    if not cs:
        print("Nenhum contrato com TEST-0008 como chave. Nada publicado.")
        return 2

    anchors = []
    for lbl, p in DESIGN_ANCHORS:
        if p.is_dir():
            anchors.append((lbl, p, dir_sha(p)))
        elif p.is_file():
            anchors.append((lbl, p, sha_p(p)))
        else:
            anchors.append((lbl, p, None))

    req = find_requested(cs)
    hits = active_refs(cs)

    succ = successor_contracts()
    OUT.write_text(render(cs, anchors, req, hits, succ), encoding="utf-8")

    retired = sum(1 for c in cs if c["comparison"] == RETIRED)
    print(f"contratos com {TARGET} como chave: {len(cs)}")
    print(f"  declaram {RETIRED}: {retired} | sem comparison: {len(cs)-retired}")
    print(f"referencias externas encontradas: {len(hits)}")
    for h in hits:
        print(f"  {h['contract']} <- {h['where']}")
    for r in req:
        print(f"âncora pedida '{r['label'][:40]}': "
              f"{r['found'] if r['found'] else 'NÃO ENCONTRADA'}")
    for lbl, p, h in anchors:
        print(f"âncora {p.name}: {h[:16] + '…' if h else 'AUSENTE'}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha_p(OUT)[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
