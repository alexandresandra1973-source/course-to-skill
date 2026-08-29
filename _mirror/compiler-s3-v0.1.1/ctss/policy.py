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
    # v0.1.1 — a citacao deixa de ser habito e vira regra declarada.
    p["response_rules"] = [CITATION_RULE]
    return p




# ============================================================================
# v0.1.1 — CONSERTO DO P-8 E DA CITAÇÃO DECLARADA. Acrescentado em 2026-08-15.
#
# P-8: os guards RG-013-002 e RG-013-003, herdados da politica canonica do
# PILOT-001, mandam PERGUNTAR usando `knowledge/questions.yaml` e apontam para
# `Q-0001` e `ADR-0004` — e o compiler-s3 nunca emitia esse arquivo. O runtime
# saia com dois guards prescrevendo uma pergunta que o pacote nao continha.
# Afetava o PILOT-004 e tambem o PILOT-003-v2.
#
# CITACAO: o canario de 15/08 mostrou que o runtime executa passo e regra sem
# citar o evidence_id de origem. Nada na politica exigia isso — era habito de
# um modelo, nao regra declarada. Agora e regra.
#
# NADA AQUI E INVENTADO. O enunciado de Q-0001 e LITERAL, recuperado do
# bundle-fonte do P001 dentro do zip do TEST-0007, em
# agent-input/runtime-bundle/knowledge/questions.yaml.
# ============================================================================

# Enunciado LITERAL de Q-0001, recuperado do bundle-fonte. Só os campos que o
# guard RG-013-002 precisa para perguntar.
Q0001_LITERAL = {
    "question_id": "Q-0001",
    "input_name": "Outcome/função",
    "question": "Qual resultado ou função você quer que o agente assuma?",
    "ask_when": "O outcome ainda não estiver definido.",
    "on_missing": "ASK_USER",
    "safe_default": None,
    "stop_after_asking": True,
    "status": "ACTIVE",
    "origin_class": "MODEL_INFERENCE",
}

# Contrato de construção que o RG-013-003 verifica, na ordem em que pergunta.
CONTRATO_BUILD = ["outcome", "input", "output", "boundaries"]

CITATION_RULE = {
    "rule_id": "RT-CITE-001",
    "name": "Citar id e evidência ao aplicar metodologia",
    "trigger": "Ao aplicar qualquer passo (S-xxxx) ou regra (R-xxxx) na resposta.",
    "condition": "A resposta usa metodologia vinda de decision-rules.yaml ou workflows.yaml.",
    "action": ("Citar na resposta o id aplicado (S-xxxx / R-xxxx) E o evidence_id de "
               "origem registrado nesse passo ou regra. Sem o par id+evidence_id, a "
               "afirmação não é rastreável até a fonte e não deve ser apresentada como "
               "metodologia do curso."),
    "stop": False,
    "status": "ACTIVE",
    "origin_class": "MODEL_INFERENCE",
    "justificativa": ("DECISAO_DE_INSTRUMENTO. A fonte não enuncia como o runtime deve "
                      "formatar a resposta. A rastreabilidade é requisito do produto, "
                      "comprovado no BLOCO 4 do PILOT-004, e passa a ser DECLARADA em "
                      "vez de esperada."),
}


def build_questions(skill_id: str, skill_version: str, pilot_id: str) -> dict:
    """Emite o `knowledge/questions.yaml` que os guards ja exigiam.

    PROVENIENCIA HONESTA: o enunciado vem do bundle do PILOT-001. Os
    `source_evidence_ids` de la NAO sao evidencia deste piloto e por isso NAO
    sao copiados — entram como origem declarada, nunca como se fossem daqui.
    """
    q = dict(Q0001_LITERAL)
    q["proveniencia"] = {
        "recuperado_de": ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip :: "
                          "agent-input/runtime-bundle/knowledge/questions.yaml"),
        "enunciado": "LITERAL, nao reescrito",
        "evidence_ids_do_P001": ["EV-0005", "EV-0029"],
        "nota": ("os evidence_id acima sao do PILOT-001 e NAO valem como evidencia "
                 "deste piloto; ficam registrados como origem do enunciado"),
    }
    return {
        "schema_version": "0.1.1",
        "skill_id": skill_id, "skill_version": skill_version, "pilot_id": pilot_id,
        "status": "ACTIVE",
        "runtime_note": ("Perguntas que os guards da runtime-policy podem exigir. "
                         "RG-013-002 exige Q-0001; RG-013-003 pergunta pelo primeiro "
                         "campo faltante do contrato de construcao."),
        "contrato_de_construcao": CONTRATO_BUILD,
        "questions": [q],
    }


def resolve_dangling_refs(policy: dict, known_rule_ids: set) -> dict:
    """P-8: referencia que nao resolve no proprio pacote vira referencia
    DECLARADA, nunca silenciosa.

    `ADR-0004` existe no bundle-fonte do P001 (decision_id ADR-0004), mas NAO
    existe nas regras deste piloto — os ids daqui sao R-xxxx. Importar a regra
    do P001 contaminaria a Skill com metodologia de outro curso. Entao a
    referencia fica, com a origem escrita ao lado.
    """
    import copy
    p = copy.deepcopy(policy)
    pend = []
    for g in p.get("guards", []):
        rid = g.get("decision_rule_id")
        if rid and rid not in known_rule_ids:
            g["decision_rule_id_resolucao"] = {
                "resolve_neste_pacote": False,
                "existe_no_bundle_fonte_P001": True,
                "onde": ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip :: "
                         "agent-input/runtime-bundle/knowledge/decision-rules.yaml"),
                "decisao": ("NAO importado. Trazer uma regra do PILOT-001 para dentro "
                            "deste piloto misturaria metodologia de outro curso. A "
                            "referencia permanece como origem do guard, que e "
                            "instrumento (MODEL_INFERENCE), nao conteudo da fonte."),
            }
            pend.append({"guard_id": g["guard_id"], "ref": rid})
    p["referencias_externas_declaradas"] = pend
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
