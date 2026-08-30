#!/usr/bin/env python3
"""ROUND 3 — SOURCE PACKAGE CONTRACT.

O pacote e um DIRETORIO, nao um blob JSON, porque e assim que o seal_verifier.py
do MS-000A opera. Nao se cria uma segunda definicao de selo.

TRES IDENTIDADES DISTINTAS
  SOURCE_ID            logica; estavel entre runs
  SOURCE_CONTENT_HASH  bytes do chapter slice; estavel se os bytes forem iguais
  SOURCE_PACKAGE_HASH  conjunto selado de UMA compilacao; muda com qualquer membro

TIMESTAMP NAO E IDENTIDADE: o COMPILE-TRACE membro carrega so campos
identity-relevant; timestamps vao para o OPERATIONAL-RUN-LOG, FORA do pacote.

REFERENCIAS: dentro do pacote usa-se {"ref_scope":"SELF","local_id":...}.
Nenhum membro conhece o hash do conjunto que o contem — isso resolve a
circularidade. A qualificacao (source_package_hash, local_id) e materializada
so na travessia de fronteira, no Fusion Package.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, unicodedata, collections, os

REPO = pathlib.Path("/home/mtx/course-to-skill-claude")
FULL = REPO/"_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript.txt"
CUT  = REPO/"_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt"
EVID = REPO/"_mirror/pilots/PILOT-002-v2/EVIDENCE.jsonl"
TMAP = REPO/"_mirror/pilots/PILOT-002-v2/temporal-map.yaml"
WF   = REPO/"_mirror/pilots/PILOT-002-v2/skill/knowledge/workflows.yaml"
DR   = REPO/"_mirror/pilots/PILOT-002-v2/skill/knowledge/decision-rules.yaml"
FULL_SHA="43b58271feb0a1d518ae6f81ab29836eb9c7f2bec5eb02e53f70c7bd1eb514ed"
CUT_SHA ="85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29"
EV_SHA  ="64853f7ac06a470f09333a80469b38e443ea5ce7aa3aee2e116ea1877059abfd"
FREEZE_SHA="6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b"
SEAL_CONTRACT_VERSION="SEALED/7-conditions/freeze-6d0eb7dd"

SOURCES = {
 "A": {"source_id":"MS000B-SRC-P002-CH12","chapter_n":12,
       "titulo":"Managing Version Control with GitHub","t_ini":3202,"t_fim":3762},
 "B": {"source_id":"MS000B-SRC-P002-CH13","chapter_n":13,
       "titulo":"Connecting Tools & Deploying Apps via MCP and CLI","t_ini":3767,"t_fim":4312},
}

# --- os 11 membros obrigatorios, nomenclatura LITERAL da v1 §4.1
REQUIRED_MEMBERS = [
 ("SOURCE-PROFILE",          "SOURCE-PROFILE.json"),
 ("L0",                      "L0/CHAPTER-SLICE.txt"),
 ("ARTIFACTS",               "ARTIFACTS/ARTIFACT-INDEX.json"),
 ("SOURCE_ANCHORS",          "SOURCE-ANCHORS.jsonl"),
 ("EVIDENCE",                "EVIDENCE.jsonl"),
 ("CLAIMS",                  "CLAIMS.jsonl"),
 ("SOURCE_LOCAL_CANDIDATES", "SOURCE-LOCAL-CANDIDATES.json"),
 ("COMPILE-TRACE",           "COMPILE-TRACE.jsonl"),
 ("LOCAL-COHERENCE-REPORT",  "LOCAL-COHERENCE-REPORT.json"),
 ("DECLARATION-SPACE-INDEX", "DECLARATION-SPACE-INDEX.json"),
 ("SEAL-RECORD",             "SEAL-RECORD.yaml"),
]
# artefato do PRODUTOR, exigido pela condicao 5 de SEALED. NAO e uma 12a categoria
# de conteudo: existe porque o contrato de selo pede referencia a TOOLCHAIN com
# hash proprio em vez de campo de texto.
TOOLCHAIN_PATH = "TOOLCHAIN.json"

WS=re.compile(r"\s+")
def sha_bytes(b)->str: return hashlib.sha256(b).hexdigest()
def sha_file(p)->str:  return sha_bytes(pathlib.Path(p).read_bytes())
def sha_text(s:str)->str: return sha_bytes(s.encode("utf-8"))
def canon(o)->str: return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def norm(s:str)->str:
    s=unicodedata.normalize("NFC",s or "").casefold(); return WS.sub(" ",s).strip()
def wjson(p,o):
    p=pathlib.Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(canon(o)+"\n",encoding="utf-8"); os.chmod(p,0o644)
def wjsonl(p,rows):
    p=pathlib.Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text("".join(canon(r)+"\n" for r in rows),encoding="utf-8"); os.chmod(p,0o644)
def wtext(p,s):
    p=pathlib.Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(s,encoding="utf-8"); os.chmod(p,0o644)

# ----------------------------------------------------------------- slice
def chapter_bounds(text):
    lines=text.split("\n")
    idx=[(i,l[3:].strip()) for i,l in enumerate(lines) if l.startswith("## ")]
    out=[]
    for k,(i,t) in enumerate(idx):
        j=idx[k+1][0] if k+1<len(idx) else len(lines)
        out.append({"n":k+1,"titulo":t,"linha_ini":i,"linha_fim":j})
    return lines,out

def slice_of(key, cut_text):
    s=SOURCES[key]; lines,ch=chapter_bounds(cut_text)
    hit=[c for c in ch if c["titulo"]==s["titulo"]]
    if len(hit)!=1: raise ValueError(f"fronteira nao unica: {len(hit)}")
    c=hit[0]; body="\n".join(lines[c["linha_ini"]:c["linha_fim"]])
    return body,c

# --------------------------------------------------- membros de conteudo
def build_content_members(key, cut_text, pkg_dir):
    """Fase A — constroi os membros identity-relevant, menos CLAIMS/TRACE/COHERENCE,
    que dependem da geracao. Devolve o material para as fases seguintes."""
    s=SOURCES[key]; body,bounds=slice_of(key,cut_text)
    content_hash=sha_text(body)
    wtext(pkg_dir/"L0/CHAPTER-SLICE.txt", body)

    ev_all=[json.loads(l) for l in EVID.read_text(encoding="utf-8").splitlines() if l.strip()]
    sel=sorted([e for e in ev_all if s["t_ini"]<=e["source_excerpt"]["span"]["start_s"]<=s["t_fim"]],
               key=lambda e:e["source_excerpt"]["span"]["start_s"])
    bn=norm(body); anchors=[]; evidence=[]
    for i,e in enumerate(sel,1):
        lid=f"EV-{i:04d}"; aid=f"AN-{i:04d}"; q=e["source_excerpt"]["quote"]
        sp=e["source_excerpt"]["span"]
        located = s["t_ini"]<=sp["start_s"]<=s["t_fim"] and s["t_ini"]<=sp["end_s"]<=s["t_fim"]+8
        anchors.append({"local_id":aid,"anchor_type":"text_span_timecoded",
                        "artifact_ref":{"ref_scope":"SELF","local_id":"ART-SLICE"},
                        "span":sp,"quote":q,
                        "LOCATED_IN":"PASS" if located else "FAIL",
                        "REPRODUCED_FROM":"PASS" if norm(q) in bn else "MISSING",
                        "SUPPORTED_BY":"NOT_APPLICABLE"})
        evidence.append({"local_id":lid,"anchor_ref":{"ref_scope":"SELF","local_id":aid},
                         "epistemic_status":e["epistemic_status"],"category":e["category"],
                         "quote":q,"span":sp,"origin_local_id_p002":e["evidence_id"]})
    wjsonl(pkg_dir/"SOURCE-ANCHORS.jsonl",anchors)
    wjsonl(pkg_dir/"EVIDENCE.jsonl",evidence)

    import yaml
    tm=yaml.safe_load(TMAP.read_text(encoding="utf-8"))["temporal_map"]
    segs=[x for x in tm if s["t_ini"]<=x["start_s"]<=s["t_fim"]]
    wjson(pkg_dir/"ARTIFACTS/temporal-map-slice.json",segs)
    wjson(pkg_dir/"ARTIFACTS/ARTIFACT-INDEX.json",{
      "artifacts":[
        {"local_id":"ART-SLICE","kind":"CHAPTER_SLICE","path":"L0/CHAPTER-SLICE.txt",
         "sha256":content_hash,"derived_from":{"CUT_L0":CUT_SHA},"bytes":len(body.encode())},
        {"local_id":"ART-TMAP","kind":"TEMPORAL_MAP_SLICE","path":"ARTIFACTS/temporal-map-slice.json",
         "sha256":sha_file(pkg_dir/"ARTIFACTS/temporal-map-slice.json"),"segments":len(segs)}],
      "upstream_by_hash_only":{"FULL_L0":FULL_SHA,"CUT_L0":CUT_SHA,
        "nota":"bytes grandes resolvidos por proveniencia/hash; nao duplicados"}})

    # SOURCE-PROFILE: SO fatos da fonte. Sem model/prompt/judge/thinking/partition.
    profile={"artifact_id":f"MS000B-R3-SOURCE-PROFILE-{key}",
      "source_id":s["source_id"],"source_content_hash":content_hash,
      "lang":"en","text_source_lang":"en",
      "author":"PILOT-002 course instructor (single author, single recording)",
      "media":{"platform":"youtube","kind":"AUTO_GENERATED_ASR_TRANSCRIPT"},
      "boundary":{"origin":"linha '## ' declarada pela propria fonte",
                  "chapter_n":s["chapter_n"],"titulo":s["titulo"],
                  "linha_ini":bounds["linha_ini"]+1,"linha_fim":bounds["linha_fim"],
                  "t_ini":s["t_ini"],"t_fim":s["t_fim"]},
      "provenance_chain":{"FULL_L0":FULL_SHA,"CUT_L0":CUT_SHA,
        "CHAPTER_SLICE":content_hash,"slice_derived_from":CUT_SHA,
        "nota":"CHAPTER SLICE e artefato derivado; os pais selados nao sao escritos"},
      "source_independence":"KNOWN_DEPENDENT",
      "independence_evidence":"mesmo autor, mesma gravacao, mesmo curso do PILOT-002",
      "authority":"DECLARED_EXTERNALLY (D37); nunca derivada da qualidade das claims",
      "scope":"PILOT_MS_000B_ONLY",
      "source_model_note":"SOURCE = CHAPTER e excecao de piloto; producao permanece SOURCE=curso / ARTIFACT=aula",
      "excluded_by_contract":["model","prompt_version","judge_version","thinking",
                              "max_tokens","partition","model_outputs",
                              "timestamps operacionais"]}
    wjson(pkg_dir/"SOURCE-PROFILE.json",profile)
    return {"body":body,"content_hash":content_hash,"anchors":anchors,"evidence":evidence,
            "profile":profile,"segments":segs}

# ------------------------------------------- membros que dependem da geracao
def write_generated_members(pkg_dir, claims, candidates, trace_rows):
    wjsonl(pkg_dir/"CLAIMS.jsonl", claims)
    wjson (pkg_dir/"SOURCE-LOCAL-CANDIDATES.json", candidates)
    wjsonl(pkg_dir/"COMPILE-TRACE.jsonl", trace_rows)

def local_coherence(pkg_dir):
    """LOCAL-COHERENCE-REPORT — MECANICO. Nao julga semantica."""
    ev=[json.loads(l) for l in (pkg_dir/"EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    an=[json.loads(l) for l in (pkg_dir/"SOURCE-ANCHORS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    cl=[json.loads(l) for l in (pkg_dir/"CLAIMS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    cand=json.loads((pkg_dir/"SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8"))
    art=json.loads((pkg_dir/"ARTIFACTS/ARTIFACT-INDEX.json").read_text(encoding="utf-8"))
    evi={e["local_id"] for e in ev}; ani={a["local_id"] for a in an}
    arti={a["local_id"] for a in art["artifacts"]}
    dup=lambda xs:[k for k,n in collections.Counter(xs).items() if n>1]
    findings=[]
    def f(code,items,detail=""):
        if items: findings.append({"code":code,"n":len(items),"items":items[:10],"detail":detail})
    f("DUPLICATE_LOCAL_ID_EVIDENCE",dup([e["local_id"] for e in ev]))
    f("DUPLICATE_LOCAL_ID_ANCHOR",  dup([a["local_id"] for a in an]))
    f("DUPLICATE_LOCAL_ID_CLAIM",   dup([c["local_id"] for c in cl]))
    f("EVIDENCE_ANCHOR_REF_BROKEN", [e["local_id"] for e in ev if e["anchor_ref"]["local_id"] not in ani])
    f("ANCHOR_ARTIFACT_REF_BROKEN", [a["local_id"] for a in an if a["artifact_ref"]["local_id"] not in arti])
    f("ANCHOR_NOT_LOCATED",         [a["local_id"] for a in an if a["LOCATED_IN"]!="PASS"])
    f("CLAIM_WITHOUT_EVIDENCE",     [c["local_id"] for c in cl if not c.get("evidence_refs")])
    f("CLAIM_EVIDENCE_REF_BROKEN",  [c["local_id"] for c in cl
                                     if any(r["local_id"] not in evi for r in c.get("evidence_refs",[]))])
    f("CLAIM_REF_NOT_SELF",         [c["local_id"] for c in cl
                                     if any(r.get("ref_scope")!="SELF" for r in c.get("evidence_refs",[]))])
    bad_c=[]
    for kind in ("rule_candidates","workflow_candidates","anti_pattern_candidates"):
        for c in cand.get(kind,[]):
            if any(r["local_id"] not in evi for r in c.get("evidence_refs",[])): bad_c.append(c["local_id"])
    f("CANDIDATE_EVIDENCE_REF_BROKEN",bad_c)
    badw=[]
    for w in cand.get("workflow_candidates",[]):
        ks=[s.get("order_key") for s in w["steps"]]
        if not w["steps"] or any(k is None for k in ks) or ks!=sorted(ks) or len(set(ks))!=len(ks):
            badw.append(w["local_id"])
    f("WORKFLOW_STRUCTURALLY_INVALID",badw)
    present=[n for n,p in REQUIRED_MEMBERS if (pkg_dir/p).is_file()]
    missing=[n for n,p in REQUIRED_MEMBERS if not (pkg_dir/p).is_file()]
    rep={"artifact_id":"MS000B-R3-LOCAL-COHERENCE-REPORT","kind":"MECHANICAL_ONLY",
         "SEMANTIC_COHERENCE_NOT_EVALUATED_IN_MS_000B":True,
         "nota":"coerencia MECANICA. Nao e 'semantic coherence PASS'.",
         "counts":{"evidence":len(ev),"anchors":len(an),"claims":len(cl),
                   "rule_candidates":len(cand.get("rule_candidates",[])),
                   "workflow_candidates":len(cand.get("workflow_candidates",[])),
                   "anti_pattern_candidates":len(cand.get("anti_pattern_candidates",[]))},
         "required_members_present":present,
         "required_members_missing_at_report_time":missing,
         "inherited_defects":[
            {"id":"N9","desc":"local ids reiniciam em EV-0001 em cada pacote; colisao global deliberada",
             "mitigation":"qualificacao (source_package_hash, local_id) na travessia de fronteira"},
            {"id":"P002-HELDOUT","desc":"o CUT teve os capitulos 6 e 10 removidos; nao afeta 12/13",
             "mitigation":"capitulos 12 e 13 verificados intactos"}],
         "findings":findings,"mechanically_coherent":not findings}
    wjson(pkg_dir/"LOCAL-COHERENCE-REPORT.json",rep); return rep

def declaration_space_index(pkg_dir, source_id, content_hash):
    """BOUNDED por pacote. Nao vira auditoria de todo o Git/Drive."""
    idx={"artifact_id":"MS000B-R3-DECLARATION-SPACE-INDEX","bounded_by":"THIS_SOURCE_PACKAGE",
      "nota":"enumeracao limitada ao que este pacote realmente resolve. "
             "'filesystem scan != corpus audit' permanece verdadeiro globalmente.",
      "spaces":[
        {"kind":"SELF","what":"o proprio Source Package","resolve":"member manifest do SEAL-RECORD"},
        {"kind":"SOURCE_LINEAGE","what":"FULL -> CUT -> SLICE",
         "FULL_L0":FULL_SHA,"CUT_L0":CUT_SHA,"CHAPTER_SLICE":content_hash},
        {"kind":"EVIDENCE_UPSTREAM","what":"EVIDENCE.jsonl do PILOT-002-v2","sha256":EV_SHA},
        {"kind":"GOVERNING_CONTRACT","what":"ARCHITECTURE FREEZE","sha256":FREEZE_SHA,
         "seal_contract_version":SEAL_CONTRACT_VERSION},
        {"kind":"DECISION_RECORDS","what":"decisoes que governam este pacote",
         "refs":["DR-MS-000A-001","DR-MS-000B-001","DR-MS-000B-R1-001","DR-MS-000B-R3-001"]},
        {"kind":"COMMITS","what":"commits citados pelos artefatos acima",
         "refs":["8d3bc019f150e1f54feaa09c73461513c87e4c40",
                 "66b153b9d8e9c0e06a8aefeccc38cc31f605b3a6"]}],
      "source_id":source_id,
      "explicitly_out_of_scope":["varredura de todo o repositorio","varredura do Drive",
                                 "enumeracao de repos/refs nao congelada pelo freeze"]}
    wjson(pkg_dir/"DECLARATION-SPACE-INDEX.json",idx); return idx

# ---------------------------- Fases B..E: manifesto, hash, selo, registro externo
def member_manifest(pkg_dir):
    """Fase B — caminho relativo + sha256, ordenado LC_ALL=C, SEM o SEAL-RECORD."""
    seal=dict(REQUIRED_MEMBERS)["SEAL-RECORD"]
    rows=[]
    for p in sorted(pkg_dir.rglob("*")):
        if not p.is_file(): continue
        rel=str(p.relative_to(pkg_dir))
        if rel==seal: continue                      # condicao 7: nao se auto-referencia
        rows.append({"path":rel,"sha256":sha_file(p)})
    return sorted(rows,key=lambda r:r["path"])

def source_package_hash(manifest)->str:
    """Fase C — SOURCE_PACKAGE_HASH := sha256(canon(member_manifest))."""
    return sha_text(canon(manifest))

def write_toolchain(pkg_dir):
    tc={"artifact_id":"MS000B-R3-TOOLCHAIN","components":["git","python3","hashlib/sha256","anthropic-sdk"],
        "seal_contract_version":SEAL_CONTRACT_VERSION,
        "nota":"artefato de PRODUTOR exigido pela condicao 5 de SEALED; nao e uma 12a categoria de conteudo"}
    wjson(pkg_dir/TOOLCHAIN_PATH,tc); return sha_file(pkg_dir/TOOLCHAIN_PATH)

def seal(pkg_dir, source_id, content_hash, registry_path):
    """Fases D e E."""
    man=member_manifest(pkg_dir); ph=source_package_hash(man)
    mh=sha_text(canon(man))
    tc_sha=sha_file(pkg_dir/TOOLCHAIN_PATH)
    lines=["# MS-000B ROUND 3 — SEAL-RECORD",
           "# Cumpre as sete condicoes de SEALED do ARCHITECTURE FREEZE.",
           "# Nao se auto-referencia (condicao 7). Nao usa mtime (condicao 6).",
           f"artifact_id: MS000B-R3-SEAL-RECORD",
           f"artifact_status: SEALED",
           f"seal_contract_version: '{SEAL_CONTRACT_VERSION}'",
           f"source_id: '{source_id}'",
           f"source_content_hash: '{content_hash}'",
           f"member_manifest_hash: '{mh}'",
           f"source_package_hash: '{ph}'",
           "producer:",
           f"  toolchain_path: {TOOLCHAIN_PATH}",
           f"  toolchain_sha256: '{tc_sha}'",
           f"members_count: {len(man)}",
           "members:"]
    for m in man:
        lines+= [f"  - path: {m['path']}", f"    sha256: '{m['sha256']}'"]
    wtext(pkg_dir/dict(REQUIRED_MEMBERS)["SEAL-RECORD"], "\n".join(lines)+"\n")
    seal_sha=sha_file(pkg_dir/dict(REQUIRED_MEMBERS)["SEAL-RECORD"])
    reg=pathlib.Path(registry_path); reg.parent.mkdir(parents=True,exist_ok=True)
    with reg.open("a",encoding="utf-8") as fh:
        fh.write(f"{seal_sha}  {pkg_dir.name}/SEAL-RECORD.yaml  source_package_hash={ph}\n")
    return {"source_package_hash":ph,"member_manifest_hash":mh,"seal_record_hash":seal_sha,
            "members_count":len(man),"manifest":man}

# ------------------------------------------------- COMPLETENESS GATE (!= selo)
def completeness_gate(pkg_dir):
    """Confronta o pacote contra os 11 membros obrigatorios congelados.
    O selo NAO detecta membro que nunca entrou no manifesto — por isso este
    instrumento e SEPARADO."""
    missing=[{"member":n,"path":p} for n,p in REQUIRED_MEMBERS if not (pkg_dir/p).is_file()]
    empty  =[{"member":n,"path":p} for n,p in REQUIRED_MEMBERS
             if (pkg_dir/p).is_file() and (pkg_dir/p).stat().st_size==0]
    codes=[]
    if missing: codes.append("REQUIRED_MEMBER_MISSING")
    if empty:   codes.append("REQUIRED_MEMBER_EMPTY")
    if not (pkg_dir/TOOLCHAIN_PATH).is_file(): codes.append("PRODUCER_ARTIFACT_MISSING")
    return {"verdict":"PASS" if not codes else "FAIL","codes":codes,
            "missing":missing,"empty":empty,"required_total":len(REQUIRED_MEMBERS)}
