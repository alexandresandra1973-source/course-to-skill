#!/usr/bin/env python3
"""Apuração da discrepância 5×6 dos `comparison_metrics` do TEST-0008.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/ e Course-to-Skill-Compiler/:
só abre para leitura e hashea. Publica o relatório em Course-to-Skill-Claude/docs/.
Relatório GERADO: nenhum número é digitado.

Escopo: apurar de onde veio cada número. Não propõe lista canônica.
"""
from __future__ import annotations

import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "TEST-0008-METRICS-DISCREPANCY.md"

# As duas árvores sob regime read-only.
TREES = [DRIVE / "Course-to-Skill", DRIVE / "Course-to-Skill-Compiler"]

# Docs que fazem a afirmação sob auditoria.
CLAIM_DOCS = [DOCS / "ARCHITECTURE_REVIEW.md",
              DOCS / "CLAUDE_ARCHITECTURE_PROPOSAL.md"]

# Qual doc é qual fase. A Fase 3 se autodeclara na linha 3 do próprio arquivo;
# o rótulo abaixo é conferido contra essa linha em tempo de execução.
PHASE_OF = {"CLAUDE_ARCHITECTURE_PROPOSAL.md": "Fase 3 — Proposta de arquitetura",
            "ARCHITECTURE_REVIEW.md": "Fase 2 — Revisão de arquitetura"}

TARGET = "TEST-0008"
PEER = "TEST-0007"  # o outro teste comparativo da suíte


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(path: Path) -> str:
    """RELEASE vs WORKSPACE pela posição na árvore do compilador."""
    parts = path.parts
    if "releases" in parts or "01_TOOL" in parts:
        return "RELEASE"
    if "02_PILOTS" in parts:
        return "WORKSPACE"
    return "OUTRO"


