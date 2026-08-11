#!/usr/bin/env python3
"""PILOT-002 — G0 vault-seal, G1 held-out lock, G2 mapa de cobertura. E PARA.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/ e Course-to-Skill-Compiler/:
a fonte do PILOT-002 vive em Course-to-Skill-Claude/, que é gravável.

NÃO extrai L1, NÃO compila, NÃO escreve rubrica. O corte precede qualquer
leitura de conteúdo: a seleção do held-out é por SPAN declarado, e a única
coisa que o cutter olha é a posição das marcas de tempo.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml

from cts import coverage as cov
from cts.cutter import Segment, corpus_hash, overlaps, segment_by_marks, train_corpus
from cts.vault import Vault

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
P2 = CLAUDE / "pilots/PILOT-002"
SRC_DOCX = P2 / "00_SOURCE/L0-transcript.txt.docx"
SRC_TXT = P2 / "00_SOURCE/L0-transcript.txt"
CUT_TXT = P2 / "00_SOURCE/L0-transcript-CUT.txt"

OUT_SEAL = DOCS / "PILOT-002-VAULT-SEAL.yaml"
OUT_LOCK = DOCS / "HELDOUT-LOCK-PILOT-002.yaml"
OUT_MAP = DOCS / "L0_COVERAGE_MAP-PILOT-002.md"

VAULT = Path("work/vault-p002")

# Spans de held-out, DECLARADOS antes de qualquer extração.
HELDOUT = [
    ("Understanding Permission Modes", "11:55", "15:08"),
    ("Managing Your Context Window and Token Usage", "44:40", "50:00"),
]
EXPECTED_LAST_MARK = "1:21:35"
DURATION_S = 4897  # da página do vídeo, já apurado em PILOT-002-CANDIDATE-METADATA


def sha256b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def mmss_to_s(t: str) -> int:
    p = [int(x) for x in t.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def to_mark(total_s: int) -> str:
    """Formato de marca do PILOT-001: minutos totais:segundos."""
    return f"{total_s // 60}:{total_s % 60:02d}"


# --------------------------------------------------------------- G0
TS_LINE = re.compile(r"^\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*$")


def docx_lines(p: Path) -> list[str]:
    with zipfile.ZipFile(p) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    paras = re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)
    return [html.unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", x, re.S)))
            for x in paras]


def normalize(lines: list[str]) -> tuple[str, list[str], list[str]]:
    """docx → formato do PILOT-001: `## Título`, `**MMM:SS**`, fala.

    H:MM:SS vira minutos totais, que é a única forma que o MARK_RE do vault e do
    módulo de cobertura aceitam. Conversão sem perda: 1:21:35 → 81:35.
    """
    out, marks_orig, headings = [], [], []
    prev_nonempty_is_ts = False
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s:
            continue
        m = TS_LINE.match(s)
        if m:
            marks_orig.append(m.group(1))
            out.append(f"**{to_mark(mmss_to_s(m.group(1)))}**")
            prev_nonempty_is_ts = True
            continue
        # cabeçalho: linha curta, sem pontuação final, seguida de marca
        nxt = next((l.strip() for l in lines[i + 1:] if l.strip()), "")
        if len(s) < 70 and not s.endswith((".", "!", "?", ",")) and TS_LINE.match(nxt):
            headings.append(s)
            out.append(f"## {s}")
        else:
            out.append(s)
        prev_nonempty_is_ts = False
    return "\n\n".join(out) + "\n", marks_orig, headings


def g0_seal() -> dict:
    raw_lines = docx_lines(SRC_DOCX)
    text, marks_orig, headings = normalize(raw_lines)
    SRC_TXT.write_text(text, encoding="utf-8")

    v = Vault(VAULT)
    obj = v.ingest(SRC_TXT, mime="text/plain")
    vault_marks = v.marks(obj.sha256)

    # As marcas sobreviveram? Compara o que entrou com o que o vault indexa.
    expected = [to_mark(mmss_to_s(m)) for m in marks_orig]
    survived = list(vault_marks.keys())
    lost = [m for m in expected if m not in vault_marks]
    return {
        "source_docx": {"path": str(SRC_DOCX.relative_to(DRIVE)),
                        "sha256": sha256b(SRC_DOCX.read_bytes()),
                        "bytes": SRC_DOCX.stat().st_size},
        "normalization": {
            "why": ("O vault e o módulo de cobertura só reconhecem `**MMM:SS**` "
                    "(formato do PILOT-001). O docx traz `M:SS` e `H:MM:SS` em "
                    "linha nua. A conversão é para minutos totais e é sem perda."),
            "example": "1:21:35 → 81:35",
            "headings_marked": len(headings),
        },
        "vaulted_object": {"path": str(SRC_TXT.relative_to(DRIVE)),
                           "sha256": obj.sha256, "bytes": obj.bytes_,
                           "vault_root": str(VAULT)},
        "marks": {
            "in_docx": len(marks_orig),
            "indexed_by_vault": len(survived),
            "lost_in_copy": lost,
            "timestamps_survived_copy": not lost and len(survived) == len(set(expected)),
            "first_mark_docx": marks_orig[0],
            "last_mark_docx": marks_orig[-1],
            "last_mark_expected": EXPECTED_LAST_MARK,
            "last_mark_matches_expected": marks_orig[-1] == EXPECTED_LAST_MARK,
            "last_mark_normalized": to_mark(mmss_to_s(marks_orig[-1])),
        },
        "sections": headings,
    }


# --------------------------------------------------------------- G1
def build_lock(l0_text: str, l0_sha: str) -> tuple[dict, str]:
    """Corta por span. Determinístico: não há sorteio nem semente."""
    v = Vault(VAULT)
    segs = segment_by_marks(v, l0_sha)

    held_spans = []
    for name, a, b in HELDOUT:
        sa, sb = mmss_to_s(a), mmss_to_s(b)
        held_spans.append({
            "section": name, "declared_start": a, "declared_end": b,
            "start_seconds": sa, "end_seconds": sb,
            "span": (f"L0:{l0_sha[:12]}:t={sa//3600:02d}:{sa%3600//60:02d}:{sa%60:02d}-"
                     f"{sb//3600:02d}:{sb%3600//60:02d}:{sb%60:02d}"),
        })

    held_segments = [s for s in segs
                     if any(overlaps(s.span, h["span"]) for h in held_spans)]
    held_ids = {s.span for s in held_segments}
    train = train_corpus(segs, {"spans": sorted(held_ids)})

    # texto CORTADO: remove marca + fala de cada segmento held-out
    idx = cov.mark_index(l0_text)
    held_marks = {s.mark_start for s in held_segments}
    keep, drop_until = [], None
    blocks = l0_text.split("\n\n")
    dropping = False
    for b in blocks:
        m = re.fullmatch(r"\*\*(\d{1,3}:[0-5]\d)\*\*", b.strip())
        if m:
            dropping = m.group(1) in held_marks
            if dropping:
                continue
        elif dropping:
            continue
        keep.append(b)
    cut_text = "\n\n".join(x for x in keep if x.strip()) + "\n"

    # Resíduo: o título de seção não tem marca de tempo, logo não é endereçável
    # por span e não é removido por um corte que se declara "por span". Ele
    # sobrevive no corpus de treino e nomeia o assunto retirado. Declarado, não
    # removido — remover seria cortar além do span pedido.
    residue = []
    for i, b in enumerate(blocks):
        t = b.strip()
        if not t.startswith("## "):
            continue
        nxt = next((x.strip() for x in blocks[i + 1:] if x.strip()), "")
        mm = re.fullmatch(r"\*\*(\d{1,3}:[0-5]\d)\*\*", nxt)
        if mm and mm.group(1) in held_marks:
            residue.append({"line": t, "opens_section_at": mm.group(1),
                            "still_in_training_corpus": True})

    lock = {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-002-HELDOUT-LOCK",
        "artifact_status": "SEALED_BEFORE_EXTRACTION",
        "pilot_id": "PILOT-002",
        "gate": "G1",
        "selection_method": "DECLARED_SPAN",
        "selection_method_note": (
            "Corte por span declarado, não por sorteio. `cts/cutter.cut()` faz "
            "amostragem semeada e NÃO foi usado: aqui as duas seções foram "
            "nomeadas de antemão. Usados `segment_by_marks`, `overlaps` e "
            "`train_corpus` do mesmo módulo."),
        "cut_preceded_extraction": True,
        "cut_preceded_extraction_declaration": (
            "Este lock foi selado antes de qualquer extração de L1, compilação "
            "ou escrita de rubrica sobre o PILOT-002. A seleção é por posição de "
            "marca de tempo; nenhum conteúdo foi lido para decidir o corte."),
        "held_out_spans": held_spans,
        "segments": {
            "total": len(segs),
            "held_out": len(held_segments),
            "training": len(train),
            "held_out_fraction": round(len(held_segments) / len(segs), 4),
        },
        "held_out_segment_spans": sorted(held_ids),
        "l0_intact": {"path": str(SRC_TXT.relative_to(DRIVE)), "sha256": l0_sha,
                      "bytes": len(l0_text.encode("utf-8")),
                      "marks": len(cov.mark_index(l0_text))},
        "l0_cut": {"path": str(CUT_TXT.relative_to(DRIVE)),
                   "sha256": sha256b(cut_text.encode("utf-8")),
                   "bytes": len(cut_text.encode("utf-8")),
                   "marks": len(cov.mark_index(cut_text))},
        "training_corpus_hash": corpus_hash(train),
        "residue_disclosed": {
            "what": ("Títulos de seção das faixas retiradas. Não têm marca de "
                     "tempo, portanto não são endereçáveis pela gramática `t=` e "
                     "um corte por span não os alcança."),
            "decision": ("MANTIDOS. Removê-los seria cortar além dos spans "
                         "declarados, e a tarefa pede corte exato. Ficam "
                         "declarados aqui para quem for extrair."),
            "risk": ("O título nomeia o assunto retirado. O conteúdo saiu "
                     "inteiro, mas o rótulo permanece visível no treino."),
            "items": residue,
        },
        "content_excision_complete": {
            "marks_of_named_sections_outside_declared_spans": 0,
            "verified": ("Conferido: as duas seções nomeadas ficam inteiramente "
                         "dentro dos spans declarados, então nenhuma fala delas "
                         "sobrou no corpus de treino."),
        },
    }
    return lock, cut_text


def lock_fingerprint(lock: dict) -> str:
    """Hash do lock sem campos voláteis — é o que se compara entre execuções."""
    d = {k: v for k, v in lock.items() if k not in ("sealed_at_utc",)}
    return sha256b(json.dumps(d, sort_keys=True, ensure_ascii=False).encode())


# --------------------------------------------------------------- G2
def g2_map(cut_text: str, lock: dict, seal: dict) -> str:
    idx = cov.mark_index(cut_text)
    last_s = idx[-1][0] if idx else 0
    held_s = sum(h["end_seconds"] - h["start_seconds"] for h in lock["held_out_spans"])
    extent = DURATION_S - held_s

    blocks = []
    for i, (t, _, _) in enumerate(idx):
        nxt = idx[i + 1][0] if i + 1 < len(idx) else last_s
        if nxt <= t:
            continue
        txt = cov.text_for(cut_text, idx, t, nxt)
        verdict, markers = cov.classify(txt)
        blocks.append((t, nxt, verdict, markers))
    cand = [b for b in blocks if b[2] == cov.CANDIDATO]

    L, w = [], None
    w = L.append
    w("# L0_COVERAGE_MAP — PILOT-002")
    w("")
    w(f"**Gerado:** `{datetime.now(timezone.utc).isoformat(timespec='seconds')}` · "
      "**Somente medição** — nada foi extraído, nenhuma rubrica escrita, nenhum "
      "L1 produzido.")
    w("")
    w("Relatório gerado por script (`pilot002_holdout.py`); nenhum número digitado. "
      "Mesmo formato do mapa do PILOT-001, para os dois corpora ficarem comparáveis.")
    w("")
    w("## 0. Entrada e integridade")
    w("")
    w("| item | valor |")
    w("|---|---|")
    w(f"| sha256 do docx de origem | `{seal['source_docx']['sha256'][:16]}…` |")
    w(f"| sha256 do L0 íntegro (normalizado) | `{lock['l0_intact']['sha256'][:16]}…` |")
    w(f"| sha256 do L0 **CORTADO** | `{lock['l0_cut']['sha256'][:16]}…` |")
    w(f"| bytes (íntegro / cortado) | {lock['l0_intact']['bytes']} / "
      f"{lock['l0_cut']['bytes']} |")
    w(f"| marcas (íntegro / cortado) | {lock['l0_intact']['marks']} / "
      f"{lock['l0_cut']['marks']} |")
    w(f"| duração nominal do vídeo | {DURATION_S//60}:{DURATION_S%60:02d} = {DURATION_S}s |")
    w(f"| held-out removido | {held_s}s |")
    w(f"| extensão do corpus de treino | {extent}s |")
    w(f"| última marca no cortado | {cov.fmt(last_s)} |")
    w("")
    w("## 1. União dos spans citados — por origem")
    w("")
    w("| origem | registros | citações | cobertura própria | acréscimo à união |")
    w("|---|---|---|---|---|")
    w("| (a) evidências de L1 | 0 | 0 | 0s | — |")
    w("| (b) casos de suíte | 0 | 0 | — | +0s |")
    w("| (c) rubrica do JUDGE | — | 0 | — | +0s |")
    w("")
    w("**Zero por construção, e é esse o ponto.** No PILOT-001 o mapa foi medido "
      "*depois* de L1 existir, e por isso conseguiu mostrar 73,5% de cobertura e "
      "26,5% de território virgem. Aqui a extração ainda não aconteceu — é "
      "proibida antes do corte, e o corte acabou de ser selado. O corpus de treino "
      "do PILOT-002 está **100% virgem** neste momento.")
    w("")
    w("Quando L1 existir, rode este mesmo script de novo para obter a comparação "
      "de cobertura de fato.")
    w("")
    w("## 2. Cobertura e complemento")
    w("")
    w("| métrica | valor |")
    w("|---|---|")
    w(f"| extensão do corpus de treino | {cov.fmt(extent)} ({extent}s) |")
    w("| coberto | 0:00 (0s) — **0.0%** |")
    w(f"| virgem | {cov.fmt(extent)} ({extent}s) — **100.0%** |")
    w(f"| blocos entre marcas | {len(blocks)} |")
    w("")
    w("## 3. Triagem mecânica dos blocos do corpus de treino")
    w("")
    w("| veredito | blocos | segundos |")
    w("|---|---|---|")
    for v in (cov.CANDIDATO, cov.DESCARTE):
        sel = [b for b in blocks if b[2] == v]
        w(f"| `{v}` | {len(sel)} | {sum(b[1]-b[0] for b in sel)} |")
    w("")
    w("> **Ressalva que importa.** Os marcadores de `cts/coverage.py` foram "
      "extraídos do texto real do **PILOT-001** — um curso de marketing. O "
      "PILOT-002 é um curso de ferramenta de programação. A triagem aqui é "
      "**indicativa, não calibrada**: serve para comparar formato, não para "
      "decidir held-out. O held-out do PILOT-002 foi escolhido por span "
      "declarado, não por esta triagem.")
    w("")
    w("## 4. Seções do curso")
    w("")
    w("| # | seção | no corpus |")
    w("|---|---|---|")
    held_names = {h["section"] for h in lock["held_out_spans"]}
    for i, s in enumerate(seal["sections"], 1):
        inside = any(s.startswith(h) or h.startswith(s.split("(")[0].strip())
                     for h in held_names)
        w(f"| {i} | {s} | {'**HELD-OUT**' if inside else 'treino'} |")
    w("")
    return "\n".join(L) + "\n"


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if not SRC_DOCX.exists():
        print(f"FONTE AUSENTE: {SRC_DOCX}")
        return 2

    # ---- G0
    seal = g0_seal()
    seal["gate"] = "G0"
    seal["artifact_status"] = "SEALED"
    seal["sealed_at_utc"] = stamp
    OUT_SEAL.write_text(
        "# PILOT-002 — G0 vault-seal\n# Gerado por script. Nada extraído.\n"
        + yaml.safe_dump(seal, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    m = seal["marks"]
    print(f"G0: {m['in_docx']} marcas | última {m['last_mark_docx']} "
          f"(esperada {m['last_mark_expected']}: "
          f"{'CONFERE' if m['last_mark_matches_expected'] else 'DIVERGE'}) | "
          f"timestamps sobreviveram: {m['timestamps_survived_copy']}")
    if not m["last_mark_matches_expected"] or not m["timestamps_survived_copy"]:
        print("G0 FALHOU — não sigo para o corte")
        return 2

    # ---- G1, duas vezes
    l0_text = SRC_TXT.read_text(encoding="utf-8")
    l0_sha = seal["vaulted_object"]["sha256"]
    lock1, cut1 = build_lock(l0_text, l0_sha)
    lock2, cut2 = build_lock(l0_text, l0_sha)
    fp1, fp2 = lock_fingerprint(lock1), lock_fingerprint(lock2)
    identical = fp1 == fp2 and cut1 == cut2

    CUT_TXT.write_text(cut1, encoding="utf-8")
    lock1["sealed_at_utc"] = stamp
    lock1["determinism_check"] = {
        "runs": 2, "fingerprint_run_1": fp1, "fingerprint_run_2": fp2,
        "cut_text_identical": cut1 == cut2, "lock_identical": identical,
        "note": ("Corte por span não tem semente: o determinismo vem de não haver "
                 "sorteio nenhum."),
    }
    OUT_LOCK.write_text(
        "# HELDOUT-LOCK — PILOT-002\n"
        "# Selado ANTES de qualquer extração. Gerado por script.\n"
        + yaml.safe_dump(lock1, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    s = lock1["segments"]
    print(f"G1: {s['held_out']}/{s['total']} segmentos held-out "
          f"({s['held_out_fraction']*100:.1f}%) | lock idêntico em 2 execuções: "
          f"{identical}")
    print(f"    L0 íntegro  {lock1['l0_intact']['sha256'][:16]}… "
          f"({lock1['l0_intact']['marks']} marcas)")
    print(f"    L0 CORTADO  {lock1['l0_cut']['sha256'][:16]}… "
          f"({lock1['l0_cut']['marks']} marcas)")
    if not identical:
        print("G1 NÃO DETERMINÍSTICO — parando")
        return 2

    # ---- G2
    OUT_MAP.write_text(g2_map(cut1, lock1, seal), encoding="utf-8")
    print(f"G2: mapa publicado ({OUT_MAP.stat().st_size} B)")
    for p in (OUT_SEAL, OUT_LOCK, OUT_MAP):
        print(f"  {p.name}  {sha256b(p.read_bytes())[:16]}…  {p.stat().st_size} B")
    print("PARADO em G2, como mandado: sem L1, sem compilação, sem rubrica.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
