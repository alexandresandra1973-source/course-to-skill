#!/usr/bin/env python3
"""Plano de execução do PILOT-001 corrigido. NÃO EXECUTA, NÃO CHAMA MODELO.

Roda daqui (ext4). READ-ONLY sobre `Course-to-Skill/`.

O que faz:
  1. confere os insumos do PILOT-001 e fatia o texto por segmento;
  2. calcula quantas chamadas a execução fará, no melhor e no pior caso;
  3. prova a fiação de ponta a ponta com um cliente FALSO — o pipeline inteiro
     roda, o extractor real é exercitado, e nenhum byte sai para a rede;
  4. reporta o que fica registrado por chamada.

O cliente falso existe para separar duas perguntas que costumam ser confundidas:
"a máquina está ligada certo?" e "o modelo extrai bem?". Esta é a primeira. A
segunda só a execução real responde.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
V2 = DRIVE / "Course-to-Skill-Claude/compiler-v2"
sys.path.insert(0, str(V2))

P1 = DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
TMAP = P1 / "analysis/temporal-map.yaml"
L0 = P1 / "sources/transcript/transcript-original-en.txt"

from ctsc2 import pipeline                                    # noqa: E402
from ctsc2.extractors.claude_extractor import (               # noqa: E402
    CATEGORIES, MAX_TOKENS, MODEL, EFFORT, SCHEMA, SYSTEM, ClaudeExtractor)
from ctsc2.model import Segment                               # noqa: E402
from ctsc2.thresholds import (COVERAGE_FLOOR, HISTORICAL,     # noqa: E402
                              MAX_RESCAN_ITERATIONS, PASS1_BAND_INCLUSIVE)

MARK_RE = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hhmmss(t: str) -> int:
    p = [int(x) for x in t.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def load_segments() -> list[Segment]:
    tm = yaml.safe_load(TMAP.read_text(encoding="utf-8"))
    return [Segment(s["segment_id"], hhmmss(s["start"]), hhmmss(s["end"]),
                    s.get("topic", ""), s.get("function", ""))
            for s in tm["temporal_map"]]


def slicer(text: str):
    """Texto de um segmento: os blocos cuja marca cai dentro do intervalo."""
    blocks = text.split("\n\n")
    idx = []
    for i, b in enumerate(blocks):
        m = MARK_RE.fullmatch(b.strip())
        if m:
            idx.append((i, int(m.group(1)) * 60 + int(m.group(2))))

    def text_for(seg: Segment) -> str:
        out = []
        for k, (i, s) in enumerate(idx):
            if seg.start_s <= s < seg.end_s:
                end = idx[k + 1][0] if k + 1 < len(idx) else len(blocks)
                out.extend(blocks[i:end])
        return "\n\n".join(out).strip()
    return text_for


class FakeClient:
    """Cliente falso. Não fala com a rede. Devolve UMA evidência válida por
    segmento, montada a partir do próprio texto — o suficiente para provar que
    a validação aceita o que é legítimo."""

    class _Usage:
        input_tokens = 0
        output_tokens = 0
        cache_read_input_tokens = 0
        cache_creation_input_tokens = 0

    class _Block:
        type = "text"

        def __init__(self, text):
            self.text = text

    class _Msg:
        stop_reason = "end_turn"
        _request_id = "req_FAKE"

        def __init__(self, text):
            self.content = [FakeClient._Block(text)]
            self.usage = FakeClient._Usage()

    class _Stream:
        def __init__(self, payload):
            self._payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get_final_message(self):
            return FakeClient._Msg(self._payload)

    class _Messages:
        def __init__(self, outer):
            self.outer = outer

        def stream(self, **kw):
            self.outer.requests.append(kw)
            body = kw["messages"][0]["content"]
            seg_id = body.split()[1] if body.startswith("SEGMENTO ") else "?"
            seg_text = body.split("---", 1)[1] if "---" in body else body
            marks = [f"{m.group(1)}:{m.group(2)}" for m in MARK_RE.finditer(seg_text)]
            quote = ""
            for b in seg_text.split("\n\n"):
                if b.strip() and not MARK_RE.fullmatch(b.strip()):
                    quote = b.strip()
                    break
            if not marks or not quote:
                return FakeClient._Stream(json.dumps({"evidence": []}))
            return FakeClient._Stream(json.dumps({"evidence": [{
                # Claim distinta por segmento: com a mesma claim em todos, a
                # dedup (corretamente) funde as 9 em 1 e o caminho de cobertura
                # nunca é exercitado. O ensaio mede fiação, não extração.
                "claim": f"unidade sintetica do cliente falso em {seg_id}",
                "start_mark": marks[0], "end_mark": marks[min(1, len(marks) - 1)],
                "quote": quote, "category": "CONCEPT",
                "epistemic_status": "SOURCE_EXPLICIT"}]}))

    def __init__(self):
        self.requests: list[dict] = []
        self.messages = FakeClient._Messages(self)


def main() -> int:
    for p in (TMAP, L0):
        if not p.is_file():
            print(f"INSUMO AUSENTE: {p}")
            return 2

    segs = load_segments()
    text = L0.read_text(encoding="utf-8")
    text_for = slicer(text)
    per = [{"id": s.segment_id, "dur": s.duration, "topic": s.topic,
            "chars": len(text_for(s)),
            "marks": len(MARK_RE.findall(text_for(s)))} for s in segs]

    n = len(segs)
    print("=" * 78)
    print("PLANO DE EXECUÇÃO — PILOT-001 corrigido (NADA FOI EXECUTADO)")
    print("=" * 78)
    print(f"temporal-map : {TMAP.relative_to(DRIVE)}")
    print(f"               sha256 {sha_p(TMAP)[:16]}… · {n} segmentos")
    print(f"L0           : {L0.relative_to(DRIVE)}")
    print(f"               sha256 {sha_p(L0)[:16]}… · {len(text)} bytes")
    print(f"banda do PASS 1: {PASS1_BAND_INCLUSIVE} · histórico {HISTORICAL['segments']}"
          f" · dentro da banda: {PASS1_BAND_INCLUSIVE[0] <= n <= PASS1_BAND_INCLUSIVE[1]}")

    print(f"\n--- fatiamento por segmento ---")
    print(f"{'segmento':<10}{'dur':>6}{'chars':>8}{'marcas':>8}  tópico")
    for r in per:
        print(f"{r['id']:<10}{r['dur']:>5}s{r['chars']:>8}{r['marks']:>8}  {r['topic'][:34]}")
    empty = [r for r in per if r["chars"] == 0]
    print(f"total: {sum(r['chars'] for r in per)} chars · "
          f"{sum(r['marks'] for r in per)} marcas · segmentos vazios: {len(empty)}")

    print(f"\n--- chamadas ---")
    print(f"PASS 2                       : {n} chamadas (1 por segmento)")
    print(f"revarredura, melhor caso     : 0 (cobertura > {COVERAGE_FLOOR:.3f} de saída)")
    print(f"revarredura, pior caso       : {n} × {MAX_RESCAN_ITERATIONS} = "
          f"{n * MAX_RESCAN_ITERATIONS}")
    print(f"TOTAL melhor caso            : {n}")
    print(f"TOTAL pior caso              : {n * (1 + MAX_RESCAN_ITERATIONS)}")
    print(f"  (a revarredura é DIRIGIDA: só segmentos que tocam bloco descoberto,")
    print(f"   então o pior caso só ocorre se todos os {n} ficarem descobertos")
    print(f"   nas {MAX_RESCAN_ITERATIONS} iterações)")

    print(f"\n--- configuração por chamada ---")
    print(f"model={MODEL} · effort={EFFORT} · max_tokens={MAX_TOKENS}")
    print(f"thinking=adaptive · streaming=sim · structured output=json_schema")
    print(f"system cacheado ({len(SYSTEM)} chars, cache_control ephemeral)")
    print(f"schema: {len(SCHEMA['properties']['evidence']['items']['required'])} campos "
          f"obrigatórios · {len(CATEGORIES)} categorias")

    print(f"\n--- ensaio de fiação com CLIENTE FALSO (sem rede) ---")
    fake = FakeClient()
    ex = ClaudeExtractor(text_for, client=fake)
    with tempfile.TemporaryDirectory(prefix="plan-p001-") as tmp:
        res = pipeline.compile_lesson(
            pilot_id="PILOT-001", lesson_id="PILOT-001-L01",
            l0_sha256=sha_p(L0), extent_s=905, segments=segs,
            extractor=ex, out_dir=Path(tmp),
            compiler_version="compiler-v2/0.2.0-frozen")
        m = res.manifest
        print(f"chamadas feitas ao cliente falso : {len(fake.requests)}")
        print(f"evidências após dedup            : {len(res.evidences)}")
        print(f"cobertura medida                 : {m['coverage_gate']['l0_coverage_pct']}%")
        print(f"portão                           : {m['coverage_gate']['result']} "
              f"({m['coverage_gate']['stop_reason']})")
        print(f"iterações de revarredura         : {m['coverage_gate']['rescan_iterations']}")
        print(f"segmentos com yield zero         : {m['pass2']['zero_yield_count']}")
        print(f"rastro por segmento              : "
              f"{len(m['pass2']['per_segment_yield'])} linhas (esperado {n})")
        t = ex.totals()
        print(f"rejeições da validação           : {t['drafts_rejected']} de "
              f"{t['drafts_returned']} devolvidas")
        one = ex.calls[0].to_dict()
        print(f"\n--- registrado POR CHAMADA (exemplo, {one['segment_id']}) ---")
        for k, v in one.items():
            print(f"  {k:<28} {v}")

    print("\n--- estado do SDK ---")
    try:
        import anthropic
        print(f"anthropic instalado: {anthropic.__version__}")
    except ImportError:
        print("anthropic AUSENTE — `pip install anthropic` antes de executar.")
    import os
    print("ANTHROPIC_API_KEY definida:" ,bool(os.environ.get("ANTHROPIC_API_KEY")))

    print("\nNADA FOI EXECUTADO CONTRA MODELO REAL. Nenhum piloto recompilado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
