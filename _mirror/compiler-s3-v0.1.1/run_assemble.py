#!/usr/bin/env python3
"""Montagem mecânica + portão + emissão. ZERO chamadas de modelo."""
from __future__ import annotations
import hashlib, json, sys
from collections import Counter
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ctss import assemble, emit, policy, validate                        # noqa: E402
from ctss.schema import PRESERVED, COURSE_CONTENT, DISCARDED_FROM_LEGACY # noqa: E402

import os as _os
DRIVE = Path("/Users/alexandresandra/Library/CloudStorage/GoogleDrive-alexandresandra1973@gmail.com/Meu Drive/Chat GPT")
# Regra: execucao longa le e escreve em ext4. O Drive so na publicacao.
CL = Path(_os.environ.get("CTSS_ROOT", str(DRIVE / "Course-to-Skill-Claude")))
import os
PILOT = os.environ.get("CTSS_PILOT", "PILOT-002-v2")
EVDIR = os.environ.get("CTSS_EVDIR", f"pilots/{PILOT}")
P2 = CL / EVDIR; OUT = CL / f"pilots/{PILOT}/skill"; K = OUT / "knowledge"
ARM = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
       / "FINAL_PRE_RUN_LOCK_F7_SCORER_BOUND/PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip")
MEMBER = ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4/agent-input/runtime-bundle/"
          "knowledge/runtime-policy.yaml")
# v0.1.1 — O RASTRO SAI DO /tmp.
# O compile-trace do PILOT-004 foi PERDIDO na limpeza do /tmp: o produto de 13
# chamadas de modelo, o unico registro da pre-classificacao e das disposicoes,
# vivia num diretorio volatil e fora de qualquer publicacao. Foi a 3a perda pelo
# mesmo motivo (antes: distance-lines e os insumos do P003).
# RULE-HASH-DOES-NOT-RECONSTRUCT vale para o proprio compilador: o rastro e
# insumo do run_assemble, nao subproduto descartavel.
# Diretorio de trabalho PERSISTENTE, parametrizavel, com default sob CTSS_ROOT.
T = Path(_os.environ.get("CTSS_TRACE_DIR", str(CL / "_trace")))
T.mkdir(parents=True, exist_ok=True)
DL = json.loads((T/f"distance-lines-{PILOT}.json").read_text(encoding="utf-8"))["lines"]


def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ts(s): return f"{s//60}:{s%60:02d}"


