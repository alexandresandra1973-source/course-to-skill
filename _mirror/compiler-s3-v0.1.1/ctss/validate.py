"""Validação dura. Toda rejeição tem código; nada passa por omissão."""
from __future__ import annotations
from .schema import (RULE_FIELDS, STEP_FIELDS, PRESERVED, UNDEFINED,
                     ORIGIN_CLASSES, DISPOSITIONS, GAP_IF_ONLY)

CODES = {
    "RULE_WITHOUT_EVIDENCE",        # regra sem evidence_id
    "EVIDENCE_ID_UNKNOWN",          # cita evidence_id inexistente
    "FIELD_NOT_UNDEFINED",          # campo sem evidência que não saiu UNDEFINED
    "MISSING_REQUIRED_FIELD",
    "UNKNOWN_ORIGIN_CLASS",
    "EVIDENCE_WITHOUT_DISPOSITION", # evidência não contabilizada
    "UNKNOWN_DISPOSITION",
    "SKILL_MD_CONTAINS_RULE",       # roteador com metodologia executável
    "GAP_NOT_REPORTED",             # lacuna ausente do gap report
}


def _err(code, **d):
    return {"code": code, **d}


def validate_entity(ent: dict, kind: str, known_ids: set[str]) -> list[dict]:
    fields = RULE_FIELDS if kind == "rule" else STEP_FIELDS
    errs = []
    for f in fields:
        if f not in ent:
            errs.append(_err("MISSING_REQUIRED_FIELD", entity=ent.get("rule_id") or
                             ent.get("step_id"), field=f))
    eids = ent.get("evidence_ids") or []
    if not eids:
        errs.append(_err("RULE_WITHOUT_EVIDENCE", entity=ent.get("rule_id") or
                         ent.get("step_id"), kind=kind))
    for e in eids:
        if e not in known_ids:
            errs.append(_err("EVIDENCE_ID_UNKNOWN", entity=ent.get("rule_id") or
                             ent.get("step_id"), evidence_id=e))
    if ent.get("origin_class") not in ORIGIN_CLASSES:
        errs.append(_err("UNKNOWN_ORIGIN_CLASS", entity=ent.get("rule_id") or
                         ent.get("step_id"), observed=ent.get("origin_class")))
    # os quatro preservados: valor OU UNDEFINED, nunca ausente nem vazio
    for f in PRESERVED:
        if f not in fields:
            continue
        v = ent.get(f, None)
        if v is None or (isinstance(v, str) and not v.strip()):
            errs.append(_err("FIELD_NOT_UNDEFINED", entity=ent.get("rule_id") or
                             ent.get("step_id"), field=f,
                             detail="campo sem evidência tem de sair literalmente UNDEFINED"))
    return errs


def validate_accounting(evidence_ids: set[str], dispositions: dict) -> list[dict]:
    """Contabilidade exaustiva: nenhuma evidência sai sem disposição."""
    errs = []
    for e in sorted(evidence_ids - set(dispositions)):
        errs.append(_err("EVIDENCE_WITHOUT_DISPOSITION", evidence_id=e))
    for e, d in dispositions.items():
        if d not in DISPOSITIONS:
            errs.append(_err("UNKNOWN_DISPOSITION", evidence_id=e, observed=d))
    return errs


# --- roteador: um SKILL.md não pode conter metodologia executável
#
# A primeira versão varria marcadores ("if", "quando", "se") no texto inteiro e
# acusava a PRÓPRIA redação canônica — "hard runtime stops WHEN emitted by the
# routed policy" é rota, não regra. Heurística de marcador não distingue prosa
# de instrução.
#
# A checagem passou a ser EXATA: o roteador é gerado por ,
# logo tem de ser reconstruível a partir do template mais as substituições
# declaradas. Qualquer texto inserido quebra a igualdade. Não há falso positivo
# possível, e nenhuma regra colada sobrevive.
RULE_MARKERS = ["if ", "se ", "quando ", "when ", "então", "then ",
                "passo 1", "step 1", "primeiro,", "first,"]


def validate_router(md: str, expected: str | None = None,
                    dispatch_lines: list[str] | None = None) -> list[dict]:
    errs = []
    if expected is not None:
        if md != expected:
            errs.append(_err("SKILL_MD_CONTAINS_RULE",
                             detail="roteador não é reconstruível a partir do template "
                                    "mais as substituições declaradas",
                             expected_sha256=__import__("hashlib").sha256(
                                 expected.encode()).hexdigest()[:16],
                             observed_sha256=__import__("hashlib").sha256(
                                 md.encode()).hexdigest()[:16]))
        return errs
    # sem template de referência: varre SÓ o bloco gerado (DISPATCH), onde
    # conteúdo variável entra. O resto é literal congelado.
    for line in (dispatch_lines or []):
        t = line.strip().lower()
        if "knowledge/" in t:
            continue
        for m in RULE_MARKERS:
            if m in t:
                errs.append(_err("SKILL_MD_CONTAINS_RULE", marker=m.strip(),
                                 text=line.strip()[:110]))
                break
    return errs


def validate_gap_report(md: str, expected: list[dict]) -> list[dict]:
    """Toda lacuna medida tem de ter linha no relatório."""
    errs = []
    for g in expected:
        key = g["gap_id"]
        if key not in md:
            errs.append(_err("GAP_NOT_REPORTED", gap_id=key, kind=g.get("kind")))
    return errs


def rule_is_course_gap(ent: dict, origin_by_evidence: dict) -> bool:
    """Regra apoiada SÓ em inferência genuína: o modelo preencheu, o curso não ensinou."""
    cls = {origin_by_evidence.get(e) for e in (ent.get("evidence_ids") or [])}
    return bool(cls) and cls == {GAP_IF_ONLY}
