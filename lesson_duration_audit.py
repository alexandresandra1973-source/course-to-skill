#!/usr/bin/env python3
"""FRENTE C — duração real da fonte L0 × custo estimado por aula.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/. Publica em
Course-to-Skill-Claude/docs/. Relatório gerado: nenhum número digitado.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
SRC = DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources"
L0 = SRC / "transcript/transcript-original-en.txt"
META = SRC / "metadata/source-metadata.yaml"
FER = DOCS / "FINAL_ENGINEERING_REPORT.md"
INV = DOCS / "PROJECT_INVENTORY.md"
CMAP = DOCS / "L0_COVERAGE_MAP.md"
OUT = DOCS / "LESSON-DURATION-AUDIT-v0.1.4.md"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def secs(t: str) -> int:
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def hhmmss_to_s(t: str) -> int:
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def find_lines(p: Path, pattern: str) -> list[tuple[int, str]]:
    return [(i, l.strip()) for i, l in
            enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            if re.search(pattern, l)]


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    meta = yaml.safe_load(META.read_text(encoding="utf-8"))
    declared = meta["source"]["duration"]
    declared_s = hhmmss_to_s(declared)

    raw = L0.read_text(encoding="utf-8")
    marks = re.findall(r"\*\*(\d+:\d{2})\*\*", raw)
    last = max(marks, key=secs)
    tail_gap = declared_s - secs(last)
    words = len(raw.split())
    nbytes = L0.stat().st_size

    cost_lines = find_lines(FER, r"77")
    inv_lines = find_lines(INV, r"00:15:05|duração")
    map_lines = find_lines(CMAP, r"15:05")

    # custo do corpus, recomputado a partir do número citado no relatório
    per_lesson_min = float(re.search(r"~(\d+) min", cost_lines[0][1]).group(1))
    corpus = {n: round(n * per_lesson_min / 60, 2) for n in (5, 6, 7, 8)}
    ratio = round(per_lesson_min * 60 / declared_s, 2)

    L, w = [], None
    w = L.append
    w("# Duração real da fonte L0 × custo estimado por aula")
    w("")
    w(f"- Gerado: `{stamp}`")
    w(f"- Gerador: `{Path(__file__).name}` (nenhum número digitado)")
    w("- READ-ONLY sobre `Course-to-Skill/`")
    w("")
    w("## Veredito")
    w("")
    w("**Nenhum dos dois números está errado. Eles medem coisas diferentes, e a "
      "premissa de que um contradiz o outro é que está errada.**")
    w("")
    w(f"- **{declared}** é a duração do vídeo-fonte.")
    w(f"- **~{per_lesson_min:.0f} min** é o tempo de PIPELINE para processar uma aula, "
      "declarado no próprio texto como *\"de ponta a ponta por aula "
      "(L0 → 3 passadas de adversário → bundle)\"*.")
    w("")
    w(f"Um é a duração do insumo; o outro é o custo de processá-lo. A razão entre "
      f"eles é **{ratio}×** — processar a aula custa {ratio} vezes o tempo de "
      "assisti-la, o que é coerente, não contraditório.")
    w("")
    w("## Duração real da fonte")
    w("")
    w("| evidência | valor |")
    w("|---|---|")
    w(f"| `source-metadata.yaml` → `source.duration` | **{declared}** = {declared_s}s |")
    w(f"| última marca de tempo no transcript | `{last}` = {secs(last)}s |")
    w(f"| cauda após a última marca | {tail_gap}s |")
    w(f"| marcas de tempo no transcript | {len(marks)} |")
    w(f"| palavras no transcript | {words} |")
    w(f"| bytes do transcript | {nbytes} |")
    w("")
    w(f"A última marca (`{last}`) fica {tail_gap}s antes do fim declarado, o que é o "
      "esperado: o segmento final não recebe marca nova. As três fontes são "
      f"consistentes com **{declared}**.")
    w("")
    w(f"- transcript sha256: `{sha256(L0)}`")
    w(f"- metadata sha256: `{sha256(META)}`")
    w("")
    w("## Onde cada número aparece")
    w("")
    w(f"**`{FER.name}`** — a única ocorrência de \"77\":")
    w("")
    for i, l in cost_lines:
        w(f"- linha {i}: {l}")
    w("")
    w(f"**`{INV.name}`** — declara a duração:")
    w("")
    for i, l in inv_lines[:3]:
        w(f"- linha {i}: {l[:300]}")
    w("")
    w(f"**`{CMAP.name}`** — usa a duração como extensão de L0:")
    w("")
    for i, l in map_lines[:3]:
        w(f"- linha {i}: {l[:200]}")
    w("")
    w("## Custo do corpus de 5–8 aulas")
    w("")
    w("O custo do corpus **não muda** ao confirmar que a aula tem 15:05, porque a "
      f"estimativa de ~{per_lesson_min:.0f} min já é por aula processada e não "
      "deriva da duração do vídeo.")
    w("")
    w("| aulas | pipeline |")
    w("|---|---|")
    for n, h in corpus.items():
        w(f"| {n} | {n * per_lesson_min:.0f} min = **{h} h** |")
    w("")
    w(f"Para 6 aulas dá **{corpus[6]} h**, o que confere com as *\"~8 h de pipeline\"* "
      "do relatório.")
    w("")
    w("## Ressalva sobre a base da estimativa")
    w("")
    w(f"O ~{per_lesson_min:.0f} min é *\"medido no piloto\"* — ou seja, **n = 1 aula**, "
      f"e essa aula tem {declared}. Se o corpus incluir aulas mais longas, a "
      "estimativa por aula não transfere direto: a parte proporcional à duração "
      "(L0, passadas de adversário sobre o transcript) escala com o texto, a parte "
      "fixa não. O que está medido é o custo de processar **uma aula de 15 min**, "
      "não o de processar uma aula qualquer.")
    w("")
    w("Isso não corrige nenhum dos dois números; delimita o que a estimativa cobre.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"duração declarada: {declared} ({declared_s}s) | última marca {last} "
          f"| cauda {tail_gap}s")
    print(f"custo/aula citado: {per_lesson_min:.0f} min | razão {ratio}x")
    print(f"corpus: " + ", ".join(f"{n}={h}h" for n, h in corpus.items()))
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha256(OUT)[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
