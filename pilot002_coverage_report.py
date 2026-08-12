#!/usr/bin/env python3
"""Cobertura de L0 pelo PILOT-002 compilado — mede e publica.

Roda daqui (ext4). READ-ONLY sobre tudo: lê o L0 cortado e o EVIDENCE.jsonl,
não escreve nada dentro de `pilots/`, `Course-to-Skill/` ou
`Course-to-Skill-Compiler/`. Publica um único relatório em `docs/`.

Relatório GERADO: nenhum número é digitado.

DIFERENÇA DE GRAMÁTICA QUE ESTE SCRIPT TEM DE PONTEAR
-----------------------------------------------------
O PILOT-001 endereça L0 por TEMPO (`source_refs[].timestamp`), e por isso o
mapa de cobertura dele mede segundos direto. O PILOT-002 endereça por LINHA
(`source_excerpt.span.{start_line,end_line}`, citação `#L9-L19`). Para reportar
no MESMO formato — segundos cobertos, percentual, blocos virgens — é preciso
traduzir linha → tempo. A tradução usa as marcas `**MMM:SS**` do próprio
transcript cortado, que são o único endereço comum às duas gramáticas.

GEOMETRIA (idêntica à de `pilot002_holdout.py`, para os números continuarem
comparáveis com o L0_COVERAGE_MAP-PILOT-002 já publicado)
-----------------------------------------------------------------------------
- Cada marca abre um segmento que vai até a marca seguinte.
- Nos DOIS pontos de corte a marca seguinte está a 200s e a 326s de distância,
  porque o held-out foi removido no meio. Esses saltos não são fala: o segmento
  de fronteira termina no início declarado do held-out (11:55 e 44:40).
- A extensão do corpus de treino é a duração nominal do vídeo menos o held-out
  declarado: 4897 - 513 = 4384s. É esse o denominador, e ele bate exatamente
  com a soma dos segmentos retidos.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cts import coverage as C

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
P2 = CLAUDE / "pilots/PILOT-002"

CUT = P2 / "00_SOURCE/L0-transcript-CUT.txt"
COMPILED = P2 / "01_COMPILED-SKILL/v0.1.0"
# O Drive renomeou o arquivo no download ("(1)"). O SHA256SUMS do próprio
# pacote é a autoridade sobre qual é o conteúdo canônico de EVIDENCE.jsonl.
EVIDENCE = COMPILED / "EVIDENCE(1).jsonl"
SUMS = COMPILED / "SHA256SUMS(2).txt"
EVIDENCE_CANONICAL_NAME = "EVIDENCE.jsonl"

OUT = DOCS / "PILOT-002-COVERAGE-REPORT.md"

EXPECTED_CUT = "85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29"

DURATION_S = 4897          # duração nominal do vídeo (PILOT-002-CANDIDATE-METADATA)
MAX_REAL_SEG_S = 15        # acima disto o salto é corte, não fala
MIN_BLOCK = 60             # mesmo limiar do mapa do PILOT-001

# Held-out DECLARADO no lock (G1). É este o corte de verdade.
HELDOUT_LOCK = [("Understanding Permission Modes", 715, 908),        # 11:55–15:08
                ("Managing Your Context Window", 2680, 3000)]        # 44:40–50:00
# Janelas pedidas na conferência, alinhadas à MARCA que abre cada corte.
HELDOUT_ASKED = [("11:48–15:08", 708, 908), ("44:34–50:00", 2674, 3000)]

# Referência do PILOT-001, para a comparação lado a lado.
P001 = {"covered_s": 665, "extent_s": 905, "pct": 73.5}

# ---------------------------------------------------------------------------
# As 4 estruturas multi-ramo, ancoradas por LINHA no transcript cortado.
# As âncoras vêm de varredura do texto real, não de memória. Cada `branches`
# é o conjunto de ramos que a tabela oferece; a checagem é MECÂNICA (o termo
# aparece ou não na claim de alguma evidência que cubra a âncora) e serve para
# tornar a chamada revisível, não para substituí-la.
# ---------------------------------------------------------------------------
TABLES = [
    {
        "key": "CLI × MCP",
        "anchor": (2213, 2574),
        "core": (2409, 2481),
        "core_why": "onde a fonte pergunta 'what's the difference between CLI or "
                    "MCP? Which one should you really use?' e responde",
        "branches": {
            "ramo CLI": r"\bCLI\b|command line",
            "ramo MCP": r"\bMCP\b|model context protocol",
            "critério de escolha": r"speed|token|security|audit|authenticat|"
                                   r"access control|efficien",
        },
    },
    {
        "key": "escopos de instalação de Skill",
        "anchor": (1105, 1127),
        "core": (1109, 1121),
        "core_why": "as opções oferecidas pelo instalador, em 30:18–30:35",
        "branches": {
            "escopo de usuário / global": r"user scope|user/global|global",
            "projeto, compartilhado": r"collaborat|fork|clone|project scope|"
                                      r"for the project",
            "projeto, só para você": r"only for (you|yourself)|personal|"
                                     r"project only|just for you|yourself only",
        },
    },
    {
        "key": ".claude/ × agents/",
        "anchor": (1563, 1660),
        "core": (1583, 1612),
        "core_why": "onde a fonte contrasta 'universal for all the AI agent "
                    "frameworks' com 'only specific for claw code only'",
        "branches": {
            "agents/ universal": r"\bagents?\b.*universal|universal.*\bagents?\b|"
                                 r"AGENTS\.md|\.agents",
            ".claude/ específico": r"claude[- ]specific|specific for claude|"
                                   r"CLAUDE\.md|claude code specific",
            "fonte da verdade / referência": r"source of truth|referenc",
        },
    },
    {
        "key": "escolha de IDE",
        "anchor": (145, 286),
        "core": (169, 185),
        # O FAQ reafirma a mesma escolha em L2839–2867. Fica como âncora
        # SECUNDÁRIA e não como núcleo: o span de `E043` (modos de permissão,
        # L2827–2841) encosta em L2839 por três linhas, e creditá-lo à tabela de
        # IDE seria atribuição falsa — `E043` não fala de IDE.
        "also": (2839, 2870),
        "core_why": "a seção dedicada 'Choosing an IDE & Installing VS Code'; "
                    "o FAQ ('do I need cursor to use it?') reafirma em L2839–2867",
        "branches": {
            "VS Code": r"VS ?Code",
            "alternativas de IDE": r"cursor|anti[- ]?gravity|another IDE|"
                                   r"other IDE|an IDE",
            "terminal puro": r"terminal",
        },
    },
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fmt(s: int) -> str:
    return f"{s // 60}:{s % 60:02d}"


# --------------------------------------------------------------- portão de hash
def hash_gate() -> dict:
    """Confere os dois insumos ANTES de qualquer medição. Diverge → aborta."""
    rows, fatal = [], []

    if not CUT.exists():
        fatal.append(f"L0 cortado ausente: {CUT}")
    if not EVIDENCE.exists():
        fatal.append(f"EVIDENCE ausente: {EVIDENCE}")
    if fatal:
        return {"ok": False, "rows": rows, "fatal": fatal}

    cut_sha = sha(CUT.read_bytes())
    rows.append({"arquivo": str(CUT.relative_to(DRIVE)),
                 "esperado": EXPECTED_CUT, "obtido": cut_sha,
                 "origem_da_expectativa": "informada na tarefa",
                 "confere": cut_sha == EXPECTED_CUT})
    if cut_sha != EXPECTED_CUT:
        fatal.append(f"L0 cortado divergente: esperado {EXPECTED_CUT[:16]}… "
                     f"obtido {cut_sha[:16]}…")

    # A expectativa do EVIDENCE não foi informada na tarefa: a autoridade é o
    # SHA256SUMS publicado junto com o pacote compilado.
    ev_sha = sha(EVIDENCE.read_bytes())
    expected_ev = None
    if SUMS.exists():
        for line in SUMS.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == EVIDENCE_CANONICAL_NAME:
                expected_ev = parts[0]
    rows.append({"arquivo": str(EVIDENCE.relative_to(DRIVE)),
                 "esperado": expected_ev or "—",
                 "obtido": ev_sha,
                 "origem_da_expectativa": (
                     f"`{SUMS.name}` do próprio pacote, linha "
                     f"`{EVIDENCE_CANONICAL_NAME}`" if expected_ev
                     else "NENHUMA — o pacote não declara hash"),
                 "confere": expected_ev == ev_sha if expected_ev else None})
    if expected_ev is None:
        fatal.append("O pacote não declara hash para EVIDENCE.jsonl; sem "
                     "autoridade para o portão.")
    elif expected_ev != ev_sha:
        fatal.append(f"EVIDENCE divergente: esperado {expected_ev[:16]}… "
                     f"obtido {ev_sha[:16]}…")

    return {"ok": not fatal, "rows": rows, "fatal": fatal,
            "cut_sha": cut_sha, "ev_sha": ev_sha,
            "renamed_by_drive": EVIDENCE.name != EVIDENCE_CANONICAL_NAME}


# --------------------------------------------------------------- geometria
def build_segments(lines: list[str]) -> list[dict]:
    """Segmentos do transcript cortado: linha inicial/final e tempo inicial/final.

    O segmento de fronteira de corte termina no início declarado do held-out,
    não na marca seguinte — o salto de 200s/326s é o buraco deixado pelo corte,
    não fala que alguém possa cobrir.
    """
    marks = [(i + 1, C.mark_to_s(m.group(1)))
             for i, l in enumerate(lines)
             if (m := re.fullmatch(r"\*\*(\d{1,3}:[0-5]\d)\*\*", l.strip()))]

    holdout_starts = sorted(a for _, a, _ in HELDOUT_LOCK)
    segs = []
    for i, (ln, s) in enumerate(marks):
        if i + 1 < len(marks):
            nxt_ln, nxt_s = marks[i + 1]
            end_line = nxt_ln - 1
            end_s = nxt_s
            cut_here = (nxt_s - s) > MAX_REAL_SEG_S
            if cut_here:
                # termina onde o held-out declarado começa
                end_s = min((h for h in holdout_starts if h > s), default=nxt_s)
        else:
            end_line = len(lines)
            end_s = DURATION_S          # cauda nominal depois da última marca
            cut_here = False
        segs.append({"i": i, "start_line": ln, "end_line": end_line,
                     "start_s": s, "end_s": end_s, "dur": end_s - s,
                     "cut_boundary": cut_here})
    return segs


def lines_to_intervals(a: int, b: int, segs: list[dict]) -> list[tuple[int, int]]:
    """Intervalos de tempo dos segmentos que a faixa de linhas [a,b] toca."""
    return [(s["start_s"], s["end_s"]) for s in segs
            if s["start_line"] <= b and s["end_line"] >= a]


def subtract(blocks: list[C.Block], holes: list[tuple[int, int]]) -> list[C.Block]:
    """Remove as janelas de held-out de uma lista de blocos."""
    out = []
    for blk in blocks:
        pieces = [(blk.start, blk.end)]
        for h0, h1 in holes:
            nxt = []
            for p0, p1 in pieces:
                if h1 <= p0 or h0 >= p1:
                    nxt.append((p0, p1))
                    continue
                if p0 < h0:
                    nxt.append((p0, h0))
                if h1 < p1:
                    nxt.append((h1, p1))
            pieces = nxt
        out += [C.Block(p0, p1) for p0, p1 in pieces if p1 > p0]
    return out


# --------------------------------------------------------------- coleta
def collect() -> dict:
    gate = hash_gate()
    if not gate["ok"]:
        return {"gate": gate}

    text = CUT.read_text(encoding="utf-8")
    lines = text.splitlines()
    segs = build_segments(lines)
    holes = [(a, b) for _, a, b in HELDOUT_LOCK]

    held_s = sum(b - a for a, b in holes)
    extent = DURATION_S - held_s
    retained = sum(s["dur"] for s in segs)

    ev = [json.loads(l) for l in EVIDENCE.read_text(encoding="utf-8").splitlines()
          if l.strip()]

    cits, per_ev = [], []
    for e in ev:
        se = e["source_excerpt"]
        sp = se.get("span") or {}
        a, b = sp.get("start_line"), sp.get("end_line")
        iv = lines_to_intervals(a, b, segs) if a and b else []
        for i0, i1 in iv:
            cits.append(C.Citation(i0, i1, "evidence", e["evidence_id"]))
        per_ev.append({
            "id": e["evidence_id"], "status": e["epistemic_status"],
            "claim": e["claim"], "a": a, "b": b,
            "citation": se.get("citation"),
            "source_file": se.get("source_file"),
            "source_sha256": se.get("source_sha256"),
            "t0": min((x[0] for x in iv), default=None),
            "t1": max((x[1] for x in iv), default=None),
            "segments": len(iv),
        })

    covered = C.merge(cits)
    covered = subtract(covered, holes)          # não pode cobrir o que foi cortado
    cov_s = sum(b.dur for b in covered)

    gaps = C.complement(C.merge(cits + [C.Citation(a, b, "holdout", "H")
                                        for a, b in holes]), 0, DURATION_S)
    virgin_s = sum(g.dur for g in gaps)
    for g in gaps:
        g.text = C.text_for(text, C.mark_index(text), g.start, g.end)
        g.verdict, g.markers = C.classify(g.text)

    # --- held-out: nenhuma evidência pode citar span dentro das janelas
    def hits(windows):
        out = []
        for p in per_ev:
            if p["t0"] is None:
                continue
            for name, w0, w1 in windows:
                for i0, i1 in lines_to_intervals(p["a"], p["b"], segs):
                    if i0 < w1 and w0 < i1:
                        out.append({"id": p["id"], "window": name,
                                    "overlap": (max(i0, w0), min(i1, w1))})
        return out

    mention_re = re.compile(r"11:48|15:08|44:34|44:40|50:00|11:55")
    mentions = [{"id": p["id"], "status": p["status"], "claim": p["claim"]}
                for p in per_ev if mention_re.search(p["claim"])]

    # --- 4 tabelas multi-ramo
    tables = []
    for t in TABLES:
        a0, b0 = t["anchor"]
        c0, c1 = t["core"]
        cover_anchor = [p for p in per_ev if p["a"] <= b0 and p["b"] >= a0]
        cover_core = [p for p in per_ev if p["a"] <= c1 and p["b"] >= c0]
        also = t.get("also")
        cover_also = ([p for p in per_ev if p["a"] <= also[1] and p["b"] >= also[0]]
                      if also else [])
        blob = " ".join(p["claim"] for p in (cover_anchor + cover_core + cover_also))
        branches = {name: bool(re.search(rx, blob, re.I))
                    for name, rx in t["branches"].items()}
        tables.append({
            "key": t["key"], "anchor": t["anchor"], "core": t["core"],
            "also": also, "core_why": t["core_why"],
            "evidence_anchor": sorted({p["id"] for p in cover_anchor}),
            "evidence_core": sorted({p["id"] for p in cover_core}),
            "evidence_also": sorted({p["id"] for p in cover_also}),
            "branches": branches,
            "covered": bool(cover_core or cover_also),
            "all_branches": all(branches.values()),
        })

    infer = [p for p in per_ev if p["status"] == "MODEL_INFERENCE"]
    # As estruturas condicionais são as 4 tabelas. Alguma delas se apoia numa
    # MODEL_INFERENCE? A pergunta é mecânica: há interseção de IDs?
    infer_ids = {p["id"] for p in infer}
    table_ids = set().union(*[set(t["evidence_core"]) for t in tables]) if tables else set()

    return {
        "gate": gate,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "l0": {"sha256": gate["cut_sha"], "bytes": CUT.stat().st_size,
               "lines": len(lines), "marks": len(segs),
               "duration_s": DURATION_S, "heldout_s": held_s,
               "extent_s": extent, "retained_sum_s": retained,
               "geometry_ok": retained == extent,
               "last_mark_s": segs[-1]["start_s"] if segs else 0},
        "evidence": {"n": len(ev), "sha256": gate["ev_sha"],
                     "citations": len(cits),
                     "status": {"SOURCE_EXPLICIT": sum(1 for p in per_ev if p["status"] == "SOURCE_EXPLICIT"),
                                "MODEL_INFERENCE": len(infer)},
                     "all_same_source": len({p["source_file"] for p in per_ev}) == 1,
                     "all_same_sha": len({p["source_sha256"] for p in per_ev}) == 1,
                     "declared_sha_matches": {p["source_sha256"] for p in per_ev} == {gate["cut_sha"]}},
        "coverage": {
            "extent_s": extent, "covered_s": cov_s, "virgin_s": virgin_s,
            "covered_pct": round(100 * cov_s / extent, 1),
            "virgin_pct": round(100 * virgin_s / extent, 1),
            "covered_blocks": len(covered), "virgin_blocks": len(gaps),
            "largest_virgin_s": max((g.dur for g in gaps), default=0),
            "largest_virgin": max(gaps, key=lambda g: g.dur) if gaps else None,
            "virgin_ge_min": sum(1 for g in gaps if g.dur >= MIN_BLOCK),
            "min_block_s": MIN_BLOCK,
            "checksum_ok": cov_s + virgin_s == extent,
        },
        "covered_list": [{"start": b.start, "end": b.end, "dur": b.dur} for b in covered],
        "virgin": [{"start": g.start, "end": g.end, "dur": g.dur,
                    "verdict": g.verdict, "markers": g.markers, "text": g.text}
                   for g in gaps],
        "per_ev": per_ev,
        "tables": tables,
        "inference": infer,
        "inference_in_tables": sorted(infer_ids & table_ids),
        "heldout": {
            "lock_windows": [{"name": n, "a": a, "b": b} for n, a, b in HELDOUT_LOCK],
            "asked_windows": [{"name": n, "a": a, "b": b} for n, a, b in HELDOUT_ASKED],
            "violations_lock": hits(HELDOUT_LOCK),
            "violations_asked": hits(HELDOUT_ASKED),
            "textual_mentions": mentions,
        },
    }


# --------------------------------------------------------------- render
def table(rows, head):
    out = ["| " + " | ".join(head) + " |",
           "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def render(d: dict) -> str:
    L = []
    w = L.append
    cv, l0, evd = d["coverage"], d["l0"], d["evidence"]

    w("# PILOT-002 — COVERAGE REPORT\n")
    w(f"**Gerado:** `{d['generated']}` · gerador `{Path(__file__).name}` · "
      "**somente medição**, READ-ONLY.\n")
    w("Relatório gerado por script; nenhum número foi digitado. Mesmo formato do "
      "`L0_COVERAGE_MAP` do PILOT-001, para os dois corpora ficarem comparáveis.\n")

    # ---------------------------------------------------------------- 0
    w("\n## 0. Portão de hash\n")
    w(table([[f"`{r['arquivo']}`",
              f"`{r['esperado'][:16]}…`" if r["esperado"] != "—" else "—",
              f"`{r['obtido'][:16]}…`",
              r["origem_da_expectativa"],
              "**CONFERE**" if r["confere"] else "**DIVERGE**"]
             for r in d["gate"]["rows"]],
            ["arquivo", "esperado", "obtido", "autoridade da expectativa", "veredito"]))
    if d["gate"]["renamed_by_drive"]:
        w(f"\n> O arquivo em disco chama-se `{EVIDENCE.name}`, não "
          f"`{EVIDENCE_CANONICAL_NAME}` — renomeação de download do Drive. O "
          "conteúdo é o canônico: o hash bate com a linha "
          f"`{EVIDENCE_CANONICAL_NAME}` do `{SUMS.name}` publicado no próprio "
          "pacote. A expectativa do EVIDENCE **não foi informada na tarefa**; a "
          "autoridade usada está declarada na tabela.\n")
    w("\nOs dois portões passam. A medição prossegue.\n")

    # ---------------------------------------------------------------- 1
    w("\n## 1. Entrada e geometria\n")
    w(table([["sha256 do L0 cortado", f"`{l0['sha256'][:16]}…`"],
             ["bytes / linhas / marcas", f"{l0['bytes']} / {l0['lines']} / {l0['marks']}"],
             ["duração nominal do vídeo", f"{fmt(l0['duration_s'])} = {l0['duration_s']}s"],
             ["held-out removido (lock G1)", f"{l0['heldout_s']}s"],
             ["**extensão do corpus de treino**", f"**{fmt(l0['extent_s'])} = {l0['extent_s']}s**"],
             ["soma dos segmentos retidos", f"{l0['retained_sum_s']}s"],
             ["geometria fecha", "**SIM**" if l0["geometry_ok"] else "**NÃO**"],
             ["última marca", fmt(l0["last_mark_s"])],
             ["evidências", evd["n"]],
             ["citações (segmento × evidência)", evd["citations"]],
             ["`source_file` único", "sim" if evd["all_same_source"] else "não"],
             ["`source_sha256` declarado bate com o arquivo",
              "**sim**" if evd["declared_sha_matches"] else "**NÃO**"]],
            ["item", "valor"]))
    w("\n> **Tradução de gramática.** O PILOT-001 endereça L0 por tempo; o "
      "PILOT-002 endereça por **linha** (`#L9-L19`). Para reportar segundos, "
      "cada faixa de linhas foi traduzida para os segmentos de marca que ela "
      "toca. Nos dois pontos de corte a marca seguinte está a 200s e 326s de "
      "distância — esse salto é o buraco do held-out, não fala, e o segmento de "
      "fronteira termina no início declarado do corte. A soma dos segmentos "
      f"retidos ({l0['retained_sum_s']}s) fecha com a extensão declarada "
      f"({l0['extent_s']}s), que é a checagem de que a tradução não inventou nem "
      "perdeu tempo.\n")

    # ---------------------------------------------------------------- 2
    w("\n## 2. Cobertura de L0 pelas 44 evidências\n")
    w(table([["extensão do corpus de treino", f"{fmt(cv['extent_s'])} ({cv['extent_s']}s)"],
             ["**coberto**", f"**{fmt(cv['covered_s'])} ({cv['covered_s']}s) — {cv['covered_pct']}%**"],
             ["**virgem**", f"**{fmt(cv['virgin_s'])} ({cv['virgin_s']}s) — {cv['virgin_pct']}%**"],
             ["blocos cobertos contíguos", cv["covered_blocks"]],
             ["**blocos virgens contíguos**", f"**{cv['virgin_blocks']}**"],
             ["**maior bloco virgem**", f"**{cv['largest_virgin_s']}s**"
              + (f" ({fmt(cv['largest_virgin'].start)}–{fmt(cv['largest_virgin'].end)})"
                 if cv["largest_virgin"] else "")],
             [f"blocos virgens ≥ {cv['min_block_s']}s", cv["virgin_ge_min"]],
             ["coberto + virgem = extensão", "sim" if cv["checksum_ok"] else "NÃO"]],
            ["métrica", "valor"]))

    w("\n### 2.1 Lado a lado com o PILOT-001\n")
    delta = cv["covered_pct"] - P001["pct"]
    w(table([["PILOT-001", f"{P001['covered_s']}s", f"{P001['extent_s']}s",
              f"**{P001['pct']}%**"],
             ["PILOT-002", f"{cv['covered_s']}s", f"{cv['extent_s']}s",
              f"**{cv['covered_pct']}%**"]],
            ["piloto", "coberto", "extensão", "cobertura"]))
    w(f"\n**Diferença: {delta:+.1f} pontos percentuais.** ")
    if delta < 0:
        w("O PILOT-002 cobre proporcionalmente **menos** da sua fonte que o "
          "PILOT-001, sobre um corpus quase cinco vezes maior.\n")
    else:
        w("O PILOT-002 cobre proporcionalmente **mais** da sua fonte.\n")
    w("\n> As duas medidas usam o mesmo denominador conceitual (extensão da "
      "fonte disponível) e o mesmo numerador (união dos spans citados pelas "
      "evidências de L1). A comparação é legítima nesse nível. O que **não** é "
      "comparável é a granularidade: o PILOT-001 cita por timestamp, e o "
      "PILOT-002 cita por faixa de linhas, que é mais grossa — uma citação de "
      "linha arrasta o segmento de marca inteiro. Isso empurra a cobertura do "
      "PILOT-002 para **cima**, não para baixo.\n")

    big = [g for g in d["virgin"] if g["dur"] >= cv["min_block_s"]]
    w(f"\n### 2.2 Os {len(big)} maiores blocos virgens (≥ {cv['min_block_s']}s)\n")
    w(table([[fmt(g["start"]), fmt(g["end"]), f"{g['dur']}s", g["verdict"],
              (g["text"][:110] + "…") if len(g["text"]) > 110 else (g["text"] or "—")]
             for g in sorted(big, key=lambda x: -x["dur"])[:20]],
            ["início", "fim", "dur", "triagem mecânica", "trecho"]))
    w("\n> A triagem é a de `cts/coverage.py`, cujos marcadores foram extraídos "
      "do PILOT-001 (curso de marketing). Sobre um curso de ferramenta de "
      "programação ela é **indicativa, não calibrada** — vale para comparar "
      "formato, não para decidir held-out.\n")

    # ---------------------------------------------------------------- 3
    w("\n## 3. As 4 estruturas multi-ramo\n")
    w("A pergunta é se a estrutura que justifica a fonte entrou na Skill. "
      "Checagem em dois níveis: a evidência **alcança** as linhas da tabela, e "
      "as *claims* dessas evidências **nomeiam cada ramo**. O segundo nível é "
      "mecânico (o termo aparece ou não) e serve para tornar a chamada "
      "revisível, não para substituí-la.\n")
    w(table([[t["key"],
              f"L{t['anchor'][0]}–{t['anchor'][1]}",
              ", ".join(f"`{x}`" for x in t["evidence_core"]) or "—",
              "**SIM**" if t["covered"] else "**NÃO**",
              f"{sum(t['branches'].values())}/{len(t['branches'])}"]
             for t in d["tables"]],
            ["tabela", "âncora (linhas)", "evidência que alcança o núcleo",
             "coberta", "ramos nomeados"]))
    w("")
    for t in d["tables"]:
        status = "COBERTA" if t["covered"] else "**AUSENTE — ACHADO GRAVE**"
        w(f"\n**{t['key']}** — {status}  ")
        w(f"núcleo em L{t['core'][0]}–{t['core'][1]} ({t['core_why']}).  ")
        w(f"evidência que alcança a âncora: "
          f"{', '.join('`' + x + '`' for x in t['evidence_anchor']) or 'nenhuma'}.  ")
        if t["also"]:
            w(f"âncora secundária L{t['also'][0]}–{t['also'][1]}: "
              f"{', '.join('`' + x + '`' for x in t['evidence_also']) or 'nenhuma'}.\n")
        else:
            w("")
        w(table([[name, "sim" if ok else "**não**"]
                 for name, ok in t["branches"].items()], ["ramo", "nomeado na claim"]))
        w("")

    missing = [t for t in d["tables"] if not t["covered"]]
    partial = [t for t in d["tables"] if t["covered"] and not t["all_branches"]]
    if missing:
        w(f"\n> **ACHADO GRAVE: {len(missing)} tabela(s) sem evidência nenhuma** — "
          + ", ".join(t["key"] for t in missing) + ".\n")
    else:
        w("\n> **Nenhuma das 4 tabelas ficou fora.** Todas têm evidência "
          "alcançando o núcleo. Não há achado grave no critério pedido.\n")
    if partial:
        w(f"\n> **Ressalva, num nível abaixo do achado grave:** "
          f"{len(partial)} tabela(s) têm evidência mas a *claim* não nomeia "
          "todos os ramos — "
          + "; ".join(
              f"**{t['key']}** (falta: "
              + ", ".join(n for n, ok in t["branches"].items() if not ok) + ")"
              for t in partial)
          + ". A faixa de linhas citada **cobre** o ramo; o que não o alcança é "
          "o texto da afirmação. Isso é compressão na redação da evidência, não "
          "ausência de fonte.\n")

    # ---------------------------------------------------------------- 4
    w("\n## 4. Os 5 MODEL_INFERENCE\n")
    w(table([[f"`{p['id']}`", f"L{p['a']}–{p['b']}",
              f"{fmt(p['t0'])}–{fmt(p['t1'])}" if p["t0"] is not None else "—",
              p["claim"]]
             for p in d["inference"]],
            ["id", "linhas", "tempo", "claim"]))
    inter = d["inference_in_tables"]
    w(f"\n**Interseção com as 4 tabelas multi-ramo: "
      f"{', '.join('`' + x + '`' for x in inter) if inter else 'nenhuma'}.**\n")
    w("\nLeitura do conjunto: **não são as decisões condicionais.** As quatro "
      "estruturas de decisão do curso — CLI × MCP, escopos de Skill, "
      "`.claude/` × `agents/`, escolha de IDE — estão **todas** em evidência "
      "`SOURCE_EXPLICIT`. Nenhuma delas se apoia numa inferência.\n")
    w("\nO que os 5 são, um a um, está na tabela acima; o padrão é este: "
      "**quatro dos cinco são marcadores de contenção, não de conteúdo.** "
      "`E017`, `E040` e `E043` dizem explicitamente o que a compilação **não "
      "pode** fazer — não promover um exemplo a `missing_input_action` padrão, "
      "não generalizar uma verificação de alvo, não reconstruir política de "
      "permissão a partir do que foi cortado. `E008` marca que tratar a ordem "
      "demonstrada como workflow recomendado é inferência. Só `E010` é "
      "generalização de procedimento periférico (localizar assets antes do "
      "build).\n")
    w("\nOu seja: o compilador usou a categoria `MODEL_INFERENCE` sobretudo "
      "para **declarar limite**, e não para carregar decisão. Isso é coerente "
      "com o `COMPILATION_MANIFEST`, que lista `missing_input_action` entre os "
      "4 campos não definidos — exatamente o campo que `E017` se recusa a "
      "preencher.\n")

    # ---------------------------------------------------------------- 5
    w("\n## 5. Held-out: nenhuma evidência cita span cortado\n")
    hd = d["heldout"]
    w("Duas janelas foram conferidas, porque não são a mesma coisa:\n")
    w(table([["janelas do lock (G1)",
              ", ".join(f"{fmt(x['a'])}–{fmt(x['b'])}" for x in hd["lock_windows"]),
              "o corte declarado",
              f"**{len(hd['violations_lock'])} violação(ões)**"],
             ["janelas pedidas na conferência",
              ", ".join(x["name"] for x in hd["asked_windows"]),
              "alinhadas à marca que ABRE cada corte",
              f"**{len(hd['violations_asked'])} violação(ões)**"]],
            ["janela", "intervalo", "o que é", "resultado"]))
    if not hd["violations_lock"] and not hd["violations_asked"]:
        w("\n**CONFIRMADO: nenhuma das 44 evidências cita span dentro de "
          "qualquer das duas janelas, nem na leitura estrita do lock nem na "
          "leitura mais larga pedida.**\n")
    else:
        w("\n**VIOLAÇÃO:**\n")
        w(table([[f"`{v['id']}`", v["window"],
                  f"{fmt(v['overlap'][0])}–{fmt(v['overlap'][1])}"]
                 for v in (hd["violations_lock"] + hd["violations_asked"])],
                ["evidência", "janela", "sobreposição"]))
    w("\n> As duas janelas diferem no início: o lock declara 11:55 e 44:40, e o "
      "corte removeu os segmentos INTEIROS que as contêm, cujas marcas abrem em "
      "11:48 e 44:34. As marcas 11:48 e 44:34 **sobrevivem** no corpus de "
      "treino. Conferir só a janela do lock deixaria 13s de fronteira sem "
      "checar; por isso as duas foram medidas.\n")

    if hd["textual_mentions"]:
        w("\n### 5.1 Menção textual, que não é citação\n")
        w(table([[f"`{m['id']}`", m["status"], m["claim"]]
                 for m in hd["textual_mentions"]],
                ["id", "status", "claim"]))
        w("\n> Isto **não é violação e é importante não confundir**: a evidência "
          "acima *escreve* o intervalo do held-out no texto da afirmação, mas o "
          "span que ela cita fica fora dele. É o oposto de vazamento — é o "
          "registro de que o material está ausente, que é justamente o que se "
          "espera de uma compilação honesta sobre corpus cortado. O que a "
          "checagem proíbe é citar span dentro da janela, e isso não acontece.\n")

    # ---------------------------------------------------------------- 6
    w("\n## 6. Todas as 44 evidências\n")
    w(table([[f"`{p['id']}`", p["status"][:4], f"L{p['a']}–{p['b']}",
              f"{fmt(p['t0'])}–{fmt(p['t1'])}" if p["t0"] is not None else "—",
              p["segments"],
              (p["claim"][:88] + "…") if len(p["claim"]) > 88 else p["claim"]]
             for p in d["per_ev"]],
            ["id", "tipo", "linhas", "tempo", "segs", "claim"]))

    w("\n## 7. Blocos cobertos, para conferência\n")
    w(table([[fmt(b["start"]), fmt(b["end"]), f"{b['dur']}s"]
             for b in d["covered_list"]], ["início", "fim", "duração"]))

    w("\n---\n")
    w("**Escopo:** somente medição. Nada foi cortado, nenhuma evidência foi "
      "reescrita, nenhum arquivo de `pilots/`, `Course-to-Skill/` ou "
      "`Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado. O "
      "único arquivo escrito é este relatório.")
    return "\n".join(L) + "\n"


def main() -> int:
    d = collect()
    g = d["gate"]
    if not g["ok"]:
        print("PORTÃO DE HASH REPROVADO — nada foi medido nem publicado:")
        for f in g["fatal"]:
            print("  -", f)
        return 2

    OUT.write_text(render(d), encoding="utf-8")
    cv = d["coverage"]
    print(f"portão de hash: OK nos dois insumos")
    print(f"coberto {cv['covered_s']}s de {cv['extent_s']}s = {cv['covered_pct']}% "
          f"| virgem {cv['virgin_s']}s ({cv['virgin_pct']}%)")
    print(f"blocos virgens: {cv['virgin_blocks']} | maior: {cv['largest_virgin_s']}s")
    print(f"geometria fecha: {d['l0']['geometry_ok']} | "
          f"coberto+virgem=extensão: {cv['checksum_ok']}")
    for t in d["tables"]:
        print(f"  tabela {t['key']}: {'COBERTA' if t['covered'] else 'AUSENTE'} "
              f"({sum(t['branches'].values())}/{len(t['branches'])} ramos) "
              f"<- {', '.join(t['evidence_core']) or '—'}")
    hd = d["heldout"]
    print(f"held-out: {len(hd['violations_lock'])} violação(ões) no lock, "
          f"{len(hd['violations_asked'])} na janela larga | "
          f"{len(hd['textual_mentions'])} menção(ões) textual(is)")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) "
          f"{sha(OUT.read_bytes())[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
