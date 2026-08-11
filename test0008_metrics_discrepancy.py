#!/usr/bin/env python3
"""Apuração da discrepância 5×6 dos `comparison_metrics` do TEST-0008.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/ e Course-to-Skill-Compiler/.
NÃO congela lista canônica, NÃO propõe lista. Só apura.

REGRA DE CASAMENTO: identidade, nunca menção. Um artefato conta quando
`TEST-0008` é chave de YAML, ou quando o `artifact_id`/nome de arquivo casa —
nunca porque o termo aparece no corpo do texto. Sondas anteriores desta sessão
deram falso positivo exatamente por casar menção.

Se as contagens divergirem entre si, o relatório publica TODAS. Não escolhe.
"""
from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "TEST-0008-METRICS-DISCREPANCY.md"
TREES = [DRIVE / "Course-to-Skill", DRIVE / "Course-to-Skill-Compiler"]

CLAIM_DOCS = [DOCS / "ARCHITECTURE_REVIEW.md",
              DOCS / "CLAUDE_ARCHITECTURE_PROPOSAL.md"]
PHASE_OF = {"CLAUDE_ARCHITECTURE_PROPOSAL.md": "Fase 3 — Proposta de arquitetura",
            "ARCHITECTURE_REVIEW.md": "Fase 2 — Revisão de arquitetura"}

TARGET, PEER = "TEST-0008", "TEST-0007"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def classify(path: str) -> str:
    """RELEASE × WORKSPACE pela posição na árvore."""
    if "01_TOOL" in path or "/releases/" in path or "RELEASE-CANDIDATE" in path:
        return "RELEASE"
    if "02_PILOTS" in path or "03_FINAL-BLIND-TEST" in path:
        return "WORKSPACE"
    if "/pilots/" in path or "PILOT-001/v0" in path:
        return "WORKSPACE"
    return "OUTRO"


def yaml_docs(text: str) -> list[dict]:
    try:
        return [d for d in yaml.safe_load_all(text) if isinstance(d, dict)]
    except yaml.YAMLError:
        return []


def walk_key(node, key):
    if isinstance(node, dict):
        if key in node:
            yield node[key]
        for v in node.values():
            yield from walk_key(v, key)
    elif isinstance(node, list):
        for v in node:
            yield from walk_key(v, key)


def yaml_sources():
    """Todo YAML das duas árvores, solto ou dentro de zip."""
    for tree in TREES:
        for p in sorted(tree.rglob("*")):
            if not p.is_file():
                continue
            if p.suffix.lower() in (".yaml", ".yml"):
                try:
                    yield str(p.relative_to(DRIVE)), p.read_bytes()
                except OSError:
                    continue
            elif p.suffix.lower() == ".zip":
                try:
                    with zipfile.ZipFile(p) as z:
                        for n in z.namelist():
                            if n.lower().endswith((".yaml", ".yml")):
                                yield f"{p.relative_to(DRIVE)} :: {n}", z.read(n)
                except zipfile.BadZipFile:
                    continue


def collect():
    """Declarações de comparison_metrics por CHAVE, e contratos legados."""
    suites, contracts = [], []
    for path, blob in yaml_sources():
        text = blob.decode("utf-8", "replace")
        if "comparison_metrics" not in text and "comparative_tests" not in text:
            continue
        for d in yaml_docs(text):
            tid = d.get("test_id")
            if tid in (TARGET, PEER):
                for m in walk_key(d, "comparison_metrics"):
                    if isinstance(m, list) and m:
                        suites.append({"path": path, "kind": classify(path),
                                       "test_id": tid, "metrics": [str(x) for x in m],
                                       "sha256": sha(blob), "bytes": len(blob)})
            ct = d.get("comparative_tests")
            if isinstance(ct, dict) and TARGET in ct:
                entry = ct[TARGET] or {}
                own = entry.get("comparison_metrics")
                contracts.append({
                    "path": path, "kind": classify(path),
                    "artifact_id": d.get("artifact_id"),
                    "comparison": entry.get("comparison"),
                    "margin_threshold": entry.get("margin_threshold"),
                    "declares_own_metrics": isinstance(own, list),
                    "own_metrics": [str(x) for x in own] if isinstance(own, list) else [],
                    "keys": sorted(entry) if isinstance(entry, dict) else [],
                    "sha256": sha(blob),
                })
    return suites, contracts


