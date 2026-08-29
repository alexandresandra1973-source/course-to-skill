"""Esquema SUBCONJUNTO para regras e passos. Decisão do Alexandre.

Quatro campos preservados POR NOME porque o Skeptic os pegou inventados no
PILOT-001: o UNDEFINED deles é sinal conhecido e significativo.
"""
from __future__ import annotations

UNDEFINED = "UNDEFINED"

# --- preservados por nome, por decisão registrada
PRESERVED = ["autonomy", "precedence", "missing_input_action", "iteration_limit"]

RULE_FIELDS = [
    "rule_id", "name", "trigger", "condition", "action",
    "autonomy", "precedence", "missing_input_action", "iteration_limit",
    "do_not", "evidence_ids", "origin_class", "segment_ids",
]
STEP_FIELDS = [
    "step_id", "workflow_id", "name", "action", "required_inputs",
    "missing_input_action", "iteration_limit", "autonomy",
    "evidence_ids", "origin_class", "segment_ids", "order_key",
]
WORKFLOW_FIELDS = ["workflow_id", "name", "anchor_evidence_id", "steps", "evidence_ids"]

# --- descartados do esquema legado do PILOT-001, para a escolha ser auditável
DISCARDED_FROM_LEGACY = {
    "course": "metadado do curso; vive no manifest, não em cada regra",
    "lesson": "idem",
    "problem": "prosa; não é executável",
    "context": "prosa; não é executável",
    "inputs_observed": "observação, não instrução de runtime",
    "alternatives": "histórico da decisão, não executável",
    "selected": "redundante com `action`",
    "decision_variables": "análise, não runtime",
    "rationale": "prosa; vai ao evidence-map",
    "validation_criteria": "pertence a quality-criteria.yaml, fora do escopo mínimo",
    "test_candidates": "pertence à suíte, não ao runtime",
    "tags": "sem consumidor no runtime",
    "confidence": "faixa numérica sem definição estável (ver PROJECT_INVENTORY §40)",
    "promotion_level": "governança de compilação, vai ao manifest",
    "status": "idem", "created_at": "idem", "updated_at": "idem",
    "reviewer_note": "idem", "superseded_by": "idem",
    "supporting_decision_ids": "idem", "conflicting_decision_ids": "idem",
    "contradiction_state": "idem", "contradiction_note": "idem",
    "exceptions": "coberto por `condition` + `precedence`",
    "output_expectation": "coberto por `action`",
    "runtime_enforcement": "coberto por `autonomy` + `missing_input_action`",
    "required_inputs": "mantido só no passo, onde tem consumidor",
    "ask_user_if_missing": "renomeado para `missing_input_action`",
    "source_evidence": "renomeado para `evidence_ids`",
    "schema_version": "vive no cabeçalho do arquivo, não em cada regra",
}

ORIGIN_CLASSES = {
    "SOURCE_EXPLICIT",           # a fonte diz
    "TRANSCRIPTION_CORRECTION",  # a fonte ensinou, o ASR estragou → conta como curso
    "PARAPHRASE",                # o modelo reescreveu sem acrescentar → conta como curso
    "GENUINE_INFERENCE",         # o modelo preencheu → NÃO é conteúdo do curso
}
COURSE_CONTENT = {"SOURCE_EXPLICIT", "TRANSCRIPTION_CORRECTION", "PARAPHRASE"}
# Regra que se apoia SÓ em GENUINE_INFERENCE é LACUNA DO CURSO, mesmo funcionando.
GAP_IF_ONLY = "GENUINE_INFERENCE"

DISPOSITIONS = {"CONSUMED_BY_RULE", "CONSUMED_BY_STEP", "NON_METHODOLOGICAL", "GAP"}