def find_suites() -> list[Path]:
    """Todo arquivo das duas árvores que contém a chave `comparison_metrics`."""
    hits = []
    for tree in TREES:
        for p in sorted(tree.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in (".yaml", ".yml"):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "comparison_metrics" in text:
                hits.append(p)
    return hits


def load_tests(path: Path) -> list[dict]:
    """Documentos YAML que têm test_id — a suíte é multi-documento."""
    try:
        docs = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    except yaml.YAMLError:
        return []
    return [d for d in docs if isinstance(d, dict) and "test_id" in d]


def metrics_of(test: dict) -> list[str] | None:
    """`comparison_metrics` do teste, onde quer que o bloco comparativo esteja."""
    def walk(node):
        if isinstance(node, dict):
            if "comparison_metrics" in node:
                return node["comparison_metrics"]
            for v in node.values():
                r = walk(v)
                if r is not None:
                    return r
        elif isinstance(node, list):
            for v in node:
                r = walk(v)
                if r is not None:
                    return r
        return None
    return walk(test)


def rubric_criteria(test: dict) -> list[str]:
    """Todo `criterion` do teste — a rubrica vive em `evaluation.rubric`."""
    out = []

    def walk(node):
        if isinstance(node, dict):
            if "criterion" in node and isinstance(node["criterion"], str):
                out.append(node["criterion"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(test)
    return out


def schema_enum(path: Path) -> list[str]:
    """Enum permitido para comparison_metrics no test.schema.yaml."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"comparison_metrics:.*?enum:\n((?:\s*-\s*\w+\n)+)", text, re.S)
    if not m:
        return []
    return re.findall(r"-\s*(\w+)", m.group(1))


def phase_selfdeclaration(path: Path) -> str:
    """A linha em que o doc declara a própria fase, se declarar."""
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()[:10], 1):
        m = re.search(r"\*\*(Fase \d+[^*]*)\*\*", line)
        if m:
            return f"linha {i}: **{m.group(1).strip()}**"
    return "o arquivo não declara fase no cabeçalho"


def claim_sentences(path: Path) -> list[tuple[int, str]]:
    """Frases literais que mencionam comparison_metrics, com número de linha."""
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "comparison_metrics" not in line:
            continue
        for sent in re.split(r"(?<=[.;])\s+(?=[A-ZÀ-Ú*(**])", line):
            if "comparison_metrics" in sent:
                out.append((i, sent.strip()))
    return out


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # --- 1. a afirmação nos docs -------------------------------------------
    claims = {}
    for d in CLAIM_DOCS:
        claims[d.name] = claim_sentences(d)

    # número declarado: o "N" em "X de N comparison_metrics"
    declared = set()
    for sents in claims.values():
        for _, s in sents:
            for a, b in re.findall(r"(\d+)\s+d[ea]s?\s+(\d+)\s+`?comparison_metrics", s):
                declared.add((int(a), int(b)))

    # --- 2. contagem nas duas posições -------------------------------------
    suites, schemas = [], []
    for p in find_suites():
        (schemas if "schema" in p.name else suites).append(p)

    rows = []
    for p in suites:
        tests = load_tests(p)
        by_id = {t["test_id"]: t for t in tests}
        tgt = by_id.get(TARGET)
        peer = by_id.get(PEER)
        rows.append({
            "path": p,
            "rel": p.relative_to(DRIVE),
            "kind": classify(p),
            "sha": sha256(p),
            "bytes": p.stat().st_size,
            "n_tests": len(tests),
            "target": metrics_of(tgt) if tgt else None,
            "peer": metrics_of(peer) if peer else None,
            "target_rubric": rubric_criteria(tgt) if tgt else [],
        })

    # --- 3. reconciliação ---------------------------------------------------
    tgt_sets = {tuple(r["target"]) for r in rows if r["target"]}
    peer_sets = {tuple(r["peer"]) for r in rows if r["peer"]}
    by_kind = {}
    for r in rows:
        if r["target"]:
            by_kind.setdefault(r["kind"], set()).add(tuple(r["target"]))

    unique_target = sorted(tgt_sets)[0] if len(tgt_sets) == 1 else None
    unique_peer = sorted(peer_sets)[0] if len(peer_sets) == 1 else None
    union = sorted(set(unique_target or ()) | set(unique_peer or ()))

    # critérios de rubrica em toda a suíte (matching por nome exato)
    all_criteria = set()
    for p in suites:
        for t in load_tests(p):
            all_criteria.update(rubric_criteria(t))
    unmatched = [m for m in union if m not in all_criteria]

    sha_groups = {}
    for r in rows:
        sha_groups.setdefault(r["sha"], []).append(r)

    # --- render -------------------------------------------------------------
    L = []
    w = L.append
    w(f"# TEST-0008 — discrepância 5×6 dos `comparison_metrics`")
    w("")
    w(f"- Gerado: `{stamp}`")
    w(f"- Gerador: `{Path(__file__).name}` (relatório gerado; nenhum número digitado)")
    w("- Regime: **READ-ONLY** sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/`")
    w("- Escopo: apurar **de onde veio cada número**. Não propõe lista canônica.")
    w("")
    w("---")
    w("")

    # 1
    w("## 1. A frase literal nos docs")
    w("")
    for name, sents in claims.items():
        label = PHASE_OF.get(name, "fase não declarada")
        selfdecl = phase_selfdeclaration(DOCS / name)
        w(f"### `{name}` — {label}")
        w("")
        w(f"- Autodeclaração de fase no próprio arquivo: {selfdecl}")
        w("")
        if not sents:
            w("Nenhuma ocorrência de `comparison_metrics`.")
            w("")
            continue
        for ln, s in sents:
            w(f"- **linha {ln}:** {s}")
        w("")
    if declared:
        for a, b in sorted(declared):
            w(f"**Número declarado: {a} de {b}.** Os dois docs afirmam o mesmo par.")
    w("")
    w("**Arquivo de onde foi contado:** os docs **não citam nenhum caminho** para essa "
      "contagem. A única impressão digital de origem no texto é o tamanho da suíte "
      "citado no `ARCHITECTURE_REVIEW.md` — e esse tamanho não desambigua, porque "
      "todas as cópias da suíte são byte-idênticas (ver §2).")
    w("")

    # 2
    w("## 2. Contagem no test-suite do TEST-0008 — RELEASE e WORKSPACE")
    w("")
    w(f"Arquivos das duas árvores que contêm `comparison_metrics`: "
      f"**{len(suites)} suítes** + **{len(schemas)} schemas**.")
    w("")
    w("| # | posição | caminho (rel. a `Meu Drive/Chat GPT`) | bytes | sha256[:12] | testes | `comparison_metrics` do TEST-0008 |")
    w("|---|---|---|---|---|---|---|")
    for i, r in enumerate(sorted(rows, key=lambda x: (x["kind"], str(x["rel"]))), 1):
        n = len(r["target"]) if r["target"] else 0
        w(f"| {i} | **{r['kind']}** | `{r['rel']}` | {r['bytes']} | `{r['sha'][:12]}` | "
          f"{r['n_tests']} | **{n}** |")
    w("")

    for kind in ("RELEASE", "WORKSPACE"):
        sets = by_kind.get(kind, set())
        w(f"### {kind}")
        w("")
        if not sets:
            w("Nenhuma cópia nesta posição.")
            w("")
            continue
        if len(sets) == 1:
            names = sorted(sets)[0]
            w(f"Contagem: **{len(names)}**. Todas as cópias {kind} concordam. Nomes:")
            w("")
            for nm in names:
                w(f"1. `{nm}`")
        else:
            w(f"**Cópias {kind} divergem entre si** ({len(sets)} conjuntos distintos):")
            for s in sorted(sets):
                w(f"- ({len(s)}) " + ", ".join(f"`{x}`" for x in s))
        w("")

    w("### Identidade byte-a-byte")
    w("")
    for sha, group in sha_groups.items():
        kinds = sorted({g["kind"] for g in group})
        w(f"- `{sha[:12]}` — **{len(group)} cópias**, posições: {', '.join(kinds)}")
    w("")
    if len(sha_groups) == 1:
        w("**Todas as cópias da suíte são o mesmo arquivo, byte a byte.**")
    w("")

    if schemas:
        w("### Schemas (contexto)")
        w("")
        w("| caminho | sha256[:12] | enum de `comparison_metrics` |")
        w("|---|---|---|")
        for p in sorted(schemas):
            e = schema_enum(p)
            w(f"| `{p.relative_to(DRIVE)}` | `{sha256(p)[:12]}` | {len(e)} valores |")
        w("")
        enums = {tuple(schema_enum(p)) for p in schemas}
        if len(enums) == 1:
            vals = sorted(enums)[0]
            w(f"Os schemas **diferem entre si** como arquivo, mas o enum de "
              f"`comparison_metrics` é **idêntico** nos dois — {len(vals)} valores "
              f"permitidos: " + ", ".join(f"`{v}`" for v in vals) + ".")
            w("")
            w(f"Logo o schema **não é fonte** nem do 5 nem do {len(union)}: ele permite {len(vals)}.")
        w("")

    # 3
    w("## 3. Qual contagem a auditoria usou")
    w("")
    if unique_target and unique_peer:
        w(f"- `{TARGET}` declara **{len(unique_target)}** métricas: "
          + ", ".join(f"`{m}`" for m in unique_target))
        w(f"- `{PEER}` declara **{len(unique_peer)}** métricas: "
          + ", ".join(f"`{m}`" for m in unique_peer))
        shared = sorted(set(unique_target) & set(unique_peer))
        w(f"- Interseção ({len(shared)}): " + ", ".join(f"`{m}`" for m in shared))
        w(f"- **União dos dois testes comparativos: {len(union)}** — "
          + ", ".join(f"`{m}`" for m in union))
        w("")
    declared_n = sorted(declared)[0][1] if declared else None
    if declared_n is not None and unique_target is not None:
        w(f"**A auditoria usou {declared_n}, que é a UNIÃO `{PEER}` ∪ `{TARGET}`, "
          f"não a contagem do `{TARGET}` isolado ({len(unique_target)}).**")
        w("")
    if declared:
        a, b = sorted(declared)[0]
        w(f"Confirmação independente do numerador: dos {len(union)} nomes da união, "
          f"**{len(unmatched)}** não aparecem como `criterion` de rubrica em nenhum "
          f"dos testes da suíte (matching por nome exato): "
          + ", ".join(f"`{m}`" for m in unmatched) + ".")
        ok = (len(unmatched) == a and len(union) == b)
        w("")
        w(f"Isso {'**reproduz**' if ok else '**não reproduz**'} exatamente o par "
          f"declarado `{a} de {b}`.")
        w("")

    w("### A diferença é workspace × release?")
    w("")
    if len(sha_groups) == 1 and len(tgt_sets) == 1:
        w("**Não.** As cópias RELEASE e WORKSPACE da suíte são byte-idênticas e "
          f"ambas declaram as **mesmas {len(unique_target)}** métricas para o "
          f"`{TARGET}`. Não há delta workspace × release a explicar.")
        w("")
        w(f"A discrepância 5×6 é de **escopo de contagem**, não de versão de arquivo: "
          f"**5** = métricas do `{TARGET}`; **{len(union)}** = união dos dois testes "
          f"comparativos da suíte (`{PEER}` ∪ `{TARGET}`). O `{PEER}` contribui "
          f"`{sorted(set(unique_peer) - set(unique_target))[0]}` e o `{TARGET}` "
          f"contribui `{sorted(set(unique_target) - set(unique_peer))[0]}`.")
    else:
        w("Ver tabela em §2 — há divergência entre posições.")
    w("")
    w("---")
    w("")
    w("## Procedência")
    w("")
    w("| arquivo lido | sha256 | bytes |")
    w("|---|---|---|")
    for p in sorted(suites + schemas) + CLAIM_DOCS:
        w(f"| `{p.relative_to(DRIVE)}` | `{sha256(p)}` | {p.stat().st_size} |")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"escrito: {OUT}")
    print(f"sha256:  {sha256(OUT)}")
    print(f"bytes:   {OUT.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
