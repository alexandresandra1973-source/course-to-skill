#!/usr/bin/env python3
"""Pendência do PASS 1 + aposentadoria do aviso claim×literal.

Roda daqui (ext4). READ-ONLY sobre `Course-to-Skill/`. Publica só em
`Course-to-Skill-Claude/docs/`. Amarrado por SHA-256 ao manifesto da rodada.

NÃO altera o compilador congelado. NÃO altera o portão.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "PASS1-STABILITY-PENDENCY.yaml"

RUN = CLAUDE / "pilots/PILOT-001-v2"
MANIFEST = RUN / "COMPILATION_MANIFEST.yaml"
TMAP_V2 = RUN / "temporal-map.yaml"
EVID = RUN / "EVIDENCE.jsonl"

TMAP_HIST = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
             / "analysis/temporal-map.yaml")
ADR = CLAUDE / "pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
FREEZE = CLAUDE / "compiler-v2/FREEZE-RECORD.yaml"
P2_LOCK = DOCS / "HELDOUT-LOCK-PILOT-002.yaml"


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    for p in (MANIFEST, TMAP_V2, TMAP_HIST, ADR, FREEZE):
        if not p.is_file():
            print(f"ÂNCORA AUSENTE: {p}")
            return 2

    man = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in EVID.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    mi = sum(1 for r in rows if r["epistemic_status"] == "MODEL_INFERENCE")

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PASS1-STABILITY-PENDENCY",
        "artifact_status": "PENDENCIA_REGISTRADA",
        "registered_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,

        "nature": {
            "additive_only": True,
            "changes_the_gate": False,
            "changes_the_compiler": False,
            "statement": ("Registro de pendência e de decisão. Não altera o "
                          "compilador congelado, o portão, a métrica nem o "
                          "resultado da rodada."),
        },

        "binds_to": {
            "compilation_manifest": {"path": str(MANIFEST.relative_to(DRIVE)),
                                     "sha256": sha_p(MANIFEST)},
            "temporal_map_da_rodada": {"path": str(TMAP_V2.relative_to(DRIVE)),
                                       "sha256": sha_p(TMAP_V2)},
            "temporal_map_historico": {"path": str(TMAP_HIST.relative_to(DRIVE)),
                                       "sha256": sha_p(TMAP_HIST)},
            "adr": {"path": str(ADR.relative_to(DRIVE)), "sha256": sha_p(ADR)},
            "compiler_v2_freeze": {"path": str(FREEZE.relative_to(DRIVE)),
                                   "sha256": sha_p(FREEZE)},
        },

        # ------------------------------------------------ 1. a pendência
        "pendencia_estabilidade_do_pass1": {
            "exigida_por": "§12 da ADR — PASS 1 stability question",
            "estado": "NAO_FEITA_NESTA_RODADA",
            "por_que": (
                "O PASS 1 não foi re-executado por modelo. Os 9 segmentos vieram "
                "do `temporal-map.yaml` histórico, herdados. O compilador v2 "
                "persistiu e hasheou esse mapa, como a §6.1 exige, mas persistir "
                "um mapa herdado não é medir a segmentação."),
            "consequencia_para_a_leitura": (
                "`segment_count: 9` e `in_comparability_band: true` são "
                "VERDADEIROS POR CONSTRUÇÃO. Não testam nada. Ler a banda 7–11 "
                "como confirmação de estabilidade do PASS 1 seria ler como "
                "medição o que é tautologia."),
            "o_que_a_rodada_de_fato_isolou": (
                "Segurar o PASS 1 fixo é o que permite atribuir a diferença de "
                "resultado ao PASS 2, que é a variável sob teste. A tautologia é "
                "efeito colateral de um desenho correto, não descuido — mas "
                "precisa ficar escrita para ninguém contá-la como evidência."),
            "manifesto_declara": {
                "segment_count": man["pass1"]["segment_count"],
                "in_comparability_band": man["pass1"]["in_comparability_band"],
                "temporal_map_sha256": man["pass1"]["temporal_map_sha256"],
                "persisted_before_pass2": man["pass1"]["persisted_before_pass2"],
            },
        },

        # ------------------------------------------------ 2. o PILOT-002
        "decisao_para_o_pilot002": {
            "mapa": "FIXO, 41 segmentos, o mesmo já apurado",
            "pass1_reexecutado": False,
            "razao": (
                "Mesma razão do PILOT-001: isolar o PASS 2. Se o PASS 1 rodasse "
                "de novo, uma diferença de resultado entre os dois pilotos "
                "poderia vir de segmentação diferente OU de extração diferente, "
                "e a comparação perderia o poder de separar as duas."),
            "consequencia": (
                "A contagem de 41 do PILOT-002 também será herdada, e também não "
                "testará a estabilidade do PASS 1. As duas rodadas ficam "
                "comparáveis entre si justamente por isso."),
            "o_que_isso_NAO_autoriza": (
                "Tratar 9 e 41 como medições deterministas. A §12 da ADR já "
                "registra que são observações de execução única, e esta "
                "pendência confirma que continuam sendo."),
        },

        # ------------------------------------------------ 3. como fechar
        "medicao_separada_que_fecha_a_pendencia": {
            "o_que": ("Re-executar o PASS 1 por modelo sobre o MESMO L0, duas ou "
                      "mais vezes, e comparar a contagem e as fronteiras de "
                      "segmento entre as execuções."),
            "por_que_e_separada": (
                "Ela mede o PASS 1, não o PASS 2. Misturá-la à rodada de "
                "aceitação do PASS 2 confundiria as duas variáveis — que é "
                "exatamente o que o mapa fixo evita."),
            "pre_requisito_que_ainda_nao_existe": (
                "O compilador v2 não tem extractor de PASS 1. Ele consome um "
                "temporal-map; não o produz. Implementá-lo é trabalho novo, não "
                "configuração."),
            "estado": "NAO_AGENDADA",
            "bloqueia_o_pilot002": False,
        },

        # --------------------------------- 4. aposentadoria do aviso
        "aposentadoria_do_aviso_claim_x_literal": {
            "estado": "APOSENTADO",
            "o_que_era": ("Aviso mecânico que sinalizava claim cuja entidade "
                          "nomeada não aparece na quote, com rótulo "
                          "SOURCE_EXPLICIT."),
            "por_que_aposentado": {
                "disparo_na_rodada": f"{man['pass2']['invocations']} chamadas, "
                                     "60 avisos em 149 evidências (40%)",
                "viés_conhecido": ("claims em português, quotes em inglês: a "
                                   "checagem acusa toda tradução — IA↔AI, "
                                   "'agente 1'↔'Agent one', 4.000↔4,000, US$↔$"),
                "tentativa_de_conserto": (
                    "Testadas duas versões mais estreitas. A invariante a idioma "
                    "(só CamelCase de nome de produto, tolerante a espaço) cai "
                    "para 7 de 149 — mas 2 dessas 7 o próprio modelo JÁ rotulou "
                    "MODEL_INFERENCE, e as outras 5 não são correção da fonte: "
                    "são a claim resolvendo o antecedente de um pronome dentro "
                    "do segmento (OpenClaw, HubSpot), que é a propriedade "
                    "desejada de claim autocontida."),
                "conclusao": (
                    "Na sua melhor versão o aviso acrescenta ZERO verdadeiro "
                    "positivo além do que o rótulo do modelo já dá, e o que ele "
                    "acusa a mais é comportamento que queremos. Um verificador "
                    "assim não é ruidoso apenas — é redundante."),
            },
            "sinal_que_permanece": {
                "qual": "o rótulo MODEL_INFERENCE emitido pelo próprio modelo",
                "na_rodada": f"{mi} de {len(rows)}",
                "funciona": True,
                "evidencia": (
                    "Inspeção das 9: a maioria é correção de erro de transcrição "
                    "corretamente rotulada — 'Chad GBT'→ChatGPT, 'a length "
                    "post'→LinkedIn, 'Gum Loop'→Gumloop, 'sits in one "
                    "dock'→documento, e o caso mais forte: a fonte diz 'Agents "
                    "are here to replace your team' (o 'not' caiu na "
                    "transcrição) e a claim afirma o oposto, rotulada "
                    "MODEL_INFERENCE. A regra de fidelidade acrescentada ao "
                    "prompt está mordendo."),
            },
            "remocao_do_codigo": {
                "estado": "NAO_EXECUTADA",
                "por_que": (
                    "Remover o código mudaria o hash do freeze do compiler-v2, e "
                    "a §12 da ADR trava a comparabilidade: os dois pilotos têm "
                    "de rodar sob a MESMA versão congelada. O aviso é puramente "
                    "observacional — não toca aceitação, validação nem saída —, "
                    "então mantê-lo no código não contamina o PILOT-002."),
                "decisao": ("Aposentado no RELATÓRIO: o campo continua no rastro "
                            "e não deve ser lido. A remoção do código fica para "
                            "depois de os dois pilotos rodarem sob o mesmo "
                            "congelamento."),
            },
        },

        "status": "PENDENCIA_REGISTRADA",
        "portao_alterado": False,
        "compilador_alterado": False,
    }

    OUT.write_text(
        "# PENDÊNCIA: estabilidade do PASS 1 não foi medida nesta rodada.\n"
        "# + aposentadoria do aviso claim×literal.\n"
        "# Amarrado por SHA-256 ao manifesto. NÃO altera compilador nem portão.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"manifesto amarrado : {sha_p(MANIFEST)[:16]}…")
    print(f"PASS 1             : herdado, {man['pass1']['segment_count']} segmentos "
          f"— banda verdadeira POR CONSTRUÇÃO")
    print(f"PILOT-002          : mapa fixo de 41, mesma razão")
    print(f"aviso claim×literal: APOSENTADO (código mantido pela trava de "
          f"comparabilidade)")
    print(f"sinal remanescente : MODEL_INFERENCE, {mi}/{len(rows)}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256: {sha_p(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
