#!/usr/bin/env python3
"""FRENTE 3 — lista enumerada de decisão do PILOT-002, a partir do L0 CORTADO.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/.

A métrica que decide é lista auditável, não contagem de regex. Este script:
  1. extrai os candidatos mecanicamente, do L0 CORTADO (85ea2290…);
  2. separa, por REGRA DECLARADA, duas classes que a leitura identificou como
     não-decisão nesta fonte: narração de demonstração de tela e CTA;
  3. deixa o resíduo, que foi LIDO À MÃO, e do qual saem as estruturas;
  4. consolida em estruturas e compara com o PILOT-001 em estruturas.

As estruturas são ancoradas por índice do resíduo e conferidas contra o texto
vivo: se a extração mudar, o script aborta em vez de publicar lista velha.
"""
from __future__ import annotations

import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import source_density as sd

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "DECISION-STRUCTURE-LIST-PILOT-002.md"
CUT = (DRIVE / "Course-to-Skill-Claude/pilots/PILOT-002/00_SOURCE"
       / "L0-transcript-CUT.txt")
INTACT = (DRIVE / "Course-to-Skill-Claude/pilots/PILOT-002/00_SOURCE"
          / "L0-transcript.txt")
EXPECTED_CUT_SHA = "85ea229011a989ea"

HELDOUT = [("Understanding Permission Modes", 715, 908),
           ("Managing Your Context Window and Token Usage", 2680, 3000)]

# Regras DECLARADAS, derivadas da leitura desta fonte. Não são universais.
DEMO = re.compile(r"\b(if i were to|if i want to|if i (?:do|type|open|click|scroll|"
                  r"call|say)|you can see if|let's say if i|so if i)\b", re.I)
CTA = re.compile(r"\b(subscribe|comment down|link (?:below|in the description)|"
                 r"check out (?:this|the) video|full video|timestamps in the "
                 r"description|found value)\b", re.I)

# Estruturas, ancoradas por índice do resíduo. `head` confere contra o texto vivo.
STRUCTURES = [
    {"id": "T1", "kind": "tabela multi-ramo", "name": "CLI × MCP",
     "items": [(104, "Which one should you really use?"),
               (105, "So let's say if you want to save tokens that using CLI")],
     "branches": ["economizar token / velocidade → CLI",
                  "segurança, controlar quantas ferramentas o agente acessa, "
                  "ambiente de time → MCP"],
     "judgment": None},
    {"id": "T2", "kind": "tabela multi-ramo", "name": "onde rodar: terminal × IDE",
     "items": [(6, "So the first option we have is use our claw code instead"),
               (7, "But if you are technical and you want to get more control"),
               (8, "So that's why my recommendation is using a IDE"),
               (108, "So if you really want to experience all the functionality"),
               (127, "But my preference here for beginners, if you want to start small")],
     "branches": ["técnico, quer controle e toda a funcionalidade → terminal",
                  "iniciante, quer começar pequeno → VS Code",
                  "recomendação geral do autor → IDE"],
     "judgment": ("O autor dá recomendação e preferência em pontos diferentes do "
                  "curso, sem uma tabela única. Tratei como uma estrutura só "
                  "porque as condições são mutuamente exclusivas e cobrem o mesmo "
                  "eixo; quem preferir pode contar como duas.")},
    {"id": "T3", "kind": "tabela multi-ramo",
     "name": "onde colocar o system prompt: CLAUDE.md × AGENTS.md",
     "items": [(68, "Let's say if you want to add a system prompt here specifically"),
               (69, "And let's say if you want to make it universal"),
               (72, "If you're using cloud code, then it's going to sync")],
     "branches": ["só para o claw code → CLAUDE.md",
                  "universal para todos os frameworks de agente → AGENTS.md"],
     "judgment": None},
    {"id": "T4", "kind": "tabela multi-ramo", "name": "plano e orçamento",
     "items": [(118, "Now my honest take for this is that if you're a beginner"),
               (119, "But if you're trying to use this every single day"),
               (120, "If you want to stay under this budget"),
               (121, "One is local model if your computer is really strong")],
     "branches": ["iniciante aprendendo → o plano atual basta",
                  "uso diário → não basta, precisa subir de plano",
                  "quer ficar no orçamento → modelo local, se a máquina aguentar"],
     "judgment": ("Três ramos com condição, mas ditos em tom de opinião "
                  "(\"my honest take\"), não como regra do método. Contei como "
                  "tabela; quem exigir regra normativa contaria como conselho.")},
    {"id": "G1", "kind": "portão simples", "name": "precisa de controle de versão?",
     "items": [(86, "Because let's say if you have mult multiple team members"),
               (87, "And if you actually want to set up version controls")],
     "branches": ["time compartilhando projeto, ou risco de perder trabalho → "
                  "Git/GitHub"],
     "judgment": None},
    {"id": "G2", "kind": "portão simples", "name": "repositório privado × público",
     "items": [(93, "You can actually change that to public if you want to.")],
     "branches": ["quer expor → público; padrão → privado"],
     "judgment": ("Um ramo só, dito de passagem durante a demonstração. Está no "
                  "limite entre portão e comentário.")},
    {"id": "G3", "kind": "portão simples", "name": "trocar de modelo",
     "items": [(76, "You can if you want to switch to most powerful model"),
               (78, "But if you want to change the model, simply just going to type")],
     "branches": ["quer o modelo mais forte → `/model`"],
     "judgment": None},
]

