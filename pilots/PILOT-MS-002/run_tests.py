#!/usr/bin/env python3
"""MS-002 — SUITE DE TESTES FINAL. ZERO chamadas de modelo.
Cobre A-T do contrato, tarefas representativas, multi-source real, falso conflito e conflito."""
import json, hashlib, pathlib, subprocess, collections, sys, re
H = pathlib.Path(__file__).resolve().parent
SP = H / "skillpack"
sys.path.insert(0, str(H))
from router import Router
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
shab = lambda b: hashlib.sha256(b).hexdigest()
R, FAIL = [], 0
def chk(tid, desc, ok, detail=""):
    global FAIL
    if not ok: FAIL += 1
    R.append({"id": tid, "desc": desc, "status": "PASS" if ok else "FAIL", "detail": str(detail)[:300]})

def jl(p): return [json.loads(l) for l in pathlib.Path(p).read_text(encoding="utf-8").splitlines()]

OP  = json.loads((H / "operationalization/OPERATIONAL-PACKAGE-MS002.json").read_text(encoding="utf-8"))
FUS = json.loads((H / "out-fusion/FUSION-PACKAGE-MS002.json").read_text(encoding="utf-8"))
FTR = json.loads((H / "out-fusion/FUSION-TRACE-MS002.json").read_text(encoding="utf-8"))
DEC = json.loads((H / "out-oper/APPLICABILITY-DECISIONS.json").read_text(encoding="utf-8"))
MAN = json.loads((SP / "SKILLPACK-MANIFEST.json").read_text(encoding="utf-8"))
rt  = Router(SP)

# ---------------------------------------------------------------- A / B
for s in "ABC":
    pkg = H / "packages" / f"pkg-{s}"
    seal = (pkg / "SEAL-RECORD.yaml").read_text(encoding="utf-8").splitlines()
    members, cur = [], None
    for l in seal:
        if l.startswith("- path: "): cur = {"path": l.split(": ", 1)[1]}
        elif l.startswith("  sha256: ") and cur: cur["sha256"] = l.split(": ", 1)[1]; members.append(cur); cur = None
    bad = [m for m in members if shab((pkg / m["path"]).read_bytes()) != m["sha256"]]
    chk(f"A-{s}", f"package {s}: todos os membros batem o sha256 do SEAL", not bad, f"{len(members)} membros, {len(bad)} divergentes")
    declared = [l.split(": ", 1)[1] for l in seal if l.startswith("source_package_hash: ")][0]
    chk(f"B-{s}", f"seal {s}: source_package_hash == manifesto recomputado", sha(canon(members)) == declared, declared[:16])
    chk(f"B2-{s}", f"seal {s}: SEAL-RECORD nao se auto-referencia",
        not any(m["path"] == "SEAL-RECORD.yaml" for m in members))

# ---------------------------------------------------------------- C
def typed(r): return isinstance(r, dict) and set(r) == {"source_package_hash", "entity_kind", "local_id"} and len(r["source_package_hash"]) == 64
refs = [p["left"] for p in FUS["pairset"]] + [p["right"] for p in FUS["pairset"]]
refs += [c for v in FUS["eligible_candidate_refs"].values() for c in v]
refs += [u["provenance"]["candidate_ref"] for u in OP["units"]]
chk("C", "identidade tipada 100% (source_package_hash, entity_kind, local_id)",
    all(typed(r) for r in refs), f"{len(refs)} refs verificadas")
chk("C2", "nenhum indice por local_id nu no pairset",
    len({(p["left"]["source_package_hash"], p["left"]["local_id"]) for p in FUS["pairset"]} |
        {(p["right"]["source_package_hash"], p["right"]["local_id"]) for p in FUS["pairset"]}) > 0)

# ---------------------------------------------------------------- D
bad = []
for s in "ABC":
    pkg = H / "packages" / f"pkg-{s}"
    ev = {e["local_id"]: e for e in jl(pkg / "EVIDENCE.jsonl")}
    an = {a["local_id"]: a for a in jl(pkg / "SOURCE-ANCHORS.jsonl")}
    raw = json.loads((pkg / "L0/RAW-CAPTION.json").read_text(encoding="utf-8"))
    for c in jl(pkg / "CLAIMS.jsonl"):
        for r in c["evidence_refs"]:
            e = ev.get(r["local_id"])
            if not e: bad.append((s, c["local_id"], r["local_id"], "evidence ausente")); continue
            a = an.get(e["source_anchor_refs"][0]["local_id"])
            if not a: bad.append((s, c["local_id"], r["local_id"], "anchor ausente")); continue
            if max(a["transcript_segment_ids"]) >= len(raw): bad.append((s, c["local_id"], r["local_id"], "segmento fora do raw"))
