#!/usr/bin/env python3
"""TEST-0008 pré-lock — baseline com paridade de informação, ancorado em L0.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/: só lê o transcript e os
pacotes de braço. Publica tudo em Course-to-Skill-Claude/docs/.

REGRA DURA: nenhum elemento entra no baseline sem um span de L0 cuja citação
seja verificada contra o transcript. O que não verifica sai do resumo e é
listado como REJEITADO_SEM_ANCORA. A verificação é do script, não do autor.

NÃO congela nada. A régua sai como DRAFT_NOT_FROZEN.
"""
from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
L0 = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources"
      / "transcript/transcript-original-en.txt")
META = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent/sources"
        / "metadata/source-metadata.yaml")
OUT_SUMMARY = DOCS / "BASELINE-SUMMARY-v0.1.4.md"
OUT_PROV = DOCS / "BASELINE-PROVENANCE-v0.1.4.yaml"
OUT_RUBRIC = DOCS / "TEST-0008-RUBRIC-DRAFT-v0.1.4.yaml"
COND_DIR = DOCS / "TEST-0008-CONDITIONS-v0.1.4"

VIDEO_ID = "YkdAx2XjWDs"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))


# --------------------------------------------------------------------------
# L0
# --------------------------------------------------------------------------

def secs(t: str) -> int:
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def load_l0() -> list[tuple[str, str]]:
    """Segmentos (timestamp, fala) do transcript.

    Os títulos de seção do YouTube vêm colados ao FIM do segmento em que a
    seção começa (`... than you ## What Platform Should You Use?`), o que parte
    frases no meio. Não são fala; são removidos antes de qualquer verificação.
    Conferido: nos 7 casos o `##` está no fim do segmento, nunca no meio da fala.
    """
    raw = L0.read_text(encoding="utf-8")
    parts = re.split(r"\*\*(\d+:\d{2})\*\*", raw)
    segs = []
    for i in range(1, len(parts) - 1, 2):
        txt = re.sub(r"\s+", " ", parts[i + 1]).strip()
        txt = re.sub(r"##.*$", "", txt).strip()
        segs.append((parts[i], txt))
    return segs


def span_text(segs: list[tuple[str, str]], a: str, b: str) -> str:
    lo, hi = secs(a), secs(b)
    return " ".join(t for ts, t in segs if lo <= secs(ts) <= hi)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"')
                  .replace("”", '"')).strip().lower()


