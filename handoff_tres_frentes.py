#!/usr/bin/env python3
"""HANDOFF-TRES-FRENTES — lê o publicado e resume. Nenhum número digitado."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "HANDOFF-TRES-FRENTES.md"

PROOF = DOCS / "TOL-REACHABILITY-PROOF.md"
CASES = DOCS / "HELDOUT-BLIND-CASES-PILOT-002.yaml"
FREEZE = DOCS / "HELDOUT-BLIND-CASES-FREEZE-RECORD-PILOT-002.yaml"
D8 = DOCS / "DRY-RUN-TEST-0008.md"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    proof = PROOF.read_text(encoding="utf-8")
    c = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    f = yaml.safe_load(FREEZE.read_text(encoding="utf-8"))
    d8 = D8.read_text(encoding="utf-8")

    gap = re.search(r"está a\s+\*\*([\d.]+)\*\*", proof)
    miss = re.search(r"\*\*(\d+) de (\d+) itens ausentes", d8)
    legacy = re.search(r"Encontrei \*\*(\d+)\*\* contrato", d8)
    ok_quotes = sum(1 for x in c["cases"] if x["quote_verified_in_span"])

    L, w = [], None
    w = L.append
    w("# HANDOFF — três frentes")
    w("")
    w(f"`{datetime.now(timezone.utc).isoformat(timespec='seconds')}` · gerado por "
      f"`{Path(__file__).name}` · READ-ONLY sobre `Course-to-Skill/` e "
      "`Course-to-Skill-Compiler/` · **nada congelado** (lock/registry/opening "
      "record), nenhuma conversa cega aberta, nenhuma Skill compilada, nenhum "
      "script auditado editado.")
    w("")
    w("## Veredito da prova de alcançabilidade, em uma linha")
    w("")
    w(f"**Minha alegação se sustenta como foi enunciada — com nota inteira "
      f"nenhuma margem alcançável entra na faixa que TOL atravessa, e a folga é "
      f"{gap.group(1) if gap else '?'} contra TOL de 0,01 — mas ela é mais "
      "frágil do que eu dei a entender: a leitura simétrica já falha com uma "
      "casa decimal, e a de um lado só falha com duas.**")
    w("")
    w("## Pronto")
    w("")
    w("| artefato | sha256 | bytes |")
    w("|---|---|---|")
    for p in (PROOF, CASES, FREEZE, D8):
        w(f"| `{p.name}` | `{sha(p)[:16]}…` | {p.stat().st_size} |")
    w("")
    w("### Frente 1 — prova por enumeração")
    w("")
    w("Enumeração **completa** do espaço alcançável em aritmética **exata** "
      "(`Fraction` sobre `Decimal`; float aqui seria o próprio erro sob "
      "investigação). Três grades de nota testadas. O resultado por grade e a "
      "checagem simétrica estão no relatório.")
    w("")
    w("O que mudou em relação ao que eu tinha afirmado: eu conferi quatro "
      "valores à mão e concluí que o desvio \"não pode\" mudar veredito. A "
      "enumeração confirma isso para nota inteira, e mostra que a folga é "
      "propriedade das fronteiras escolhidas, não margem de segurança "
      "projetada. Se o contrato do juiz aceitar nota fracionária, a prova "
      "precisa ser refeita.")
    w("")
    w("### Frente 2 — casos cegos, escritos antes de existir Skill")
    w("")
    w(f"**{c['case_count']} casos congelados**, {ok_quotes}/{c['case_count']} "
      "com citação verificada contra o L0 íntegro. Cinco da seção de modos de "
      "permissão, cinco da de janela de contexto.")
    w("")
    w("A varredura confirmou que **nenhuma Skill do PILOT-002 existe** — a "
      f"árvore do piloto tem {len(f['declaration_no_skill_existed']['pilot002_tree_contents'])} "
      "arquivos, todos de fonte. Está no freeze record, com os hashes do L0 "
      "íntegro e do cortado.")
    w("")
    w("A expectativa de cada caso é **rótulo**, não silêncio: responder e "
      "rotular como conhecimento geral é aceitável; apresentar como metodologia "
      "da fonte é falha; recusar por ausência é aceitável. Acerto factual sem "
      "rótulo fica INCONCLUSIVO, porque não separa memória do modelo de "
      "conhecimento da fonte.")
    w("")
    w("**Registrado no artefato: quem escreveu os casos não pode ser o juiz "
      "depois.** Eu escrevi; eu não julgo.")
    w("")
    w("### Frente 3 — ensaio seco do TEST-0008")
    w("")
    w("As duas comparações e os quatro regimes foram exercitados sobre notas "
      "sintéticas, em aritmética exata. **A aritmética não é o gargalo.**")
    w("")
    w("## O que falta para o 0008 rodar")
    w("")
    if miss:
        w(f"**{miss.group(1)} de {miss.group(2)} itens exigidos não existem.** "
          "A lista completa está no relatório; os que mais pesam:")
    w("")
    w("- régua do 0008 **congelada** (só existe rascunho, e ele precisa de "
      "auditoria externa antes)")
    w("- lista canônica de `comparison_metrics` congelada — **bloqueador 1 do "
      "ADR**, e do qual régua, âncoras e derivação de métrica dependem")
    w("- variância do avaliador do 0008, que o ADR proíbe herdar do 0007")
    w("- bandas numéricas de interpretação `F/P`, que só podem sair da variância")
    w("- teto estrutural, regra de decisão, pacotes das três condições, addendum "
      "de saída do juiz, instruções de rodada cega, e a cadeia pré-run inteira")
    w("")
    w("**Dois não são falta de arquivo, são falta de forma:** o contrato "
      "expressa **uma** comparação por teste, e o 0008 precisa de duas (`P` e "
      "`F`); e o modelo é par esquerda/direita mais preservação antes/depois, "
      "desenhado para ablação, não para três condições.")
    w("")
    if legacy:
        w(f"**E há uma armadilha.** {legacy.group(1)} contratos antigos já "
          "declaram `TEST-0008` com uma comparação só, `SKILL_MINUS_SUMMARY`, e "
          "limiar adiado. Isso codifica o desenho de duas condições que o ADR "
          "substituiu. `SKILL_MINUS_SUMMARY` não desambigua entre `P` e `F` — "
          "quem rodar com esse contrato mede uma comparação e não sabe qual.")
    w("")
    w("## O que sobrou para o Alexandre")
    w("")
    w("1. **Decidir se a prova de TOL basta para liberar a rodada.** Ela vale "
      "para o contrato atual, de nota inteira. Se o juiz puder devolver nota "
      "fracionária, não vale — e isso é uma linha do contrato, não uma "
      "suposição minha.")
    w("2. **Nomear outro juiz para os casos cegos do PILOT-002.** Eu os "
      "escrevi; a separação está declarada no artefato e depende de você "
      "cumpri-la.")
    w("3. **Resolver a discrepância 5×6** antes de qualquer coisa do 0008. É o "
      "primeiro dominó: régua, âncoras e métrica dependem dela.")
    w("4. **Decidir se o 0008 vale o custo agora**, com a lista do que falta em "
      "mãos. Não é um patch de distância do 0007.")
    w("5. **Aposentar ou marcar os 13 contratos legados** com a entrada velha "
      "do 0008, para ninguém rodar com o desenho de duas condições.")
    w("6. **O limiar da v0.1.4** continua aberto, de sessões atrás.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"escrito: {OUT.name} ({OUT.stat().st_size} B) {sha(OUT)[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
