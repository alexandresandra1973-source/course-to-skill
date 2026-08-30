#!/usr/bin/env python3
"""PILOT-MS-001A — execucao. HARD CAP 10, RETRY 0.
Raw persistido ANTES de qualquer processamento. Zero cross-source."""
import sys, os, json, hashlib, pathlib, datetime, collections
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib")); sys.path.insert(0, str(H.parent / "PILOT-MS-000A"))
import builders as B, identity as I, validate as V, gate as G, package as P
import seal_verifier as SV
import anthropic

MODEL = "claude-opus-5"; THINKING = {"type": "disabled"}; MAX_TOKENS = 8000
HARD_CAP = 10; RETRY = 0
OUT = H / "out"; RAW = OUT / "raw"; PKGS = OUT / "packages"
for d in (OUT, RAW, PKGS): d.mkdir(parents=True, exist_ok=True)
OPLOG = OUT / "OPERATIONAL-RUN-LOG.jsonl"
_n = {"n": 0}; _calls = []
EXTRACTION_PROMPT = (H / "instruments/EXTRACTION-PROMPT-v1.txt").read_text(encoding="utf-8")
EXTRACTION_SCHEMA = (H / "instruments/EXTRACTION-SCHEMA-v1.json").read_text(encoding="utf-8")
ENTAIL_PROMPT = (H / "instruments/ENTAILMENT-PROMPT-v1.txt").read_text(encoding="utf-8")
PROMPT_HASHES = {f.name: P.sha_file(f) for f in sorted((H / "instruments").glob("*"))}
LIB_HASHES = {f.name: P.sha_file(f) for f in sorted((H / "lib").glob("*.py"))}


def split_prompt(t):
    a = t.index("[SYSTEM]"); b = t.index("[USER]")
    return t[a + 8:b].strip(), t[b + 6:].strip()


def call(client, role, label, system, user, meta):
    if _n["n"] >= HARD_CAP:
        raise SystemExit(f"HARD CAP {HARD_CAP} atingido — MS_001A_INVALID")
    t0 = datetime.datetime.now().astimezone().isoformat()
    r = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, thinking=THINKING,
                               system=system, messages=[{"role": "user", "content": user}])
    _n["n"] += 1
    txt = "".join(b.text for b in r.content if b.type == "text")
    # PERSISTIR RAW ANTES DE QUALQUER PROCESSAMENTO
    (RAW / f"call-{_n['n']:02d}-{label}-RAW.txt").write_text(txt, encoding="utf-8")
    (RAW / f"call-{_n['n']:02d}-{label}-INPUT.json").write_text(
        json.dumps({"system_sha256": P.sha_text(system), "user_sha256": P.sha_text(user),
                    "user": user, "meta": meta}, ensure_ascii=False, indent=1), encoding="utf-8")
    rec = {"call_seq": _n["n"], "instrument_role": role, "label": label,
           "model_requested": MODEL, "model_resolved": r.model, "thinking": THINKING,
           "max_tokens": MAX_TOKENS, "stop_reason": r.stop_reason,
           "input_sha256": P.sha_text(P.canon(meta)), "output_sha256": P.sha_text(txt),
           "tokens": {"input": r.usage.input_tokens, "output": r.usage.output_tokens}}
    _calls.append(rec)
    with open(OPLOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({**{k: rec[k] for k in ("call_seq", "instrument_role", "label")},
                            "started_at": t0,
                            "finished_at": datetime.datetime.now().astimezone().isoformat(),
                            "nota": "timestamp operacional: registro, NUNCA identidade"},
                           ensure_ascii=False) + "\n")
    if r.model != MODEL:
        raise SystemExit(f"resolved_model={r.model} != {MODEL} — MS_001A_INSTRUMENT_INVALID")
    return txt


def jparse(t):
    t = t.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0]
    a, b = t.find("{"), t.rfind("}")
    return t[a:b + 1] if a >= 0 else t


