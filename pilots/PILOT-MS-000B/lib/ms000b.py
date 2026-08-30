#!/usr/bin/env python3
"""PILOT-MS-000B — biblioteca do piloto. Partes DETERMINISTICAS (sem modelo).

Escopo congelado em DECISION-RECORD-MS-000B-SCOPE.md:
  SOURCE = CHAPTER, scope = PILOT_MS_000B_ONLY
  source_independence = KNOWN_DEPENDENT nos dois
  cadeia FULL -> CUT -> SLICE -> SOURCE PACKAGE

Nada aqui le .docx. Nada aqui escreve nos L0 pais selados.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, unicodedata, collections

REPO = pathlib.Path("/home/mtx/course-to-skill-claude")
P    = REPO / "pilots/PILOT-MS-000B"
FULL = REPO / "_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript.txt"
CUT  = REPO / "_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt"
EVID = REPO / "_mirror/pilots/PILOT-002-v2/EVIDENCE.jsonl"
WF   = REPO / "_mirror/pilots/PILOT-002-v2/skill/knowledge/workflows.yaml"
DR   = REPO / "_mirror/pilots/PILOT-002-v2/skill/knowledge/decision-rules.yaml"
TMAP = REPO / "_mirror/pilots/PILOT-002-v2/temporal-map.yaml"

FULL_SHA = "43b58271feb0a1d518ae6f81ab29836eb9c7f2bec5eb02e53f70c7bd1eb514ed"
CUT_SHA  = "85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29"
EV_SHA   = "64853f7ac06a470f09333a80469b38e443ea5ce7aa3aee2e116ea1877059abfd"

CHAPTERS = {
  "A": {"n": 12, "titulo": "Managing Version Control with GitHub",
        "t_ini": 3202, "t_fim": 3762},
  "B": {"n": 13, "titulo": "Connecting Tools & Deploying Apps via MCP and CLI",
        "t_ini": 3767, "t_fim": 4312},
}

WS = re.compile(r"\s+")
def sha(b) -> str:
    if isinstance(b, (str, pathlib.Path)): b = pathlib.Path(b).read_bytes()
    return hashlib.sha256(b).hexdigest()
def sha_text(s: str) -> str: return hashlib.sha256(s.encode("utf-8")).hexdigest()
def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").casefold()
    return WS.sub(" ", s).strip()
def canon(o) -> str:
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

# ------------------------------------------------------------------ A. SLICER
MARK = re.compile(r"^\*\*(?:(\d+):)?(\d+):(\d{2})\*\*$")
def chapter_bounds(text):
    """Fronteiras vindas da PROPRIA FONTE: linhas '## '. Nao inventa fronteira."""
    lines = text.split("\n")
    idx = [(i, l[3:].strip()) for i, l in enumerate(lines) if l.startswith("## ")]
    out = []
    for k, (i, t) in enumerate(idx):
        j = idx[k+1][0] if k+1 < len(idx) else len(lines)
        out.append({"n": k+1, "titulo": t, "linha_ini": i, "linha_fim": j})
    return lines, out

def slice_chapter(cut_text, titulo):
    lines, chaps = chapter_bounds(cut_text)
    hit = [c for c in chaps if c["titulo"] == titulo]
    if len(hit) != 1:
        raise ValueError(f"fronteira nao unica para {titulo!r}: {len(hit)}")
    c = hit[0]
    body = "\n".join(lines[c["linha_ini"]:c["linha_fim"]])
    return body, c

# --------------------------------------------------------------- B. PACKAGER
def load_evidence():
    return [json.loads(l) for l in EVID.read_text(encoding="utf-8").splitlines() if l.strip()]

def build_package(key, cut_text, model_policy):
    """Monta um SOURCE PACKAGE experimental para um capitulo.

    local_id e RENUMERADO a partir de EV-0001 em CADA pacote — reproduz de
    proposito a colisao N9 sobre corpus real. A resolucao e por qualificacao.
    """
    ch = CHAPTERS[key]
    body, bounds = slice_chapter(cut_text, ch["titulo"])
    slice_sha = sha_text(body)
    ev_all = load_evidence()
    sel = [e for e in ev_all if ch["t_ini"] <= e["source_excerpt"]["span"]["start_s"] <= ch["t_fim"]]
    sel.sort(key=lambda e: e["source_excerpt"]["span"]["start_s"])

    body_norm = norm(body)
    items, anchors = [], []
    for i, e in enumerate(sel, 1):
        lid = f"EV-{i:04d}"                       # RENUMERADO: comeca em EV-0001 nos dois
        q = e["source_excerpt"]["quote"]
        sp = e["source_excerpt"]["span"]
        # D7: os TRES predicados sao distintos e medidos separadamente.
        #   LOCATED_IN      o span resolve dentro do artefato (a fatia)
        #   REPRODUCED_FROM a quote reaparece verbatim no artefato
        #   SUPPORTED_BY    substancia — julgamento, NAO medido aqui: NOT_APPLICABLE
        located = (ch["t_ini"] <= sp["start_s"] <= ch["t_fim"]
                   and ch["t_ini"] <= sp["end_s"] <= ch["t_fim"] + 8)
        reproduced = norm(q) in body_norm
        anchor = {"anchor_id": f"AN-{i:04d}", "anchor_type": "text_span_timecoded",
                  "artifact": "CHAPTER-SLICE", "slice_sha256": slice_sha,
                  "span": sp, "quote": q,
                  "LOCATED_IN": "PASS" if located else "FAIL",
                  "REPRODUCED_FROM": "PASS" if reproduced else "MISSING",
                  "SUPPORTED_BY": "NOT_APPLICABLE"}
        anchors.append(anchor)
        items.append({"local_id": lid, "origin_local_id_p002": e["evidence_id"],
                      "epistemic_status": e["epistemic_status"], "category": e["category"],
                      "claim_text_p002": e["claim"], "quote": q,
                      "span": e["source_excerpt"]["span"], "anchor_id": anchor["anchor_id"]})

    profile = {"artifact_id": f"MS000B-SOURCE-PROFILE-{key}",
               "scope": "PILOT_MS_000B_ONLY",
               "source_model": "SOURCE = CHAPTER (excecao experimental; producao = SOURCE curso / ARTIFACT aula)",
               "chapter_n": ch["n"], "chapter_titulo": ch["titulo"],
               "boundary_origin": "linha '## ' declarada pela propria fonte",
               "linha_ini": bounds["linha_ini"] + 1, "linha_fim": bounds["linha_fim"],
               "t_ini": ch["t_ini"], "t_fim": ch["t_fim"],
               "source_independence": "KNOWN_DEPENDENT",
               "independence_evidence": "mesmo autor, mesma gravacao, mesmo curso do PILOT-002",
               "authority": "DECLARED_EXTERNALLY (SOURCE-PROFILE); nunca derivada da qualidade das claims",
               "lang": "en", "text_source_lang": "en",
               "provenance_chain": {"FULL_L0": FULL_SHA, "CUT_L0": CUT_SHA,
                                    "CHAPTER_SLICE": slice_sha,
                                    "slice_derived_from": CUT_SHA,
                                    "slice_created_at": "2026-08-30",
                                    "nota": "o CHAPTER SLICE e artefato NOVO e derivado desta rodada; nao existia antes"},
               "evidence_source": {"path": str(EVID.relative_to(REPO)), "sha256": EV_SHA},
               "model_policy": model_policy,
               "items_count": len(items)}
    pkg = {"profile": profile, "anchors": anchors, "items": items}
    pkg["source_package_hash"] = sha_text(canon(pkg))
    return pkg, body

# --------------------------------------------- source-local candidates (workflow/rule)
def source_local_candidates(key):
    import yaml
    ch = CHAPTERS[key]
    tm = yaml.safe_load(TMAP.read_text(encoding="utf-8"))["temporal_map"]
    st = {s["segment_id"]: s.get("start_s") for s in tm}
    wf = yaml.safe_load(WF.read_text(encoding="utf-8"))
    dr = yaml.safe_load(DR.read_text(encoding="utf-8"))
    def in_ch(seg_ids):
        ts = [st[s] for s in (seg_ids or []) if s in st and st[s] is not None]
        return bool(ts) and ch["t_ini"] <= min(ts) <= ch["t_fim"]
    steps_by_wf = collections.defaultdict(list)
    for s in wf["steps"]: steps_by_wf[s["workflow_id"]].append(s)
    wcands = []
    for w in wf["workflows"]:
        ss = sorted(steps_by_wf[w["workflow_id"]], key=lambda x: x.get("order_key", 0))
        if not ss or not in_ch(ss[0].get("segment_ids")): continue
        wcands.append({"candidate_type": "WORKFLOW_CANDIDATE",
                       "local_id": w["workflow_id"], "name": w["name"],
                       "anchor_evidence_id": w.get("anchor_evidence_id"),
                       "evidence_ids": w.get("evidence_ids") or [],
                       "steps": [{"step_id": s["step_id"], "order_key": s.get("order_key"),
                                  "name": s.get("name"), "action": s.get("action"),
                                  "required_inputs": s.get("required_inputs"),
                                  "missing_input_action": s.get("missing_input_action"),
                                  "iteration_limit": s.get("iteration_limit"),
                                  "autonomy": s.get("autonomy"),
                                  "evidence_ids": s.get("evidence_ids") or []} for s in ss]})
    rcands = [{"candidate_type": "RULE_CANDIDATE", "local_id": r["rule_id"], "name": r.get("name"),
               "trigger": r.get("trigger"), "condition": r.get("condition"), "action": r.get("action"),
               "do_not": r.get("do_not") or [], "precedence": r.get("precedence"),
               "evidence_ids": r.get("evidence_ids") or []}
              for r in dr["decision_rules"] if in_ch(r.get("segment_ids"))]
    apats = [c for c in rcands if c["do_not"]]
    return {"workflow_candidates": wcands, "rule_candidates": rcands,
            "anti_pattern_candidates": [{"candidate_type": "ANTI_PATTERN_CANDIDATE",
                                         "local_id": c["local_id"], "do_not": c["do_not"],
                                         "evidence_ids": c["evidence_ids"]} for c in apats]}

def struct_hash(cands):
    """Hash canonico da ESTRUTURA source-local. Usado para provar travessia sem
    re-derivacao: qualquer reconstrucao silenciosa muda este hash."""
    return sha_text(canon(cands))

# ------------------------------------------------------- C. BLOCKER experimental
STOP = set("""a an the of to in on for with and or is are was were be been being this that these those
it its as at by from into over under after before while when where how what which who whom your you
we our they their he she his her i me my do does did done can could should would may might must will
shall not no nor if then than so such very just also only own same too s t don now then there here all
any both each few more most other some own get got go going make made use used using want need like""".split())
TOKEN = re.compile(r"[a-z0-9][a-z0-9\-_/\.]{2,}")
def content_tokens(s):
    return {t for t in TOKEN.findall(norm(s)) if t not in STOP and not t.isdigit()}

BLOCK_MIN_SHARED = 2   # REGRA ESTRUTURAL declarada ANTES de rodar. Nao e threshold ajustado.
def blocker(claims_a, claims_b, controls=()):
    """Reduz o espaco de pares cross-package ANTES da classificacao cara (D16).
    Regra: >= BLOCK_MIN_SHARED tokens de conteudo compartilhados. Declarada antes."""
    ta = {c["claim_id"]: content_tokens(c["text"]) for c in claims_a}
    tb = {c["claim_id"]: content_tokens(c["text"]) for c in claims_b}
    possible, survived = [], []
    for a in claims_a:
        for b in claims_b:
            possible.append((a["claim_id"], b["claim_id"]))
            if len(ta[a["claim_id"]] & tb[b["claim_id"]]) >= BLOCK_MIN_SHARED:
                survived.append((a["claim_id"], b["claim_id"]))
    ctrl = []
    for c in controls:                      # controles positivos SINTETICOS, fora da populacao
        shared = len(content_tokens(c["a_text"]) & content_tokens(c["b_text"]))
        ctrl.append({"control_id": c["control_id"], "shared": shared,
                     "survived": shared >= BLOCK_MIN_SHARED})
    return {"possible": len(possible), "survived": len(survived),
            "reduction_pct": (1 - len(survived)/len(possible))*100 if possible else None,
            "pairs": survived, "controls": ctrl,
            "rule": f"shared_content_tokens >= {BLOCK_MIN_SHARED}"}

# ------------------------------------------------- D. RELACOES — so mecanica (D15)
def relations_mechanical(claims_a, claims_b, pairs):
    """D15: relacao mecanicamente decidivel NUNCA e produzida por modelo.
    Nesta rodada so IDENTICAL (hash de conteudo normalizado). O resto = UNRELATED
    por DEFAULT (ausencia de asserçao), nao rotulo."""
    ha = {c["claim_id"]: sha_text(norm(c["text"])) for c in claims_a}
    hb = {c["claim_id"]: sha_text(norm(c["text"])) for c in claims_b}
    out = []
    for a, b in pairs:
        if ha[a] == hb[b]:
            out.append({"a": a, "b": b, "representation": "IDENTICAL",
                        "translated_comparison": False, "produced_by": "MECHANICAL_HASH"})
    return {"identical": out, "evaluated_pairs": len(pairs),
            "default": "UNRELATED (ausencia de asserçao; nenhum par obrigado a receber relacao)"}

# ------------------------------------------------------------- E. ISOLAMENTO
def isolation_check(pkg_a, pkg_b, claims_a, claims_b):
    """Informacao EXCLUSIVA de A nunca atribuida a B, e vice-versa.
    Exclusivo = token de conteudo presente nas quotes de um pacote e AUSENTE no outro."""
    qa = " ".join(i["quote"] for i in pkg_a["items"])
    qb = " ".join(i["quote"] for i in pkg_b["items"])
    ea, eb = content_tokens(qa), content_tokens(qb)
    excl_a, excl_b = ea - eb, eb - ea
    viol = []
    for c in claims_a:
        bad = content_tokens(c["text"]) & excl_b
        if bad: viol.append({"claim_id": c["claim_id"], "pacote": "A",
                             "tokens_exclusivos_do_outro": sorted(bad)})
    for c in claims_b:
        bad = content_tokens(c["text"]) & excl_a
        if bad: viol.append({"claim_id": c["claim_id"], "pacote": "B",
                             "tokens_exclusivos_do_outro": sorted(bad)})
    return {"exclusivos_A": len(excl_a), "exclusivos_B": len(excl_b),
            "violacoes": viol, "falsa_atribuicao": len(viol)}

# ---------------------------------------------------- F. FUSION PACKAGE experimental
def fusion_package(pkg_a, pkg_b, sealed_a, sealed_b, cand_a, cand_b, rel, blk):
    """SELETIVA: transporta a estrutura source-local, nao a reconstroi.
    fusion_id por conjunto ORDENADO de hashes, SEM mtx_policy_hash (I26)."""
    hashes = sorted([pkg_a["source_package_hash"], pkg_b["source_package_hash"]])
    fp = {"artifact_id": "MS000B-FUSION-PACKAGE-EXPERIMENTAL",
          "source_package_hashes": hashes,
          "mtx_policy_hash": None,
          "nota_I26": "fusion_id NAO inclui mtx_policy_hash; a fusao e cega a MTX-POLICY",
          "source_independence": {"A": "KNOWN_DEPENDENT", "B": "KNOWN_DEPENDENT",
                                  "nota": "corroboracao entre A e B NAO conta como independencia"},
          "corroboration_reporting": {"campos": 2, "nota": "contagem e estado de independencia, nunca colapsados (I15)"},
          "claims": {"A": [{**c, "qualified_id": [hashes and pkg_a["source_package_hash"], c["claim_id"]]} for c in sealed_a],
                     "B": [{**c, "qualified_id": [pkg_b["source_package_hash"], c["claim_id"]]} for c in sealed_b]},
          "transported_candidates": {"A": cand_a, "B": cand_b},
          "relations": rel, "blocking": {k: v for k, v in blk.items() if k != "pairs"},
          "synthesis": None,
          "nota_fusao": "SELETIVA: nenhum artefato novo sintetizado; nenhuma composicao atribuida as fontes (I21)"}
    fp["fusion_id"] = sha_text(canon({"h": hashes, "c": [c["claim_id"] for c in sealed_a] + [c["claim_id"] for c in sealed_b]}))
    return fp