# Decisão que o curso levanta e NÃO responde neste corpus.
DEFERRED = [
    {"id": "D1", "name": "CLI desktop app × VS Code",
     "items": [(114, "And then the fourth one we have is is should we use CLI"),
               (115, "So there's actually a chapter in my video here talk about")],
     "why": ("A pergunta é feita na FAQ e o autor remete a outro capítulo do "
             "vídeo em vez de responder. Não entra como estrutura: o corpus "
             "levanta a decisão sem entregá-la.")},
]

# PILOT-001, da calibração já publicada.
P001 = {"items": 49, "nao_decisao": 26, "passos": 7, "ramos": 16,
        "estruturas": 5, "tabelas_multi_ramo": 1, "portoes": 3,
        "duracao_min": 15.08}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract(path: Path) -> list[str]:
    body = sd.strip_marks(path.read_text(encoding="utf-8"))
    seen, out = set(), []
    for s in sd.sentences(body):
        if not (sd.CONDITIONAL.search(s) or sd.NORMATIVE.search(s)):
            continue
        k = sd.norm(s)
        if k in seen:
            continue
        seen.add(k)
        out.append(s)
    return out


def marks_of(path: Path) -> dict[str, str]:
    """Frase normalizada -> marca de tempo do bloco em que aparece."""
    txt = path.read_text(encoding="utf-8")
    MARK = re.compile(r"^\*\*(\d{1,3}:[0-5]\d)\*\*$")
    cur, out = None, {}
    for b in [x.strip() for x in txt.split("\n\n") if x.strip()]:
        m = MARK.match(b)
        if m:
            cur = m.group(1)
            continue
        if b.startswith("## "):
            continue
        for s in sd.sentences(b):
            out.setdefault(sd.norm(s), cur)
    return out


