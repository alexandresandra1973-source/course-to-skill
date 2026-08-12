#!/usr/bin/env python3
"""Aditivo: regra PRÉ-REGISTRADA de leitura do portão.

Roda daqui (ext4). READ-ONLY. Publica só em `Course-to-Skill-Claude/docs/`.

ADITIVO à ressalva de cobertura, amarrado a ela por SHA-256. Publicado ANTES da
execução — é essa a única coisa que faz dele pré-registro e não racionalização.

NÃO altera o portão.
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "GATE-READING-RULE-PREREGISTERED.yaml"

CAVEAT = DOCS / "L0-COVERAGE-DECLARED-VS-EVIDENCED-CAVEAT.yaml"
PREDICTION = DOCS / "PREDICTION-COMPILER-V2.yaml"
ADR = CLAUDE / "pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
FREEZE = CLAUDE / "compiler-v2/FREEZE-RECORD.yaml"

EXPECTED_CAVEAT = "b105f6c6d3b871ddcd04f02322487fc4132f14e1c5a21f560cce79fa061eec54"
EXPECTED_PREDICTION = "4963fd27d4640c4831306e74b0dc9f624ef5fe409f6c46f48c7f46fbeda1b44d"

EV1 = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
       / "analysis/evidence.jsonl")
TRACE0 = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude"
              "/canary-trace-run0-promptantigo.json")


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hhmmss(t: str) -> int:
    q = [int(x) for x in t.split(":")]
    return q[0] * 3600 + q[1] * 60 + q[2]


def historical_quote_availability() -> dict:
    rows = [json.loads(l) for l in EV1.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    with_q = sum(1 for r in rows if r.get("source_excerpt"))
    widths = []
    for r in rows:
        for ref in (r.get("source_refs") or []):
            ts = ref.get("timestamp") or {}
            if ts.get("start") and ts.get("end"):
                widths.append(hhmmss(ts["end"]) - hhmmss(ts["start"]))
    return {"path": str(EV1.relative_to(DRIVE)), "sha256": sha_p(EV1),
            "evidencias": len(rows), "com_source_excerpt": with_q,
            "spans_declarados": len(widths),
            "mediana_span_s": statistics.median(widths),
            "media_span_s": round(statistics.mean(widths), 1),
            "min_span_s": min(widths), "max_span_s": max(widths)}


def canary_span_widths() -> dict:
    d = json.loads(TRACE0.read_text(encoding="utf-8"))
    w = [x["end_s"] - x["start_s"] for x in d["drafts"]]
    return {"origem": "canário SEG-005, compilador v2, prompt antigo",
            "evidencias": len(w), "mediana_span_s": statistics.median(w),
            "media_span_s": round(statistics.mean(w), 1),
            "min_span_s": min(w), "max_span_s": max(w)}


def main() -> int:
    for p, exp, nome in ((CAVEAT, EXPECTED_CAVEAT, "ressalva"),
                         (PREDICTION, EXPECTED_PREDICTION, "previsão")):
        if not p.is_file():
            print(f"ÂNCORA AUSENTE: {p}")
            return 2
        if sha_p(p) != exp:
            print(f"ÂNCORA DIVERGENTE ({nome}):\n  esperado {exp}\n  obtido   {sha_p(p)}")
            return 2

    hist = historical_quote_availability()
    can = canary_span_widths()
    proxy = round(can["mediana_span_s"] / hist["mediana_span_s"], 2)

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "GATE-READING-RULE-PREREGISTERED",
        "artifact_status": "PRE_REGISTRADA_ANTES_DA_EXECUCAO",
        "registered_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "registered_by": "revisor",

        "nature": {
            "additive_only": True,
            "changes_the_gate": False,
            "statement": ("Aditivo à ressalva de cobertura. Não altera o piso de "
                          "73,5%, a métrica nem a previsão. Publicado ANTES da "
                          "execução — é isso que o torna pré-registro."),
        },

        "binds_to": {
            "coverage_caveat": {"path": str(CAVEAT.relative_to(DRIVE)),
                                "sha256": sha_p(CAVEAT)},
            "prediction": {"path": str(PREDICTION.relative_to(DRIVE)),
                           "sha256": sha_p(PREDICTION)},
            "adr": {"path": str(ADR.relative_to(DRIVE)), "sha256": sha_p(ADR)},
            "compiler_v2_freeze": {"path": str(FREEZE.relative_to(DRIVE)),
                                   "sha256": sha_p(FREEZE)},
        },

        # ------------------------------------------------- a regra, verbatim
        "regra_de_leitura_do_portao": {
            "condicao": ("cobertura da rodada corrigida cai PERTO do piso de "
                         "73,5%"),
            "proibicao": ("o veredito do portão NÃO pode ser lido antes de "
                          "comparar a razão declarado÷sustentado entre a rodada "
                          "histórica e a corrigida"),
            "razao": ("o piso 73,5% foi medido com spans inflados; se a rodada "
                      "corrigida declarar spans mais apertados, a mesma "
                      "qualidade real produz número menor, e o portão reprova "
                      "quem merecia passar"),
            "acao_se_a_razao_nova_for_menor": ("recalibrar o piso antes de "
                                               "reprovar, com o método declarado "
                                               "antes de ver o resultado"),
            "status": "PRE_REGISTRADA_ANTES_DA_EXECUCAO",
        },

        # ------------------------------- o insumo que a regra pede e não existe
        "bloqueio_material_da_regra": {
            "achado": ("A razão declarado÷sustentado da rodada HISTÓRICA é "
                       "INOBTENÍVEL: as 44 evidências do PILOT-001 antigo não "
                       "têm citação nenhuma. `source_excerpt` é nulo em "
                       f"{hist['evidencias']}/{hist['evidencias']}."),
            "consequencia": (
                "Sem citação histórica não há como medir quanto daquele span "
                "declarado era sustentado. A comparação que a regra exige tem um "
                "dos dois lados ausente, e nenhuma medição futura o recupera — o "
                "dado nunca foi gravado."),
            "evidencia": hist,
            "por_que_isto_importa_mais_que_a_regra": (
                "O piso de 73,5% é, portanto, um número cuja inflação não pode "
                "ser quantificada nem hoje nem nunca. Ele continua servindo como "
                "piso histórico — foi para isso que a ADR o congelou — mas a "
                "correção que a regra pede não é computável."),
        },

        # --------------------------------------- ao que a regra fica reduzida
        "metodo_pre_declarado": {
            "recalibracao_automatica": "IMPOSSIVEL",
            "por_que": (
                "Qualquer fórmula que ajuste o piso precisa da razão histórica, "
                "que não existe. Declarar aqui uma fórmula que use um substituto "
                "seria inventar precisão — exatamente o vício que a ressalva de "
                "cobertura recusou ao NÃO multiplicar 73,5% por 0,51."),
            "acao_pre_declarada": (
                "Se a cobertura corrigida cair na FAIXA DE INDECISÃO abaixo, o "
                "veredito do portão fica SUSPENSO — nem aprovado nem reprovado — "
                "e a decisão sobe para o revisor com os dois números na mesa: a "
                "cobertura declarada e a razão declarado÷sustentado da rodada "
                "corrigida. Suspender é o único movimento honesto quando falta "
                "metade da comparação."),
            "fora_da_faixa": ("Acima do topo da faixa, o portão é lido "
                              "normalmente e APROVA. Abaixo da base, REPROVA — a "
                              "distância é grande demais para ser explicada por "
                              "diferença de aperto de span."),
        },

        "faixa_de_indecisao": {
            "proposta": {"de": 0.685, "ate": 0.785},
            "expressa_como": "piso 0,735 ± 0,05 absoluto",
            "status": "NAO_RATIFICADA",
            "por_que_precisa_de_numero": (
                "'PERTO do piso' não é falsificável sem fronteira — mesmo "
                "problema de 'próxima de 1,0' na banda de yield. Sem "
                "ratificação ANTES da execução, 'perto' vira julgamento "
                "pós-resultado, que é o que o pré-registro existe para impedir."),
            "regra": ("Se esta faixa não for ratificada antes da execução, a "
                      "condição 'perto do piso' permanece qualitativa e nenhum "
                      "resultado pode ser declarado suspenso por proximidade."),
        },

        # ------------------------------------------- o proxy que É mensurável
        "proxy_mensuravel_do_aperto_de_span": {
            "o_que_e": ("Largura do span DECLARADO não depende de citação, então "
                        "é comparável entre as duas gerações. Não mede "
                        "declarado÷sustentado; mede a DIREÇÃO do risco que a "
                        "regra antecipa."),
            "historico": {k: hist[k] for k in
                          ("mediana_span_s", "media_span_s", "min_span_s",
                           "max_span_s", "spans_declarados")},
            "compilador_v2": can,
            "razao_das_medianas_v2_sobre_historico": proxy,
            "leitura": (
                f"O v2 declara spans com mediana {can['mediana_span_s']}s contra "
                f"{hist['mediana_span_s']}s do histórico — razão {proxy}. A "
                "direção do risco que a regra antecipa está CONFIRMADA: o "
                "compilador corrigido declara spans mais apertados."),
            "limite": (
                "Isto NÃO autoriza escalar o piso por 0,70. Cobertura é união, e "
                "união depende de contagem × largura × sobreposição; o v2 produz "
                "MAIS evidências, o que empurra a união para cima enquanto a "
                "largura a empurra para baixo. Os dois efeitos não se cancelam "
                "de forma calculável a priori. O proxy indica direção, não "
                "magnitude."),
            "base_amostral": ("10 evidências de UM segmento contra 47 spans de "
                              "44 evidências do corpus inteiro. Amostra pequena "
                              "de um lado."),
        },

        "o_que_esta_regra_NAO_faz": [
            "não altera o piso de 73,5%",
            "não autoriza recalibrar o piso por fórmula",
            "não converte o proxy de largura em fator de correção",
            "não decide nada sobre a rodada corrigida antes de ela existir",
        ],

        "status": "PRE_REGISTRADA_ANTES_DA_EXECUCAO",
        "execucao_realizada": False,
        "portao_alterado": False,
    }

    OUT.write_text(
        "# REGRA PRÉ-REGISTRADA de leitura do portão.\n"
        "# Aditivo à ressalva de cobertura; amarrada por SHA-256.\n"
        "# Publicada ANTES da execução. NÃO altera o portão.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"ressalva conferida: {sha_p(CAVEAT)[:16]}… OK")
    print(f"razão histórica declarado÷sustentado: INOBTENÍVEL "
          f"({hist['com_source_excerpt']}/{hist['evidencias']} com citação)")
    print(f"proxy de aperto de span (mediana v2/histórico): {proxy} "
          f"({can['mediana_span_s']}s vs {hist['mediana_span_s']}s)")
    print(f"faixa de indecisão proposta: 0,685–0,785 (NÃO RATIFICADA)")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256: {sha_p(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
