#!/usr/bin/env python3
"""FRENTE 2 — densidade de decisão: UM script, MESMA métrica, DUAS fontes.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/. Publica em
Course-to-Skill-Claude/docs/.

A comparação só vale se as duas fontes passarem exatamente pelas mesmas
funções de contagem. Não há caminho de código separado por fonte: a única
diferença entre elas é o texto e a duração declarada.

Se o transcript do candidato não existir, o relatório sai PARCIAL e SEM
veredito. Veredito exige as duas fontes medidas.
"""
from __future__ import annotations

import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "SOURCE-DENSITY-COMPARISON.md"

P001_TRANSCRIPT = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources"
                   / "transcript/transcript-original-en.txt")
P001_META = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources"
             / "metadata/source-metadata.yaml")

CAND_META = DOCS / "PILOT-002-CANDIDATE-METADATA.yaml"
# Onde o Alexandre cola o transcript. Qualquer um destes serve.
CAND_TRANSCRIPT_CANDIDATES = [
    DOCS / "PILOT-002-transcript.txt",
    DOCS / "PILOT-002" / "transcript.txt",
]

ONE_PAGE_LINES = 45

# --------------------------------------------------------------------------
# métricas — definidas UMA vez, aplicadas às duas fontes sem exceção
# --------------------------------------------------------------------------
CONDITIONAL = re.compile(
    r"\b(if|when|unless|except|depends|depending|otherwise|caso|quando)\b", re.I)
NORMATIVE = re.compile(
    r"\b(never|always|must|should|don't|do not|avoid|instead of|rather than|"
    r"choose|pick|decide|select|start with|prefer|make sure|nunca|sempre|"
    r"deve|escolha|evite)\b", re.I)
FRAMEWORK = re.compile(
    r"\b([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,3})\s+"
    r"(framework|method|model|principle|process|system|checklist|loop|pattern)\b")
STEP = re.compile(r"\bstep\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
                  re.I)
THRESHOLD = re.compile(
    r"\b(?:at least\s+)?\d+(?:[.,]\d+)?\s*"
    r"(%|percent|hours?|minutes?|seconds?|days?|weeks?|months?|years?|times|x)\b", re.I)
RANGE = re.compile(r"\b\d+\s*(?:to|–|-|a)\s*\d+\b")

TS = re.compile(r"\*\*(\d+:\d{2})\*\*|^\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*$", re.M)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def strip_marks(text: str) -> str:
    """Remove marcas de tempo e títulos de seção; sobra a fala."""
    t = re.sub(r"\*\*\d+:\d{2}\*\*", " ", text)
    t = re.sub(r"^\s*\d{1,2}:\d{2}(?::\d{2})?\s*$", " ", t, flags=re.M)
    t = re.sub(r"^#{1,6}\s.*$", " ", t, flags=re.M)
    t = re.sub(r"##[^\n]*", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 3]


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def measure(name: str, text: str, duration_s: int, src: dict) -> dict:
    body = strip_marks(text)
    sents = sentences(body)

    cond = [s for s in sents if CONDITIONAL.search(s)]
    norm_s = [s for s in sents if NORMATIVE.search(s)]
    decision_sents = {norm(s): s for s in sents
                      if CONDITIONAL.search(s) or NORMATIVE.search(s)}

    fw = {m.group(0).strip() for m in FRAMEWORK.finditer(body)}
    steps = {m.group(0).lower() for m in STEP.finditer(body)}
    thr = {m.group(0).strip().lower() for m in THRESHOLD.finditer(body)}
    rng = {m.group(0).strip() for m in RANGE.finditer(body)}

    minutes = duration_s / 60
    n_dec = len(decision_sents)
    return {
        "source": name,
        "provenance": src,
        "duration_seconds": duration_s,
        "duration_minutes": round(minutes, 2),
        "words": len(body.split()),
        "sentences": len(sents),
        "conditional_sentences": len(cond),
        "normative_sentences": len(norm_s),
        "distinct_decision_points": n_dec,
        "named_frameworks_and_procedures": sorted(fw | steps),
        "named_frameworks_count": len(fw | steps),
        "numeric_thresholds": sorted(thr | rng),
        "numeric_thresholds_count": len(thr | rng),
        "decision_density_per_minute": round(n_dec / minutes, 3),
        "words_per_minute": round(len(body.split()) / minutes, 1),
        "one_page_test": {
            "rule": (f"Um bullet por ponto de decisão distinto. Cabe em "
                     f"{ONE_PAGE_LINES} linhas? Então a fonte é FINA."),
            "bullets_needed": n_dec,
            "limit": ONE_PAGE_LINES,
            "fits_in_one_page": n_dec <= ONE_PAGE_LINES,
            "verdict": "FINA" if n_dec <= ONE_PAGE_LINES else "NAO_FINA",
        },
    }


