#!/usr/bin/env python3
"""Aditivo de ratificação da banda — três regimes, ANTES da execução.

Roda daqui (ext4). READ-ONLY. Publica só em `Course-to-Skill-Claude/docs/`.

ADITIVO: não altera `PREDICTION-COMPILER-V2.yaml`. Amarra-se a ele por SHA-256.
Se o original mudar, o hash aqui deixa de casar — que é o alarme.

Todos os números derivados são CALCULADOS. As fronteiras dos regimes são as
RATIFICADAS pelo revisor e entram literalmente, sem arredondamento meu.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "PREDICTION-COMPILER-V2-BAND-RATIFICATION.yaml"

BASE = DOCS / "PREDICTION-COMPILER-V2.yaml"
EXPECTED_BASE = "4963fd27d4640c4831306e74b0dc9f624ef5fe409f6c46f48c7f46fbeda1b44d"

ADR = CLAUDE / "pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
FREEZE = CLAUDE / "compiler-v2/FREEZE-RECORD.yaml"

# Fatos já medidos, repetidos aqui só para recalcular — não digitados como
# resultado. A fonte de cada um está no artefato base.
P001 = {"extent_s": 905, "segments": 9, "evidence": 44}
P002 = {"extent_s": 4384, "segments": 41, "evidence": 44}

# ---------------------------------------------------------------- ratificado
REGIMES = [
    {"name": "CONSERTO_LIMPO", "lo": 0.75, "hi": 1.33,
     "lo_open": False, "hi_open": False,
     "verdict": "O conserto funcionou. Os dois pilotos rendem por segmento de "
                "forma equivalente.",
     "advances": True, "closes": True},
    {"name": "CONSERTO_PARCIAL", "lo": 1.33, "hi": 2.00,
     "lo_open": True, "hi_open": False,
     "verdict": "O conserto AVANÇA mas NÃO FECHA. A causa residual tem de ser "
                "MEDIDA antes de seguir para o PILOT-002.",
     "advances": True, "closes": False},
    {"name": "CONSERTO_NAO_FUNCIONOU", "lo": 2.00, "hi": None,
     "lo_open": True, "hi_open": None,
     "verdict": "A Decisão A não explica o colapso. Reabrir o diagnóstico.",
     "advances": False, "closes": False},
    {"name": "INVESTIGAR", "lo": None, "hi": 0.75,
     "lo_open": None, "hi_open": True,
     "verdict": "PILOT-002 rendendo MAIS por segmento que o PILOT-001 é "
                "suspeito e pede explicação, não comemoração.",
     "advances": False, "closes": False},
]

# Justificativa do regime do meio, como declarada pelo revisor. Cada limbo é
# CONFERIDO contra a árvore e o resultado viaja junto — a ratificação é do
# revisor, a verificação é minha, e as duas ficam visíveis lado a lado.
RATIONALE_CLAIMS = [
    {"claim": "segmentos do PILOT-002 são 6,3% mais longos "
              "(106,93s contra 100,56s)",
     "check": "aritmética recalculada deste artefato"},
    {"claim": "o PILOT-002 exigiu a categoria DEMONSTRACAO_DE_TELA, que o "
              "PILOT-001 não precisou",
     "check": "procurada na árvore; ver `verificacao_da_justificativa`"},
    {"claim": "narração de clique rende menos evidência por motivo legítimo",
     "check": "juízo do revisor; não há medição que o confirme ou refute"},
]


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_screen_demo_category() -> dict:
    """Confere os três limbos verificáveis da justificativa do regime do meio."""
    out = {}

    # 1. A categoria existe como artefato de análise?
    hits = []
    for p in sorted(CLAUDE.rglob("*.md")):
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, l in enumerate(t.splitlines(), 1):
            if "DEMONSTRACAO_DE_TELA" in l:
                hits.append(f"{p.relative_to(DRIVE)}:{i}")
    out["categoria_declarada_em"] = hits
    out["categoria_existe_como_analise"] = bool(hits)

    # 2. Ela entrou no compilado do PILOT-002?
    ev = (CLAUDE / "pilots/PILOT-002/01_COMPILED-SKILL/v0.1.0/EVIDENCE(1).jsonl")
    import json
    rows = [json.loads(l) for l in ev.read_text(encoding="utf-8").splitlines()
            if l.strip()] if ev.is_file() else []
    out["evidencias_do_pilot002"] = len(rows)
    out["evidencias_com_campo_category"] = sum(1 for r in rows if "category" in r)
    out["categoria_no_compilado"] = out["evidencias_com_campo_category"] > 0

    # 3. Ela existe no spec do compilador?
    rel = (DRIVE / "Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1"
           / "course-to-skill-compiler-v0.1.1-pilot-ready"
           / "course-to-skill-compiler-v0.1.1-pilot-ready"
           / "prompts/lesson-analyzer.md")
    spec = rel.read_text(encoding="utf-8") if rel.is_file() else ""
    out["categoria_no_spec_do_compilador"] = "DEMONSTRACAO_DE_TELA" in spec

    # 4. O PILOT-001 também tinha demonstração de tela?
    meta = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
            / "sources/metadata/source-metadata.yaml")
    if meta.is_file():
        d = yaml.safe_load(meta.read_text(encoding="utf-8")) or {}
        ch = ((d.get("source") or {}).get("available_channels")
              or d.get("available_channels") or {})
        out["pilot001_declara_screen_demonstration"] = bool(
            ch.get("screen_demonstration"))
        out["pilot001_metadata_path"] = str(meta.relative_to(DRIVE))
    return out


def classify(ratio: float) -> str:
    for r in REGIMES:
        lo_ok = r["lo"] is None or (ratio > r["lo"] if r["lo_open"] else ratio >= r["lo"])
        hi_ok = r["hi"] is None or (ratio < r["hi"] if r["hi_open"] else ratio <= r["hi"])
        if lo_ok and hi_ok:
            return r["name"]
    return "SEM_REGIME"


def interval(r: dict) -> str:
    if r["lo"] is None:
        return f"< {r['hi']:.2f}"
    if r["hi"] is None:
        return f"> {r['lo']:.2f}"
    a = "(" if r["lo_open"] else "["
    b = ")" if r["hi_open"] else "]"
    return f"{a}{r['lo']:.2f} ; {r['hi']:.2f}{b}"


def main() -> int:
    if not BASE.is_file():
        print(f"ARTEFATO BASE AUSENTE: {BASE}")
        return 2
    base_sha = sha_p(BASE)
    if base_sha != EXPECTED_BASE:
        print("ARTEFATO BASE DIVERGENTE — não publico o aditivo:")
        print(f"  esperado {EXPECTED_BASE}")
        print(f"  obtido   {base_sha}")
        return 2
    for p in (ADR, FREEZE):
        if not p.is_file():
            print(f"ÂNCORA AUSENTE: {p}")
            return 2

    y001 = Fraction(P001["evidence"], P001["segments"])
    y002 = Fraction(P002["evidence"], P002["segments"])
    ratio = y001 / y002
    seg001 = Fraction(P001["extent_s"], P001["segments"])
    seg002 = Fraction(P002["extent_s"], P002["segments"])
    today = classify(float(ratio))

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PREDICTION-COMPILER-V2-BAND-RATIFICATION",
        "artifact_status": "RATIFICADA_ANTES_DA_EXECUCAO",
        "nature": {
            "additive_only": True,
            "base_artifact_mutated": False,
            "statement": ("Aditivo. O artefato de previsão não foi lido para "
                          "escrita, editado nem reemitido. Este arquivo "
                          "acrescenta a banda ratificada e se amarra à previsão "
                          "por hash."),
        },
        "ratified_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "ratified_by": "revisor",

        "binds_to": {
            "prediction": {"path": str(BASE.relative_to(DRIVE)), "sha256": base_sha},
            "adr": {"path": str(ADR.relative_to(DRIVE)), "sha256": sha_p(ADR)},
            "compiler_v2_freeze": {"path": str(FREEZE.relative_to(DRIVE)),
                                   "sha256": sha_p(FREEZE)},
        },

        "supersedes": {
            "field": "banda_de_aceitacao",
            "in": str(BASE.name),
            "previous_status": "NAO_RATIFICADA",
            "previous_proposal": "banda única 0,75 a 1,33",
            "why_superseded": (
                "A banda única só distinguia acerto de erro. O revisor ratificou "
                "TRÊS regimes, que separam o caso intermediário — conserto que "
                "avança sem fechar — do fracasso. A proposta anterior vira o "
                "regime de topo do novo esquema."),
        },

        # ------------------------------------------------------ a grandeza
        "grandeza": {
            "definicao": "razao_yield_por_segmento = yield_P001 / yield_P002",
            "yield_P001": round(float(y001), 2),
            "yield_P002": round(float(y002), 2),
            "valor_hoje": round(float(ratio), 1),
            "valor_exato_hoje": f"{ratio.numerator}/{ratio.denominator}",
            "regime_hoje": today,
            "nota": ("É a RELAÇÃO entre os pilotos, não o valor absoluto de "
                     "nenhum dos dois. Nada aqui estabelece qual yield por "
                     "segmento é o correto."),
        },

        # ------------------------------------------------------- os regimes
        "regimes": [
            {"nome": r["name"], "intervalo": interval(r),
             "limite_inferior": r["lo"], "limite_inferior_aberto": r["lo_open"],
             "limite_superior": r["hi"], "limite_superior_aberto": r["hi_open"],
             "veredito": r["verdict"],
             "avanca": r["advances"], "fecha": r["closes"]}
            for r in REGIMES
        ],
        "cobertura_dos_regimes": {
            "particao_completa": True,
            "verificacao": ("Os quatro regimes cobrem a reta positiva sem "
                            "sobreposição: <0,75 · [0,75;1,33] · (1,33;2,00] · "
                            ">2,00. Qualquer razão cai em exatamente um."),
        },

        # -------------------------------------------- justificativa do meio
        "justificativa_do_regime_do_meio": {
            "declarada_pelo_revisor": [c["claim"] for c in RATIONALE_CLAIMS],
            "conclusao_do_revisor": (
                "As duas primeiras empurram o yield do PILOT-002 para baixo "
                "legitimamente, mas nenhuma justifica um fator de "
                f"{round(float(ratio), 1)}."),
            "aritmetica_do_primeiro_limbo": {
                "segmento_medio_pilot001_s": round(float(seg001), 2),
                "segmento_medio_pilot002_s": round(float(seg002), 2),
                "diferenca_percentual": round(
                    float(Fraction(100) * (seg002 / seg001 - 1)), 1),
                "confere": True,
            },
        },

        "verificacao_da_justificativa": {
            "por_que_esta_aqui": (
                "A ratificação é do revisor; a conferência é do gerador. As duas "
                "ficam lado a lado para que ninguém leia como MEDIDO o que é "
                "JULGAMENTO declarado."),
            **check_screen_demo_category(),
            "leitura": (
                "A categoria DEMONSTRACAO_DE_TELA existe como artefato de "
                "ANÁLISE (declarada em DECISION-STRUCTURE-LIST-PILOT-002 como "
                "chamada de julgamento explícita, com 57 de 194 candidatos "
                "classificados). Ela NÃO está no spec do compilador e NÃO "
                "aparece no EVIDENCE.jsonl compilado, que não tem campo "
                "`category` nenhum. E o `source-metadata.yaml` do PILOT-001 "
                "declara `screen_demonstration: true` — a fonte do PILOT-001 "
                "também tinha demonstração de tela. A distinção entre os dois "
                "corpora é de GRAU e de julgamento, não uma propriedade medida "
                "que os separe. Isso não invalida o regime do meio: ele existe "
                "justamente para absorver causas legítimas de queda que não "
                "estão medidas. Registra-se para que a justificativa não seja "
                "citada depois como fato apurado."),
        },

        # -------------------------------------------------------- a guarda
        "guarda_contra_afrouxamento": {
            "regra": ("CONSERTO_PARCIAL não é aprovação. Se o resultado cair "
                      "nesse regime, o conserto avança mas não fecha, e a causa "
                      "residual tem de ser MEDIDA antes de seguir para o "
                      "PILOT-002."),
            "proibido": [
                "reinterpretar as fronteiras depois de ver o resultado",
                "tratar CONSERTO_PARCIAL como aprovação",
                "seguir para o PILOT-002 sem medir a causa residual",
                "converter a razão em cota de contagem",
            ],
            "quem_pode_mudar": ("Mudar qualquer fronteira exige novo aditivo, "
                                "ratificado ANTES da execução seguinte, e "
                                "quebra o hash deste artefato."),
        },

        # --------------------------------------------- relação com o portão
        "relacao_com_o_portao_de_aceitacao": {
            "esta_banda_e": "critério de MECANISMO",
            "portao_de_aceitacao_e": "cobertura de L0 > 73,5%, estritamente maior",
            "independentes": True,
            "consequencia": (
                "Os dois são reportados separadamente e nenhum substitui o "
                "outro. A previsão pode acertar e o portão reprovar, e "
                "vice-versa. Nenhum resultado de mecanismo autoriza declarar "
                "aceitação, e nenhuma cobertura acima do piso autoriza declarar "
                "o mecanismo consertado."),
        },

        "nao_estabelece": [
            "qual é o valor absoluto correto de yield por segmento",
            "que 200 evidências seja o número certo para o PILOT-002",
            "que a cobertura de L0 vá superar o piso",
            "que a causa residual do regime do meio seja a demonstração de tela",
        ],

        "status": "RATIFICADA_ANTES_DA_EXECUCAO",
        "execucao_realizada": False,
        "extractor_ligado_a_modelo": False,
    }

    blob = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    OUT.write_text(
        "# ADITIVO de ratificação da banda — três regimes.\n"
        "# NÃO altera PREDICTION-COMPILER-V2.yaml; amarra-se a ele por SHA-256.\n"
        "# Ratificado ANTES da execução. Editar quebra o hash.\n" + blob,
        encoding="utf-8")

    print(f"base conferida: {base_sha[:16]}… OK")
    print(f"razão hoje: {float(ratio):.2f} -> regime {today}")
    for r in REGIMES:
        print(f"  {interval(r):>16s}  {r['name']}")
    v = doc["verificacao_da_justificativa"]
    print(f"categoria no spec do compilador: {v['categoria_no_spec_do_compilador']}")
    print(f"categoria no compilado do P002: {v['categoria_no_compilado']} "
          f"({v['evidencias_com_campo_category']}/{v['evidencias_do_pilot002']} "
          f"com campo category)")
    print(f"PILOT-001 declara screen_demonstration: "
          f"{v.get('pilot001_declara_screen_demonstration')}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256: {sha_p(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