# --------------------------------------------------------------------------
# elementos candidatos do baseline — cada um com span e citação a verificar
# --------------------------------------------------------------------------
# (id, seção, span_ini, span_fim, citação verbatim, prosa do resumo)
ELEMENTS = [
    ("E01", "framing", "1:30", "1:55",
     "Stop asking what task can I automate and start asking what system of agents "
     "can I build to handle this entire function",
     "The lesson's central reframe is to stop asking which task can be automated and "
     "to start asking what system of agents can handle an entire function. Starting "
     "from outcomes rather than from a to-do list is what makes the work compound "
     "instead of producing one-off automations."),

    ("E02", "framing", "5:20", "5:35",
     "Use humans for judgment and agents for execution",
     "The operating principle is to use humans for judgment and agents for execution."),

    ("E03", "concepts", "2:20", "3:02",
     "A chatbot answers a question. An automation runs a playbook. And an agent does a job",
     "Three things are distinguished. A chatbot answers a question. An automation runs "
     "a fixed playbook and breaks when something unexpected happens. An agent has a "
     "goal, reasons through multiple steps, uses tools to act, and adapts when "
     "conditions change."),

    ("E04", "anatomy", "4:16", "4:22",
     "Every working agent, simple or complex, has the same five building blocks",
     "Every working agent, simple or complex, is said to have the same five building "
     "blocks, and the whole thing falls apart if any one of them is missing or weak."),

    ("E05", "anatomy", "4:22", "4:32",
     "the underlying language model doing the reasoning",
     "The first block is the brain: the underlying language model doing the reasoning. "
     "The lesson holds that the model matters less than people think."),

    ("E06", "anatomy", "4:32", "4:52",
     "The system prompt is 80% of the quality of what comes out",
     "The second block is the instructions, the system prompt, described as the job "
     "description for the agent: who it is, what it does, what it is allowed to do and "
     "what it must never do. Weak instructions equal a weak agent, and the system "
     "prompt is presented as 80% of the quality of what comes out."),

    ("E07", "anatomy", "4:52", "5:02",
     "Without tools, your agent is just a chatbot with a fancy hat",
     "The third block is the tools, which is what the agent can actually do — web "
     "search, CRM read and write, email send, calendar actions. Without tools the "
     "agent is just a chatbot with a fancy hat."),

    ("E08", "anatomy", "5:02", "5:08",
     "Long-term, your brand guidelines",
     "The fourth block is memory: short-term within the conversation, and long-term "
     "for brand guidelines, product information, customer context and past sessions."),

    ("E09", "anatomy", "5:08", "5:30",
     "Any agent that touches money, messaging, or the customer needs a review step in "
     "the first 30 days. No exceptions",
     "The fifth block is presented as non-negotiable: a human in the loop. Any agent "
     "that touches money, messaging or the customer needs a review step in the first "
     "30 days, with no exceptions."),

    ("E10", "portfolio", "5:49", "7:09",
     "Agent one tells you what to say. Agent two turns it into distribution",
     "Three agents are proposed as the first ones worth building: an intelligence "
     "agent at the top of the funnel that monitors competitors and delivers a plain "
     "English briefing; a content production agent in the middle that turns one "
     "approved long-form input into a multi-channel cascade queued for human review; "
     "and a revenue operations agent at the bottom that enriches and qualifies leads, "
     "scores them against the ICP and flags hot ones to a human rep. They chain: the "
     "first tells you what to say, the second turns it into distribution, the third "
     "converts the demand."),

    ("E11", "platform", "7:13", "7:23",
     "Honestly, it matters less than you think",
     "On platform choice, the lesson says it matters less than people think and that "
     "what matters is picking one and shipping something."),

    ("E12", "platform", "7:23", "8:59",
     "A security audit found that over a third of OpenClaw skills had at least one flaw",
     "The options are framed by where the team already is. HubSpot Breeze for teams "
     "already on HubSpot Professional or Enterprise, with near-zero setup overhead. "
     "Claude for no-code research and content work, which is what the live build uses. "
     "Gumloop for visual thinkers who want drag-and-drop. Zapier Agents for teams "
     "already on Zapier doing light operational work. OpenClaw is treated separately: "
     "open source, runs locally, controls the computer directly, and unlocks tools "
     "with no API — but a security audit found that over a third of its skills had at "
     "least one flaw, so it is presented as a last resort."),

    ("E13", "build", "9:08", "9:46",
     "What information you'll give, what output you want back, and clear boundaries",
     "The build starts with the outcome. Before opening any tool, write down three "
     "things: what information you will give, what output you want back, and clear "
     "boundaries — what the agent is never allowed to do. The most common mistake is "
     "opening the platform before defining what you actually want, which ends in "
     "automating a task instead of owning an outcome."),

    ("E14", "build", "9:18", "9:37",
     "never sends external emails, never posts outside the designated channel, and "
     "never stores contact data",
     "The worked example uses three competitor URLs as the input, a structured "
     "briefing posted to a Slack channel every Monday morning as the output, and "
     "boundaries that the agent never sends external emails, never posts outside the "
     "designated channel and never stores contact data."),

    ("E15", "build", "9:46", "10:02",
     "Structure your system prompt using this robot framework. role, objective, "
     "boundaries, output, tone. Every great agent prompt has all five",
     "The instructions are written with the ROBOT framework: role, objective, "
     "boundaries, output, tone. Every great agent prompt is said to have all five, "
     "every line in the prompt is doing a job, and the more specific it is the better "
     "the result — vague instructions equal vague output every time."),

    ("E16", "build", "10:02", "10:47",
     "For this agent, we need two. Web search",
     "Then the platform is chosen and the tools connected. What a platform can connect "
     "to is one of the first things to look at, because integrations are what turn a "
     "chat window into something that does work. The example connects exactly two: web "
     "search, toggled on so it pulls live competitor data, and Slack, so it posts the "
     "briefing to the channel. Running it automatically every Monday is described as "
     "an optional Zapier schedule added on top."),

    ("E17", "build", "10:47", "11:23",
     "This is what separates a generic bot from one that actually understands your "
     "business",
     "Next the agent is fed memory, which is what separates a generic bot from one "
     "that understands the business: context about who you are, who you serve and what "
     "good looks like. In the example this is channel context — audience description, "
     "competitor list, content pillars and goal — and the lesson notes it would be a "
     "product catalogue and personas for e-commerce, an ICP and positioning doc for "
     "B2B, or a client brief for an agency."),

    ("E18", "build", "11:23", "11:42",
     "Run it three to five times",
     "Then it is tested, broken and fixed. Run it three to five times; every time it "
     "produces something off-brand or surface level, go back to the system prompt and "
     "tighten it, and write down every failure as a fix list."),

    ("E19", "build", "11:42", "11:53",
     "add a human in the loop for the first 30 days",
     "Then a human is added in the loop for the first 30 days, reviewing every output "
     "before it goes anywhere; after 30 days, if it is consistently solid, the review "
     "can be loosened."),

    ("E20", "build", "11:53", "12:09",
     "Is it saving you at least 2 hours a week? Is the output better than what you "
     "produce manually?",
     "Finally it is measured with two questions: is it saving at least two hours a "
     "week, and is the output better than what you would produce manually. If both are "
     "yes, expand it; if either is no, go back and rebuild it."),

    ("E21", "market", "3:17", "4:06",
     "over 40% of agent projects will be cancelled by the end of 2027",
     "The market context given is that the agents market is on track to hit $50 "
     "billion by 2030 and that Gartner expects 60% of brands to use agentic AI by "
     "2028, but also that over 40% of agent projects will be cancelled by the end of "
     "2027 because teams rushed in without a plan, a clear outcome or governance. "
     "Building the wrong agent is said to be just as expensive as building nothing."),

    ("E22", "closing", "13:53", "14:09",
     "Start with one gap. The workflow that costs your team the most time every week",
     "The closing advice is not to build everything at once but to start with one gap "
     "— the workflow that costs the team the most time every week."),

    ("E23", "demo", "12:18", "13:41",
     "6 minutes and 19 seconds",
     "The lesson includes a live build of the intelligence agent in Claude — project, "
     "instructions, memory, two tools, then a test — completed in 6 minutes and 19 "
     "seconds."),
]

