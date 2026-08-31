#!/usr/bin/env python3
"""MS-002 — SKILL PACK MODULAR. Deterministico, ZERO chamadas de modelo.
Converte o Operational Package num pacote modular com router e carregamento seletivo.
Proibido produto monolitico. Progressive disclosure em tres niveis."""
import json, hashlib, pathlib, collections, re, unicodedata, shutil, sys
H = pathlib.Path(__file__).resolve().parent
SP = H / "skillpack"
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()

OP = json.loads((H / "operationalization/OPERATIONAL-PACKAGE-MS002.json").read_text(encoding="utf-8"))
BD = json.loads((H / "blocker/BLOCKER-DESIGN-MS002-v1.0.json").read_text(encoding="utf-8"))
CONCEPTS = BD["CHANNEL_A_FROZEN_CONCEPTS"]["conceitos"]

def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s)

# ---- familias de modulo: ordem = prioridade de atribuicao (deterministica)
FAMILIES = [
 ("instagram-content",   {"channels": {"instagram"}, "concepts": set()},
  "Producao e publicacao de conteudo no Instagram (video, imagem, reels, stories)."),
 ("whatsapp-automation", {"channels": {"whatsapp"}, "concepts": set()},
  "Automacao de WhatsApp: instancias, grupos, mensagens, atendimento e Status."),
 ("ads-paid-media",      {"channels": {"google_ads"}, "concepts": {"ads_paid"}},
  "Midia paga: Google Ads, campanhas, orcamento e creditos."),
 ("creative-production", {"channels": set(), "concepts": {"content_creative"}},
  "Producao criativa: geracao de imagem e video, copy, thumbnails, fabrica de criativos."),
 ("lead-followup",       {"channels": set(), "concepts": {"lead_customer", "followup_speed"}},
  "Captacao, velocidade de resposta e follow-up contextual de leads."),
 ("agent-memory",        {"channels": set(), "concepts": {"agent_ai", "database_memory"}},
  "Agentes de IA, memoria, contexto e persistencia."),
 ("observability",       {"channels": set(), "concepts": {"observability"}},
  "Logs, monitoramento, erros e alertas das automacoes."),
 ("dashboards-data",     {"channels": set(), "concepts": {"dashboard_data"}},
  "Dashboards, metricas, planilhas e relatorios."),
 ("human-handoff",       {"channels": set(), "concepts": {"human_handoff"}},
  "Transferencia para humano, takeover e operacao manual."),
 ("maintenance",         {"channels": set(), "concepts": {"maintenance"}},
  "Manutencao de automacoes: atualizacoes, quebras e versoes."),
 ("orchestration-core",  {"channels": set(), "concepts": {"prompt_skill", "automation", "bottleneck"}},
  "Orquestracao: diagnostico de gargalo, prompt, skill, loop e rotina."),
]
# dependencias de MODULO (runtime) — vocabulario proprio, NAO a taxonomia semantica
DEPS = {
 "instagram-content":   [("REQUIRES", "creative-production")],
 "whatsapp-automation": [("OPTIONAL", "agent-memory"), ("OPTIONAL", "human-handoff")],
 "ads-paid-media":      [("OPTIONAL", "dashboards-data")],
 "creative-production": [],
 "lead-followup":       [("OPTIONAL", "whatsapp-automation")],
 "agent-memory":        [],
 "observability":       [],
 "dashboards-data":     [("OPTIONAL", "observability")],
 "human-handoff":       [],
 "maintenance":         [("OPTIONAL", "observability")],
 "orchestration-core":  [],
}
TRIGGERS = {
 "instagram-content":   ["instagram", "reels", "story", "stories", "feed", "carrossel", "carousel", "post"],
 "whatsapp-automation": ["whatsapp", "zap", "grupo", "group", "instancia", "instance", "mensagem", "message",
                         "conversa", "chat", "atendimento", "status"],
 "ads-paid-media":      ["ads", "anuncio", "anuncios", "campanha", "campaign", "google ads", "orcamento", "budget"],
 "creative-production": ["video", "imagem", "image", "criativo", "creative", "copy", "thumbnail", "gerar", "generate"],
 "lead-followup":       ["lead", "leads", "follow", "followup", "cliente", "customer", "resposta", "speed", "velocidade"],
 "agent-memory":        ["agente", "agent", "memoria", "memory", "contexto", "context", "redis", "banco", "database"],
 "observability":       ["log", "logs", "monitor", "erro", "error", "alerta", "alert", "debug", "observabilidade"],
 "dashboards-data":     ["dashboard", "painel", "metrica", "metric", "planilha", "sheet", "relatorio", "report", "analytics"],
 "human-handoff":       ["humano", "human", "takeover", "handoff", "manual", "atendente", "escalar"],
 "maintenance":         ["manutencao", "maintenance", "atualizar", "update", "quebrou", "break", "versao", "version", "corrigir"],
 "orchestration-core":  ["gargalo", "bottleneck", "prompt", "skill", "loop", "rotina", "routine", "automacao",
                         "automation", "orquestrar", "workflow", "fluxo", "estrategia", "strategy"],
}

