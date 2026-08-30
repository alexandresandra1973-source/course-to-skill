#!/usr/bin/env python3
"""PILOT-MS-000A — SEAL CANARY runner.

MECHANICAL / OFFLINE. Zero chamadas de modelo.
Implementa a matriz pre-declarada em OPENING-RECORD.md
(sha256 bb4427c458e21f2938ce0ee0a9d084676d0d2a681d061b686ef5481aeec281e6).

Todo numero dos artefatos de saida e emitido aqui. Contagem manual: proibida.
"""
from __future__ import annotations
import json, pathlib, hashlib, sys, datetime, yaml
import seal_verifier, identity_verifier

P = pathlib.Path(__file__).parent
F = P / "fixtures"; OUT = P / "out"
REG = F / "EXTERNAL-SEAL-REGISTRY.txt"
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

# ---- matriz PRE-DECLARADA (copiada do Opening Record, nao alterada apos ver resultado)
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

# ---- assercao ESTRUTURAL independente: a fixture contem mesmo o defeito?
def defect_present(name):
    d = F / name
    if name == "HAPPY":
        return True, "conjunto integro por construcao"
    if name == "C1":
        seals = sorted(d.glob("*SEAL-RECORD*.yaml"))
        vs = {str(yaml.safe_load(s.read_text(encoding='utf-8')).get("version")) for s in seals}
        return (len(seals) > 1 and len(vs) > 1), f"{len(seals)} selos, versoes {sorted(vs)}"
    if name == "C2":
        a = F / "C2_SET_A" / "SEAL-RECORD.yaml"
        same = sha(a) == sha(d / "SEAL-RECORD.yaml")
        doc = yaml.safe_load((d / "SEAL-RECORD.yaml").read_text(encoding='utf-8'))
        diverge = any(sha(d / m["path"]) != m["sha256"] for m in doc["members"] if (d / m["path"]).is_file())
        return (same and diverge), f"selo byte-identico ao de C2_SET_A={same}; diverge no lugar={diverge}"
    if name == "C3":
        doc = yaml.safe_load((d / "SEAL-RECORD.yaml").read_text(encoding='utf-8'))
        hit = [m["path"] for m in doc["members"] if "SEAL-RECORD" in m["path"]]
        return bool(hit), f"members[] contem o proprio selo: {hit}"
    if name == "C4":
        doc = yaml.safe_load((d / "SEAL-RECORD.yaml").read_text(encoding='utf-8'))
        decl = doc["producer"]["toolchain_sha256"]; real = sha(d / doc["producer"]["toolchain_path"])
        return (decl != real), f"declarado={decl[:16]}… real={real[:16]}…"
    if name == "C5":
        ids = []
        for p in sorted(d.glob("*.json")):
            doc = json.loads(p.read_text(encoding='utf-8')); ids += [i["local_id"] for i in doc["items"]]
        dup = len(ids) != len(set(ids))
        return dup, f"local_ids={ids}; repetidos={dup}"
    if name == "C6":
        naked = []
        for p in sorted(d.glob("*.json")):
            doc = json.loads(p.read_text(encoding='utf-8'))
            naked += [r for r in doc.get("cross_refs", []) if not r.get("source_package_hash")]
        return bool(naked), f"cross_refs sem source_package_hash: {naked}"
    if name == "CTRL-INVALID":
        try:
            yaml.safe_load((d / "SEAL-RECORD.yaml").read_text(encoding='utf-8')); return False, "YAML parseou"
        except Exception as e:
            return True, f"YAML ilegivel: {type(e).__name__}"
    return False, "fixture desconhecida"

def run_one(name, kind):
    if kind == "SEAL_INTEGRITY":
        return seal_verifier.verify(F / name, REG, F / name)
    return identity_verifier.verify(F / name)

