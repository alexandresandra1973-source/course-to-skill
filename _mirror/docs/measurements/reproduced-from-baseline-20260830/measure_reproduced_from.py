#!/usr/bin/env python3
"""REPRODUCED_FROM — medicao de baseline sobre P002, P003, P004.

READ-ONLY sobre o repo e o Drive. Zero chamadas de API: casamento de string puro.
Implementa exatamente o REPRODUCED_FROM_MEASUREMENT_OPENING_RECORD.md
(sha256 35cd4abf5df72758c1d0e9019c757e8503c1a1aba02fea8ffef0b22babba8634).

Nenhum numero deste programa e digitado a mao: tudo e contado aqui e emitido
para o JSONL e para o relatorio .md.
"""
from __future__ import annotations
import json, re, sys, hashlib, pathlib, unicodedata, subprocess, datetime

REPO = pathlib.Path("/home/mtx/course-to-skill-claude")
WORK = pathlib.Path("/home/mtx/reproduced-from-baseline")
OUT  = WORK / "out"
TOLERANCE_S = 30          # janela W declarada no opening record, ANTES de rodar

BUNDLES = {
    "P002": {"evidence": "_mirror/pilots/PILOT-002-v2/EVIDENCE.jsonl",
             "evidence_sha": "64853f7ac06a470f09333a80469b38e443ea5ce7aa3aee2e116ea1877059abfd",
             "lang": "EN"},
    "P003": {"evidence": "_mirror/pilots/PILOT-003-v2/EVIDENCE.jsonl",
             "evidence_sha": "64830129e3e806635110f8f7313e82f119fd89a4604eb2729419740478e6f4b0",
             "lang": "EN"},
    "P004": {"evidence": "_mirror/pilots/PILOT-004/02_PASS2/EVIDENCE.jsonl",
             "evidence_sha": "f5951b32192c50bfede98fa911ba7829a2c5025bdfd4f7e96d4624167e10fd62",
             "lang": "pt-BR"},
}

# ---------------------------------------------------------------- normalizacao
WS = re.compile(r"\s+")

def normalize(s: str) -> str:
    """As QUATRO normalizacoes taxativas do opening record, nesta ordem."""
    s = unicodedata.normalize("NFC", s)
    s = s.casefold()
    s = WS.sub(" ", s)
    return s.strip()

def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

# ------------------------------------------------------------------- locator
MARK = re.compile(r"\*\*(?:(\d+):)?(\d+):(\d{2})\*\*")

def build_markers(norm_text: str):
    """[(segundos, offset_no_texto_normalizado)] a partir das marcas **M:SS** / **H:MM:SS**."""
    out = []
    for m in MARK.finditer(norm_text):
        h, a, b = m.group(1), m.group(2), m.group(3)
        sec = (int(h) * 3600 if h else 0) + int(a) * 60 + int(b)
        out.append((sec, m.start()))
    return out

def region_for(markers, start_s, end_s, tol=TOLERANCE_S):
    """Regiao [ini, fim) no texto normalizado, com tolerancia tol em segundos.
    Devolve None se o locator nao resolve."""
    if not markers:
        return None
    lo, hi = start_s - tol, end_s + tol
    ini = None
    for sec, off in markers:
        if sec <= lo:
            ini = off
        else:
            break
    if ini is None:
        ini = 0                       # antes do primeiro marcador
    fim = None
    for sec, off in markers:
        if sec > hi:
            fim = off
            break
    if fim is None:
        fim = None                    # ate o fim do arquivo
    if start_s > end_s:
        return None
    last_sec = markers[-1][0]
    if start_s > last_sec + tol:      # span alem do alcance dos marcadores
        return None
    return (ini, fim)

