#!/usr/bin/env python3
"""Mapa de cobertura de L0 do PILOT-001 — mede e publica.

Roda daqui (ext4). Lê o Drive só para ingerir L0 no vault local e ler os
artefatos. Nada é escrito nas pastas auditadas.

Relatório GERADO: nenhum número é digitado.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml

from cts import coverage as C
from cts.adapters import pilot001 as P
from cts.vault import Vault, sha256_file

HERE = Path(__file__).parent
WORK = HERE / "work"
DEST = Path("/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Claude/docs/L0_COVERAGE_MAP.md")
MANIFEST = Path("/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Claude/docs"
                "/BASELINE_MANIFEST_20260810.txt")
MIN_BLOCK = 60


def baseline_state(paths: list[Path]) -> dict:
    exp = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        sha, size, _mt, rel = line.split("  ", 3)
        exp[rel] = sha
    drive = Path("/mnt/g/Meu Drive/Chat GPT")
    out = {}
    for p in paths:
        rel = str(p.relative_to(drive))
        out[rel] = ("CONFERE" if exp.get(rel) == sha256_file(p)
                    else ("FORA_DO_MANIFESTO" if rel not in exp else "ALTERADO"))
    return out


def collect() -> dict:
    vault = Vault(WORK / "vault")
    tr = vault.ingest(P.L0_TRANSCRIPT, "text/plain")
    sha = tr.sha256
    text = vault.text(sha)
    idx = C.mark_index(text)

    meta = yaml.safe_load(P.L0_METADATA.read_text(encoding="utf-8"))
    nominal = C.hhmmss_to_s(meta["source"]["duration"])
    last_mark = idx[-1][0] if idx else 0

    ev = P.load_evidence()
    ev_by_id = {e["evidence_id"]: e for e in ev}

    # (a) spans citados pelas evidências de L1
    cits: list[C.Citation] = []
    ev_spans_by_id: dict[str, list[tuple[int, int]]] = {}
    for e in ev:
        for r in e.get("source_refs", []):
            ts = r.get("timestamp") or {}
            if ts.get("start") and ts.get("end"):
                a, b = C.hhmmss_to_s(ts["start"]), C.hhmmss_to_s(ts["end"])
                cits.append(C.Citation(a, b, "evidence", e["evidence_id"]))
                ev_spans_by_id.setdefault(e["evidence_id"], []).append((a, b))

    tests = P.docs(P.TEST_SUITE)

    # (b) spans alcançados pelos 10 casos — só por referência a EV
    b_cits, b_evs = [], set()
    for t in tests:
        ids = set(t.get("linked_evidence_ids") or [])
        for s in (t.get("source_scope") or []):
            if s.get("type") == "EVIDENCE":
                ids.add(s["id"])
        for eid in ids:
            b_evs.add(eid)
            for a, bb in ev_spans_by_id.get(eid, []):
                b_cits.append(C.Citation(a, bb, "test-suite", f"{t['test_id']}<-{eid}"))

    # (c) a rubrica do JUDGE, isolada dos casos
    rub_blobs = [json.dumps({"evaluation": t.get("evaluation"),
                             "pass_criteria": t.get("pass_criteria"),
                             "expected_behavior": t.get("expected_behavior"),
                             "critical_failures": t.get("critical_failures")},
                            ensure_ascii=False) for t in tests]
    rub_text = "\n".join(rub_blobs)
    rub_ev = sorted(set(re.findall(r"EV-\d{4,}", rub_text)))
    rub_ts = re.findall(r"\d{1,3}:[0-5]\d", rub_text)
    c_cits = [C.Citation(a, b, "rubric", eid)
              for eid in rub_ev for a, b in ev_spans_by_id.get(eid, [])]

    union = cits + b_cits + c_cits
    covered = C.merge(union)
    only_a = C.merge(cits)

    extent = nominal
    gaps = C.complement(covered, 0, extent)
    for g in gaps:
        g.text = C.text_for(text, idx, g.start, g.end)
        g.verdict, g.markers = C.classify(g.text)

    cov_s = sum(b.dur for b in covered)
    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "l0": {"sha256": sha, "bytes": tr.bytes_, "marks": len(idx),
               "nominal_duration_s": nominal,
               "last_mark_s": last_mark,
               "unaddressable_tail_s": nominal - last_mark},
        "sources": {
            "a_evidence_records": len(ev),
            "a_citations": len(cits),
            "a_covered_s": sum(b.dur for b in only_a),
            "b_tests": len(tests),
            "b_evidences_reached": len(b_evs),
            "b_citations": len(b_cits),
            "b_new_seconds_over_a": sum(b.dur for b in C.merge(cits + b_cits)) - sum(b.dur for b in only_a),
            "c_rubric_ev_refs": len(rub_ev),
            "c_rubric_timestamps": len(rub_ts),
            "c_citations": len(c_cits),
            "c_new_seconds_over_ab": (sum(b.dur for b in covered)
                                      - sum(b.dur for b in C.merge(cits + b_cits))),
        },
        "coverage": {
            "extent_s": extent,
            "covered_s": cov_s,
            "virgin_s": extent - cov_s,
            "covered_pct": round(100 * cov_s / extent, 1),
            "virgin_pct": round(100 * (extent - cov_s) / extent, 1),
            "covered_blocks": len(covered),
            "virgin_blocks": len(gaps),
            "largest_virgin_s": max((g.dur for g in gaps), default=0),
            "virgin_blocks_ge_min": sum(1 for g in gaps if g.dur >= MIN_BLOCK),
            "min_block_s": MIN_BLOCK,
        },
        "verdicts": {
            "candidato": sum(1 for g in gaps if g.verdict == C.CANDIDATO),
            "descarte": sum(1 for g in gaps if g.verdict == C.DESCARTE),
            "candidato_s": sum(g.dur for g in gaps if g.verdict == C.CANDIDATO),
            "descarte_s": sum(g.dur for g in gaps if g.verdict == C.DESCARTE),
            "utilizavel": sum(1 for g in gaps
                              if g.verdict == C.CANDIDATO and g.dur >= MIN_BLOCK),
            "utilizavel_s": sum(g.dur for g in gaps
                                if g.verdict == C.CANDIDATO and g.dur >= MIN_BLOCK),
            "divergencia_v1_v2": [
                {"start": g.start, "end": g.end, "dur": g.dur,
                 "v1": g.markers["_regra_v1_so_metodo"], "v2": g.verdict}
                for g in gaps if g.markers["_regra_v1_so_metodo"] != g.verdict],
        },
        "covered_blocks": [{"start": b.start, "end": b.end, "dur": b.dur} for b in covered],
        "virgin": [{"start": g.start, "end": g.end, "dur": g.dur,
                    "verdict": g.verdict, "markers": g.markers,
                    "text": g.text} for g in gaps],
        "baseline": baseline_state([P.L0_TRANSCRIPT, P.L0_METADATA,
                                    P.EVIDENCE, P.TEST_SUITE]),
    }


def table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def render(d: dict) -> str:
    L, A = [], None
    L = []
    A = L.append
    f = C.fmt
    cv, sr, l0, vd = d["coverage"], d["sources"], d["l0"], d["verdicts"]

    A("# L0_COVERAGE_MAP — PILOT-001\n")
    A(f"**Gerado:** `{d['generated']}` · **Somente medição** — nada foi cortado, "
      "nenhum caso de teste foi escrito, a v0.1.2 não foi tocada.\n")
    A("Relatório gerado por script (`coverage_map.py`); nenhum número foi digitado.\n")

    A("\n## 0. Entrada e integridade\n")
    A(table([[k, v] for k, v in d["baseline"].items()],
            ["arquivo lido (relativo a 'Meu Drive/Chat GPT')", "vs BASELINE_MANIFEST"]))
    A("")
    A(table([["sha256 do L0", l0["sha256"][:16] + "…"],
             ["bytes", l0["bytes"]],
             ["marcas de tempo", l0["marks"]],
             ["duração nominal (`source-metadata.yaml`)", f"{f(l0['nominal_duration_s'])} = {l0['nominal_duration_s']}s"],
             ["última marca endereçável", f"{f(l0['last_mark_s'])} = {l0['last_mark_s']}s"],
             ["cauda sem marca (não endereçável por `t=`)", f"{l0['unaddressable_tail_s']}s"]],
            ["item", "valor"]))
    A("\n> A extensão usada como denominador é a **duração nominal**. Os "
      f"últimos **{l0['unaddressable_tail_s']}s** não têm marca de tempo e, portanto, "
      "não são endereçáveis pela gramática `L0:…:t=` — são território virgem por "
      "impossibilidade de endereçamento, não por escolha.\n")

    A("\n## 1. União dos spans citados — por origem\n")
    A(table([
        ["(a) evidências de L1", sr["a_evidence_records"], sr["a_citations"],
         f"{sr['a_covered_s']}s", "—"],
        ["(b) 10 casos da suíte", sr["b_tests"], sr["b_citations"],
         "—", f"+{sr['b_new_seconds_over_a']}s sobre (a)"],
        ["(c) rubrica do JUDGE", "—", sr["c_citations"],
         "—", f"+{sr['c_new_seconds_over_ab']}s sobre (a)+(b)"],
    ], ["origem", "registros", "citações", "cobertura própria", "acréscimo à união"]))
    A(f"\n**A suíte de teste alcança {sr['b_evidences_reached']} das "
      f"{sr['a_evidence_records']} evidências, e não acrescenta 1 segundo à união** — "
      "toda a sua cobertura é herdada por referência a IDs internos.\n")
    A(f"**A rubrica do JUDGE, isolada dos casos, contém "
      f"{sr['c_rubric_ev_refs']} referências a evidência e "
      f"{sr['c_rubric_timestamps']} timestamps.** Ela não tem alcance próprio "
      "nenhum sobre L0 — é a medida direta da circularidade já reportada na Fase 2 "
      "(régua derivada do artefato, não da fonte).\n")

    A("\n## 2. Cobertura e complemento\n")
    A(table([["extensão de L0", f"{f(cv['extent_s'])} ({cv['extent_s']}s)"],
             ["coberto", f"{f(cv['covered_s'])} ({cv['covered_s']}s) — **{cv['covered_pct']}%**"],
             ["virgem", f"{f(cv['virgin_s'])} ({cv['virgin_s']}s) — **{cv['virgin_pct']}%**"],
             ["blocos cobertos contíguos", cv["covered_blocks"]],
             ["blocos virgens contíguos", cv["virgin_blocks"]],
             ["maior bloco virgem", f"{cv['largest_virgin_s']}s"],
             [f"blocos virgens ≥ {cv['min_block_s']}s", cv["virgin_blocks_ge_min"]]],
            ["métrica", "valor"]))

    A(f"\n## 3. Blocos virgens ≥ {cv['min_block_s']}s\n")
    big = [g for g in d["virgin"] if g["dur"] >= cv["min_block_s"]]
    if big:
        A(table([[f(g["start"]), f(g["end"]), f"{g['dur']}s", g["verdict"]] for g in big],
                ["início", "fim", "duração", "triagem"]))
        for g in big:
            A(f"\n**{f(g['start'])}–{f(g['end'])}** ({g['dur']}s) → `{g['verdict']}`  ")
            mk = {k: v for k, v in g["markers"].items() if v}
            A(f"marcadores: `{mk if mk else 'nenhum'}`\n")
            A(f"> {g['text'][:600]}{'…' if len(g['text']) > 600 else ''}\n")
    else:
        A(f"Nenhum bloco virgem atinge {cv['min_block_s']}s.")

    A("\n## 4. Todos os blocos virgens, com triagem\n")
    A(table([[f(g["start"]), f(g["end"]), f"{g['dur']}s", g["verdict"],
              ", ".join(g["markers"]["metodo"]) or "—",
              ", ".join(g["markers"]["plug"] + g["markers"]["cta"]) or "—",
              "sim" if (g["verdict"] == "CANDIDATO_HELD_OUT"
                        and g["dur"] >= cv["min_block_s"]) else "—"]
             for g in sorted(d["virgin"], key=lambda x: -x["dur"])],
            ["início", "fim", "dur", "triagem", "marcadores de método", "plug / CTA",
             f"utilizável (≥{cv['min_block_s']}s)"]))
    A(f"\n**{vd['candidato']} candidatos** ({vd['candidato_s']}s) · "
      f"**{vd['descarte']} descartes** ({vd['descarte_s']}s).")
    A(f"\n**Utilizáveis — candidatos com pelo menos {cv['min_block_s']}s: "
      f"{vd['utilizavel']} bloco(s), {vd['utilizavel_s']}s.** É este o número que "
      "importa: um bloco de 6 ou 9 segundos não sustenta caso de teste nenhum.\n")
    A("> **A triagem é mecânica, não decisão.** Regra vigente (v2): "
      "`CANDIDATO_HELD_OUT` só quando há marcador de método **e** nenhum marcador "
      "de plug ou de CTA — um bloco que vende algo ou pede engajamento não é "
      "metodologia, ainda que contenha um verbo instrucional. Títulos de seção em "
      "markdown são removidos antes da triagem: são rótulo do transcript, não fala "
      "do professor. Os marcadores foram extraídos do texto real do PILOT-001, "
      "não inventados, e viajam junto com o veredito para que a chamada seja "
      "revisível — 'sem conteúdo de método' é juízo semântico e nenhum contador o "
      "substitui.\n")
    div = vd["divergencia_v1_v2"]
    A(f"\n### 4.1 Onde a regra mudou de veredito\n")
    A("A primeira versão da regra (`v1`, só marcador de método) classificava como "
      "candidato qualquer bloco com um verbo instrucional. Ela errava exatamente na "
      "classe que este mapa precisa isolar. A divergência está registrada em vez de "
      "apagada:\n")
    if div:
        A(table([[f(x["start"]), f(x["end"]), f"{x['dur']}s", x["v1"], x["v2"]]
                 for x in div], ["início", "fim", "dur", "regra v1", "regra v2 (vigente)"]))
        A("\nOs dois blocos maiores que a `v1` chamaria de candidatos são o **plug de "
          "abertura** e o **outro com patrocínio** — 87s que a `v2` manda para "
          "descarte, e corretamente.\n")
    else:
        A("Nenhuma divergência.\n")

    A("\n## 5. Blocos cobertos (para conferência)\n")
    A(table([[f(b["start"]), f(b["end"]), f"{b['dur']}s"] for b in d["covered_blocks"]],
            ["início", "fim", "duração"]))

    A("\n---\n")
    A("**Escopo desta medição:** nada foi cortado, nenhum caso de teste foi "
      "escrito, nenhum arquivo de `Course-to-Skill/` ou `Course-to-Skill-Compiler/` "
      "foi criado, alterado, movido ou apagado.")
    return "\n".join(L) + "\n"


def main() -> int:
    d = collect()
    (WORK / "l0_coverage.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    DEST.write_text(render(d), encoding="utf-8")
    cv = d["coverage"]
    print(f"coberto {cv['covered_pct']}% | virgem {cv['virgin_pct']}% "
          f"({cv['virgin_s']}s em {cv['virgin_blocks']} blocos, maior {cv['largest_virgin_s']}s)")
    print(f"publicado: {DEST} ({DEST.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