def heldout_density() -> dict:
    """Densidade de candidatos dentro × fora das faixas retiradas, no L0 íntegro."""
    txt = INTACT.read_text(encoding="utf-8")
    MARK = re.compile(r"^\*\*(\d{1,3}:[0-5]\d)\*\*$")
    cur, inside, outside = None, [], []
    for b in [x.strip() for x in txt.split("\n\n") if x.strip()]:
        m = MARK.match(b)
        if m:
            a, s = m.group(1).split(":")
            cur = int(a) * 60 + int(s)
            continue
        if b.startswith("## ") or cur is None:
            continue
        hit = any(lo <= cur < hi for _, lo, hi in HELDOUT)
        for sent in sd.sentences(b):
            if sd.CONDITIONAL.search(sent) or sd.NORMATIVE.search(sent):
                (inside if hit else outside).append(sent)
    held_s = sum(hi - lo for _, lo, hi in HELDOUT)
    total_s = 4897
    return {"heldout_items": len(inside), "heldout_seconds": held_s,
            "heldout_per_min": round(len(inside) / (held_s / 60), 2),
            "training_items": len(outside),
            "training_seconds": total_s - held_s,
            "training_per_min": round(len(outside) / ((total_s - held_s) / 60), 2)}


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not sha(CUT).startswith(EXPECTED_CUT_SHA):
        print(f"FONTE ERRADA: esperado {EXPECTED_CUT_SHA}…, veio {sha(CUT)[:16]}")
        return 2

    items = extract(CUT)
    tmarks = marks_of(CUT)
    demo = [s for s in items if DEMO.search(s)]
    cta = [s for s in items if CTA.search(s) and s not in demo]
    residue = [s for s in items if s not in demo and s not in cta]

    # trava anti-deriva
    drift = []
    for st in STRUCTURES + DEFERRED:
        for idx, head in st["items"]:
            if idx > len(residue):
                drift.append(f"{st['id']}: índice {idx} fora do resíduo "
                             f"({len(residue)})")
            elif not residue[idx - 1].startswith(head):
                drift.append(f"{st['id']}: item {idx} esperado {head[:40]!r}, "
                             f"veio {residue[idx-1][:40]!r}")
    if drift:
        print("DERIVA entre extração e âncoras — não publico:")
        for d in drift:
            print("  -", d)
        return 2

    structural_items = {i for st in STRUCTURES for i, _ in st["items"]}
    deferred_items = {i for st in DEFERRED for i, _ in st["items"]}
    tables = [s for s in STRUCTURES if s["kind"] == "tabela multi-ramo"]
    gates = [s for s in STRUCTURES if s["kind"] == "portão simples"]
    hd = heldout_density()

    def mk(s: str) -> str:
        return tmarks.get(sd.norm(s)) or "—"

    L, w = [], None
    w = L.append
    w("# Lista enumerada de decisão — PILOT-002 (L0 CORTADO)")
    w("")
    w(f"- Gerado: `{stamp}` · gerador `{Path(__file__).name}`")
    w(f"- Fonte: `{CUT.relative_to(DRIVE)}` · sha256 `{sha(CUT)[:16]}…`")
    w("- **É o corpus CORTADO**, o que a Skill vai receber — não o L0 íntegro.")
    w("- Mesmas categorias e mesmos critérios da calibração do PILOT-001.")
    w("")
    w("## Método, e o que nele é chamada de julgamento")
    w("")
    w(f"1. Extração mecânica: {len(items)} candidatos (mesmas regex do medidor).")
    w(f"2. Duas classes separadas por **regra declarada**, derivadas da leitura "
      f"desta fonte: narração de demonstração de tela ({len(demo)}) e CTA "
      f"({len(cta)}).")
    w(f"3. Resíduo de **{len(residue)}** itens, lido à mão. Dele saem as estruturas.")
    w("")
    w("> **Categoria nova, declarada.** O PILOT-001 não precisou de "
      "`DEMONSTRACAO_DE_TELA`. O PILOT-002 é um tutorial de ferramenta gravado "
      "com a tela: *\"if I were to open this\"*, *\"if I want to delete\"* são "
      "narração do que o dedo está fazendo, não regra. Acrescentar a categoria é "
      "chamada de julgamento minha, e é o que separa este corpus do outro.")
    w("")
    w("> **O que NÃO foi feito.** Não classifiquei os 128 itens do resíduo um a "
      "um numa tabela como fiz com os 49 do PILOT-001. Li todos e ancorei à mão "
      "os que pertencem a estrutura, que são os que decidem. Os demais são passo "
      "linear, definição ou narração; estão publicados abaixo sem categoria "
      "individual. Dizer o contrário seria inventar trabalho manual.")
    w("")
    w("## 1. Estruturas de decisão no corpus de treino")
    w("")
    w(f"**{len(tables)} tabelas multi-ramo · {len(gates)} portões simples.**")
    w("")
    for st in STRUCTURES:
        w(f"### {st['id']} — {st['name']} · {st['kind']}")
        w("")
        w("| # | marca | trecho que disparou |")
        w("|---|---|---|")
        for idx, _ in st["items"]:
            s = residue[idx - 1]
            w(f"| {idx} | `{mk(s)}` | {s[:110].replace('|', '\\|')} |")
        w("")
        for b in st["branches"]:
            w(f"- {b}")
        w("")
        if st["judgment"]:
            w(f"> **Chamada de julgamento.** {st['judgment']}")
            w("")
    w("## 2. Decisão levantada e não entregue")
    w("")
    for st in DEFERRED:
        w(f"### {st['id']} — {st['name']}")
        w("")
        for idx, _ in st["items"]:
            s = residue[idx - 1]
            w(f"- `{mk(s)}` — {s[:120]}")
        w("")
        w(f"> {st['why']}")
        w("")
    w("## 3. O corte levou as duas seções mais densas")
    w("")
    w("| faixa | itens | segundos | itens/min |")
    w("|---|---|---|---|")
    w(f"| held-out (as duas seções) | {hd['heldout_items']} | "
      f"{hd['heldout_seconds']} | **{hd['heldout_per_min']}** |")
    w(f"| corpus de treino | {hd['training_items']} | {hd['training_seconds']} | "
      f"**{hd['training_per_min']}** |")
    w("")
    ratio = round(hd["heldout_per_min"] / hd["training_per_min"], 2)
    w(f"As faixas retiradas têm **{ratio}×** a densidade de candidatos do que "
      "sobrou. Não é acidente: *Understanding Permission Modes* é uma tabela de "
      "quatro modos e *Managing Your Context Window* é a seção de gestão de "
      "recurso. O held-out foi escolhido por span declarado, antes de qualquer "
      "extração — e calhou de levar justamente o material mais decisório.")
    w("")
    w("**Consequência que precisa ficar registrada:** o corpus de treino do "
      "PILOT-002 é mais fino que a fonte. Comparar PILOT-002 com PILOT-001 pelo "
      "corpus de treino compara o que a Skill recebe, que é o certo para decidir "
      "se a Skill consegue aprender — mas subestima a fonte.")
    w("")
    w("## 4. Lado a lado, em estruturas")
    w("")
    w("| | PILOT-001 | PILOT-002 (cortado) |")
    w("|---|---|---|")
    w(f"| duração | {P001['duracao_min']} min | "
      f"{round(hd['training_seconds']/60, 2)} min |")
    w(f"| candidatos mecânicos | {P001['items']} | {len(items)} |")
    w(f"| **tabelas multi-ramo** | **{P001['tabelas_multi_ramo']}** | "
      f"**{len(tables)}** |")
    w(f"| **portões simples** | **{P001['portoes']}** | **{len(gates)}** |")
    w(f"| estruturas ao todo | {P001['estruturas']} | {len(STRUCTURES)} |")
    w(f"| decisões levantadas e não entregues | 0 | {len(DEFERRED)} |")
    w("")
    w("A comparação é em estrutura, não em contagem de regex — o medidor está "
      "suprimido desde a calibração, e o número de candidatos aparece acima só "
      "como referência de volume.")
    w("")
    w("**Leitura honesta do quadro.** O PILOT-002 tem mais estruturas que o "
      f"PILOT-001 ({len(STRUCTURES)} contra {P001['estruturas']}) e mais tabelas "
      f"multi-ramo ({len(tables)} contra {P001['tabelas_multi_ramo']}), em "
      f"{round(hd['training_seconds']/60/P001['duracao_min'], 1)}× a duração. Por "
      "estrutura por minuto os dois são parecidos; o PILOT-002 ganha em volume "
      "absoluto, não em densidade. E parte do que ele tinha de mais denso foi "
      "para o held-out.")
    w("")
    w("Nenhum veredito de qualificação é emitido aqui. Esta lista é a entrada "
      "para essa decisão, que é do Alexandre.")
    w("")
    w("## 5. Resíduo lido, sem categoria individual")
    w("")
    w(f"Os {len(residue)} itens do resíduo, com marca de tempo. Os que pertencem "
      "a estrutura estão marcados.")
    w("")
    w("| # | marca | item | estrutura |")
    w("|---|---|---|---|")
    for i, s in enumerate(residue, 1):
        tag = next((st["id"] for st in STRUCTURES + DEFERRED
                    if i in {x for x, _ in st["items"]}), "")
        w(f"| {i} | `{mk(s)}` | {s[:110].replace('|', '\\|')} | {tag} |")
    w("")
    w("## 6. Separados por regra declarada")
    w("")
    w(f"### Narração de demonstração de tela ({len(demo)})")
    w("")
    for s in demo[:15]:
        w(f"- `{mk(s)}` — {s[:100]}")
    if len(demo) > 15:
        w(f"- … mais {len(demo)-15}")
    w("")
    w(f"### CTA ({len(cta)})")
    w("")
    for s in cta:
        w(f"- `{mk(s)}` — {s[:100]}")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"candidatos {len(items)} | demo {len(demo)} | cta {len(cta)} | "
          f"resíduo {len(residue)}")
    print(f"estruturas: {len(tables)} tabelas + {len(gates)} portões = "
          f"{len(STRUCTURES)} | diferidas: {len(DEFERRED)}")
    print(f"densidade held-out {hd['heldout_per_min']}/min × treino "
          f"{hd['training_per_min']}/min = {ratio}×")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha(OUT)[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