# Candidatos deliberadamente submetidos à regra e que devem falhar por não
# existirem em L0. São formas ESTRUTURAIS do runtime compilado, não conteúdo da
# aula. O script confirma a ausência; se alguma aparecer, vira achado.
STRUCTURAL_CANDIDATES = [
    ("R01", "METHOD_NOT_DEFINED", "código de recusa do runtime compilado"),
    ("R02", "MISSING_REQUIRED_INPUT", "código de parada do runtime compilado"),
    ("R03", "fail-closed", "política de falha fechada"),
    ("R04", "precedence", "ordem de precedência entre guardas"),
    ("R05", "schema", "contrato de schema"),
    ("R06", "resource routing", "roteamento entre recursos executáveis"),
    ("R07", "origin_class", "classificação epistêmica de origem"),
    ("R08", "decision-rules", "arquivo de regras de decisão executáveis"),
    ("R09", "workflows.yaml", "arquivo de workflow executável"),
    ("R10", "guard", "guarda de runtime"),
    ("R11", "ADR-", "registro atômico de decisão"),
    ("R12", "gate", "gate de workflow"),
]


def verify_elements(segs) -> tuple[list[dict], list[dict]]:
    accepted, rejected = [], []
    for eid, section, a, b, quote, prose in ELEMENTS:
        hay = norm(span_text(segs, a, b))
        ok = norm(quote) in hay
        rec = {"element_id": eid, "section": section,
               "span": {"source": f"youtube:{VIDEO_ID}", "start": a, "end": b},
               "quote": quote, "quote_verified_in_span": ok, "prose": prose}
        (accepted if ok else rejected).append(rec)
    for r in rejected:
        r["rejection_reason"] = "QUOTE_NOT_FOUND_IN_DECLARED_SPAN"
    return accepted, rejected


