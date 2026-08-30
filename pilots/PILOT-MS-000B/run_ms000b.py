#!/usr/bin/env python3
"""PILOT-MS-000B — runner da execucao avaliatoria.

Model/policy: claude-opus-5, thinking disabled — o MESMO ja autorizado no pipeline
(claude_extractor.py, p002_blind_run.py, p002_judge.py, p003_apply_step4.py).
HARD CAP: 24 chamadas. O runner ABORTA antes de ultrapassar.

COMPILE-TRACE (I19) e gravado APOS CADA CHAMADA, em caminho versionado, nunca /tmp.
"""
from __future__ import annotations
import json, os, pathlib, sys, datetime, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "lib"))
import ms000b as M
import anthropic

P    = pathlib.Path(__file__).parent
OUT  = P / "out"; OUT.mkdir(exist_ok=True)
TRACE = OUT / "COMPILE-TRACE.jsonl"

MODEL      = "claude-opus-5"
THINKING   = {"type": "disabled"}
MAX_TOKENS = 8000
HARD_CAP   = 24
PROMPT_VERSION = "ms000b-claimgen-v1"
JUDGE_VERSION  = "ms000b-entail-v1"

CLAIMGEN_SYS = (
 "Voce gera CLAIMS a partir de EVIDENCIAS de uma aula. Uma claim e uma asserçao "
 "normalizada, curta, autocontida, que segue INTEIRAMENTE das evidencias citadas, "
 "SEM acrescentar fato, causalidade, condicao ou generalizacao nova. "
 "Cada claim referencia >=1 local_id de evidencia deste pacote. "
 "NAO invente identificadores. NAO use conhecimento externo. "
 "Responda SOMENTE com JSON: {\"claims\":[{\"text\":\"...\",\"evidence_refs\":[\"EV-0001\"]}]}")

JUDGE_SYS = (
 "Voce julga ENTAILMENT. Para cada item, decida se TODA afirmacao da claim segue do "
 "conjunto de evidencias dado, SEM introduzir fato, causalidade, condicao ou "
 "generalizacao nova. Semelhanca lexical NAO e entailment. "
 "Estados: ENTAILED | NOT_ENTAILED | INDETERMINATE. "
 "Responda SOMENTE com JSON: {\"verdicts\":[{\"claim_id\":\"...\",\"state\":\"...\",\"why\":\"...\"}]}")

_calls = {"n": 0}
def call(client, run, source, system, user, purpose, input_obj):
    if _calls["n"] >= HARD_CAP:
        raise SystemExit(f"HARD CAP {HARD_CAP} atingido — abortando antes de estourar")
    ih = M.sha_text(M.canon(input_obj))
    t0 = datetime.datetime.now().astimezone().isoformat()
    r = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, thinking=THINKING,
                               system=system, messages=[{"role": "user", "content": user}])
    _calls["n"] += 1
    txt = "".join(b.text for b in r.content if b.type == "text")
    rec = {"call_seq": _calls["n"], "run": run, "source": source, "purpose": purpose,
           "input_sha256": ih, "partition": input_obj.get("_partition"),
           "prompt_version": input_obj.get("_prompt_version"),
           "model_requested": MODEL, "model_resolved": r.model,
           "thinking": THINKING, "max_tokens": MAX_TOKENS,
           "output_sha256": M.sha_text(txt), "stop_reason": r.stop_reason,
           "tokens": {"input": r.usage.input_tokens, "output": r.usage.output_tokens},
           "timestamp_operacional": t0,
           "nota_timestamp": "registro operacional apenas; NUNCA identidade"}
    with TRACE.open("a", encoding="utf-8") as fh:      # grava ANTES de qualquer descarte
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return txt, rec

def jparse(t):
    t = t.strip()
    if t.startswith("```"): t = t.split("```")[1].lstrip("json").strip()
    i, j = t.find("{"), t.rfind("}")
    return json.loads(t[i:j+1])

