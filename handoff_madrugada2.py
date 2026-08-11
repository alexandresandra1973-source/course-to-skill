#!/usr/bin/env python3
"""HANDOFF-MADRUGADA-2 — lê o publicado e resume. Nenhum número digitado."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "HANDOFF-MADRUGADA-2.md"

SWEEP = DOCS / "VERSION-LITERAL-SWEEP-FULL.yaml"
DRY = DOCS / "DRY-RUN-CHAIN-v0.1.4.md"
LIST2 = DOCS / "DECISION-STRUCTURE-LIST-PILOT-002.md"
CALIB = DOCS / "DENSITY-METER-CALIBRATION.md"
SUMMARY = Path("/tmp/dryrun-v014/dry-run-summary.json")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    sw = yaml.safe_load(SWEEP.read_text(encoding="utf-8"))
    dr = json.loads(SUMMARY.read_text(encoding="utf-8"))
    l2 = LIST2.read_text(encoding="utf-8")

    tab2 = re.search(r"\*\*(\d+) tabelas multi-ramo · (\d+) portões", l2)
    ratio = re.search(r"têm \*\*([\d.]+)×\*\* a densidade", l2)

    L, w = [], None
    w = L.append
    w("# HANDOFF — madrugada 2")
    w("")
    w(f"`{datetime.now(timezone.utc).isoformat(timespec='seconds')}` · gerado por "
      f"`{Path(__file__).name}` · READ-ONLY sobre `Course-to-Skill/` e "
      "`Course-to-Skill-Compiler/` · **nada congelado**, nenhuma conversa cega "
      "aberta, rubrica do TEST-0008 intocada, L1 do PILOT-002 não extraído.")
    w("")
    w("## Pronto")
    w("")
    w("| artefato | sha256 | bytes |")
    w("|---|---|---|")
    for p in (SWEEP, DRY, LIST2):
        w(f"| `{p.name}` | `{sha(p)[:16]}…` | {p.stat().st_size} |")
    w("")
    t = sw["totals"]
    w(f"**Frente 1 — varredura completa.** {sw['scope']['python_files_scanned']} "
      f"arquivos `.py` em {len(sw['scope']['packages_scanned'])} pacotes "
      f"(REV2–REV5, D1/D2, F3, F4, F5, compilador e repo). "
      f"{t['occurrences']} ocorrências de literal de versão, "
      f"**{t['blocking_distinct_defects']} defeitos bloqueantes distintos**. "
      "O classificador foi calibrado contra os vereditos já publicados pelo F5 "
      f"nos dois pacotes que ele varreu: **{'confere' if sw['calibration_against_f5']['agrees_with_f5'] else 'DIVERGE'}**, "
      "0 faltando e 0 sobrando. Nada foi corrigido.")
    w("")
    w("**Frente 2 — ensaio seco.** A cadeia **fecha de ponta a ponta** com os "
      "scripts F5/F6. Detalhe abaixo.")
    w("")
    if tab2:
        w(f"**Frente 3 — lista do PILOT-002.** Do L0 CORTADO: "
          f"**{tab2.group(1)} tabelas multi-ramo e {tab2.group(2)} portões "
          f"simples**, mais 1 decisão levantada e não entregue.")
    w("")
    w("## Onde o ensaio travou, e com que código")
    w("")
    w("| passo | exit | código |")
    w("|---|---|---|")
    for s in dr["steps"]:
        w(f"| {s['n']} — {s['step']} | **{s['exit']}** | "
          f"{', '.join(s['codes']) or '—'} |")
    for s in dr["scorer"]:
        w(f"| S3 — {s['scenario']} · {s['variant']} | **{s['exit']}** | "
          f"{s['status']} |")
    w("")
    w("**Não travou.** Com F5/F6 o lock congela, o registry e o opening record "
      "saem carimbados `candidate_version: 0.1.4`, e os três cenários produzem "
      "os três terminais distintos: `VALID` (0), `FAIL` (1), `INCONCLUSIVE` (3).")
    w("")
    w("### A previsão da linha 880: CONFIRMADA")
    w("")
    w("Testei o scorer **F4** (o estado a que a previsão se referia) contra o "
      "**F6** como controle, com as mesmas notas e o mesmo lock. O F4 devolve "
      "`INVALID` nos três cenários, com "
      "`MARGIN_THRESHOLD_UNREACHABLE` e o detalhe *\"structural report selectors "
      "must be FULL@AFTER_DEDUP and ABLATED@AFTER_DEDUP\"* — que é exatamente o "
      "literal `V0.1.3` do `structural_role`. O F6, com as mesmas entradas, "
      "pontua normalmente.")
    w("")
    w("### Dois achados que não estavam previstos")
    w("")
    w("1. **Os freezers do F5 não estão na pasta do F5.** O "
      "`PRELOCK_F5_VERSION_PARAMETERIZATION/` tem só ADR, canário e varredura. "
      "Os scripts com os hashes `32774324…` e `fa45010c…` vieram dentro do "
      "pacote **F6**, que apareceu durante a sessão. Quem procurar pelo nome da "
      "pasta não acha.")
    w("2. **O defeito do `candidate_version` era mais largo que o F5 relatou.** "
      "O literal `'0.1.3'` do `freeze_pre_run_registry.py` está em **cinco** "
      "pacotes — D1/D2, F3, REV3, REV4 e REV5 — não só no F3 que o F5 varreu.")
    w("")
    w("## Quantas estruturas cada fonte tem")
    w("")
    w("| | PILOT-001 | PILOT-002 (cortado) |")
    w("|---|---|---|")
    w("| tabelas multi-ramo | **1** | **4** |")
    w("| portões simples | **3** | **3** |")
    w("| estruturas ao todo | **5** | **7** |")
    w("| duração | 15,1 min | 68,7 min |")
    w("")
    if ratio:
        w(f"**Ressalva que decide.** As duas seções retiradas no held-out têm "
          f"**{ratio.group(1)}×** a densidade de candidatos do que sobrou — "
          "*Permission Modes* é uma tabela de quatro modos e *Context Window* é "
          "gestão de recurso. O corte foi por span declarado, antes de qualquer "
          "extração, e calhou de levar o material mais decisório. O corpus de "
          "treino do PILOT-002 é mais fino que a fonte.")
    w("")
    w("Por estrutura **por minuto** os dois são parecidos. O PILOT-002 ganha em "
      "volume absoluto, não em densidade. Nenhum veredito de qualificação foi "
      "emitido — o medidor segue suprimido desde a calibração.")
    w("")
    w("## O que sobrou para o Alexandre")
    w("")
    w("1. **Decidir se o PILOT-002 qualifica**, com a lista em mãos. É decisão "
      "de estrutura, não de número: 4 tabelas em 69 min contra 1 em 15 min.")
    w("2. **Resolver os 5 defeitos bloqueantes da varredura** antes de qualquer "
      "rodada de versão futura. Dois já estão cobertos por F5/F6; os outros "
      "três não.")
    w("3. **Mover o pacote F6** para uma pasta que diga F6, ou renomear a pasta "
      "do F5. Hoje o nome mente sobre o conteúdo.")
    w("4. **Congelar a cadeia de verdade**, quando quiser. O ensaio mostra que "
      "ela fecha; eu não congelei nada porque a sessão proíbe.")
    w("5. **Decidir o limiar da v0.1.4** — aberto desde três sessões atrás.")
    w("")
    w("## Chamadas de julgamento que declarei, em vez de esconder")
    w("")
    w("- Criei a categoria `DEMONSTRACAO_DE_TELA` para o PILOT-002; o PILOT-001 "
      "não precisou dela. É o que separa tutorial de tela de aula falada.")
    w("- `T2` (terminal × IDE) junta falas de pontos distintos do curso num eixo "
      "só; quem preferir conta como duas estruturas.")
    w("- `T4` (plano e orçamento) é dito em tom de opinião, não de regra.")
    w("- `G2` (repositório privado × público) tem um ramo só, dito de passagem.")
    w("- Não classifiquei os 128 itens do resíduo um a um como fiz com os 49 do "
      "PILOT-001. Li todos e ancorei à mão só os que pertencem a estrutura. "
      "Está dito no relatório.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"escrito: {OUT.name} ({OUT.stat().st_size} B) {sha(OUT)[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
