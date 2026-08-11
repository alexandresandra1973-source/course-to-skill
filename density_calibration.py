#!/usr/bin/env python3
"""TAREFA 1 — calibrar o medidor de densidade ANTES de usá-lo.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/.

CANÁRIO: o medidor só é aprovado se classificar o PILOT-001 como FINA.
Reprovou, nenhum veredito de densidade é emitido.

Este script NÃO ajusta regex para o canário passar. Ajustar o contador até o
número dar certo em n=1 é fabricar o número, que é o que o projeto combate.
A classificação estrutural abaixo é DADO auditável, digitado à mão e conferido
contra a saída viva do medidor: se o medidor mudar, a conferência quebra alto.
"""
from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import source_density as sd

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "DENSITY-METER-CALIBRATION.md"
P001 = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources"
        / "transcript/transcript-original-en.txt")

# --------------------------------------------------------------------------
# Classificação ESTRUTURAL dos itens que o medidor contou.
#
# Chave = posição na ordem de extração do medidor. `head` é conferido contra a
# frase viva; divergiu, o script aborta em vez de publicar classificação velha.
#
# Categorias:
#   RETORICA     — pergunta retórica, narração, transição de seção
#   AFIRMACAO    — asserção/consequência, não instrução
#   DEFINICAO    — define um termo ou dá exemplo ilustrativo
#   CTA_PLUG     — chamada para ação, brinde, inscrição
#   PASSO_LINEAR — instrução de checklist, sem ramo
#   RAMO         — condição com alternativas, ou portão real de decisão
# --------------------------------------------------------------------------
CLASSIFICATION = {
    1:  ("RETORICA", "In this video, we're going to answer", "enquadramento do vídeo"),
    2:  ("RETORICA", "All right, let's start with the most", "transição de seção"),
    3:  ("RETORICA", "If your answer is,", "diagnóstico retórico, sem ação"),
    4:  ("AFIRMACAO", "Marketing teams don't fail because", "tese, não regra"),
    5:  ("AFIRMACAO", "And when you start with outcomes", "consequência declarada"),
    6:  ("RETORICA", "So if you feel like you need to hire", "diagnóstico retórico"),
    7:  ("DEFINICAO", "If this happens, do that.", "define o que é automação"),
    8:  ("DEFINICAO", "Like an automation that sends a welcome", "exemplo ilustrativo"),
    9:  ("DEFINICAO", "And it adapts when conditions change.", "define o que é agente"),
    10: ("RETORICA", "So, if you've been relying on chat bots", "transição retórica"),
    11: ("RETORICA", "So let's start with the most important", "transição de seção"),
    12: ("AFIRMACAO", "If any one of these is missing or weak", "asserção sobre o modelo"),
    13: ("DEFINICAO", "Who it is, what it does, what it's allowed", "define o system prompt"),
    14: ("DEFINICAO", "Eager, tireless, and never complains", "analogia do novo contratado"),
    15: ("RETORICA", "So with that being said, which agents", "transição de seção"),
    16: ("RETORICA", "We won't start with the flashiest", "narração da seleção"),
    17: ("RETORICA", "But the next question people ask is", "transição + asserção"),
    18: ("RAMO", "Here's how to choose based on where you are", "abre a tabela de plataforma"),
    19: ("RAMO", "If you're already on HubSpot Professional", "ramo: HubSpot Breeze"),
    20: ("RAMO", "is the fastest way to your first working", "reafirma a condição HubSpot"),
    21: ("RAMO", "If you want to build without any code", "ramo: Claude"),
    22: ("RAMO", "If you're more of a visual thinker", "ramo: Gumloop"),
    23: ("RAMO", "If you're already on Zapier", "ramo: Zapier Agents"),
    24: ("RAMO", "If you can't run a command line", "portão de segurança do OpenClaw"),
    25: ("RAMO", "If any of the tools we just covered", "prefira o já coberto"),
    26: ("RAMO", "Open Claw is the one you reach for when", "ramo: último recurso"),
    27: ("PASSO_LINEAR", "Step one, start with the outcome.", "passo 1 do checklist"),
    28: ("DEFINICAO", "Basically, what the agent is never allowed", "define boundaries"),
    29: ("DEFINICAO", "For the HubSpot YouTube intelligence agent", "exemplo trabalhado"),
    30: ("AFIRMACAO", "You'll end up automating a task instead", "consequência do erro"),
    31: ("PASSO_LINEAR", "Step three, choose your platform", "passo 3 do checklist"),
    32: ("PASSO_LINEAR", "This is where you choose what you're", "reafirma o passo 3"),
    33: ("PASSO_LINEAR", "Whatever platform you choose, one of the", "olhar integrações"),
    34: ("RAMO", "If you want to run it automatically every", "opcional: agendar no Zapier"),
    35: ("PASSO_LINEAR", "Instead of starting from scratch every", "passo 4: memória"),
    36: ("RAMO", "If you're an e-commerce brand", "ramo: contexto de e-commerce"),
    37: ("RAMO", "If you're a B2B company", "ramo: contexto B2B"),
    38: ("RAMO", "And if you're an agency", "ramo: contexto de agência"),
    39: ("AFIRMACAO", "Every time it produces something off brand", "não desista"),
    40: ("RAMO", "After 30 days, if it's consistently solid", "portão: afrouxar revisão"),
    41: ("RAMO", "If both are yes, expand it.", "portão: expandir"),
    42: ("RAMO", "If either's a no, go back and rebuild it.", "portão: reconstruir"),
    43: ("AFIRMACAO", "Don't let dead agents live in your stack.", "slogan"),
    44: ("PASSO_LINEAR", "Make sure that's toggled on so it pulls", "ligar a busca web"),
    45: ("AFIRMACAO", "But don't try to build everything at once.", "conselho genérico"),
    46: ("PASSO_LINEAR", "Start with one gap.", "escolher o primeiro agente"),
    47: ("CTA_PLUG", "If you want to go deeper on any of this", "brinde"),
    48: ("CTA_PLUG", "If this video helped in any way", "curtir e compartilhar"),
    49: ("CTA_PLUG", "For more helpful marketing content", "inscrever-se"),
}

