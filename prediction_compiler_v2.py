#!/usr/bin/env python3
"""Registra a previsão ANTES da execução, congelada por hash.

Roda daqui (ext4). READ-ONLY. Publica só em `Course-to-Skill-Claude/docs/`.

POR QUE ESTE ARTEFATO EXISTE
----------------------------
Se a previsão só for escrita depois de ver o resultado, ela não é previsão: é
descrição. Este arquivo existe para que a relação prevista não possa ser
ajustada depois. Ele se amarra por SHA-256 à ADR e ao freeze do compilador, e o
seu próprio hash é publicado, de modo que qualquer edição posterior é
detectável.

Todos os números são CALCULADOS dos fatos medidos. Nenhum é digitado.

NÃO liga extractor. NÃO recompila.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "PREDICTION-COMPILER-V2.yaml"

ADR = CLAUDE / "pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
FREEZE = CLAUDE / "compiler-v2/FREEZE-RECORD.yaml"

EXPECTED_ADR = "b8cddc93b74a65d6cbc2ad6859e4e3b8a4a81404137d4f95260f1b92668cf3f8"
EXPECTED_FREEZE_PREFIX = "bb3ac605"

# ------------------------------------------------------------------ fatos
# Medidos, não estimados. Origem de cada um declarada no artefato.
P001 = {"extent_s": 905, "segments": 9, "evidence": 44,
        "source": "temporal-map.yaml + analysis/evidence.jsonl do PILOT-001"}
P002 = {"extent_s": 4384, "segments": 41, "evidence": 44,
        "source": ("extensão do corpus de treino apurada no "
                   "PILOT-002-COVERAGE-REPORT; contagem de segmentos do PASS 1 "
                   "declarada na §1 da ADR; 44 evidências do EVIDENCE.jsonv")}


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def r(x: Fraction, n: int = 2) -> float:
    return round(float(x), n)


def main() -> int:
    for label, p, exp in (("ADR", ADR, EXPECTED_ADR),
                          ("freeze do compiler-v2", FREEZE, EXPECTED_FREEZE_PREFIX)):
        if not p.is_file():
            print(f"ÂNCORA AUSENTE: {label} — {p}")
            return 2
        got = sha_p(p)
        if not got.startswith(exp):
            print(f"ÂNCORA DIVERGENTE: {label}\n  esperado {exp}…\n  obtido   {got}")
            return 2

    # ---- aritmética exata, para o arredondamento não virar discussão
    seg001 = Fraction(P001["extent_s"], P001["segments"])
    seg002 = Fraction(P002["extent_s"], P002["segments"])
    y001 = Fraction(P001["evidence"], P001["segments"])
    y002 = Fraction(P002["evidence"], P002["segments"])
    yield_ratio = y001 / y002
    seg_ratio = seg002 / seg001
    total_factor = Fraction(P002["segments"], P001["segments"])

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PREDICTION-COMPILER-V2",
        "artifact_status": "REGISTRADA_ANTES_DA_EXECUCAO",
        "registered_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "purpose": (
            "Registrar a relação prevista ANTES de ligar o extractor, para que "
            "ela não possa ser ajustada depois de ver o resultado. Previsão "
            "escrita depois do resultado não é previsão, é descrição."),

        "binds_to": {
            "adr": {"path": str(ADR.relative_to(DRIVE)), "sha256": sha_p(ADR)},
            "compiler_v2_freeze": {"path": str(FREEZE.relative_to(DRIVE)),
                                   "sha256": sha_p(FREEZE)},
        },

        # ------------------------------------------------------------ fato
        "fato_medido": {
            "segmento_medio_pilot001_s": {
                "expressao": f"{P001['extent_s']} / {P001['segments']}",
                "valor": r(seg001),
                "fonte": P001["source"]},
            "segmento_medio_pilot002_s": {
                "expressao": f"{P002['extent_s']} / {P002['segments']}",
                "valor": r(seg002),
                "fonte": P002["source"]},
            "razao_entre_duracoes_medias": r(seg_ratio, 3),
            "diferenca_percentual": r(Fraction(100) * (seg_ratio - 1), 1),
            "observacao": (
                "Os segmentos têm praticamente a mesma duração média nos dois "
                "pilotos. Logo a queda de yield NÃO se explica por segmento "
                "maior: o PASS 1 entregou ao PASS 2 unidades de trabalho de "
                "tamanho equivalente nos dois casos, e mesmo assim o yield por "
                "unidade caiu."),
        },

        # ----------------------------------------------------------- yield
        "yield_atual": {
            "pilot001_por_segmento": r(y001),
            "pilot002_por_segmento": r(y002),
            "razao": r(yield_ratio, 1),
            "razao_exata": f"{yield_ratio.numerator}/{yield_ratio.denominator}",
            "leitura": (
                "Com unidades de trabalho de tamanho equivalente, o PILOT-002 "
                "rendeu por segmento cerca de um quarto do PILOT-001. É o "
                "sintoma do orçamento de saída global."),
        },

        # -------------------------------------------------------- previsão
        "previsao": {
            "se_decisao_A_funcionar": (
                "O yield por segmento dos dois pilotos converge para "
                "aproximadamente o mesmo valor, porque cada segmento passa a "
                "ser exaurido por conta própria em vez de competir por um "
                "total global."),
            "criterio_de_relacao": (
                "Razão entre os yields por segmento próxima de 1,0 — a "
                "grandeza prevista é a RELAÇÃO entre os pilotos, não o valor "
                "absoluto de nenhum dos dois."),
            "razao_atual_para_comparar": r(yield_ratio, 1),
            "total_pilot002_esperado": {
                "expressao": (f"{P002['segments']} / {P001['segments']} × "
                              "total do PILOT-001 corrigido"),
                "fator": r(total_factor, 1),
                "nota": ("Segue da convergência de yield: se o yield por "
                         "segmento igualar, os totais ficam na razão das "
                         "contagens de segmento. NÃO é alvo de contagem — é a "
                         "consequência aritmética da previsão."),
            },
            "direcao_do_teste": (
                "A previsão FALHA se o yield do PILOT-002 corrigido continuar "
                "muito abaixo do PILOT-001 corrigido, ou seja, se a razão "
                "permanecer longe de 1,0. Nesse caso a Decisão A não explica o "
                "colapso e a §12 da ADR manda reabrir o diagnóstico."),
        },

        # ---------------------------------------------- banda ainda em aberto
        "banda_de_aceitacao": {
            "status": "NAO_RATIFICADA",
            "problema": (
                "'Próxima de 1,0' não é falsificável sem um número. Sem banda "
                "ratificada antes da execução, qualquer resultado pode ser "
                "narrado como próximo o bastante — que é exatamente o vício "
                "que este artefato existe para impedir."),
            "proposta_para_ratificacao": {
                "razao_entre_yields": "0,75 a 1,33",
                "justificativa": (
                    "Banda simétrica em escala logarítmica (fator 4/3 para "
                    "cada lado). A razão de hoje é "
                    f"{r(yield_ratio, 1)}, muito fora dela, então a banda "
                    "distingue convergência real de melhora parcial."),
            },
            "regra": (
                "Se esta banda não for ratificada ANTES da execução, o "
                "critério permanece qualitativo e o resultado NÃO pode ser "
                "declarado aprovado por proximidade. Ratificar depois de ver o "
                "resultado é proibido."),
        },

        # ------------------------------------------------------- limites
        "nao_estabelece": [
            "qual é o valor absoluto correto de yield por segmento",
            "que 200 evidências seja o número certo para o PILOT-002",
            "que a contagem de segmentos do PASS 1 se repita entre execuções",
            "que a cobertura de L0 vá superar o piso de 73,5%",
        ],
        "relacao_com_o_portao": (
            "Esta previsão é sobre MECANISMO (yield por segmento). O critério "
            "que DECIDE a aceitação continua sendo a cobertura de L0 > 73,5%, "
            "congelada em thresholds.py. Os dois são independentes: a previsão "
            "pode acertar e o portão reprovar, e vice-versa. Cada um é "
            "reportado por si."),

        "status": "REGISTRADA_ANTES_DA_EXECUCAO",
        "execucao_realizada": False,
        "extractor_ligado_a_modelo": False,
    }

    blob = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    header = ("# PREDICTION-COMPILER-V2 — registrada ANTES da execução.\n"
              "# Nenhum número foi digitado: todos calculados dos fatos medidos.\n"
              "# Editar este arquivo muda o seu SHA-256 e quebra a amarração.\n")
    OUT.write_text(header + blob, encoding="utf-8")

    print(f"segmento médio: P001 {r(seg001)}s | P002 {r(seg002)}s "
          f"(razão {r(seg_ratio,3)})")
    print(f"yield/segmento: P001 {r(y001)} | P002 {r(y002)} | razão {r(yield_ratio,1)}")
    print(f"fator de total previsto para o P002: {r(total_factor,1)}×")
    print(f"amarrada a ADR {sha_p(ADR)[:16]}… e freeze {sha_p(FREEZE)[:16]}…")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256 do próprio artefato: {sha_p(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