def main() -> int:
    tr = json.loads((T/f"compile-trace-{PILOT}.json").read_text(encoding="utf-8"))
    ev = [json.loads(l) for l in (P2/"EVIDENCE.jsonl").read_text(encoding="utf-8")
          .splitlines() if l.strip()]
    known = {e["evidence_id"] for e in ev}
    span = {e["evidence_id"]: (e["source_excerpt"]["span"]["start_s"],
                               e["source_excerpt"]["span"]["end_s"]) for e in ev}
    quote = {e["evidence_id"]: e["source_excerpt"]["quote"] for e in ev}
    claim = {e["evidence_id"]: e["claim"] for e in ev}
    cls = {k: v["origin_class"] for k, v in tr["classes"].items()}
    rules, steps, anchors, disp = tr["rules"], tr["steps"], tr["anchors"], tr["dispositions"]

    # ---- validação dura
    errs = []
    for r in rules:
        errs += validate.validate_entity(r, "rule", known)
    for s in steps:
        errs += validate.validate_entity(s, "step", known)
    errs += validate.validate_accounting(known, disp)
    print(f"validação: {len(errs)} erros")
    for e in errs[:10]:
        print("   ", e)

    # ---- montagem mecânica
    rules, mr = assemble.dedup(rules, ("condition", "action"))
    steps, ms = assemble.dedup(steps, ("action",))
    wfs, used = assemble.assign_workflows(steps, anchors, span)
    for r in rules:
        r["order_key"] = assemble.order_key(r, span)
    rules.sort(key=lambda r: r["order_key"])

    # ---- cobertura evidência→regra
    consumed = {e for x in rules + steps for e in x["evidence_ids"]}
    dc = Counter(disp.values())
    only_inf = [x for x in rules + steps if validate.rule_is_course_gap(x, cls)]
    only_inf_rules = [x for x in only_inf if "rule_id" in x]

    # ---- emissão
    OUT.mkdir(parents=True, exist_ok=True); K.mkdir(exist_ok=True)
    canon, _ = policy.load_canonical(ARM, MEMBER)
    pol = policy.derive(canon, skill_id=os.environ.get("CTSS_SKILL_ID","PILOT-002-SKILL"), skill_version="0.1.0",
        scope_condition=os.environ.get("CTSS_SCOPE","Primary request is outside what this course teaches."),
        scope_justification={"kind": "DECISAO_DE_INSTRUMENTO",
            "rationale": ("delimita o que a Skill aceita responder. A fonte não enuncia "
                          "a própria fronteira, então isto é decisão de instrumento e "
                          "NÃO conteúdo do curso."),
            "nao_e_conteudo_da_fonte": True,
            "derivado_dos_topicos_do_temporal_map": True})
    # v0.1.1 — P-8: emitir o questions.yaml que os guards ja exigiam, e declarar
    # a referencia que nao resolve neste pacote.
    known_rule_ids = {r.get("rule_id") for r in rules} | {r.get("decision_id") for r in rules}
    pol = policy.resolve_dangling_refs(pol, known_rule_ids)
    questions = policy.build_questions(
        os.environ.get("CTSS_SKILL_ID", "PILOT-002-SKILL"), "0.1.0",
        os.environ.get("CTSS_PILOT", "PILOT-002"))
    ok_t, got_t = policy.verify_template_byte_identical(pol)
    (K/"runtime-policy.yaml").write_text(yaml.safe_dump(pol, allow_unicode=True,
                                                        sort_keys=False, width=100),
                                         encoding="utf-8")
    (K/"questions.yaml").write_text(yaml.safe_dump(questions, allow_unicode=True,
                                                    sort_keys=False, width=100),
                                    encoding="utf-8")
    (K/"decision-rules.yaml").write_text(yaml.safe_dump(
        {"schema_version":"0.1.0","skill_id":"PILOT-002-SKILL","skill_version":"0.1.0",
         "decision_rules":rules}, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    (K/"workflows.yaml").write_text(yaml.safe_dump(
        {"schema_version":"0.1.0","skill_id":"PILOT-002-SKILL","skill_version":"0.1.0",
         "workflows":wfs,"steps":steps}, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    router = emit.render_router(name=os.environ.get("CTSS_SKILL_NAME","Claude Code — PILOT-002"), skill_id=os.environ.get("CTSS_SKILL_ID","PILOT-002-SKILL"),
                                version="0.1.0", workflows=wfs)
    (OUT/"SKILL.md").write_text(router, encoding="utf-8")
    router_errs = validate.validate_router(router, expected=emit.render_router(
        name=os.environ.get("CTSS_SKILL_NAME","Claude Code — PILOT-002"), skill_id=os.environ.get("CTSS_SKILL_ID","PILOT-002-SKILL"), version="0.1.0",
        workflows=wfs))
    (OUT/"manifest.yaml").write_text(yaml.safe_dump({
        "schema_version":"0.3.0",
        "skill":{"id":os.environ.get("CTSS_SKILL_ID","PILOT-002-SKILL"),"name":os.environ.get("CTSS_SKILL_NAME","Claude Code — PILOT-002"),
                 "version":"0.1.0","status":"CANDIDATE_PENDING_USE"},
        "source":{"type":"single_course_pilot","course_id":os.environ.get("CTSS_PILOT","PILOT-002"),
                  "l0_sha256":os.environ.get("CTSS_L0SHA","")},
        "runtime":{"entrypoint":"SKILL.md",
                   "load_order":["knowledge/runtime-policy.yaml",
                                 "knowledge/questions.yaml",
                                 "knowledge/decision-rules.yaml",
                                 "knowledge/workflows.yaml"],
                   "required_executable_resources":["knowledge/decision-rules.yaml",
                                                    "knowledge/workflows.yaml"],
                   "fail_closed_on_missing_executable_resource":True,
                   "general_knowledge_fallback_for_missing_methodology":False},
        "maturity":{"level":"S3_EXECUTABLE","pilot_scope":True},
        "production_ready":False}, allow_unicode=True, sort_keys=False),
        encoding="utf-8")

    gaps = emit.collect_gaps(rules, steps, disp, ev, cls, validate.rule_is_course_gap)
    und = [g for g in gaps if g["kind"] == "UNDEFINED_FIELD"]
    und_by_field = Counter(g["field"] for g in und)

    # ---- COURSE-GAP-REPORT com cadeias
    L = ["# COURSE-GAP-REPORT — " + os.environ.get("CTSS_PILOT","PILOT-002") + "", "",
         "*Gerado da compilação evidência→Skill. Nenhum número digitado.*", "",
         "## Resumo", "", "| | |", "|---|---|",
         f"| regras | {len(rules)} |", f"| workflows | {len(wfs)} |",
         f"| passos | {len(steps)} |",
         f"| evidências consumidas | {len(consumed)} de {len(known)} "
         f"({100*len(consumed)/len(known):.1f}%) |",
         f"| **regras só de inferência genuína** | **{len(only_inf_rules)}** |",
         f"| campos UNDEFINED | {len(und)} |", "",
         "## Campos UNDEFINED — lacuna pedagógica", "",
         "Os quatro preservados por decisão. Nenhum é metadado: os quatro são "
         "perguntas que a execução faz e o curso não responde.", "",
         "| campo | vezes | a pergunta que o curso não responde |", "|---|---|---|"]
    PERG = {"autonomy":"até onde o agente pode agir sozinho antes de parar",
            "precedence":"qual regra ganha quando duas se aplicam",
            "missing_input_action":"o que fazer quando falta um insumo obrigatório",
            "iteration_limit":"quantas vezes repetir antes de desistir"}
    for f, n in und_by_field.most_common():
        L.append(f"| `{f}` | {n} | {PERG.get(f,'—')} |")
    L += ["", "> **Nenhum metadado nesta lista.** O esquema é subconjunto: os 30 campos "
          "legados que eram metadado foram descartados por decisão registrada, com o "
          "motivo escrito em `ctss/schema.py`. O que sobra aqui é lacuna do curso.", ""]
    if only_inf:
        L += ["---", "", "## Regras e passos que o curso NÃO ensinou", "",
              f"**{len(only_inf)}** entidades se apoiam SÓ em inferência genuína. "
              "Funcionam — mas o modelo as preencheu, não o curso. Para cada uma, a "
              "cadeia:", ""]
        for x in sorted(only_inf, key=lambda z: z.get("order_key", 0)):
            xid = x.get("rule_id") or x.get("step_id")
            L += [f"### `{xid}` — {x['name']}", "",
                  f"**a regra diz:** {x.get('condition', x.get('action'))} → "
                  f"{x['action']}", ""]
            for e in x["evidence_ids"]:
                L += [f"> **o curso disse** ({ts(span[e][0])}): {quote[e].strip()}", "",
                      f"**o modelo concluiu:** {claim[e]}", "",
                      f"**distância:** {DL.get(e,'(não medida)')}", ""]
    L += ["---", "", "## Evidência não consumida", "",
          "| disposição | n | significado |", "|---|---|---|",
          f"| NON_METHODOLOGICAL | {dc.get('NON_METHODOLOGICAL',0)} | contexto, "
          "motivação, mercado — não é método |",
          f"| GAP | {dc.get('GAP',0)} | é método, mas a fonte não dá o suficiente |", ""]
    gp = [g for g in gaps if g["kind"] == "EVIDENCE_UNDERSPECIFIED"]
    if gp:
        L += ["### Método que a fonte menciona sem especificar", "",
              "| onde | o que o curso disse |", "|---|---|"]
        for g in gp[:20]:
            L.append(f"| **{g['timestamp']}** | {claim[g['entity']][:110]} |")
        L.append("")
    (OUT/"COURSE-GAP-REPORT.md").write_text("\n".join(L)+"\n", encoding="utf-8")

    man = {"artifact_id":"PILOT-002-SKILL-COMPILATION-MANIFEST",
           "compiler":"compiler-s3/0.1.0",
           "execution_mode":"PER_SEGMENT","invocations":len(tr["calls"]),
           "monolithic_sweep_used":False,
           "evidence":{"total":len(known),"consumed":len(consumed),
                       "coverage_pct":round(100*len(consumed)/len(known),2),
                       "dispositions":dict(dc)},
           "origin_classes":dict(Counter(cls.values())),
           "course_content_evidence":sum(1 for v in cls.values() if v in COURSE_CONTENT),
           "output":{"rules":len(rules),"steps":len(steps),"workflows":len(wfs)},
           "rules_only_from_genuine_inference":len(only_inf_rules),
           "undefined_fields":dict(und_by_field),
           "deduplication":{"rule":"IDENTICAL_NORMALIZED","rules_merged":len(mr),
                            "steps_merged":len(ms)},
           "validation":{"errors":len(errs),"router_errors":len(router_errs),
                         "failclosed_template_byte_identical":ok_t,
                         "template_sha256":got_t},
           "schema":{"kind":"SUBSET","preserved_by_name":PRESERVED,
                     "discarded_from_legacy":len(DISCARDED_FROM_LEGACY)},
           "files":{f.name: sh(f) for f in sorted(OUT.rglob("*")) if f.is_file()}}
    (OUT/"COMPILATION_MANIFEST.yaml").write_text(
        yaml.safe_dump(man, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print("=" * 78)
    print(f"regras {len(rules)} · passos {len(steps)} · workflows {len(wfs)}")
    print(f"cobertura evidência→regra: {len(consumed)}/{len(known)} "
          f"({100*len(consumed)/len(known):.1f}%)")
    print(f"disposições: {dict(dc)}")
    print(f"REGRAS SÓ DE INFERÊNCIA GENUÍNA: {len(only_inf_rules)} "
          f"(+{len(only_inf)-len(only_inf_rules)} passos)")
    print(f"UNDEFINED: {dict(und_by_field)}")
    print(f"template fail-closed byte a byte: {ok_t}")
    print(f"erros de validação: {len(errs)} · roteador: {len(router_errs)}")
    print(f"saída: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
