#!/usr/bin/env python3
"""TESTE DE VAZAMENTO DA RÉGUA DO JUIZ — uma chamada limpa.

Converte a ressalva "paráfrase passa pelo varredor" em medição.

A chamada recebe SOMENTE o conteúdo de RUBRIC-JUDGE.yaml e a pergunta. Sem
system prompt, sem outputs, sem dizer que existem condições, sem dizer que é
experimento comparativo, sem mencionar o projeto. Se a leitura reconstruir as
três condições, o cegamento vaza por paráfrase.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import anthropic

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
RUBRIC = (DRIVE / "Course-to-Skill-Claude/docs/TEST-0008-JUDGE-PACKAGE"
          / "RUBRIC-JUDGE.yaml")
import time
OUT = Path(f"/tmp/claude-1000/-home-mtx-course-to-skill-claude/leak-test-{int(time.time())}.json")

QUESTION = ("Lendo este documento, o que dá para inferir sobre como os materiais "
            "avaliados foram produzidos? Quantos tipos distintos você esperaria, "
            "e como os descreveria?")


def main() -> int:
    text = RUBRIC.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode()).hexdigest()
    payload = f"{text}\n\n---\n\n{QUESTION}"

    print(f"régua      : {RUBRIC.name}  sha256 {sha}")
    print(f"bytes      : {len(text)}")
    print(f"system     : NENHUM")
    print(f"anexos     : só a régua")
    print(f"pergunta   : {QUESTION}\n")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    with client.messages.stream(
        model="claude-opus-5",
        max_tokens=16000,
        messages=[{"role": "user", "content": payload}],
    ) as stream:
        msg = stream.get_final_message()
    answer = "".join(b.text for b in msg.content if b.type == "text")

    print("=" * 78)
    print("RESPOSTA INTEIRA")
    print("=" * 78)
    print(answer)
    print("=" * 78)

    OUT.write_text(json.dumps({
        "rubric_file": RUBRIC.name, "rubric_sha256": sha,
        "question": QUESTION, "model": "claude-opus-5",
        "system_prompt": None, "attachments": ["RUBRIC-JUDGE.yaml"],
        "answer": answer, "answer_sha256": hashlib.sha256(answer.encode()).hexdigest(),
        "usage": {"input": msg.usage.input_tokens, "output": msg.usage.output_tokens},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nresposta sha256: {hashlib.sha256(answer.encode()).hexdigest()}")
    print(f"tokens: entrada {msg.usage.input_tokens} saída {msg.usage.output_tokens}")
    print(f"rastro: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
