#!/usr/bin/env python3
"""Suíte de canário do compilador v2.

REGRA DE PODER: cada caso roda DUAS vezes.
  - contra a implementação real  → TEM de passar;
  - contra o mutante do caso     → TEM de falhar.
Se o mutante passar, o caso não tem poder de detecção e a suíte inteira
REPROVA, mesmo que a execução real esteja verde. Um teste que não falha quando
a proteção some não é teste.

Nada é compilado aqui. Nenhum piloto é tocado.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import fixtures                                   # noqa: E402
from mutants import MUTANTS                       # noqa: E402

from ctsc2 import pipeline                        # noqa: E402
from ctsc2.thresholds import COVERAGE_FLOOR       # noqa: E402

COMPILER_VERSION = "compiler-v2/0.2.0-frozen"


def _run(extractor, segments, outdir: Path):
    return pipeline.compile_lesson(
        pilot_id="CANARY", lesson_id="CANARY-L01",
        l0_sha256="0" * 64, extent_s=fixtures.EXTENT_S, segments=segments,
        extractor=extractor, out_dir=outdir,
        compiler_version=COMPILER_VERSION)


# ------------------------------------------------------------------ asserções
def check_C1(r) -> tuple[bool, str]:
    claims = {e.claim for e in r.evidences}
    left = fixtures.BOUNDARY_LEFT in claims
    right = fixtures.BOUNDARY_RIGHT in claims
    if left and right:
        segs = {e.claim: e.segment_id for e in r.evidences}
        if segs.get(fixtures.BOUNDARY_LEFT) != "SEG-001":
            return False, "proveniência da vizinha esquerda perdida"
        if segs.get(fixtures.BOUNDARY_RIGHT) != "SEG-002":
            return False, "proveniência da vizinha direita perdida"
        return True, "as duas vizinhas distintas sobreviveram, com proveniência"
    return False, (f"vizinha fundida: esquerda={'ok' if left else 'PERDIDA'}, "
                   f"direita={'ok' if right else 'PERDIDA'}")


def check_C2(r) -> tuple[bool, str]:
    dup = fixtures.TrueDuplicate.DUP
    n = sum(1 for e in r.evidences if e.claim == dup)
    merges = r.manifest["deduplication"]["merges"]
    if n == 1 and merges:
        return True, f"duplicata real fundida ({len(merges)} fusão(ões))"
    return False, f"duplicata sobreviveu {n}× (esperado 1), fusões={len(merges)}"


def check_C3(r) -> tuple[bool, str]:
    y = r.manifest["pass2"]["per_segment_yield"]
    ids = [x["segment_id"] for x in y]
    if len(y) != 3:
        return False, f"rastro tem {len(y)} segmentos, esperado 3"
    mid = next((x for x in y if x["segment_id"] == "SEG-002"), None)
    if mid is None:
        return False, "SEG-002 sumiu do rastro"
    if mid["evidence_count"] != 0 or mid["extraction_status"] != "ZERO_YIELD":
        return False, f"SEG-002 não marcado como zero: {mid}"
    if "SEG-002" not in r.manifest["pass2"]["segments_with_zero_yield"]:
        return False, "zero_yield não listado no manifesto"
    return True, f"segmento de yield zero visível no rastro ({ids})"


def check_C4(r) -> tuple[bool, str]:
    g = r.manifest["coverage_gate"]
    if g["rescan_iterations"] < 1:
        return False, "cobertura abaixo do piso não disparou revarredura"
    it = g["iterations"][0]
    if it["coverage_before"] > COVERAGE_FLOOR:
        return False, "fixture não estava abaixo do piso"
    if it["evidence_added"] < 1:
        return False, "revarredura não acrescentou evidência"
    if not g["result"] == "SATISFIED":
        return False, f"portão não satisfez após revarredura: {g['result']}"
    return True, (f"revarredura disparada: {it['coverage_before']:.2f} → "
                  f"{it['coverage_after']:.2f} em {g['rescan_iterations']} iteração(ões)")


def check_C5(r) -> tuple[bool, str]:
    g = r.manifest["coverage_gate"]
    if g["rescan_iterations"] != 0:
        return False, f"revarreu {g['rescan_iterations']}× acima do piso"
    if g["stop_reason"] != "THRESHOLD_SATISFIED_WITHOUT_RESCAN":
        return False, f"motivo de parada inesperado: {g['stop_reason']}"
    if not g["l0_coverage"] > COVERAGE_FLOOR:
        return False, "fixture não estava acima do piso"
    return True, (f"encerrou sem revarredura com cobertura "
                  f"{g['l0_coverage']:.2f} > {COVERAGE_FLOOR}")


def check_C6(_ignored=None) -> tuple[bool, str]:
    """C6 — a normalização recupera citação LEGÍTIMA e continua rejeitando a
    FABRICADA. As duas metades são obrigatórias: só a primeira seria
    afrouxamento, só a segunda seria não ter consertado nada."""
    from ctsc2.extractors.claude_extractor import ClaudeExtractor
    seg, text = fixtures.SEG_C6, fixtures.C6_TEXT
    marks = ClaudeExtractor._marks(text)
    ex = ClaudeExtractor.__new__(ClaudeExtractor)   # sem cliente: só o validador

    def verdict(quote):
        raw = {"claim": "afirmacao de fixture", "start_mark": "0:12",
               "end_mark": "0:20", "quote": quote, "category": "CONCEPT",
               "epistemic_status": "SOURCE_EXPLICIT"}
        d, info = ClaudeExtractor._validate(ex, raw, seg, text, marks)
        return d is not None, info

    legit_ok, _ = verdict(fixtures.C6_QUOTE_LEGITIMA)
    mark_ok, _ = verdict(fixtures.C6_QUOTE_COM_MARCA)
    fake_ok, fake_info = verdict(fixtures.C6_QUOTE_FABRICADA)
    near_ok, near_info = verdict(fixtures.C6_QUOTE_FABRICADA_PROXIMA)

    if fake_ok:
        return False, ("CITAÇÃO FABRICADA (longe) ACEITA — o conserto virou "
                       "afrouxamento")
    if near_ok:
        return False, ("CITAÇÃO FABRICADA (perto, uma palavra trocada) ACEITA "
                       "— o conserto virou afrouxamento")
    if not legit_ok:
        return False, "citação legítima através de marca continua rejeitada"
    if not mark_ok:
        return False, "citação legítima com marca preservada continua rejeitada"
    return True, ("legítima através de marca: aceita · legítima com marca "
                  "preservada: aceita · fabricada-longe: rejeitada · "
                  "fabricada-perto (1 palavra trocada): rejeitada "
                  f"({near_info.get('reason')})")


CHECKS = {"C1_boundary_distinct": check_C1, "C2_true_duplicate": check_C2,
          "C3_zero_yield_visible": check_C3, "C4_below_threshold_rescans": check_C4,
          "C5_above_threshold_stops": check_C5,
          "C6_quote_normalization": check_C6}

# C6 não passa pelo pipeline: exerce o validador do extractor direto.
NO_PIPELINE = {"C6_quote_normalization"}


def patch(targets, fn):
    """Troca a função em TODAS as ligações informadas e devolve o desfazer."""
    import importlib
    undo = []
    for target in targets:
        mod, attr = target.rsplit(".", 1)
        m = importlib.import_module(mod)
        old = getattr(m, attr)
        setattr(m, attr, fn)
        undo.append((m, attr, old))
    return lambda: [setattr(m, a, o) for m, a, o in undo]


def main() -> int:
    results = []
    with tempfile.TemporaryDirectory(prefix="canary-v2-") as tmp:
        root = Path(tmp)
        cases = list(fixtures.CASES.items()) + [(n, (None, None)) for n in NO_PIPELINE]
        for name, (extractor, segments) in cases:
            check = CHECKS[name]
            pipeline_case = name not in NO_PIPELINE

            # --- 1. implementação real: TEM de passar
            try:
                r = (_run(extractor, segments, root / f"{name}-real")
                     if pipeline_case else None)
                real_ok, real_msg = check(r)
            except Exception as e:
                real_ok, real_msg = False, f"exceção: {type(e).__name__}: {e}"

            # --- 2. mutante: TEM de falhar
            targets, fn, desc = MUTANTS[name]
            undo = patch(targets, fn)
            try:
                rm = (_run(extractor, segments, root / f"{name}-mutant")
                      if pipeline_case else None)
                mut_ok, mut_msg = check(rm)
            except Exception as e:
                mut_ok, mut_msg = False, f"exceção: {type(e).__name__}: {e}"
            finally:
                undo()

            has_power = not mut_ok
            passed = real_ok and has_power
            results.append({
                "case": name, "passed": passed,
                "real_ok": real_ok, "real_detail": real_msg,
                "mutant": desc, "mutant_failed_as_required": has_power,
                "mutant_detail": mut_msg,
            })

    ok = all(r["passed"] for r in results)
    print("=" * 74)
    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        print(f"[{mark}] {r['case']}")
        print(f"       real    : {'ok' if r['real_ok'] else 'FALHOU'} — {r['real_detail']}")
        print(f"       mutante : {r['mutant']}")
        print(f"       poder   : {'falhou como exigido' if r['mutant_failed_as_required'] else 'PASSOU — CANÁRIO SEM PODER'}"
              f" — {r['mutant_detail']}")
    print("=" * 74)
    print(f"{sum(1 for r in results if r['passed'])}/{len(results)} casos com "
          f"execução real verde E mutante vermelho")
    print("SUÍTE:", "APROVADA" if ok else "REPROVADA")

    (HERE / "canary-results.json").write_text(
        json.dumps({"suite_passed": ok, "cases": results}, ensure_ascii=False,
                   indent=2), encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
