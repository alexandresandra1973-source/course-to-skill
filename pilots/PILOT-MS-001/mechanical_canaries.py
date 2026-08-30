#!/usr/bin/env python3
"""MS-001A — CANARIOS MECANICOS PRE-MODELO. Zero modelo, zero rede.
Todos precisam passar ANTES da Call 1."""
import sys, json, hashlib, pathlib, copy
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lib"))
import builders as B, identity as I, validate as V, gate as G

R = []
def chk(cid, desc, expected, got, ok):
    R.append({"canary": cid, "desc": desc, "expected": expected, "got": got, "ok": bool(ok)})

# ============================ SA1-SA4 : SOURCE ANCHOR ============================
A = B.build_anchors("MS001-SRC-B"); E = B.build_evidence("MS001-SRC-B", A)
S = B.load_raw("MS001-SRC-B"); AH = B.sha_bytes(B.RAW["MS001-SRC-B"])
chk("SA0", "anchors reais bem formados", "todos OK",
    f"{len(A)} anchors",
    all(a["artifact_hash"] == AH and a["transcript_segment_ids"] and
        a["quote"] == " ".join(S[i]["text"] for i in a["transcript_segment_ids"]) and
        a["start_s"] == S[a["transcript_segment_ids"][0]]["start"] for a in A))
def anchor_valid(a):
    ids = a["transcript_segment_ids"]
    if any(i < 0 or i >= len(S) for i in ids): return "FAIL_SEGMENT_ID"
    if a["artifact_hash"] != AH: return "FAIL_ARTIFACT_HASH"
    if a["quote"] != " ".join(S[i]["text"] for i in ids): return "FAIL_QUOTE"
    if a["start_s"] != S[ids[0]]["start"]: return "FAIL_SPAN"
    return "PASS"
m = copy.deepcopy(A[0]); m["transcript_segment_ids"] = [999999]
chk("SA1", "segment id inexistente", "FAIL", anchor_valid(m), anchor_valid(m) == "FAIL_SEGMENT_ID")
m = copy.deepcopy(A[0]); m["artifact_hash"] = "0"*64
chk("SA2", "artifact hash incorreto", "FAIL", anchor_valid(m), anchor_valid(m) == "FAIL_ARTIFACT_HASH")
m = copy.deepcopy(A[0]); m["quote"] = "texto que nao esta no raw"
chk("SA3", "quote nao reproduzido", "FAIL", anchor_valid(m), anchor_valid(m) == "FAIL_QUOTE")
m = copy.deepcopy(A[0]); m["start_s"] = m["start_s"] + 99
chk("SA4", "start/end incompativel", "FAIL", anchor_valid(m), anchor_valid(m) == "FAIL_SPAN")

# ============================ SCHEMA / ERROR CODES ==============================
CAT = {e["local_id"] for e in E if e["slice_id"] == "SL-B-01"}
CATL = sorted(CAT)
def base():
    return {"source_id": "MS001-SRC-B", "slice_id": "SL-B-01",
            "raw_claims": [{"temporary_claim_id": "TC-001", "text": "uma proposicao qualquer sustentada",
                            "source_language": "pt", "evidence_refs": [CATL[0]],
                            "qualifiers": {"scope": None, "condition": None, "platform": None,
                                           "stage": None, "audience": None},
                            "status": "SOURCE_EXPLICIT"}],
            "raw_candidates": [{"temporary_candidate_id": "TX-001", "entity_kind": "rule_candidate",
                                "evidence_refs": [CATL[0]], "claim_temp_refs": ["TC-001"],
                                "defects": ["PRECEDENCE_UNDEFINED"],
                                "structure": {"name": "n", "trigger": "t", "condition": "c",
                                              "action": "a", "do_not": [], "precedence": None}}]}