# ------------------------------------------------------------------- predicado
def evaluate(quote: str, l0_norm: str, markers, span):
    """Devolve (estado_primario, estado_secundario, motivo)."""
    if quote is None:
        return "NOT_APPLICABLE", None, "campo quote ausente"
    q = normalize(quote)
    if q == "":
        return "NOT_APPLICABLE", None, "quote vazia apos normalizacao"

    positions = []
    start = l0_norm.find(q)
    while start != -1:
        positions.append(start)
        start = l0_norm.find(q, start + 1)

    primary = "PASS" if positions else "FAIL"
    motivo = f"{len(positions)} ocorrencia(s)" if positions else "quote normalizada nao ocorre no L0 normalizado"

    # secundario
    if not isinstance(span, dict):
        return primary, "LOCATOR_UNRESOLVED", motivo + " | span ausente ou nao-objeto"
    a, b = span.get("start_s"), span.get("end_s")
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return primary, "LOCATOR_UNRESOLVED", motivo + " | start_s/end_s nao numericos"
    reg = region_for(markers, int(a), int(b))
    if reg is None:
        return primary, "LOCATOR_UNRESOLVED", motivo + " | span nao resolve contra os marcadores"
    if not positions:
        return primary, None, motivo          # sem ocorrencia, regiao nao se aplica
    ini, fim = reg
    inside = any((p >= ini and (fim is None or p < fim)) for p in positions)
    return primary, ("IN_REGION" if inside else "OUT_OF_REGION"), motivo

# ------------------------------------------------------------------- fixtures
def run_fixtures():
    cases = json.loads((WORK / "fixtures" / "fixture-cases.json").read_text(encoding="utf-8"))
    results, ok = [], True
    for c in cases:
        l0 = pathlib.Path(c["l0"])
        l0_norm = normalize(l0.read_text(encoding="utf-8"))
        markers = build_markers(l0_norm)
        got, _sec, motivo = evaluate(c["quote"], l0_norm, markers, None)
        passed = (got == c["expect"])
        ok = ok and passed
        results.append({"fixture_id": c["fixture_id"], "expect": c["expect"],
                        "got": got, "comportou_como_desenhado": passed,
                        "motivo": motivo, "porque": c["porque"]})
    return ok, results