# Colisões lexicais conhecidas: o termo estrutural existe em L0 com OUTRO
# sentido, então o teste de ausência usa a forma precisa e registra a colisão.
LEXICAL_COLLISIONS = {
    "resource routing": ("A palavra 'routing' ocorre em L0 uma vez, em 8:10, como "
                         "'lead routing' — encaminhamento de leads no Zapier, não "
                         "roteamento entre recursos executáveis. Sentidos distintos."),
}


def verify_absences(segs) -> list[dict]:
    whole = norm(" ".join(t for _, t in segs))
    out = []
    for rid, term, why in STRUCTURAL_CANDIDATES:
        present = norm(term) in whole
        out.append({
            "element_id": rid, "candidate_term": term, "what_it_is": why,
            "present_in_L0": present,
            "status": "PRESENTE_EM_L0_REVISAR" if present else "REJEITADO_SEM_ANCORA",
            "reason": ("Encontrado em L0 — a rejeição automática não se aplica, "
                       "revisar à mão." if present else
                       "Nenhuma ocorrência em L0; forma estrutural do runtime "
                       "compilado, não conteúdo da aula."),
            **({"lexical_collision_note": LEXICAL_COLLISIONS[term]}
               if term in LEXICAL_COLLISIONS else {}),
        })
    return out


# --------------------------------------------------------------------------
# régua RASCUNHO (B4) — critérios só a partir de L0
# --------------------------------------------------------------------------
DRAFT_CRITERIA = [
    ("OUTCOME_CONTRACT", "9:08", "9:37",
     "Declara outcome, input, output e boundaries antes de construir.",
     [("complete", [90, 100], "Os quatro estão presentes e específicos."),
      ("partial", [40, 89], "Faltam um ou mais, ou ficam genéricos."),
      ("absent", [0, 39], "Parte para plataforma/ferramenta sem contrato de resultado.")]),
    ("ROBOT_PROMPT_STRUCTURE", "9:46", "9:57",
     "Escreve as instruções com role, objective, boundaries, output e tone.",
     [("all_five", [90, 100], "Os cinco componentes aparecem e fazem trabalho."),
      ("partial", [40, 89], "Alguns dos cinco, ou presentes só de nome."),
      ("absent", [0, 39], "Prompt sem estrutura declarada.")]),
    ("TOOL_SELECTION", "10:02", "10:47",
     "Escolhe ferramentas pelo que a tarefa exige e diz o que cada uma faz.",
     [("justified", [90, 100], "Ferramentas nomeadas e amarradas ao outcome."),
      ("partial", [40, 89], "Ferramentas nomeadas sem ligação com o outcome."),
      ("absent", [0, 39], "Nenhuma ferramenta ou lista sem propósito.")]),
    ("MEMORY_CONTEXT", "10:47", "11:23",
     "Especifica que contexto persistente o agente recebe.",
     [("specified", [90, 100], "Diz qual contexto e por quê."),
      ("partial", [40, 89], "Menciona memória sem dizer o conteúdo."),
      ("absent", [0, 39], "Não trata de memória.")]),
    ("TESTING_ITERATION", "11:23", "11:42",
     "Prevê rodar de três a cinco vezes e corrigir pelo que falhou.",
     [("specified", [90, 100], "Número de rodadas e laço de correção."),
      ("partial", [40, 89], "Fala em testar sem quantidade nem laço."),
      ("absent", [0, 39], "Não prevê teste.")]),
    ("HUMAN_REVIEW_30_DAYS", "11:42", "11:53",
     "Mantém revisão humana nos primeiros 30 dias antes de afrouxar.",
     [("explicit", [90, 100], "Revisão declarada com a janela de 30 dias."),
      ("partial", [40, 89], "Revisão humana sem janela."),
      ("absent", [0, 39], "Sem revisão humana.")]),
    ("MEASUREMENT", "11:53", "12:09",
     "Define como medir: 2h/semana economizadas e qualidade acima do manual.",
     [("both_questions", [90, 100], "As duas perguntas, com critério de expandir."),
      ("partial", [40, 89], "Uma das duas, ou métrica vaga."),
      ("absent", [0, 39], "Sem critério de medição.")]),
]


