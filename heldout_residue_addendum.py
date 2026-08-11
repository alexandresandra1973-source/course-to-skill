#!/usr/bin/env python3
"""Aditivo de resíduo do held-out do PILOT-002 — ADITIVO, não emenda.

Roda daqui (ext4). READ-ONLY sobre as fontes. NÃO toca no lock congelado:
publica um artefato novo que se liga a ele por SHA-256.

A evidência é REGENERADA do arquivo real no momento de publicar, não copiada
das minhas anotações. Os valores abaixo entram como EXPECTATIVA: se a varredura
ao vivo discordar, o script aborta em vez de publicar.

Não congela nada além de si próprio, não altera casos, não altera o lock.
"""
from __future__ import annotations

import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
P2 = DRIVE / "Course-to-Skill-Claude/pilots/PILOT-002/00_SOURCE"

CUT = P2 / "L0-transcript-CUT.txt"
INTACT = P2 / "L0-transcript.txt"
LOCK = DOCS / "HELDOUT-LOCK-PILOT-002.yaml"
CASES = DOCS / "HELDOUT-BLIND-CASES-PILOT-002.yaml"
FREEZE = DOCS / "HELDOUT-BLIND-CASES-FREEZE-RECORD-PILOT-002.yaml"
OUT = DOCS / "HELDOUT-RESIDUE-ADDENDUM-PILOT-002.yaml"

EXPECTED_CUT = "85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29"
EXPECTED_INTACT = "43b58271feb0a1d518ae6f81ab29836eb9c7f2bec5eb02e53f70c7bd1eb514ed"

# Nomes de modo que a seção retirada DEFINE, e que podem aparecer como uso em
# outras seções. A varredura decide; isto é só a lista de termos a procurar.
MODE_TERMS = {
    "plan mode": r"plan\s+mode",
    "accept edits": r"accept(?:ed)?\s+edits",
    "auto mode": r"auto\s+mode",
    "bypass permission": r"bypass\s+permission",
    "shift tab": r"shift\s?tab",
}
# Ensinamentos das duas seções. Se algum aparecer, o held-out vazou de verdade.
TEACHING_TERMS = {
    "/compact": r"/\s?compact|slash\s?compact",
    "/clear": r"/\s?clear|slash\s?clear",
    "/context": r"/\s?context|slashcontext|slash\s?context",
    "limiar de 50%": r"\b50\s?%",
    "context rot": r"context\s+rot",
    "1 milhão de tokens": r"1\s*million",
}

# Expectativas apuradas na varredura anterior, sobre a reconstrução do cortado.
EXPECTED_LEAKS = {
    "plan mode": ["15:38", "16:59"],
    "auto mode": ["29:08"],
    "bypass permission": ["22:58", "23:20"],
}
EXPECTED_CLEAN = ["accept edits", "shift tab", "/compact", "/clear", "/context",
                  "limiar de 50%", "context rot", "1 milhão de tokens"]

