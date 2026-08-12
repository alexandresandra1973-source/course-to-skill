#!/usr/bin/env python3
"""Mede, nas evidências ACEITAS, duas coisas que 'quote resolve' não garante.

(a) DIVERGÊNCIA CLAIM×LITERAL — a claim afirma um termo que a quote não contém.
    Mede por entidade nomeada: nomes próprios, acrônimos e marcas transferem
    entre o português da claim e o inglês da quote, então a ausência é sinal.

(b) BURACO DE SUSTENTAÇÃO — quanto do span declarado a quote de fato cobre.
    A claim é rotulada com [start_s, end_s]; se a quote ocupa uma fração pequena
    desse intervalo, a evidência declara mais fonte do que exibe.

As duas são MECÂNICAS e não decidem: apontam onde olhar. Nenhuma substitui ler
a claim ao lado da quote.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
P1 = DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
L0 = P1 / "sources/transcript/transcript-original-en.txt"
TRACE = Path(sys.argv[1] if len(sys.argv) > 1
             else "/tmp/claude-1000/-home-mtx-course-to-skill-claude/canary-trace.json")

MARK = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")

# Palavras que parecem entidade mas são só início de frase ou genéricas.
STOP = {"Ao", "Exemplo", "Todo", "Leads", "Encadear", "O", "A", "Os", "As", "Um",
        "Uma", "Toda", "Este", "Esse", "Agent", "Agente", "IA", "AI"}


def norm(s: str) -> str:
    """Normalização declarada: remove marcas de tempo e colapsa espaço."""
    return " ".join(MARK.sub(" ", s).split())


def entities(text: str) -> set[str]:
    out = set()
    for w in re.findall(r"\b[A-Z][A-Za-z0-9]*\b", text):
        if w in STOP or len(w) < 2:
            continue
        out.add(w)
    for w in re.findall(r"\b[A-Z]{2,}\b", text):
        out.add(w)
    return out


def mark_positions(text: str) -> list[tuple[int, int]]:
    """[(offset_no_texto_normalizado, segundos)] das marcas, em ordem."""
    out, acc = [], []
    pos = 0
    for part in re.split(r"(\*\*\d{1,3}:[0-5]\d\*\*)", text):
        m = MARK.fullmatch(part)
        if m:
            out.append((pos, int(m.group(1)) * 60 + int(m.group(2))))
        else:
            n = norm(part)
            pos += len(n) + (1 if n else 0)
    return out


def main() -> int:
    d = json.loads(TRACE.read_text(encoding="utf-8"))
    drafts = d["drafts"]

    text = L0.read_text(encoding="utf-8")
    blocks = text.split("\n\n")
    idx = [(i, int(m.group(1)) * 60 + int(m.group(2)))
           for i, b in enumerate(blocks) if (m := MARK.fullmatch(b.strip()))]
    lo = min(x["start_s"] for x in drafts)
    hi = max(x["end_s"] for x in drafts)
    keep = []
    for k, (i, s) in enumerate(idx):
        if lo - 60 <= s <= hi + 60:
            end = idx[k + 1][0] if k + 1 < len(idx) else len(blocks)
            keep.extend(blocks[i:end])
    seg_raw = "\n\n".join(keep)
    seg_norm = norm(seg_raw)
    mpos = mark_positions(seg_raw)

    def quote_span(q: str) -> tuple[int | None, int | None]:
        qn = norm(q)
        at = seg_norm.find(qn)
        if at < 0:
            return None, None
        a, b = at, at + len(qn)
        before = [s for p, s in mpos if p <= a]
        inside = [s for p, s in mpos if a <= p <= b]
        start = (before[-1] if before else (mpos[0][1] if mpos else None))
        end = inside[-1] if inside else start
        return start, end

    print("=" * 92)
    print("(a) DIVERGÊNCIA CLAIM × LITERAL — entidade na claim ausente da quote")
    print("=" * 92)
    div = []
    for i, x in enumerate(drafts, 1):
        ce, qe = entities(x["claim"]), entities(x["quote"])
        missing = {e for e in ce - qe
                   if e.lower() not in x["quote"].lower()}
        if missing:
            div.append((i, x, missing))
            print(f"[{i:>2}] {x['epistemic_status']:<15} ausente da quote: "
                  f"{', '.join(sorted(missing))}")
            print(f"     claim: {x['claim'][:110]}")
            print(f"     quote: {x['quote'][:110]}")
    print(f"\n{len(div)}/{len(drafts)} com entidade da claim ausente da quote.")
    se = [i for i, x, _ in div if x["epistemic_status"] == "SOURCE_EXPLICIT"]
    print(f"Destas, {len(se)} rotuladas SOURCE_EXPLICIT: {se}")

    print()
    print("=" * 92)
    print("(b) BURACO DE SUSTENTAÇÃO — span declarado × span que a quote cobre")
    print("=" * 92)
    print(f"{'#':>3} {'declarado':>12} {'quote cobre':>12} {'razão':>7}  claim")
    rows = []
    for i, x in enumerate(drafts, 1):
        a, b = quote_span(x["quote"])
        decl = x["end_s"] - x["start_s"]
        cov = (b - a) if (a is not None and b is not None) else None
        r = (cov / decl) if (cov is not None and decl) else None
        rows.append((i, decl, cov, r))
        rr = f"{r:.2f}" if r is not None else "—"
        cc = f"{cov}s" if cov is not None else "não localiza"
        print(f"{i:>3} {str(decl)+'s':>12} {cc:>12} {rr:>7}  {x['claim'][:52]}")
    ok = [r for _, _, _, r in rows if r is not None]
    thin = [i for i, _, _, r in rows if r is not None and r < 0.5]
    print(f"\nmediana da razão: {sorted(ok)[len(ok)//2]:.2f}" if ok else "")
    print(f"evidências cuja quote cobre menos da METADE do span declarado: "
          f"{thin if thin else 'nenhuma'}")
    print("\n> A razão não é erro por si: uma quote curta pode sustentar uma claim "
          "curta.\n> O que ela mede é o TAMANHO DO BURACO entre o que a evidência "
          "declara\n> como fonte e o que ela exibe. Ler as marcadas acima.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
