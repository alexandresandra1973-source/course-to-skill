#!/usr/bin/env python3
"""MS-002 — OPERATIONAL PACKAGE. Deterministico, ZERO chamadas de modelo.
Contem SOMENTE o que a MTX decidiu operar. NAO substitui o Fusion Package.
Toda unidade mantem trace ate Claim/Evidence/Anchor. Conteudo nao literal e
marcado MTX_DERIVED_OPERATIONAL_ARTIFACT."""
import json, hashlib, pathlib, collections, sys
H = pathlib.Path(__file__).resolve().parent
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
shaf = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

DEC = json.loads((H / "out-oper/APPLICABILITY-DECISIONS.json").read_text(encoding="utf-8"))
FUS = json.loads((H / "out-fusion/FUSION-PACKAGE-MS002.json").read_text(encoding="utf-8"))
POL = json.loads((H / "operationalization/MTX-POLICY-v1.json").read_text(encoding="utf-8"))

# ---- catalogo source-local completo, para provenance
CAND, CLAIMS, EVID, ANCH = {}, {}, {}, {}
for s in "ABC":
    pkg = H / "packages" / f"pkg-{s}"
    sid = f"MS002-SRC-{s}"
    for bucket, lst in json.loads((pkg / "SOURCE-LOCAL-CANDIDATES.json").read_text(encoding="utf-8")).items():
        for c in lst: CAND[f'{sid}|{c["local_id"]}'] = c
    for l in (pkg / "CLAIMS.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(l); CLAIMS[(sid, c["local_id"])] = c
    for l in (pkg / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines():
        e = json.loads(l); EVID[(sid, e["local_id"])] = e
    for l in (pkg / "SOURCE-ANCHORS.jsonl").read_text(encoding="utf-8").splitlines():
        a = json.loads(l); ANCH[(sid, a["local_id"])] = a

OPERABLE = {"DIRECT_USE", "ADAPT_TO_MTX"}

def trace(uid):
    """Operational artifact -> Candidate -> Claim -> Evidence -> Anchor -> raw source."""
    sid = uid.split("|")[0]; c = CAND[uid]
    evs = []
    for e in c["evidence_refs"]:
        ev = EVID[(sid, e)]
        an = ANCH[(sid, ev["source_anchor_refs"][0]["local_id"])]
        evs.append({"evidence_ref": {"source_id": sid, "local_id": e},
                    "anchor_ref": {"source_id": sid, "local_id": an["local_id"],
                                   "start_s": an["start_s"], "end_s": an["end_s"]},
                    "raw_source": {"video_id": an["video_id"], "artifact_hash": an["artifact_hash"],
                                   "transcript_segment_ids": an["transcript_segment_ids"]}})
    return {"candidate_ref": DEC["unit_index"][uid]["typed_ref"],
            "claim_refs": [{"source_id": sid, "local_id": cl} for cl in c["sealed_claim_refs"]],
            "evidence_chain": evs}

def main():
    units = []
    for uid, d in DEC["decisions"].items():
        c = CAND[uid]
        units.append({"unit_id": uid, "entity_kind": c["entity_kind"], "source_id": c["source_id"],
                      "applicability": d["applicability"], "channels": d["channels"],
                      "rationale": d["rationale"], "scope": d["scope"],
                      "adaptations": d["adaptations"], "limitations": d["limitations"],
                      "mtx_derived": d["mtx_derived"], "derivation": d.get("derivation"),
                      "structure": c["structure"], "defects": c["defects"],
                      "provenance": trace(uid),
                      "assertion_class": ("MTX_DERIVED_OPERATIONAL_ARTIFACT" if d["mtx_derived"]
                                          else "SOURCE_GROUNDED_OPERATIONAL_ARTIFACT")})
    operable = [u for u in units if u["applicability"] in OPERABLE]
    workflows = [u for u in operable if u["entity_kind"] == "workflow_candidate"]
    rules     = [u for u in operable if u["entity_kind"] == "rule_candidate"]
    antipat   = [u for u in operable if u["entity_kind"] == "anti_pattern_candidate"]

    # --- checkpoints humanos: derivados de anti-padroes e de defeitos declarados
    checkpoints = []
    for u in antipat:
        checkpoints.append({"checkpoint_id": f"HC-{len(checkpoints)+1:03d}",
                            "trigger": "antes de executar automacao no escopo deste anti-padrao",
                            "why": u["structure"].get("why", ""),
                            "do_not": u["structure"].get("do_not", []),
                            "derived_from": u["unit_id"],
                            "assertion_class": "MTX_DERIVED_OPERATIONAL_ARTIFACT",
                            "derivation": "checkpoint humano derivado mecanicamente de um anti-padrao source-local; "
                                          "a fonte descreve o anti-padrao, nao o checkpoint"})
    for u in operable:
        if "SCOPE_UNSTATED" in u["defects"] or "PRECEDENCE_UNDEFINED" in u["defects"]:
            checkpoints.append({"checkpoint_id": f"HC-{len(checkpoints)+1:03d}",
                                "trigger": f"antes de aplicar {u['unit_id']}",
                                "why": f"a unidade carrega o defeito {u['defects']}: escopo ou precedencia nao declarados na fonte",
                                "do_not": ["nao presumir escopo nem precedencia que a fonte nao declara"],
                                "derived_from": u["unit_id"],
                                "assertion_class": "MTX_DERIVED_OPERATIONAL_ARTIFACT",
                                "derivation": "checkpoint derivado mecanicamente de defeito declarado na extracao"})
    # --- metricas/observabilidade e manutencao: so o que as unidades operaveis sustentam
    OBS = ("observability", "dashboard_data", "maintenance")
    def tagged(u, words):
        blob = canon(u["structure"]).lower()
        return any(w in blob for w in words)
    metrics = [{"unit_id": u["unit_id"], "channels": u["channels"], "name": u["structure"].get("name"),
                "assertion_class": u["assertion_class"]}
               for u in operable if tagged(u, ("metric", "metrica", "dashboard", "painel", "analytics",
                                               "relatorio", "report", "kpi", "sheet", "planilha"))]
    observability = [{"unit_id": u["unit_id"], "name": u["structure"].get("name"),
                      "assertion_class": u["assertion_class"]}
                     for u in operable if tagged(u, ("log", "monitor", "alert", "alerta", "error", "erro", "debug"))]
    maintenance = [{"unit_id": u["unit_id"], "name": u["structure"].get("name"),
                    "assertion_class": u["assertion_class"]}
                   for u in operable if tagged(u, ("maintenance", "manutencao", "update", "atualiz",
                                                   "version", "versao", "break", "quebra", "fix", "corrig"))]
    dist = collections.Counter(u["applicability"] for u in units)
    chan = collections.Counter(c for u in operable for c in u["channels"])
    pkg = {
      "operational_package_id": "OPERATIONAL-PACKAGE-MS002",
      "version": "v1",
      "fusion_input_identity": {
        "fusion_id": FUS["fusion_id"],
        "source_package_hash_A": FUS["source_package_hash_A"],
        "source_package_hash_B": FUS["source_package_hash_B"],
        "source_package_hash_C": FUS["source_package_hash_C"],
        "pairset_hash": FUS["pairset_hash"],
        "blocker_variant": FUS["blocker"]["selected_variant"]},
      "policy_trace": {"policy_id": POL["policy_id"],
                       "policy_hash": shaf(H / "operationalization/MTX-POLICY-v1.json"),
                       "channel_priority": [c["channel"] for c in POL["channel_priority"]],
                       "secondary_default": POL["secondary_channels"]["default_treatment"],
                       "fail_closed": POL["fail_closed"]},
      "applicability_distribution": dict(dist),
      "channel_distribution_operable": dict(chan),
      "units": units,
      "operational_rules": [u["unit_id"] for u in rules],
      "operational_workflows": [u["unit_id"] for u in workflows],
      "anti_patterns": [u["unit_id"] for u in antipat],
      "human_checkpoints": checkpoints,
      "metrics": metrics, "observability": observability, "maintenance": maintenance,
      "mtx_derived_artifacts": [u["unit_id"] for u in units if u["mtx_derived"]] +
                               [c["checkpoint_id"] for c in checkpoints],
      "unresolved_operational_questions": [
        f'{dist.get("NOT_YET_CLASSIFIED",0)} unidades permanecem NOT_YET_CLASSIFIED (fail-closed): nenhuma foi promovida.',
        "Nenhuma precedencia entre unidades foi derivada; precedencia permanece governanca.",
        "As relations de Fusion nao foram usadas para reescrever nenhuma unidade source-local.",
        "Unidades NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION permanecem source-local e fora deste pacote."],
      "separation_guarantees": {
        "does_not_replace_fusion_package": True,
        "no_writeback_to_source_packages": True,
        "no_writeback_to_fusion": True,
        "mtx_policy_absent_from_fusion_identity": FUS.get("mtx_policy_hash") is None}
    }
    pkg["operational_package_hash"] = sha(canon({k: v for k, v in pkg.items()
                                                 if k != "operational_package_hash"}))
    out = H / "operationalization"; out.mkdir(exist_ok=True)
    (out / "OPERATIONAL-PACKAGE-MS002.json").write_text(canon(pkg) + "\n", encoding="utf-8")
    print(f"  unidades: {len(units)} · operaveis: {len(operable)} "
          f"(rules {len(rules)}, workflows {len(workflows)}, anti-patterns {len(antipat)})")
    print(f"  aplicabilidade: {dict(dist)}")
    print(f"  canais (operaveis): {dict(chan)}")
    print(f"  checkpoints humanos: {len(checkpoints)} · metricas: {len(metrics)} · "
          f"observabilidade: {len(observability)} · manutencao: {len(maintenance)}")
    print(f"  MTX_DERIVED: {len(pkg['mtx_derived_artifacts'])}")
    print(f"  operational_package_hash = {pkg['operational_package_hash']}")

if __name__ == "__main__":
    sys.exit(main())
