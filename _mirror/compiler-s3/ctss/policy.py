"""runtime-policy DERIVADA da canônica cab31454…, com o template intocado.

Decisão registrada: RG-013-001 (scope gate) é PARAMETRIZADO — copiado como está,
a Skill do PILOT-002 recusaria toda pergunta sobre Claude Code por "fora de
escopo". RG-013-004 e o seu response_template ficam BYTE-IDÊNTICOS.

A condição de escopo é o ÚNICO texto escrito à mão num sistema que exige citação
em tudo. Por isso ela não fica em silêncio: ou cita evidência, ou se declara
DECISAO_DE_INSTRUMENTO. O campo é obrigatório.
"""
from __future__ import annotations
import hashlib, zipfile
from pathlib import Path
import yaml

CANONICAL_POLICY_SHA = "cab31454c9a7ea328298e964ddb4187e4ba072ca65c4f515de4d9eb09f5002eb"
CANONICAL_TEMPLATE_SHA = "50848d02ac32c22aac843cc20d72c9f335f89027fcfa4911a50d7e8719ead814"
PARAMETERIZED = ["skill_id", "skill_version", "guards[RG-013-001].condition"]
IMMUTABLE = ["guards[RG-013-004].response_template",
             "guards[RG-013-004].template_substitution",
             "guards[RG-013-004].required_resources", "precedence"]


def load_canonical(zip_path: Path, member: str) -> tuple[dict, str]:
    raw = zipfile.ZipFile(zip_path).read(member)
    got = hashlib.sha256(raw).hexdigest()
    if got != CANONICAL_POLICY_SHA:
        raise ValueError(f"runtime-policy canônica não confere: {got}")
    return yaml.safe_load(raw), got


def derive(canonical: dict, *, skill_id: str, skill_version: str,
           scope_condition: str, scope_justification: dict) -> dict:
    """Deriva a policy. Falha fechado se a justificativa do escopo faltar."""
    if not scope_condition or not scope_condition.strip():
        raise ValueError("scope_condition é obrigatório")
    kind = scope_justification.get("kind")
    if kind not in {"EVIDENCE_CITED", "DECISAO_DE_INSTRUMENTO"}:
        raise ValueError("scope_justification.kind tem de ser EVIDENCE_CITED ou "
                         "DECISAO_DE_INSTRUMENTO — silêncio não serve")
    if kind == "EVIDENCE_CITED" and not scope_justification.get("evidence_ids"):
        raise ValueError("EVIDENCE_CITED exige evidence_ids")
    if kind == "DECISAO_DE_INSTRUMENTO" and not scope_justification.get("rationale"):
        raise ValueError("DECISAO_DE_INSTRUMENTO exige rationale escrito")

    import copy
    p = copy.deepcopy(canonical)
    p["skill_id"] = skill_id
    p["skill_version"] = skill_version
    p["derived_from"] = {"canonical_runtime_policy_sha256": CANONICAL_POLICY_SHA,
                         "parameterized_fields": PARAMETERIZED,
                         "immutable_fields": IMMUTABLE}
    for g in p["guards"]:
        if g["guard_id"] == "RG-013-001":
            g["condition"] = scope_condition
            g["scope_justification"] = scope_justification
    return p


def verify_template_byte_identical(policy: dict) -> tuple[bool, str]:
    """O template fail-closed tem de bater byte a byte com 50848d02…."""
    for g in policy.get("guards", []):
        if g["guard_id"] == "RG-013-004":
            got = hashlib.sha256(g["response_template"].encode("utf-8")).hexdigest()
            return got == CANONICAL_TEMPLATE_SHA, got
    return False, ""


def fail_closed_message(policy: dict, missing: list[str]) -> str:
    """A recusa, montada pela própria política — sem texto inventado aqui."""
    g = next(x for x in policy["guards"] if x["guard_id"] == "RG-013-004")
    sub = g["template_substitution"]
    return g["response_template"].replace(
        "{" + sub["variable"] + "}", sub["join_with"].join(missing))