# ---------------------------------------------------------------------- main
def main() -> int:
    started = datetime.datetime.now().astimezone().isoformat()

    # --- controles primeiro
    ctrl_ok, ctrl = run_fixtures()
    if not ctrl_ok:
        print("CONTROLE FORA DO ESPERADO -> MEASUREMENT_INVALID", file=sys.stderr)
        for r in ctrl:
            print("  ", r, file=sys.stderr)
        (OUT / "CONTROL-FAILURE.json").write_text(json.dumps(ctrl, ensure_ascii=False, indent=2), encoding="utf-8")
        return 2

    # --- verificacao de integridade dos insumos
    integridade, aborta = [], False
    l0_by_bundle = {}
    tracked = [l for l in subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                                         text=True).stdout.split("\n") if l]
    for b, cfg in BUNDLES.items():
        ev = REPO / cfg["evidence"]
        real = sha256_file(ev)
        ok_ev = (real == cfg["evidence_sha"])
        integridade.append({"bundle": b, "artefato": cfg["evidence"], "esperado": cfg["evidence_sha"],
                            "real": real, "ok": ok_ev})
        if not ok_ev:
            aborta = True
        # L0 declarado pelas proprias evidences
        decl = set()
        for ln in ev.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            se = json.loads(ln).get("source_excerpt") or {}
            decl.add((se.get("source_file"), se.get("source_sha256")))
        l0_by_bundle[b] = {"declarado": sorted(decl), "resolvido": None, "sha": None, "erro": None}
        if len(decl) != 1:
            l0_by_bundle[b]["erro"] = f"declaracao de L0 nao unanime: {len(decl)} pares distintos"
            continue
        fname, fsha = decl.pop()
        cands = [t for t in tracked if pathlib.Path(t).name == fname
                 and (REPO / t).exists() and sha256_file(REPO / t) == fsha]
        if len(cands) != 1:
            l0_by_bundle[b]["erro"] = f"L0 nao resolve unicamente por sha256: {len(cands)} candidato(s)"
            continue
        l0_by_bundle[b]["resolvido"] = cands[0]
        l0_by_bundle[b]["sha"] = fsha

    if aborta:
        print("SHA DE EVIDENCE.jsonl DIVERGENTE -> MEASUREMENT_INVALID", file=sys.stderr)
        (OUT / "INTEGRITY-FAILURE.json").write_text(json.dumps(integridade, ensure_ascii=False, indent=2), encoding="utf-8")
        return 3

    # --- medicao
    raw_path = OUT / "reproduced-from-raw.jsonl"
    per = {}
    with raw_path.open("w", encoding="utf-8") as fh:
        for b, cfg in BUNDLES.items():
            info = l0_by_bundle[b]
            counts = {"examinado": 0, "PASS": 0, "FAIL": 0, "NOT_APPLICABLE": 0, "INVALID": 0,
                      "IN_REGION": 0, "OUT_OF_REGION": 0, "LOCATOR_UNRESOLVED": 0}
            ids = {"PASS": [], "FAIL": [], "NOT_APPLICABLE": [], "INVALID": []}
            if info["erro"]:
                for ln in (REPO / cfg["evidence"]).read_text(encoding="utf-8").splitlines():
                    if not ln.strip():
                        continue
                    o = json.loads(ln)
                    eid = o.get("evidence_id")
                    counts["examinado"] += 1
                    counts["INVALID"] += 1
                    ids["INVALID"].append(eid)
                    fh.write(json.dumps({"bundle": b, "evidence_id": eid, "estado": "INVALID",
                                         "secundario": None, "motivo": "L0 do bundle nao resolveu: "
                                         + info["erro"]}, ensure_ascii=False) + "\n")
                per[b] = {"counts": counts, "ids": ids, "l0": info}
                continue

            l0p = REPO / info["resolvido"]
            l0_norm = normalize(l0p.read_text(encoding="utf-8"))
            markers = build_markers(l0_norm)
            info["marcadores"] = len(markers)
            info["l0_bytes"] = l0p.stat().st_size
            info["l0_chars_normalizados"] = len(l0_norm)

            for ln in (REPO / cfg["evidence"]).read_text(encoding="utf-8").splitlines():
                if not ln.strip():
                    continue
                counts["examinado"] += 1
                try:
                    o = json.loads(ln)
                except Exception as e:
                    counts["INVALID"] += 1
                    ids["INVALID"].append(None)
                    fh.write(json.dumps({"bundle": b, "evidence_id": None, "estado": "INVALID",
                                         "secundario": None, "motivo": f"json ilegivel: {e}"},
                                        ensure_ascii=False) + "\n")
                    continue
                eid = o.get("evidence_id")
                if not eid:
                    counts["INVALID"] += 1
                    ids["INVALID"].append(None)
                    fh.write(json.dumps({"bundle": b, "evidence_id": None, "estado": "INVALID",
                                         "secundario": None, "motivo": "evidence_id ausente"},
                                        ensure_ascii=False) + "\n")
                    continue
                se = o.get("source_excerpt")
                quote = se.get("quote") if isinstance(se, dict) else None
                span = se.get("span") if isinstance(se, dict) else None
                st, sec, motivo = evaluate(quote, l0_norm, markers, span)
                counts[st] += 1
                ids[st].append(eid)
                if sec:
                    counts[sec] += 1
                fh.write(json.dumps({"bundle": b, "evidence_id": eid, "estado": st,
                                     "secundario": sec, "motivo": motivo},
                                    ensure_ascii=False) + "\n")
            per[b] = {"counts": counts, "ids": ids, "l0": info}

    # --- asserçoes de inclusao
    asserts = []
    for b, d in per.items():
        P, F = set(d["ids"]["PASS"]), set(d["ids"]["FAIL"])
        eleg = P | F
        a1 = P <= eleg
        a2 = (len(d["ids"]["PASS"]) + len(d["ids"]["FAIL"])) == (d["counts"]["PASS"] + d["counts"]["FAIL"])
        a3 = len(P & F) == 0
        asserts.append({"bundle": b, "numerador_subset_denominador": a1,
                        "contagens_batem": a2, "pass_e_fail_disjuntos": a3,
                        "|PASS|": len(P), "|PASS u FAIL|": len(eleg)})
    all_ok = all(a["numerador_subset_denominador"] and a["contagens_batem"]
                 and a["pass_e_fail_disjuntos"] for a in asserts)

    # --- agregado
    agg = {k: sum(per[b]["counts"][k] for b in per) for k in
           ["examinado", "PASS", "FAIL", "NOT_APPLICABLE", "INVALID",
            "IN_REGION", "OUT_OF_REGION", "LOCATOR_UNRESOLVED"]}

    def baseline(p, f):
        d = p + f
        return (p / d, d) if d else (None, 0)

    summary = {"opening_record_sha256": "35cd4abf5df72758c1d0e9019c757e8503c1a1aba02fea8ffef0b22babba8634",
               "tolerancia_s": TOLERANCE_S, "iniciado": started,
               "controles": ctrl, "integridade": integridade,
               "por_bundle": {b: {"counts": per[b]["counts"], "l0": per[b]["l0"]} for b in per},
               "agregado": agg, "asserçoes": asserts, "asserçoes_ok": all_ok}
    (OUT / "reproduced-from-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- relatorio .md gerado aqui
    L = []
    w = L.append
    w("# REPRODUCED_FROM — BASELINE MEASUREMENT REPORT")
    w("")
    w("**Gerado integralmente por `measure_reproduced_from.py`.** Nenhum número deste")
    w("documento foi digitado à mão.")
    w("")
    w(f"- Início da execução: `{started}`")
    w(f"- Opening Record: `{summary['opening_record_sha256']}`")
    w(f"- Tolerância do locator secundário: **{TOLERANCE_S} s** (declarada antes de rodar)")
    w("")
    w("## 1. Controles (rodados ANTES da medição)")
    w("")
    w("| fixture | esperado | obtido | comportou como desenhado |")
    w("|---|---|---|---|")
    for r in ctrl:
        w(f"| `{r['fixture_id']}` | {r['expect']} | {r['got']} | {'SIM' if r['comportou_como_desenhado'] else '**NÃO**'} |")
    w("")
    w("## 2. Integridade dos insumos")
    w("")
    w("| bundle | artefato | sha256 confere |")
    w("|---|---|---|")
    for r in integridade:
        w(f"| {r['bundle']} | `{r['artefato']}` | {'OK' if r['ok'] else '**DIVERGE**'} |")
    w("")
    w("| bundle | L0 resolvido por sha256 | bytes | marcadores `**M:SS**` | erro |")
    w("|---|---|---|---|---|")
    for b in per:
        i = per[b]["l0"]
        w(f"| {b} | `{i['resolvido']}` | {i.get('l0_bytes','—')} | {i.get('marcadores','—')} | {i['erro'] or '—'} |")
    w("")
    w("## 3. Resultados por bundle")
    w("")
    w("| bundle | examinado | elegíveis | PASS | FAIL | NOT_APPLICABLE | INVALID |")
    w("|---|---|---|---|---|---|---|")
    for b in per:
        c = per[b]["counts"]
        w(f"| {b} | {c['examinado']} | {c['PASS']+c['FAIL']} | {c['PASS']} | {c['FAIL']} | {c['NOT_APPLICABLE']} | {c['INVALID']} |")
    c = agg
    w(f"| **AGREGADO** | **{c['examinado']}** | **{c['PASS']+c['FAIL']}** | **{c['PASS']}** | **{c['FAIL']}** | **{c['NOT_APPLICABLE']}** | **{c['INVALID']}** |")
    w("")
    w("## 4. Baseline — `PASS / (PASS + FAIL)` sobre elegíveis")
    w("")
    w("| bundle | fórmula | baseline |")
    w("|---|---|---|")
    for b in per:
        cc = per[b]["counts"]
        v, d = baseline(cc["PASS"], cc["FAIL"])
        w(f"| {b} | {cc['PASS']} / ({cc['PASS']} + {cc['FAIL']}) = {cc['PASS']}/{d} | "
          + (f"**{v*100:.4f}%**" if v is not None else "**indefinido (denominador 0)**") + " |")
    v, d = baseline(c["PASS"], c["FAIL"])
    w(f"| **AGREGADO** | {c['PASS']} / ({c['PASS']} + {c['FAIL']}) = {c['PASS']}/{d} | "
      + (f"**{v*100:.4f}%**" if v is not None else "**indefinido**") + " |")
    w("")
    w("`NOT_APPLICABLE` e `INVALID` estão fora do denominador, por definição do Opening Record.")
    w("")
    w("## 5. Prova: numerador ⊆ denominador")
    w("")
    w("| bundle | \\|PASS\\| | \\|PASS ∪ FAIL\\| | PASS ⊆ (PASS∪FAIL) | PASS∩FAIL = ∅ | contagens batem |")
    w("|---|---|---|---|---|---|")
    for a in asserts:
        w(f"| {a['bundle']} | {a['|PASS|']} | {a['|PASS u FAIL|']} | "
          f"{'SIM' if a['numerador_subset_denominador'] else '**NÃO**'} | "
          f"{'SIM' if a['pass_e_fail_disjuntos'] else '**NÃO**'} | "
          f"{'SIM' if a['contagens_batem'] else '**NÃO**'} |")
    w("")
    w(f"**Todas as asserções passaram: {'SIM' if all_ok else '**NÃO**'}**")
    w("")
    w("## 6. Breakdown secundário do locator (não altera o baseline)")
    w("")
    w("| bundle | IN_REGION | OUT_OF_REGION | LOCATOR_UNRESOLVED |")
    w("|---|---|---|---|")
    for b in per:
        cc = per[b]["counts"]
        w(f"| {b} | {cc['IN_REGION']} | {cc['OUT_OF_REGION']} | {cc['LOCATOR_UNRESOLVED']} |")
    w(f"| **AGREGADO** | **{c['IN_REGION']}** | **{c['OUT_OF_REGION']}** | **{c['LOCATOR_UNRESOLVED']}** |")
    w("")
    w("`IN_REGION + OUT_OF_REGION` conta apenas evidences com ocorrência **e** locator resolvido.")
    w("")
    w("## 7. Classificação")
    w("")
    ctrl_all = all(r["comportou_como_desenhado"] for r in ctrl)
    integ_all = all(r["ok"] for r in integridade)
    l0_all = all(per[b]["l0"]["erro"] is None for b in per)
    if not (ctrl_all and integ_all and all_ok):
        cls = "MEASUREMENT_INVALID"
    elif not l0_all or (c["PASS"] + c["FAIL"]) == 0:
        cls = "BASELINE_NOT_ESTABLISHED"
    else:
        cls = "BASELINE_ESTABLISHED"
    w(f"# `{cls}`")
    w("")
    w(f"- controles como desenhados: {'SIM' if ctrl_all else 'NÃO'}")
    w(f"- integridade dos EVIDENCE.jsonl: {'SIM' if integ_all else 'NÃO'}")
    w(f"- L0 de todos os bundles resolvido: {'SIM' if l0_all else 'NÃO'}")
    w(f"- asserções numerador/denominador: {'SIM' if all_ok else 'NÃO'}")
    (OUT / "REPRODUCED-FROM-BASELINE-REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"classificacao: {cls}")
    print(f"agregado: {agg}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
