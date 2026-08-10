"""Adaptador do material real do PILOT-001 para o contrato da arquitetura nova.

O piloto v0.1.1 não tem os campos `span`/`quote`/`claim` da ADR-0002. Ele tem
`source_refs[].timestamp` (endereço), `source_excerpt` (citação) e `observation`
(afirmação). O adaptador faz essa ponte — sem inventar dado: onde o piloto não
tem valor, o adaptador devolve None e o portão trata como ausência medida.

Nada aqui é mock. Todos os caminhos apontam para arquivos reais, verificados
contra BASELINE_MANIFEST_20260810.txt.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
PILOT = DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
RELEASE = (DRIVE / "Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1"
           / "course-to-skill-compiler-v0.1.1-pilot-ready"
           / "course-to-skill-compiler-v0.1.1-pilot-ready")
KIT = (DRIVE / "Course-to-Skill-Compiler/02_PILOTS/PILOT-001/02_VALIDATION"
       / "PILOT-001-final-blind-test-kit/PILOT-001-final-blind-test-kit")

L0_TRANSCRIPT = PILOT / "sources/transcript/transcript-original-en.txt"
L0_FRAMES = sorted((PILOT / "sources/frames").glob("*.png"))
L0_METADATA = PILOT / "sources/metadata/source-metadata.yaml"

EVIDENCE = PILOT / "analysis/evidence.jsonl"
DECISIONS_POST_AUDIT = PILOT / "analysis/decisions-revised.yaml"
WORKFLOWS_POST_AUDIT = PILOT / "analysis/workflows-revised-v3.yaml"
BUNDLE = PILOT / "PILOT-001-generated-skill-v0.1.1-corrected/generated-skill"
HELDOUT_REGISTRY = KIT / "judge-private/held-out-registry.yaml"
TEST_SUITE = KIT / "judge-private/test-suite.yaml"

EV_RE = re.compile(r"EV-\d{4,}")


def docs(path: Path) -> list:
    return [d for d in yaml.safe_load_all(path.read_text(encoding="utf-8")) if d]


def load_evidence() -> list[dict]:
    return [json.loads(l) for l in EVIDENCE.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def evidence_spans(rec: dict, transcript_sha: str) -> list[str]:
    """Traduz source_refs[].timestamp para a gramática de span da ADR-0001."""
    out = []
    for r in rec.get("source_refs", []):
        ts = r.get("timestamp") or {}
        if ts.get("start") and ts.get("end"):
            out.append(f"L0:{transcript_sha[:12]}:t={ts['start']}-{ts['end']}")
    return out


def enum_size(schema_path: Path, dotted: str) -> int:
    """Tamanho do domínio de um campo, lido do schema REAL do release."""
    node = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    for part in dotted.split("."):
        node = node[part]
    return len(node)


def schema_domains() -> dict[str, int]:
    ev = RELEASE / "schemas/evidence.schema.yaml"
    de = RELEASE / "schemas/decision.schema.yaml"
    return {
        "evidence.origin_class":      enum_size(ev, "properties.origin_class.enum"),
        "evidence.status":            enum_size(ev, "properties.status.enum"),
        "evidence.evidence_strength": enum_size(ev, "properties.evidence_strength.enum"),
        "evidence.confidence.level":  enum_size(ev, "$defs.confidence.properties.level.enum"),
        "evidence.category":          enum_size(ev, "properties.category.enum"),
        "decision.origin_class":      enum_size(de, "properties.origin_class.enum"),
        "decision.rationale.state":   enum_size(de, "$defs.rationale.properties.state.enum"),
        "decision.promotion_level":   enum_size(de, "properties.promotion_level.enum"),
        "decision.autonomy.level":    enum_size(de, "$defs.autonomy.properties.level.enum"),
        "decision.status":            enum_size(de, "properties.status.enum"),
    }


def normalize_claim(s: str) -> str:
    """Normalização estrita para comparação de conjuntos (ADR-0007).

    Estrita de propósito: começa apertada e só afrouxa com caso documentado.
    """
    s = (s or "").lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s]", "", s, flags=re.UNICODE)
    return s.strip()


def claim_texts(obj) -> list[str]:
    """Extrai afirmações textuais operacionais de uma estrutura YAML/JSON."""
    keys = {"name", "problem", "context", "selected", "action", "statement",
            "expression", "consequence", "purpose", "behavior", "condition",
            "question", "criterion", "description", "effect", "rule",
            "output_expectation", "trigger"}
    out: list[str] = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in keys and isinstance(v, str) and v.strip():
                    out.append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            pass
    walk(obj)
    return out


def bundle_claims() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in sorted(BUNDLE.rglob("*.yaml")):
        rel = str(p.relative_to(BUNDLE))
        # manifest.yaml e audit.yaml sao METADADO por contrato, nao camada de
        # conhecimento: nome da skill, contagens, status. Excluir e' estreitar
        # ESCOPO (o que e' claim), nao afrouxar LIMIAR. tests/ nao viaja no bundle.
        if rel.startswith("tests/") or rel in ("manifest.yaml", "audit.yaml"):
            continue
        out[rel] = claim_texts(docs(p))   # multi-doc: o piloto usa os dois formatos
    return out


def audited_claims() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in [DECISIONS_POST_AUDIT, WORKFLOWS_POST_AUDIT,
              PILOT / "analysis/principles-revised.yaml",
              PILOT / "analysis/anti-patterns.yaml",
              PILOT / "analysis/questions-revised.yaml",
              PILOT / "analysis/quality-criteria.yaml",
              PILOT / "analysis/tools-revised-v2.yaml"]:
        out[p.name] = claim_texts(docs(p))
    return out


def blind_cases(transcript_sha: str) -> list[dict]:
    """Casos da suíte travada que se declaram cegos/held-out, com seus spans."""
    ev = {e["evidence_id"]: e for e in load_evidence()}
    cases = []
    for t in docs(TEST_SUITE):
        declared = t.get("test_type")
        iso = t.get("isolation") or {}
        claims_blind = declared in ("BLIND_EVALUATION",) or iso.get("source_hidden") is True
        if not claims_blind:
            continue
        spans: list[str] = []
        for eid in (t.get("linked_evidence_ids") or []):
            if eid in ev:
                spans.extend(evidence_spans(ev[eid], transcript_sha))
        cases.append({"case_id": t["test_id"], "declared_type": declared,
                      "support_spans": spans,
                      "linked_evidence_ids": t.get("linked_evidence_ids") or [],
                      "hidden_items": iso.get("hidden_items") or []})
    return cases
