#!/usr/bin/env python3
"""Aplicação da Skill do PILOT-003 — ETAPA 1: a Skill decide o que olhar.

Contexto da Skill: os cinco arquivos e NADA MAIS do projeto. Recebe o relatório
de campanha inteiro (10 linhas) e só o CABEÇALHO dos outros dois, com contagem.

A Skill decide o recorte. Se o pedido vier ambíguo, eu reporto e paro — resolver
seria eu encontrando o achado.
"""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import anthropic

S = Path("/home/mtx/course-to-skill-claude/_mirror/pilots/PILOT-003-v2/skill")
CSV = Path("/mnt/g/Meu Drive/Chat GPT/MTX-Google-Ads-Export")
OUT = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-apply1.json")

FILES = ["SKILL.md", "knowledge/runtime-policy.yaml", "knowledge/decision-rules.yaml",
         "knowledge/workflows.yaml", "manifest.yaml"]
TASK = ("Avalie esta conta do Google Ads segundo a metodologia do curso.\n\n"
        "Tenho três exportações. Abaixo vai o relatório de campanha INTEIRO e, dos "
        "outros dois, apenas o cabeçalho com a contagem de linhas.\n\n"
        "Diga o que a metodologia manda examinar e QUAL RECORTE dos dois relatórios "
        "grandes você precisa. Seja mecanicamente executável no pedido: coluna, "
        "critério, limiar, ordenação. Se precisar de dado que não está nas três "
        "exportações, peça explicitamente e diga qual regra exige.")


def read(p, n=None):
    t = p.read_text(encoding="utf-8-sig", errors="replace")
    ls = [l for l in t.splitlines() if l.strip()]
    return ("\n".join(ls) if n is None else "\n".join(ls[:n])), len(ls)


def main() -> int:
    bundle = []
    for f in FILES:
        p = S / f
        bundle.append(f"=== {f} ===\n{p.read_text(encoding='utf-8')}")
    camp, n_camp = read(CSV/"Relatório de campanha.csv")
    kw, n_kw = read(CSV/"Relatório de palavras-chave da rede de pesquisa.csv", 3)
    st, n_st = read(CSV/"Relatório de termos de pesquisa.csv", 3)
    payload = (TASK +
               f"\n\n=== Relatório de campanha.csv ({n_camp} linhas, INTEIRO) ===\n{camp}"
               f"\n\n=== Relatório de palavras-chave da rede de pesquisa.csv "
               f"({n_kw} linhas — só cabeçalho) ===\n{kw}"
               f"\n\n=== Relatório de termos de pesquisa.csv "
               f"({n_st} linhas — só cabeçalho) ===\n{st}")
    system = ("Você está executando a Skill abaixo. Os arquivos presentes no bundle "
              "são exatamente estes: " + ", ".join(FILES) + "\n\n" + "\n\n".join(bundle))
    print(f"bundle: {len(system)} chars · payload: {len(payload)} chars")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    with client.messages.stream(model="claude-opus-5", max_tokens=32000,
                                system=system,
                                messages=[{"role": "user", "content": payload}]) as s:
        m = s.get_final_message()
    tipos = [b.type for b in m.content]
    print("blocos devolvidos:", tipos, "· stop_reason:", m.stop_reason)
    ans = "".join(getattr(b, "text", "") for b in m.content if b.type == "text")
    print("=" * 80); print(ans); print("=" * 80)
    OUT.write_text(json.dumps({"answer": ans, "sha256": hashlib.sha256(ans.encode()).hexdigest(),
                               "usage": {"in": m.usage.input_tokens, "out": m.usage.output_tokens},
                               "bundle_files": FILES}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"\ntokens {m.usage.input_tokens}/{m.usage.output_tokens} · sha {hashlib.sha256(ans.encode()).hexdigest()[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
