#!/usr/bin/env python3
"""HANDOFF-MADRUGADA — lê o que foi publicado e resume. Nenhum número digitado."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "HANDOFF-MADRUGADA.md"

SC = DOCS / "STRUCTURAL-CEILING-REPORT-v0.1.4.yaml"
PROV = DOCS / "BASELINE-PROVENANCE-v0.1.4.yaml"
RUB = DOCS / "TEST-0008-RUBRIC-DRAFT-v0.1.4.yaml"
SUM = DOCS / "BASELINE-SUMMARY-v0.1.4.md"
T8 = DOCS / "TEST-0008-METRICS-DISCREPANCY.md"
DUR = DOCS / "LESSON-DURATION-AUDIT-v0.1.4.md"
BRR = DOCS / "BLIND_RUN_READY-v0.1.4"

REPO = Path(__file__).parent


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    d = yaml.safe_load(SC.read_text(encoding="utf-8"))
    pv = yaml.safe_load(PROV.read_text(encoding="utf-8"))
    rb = yaml.safe_load(RUB.read_text(encoding="utf-8"))
    c = pv["counts"]
    cond = pv["conditions_b3"]

    L, w = [], None
    w = L.append
    w("# HANDOFF — sessão de madrugada")
    w("")
    w(f"`{datetime.now(timezone.utc).isoformat(timespec='seconds')}` · gerado por "
      f"`{Path(__file__).name}` · READ-ONLY sobre `Course-to-Skill/` e "
      "`Course-to-Skill-Compiler/` · nada congelado, nenhuma conversa aberta.")
    w("")
    w("## 1. Pronto")
    w("")
    w("| artefato | sha256 | bytes |")
    w("|---|---|---|")
    for p in (SC, SUM, PROV, RUB, T8, DUR):
        w(f"| `{p.name}` | `{sha(p)[:16]}…` | {p.stat().st_size} |")
    for p in sorted(BRR.iterdir()):
        w(f"| `{BRR.name}/{p.name}` | `{sha(p)[:16]}…` | {p.stat().st_size} |")
    w("")
    w(f"**FRENTE A** — portão de hash **{d['hash_gate']['result']}** "
      f"({d['hash_gate']['checked_count']} artefatos); cinco checks estruturais "
      f"recomputados dos bytes, todos PASS; teto **{d['structural_ceiling']}**, banda "
      f"**[{d['margin_band']['min']}; {d['margin_band']['max']}]**. "
      f"Portão dos canários: **{d['canary_check']['result']}**, "
      f"{sum(1 for x in d['canary_check']['checked'] if x['match'])}/"
      f"{len(d['canary_check']['checked'])}.")
    w("")
    w(f"**FRENTE B** — baseline com {c['accepted']}/{c['candidates']} elementos, cada "
      f"um com span de L0 e citação verificada pelo script; "
      f"{c['rejected_sem_ancora']}/{c['structural_candidates_tested']} formas "
      "estruturais rejeitadas por falta de âncora. ROBOT e os cinco componentes "
      f"cobertos (`{pv['robot_coverage_check']['span']}`): "
      f"**{pv['robot_coverage_check']['present_in_summary']}**. Resumo das condições "
      f"2 e 3 byte-idêntico: **{cond['summary_byte_identical_between_2_and_3']}**. "
      f"Régua em `{rb['artifact_status']}`.")
    w("")
    w("**FRENTE C** — duração real da fonte confirmada em três evidências "
      "independentes; conclusão no relatório.")
    w("")
    w("## 2. O que divergiu e travou")
    w("")
    w("**A4 travou — não congelei nada.** `freeze_margin_lock.py` e "
      "`freeze_pre_run_registry.py` não existem no repositório. A tarefa mandava usar "
      "\"os scripts já auditados\"; escrever scripts de congelamento novos na "
      "madrugada e usá-los seria justamente o contrário disso. A cadeia margin lock → "
      "registry → opening record continua por fazer.")
    w("")
    ir = d["input_resolution"]
    if not ir.get("declared_path_exists"):
        w(f"**Caminho de entrada, de novo.** `{ir['declared_path']}` não existe. Achei "
          f"os três braços por conteúdo em `{ir['resolved_from']}`. Os hashes "
          "conferem, então é divergência de caminho, não de conteúdo — mas é a "
          "segunda sessão seguida em que isso aparece.")
        w("")
    w("**A5 saiu em outro lugar.** A pasta foi pedida dentro de `Course-to-Skill/`, "
      "que esta sessão declarou read-only absoluto. Montei em "
      f"`docs/{BRR.name}/` e ela só REFERENCIA os pacotes por hash, sem copiar. "
      "Mover é decisão sua.")
    w("")
    w("**Falta o `JUDGE-BLIND-RUN-INSTRUCTIONS` da v0.1.4.** Só existe o da v0.1.3. "
      "Não gerei: seria inventar artefato congelado. Por isso a linha de âncora do "
      "juiz está PENDENTE.")
    w("")
    w("**Duas descobertas do próprio teste da Frente B**, ambas corrigidas e "
      "registradas: os títulos de seção do YouTube vêm colados ao fim do segmento e "
      "partiam citações ao meio; e `routing` ocorre em L0 uma vez, em 8:10, como "
      "\"lead routing\" — sentido diferente do roteamento entre recursos.")
    w("")
    w("## 3. O que fazer à mão ao acordar")
    w("")
    w("1. **Decidir o limiar** da v0.1.4 (ver §4) — nada abaixo disso destrava.")
    w("2. **Escrever/recuperar** `freeze_margin_lock.py` e "
      "`freeze_pre_run_registry.py`, com auditoria, e só então rodar a cadeia.")
    w("3. **Reemitir e congelar** o `JUDGE-BLIND-RUN-INSTRUCTIONS` para a v0.1.4.")
    w("4. **Criar** a árvore `v0.1.4/06_COMPARISON_ARMS/TEST-0007/` e mover para lá o "
      "pacote de braços e a pasta `BLIND_RUN_READY`.")
    w("5. **Mandar auditar por terceiro** o `TEST-0008-RUBRIC-DRAFT-v0.1.4.yaml` "
      "antes de congelar — quem escreveu o baseline (eu) escreveu o rascunho da "
      "régua, e é exatamente a circularidade que o TEST-0008 mede.")
    w("6. **Só depois** abrir as conversas cegas, seguindo o "
      f"`{BRR.name}/README-ABERTURA.md`.")
    w("")
    w("## 4. Decisões que sobraram para você")
    w("")
    w(f"**a) O limiar da v0.1.4.** A banda [{d['margin_band']['min']}; "
      f"{d['margin_band']['max']}] não mudou da v0.1.3, porque a Opção B mudou o "
      "candidato e não a régua. Reconfirmar 34,0 herdado, ou pré-declarar regra "
      "própria para o estímulo novo? Não derivei nem congelei limiar.")
    w("")
    w("**b) Quem audita a régua do 0008.** Precisa ser alguém que não escreveu o "
      "baseline. Sem isso o teste mede a si mesmo.")
    w("")
    w("**c) Onde mora a v0.1.4.** Hoje os artefatos v0.1.4 vivem sob a árvore "
      "`v0.1.3/`. Enquanto isso não for resolvido, todo caminho declarado em tarefa "
      "vai continuar não batendo.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"escrito: {OUT} ({OUT.stat().st_size} B)")
    print(f"sha256:  {sha(OUT)}")
    print(f"linhas:  {len(L)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
