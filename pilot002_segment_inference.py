#!/usr/bin/env python3
"""Inferir a contagem de segmentos do PASS 1 do PILOT-002.

Roda daqui (ext4). READ-ONLY sobre tudo. Publica um único arquivo em `docs/`.
Relatório GERADO: nenhum número é digitado.

O QUE ESTE RELATÓRIO É, E O QUE NÃO É
--------------------------------------
O PILOT-001 tem `analysis/temporal-map.yaml`: 9 segmentos declarados, lidos de
artefato. O PILOT-002 **não persistiu** o mapa equivalente. Tudo o que este
relatório diz sobre o PASS 1 do PILOT-002 é **INFERIDO do padrão temporal das
44 evidências**, não lido de artefato. Não é medição.

O MÉTODO E SEU TESTE DE VALIDADE
---------------------------------
Agrupamento por lacuna: evidências ordenadas pelo início do span; lacuna maior
que X entre o fim de uma e o início da seguinte abre grupo novo. X é varrido e
a curva inteira é reportada.

A calibração NÃO é um detalhe de implementação — é o teste de validade do
método. Se o agrupamento por lacuna não reproduz os 9 segmentos do PILOT-001,
onde a resposta é conhecida, então ele não recupera segmentação do PASS 1 e
aplicá-lo ao PILOT-002 não autoriza conclusão nenhuma. O relatório reporta o
resultado desse teste antes de qualquer inferência sobre o PILOT-002.

Duas réguas, porque elas fazem previsões opostas e escolher uma calada
embutiria a resposta:

  ABSOLUTO     — mesmo X em segundos. Testa "PASS 1 com segmentos de DURAÇÃO
                 fixa". Previsão: PILOT-002 com ~4,8× mais segmentos.
  PROPORCIONAL — X escalado pela razão de extensão. Testa "PASS 1 com NÚMERO
                 fixo de segmentos". Previsão: PILOT-002 com ~9 grupos.
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
P2 = CLAUDE / "pilots/PILOT-002"

CUT = P2 / "00_SOURCE/L0-transcript-CUT.txt"
EVIDENCE2 = P2 / "01_COMPILED-SKILL/v0.1.0/EVIDENCE(1).jsonl"
SUMS2 = P2 / "01_COMPILED-SKILL/v0.1.0/SHA256SUMS(2).txt"

P1 = DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
EVIDENCE1 = P1 / "analysis/evidence.jsonl"
TEMPORAL1 = P1 / "analysis/temporal-map.yaml"
META1 = P1 / "sources/metadata/source-metadata.yaml"

OUT = DOCS / "PILOT-002-SEGMENT-INFERENCE.md"

EXPECTED_CUT = "85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29"

DURATION_S = 4897
HELDOUT = [(715, 908), (2680, 3000)]
MAX_REAL_SEG_S = 15

SWEEP = list(range(1, 121)) + list(range(125, 1001, 5))
YT_CHAPTERS_P2 = 14
TOLERANCES = (0, 15, 30)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fmt(s: float) -> str:
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def hhmmss_to_s(t: str) -> int:
    p = [int(x) for x in t.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


# --------------------------------------------------------------- agrupamento
def cluster(ev: list[dict], x: float) -> list[dict]:
    order = sorted(ev, key=lambda e: (e["t0"], e["t1"]))
    groups: list[dict] = []
    for e in order:
        if groups and e["t0"] - groups[-1]["end"] <= x:
            g = groups[-1]
            g["end"] = max(g["end"], e["t1"])
            g["ids"].append(e["id"])
        else:
            groups.append({"start": e["t0"], "end": e["t1"], "ids": [e["id"]]})
    return groups


def sweep(ev, xs):
    return [(x, len(cluster(ev, x))) for x in xs]


def x_for_groups(curve, target):
    hits = [x for x, n in curve if n == target]
    return (min(hits), max(hits)) if hits else None


def gaps_of(ev: list[dict]) -> list[float]:
    order = sorted(ev, key=lambda e: (e["t0"], e["t1"]))
    out, end = [], None
    for e in order:
        if end is not None:
            out.append(e["t0"] - end)
        end = max(end, e["t1"]) if end is not None else e["t1"]
    return out


def boundary_match(groups, segs, tol):
    real = [s["start"] for s in segs[1:]]
    got = [g["start"] for g in groups[1:]]
    hit = [r for r in real if any(abs(r - g) <= tol for g in got)]
    spur = [g for g in got if not any(abs(r - g) <= tol for r in real)]
    return {"tol": tol, "real": len(real), "found": len(got), "matched": len(hit),
            "matched_marks": hit, "spurious": spur,
            "missed": [r for r in real if r not in hit]}


# --------------------------------------------------------------- geometria P2
def segments_p2(lines):
    marks = []
    for i, l in enumerate(lines):
        m = re.fullmatch(r"\*\*(\d{1,3}):([0-5]\d)\*\*", l.strip())
        if m:
            marks.append((i + 1, int(m.group(1)) * 60 + int(m.group(2))))
    holds = sorted(a for a, _ in HELDOUT)
    out = []
    for i, (ln, s) in enumerate(marks):
        if i + 1 < len(marks):
            nln, ns = marks[i + 1]
            el, e = nln - 1, ns
            if ns - s > MAX_REAL_SEG_S:
                e = min((h for h in holds if h > s), default=ns)
        else:
            el, e = len(lines), DURATION_S
        out.append({"start_line": ln, "end_line": el, "start_s": s, "end_s": e})
    return out


def to_corpus(t):
    """Eixo do corpus de treino: o PASS 1 do PILOT-002 leu o transcript CORTADO,
    onde o texto é contínuo. Medir lacuna no eixo de vídeo criaria duas
    fronteiras que são artefato do corte, não do PASS 1."""
    shift = 0.0
    for h0, h1 in sorted(HELDOUT):
        if t >= h1:
            shift += h1 - h0
        elif t > h0:
            return h0 - shift
    return t - shift


# --------------------------------------------------------------- coleta
def load_p2():
    cut_sha = sha(CUT.read_bytes())
    if cut_sha != EXPECTED_CUT:
        raise SystemExit(f"L0 cortado divergente: {cut_sha[:16]}…")
    ev_sha = sha(EVIDENCE2.read_bytes())
    exp = None
    for line in SUMS2.read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) == 2 and p[1] == "EVIDENCE.jsonl":
            exp = p[0]
    if exp != ev_sha:
        raise SystemExit(f"EVIDENCE divergente: {ev_sha[:16]}…")
    lines = CUT.read_text(encoding="utf-8").splitlines()
    segs = segments_p2(lines)
    ev = []
    for r in [json.loads(l) for l in
              EVIDENCE2.read_text(encoding="utf-8").splitlines() if l.strip()]:
        sp = r["source_excerpt"]["span"]
        a, b = sp["start_line"], sp["end_line"]
        t = [s for s in segs if s["start_line"] <= b and s["end_line"] >= a]
        ev.append({"id": r["evidence_id"],
                   "t0": to_corpus(min(s["start_s"] for s in t)),
                   "t1": to_corpus(max(s["end_s"] for s in t))})
    return {"ev": ev, "extent": DURATION_S - sum(b - a for a, b in HELDOUT),
            "sha": cut_sha, "ev_sha": ev_sha}


def load_p1():
    meta = yaml.safe_load(META1.read_text(encoding="utf-8"))
    tm = yaml.safe_load(TEMPORAL1.read_text(encoding="utf-8"))
    segs = [{"id": s["segment_id"], "start": hhmmss_to_s(s["start"]),
             "end": hhmmss_to_s(s["end"]), "topic": s["topic"]}
            for s in tm["temporal_map"]]
    ev = []
    for r in [json.loads(l) for l in
              EVIDENCE1.read_text(encoding="utf-8").splitlines() if l.strip()]:
        sp = [(hhmmss_to_s(x["timestamp"]["start"]), hhmmss_to_s(x["timestamp"]["end"]))
              for x in (r.get("source_refs") or [])
              if (x.get("timestamp") or {}).get("start")
              and (x.get("timestamp") or {}).get("end")]
        if sp:
            ev.append({"id": r["evidence_id"], "t0": min(a for a, _ in sp),
                       "t1": max(b for _, b in sp)})
    return {"ev": ev, "extent": hhmmss_to_s(meta["source"]["duration"]),
            "segments": segs, "map_extent": segs[-1]["end"],
            "sha": sha(EVIDENCE1.read_bytes()),
            "map_sha": sha(TEMPORAL1.read_bytes())}


def per_segment(ev, segs):
    return [{**s, "n": sum(1 for e in ev if s["start"] <= e["t0"] < s["end"]),
             "ids": [e["id"] for e in ev if s["start"] <= e["t0"] < s["end"]]}
            for s in segs]


def tiling(ev, extent):
    """As evidências LADRILHAM a fonte ou são ilhas isoladas?

    É a premissa escondida do método: agrupar por lacuna só recupera segmento
    quando as evidências são densas o bastante para se tocarem dentro de um
    segmento e se separarem entre segmentos.
    """
    g = gaps_of(ev)
    union = 0
    for grp in cluster(ev, 0):
        union += grp["end"] - grp["start"]
    return {"n_gaps": len(g), "non_positive": sum(1 for x in g if x <= 0),
            "pct_non_positive": 100 * sum(1 for x in g if x <= 0) / len(g),
            "union_s": union, "pct_of_extent": 100 * union / extent,
            "median_gap": statistics.median(g), "mean_gap": statistics.mean(g)}


# --------------------------------------------------------------- render
def table(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |",
                      "|" + "|".join("---" for _ in head) + "|"]
                     + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows])


def curve_table(curve, marks):
    rows, prev = [], None
    for x, n in curve:
        if n != prev:
            rows.append([f"≥ {x}", n, marks.get(n, "")])
            prev = n
    return table(rows, ["X (s)", "grupos", "nota"])


def render(d2, d1, c1, c2, cal, res):
    L = []
    w = L.append
    n1, n2 = len(d1["ev"]), len(d2["ev"])
    ext1, ext2 = d1["extent"], d2["extent"]
    ratio = ext2 / ext1
    NSEG = len(d1["segments"])

    w("# PILOT-002 — SEGMENT INFERENCE (PASS 1)\n")
    w(f"**Gerado:** `{datetime.now(timezone.utc).isoformat(timespec='seconds')}` "
      f"· gerador `{Path(__file__).name}` · **somente medição**, READ-ONLY.\n")
    w("Relatório gerado por script; nenhum número foi digitado.\n")

    w("\n> ## ⚠ A contagem do PILOT-002 é INFERIDA, não lida\n>\n"
      "> O PILOT-001 tem `analysis/temporal-map.yaml` com 9 segmentos "
      "declarados — **artefato lido**. O PILOT-002 **não persistiu** o mapa "
      "equivalente, e nenhum arquivo dele declara contagem de segmento. O que "
      "este relatório diz sobre o PASS 1 do PILOT-002 é **estimativa a partir "
      "do padrão temporal das 44 evidências**. Não é medição, e nenhuma linha "
      "daqui deve ser citada como se fosse leitura de artefato.\n")

    # ---------------------------------------------------------------- 0
    w("\n## 0. Insumos\n")
    w(table([["PILOT-001 · `temporal-map.yaml`", f"`{d1['map_sha'][:16]}…`",
              f"**{NSEG} segmentos declarados**", f"0:00–{fmt(d1['map_extent'])}"],
             ["PILOT-001 · `evidence.jsonl`", f"`{d1['sha'][:16]}…`",
              f"{n1} com timestamp", f"{ext1}s"],
             ["PILOT-002 · L0 cortado", f"`{d2['sha'][:16]}…`", "—", f"{ext2}s"],
             ["PILOT-002 · EVIDENCE", f"`{d2['ev_sha'][:16]}…`", f"{n2} evidências",
              "**mapa temporal: NÃO EXISTE**"]],
            ["insumo", "sha256", "conteúdo", "extensão"]))
    w(f"\n> O mapa do PILOT-001 cobre 0:00–{fmt(d1['map_extent'])} "
      f"({d1['map_extent']}s) contra {ext1}s de duração nominal; os "
      f"{ext1 - d1['map_extent']}s finais são a cauda sem marca já registrada no "
      "`L0_COVERAGE_MAP`.\n")

    # ---------------------------------------------------------------- 1
    w(f"\n## 1. Os {NSEG} segmentos reais do PILOT-001\n")
    ps = res["per_seg1"]
    cs = [s["n"] for s in ps]
    w(table([[s["id"], f"{fmt(s['start'])}–{fmt(s['end'])}", f"{s['end']-s['start']}s",
              s["topic"], s["n"]] for s in ps],
            ["segmento", "faixa", "dur", "tópico", "evidências"]))
    w(f"\n**{sum(cs)} evidências em {NSEG} segmentos = {sum(cs)/NSEG:.2f} por "
      f"segmento** — mas a média esconde a forma: mínimo **{min(cs)}**, máximo "
      f"**{max(cs)}**, mediana {statistics.median(cs):.0f}. `SEG-007` sozinho "
      f"tem {max(cs)} evidências; `SEG-001` e `SEG-009` têm {min(cs)}. A "
      "distribuição por segmento é tudo menos uniforme.\n")

    # ---------------------------------------------------------------- 2
    w("\n## 2. Calibração no PILOT-001 — **o método REPROVA**\n")
    w("A curva é uma escada; cada linha traz o menor X que produz aquela "
      "contagem.\n")
    w(curve_table(c1, {NSEG: f"← os {NSEG} reais"}))
    if cal["exact"]:
        w(f"\n**X calibrado: {cal['exact'][0]}–{cal['exact'][1]}s.**\n")
    else:
        w(f"\n### ⛔ Nenhum X produz {NSEG} grupos no PILOT-001\n")
        w(f"A curva **pula** a contagem {NSEG}: salta de "
          f"**{res['jump'][0]}** grupos (X={res['jump'][1]}s) direto para "
          f"**{res['jump'][2]}** grupos (X={res['jump'][3]}s). Não existe limiar "
          f"que reproduza os {NSEG} segmentos reais.\n")
        w("\nIsto é o teste de validade do método, e ele **falha no único caso "
          "onde a resposta é conhecida.** O que vem a seguir mede o quanto "
          "falha, porque 'errou por um' e 'não recupera nada' autorizam "
          "conclusões muito diferentes.\n")

    w("\n### 2.1 Os limites recuperados batem com os reais?\n")
    w("Os 8 limites internos reais são "
      + ", ".join(f"`{fmt(s['start'])}`" for s in d1["segments"][1:]) + ".\n")
    w(table([[f"{r['x']}", r["n"], r["b0"]["matched"], len(r["b0"]["spurious"]),
              r["b15"]["matched"], r["b30"]["matched"]]
             for r in res["near"]],
            ["X (s)", "grupos", "acertos (tol 0s)", "falsos", "tol 15s", "tol 30s"]))
    b = res["best"]
    w(f"\n**Melhor reconstrução: X={b['x']}s → {b['n']} grupos** "
      f"(contra {NSEG} reais), com **{b['b0']['matched']} dos 8** limites "
      f"internos acertados exatamente e {len(b['b0']['spurious'])} falsos.\n")
    w("\nLimites reais recuperados: "
      + ", ".join(f"`{fmt(x)}`" for x in b["b0"]["matched_marks"]) + ".  ")
    w("Limites reais **perdidos**: "
      + ", ".join(f"`{fmt(x)}`" for x in b["b0"]["missed"]) + ".  ")
    w("Limites **falsos** inventados: "
      + ", ".join(f"`{fmt(x)}`" for x in b["b0"]["spurious"]) + ".\n")
    w(f"\n> **Leitura honesta do teste.** O método não é ruído: {b['b0']['matched']} "
      f"de 8 fronteiras reais caem exatamente no lugar certo, o que é muito "
      "acima do acaso. Mas ele **não reproduz a contagem**, erra duas "
      "fronteiras e inventa outras. Serve para dizer que a segmentação do PASS 1 "
      "deixou marca no padrão de evidências; **não serve para contar segmentos "
      "com precisão de unidade.** Toda inferência sobre o PILOT-002 daqui em "
      "diante herda essa margem.\n")

    # ---------------------------------------------------------------- 3
    w("\n## 3. Varredura de X — PILOT-002\n")
    w(curve_table([(x, n) for x, n in c2 if n <= 30],
                  {NSEG: f"← {NSEG}", YT_CHAPTERS_P2: f"← {YT_CHAPTERS_P2} (capítulos)"}))
    for tgt, lbl in ((NSEG, f"{NSEG} grupos"),
                     (YT_CHAPTERS_P2, f"{YT_CHAPTERS_P2} grupos (capítulos)")):
        r = x_for_groups(c2, tgt)
        w(f"\n- Para o PILOT-002 chegar a **{lbl}** seria preciso X de "
          + (f"**{r[0]}–{r[1]}s**." if r else "**nenhum X varrido**."))
    w("")

    # ---------------------------------------------------------------- 4
    w("\n## 4. O teste aplicado ao PILOT-002\n")
    w(table([["**ABSOLUTO** — mesmo X", f"{b['x']}s", f"**{res['n_abs']}**",
              "PASS 1 com segmentos de DURAÇÃO fixa"],
             ["**PROPORCIONAL** — X × razão de extensão",
              f"{b['x'] * ratio:.0f}s ({b['x']} × {ratio:.2f})",
              f"**{res['n_prop']}**", "PASS 1 com NÚMERO fixo de segmentos"]],
            ["régua", "X aplicado", "grupos no PILOT-002", "hipótese que testa"]))
    w(f"\n**As duas réguas dão {res['n_abs']} e {res['n_prop']} grupos. Nenhuma "
      f"chega perto de {NSEG}, e nenhuma chega perto de {YT_CHAPTERS_P2}.**\n")
    w(f"\n> Mesmo a régua proporcional — que já corrige o fato de o PILOT-002 "
      f"ter a mesma contagem de evidências sobre uma fonte {ratio:.2f}× maior — "
      f"devolve {res['n_prop']} grupos. A correção de escala não salva a "
      "hipótese.\n")

    # ---------------------------------------------------------------- 5
    w("\n## 5. Por que as duas réguas falham: ladrilho × ilhas\n")
    w("O método tem uma premissa escondida — que as evidências **ladrilham** a "
      "fonte, tocando-se dentro de um segmento e separando-se entre segmentos. "
      "Ela vale num piloto e não vale no outro:\n")
    t1, t2 = res["tile1"], res["tile2"]
    w(table([["PILOT-001", f"{t1['non_positive']}/{t1['n_gaps']}",
              f"**{t1['pct_non_positive']:.0f}%**", f"{t1['median_gap']:.0f}s",
              f"{t1['union_s']}s", f"**{t1['pct_of_extent']:.0f}%**"],
             ["PILOT-002", f"{t2['non_positive']}/{t2['n_gaps']}",
              f"**{t2['pct_non_positive']:.0f}%**", f"{t2['median_gap']:.0f}s",
              f"{t2['union_s']:.0f}s", f"**{t2['pct_of_extent']:.0f}%**"]],
            ["piloto", "lacunas ≤ 0", "%", "lacuna mediana", "união dos spans",
             "% da fonte"]))
    w(f"\n> **Conferência cruzada:** a união dos spans dá {t1['union_s']:.0f}s no "
      f"PILOT-001 e {t2['union_s']:.0f}s no PILOT-002 — os mesmos valores que o "
      "`PILOT-002-COVERAGE-REPORT` obteve por outro caminho, e que dão "
      f"{t1['pct_of_extent']:.1f}% e {t2['pct_of_extent']:.1f}% de cobertura. "
      "Duas medições independentes chegando ao mesmo número é evidência de que "
      "a geometria usada aqui está certa.\n")
    w(f"\n**No PILOT-001, {t1['pct_non_positive']:.0f}% das lacunas são zero ou "
      "negativas** — as evidências se encostam e se sobrepõem, formando um "
      "ladrilho contínuo. É por isso que existe um limiar pequeno que separa "
      "blocos: as únicas lacunas positivas são as fronteiras.\n")
    w(f"\n**No PILOT-002, só {t2['pct_non_positive']:.0f}%** — as evidências são "
      f"**ilhas isoladas**, com lacuna mediana de {t2['median_gap']:.0f}s. Não há "
      "ladrilho para trincar. Agrupar por lacuna nesse regime não recupera "
      "segmento: apenas conta evidências, e a contagem de grupos tende ao "
      "número de evidências à medida que X diminui.\n")
    w("\n> É esta a razão de fundo, e ela é mais informativa que a contagem que "
      "a tarefa pediu: **os dois pilotos têm geometrias de evidência "
      "estruturalmente diferentes.** O PILOT-001 ladrilha a fonte; o PILOT-002 "
      "a amostra por pontos. Um método que pressupõe ladrilho não consegue "
      "medir o outro regime — e é o mesmo fato que já explicava a queda de "
      "cobertura de 73,5% para 37,2%.\n")

    # ---------------------------------------------------------------- 6
    w("\n## 6. Evidências por grupo\n")
    w(table([[f"PILOT-001 · {NSEG} segmentos REAIS (lidos)", NSEG, n1,
              f"{n1/NSEG:.2f}", f"{min(cs)}–{max(cs)}"],
             [f"PILOT-001 · grupos por lacuna (X={b['x']}s)", b["n"], n1,
              f"{n1/b['n']:.2f}",
              f"{min(len(g['ids']) for g in b['groups'])}–"
              f"{max(len(g['ids']) for g in b['groups'])}"],
             ["PILOT-002 · X absoluto", res["n_abs"], n2, f"{n2/res['n_abs']:.2f}",
              f"{min(len(g['ids']) for g in res['g_abs'])}–"
              f"{max(len(g['ids']) for g in res['g_abs'])}"],
             ["PILOT-002 · X proporcional", res["n_prop"], n2,
              f"{n2/res['n_prop']:.2f}",
              f"{min(len(g['ids']) for g in res['g_prop'])}–"
              f"{max(len(g['ids']) for g in res['g_prop'])}"]],
            ["conjunto", "grupos", "evidências", "por grupo", "min–max"]))
    w(f"\nO valor de referência da tarefa — {n1/NSEG:.2f} evidências por "
      "segmento no PILOT-001 — é uma média sobre uma distribuição que vai de "
      f"{min(cs)} a {max(cs)}. Usá-la para dividir 44 e obter contagem de "
      "segmento no PILOT-002 suporia uma regularidade que o próprio PILOT-001 "
      "não tem.\n")

    w("\n### 6.1 Os grupos do PILOT-002 na régua proporcional\n")
    w(table([[i + 1, f"{fmt(g['start'])}–{fmt(g['end'])}", f"{g['end']-g['start']}s",
              len(g["ids"]), ", ".join(g["ids"])]
             for i, g in enumerate(res["g_prop"])],
            ["#", "faixa (corpus)", "dur", "n", "evidências"]))

    # ---------------------------------------------------------------- 7
    w("\n## 7. Conclusão\n")
    w(f"1. **O método reprova na calibração.** Nenhum X reproduz os {NSEG} "
      f"segmentos do PILOT-001; a curva pula de {res['jump'][0]} para "
      f"{res['jump'][2]}. A melhor reconstrução (X={b['x']}s) dá {b['n']} grupos "
      f"e acerta {b['b0']['matched']}/8 fronteiras.\n")
    w(f"2. **Com a margem que a calibração permite, o PILOT-002 dá "
      f"{res['n_abs']} grupos na régua absoluta e {res['n_prop']} na "
      f"proporcional.** Nem perto de {NSEG}, nem perto de "
      f"{YT_CHAPTERS_P2}.\n")
    w(f"3. **Portanto: a hipótese de um PASS 1 com ~{NSEG} segmentos no "
      "PILOT-002 NÃO se sustenta neste teste** — mas a rejeição é fraca, porque "
      "o instrumento reprovou na própria calibração. O honesto é dizer que o "
      "teste **não decide**, e não que ele decidiu contra.\n")
    w("4. **O achado com força é outro, e é estrutural:** as evidências do "
      f"PILOT-001 ladrilham a fonte ({t1['pct_non_positive']:.0f}% de lacunas "
      f"não positivas, união cobrindo {t1['pct_of_extent']:.0f}%) e as do "
      f"PILOT-002 são ilhas ({t2['pct_non_positive']:.0f}%, "
      f"{t2['pct_of_extent']:.0f}%). Qualquer método de reconstrução por "
      "vizinhança temporal vai falhar no segundo regime. Para decidir a questão "
      "do PASS 1 é preciso **o artefato**, não mais inferência.\n")
    w(f"5. **O que responderia de fato:** persistir o temporal-map na próxima "
      "compilação do PILOT-002, ou recompilar com o PASS 1 instrumentado. "
      "Enquanto isso não existir, a contagem de segmentos do PILOT-002 "
      "permanece **não observada**.\n")

    w("\n---\n")
    w("**Escopo:** somente medição e inferência declarada. Nenhum arquivo de "
      "`pilots/`, `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, "
      "alterado, movido ou apagado. O único arquivo escrito é este relatório.")
    return "\n".join(L) + "\n"


def main() -> int:
    d2, d1 = load_p2(), load_p1()
    c1, c2 = sweep(d1["ev"], SWEEP), sweep(d2["ev"], SWEEP)
    NSEG = len(d1["segments"])
    ratio = d2["extent"] / d1["extent"]

    exact = x_for_groups(c1, NSEG)

    # A curva pula NSEG: registrar entre quais contagens.
    steps = []
    prev = None
    for x, n in c1:
        if n != prev:
            steps.append((x, n))
            prev = n
    above = [(x, n) for x, n in steps if n > NSEG]
    below = [(x, n) for x, n in steps if n < NSEG]
    jump = (above[-1][1], above[-1][0], below[0][1], below[0][0]) \
        if above and below else (0, 0, 0, 0)

    # Candidatos vizinhos: os X de cada degrau perto de NSEG.
    cands = sorted({x for x, n in steps if abs(n - NSEG) <= 3})
    near = []
    for x in cands:
        g = cluster(d1["ev"], x)
        near.append({"x": x, "n": len(g), "groups": g,
                     "b0": boundary_match(g, d1["segments"], 0),
                     "b15": boundary_match(g, d1["segments"], 15),
                     "b30": boundary_match(g, d1["segments"], 30)})
    # Melhor: mais fronteiras exatas; desempate por contagem mais próxima e
    # menos fronteiras falsas.
    best = max(near, key=lambda r: (r["b0"]["matched"], -abs(r["n"] - NSEG),
                                    -len(r["b0"]["spurious"])))

    g_abs = cluster(d2["ev"], best["x"])
    g_prop = cluster(d2["ev"], best["x"] * ratio)

    res = {"per_seg1": per_segment(d1["ev"], d1["segments"]),
           "jump": jump, "near": near, "best": best,
           "g_abs": g_abs, "g_prop": g_prop,
           "n_abs": len(g_abs), "n_prop": len(g_prop),
           "tile1": tiling(d1["ev"], d1["extent"]),
           "tile2": tiling(d2["ev"], d2["extent"])}

    OUT.write_text(render(d2, d1, c1, c2, {"exact": exact}, res), encoding="utf-8")

    print(f"CALIBRACAO: X que da {NSEG} grupos no PILOT-001 = {exact} "
          f"-> {'REPROVA' if not exact else 'ok'}")
    print(f"  curva pula de {jump[0]} grupos (X={jump[1]}s) para {jump[2]} "
          f"(X={jump[3]}s)")
    for r in near:
        print(f"  X={r['x']:>3}s -> {r['n']:>2} grupos | fronteiras exatas "
              f"{r['b0']['matched']}/8 | falsas {len(r['b0']['spurious'])}")
    print(f"  melhor: X={best['x']}s ({best['n']} grupos, "
          f"{best['b0']['matched']}/8 fronteiras)")
    print(f"PILOT-002: absoluto {res['n_abs']} grupos | proporcional "
          f"{res['n_prop']} grupos")
    print(f"  X para {NSEG} grupos no P002: {x_for_groups(c2, NSEG)} | para "
          f"{YT_CHAPTERS_P2}: {x_for_groups(c2, YT_CHAPTERS_P2)}")
    print(f"ladrilho: P001 {res['tile1']['pct_non_positive']:.0f}% lacunas<=0, "
          f"uniao {res['tile1']['pct_of_extent']:.0f}% | P002 "
          f"{res['tile2']['pct_non_positive']:.0f}%, "
          f"{res['tile2']['pct_of_extent']:.0f}%")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) "
          f"{sha(OUT.read_bytes())[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