# ======================= FIXTURES SINTETICOS DOS CONTROLES =======================
EC_CATALOG = [
 {"evidence_id": "EV-9001", "excerpt": "O Evolution API precisa ser hospedado em uma VPS para ficar disponivel o tempo todo."},
 {"evidence_id": "EV-9002", "excerpt": "Para quem esta comecando, o instrutor recomenda criar os primeiros anuncios pelo painel."},
 {"evidence_id": "EV-9003", "excerpt": "Primeiro voce cria a instancia, depois gera o QR Code, e por fim escaneia com o celular."},
 {"evidence_id": "EV-9004", "excerpt": "O video foi gravado em um domingo de manha."},
 {"evidence_id": "EV-9005", "excerpt": "Nao deixe a estrutura na conta pessoal: isso aumenta a chance de restricao."},
]
EC_SLICE = ("O Evolution API precisa ser hospedado em uma VPS para ficar disponivel o tempo todo. "
            "A VPS da HostGator e a mais rapida do mercado. "
            "Para quem esta comecando, o instrutor recomenda criar os primeiros anuncios pelo painel. "
            "Primeiro voce cria a instancia, depois gera o QR Code, e por fim escaneia com o celular. "
            "O video foi gravado em um domingo de manha. "
            "Nao deixe a estrutura na conta pessoal: isso aumenta a chance de restricao.")
JE_ITEMS = [
 {"claim_id": "CL-9001", "claim": "O Evolution API nao tem custo de licenca.",
  "qualifiers": {}, "evidence": [{"evidence_id": "EV-9101", "excerpt": "O Evolution API e open source e voce nao paga por ele."}]},
 {"claim_id": "CL-9002", "claim": "Criar pelo Business Suite e sempre a melhor opcao.",
  "qualifiers": {}, "evidence": [{"evidence_id": "EV-9102", "excerpt": "Para quem esta comecando, criar pelo Business Suite e recomendado."}]},
 {"claim_id": "CL-9003", "claim": "O webhook deve usar o metodo POST.",
  "qualifiers": {}, "evidence": [{"evidence_id": "EV-9103", "excerpt": "O Redis e um banco nao relacional que guarda chave e valor."}]},
 {"claim_id": "CL-9004", "claim": "A verificacao do resultado leva menos de um minuto.",
  "qualifiers": {}, "evidence": [{"evidence_id": "EV-9104", "excerpt": "Depois voce volta para o painel e verifica o resultado."}]},
]
JE_EXPECT = {"CL-9001": "ENTAILED", "CL-9002": "NOT_ENTAILED",
             "CL-9003": "NOT_ENTAILED", "CL-9004": "INDETERMINATE"}


def build_extraction_user(source_id, slice_id, start_s, end_s, text, catalog):
    _, u = split_prompt(EXTRACTION_PROMPT)
    return (u.replace("{SOURCE_ID}", source_id).replace("{SLICE_ID}", slice_id)
             .replace("{START_S}", f"{start_s:.0f}").replace("{END_S}", f"{end_s:.0f}")
             .replace("{SLICE_TEXT}", text)
             .replace("{EVIDENCE_CATALOG_JSON}", json.dumps(catalog, ensure_ascii=False, indent=1))
             .replace("{JSON_SCHEMA}", EXTRACTION_SCHEMA))


