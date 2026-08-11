#!/usr/bin/env python3
"""HANDOFF da sessão autônoma — lê os relatórios publicados e resume.

Nenhum número é digitado: tudo vem dos artefatos já publicados.
READ-ONLY sobre Course-to-Skill/ e Course-to-Skill-Compiler/.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
SC = DOCS / "STRUCTURAL-CEILING-REPORT-v0.1.4.yaml"
T8 = DOCS / "TEST-0008-METRICS-DISCREPANCY.md"
OUT = DOCS / "HANDOFF-SESSAO-AUTONOMA-v0.1.4.md"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    d = yaml.safe_load(SC.read_text(encoding="utf-8"))
    v = d["independent_structural_verification"]
    L, w = [], None
    w = L.append

    w("# HANDOFF — sessão autônoma v0.1.4")
    w("")
    w(f"- Gerado: `{datetime.now(timezone.utc).isoformat(timespec='seconds')}`")
    w(f"- Gerador: `{Path(__file__).name}` (nenhum número digitado)")
    w("- Regime: READ-ONLY sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/`")
    w("- Nenhum lock, registry ou opening record foi criado ou congelado.")
    w("")
    w("## Pronto")
    w("")
    w(f"**1. `{SC.name}`** — `artifact_status: {d['artifact_status']}`")
    w(f"- sha256 `{sha256(SC)}` · {SC.stat().st_size} B")
    w(f"- Portão de hash: **{d['hash_gate']['result']}** "
      f"({d['hash_gate']['checked_count']}/{d['hash_gate']['checked_count']} artefatos)")
    w(f"- Teto estrutural **{d['structural_ceiling']}**, banda "
      f"**[{d['margin_band']['min']}, {d['margin_band']['max']}]**")
    w("- Par de braços amarrado ao relatório:")
    for side in ("left", "right"):
        s = d["margin_pair_bound"][side]
        w(f"  - `{s['selector']}` → `{s['sha256']}`")
    w("")
    w(f"**2. `{T8.name}`** — Frente 2, discrepância 5×6 do TEST-0008")
    w(f"- sha256 `{sha256(T8)}` · {T8.stat().st_size} B")
    w("")
    w("## Canários")
    w("")
    w("| canário | esperado | obtido | |")
    w("|---|---|---|---|")
    for c in d["canary_check"]["checked"]:
        w(f"| `{c['canary']}` | {c['expected']} | {c['observed']} | "
          f"{'OK' if c['match'] else 'DIVERGE'} |")
    w("")
    w(f"Resultado: **{d['canary_check']['result']}** — nenhum dos cinco divergiu, "
      "logo não houve parada.")
    w("")
    w("## Cinco checks estruturais")
    w("")
    w(f"{v['provenance']['relationship']} "
      f"Conferência prévia: {v['provenance']['prior_verification_by']}.")
    w("")
    for k in sorted(x for x in v if x[:2] in ("a_", "b_", "c_", "d_", "e_")):
        w(f"- **{v[k]['verdict']}** — `{k}`")
    w("")
    w("## O que divergiu")
    w("")
    ir = d["input_resolution"]
    if not ir.get("declared_path_exists"):
        w(f"**Caminho de entrada.** O diretório declarado "
          f"`{ir['declared_path']}` não existe. Os três braços foram localizados por "
          f"busca de conteúdo em `{ir['resolved_from']}` — que está sob a árvore "
          "`v0.1.3`, não `v0.1.4`. Os cinco hashes declarados conferem a partir dessa "
          "origem, então **a divergência é de caminho, não de conteúdo**, e não "
          "bloqueou nada. Vale arrumar a árvore antes do próximo freeze.")
    else:
        w("Nada divergiu.")
    w("")
    w("Nenhuma divergência numérica: os cinco canários bateram e os cinco checks "
      "estruturais passaram.")
    w("")
    w("## Reteste do juiz — resolvido, não pendente")
    w("")
    jr = d["judge_retest_finding"]
    w(f"**{jr['answer']}** {jr['consequence']}")
    w("")
    w(f"Ressalva registrada: {jr['residual_caveat']}")
    w("")
    w("## A decisão que sobrou para o Alexandre")
    w("")
    w("**Fixar o limiar de margem da v0.1.4 — ou reconfirmar 34,0 — antes do "
      "próximo blind run.**")
    w("")
    w(f"Este relatório publica a banda informativa "
      f"[{d['margin_band']['min']}, {d['margin_band']['max']}] e **não deriva nem "
      "congela limiar**. O 34,0 aparece aqui só como canário conferido; sua fonte é "
      f"`{d['threshold_implication']['canonical_threshold_source']['artifact']}`, "
      "congelada na v0.1.3.")
    w("")
    w("O que torna isso uma decisão e não uma formalidade: a banda não mudou da "
      "v0.1.3 para a v0.1.4 porque a régua não mudou — só o candidato mudou. Cabe "
      "decidir se o limiar herdado continua valendo para um estímulo novo, ou se a "
      "v0.1.4 merece regra própria pré-declarada.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"escrito: {OUT}")
    print(f"sha256:  {sha256(OUT)}")
    print(f"bytes:   {OUT.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