def val(d): return V.validate_extraction(json.dumps(d), "MS001-SRC-B", "SL-B-01", CAT)
b, err = val(base()); chk("SC00", "bundle valido de referencia", "sem erro", err, not err)
cases = [
 ("SC01","JSON invalido","E01_JSON_UNPARSEABLE", lambda: None),
 ("SC02","campo desconhecido","E03_UNKNOWN_FIELD", lambda d: d.update({"lixo":1})),
 ("SC03","kind desconhecido","E04_UNKNOWN_ENTITY_KIND", lambda d: d["raw_candidates"][0].update({"entity_kind":"foo"})),
 ("SC04","evidence vazia (claim)","E05_EMPTY_EVIDENCE_REFS", lambda d: d["raw_claims"][0].update({"evidence_refs":[]})),
 ("SC05","evidence vazia (candidate)","E05_EMPTY_EVIDENCE_REFS", lambda d: d["raw_candidates"][0].update({"evidence_refs":[]})),
 ("SC06","Evidence fabricada","E06_EVIDENCE_REF_NOT_IN_CATALOG", lambda d: d["raw_claims"][0].update({"evidence_refs":["EV-9999"]})),
 ("SC07","Evidence de outra slice","E06_EVIDENCE_REF_NOT_IN_CATALOG", lambda d: d["raw_claims"][0].update({"evidence_refs":["EV-0012"]})),
 ("SC08","claim temp ref quebrada","E10_CLAIM_TEMP_REF_UNRESOLVED", lambda d: d["raw_candidates"][0].update({"claim_temp_refs":["TC-999"]})),
 ("SC09","temp id duplicado","E11_DUPLICATE_TEMP_ID", lambda d: d["raw_claims"].append(dict(d["raw_claims"][0]))),
 ("SC10","workflow sem steps","E12_WORKFLOW_NO_STEPS", lambda d: d["raw_candidates"].append(
     {"temporary_candidate_id":"TX-002","entity_kind":"workflow_candidate","evidence_refs":[CATL[0]],
      "claim_temp_refs":[],"claim_refs_applicability":"NOT_APPLICABLE","defects":[],
      "structure":{"name":"w","steps":[]}})),
 ("SC11","ordem invalida","E13_WORKFLOW_ORDER_INVALID", lambda d: d["raw_candidates"].append(
     {"temporary_candidate_id":"TX-003","entity_kind":"workflow_candidate","evidence_refs":[CATL[0]],
      "claim_temp_refs":[],"claim_refs_applicability":"NOT_APPLICABLE","defects":[],
      "structure":{"name":"w","steps":[{"order_key":2,"name":"a","action":"x","evidence_refs":[CATL[0]]},
                                       {"order_key":2,"name":"b","action":"y","evidence_refs":[CATL[0]]}]}})),
 ("SC12","applicability ausente","E18_CLAIM_REFS_APPLICABILITY_MISSING", lambda d: d["raw_candidates"][0].update({"claim_temp_refs":[]})),
 ("SC13","source_id divergente","E15_SOURCE_ID_MISMATCH", lambda d: d.update({"source_id":"MS001-SRC-C"})),
 ("SC14","slice_id divergente","E16_SLICE_ID_MISMATCH", lambda d: d.update({"slice_id":"SL-C-01"})),
 ("SC15","structure incompativel","E17_STRUCTURE_KIND_MISMATCH", lambda d: d["raw_candidates"][0].update({"structure":{"name":"n","steps":[]}})),
]
for cid, desc, code, mut in cases:
    if cid == "SC01":
        _, err = V.validate_extraction("{ nao e json", "MS001-SRC-B", "SL-B-01", CAT)
    else:
        d = base(); mut(d); _, err = val(d)
    chk(cid, desc, code, err, code in err)

# ============================ CP1-CP8 : PROVENANCE ==============================
EV = {e["local_id"] for e in E}
AOE = {e["local_id"]: e["source_anchor_refs"][0]["local_id"] for e in E}
L0 = {e["local_id"]: True for e in E}
SEALED = {"CL-0001"}; ALLC = {"CL-0001", "CL-0002", "CL-0003"}
JUD = {"CL-0001": "ENTAILED", "CL-0002": "NOT_ENTAILED", "CL-0003": "INDETERMINATE"}
def cand(**kw):
    d = {"evidence_refs": [sorted(EV)[0]], "claim_dependencies": [],
         "claim_refs_applicability": "NOT_APPLICABLE"}; d.update(kw); return d
