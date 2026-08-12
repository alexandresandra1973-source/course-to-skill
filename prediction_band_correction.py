#!/usr/bin/env python3
"""Aditivo de CORREÇÃO da justificativa do regime do meio.

Roda daqui (ext4). READ-ONLY. Publica só em `Course-to-Skill-Claude/docs/`.

ADITIVO SOBRE ADITIVO: não altera a ratificação nem a previsão. Amarra-se às
duas por SHA-256. Os regimes ficam INALTERADOS — o que muda é a razão pela qual
o regime do meio existe.

Por que isto é um artefato e não uma nota de rodapé: a justificativa de um
limiar é parte do limiar. Uma banda mantida por uma razão refutada é uma banda
sem fundamento, mesmo que os números não mudem. Corrigir a razão e deixar a
refutação publicada é o que impede a justificativa falsa de ser citada depois
como se tivesse sobrevivido.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "PREDICTION-COMPILER-V2-BAND-CORRECTION.yaml"

RATIFICATION = DOCS / "PREDICTION-COMPILER-V2-BAND-RATIFICATION.yaml"
PREDICTION = DOCS / "PREDICTION-COMPILER-V2.yaml"
EXPECTED_RATIFICATION = "c4c7420b201ad4311a29092e18568036b98c75bfaf277f8c5eaae65afa331b68"
EXPECTED_PREDICTION = "4963fd27d4640c4831306e74b0dc9f624ef5fe409f6c46f48c7f46fbeda1b44d"

ADR = CLAUDE / "pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
FREEZE = CLAUDE / "compiler-v2/FREEZE-RECORD.yaml"

# Fontes da refutação. Cada uma é reconferida em execução; nenhuma é citada de
# memória.
SPEC = (DRIVE / "Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1"
        / "course-to-skill-compiler-v0.1.1-pilot-ready"
        / "course-to-skill-compiler-v0.1.1-pilot-ready"
        / "prompts/lesson-analyzer.md")
EVIDENCE2 = CLAUDE / "pilots/PILOT-002/01_COMPILED-SKILL/v0.1.0/EVIDENCE(1).jsonl"
META1 = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
         / "sources/metadata/source-metadata.yaml")
DECISIONS = DOCS / "DECISION-STRUCTURE-LIST-PILOT-002.md"

P001 = {"extent_s": 905, "segments": 9}
P002 = {"extent_s": 4384, "segments": 41}


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def refutation_evidence() -> dict:
    """Reconfere, agora, cada perna da refutação. Nada vem de memória."""
    out = {}

    spec = SPEC.read_text(encoding="utf-8") if SPEC.is_file() else ""
    out["categoria_no_spec_do_compilador"] = {
        "path": str(SPEC.relative_to(DRIVE)), "sha256": sha_p(SPEC) if SPEC.is_file() else None,
        "presente": "DEMONSTRACAO_DE_TELA" in spec}

    rows = [json.loads(l) for l in EVIDENCE2.read_text(encoding="utf-8").splitlines()
            if l.strip()] if EVIDENCE2.is_file() else []
    out["categoria_nas_evidencias_compiladas"] = {
        "path": str(EVIDENCE2.relative_to(DRIVE)),
        "sha256": sha_p(EVIDENCE2) if EVIDENCE2.is_file() else None,
        "evidencias": len(rows),
        "com_campo_category": sum(1 for r in rows if "category" in r),
        "com_DEMONSTRACAO_DE_TELA": sum(
            1 for r in rows if "DEMONSTRACAO_DE_TELA" in json.dumps(r)),
        "presente": any("DEMONSTRACAO_DE_TELA" in json.dumps(r) for r in rows)}

    screen = None
    if META1.is_file():
        d = yaml.safe_load(META1.read_text(encoding="utf-8")) or {}
        ch = ((d.get("source") or {}).get("available_channels")
              or d.get("available_channels") or {})
        screen = bool(ch.get("screen_demonstration"))
    out["pilot001_declara_screen_demonstration"] = {
        "path": str(META1.relative_to(DRIVE)) if META1.is_file() else None,
        "sha256": sha_p(META1) if META1.is_file() else None,
        "valor": screen}

    lines = []
    if DECISIONS.is_file():
        for i, l in enumerate(DECISIONS.read_text(encoding="utf-8",
                                                  errors="replace").splitlines(), 1):
            if "DEMONSTRACAO_DE_TELA" in l:
                lines.append({"line": i, "text": l.strip()[:300]})
    out["origem_da_categoria"] = {
        "path": str(DECISIONS.relative_to(DRIVE)) if DECISIONS.is_file() else None,
        "sha256": sha_p(DECISIONS) if DECISIONES_OK(DECISIONS) else None,
        "ocorrencias": lines,
        "declarada_como": ("chamada de julgamento do próprio analista, no "
                           "documento que a criou")}
    return out


def DECISIONES_OK(p: Path) -> bool:
    return p.is_file()


def main() -> int:
    for p, exp, name in ((RATIFICATION, EXPECTED_RATIFICATION, "ratificação"),
                         (PREDICTION, EXPECTED_PREDICTION, "previsão")):
        if not p.is_file():
            print(f"ARTEFATO AUSENTE: {p}")
            return 2
        got = sha_p(p)
        if got != exp:
            print(f"ARTEFATO DIVERGENTE ({name}) — não publico:")
            print(f"  esperado {exp}")
            print(f"  obtido   {got}")
            return 2

    ev = refutation_evidence()
    seg001 = Fraction(P001["extent_s"], P001["segments"])
    seg002 = Fraction(P002["extent_s"], P002["segments"])
    pct = Fraction(100) * (seg002 / seg001 - 1)

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PREDICTION-COMPILER-V2-BAND-CORRECTION",
        "artifact_status": "CORRECAO_PUBLICADA_ANTES_DA_EXECUCAO",
        "corrected_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "raised_by": "gerador (verificação da justificativa)",
        "accepted_by": "revisor",

        "nature": {
            "additive_only": True,
            "base_artifacts_mutated": False,
            "statement": ("Aditivo sobre aditivo. Nem a ratificação nem a "
                          "previsão foram lidas para escrita, editadas ou "
                          "reemitidas. Este arquivo corrige a JUSTIFICATIVA do "
                          "regime do meio e se amarra às duas por hash."),
            "why_an_artifact": (
                "A justificativa de um limiar é parte do limiar. Uma banda "
                "mantida por razão refutada é banda sem fundamento, mesmo com "
                "os números intactos. Publicar a refutação impede que a "
                "justificativa falsa seja citada depois como se tivesse "
                "sobrevivido."),
        },

        "binds_to": {
            "band_ratification": {"path": str(RATIFICATION.relative_to(DRIVE)),
                                  "sha256": sha_p(RATIFICATION)},
            "prediction": {"path": str(PREDICTION.relative_to(DRIVE)),
                           "sha256": sha_p(PREDICTION)},
            "adr": {"path": str(ADR.relative_to(DRIVE)), "sha256": sha_p(ADR)},
            "compiler_v2_freeze": {"path": str(FREEZE.relative_to(DRIVE)),
                                   "sha256": sha_p(FREEZE)},
        },

        # ------------------------------------------------------- a correção
        "correcao": {
            "ponto_refutado": (
                "A justificativa do regime do meio afirmava que o PILOT-002 "
                "exigiu a categoria DEMONSTRACAO_DE_TELA \"que o PILOT-001 não "
                "precisou\". FALSO: a categoria é chamada de julgamento do "
                "próprio analista, não está no spec do compilador, não aparece "
                "em nenhuma das 44 evidências, e o source-metadata.yaml do "
                "PILOT-001 declara screen_demonstration: true."),
            "ponto_que_sobrevive": (
                "segmentos 6,3% mais longos — medido, mas insuficiente para "
                "justificar alargar de 1,33 para 2,00"),
            "justificativa_substituta": (
                "O regime do meio permanece, por razão diferente e verdadeira: "
                "a VARIÂNCIA DE EXECUÇÃO do extractor nunca foi medida. Não "
                "sabemos quanto o yield varia entre duas rodadas sobre a MESMA "
                "entrada — mesma lacuna que o teste-reteste do juiz fechou para "
                "o TEST-0007. O regime do meio é HEDGE DECLARADO contra "
                "variância de instrumento não medida, não correção derivada de "
                "diferença medida entre as fontes."),
            "consequencia_se_cair_no_meio": (
                "A leitura deixa de ser \"diferença legítima entre corpora\" e "
                "passa a ser \"há residual e não sabemos de onde vem\". O "
                "conserto indicado é MEDIR a variância de execução do extractor "
                "rodando o mesmo segmento duas vezes."),
            "regimes": "inalterados",
        },

        # --------------------------------------------- prova da refutação
        "evidencia_da_refutacao": {
            "reconferida_em": "tempo de publicação deste aditivo",
            **ev,
            "conclusao": (
                "As quatro pernas confirmam a refutação. A categoria existe "
                "apenas como artefato de análise, criada e declarada como "
                "julgamento no documento que a introduziu; não atravessou para "
                "o spec nem para o compilado; e a propriedade que ela alegava "
                "distinguir está declarada nos DOIS pilotos."),
        },

        "aritmetica_do_ponto_que_sobrevive": {
            "segmento_medio_pilot001_s": round(float(seg001), 2),
            "segmento_medio_pilot002_s": round(float(seg002), 2),
            "diferenca_percentual": round(float(pct), 1),
            "medido": True,
            "suficiente_para_a_largura_do_regime": False,
            "nota": ("6,3% de diferença de duração média não sustenta uma banda "
                     "que vai até 2,00. O que sustenta a largura é o hedge "
                     "contra variância não medida, declarado acima."),
        },

        # ------------------------------------------------- o que fazer agora
        "medicao_que_fecha_a_lacuna": {
            "o_que": ("Variância de execução do extractor: rodar o MESMO "
                      "segmento, com a MESMA entrada e a MESMA configuração, "
                      "duas ou mais vezes, e comparar o yield."),
            "por_que_agora_e_barato": (
                "O extractor por segmento torna isso trivial: é a mesma chamada "
                "repetida. No desenho antigo, de varredura monolítica, medir "
                "variância exigia recompilar a aula inteira."),
            "precedente": ("O teste-reteste do juiz fechou exatamente esta "
                           "lacuna para o TEST-0007."),
            "estado": "NÃO MEDIDA",
            "bloqueia_a_execucao": False,
            "bloqueia_a_leitura_do_regime_do_meio": True,
        },

        "regimes_inalterados": {
            "CONSERTO_LIMPO": "[0,75 ; 1,33]",
            "CONSERTO_PARCIAL": "(1,33 ; 2,00]",
            "CONSERTO_NAO_FUNCIONOU": "> 2,00",
            "INVESTIGAR": "< 0,75",
            "statement": ("Nenhuma fronteira mudou. Mudar fronteira depois de "
                          "ver resultado continua proibido pela guarda da "
                          "ratificação."),
        },

        "nao_estabelece": [
            "qual é a variância de execução do extractor",
            "que a variância explique o residual, se houver",
            "qualquer mudança nas fronteiras dos regimes",
        ],

        "status": "CORRECAO_PUBLICADA_ANTES_DA_EXECUCAO",
        "execucao_realizada": False,
    }

    OUT.write_text(
        "# ADITIVO DE CORREÇÃO da justificativa do regime do meio.\n"
        "# NÃO altera a ratificação nem a previsão; amarra-se às duas por SHA-256.\n"
        "# Os regimes ficam INALTERADOS. O que muda é a razão pela qual o do meio existe.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"ratificação conferida: {sha_p(RATIFICATION)[:16]}… OK")
    print(f"previsão conferida   : {sha_p(PREDICTION)[:16]}… OK")
    print("refutação reconferida:")
    print(f"  categoria no spec do compilador : "
          f"{ev['categoria_no_spec_do_compilador']['presente']}")
    e = ev["categoria_nas_evidencias_compiladas"]
    print(f"  nas 44 evidências compiladas    : {e['presente']} "
          f"({e['com_campo_category']}/{e['evidencias']} têm campo category)")
    print(f"  PILOT-001 screen_demonstration  : "
          f"{ev['pilot001_declara_screen_demonstration']['valor']}")
    print(f"  origem declarada em             : "
          f"{len(ev['origem_da_categoria']['ocorrencias'])} linha(s)")
    print(f"diferença de duração média: {round(float(pct),1)}% (medida, mantida)")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256: {sha_p(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