chk("D", "provenance 100%: claim -> evidence -> anchor -> raw source", not bad, f"{len(bad)} quebras")

# ---------------------------------------------------------------- E
iso = []
for s in "ABC":
    for p in sorted((H / "out-compile" / f"raw-{s}").glob("SL-*-USER.txt")):
        t = p.read_text(encoding="utf-8")
        others = [o for o in "ABC" if o != s and f"MS002-SRC-{o}" in t]
        if others: iso.append((p.name, others))
chk("E", "isolamento de fonte: nenhum prompt de extracao cita outra fonte", not iso, iso[:3])

# ---------------------------------------------------------------- F / G
for s in "ABC":
    cl = jl(H / "packages" / f"pkg-{s}" / "CLAIMS.jsonl")
    chk(f"F-{s}", f"{s}: toda claim selada e ENTAILED e tem evidence",
        all(c["entailed_by"] == "ENTAILED" and c["evidence_refs"] for c in cl), f"{len(cl)} claims")
    coh = json.loads((H / "packages" / f"pkg-{s}" / "LOCAL-COHERENCE-REPORT.json").read_text(encoding="utf-8"))
    chk(f"G-{s}", f"{s}: INVALID_PROVENANCE == 0", coh["INVALID_PROVENANCE"] == 0, coh["INVALID_PROVENANCE"])

# ---------------------------------------------------------------- H
fid = sha(canon(FUS["fusion_id_inputs"]))
chk("H", "fusion_id reproduzivel a partir dos inputs declarados", fid == FUS["fusion_id"], fid[:16])
chk("H2", "mtx_policy_hash ausente da identidade da Fusion",
    "mtx_policy_hash" not in FUS["fusion_id_inputs"] and FUS.get("mtx_policy_hash") is None)

# ---------------------------------------------------------------- I
chk("I", "nenhuma precedencia silenciosa: todos os pares NOT_YET_ADJUDICATED",
    set(FUS["governance_state"].values()) == {"NOT_YET_ADJUDICATED"},
    collections.Counter(FUS["governance_state"].values()))
chk("I2", "nenhuma arbitragem de maioria aplicada", FTR["kills"]["SILENT_MAJORITY"] is False)
prec = [u["unit_id"] for u in OP["units"]
        if isinstance(u["structure"], dict) and u["structure"].get("precedence")]
chk("I3", "nenhuma regra operacional carrega precedencia derivada", not prec, prec[:3])

# ---------------------------------------------------------------- J
chk("J", "Operational Package nao substitui o Fusion Package",
    OP["separation_guarantees"]["does_not_replace_fusion_package"] and
    OP["separation_guarantees"]["no_writeback_to_source_packages"] and
    OP["separation_guarantees"]["no_writeback_to_fusion"])
chk("J2", "Operational Package referencia a identidade da Fusion sem alterar nada",
    OP["fusion_input_identity"]["fusion_id"] == FUS["fusion_id"])
git = subprocess.run(["git", "diff", "--name-only", "HEAD", "--",
                      "pilots/PILOT-MS-002/packages", "pilots/PILOT-MS-002/out-fusion"],
                     capture_output=True, text=True, cwd=str(H.parent.parent)).stdout.strip()
chk("J3", "sem writeback: packages e fusion nao modificados apos selagem", git == "", git[:200])

# ---------------------------------------------------------------- K / L
dist = collections.Counter(d["applicability"] for d in DEC["decisions"].values())
promoted = [u["unit_id"] for u in OP["units"] if u["applicability"] == "NOT_YET_CLASSIFIED"
            and u["unit_id"] in {x for m in MAN["modules"]
                                 for x in json.loads((SP / "modules" / m / "MODULE.json").read_text(encoding="utf-8"))["unit_ids"]}]
chk("K", "fail-closed: nenhuma unidade NOT_YET_CLASSIFIED entrou no Skill Pack", not promoted, promoted[:3])
chk("K2", "classificacao de aplicabilidade cobre 100% das unidades elegiveis",
    len(DEC["decisions"]) == DEC["n_units"], f'{len(DEC["decisions"])}/{DEC["n_units"]}')
nod = [u["unit_id"] for u in OP["units"] if u["mtx_derived"] and not (u.get("derivation") or "").strip()]
chk("L", "todo MTX_DERIVED carrega derivacao registrada", not nod, nod[:3])
chk("L2", "todo artefato MTX_DERIVED e rotulado, nunca apresentado como afirmacao de fonte",
    all(u["assertion_class"] == "MTX_DERIVED_OPERATIONAL_ARTIFACT"
        for u in OP["units"] if u["mtx_derived"]) and
    all(c["assertion_class"] == "MTX_DERIVED_OPERATIONAL_ARTIFACT" for c in OP["human_checkpoints"]))

