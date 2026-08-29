#!/usr/bin/env python3
"""Varredura de CORRUPÇÃO DA FONTE propagada para a claim.

Roda daqui (ext4). READ-ONLY. Sem chamada de modelo.

A falha que este script procura é a mais grave que o compilador pode cometer:
a fonte automática está corrompida, o modelo corrige a corrupção ao escrever a
claim, e o registro sai rotulado SOURCE_EXPLICIT — propagando como "a fonte diz
isto" algo que a fonte, literalmente, não diz.

Corrigir a corrupção é DESEJÁVEL. Corrigir e chamar de fonte explícita é o dano.
Por isso o veredito por evidência tem duas colunas: houve divergência, e como
ela foi rotulada.

DOIS DETECTORES, ambos mecânicos:

  1. NEGAÇÃO PERDIDA — a claim nega e a quote não tem marca de negação alguma.
     É o caso EV-0026: a fonte diz "Agents are here to replace your team" (o
     "not" caiu na transcrição) e a claim afirma o contrário. Inverter o sentido
     é a corrupção mais perigosa porque o texto continua gramatical.

  2. NOME CORROMPIDO — a claim traz um nome de produto que não está na quote,
     mas a quote contém um quase-igual. "Chad GBT" para ChatGPT, "Gum Loop"
     para Gumloop, "a length post" para LinkedIn.

Nenhum decide sozinho: os dois imprimem claim e quote inteiras.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")

# Marcas de negação. A claim sai em português, a quote em inglês — o detector
# tem de conhecer os dois lados ou acusa toda tradução.
NEG_PT = re.compile(r"\b(não|nao|nunca|jamais|nenhum\w*|nem|sem)\b", re.I)
# Precisa cobrir a negação INCORPORADA do inglês — nobody, nothing, neither —
# senão acusa como "negação perdida" toda claim cuja quote nega por pronome.
# Foi o que aconteceu na primeira versão: 'Nobody needs' e 'building nothing'
# vieram marcados como negação ausente.
NEG_EN = re.compile(r"\b(not|never|no|none|nor|without|cannot|nobody|nothing|"
                    r"neither|nowhere|hardly|barely|stop|stops|instead|avoid|"
                    r"can't|don't|doesn't|isn't|aren't|won't|wasn't|weren't|"
                    r"didn't|shouldn't|couldn't|wouldn't)\b|n't\b|\bnon-\w+|\bun\w+able\b",
                    re.I)

CAMEL = re.compile(r"\b[A-Z][a-z]+[A-Z][A-Za-z]*\b")
# Nome próprio candidato: >=5 letras. A âncora que torna isto robusto entre
# idiomas é a do CASAMENTO, não a da extração — o quase-igual na quote também
# tem de estar CAPITALIZADO. Nome próprio permanece capitalizado em português e
# em inglês; palavra comum, não. Sem essa âncora o detector casa 'Times' com
# 'creative' e 'Cada' com 'and'.
PROPER = re.compile(r"\b[A-Z][A-Za-z]{4,}\b")
SIM_FLOOR = 0.60
MIN_MATCH_CHARS = 5


def norm(s: str) -> str:
    return re.sub(r"[^\w\s]", " ", s.lower())


def lost_negation(claim: str, quote: str) -> dict | None:
    """Claim nega, quote não tem negação nenhuma."""
    c = NEG_PT.findall(claim)
    q = NEG_EN.findall(quote)
    if c and not q:
        return {"tipo": "NEGACAO_PERDIDA", "negacoes_na_claim": sorted(set(c)),
                "negacoes_na_quote": 0}
    return None


def corrupted_name(claim: str, quote: str) -> dict | None:
    """Nome na claim ausente da quote, mas com quase-igual CAPITALIZADO nela.

    As três âncoras que separam corrupção de tradução:
      - o candidato tem >=5 letras e é capitalizado na claim;
      - o quase-igual na quote também é CAPITALIZADO — nome próprio sobrevive à
        tradução capitalizado, palavra comum não;
      - similaridade >= 0.60 e < 0.95, sobre janelas de 1 e 2 palavras.
    """
    cap_words = [w for w in re.findall(r"\b[\w'\-]+\b", quote)
                 if w[:1].isupper() and len(w) >= 3]
    ql = quote.lower()
    for ent in sorted(set(CAMEL.findall(claim)) | set(PROPER.findall(claim))):
        if ent.lower() in ql:
            continue
        if re.sub(r"[\s\-]", "", ent.lower()) in re.sub(r"[\s\-]", "", ql):
            continue
        best, score = None, 0.0
        for k in range(len(cap_words)):
            for j in (1, 2):
                cand = " ".join(cap_words[k:k + j])
                if len(cand) < MIN_MATCH_CHARS:
                    continue
                r = difflib.SequenceMatcher(None, ent.lower(), cand.lower()).ratio()
                if r > score:
                    best, score = cand, r
        if best and SIM_FLOOR <= score < 0.95:
            return {"tipo": "NOME_CORROMPIDO", "nome_na_claim": ent,
                    "quase_igual_na_quote": best, "similaridade": round(score, 2)}
    return None


def scan(path: Path, label: str) -> dict:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    hits = []
    for r in rows:
        q = r["source_excerpt"]["quote"]
        for det in (lost_negation, corrupted_name):
            d = det(r["claim"], q)
            if d:
                hits.append({**d, "id": r["evidence_id"],
                             "status": r["epistemic_status"],
                             "claim": r["claim"], "quote": q})
                break
    mi = [h for h in hits if h["status"] == "MODEL_INFERENCE"]
    se = [h for h in hits if h["status"] == "SOURCE_EXPLICIT"]

    print("=" * 88)
    print(f"{label} — {len(rows)} evidências")
    print("=" * 88)
    print(f"divergências que só se explicam por corrupção da fonte: {len(hits)}")
    print(f"  rotuladas MODEL_INFERENCE (correto)      : {len(mi)}")
    print(f"  passaram como SOURCE_EXPLICIT (o dano)   : {len(se)}")
    for grupo, nome in ((se, "SOURCE_EXPLICIT — PROPAGADA COMO FONTE"),
                        (mi, "MODEL_INFERENCE — rotulada corretamente")):
        if not grupo:
            continue
        print(f"\n### {nome} ({len(grupo)})")
        for h in grupo:
            det = (f"negações na claim {h['negacoes_na_claim']}, zero na quote"
                   if h["tipo"] == "NEGACAO_PERDIDA"
                   else f"'{h['nome_na_claim']}' ↔ '{h['quase_igual_na_quote']}' "
                        f"(sim {h['similaridade']})")
            print(f"\n[{h['id']}] {h['tipo']} · {det}")
            print(f"   claim: {h['claim']}")
            print(f"   quote: {h['quote'][:200].replace(chr(10), ' ')}")
    return {"n": len(rows), "hits": len(hits), "mi": len(mi), "se": len(se),
            "detalhe": hits}


def main() -> int:
    alvos = [
        (DRIVE / "Course-to-Skill-Claude/pilots/PILOT-001-v2/EVIDENCE.jsonl",
         "PILOT-001-v2 (retroativo)"),
        (DRIVE / "Course-to-Skill-Claude/pilots/PILOT-002-v2/EVIDENCE.jsonl",
         "PILOT-002-v2"),
    ]
    out = {}
    for p, lbl in alvos:
        if not p.is_file():
            print(f"\n[{lbl}] AUSENTE ainda: {p}")
            continue
        out[lbl] = scan(p, lbl)
        print()
    if len(out) == 2:
        print("=" * 88)
        print("RESUMO")
        print("=" * 88)
        for lbl, r in out.items():
            print(f"  {lbl:<28} {r['hits']}/{r['n']} divergências · "
                  f"{r['se']} como SOURCE_EXPLICIT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
