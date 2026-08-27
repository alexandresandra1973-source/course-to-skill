#!/usr/bin/env python3
"""PILOT-003 · etapa (a): L0 com marcas, hash, duração e contagem. Zero chamadas."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
OUT = DRIVE / "Course-to-Skill-Claude/pilots/PILOT-003/00_SOURCE"
T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
RAW = json.loads((T/"p003-raw.json").read_text(encoding="utf-8"))
MARK_EVERY = 6          # mesma densidade do PILOT-002 (733 marcas / 4897s ≈ 6,7s)


def fmt(s): return f"{int(s)//60}:{int(s)%60:02d}"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    blocks, buf, next_mark = [], [], 0
    for sn in RAW:
        if sn["start"] >= next_mark:
            if buf:
                blocks.append(" ".join(buf)); buf = []
            blocks.append(f"**{fmt(sn['start'])}**")
            next_mark = sn["start"] + MARK_EVERY
        buf.append(sn["text"].replace("\n", " ").strip())
    if buf:
        blocks.append(" ".join(buf))
    text = ("## (2026) Ecommerce Google Ads Free Course\n\n" +
            "\n\n".join(blocks) + "\n")
    p = OUT / "L0-transcript.txt"
    p.write_text(text, encoding="utf-8")
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    dur = int(RAW[-1]["start"] + RAW[-1].get("duration", 0))
    marks = sum(1 for b in blocks if b.startswith("**"))
    meta = {
        "schema_version": "0.1.0", "pilot_id": "PILOT-003",
        "artifact_status": "SOURCE_SEALED",
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {"platform": "youtube", "video_id": "c6qEURhNsYw",
                   "title": "(2026) Ecommerce Google Ads Free Course (4+ Hours)",
                   "url": "https://www.youtube.com/watch?v=c6qEURhNsYw"},
        "transcript": {"kind": "AUTO_GENERATED_ASR", "language": "en",
                       "snippets": len(RAW), "chars_raw": sum(len(s["text"]) for s in RAW)},
        "l0": {"path": "L0-transcript.txt", "sha256": sha, "bytes": p.stat().st_size,
               "marks": marks, "mark_every_s": MARK_EVERY,
               "duration_s": dur, "duration": f"{dur//3600}:{(dur%3600)//60:02d}:{dur%60:02d}"},
        "HELD_OUT": {
            "applied": False,
            "DIFERENCA_DECLARADA": (
                "Os PILOT-001 e PILOT-002 tiveram janelas de held-out removidas ANTES "
                "da extração, para testar resistência à invenção: se a Skill "
                "respondesse sobre território removido, estaria inventando. O "
                "PILOT-003 é piloto de USO — a pergunta não é 'a Skill inventa?', é "
                "'a recomendação bate com a conta real?'. O ground truth é EXTERNO "
                "(conta Google Ads viva), não um pedaço escondido da fonte."),
            "consequencia": ("os casos cegos do PILOT-002 NÃO têm equivalente aqui, e "
                             "nenhum número deste piloto é comparável aos de "
                             "resistência à invenção dos outros dois"),
            "corpus_de_treino_s": dur, "corpus_igual_a_fonte_inteira": True},
    }
    (OUT/"SOURCE-MANIFEST.yaml").write_text(
        yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    print(f"L0        : {sha}")
    print(f"bytes     : {p.stat().st_size}")
    print(f"marcas    : {marks}")
    print(f"duração   : {meta['l0']['duration']} ({dur}s)")
    print(f"held-out  : NÃO APLICADO (declarado no manifest)")
    # -------- estimativa de custo
    seg_target = 135
    n_seg = round(dur / seg_target)
    pass1_chunks = -(-dur // 1200)          # janelas de 20 min
    print("\n" + "="*64)
    print("ESTIMATIVA DE CHAMADAS, ANTES DE DISPARAR")
    print("="*64)
    print(f"  PASS 1 (segmentação, janelas de 20 min) : {pass1_chunks}")
    print(f"  PASS 2 (1 por segmento, alvo {seg_target}s)   : ~{n_seg}")
    print(f"  linhas de distância (lotes de 12)       : ~7")
    print(f"  compilação evidência→Skill (1/segmento) : ~{n_seg}")
    print(f"  ESPERADO (0 revarreduras, como nos dois pilotos anteriores): "
          f"{pass1_chunks + n_seg + 7 + n_seg}")
    print(f"  LIMITE DURO (1 revarredura em TODOS os segmentos)          : "
          f"{pass1_chunks + n_seg*3 + 7}")
    print(f"\n  MAX_RESCAN_ITERATIONS = 1 para este piloto (era 3), pré-declarado")
    print(f"  agora, e a razão é o teto de 400 chamadas — não o resultado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
