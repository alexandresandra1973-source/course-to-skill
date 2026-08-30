#!/usr/bin/env python3
"""PILOT-MS-000A / ROUND 3 — runner.

MECHANICAL / OFFLINE. Zero chamadas de modelo.
Matriz pre-declarada em OPENING-RECORD.md
(a11fff651aca8797aa39aaca928fa4f06744478fdd29f8501c16979885c3be45).

Verificadores REUTILIZADOS SEM ALTERACAO do diretorio do piloto.
Todo numero dos artefatos de saida e emitido aqui. Contagem manual: proibida.
"""
from __future__ import annotations
import json, pathlib, hashlib, sys, datetime
P = pathlib.Path(__file__).parent
sys.path.insert(0, str(P.parent))                 # instrumento da ROUND 2, intacto
import seal_verifier, identity_verifier           # noqa: E402
import structural_proof                           # noqa: E402

F = P / "fixtures"; OUT = P / "out"; REG = F / "EXTERNAL-SEAL-REGISTRY.txt"
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

MATRIX = [
 ("HAPPY",        "SEAL_INTEGRITY",   "PASS",    []),
 ("C1",           "SEAL_INTEGRITY",   "FAIL",    ["SHARED_MUTABLE_DIRECTORY"]),
 ("C2",           "SEAL_INTEGRITY",   "FAIL",    ["DOES_NOT_VALIDATE_IN_PLACE"]),
 ("C3",           "SEAL_INTEGRITY",   "FAIL",    ["SEAL_SELF_REFERENCE"]),
 ("C4",           "SEAL_INTEGRITY",   "FAIL",    ["PRODUCER_IDENTITY_MISMATCH"]),
 ("C5",           "PACKAGE_IDENTITY", "FAIL",    ["GLOBAL_ID_COLLISION"]),
 ("C6",           "PACKAGE_IDENTITY", "FAIL",    ["NAKED_LOCAL_ID"]),
 ("CTRL-INVALID", "SEAL_INTEGRITY",   "INVALID", ["SEAL_RECORD_UNPARSEABLE"]),
]