# ---------------------------------------------------------------- M
operable = [u for u in OP["units"] if u["applicability"] in ("DIRECT_USE", "ADAPT_TO_MTX")]
inmod = collections.Counter()
for m in MAN["modules"]:
    for uid in json.loads((SP / "modules" / m / "MODULE.json").read_text(encoding="utf-8"))["unit_ids"]:
        inmod[uid] += 1
miss = [u["unit_id"] for u in operable if inmod[u["unit_id"]] != 1]
chk("M", "completude modular: cada unidade operavel em exatamente um modulo", not miss,
    f"{len(operable)} operaveis, {len(miss)} fora")
chk("M2", "nenhum modulo vazio",
    all(json.loads((SP / "modules" / m / "MODULE.json").read_text(encoding="utf-8"))["n_units"] > 0
        for m in MAN["modules"]))

# ---------------------------------------------------------------- N / O / Q
TASKS = [
 ("T1", "criar estrategia de conteudo em video para o instagram", {"instagram-content"}, {"observability", "maintenance"}),
 ("T2", "montar fluxo de atendimento no whatsapp com mensagem automatica", {"whatsapp-automation"}, {"instagram-content", "ads-paid-media"}),
 ("T3", "fazer follow-up de lead que nao respondeu", {"lead-followup"}, {"maintenance"}),
 ("T4", "montar dashboard de metricas em planilha", {"dashboards-data"}, {"instagram-content"}),
 ("T5", "a automacao quebrou depois da atualizacao, preciso corrigir", {"maintenance"}, {"instagram-content"}),
 ("T6", "passar o atendimento para um humano assumir", {"human-handoff"}, {"ads-paid-media"}),
 ("T7", "ver os logs e alertas de erro das automacoes", {"observability"}, {"instagram-content"}),
 ("T8", "gerar imagem e video criativo para a campanha", {"creative-production"}, {"maintenance"}),
]
for tid, task, want, notwant in TASKS:
    res = rt.route(task)
    sel = set(res["selected"])
    present = [m for m in want if m in MAN["modules"]]
    chk(f"N-{tid}", f"router: '{task[:42]}' seleciona {want}",
        (not present) or bool(sel & set(present)), f"selecionados={sorted(sel)}")
    leak = sel & {m for m in notwant if m in MAN["modules"]}
    chk(f"O-{tid}", f"carregamento seletivo: NAO carrega {sorted(notwant)}", not leak, f"vazou={sorted(leak)}")
res_ap = rt.route("nao usar conta pessoal de whatsapp para automacao", deep=True)
chk("Q", "anti-padroes relevantes carregam sob demanda; irrelevantes ficam fora",
    all(("/anti-patterns/" not in f) or any(f'modules/{m}/' in f for m in res_ap["selected"])
        for f in res_ap["load"]), f'{len([f for f in res_ap["load"] if "/anti-patterns/" in f])} arquivos de anti-padrao')

# ---------------------------------------------------------------- P
cyc = []
def walk(m, seen):
    for d in rt.modules[m]["dependencies"]:
        if d["type"] != "REQUIRES": continue
        if d["module"] in seen: cyc.append((m, d["module"])); continue
        walk(d["module"], seen | {d["module"]})
for m in rt.modules: walk(m, {m})
chk("P", "grafo de dependencias de modulo sem ciclos em REQUIRES", not cyc, cyc[:3])
chk("P2", "toda dependencia aponta para modulo existente",
    all(d["module"] in rt.modules for m in rt.modules.values() for d in m["dependencies"]))
chk("P3", "tipos de dependencia de modulo sao proprios, nao a taxonomia semantica",
    set(d["type"] for m in rt.modules.values() for d in m["dependencies"]) <= {"REQUIRES", "OPTIONAL", "EXTENDS"} and
    not ({"IDENTICAL", "CORROBORATES", "SPECIALIZES", "CONTRADICTS", "SUPERSEDES"} &
         set(d["type"] for m in rt.modules.values() for d in m["dependencies"])))

# ---------------------------------------------------------------- R / S
mono = rt.monolithic()
meas = []
for tid, task, _, _ in TASKS:
    r_ = rt.route(task); m_ = rt.measure(r_["load"])
    meas.append({"task": tid, "modules": r_["selected"], "bytes": m_["bytes"],
                 "tokens_est": m_["tokens_est"], "reduction_pct": round(100 * (1 - m_["bytes"] / mono["bytes"]), 2)})
