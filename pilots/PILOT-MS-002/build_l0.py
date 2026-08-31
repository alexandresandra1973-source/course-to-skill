#!/usr/bin/env python3
"""MS-002 — camada L0 mecanica: anchors, evidence e slices. ZERO chamadas de modelo.
Determinismo: mesma entrada -> mesmos ids, mesmos hashes."""
import json, hashlib, pathlib, sys
H = pathlib.Path(__file__).resolve().parent
RAW = H / "00_RAW"
MAN = json.loads((H / "SOURCE-MANIFEST-MS-002.json").read_text(encoding="utf-8"))

# segmentos por unidade de anchor/evidence, por fonte
SEG_PER_UNIT = {"A": 10, "B": 4, "C": 4}
# unidades de evidence por slice de extracao
UNITS_PER_SLICE = {"A": 60, "B": 50, "C": 40}

def build(src):
    sid = f"MS002-SRC-{src}"
    m = MAN[sid]
    segs = json.loads((RAW / f"SRC-{src}-RAW-CAPTION.json").read_text(encoding="utf-8"))
    n = SEG_PER_UNIT[src]
    units = []
    for i in range(0, len(segs), n):
        grp = segs[i:i + n]
        quote = " ".join(x["text"].strip() for x in grp)
        quote = " ".join(quote.split())
        units.append({"idx": len(units) + 1, "segment_ids": list(range(i, i + len(grp))),
                      "start_s": round(grp[0]["start"], 3),
                      "end_s": round(grp[-1]["start"] + grp[-1]["duration"], 3),
                      "quote": quote})
    ups = UNITS_PER_SLICE[src]
    anchors, evidence, slices = [], [], []
    for k in range(0, len(units), ups):
        slice_no = k // ups + 1
        slice_id = f"SL-{src}-{slice_no:02d}"
        chunk = units[k:k + ups]
        slices.append({"slice_id": slice_id, "n_units": len(chunk),
                       "start_s": chunk[0]["start_s"], "end_s": chunk[-1]["end_s"],
                       "chars": sum(len(u["quote"]) for u in chunk)})
        for u in chunk:
            an = f"AN-{u['idx']:04d}"; ev = f"EV-{u['idx']:04d}"
            anchors.append({"entity_kind": "source_anchor", "local_id": an, "source_id": sid,
                            "slice_id": slice_id, "video_id": m["video_id"],
                            "artifact_hash": m["SOURCE_CONTENT_HASH"],
                            "start_s": u["start_s"], "end_s": u["end_s"],
                            "transcript_segment_ids": u["segment_ids"], "quote": u["quote"]})
            evidence.append({"entity_kind": "evidence", "local_id": ev, "source_id": sid,
                             "slice_id": slice_id, "source_language": m["language"],
                             "excerpt": u["quote"],
                             "source_anchor_refs": [{"local_id": an, "ref_scope": "SELF"}],
                             "provenance": {"video_id": m["video_id"],
                                            "artifact_hash": m["SOURCE_CONTENT_HASH"],
                                            "transcript_segment_ids": u["segment_ids"]}})
    pkg = H / "packages" / f"pkg-{src}"
    (pkg / "L0").mkdir(parents=True, exist_ok=True)
    (pkg / "L0" / "RAW-CAPTION.json").write_text(
        (RAW / f"SRC-{src}-RAW-CAPTION.json").read_text(encoding="utf-8"), encoding="utf-8")
    def wl(p, rows):
        (pkg / p).write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n"
                                     for r in rows), encoding="utf-8")
    wl("SOURCE-ANCHORS.jsonl", anchors); wl("EVIDENCE.jsonl", evidence)
    (pkg / "SLICES.json").write_text(json.dumps(slices, ensure_ascii=False, indent=1), encoding="utf-8")
    (pkg / "SOURCE-PROFILE.json").write_text(json.dumps({
        "source_id": sid, "video_id": m["video_id"], "canonical_url": m["canonical_url"],
        "authority": m["author_channel"], "channel_id": m["channel_id"],
        "language": m["language"], "media_type": "video/youtube",
        "caption_type": m["caption_type"], "source_content_hash": m["SOURCE_CONTENT_HASH"],
        "source_boundary": "video inteiro, cobertura integral",
        "provenance_chain": ["video -> raw caption artifact -> anchors -> evidence"],
        "source_independence_state": "DECLARED_INDEPENDENT",
        "independence_decision_record": "DR-MS-002-INDEP-001",
        "text_status": "SOURCE_TEXT_READY_WITH_LIMITATION",
        "limitations": m["limitations"]}, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    return {"source_id": sid, "units": len(units), "anchors": len(anchors),
            "evidence": len(evidence), "slices": len(slices),
            "chars": sum(len(u["quote"]) for u in units),
            "coverage_segments": sum(len(u["segment_ids"]) for u in units), "total_segments": len(segs)}

if __name__ == "__main__":
    out = {}
    for s in ("A", "B", "C"):
        r = build(s); out[r["source_id"]] = r
        assert r["coverage_segments"] == r["total_segments"], f"cobertura incompleta em {s}"
        print(f"  {r['source_id']}: {r['units']} unidades · {r['slices']} slices · "
              f"{r['chars']} chars · cobertura {r['coverage_segments']}/{r['total_segments']} segmentos")
    (H / "packages" / "L0-SUMMARY.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