def phase_line(path: Path) -> str:
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()[:10], 1):
        m = re.search(r"\*\*(Fase \d+[^*]*)\*\*", line)
        if m:
            return f"linha {i}: **{m.group(1).strip()}**"
    return "o arquivo não declara fase no cabeçalho"


def claim_sentences(path: Path):
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "comparison_metrics" not in line:
            continue
        for s in re.split(r"(?<=[.;])\s+(?=[A-ZÀ-Ú*(])", line):
            if "comparison_metrics" in s:
                out.append((i, s.strip()))
    return out


def main() -> int:
    try:
        drive_ok = DRIVE.is_dir()
    except OSError as e:
        drive_ok = False
        print(f"ERRO DE MONTAGEM: {e}")
    if not drive_ok:
        print(f"FONTE INDISPONÍVEL: {DRIVE} não está acessível.")
        print("A apuração exige ler as árvores RELEASE e WORKSPACE ao vivo e "
              "publicar em Course-to-Skill-Claude/docs/. Nenhuma das duas coisas "
              "é possível agora. Nada foi publicado.")
        return 2

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    suites, contracts = collect()

    tgt = [s for s in suites if s["test_id"] == TARGET]
    peer = [s for s in suites if s["test_id"] == PEER]
    by_kind = {}
    for s in tgt:
        by_kind.setdefault(s["kind"], set()).add(tuple(s["metrics"]))
    distinct_tgt = {tuple(s["metrics"]) for s in tgt}
    distinct_peer = {tuple(s["metrics"]) for s in peer}
    union = sorted(set().union(*distinct_tgt) | set().union(*distinct_peer)) \
        if distinct_tgt and distinct_peer else []

    claims = {d.name: claim_sentences(d) for d in CLAIM_DOCS}
    declared = set()
    for sents in claims.values():
        for _, s in sents:
            for a, b in re.findall(r"(\d+)\s+d[ea]s?\s+(\d+)\s+`?comparison_metrics", s):
                declared.add((int(a), int(b)))

    contract_metric_counts = Counter(
        len(c["own_metrics"]) if c["declares_own_metrics"] else -1
        for c in contracts)

    L, w = [], None
    w = L.append
    w("# TEST-0008 — discrepância 5×6 dos `comparison_metrics`")
    w("")
    w(f"- Gerado: `{stamp}` · gerador `{Path(__file__).name}`")
    w("- READ-ONLY sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/`")
    w("- **Casamento por identidade**: `TEST-0008` como chave de YAML, ou "
      "`artifact_id`/nome de arquivo. Menção no corpo do texto nunca conta.")
    w("- Nada congelado, nenhuma lista canônica proposta.")
    w("")

    w("## 1. A frase literal, e de qual arquivo veio cada número")
    w("")
    for name, sents in claims.items():
        w(f"### `{name}` — {PHASE_OF.get(name, 'fase não declarada')}")
        w("")
        w(f"- Autodeclaração de fase: {phase_line(DOCS / name)}")
        w("")
        for ln, s in sents:
            w(f"- **linha {ln}:** {s}")
        w("")
    if declared:
        for a, b in sorted(declared):
            w(f"**Número declarado: {a} de {b}.**")
        w("")
    w("**De qual arquivo foi contado:** os dois docs **não citam caminho nenhum** "
      "para essa contagem. Não há como atribuí-la a um arquivo por leitura do "
      "texto; o que dá para fazer é reconstruir a contagem, que é a §3.")
    w("")

    w("## 2. RELEASE × WORKSPACE, lado a lado")
    w("")
    w(f"Artefatos em que `{TARGET}` declara `comparison_metrics` **como chave**: "
      f"**{len(tgt)}**.")
    w("")
    w("| posição | artefatos | conjuntos distintos | métricas |")
    w("|---|---|---|---|")
    for kind in sorted(by_kind):
        sets_ = by_kind[kind]
        n = sum(1 for s in tgt if s["kind"] == kind)
        if len(sets_) == 1:
            names = ", ".join(f"`{x}`" for x in sorted(sets_)[0])
            w(f"| **{kind}** | {n} | 1 | {names} |")
        else:
            w(f"| **{kind}** | {n} | **{len(sets_)}** | "
              + " · ".join("(" + ", ".join(s) + ")" for s in sorted(sets_)) + " |")
    w("")
    if len(distinct_tgt) == 1:
        only = sorted(distinct_tgt)[0]
        w(f"**Um único conjunto, de {len(only)} métricas, em todas as posições.** "
          "RELEASE e WORKSPACE declaram exatamente o mesmo.")
    else:
        w(f"**{len(distinct_tgt)} conjuntos distintos.** Ver acima.")
    w("")
    w("| # | posição | artefato | sha256 | métricas |")
    w("|---|---|---|---|---|")
    for i, s in enumerate(sorted(tgt, key=lambda x: (x["kind"], x["path"])), 1):
        w(f"| {i} | {s['kind']} | `{s['path']}` | `{s['sha256'][:12]}` | "
          f"{len(s['metrics'])} |")
    w("")

    w("## 3. A diferença é workspace × release?")
    w("")
    if len(distinct_tgt) == 1:
        only = sorted(distinct_tgt)[0]
        w("**Não.** As duas posições declaram o mesmo conjunto, de "
          f"**{len(only)}** métricas. Não existe sexta métrica em nenhum dos "
          "lados, e portanto não há sexta métrica \"morando\" em lugar nenhum.")
        w("")
        if distinct_peer and len(distinct_peer) == 1:
            p = sorted(distinct_peer)[0]
            shared = sorted(set(only) & set(p))
            w(f"O `{PEER}` declara **{len(p)}**: " + ", ".join(f"`{x}`" for x in p))
            w("")
            w(f"- interseção ({len(shared)}): " + ", ".join(f"`{x}`" for x in shared))
            w(f"- só no `{PEER}`: "
              + ", ".join(f"`{x}`" for x in sorted(set(p) - set(only))))
            w(f"- só no `{TARGET}`: "
              + ", ".join(f"`{x}`" for x in sorted(set(only) - set(p))))
            w("")
            w(f"**União dos dois testes comparativos: {len(union)}** — "
              + ", ".join(f"`{x}`" for x in union))
            w("")
            if declared and sorted(declared)[0][1] == len(union):
                w(f"É esse o **{len(union)}** da auditoria: união "
                  f"`{PEER}` ∪ `{TARGET}`, não a contagem do `{TARGET}` isolado.")
                w("")
    else:
        w("**Talvez.** Há mais de um conjunto declarado; ver §2.")
        w("")

    w("## 4. Os contratos legados que declaram o TEST-0008")
    w("")
    w(f"Contratos com `TEST-0008` como **chave** de `comparative_tests`: "
      f"**{len(contracts)}**.")
    w("")
    own = [c for c in contracts if c["declares_own_metrics"]]
    if own:
        w(f"**{len(own)} deles declaram `comparison_metrics` próprio** — "
          "possível terceira contagem:")
        w("")
        w("| artefato | métricas | nomes |")
        w("|---|---|---|")
        for c in own:
            w(f"| `{c['path']}` | {len(c['own_metrics'])} | "
              + ", ".join(f"`{x}`" for x in c["own_metrics"]) + " |")
    else:
        w("**Nenhum declara `comparison_metrics` próprio.** Eles trazem só "
          "`comparison` e `margin_threshold`, ou seja, dizem COMO comparar e não "
          "O QUE medir. Não há terceira contagem escondida aqui.")
    w("")
    w("| artefato | `comparison` | `margin_threshold` | chaves |")
    w("|---|---|---|---|")
    for c in sorted(contracts, key=lambda x: x["path"]):
        w(f"| `{c['path']}` | `{c['comparison']}` | `{c['margin_threshold']}` | "
          f"{', '.join(c['keys']) or '—'} |")
    w("")

    w("## 5. As contagens encontradas")
    w("")
    w("| contagem | de onde vem |")
    w("|---|---|")
    for s in sorted(distinct_tgt):
        w(f"| **{len(s)}** | declaração do `{TARGET}` nos artefatos de suíte |")
    if union:
        w(f"| **{len(union)}** | união `{PEER}` ∪ `{TARGET}` |")
    for n, c in sorted(contract_metric_counts.items()):
        if n >= 0:
            w(f"| **{n}** | contratos legados que declaram métrica própria "
              f"({c} artefato(s)) |")
    w("")
    w("Nenhuma foi escolhida como canônica. Congelar a lista é decisão de quem "
      "conduz o teste, e o ADR de paridade de informação a lista como bloqueador "
      "número 1 do TEST-0008.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"suítes com {TARGET}: {len(tgt)} | conjuntos distintos: "
          f"{len(distinct_tgt)}")
    for s in sorted(distinct_tgt):
        print(f"  n={len(s)}: {', '.join(s)}")
    print(f"contratos legados com {TARGET}: {len(contracts)} | com métrica "
          f"própria: {len(own)}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha(OUT.read_bytes())[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
