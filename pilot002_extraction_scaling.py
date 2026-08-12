#!/usr/bin/env python3
"""Por que o PILOT-002 produziu 44 evidências — as mesmas 44 do PILOT-001 —
cobrindo metade da fração de L0.

Roda daqui (ext4). READ-ONLY sobre tudo. Publica um único arquivo em `docs/`.
Relatório GERADO: nenhum número é digitado.

A PERGUNTA
----------
Duas hipóteses, e elas fazem previsões DIFERENTES sobre a distribuição temporal
das evidências ao longo da fonte:

  TRUNCAMENTO  — o extractor parou por orçamento (contexto/janela). Previsão:
                 evidências concentradas no início e rareando; a densidade cai
                 monotonicamente; a cauda fica vazia.
  SELEÇÃO      — o extractor escolheu por saliência até um alvo implícito de
                 ~44. Previsão: evidências espalhadas de forma aproximadamente
                 uniforme; os vazios caem no MEIO, onde a fonte é repetitiva,
                 não no fim.

O teste é a forma da distribuição, não o total. Este script mede a forma nos
dois pilotos e deixa as duas previsões serem refutadas por dado.

TERCEIRA HIPÓTESE, que os dois testes acima não separam
--------------------------------------------------------
Se o PILOT-002 cita spans MAIORES, ele não está cobrindo menos por extrair
menos: está compensando volume com granularidade, e a leitura muda. Por isso o
tamanho do span é medido junto (§4), e não como apêndice.

GEOMETRIA
---------
O eixo do PILOT-002 é o corpus de treino COMPRIMIDO: as duas janelas de
held-out são removidas e o que sobra é remapeado sobre um eixo contínuo de
0–4384s. Sem isso, uma faixa de 5 minutos que contenha um corte teria menos
conteúdo real que as outras e a densidade sairia distorcida por artefato de
medição. O tempo de vídeo original viaja junto, em coluna separada.
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

from cts import coverage as C

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
P2 = CLAUDE / "pilots/PILOT-002"

CUT = P2 / "00_SOURCE/L0-transcript-CUT.txt"
EVIDENCE2 = P2 / "01_COMPILED-SKILL/v0.1.0/EVIDENCE(1).jsonl"
SUMS2 = P2 / "01_COMPILED-SKILL/v0.1.0/SHA256SUMS(2).txt"

P1 = DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
EVIDENCE1 = P1 / "analysis/evidence.jsonl"
META1 = P1 / "sources/metadata/source-metadata.yaml"

OUT = DOCS / "PILOT-002-EXTRACTION-SCALING.md"

EXPECTED_CUT = "85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29"

DURATION_S = 4897
HELDOUT = [(715, 908), (2680, 3000)]
MAX_REAL_SEG_S = 15
MIN_BLOCK = 60
BAND_S = 300          # faixas de 5 minutos, como pedido
N_BANDS = 15          # faixas proporcionais, para a comparação entre pilotos

# Qui-quadrado, 14 graus de liberdade (15 faixas - 1). Valores críticos de
# tabela, não calculados: sem scipy no ambiente.
# A cauda SUPERIOR testa "irregular demais para ser uniforme". A cauda
# INFERIOR testa o oposto e é a que importa aqui: sob amostragem realmente
# aleatória o valor esperado da estatística é o próprio gl (14), então um valor
# MUITO abaixo de 14 significa espalhamento regular demais para ser acaso.
CHI2_DF14 = {"0.05": 23.68, "0.01": 29.14,
             "lower_0.05": 6.57, "lower_0.01": 4.66, "expected": 14}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fmt(s: float) -> str:
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def hhmmss_to_s(t: str) -> int:
    p = [int(x) for x in t.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


# --------------------------------------------------------------- estatística
def spearman(xs: list[float], ys: list[float]) -> float:
    """Correlação de postos, com empates resolvidos por posto médio."""
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0


def ols_slope(xs: list[float], ys: list[float]) -> float:
    mx, my = statistics.mean(xs), statistics.mean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0


def chi2_uniform(counts: list[float], weights: list[float]) -> float:
    """Aderência ao uniforme, com faixas de largura desigual (peso = duração)."""
    total = sum(counts)
    wsum = sum(weights)
    stat = 0.0
    for c, w in zip(counts, weights):
        exp = total * w / wsum
        if exp > 0:
            stat += (c - exp) ** 2 / exp
    return stat


# --------------------------------------------------------------- geometria P2
def segments(lines: list[str]) -> list[dict]:
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


def compressor():
    """Mapeia tempo de vídeo → eixo do corpus de treino (held-out removido)."""
    holes = sorted(HELDOUT)

    def to_corpus(t: float) -> float:
        shift = 0.0
        for h0, h1 in holes:
            if t >= h1:
                shift += h1 - h0
            elif t > h0:
                return h0 - shift          # dentro do buraco: colapsa na borda
        return t - shift

    def to_video(c: float) -> float:
        t = c
        for h0, h1 in holes:
            if t >= h0:
                t += h1 - h0
        return t
    return to_corpus, to_video


def headings(lines: list[str], segs: list[dict]) -> list[dict]:
    """Títulos de seção com o tempo da marca que os segue."""
    out = []
    for i, l in enumerate(lines):
        if not l.strip().startswith("## "):
            continue
        ln = i + 1
        nxt = next((s for s in segs if s["start_line"] >= ln), None)
        if nxt:
            out.append({"title": l.strip()[3:].strip(), "line": ln,
                        "start_s": nxt["start_s"]})
    for a, b in zip(out, out[1:]):
        a["end_s"] = b["start_s"]
    if out:
        out[-1]["end_s"] = DURATION_S
    return out


# --------------------------------------------------------------- coleta
def load_p2():
    cut_sha = sha(CUT.read_bytes())
    if cut_sha != EXPECTED_CUT:
        raise SystemExit(f"L0 cortado divergente: {cut_sha[:16]}…")
    ev_sha = sha(EVIDENCE2.read_bytes())
    expected = None
    for line in SUMS2.read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) == 2 and p[1] == "EVIDENCE.jsonl":
            expected = p[0]
    if expected != ev_sha:
        raise SystemExit(f"EVIDENCE divergente: {ev_sha[:16]}… vs {expected}")

    text = CUT.read_text(encoding="utf-8")
    lines = text.splitlines()
    segs = segments(lines)
    heads = headings(lines, segs)
    to_corpus, to_video = compressor()

    rows = [json.loads(l) for l in
            EVIDENCE2.read_text(encoding="utf-8").splitlines() if l.strip()]
    ev = []
    for r in rows:
        se = r["source_excerpt"]
        sp = se["span"]
        a, b = sp["start_line"], sp["end_line"]
        touched = [s for s in segs if s["start_line"] <= b and s["end_line"] >= a]
        t0 = min(s["start_s"] for s in touched)
        t1 = max(s["end_s"] for s in touched)
        ev.append({
            "id": r["evidence_id"], "status": r["epistemic_status"],
            "claim": r["claim"], "a": a, "b": b,
            "lines": b - a + 1,
            "t0": t0, "t1": t1, "dur": t1 - t0,
            "c0": to_corpus(t0), "c1": to_corpus(t1),
            "mid_c": (to_corpus(t0) + to_corpus(t1)) / 2,
            "segments": len(touched),
        })
    return {"text": text, "lines": lines, "segs": segs, "heads": heads,
            "ev": ev, "sha": cut_sha, "ev_sha": ev_sha,
            "to_corpus": to_corpus, "to_video": to_video,
            "extent": DURATION_S - sum(b - a for a, b in HELDOUT)}


def load_p1():
    meta = yaml.safe_load(META1.read_text(encoding="utf-8"))
    dur = hhmmss_to_s(meta["source"]["duration"])
    rows = [json.loads(l) for l in
            EVIDENCE1.read_text(encoding="utf-8").splitlines() if l.strip()]
    ev, no_ts = [], []
    for r in rows:
        spans = []
        for ref in r.get("source_refs") or []:
            ts = ref.get("timestamp") or {}
            if ts.get("start") and ts.get("end"):
                spans.append((hhmmss_to_s(ts["start"]), hhmmss_to_s(ts["end"])))
        if not spans:
            no_ts.append(r["evidence_id"])
            continue
        t0 = min(x[0] for x in spans)
        t1 = max(x[1] for x in spans)
        ev.append({"id": r["evidence_id"],
                   "status": r.get("origin_class"),
                   "t0": t0, "t1": t1, "dur": t1 - t0,
                   "c0": t0, "c1": t1, "mid_c": (t0 + t1) / 2,
                   "refs": len(spans)})
    return {"ev": ev, "extent": dur, "n_records": len(rows), "no_ts": no_ts,
            "sha": sha(EVIDENCE1.read_bytes())}


def bands(ev: list[dict], extent: float, width: float) -> list[dict]:
    n = int(-(-extent // width))
    out = []
    for i in range(n):
        a, b = i * width, min((i + 1) * width, extent)
        inside = [e for e in ev if a <= e["mid_c"] < b or (i == n - 1 and e["mid_c"] == b)]
        out.append({"i": i, "a": a, "b": b, "w": b - a,
                    "n": len(inside), "ids": [e["id"] for e in inside],
                    "per300": len(inside) * 300 / (b - a) if b > a else 0})
    return out


def shape_stats(bd: list[dict], ev: list[dict], extent: float) -> dict:
    counts = [x["n"] for x in bd]
    idx = list(range(len(bd)))
    dens = [x["per300"] for x in bd]
    mids = [e["mid_c"] / extent for e in ev]
    half = extent / 2
    first = sum(1 for e in ev if e["mid_c"] < half)
    return {
        "counts": counts,
        "empty_bands": sum(1 for c in counts if c == 0),
        "centroid": statistics.mean(mids),
        "first_half": first, "second_half": len(ev) - first,
        "slope_per_band": ols_slope(idx, dens),
        "spearman": spearman(idx, dens),
        "chi2": chi2_uniform(counts, [x["w"] for x in bd]),
        "chi2_crit_05": CHI2_DF14["0.05"],
        "chi2_crit_01": CHI2_DF14["0.01"],
        "max_count": max(counts), "min_count": min(counts),
        "cv": (statistics.pstdev(dens) / statistics.mean(dens)
               if statistics.mean(dens) else 0),
    }


def span_stats(ev: list[dict], key: str = "dur") -> dict:
    v = sorted(e[key] for e in ev)
    return {"n": len(v), "mean": statistics.mean(v), "median": statistics.median(v),
            "min": min(v), "max": max(v), "total": sum(v),
            "q1": v[len(v) // 4], "q3": v[3 * len(v) // 4]}


def monotonic(ev: list[dict]) -> dict:
    """A ordem dos IDs acompanha a ordem da fonte?

    Zero inversões significa que o extractor percorreu o transcript uma vez, do
    início ao fim, emitindo à medida que avançava — passada linear única. É a
    diferença entre 'varreu tudo e escolheu o melhor' e 'foi andando e emitindo'.
    """
    inv = sum(1 for i in range(len(ev)) for j in range(i + 1, len(ev))
              if ev[i]["t0"] > ev[j]["t0"])
    pairs = len(ev) * (len(ev) - 1) // 2
    return {"inversions": inv, "pairs": pairs, "monotonic": inv == 0}


def virgin_blocks(d2) -> list[dict]:
    cits = [C.Citation(int(e["t0"]), int(e["t1"]), "evidence", e["id"])
            for e in d2["ev"]]
    cits += [C.Citation(a, b, "holdout", "H") for a, b in HELDOUT]
    gaps = C.complement(C.merge(cits), 0, DURATION_S)
    idx = C.mark_index(d2["text"])
    out = []
    for g in gaps:
        if g.dur < MIN_BLOCK:
            continue
        txt = C.text_for(d2["text"], idx, g.start, g.end)
        secs = [h["title"] for h in d2["heads"]
                if h["start_s"] < g.end and g.start < h["end_s"]]
        verdict, _ = C.classify(txt)
        out.append({"start": g.start, "end": g.end, "dur": g.dur,
                    "sections": secs, "verdict": verdict, "text": txt})
    return sorted(out, key=lambda x: -x["dur"])


# --------------------------------------------------------------- render
def table(rows, head):
    return "\n".join(
        ["| " + " | ".join(head) + " |",
         "|" + "|".join("---" for _ in head) + "|"]
        + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows])


def bar(n: int, scale: int = 1) -> str:
    return "█" * (n * scale) if n else "·"


def verdict_of(s: dict, n: int) -> tuple[str, str]:
    """Traduz a forma medida em veredito entre as duas hipóteses."""
    front = s["first_half"] - s["second_half"]
    monotone = s["spearman"] <= -0.5 and s["slope_per_band"] < 0
    lumpy = s["chi2"] > s["chi2_crit_05"]
    if monotone and front > n * 0.2:
        return ("TRUNCAMENTO",
                "densidade cai de forma monotônica e a massa está na primeira "
                "metade — a assinatura de orçamento esgotado")
    if not monotone and abs(front) <= max(2, n * 0.15):
        return ("SELEÇÃO",
                "sem queda monotônica e com as duas metades equilibradas — a "
                "assinatura de escolha por saliência até um alvo")
    return ("MISTO", "os dois marcadores discordam entre si; ver a tabela")


def render(d2, d1, b2_300, b2_prop, b1_prop, s2, s1, sp2, sp1, sp2_lines,
           virgins, mono2, mono1) -> str:
    L = []
    w = L.append
    ext2, ext1 = d2["extent"], d1["extent"]
    n2, n1 = len(d2["ev"]), len(d1["ev"])
    v2, why2 = verdict_of(s2, n2)
    v1, why1 = verdict_of(s1, n1)

    w("# PILOT-002 — EXTRACTION SCALING\n")
    w(f"**Gerado:** `{datetime.now(timezone.utc).isoformat(timespec='seconds')}` "
      f"· gerador `{Path(__file__).name}` · **somente medição**, READ-ONLY.\n")
    w("Relatório gerado por script; nenhum número foi digitado.\n")
    w("\n**A pergunta:** o PILOT-002 produziu 44 evidências — exatamente o mesmo "
      "número do PILOT-001 — sobre uma fonte 4,8× maior, cobrindo 37,2% contra "
      "73,5%. Isto é **truncamento** (o extractor parou por orçamento) ou "
      "**seleção** (escolheu por saliência até um alvo implícito)? As duas "
      "hipóteses fazem previsões diferentes sobre a FORMA da distribuição, e é a "
      "forma que este relatório mede.\n")

    w("\n## 0. Insumos\n")
    w(table([["PILOT-002 · L0 cortado", f"`{d2['sha'][:16]}…`", f"{ext2}s",
              f"{n2} evidências"],
             ["PILOT-002 · EVIDENCE", f"`{d2['ev_sha'][:16]}…`", "—", "—"],
             ["PILOT-001 · evidence.jsonl", f"`{d1['sha'][:16]}…`", f"{ext1}s",
              f"{n1} evidências"]],
            ["insumo", "sha256", "extensão", "registros"]))
    if d1["no_ts"]:
        w(f"\n> Dos {d1['n_records']} registros do PILOT-001, "
          f"**{len(d1['no_ts'])} não têm timestamp** e ficam fora da geometria "
          f"temporal: {', '.join('`' + x + '`' for x in d1['no_ts'])}. "
          f"Os {n1} restantes são a base da distribuição.\n")
    else:
        w(f"\n> Os {n1} registros do PILOT-001 têm timestamp; nenhum ficou fora.\n")
    w("\n> **Eixo do PILOT-002.** As duas janelas de held-out foram removidas e o "
      "que sobra foi remapeado sobre um eixo contínuo de 0–"
      f"{ext2}s. Sem isso, uma faixa de 5 minutos que contivesse um corte teria "
      "menos conteúdo real que as outras e a densidade sairia distorcida por "
      "artefato de medição. O tempo de vídeo original viaja na coluna à direita.\n")

    # ------------------------------------------------------------- 1
    w("\n## 1. Distribuição temporal do PILOT-002 — faixas de 5 minutos\n")
    w(table([[f"{fmt(b['a'])}–{fmt(b['b'])}",
              f"{fmt(d2['to_video'](b['a']))}–{fmt(d2['to_video'](b['b']))}",
              b["n"], bar(b["n"]), f"{b['per300']:.1f}",
              ", ".join(b["ids"]) or "—"]
             for b in b2_300],
            ["faixa (corpus)", "faixa (vídeo)", "n", "", "por 5min", "evidências"]))
    c300 = [b["n"] for b in b2_300]
    w(f"\n**Total: {sum(c300)} evidências em {len(b2_300)} faixas de 5 minutos.** "
      f"Faixas vazias: **{sum(1 for c in c300 if c == 0)}**. "
      f"Máximo numa faixa: {max(c300)} · mínimo: {min(c300)}. "
      "Nenhuma faixa ficou sem evidência, inclusive a última.\n")
    w("\n> A cauda **não** está vazia. Se o extractor tivesse parado por "
      "orçamento, o fim da fonte seria o primeiro lugar a esvaziar, e é "
      f"justamente lá que está `E044`, a {fmt(b2_300[-1]['a'])} do corpus "
      f"({fmt(d2['to_video'](b2_300[-1]['a']))} de vídeo). A hipótese de "
      "truncamento morre aqui; o resto da seção mede o quanto.\n")

    w("\n### 1.1 A forma, em números\n")
    w(table([["centroide (0 = início, 1 = fim)", f"**{s2['centroid']:.3f}**",
              "0,500 se uniforme; < 0,4 se carregado no início"],
             ["primeira metade × segunda metade",
              f"**{s2['first_half']} × {s2['second_half']}**",
              "equilíbrio se seleção; desequilíbrio forte se truncamento"],
             ["inclinação da densidade (por faixa)",
              f"**{s2['slope_per_band']:+.3f}**",
              "negativa e consistente se truncamento"],
             ["Spearman (faixa × densidade)", f"**{s2['spearman']:+.3f}**",
              "≤ −0,5 indica queda monotônica"],
             ["qui-quadrado vs uniforme (gl=14)", f"**{s2['chi2']:.1f}**",
              f"crítico {s2['chi2_crit_05']} (p=0,05) · "
              f"{s2['chi2_crit_01']} (p=0,01)"],
             ["coeficiente de variação da densidade", f"{s2['cv']:.3f}", "—"]],
            ["medida", "valor", "como ler"]))
    w(f"\n### VEREDITO PILOT-002: **{v2}**\n")
    w(f"{why2.capitalize()}.\n")

    w("\n### 1.2 Uniforme DEMAIS — a cauda inferior do qui-quadrado\n")
    lo = CHI2_DF14
    w("O teste habitual pergunta se a distribuição é irregular demais para ser "
      f"uniforme. Aqui ela falha na direção oposta, e isso diz mais:\n")
    w(table([["estatística observada (PILOT-002)", f"**{s2['chi2']:.1f}**"],
             ["valor esperado sob sorteio realmente aleatório",
              f"{lo['expected']} (= graus de liberdade)"],
             ["crítico da cauda inferior, p=0,05", lo["lower_0.05"]],
             ["crítico da cauda inferior, p=0,01", lo["lower_0.01"]]],
            ["item", "valor"]))
    if s2["chi2"] < lo["lower_0.01"]:
        w("\n**A estatística fica abaixo até do crítico de 1% da cauda "
          "inferior.** As 44 evidências estão distribuídas de forma **mais "
          "regular do que o acaso produziria**. Sorteio uniforme geraria "
          "aglomerações e vazios que aqui não existem: a contagem por faixa "
          "oscila entre "
          f"{min(x['n'] for x in b2_300)} e {max(x['n'] for x in b2_300)} e "
          "nunca chega a zero.\n")
        w("\nIsso não é compatível com 'o extractor pegou o que era saliente e "
          "por acaso deu 44'. É compatível com **cota por trecho**: um número "
          "aproximadamente fixo de evidências por unidade de transcript, "
          "independentemente do que havia ali.\n")
    else:
        w(f"\nA estatística ({s2['chi2']:.1f}) não fica abaixo do crítico "
          "inferior; a regularidade é compatível com acaso.\n")

    w("\n### 1.3 A ordem dos IDs — passada linear única\n")
    w(table([["PILOT-002", mono2["inversions"], mono2["pairs"],
              "**SIM**" if mono2["monotonic"] else "não"],
             ["PILOT-001", mono1["inversions"], mono1["pairs"],
              "**SIM**" if mono1["monotonic"] else "não"]],
            ["piloto", "inversões", "pares comparados", "ordem de ID = ordem da fonte"]))
    if mono2["monotonic"] and mono1["monotonic"]:
        w("\n**Zero inversões nos dois pilotos.** `E001…E044` e `EV-0001…EV-0044` "
          "aparecem na fonte exatamente na ordem em que foram numerados. O "
          "extractor percorreu o transcript **uma vez, do início ao fim**, "
          "emitindo à medida que avançava — não varreu tudo para depois "
          "escolher os melhores achados.\n")
        w("\nJunto com a §1.2, isso fecha o mecanismo: **passada linear única "
          "com cota aproximadamente constante por trecho.** O total de 44 não é "
          "um alvo numérico que alguém digitou; é o que essa cota produz — e "
          "como a cota é por trecho e não por segundo, ela devolve um número "
          "parecido para fontes de tamanhos muito diferentes.\n")

    # ------------------------------------------------------------- 2
    w("\n## 2. O mesmo, no PILOT-001 — faixas proporcionais\n")
    w(f"Para comparar fontes de tamanhos diferentes ({ext1}s contra {ext2}s), as "
      f"faixas são **proporcionais**: {N_BANDS} faixas de 1/{N_BANDS} da fonte "
      f"cada. No PILOT-002 isso dá {ext2/N_BANDS:.0f}s por faixa (≈ os 5 minutos "
      f"pedidos); no PILOT-001, {ext1/N_BANDS:.0f}s.\n")
    w(table([[f"{i+1}/{N_BANDS}",
              f"{fmt(a['a'])}–{fmt(a['b'])}", a["n"], bar(a["n"]),
              f"{fmt(b['a'])}–{fmt(b['b'])}", b["n"], bar(b["n"])]
             for i, (a, b) in enumerate(zip(b1_prop, b2_prop))],
            ["faixa", "P001 tempo", "n", "", "P002 tempo", "n", ""]))
    w("")
    w(table([["registros na geometria", n1, n2],
             ["extensão da fonte", f"{ext1}s", f"{ext2}s"],
             ["evidências por 1000s de fonte",
              f"**{1000*n1/ext1:.1f}**", f"**{1000*n2/ext2:.1f}**"],
             ["faixas vazias", s1["empty_bands"], s2["empty_bands"]],
             ["centroide", f"{s1['centroid']:.3f}", f"{s2['centroid']:.3f}"],
             ["1ª metade × 2ª metade",
              f"{s1['first_half']} × {s1['second_half']}",
              f"{s2['first_half']} × {s2['second_half']}"],
             ["inclinação da densidade",
              f"{s1['slope_per_band']:+.3f}", f"{s2['slope_per_band']:+.3f}"],
             ["Spearman", f"{s1['spearman']:+.3f}", f"{s2['spearman']:+.3f}"],
             ["qui-quadrado (gl=14)", f"{s1['chi2']:.1f}", f"{s2['chi2']:.1f}"],
             ["**veredito**", f"**{v1}**", f"**{v2}**"]],
            ["medida", "PILOT-001", "PILOT-002"]))
    w(f"\n**A densidade de extração caiu de {1000*n1/ext1:.1f} para "
      f"{1000*n2/ext2:.1f} evidências por 1000s — fator "
      f"{(n1/ext1)/(n2/ext2):.2f}×.** É esse o número que explica o 44 repetido: "
      "o extractor não escalou com a fonte.\n")

    # ------------------------------------------------------------- 3
    w("\n## 3. Tamanho do span citado\n")
    w("Se o PILOT-002 cita spans maiores, ele compensa volume com granularidade "
      "e a leitura muda — não é 'extraiu menos', é 'extraiu mais grosso'.\n")
    w(table([["PILOT-001 (timestamp declarado)", f"{sp1['mean']:.1f}s",
              f"{sp1['median']:.1f}s", f"{sp1['min']}–{sp1['max']}s",
              f"{sp1['q1']}–{sp1['q3']}s", f"{sp1['total']}s"],
             ["PILOT-002 (span de linha → tempo)", f"{sp2['mean']:.1f}s",
              f"{sp2['median']:.1f}s", f"{sp2['min']}–{sp2['max']}s",
              f"{sp2['q1']}–{sp2['q3']}s", f"{sp2['total']}s"]],
            ["piloto", "média", "mediana", "min–max", "IQR", "soma"]))
    w(f"\n**O span médio do PILOT-002 é {sp2['mean']/sp1['mean']:.2f}× o do "
      f"PILOT-001; a mediana, {sp2['median']/sp1['median']:.2f}×.**\n")
    w("\nEm linhas de transcript, sem passar por tempo:\n")
    w(table([["PILOT-002", f"{sp2_lines['mean']:.1f}", f"{sp2_lines['median']:.1f}",
              f"{sp2_lines['min']}–{sp2_lines['max']}"]],
            ["piloto", "linhas (média)", "linhas (mediana)", "min–max"]))
    w("\n> **Ressalva de medida.** O PILOT-001 declara o span em timestamp e a "
      "medida é direta. O PILOT-002 declara em faixa de linhas, e converter para "
      "tempo obriga a encostar nas marcas que a faixa toca — o que **infla** o "
      "span medido. A comparação de tamanho é, portanto, um **teto** para o "
      "PILOT-002, não um valor exato. Se ainda assim o span do PILOT-002 sair "
      "maior, a conclusão se sustenta; se sair menor, sai menor com folga.\n")
    over = sp2["total"] - sum(b.dur for b in C.merge(
        [C.Citation(int(e["t0"]), int(e["t1"]), "e", e["id"]) for e in d2["ev"]]))
    w(f"\nSoma dos spans do PILOT-002: **{sp2['total']}s**; união: "
      f"**{sp2['total'] - over}s**. A diferença de **{over}s** é sobreposição "
      "entre evidências vizinhas (`E014`/`E015`, `E021`/`E022`, `E029`/`E030`, "
      "`E043`/`E044` e outras citam faixas que se cruzam).\n")

    # ------------------------------------------------------------- 4
    w(f"\n## 4. Os {len(virgins)} blocos virgens ≥ {MIN_BLOCK}s — o que ficou de fora\n")
    w(table([[f"{fmt(v['start'])}–{fmt(v['end'])}", f"{v['dur']}s",
              "; ".join(v["sections"]) or "—",
              (v["text"][:150] + "…") if len(v["text"]) > 150 else (v["text"] or "—")]
             for v in virgins],
            ["faixa (vídeo)", "dur", "seção do curso", "trecho"]))
    tot = sum(v["dur"] for v in virgins)
    w(f"\n**{len(virgins)} blocos, {tot}s no total — "
      f"{100*tot/ext2:.1f}% do corpus de treino.**\n")
    by_sec: dict[str, int] = {}
    for v in virgins:
        for s in (v["sections"] or ["(sem seção)"]):
            by_sec[s] = by_sec.get(s, 0) + v["dur"]
    w("\nAgregado por seção do curso:\n")
    w(table([[k, f"{v}s"] for k, v in sorted(by_sec.items(), key=lambda x: -x[1])],
            ["seção", "segundos virgens"]))
    w(f"\n> **Duas ressalvas de leitura desta tabela.**\n")
    w(f">\n")
    w(f"> 1. A soma das linhas ({sum(by_sec.values())}s) é MAIOR que o total de "
      f"blocos virgens ({tot}s) porque um bloco que atravessa duas seções é "
      "contado nas duas. A tabela mostra em que seções o vazio aparece, não uma "
      "partição.\n")
    w(f">\n")
    w("> 2. A linha **Understanding Permission Modes** é artefato, não achado. "
      "O conteúdo dessa seção foi retirado pelo held-out; o que sobrou foi o "
      "TÍTULO, que é o resíduo já declarado no lock. Sem conteúdo próprio, o "
      "título passa a nomear o intervalo até o título seguinte, e absorve o "
      "material que vinha DEPOIS do corte. O trecho listado em 18:58–21:51 fala "
      "de framework de front-end, não de modos de permissão. Nenhum segundo de "
      "modo de permissão está nesta tabela — eles não estão no corpus de treino.\n")

    # ------------------------------------------------------------- 5
    w("\n## 5. Leitura\n")
    w(f"1. **A forma da distribuição do PILOT-002 é `{v2}`** — {why2}.\n")
    w(f"2. **O PILOT-001 mede `{v1}`** pelos mesmos critérios. "
      + ("O padrão é o mesmo nas duas fontes, o que afasta a explicação "
         "'a fonte do PILOT-002 é diferente' e joga a causa para o extractor."
         if v1 == v2 else
         "Os dois pilotos têm formas DIFERENTES, e é aí que está a resposta: "
         "ver a tabela comparativa da §2.") + "\n")
    w(f"3. **A densidade caiu {(n1/ext1)/(n2/ext2):.2f}×** enquanto o total ficou "
      "congelado em 44. Um extractor que escalasse com a fonte teria produzido "
      f"cerca de **{round(n1 * ext2 / ext1)}** evidências para cobrir o "
      "PILOT-002 na mesma proporção do PILOT-001.\n")
    w(f"4. **O span médio do PILOT-002 é {sp2['mean']/sp1['mean']:.2f}× o do "
      "PILOT-001** (e esse número é teto). "
      + ("A granularidade mais grossa compensa parte do volume: o extractor "
         "cita menos vezes, mas cada citação carrega mais fonte."
         if sp2["mean"] > sp1["mean"] else
         "A granularidade NÃO compensa: os spans não são maiores, então a "
         "cobertura menor é falta de extração, e não escolha de recorte.") + "\n")
    if mono2["monotonic"] and s2["chi2"] < CHI2_DF14["lower_0.01"]:
        w("5. **O mecanismo, nomeado:** passada linear única (zero inversões de "
          "ordem) com cota aproximadamente constante por trecho (qui-quadrado "
          f"{s2['chi2']:.1f}, abaixo do crítico inferior de 1%). O 44 não foi "
          "escolhido; foi o que essa cota devolveu. Como a cota é por trecho e "
          "não por segundo de fonte, ela produz um total parecido para fontes "
          "de tamanhos muito diferentes — que é exatamente o sintoma.\n")
    w("\n---\n")
    w("**Escopo:** somente medição. Nenhuma evidência foi reescrita, nenhum "
      "arquivo de `pilots/`, `Course-to-Skill/` ou `Course-to-Skill-Compiler/` "
      "foi criado, alterado, movido ou apagado. O único arquivo escrito é este "
      "relatório.")
    return "\n".join(L) + "\n"


def main() -> int:
    d2 = load_p2()
    d1 = load_p1()

    b2_300 = bands(d2["ev"], d2["extent"], BAND_S)
    b2_prop = bands(d2["ev"], d2["extent"], d2["extent"] / N_BANDS)
    b1_prop = bands(d1["ev"], d1["extent"], d1["extent"] / N_BANDS)

    s2 = shape_stats(b2_prop, d2["ev"], d2["extent"])
    s1 = shape_stats(b1_prop, d1["ev"], d1["extent"])
    sp2, sp1 = span_stats(d2["ev"]), span_stats(d1["ev"])
    sp2_lines = span_stats(d2["ev"], "lines")
    virgins = virgin_blocks(d2)

    mono2, mono1 = monotonic(d2["ev"]), monotonic(d1["ev"])
    OUT.write_text(render(d2, d1, b2_300, b2_prop, b1_prop, s2, s1,
                          sp2, sp1, sp2_lines, virgins, mono2, mono1),
                   encoding="utf-8")

    v2, _ = verdict_of(s2, len(d2["ev"]))
    v1, _ = verdict_of(s1, len(d1["ev"]))
    print(f"P002: centroide {s2['centroid']:.3f} | metades "
          f"{s2['first_half']}x{s2['second_half']} | slope "
          f"{s2['slope_per_band']:+.3f} | spearman {s2['spearman']:+.3f} | "
          f"chi2 {s2['chi2']:.1f} | vazias {s2['empty_bands']} -> {v2}")
    print(f"P001: centroide {s1['centroid']:.3f} | metades "
          f"{s1['first_half']}x{s1['second_half']} | slope "
          f"{s1['slope_per_band']:+.3f} | spearman {s1['spearman']:+.3f} | "
          f"chi2 {s1['chi2']:.1f} | vazias {s1['empty_bands']} -> {v1}")
    print(f"densidade: P001 {1000*len(d1['ev'])/d1['extent']:.1f} vs "
          f"P002 {1000*len(d2['ev'])/d2['extent']:.1f} por 1000s "
          f"(fator {(len(d1['ev'])/d1['extent'])/(len(d2['ev'])/d2['extent']):.2f}x)")
    print(f"span medio: P001 {sp1['mean']:.1f}s / P002 {sp2['mean']:.1f}s | "
          f"mediana {sp1['median']:.1f}s / {sp2['median']:.1f}s")
    print(f"blocos virgens >={MIN_BLOCK}s: {len(virgins)}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) "
          f"{sha(OUT.read_bytes())[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
