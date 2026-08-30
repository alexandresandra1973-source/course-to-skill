#!/usr/bin/env python3
"""PILOT-MS-000B — consolidacao, KILL checks e relatorio.

Todo numero e emitido aqui a partir de out/runs.json, out/source-packages.json e
out/COMPILE-TRACE.jsonl. Contagem manual: proibida.
"""
from __future__ import annotations
import json, pathlib, sys, hashlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).parent / "lib"))
import ms000b as M

P = pathlib.Path(__file__).parent; OUT = P / "out"
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

runs  = json.loads((OUT/"runs.json").read_text(encoding="utf-8"))
pkgs  = json.loads((OUT/"source-packages.json").read_text(encoding="utf-8"))
cands = json.loads((OUT/"source-local-candidates.json").read_text(encoding="utf-8"))
trace = [json.loads(l) for l in (OUT/"COMPILE-TRACE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

R = {}
# ---------------- KILL-1: camada selada intacta
R["kill1"] = {"esperado": {"FULL": M.FULL_SHA, "CUT": M.CUT_SHA, "EVIDENCE": M.EV_SHA},
              "real": {"FULL": sha(M.FULL), "CUT": sha(M.CUT), "EVIDENCE": sha(M.EVID)}}
R["kill1"]["ok"] = R["kill1"]["esperado"] == R["kill1"]["real"]

# ---------------- identidade
ids = collections.Counter()
qual = set()
for k in ("A","B"):
    for it in pkgs[k]["items"]:
        ids[it["local_id"]] += 1
        qual.add((pkgs[k]["source_package_hash"], it["local_id"]))
naked_refs = 0
for run, d in runs.items():
    for k in ("A","B"):
        for c in d["sealed"][k]:
            for q in c["qualified_refs"]:
                if not q[0] or len(q) != 2: naked_refs += 1
R["identity"] = {"local_ids_total": sum(ids.values()),
                 "local_ids_colidindo_nus": sorted([i for i,n in ids.items() if n>1])[:3],
                 "colisoes_nuas": sum(1 for n in ids.values() if n>1),
                 "identidades_qualificadas_distintas": len(qual),
                 "pkg_hash_A": pkgs["A"]["source_package_hash"],
                 "pkg_hash_B": pkgs["B"]["source_package_hash"],
                 "pkg_hashes_distintos": pkgs["A"]["source_package_hash"] != pkgs["B"]["source_package_hash"],
                 "referencias_cross_package_nuas": naked_refs}
R["identity"]["ok"] = (R["identity"]["colisoes_nuas"] > 0
                       and R["identity"]["identidades_qualificadas_distintas"] == R["identity"]["local_ids_total"]
                       and R["identity"]["pkg_hashes_distintos"] and naked_refs == 0)

# ---------------- proveniencia
prov = {"claims": 0, "resolve": 0, "quebradas": []}
for run, d in runs.items():
    for k in ("A","B"):
        valid = {i["local_id"]: i for i in pkgs[k]["items"]}
        anc = {a["anchor_id"]: a for a in pkgs[k]["anchors"]}
        for c in d["sealed"][k]:
            prov["claims"] += 1
            ok = bool(c["evidence_refs"]) and all(
                r in valid and valid[r]["anchor_id"] in anc
                and anc[valid[r]["anchor_id"]]["LOCATED_IN"] == "PASS"
                and anc[valid[r]["anchor_id"]]["slice_sha256"] == pkgs[k]["profile"]["provenance_chain"]["CHAPTER_SLICE"]
                and pkgs[k]["profile"]["provenance_chain"]["slice_derived_from"] == M.CUT_SHA
                for r in c["evidence_refs"])
            if ok: prov["resolve"] += 1
            else: prov["quebradas"].append(c["claim_id"])
prov["pct"] = prov["resolve"]/prov["claims"]*100 if prov["claims"] else None
prov["ok"] = prov["claims"] > 0 and not prov["quebradas"]
R["provenance"] = prov

# ---------------- claims raw x sealed x entailment
cl = {}
for run, d in runs.items():
    raw = sum(len(d["raw"][k]) for k in ("A","B"))
    rej = sum(len(d["rejected"][k]) for k in ("A","B"))
    sl  = sum(len(d["sealed"][k]) for k in ("A","B"))
    ent = sum(1 for k in ("A","B") for c in d["sealed"][k] if c.get("entailed_by")=="ENTAILED")
    motivos = collections.Counter(r["reject_reason"] for k in ("A","B") for r in d["rejected"][k])
    cl[run] = {"raw_propostas": raw, "rejeitadas_antes_do_selo": rej, "seladas": sl,
               "seladas_entailed": ent, "motivos_de_rejeicao": dict(motivos),
               "por_pacote": {k: {"raw": len(d["raw"][k]), "sealed": len(d["sealed"][k])} for k in ("A","B")}}
R["claims"] = cl
R["kill3"] = {"seladas_totais": sum(v["seladas"] for v in cl.values()),
              "seladas_entailed": sum(v["seladas_entailed"] for v in cl.values())}
R["kill3"]["ok"] = R["kill3"]["seladas_totais"] == R["kill3"]["seladas_entailed"]

# ---------------- variancia / KILL-2
seal = [cl[r]["seladas"] for r in sorted(cl)]
R["variance"] = {"seladas_por_run": {r: cl[r]["seladas"] for r in sorted(cl)},
                 "raw_por_run": {r: cl[r]["raw_propostas"] for r in sorted(cl)},
                 "max": max(seal), "min": min(seal),
                 "razao_max_min": (max(seal)/min(seal)) if min(seal) else None,
                 "teto_medido": 1.5}
R["variance"]["ok"] = bool(min(seal)) and (max(seal)/min(seal)) <= 1.5
# sobreposicao de texto normalizado entre runs
sets = {r: {M.norm(c["text"]) for k in ("A","B") for c in runs[r]["sealed"][k]} for r in sorted(runs)}
rs = sorted(sets)
R["variance"]["sobreposicao"] = {f"{a}∩{b}": len(sets[a]&sets[b]) for i,a in enumerate(rs) for b in rs[i+1:]}
R["variance"]["nucleo_comum_3_runs"] = len(set.intersection(*sets.values())) if len(sets)==3 else None

# ---------------- workflow preservation
wp = {r: runs[r]["workflow_preservation"] for r in runs}
R["workflow"] = {"por_run": wp,
                 "ok": all(wp[r][k]["preservado"] for r in wp for k in ("A","B"))}

# ---------------- blocagem
bl = {r: {kk: vv for kk, vv in runs[r]["blocking"].items() if kk != "pairs"} for r in runs}
R["blocking"] = {"por_run": bl,
                 "controles_ok": all(c["survived"] for r in runs for c in runs[r]["blocking"]["controls"]),
                 "regra": runs[rs[0]]["blocking"]["rule"]}
R["blocking"]["ok"] = R["blocking"]["controles_ok"]

# ---------------- isolamento
R["isolation"] = {"por_run": {r: runs[r]["isolation"] for r in runs}}
R["isolation"]["ok"] = all(runs[r]["isolation"]["falsa_atribuicao"] == 0 for r in runs)

# ---------------- relacoes
R["relations"] = {r: {"identical": len(runs[r]["relations"]["identical"]),
                      "pares_avaliados": runs[r]["relations"]["evaluated_pairs"]} for r in runs}

# ---------------- compile-trace
esperadas = len(runs)*3
R["trace"] = {"chamadas_registradas": len(trace), "chamadas_esperadas": esperadas,
              "hard_cap": 24, "dentro_do_cap": len(trace) <= 24,
              "tokens_input": sum(t["tokens"]["input"] for t in trace),
              "tokens_output": sum(t["tokens"]["output"] for t in trace),
              "modelos_resolvidos": sorted({t["model_resolved"] for t in trace}),
              "particoes": sorted({t["partition"] for t in trace}),
              "prompt_versions": sorted({t["prompt_version"] for t in trace}),
              "campos_completos": all(all(t.get(f) for f in
                 ("run","source","purpose","input_sha256","partition","prompt_version",
                  "model_resolved","output_sha256")) for t in trace)}
R["trace"]["ok"] = (R["trace"]["chamadas_registradas"] == esperadas
                    and R["trace"]["dentro_do_cap"] and R["trace"]["campos_completos"])
# config identica entre runs
cfg = {(t["model_resolved"], json.dumps(t["thinking"]), t["max_tokens"], t["prompt_version"], t["partition"])
       for t in trace if t["purpose"]=="CLAIM_GENERATION"}
R["trace"]["config_claimgen_distintas"] = len(cfg)
R["trace"]["mesma_config_entre_runs"] = len({(m,th,mt,pv) for m,th,mt,pv,_ in cfg}) == 1

# ---------------- veredito
gates = {"KILL-1 camada selada intacta": R["kill1"]["ok"],
         "identidade": R["identity"]["ok"],
         "proveniencia 100%": R["provenance"]["ok"],
         "KILL-3 sealed 100% ENTAILED": R["kill3"]["ok"],
         "KILL-2 variancia <= 1,5x": R["variance"]["ok"],
         "workflow preservado": R["workflow"]["ok"],
         "controles de blocagem": R["blocking"]["ok"],
         "isolamento": R["isolation"]["ok"],
         "COMPILE-TRACE completo": R["trace"]["ok"],
         "config identica entre runs": R["trace"]["mesma_config_entre_runs"]}
R["gates"] = gates
R["classificacao"] = "PILOT_MS_000B_PASS" if all(gates.values()) else "PILOT_MS_000B_FAIL"
(OUT/"summary.json").write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")

L=[];w=L.append
w("# PILOT-MS-000B — RELATÓRIO"); w("")
w("**Gerado integralmente por `consolidate.py`.** Nenhum número digitado à mão."); w("")
w(f"- Opening Record: `{sha(P/'OPENING-RECORD.md')}`")
w(f"- modelo resolvido: {', '.join(R['trace']['modelos_resolvidos'])} · thinking disabled")
w(f"- chamadas: **{R['trace']['chamadas_registradas']}** de cap **{R['trace']['hard_cap']}**")
w("")
w("## 1. Portões"); w(""); w("| portão | resultado |"); w("|---|---|")
for k,v in gates.items(): w(f"| {k} | {'**OK**' if v else '**FALHOU**'} |")
w("")
w("## 2. Source Packages"); w("")
w("| pacote | cap | slice sha256 | package hash | itens | LOCATED_IN | REPRODUCED_FROM |")
w("|---|---|---|---|---|---|---|")
for k in ("A","B"):
    a=pkgs[k]["anchors"]
    w(f"| {k} | {pkgs[k]['profile']['chapter_n']} | `{pkgs[k]['profile']['provenance_chain']['CHAPTER_SLICE'][:16]}…` | "
      f"`{pkgs[k]['source_package_hash'][:16]}…` | {len(pkgs[k]['items'])} | "
      f"{sum(1 for x in a if x['LOCATED_IN']=='PASS')}/{len(a)} | "
      f"{sum(1 for x in a if x['REPRODUCED_FROM']=='PASS')}/{len(a)} |")
w("")
w("## 3. Identidade"); w("")
w(f"- `local_id` totais: **{R['identity']['local_ids_total']}** · colisões nuas: **{R['identity']['colisoes_nuas']}** (deliberadas)")
w(f"- identidades qualificadas distintas: **{R['identity']['identidades_qualificadas_distintas']}**")
w(f"- package hashes distintos: **{R['identity']['pkg_hashes_distintos']}**")
w(f"- **referências cross-package nuas: {R['identity']['referencias_cross_package_nuas']}**")
w("")
w("## 4. Claims — raw × selada × entailed"); w("")
w("| run | raw propostas | rejeitadas antes do selo | seladas | seladas ENTAILED |")
w("|---|---|---|---|---|")
for r in sorted(cl): w(f"| {r} | {cl[r]['raw_propostas']} | {cl[r]['rejeitadas_antes_do_selo']} | {cl[r]['seladas']} | {cl[r]['seladas_entailed']} |")
w("")
w("Motivos de rejeição por run:"); w("")
for r in sorted(cl): w(f"- `{r}`: {cl[r]['motivos_de_rejeicao'] or '—'}")
w("")
w("## 5. Variância entre runs (KILL-2)"); w("")
w(f"- seladas por run: {R['variance']['seladas_por_run']}")
w(f"- máx/mín = **{R['variance']['razao_max_min']:.4f}×** · teto medido **1,5×** → "
  f"{'dentro' if R['variance']['ok'] else '**EXCEDIDO**'}")
w(f"- núcleo comum aos 3 runs: **{R['variance']['nucleo_comum_3_runs']}** claims idênticas normalizadas")
w(f"- sobreposição par a par: {R['variance']['sobreposicao']}")
w("")
w("## 6. Preservação de workflow (DESIGN C)"); w("")
w("| run | pacote | workflows | steps | struct source | struct fusion | preservado |")
w("|---|---|---|---|---|---|---|")
for r in sorted(wp):
    for k in ("A","B"):
        x=wp[r][k]
        w(f"| {r} | {k} | {x['workflows']} | {x['steps']} | `{x['struct_source'][:12]}…` | `{x['struct_fusion'][:12]}…` | "
          f"{'**OK**' if x['preservado'] else '**FALHOU**'} |")
w("")
w("## 7. Blocagem"); w(""); w(f"Regra declarada antes: `{R['blocking']['regra']}`"); w("")
w("| run | pares possíveis | sobreviventes | redução | controles positivos |")
w("|---|---|---|---|---|")
for r in sorted(bl):
    c=runs[r]["blocking"]["controls"]
    w(f"| {r} | {bl[r]['possible']} | {bl[r]['survived']} | {bl[r]['reduction_pct']:.2f}% | "
      f"{sum(1 for x in c if x['survived'])}/{len(c)} |")
w("")
w("## 8. Isolamento"); w(""); w("| run | tokens exclusivos A | exclusivos B | falsa atribuição |"); w("|---|---|---|---|")
for r in sorted(runs):
    i=runs[r]["isolation"]
    w(f"| {r} | {i['exclusivos_A']} | {i['exclusivos_B']} | **{i['falsa_atribuicao']}** |")
w("")
w("## 9. Relações executadas"); w("")
w("Só `IDENTICAL` mecânica (`D15`). `UNRELATED` é default, não rótulo."); w("")
w("| run | pares avaliados | IDENTICAL |"); w("|---|---|---|")
for r in sorted(R["relations"]): w(f"| {r} | {R['relations'][r]['pares_avaliados']} | {R['relations'][r]['identical']} |")
w("")
w("## 10. COMPILE-TRACE"); w("")
w(f"- chamadas registradas **{R['trace']['chamadas_registradas']}** de esperadas **{R['trace']['chamadas_esperadas']}**")
w(f"- tokens: entrada **{R['trace']['tokens_input']}** · saída **{R['trace']['tokens_output']}**")
w(f"- campos completos em todas: **{R['trace']['campos_completos']}**")
w(f"- config idêntica entre runs: **{R['trace']['mesma_config_entre_runs']}**")
w(f"- partições: {R['trace']['particoes']}")
w("")
w("## 11. KILL checks"); w("")
w(f"- **KILL-1** camada selada byte-idêntica: {'OK' if R['kill1']['ok'] else '**VIOLADO**'}")
w(f"- **KILL-2** variância {R['variance']['razao_max_min']:.4f}× ≤ 1,5×: {'OK' if R['variance']['ok'] else '**VIOLADO**'}")
w(f"- **KILL-3** {R['kill3']['seladas_entailed']}/{R['kill3']['seladas_totais']} seladas ENTAILED: {'OK' if R['kill3']['ok'] else '**VIOLADO**'}")
w(""); w("## 12. Classificação"); w(""); w(f"# `{R['classificacao']}`")
(OUT/"PILOT-MS-000B-REPORT.md").write_text("\n".join(L)+"\n", encoding="utf-8")
print(R["classificacao"])
for k,v in gates.items(): print(f"  {'OK  ' if v else 'FALHA'} {k}")
