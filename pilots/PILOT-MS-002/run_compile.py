#!/usr/bin/env python3
"""MS-002 — compilacao dos Source Packages reais A/B/C, ISOLADAMENTE.
EC control -> extracao por slice -> claim identity -> JE control -> entailment ->
seal -> candidates -> coerencia local -> completude -> SOURCE_PACKAGE_HASH -> SEAL-RECORD.
Transporte: Claude Max OAuth. PAYG PROIBIDA.  Uso: run_compile.py [A|B|C|ALL] [--dry]"""
import json, hashlib, pathlib, sys, re, unicodedata, collections, warnings
warnings.filterwarnings("ignore")
import jsonschema
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H / "lib"))
import transport as T

DRY  = "--dry" in sys.argv
WHICH = [a for a in sys.argv[1:] if a in ("A", "B", "C", "ALL")] or ["ALL"]
SRCS = ["A", "B", "C"] if "ALL" in WHICH else WHICH
OUT  = H / "out-compile"; OUT.mkdir(exist_ok=True)
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha   = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
shaf  = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

EX_SYS, EX_USR = T.split_prompt((H / "instruments/EXTRACTION-PROMPT-v3.txt").read_text(encoding="utf-8"))
EN_SYS, EN_USR = T.split_prompt((H / "instruments/ENTAILMENT-PROMPT-v3.txt").read_text(encoding="utf-8"))
EX_SCHEMA = (H / "instruments/EXTRACTION-SCHEMA-v3.json").read_text(encoding="utf-8")
EN_SCHEMA = (H / "instruments/ENTAILMENT-SCHEMA-v3.json").read_text(encoding="utf-8")
EX_SCH = json.loads(EX_SCHEMA); EN_SCH = json.loads(EN_SCHEMA)
BUDGET = T.Budget(cap=int(next((a.split("=")[1] for a in sys.argv if a.startswith("--cap=")), 90)))

SYSDIR = OUT / "sys"; SYSDIR.mkdir(exist_ok=True)
(SYSDIR / "EXTRACT-SYSTEM.txt").write_text(EX_SYS, encoding="utf-8")
(SYSDIR / "ENTAIL-SYSTEM.txt").write_text(EN_SYS, encoding="utf-8")

# ----------------------------------------------------------- controles EC
EC_EV = [("EV-9001", "O Evolution API precisa ser hospedado em uma VPS para ficar disponivel o tempo todo."),
         ("EV-9002", "Para quem esta comecando, o instrutor recomenda criar os primeiros anuncios pelo painel."),
         ("EV-9003", "Primeiro voce cria a instancia, depois gera o QR Code, e por fim escaneia com o celular."),
         ("EV-9004", "O video foi gravado em um domingo de manha."),
         ("EV-9005", "Nao deixe a estrutura na conta pessoal: isso aumenta a chance de restricao.")]
EC_TEXT = (" ".join(x[1] for x in EC_EV) +
           " A VPS da HostGator e a mais rapida do mercado, todo mundo sabe disso.")

def ec_control():
    cat = [{"local_id": i, "excerpt": e} for i, e in EC_EV]
    u = (EX_USR.replace("{SOURCE_ID}", "MS002-SRC-B").replace("{SLICE_ID}", "SL-B-01")
              .replace("{START_S}", "0").replace("{END_S}", "60")
              .replace("{SLICE_TEXT}", EC_TEXT)
              .replace("{EVIDENCE_CATALOG_JSON}", json.dumps(cat, ensure_ascii=False, indent=1))
              .replace("{JSON_SCHEMA}", EX_SCHEMA))
    txt, _ = T.call(BUDGET, SYSDIR / "EXTRACT-SYSTEM.txt", u, OUT / "controls", "EC")
    d = json.loads(T.jparse(txt))
    jsonschema.validate(d, EX_SCH)
    cl, cd = d["raw_claims"], d["raw_candidates"]
    allev = {i for i, _ in EC_EV}
    res = {}
    res["EC1"] = any("EV-9001" in c["evidence_refs"] for c in cl)
    bad = re.compile(r"hostgator|mais r[aá]pida", re.I)
    res["EC2"] = not any(bad.search(c["text"]) for c in cl)
    res["EC3"] = any(c["entity_kind"] == "anti_pattern_candidate" and "EV-9005" in c["evidence_refs"] for c in cd)
    tcs = {c["temporary_claim_id"] for c in cl}
    wf = [c for c in cd if c["entity_kind"] == "workflow_candidate" and "EV-9003" in c["evidence_refs"]]
    res["EC4"] = bool(wf) and all(set(c["claim_temp_refs"]) <= tcs for c in wf)
    res["EC5"] = not any(c["evidence_refs"] == ["EV-9004"] for c in cd)
    q = [c for c in cl if "EV-9002" in c["evidence_refs"]]
    res["EC6"] = bool(q) and any((c["qualifiers"].get("audience") or c["qualifiers"].get("scope") or "")
                                 .lower().find("comec") >= 0 or "comec" in (c.get("text") or "").lower() for c in q)
    res["EC0_no_invented_ev"] = all(set(c["evidence_refs"]) <= allev for c in cl + cd)
    return res, d