def load_candidate() -> tuple[str, int, dict] | None:
    if not CAND_META.exists():
        return None
    meta = yaml.safe_load(CAND_META.read_text(encoding="utf-8"))
    path = next((p for p in CAND_TRANSCRIPT_CANDIDATES if p.exists()), None)
    if path is None:
        return None
    return (path.read_text(encoding="utf-8"),
            int(meta["source"]["duration_seconds"]),
            {"path": str(path.relative_to(DRIVE)),
             "sha256": sha256(path.read_bytes()),
             "video_id": meta["source"].get("video_id")})


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    p1_meta = yaml.safe_load(P001_META.read_text(encoding="utf-8"))
    h, m, s = p1_meta["source"]["duration"].split(":")
    p1_dur = int(h) * 3600 + int(m) * 60 + int(s)
    p1 = measure("PILOT-001 — HubSpot, How to Build Your First AI Agent",
                 P001_TRANSCRIPT.read_text(encoding="utf-8"), p1_dur,
                 {"path": str(P001_TRANSCRIPT.relative_to(DRIVE)),
                  "sha256": sha256(P001_TRANSCRIPT.read_bytes()),
                  "video_id": p1_meta["source"]["video_id"]})

    cand = load_candidate()
    c = None
    if cand:
        text, dur, src = cand
        cmeta = yaml.safe_load(CAND_META.read_text(encoding="utf-8"))
        c = measure(f"PILOT-002 candidato — {cmeta['source']['title']}",
                    text, dur, src)

    L, w = [], None
    w = L.append
    w("# Densidade de decisão — PILOT-001 × candidato PILOT-002")
    w("")
    w(f"- Gerado: `{stamp}` · gerador `{Path(__file__).name}`")
    w("- READ-ONLY sobre `Course-to-Skill/`")
    w("- **Um único script mede as duas fontes.** Não há caminho de código por "
      "fonte: mesmas regex, mesmos cortes, mesma definição de ponto de decisão.")
    w("")
    w("## Como cada coisa é contada")
    w("")
    w("| métrica | definição operacional |")
    w("|---|---|")
    w("| ponto de decisão | frase distinta (após normalizar) que contém marca "
      "condicional **ou** marca normativa |")
    w(f"| condicional | `{CONDITIONAL.pattern}` |")
    w(f"| normativa | `{NORMATIVE.pattern}` |")
    w("| framework/procedimento | nome próprio seguido de "
      "framework/method/model/principle/process/system/checklist/loop/pattern, "
      "mais `step N` |")
    w("| limiar numérico | número com unidade (%/h/min/dias/vezes) ou faixa `N a M` |")
    w("| **densidade de decisão** | pontos de decisão distintos ÷ minutos |")
    w(f"| teste da uma página | 1 bullet por ponto de decisão; ≤ {ONE_PAGE_LINES} "
      "linhas ⇒ FINA |")
    w("")
    w("Marcas de tempo e títulos de seção são removidos antes de contar, nas duas "
      "fontes.")
    w("")
    w("## Medição")
    w("")
    rows = [("duração (min)", "duration_minutes"), ("palavras", "words"),
            ("frases", "sentences"), ("frases condicionais", "conditional_sentences"),
            ("frases normativas", "normative_sentences"),
            ("**pontos de decisão distintos**", "distinct_decision_points"),
            ("frameworks/procedimentos nomeados", "named_frameworks_count"),
            ("limiares numéricos", "numeric_thresholds_count"),
            ("palavras/min", "words_per_minute"),
            ("**decisões/min**", "decision_density_per_minute")]
    w("| métrica | PILOT-001 | candidato |")
    w("|---|---|---|")
    for label, key in rows:
        w(f"| {label} | {p1[key]} | {c[key] if c else '—'} |")
    w("")
    w("## Teste da uma página")
    w("")
    w("| fonte | bullets | limite | cabe? | veredito |")
    w("|---|---|---|---|---|")
    for src in (p1, c):
        if not src:
            w("| candidato | — | — | — | **NÃO MEDIDO** |")
            continue
        t = src["one_page_test"]
        w(f"| {src['source'][:38]} | {t['bullets_needed']} | {t['limit']} | "
          f"{'sim' if t['fits_in_one_page'] else 'não'} | **{t['verdict']}** |")
    w("")

    if c:
        ratio = round(c["decision_density_per_minute"]
                      / p1["decision_density_per_minute"], 3)
        qualifies = not c["one_page_test"]["fits_in_one_page"]
        w("## Veredito")
        w("")
        w(f"**{'QUALIFICA' if qualifies else 'NÃO QUALIFICA'}**")
        w("")
        w(f"- Razão candidato ÷ PILOT-001 em decisões/min: **{ratio}×**")
        w(f"- Teste da uma página do candidato: **{c['one_page_test']['verdict']}**")
        w("")
        if qualifies:
            w("O candidato REPROVA no teste da uma página, que é a condição para "
              "qualificar: a metodologia dele não cabe em bullets sem perder decisão.")
        else:
            w("O candidato PASSA no teste da uma página, logo **não** qualifica: a "
              "metodologia cabe em bullets, então a fonte é fina. Volume de palavras "
              "não compensa isso.")
        w("")
        w(f"Nota: o candidato tem {c['words_per_minute']} palavras/min contra "
          f"{p1['words_per_minute']} do PILOT-001. Prolixidade não é densidade — "
          "a decisão é pelo teste da uma página e por decisões/min, não por volume.")
    else:
        w("## Veredito")
        w("")
        w("**NÃO EMITIDO — medição parcial.**")
        w("")
        w("O transcript do candidato não foi obtido. O YouTube devolve as legendas "
          "com HTTP 200 e corpo vazio (exige PO token), e a API de player responde "
          "`LOGIN_REQUIRED`/`UNPLAYABLE` para todos os clientes testados. Emitir "
          "veredito com uma fonte medida e outra estimada seria exatamente a "
          "comparação com métrica diferente que esta frente proíbe.")
        w("")
        w("### Para completar")
        w("")
        w(f"1. Cole o transcript em `docs/{CAND_TRANSCRIPT_CANDIDATES[0].name}`.")
        w(f"2. Rode `python3 {Path(__file__).name}` de novo.")
        w("")
        w("Os metadados do candidato já estão apurados e congelados em "
          f"`{CAND_META.name}` — duração, capítulos e id do vídeo saíram da página "
          "do YouTube, não de estimativa.")
    w("")
    w("## Detalhe por fonte")
    w("")
    for src in (p1, c):
        if not src:
            continue
        w(f"### {src['source']}")
        w("")
        w(f"- fonte: `{src['provenance']['path']}`")
        w(f"- sha256: `{src['provenance']['sha256']}`")
        w(f"- frameworks/procedimentos: {', '.join(src['named_frameworks_and_procedures'][:20]) or '—'}")
        w(f"- limiares: {', '.join(src['numeric_thresholds'][:20]) or '—'}")
        w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"PILOT-001: {p1['distinct_decision_points']} decisões / "
          f"{p1['duration_minutes']} min = {p1['decision_density_per_minute']}/min "
          f"| uma página: {p1['one_page_test']['verdict']}")
    if c:
        print(f"candidato: {c['distinct_decision_points']} decisões / "
              f"{c['duration_minutes']} min = {c['decision_density_per_minute']}/min "
              f"| uma página: {c['one_page_test']['verdict']}")
    else:
        print("candidato: NÃO MEDIDO — transcript ausente; veredito não emitido")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha256(OUT.read_bytes())[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
