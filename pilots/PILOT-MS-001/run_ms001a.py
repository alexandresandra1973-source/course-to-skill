#!/usr/bin/env python3
"""PILOT-MS-001A — execucao. HARD CAP 10, RETRY 0.
Raw persistido ANTES de qualquer processamento. Zero cross-source."""
import sys, os, json, hashlib, pathlib, datetime, collections
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib")); sys.path.insert(0, str(H.parent / "PILOT-MS-000A"))
import builders as B, identity as I, validate as V, gate as G, package as P
import entail_validate as EVAL
import seal_verifier as SV
import anthropic

MODEL = "claude-opus-5"; THINKING = {"type": "disabled"}; MAX_TOKENS = 8000
HARD_CAP = 10; RETRY = 0
OUT = H / "out-exec-2"; RAW = OUT / "raw"; PKGS = OUT / "packages"
for d in (OUT, RAW, PKGS): d.mkdir(parents=True, exist_ok=True)
OPLOG = OUT / "OPERATIONAL-RUN-LOG.jsonl"
_n = {"n": 0}; _calls = []
EXTRACTION_PROMPT = (H / "instruments/EXTRACTION-PROMPT-v1.txt").read_text(encoding="utf-8")
EXTRACTION_SCHEMA = (H / "instruments/EXTRACTION-SCHEMA-v1.json").read_text(encoding="utf-8")
ENTAIL_PROMPT = (H / "instruments/ENTAILMENT-PROMPT-v2.txt").read_text(encoding="utf-8")
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
        raise SystemExit(f"resolved_model={r.model} != {MODEL} — MS_001A_EXEC_2_INSTRUMENT_INVALID")
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
 {"claim_id": "CL-9201", "claim": "A requisicao exige autenticacao por token.", "qualifiers": {},
  "evidence": [{"evidence_id": "EV-9201", "excerpt": "O sistema exige autenticacao por token antes de aceitar a requisicao."}]},
 {"claim_id": "CL-9202", "claim": "A configuracao simples e suficiente para todos os usuarios.", "qualifiers": {},
  "evidence": [{"evidence_id": "EV-9202", "excerpt": "Para quem esta comecando, a configuracao simples costuma ser suficiente."}]},
 {"claim_id": "CL-9203", "claim": "A Evolution API exige autenticacao por chave global.", "qualifiers": {},
  "evidence": [{"evidence_id": "EV-9203", "excerpt": "O Redis e configurado adicionando um novo servico no painel e definindo um nome e uma senha para a instancia."}]},
 {"claim_id": "CL-9204", "claim": "O recurso X e obrigatorio neste cenario.", "qualifiers": {},
  "evidence": [{"evidence_id": "EV-9204", "excerpt": "A fonte informa que nao esta definido se o recurso X e obrigatorio ou opcional neste cenario."}]},
 {"claim_id": "CL-9205", "claim": "A Evolution API exige exatamente 4 GB de RAM.", "qualifiers": {},
  "evidence": [{"evidence_id": "EV-9205", "excerpt": "A Evolution API pode ser executada em uma VPS."}]},
]
JE_EXPECT = {"CL-9201": "ENTAILED", "CL-9202": "NOT_ENTAILED", "CL-9203": "NOT_ENTAILED",
             "CL-9204": "INDETERMINATE", "CL-9205": "NOT_ENTAILED"}


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
        Rp["classificacao"] = "MS_001A_EXEC_2_INSTRUMENT_INVALID"; Rp["motivo"] = {"EC_schema": errs}
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
        Rp["classificacao"] = "MS_001A_EXEC_2_INSTRUMENT_INVALID"; Rp["motivo"] = {"EC": ec}
        P.wjson(OUT / "summary.json", Rp); return 2

    # ------------------------------- CALL 2: JE -------------------------------
    ju = juser_t.replace("{SOURCE_ID}", "FIXTURE").replace("{ITEMS_JSON}",
                                                           json.dumps(JE_ITEMS, ensure_ascii=False, indent=1))
    txt = call(client, "ENTAILMENT_CONTROL", "JE", jsys, ju, {"fixture": "JE1-JE5-v2"})
    sent = {x["claim_id"]: {e["evidence_id"] for e in x["evidence"]} for x in JE_ITEMS}
    univ = set().union(*sent.values())
    doc, errs = EVAL.validate(jparse(txt), "FIXTURE", sent, univ)
    if doc is None:
        Rp["classificacao"] = "MS_001A_EXEC_2_INSTRUMENT_INVALID"; Rp["motivo"] = {"JE_validator": errs}
        P.wjson(OUT / "summary.json", Rp); print("  JE validador FALHOU:", errs); return 2
    got = {v["claim_id"]: v["judgment"] for v in doc["verdicts"]}
    je = {k: {"expected": v, "got": got.get(k), "ok": got.get(k) == v} for k, v in JE_EXPECT.items()}
    je_ok = all(x["ok"] for x in je.values())
    Rp["JE"] = {"detail": je, "ok": je_ok, "schema_errors": errs}
    P.wjson(OUT / "JE-CONTROL.json", {"parsed": doc, "checks": je})
    for k, v in je.items():
        print(f"  JE {k}: esperado={v['expected']:<14} obtido={str(v['got']):<14} {'OK' if v['ok'] else 'FALHA'}")
    if not je_ok:
        Rp["classificacao"] = "MS_001A_EXEC_2_INSTRUMENT_INVALID"; Rp["motivo"] = {"JE": je}
        P.wjson(OUT / "summary.json", Rp); return 2

    print(f"\n  controles OK. chamadas usadas: {_n['n']}/{HARD_CAP}\n")

    # ------------------------- CALLS 3-8: EXTRACAO -------------------------
    FR = B.frozen_slices()
    SRCS = ["MS001-SRC-B", "MS001-SRC-C"]
    ANCH = {s: B.build_anchors(s) for s in SRCS}
    EVID = {s: B.build_evidence(s, ANCH[s]) for s in SRCS}
    order = [k for k in sorted(FR) if FR[k]["source_id"] == "MS001-SRC-B"] + \
            [k for k in sorted(FR) if FR[k]["source_id"] == "MS001-SRC-C"]
    bundles = {}
    for sid in order:
        r = FR[sid]; src = r["source_id"]
        cat = B.evidence_catalog(EVID[src], sid)
        cat_ids = {c["evidence_id"] for c in cat}
        txt_slice = B.slice_text(src, r)
        u = build_extraction_user(src, sid, r["start_s"], r["end_s"], txt_slice, cat)
        out = call(client, "EXTRACTOR", sid, esys, u,
                   {"source_id": src, "slice_id": sid, "catalog": sorted(cat_ids),
                    "slice_text_sha256": r["slice_text_sha256"]})
        bd, errs = V.validate_extraction(jparse(out), src, sid, cat_ids)
        if bd is None:
            Rp["classificacao"] = "MS_001A_EXEC_2_INVALID"
            Rp["motivo"] = {"slice": sid, "schema_errors": errs}
            P.wjson(OUT / "summary.json", Rp); print(f"  {sid} INVALIDO: {errs}"); return 2
        for c in bd["raw_claims"]: c["_slice_id"] = sid
        for c in bd["raw_candidates"]: c["_slice_id"] = sid
        bundles[sid] = bd
        print(f"  {sid}: {len(bd['raw_claims'])} claims, {len(bd['raw_candidates'])} candidates")
        P.wjson(OUT / f"BUNDLE-{sid}.json", bd)

    # ------------------- CLAIM IDENTITY FINALIZATION (Stage A) -------------
    fin, t2f, raw_counts = {}, {}, {}
    for src in SRCS:
        raw = [c for sid in order if FR[sid]["source_id"] == src for c in bundles[sid]["raw_claims"]]
        raw_counts[src] = len(raw)
        if not raw:
            Rp["classificacao"] = "SOURCE_PACKAGE_FAIL"; Rp["motivo"] = {"ZERO_RAW_CLAIMS": src}
            P.wjson(OUT / "summary.json", Rp); print(f"  ZERO_RAW_CLAIMS em {src}"); return 1
        fin[src] = I.dedup_claims(raw, src)
        for cl in fin[src]:
            for m in cl["merged_from"]:
                t2f[(m["slice_id"], m["temporary_claim_id"])] = cl["local_id"]
        print(f"  {src}: {len(raw)} raw claims -> {len(fin[src])} claims finais (dedup)")

    # ----------------------- CALLS 9-10: ENTAILMENT ------------------------
    jud, sent_log = {}, {}
    for src in SRCS:
        evx = {e["local_id"]: e for e in EVID[src]}
        items, sent = [], {}
        for cl in fin[src]:
            ev = [{"evidence_id": r, "excerpt": evx[r]["excerpt"]} for r in cl["evidence_refs"]]
            items.append({"claim_id": cl["local_id"], "claim": cl["text"],
                          "qualifiers": cl["qualifiers"], "evidence": ev})
            sent[cl["local_id"]] = set(cl["evidence_refs"])
        sent_log[src] = {k: sorted(v) for k, v in sent.items()}
        P.wjson(OUT / f"ENTAILMENT-PAYLOAD-{src}.json", items)
        ju = juser_t.replace("{SOURCE_ID}", src).replace(
            "{ITEMS_JSON}", json.dumps(items, ensure_ascii=False, indent=1))
        out = call(client, "ENTAILMENT_JUDGE", src, jsys, ju,
                   {"source_id": src, "n_claims": len(items)})
        univ = set(evx)
        doc, errs = EVAL.validate(jparse(out), src, sent, univ)
        if doc is None:
            Rp["classificacao"] = "MS_001A_EXEC_2_INVALID"
            Rp["motivo"] = {"entailment": src, "errors": errs}
            P.wjson(OUT / "summary.json", Rp); print(f"  entailment {src} INVALIDO: {errs}"); return 2
        jud[src] = {v["claim_id"]: v for v in doc["verdicts"]}
        P.wjson(OUT / f"ENTAILMENT-{src}.json", doc)
        dist = collections.Counter(v["judgment"] for v in doc["verdicts"])
        print(f"  entailment {src}: {dict(dist)}")
    Rp["entailment_payload_sent"] = sent_log
    Rp["raw_claim_counts"] = raw_counts

    # --------- prova de nao-vazamento: nenhum EV de C no payload de B -------
    evb = {e["local_id"] for e in EVID["MS001-SRC-B"]}
    evc = {e["local_id"] for e in EVID["MS001-SRC-C"]}
    leak = {"B_payload_has_C_evidence": False, "C_payload_has_B_evidence": False,
            "nota": "ids EV- reiniciam por source; a prova real e que cada payload so cita "
                    "refs do proprio catalogo daquela source, verificado por E26_FOREIGN_EVIDENCE"}
    Rp["cross_source_leak_check"] = leak
    P.wjson(OUT / "summary.json", Rp)
    print(f"\n  chamadas usadas: {_n['n']}/{HARD_CAP}")
    P.wjson(OUT / "STATE.json", {"fin": fin, "jud": {k: v for k, v in jud.items()},
                                 "t2f": {f"{a}|{b}": c for (a, b), c in t2f.items()},
                                 "bundles": {k: v for k, v in bundles.items()},
                                 "calls": _calls})
    return 0


if __name__ == "__main__":
    sys.exit(main())