NAO_DECISAO = {"RETORICA", "AFIRMACAO", "DEFINICAO", "CTA_PLUG"}

# As estruturas de decisão que sobram, por leitura estrutural.
STRUCTURES = [
    {"kind": "tabela de decisão multi-ramo", "name": "escolha de plataforma",
     "items": [18, 19, 20, 21, 22, 23, 24, 25, 26],
     "branches": ["HubSpot Breeze", "Claude", "Gumloop", "Zapier Agents",
                  "OpenClaw (último recurso, com portão de segurança)"],
     "note": "É a única tabela realmente multi-ramo da aula."},
    {"kind": "mapeamento ilustrativo", "name": "que contexto dar por tipo de empresa",
     "items": [36, 37, 38],
     "branches": ["e-commerce", "B2B", "agência"],
     "note": ("Três ramos, mas ilustram o mesmo passo de memória com exemplos "
              "por segmento. Fica no limite entre tabela e exemplo.")},
    {"kind": "portão", "name": "afrouxar a revisão humana", "items": [40],
     "branches": ["≥30 dias e consistente → afrouxa"], "note": ""},
    {"kind": "portão", "name": "expandir ou reconstruir", "items": [41, 42],
     "branches": ["ambas sim → expande", "qualquer não → reconstrói"], "note": ""},
    {"kind": "opcional", "name": "agendamento automático", "items": [34],
     "branches": ["quer rodar sozinho → agenda no Zapier"], "note": ""},
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract() -> list[tuple[str, str | None, str | None]]:
    body = sd.strip_marks(P001.read_text(encoding="utf-8"))
    seen, out = set(), []
    for s in sd.sentences(body):
        c = sd.CONDITIONAL.search(s)
        n = sd.NORMATIVE.search(s)
        if not (c or n):
            continue
        k = sd.norm(s)
        if k in seen:
            continue
        seen.add(k)
        out.append((s, c.group(0) if c else None, n.group(0) if n else None))
    return out


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    items = extract()
    n = len(items)

    # conferência: a classificação ainda descreve o que o medidor extrai?
    drift = []
    if n != len(CLASSIFICATION):
        drift.append(f"o medidor extraiu {n} itens; a classificação cobre "
                     f"{len(CLASSIFICATION)}")
    for i, (s, _, _) in enumerate(items, 1):
        exp = CLASSIFICATION.get(i)
        if not exp:
            drift.append(f"item {i} sem classificação")
        elif not s.startswith(exp[1]):
            drift.append(f"item {i}: esperado começar por {exp[1]!r}, veio {s[:40]!r}")
    if drift:
        print("DERIVA entre medidor e classificação — não publico:")
        for d in drift:
            print("  -", d)
        return 2

    cats = {}
    for i in range(1, n + 1):
        cats.setdefault(CLASSIFICATION[i][0], []).append(i)
    trivial = sorted(i for i in range(1, n + 1)
                     if CLASSIFICATION[i][0] in NAO_DECISAO)
    steps = cats.get("PASSO_LINEAR", [])
    branches = cats.get("RAMO", [])

    minutes = 905 / 60
    lexical_verdict = "FINA" if n <= sd.ONE_PAGE_LINES else "NAO_FINA"
    canary_pass = lexical_verdict == "FINA"

    # Instabilidade: de que exclusão depende virar FINA?
    scenarios = []
    for label, drop in [("bruto, sem exclusão", set()),
                        ("menos CTA/plug", {"CTA_PLUG"}),
                        ("menos CTA/plug e retórica", {"CTA_PLUG", "RETORICA"}),
                        ("menos tudo que não é decisão", NAO_DECISAO)]:
        k = sum(1 for i in range(1, n + 1) if CLASSIFICATION[i][0] not in drop)
        scenarios.append((label, k, "FINA" if k <= sd.ONE_PAGE_LINES else "NAO_FINA"))

    L, w = [], None
    w = L.append
    w("# Calibração do medidor de densidade — reprovado no canário")
    w("")
    w(f"- Gerado: `{stamp}` · gerador `{Path(__file__).name}`")
    w("- READ-ONLY sobre `Course-to-Skill/`")
    w(f"- Fonte: `{P001.relative_to(DRIVE)}` · sha256 `{sha(P001)[:16]}…`")
    w("")
    w("## Canário de calibração")
    w("")
    w(f"| | |")
    w(f"|---|---|")
    w(f"| exigido | PILOT-001 deve sair **FINA** |")
    w(f"| medidor deu | **{lexical_verdict}** ({n} pontos de decisão > "
      f"{sd.ONE_PAGE_LINES}) |")
    w(f"| resultado | **{'APROVADO' if canary_pass else 'REPROVADO'}** |")
    w("")
    if not canary_pass:
        w("**Nenhum veredito de densidade é emitido enquanto o medidor não passar "
          "no canário.** O `SOURCE-DENSITY-COMPARISON.md` não deve ser usado para "
          "qualificar o PILOT-002.")
    w("")
    w("## 1. Os 49 itens que o medidor contou, nominalmente")
    w("")
    w("| # | disparo | categoria | trecho | por quê |")
    w("|---|---|---|---|---|")
    for i, (s, c, nn) in enumerate(items, 1):
        cat, _, why = CLASSIFICATION[i]
        trig = f"`{c or nn}`"
        mark = "" if cat in NAO_DECISAO else "**"
        w(f"| {i} | {trig} | {mark}{cat}{mark} | {s[:95].replace('|','\\|')} | {why} |")
    w("")
    w("## 2. Quantos são condicionais triviais de tutorial")
    w("")
    w("| categoria | itens | é decisão? |")
    w("|---|---|---|")
    for cat in ("RETORICA", "AFIRMACAO", "DEFINICAO", "CTA_PLUG", "PASSO_LINEAR",
                "RAMO"):
        ids = cats.get(cat, [])
        w(f"| `{cat}` | {len(ids)} | {'não' if cat in NAO_DECISAO else 'sim'} |")
    w("")
    w(f"**{len(trivial)} dos {n} ({len(trivial)/n*100:.0f}%) não são decisão "
      f"nenhuma.** São pergunta retórica, transição de seção, definição de termo, "
      f"exemplo, slogan e chamada para curtir e se inscrever. O medidor os contou "
      f"porque `if`, `when`, `should`, `never` e `make sure` aparecem em todos "
      f"eles — em inglês falado essas palavras são cola de discurso, não sintaxe "
      f"de regra.")
    w("")
    w("Casos que mostram bem o problema:")
    w("")
    for i in (7, 14, 48):
        s = items[i - 1][0]
        w(f"- **item {i}** — *\"{s[:90]}\"* → {CLASSIFICATION[i][2]}")
    w("")
    w("## 3. O que sobra por leitura estrutural")
    w("")
    w(f"Tirando os {len(trivial)} não-decisões, sobram {len(steps)} passos "
      f"lineares e {len(branches)} itens com ramo. Esses {len(branches)} não são "
      f"{len(branches)} decisões independentes: colapsam em **{len(STRUCTURES)} "
      "estruturas**.")
    w("")
    for st in STRUCTURES:
        w(f"### {st['name']} — {st['kind']}")
        w("")
        w(f"- itens do medidor: {', '.join(str(i) for i in st['items'])}")
        w(f"- ramos: {', '.join(st['branches'])}")
        if st["note"]:
            w(f"- nota: {st['note']}")
        w("")
    w("A premissa da tarefa se confirma, com um ajuste: há **uma** tabela "
      "realmente multi-ramo — a de plataforma — e o resto é checklist linear mais "
      "três portões simples. O mapeamento por tipo de empresa tem três ramos, mas "
      "ilustra um único passo de memória; classificá-lo como tabela ou como "
      "exemplo é chamada de julgamento, e por isso está declarado, não escondido "
      "num contador.")
    w("")
    w("## 4. Por que não ajustei o regex")
    w("")
    w("| cenário de exclusão | contagem | daria |")
    w("|---|---|---|")
    for label, k, v in scenarios:
        w(f"| {label} | {k} | {v} |")
    w("")
    w("Dá para fazer o canário passar excluindo categorias. Mas repare no que "
      "isso é: as categorias foram lidas **deste** vídeo, uma fonte, à mão. "
      "Calibrar o contador contra n=1 até o número bater não produz um medidor — "
      "produz um número que concorda com quem o ajustou. É exatamente o defeito "
      "que o projeto persegue nos outros artefatos, e seria pior aqui, porque "
      "este medidor existe para decidir se vale gastar um corpus inteiro.")
    w("")
    w("## 5. Achado")
    w("")
    w("**A contagem puramente léxica não separa metodologia de discurso, e não "
      "deve ser a métrica que decide.**")
    w("")
    w("Em transcrição de aula falada, `if`, `when`, `should`, `never` e "
      "`make sure` funcionam como conectivo retórico com a mesma frequência com "
      "que funcionam como condição de regra. Nenhum ajuste de vocabulário "
      "resolve isso sem ler a estrutura: a diferença entre *\"If this happens, do "
      "that\"* (definição de automação) e *\"If you're already on Zapier…\"* "
      "(ramo de tabela) não está nas palavras, está no papel que a frase cumpre.")
    w("")
    w("**Consequência prática.** A métrica que decide se uma fonte qualifica "
      "precisa ser publicada como **lista enumerada e auditável** — cada ponto de "
      "decisão nomeado, com o trecho que o sustenta e a estrutura a que pertence, "
      "como nas seções 1 e 3 acima. Um número de regex pode acompanhar como "
      "indício, nunca como veredito.")
    w("")
    w("O que o medidor continua servindo para medir sem ressalva: duração, "
      "palavras, palavras por minuto, limiares numéricos e frameworks nomeados. "
      "São contagens de superfície e é isso que elas dizem ser.")
    w("")
    w("## 6. Estado do PILOT-002")
    w("")
    w("Sem veredito. O canário reprovou, então o instrumento não está apto a "
      "qualificar ou desqualificar o candidato. Qualificar o PILOT-002 exige "
      "enumerar as decisões dele à mão, no formato da seção 3, e comparar "
      "estrutura com estrutura.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"itens: {n} | não-decisões: {len(trivial)} | passos: {len(steps)} | "
          f"ramos: {len(branches)} | estruturas: {len(STRUCTURES)}")
    print(f"canário: {'APROVADO' if canary_pass else 'REPROVADO'} "
          f"(medidor deu {lexical_verdict}, exigido FINA)")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha(OUT)[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