# ----------------------------------------------------------- controles JE
JE = [("JE1", "EV-9201", "O sistema exige autenticacao por token antes de aceitar a requisicao.",
       "CL-9201", "A requisicao exige autenticacao por token.", "ENTAILED"),
      ("JE2", "EV-9202", "Para quem esta comecando, a configuracao simples costuma ser suficiente.",
       "CL-9202", "A configuracao simples e suficiente para todos os usuarios.", "NOT_ENTAILED"),
      ("JE3", "EV-9203", "O Redis e configurado adicionando um novo servico no painel e definindo um nome e uma senha para a instancia.",
       "CL-9203", "A Evolution API exige autenticacao por chave global.", "NOT_ENTAILED"),
      ("JE4", "EV-9204", "A fonte informa que nao esta definido se o recurso X e obrigatorio ou opcional neste cenario.",
       "CL-9204", "O recurso X e obrigatorio neste cenario.", "INDETERMINATE"),
      ("JE5", "EV-9205", "A Evolution API pode ser executada em uma VPS.",
       "CL-9205", "A Evolution API exige exatamente 4 GB de RAM.", "NOT_ENTAILED")]

def je_control():
    items = [{"claim_id": c, "claim_text": ct, "evidence": [{"local_id": e, "excerpt": et}]}
             for _, e, et, c, ct, _ in JE]
    u = (EN_USR.replace("{SOURCE_ID}", "MS002-SRC-B")
              .replace("{ITEMS_JSON}", json.dumps(items, ensure_ascii=False, indent=1)))
    txt, _ = T.call(BUDGET, SYSDIR / "ENTAIL-SYSTEM.txt", u, OUT / "controls", "JE")
    d = json.loads(T.jparse(txt))
    got = {v["claim_id"]: v["judgment"] for v in d["verdicts"]}
    return {name: got.get(cid) == want for name, _, _, cid, _, want in JE}, got

# --------------------------------------------------------------- extracao
def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s).strip()
def sem_key(text, qual, sid):
    return sha(canon({"t": " ".join(norm(text).split()), "q": {k: (v or None) for k, v in sorted(qual.items())}, "s": sid}))

