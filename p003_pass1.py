#!/usr/bin/env python3
"""PILOT-003 · (c) PASS 1 — temporal-map por janelas de 20 min. 12 chamadas."""
from __future__ import annotations
import hashlib, json, os, re, time
from pathlib import Path
import anthropic, yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
SRC = DRIVE / "Course-to-Skill-Claude/pilots/PILOT-003/00_SOURCE"
OUT = DRIVE / "Course-to-Skill-Claude/pilots/PILOT-003/01_PASS1"
MARK = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")
WIN = 1200
TARGET = 135

SYSTEM = """Você segmenta a transcrição de uma AULA em blocos temáticos contíguos.

Cada segmento é um trecho de ensino coerente: um assunto, uma demonstração, uma explicação. Um segmento NÃO é um parágrafo nem uma frase.

Alvo: cerca de 135 segundos por segmento. Aceitável de 60s a 300s. Prefira a fronteira temática real à duração alvo.

Os segmentos têm de COBRIR a janela inteira, sem buraco e sem sobreposição: o primeiro começa no início da janela, o último termina no fim, e cada um começa onde o anterior terminou.

Use SOMENTE marcas de tempo que aparecem no texto."""

SCHEMA = {"type":"object","properties":{"segments":{"type":"array","items":{
    "type":"object","properties":{
        "start":{"type":"string"},"end":{"type":"string"},
        "topic":{"type":"string"},"function":{"type":"string"}},
    "required":["start","end","topic","function"],"additionalProperties":False}}},
    "required":["segments"],"additionalProperties":False}


def sec(t):
    q=[int(x) for x in t.split(":")]
    return q[0]*3600+q[1]*60+q[2] if len(q)==3 else q[0]*60+q[1]


def fmt(s): return f"{s//3600:d}:{(s%3600)//60:02d}:{s%60:02d}"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    text = (SRC/"L0-transcript.txt").read_text(encoding="utf-8")
    meta = yaml.safe_load((SRC/"SOURCE-MANIFEST.yaml").read_text(encoding="utf-8"))
    dur = meta["l0"]["duration_s"]
    blocks = text.split("\n\n")
    idx = [(i, sec(m.group(0).strip("*"))) for i,b in enumerate(blocks)
           if (m:=MARK.fullmatch(b.strip()))]
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    segs, calls = [], []
    t0=time.time()
    for w0 in range(0, dur, WIN):
        w1 = min(w0+WIN, dur)
        sel = [k for k,(i,s) in enumerate(idx) if w0 <= s < w1]
        if not sel: continue
        a = idx[sel[0]][0]
        b = idx[sel[-1]+1][0] if sel[-1]+1 < len(idx) else len(blocks)
        chunk = "\n\n".join(blocks[a:b])
        payload = (f"JANELA {fmt(w0)}–{fmt(w1)} da aula.\n"
                   f"Segmente esta janela inteira. O primeiro segmento começa em "
                   f"{fmt(w0)} e o último termina em {fmt(w1)}.\n\n{chunk}")
        st=time.time()
        with client.messages.stream(model="claude-opus-5", max_tokens=8000,
                system=SYSTEM, messages=[{"role":"user","content":payload}],
                output_config={"format":{"type":"json_schema","schema":SCHEMA}}) as s:
            m=s.get_final_message()
        d=json.loads("".join(x.text for x in m.content if x.type=="text"))
        for g in d["segments"]:
            segs.append({"start_s":sec(g["start"]),"end_s":sec(g["end"]),
                         "topic":g["topic"],"function":g["function"]})
        calls.append({"window":[w0,w1],"segments":len(d["segments"]),
                      "latency_s":round(time.time()-st,1),
                      "in":m.usage.input_tokens,"out":m.usage.output_tokens})
        print(f"  {fmt(w0)}–{fmt(w1)}: {len(d['segments'])} segmentos "
              f"({round(time.time()-st)}s)")
    # ---- costura mecânica: ordena, fecha buracos, remove sobreposição
    segs.sort(key=lambda s:s["start_s"])
    fixed=[]
    for s in segs:
        if fixed and s["start_s"] < fixed[-1]["end_s"]:
            s["start_s"]=fixed[-1]["end_s"]
        if s["end_s"]<=s["start_s"]: continue
        if fixed and s["start_s"]>fixed[-1]["end_s"]:
            fixed[-1]["end_s"]=s["start_s"]        # fecha buraco estendendo o anterior
        fixed.append(s)
    if fixed: fixed[0]["start_s"]=0; fixed[-1]["end_s"]=dur
    for i,s in enumerate(fixed,1):
        s["segment_id"]=f"SEG-{i:03d}"; s["start"]=fmt(s["start_s"])
        s["end"]=fmt(s["end_s"]); s["duration_s"]=s["end_s"]-s["start_s"]
    tm={"schema_version":"0.1.0","pilot_id":"PILOT-003",
        "l0_sha256":meta["l0"]["sha256"],"extent_s":dur,
        "pass1":{"executed_by_model":True,"windows":len(calls),
                 "target_segment_s":TARGET,
                 "stitching":"MECÂNICA: ordena, corta sobreposição, estende o anterior "
                             "para fechar buraco. Nenhuma fronteira inventada por modelo "
                             "fora da sua janela."},
        "temporal_map":[{k:s[k] for k in ("segment_id","start","end","start_s","end_s",
                                          "duration_s","topic","function")} for s in fixed]}
    p=OUT/"temporal-map.yaml"
    p.write_text(yaml.safe_dump(tm,allow_unicode=True,sort_keys=False,width=100),
                 encoding="utf-8")
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    cov=sum(s["duration_s"] for s in fixed)
    print(f"\nsegmentos {len(fixed)} · cobertura {cov}/{dur}s "
          f"({100*cov/dur:.1f}%) · duração min/med/max "
          f"{min(s['duration_s'] for s in fixed)}/"
          f"{cov//len(fixed)}/{max(s['duration_s'] for s in fixed)}s")
    print(f"temporal-map sha256: {sha}")
    print(f"{len(calls)} chamadas em {round(time.time()-t0)}s · "
          f"tokens {sum(c['in'] for c in calls)}/{sum(c['out'] for c in calls)}")
    Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-pass1.json").write_text(
        json.dumps({"calls":calls,"sha256":sha},ensure_ascii=False,indent=1),encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