def main():
    started = datetime.datetime.now().astimezone().isoformat()
    rows, executed = [], 0
    for name, kind, exp_verdict, exp_codes in MATRIX:
        present, why = defect_present(name)
        r = run_one(name, kind); executed += 1
        got, codes = r["verdict"], r["codes"]
        verdict_ok = (got == exp_verdict)
        codes_ok = all(c in codes for c in exp_codes)
        rows.append({"fixture": name, "classe": kind,
                     "defeito_presente": present, "assercao_estrutural": why,
                     "esperado": exp_verdict, "observado": got,
                     "codigos_esperados": exp_codes, "codigos_observados": codes,
                     "veredito_confere": verdict_ok, "motivo_confere": codes_ok,
                     "resultado": "ESPERADO" if (present and verdict_ok and codes_ok) else "INESPERADO",
                     "detail": r["detail"]})
    # --- C5: as tres asserçoes
    c5 = next(r for r in rows if r["fixture"] == "C5")
    det = c5["detail"]
    c5_extra = {"local_ids_podem_repetir": bool(det.get("naked_collisions")),
                "identidade_nua_colide": "GLOBAL_ID_COLLISION" in c5["codigos_observados"],
                "identidade_qualificada_distinta": det.get("qualified_distinct") == det.get("local_ids_total")
                                                   and "QUALIFIED_ID_NOT_DISTINCT" not in c5["codigos_observados"]}
    c5_ok = all(c5_extra.values())

    unexpected = [r["fixture"] for r in rows if r["resultado"] == "INESPERADO"]
    fixtures_bad = [r["fixture"] for r in rows if not r["defeito_presente"] and r["fixture"] != "HAPPY"]
    if fixtures_bad:
        classificacao = "PILOT_MS_000A_INVALID"
    elif executed != len(MATRIX):
        classificacao = "PILOT_MS_000A_INVALID"
    elif unexpected or not c5_ok:
        escaped = [r["fixture"] for r in rows if r["esperado"] == "FAIL" and r["observado"] == "PASS"]
        classificacao = "PILOT_MS_000A_FAIL" if escaped else "PILOT_MS_000A_INVALID"
    else:
        classificacao = "PILOT_MS_000A_PASS"

    summary = {"iniciado": started, "opening_record_sha256": sha(P / "OPENING-RECORD.md"),
               "seal_verifier_sha256": sha(P / "seal_verifier.py"),
               "identity_verifier_sha256": sha(P / "identity_verifier.py"),
               "build_fixtures_sha256": sha(P / "build_fixtures.py"),
               "runner_sha256": sha(P / "run_canary.py"),
               "fixtures_executadas": executed, "fixtures_na_matriz": len(MATRIX),
               "resultados_inesperados": unexpected, "fixtures_sem_defeito": fixtures_bad,
               "c5_asserçoes": c5_extra, "c5_ok": c5_ok,
               "classificacao": classificacao, "linhas": rows}
    OUT.mkdir(exist_ok=True)
    with (OUT / "raw-results.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    L=[]; w=L.append
    w("# PILOT-MS-000A — SEAL CANARY · RELATÓRIO"); w("")
    w("**Gerado integralmente por `run_canary.py`.** Nenhum número digitado à mão."); w("")
    w(f"- Início: `{started}`")
    w(f"- Opening Record: `{summary['opening_record_sha256']}`")
    w(f"- `seal_verifier.py`: `{summary['seal_verifier_sha256']}`")
    w(f"- `identity_verifier.py`: `{summary['identity_verifier_sha256']}`")
    w("- Julgamento: **`MECHANICAL / OFFLINE`** — zero chamadas de modelo"); w("")
    w("## 1. As fixtures negativas contêm mesmo o defeito?"); w("")
    w("| fixture | defeito presente | asserção estrutural independente |"); w("|---|---|---|")
    for r in rows: w(f"| `{r['fixture']}` | {'SIM' if r['defeito_presente'] else '**NÃO**'} | {r['assercao_estrutural']} |")
    w("")
    w("## 2. Matriz esperado × observado"); w("")
    w("| fixture | classe | esperado | observado | veredito | código esperado presente | resultado |")
    w("|---|---|---|---|---|---|---|")
    for r in rows:
        w(f"| `{r['fixture']}` | `{r['classe']}` | `{r['esperado']}` | `{r['observado']}` | "
          f"{'OK' if r['veredito_confere'] else '**X**'} | {'OK' if r['motivo_confere'] else '**X**'} | "
          f"{'**ESPERADO**' if r['resultado']=='ESPERADO' else '**INESPERADO**'} |")
    w("")
    w("## 3. Códigos emitidos por fixture"); w("")
    w("| fixture | esperado | observado |"); w("|---|---|---|")
    for r in rows:
        w(f"| `{r['fixture']}` | {', '.join(f'`{c}`' for c in r['codigos_esperados']) or '—'} | "
          f"{', '.join(f'`{c}`' for c in r['codigos_observados']) or '—'} |")
    w("")
    w("## 4. C5 — as três asserções de identidade"); w("")
    w("| asserção | resultado |"); w("|---|---|")
    for k,v in c5_extra.items(): w(f"| {k.replace('_',' ')} | {'OK' if v else '**FALHOU**'} |")
    w("")
    w("## 5. Controles do instrumento"); w("")
    w(f"- fixtures na matriz: **{len(MATRIX)}** · executadas: **{executed}** — "
      f"{'nenhum teste passou por ausência de execução' if executed==len(MATRIX) else '**DIVERGE**'}")
    w(f"- fixtures negativas sem o defeito: **{len(fixtures_bad)}**")
    w(f"- resultados inesperados: **{len(unexpected)}**{' — ' + ', '.join(unexpected) if unexpected else ''}")
    inv = next(r for r in rows if r['fixture']=='CTRL-INVALID')
    w(f"- `CTRL-INVALID` devolveu `{inv['observado']}` — "
      f"{'o verificador distingue INVALID de FAIL' if inv['observado']=='INVALID' else '**colapsou INVALID em FAIL**'}")
    w("")
    w("## 6. Classificação"); w(""); w(f"# `{classificacao}`")
    (OUT / "PILOT-MS-000A-REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"classificacao: {classificacao}")
    print(f"executadas={executed}/{len(MATRIX)} inesperados={unexpected} fixtures_sem_defeito={fixtures_bad} c5_ok={c5_ok}")
    return 0 if classificacao == "PILOT_MS_000A_PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