def build_rubric(segs) -> dict:
    crits, dropped = [], []
    for name, a, b, desc, anchors in DRAFT_CRITERIA:
        hay = span_text(segs, a, b)
        if not hay.strip():
            dropped.append(name)
            continue
        crits.append({
            "criterion": name,
            "description": desc,
            "l0_span": {"source": f"youtube:{VIDEO_ID}", "start": a, "end": b},
            "l0_excerpt": hay[:400],
            "score_anchors": {n: {"range": r, "condition": c} for n, r, c in anchors},
        })
    return {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-001-TEST-0008-RUBRIC-DRAFT-v0.1.4",
        "artifact_status": "DRAFT_NOT_FROZEN",
        "test_id": "TEST-0008",
        "candidate_version": "0.1.4",
        "external_audit_required_before_freeze": True,
        "why_audit_required": (
            "Quem escreveu o baseline não deveria escrever a régua sozinho. Este "
            "rascunho foi produzido na mesma passada que BASELINE-SUMMARY-v0.1.4.md, "
            "a partir da mesma fonte L0 e pelo mesmo autor. Congelar sem auditoria "
            "externa reintroduz a circularidade que o TEST-0008 existe para medir."),
        "derivation_constraint": (
            "Todo critério e toda âncora saem de um span de L0. Nenhum critério foi "
            "importado da régua do TEST-0007 nem do artefato sob teste."),
        "source": {"video_id": VIDEO_ID, "transcript_sha256": sha256_bytes(L0.read_bytes()),
                   "duration": yaml.safe_load(META.read_text(encoding="utf-8"))["source"]["duration"]},
        "criteria_without_l0_span_dropped": dropped,
        "rubric": crits,
        "not_frozen_note": (
            "Sem pesos, sem pisos obrigatórios e sem regra de decisão. Fixar peso e "
            "piso é decisão de quem conduz o teste, depois da auditoria."),
    }


# --------------------------------------------------------------------------
# condições (B3)
# --------------------------------------------------------------------------

def find_full_arm() -> tuple[str, bytes] | tuple[None, None]:
    want = "b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028"
    root = DRIVE / "Course-to-Skill"
    for p in sorted(root.rglob("*.zip")):
        try:
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if n.endswith("/"):
                        continue
                    b = z.read(n)
                    if sha256_bytes(b) == want:
                        return f"{p.relative_to(DRIVE)} :: {n}", b
        except zipfile.BadZipFile:
            continue
    return None, None