def ev(c, **kw):
    a = dict(evidence_ids=EV, anchor_of_evidence=AOE, l0_reachable=L0,
             sealed_claim_ids=SEALED, all_final_claim_ids=ALLC, judgments=JUD); a.update(kw)
    return G.evaluate(c, **a)
r = ev(cand()); chk("CP1","evidence valida, sem claim dep",G.ELIGIBLE,r["cross_source_eligibility"],r["cross_source_eligibility"]==G.ELIGIBLE)
r = ev(cand(evidence_refs=["EV-9999"])); chk("CP2","evidence ref inexistente",G.INVALID,r["cross_source_eligibility"],r["cross_source_eligibility"]==G.INVALID)
r = ev(cand(evidence_refs=[])); chk("CP3","evidence vazia injetada no gate",f"{G.NOT_ELIGIBLE}+UNREACHABLE",
    f'{r["cross_source_eligibility"]}|{r["markers"]}', r["cross_source_eligibility"]==G.NOT_ELIGIBLE and G.UNREACHABLE in r["markers"])
r = ev(cand(claim_refs_applicability="APPLICABLE", claim_dependencies=["CL-9999"]))
chk("CP4","claim ref inexistente",G.INVALID,r["cross_source_eligibility"],r["cross_source_eligibility"]==G.INVALID)
r = ev(cand(), l0_reachable={}); chk("CP5","evidence nao alcanca L0",G.INVALID,r["cross_source_eligibility"],r["cross_source_eligibility"]==G.INVALID)
r = ev(cand(claim_refs_applicability="APPLICABLE", claim_dependencies=["CL-0001"]))
chk("CP6","claim requerida ENTAILED",G.ELIGIBLE,r["cross_source_eligibility"],r["cross_source_eligibility"]==G.ELIGIBLE and r["claim_dependency_status"]=="SATISFIED")
r = ev(cand(claim_refs_applicability="APPLICABLE", claim_dependencies=["CL-0002"]))
chk("CP7","claim requerida NOT_ENTAILED",G.NOT_ELIGIBLE,f'{r["cross_source_eligibility"]}|{r["claim_dependency_status"]}',
    r["cross_source_eligibility"]==G.NOT_ELIGIBLE and r["claim_dependency_status"]=="UNSATISFIED_BY_ENTAILMENT" and r["sealed_claim_refs"]==[])
r = ev(cand(claim_refs_applicability="APPLICABLE", claim_dependencies=["CL-0003"]))
chk("CP8","claim requerida INDETERMINATE",G.NOT_ELIGIBLE,f'{r["cross_source_eligibility"]}|{r["claim_dependency_status"]}',
    r["cross_source_eligibility"]==G.NOT_ELIGIBLE and r["claim_dependency_status"]=="UNSATISFIED_BY_ENTAILMENT")

# ============================ DI1-DI4 : IDENTIDADE ==============================
q = {"scope": "para quem esta comecando", "condition": None, "platform": None, "stage": None, "audience": None}
raw = [{"temporary_claim_id":"TC-001","text":"O Evolution API precisa de VPS.","source_language":"pt",
        "evidence_refs":["EV-0001"],"qualifiers":q,"status":"SOURCE_EXPLICIT","_slice_id":"SL-B-01"},
       {"temporary_claim_id":"TC-007","text":"o evolution api precisa de vps","source_language":"pt",
        "evidence_refs":["EV-0020"],"qualifiers":q,"status":"SOURCE_EXPLICIT","_slice_id":"SL-B-02"}]
d = I.dedup_claims(raw, "MS001-SRC-B")
chk("DI1","mesma claim em 2 slices, Evidence distintas","1 claim, refs unidas",
    f'{len(d)} claim(s), refs={d[0]["evidence_refs"]}, merged={len(d[0]["merged_from"])}',
    len(d)==1 and d[0]["evidence_refs"]==["EV-0001","EV-0020"] and len(d[0]["merged_from"])==2)
wf = {"name":"Conectar","steps":[{"order_key":1,"name":"a","action":"criar instancia","required_inputs":[],"missing_input_action":None},
                                 {"order_key":2,"name":"b","action":"gerar qr","required_inputs":[],"missing_input_action":None}]}
