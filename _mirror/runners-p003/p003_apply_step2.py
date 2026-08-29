#!/usr/bin/env python3
"""ETAPA 2 — a Skill recebe os recortes que pediu e conclui. Mesmo bundle."""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import anthropic

S = Path("/home/mtx/course-to-skill-claude/_mirror/pilots/PILOT-003-v2/skill")
T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
FILES = ["SKILL.md", "knowledge/runtime-policy.yaml", "knowledge/decision-rules.yaml",
         "knowledge/workflows.yaml", "manifest.yaml"]
R = json.loads((T/"p003-recortes.json").read_text(encoding="utf-8"))
PREV = json.loads((T/"p003-apply1.json").read_text(encoding="utf-8"))["answer"]

MSG = """Executei mecanicamente os recortes que você pediu. Segue o resultado.

NÃO ATENDIDO, e registro por quê:
- RECORTE A e H (contaminação de marca / keywords de marca fora de campanha de
  marca): você pediu a LISTA DE TOKENS DE MARCA (seu item 5) e ela não existe nas
  exportações. Não vou inventar a lista — inventá-la seria eu escolhendo o
  achado. Fica bloqueado.
- Seus itens 1 a 14 de dados faltantes: nenhum pode ser atendido. As três
  exportações são tudo o que existe. Configurações de conta e tela de conversões
  NÃO foram exportadas.

Com o que você TEM agora, conclua o que a metodologia permite concluir.
Onde um limiar depender de dado que falta, diga METHOD_NOT_DEFINED ou aponte o
campo UNDEFINED em vez de arbitrar número.
Cite o identificador da regra em cada conclusão."""


def main() -> int:
    system = ("Você está executando a Skill abaixo. Os arquivos presentes no bundle "
              "são exatamente estes: " + ", ".join(FILES) + "\n\n" +
              "\n\n".join(f"=== {f} ===\n{(S/f).read_text(encoding='utf-8')}" for f in FILES))
    payload = (MSG + "\n\n=== SUA ANÁLISE ANTERIOR ===\n" + PREV[:6000] +
               "\n\n=== RECORTES EXECUTADOS ===\n" +
               json.dumps(R, ensure_ascii=False, indent=1)[:60000])
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    with client.messages.stream(model="claude-opus-5", max_tokens=32000, system=system,
                                messages=[{"role": "user", "content": payload}]) as s:
        m = s.get_final_message()
    ans = "".join(getattr(b, "text", "") for b in m.content if b.type == "text")
    (T/"p003-apply2.json").write_text(json.dumps(
        {"answer": ans, "sha256": hashlib.sha256(ans.encode()).hexdigest(),
         "usage": {"in": m.usage.input_tokens, "out": m.usage.output_tokens}},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"len {len(ans)} · tokens {m.usage.input_tokens}/{m.usage.output_tokens}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
