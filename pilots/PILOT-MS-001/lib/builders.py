"""MS-001 — construtores DETERMINISTICOS pre-modelo.
L0 / slices / anchors / evidence. Zero modelo, zero rede."""
import json, hashlib, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "00_SOURCE"
RAW = {"MS001-SRC-B": SRC / "B-dtAoZYMEzcM-pt.json",
       "MS001-SRC-C": SRC / "C-NvrBpnbNfv4-pt.json"}
VIDEO = {"MS001-SRC-B": "dtAoZYMEzcM", "MS001-SRC-C": "NvrBpnbNfv4"}
EVIDENCE_GROUP_N = 4          # decidido por medicao; banda historica 6,67-6,83/1000 chars
EVIDENCE_MIN_LAST = 2         # grupo final < 2 e fundido no anterior


def sha_bytes(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_raw(source_id):
    return json.loads(RAW[source_id].read_text(encoding="utf-8"))


def frozen_slices():
    return json.loads((SRC / "FROZEN-SLICES.json").read_text(encoding="utf-8"))


def slice_segments(source_id, slice_rec):
    a, b = slice_rec["transcript_segment_ids"]
    return list(range(a, b + 1))


def slice_text(source_id, slice_rec):
    S = load_raw(source_id)
    return " ".join(S[i]["text"] for i in slice_segments(source_id, slice_rec))


def evidence_groups(source_id, slice_rec, n=EVIDENCE_GROUP_N, minlast=EVIDENCE_MIN_LAST):
    """Grupos contiguos de n segmentos, sem sobreposicao; resto < minlast funde no anterior."""
    idx = slice_segments(source_id, slice_rec)
    G = [idx[i:i + n] for i in range(0, len(idx), n)]
    if len(G) > 1 and len(G[-1]) < minlast:
        G[-2] = G[-2] + G.pop()
    return G


def build_anchors(source_id):
    """SOURCE_ANCHORS mecanicos. quote verbatim; spans sobrepostos permitidos."""
    S = load_raw(source_id)
    ah = sha_bytes(RAW[source_id])
    FR = frozen_slices()
    out = []
    k = 0
    for sid in sorted(FR):
        r = FR[sid]
        if r["source_id"] != source_id:
            continue
        for g in evidence_groups(source_id, r):
            k += 1
            segs = [S[i] for i in g]
            out.append({"local_id": f"AN-{k:04d}", "entity_kind": "source_anchor",
                        "source_id": source_id, "artifact_hash": ah,
                        "video_id": VIDEO[source_id], "slice_id": sid,
                        "start_s": segs[0]["start"],
                        "end_s": round(segs[-1]["start"] + segs[-1]["duration"], 3),
                        "quote": " ".join(x["text"] for x in segs),
                        "transcript_segment_ids": g})
    return out


def build_evidence(source_id, anchors):
    """Evidence 1:1 com anchor. Nenhum modelo cria Evidence."""
    return [{"local_id": f"EV-{i:04d}", "entity_kind": "evidence",
             "source_id": source_id, "slice_id": a["slice_id"],
             "source_anchor_refs": [{"ref_scope": "SELF", "local_id": a["local_id"]}],
             "excerpt": a["quote"], "source_language": "pt",
             "provenance": {"artifact_hash": a["artifact_hash"], "video_id": a["video_id"],
                            "transcript_segment_ids": a["transcript_segment_ids"]}}
            for i, a in enumerate(anchors, 1)]


def evidence_catalog(evidence, slice_id):
    """Catalogo FECHADO por chamada: so as Evidence daquela slice."""
    return [{"evidence_id": e["local_id"], "excerpt": e["excerpt"]}
            for e in evidence if e["slice_id"] == slice_id]