AFFECTED_CASES = {
    "BC-001": ("Quais são os modos de permissão e o que cada um permite",
               "o corpus de treino nomeia três dos quatro modos; nomear não é "
               "saber o que cada um permite"),
    "BC-003": ("Diferença entre accept edits e auto",
               "`auto mode` aparece como uso; `accept edits` não aparece em "
               "lugar nenhum — a distinção entre os dois continua fora"),
    "BC-004": ("Condição e risco do bypass permissions",
               "`bypass permission` aparece duas vezes como uso em demo; a "
               "condição de ambiente e o risco não aparecem"),
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def scan(text: str, terms: dict[str, str]) -> dict[str, list[dict]]:
    """Ocorrências na FALA do cortado, com marca de tempo. Título não conta."""
    MARK = re.compile(r"^\*\*(\d{1,3}:[0-5]\d)\*\*$")
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    out = {k: [] for k in terms}
    cur = None
    for b in blocks:
        m = MARK.match(b)
        if m:
            cur = m.group(1)
            continue
        if b.startswith("## "):
            continue
        for label, rx in terms.items():
            for mm in re.finditer(rx, b, re.I):
                out[label].append({
                    "mark": cur,
                    "quote": " ".join(
                        b[max(0, mm.start() - 60):mm.end() + 60].split()),
                })
    return out


def titles(text: str) -> list[dict]:
    out = []
    for b in [x.strip() for x in text.split("\n\n") if x.strip()]:
        if b.startswith("## ") and ("Permission Modes" in b or
                                    "Context Window" in b):
            out.append({"line": b})
    return out


def main() -> int:
    try:
        ok = DOCS.is_dir()
    except OSError as e:
        ok = False
        print(f"ERRO DE MONTAGEM: {e}")
    if not ok:
        print(f"FONTE INDISPONÍVEL: {DRIVE} não está acessível.")
        print("O aditivo tem de ligar por SHA-256 ao lock e aos casos cegos, que "
              "vivem no Drive, e ser publicado lá. Sem o Drive não há hash para "
              "amarrar nem lugar para publicar. Nada foi publicado.")
        return 2

    missing = [p.name for p in (CUT, INTACT, LOCK, CASES, FREEZE) if not p.exists()]
    if missing:
        print("ARTEFATOS AUSENTES, não publico: " + ", ".join(missing))
        return 2

    cut_sha, intact_sha = sha(CUT), sha(INTACT)
    if cut_sha != EXPECTED_CUT or intact_sha != EXPECTED_INTACT:
        print("FONTE DIVERGENTE — não publico:")
        print(f"  cortado esperado {EXPECTED_CUT[:16]}… obtido {cut_sha[:16]}…")
        print(f"  íntegro esperado {EXPECTED_INTACT[:16]}… obtido {intact_sha[:16]}…")
        return 2

    text = CUT.read_text(encoding="utf-8")
    modes = scan(text, MODE_TERMS)
    teach = scan(text, TEACHING_TERMS)

    leaks = {k: v for k, v in modes.items() if v}
    clean = ([k for k, v in modes.items() if not v]
             + [k for k, v in teach.items() if not v])
    unexpected = {k: v for k, v in teach.items() if v}

    drift = []
    for label, marks in EXPECTED_LEAKS.items():
        got = [x["mark"] for x in leaks.get(label, [])]
        if got != marks:
            drift.append(f"{label}: esperado {marks}, obtido {got}")
    for label in EXPECTED_CLEAN:
        if label in leaks or label in unexpected:
            drift.append(f"{label}: esperado limpo, apareceu na fala")
    if unexpected:
        drift.append("ensinamento do held-out apareceu na fala: "
                     + ", ".join(unexpected))
    if drift:
        print("DIVERGÊNCIA entre a apuração anterior e a varredura ao vivo — "
              "não publico:")
        for d in drift:
            print("  -", d)
        return 2

    n_leaks = sum(len(v) for v in leaks.values())
    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-002-HELDOUT-RESIDUE-ADDENDUM",
        "artifact_status": "ADDENDUM_ONLY_BASE_LOCK_UNMODIFIED",
        "pilot_id": "PILOT-002",
        "published_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "nature": {
            "additive_only": True,
            "base_artifact_mutated": False,
            "statement": ("Aditivo. O lock congelado não foi lido para escrita, "
                          "editado nem reemitido. Este artefato acrescenta "
                          "divulgação de resíduo e se amarra ao lock por hash."),
        },
        "binds_to": {
            "heldout_lock": {"path": str(LOCK.relative_to(DRIVE)),
                             "sha256": sha(LOCK)},
            "blind_cases": {"path": str(CASES.relative_to(DRIVE)),
                            "sha256": sha(CASES)},
            "blind_cases_freeze_record": {"path": str(FREEZE.relative_to(DRIVE)),
                                          "sha256": sha(FREEZE)},
            "l0_cut": {"path": str(CUT.relative_to(DRIVE)), "sha256": cut_sha},
            "l0_intact": {"path": str(INTACT.relative_to(DRIVE)),
                          "sha256": intact_sha},
        },
        "why_this_addendum_exists": (
            "O lock declarou como resíduo apenas as duas linhas de TÍTULO das "
            "seções retiradas. Uma varredura posterior do corpo falado do L0 "
            "cortado encontrou mais: os NOMES de três dos quatro modos de "
            "permissão aparecem como narração de uso em outras seções. O "
            "conteúdo continua fora; os nomes não."),
        "residue_already_declared_in_lock": {
            "kind": "linhas de título de seção",
            "items": titles(text),
        },
        "residue_newly_disclosed": {
            "kind": "nomes de modo na fala, fora dos spans retirados",
            "count": n_leaks,
            "note": ("São narração de uso durante demonstração em outras seções, "
                     "não definição. Nenhuma condição de escolha e nenhuma linha "
                     "da tabela de quatro modos aparece."),
            "items": [{"term": k, "occurrences": v} for k, v in sorted(leaks.items())],
        },
        "verified_clean": {
            "statement": ("Estes termos NÃO aparecem no corpo falado do L0 "
                          "cortado."),
            "terms": sorted(clean),
            "context_window_section": {
                "verdict": "LIMPA",
                "detail": ("Nenhum ensinamento da seção de janela de contexto "
                           "vaza: nem /compact, nem /clear, nem /context, nem o "
                           "limiar de 50%, nem context rot, nem o total de 1 "
                           "milhão de tokens."),
            },
            "permission_modes_section": {
                "verdict": "NOMES VAZAM, DEFINIÇÕES NÃO",
                "detail": ("`accept edits` e `shift tab` não aparecem. `plan "
                           "mode`, `auto mode` e `bypass permission` aparecem "
                           "como uso."),
            },
        },
        "effect_on_blind_cases": {
            "rule_change": (
                "BC-001, BC-003 e BC-004 passam a testar SEMÂNTICA, não "
                "NOMEAÇÃO. Nomear um modo deixa de contar como acerto, porque o "
                "nome está disponível no corpus de treino. O que conta é dizer o "
                "que o modo permite, em que condição escolhê-lo e qual o risco."),
            "unchanged": (
                "BC-002 e BC-005 seguem como estavam. BC-006 a BC-010 seguem "
                "cegos: a seção de janela de contexto está limpa."),
            "cases": [{"case_id": k, "about": v[0], "why": v[1]}
                      for k, v in sorted(AFFECTED_CASES.items())],
            "scoring_consequence": (
                "Numa resposta que apenas liste nomes de modo, o rótulo correto "
                "é GENERAL_KNOWLEDGE ou inconclusivo — nunca SOURCE_EXPLICIT com "
                "crédito, porque a fonte de treino contém os nomes."),
        },
        "method": {
            "scan_scope": ("corpo falado do L0 cortado; linhas de título e marcas "
                           "de tempo excluídas da busca"),
            "evidence_regenerated_at_publish_time": True,
            "expectations_asserted": ("A apuração anterior entrou como "
                                      "expectativa; divergência abortaria a "
                                      "publicação."),
        },
        "does_not": [
            "não altera o lock congelado",
            "não altera os casos cegos nem o freeze record",
            "não recorta nada a mais do L0",
            "não congela lista canônica de nada",
        ],
    }

    OUT.write_text(
        "# HELDOUT-RESIDUE-ADDENDUM — PILOT-002\n"
        "# ADITIVO. O lock congelado não foi tocado.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"vazamentos de nome: {n_leaks} em {len(leaks)} termos")
    for k, v in sorted(leaks.items()):
        print(f"  {k}: {', '.join(x['mark'] for x in v)}")
    print(f"limpos: {len(clean)} termos | Context Window: LIMPA")
    print(f"casos afetados: {', '.join(sorted(AFFECTED_CASES))}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha(OUT)[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