def main():
    started = datetime.datetime.now().astimezone().isoformat()
    OUT.mkdir(exist_ok=True)

    # ---- PORTAO PRE-EXECUCAO
    proofs = structural_proof.prove()
    pmap = {p["fixture"]: p for p in proofs}
    nao_provadas = [p["fixture"] for p in proofs if not p["provado"]]
    if nao_provadas:
        (OUT / "ROUND-3-INVALID.json").write_text(json.dumps(
            {"classificacao": "ROUND_3_INVALID", "sem_prova": nao_provadas, "proofs": proofs},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print("ROUND_3_INVALID — fixtures sem prova estrutural:", nao_provadas)
        return 2

    rows, executed = [], 0
    for name, kind, exp_v, exp_c in MATRIX:
        r = (seal_verifier.verify(F/name, REG, F/name) if kind == "SEAL_INTEGRITY"
             else identity_verifier.verify(F/name))
        executed += 1
        vok, cok = r["verdict"] == exp_v, all(c in r["codes"] for c in exp_c)
        rows.append({"fixture": name, "classe": kind,
                     "prova_estrutural": pmap[name]["prova"], "defeito_provado": True,
                     "esperado": exp_v, "observado": r["verdict"],
                     "codigos_esperados": exp_c, "codigos_observados": r["codes"],
                     "veredito_confere": vok, "motivo_confere": cok,
                     "resultado": "ESPERADO" if (vok and cok) else "INESPERADO",
                     "detail": r["detail"]})

    c5 = next(x for x in rows if x["fixture"] == "C5"); det = c5["detail"]
    c5x = {"local_ids_podem_repetir": bool(det.get("naked_collisions")),
           "identidade_nua_colide": "GLOBAL_ID_COLLISION" in c5["codigos_observados"],
           "identidade_qualificada_distinta": det.get("qualified_distinct") == det.get("local_ids_total")
                                              and "QUALIFIED_ID_NOT_DISTINCT" not in c5["codigos_observados"]}
    c5_ok = all(c5x.values())
    unexpected = [x["fixture"] for x in rows if x["resultado"] == "INESPERADO"]
    escaped = [x["fixture"] for x in rows if x["esperado"] == "FAIL" and x["observado"] == "PASS"]

    if executed != len(MATRIX):
        cls = "PILOT_MS_000A_INVALID"
    elif escaped:
        cls = "PILOT_MS_000A_FAIL"
    elif unexpected or not c5_ok:
        cls = "PILOT_MS_000A_INVALID"
    else:
        cls = "PILOT_MS_000A_PASS"

    summary = {"rodada": "ROUND 3", "iniciado": started,
               "opening_record_sha256": sha(P/"OPENING-RECORD.md"),
               "seal_verifier_sha256": sha(P.parent/"seal_verifier.py"),
               "identity_verifier_sha256": sha(P.parent/"identity_verifier.py"),
               "build_fixtures_sha256": sha(P/"build_fixtures.py"),
               "structural_proof_sha256": sha(P/"structural_proof.py"),
               "runner_sha256": sha(P/"run_canary.py"),
               "portao_estrutural": {"provadas": len(proofs)-len(nao_provadas), "total": len(proofs)},
               "fixtures_executadas": executed, "fixtures_na_matriz": len(MATRIX),
               "resultados_inesperados": unexpected, "defeitos_que_escaparam": escaped,
               "c5_asserçoes": c5x, "c5_ok": c5_ok, "classificacao": cls,
               "proofs": proofs, "linhas": rows}
    with (OUT/"raw-results.jsonl").open("w", encoding="utf-8") as fh:
        for x in rows: fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    (OUT/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    L=[]; w=L.append
    w("# PILOT-MS-000A / ROUND 3 — RELATÓRIO"); w("")
    w("**Gerado integralmente por `round-3/run_canary.py`.** Nenhum número digitado à mão."); w("")
    w(f"- Início: `{started}`")
    w(f"- Opening Record da ROUND 3: `{summary['opening_record_sha256']}`")
    w(f"- `seal_verifier.py`: `{summary['seal_verifier_sha256']}` — **reutilizado sem alteração**")
    w(f"- `identity_verifier.py`: `{summary['identity_verifier_sha256']}` — **reutilizado sem alteração**")
    w("- Julgamento: **`MECHANICAL / OFFLINE`** — zero chamadas de modelo"); w("")
    w("## 1. Portão pré-execução — prova estrutural do defeito"); w("")
    w(f"**{summary['portao_estrutural']['provadas']}/{summary['portao_estrutural']['total']} fixtures "
      "com o defeito provado mecanicamente, antes de o verificador rodar.**"); w("")
    w("| fixture | prova |"); w("|---|---|")
    for p in proofs: w(f"| `{p['fixture']}` | {p['prova']} |")
    w("")
    w("## 2. Matriz esperado × observado"); w("")
    w("| fixture | classe | esperado | observado | veredito | código esperado presente | resultado |")
    w("|---|---|---|---|---|---|---|")
    for x in rows:
        w(f"| `{x['fixture']}` | `{x['classe']}` | `{x['esperado']}` | `{x['observado']}` | "
          f"{'OK' if x['veredito_confere'] else '**X**'} | {'OK' if x['motivo_confere'] else '**X**'} | "
          f"{'**ESPERADO**' if x['resultado']=='ESPERADO' else '**INESPERADO**'} |")
    w("")
    w("## 3. Códigos emitidos"); w(""); w("| fixture | esperado | observado |"); w("|---|---|---|")
    for x in rows:
        w(f"| `{x['fixture']}` | {', '.join(f'`{c}`' for c in x['codigos_esperados']) or '—'} | "
          f"{', '.join(f'`{c}`' for c in x['codigos_observados']) or '—'} |")
    w("")
    c4 = next(x for x in rows if x["fixture"]=="C4")
    w("## 4. C4 — a correção desta rodada"); w("")
    w(f"- produtor declarado: `{c4['detail'].get('producer_declared','')}`")
    w(f"- produtor real no caminho: `{c4['detail'].get('producer_real','')}`")
    w(f"- código emitido: {', '.join(f'`{c}`' for c in c4['codigos_observados'])}")
    w(f"- disparou por identidade divergente, **não** por formato inválido: "
      f"{'SIM' if 'PRODUCER_IDENTITY_MISMATCH' in c4['codigos_observados'] else '**NÃO**'}")
    w("")
    w("## 5. C5 — as três asserções"); w(""); w("| asserção | resultado |"); w("|---|---|")
    for k,v in c5x.items(): w(f"| {k.replace('_',' ')} | {'OK' if v else '**FALHOU**'} |")
    w("")
    w("## 6. Controles do instrumento"); w("")
    w(f"- na matriz **{len(MATRIX)}** · executadas **{executed}** — "
      f"{'nenhum teste passou por ausência de execução' if executed==len(MATRIX) else '**DIVERGE**'}")
    w(f"- resultados inesperados: **{len(unexpected)}**")
    w(f"- defeitos que escaparam: **{len(escaped)}**")
    inv = next(x for x in rows if x['fixture']=='CTRL-INVALID')
    w(f"- `CTRL-INVALID` → `{inv['observado']}` — "
      f"{'distingue INVALID de FAIL' if inv['observado']=='INVALID' else '**colapsou INVALID em FAIL**'}")
    w(""); w("## 7. Classificação"); w(""); w(f"# `{cls}`")
    (OUT/"ROUND-3-REPORT.md").write_text("\n".join(L)+"\n", encoding="utf-8")
    print(f"classificacao: {cls}")
    print(f"portao={summary['portao_estrutural']} executadas={executed}/{len(MATRIX)} "
          f"inesperados={unexpected} escaparam={escaped} c5_ok={c5_ok}")
    return 0 if cls == "PILOT_MS_000A_PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
