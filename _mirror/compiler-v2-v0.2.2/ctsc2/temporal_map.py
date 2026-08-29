"""PASS 1 — `temporal-map.yaml` obrigatório, persistido e hasheado ANTES do PASS 2.

§6.1 da ADR: um passe obrigatório do pipeline não pode continuar inauditável
num sistema cujos artefatos de jusante são endereçados por conteúdo.

A ordem importa e é verificada: o mapa é gravado e hasheado ANTES de qualquer
chamada do PASS 2. Se o PASS 2 começar sem mapa persistido, é erro.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from .model import Segment


def _s(t: int) -> str:
    return f"{t//3600:02d}:{t%3600//60:02d}:{t%60:02d}"


def build(segments: list[Segment], pilot_id: str, lesson_id: str,
          l0_sha256: str, extent_s: int) -> dict:
    if not segments:
        raise ValueError("PASS 1 não pode produzir zero segmentos")
    ordered = sorted(segments, key=lambda s: s.start_s)
    for a, b in zip(ordered, ordered[1:]):
        if b.start_s < a.end_s:
            raise ValueError(f"segmentos sobrepostos: {a.segment_id}/{b.segment_id}")
    return {
        "schema_version": "0.2.0",
        "artifact_id": f"{pilot_id}-TEMPORAL-MAP",
        "pilot_id": pilot_id,
        "lesson_id": lesson_id,
        "produced_by": "PASS 1 — TEMPORAL MAP",
        "l0": {"sha256": l0_sha256, "extent_s": extent_s},
        "segment_count": len(ordered),
        "temporal_map": [
            {"segment_id": s.segment_id, "start": _s(s.start_s), "end": _s(s.end_s),
             "start_s": s.start_s, "end_s": s.end_s, "duration_s": s.duration,
             "topic": s.topic, "function": s.function}
            for s in ordered
        ],
        "note": ("Contagem de segmentos é RESULTADO da segmentação semântica, "
                 "não parâmetro. Nenhum alvo de contagem existe no PASS 1."),
    }


def persist(doc: dict, out_dir: Path) -> tuple[Path, str]:
    """Grava e devolve (caminho, sha256). Hash calculado do byte gravado."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "temporal-map.yaml"
    blob = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False,
                          width=100).encode("utf-8")
    path.write_bytes(blob)
    return path, hashlib.sha256(blob).hexdigest()


class TemporalMapHandle:
    """Prova de que o mapa foi persistido antes do PASS 2.

    O driver do PASS 2 exige este objeto. Não há caminho no código que permita
    extrair sem mapa gravado — a dependência é estrutural, não um lembrete.
    """

    def __init__(self, path: Path, sha256: str, segments: list[Segment]):
        self.path, self.sha256, self.segments = path, sha256, segments
        if not path.exists():
            raise RuntimeError("temporal-map não está em disco")

    @property
    def segment_count(self) -> int:
        return len(self.segments)


def write_and_seal(segments: list[Segment], out_dir: Path, *, pilot_id: str,
                   lesson_id: str, l0_sha256: str,
                   extent_s: int) -> TemporalMapHandle:
    doc = build(segments, pilot_id, lesson_id, l0_sha256, extent_s)
    path, sha = persist(doc, out_dir)
    return TemporalMapHandle(path, sha, sorted(segments, key=lambda s: s.start_s))