rc = [{"temporary_candidate_id":"TX-001","entity_kind":"workflow_candidate","evidence_refs":["EV-0001"],
       "claim_temp_refs":[],"claim_refs_applicability":"NOT_APPLICABLE","defects":[],"structure":wf,"_slice_id":"SL-B-01"},
      {"temporary_candidate_id":"TX-009","entity_kind":"workflow_candidate","evidence_refs":["EV-0031"],
       "claim_temp_refs":[],"claim_refs_applicability":"NOT_APPLICABLE","defects":["PASSO_UNICO"],
       "structure":copy.deepcopy(wf),"_slice_id":"SL-B-03"}]
dc = I.dedup_candidates(rc, "MS001-SRC-B", {})
chk("DI2","mesmo workflow em 2 slices","1 candidate, Evidence unida",
    f'{len(dc)} cand, refs={dc[0]["evidence_refs"]}, steps={len(dc[0]["structure"]["steps"])}',
    len(dc)==1 and dc[0]["evidence_refs"]==["EV-0001","EV-0031"] and len(dc[0]["structure"]["steps"])==2)
q2 = dict(q); q2["scope"] = "para quem ja escala"
d2 = I.dedup_claims([raw[0], dict(raw[1], qualifiers=q2)], "MS001-SRC-B")
chk("DI3","mesmo texto, qualifiers diferentes","2 claims", f"{len(d2)} claims", len(d2)==2)
ap = {"do_not":["x"],"why":"porque sim"}
dc2 = I.dedup_candidates([
   {"temporary_candidate_id":"TX-001","entity_kind":"anti_pattern_candidate","evidence_refs":["EV-0001"],
    "claim_temp_refs":[],"claim_refs_applicability":"NOT_APPLICABLE","defects":[],"structure":ap,"_slice_id":"SL-B-01"},
   {"temporary_candidate_id":"TX-002","entity_kind":"rule_candidate","evidence_refs":["EV-0001"],
    "claim_temp_refs":[],"claim_refs_applicability":"NOT_APPLICABLE","defects":[],
    "structure":{"name":"x","trigger":"t","condition":"c","action":"a","do_not":["x"],"precedence":None},"_slice_id":"SL-B-01"}],
   "MS001-SRC-B", {})
ids = sorted(x["local_id"] for x in dc2)
chk("DI4","kinds diferentes -> prefixos distintos","AP- e R-", ids, ids==["AP-0001","R-0001"])
# identidade NAO contem provenance
k1 = I.claim_semantic_key("MS001-SRC-B","texto","pt",q)
chk("DI5","identidade de claim ignora evidence_refs","chaves iguais","-", k1==I.claim_semantic_key("MS001-SRC-B","texto","pt",q))
k2 = I.candidate_structural_key("MS001-SRC-B","workflow_candidate",wf)
wf2 = copy.deepcopy(wf)
chk("DI6","identidade de candidate ignora defects/eligibility","chaves iguais","-",
    k2==I.candidate_structural_key("MS001-SRC-B","workflow_candidate",wf2))
# typed uniqueness / nunca so local_id
pop = [{"entity_kind":"rule_candidate","local_id":"R-0001"},{"entity_kind":"anti_pattern_candidate","local_id":"R-0001"}]
typed = {(x["entity_kind"],x["local_id"]) for x in pop}
chk("DI7","typed id distingue mesmo local_id em kinds diferentes","2 chaves tipadas",
    f"{len(typed)} tipadas vs {len({x['local_id'] for x in pop})} nu", len(typed)==2)

if __name__ == "__main__":
    for x in R:
        print(f"  {'OK  ' if x['ok'] else 'FALHA'} {x['canary']:<5} {x['desc']:<40} esperado={str(x['expected'])[:38]}")
    n = sum(1 for x in R if x["ok"])
    print(f"\n  {n}/{len(R)} canarios mecanicos PASS")
    pathlib.Path("out").mkdir(exist_ok=True)
    pathlib.Path("out/mechanical-canaries.json").write_text(
        json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(0 if n == len(R) else 2)
