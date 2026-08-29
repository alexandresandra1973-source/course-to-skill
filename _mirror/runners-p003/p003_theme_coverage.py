#!/usr/bin/env python3
"""Cobertura de TEMA — derivada do corpus, nunca de uma lista minha.

O problema: dizer "o curso quase não fala de X" exige saber que X importa no
domínio. Se eu trouxer essa lista, sou eu avaliando o curso, não a medição.

A saída: deixar o CURSO nomear os temas. O PASS 1 produziu `topic` e `function`
para 148 segmentos, a partir do próprio texto. Um termo que aparece ali é um
termo que o curso trata como assunto — sem que eu opine.

Depois disso, contar quantas EVIDÊNCIAS mencionam cada termo. Tema que o curso
nomeia e quase não sustenta com evidência é o achado. Quem julga se o tema é
central é o revisor; eu entrego contagem e timestamp.
"""
from __future__ import annotations
import json, re, sys
from collections import Counter
from pathlib import Path
import yaml

W = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-work")
OUT = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-themes.json")
STOP = set("""a o e de da do the of to in and for on with is are you your it that this
be as at by an we i not or from can will if what how when they them their there
here more most very just also only than then so do does did have has had was were
been being um uh like really gonna going want need make sure lets let get got
one two three first second next last time way thing things people right okay ok
yeah yes no now new good great best better big small high low use using used
about into over under out up down all any some each every other another same
different because but however though while during before after between within""".split())


def norm(s):
    """Preserva acento. A primeira versao removia [^a-z0-9] e transformava
    'estrategia' em 'estrat gia' e 'pagina' em 'gina', fabricando temas que nao
    existem e zerando a contagem de temas que existem."""
    return re.sub(r"[^0-9a-zà-öø-ÿ ]", " ", (s or "").lower())


def grams(s, n):
    ws = [w for w in norm(s).split() if len(w) > 2]
    return [" ".join(ws[i:i+n]) for i in range(len(ws)-n+1)
            if not all(w in STOP for w in ws[i:i+n])]


def main() -> int:
    tm = yaml.safe_load((W/"01_PASS1/temporal-map.yaml").read_text(encoding="utf-8"))["temporal_map"]
    ev = [json.loads(l) for l in (W/"02_PASS2/EVIDENCE.jsonl").read_text(encoding="utf-8")
          .splitlines() if l.strip()]
    # --- 1. o curso nomeia os temas (PASS 1, derivado do texto)
    # SO o `topic`. O campo `function` do PASS 1 descreve o que o segmento FAZ
    # ("demonstracao pratica", "abertura de novo modulo"), nao o assunto — e
    # polui a lista de temas com meta-linguagem do segmentador.
    topic_text = " ".join(s["topic"] for s in tm)
    cand = Counter()
    for n in (2, 3):
        cand.update(g for g in grams(topic_text, n)
                    if not any(w in STOP for w in g.split()))
    themes = [t for t, c in cand.items() if c >= 2]
    # --- 2. quantas EVIDÊNCIAS mencionam cada tema
    # Compara SO contra a claim: os topicos do PASS 1 saem em portugues e as
    # citacoes sao em ingles. Misturar as duas linguas zera contagens por
    # diferenca de idioma, nao por ausencia de cobertura.
    # A MESMA transformacao dos dois lados. As versoes anteriores montavam o
    # n-grama filtrando palavras curtas ("volume de busca" -> "volume busca") e
    # procuravam no texto NAO filtrado, onde "volume busca" nunca aparece. Zero
    # por incompatibilidade de transformacao, nao por ausencia de cobertura.
    def reduced(txt):
        return " " + " ".join(w for w in norm(txt).split() if len(w) > 2) + " "
    blob = [(e["evidence_id"], reduced(e["claim"]),
             e["source_excerpt"]["span"]["start_s"]) for e in ev]
    rows = []
    for t in themes:
        hits = [(i, s) for i, b, s in blob if f" {t} " in b]
        rows.append({"theme": t, "named_in_topics": cand[t], "evidence_mentions": len(hits),
                     "first_s": min((s for _, s in hits), default=None),
                     "evidence_ids": [i for i, _ in hits][:6]})
    rows.sort(key=lambda r: (r["evidence_mentions"], -r["named_in_topics"]))
    OUT.write_text(json.dumps({"themes": rows, "n_evidence": len(ev),
                               "n_segments": len(tm)}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"temas nomeados pelo curso (>=2 segmentos): {len(rows)}")
    print("\nOS MENOS SUSTENTADOS POR EVIDÊNCIA:")
    print(f"  {'tema':<34} {'nos tópicos':>11} {'evidências':>11}  1ª menção")
    for r in rows[:18]:
        ts = f"{r['first_s']//60}:{r['first_s']%60:02d}" if r["first_s"] is not None else "—"
        print(f"  {r['theme']:<34} {r['named_in_topics']:>11} {r['evidence_mentions']:>11}  {ts}")
    print("\nOS MAIS SUSTENTADOS (para contraste):")
    for r in sorted(rows, key=lambda x: -x["evidence_mentions"])[:8]:
        print(f"  {r['theme']:<34} {r['named_in_topics']:>11} {r['evidence_mentions']:>11}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