def main():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raw = (pathlib.Path.home() / ".anthropic_key").read_text(encoding="utf-8")
        key = (raw.split("=", 1)[1] if "=" in raw else raw).strip().strip('"\'')
    client = anthropic.Anthropic(api_key=key)
    started = datetime.datetime.now().astimezone().isoformat()
    if TRACE.exists(): TRACE.unlink()

    cut = M.CUT.read_text(encoding="utf-8")
    assert M.sha(M.CUT) == M.CUT_SHA and M.sha(M.FULL) == M.FULL_SHA
    policy = {"model": MODEL, "thinking": THINKING, "max_tokens": MAX_TOKENS,
              "prompt_version": PROMPT_VERSION, "judge_version": JUDGE_VERSION}
    pkgs, bodies, cands = {}, {}, {}
    for k in ("A", "B"):
        pkgs[k], bodies[k] = M.build_package(k, cut, policy)
        cands[k] = M.source_local_candidates(k)
    (OUT / "source-packages.json").write_text(json.dumps(pkgs, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "source-local-candidates.json").write_text(json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8")
    for k in ("A", "B"):
        (OUT / f"chapter-slice-{k}.txt").write_text(bodies[k], encoding="utf-8")

    # controles positivos SINTETICOS de blocagem, declarados no Opening Record
    CONTROLS = [
      {"control_id": "BLK-CTRL-01",
       "a_text": "The repository must be initialized before pushing commits to github.",
       "b_text": "Authenticate the github repository before deploying through the cli."},
      {"control_id": "BLK-CTRL-02",
       "a_text": "Commit changes locally before syncing the remote repository.",
       "b_text": "The remote repository connection is configured before the deploy step."},
    ]

    runs = {}
    for run in ("RUN-1", "RUN-2", "RUN-3"):
        raw, sealed, rejected = {}, {}, {}
        for k in ("A", "B"):
            ev = [{"local_id": i["local_id"], "quote": i["quote"],
                   "epistemic_status": i["epistemic_status"]} for i in pkgs[k]["items"]]
            payload = {"_partition": f"1 chamada por (source,run); todas as {len(ev)} evidencias do pacote {k}",
                       "_prompt_version": PROMPT_VERSION,
                       "source_package_hash": pkgs[k]["source_package_hash"], "evidence": ev}
            user = (f"Pacote {k} — capitulo {pkgs[k]['profile']['chapter_n']}: "
                    f"{pkgs[k]['profile']['chapter_titulo']}\n\nEVIDENCIAS:\n" +
                    json.dumps(ev, ensure_ascii=False, indent=1))
            txt, _ = call(client, run, k, CLAIMGEN_SYS, user, "CLAIM_GENERATION", payload)
            got = jparse(txt).get("claims", [])
            valid_ids = {i["local_id"] for i in pkgs[k]["items"]}
            rl, rj = [], []
            for n, c in enumerate(got, 1):
                cid = f"{run}-{k}-CL-{n:04d}"
                refs = [r for r in (c.get("evidence_refs") or []) if r in valid_ids]
                rec = {"claim_id": cid, "package": k, "text": (c.get("text") or "").strip(),
                       "evidence_refs": refs,
                       "qualified_refs": [[pkgs[k]["source_package_hash"], r] for r in refs]}
                rl.append(rec)
                if not rec["text"]:
                    rj.append({**rec, "reject_reason": "TEXTO_VAZIO"})
                elif not refs:
                    rj.append({**rec, "reject_reason": "EVIDENCE_REFS_VAZIO_OU_INEXISTENTE"})
            raw[k] = rl; rejected[k] = rj
        # --- ENTAILED_BY: julga TODAS as claims candidatas do run, sem amostra
        cand = [c for k in ("A", "B") for c in raw[k]
                if c["claim_id"] not in {r["claim_id"] for r in rejected[k]}]
        by_id = {c["claim_id"]: c for c in cand}
        items = []
        for c in cand:
            qs = [i["quote"] for i in pkgs[c["package"]]["items"] if i["local_id"] in c["evidence_refs"]]
            items.append({"claim_id": c["claim_id"], "claim": c["text"], "evidence": qs})
        payload = {"_partition": f"1 chamada por run; TODAS as {len(items)} claims candidatas",
                   "_prompt_version": JUDGE_VERSION, "items": items}
        txt, _ = call(client, run, "A+B", JUDGE_SYS, json.dumps(items, ensure_ascii=False),
                      "ENTAILED_BY_JUDGMENT", payload)
        verd = {v["claim_id"]: v for v in jparse(txt).get("verdicts", [])}
        for k in ("A", "B"):
            s = []
            for c in raw[k]:
                if c["claim_id"] not in by_id: continue
                v = verd.get(c["claim_id"], {"state": "INDETERMINATE", "why": "sem veredito"})
                c["entailed_by"] = v["state"]; c["entail_why"] = v.get("why", "")
                if v["state"] == "ENTAILED": s.append(c)
                else: rejected[k].append({**c, "reject_reason": f"ENTAILED_BY={v['state']}"})
            sealed[k] = s
        blk = M.blocker(sealed["A"], sealed["B"], CONTROLS)
        rel = M.relations_mechanical(sealed["A"], sealed["B"], blk["pairs"])
        iso = M.isolation_check(pkgs["A"], pkgs["B"], sealed["A"], sealed["B"])
        fus = M.fusion_package(pkgs["A"], pkgs["B"], sealed["A"], sealed["B"],
                               cands["A"], cands["B"], rel, blk)
        # workflow preservation: estrutura source-local vs transportada
        wp = {k: {"struct_source": M.struct_hash(cands[k]),
                  "struct_fusion": M.struct_hash(fus["transported_candidates"][k]),
                  "preservado": M.struct_hash(cands[k]) == M.struct_hash(fus["transported_candidates"][k]),
                  "workflows": len(cands[k]["workflow_candidates"]),
                  "steps": sum(len(w["steps"]) for w in cands[k]["workflow_candidates"])}
              for k in ("A", "B")}
        runs[run] = {"raw": raw, "rejected": rejected, "sealed": sealed, "blocking": blk,
                     "relations": rel, "isolation": iso, "workflow_preservation": wp,
                     "fusion_id": fus["fusion_id"], "controls": CONTROLS}
        (OUT / f"fusion-package-{run}.json").write_text(json.dumps(fus, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  {run}: raw A={len(raw['A'])} B={len(raw['B'])} | sealed A={len(sealed['A'])} B={len(sealed['B'])} "
              f"| pares {blk['survived']}/{blk['possible']} | chamadas={_calls['n']}")
    (OUT / "runs.json").write_text(json.dumps(runs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  TOTAL de chamadas: {_calls['n']} de {HARD_CAP}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
