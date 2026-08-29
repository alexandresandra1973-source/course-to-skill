"""Decisão A — PASS 2 por SEGMENTO, um de cada vez.

A varredura monolítica sobre todos os segmentos NÃO existe aqui como mecanismo
primário. O laço é por segmento e o extractor recebe UM segmento por chamada;
não há caminho no código que entregue a aula inteira ao extractor.

§6.3: o rastro por segmento é obrigatório e inclui segmento com yield ZERO.
Segmento vazio permanece visível — sumir do rastro é o que impede distinguir o
Caso 2 (segmento legitimamente pobre) do Caso 3 (extractor truncado) da §8.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

from .model import Evidence, EvidenceDraft, Extractor, IdAllocator, Segment
from .temporal_map import TemporalMapHandle


@dataclass
class SegmentYield:
    segment_id: str
    start_s: int
    end_s: int
    duration_s: int
    evidence_count: int
    evidence_ids: list[str]
    extraction_status: str          # OK | ZERO_YIELD | EXTRACTOR_ERROR
    rescanned: bool = False
    rescan_added: int = 0
    iteration: int = 0
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Pass2Result:
    evidences: list[Evidence] = field(default_factory=list)
    yields: list[SegmentYield] = field(default_factory=list)

    @property
    def zero_yield_segments(self) -> list[str]:
        return [y.segment_id for y in self.yields if y.evidence_count == 0]

    @property
    def total(self) -> int:
        return len(self.evidences)

    def yield_per_segment(self) -> float:
        return self.total / len(self.yields) if self.yields else 0.0


def _local_context(seg: Segment, all_segs: list[Segment]) -> dict:
    """O mínimo contexto local da §5 Decisão A — vizinhos por rótulo, não por texto.

    Passa apenas os IDs e limites dos segmentos adjacentes, para o extractor
    saber onde termina o seu escopo. Não passa o conteúdo dos vizinhos: isso
    reintroduziria a competição global que a Decisão A remove.
    """
    idx = {s.segment_id: i for i, s in enumerate(all_segs)}
    i = idx[seg.segment_id]
    prev = all_segs[i - 1] if i > 0 else None
    nxt = all_segs[i + 1] if i + 1 < len(all_segs) else None
    return {
        "segment_id": seg.segment_id,
        "position": {"index": i, "of": len(all_segs)},
        "bounds_s": [seg.start_s, seg.end_s],
        "previous_segment_id": prev.segment_id if prev else None,
        "next_segment_id": nxt.segment_id if nxt else None,
        "scope_rule": ("Extraia SOMENTE do intervalo deste segmento. Vizinhos "
                       "são informados para você saber onde parar, não para "
                       "extrair deles."),
    }


def run_pass2(*, tmap: TemporalMapHandle, extractor: Extractor,
              ids: IdAllocator) -> Pass2Result:
    """Percorre os segmentos, um por chamada. Nunca uma varredura só."""
    if not tmap.path.exists():
        raise RuntimeError("PASS 2 exige temporal-map persistido (§6.1)")

    res = Pass2Result()
    segs = tmap.segments

    for seg in segs:
        try:
            drafts = extractor.extract(seg, _local_context(seg, segs), 0) or []
            status = "OK" if drafts else "ZERO_YIELD"
            err = ""
        except Exception as e:                      # o erro é dado, não crash
            drafts, status, err = [], "EXTRACTOR_ERROR", f"{type(e).__name__}: {e}"

        emitted = []
        for d in drafts:
            ev = Evidence(
                evidence_id=ids.issue(), segment_id=seg.segment_id,
                claim=d.claim, start_s=d.start_s, end_s=d.end_s,
                category=d.category, epistemic_status=d.epistemic_status,
                quote=d.quote, origin="PASS2", iteration=0)
            emitted.append(ev)

        res.evidences.extend(emitted)
        # Registrado SEMPRE, inclusive com zero. Nunca filtrado.
        res.yields.append(SegmentYield(
            segment_id=seg.segment_id, start_s=seg.start_s, end_s=seg.end_s,
            duration_s=seg.duration, evidence_count=len(emitted),
            evidence_ids=[e.evidence_id for e in emitted],
            extraction_status=status, error=err))

    if len(res.yields) != len(segs):
        raise RuntimeError("rastro por segmento incompleto")
    return res


def make_rescanner(*, tmap: TemporalMapHandle, extractor: Extractor,
                   ids: IdAllocator, result: Pass2Result):
    """Revarredura DIRIGIDA: só os segmentos pedidos pelo portão.

    Atualiza o rastro dos segmentos revisitados em vez de criar rastro paralelo,
    para o manifesto continuar tendo uma linha por segmento.
    """
    by_id = {s.segment_id: s for s in tmap.segments}
    trace = {y.segment_id: y for y in result.yields}

    def rescan(segment_ids: list[str], iteration: int) -> list[Evidence]:
        out: list[Evidence] = []
        for sid in segment_ids:
            seg = by_id.get(sid)
            if seg is None:
                continue
            try:
                drafts = extractor.extract(
                    seg, _local_context(seg, tmap.segments), iteration) or []
            except Exception:
                drafts = []
            new = [Evidence(evidence_id=ids.issue(), segment_id=sid,
                            claim=d.claim, start_s=d.start_s, end_s=d.end_s,
                            category=d.category,
                            epistemic_status=d.epistemic_status, quote=d.quote,
                            origin="RESCAN", iteration=iteration)
                   for d in drafts]
            out.extend(new)
            y = trace.get(sid)
            if y:
                y.rescanned = True
                y.rescan_added += len(new)
                y.iteration = iteration
                y.evidence_ids += [e.evidence_id for e in new]
        return out

    return rescan
