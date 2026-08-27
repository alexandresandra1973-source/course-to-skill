#!/usr/bin/env python3
"""Executa MECANICAMENTE os recortes que a Skill pediu. Nenhuma escolha minha."""
from __future__ import annotations
import csv, io, json
from pathlib import Path
CSV = Path("/mnt/g/Meu Drive/Chat GPT/MTX-Google-Ads-Export")
OUT = Path("/home/mtx/course-to-skill-claude/_mirror/pilots/PILOT-003-v2/apply/p003-recortes.json")


def load(p):
    t = p.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    hdr = next(i for i, l in enumerate(t) if l.startswith(("Termo de pesquisa", "Status da palavra")))
    return list(csv.DictReader(io.StringIO("\n".join(t[hdr:]))))


def num(s):
    try: return float(str(s).replace(".", "").replace(",", ".").strip() or 0)
    except Exception: return 0.0


st = load(CSV/"Relatório de termos de pesquisa.csv")
kw = load(CSV/"Relatório de palavras-chave da rede de pesquisa.csv")
C = lambda r, *n: next((r[k] for k in r if k and any(x.lower() in k.lower() for x in n)), "")
res = {}

# B — vencedores a promover (Conversões>0 E não adicionada/excluída)
b = [r for r in st if num(C(r, "Conversões")) > 0
     and C(r, "Adicionada/excluída").strip().lower() in ("", "nenhum", "nenhum(a)", "none", " --")]
b.sort(key=lambda r: (-num(C(r, "Conversões")), num(C(r, "Custo / conv"))))
res["B_vencedores"] = [{"termo": C(r, "Termo de pesquisa"), "campanha": C(r, "Campanha"),
                        "conv": num(C(r, "Conversões")), "custo": num(C(r, "Custo")),
                        "cpa": num(C(r, "Custo / conv"))} for r in b[:50]]

# C — desperdício (Conversões=0 E Custo>0)
c = [r for r in st if num(C(r, "Conversões")) == 0 and num(C(r, "Custo")) > 0]
c.sort(key=lambda r: -num(C(r, "Custo")))
res["C_desperdicio"] = {"n": len(c), "custo_total": round(sum(num(C(r, "Custo")) for r in c), 2),
    "top": [{"termo": C(r, "Termo de pesquisa"), "campanha": C(r, "Campanha"),
             "custo": num(C(r, "Custo")), "cliques": num(C(r, "Cliques"))} for r in c[:40]]}

# D — termos do PMax
d = [r for r in st if "perf" in C(r, "Tipo de corresp").lower()]
d.sort(key=lambda r: -num(C(r, "Custo")))
res["D_pmax"] = {"n": len(d), "custo": round(sum(num(C(r, "Custo")) for r in d), 2),
    "top": [{"termo": C(r, "Termo de pesquisa"), "custo": num(C(r, "Custo")),
             "conv": num(C(r, "Conversões"))} for r in d[:25]]}

# E — flywheel de negativas
from collections import Counter
res["E_negativas"] = dict(Counter(C(r, "Adicionada/excluída").strip() or "(vazio)" for r in st))

# F — distribuição por tipo de correspondência
agg = {}
for r in kw:
    k = (C(r, "Tipo de corresp"), C(r, "Campanha"))
    a = agg.setdefault(k, {"custo": 0, "conv": 0, "valor": 0, "n": 0})
    a["custo"] += num(C(r, "Custo")); a["conv"] += num(C(r, "Conversões"))
    a["valor"] += num(C(r, "Valor conv")); a["n"] += 1
res["F_match"] = [{"tipo": k[0], "campanha": k[1], **v} for k, v in
                  sorted(agg.items(), key=lambda x: -x[1]["custo"])]

# G — keywords sem conversão
g = [r for r in kw if num(C(r, "Conversões")) == 0 and num(C(r, "Custo")) > 0]
g.sort(key=lambda r: -num(C(r, "Custo")))
res["G_kw_sem_conv"] = {"n": len(g), "custo": round(sum(num(C(r, "Custo")) for r in g), 2),
    "top": [{"kw": C(r, "Palavra-chave"), "match": C(r, "Tipo de corresp"),
             "campanha": C(r, "Campanha"), "custo": num(C(r, "Custo"))} for r in g[:30]]}

# I — congruência de destino
u = {}
for r in kw:
    k = C(r, "URL final") or "(vazio)"
    a = u.setdefault(k, {"custo": 0, "conv": 0, "n": 0})
    a["custo"] += num(C(r, "Custo")); a["conv"] += num(C(r, "Conversões")); a["n"] += 1
res["I_urls"] = [{"url": k[:90], **v} for k, v in sorted(u.items(), key=lambda x: -x[1]["custo"])[:20]]

OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"B vencedores      : {len(res['B_vencedores'])}")
print(f"C desperdício     : {res['C_desperdicio']['n']} termos, R$ {res['C_desperdicio']['custo_total']}")
print(f"D PMax            : {res['D_pmax']['n']} termos, R$ {res['D_pmax']['custo']}")
print(f"E negativas       : {res['E_negativas']}")
print(f"F match types     : {len(res['F_match'])} combinações")
print(f"G kw sem conversão: {res['G_kw_sem_conv']['n']}, R$ {res['G_kw_sem_conv']['custo']}")
print(f"I URLs            : {len(res['I_urls'])}")
print(f"\ntop desperdício:")
for x in res["C_desperdicio"]["top"][:6]: print(f"   R$ {x['custo']:>7.2f}  {x['termo'][:56]}")