def concepts_of(u):
    t = " " + norm(canon(u["structure"]) + " " + u.get("scope", "") + " " + " ".join(u.get("adaptations", []))) + " "
    return {k for k, al in CONCEPTS.items() if any(f" {norm(a)} " in t for a in al)}

def assign(u):
    ch = set(u["channels"]); co = concepts_of(u)
    for name, m, _ in FAMILIES:
        if (m["channels"] and ch & m["channels"]) or (m["concepts"] and co & m["concepts"]):
            return name
    return "orchestration-core"

def md_rule(u):
    s = u["structure"]
    L = [f'### {s.get("name","(sem nome)")}', "", f'- **Quando:** {s.get("trigger","—")}',
         f'- **Condicao:** {s.get("condition","—")}', f'- **Acao:** {s.get("action","—")}']
    if s.get("do_not"): L += ["- **Nao fazer:**"] + [f"  - {x}" for x in s["do_not"]]
    if s.get("prerequisites"): L += ["- **Pre-requisitos:**"] + [f"  - {x}" for x in s["prerequisites"]]
    if s.get("exceptions"): L += ["- **Excecoes:**"] + [f"  - {x}" for x in s["exceptions"]]
    L += [f'- **Precedencia:** {s.get("precedence") or "UNDEFINED (governanca, nao derivada)"}']
    return L

def md_workflow(u):
    s = u["structure"]
    L = [f'### {s.get("name","(sem nome)")}', ""]
    if s.get("prerequisites"): L += ["**Pre-requisitos:**"] + [f"- {x}" for x in s["prerequisites"]] + [""]
    for st in sorted(s.get("steps", []), key=lambda x: x["order_key"]):
        L.append(f'{st["order_key"]}. **{st["name"]}** — {st["action"]}')
        if st.get("required_inputs"): L.append(f'   - entradas: {", ".join(st["required_inputs"])}')
        if st.get("missing_input_action"): L.append(f'   - se faltar entrada: {st["missing_input_action"]}')
    if s.get("exceptions"): L += ["", "**Excecoes:**"] + [f"- {x}" for x in s["exceptions"]]
    return L

def md_ap(u):
    s = u["structure"]
    L = ["### " + (s.get("do_not") or ["(anti-padrao)"])[0][:90], "", "**Nao fazer:**"]
    L += [f'- {x}' for x in s.get("do_not", [])]
    L += ["", f'**Por que:** {s.get("why","—")}']
    if s.get("conditions"): L += ["", "**Quando se aplica:**"] + [f"- {x}" for x in s["conditions"]]
    return L

def unit_footer(u):
    p = u["provenance"]
    ev = ", ".join(e["evidence_ref"]["local_id"] for e in p["evidence_chain"][:6])
    cls = "MTX_DERIVED" if u["mtx_derived"] else "SOURCE_GROUNDED"
    return ["", f'> `{u["unit_id"]}` · **{u["applicability"]}** · `{cls}` · fonte `{u["source_id"]}` · evidence `{ev}`",'
            .replace('",', '`') , ""]

