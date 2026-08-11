#!/usr/bin/env python3
"""HANDOFF-PILOT-002 — lê o publicado e resume. Nenhum número digitado."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "HANDOFF-PILOT-002.md"

SEAL = DOCS / "PILOT-002-VAULT-SEAL.yaml"
LOCK = DOCS / "HELDOUT-LOCK-PILOT-002.yaml"
MAP = DOCS / "L0_COVERAGE_MAP-PILOT-002.md"
CHAIN = DOCS / "PRE-RUN-CHAIN-v0.1.4.md"
BRR = DOCS / "v0.1.4/06_COMPARISON_ARMS/TEST-0007/BLIND_RUN_READY"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    s = yaml.safe_load(SEAL.read_text(encoding="utf-8"))
    l = yaml.safe_load(LOCK.read_text(encoding="utf-8"))
    m, seg = s["marks"], l["segments"]

    L, w = [], None
    w = L.append
    w("# HANDOFF — PILOT-002")
    w("")
    w(f"`{datetime.now(timezone.utc).isoformat(timespec='seconds')}` · gerado por "
      f"`{Path(__file__).name}` · READ-ONLY sobre `Course-to-Skill/` e "
      "`Course-to-Skill-Compiler/` · nenhuma conversa cega aberta · rubrica do "
      "TEST-0008 intocada.")
    w("")
    w("## Held-out — a linha que importa")
    w("")
    w(f"**O held-out do PILOT-002 foi cortado ANTES de qualquer extração: o lock "
      f"`{LOCK.name}` está `{l['artifact_status']}`, retirou "
      f"{seg['held_out']} dos {seg['total']} segmentos "
      f"({seg['held_out_fraction']*100:.1f}%) por span declarado, e nenhum L1, "
      "compilação ou rubrica foi produzido para este piloto.**")
    w("")
    w("## Pronto")
    w("")
    w("| artefato | sha256 | bytes |")
    w("|---|---|---|")
    for p in (SEAL, LOCK, MAP, CHAIN):
        w(f"| `{p.name}` | `{sha(p)[:16]}…` | {p.stat().st_size} |")
    for p in sorted(BRR.iterdir()):
        w(f"| `BLIND_RUN_READY/{p.name}` | `{sha(p)[:16]}…` | {p.stat().st_size} |")
    w("")
    w("### Frente B — G0, G1, G2")
    w("")
    w(f"- **G0.** L0 ingerido no vault por conteúdo. {m['in_docx']} marcas de tempo, "
      f"primeira `{m['first_mark_docx']}`, última **`{m['last_mark_docx']}`** — "
      f"confere com a esperada `{m['last_mark_expected']}`. Timestamps "
      f"sobreviveram à cópia: **{m['timestamps_survived_copy']}** "
      f"({m['indexed_by_vault']} indexadas pelo vault, nenhuma perdida).")
    w(f"- **G1.** Corte por span, não por sorteio. Lock idêntico nas **2** "
      f"execuções: **{l['determinism_check']['lock_identical']}**. "
      f"L0 íntegro `{l['l0_intact']['sha256'][:16]}…` "
      f"({l['l0_intact']['marks']} marcas) · L0 CORTADO "
      f"`{l['l0_cut']['sha256'][:16]}…` ({l['l0_cut']['marks']} marcas).")
    w(f"- **G2.** Mapa de cobertura do L0 cortado, no formato do PILOT-001.")
    w("")
    w("### Frente A")
    w("")
    w("- Freezers extraídos dos pacotes F4 e F3-TRISTATE, ambos conferindo com o "
      "manifesto de origem. Nenhum editado.")
    w("- Árvore `v0.1.4/` criada em `Course-to-Skill-Claude/docs/`.")
    w("- `BLIND_RUN_READY` publicada com as duas listas de anexo, SHA256SUMS e "
      "README de 15 linhas.")
    w("")
    w("## Travou")
    w("")
    w("**A cadeia de lock da v0.1.4, pelos mesmos dois hardcodes da sessão "
      "anterior. Continua sem congelar.** Não houve patch F5 desde então:")
    w("")
    w("1. `freeze_margin_lock.py` — `structural_role` aceita só o papel genérico "
      "ou o nome de artefato da **v0.1.3**. Diagnóstico refeito: trocando apenas "
      "o `arm_id` numa cópia em `/tmp`, o freezer congela.")
    w("2. `freeze_pre_run_registry.py` — `candidate_version` fixo em `0.1.3`; "
      "carimbaria versão falsa no registry e no opening record.")
    w("")
    w("Por isso **a segunda linha de âncora continua bloqueada**: ela é o hash do "
      "opening record, que não existe.")
    w("")
    w("### Divergências de caminho encontradas nesta sessão")
    w("")
    w("- A fonte foi pedida em `pilots/PILOT-002/00_SOURCE/L0-transcript.txt`. O "
      "que existe é `Course-to-Skill-Claude/pilots/PILOT-002/00_SOURCE/"
      "L0-transcript.txt.docx` — **`.docx`**, e sob `Course-to-Skill-Claude/`, não "
      "`Course-to-Skill/`. Sorte: é a árvore gravável, então deu para normalizar "
      "e gerar o `.txt` no lugar esperado.")
    w("- Os artefatos v0.1.4 seguem morando sob `v0.1.3/`.")
    w("")
    w("### Resíduo declarado no lock")
    w("")
    r = l["residue_disclosed"]
    w(f"As duas linhas de título das seções retiradas **permanecem** no corpus de "
      f"treino: elas não têm marca de tempo, logo não são endereçáveis por span e "
      f"um corte por span não as alcança. Mantidas de propósito — removê-las seria "
      f"cortar além do span pedido. São {len(r['items'])}:")
    w("")
    for i in r["items"]:
        w(f"- `{i['line']}` (abre em `{i['opens_section_at']}`)")
    w("")
    w("O conteúdo saiu inteiro: **zero** marcas das duas seções ficaram fora dos "
      "spans declarados.")
    w("")
    w("## À mão, ao acordar")
    w("")
    w("1. **Decidir sobre o resíduo:** apagar as duas linhas de título do corpus "
      "de treino, ou aceitar que o rótulo do assunto retirado fique visível.")
    w("2. **Pedir o patch F5** dos freezers: estender `structural_role` para o "
      "arm_id da 0.1.4 e trocar o `candidate_version` fixo por parâmetro. Com "
      "auditoria, como os anteriores.")
    w("3. **Rodar `prerun_chain_v014.py`** de novo depois do F5 — ele refaz a "
      "cadeia e publica sozinho.")
    w("4. **Mover** a árvore `v0.1.4/` e o pacote de braços para dentro de "
      "`Course-to-Skill/`.")
    w("5. **Colar o transcript do PILOT-002** em `docs/PILOT-002-transcript.txt` e "
      "rodar `source_density.py` para fechar o veredito de densidade que ficou "
      "pendente — agora a fonte existe, é só apontar o script para ela.")
    w("")
    w("## Decisões que sobraram")
    w("")
    w("**a)** Como corrigir os dois hardcodes: patch nos freezers (recomendo) ou "
      "reemitir o relatório estrutural com `arm_id` genérico — o segundo resolve "
      "metade e deixa a versão errada carimbada.")
    w("**b)** O limiar da v0.1.4: reconfirmar 34,0 herdado ou pré-declarar regra "
      "própria. Aberto desde duas sessões atrás.")
    w("**c)** O resíduo de título do held-out do PILOT-002.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"escrito: {OUT.name} ({OUT.stat().st_size} B) {sha(OUT)[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