def build_conditions(summary_text: str) -> dict:
    COND_DIR.mkdir(parents=True, exist_ok=True)
    arm_path, arm_bytes = find_full_arm()

    f2 = ("You are given a written summary of a lesson about building AI agents.\n"
          "Treat it as reference material: a summary, not an operating procedure.\n"
          "Answer the user's request using it as background knowledge.\n")
    f3 = ("You are given the following as your operating skill.\n"
          "Treat it as the methodology you must apply to the user's request.\n"
          "Follow it as your working method.\n")

    files = {}
    (COND_DIR / "1_FULL_SKILL").mkdir(exist_ok=True)
    (COND_DIR / "2_SUMMARY_AS_SUMMARY").mkdir(exist_ok=True)
    (COND_DIR / "3_SUMMARY_AS_SKILL").mkdir(exist_ok=True)

    p = COND_DIR / "1_FULL_SKILL/POINTER.md"
    p.write_text(
        "# Condition 1 — FULL_SKILL\n\n"
        "Attach the frozen v0.1.4 FULL@AFTER_DEDUP runtime bundle.\n\n"
        f"- sha256: `{sha256_bytes(arm_bytes) if arm_bytes else 'NAO_LOCALIZADO'}`\n"
        f"- origem: `{arm_path or 'NAO_LOCALIZADO'}`\n\n"
        "O pacote NÃO é copiado para cá: Course-to-Skill/ é read-only nesta sessão e "
        "duplicar um artefato congelado criaria uma segunda fonte de verdade.\n",
        encoding="utf-8")
    files["1_FULL_SKILL/POINTER.md"] = p

    for d, framing in (("2_SUMMARY_AS_SUMMARY", f2), ("3_SUMMARY_AS_SKILL", f3)):
        fp = COND_DIR / d / "FRAMING.md"
        fp.write_text(framing, encoding="utf-8")
        sp = COND_DIR / d / "SUMMARY.md"
        sp.write_text(summary_text, encoding="utf-8")
        files[f"{d}/FRAMING.md"] = fp
        files[f"{d}/SUMMARY.md"] = sp

    h2 = sha256_bytes((COND_DIR / "2_SUMMARY_AS_SUMMARY/SUMMARY.md").read_bytes())
    h3 = sha256_bytes((COND_DIR / "3_SUMMARY_AS_SKILL/SUMMARY.md").read_bytes())
    return {
        "conditions": {
            "1_FULL_SKILL": {"kind": "frozen runtime bundle (referenciado, não copiado)",
                             "arm_sha256": sha256_bytes(arm_bytes) if arm_bytes else None,
                             "arm_source": arm_path},
            "2_SUMMARY_AS_SUMMARY": {
                "summary_sha256": h2,
                "framing_sha256": sha256_bytes(
                    (COND_DIR / "2_SUMMARY_AS_SUMMARY/FRAMING.md").read_bytes())},
            "3_SUMMARY_AS_SKILL": {
                "summary_sha256": h3,
                "framing_sha256": sha256_bytes(
                    (COND_DIR / "3_SUMMARY_AS_SKILL/FRAMING.md").read_bytes())},
        },
        "summary_byte_identical_between_2_and_3": h2 == h3,
        "only_framing_differs": True,
        "executed": False,
        "note": "Condições montadas, nenhuma executada.",
    }


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    segs = load_l0()
    accepted, rejected = verify_elements(segs)
    absences = verify_absences(segs)

    order = ["framing", "concepts", "market", "anatomy", "portfolio", "platform",
             "build", "demo", "closing"]
    body = []
    for sec in order:
        for e in accepted:
            if e["section"] == sec:
                body.append(e["prose"])
    summary = ("# PILOT-001 — Baseline Summary (v0.1.4, information parity)\n\n"
               + "\n\n".join(body) + "\n")

    OUT_SUMMARY.write_text(summary, encoding="utf-8")

    prov = {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-001-TEST-0008-BASELINE-PROVENANCE-v0.1.4",
        "artifact_status": "DRAFT_NOT_FROZEN",
        "generated_at_utc": stamp,
        "generator": Path(__file__).name,
        "principle": "PARIDADE DE INFORMAÇÃO, DIFERENÇA DE ESTRUTURA",
        "hard_rule": (
            "Todo elemento do resumo tem span de L0 e citação verificada contra o "
            "transcript pelo próprio script. Elemento cuja citação não é encontrada no "
            "span declarado não entra no resumo."),
        "what_is_excluded_by_design": [
            "workflow executável", "gates", "precedência", "schema", "routing",
        ],
        "source": {
            "video_id": VIDEO_ID,
            "transcript_path": str(L0.relative_to(DRIVE)),
            "transcript_sha256": sha256_bytes(L0.read_bytes()),
            "transcript_bytes": L0.stat().st_size,
            "declared_duration":
                yaml.safe_load(META.read_text(encoding="utf-8"))["source"]["duration"],
            "segments": len(segs),
        },
        "baseline_summary": {
            "path": OUT_SUMMARY.name,
            "sha256": sha256_text(summary),
            "bytes": len(summary.encode("utf-8")),
        },
        "counts": {
            "candidates": len(ELEMENTS),
            "accepted": len(accepted),
            "rejected_quote_not_found": len(rejected),
            "structural_candidates_tested": len(absences),
            "rejected_sem_ancora": sum(1 for a in absences
                                       if a["status"] == "REJEITADO_SEM_ANCORA"),
        },
        "elements": accepted,
        "REJEITADO_SEM_ANCORA": [a for a in absences
                                 if a["status"] == "REJEITADO_SEM_ANCORA"],
        "REJEITADO_CITACAO_NAO_ENCONTRADA": rejected,
        "PRESENTE_EM_L0_REVISAR": [a for a in absences
                                   if a["status"] != "REJEITADO_SEM_ANCORA"],
        "robot_coverage_check": {
            "required_components": ["role", "objective", "boundaries", "output", "tone"],
            "element_id": "E15",
            "span": "9:46-10:02",
            "present_in_summary": all(
                c in summary.lower()
                for c in ["role", "objective", "boundaries", "output", "tone"]),
            "why_it_matters": (
                "O baseline anterior não mencionava ROBOT, enquanto a régua exigia "
                "'ROBOT prompt'. A condição-resumo era penalizada por não saber algo "
                "que a régua herdou do outro braço. Cobrir ROBOT é o que torna a "
                "comparação de PARIDADE DE INFORMAÇÃO honesta."),
        },
    }

    # Contaminação estrutural: o resumo não pode carregar as formas do runtime.
    # "workflow" é tolerado SÓ quando vem de citação literal de L0 (sentido
    # corrente de "fluxo de trabalho"), e a origem é apontada.
    contam = []
    low = summary.lower()
    for term in ["gate", "precedence", "schema", "resource routing",
                 "method_not_defined", "step_id", "rg-013", "yaml", "workflow"]:
        n = low.count(term)
        entry = {"term": term, "occurrences": n}
        if n and term == "workflow":
            src = [e for e in accepted if "workflow" in e["prose"].lower()]
            entry["allowed"] = True
            entry["justification"] = (
                "Ocorre em citação literal de L0 (14:00-14:04, 'The workflow that "
                "costs your team the most time every week'), no sentido corrente de "
                "fluxo de trabalho — não como workflow executável.")
            entry["elements"] = [e["element_id"] for e in src]
        elif n:
            entry["allowed"] = False
        contam.append(entry)
    prov["structural_contamination_check"] = {
        "rule": ("O baseline é prosa. Nenhuma forma estrutural do runtime compilado "
                 "pode aparecer, exceto palavra do vocabulário comum que L0 usa."),
        "terms": contam,
        "clean": all(c["occurrences"] == 0 or c.get("allowed") for c in contam),
    }

    conds = build_conditions(summary)
    prov["conditions_b3"] = conds

    OUT_PROV.write_text(
        "# BASELINE-PROVENANCE — TEST-0008 v0.1.4\n"
        "# Gerado por script. Toda citação verificada contra o transcript L0.\n"
        "# READ-ONLY sobre Course-to-Skill/. Nada congelado.\n"
        + yaml.safe_dump(prov, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    rub = build_rubric(segs)
    OUT_RUBRIC.write_text(
        "# TEST-0008 RUBRIC — RASCUNHO, NÃO CONGELADO\n"
        "# Precisa de auditoria externa antes de congelar: quem escreveu o baseline\n"
        "# não deveria escrever a régua sozinho.\n"
        + yaml.safe_dump(rub, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"elementos: {len(accepted)}/{len(ELEMENTS)} aceitos, "
          f"{len(rejected)} rejeitados por citação")
    for r in rejected:
        print(f"  REJEITADO {r['element_id']} span {r['span']['start']}-"
              f"{r['span']['end']}: citação não encontrada")
    print(f"REJEITADO_SEM_ANCORA: {prov['counts']['rejected_sem_ancora']}"
          f"/{len(absences)}")
    for a in absences:
        if a["status"] != "REJEITADO_SEM_ANCORA":
            print(f"  ATENÇÃO {a['candidate_term']!r} aparece em L0 — revisar")
    print(f"ROBOT coberto: {prov['robot_coverage_check']['present_in_summary']}")
    print(f"resumo 2 == 3 byte a byte: {conds['summary_byte_identical_between_2_and_3']}")
    for f in (OUT_SUMMARY, OUT_PROV, OUT_RUBRIC):
        print(f"publicado: {f.name} ({f.stat().st_size} B) {sha256_bytes(f.read_bytes())[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
