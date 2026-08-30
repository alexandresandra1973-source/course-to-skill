#!/usr/bin/env python3
"""EO1-EO8 — canarios mecanicos do validador de entailment v2. Zero modelo."""
import sys, json, pathlib
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib"))
import entail_validate as EV

SENT = {"CL-0001": {"EV-0001", "EV-0002"}, "CL-0002": {"EV-0003"}}
UNIV = {"EV-0001", "EV-0002", "EV-0003", "EV-0004"}
def ok_v(cid, refs, j="ENTAILED"):
    return {"claim_id": cid, "judgment": j, "entail_why": "razao suficiente aqui", "evidence_refs_checked": refs}
def doc(vs): return json.dumps({"source_id": "MS001-SRC-B", "verdicts": vs})

R = []
def chk(c, d, code, txt):
    _, e = EV.validate(txt, "MS001-SRC-B", SENT, UNIV)
    R.append({"canary": c, "desc": d, "expected": code, "got": e, "ok": (code in e) if code else not e})

chk("EO0", "output correto de referencia", None,
    doc([ok_v("CL-0001", ["EV-0001", "EV-0002"]), ok_v("CL-0002", ["EV-0003"], "NOT_ENTAILED")]))
chk("EO1", "claim omitida", "E20_JUDGMENT_MISSING", doc([ok_v("CL-0001", ["EV-0001", "EV-0002"])]))
chk("EO2", "claim duplicada", "E24_JUDGMENT_DUPLICATED",
    doc([ok_v("CL-0001", ["EV-0001", "EV-0002"]), ok_v("CL-0001", ["EV-0001", "EV-0002"]), ok_v("CL-0002", ["EV-0003"])]))
chk("EO3", "claim_id desconhecida", "E21_UNKNOWN_CLAIM_ID",
    doc([ok_v("CL-0001", ["EV-0001", "EV-0002"]), ok_v("CL-0002", ["EV-0003"]), ok_v("CL-9999", ["EV-0001"])]))
chk("EO4", "campo extra", "E04b_JUDGE_EXTRA_FIELD",
    doc([dict(ok_v("CL-0001", ["EV-0001", "EV-0002"]), lixo=1), ok_v("CL-0002", ["EV-0003"])]))
chk("EO5", "judgment fora da enum", "E25_JUDGMENT_NOT_IN_ENUM",
    doc([ok_v("CL-0001", ["EV-0001", "EV-0002"], "TALVEZ"), ok_v("CL-0002", ["EV-0003"])]))
chk("EO6", "formato ANTIGO da v1", "E23_JUDGE_LEGACY_FORMAT",
    json.dumps({"source_id": "MS001-SRC-B", "verdicts": [
        {"temporary_claim_id": "CL-0001", "state": "ENTAILED", "why": "razao suficiente aqui"}]}))
chk("EO7", "evidence_refs_checked acrescentada", "E19_JUDGE_ADDED_EVIDENCE",
    doc([ok_v("CL-0001", ["EV-0001", "EV-0002", "EV-0004"]), ok_v("CL-0002", ["EV-0003"])]))
chk("EO8", "evidence_refs_checked omitida", "E27_JUDGE_OMITTED_EVIDENCE",
    doc([ok_v("CL-0001", ["EV-0001"]), ok_v("CL-0002", ["EV-0003"])]))
chk("EO9", "evidence estrangeira", "E26_FOREIGN_EVIDENCE",
    doc([ok_v("CL-0001", ["EV-0001", "EV-0002"]), ok_v("CL-0002", ["EV-7777"])]))
chk("EO10", "evidence_refs_checked ausente", "E22_JUDGE_SCHEMA_VIOLATION",
    doc([{"claim_id": "CL-0001", "judgment": "ENTAILED", "entail_why": "razao suficiente aqui"},
         ok_v("CL-0002", ["EV-0003"])]))

if __name__ == "__main__":
    for x in R:
        print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['canary']:<5} {x['desc']:<38} esperado={x['expected'] or 'sem erro'}")
    n = sum(1 for x in R if x["ok"]); print(f"\n  {n}/{len(R)} canarios do validador de entailment PASS")
    pathlib.Path("out").mkdir(exist_ok=True)
    pathlib.Path("out/entail-validator-canaries.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(0 if n == len(R) else 2)
