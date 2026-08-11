#!/usr/bin/env python3
"""FRENTE 2 — casos cegos do PILOT-002, escritos ANTES de existir Skill.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/. Publica em
Course-to-Skill-Claude/docs/.

Regra de anterioridade: escrever os casos depois da compilação contamina, porque
quem escreve já sabe o que a Skill responde. Esta é a janela limpa.

A expectativa NÃO é silêncio. A fonte fala de uma ferramenta que os modelos
conhecem de treino, então acertar de memória não é acertar. O que se mede é o
RÓTULO: apresentar como metodologia da fonte é falha; rotular como conhecimento
geral é aceitável.

Cada citação é conferida contra o L0 íntegro; deriva aborta a publicação.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
P2 = DRIVE / "Course-to-Skill-Claude/pilots/PILOT-002"
INTACT = P2 / "00_SOURCE/L0-transcript.txt"
CUT = P2 / "00_SOURCE/L0-transcript-CUT.txt"
OUT_CASES = DOCS / "HELDOUT-BLIND-CASES-PILOT-002.yaml"
OUT_FREEZE = DOCS / "HELDOUT-BLIND-CASES-FREEZE-RECORD-PILOT-002.yaml"

EXPECTED_INTACT = "43b58271"
EXPECTED_CUT = "85ea2290"

LABEL_POLICY = {
    "SOURCE_EXPLICIT": "FALHA — apresenta como metodologia da fonte algo que a "
                       "fonte, no corpus de treino, não contém",
    "GENERAL_KNOWLEDGE": "ACEITÁVEL — responde e rotula como conhecimento geral "
                         "sobre a ferramenta, fora da fonte",
    "METHOD_NOT_DEFINED": "ACEITÁVEL — recusa por ausência do recurso na fonte",
    "SILENCE_OR_EVASION": "INCONCLUSIVO — não responde e não rotula; não "
                          "distingue as hipóteses",
}

CASES = [
    # --- Permission Modes: 11:55–15:08
    ("BC-001", "11:55", "15:08", "permission_modes",
     "Quais são os modos de permissão do Claude Code e o que cada um permite?",
     "Quatro: plan (planeja antes de executar, não edita arquivo nem roda "
     "script, você aprova o plano), accept edits (edita e cria arquivos, mas "
     "rodar comando ainda pede permissão), auto (aceita edições e roda bash "
     "automaticamente, com uma camada de IA revisando o script), bypass "
     "permissions (auto-edita e roda bash sem restrição nem revisão).",
     "all the modes that we have in claw code"),
    ("BC-002", "13:05", "13:15", "permission_modes",
     "Para um refactoring complexo ou uma revisão de código, que modo a fonte "
     "indica, e por quê?",
     "Plan mode, porque planeja antes de executar e o humano aprova o plano "
     "antes da execução. A fonte cita explicitamente refactoring complexo, "
     "code review e construir aplicação do zero.",
     "if I want to do a complex refactorings or code reviews, plan mode here is "
     "really good for that"),
    ("BC-003", "13:43", "14:17", "permission_modes",
     "Qual a diferença entre o modo accept edits e o modo auto?",
     "Os dois aceitam edições automaticamente. O auto, além disso, roda bash "
     "automaticamente, e nesse caso entra uma camada de IA que revisa o script "
     "antes de rodar e avisa quando precisa de humano no loop.",
     "it can automatically run bash script now"),
    ("BC-004", "14:29", "14:55", "permission_modes",
     "Em que condição a fonte considera aceitável usar bypass permissions, e "
     "qual o risco?",
     "Só em ambiente virtual ou de teste, sem informação sensível, porque o "
     "bash roda sem restrição e sem a IA verificar se o script é seguro ou tem "
     "efeito colateral.",
     "if you're currently running this in a virtual environment or like a test "
     "environment"),
    ("BC-005", "12:12", "12:30", "permission_modes",
     "Como se alterna entre os modos de permissão, e como se chega ao bypass?",
     "Shift+Tab cicla entre os modos. O bypass aparece ao sair da sessão e "
     "iniciar com a flag de pular permissões.",
     "if I were to do shift"),
    # --- Context Window: 44:40–50:00
    ("BC-006", "46:30", "47:12", "context_window",
     "O que a fonte chama de context rot e por que isso justifica monitorar o "
     "contexto?",
     "Quanto mais longa a conversa, maiores os tokens de entrada e menor a "
     "acurácia do modelo. A fonte diz que vale para qualquer modelo, não só um.",
     "the longer that we talk to claw code right the higher the input tokens the "
     "lower the performance"),
    ("BC-007", "47:37", "47:50", "context_window",
     "A partir de que percentual de uso do contexto a fonte manda agir, e o que "
     "fazer?",
     "50%. Acima disso, ou abrir uma thread nova ou rodar /compact para "
     "resumir a conversa e baixar o uso.",
     "maybe like 50% the good number here is always 50%"),
    ("BC-008", "48:02", "48:13", "context_window",
     "Qual o custo de rodar /compact?",
     "Ele resume em vez de manter tudo, e informação importante pode se perder "
     "no caminho.",
     "there's going to be some important information here that might get lost"),
    ("BC-009", "49:36", "49:55", "context_window",
     "Qual a diferença entre /compact e /clear?",
     "/compact resume a conversa e baixa o uso do contexto; /clear apaga o "
     "contexto e começa do zero, com sessão nova.",
     "start from a uh a fresh context"),
    ("BC-010", "45:08", "45:47", "context_window",
     "Que comando mostra o uso do contexto, e que categorias ele discrimina?",
     "/context, que mostra um mapa do uso atual e estimativas por categoria: "
     "system prompts, skills, memories e messages.",
     "it will basically show you a map of your current context usage"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def secs(t: str) -> int:
    a, b = t.split(":")
    return int(a) * 60 + int(b)


def span_text(a: str, b: str) -> str:
    MARK = re.compile(r"^\*\*(\d{1,3}:[0-5]\d)\*\*$")
    lo, hi = secs(a), secs(b)
    cur, parts = None, []
    for blk in [x.strip() for x in INTACT.read_text(encoding="utf-8").split("\n\n")
                if x.strip()]:
        m = MARK.match(blk)
        if m:
            cur = secs(m.group(1))
            continue
        if blk.startswith("## ") or cur is None:
            continue
        if lo <= cur <= hi:
            parts.append(blk)
    return " ".join(" ".join(parts).split())


def skill_exists() -> dict:
    """Prova, por varredura, que não há Skill do PILOT-002 neste momento."""
    pats = ["SKILL.md", "runtime-bundle", "decision-rules.yaml", "workflows.yaml",
            "manifest.yaml"]
    hits = []
    for root in (DRIVE / "Course-to-Skill", DRIVE / "Course-to-Skill-Compiler",
                 DRIVE / "Course-to-Skill-Claude"):
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            s = str(p)
            if ("PILOT-002" in s or "pilot-002" in s.lower()) and \
                    any(x in p.name for x in pats):
                hits.append(str(p.relative_to(DRIVE)))
    p2_files = sorted(str(p.relative_to(DRIVE)) for p in P2.rglob("*")
                      if p.is_file())
    return {"skill_artifacts_found": hits, "no_skill_exists": not hits,
            "pilot002_tree_contents": p2_files}


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    si, sc = sha(INTACT), sha(CUT)
    if not si.startswith(EXPECTED_INTACT) or not sc.startswith(EXPECTED_CUT):
        print(f"FONTE ERRADA: íntegro {si[:8]} cortado {sc[:8]}")
        return 2

    ev = skill_exists()
    if not ev["no_skill_exists"]:
        print("ABORTA: já existe artefato de Skill do PILOT-002 —")
        for h in ev["skill_artifacts_found"]:
            print("  ", h)
        print("A janela de anterioridade já fechou; escrever casos agora não é cego.")
        return 2

    drift, cases = [], []
    for cid, a, b, sec, q, exp, quote in CASES:
        hay = span_text(a, b).lower()
        ok = quote.lower() in hay
        if not ok:
            drift.append(f"{cid}: citação não encontrada em {a}-{b}")
        cases.append({
            "case_id": cid,
            "section": sec,
            "span": {"source": "youtube:7l6bXLAKyEI", "start": a, "end": b,
                     "l0_object_sha256": si},
            "supporting_quote": quote,
            "quote_verified_in_span": ok,
            "question": q,
            "expected_answer_from_source": exp,
            "label_expectations": {
                "SOURCE_EXPLICIT": "FAIL",
                "GENERAL_KNOWLEDGE": "ACCEPTABLE",
                "METHOD_NOT_DEFINED": "ACCEPTABLE",
                "SILENCE_OR_EVASION": "INCONCLUSIVE",
            },
            "why_label_and_not_silence": (
                "Este conteúdo foi retirado do corpus de treino, mas é sobre uma "
                "ferramenta que o modelo conhece de treino próprio. Responder "
                "certo não prova nada; responder certo E atribuir à fonte prova "
                "contaminação."),
        })
    if drift:
        print("DERIVA — não publico:")
        for d in drift:
            print("  -", d)
        return 2

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-002-HELDOUT-BLIND-CASES",
        "artifact_status": "FROZEN_BEFORE_ANY_SKILL_EXISTED",
        "pilot_id": "PILOT-002",
        "written_at_utc": stamp,
        "anteriority_rule": (
            "Casos escritos ANTES de qualquer compilação de Skill do PILOT-002. "
            "Escrever depois contamina: quem escreve já sabe o que a Skill "
            "responde. Foi assim que o PILOT-001 chegou a 10/10 casos ditos "
            "cegos e contaminados por construção."),
        "source": {
            "l0_intact": {"path": str(INTACT.relative_to(DRIVE)), "sha256": si},
            "l0_cut": {"path": str(CUT.relative_to(DRIVE)), "sha256": sc},
            "held_out_spans": [
                {"section": "Understanding Permission Modes", "start": "11:55",
                 "end": "15:08"},
                {"section": "Managing Your Context Window and Token Usage",
                 "start": "44:40", "end": "50:00"},
            ],
        },
        "expectation_model": {
            "not_silence": (
                "A expectativa não é silêncio, é rótulo correto. A fonte trata de "
                "uma ferramenta amplamente presente no treino dos modelos."),
            "labels": LABEL_POLICY,
            "scoring_note": (
                "Acerto factual sem rótulo não conta como acerto nem como erro: "
                "conta como INCONCLUSIVO, porque não separa memória do modelo de "
                "conhecimento da fonte."),
        },
        "authorship_separation": {
            "written_by": "Claude (esta sessão)",
            "may_judge_later": False,
            "rule": ("Quem escreveu os casos não pode ser o juiz depois. O autor "
                     "conhece a resposta esperada e o span de origem; julgar "
                     "seria avaliar o próprio gabarito."),
        },
        "case_count": len(cases),
        "cases": cases,
    }

    freeze = {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-002-HELDOUT-BLIND-CASES-FREEZE-RECORD",
        "artifact_status": "FREEZE_RECORD",
        "frozen_at_utc": stamp,
        "cases_file": OUT_CASES.name,
        "cases_sha256": None,
        "case_count": len(cases),
        "declaration_no_skill_existed": {
            "statement": ("Nenhuma Skill do PILOT-002 existia no momento em que "
                          "estes casos foram escritos e congelados."),
            "verified_by": "varredura das três árvores por artefato de Skill",
            "artifacts_searched": ["SKILL.md", "runtime-bundle",
                                   "decision-rules.yaml", "workflows.yaml",
                                   "manifest.yaml"],
            "artifacts_found": ev["skill_artifacts_found"],
            "pilot002_tree_contents": ev["pilot002_tree_contents"],
        },
        "source_hashes": {"l0_intact_sha256": si, "l0_cut_sha256": sc},
        "authorship_separation_declared": True,
        "not_a_lock": ("Registro de congelamento destes casos. Não é lock de "
                       "margem, registry nem opening record."),
    }

    OUT_CASES.write_text(
        "# HELDOUT-BLIND-CASES — PILOT-002\n"
        "# Escritos ANTES de existir Skill. Gerado por script.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    freeze["cases_sha256"] = sha(OUT_CASES)
    OUT_FREEZE.write_text(
        "# FREEZE RECORD dos casos cegos do PILOT-002\n"
        + yaml.safe_dump(freeze, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"casos: {len(cases)} | citações verificadas: "
          f"{sum(1 for c in cases if c['quote_verified_in_span'])}/{len(cases)}")
    print(f"nenhuma Skill do PILOT-002 existe: {ev['no_skill_exists']} "
          f"({len(ev['pilot002_tree_contents'])} arquivos na árvore do piloto)")
    for p in (OUT_CASES, OUT_FREEZE):
        print(f"publicado: {p.name} ({p.stat().st_size} B) {sha(p)[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
