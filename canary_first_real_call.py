#!/usr/bin/env python3
"""Canário da PRIMEIRA chamada real — UM segmento, e para.

Roda daqui (ext4). READ-ONLY sobre `Course-to-Skill/`. Não publica nada:
imprime o relatório e grava o rastro cru no scratchpad.

NÃO roda o pipeline. Chama o extractor DIRETO, uma vez, num único segmento.
Não há caminho aqui que toque os outros 8.

A pergunta que este canário existe para responder não é "a máquina funciona"
(isso o ensaio com cliente falso já respondeu) e sim: **as claims saem íntegras
ou dependem de contexto que ficou fora do segmento?** Com chamada por segmento o
modelo vê ~100s e só metadado dos vizinhos; na rodada original ele via a aula
inteira. Se as claims saírem soltas, é achado de desenho, não de execução.

Uso:
    .venv/bin/python canary_first_real_call.py [SEG-005]
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
V2 = DRIVE / "Course-to-Skill-Claude/compiler-v2"
sys.path.insert(0, str(V2))

P1 = DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
TMAP = P1 / "analysis/temporal-map.yaml"
L0 = P1 / "sources/transcript/transcript-original-en.txt"
TRACE = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude") / "canary-trace.json"

from ctsc2.extractors.claude_extractor import ClaudeExtractor   # noqa: E402
from ctsc2.model import Segment                                 # noqa: E402

MARK_RE = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")

# Marcadores MECÂNICOS de dependência de contexto externo. Não decidem nada:
# apontam onde olhar. "Claim solta" é juízo semântico e nenhum regex o substitui.
DEIXIS = re.compile(
    r"^\s*(it|this|that|these|those|they|he|she|there|such|the (former|latter))\b"
    r"|(\bas (mentioned|discussed|described|shown)\b)"
    r"|(\b(above|below|earlier|previously|aforementioned)\b)"
    r"|(\bthe (tool|platform|framework|agent|step|process|approach)\b(?!\s+\w))",
    re.I)
BARE_REF = re.compile(r"\b(this|that|these|those)\s+(one|thing|step|part|way)\b", re.I)


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hhmmss(t: str) -> int:
    p = [int(x) for x in t.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def slicer(text: str):
    blocks = text.split("\n\n")
    idx = [(i, int(m.group(1)) * 60 + int(m.group(2)))
           for i, b in enumerate(blocks)
           if (m := MARK_RE.fullmatch(b.strip()))]

    def text_for(seg: Segment) -> str:
        out = []
        for k, (i, s) in enumerate(idx):
            if seg.start_s <= s < seg.end_s:
                end = idx[k + 1][0] if k + 1 < len(idx) else len(blocks)
                out.extend(blocks[i:end])
        return "\n\n".join(out).strip()
    return text_for


def fmt(s: int) -> str:
    return f"{s // 60}:{s % 60:02d}"


def standalone_flags(claim: str) -> list[str]:
    f = []
    if DEIXIS.search(claim):
        f.append("DEIXIS_OU_REFERENCIA_EXTERNA")
    if BARE_REF.search(claim):
        f.append("REFERENCIA_VAGA")
    if len(claim.split()) < 6:
        f.append("CURTA_DEMAIS_PARA_SER_AUTOCONTIDA")
    if not re.search(r"[A-Z][a-z]|\b(agent|prompt|tool|platform|output|input|"
                     r"workflow|instruction|boundar|outcome|test|model)\w*", claim, re.I):
        f.append("SEM_ANCORA_NOMINAL")
    return f


def main() -> int:
    seg_id = sys.argv[1] if len(sys.argv) > 1 else "SEG-005"

    if not (os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("ANTHROPIC_AUTH_TOKEN")
            or (Path.home() / ".config/anthropic").is_dir()):
        print("SEM CREDENCIAL — nada foi chamado.")
        print("O código lê a chave via `anthropic.Anthropic()` sem argumentos,")
        print("que resolve, nesta ordem:")
        print("  1. variável de ambiente ANTHROPIC_API_KEY   <- o caminho esperado")
        print("  2. variável de ambiente ANTHROPIC_AUTH_TOKEN")
        print("  3. perfil de `ant auth login` em ~/.config/anthropic/")
        print("Nenhuma chave é lida de arquivo do repositório e nenhuma é escrita.")
        return 2

    tm = yaml.safe_load(TMAP.read_text(encoding="utf-8"))
    segs = [Segment(s["segment_id"], hhmmss(s["start"]), hhmmss(s["end"]),
                    s.get("topic", ""), s.get("function", ""))
            for s in tm["temporal_map"]]
    seg = next((s for s in segs if s.segment_id == seg_id), None)
    if seg is None:
        print(f"segmento {seg_id} não existe. Disponíveis: "
              + ", ".join(s.segment_id for s in segs))
        return 2

    text = L0.read_text(encoding="utf-8")
    text_for = slicer(text)
    seg_text = text_for(seg)
    marks = [f"{m.group(1)}:{m.group(2)}" for m in MARK_RE.finditer(seg_text)]

    print("=" * 78)
    print(f"CANÁRIO DA PRIMEIRA CHAMADA REAL — {seg.segment_id}, e PARA")
    print("=" * 78)
    print(f"L0            : sha256 {sha_p(L0)[:16]}…")
    print(f"temporal-map  : sha256 {sha_p(TMAP)[:16]}…")
    print(f"segmento      : {seg.segment_id} · {fmt(seg.start_s)}–{fmt(seg.end_s)} "
          f"({seg.duration}s)")
    print(f"tópico        : {seg.topic}")
    print(f"texto enviado : {len(seg_text)} chars · {len(marks)} marcas "
          f"({marks[0]} … {marks[-1]})")
    print(f"\nOs outros {len(segs)-1} segmentos NÃO serão chamados.\n")

    # contexto local idêntico ao que o pipeline monta
    i = [s.segment_id for s in segs].index(seg.segment_id)
    ctx = {"segment_id": seg.segment_id,
           "position": {"index": i, "of": len(segs)},
           "bounds_s": [seg.start_s, seg.end_s],
           "previous_segment_id": segs[i-1].segment_id if i > 0 else None,
           "next_segment_id": segs[i+1].segment_id if i+1 < len(segs) else None,
           "scope_rule": "Extraia SOMENTE do intervalo deste segmento."}

    ex = ClaudeExtractor(text_for)
    try:
        drafts = ex.extract(seg, ctx, 0)
    except Exception as e:
        print(f"CHAMADA FALHOU: {type(e).__name__}: {e}")
        if ex.calls:
            print(json.dumps(ex.calls[0].to_dict(), ensure_ascii=False, indent=2))
        return 1

    rec = ex.calls[0]
    print("--- chamada ---")
    print(f"model={rec.model} effort={rec.effort} stop_reason={rec.stop_reason}")
    print(f"request_id={rec.request_id} latência={rec.latency_s}s")
    print(f"tokens: entrada={rec.input_tokens} saída={rec.output_tokens} "
          f"cache_read={rec.cache_read_input_tokens} "
          f"cache_write={rec.cache_creation_input_tokens}")
    print(f"devolvidas={rec.drafts_returned} aceitas={rec.drafts_accepted} "
          f"rejeitadas={len(rec.rejected)}")
    print(f"  passariam pela regra ESTRITA (antes)  : {rec.strict_pass}")
    print(f"  recuperadas SÓ pela normalização      : {len(rec.normalized_only)}")
    for r in rec.normalized_only:
        print(f"     +{r['marcas_na_quote']} marca(s) na quote · {r['claim'][:80]}")

    if rec.warnings:
        print(f"\n--- avisos: claim diverge do literal e se diz SOURCE_EXPLICIT ---")
        for w in rec.warnings:
            print(f"  ausentes da quote: {w['entidades_ausentes_da_quote']}")
            print(f"    claim: {w['claim']}")
            print(f"    quote: {w['quote']}")
    else:
        print("\n--- avisos de divergência claim×literal: nenhum ---")

    if rec.rejected:
        print("\n--- rejeições ---")
        for n, r in enumerate(rec.rejected, 1):
            print(f"\n  ({n}) [{r['reason']}] {r.get('claim','')}")
            if "quote_devolvida" in r:
                print(f"      quote devolvida  : {r['quote_devolvida']!r}")
                print(f"      quote normalizada: {r['quote_normalizada']!r}")
                print(f"      janela da fonte  : {r['janela_da_fonte']!r}")
                print(f"      maior trecho comum: {r['maior_trecho_comum_chars']} chars "
                      f"({r['cobertura_do_maior_trecho']:.0%} da quote)")
                print(f"      marcas na quote  : {r['marcas_na_quote_devolvida']}")
                for op in r.get("operacoes", []):
                    print(f"        {op['op']:<7} fonte={op['fonte']!r}")
                    print(f"        {'':<7} quote={op['quote']!r}")
            else:
                for k, v in r.items():
                    if k not in ("reason", "claim"):
                        print(f"      {k}={v}")
    else:
        print("\n--- rejeições: nenhuma ---")

    print(f"\n--- as {len(drafts)} evidências, INTEIRAS ---")
    for n, d in enumerate(drafts, 1):
        flags = standalone_flags(d.claim)
        print(f"\n[{n}] {fmt(d.start_s)}–{fmt(d.end_s)} · {d.category} · "
              f"{d.epistemic_status}")
        print(f"    claim: {d.claim}")
        print(f"    quote: {d.quote[:400]}{'…' if len(d.quote) > 400 else ''}")
        print(f"    autocontida (triagem mecânica): "
              f"{'OK' if not flags else ', '.join(flags)}")

    flagged = [d for d in drafts if standalone_flags(d.claim)]
    print(f"\n--- integridade das claims ---")
    print(f"{len(drafts) - len(flagged)}/{len(drafts)} sem marcador de dependência "
          f"de contexto externo.")
    print("> A triagem é MECÂNICA e não decide: aponta dêixis sem antecedente, "
          "referência vaga e ausência de âncora nominal. 'Claim solta' é juízo "
          "semântico — leia as claims acima.")

    TRACE.parent.mkdir(parents=True, exist_ok=True)
    TRACE.write_text(json.dumps({
        "segment": seg.segment_id, "call": rec.to_dict(),
        "drafts": [{"claim": d.claim, "start_s": d.start_s, "end_s": d.end_s,
                    "category": d.category, "epistemic_status": d.epistemic_status,
                    "quote": d.quote, "flags": standalone_flags(d.claim)}
                   for d in drafts],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nrastro cru: {TRACE}")
    print(f"\nPAREI. Os outros {len(segs)-1} segmentos não foram chamados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