def main():
    key = pathlib.Path(os.path.expanduser("~/.anthropic_key")).read_text().strip()
    client = anthropic.Anthropic(api_key=key)
    Rp = {"pilot": "PILOT-MS-001A", "hard_cap": HARD_CAP, "retry": RETRY,
          "instrument_hashes": PROMPT_HASHES, "lib_hashes": LIB_HASHES}
    esys, _ = split_prompt(EXTRACTION_PROMPT)
    jsys, juser_t = split_prompt(ENTAIL_PROMPT)

    # ------------------------------- CALL 1: EC -------------------------------
    cat_ids = {e["evidence_id"] for e in EC_CATALOG}
    u = build_extraction_user("MS001-SRC-B", "SL-B-01", 0, 90, EC_SLICE, EC_CATALOG)
    txt = call(client, "EXTRACTOR_CONTROL", "EC", esys, u,
               {"fixture": "EC1-EC6", "catalog": [e["evidence_id"] for e in EC_CATALOG]})
    bundle, errs = V.validate_extraction(jparse(txt), "MS001-SRC-B", "SL-B-01", cat_ids)
    ec = {"schema_errors": errs}
    if bundle is None:
        Rp["classificacao"] = "MS_001A_INSTRUMENT_INVALID"; Rp["motivo"] = {"EC_schema": errs}
        P.wjson(OUT / "summary.json", Rp); print("EC schema FALHOU:", errs); return 2
    claims = bundle["raw_claims"]; cands = bundle["raw_candidates"]
    low = " ".join(c["text"].lower() for c in claims)
    ec["EC1_supported"] = any("EV-9001" in c["evidence_refs"] for c in claims)
    ec["EC2_trap_refused"] = not any(("mais rapida" in c["text"].lower() or "hostgator" in c["text"].lower())
                                     for c in claims)
    ec["EC3_candidate_provenance"] = any(c["entity_kind"] == "anti_pattern_candidate"
                                         and c["evidence_refs"] for c in cands)
    ec["EC4_claim_link"] = any(c.get("claim_temp_refs") for c in cands)
    ec["EC5_no_candidate_from_factual"] = not any("domingo" in json.dumps(c, ensure_ascii=False).lower()
                                                  for c in cands)
    ec["EC6_scope_preserved"] = any(
        (("comec" in json.dumps(c.get("qualifiers"), ensure_ascii=False).lower())
         or ("comec" in c["text"].lower()))
        for c in claims if "EV-9002" in c["evidence_refs"])
    ec["ok"] = all(ec[k] for k in ("EC1_supported", "EC2_trap_refused", "EC3_candidate_provenance",
                                   "EC4_claim_link", "EC5_no_candidate_from_factual", "EC6_scope_preserved"))
    Rp["EC"] = ec
    P.wjson(OUT / "EC-CONTROL.json", {"bundle": bundle, "checks": ec})
    print("  EC:", {k: v for k, v in ec.items() if k.startswith("EC") or k == "ok"})
    if not ec["ok"]:
        Rp["classificacao"] = "MS_001A_INSTRUMENT_INVALID"; Rp["motivo"] = {"EC": ec}
        P.wjson(OUT / "summary.json", Rp); return 2

    # ------------------------------- CALL 2: JE -------------------------------
    ju = juser_t.replace("{SOURCE_ID}", "FIXTURE").replace("{ITEMS_JSON}",
                                                           json.dumps(JE_ITEMS, ensure_ascii=False, indent=1))
    txt = call(client, "ENTAILMENT_CONTROL", "JE", jsys, ju, {"fixture": "JE1-JE4"})
    try:
        jd = json.loads(jparse(txt))
        got = {v["claim_id"]: v["judgment"] for v in jd["verdicts"]}
    except Exception as e:
        Rp["classificacao"] = "MS_001A_INSTRUMENT_INVALID"; Rp["motivo"] = {"JE_parse": str(e)}
        P.wjson(OUT / "summary.json", Rp); return 2
    je = {k: {"expected": v, "got": got.get(k), "ok": got.get(k) == v} for k, v in JE_EXPECT.items()}
    je_ok = all(x["ok"] for x in je.values())
    Rp["JE"] = {"detail": je, "ok": je_ok}
    P.wjson(OUT / "JE-CONTROL.json", {"raw_parsed": got, "checks": je})
    print("  JE:", {k: (v["expected"], v["got"]) for k, v in je.items()})
    if not je_ok:
        Rp["classificacao"] = "MS_001A_INSTRUMENT_INVALID"; Rp["motivo"] = {"JE": je}
        P.wjson(OUT / "summary.json", Rp); return 2

    P.wjson(OUT / "summary.json", Rp)
    print(f"\n  controles OK. chamadas usadas: {_n['n']}/{HARD_CAP}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
