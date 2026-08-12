#!/usr/bin/env python3
"""Segunda âncora do detector de nome corrompido: quase-igual MINÚSCULO.

A âncora original exige que o quase-igual na quote esteja CAPITALIZADO — nome
próprio sobrevive à tradução capitalizado, palavra comum não. Ela existe porque
sem ela o detector casava 'Times' com 'creative'.

O custo dela é recall: o ASR MINUSCULIZA. 'Claude Code' vira 'clawed code',
'claw code', 'cloud'. O nome continua sendo nome; só perdeu a maiúscula.

Conserto: um SEGUNDO caminho, mais estreito para compensar a âncora perdida —
similaridade >= 0.78 (contra 0.60), o candidato tem de ser CamelCase ou nome
próprio de >=4 letras NA CLAIM, e o quase-igual tem de ser palavra inteira.
Testado contra o corpus inteiro para medir o lixo que ele deixa entrar.
"""
from __future__ import annotations
import difflib, json, re
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CAMEL = re.compile(r"\b[A-Z][a-z]+[A-Z][A-Za-z]*\b")
PROPER = re.compile(r"\b[A-Z][A-Za-z]{3,}\b")
STOP = {"Para", "Como", "Quando", "Depois", "Antes", "Isso", "Esse", "Essa", "Ao",
        "Uma", "Cada", "Todo", "Toda", "Não", "Mas", "Sem", "Com", "Este", "Esta",
        "Aqui", "Onde", "Além", "Após", "Pelo", "Pela", "Nesse", "Nessa", "Caso"}
FLOOR2 = 0.78


def corrupted_name_lower(claim: str, quote: str):
    """Segundo caminho: quase-igual em MINÚSCULA, com piso de similaridade alto."""
    words = re.findall(r"\b[\w'\-]+\b", quote)
    ql = quote.lower()
    for ent in sorted(set(CAMEL.findall(claim)) | set(PROPER.findall(claim))):
        if ent in STOP or ent.lower() in ql:
            continue
        if re.sub(r"[\s\-]", "", ent.lower()) in re.sub(r"[\s\-]", "", ql):
            continue
        best, score = None, 0.0
        for k in range(len(words)):
            for j in (1, 2):
                cand = " ".join(words[k:k + j])
                if len(cand) < 4:
                    continue
                r = difflib.SequenceMatcher(None, ent.lower(), cand.lower()).ratio()
                if r > score:
                    best, score = cand, r
        if best and FLOOR2 <= score < 0.95:
            return {"tipo": "NOME_CORROMPIDO_MINUSCULO", "nome_na_claim": ent,
                    "quase_igual_na_quote": best, "similaridade": round(score, 2)}
    return None


def main() -> int:
    out = {}
    for pid in ("PILOT-001-v2", "PILOT-002-v2"):
        p = DRIVE / f"Course-to-Skill-Claude/pilots/{pid}/EVIDENCE.jsonl"
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        hits = []
        for r in rows:
            d = corrupted_name_lower(r["claim"], r["source_excerpt"]["quote"])
            if d:
                hits.append({**d, "evidence_id": r["evidence_id"],
                             "status": r["epistemic_status"],
                             "claim": r["claim"][:100],
                             "quote": r["source_excerpt"]["quote"][:120]})
        out[pid] = hits
        print(f"\n=== {pid} — segundo caminho, {len(hits)} disparos em {len(rows)} ===")
        from collections import Counter
        print("  pares mais frequentes:",
              Counter((h["nome_na_claim"], h["quase_igual_na_quote"]) for h in hits).most_common(8))
        print("  amostra para julgar LIXO vs ACERTO:")
        for h in hits[:10]:
            print(f"    [{h['evidence_id']}] '{h['nome_na_claim']}' ↔ "
                  f"'{h['quase_igual_na_quote']}' (sim {h['similaridade']}) "
                  f"{h['status']}")
    Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/detector2.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