def extract_source(src):
    sid = f"MS002-SRC-{src}"
    pkg = H / "packages" / f"pkg-{src}"
    ev = [json.loads(l) for l in (pkg / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines()]
    slices = json.loads((pkg / "SLICES.json").read_text(encoding="utf-8"))
    byslice = collections.defaultdict(list)
    for e in ev: byslice[e["slice_id"]].append(e)
    bundles, trace = [], []
    for sl in slices:
        chunk = byslice[sl["slice_id"]]
        cat = [{"local_id": e["local_id"], "excerpt": e["excerpt"]} for e in chunk]
        text = " ".join(e["excerpt"] for e in chunk)
        u = (EX_USR.replace("{SOURCE_ID}", sid).replace("{SLICE_ID}", sl["slice_id"])
                  .replace("{START_S}", str(sl["start_s"])).replace("{END_S}", str(sl["end_s"]))
                  .replace("{SLICE_TEXT}", text)
                  .replace("{EVIDENCE_CATALOG_JSON}", json.dumps(cat, ensure_ascii=False, indent=1))
                  .replace("{JSON_SCHEMA}", EX_SCHEMA))
        if DRY:
            trace.append({"slice": sl["slice_id"], "user_sha256": sha(u), "user_bytes": len(u.encode())})
            continue
        txt, rec = T.call(BUDGET, SYSDIR / "EXTRACT-SYSTEM.txt", u, OUT / f"raw-{src}", sl["slice_id"])
        d = json.loads(T.jparse(txt))
        jsonschema.validate(d, EX_SCH)
        if d["source_id"] != sid or d["slice_id"] != sl["slice_id"]:
            raise SystemExit(f"X01_SLICE_MISMATCH em {sl['slice_id']} — MS_002_INVALID")
        allow = {e["local_id"] for e in chunk}
        for c in d["raw_claims"] + d["raw_candidates"]:
            if not set(c["evidence_refs"]) <= allow:
                raise SystemExit(f"X02_INVENTED_EVIDENCE em {sl['slice_id']} — MS_002_INVALID")
        tcs = {c["temporary_claim_id"] for c in d["raw_claims"]}
        for c in d["raw_candidates"]:
            if not set(c["claim_temp_refs"]) <= tcs:
                raise SystemExit(f"X03_DANGLING_CLAIM_REF em {sl['slice_id']} — MS_002_INVALID")
        bundles.append(d)
        trace.append({"slice": sl["slice_id"], "claims": len(d["raw_claims"]),
                      "candidates": len(d["raw_candidates"]), "call_seq": rec["call_seq"]})
        print(f"    {sl['slice_id']}: {len(d['raw_claims'])} claims, {len(d['raw_candidates'])} candidates")
    return bundles, trace

# ------------------------------------------- identidade + entailment + seal
def compile_source(src, bundles):
    sid = f"MS002-SRC-{src}"
    pkg = H / "packages" / f"pkg-{src}"
    prof = json.loads((pkg / "SOURCE-PROFILE.json").read_text(encoding="utf-8"))
    lang = prof["language"]
    claims, bykey = [], {}
    tcmap = {}                                  # (slice, TC) -> CL
    for b in bundles:
        for rc in b["raw_claims"]:
            k = sem_key(rc["text"], rc["qualifiers"], sid)
            if k in bykey:
                cl = bykey[k]
                cl["merged_from"].append({"slice_id": b["slice_id"], "temporary_claim_id": rc["temporary_claim_id"]})
                for e in rc["evidence_refs"]:
                    if e not in [x["local_id"] for x in cl["evidence_refs"]]:
                        cl["evidence_refs"].append({"local_id": e, "ref_scope": "SELF"})
                if rc["status"] not in cl["status_raw"]: cl["status_raw"].append(rc["status"])
            else:
                cl = {"entity_kind": "claim", "local_id": f"CL-{len(claims)+1:04d}",
                      "source_id": sid, "claim_id": f"{sid}|CL-{len(claims)+1:04d}",
                      "text": rc["text"], "source_language": rc["source_language"],
                      "qualifiers": rc["qualifiers"], "semantic_key": k,
                      "evidence_refs": [{"local_id": e, "ref_scope": "SELF"} for e in rc["evidence_refs"]],
                      "merged_from": [{"slice_id": b["slice_id"], "temporary_claim_id": rc["temporary_claim_id"]}],
                      "status_raw": [rc["status"]], "status": "PENDING_ENTAILMENT"}
                claims.append(cl); bykey[k] = cl
            tcmap[(b["slice_id"], rc["temporary_claim_id"])] = cl["local_id"]
    return claims, tcmap

def entail(src, claims, evidence_by_id):
    sid = f"MS002-SRC-{src}"
    verdicts = {}
    B = 25
    for i in range(0, len(claims), B):
        chunk = claims[i:i + B]
        items = [{"claim_id": c["local_id"], "claim_text": c["text"],
                  "evidence": [{"local_id": r["local_id"], "excerpt": evidence_by_id[r["local_id"]]}
                               for r in c["evidence_refs"]]} for c in chunk]
        u = (EN_USR.replace("{SOURCE_ID}", sid)
                  .replace("{ITEMS_JSON}", json.dumps(items, ensure_ascii=False, indent=1)))
        label = f"ENTAIL-{i//B+1:02d}"
        txt, _ = T.call(BUDGET, SYSDIR / "ENTAIL-SYSTEM.txt", u, OUT / f"raw-{src}", label)
        d = json.loads(T.jparse(txt))
        jsonschema.validate(d, EN_SCH)
        got = {v["claim_id"]: v for v in d["verdicts"]}
        want = {c["local_id"] for c in chunk}
        if set(got) != want:
            raise SystemExit(f"E01_ENTAIL_SET_MISMATCH em {label} — MS_002_INVALID")
        for c in chunk:
            v = got[c["local_id"]]
            need = {r["local_id"] for r in c["evidence_refs"]}
            if set(v["evidence_refs_checked"]) != need:
                raise SystemExit(f"E02_EVIDENCE_SET_MISMATCH {c['local_id']} — MS_002_INVALID")
            verdicts[c["local_id"]] = v
        print(f"    {label}: {len(chunk)} claims julgadas")
    return verdicts

# ------------------------------------------------- candidates + selagem
def finalize(src, claims, tcmap, bundles, verdicts):
    sid = f"MS002-SRC-{src}"
    pkg = H / "packages" / f"pkg-{src}"
    sealed = []
    for c in claims:
        v = verdicts[c["local_id"]]
        c["entailed_by"] = v["judgment"]; c["entail_why"] = v["entail_why"]
        c["status"] = "SEALED" if v["judgment"] == "ENTAILED" else "REJECTED_NOT_ENTAILED"
        if c["status"] == "SEALED": sealed.append(c)
    sealed_ids = {c["local_id"] for c in sealed}
    ev_ids = {json.loads(l)["local_id"] for l in (pkg / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines()}
    buckets = {"rule_candidate": "rule_candidates", "workflow_candidate": "workflow_candidates",
               "anti_pattern_candidate": "anti_pattern_candidates"}
    cands = {v: [] for v in buckets.values()}
    n = {"rule_candidate": 0, "workflow_candidate": 0, "anti_pattern_candidate": 0}
    pref = {"rule_candidate": "R", "workflow_candidate": "WF", "anti_pattern_candidate": "AP"}
    invalid_prov = 0
    for b in bundles:
        for rc in b["raw_candidates"]:
            kind = rc["entity_kind"]; n[kind] += 1
            deps = sorted({tcmap[(b["slice_id"], t)] for t in rc["claim_temp_refs"]})
            unsat = [d for d in deps if d not in sealed_ids]
            prov_ok = bool(rc["evidence_refs"]) and set(rc["evidence_refs"]) <= ev_ids
            if not prov_ok: invalid_prov += 1
            dep_status = ("SATISFIED" if not unsat else "UNSATISFIED_BY_ENTAILMENT") if deps else "NO_CLAIM_DEPENDENCY"
            elig = ("ELIGIBLE_FOR_CROSS_SOURCE_DECISION"
                    if prov_ok and dep_status in ("SATISFIED", "NO_CLAIM_DEPENDENCY")
                    else "NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION")
            cands[buckets[kind]].append({
                "entity_kind": kind, "local_id": f"{pref[kind]}-{n[kind]:04d}", "source_id": sid,
                "structure": rc["structure"],
                "evidence_refs": rc["evidence_refs"],
                "claim_dependencies": deps, "unsealed_claim_dependencies": unsat,
                "claim_dependency_status": dep_status,
                "claim_refs_applicability": rc.get("claim_refs_applicability", "APPLICABLE"),
                "sealed_claim_refs": [d for d in deps if d in sealed_ids],
                "defects": rc["defects"], "markers": [],
                "cross_source_eligibility": elig,
                "provenance_detail": {"slice_id": b["slice_id"],
                                      "temporary_candidate_id": rc["temporary_candidate_id"],
                                      "provenance_state": "DIRECT_EVIDENCE" if prov_ok else "INVALID_PROVENANCE"},
                "merged_from": [{"slice_id": b["slice_id"], "temporary_candidate_id": rc["temporary_candidate_id"]}],
                "structural_key": sha(canon(rc["structure"]))})
    # ---- persistencia
    def wl(p, rows):
        (pkg / p).write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    wl("CLAIMS.jsonl", sealed)
    wl("CLAIMS-REJECTED.jsonl", [c for c in claims if c["status"] != "SEALED"])
    (pkg / "SOURCE-LOCAL-CANDIDATES.json").write_text(json.dumps(cands, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    dist = collections.Counter(c["entailed_by"] for c in claims)
    coh = {"source_id": sid,
           "claims_total": len(claims), "claims_sealed": len(sealed),
           "entailment_distribution": dict(dist),
           "candidates_total": sum(len(v) for v in cands.values()),
           "candidates_by_kind": {k: len(v) for k, v in cands.items()},
           "candidates_eligible": sum(1 for v in cands.values() for c in v
                                      if c["cross_source_eligibility"] == "ELIGIBLE_FOR_CROSS_SOURCE_DECISION"),
           "INVALID_PROVENANCE": invalid_prov,
           "all_claims_have_evidence": all(c["evidence_refs"] for c in claims),
           "all_sealed_are_entailed": all(c["entailed_by"] == "ENTAILED" for c in sealed),
           "duplicate_semantic_keys": len(sealed) - len({c["semantic_key"] for c in sealed})}
    (pkg / "LOCAL-COHERENCE-REPORT.json").write_text(json.dumps(coh, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    (pkg / "DECLARATION-SPACE-INDEX.json").write_text(json.dumps(
        {"bounded_to": sid, "nota": "enumera SO o proprio pacote. filesystem scan != corpus audit.",
         "referenced": ["DR-MS-002-INDEP-001", "OPENING-RECORD-MS-002-COMPILE"],
         "slices": [s["slice_id"] for s in json.loads((pkg / "SLICES.json").read_text(encoding="utf-8"))]},
        ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    (pkg / "TOOLCHAIN.json").write_text(json.dumps(
        {"compiler": "run_compile.py", "compiler_sha256": shaf(H / "run_compile.py"),
         "l0_builder_sha256": shaf(H / "build_l0.py"), "transport_sha256": shaf(H / "lib/transport.py"),
         "extraction_prompt_sha256": shaf(H / "instruments/EXTRACTION-PROMPT-v3.txt"),
         "extraction_schema_sha256": shaf(H / "instruments/EXTRACTION-SCHEMA-v3.json"),
         "entailment_prompt_sha256": shaf(H / "instruments/ENTAILMENT-PROMPT-v3.txt"),
         "entailment_schema_sha256": shaf(H / "instruments/ENTAILMENT-SCHEMA-v3.json"),
         "model_transport": "CLAUDE_CODE_MAX_OAUTH_PRINT_MODE", "model": T.MODEL,
         "claude_code_version": "2.1.251", "payg_api_used": 0},
        ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    if invalid_prov:
        raise SystemExit(f"INVALID_PROVENANCE={invalid_prov} em {sid} — package NAO pode selar")
    return coh

def seal(src):
    pkg = H / "packages" / f"pkg-{src}"
    members = []
    for p in sorted(pkg.rglob("*")):
        if p.is_file() and p.name not in ("SEAL-RECORD.yaml",):
            members.append({"path": str(p.relative_to(pkg)), "sha256": shaf(p)})
    mh = sha(canon(members))
    prof = json.loads((pkg / "SOURCE-PROFILE.json").read_text(encoding="utf-8"))
    y = ["artifact_id: MS002-SEAL-" + prof["source_id"], "artifact_status: SEALED",
         f"member_manifest_hash: {mh}", "members:"]
    for m in members: y += [f"- path: {m['path']}", f"  sha256: {m['sha256']}"]
    y += [f"members_count: {len(members)}",
          "nota: SEAL-RECORD nao se auto-referencia. Sem mtime.",
          "producer:", "  toolchain_path: TOOLCHAIN.json",
          f"  toolchain_sha256: {shaf(pkg / 'TOOLCHAIN.json')}",
          "seal_contract_version: SEALED/7-conditions/MS-002",
          f"source_content_hash: {prof['source_content_hash']}",
          f"source_id: {prof['source_id']}", f"source_package_hash: {mh}"]
    (pkg / "SEAL-RECORD.yaml").write_text("\n".join(y) + "\n", encoding="utf-8")
    return mh

def main():
    T.guard_env()
    print(f"MS-002 compile · fontes={SRCS} · dry={DRY} · cap={BUDGET.cap}")
    state = {}
    if not DRY:
        print("  controle EC (extrator)...")
        ec, _ = ec_control()
        print("   ", {k: ("OK" if v else "FALHA") for k, v in ec.items()})
        if not all(ec.values()): raise SystemExit("MS_002_INSTRUMENT_INVALID (EC)")
        print("  controle JE (entailment)...")
        je, got = je_control()
        print("   ", {k: ("OK" if v else "FALHA") for k, v in je.items()}, got)
        if not all(je.values()): raise SystemExit("MS_002_INSTRUMENT_INVALID (JE)")
        state["controls"] = {"EC": ec, "JE": je}
    for src in SRCS:
        print(f"  === fonte {src} ===")
        bundles, trace = extract_source(src)
        if DRY:
            state[src] = {"trace": trace}; continue
        (OUT / f"BUNDLES-{src}.json").write_text(json.dumps(bundles, ensure_ascii=False, indent=1), encoding="utf-8")
        claims, tcmap = compile_source(src, bundles)
        print(f"    claims unicas: {len(claims)}")
        pkg = H / "packages" / f"pkg-{src}"
        evmap = {}
        for l in (pkg / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines():
            e = json.loads(l); evmap[e["local_id"]] = e["excerpt"]
        verdicts = entail(src, claims, evmap)
        coh = finalize(src, claims, tcmap, bundles, verdicts)
        h = seal(src)
        coh["source_package_hash"] = h
        state[src] = coh
        print(f"    SEALED: {coh['claims_sealed']}/{coh['claims_total']} claims · "
              f"{coh['candidates_total']} candidates ({coh['candidates_eligible']} eligible) · hash {h[:16]}…")
    state["calls"] = BUDGET.calls; state["executed_calls"] = BUDGET.n
    (OUT / ("COMPILE-STATE-dry.json" if DRY else "COMPILE-STATE.json")).write_text(
        json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  chamadas: {BUDGET.n}/{BUDGET.cap}")

if __name__ == "__main__":
    sys.exit(main())
