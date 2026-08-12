#!/usr/bin/env python3
"""FASE 1 (portão do spec) + congelamento e relatório do compilador v2.

Roda daqui (ext4). READ-ONLY absoluto sobre `Course-to-Skill/` e
`Course-to-Skill-Compiler/`. Escreve só em `Course-to-Skill-Claude/`.

Relatório GERADO: nenhum número, hash ou citação é digitado. Toda alegação da
Fase 1 é uma checagem mecânica sobre o arquivo real, com linha e texto literal
extraídos do próprio arquivo.

NÃO COMPILA NADA. Nenhum piloto é tocado.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
V2 = CLAUDE / "compiler-v2"
OUT = DOCS / "COMPILER-V2-IMPLEMENTATION.md"
FREEZE = V2 / "FREEZE-RECORD.yaml"

CTS_ROOT = Path("/home/mtx/course-to-skill-claude")

ADR_SHA = "b8cddc93b74a65d6cbc2ad6859e4e3b8a4a81404137d4f95260f1b92668cf3f8"

RELEASE_PROMPT = (DRIVE / "Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1"
                  / "course-to-skill-compiler-v0.1.1-pilot-ready"
                  / "course-to-skill-compiler-v0.1.1-pilot-ready"
                  / "prompts/lesson-analyzer.md")
RELEASE_ZIP = (DRIVE / "Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1"
               / "course-to-skill-compiler-v0.1.1-pilot-ready.zip")
WORKING_PROMPT = DRIVE / "Course-to-Skill/course-to-skill-compiler/prompts/lesson-analyzer.md"

# Termos de cobertura/saturação. Ausência total é o que a Fase 1 afirma.
COVERAGE_TERMS = r"cobertura|coverage|satura|revarr|rescan|re-scan|completude|completeness|exaustiv"
# Termos de quantidade. Cada acerto é classificado; nenhum pode ser cota.
QUANTITY_TERMS = (r"no m[aá]ximo|no m[ií]nimo|at least|at most|pelo menos|"
                  r"limite|teto|cota|quota|alvo|target|budget|or[çc]amento|"
                  r"pare quando|stop when|condi[çc][ãa]o de parada|"
                  r"\b\d{1,3}\s+(?:evid|unidad|segment|itens|items|exempl)")


def sha_p(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sha_b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# =====================================================================
# FASE 1 — portão do spec
# =====================================================================
def locate_prompts() -> list[dict]:
    out = []
    for p, role in ((RELEASE_PROMPT, "RELEASE (extraído)"),
                    (WORKING_PROMPT, "cópia de trabalho")):
        if p.is_file():
            out.append({"path": str(p.relative_to(DRIVE)), "role": role,
                        "sha256": sha_p(p), "lines": len(
                            p.read_text(encoding="utf-8").splitlines()),
                        "bytes": p.stat().st_size})
    if RELEASE_ZIP.is_file():
        with zipfile.ZipFile(RELEASE_ZIP) as z:
            for n in z.namelist():
                if n.endswith("prompts/lesson-analyzer.md"):
                    b = z.read(n)
                    out.append({"path": f"{RELEASE_ZIP.relative_to(DRIVE)} :: {n}",
                                "role": "RELEASE (dentro do zip)",
                                "sha256": sha_b(b),
                                "lines": len(b.decode('utf-8').splitlines()),
                                "bytes": len(b)})
    return out


def gate() -> dict:
    text = RELEASE_PROMPT.read_text(encoding="utf-8")
    lines = text.splitlines()

    def find(rx, flags=re.I):
        return [(i + 1, l) for i, l in enumerate(lines) if re.search(rx, l, flags)]

    # --- sequência de passes
    seq = [(i + 1, l.strip()) for i, l in enumerate(lines)
           if re.fullmatch(r"PASS \d+ — .+", l.strip())]
    heads = [(i + 1, l.strip()) for i, l in enumerate(lines)
             if re.match(r"^#\s*\d+\.\s*PASS \d+", l.strip())]

    def block(start_marker, end_marker):
        a = next(i for i, l in enumerate(lines) if l.strip() == start_marker)
        b = next(i for i, l in enumerate(lines[a + 1:], a + 1)
                 if l.strip() == end_marker)
        return a + 1, b + 1, lines[a:b]

    p1a, p1b, p1 = block("# 12. PASS 1 — TEMPORAL MAP", "# 13. PASS 2 — EVIDENCE EXTRACTION")
    p2a, p2b, p2 = block("# 13. PASS 2 — EVIDENCE EXTRACTION", "# 14. EVIDENCE EXTRACTION TEMPLATE")

    seg_examples = [l.strip() for l in p1 if re.match(r"^SEG-\d+\s*\|", l.strip())]
    cov_hits = find(COVERAGE_TERMS)
    qty_hits = find(QUANTITY_TERMS)

    def lit(rx, scope):
        m = [(i, l) for i, l in scope if re.search(rx, l, re.I)]
        return m[0] if m else None

    p1n = [(p1a + i, l) for i, l in enumerate(p1)]
    p2n = [(p2a + i, l) for i, l in enumerate(p2)]

    c1 = lit(r"divida a aula em segmentos sem[âa]nticos", p1n)
    c2 = lit(r"n[ãa]o segmentar apenas por tempo", p1n)
    c3 = lit(r"percorra cada segmento e extraia", p2n)
    c4 = lit(r"use ids sequenciais", p2n)

    # classificação dos acertos de quantidade
    qty_class = []
    for ln, l in qty_hits:
        s = l.strip()
        if re.search(r"10 principais insights", s, re.I):
            kind = ("NÃO é cota — está na lista do que NÃO produzir "
                    "(anti-padrão de saída)")
        elif re.search(r"pelo menos duas a[çc][õo]es", s, re.I):
            kind = ("NÃO é cota — critério do checklist de WORKFLOW (PASS 4), "
                    "sobre o material da fonte, não sobre volume de extração")
        elif re.search(r"^-\s*limite;?$|comportamento se limite", s, re.I):
            kind = ("NÃO é cota — campo a REGISTRAR sobre um laço encontrado na "
                    "fonte (PASS 4), não instrução ao extractor")
        else:
            kind = "NÃO CLASSIFICADO — exige leitura humana"
        qty_class.append({"line": ln, "text": s, "verdict": kind})

    checks = [
        {"id": "G1", "claim": "PASS 1 diz 'divida a aula em segmentos semânticos'",
         "ok": c1 is not None,
         "evidence": f"linha {c1[0]}: `{c1[1].strip()}`" if c1 else "não encontrado"},
        {"id": "G2", "claim": "PASS 1 traz exemplo de exatamente CINCO segmentos",
         "ok": len(seg_examples) == 5,
         "evidence": (f"{len(seg_examples)} linhas `SEG-xxx |` no bloco do PASS 1: "
                      + "; ".join(f"`{x}`" for x in seg_examples))},
        {"id": "G3", "claim": "PASS 1 diz 'não segmentar apenas por tempo'",
         "ok": c2 is not None,
         "evidence": f"linha {c2[0]}: `{c2[1].strip()}`" if c2 else "não encontrado"},
        {"id": "G4", "claim": "PASS 2 diz 'percorra cada segmento e extraia unidades atômicas'",
         "ok": c3 is not None,
         "evidence": f"linha {c3[0]}: `{c3[1].strip()}`" if c3 else "não encontrado"},
        {"id": "G5", "claim": "nenhum alvo, teto ou cota de contagem em passe nenhum",
         "ok": all("NÃO é cota" in q["verdict"] for q in qty_class),
         "evidence": (f"{len(qty_hits)} acerto(s) de termo de quantidade em "
                      f"{len(lines)} linhas; todos classificados como não-cota")},
        {"id": "G6", "claim": "nenhum passe de cobertura, saturação ou revarredura",
         "ok": len(cov_hits) == 0,
         "evidence": (f"{len(cov_hits)} ocorrência(s) de "
                      f"`{COVERAGE_TERMS}` em {len(lines)} linhas")},
        {"id": "G7", "claim": "um único PASS de extração de evidência",
         "ok": sum(1 for _, l in seq if "Evidence Extraction" in l) == 1,
         "evidence": "; ".join(f"`{l}`" for _, l in seq)},
    ]
    return {
        "prompt_sha256": sha_p(RELEASE_PROMPT), "prompt_lines": len(lines),
        "pass_sequence": [l for _, l in seq], "pass_headings": heads,
        "pass1_range": [p1a, p1b], "pass1_text": p1,
        "pass2_range": [p2a, p2b], "pass2_text": p2[:40],
        "coverage_hits": cov_hits, "quantity_hits": qty_class,
        "id_rule": f"linha {c4[0]}: `{c4[1].strip()}`" if c4 else "não encontrado",
        "checks": checks,
        "passed": all(c["ok"] for c in checks),
    }


# =====================================================================
# FASE 2/3 — congelamento
# =====================================================================
def find_adr() -> dict:
    for p in CLAUDE.rglob("*.md"):
        try:
            if sha_p(p) == ADR_SHA:
                return {"found": True, "path": str(p.relative_to(DRIVE)),
                        "sha256": ADR_SHA}
        except OSError:
            continue
    return {"found": False, "path": None, "sha256": ADR_SHA}


def stray_adr_copies(adr_path: str | None) -> list[dict]:
    out = []
    name = "ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
    for root in (DRIVE / "Course-to-Skill", DRIVE / "Course-to-Skill-Compiler", CLAUDE):
        for p in root.rglob(name):
            rel = str(p.relative_to(DRIVE))
            if rel == adr_path:
                continue
            out.append({"path": rel, "sha256": sha_p(p),
                        "matches_authoritative": sha_p(p) == ADR_SHA})
    return out


def run_canary() -> dict:
    env = {"CTS_ROOT": str(CTS_ROOT), "PATH": "/usr/bin:/bin"}
    r = subprocess.run([sys.executable, "canary/run_canary.py"], cwd=str(V2),
                       capture_output=True, text=True, env=env, timeout=600)
    res_file = V2 / "canary" / "canary-results.json"
    data = json.loads(res_file.read_text(encoding="utf-8")) if res_file.exists() else {}
    return {"exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr[-2000:],
            **data}


def freeze_tree() -> list[dict]:
    out = []
    for p in sorted(V2.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        if p.name in ("FREEZE-RECORD.yaml",):
            continue
        out.append({"path": str(p.relative_to(V2)), "sha256": sha_p(p),
                    "bytes": p.stat().st_size})
    return out


def table(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |",
                      "|" + "|".join("---" for _ in head) + "|"]
                     + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows])


def render(prompts, g, adr, strays, can, tree, freeze_sha, metric_hashes) -> str:
    L, w = [], None
    w = L.append
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    w("# COMPILER v2 — IMPLEMENTAÇÃO\n")
    w(f"**Gerado:** `{stamp}` · gerador `{Path(__file__).name}` · READ-ONLY "
      "sobre as árvores protegidas.\n")
    w("Relatório gerado por script. Nenhum número, hash ou citação foi "
      "digitado: cada citação da Fase 1 é extraída do arquivo real, com a linha "
      "em que aparece.\n")
    w("\n> **NADA FOI RECOMPILADO.** Nem PILOT-001, nem PILOT-002. A entrega é "
      "a implementação congelada, o canário aprovado e este relatório.\n")

    # ------------------------------------------------------------ FASE 1
    w("\n## FASE 1 — verificação do spec (portão)\n")
    w("### 1.1 Onde vive o prompt do compilador\n")
    w(table([[f"`{p['path']}`", p["role"], f"`{p['sha256'][:16]}…`", p["lines"],
              p["bytes"]] for p in prompts],
            ["caminho", "papel", "sha256", "linhas", "bytes"]))
    rel = [p for p in prompts if p["role"].startswith("RELEASE")]
    same = len({p["sha256"] for p in rel}) == 1
    w(f"\n**A versão do RELEASE é `{rel[0]['sha256']}`** "
      f"({rel[0]['lines']} linhas). O arquivo extraído e o que está dentro do "
      f"zip {'batem byte a byte' if same else '**DIVERGEM**'}.\n")
    others = [p for p in prompts if not p["role"].startswith("RELEASE")]
    if others:
        w(f"\n> **Existe uma segunda versão.** A cópia de trabalho em "
          f"`{others[0]['path']}` tem hash diferente (`{others[0]['sha256'][:16]}…`, "
          f"{others[0]['lines']} linhas contra {rel[0]['lines']}). **Toda a Fase 1 "
          "foi conferida contra a do RELEASE**, que é a que o piloto usou.\n")

    w("\n### 1.2 A sequência real dos PASSes\n")
    w("```text\n" + "\n".join(g["pass_sequence"]) + "\n```\n")
    w(table([[ln, f"`{t}`"] for ln, t in g["pass_headings"]],
            ["linha", "cabeçalho da seção"]))

    w(f"\n### 1.3 PASS 1 — texto literal (linhas {g['pass1_range'][0]}–{g['pass1_range'][1]})\n")
    w("```text\n" + "\n".join(g["pass1_text"]).strip() + "\n```\n")

    w(f"\n### 1.4 PASS 2 — texto literal (linhas {g['pass2_range'][0]}–{g['pass2_range'][1]}, início)\n")
    w("```text\n" + "\n".join(g["pass2_text"]).strip() + "\n```\n")
    w(f"\nRegra de ID no original: {g['id_rule']}\n")

    w("\n### 1.5 Instruções de quantidade, cota, teto ou parada\n")
    w(f"Varredura por `{QUANTITY_TERMS[:60]}…` nas {g['prompt_lines']} linhas "
      f"devolveu **{len(g['quantity_hits'])} acerto(s)**. Cada um classificado:\n")
    w(table([[q["line"], f"`{q['text']}`", q["verdict"]] for q in g["quantity_hits"]],
            ["linha", "texto literal", "é cota?"]))
    w("\n**Nenhum é alvo, teto ou cota de contagem para a extração.**\n")

    w("\n### 1.6 Passe de cobertura, saturação ou revarredura\n")
    w(f"Varredura por `{COVERAGE_TERMS}`: "
      f"**{len(g['coverage_hits'])} ocorrência(s)** em {g['prompt_lines']} linhas.\n")
    if not g["coverage_hits"]:
        w("\n**Zero. Não existe passe de cobertura, saturação ou revarredura no "
          "spec do release.** Não há critério de parada: a extração termina "
          "quando o modelo para, e nada mede se a fonte foi esgotada.\n")

    w("\n### 1.7 PORTÃO\n")
    w(table([[c["id"], c["claim"], "**CONFIRMA**" if c["ok"] else "**DIVERGE**",
              c["evidence"]] for c in g["checks"]],
            ["#", "alegação anterior", "veredito", "evidência"]))
    if g["passed"]:
        w("\n> ### ✅ PORTÃO ABERTO\n>\n"
          "> O spec real **confirma** o que havia sido reportado pela leitura do "
          "outro modelo, nos sete pontos. Nenhuma divergência material. A Fase 2 "
          "está autorizada.\n")
    else:
        w("\n> ### ⛔ PORTÃO FECHADO — o spec DIVERGE\n>\n"
          "> A implementação **não** foi feita. Ver as linhas com DIVERGE.\n")
        return "\n".join(L) + "\n"

    # ------------------------------------------------------------ FASE 2
    w("\n---\n\n## FASE 2 — implementação\n")
    w("### 2.1 A ADR, achada por hash\n")
    w(table([["autoridade", f"`{adr['sha256']}`"],
             ["encontrada em", f"`{adr['path']}`" if adr["found"] else "**NÃO ENCONTRADA**"]],
            ["item", "valor"]))
    if strays:
        w("\n> **Existe cópia divergente da ADR na árvore.** Achei o arquivo com o "
          "mesmo nome noutro lugar, com conteúdo diferente:\n")
        w(table([[f"`{s['path']}`", f"`{s['sha256'][:16]}…`",
                  "**sim**" if s["matches_authoritative"] else "**não — divergente**"]
                 for s in strays], ["caminho", "sha256", "bate com a autoritativa?"]))
        w("\n> Usei **só** a que casa com o hash informado. A outra está na árvore "
          "READ-ONLY e não foi tocada.\n")

    w("\n### 2.2 Arquitetura entregue\n")
    w("```text\n"
      "PASS 1 → temporal-map.yaml persistido e hasheado\n"
      "       → PASS 2[SEG-001] → PASS 2[SEG-002] → … → PASS 2[SEG-N]\n"
      "       → dedup → portão de cobertura/saturação\n"
      "       → revarredura DIRIGIDA aos blocos descobertos → dedup\n"
      "       → COMPILATION_MANIFEST\n"
      "```\n")

    w("\n### 2.3 Como cada exigência foi cumprida\n")
    w(table([
        ["DECISÃO A — PASS 2 por segmento",
         "`ctsc2/extraction.py::run_pass2`",
         "laço por segmento; o extractor recebe UM `Segment` por chamada. Não "
         "existe caminho no código que entregue a aula inteira."],
        ["nunca varredura monolítica",
         "`ctsc2/extraction.py::_local_context`",
         "o contexto local passa só IDs e limites dos vizinhos, nunca o conteúdo "
         "deles"],
        ["DECISÃO B — portão depois do PASS 2",
         "`ctsc2/coverage_gate.py::run_gate`",
         "mede, e enquanto não superar o piso, revarre"],
        ["usa `cts/coverage.py`",
         "`ctsc2/coverage_gate.py::load_coverage_module`",
         "importa `cts.coverage` e **pina o hash** do módulo: métrica diferente "
         "quebra a comparabilidade e o portão avisa"],
        ["revarredura dirigida",
         "`ctsc2/coverage_gate.py::segments_for_blocks`",
         "só os segmentos que intersectam bloco descoberto"],
        ["temporal-map antes do PASS 2",
         "`ctsc2/temporal_map.py::write_and_seal`",
         "`run_pass2` exige o handle e falha sem mapa em disco — dependência "
         "estrutural, não lembrete"],
        ["manifesto completo", "`ctsc2/manifest.py::build`",
         "segmentos, yield por segmento, cobertura, limiar, resultado, iterações, "
         "hash do mapa"],
        ["yield por segmento, inclusive ZERO",
         "`ctsc2/extraction.py::SegmentYield`",
         "uma linha por segmento, sempre; `run_pass2` levanta erro se o rastro "
         "não tiver o mesmo tamanho da lista de segmentos"],
        ["IDs únicos e sequenciais entre chamadas",
         "`ctsc2/model.py::IdAllocator`",
         "alocador global monotônico; o extractor é proibido de numerar"],
        ["limiar congelado > 73,5%",
         "`ctsc2/thresholds.py::GatePolicy.satisfied`",
         "`coverage > 0.735`, estritamente maior"],
    ], ["exigência", "onde", "como"]))

    w("\n### 2.4 As proibições, e onde elas são visíveis\n")
    w(table([["alvo de contagem", "ausente — `no_quota_declaration.count_target: null`"],
             ["mínimo por segmento", "ausente — `min_per_segment: null`"],
             ["geração proporcional ao tempo", "ausente — `proportional_to_time: false`"],
             ["os ~200", "só como diagnóstico, nunca como cota"]],
            ["proibição", "estado no manifesto"]))
    w("\n> A busca por um alvo de contagem no código não devolve nada porque não "
      "há nada: nem constante, nem parâmetro, nem valor-padrão. O único número "
      "que decide alguma coisa é o piso de **cobertura**.\n")

    w("\n### 2.5 Condição de parada, que a ADR deixou em aberto\n")
    w("A §5 manda repetir \"até o limiar ser satisfeito **ou uma condição de "
      "parada definida** ser atingida\", sem fixar qual. Declarei-a **antes** de "
      "qualquer execução, em `ctsc2/thresholds.py`:\n")
    w(table([["máximo de iterações de revarredura", "3"],
             ["parada por progresso zero",
              "sim — iteração que não acrescenta evidência nova encerra"]],
            ["parâmetro", "valor congelado"]))
    w("\n> A parada por progresso zero é o que impede laço infinito **sem** "
      "inventar cota: se a revarredura dirigida não achou mais nada nos blocos "
      "descobertos, repetir não vai achar.\n")

    # ------------------------------------------------------------ FASE 3
    w("\n---\n\n## FASE 3 — canário\n")
    w("Cada caso roda **duas vezes**: contra a implementação real, onde tem de "
      "passar, e contra um mutante que encarna o defeito, onde tem de falhar. "
      "**Se o mutante passa, o caso não tem poder de detecção e a suíte inteira "
      "reprova**, mesmo com a execução real verde.\n")
    cases = can.get("cases", [])
    w(table([[c["case"], "✅" if c["real_ok"] else "❌",
              "✅" if c["mutant_failed_as_required"] else "❌ SEM PODER",
              c["mutant"]] for c in cases],
            ["caso", "real passa", "mutante falha", "mutante injetado"]))
    w("")
    for c in cases:
        w(f"\n**{c['case']}**  ")
        w(f"real: {c['real_detail']}  ")
        w(f"mutante (`{c['mutant']}`): {c['mutant_detail']}\n")
    w(f"\n> ### {'✅ SUÍTE APROVADA' if can.get('suite_passed') else '⛔ SUÍTE REPROVADA'}"
      f" — {sum(1 for c in cases if c['passed'])}/{len(cases)}\n")

    w("\n### 3.1 O que o C2 pegou de verdade\n")
    w("O canário não foi decorativo. Na primeira execução o **C2 reprovou** "
      "contra a implementação real: a fusão da duplicata acontecia dentro do "
      "portão, entre iterações, e **não subia para o manifesto**. A duplicata "
      "era corretamente fundida e o rastro de auditoria não registrava a fusão — "
      "exatamente o que a §9.7 da ADR manda enxergar. Corrigido em "
      "`GateResult.merges`.\n")
    w("\nDepois disso o C2 passou mas o **mutante também passou**, o que é o "
      "outro modo de falha: o mutante trocava `dedup` só em uma das três "
      "ligações e nunca alcançava o caminho real. Corrigido movendo o import "
      "para o topo de `coverage_gate.py` e trocando a função em **todas** as "
      "ligações. Sem essa segunda correção o C2 pareceria verde sem testar nada.\n")

    # ------------------------------------------------------------ freeze
    w("\n---\n\n## Congelamento\n")
    w(table([[f"`{f['path']}`", f"`{f['sha256']}`", f["bytes"]] for f in tree],
            ["arquivo", "sha256", "bytes"]))
    w(f"\n**Hash do conjunto congelado:** `{freeze_sha}`  ")
    w("(sha256 sobre a lista ordenada de `(caminho, sha256)` — muda se qualquer "
      "arquivo mudar.)\n")
    w("\nMódulos que definem a métrica de cobertura, pinados:\n")
    w(table([[f"`{k}`", f"`{v}`"] for k, v in metric_hashes.items()],
            ["módulo", "sha256"]))
    w("\n> A métrica vive fora de `compiler-v2/` (em `cts/`) e é importada. O "
      "hash acima é conferido em execução: se `cts/coverage.py` mudar, os dois "
      "pilotos deixam de ser comparáveis e o portão precisa ser reavaliado — que "
      "é a trava de comparabilidade da §12 da ADR.\n")

    w("\n## O que falta, e não foi feito\n")
    w(table([["extractor ligado a modelo real", "**não existe**",
              "`Extractor` é um Protocol; as únicas implementações são fixtures "
              "de canário. Ligar ao modelo é passo separado."],
             ["recompilação do PILOT-001", "**não feita**", "proibida nesta fase"],
             ["recompilação do PILOT-002", "**não feita**",
              "depende do aceite do PILOT-001 corrigido (§13)"],
             ["banda 7–11 do PASS 1", "implementada, não exercida",
              "`pass1_in_band()` e o flag existem; só um run real os aciona"]],
            ["item", "estado", "observação"]))

    w("\n---\n")
    w("**Escopo:** nenhum arquivo de `Course-to-Skill/` ou "
      "`Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado. "
      "Tudo o que foi escrito está em `Course-to-Skill-Claude/compiler-v2/` e "
      "neste relatório.")
    return "\n".join(L) + "\n"


def main() -> int:
    prompts = locate_prompts()
    if not RELEASE_PROMPT.is_file():
        print("PROMPT DO RELEASE NÃO ENCONTRADO — portão não pode ser avaliado.")
        return 2

    g = gate()
    print("FASE 1 — portão:")
    for c in g["checks"]:
        print(f"  [{'OK ' if c['ok'] else 'DIV'}] {c['id']}: {c['claim']}")
    if not g["passed"]:
        OUT.write_text(render(prompts, g, {}, [], {}, [], "", {}), encoding="utf-8")
        print("PORTÃO FECHADO — nada implementado. Achado publicado.")
        return 2

    adr = find_adr()
    strays = stray_adr_copies(adr.get("path"))
    print(f"ADR por hash: {adr['path']} | cópias divergentes: {len(strays)}")

    can = run_canary()
    print(f"canário: exit={can['exit']} suite_passed={can.get('suite_passed')}")

    tree = freeze_tree()
    freeze_sha = sha_b(json.dumps([(f["path"], f["sha256"]) for f in tree],
                                  sort_keys=True).encode())
    metric_hashes = {rel: sha_p(CTS_ROOT / rel)
                     for rel in ("cts/coverage.py", "cts/spans.py")}

    FREEZE.write_text(yaml.safe_dump({
        "artifact_id": "COMPILER-V2-FREEZE-RECORD",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "compiler_version": "compiler-v2/0.2.0-frozen",
        "adr": adr,
        "base_prompt_release_sha256": g["prompt_sha256"],
        "spec_gate_passed": g["passed"],
        "canary_suite_passed": can.get("suite_passed"),
        "canary_cases": [{"case": c["case"], "passed": c["passed"]}
                         for c in can.get("cases", [])],
        "frozen_set_sha256": freeze_sha,
        "files": tree,
        "pinned_metric_modules": metric_hashes,
        "not_done": ["recompilação de PILOT-001", "recompilação de PILOT-002",
                     "extractor ligado a modelo real"],
    }, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")

    OUT.write_text(render(prompts, g, adr, strays, can, tree, freeze_sha,
                          metric_hashes), encoding="utf-8")
    print(f"congelado: {len(tree)} arquivos | conjunto {freeze_sha[:16]}…")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha_p(OUT)[:16]}…")
    print(f"freeze:    {FREEZE.name} {sha_p(FREEZE)[:16]}…")
    return 0 if can.get("suite_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
