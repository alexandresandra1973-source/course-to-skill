#!/usr/bin/env python3
"""HANDOFF-DENSIDADE — lê o que foi publicado e resume. Nenhum número digitado."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "HANDOFF-DENSIDADE.md"

CHAIN = DOCS / "PRE-RUN-CHAIN-v0.1.4.md"
DENS = DOCS / "SOURCE-DENSITY-COMPARISON.md"
CMETA = DOCS / "PILOT-002-CANDIDATE-METADATA.yaml"
BRR = DOCS / "v0.1.4/06_COMPARISON_ARMS/TEST-0007/BLIND_RUN_READY"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def grab(text: str, pat: str) -> str | None:
    m = re.search(pat, text)
    return m.group(1) if m else None


def main() -> int:
    dens = DENS.read_text(encoding="utf-8")
    cm = yaml.safe_load(CMETA.read_text(encoding="utf-8"))

    p1_dec = grab(dens, r"\*\*pontos de decisão distintos\*\* \| (\d+)")
    p1_den = grab(dens, r"\*\*decisões/min\*\* \| ([\d.]+)")
    p1_min = grab(dens, r"duração \(min\) \| ([\d.]+)")
    p1_page = grab(dens, r"\| (FINA|NAO_FINA) \|")
    measured = "NÃO MEDIDO" not in dens

    L, w = [], None
    w = L.append
    w("# HANDOFF — densidade")
    w("")
    w(f"`{datetime.now(timezone.utc).isoformat(timespec='seconds')}` · gerado por "
      f"`{Path(__file__).name}` · READ-ONLY sobre `Course-to-Skill/` e "
      "`Course-to-Skill-Compiler/` · **nada congelado**, nenhuma conversa aberta.")
    w("")
    w("## Veredito de densidade, em uma linha")
    w("")
    if measured:
        w("**Veredito emitido — ver `SOURCE-DENSITY-COMPARISON.md`.**")
    else:
        w(f"**NÃO EMITIDO: o transcript do candidato não foi obtido; o PILOT-001 "
          f"mediu {p1_den} decisões/min em {p1_min} min e REPROVA o teste da uma "
          f"página ({p1_dec} bullets > 45), então a régua está calibrada e falta só "
          "a segunda fonte.**")
    w("")
    w("## Pronto")
    w("")
    w("| artefato | sha256 | bytes |")
    w("|---|---|---|")
    for p in (CHAIN, DENS, CMETA):
        w(f"| `{p.name}` | `{sha(p)[:16]}…` | {p.stat().st_size} |")
    for p in sorted(BRR.iterdir()):
        w(f"| `BLIND_RUN_READY/{p.name}` | `{sha(p)[:16]}…` | {p.stat().st_size} |")
    w("")
    w("- **Freezers extraídos e conferidos**: `freeze_margin_lock.py` (pacote F4) e "
      "`freeze_pre_run_registry.py` (pacote F3-TRISTATE), ambos batendo com o "
      "manifesto do próprio pacote. Nenhum foi editado.")
    w("- **Árvore `v0.1.4/`** criada em `docs/`, com a nota de que os artefatos "
      "v0.1.4 hoje moram sob `v0.1.3/`.")
    w("- **BLIND_RUN_READY completa**, incluindo o `JUDGE-BLIND-RUN-INSTRUCTIONS-"
      "v0.1.4.md` derivado da v0.1.3 e marcado como derivado no cabeçalho.")
    w(f"- **PILOT-001 medido**: {p1_dec} pontos de decisão, {p1_den}/min, teste da "
      f"uma página **{p1_page}**.")
    w(f"- **Metadados do PILOT-002 apurados**: vídeo `{cm['source']['video_id']}`, "
      f"{cm['source']['duration_hms']} ({cm['source']['duration_seconds']}s), "
      f"{len(cm['chapters'])} capítulos.")
    w("")
    w("## Travou")
    w("")
    w("**A cadeia de lock, em dois pontos independentes. Não congelei nada.**")
    w("")
    w("1. `freeze_margin_lock.py` recusa: a função `structural_role` aceita só o "
      "papel genérico ou o nome de artefato **da v0.1.3**, cravado no código. "
      "Isolei a causa trocando apenas o `arm_id` numa cópia em `/tmp` — com o nome "
      "genérico o freezer congela. É amarração de versão, não erro de conteúdo.")
    w("2. `freeze_pre_run_registry.py` tem `candidate_version` **fixo em `0.1.3`**. "
      "Sondado, carimbaria 0.1.3 no registry e no opening record de uma rodada "
      "v0.1.4 — afirmação falsa dentro dos artefatos que existem para provar "
      "integridade. Esse é o bloqueio decisivo: o primeiro tem contorno, este não.")
    w("")
    w("**O transcript do PILOT-002.** O YouTube devolve as legendas com HTTP 200 e "
      "corpo vazio (exige PO token) e a API de player responde `LOGIN_REQUIRED` ou "
      "`UNPLAYABLE` em ANDROID_VR, IOS, WEB e MWEB. Parei a medição, como mandado. "
      "Não estimei nada.")
    w("")
    w("**Achado lateral:** o artigo do freeCodeCamp anuncia \"1.5-hour watch\", mas "
      f"o vídeo tem {cm['source']['duration_hms']} — "
      f"{cm['source']['duration_seconds']}s contra 5400s.")
    w("")
    w("## À mão, ao acordar")
    w("")
    w("1. **Cole o transcript** do vídeo `7l6bXLAKyEI` em "
      "`docs/PILOT-002-transcript.txt` e rode `python3 source_density.py`. O "
      "veredito sai sozinho — a métrica e a metade do PILOT-001 já estão prontas.")
    w("2. **Peça um patch F5** que estenda `structural_role` para aceitar o arm_id "
      "da 0.1.4, e que troque o `candidate_version` fixo do registry por parâmetro. "
      "Com auditoria, como os anteriores.")
    w("3. **Rode a cadeia** de novo depois do F5: `prerun_chain_v014.py` refaz tudo "
      "e publica sozinho.")
    w("4. **Mova** o pacote de braços v0.1.4 e a árvore `v0.1.4/` para dentro de "
      "`Course-to-Skill/`.")
    w("5. **Só então** abra as conversas cegas, seguindo o `README-ABERTURA.md`.")
    w("")
    w("## Decisões que sobraram")
    w("")
    w("**a) Como corrigir os dois hardcodes.** Patch F5 nos freezers, ou reemitir o "
      "relatório estrutural com `arm_id` genérico? O segundo resolve só metade e "
      "deixa o `candidate_version` errado. Recomendo o patch.")
    w("**b) O limiar da v0.1.4** continua em aberto desde a sessão anterior: "
      "reconfirmar 34,0 herdado ou pré-declarar regra própria.")
    w("**c) Se o PILOT-002 não qualificar**, decidir se procura outra fonte ou se "
      "aceita um corpus de fontes finas com o custo estatístico que isso traz.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"escrito: {OUT.name} ({OUT.stat().st_size} B) {sha(OUT)[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