def main():
    if SP.exists(): shutil.rmtree(SP)
    (SP / "router").mkdir(parents=True); (SP / "core").mkdir(); (SP / "policies").mkdir()
    (SP / "modules").mkdir(); (SP / "tests").mkdir()
    operable = [u for u in OP["units"] if u["applicability"] in ("DIRECT_USE", "ADAPT_TO_MTX")]
    bymod = collections.defaultdict(list)
    for u in operable: bymod[assign(u)].append(u)
    checkpoints = collections.defaultdict(list)
    umod = {u["unit_id"]: assign(u) for u in operable}
    for c in OP["human_checkpoints"]:
        m = umod.get(c["derived_from"])
        if m: checkpoints[m].append(c)

    modules = {}
    for name, _, desc in FAMILIES:
        us = bymod.get(name, [])
        if not us:            # §20: nao criar modulo vazio
            continue
        mdir = SP / "modules" / name
        (mdir / "workflows").mkdir(parents=True); (mdir / "anti-patterns").mkdir(); (mdir / "references").mkdir()
        rules = [u for u in us if u["entity_kind"] == "rule_candidate"]
        wfs   = [u for u in us if u["entity_kind"] == "workflow_candidate"]
        aps   = [u for u in us if u["entity_kind"] == "anti_pattern_candidate"]
        # NIVEL 2 — contrato compacto do modulo (carregado ao rotear)
        L = [f"# {name}", "", desc, "",
             f"**Unidades:** {len(rules)} regras · {len(wfs)} workflows · {len(aps)} anti-padroes",
             f"**Canais:** {', '.join(sorted({c for u in us for c in u['channels']}) ) or 'none'}", ""]
        if rules:
            L += ["## Regras operacionais", ""]
            for u in rules: L += md_rule(u) + unit_footer(u)
        if wfs: L += ["## Workflows", "", f"Carregue `workflows/` sob demanda ({len(wfs)} arquivos).", ""]
        if aps: L += ["## Anti-padroes", "", f"Carregue `anti-patterns/` sob demanda ({len(aps)} arquivos).", ""]
        if checkpoints[name]:
            L += ["## Checkpoints humanos", ""]
            for c in checkpoints[name]:
                L += [f'- **{c["checkpoint_id"]}** — {c["trigger"]}: {c["why"]}',
                      f'  · `MTX_DERIVED_OPERATIONAL_ARTIFACT` (derivado de `{c["derived_from"]}`)']
            L += [""]
        (mdir / "MODULE.md").write_text("\n".join(L), encoding="utf-8")
        # NIVEL 3 — profundidade sob demanda
        for i, u in enumerate(wfs, 1):
            (mdir / "workflows" / f"WF-{i:02d}.md").write_text(
                "\n".join(md_workflow(u) + unit_footer(u)), encoding="utf-8")
        for i, u in enumerate(aps, 1):
            (mdir / "anti-patterns" / f"AP-{i:02d}.md").write_text(
                "\n".join(md_ap(u) + unit_footer(u)), encoding="utf-8")
        (mdir / "references" / "PROVENANCE.json").write_text(json.dumps(
            {u["unit_id"]: u["provenance"] for u in us}, ensure_ascii=False, indent=1), encoding="utf-8")
        res = {"contract": "MODULE.md",
               "workflows": [f"workflows/WF-{i:02d}.md" for i in range(1, len(wfs)+1)],
               "anti_patterns": [f"anti-patterns/AP-{i:02d}.md" for i in range(1, len(aps)+1)],
               "references": ["references/PROVENANCE.json"]}
        contract = {"module_id": name, "description": desc,
                    "capabilities": sorted({c for u in us for c in u["channels"]} |
                                           {u["entity_kind"] for u in us}),
                    "triggers": TRIGGERS[name],
                    "dependencies": [{"type": t, "module": m} for t, m in DEPS[name]],
                    "resources": res,
                    "unit_ids": [u["unit_id"] for u in us],
                    "n_units": len(us),
                    "mtx_derived_units": [u["unit_id"] for u in us if u["mtx_derived"]],
                    "bytes": {k: (mdir / v).stat().st_size if isinstance(v, str)
                              else sum((mdir / x).stat().st_size for x in v) for k, v in res.items()}}
        (mdir / "MODULE.json").write_text(json.dumps(contract, ensure_ascii=False, indent=1), encoding="utf-8")
        modules[name] = contract

    # ---- dependencias apontando para modulo inexistente sao removidas
    for m in modules.values():
        m["dependencies"] = [d for d in m["dependencies"] if d["module"] in modules]
    # ---- core minimo (sempre carregado)
    core = ["# CORE — contrato minimo do Skill Pack MTX", "",
            "Este e o unico arquivo sempre carregado, alem do indice do router.", "",
            "## Regras invariantes", "",
            "1. Toda afirmacao operacional marcada `SOURCE_GROUNDED` tem trace ate Evidence e Anchor.",
            "2. Toda afirmacao marcada `MTX_DERIVED_OPERATIONAL_ARTIFACT` **nao** e afirmacao de fonte:",
            "   ela vem de combinacao legitima mais politica MTX, e carrega derivacao registrada.",
            "3. Precedencia entre regras e **governanca**, nunca derivada de data, autor, canal ou modelo.",
            "   Onde a fonte nao ordena, a precedencia e `UNDEFINED`.",
            "4. Unidades `NOT_YET_CLASSIFIED` **nao** estao neste pacote e nunca sao promovidas por omissao.",
            "5. Nenhuma decisao operacional reescreve Claim, Candidate ou relation de Fusion.", "",
            "## Prioridade de canal", "",
            "1. **Instagram** — ferramenta principal, especialmente video e imagem",
            "2. **WhatsApp** — conversacao e Status",
            "3. **Google Ads** — midia paga",
            "", "Email, SMS e voz sao secundarios (`REFERENCE_ONLY` por padrao).", "",
            "## Como carregar", "",
            "Consulte `router/ROUTER.json`. Carregue **apenas** os modulos que o router selecionar,",
            "mais as dependencias `REQUIRES`. `OPTIONAL` so entra se a tarefa pedir.",
            "Dentro de um modulo, `MODULE.md` e o contrato; `workflows/`, `anti-patterns/` e",
            "`references/` sao carregados sob demanda.", ""]
    (SP / "core" / "CORE.md").write_text("\n".join(core), encoding="utf-8")
    (SP / "policies" / "MTX-POLICY.md").write_text(
        "# Politica MTX (operacional)\n\n```json\n" +
        json.dumps(json.loads((H / "operationalization/MTX-POLICY-v1.json").read_text(encoding="utf-8")),
                   ensure_ascii=False, indent=1) + "\n```\n", encoding="utf-8")
    router = {"router_version": "v1",
              "selection": "deterministica por casamento de trigger sobre texto normalizado da tarefa",
              "dependency_types": {"REQUIRES": "carregado sempre junto",
                                   "OPTIONAL": "carregado so se a tarefa pedir",
                                   "EXTENDS": "especializa outro modulo (nao usado nesta versao)"},
              "fallback": {"when": "nenhum trigger casa",
                           "load": ["core/CORE.md", "router/ROUTER.json"],
                           "flag": "NO_MODULE_MATCH — responder com o core e pedir precisao, nunca carregar tudo"},
              "ambiguity": {"when": "mais de 3 modulos empatam no topo",
                            "action": "carregar os 3 de maior score e sinalizar AMBIGUOUS_ROUTE"},
              "no_monolithic_default": True,
              "modules": {k: {"triggers": v["triggers"], "capabilities": v["capabilities"],
                              "dependencies": v["dependencies"], "resources": v["resources"],
                              "n_units": v["n_units"], "bytes": v["bytes"]} for k, v in modules.items()}}
    (SP / "router" / "ROUTER.json").write_text(json.dumps(router, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy(H / "router.py", SP / "router" / "router.py")
    files = sorted(p for p in SP.rglob("*") if p.is_file())
    man = {"skillpack_id": "SKILLPACK-MTX-MS002", "version": "v1",
           "built_from": {"operational_package_hash": OP["operational_package_hash"],
                          "fusion_id": OP["fusion_input_identity"]["fusion_id"],
                          "policy_hash": OP["policy_trace"]["policy_hash"]},
           "modules": sorted(modules), "n_modules": len(modules),
           "n_units": sum(m["n_units"] for m in modules.values()),
           "members": [{"path": str(p.relative_to(SP)),
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                        "bytes": p.stat().st_size} for p in files],
           "monolithic_forbidden": True,
           "progressive_disclosure": ["router/ROUTER.json + core/CORE.md",
                                      "modules/<m>/MODULE.json (contrato)",
                                      "modules/<m>/MODULE.md",
                                      "modules/<m>/{workflows,anti-patterns,references}/"]}
    man["skillpack_hash"] = sha(canon(man["members"]))
    (SP / "SKILLPACK-MANIFEST.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  modulos criados: {len(modules)} → {', '.join(sorted(modules))}")
    for k, v in sorted(modules.items()):
        print(f"    {k:<22} unidades={v['n_units']:<3} bytes contrato={v['bytes']['contract']:<6} "
              f"wf={v['bytes']['workflows']:<6} ap={v['bytes']['anti_patterns']}")
    print(f"  total de arquivos: {len(files)} · skillpack_hash={man['skillpack_hash'][:16]}…")

if __name__ == "__main__":
    sys.exit(main())
