"""Limiares CONGELADOS, pré-declarados antes de qualquer execução corrigida.

Todos os valores deste módulo vêm da ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE
(sha256 b8cddc93b74a65d6cbc2ad6859e4e3b8a4a81404137d4f95260f1b92668cf3f8) e
foram fixados ANTES de rodar qualquer compilação corrigida.

REGRA: nenhum valor daqui pode ser levantado, baixado, reinterpretado ou
substituído depois de observar o resultado de PILOT-001 ou PILOT-002. Quem
precisar mudar um limiar muda a ADR primeiro, e o `ADR_SHA256` abaixo deixa de
casar — o que é justamente o alarme.

O que NÃO existe aqui, por proibição explícita da §10 da ADR:
  - alvo de contagem total de evidências (nem 44, nem 200);
  - mínimo de evidências por segmento;
  - cota de densidade;
  - geração proporcional ao tempo decorrido.
Os ~200 são DIAGNÓSTICO. Nunca cota.
"""
from __future__ import annotations

from dataclasses import dataclass

ADR_ID = "ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE"
ADR_SHA256 = "b8cddc93b74a65d6cbc2ad6859e4e3b8a4a81404137d4f95260f1b92668cf3f8"

# ---------------------------------------------------------------- decisório
# §7 e §12: piso histórico, comparação ESTRITAMENTE maior. Igualar 73,5% não
# demonstra melhora sobre a linha de base antiga.
COVERAGE_FLOOR = 0.735
COVERAGE_COMPARISON = "strictly_greater"

# §12: banda de comparabilidade do PASS 1 do PILOT-001, inclusiva nas pontas.
PASS1_BAND_INCLUSIVE = (7, 11)
PASS1_VARIANCE_FLAG = "PASS1_SEGMENTATION_VARIANCE_REVIEW_REQUIRED"

# ---------------------------------------------------------- referências históricas
# §13: valores do PILOT-001 antigo. São REFERÊNCIA de mecanismo, não critério
# de aceitação — o critério decisório é só a cobertura.
HISTORICAL = {
    "pilot": "PILOT-001",
    "compiler_state": "old_global_pass2",
    "segments": 9,
    "evidence": 44,
    "coverage": 0.735,
    "yield_per_segment": 4.89,
}

# ------------------------------------------------------------- parada do portão
# §5 Decisão B manda repetir "até o limiar ser satisfeito OU uma condição de
# parada definida ser atingida". A ADR não fixa a condição; ela é declarada
# AQUI, antes de qualquer execução, e é parte do congelamento.
MAX_RESCAN_ITERATIONS = 3
# Uma iteração que não acrescenta NENHUMA evidência nova encerra o laço: se a
# revarredura dirigida não encontrou mais nada nos blocos descobertos, repetir
# não vai encontrar. Isto impede laço infinito sem inventar cota.
STOP_ON_ZERO_PROGRESS = True

# ------------------------------------------------------------ métrica congelada
# §11 dos custos: "Coverage measurement must be formally specified and frozen".
# A definição é esta e não muda entre pilotos:
COVERAGE_METRIC = {
    "name": "L0_UNION_SPAN_COVERAGE",
    "numerator": ("união dos intervalos de tempo citados pelas evidências, "
                  "mesclada por `cts.coverage.merge`"),
    "denominator": ("extensão do corpus de treino: duração nominal da fonte "
                    "menos as janelas de held-out declaradas em lock"),
    "excluded_from_both": "janelas de held-out",
    "module": "cts/coverage.py",
    "functions": ["merge", "complement", "Citation", "Block"],
}

# Módulos cujo conteúdo define a métrica. O hash é conferido em tempo de
# execução: se `cts/coverage.py` mudar, a métrica mudou, e a comparação entre
# pilotos deixa de ser válida (§12, trava de comparabilidade).
PINNED_METRIC_MODULES = ("cts/coverage.py", "cts/spans.py")


@dataclass(frozen=True)
class GatePolicy:
    """Política do portão de saturação. Congelada na construção."""
    coverage_floor: float = COVERAGE_FLOOR
    max_iterations: int = MAX_RESCAN_ITERATIONS
    stop_on_zero_progress: bool = STOP_ON_ZERO_PROGRESS

    def satisfied(self, coverage: float) -> bool:
        """Estritamente maior. `>=` seria reinterpretar o limiar."""
        return coverage > self.coverage_floor


def pass1_in_band(n_segments: int) -> bool:
    lo, hi = PASS1_BAND_INCLUSIVE
    return lo <= n_segments <= hi


FROZEN = {
    "adr_id": ADR_ID,
    "adr_sha256": ADR_SHA256,
    "coverage_floor": COVERAGE_FLOOR,
    "coverage_comparison": COVERAGE_COMPARISON,
    "pass1_band_inclusive": list(PASS1_BAND_INCLUSIVE),
    "max_rescan_iterations": MAX_RESCAN_ITERATIONS,
    "stop_on_zero_progress": STOP_ON_ZERO_PROGRESS,
    "coverage_metric": COVERAGE_METRIC,
    "historical_reference": HISTORICAL,
    "forbidden": [
        "alvo de contagem total de evidências",
        "mínimo de evidências por segmento",
        "cota de densidade",
        "geração proporcional ao tempo",
    ],
}