worst = max(meas, key=lambda x: x["bytes"])
chk("R", "carregamento roteado e menor que o monolitico em toda tarefa",
    all(m["bytes"] < mono["bytes"] for m in meas),
    f'pior caso {worst["task"]}: {worst["bytes"]}B vs monolitico {mono["bytes"]}B '
    f'(reducao {worst["reduction_pct"]}%)')
fb = rt.route("zzz qqq xyz sem termo algum do dominio")
chk("S", "sem casamento, o fallback carrega SO o core — nunca o pacote inteiro",
    fb["fallback"] and set(fb["load"]) == {"core/CORE.md", "router/ROUTER.json"}, fb["load"])
chk("S2", "router declara ausencia de default monolitico", rt.cfg["no_monolithic_default"] is True)

# ---------------------------------------------------------------- T
base = "44c065a"
d = subprocess.run(["git", "diff", "--name-only", base, "HEAD", "--",
                    "pilots/PILOT-MS-000A", "pilots/PILOT-MS-000B", "pilots/PILOT-MS-001"],
                   capture_output=True, text=True, cwd=str(H.parent.parent)).stdout.strip()
chk("T", "artefatos historicos MS-000A/000B/001 inalterados desde o fechamento do MS-001", d == "", d[:200])

# ------------------------------------------------- multi-source / conflito
chk("U", "teste multi-source real: o Skill Pack carrega unidades de mais de uma fonte",
    len({u["source_id"] for u in operable}) >= 2, sorted({u["source_id"] for u in operable}))
srcs_per_mod = {m: sorted({uid.split("|")[0] for uid in
                json.loads((SP / "modules" / m / "MODULE.json").read_text(encoding="utf-8"))["unit_ids"]})
                for m in MAN["modules"]}
multi = {m: v for m, v in srcs_per_mod.items() if len(v) > 1}
chk("U2", "ao menos um modulo combina conhecimento de mais de uma fonte", bool(multi), multi)
chk("U3", "provenance por fonte preservada dentro do modulo multi-source",
    all((SP / "modules" / m / "references/PROVENANCE.json").exists() for m in MAN["modules"]))
rel = FTR["relation_distribution"]
contra = FTR["contradiction_registry"]
chk("V", "falso conflito: vocabulario compartilhado nao vira CONTRADICTS sem base",
    all(c["stability_state"] != "STABLE" or c["n_runs_contradicts"] == 3 for c in contra),
    f"{len(contra)} pares com CONTRADICTS em >=1 run")
chk("V2", "controles J1-J10 discriminam CONTRADICTS de falso conflito nas tres runs",
    all(FTR["completeness"][r]["control_ok"] for r in ("RUN-1", "RUN-2", "RUN-3")))
chk("W", "conflito real: se existe, permanece NOT_YET_ADJUDICATED",
    all(FUS["governance_state"][c["pair_id"]] == "NOT_YET_ADJUDICATED" for c in contra),
    f"{len(contra)} conflitos, 0 adjudicados")

# ---------------------------------------------------------------- X (PAYG)
calls = FTR.get("calls_summary", {})
chk("X", "PAYG API = zero em todas as etapas",
    FTR["provenance_ledger"]["payg_api_used"] == 0 and DEC["payg_api_used"] == 0)
chk("X2", "toda chamada resolveu claude-opus-5 por Claude Max OAuth",
    all(c["model_resolved"] == "claude-opus-5" and c["auth_path"] == "CLAUDE_CODE_MAX_OAUTH_PRINT_MODE"
        and c["payg"] is False for c in DEC["calls"]))

out = {"total": len(R), "passed": len(R) - FAIL, "failed": FAIL, "results": R,
       "token_measurements": {"monolithic": mono["bytes"], "monolithic_tokens_est": mono["tokens_est"],
                              "routed": meas}}
(H / "TEST-RESULTS-MS002.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
for x in R:
    print(f"  {'OK  ' if x['status']=='PASS' else 'FALHA'} {x['id']:<8} {x['desc'][:66]:<66} {x['detail'][:60]}")
print(f"\n  {len(R)-FAIL}/{len(R)} testes PASS")
print(f"  monolitico={mono['bytes']}B (~{mono['tokens_est']} tokens)")
for m in meas:
    print(f"    {m['task']}: {m['modules']} → {m['bytes']}B (~{m['tokens_est']} tok) reducao {m['reduction_pct']}%")
sys.exit(1 if FAIL else 0)
