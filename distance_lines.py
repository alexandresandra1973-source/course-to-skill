#!/usr/bin/env python3
"""A linha de distância de cada inferência genuína. Lotes de 12.

Por que com chamada: "a distância entre o que o curso disse e o que o modelo
concluiu" é propriedade SEMÂNTICA. Este projeto já registrou quatro vezes que
proxy mecânico para propriedade semântica falha aqui; um diff lexical seria a
quinta tentativa e leria como precisão que não tem.

Contabilidade dura: toda evidência do lote tem de voltar com linha. Faltou,
o lote é refeito só com as que faltaram.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import anthropic

T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
import os
PILOT = os.environ.get("CTSS_PILOT", "PILOT-002-v2")
SPLIT = json.loads((T/os.environ.get("CTSS_SPLIT","mi-split-v2.json")).read_text(encoding="utf-8"))
OUT = T/f"distance-lines-{PILOT}.json"
BATCH = 12

SYSTEM = """Você compara o que uma fonte DISSE com o que um extrator CONCLUIU.

Para cada item recebe: a CITAÇÃO literal da fonte e a AFIRMAÇÃO derivada dela.

Devolva, para cada evidence_id, UMA linha no formato exato:
  "o curso não ensina X; o modelo inferiu de Y"
onde X é o que a afirmação acrescenta e a citação não sustenta, e Y é o que a
citação de fato diz.

Regras:
- se a afirmação NÃO acrescenta nada além da citação (é tradução, paráfrase ou
  reordenação), devolva: "sem distância: a afirmação é paráfrase da citação".
- seja específico. "o modelo generalizou" não serve; diga o quê.
- máximo 30 palavras por linha. Português.
- não julgue se a inferência é boa ou ruim. Só descreva a distância."""

SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {
    "type": "object",
    "properties": {"evidence_id": {"type": "string"}, "line": {"type": "string"}},
    "required": ["evidence_id", "line"], "additionalProperties": False}}},
    "required": ["items"], "additionalProperties": False}


def ask(client, batch):
    payload = "\n\n".join(
        f"[{b['evidence_id']}]\nCITAÇÃO: {b['quote']}\nAFIRMAÇÃO: {b['claim']}"
        for b in batch)
    with client.messages.stream(
        model="claude-opus-5", max_tokens=4000, system=SYSTEM,
        messages=[{"role": "user", "content": payload}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    ) as st:
        m = st.get_final_message()
    txt = "".join(b.text for b in m.content if b.type == "text")
    return {i["evidence_id"]: i["line"] for i in json.loads(txt)["items"]}, m.usage


def main() -> int:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    lines, calls, tin, tout = {}, 0, 0, 0
    for pid, d in SPLIT.items():
        items = d["genuina"]
        pend = list(items)
        for attempt in range(3):
            if not pend:
                break
            nxt = []
            for i in range(0, len(pend), BATCH):
                b = pend[i:i+BATCH]
                got, u = ask(client, b)
                calls += 1; tin += u.input_tokens; tout += u.output_tokens
                lines.update(got)
                miss = [x for x in b if x["evidence_id"] not in got]
                nxt += miss
                print(f"  {pid} lote {i//BATCH+1}: {len(got)}/{len(b)}"
                      f"{'  FALTOU '+str([m['evidence_id'] for m in miss]) if miss else ''}")
            pend = nxt
        if pend:
            print(f"  !! {pid}: {len(pend)} sem linha após 3 tentativas")
    OUT.write_text(json.dumps({"lines": lines, "calls": calls,
                               "tokens": {"in": tin, "out": tout}},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(len(d["genuina"]) for d in SPLIT.values())
    print(f"\nlinhas: {len(lines)}/{total} · chamadas: {calls} · "
          f"tokens {tin}/{tout}")
    return 0 if len(lines) == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
