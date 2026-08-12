#!/usr/bin/env python3
"""PASSO 3 — rascunho da rubrica do TEST-0008, decisão do Alexandre aplicada.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/. NÃO congela nada.
Zero chamadas de modelo.

Decisão congelada, não reaberta aqui:
  sete métricas; CONSISTENCY e HUMAN_CHECKPOINT_COMPLIANCE em PAPEL DUPLO —
  métricas diretas E portão pelos seus pisos; primária TOTAL_SCORE; as outras
  seis são decomposição diagnóstica.

REGRA DURA: toda citação — de critério, de peso e de ÂNCORA — tem de resolver em
L0 por substring normalizada. Uma que não resolva ABORTA a geração.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CL = DRIVE / "Course-to-Skill-Claude"
DOCS = CL / "docs"
PKG = DOCS / "TEST-0008-RUBRIC-AUDIT-PACKAGE"
L0 = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
      / "sources/transcript/transcript-original-en.txt")
L0_SHA = "068b4998c160d143ee6bc2942e444157fdaebb4311b2ca9eced625c22626df67"
PREV_DRAFT = DOCS / "TEST-0008-RUBRIC-DRAFT-v0.1.4.yaml"
PROV = DOCS / "BASELINE-PROVENANCE-v0.1.4.yaml"
BASELINE = DOCS / "BASELINE-SUMMARY-v0.1.4.md"
CONDS = DOCS / "TEST-0008-CONDITIONS-v0.1.4"
METRIC_LOCK = DOCS / "TEST-0008-METRIC-LOCK.yaml"
SCORER_REPORT = DOCS / "SCORER-V2-TWO-COMPARISONS.yaml"
MARK = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")


def sh(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def shp(p: Path) -> str: return sh(p.read_bytes())
def fmt(s: int) -> str: return f"{s // 60}:{s % 60:02d}"


class Transcript:
    def __init__(self, path: Path) -> None:
        raw = path.read_text(encoding="utf-8")
        marks = [(m.start(), m.end(), int(m.group(1)) * 60 + int(m.group(2)))
                 for m in MARK.finditer(raw)]
        self.segments: list[tuple[int, int, int]] = []
        parts, pos = [], 0
        chunks = [(0, raw[:marks[0][0]] if marks else raw)]
        for i, (a, b, s) in enumerate(marks):
            end = marks[i + 1][0] if i + 1 < len(marks) else len(raw)
            chunks.append((s, raw[b:end]))
        for s, txt in chunks:
            t = " ".join(txt.split())
            if not t:
                continue
            parts.append(t)
            self.segments.append((pos, pos + len(t), s))
            pos += len(t) + 1
        self.norm = " ".join(parts)

    def span(self, quote: str) -> dict | None:
        q = " ".join(quote.split())
        a = self.norm.find(q)
        if a < 0:
            return None
        b = a + len(q)
        start = next((s for x, y, s in self.segments if x <= a <= y), 0)
        k = next((i for i, (x, y, s) in enumerate(self.segments) if x <= b <= y), None)
        if k is None:
            end = self.segments[-1][2]
        elif k + 1 < len(self.segments):
            end = self.segments[k + 1][2]
        else:
            end = self.segments[k][2]
        return {"source": "youtube:YkdAx2XjWDs", "start": fmt(start), "end": fmt(end),
                "start_s": start, "end_s": end}


# ---------------------------------------------------------- OS TRÊS REGIMES
# As âncoras têm de separar TRÊS coisas, não duas. Recusa e execução completa
# deixariam invisível o regime do meio — e é o do meio que o TEST-0008 mede.
#
#   R1 APLICACAO_ESTRUTURAL   — aplica a partir de representação operacional
#                               explícita. É o que FULL_SKILL pode fazer.
#   R2 APLICACAO_INFERENCIAL  — reconstrói o comportamento a partir de prosa,
#                               sem camada de roteamento. É o que
#                               SUMMARY_AS_SUMMARY pode fazer, e faz honestamente.
#   R3 ASSERCAO_SEM_SUBSTANCIA — enuncia o método sem executá-lo. É o artefato
#                               de ENQUADRAMENTO que SUMMARY_AS_SKILL pode
#                               produzir: o mesmo texto, apresentado como
#                               procedimento, convida a performar estrutura que
#                               o braço não tem.
#
# R3 TEM DE FICAR ABAIXO DE R2. Se performar estrutura pontuasse acima de
# reconstruí-la de prosa, F mediria a disposição de encenar, e a comparação
# primária P herdaria esse ruído. O canário A2 trava isso.
REGIMES = [
    ("APLICACAO_ESTRUTURAL", 90, 100,
     "Aplica o passo a partir de representação operacional explícita: a decisão "
     "aparece tomada, com o critério visível, no ponto certo da sequência."),
    ("APLICACAO_INFERENCIAL", 70, 89,
     "Reconstrói o passo corretamente a partir de conhecimento em prosa, sem "
     "camada operacional explícita. Substância presente, estrutura ausente."),
    ("ASSERCAO_SEM_SUBSTANCIA", 30, 69,
     "Enuncia, nomeia ou promete o passo sem executá-lo: cita o método, declara "
     "conformidade ou descreve o que faria, sem produzir o conteúdo."),
    ("AUSENTE_OU_CONTRADIZ", 0, 29,
     "Ausente, ou contradiz o que a fonte estabelece."),
]

CRITERIA = [
    {"criterion": "OUTCOME_CONTRACT", "weight": "0.18",
     "metric": "DECISION_ACCURACY", "minimum_score": 80,
     "description": "Declara outcome, input, output e boundaries antes de escolher ferramenta.",
     "quote": "Step one, start with the outcome. Before you open anything, write down three things. What information you'll give, what output you want back, and clear boundaries.",
     "weight_quote": "You'll end up automating a task instead of owning an outcome.",
     "weight_rationale": "L0 nomeia partir da ferramenta como o erro mais comum; segundo maior peso.",
     "r3_quote": "automating a task instead of owning an outcome"},
    {"criterion": "ROBOT_PROMPT_STRUCTURE", "weight": "0.12",
     "metric": "METHODOLOGY_FIDELITY", "minimum_score": 85,
     "description": "Escreve as instruções com role, objective, boundaries, output e tone.",
     "quote": "Structure your system prompt using this robot framework. role, objective, boundaries, output, tone. Every great agent prompt has all five.",
     "weight_quote": "Vague instructions equal vague output every time.",
     "weight_rationale": "L0 trata o system prompt como determinante da qualidade da saída.",
     "r3_quote": "Vague instructions equal vague output every time."},
    {"criterion": "TOOL_SELECTION", "weight": "0.10",
     "metric": "DECISION_ACCURACY", "minimum_score": 80,
     "description": "Escolhe plataforma e conecta só as ferramentas que o outcome exige.",
     "quote": "Step three, choose your platform and connect the tools. This is where you choose what you're building in and what it's going to connect to.",
     "weight_quote": "The model matters less than you think.",
     "weight_rationale": "L0 relativiza a escolha de plataforma; peso deliberadamente menor.",
     "r3_quote": "Without tools, your agent is just a chatbot with a fancy hat."},
    {"criterion": "MEMORY_CONTEXT", "weight": "0.08",
     "metric": "EXECUTION_QUALITY", "minimum_score": 75,
     "description": "Alimenta o agente com contexto de negócio, não só instruções.",
     "quote": "Step four, feed it memory. This is what separates a generic bot from one that actually understands your business.",
     "weight_quote": "you give it context about who you are, who you serve, and what good looks like for you",
     "weight_rationale": "Passo presente em L0 e sem qualificador de criticidade; peso baixo.",
     "r3_quote": "separates a generic bot from one that actually understands your business"},
    {"criterion": "TESTING_ITERATION", "weight": "0.12",
     "metric": "EXECUTION_QUALITY", "minimum_score": 80,
     "description": "Roda de três a cinco vezes, registra falhas e volta ao prompt.",
     "quote": "Step five, test it, break it, fix it. Run it three to five times.",
     "weight_quote": "Go back to the system prompt and tighten it.",
     "weight_rationale": "L0 dá procedimento numérico explícito; passo verificável.",
     "r3_quote": "Every time it produces something off brand or surface level"},
    {"criterion": "HUMAN_REVIEW_30_DAYS", "weight": "0.20",
     "metric": "HUMAN_CHECKPOINT_COMPLIANCE", "minimum_score": 90,
     "description": "Mantém revisão humana de toda saída nos primeiros 30 dias.",
     "quote": "Step six, add a human in the loop for the first 30 days. Review every output before it goes anywhere.",
     "weight_quote": "Any agent that touches money, messaging, or the customer needs a review step in the first 30 days. No exceptions.",
     "weight_rationale": "MAIOR PESO: é o único passo que L0 qualifica com 'No exceptions'.",
     "r3_quote": "Skip this and you risk a weird auto reply going to 4,000 leads."},
    {"criterion": "MEASUREMENT", "weight": "0.08",
     "metric": "EXECUTION_QUALITY", "minimum_score": 75,
     "description": "Fecha com as duas perguntas de medição e a decisão de expandir ou refazer.",
     "quote": "In step seven, measure it with these two questions. Is it saving you at least 2 hours a week?",
     "weight_quote": "If both are yes, expand it. If either's a no, go back and rebuild it.",
     "weight_rationale": "Passo final, critério binário simples; peso baixo.",
     "r3_quote": "Don't let dead agents live in your stack."},
    {"criterion": "STEP_ORDER_INTEGRITY", "weight": "0.12",
     "metric": "CONSISTENCY", "minimum_score": 80,
     "description": "Mantém a ordem dos passos e a precedência declarada entre opções.",
     "quote": "If any of the tools we just covered do what you need, start there. Open Claw is the one you reach for when you have a specific piece of software that nothing else can connect to.",
     "weight_quote": "But that's the wrong starting point.",
     "weight_rationale": "L0 trata a ORDEM como conteúdo, não como forma: começar no lugar errado é o erro nomeado.",
     "r3_quote": "But that's the wrong starting point."},
]

GATE_CRITERIA = ["HUMAN_REVIEW_30_DAYS", "STEP_ORDER_INTEGRITY"]
METRICS = ["TOTAL_SCORE", "DECISION_ACCURACY", "METHODOLOGY_FIDELITY",
           "EXECUTION_QUALITY", "HALLUCINATION_RATE", "CONSISTENCY",
           "HUMAN_CHECKPOINT_COMPLIANCE"]

# ---------------------------------------------------------- CLASSES DE MÉTRICA
# HALLUCINATION_RATE não é uma métrica sem critério: é uma métrica de OUTRA
# CLASSE. As seis medem o output contra um ENSINAMENTO da fonte — logo exigem
# âncora em L0, e é dela que vem o critério. Ela mede o output contra a FONTE:
# afirma-se algo que a fonte não sustenta? Não há ensinamento a ancorar, porque
# o que se mede é a AUSÊNCIA de invenção, não a presença de um passo.
#
# Sem esta declaração o auditor cobraria — com razão — a âncora que ela não pode
# ter, e leria como defeito o que é diferença de classe.
METRIC_CLASSES = {
    "TOTAL_SCORE": {
        "metric_class": "AGREGADO",
        "measures_against": "os oito critérios ponderados, não uma fonte externa",
        "l0_anchor_required": False,
        "por_que_nao_requer_ancora": ("é a soma ponderada dos critérios; a ancoragem "
                                      "está nos critérios que a compõem, não nela"),
        "criteria_backing": "ALL",
    },
    "DECISION_ACCURACY": {"metric_class": "CONFORMIDADE"},
    "METHODOLOGY_FIDELITY": {"metric_class": "CONFORMIDADE"},
    "EXECUTION_QUALITY": {"metric_class": "CONFORMIDADE"},
    "CONSISTENCY": {"metric_class": "CONFORMIDADE"},
    "HUMAN_CHECKPOINT_COMPLIANCE": {"metric_class": "CONFORMIDADE"},
    "HALLUCINATION_RATE": {
        "metric_class": "INTEGRIDADE",
        "measures_against": "a FONTE, não um ensinamento da fonte",
        "l0_anchor_required": False,
        "anchoring_requirement_applies": False,
        "por_que_a_exigencia_de_ancora_NAO_se_aplica": (
            "As métricas de CONFORMIDADE perguntam: o output faz o que a fonte "
            "ENSINA? Cada uma tem um passo ensinado, logo tem span e citação. Esta "
            "pergunta outra coisa: o output afirma algo que a fonte NÃO SUSTENTA? "
            "O objeto medido é a ausência de invenção. Não existe passo a ancorar, "
            "e exigir um obrigaria a inventar um span — que é precisamente o defeito "
            "que a métrica existe para detectar."),
        "criteria_backing": "NENHUM, POR CLASSE — não por omissão",
        "definicao_vem_de": "TEST-0008-METRIC-LOCK.yaml",
        "polarity": "LOWER_IS_BETTER",
        "sinal_invertido_antes_de_entrar_em_margem": True,
        "numerador_denominador_e_regra_de_zero": "declarados no metric lock",
    },
}
CLASS_CONFORMIDADE_DEFAULTS = {
    "measures_against": "um ENSINAMENTO da fonte",
    "l0_anchor_required": True,
    "anchoring_requirement_applies": True,
    "por_que_requer_ancora": ("mede se o output faz o que a fonte ensina; sem span e "
                             "citação não há como distinguir o que a fonte ensina do "
                             "que o avaliador acha que ela deveria ensinar"),
}

# Nomes que NÃO podem viajar na rubrica do juiz. Ver `strip_for_judge`.
CONDITION_NAMES = ["FULL_SKILL", "SUMMARY_AS_SUMMARY", "SUMMARY_AS_SKILL"]
OPERATOR_ONLY_VOCAB = ["condicao_que_o_produz", "condição", "condition", "braço",
                       "enquadramento", "framing", "baseline", "comparison_id",
                       "primary_metric", "diagnóstica", "diagnostic", "PARA_O_AUDITOR",
                       "auditor", "premissa"]


def wsum(items, key="weight") -> Decimal:
    return sum((Decimal(str(i[key])) for i in items), Decimal("0"))


def check_weights(items) -> tuple[bool, str, Decimal]:
    s = wsum(items)
    return (s == Decimal("1.0"), "ACCEPTED" if s == Decimal("1.0")
            else f"WEIGHT_SUM_NOT_ONE: {s}", s)


def canary(tr: Transcript, baseline_norm: str, rejected_terms: list[str],
           built: list[dict]) -> list[dict]:
    rows: list[dict] = []

    def rec(case, expect, got, ok, note=""):
        rows.append({"case": case, "expect": expect, "got": got, "passed": ok,
                     "note": note})

    ok, code, s = check_weights(CRITERIA)
    rec("W1_SOMA_EXATA_UM", "ACEITA", f"{code} soma={s}", ok)
    okL, codeL, _ = check_weights([{"weight": w} for w in ("0.3", "0.2", "0.2", "0.2")])
    rec("W2_SOMA_0_9_A_LEGADA", "REJEITA", codeL, not okL,
        "a rubrica legada do RELEASE soma 0,9 e limita o TOTAL_SCORE a 90")
    over = [dict(c) for c in CRITERIA]; over[0]["weight"] = "0.28"
    okO, codeO, _ = check_weights(over)
    rec("W3_SOMA_1_1", "REJEITA", codeO, not okO)
    alt = [{"weight": w} for w in ("0.57", "0.29", "0.09", "0.05")]
    okA, _, sA = check_weights(alt)
    fa = sum(float(a["weight"]) for a in alt)
    fthis = sum(float(c["weight"]) for c in CRITERIA)
    rec("W4_CONJUNTO_VALIDO_QUE_O_FLOAT_RECUSA", "EXATO aceita E float recusaria",
        f"Decimal={sA} aceita={okA} · float={fa!r} recusaria={fa != 1.0}",
        okA and fa != 1.0,
        f"nos pesos DESTE rascunho a soma binária calha de dar {fthis!r} — sorte, "
        f"não propriedade; por isso a checagem é em Decimal")

    # citações: critério, peso e ÂNCORA
    bad = [(c["criterion"], k) for c in CRITERIA
           for k in ("quote", "weight_quote", "r3_quote")
           if tr.span(c[k]) is None]
    rec("Q1_TODA_CITACAO_RESOLVE_EM_L0",
        f"{len(CRITERIA)*3} citações resolvem",
        "todas" if not bad else bad, not bad,
        "critério, justificativa de peso e âncora do regime R3")
    fake = "the compiled skill routing gate precedence schema for this lesson"
    rec("Q2_CITACAO_FABRICADA", "REJEITA",
        "não resolve" if tr.span(fake) is None else "RESOLVEU", tr.span(fake) is None)
    n_anchor_quotes = sum(1 for c in built for a in c["score_anchors"].values()
                          if a["l0_anchor"]["quote_verified_in_span"])
    n_anchors = sum(len(c["score_anchors"]) for c in built)
    rec("Q3_TODA_ANCORA_TEM_CITACAO_VERIFICADA", f"{n_anchors} âncoras",
        f"{n_anchor_quotes}/{n_anchors}", n_anchor_quotes == n_anchors)

    # os três regimes
    faixas = [(lo, hi) for _, lo, hi, _ in REGIMES]
    cobre = (min(lo for lo, _ in faixas) == 0 and max(hi for _, hi in faixas) == 100
             and all(faixas[i][1] + 1 == faixas[i - 1][0]
                     for i in range(1, len(faixas))))
    rec("A1_FAIXAS_CONTIGUAS_E_COMPLETAS", "0–100 sem buraco nem sobreposição",
        str(faixas), cobre)
    r2_lo = dict((n, (lo, hi)) for n, lo, hi, _ in REGIMES)["APLICACAO_INFERENCIAL"][0]
    r3_hi = dict((n, (lo, hi)) for n, lo, hi, _ in REGIMES)["ASSERCAO_SEM_SUBSTANCIA"][1]
    rec("A2_ASSERCAO_ABAIXO_DE_INFERENCIA",
        "teto de ASSERCAO_SEM_SUBSTANCIA < piso de APLICACAO_INFERENCIAL",
        f"{r3_hi} < {r2_lo}", r3_hi < r2_lo,
        "se performar estrutura pontuasse acima de reconstruí-la de prosa, F "
        "mediria disposição de encenar e P herdaria o ruído")
    mut = [(0, 69), (60, 89)]      # sobreposição deliberada
    rec("A2_ASSERCAO_ABAIXO_DE_INFERENCIA", "MUTANTE com sobreposição é REJEITADO",
        f"{mut[0][1]} < {mut[1][0]} -> {mut[0][1] < mut[1][0]}",
        not (mut[0][1] < mut[1][0]))
    rec("A3_TRES_REGIMES_PRESENTES",
        "três regimes de condição + ausência, não só recusa e execução",
        [n for n, _, _, _ in REGIMES], len(REGIMES) == 4)

    # circularidade mecanizável
    leaked = [c["criterion"] for c in CRITERIA
              for k in ("quote", "weight_quote", "r3_quote")
              if tr.span(c[k]) is None and " ".join(c[k].split()) in baseline_norm]
    rec("C1_CITACAO_VINDA_DO_BASELINE", "nenhuma",
        "nenhuma" if not leaked else leaked, not leaked)
    probe = "The lesson's central reframe is to stop asking which task can be automated"
    rec("C1_CITACAO_VINDA_DO_BASELINE",
        "detector tem poder: frase só-do-baseline é reconhecível",
        f"no baseline={probe in baseline_norm} em L0={tr.span(probe) is not None}",
        (probe in baseline_norm) and tr.span(probe) is None)
    text_all = json.dumps(CRITERIA, ensure_ascii=False).lower()
    hits = [t for t in rejected_terms if t.lower() in text_all]
    rec("C2_TERMO_SEM_ANCORA_EM_L0", "nenhum dos 12 termos rejeitados",
        "nenhum" if not hits else hits, not hits)

    # portão
    gate = [c for c in CRITERIA if c["criterion"] in GATE_CRITERIA]
    rec("G1_PORTAO_TEM_PAPEL_DUPLO",
        "os dois critérios do portão também são métricas diretas",
        [c["metric"] for c in gate],
        all(c["metric"] in METRICS for c in gate))
    rec("G2_METRICAS", "sete", len(METRICS), len(METRICS) == 7)
    rec("G3_PRIMARIA_UNICA", "TOTAL_SCORE e só ela",
        "TOTAL_SCORE", METRICS[0] == "TOTAL_SCORE")
    return rows


def canary_blinding_and_classes(operator: dict, judge: dict,
                                built: list[dict]) -> list[dict]:
    rows: list[dict] = []

    def rec(case, expect, got, ok, note=""):
        rows.append({"case": case, "expect": expect, "got": got, "passed": ok,
                     "note": note})

    # ---- L1: a régua do juiz não pode conter nome de condição
    hits = scan_leaks(judge)
    rec("L1_REGUA_DO_JUIZ_SEM_NOME_DE_CONDICAO", "zero vazamentos",
        "limpa" if not hits else hits[:3], not hits)

    contaminated = json.loads(json.dumps(judge))
    first = contaminated["rubric"][0]["score_anchors"]["ASSERCAO_SEM_SUBSTANCIA"]
    first["observable_definition"] += " (típico de SUMMARY_AS_SKILL)"
    mut = scan_leaks(contaminated)
    rec("L1_REGUA_DO_JUIZ_SEM_NOME_DE_CONDICAO",
        "FIXTURE CONTAMINADA É REJEITADA",
        [h["term"] for h in mut] or "PASSOU — sem poder de detecção",
        any(h["severity"] == "FORBIDDEN_CONDITION_NAME" for h in mut),
        "injeta um nome de condição numa âncora; o varredor tem de pegar")

    op_hits = scan_leaks(operator)
    rec("L2_REGUA_DO_OPERADOR_MANTEM_A_COLUNA",
        "o operador CONTÉM os nomes (é o ponto da separação)",
        f"{len(op_hits)} ocorrências no operador, 0 no juiz",
        len(op_hits) > 0 and not hits,
        "se as duas estivessem limpas, não haveria separação — haveria perda")

    # ---- M: classes de métrica
    no_class = [m for m in METRICS if m not in METRIC_CLASSES]
    rec("M1_TODA_METRICA_TEM_CLASSE", "nenhuma sem classe",
        "todas" if not no_class else no_class, not no_class)

    backed = {}
    for m in METRICS:
        backed[m] = [c["criterion"] for c in built if c["maps_to_metric"] == m]
    conf = [m for m, v in METRIC_CLASSES.items()
            if v["metric_class"] == "CONFORMIDADE"]
    orphan_conf = [m for m in conf if not backed[m]]
    rec("M2_CONFORMIDADE_TEM_CRITERIO", "toda métrica de CONFORMIDADE tem critério",
        {m: backed[m] for m in conf} if not orphan_conf else orphan_conf,
        not orphan_conf)

    # o mutante é o defeito real que o revisor encontrou
    fake_classes = dict(METRIC_CLASSES)
    fake_classes["HALLUCINATION_RATE"] = {"metric_class": "CONFORMIDADE"}
    fake_orphans = [m for m, v in fake_classes.items()
                    if v["metric_class"] == "CONFORMIDADE" and not backed.get(m)]
    rec("M2_CONFORMIDADE_TEM_CRITERIO",
        "MUTANTE: HALLUCINATION_RATE como CONFORMIDADE é REJEITADA",
        fake_orphans or "PASSOU — sem poder de detecção",
        "HALLUCINATION_RATE" in fake_orphans,
        "é exatamente o defeito apontado: métrica órfã. O canário o pega agora")

    integ = [m for m, v in METRIC_CLASSES.items()
             if v["metric_class"] == "INTEGRIDADE"]
    ok_i = all(not backed[m] and METRIC_CLASSES[m]["l0_anchor_required"] is False
               and METRIC_CLASSES[m]["anchoring_requirement_applies"] is False
               for m in integ)
    rec("M3_INTEGRIDADE_SEM_ANCORA_POR_CLASSE",
        "INTEGRIDADE: sem critério, sem exigência de âncora, com razão escrita",
        {m: METRIC_CLASSES[m]["criteria_backing"] for m in integ}, ok_i)

    total = [m for m, v in METRIC_CLASSES.items() if v["metric_class"] == "AGREGADO"]
    rec("M4_AGREGADO_E_SO_A_PRIMARIA", "só TOTAL_SCORE é AGREGADO",
        total, total == ["TOTAL_SCORE"])
    return rows



# ------------------------------------------------------- CEGAMENTO DO JUIZ
def walk_strings(o, path="$"):
    if isinstance(o, dict):
        # SÓ valores. Nome de campo é estrutura do documento, não conteúdo que o
        # juiz lê como informação sobre o experimento.
        for k, v in o.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(o, str):
        yield path, o


def scan_leaks(doc) -> list[dict]:
    """Procura na rubrica do juiz o que só o operador pode saber.

    Duas listas, ambas de rejeição dura:
      - CONDITION_NAMES: identificador de condição. Se o juiz souber qual output
        e qual, classifica por EXPECTATIVA. É fatal aqui porque as condicoes 2 e
        3 tem conteudo BYTE-IDENTICO e diferem so no enquadramento: sabendo qual
        e qual, o juiz pontua a 3 mais baixo por rotulo e F sai negativo por
        construcao, medindo o rotulo em vez do efeito.
      - OPERATOR_ONLY_VOCAB: o vocabulario do desenho. Uma regua de pontuacao nao
        tem por que conter 'condicao', 'enquadramento' ou 'baseline'; se contem,
        esta contando ao juiz como o experimento e montado.

    LIMITE DECLARADO: pega o literal e variantes proximas. Uma parafrase — "o
    artefato compilado", "a versao em prosa" — NAO e pega. E triagem, nao prova.
    """
    hits = []
    for path, text in walk_strings(doc):
        low = text.lower()
        for name in CONDITION_NAMES:
            for form in (name, name.replace("_", " "), name.replace("_", "-")):
                if form.lower() in low:
                    hits.append({"severity": "FORBIDDEN_CONDITION_NAME",
                                 "term": name, "path": path,
                                 "excerpt": text[:120]})
                    break
        for term in OPERATOR_ONLY_VOCAB:
            if term.lower() in low:
                hits.append({"severity": "OPERATOR_ONLY_VOCABULARY",
                             "term": term, "path": path, "excerpt": text[:120]})
    return hits


def strip_for_judge(operator: dict) -> dict:
    """A regua do juiz: faixas definidas SO por comportamento observavel.

    As definicoes comportamentais NAO sao alteradas — o problema nunca foi a
    definicao, foi o rotulo viajar junto com ela.
    """
    keep_criterion = ("criterion", "weight", "mandatory", "minimum_score",
                      "description", "l0_span", "l0_excerpt", "score_anchors")
    rubric = []
    for c in operator["rubric"]:
        row = {k: c[k] for k in keep_criterion}
        row["score_anchors"] = {
            name: {"range": a["range"], "observable_definition": a["condition"],
                   "l0_anchor": {"span": a["l0_anchor"]["span"],
                                 "quote": a["l0_anchor"]["quote"]}}
            for name, a in c["score_anchors"].items()}
        rubric.append(row)
    return {
        "schema_version": "0.3.0",
        "artifact_id": "PILOT-001-TEST-0008-RUBRIC-JUDGE",
        "artifact_status": "DRAFT_NOT_FROZEN",
        "test_id": "TEST-0008", "candidate_version": "0.1.4",
        "audience": "JUIZ",
        "blinding": {
            "outputs_are_unlabelled": True,
            "slots": ["A", "B", "C"],
            "order_is_shuffled": True,
            "order_recorded_where_the_judge_cannot_see": True,
            "instruction": ("Pontue cada slot SOMENTE pelo que o texto do slot faz. "
                            "Nao infira origem, nao compare slots entre si para "
                            "decidir nota, nao ordene os slots antes de pontuar."),
        },
        "scoring_method": operator["scoring_method"],
        "score_scale": operator["score_scale"],
        "weights_sum": operator["weights"]["sum"],
        "score_bands": [{"name": n, "range": [lo, hi], "observable_definition": cond}
                        for n, lo, hi, cond in REGIMES],
        "band_rule": ("As faixas sao definidas por COMPORTAMENTO OBSERVAVEL no texto "
                      "pontuado. Nenhuma faixa corresponde a uma origem, e nenhuma "
                      "origem e conhecida por quem pontua."),
        "citation_requirement": ("toda nota exige citacao literal do slot pontuado, "
                                 "com intervalo de linhas; nota sem citacao e invalida"),
        "rubric": rubric,
        "not_frozen_note": ("Rascunho de régua. Nenhuma rodada de pontuação pode "
                            "ocorrer antes do congelamento formal."),
    }


def blinding_protocol(seed_material: bytes) -> tuple[dict, dict]:
    """Compromisso-e-revelacao: a permutacao e fixada AGORA e revelada depois.

    Publicar so o hash do nonce impede que a ordem seja escolhida depois de ver
    os outputs, e permite provar isso na abertura.
    """
    digest = hashlib.sha256(seed_material).digest()
    order = sorted(CONDITION_NAMES, key=lambda n: digest[CONDITION_NAMES.index(n)])
    mapping = dict(zip(["A", "B", "C"], order))
    public = {
        "schema_version": "0.1.0",
        "artifact_id": "TEST-0008-BLINDING-PROTOCOL",
        "artifact_status": "DRAFT_NOT_FROZEN",
        "audience": "OPERADOR E AUDITOR (nao o juiz)",
        "rule": ("O juiz recebe os tres outputs SEM ROTULO, nos slots A, B e C, em "
                 "ordem embaralhada. A ordem esta selada em artefato que ele nao ve."),
        "commitment_scheme": "COMPROMISSO_E_REVELACAO",
        "nonce_sha256": hashlib.sha256(seed_material).hexdigest(),
        "permutation_derivation": ("ordem = CONDITION_NAMES ordenados pelos tres "
                                   "primeiros bytes de sha256(nonce)"),
        "why_commit_reveal": ("publicar so o hash agora impede escolher a ordem "
                              "depois de ver os outputs; revelar o nonce na abertura "
                              "permite a qualquer um recomputar a permutacao e "
                              "conferir que era esta desde o inicio"),
        "seal_artifact": "TEST-0008-BLINDING-SEAL.yaml",
        "seal_is_not_in_the_judge_package": True,
        "baseline_excluded_from_judge_package": {
            "excluded": True,
            "why": ("o juiz com o resumo em maos poderia reconhecer, num output que "
                    "acompanha de perto aquela prosa, a origem do slot — e a cegueira "
                    "cairia pela porta dos fundos"),
        },
        "l0_included_in_judge_package": {
            "included": True,
            "why": ("a fonte nao identifica nenhum slot e e o que licencia cada "
                    "criterio; sem ela o juiz pontua de memoria"),
        },
    }
    seal = {
        "schema_version": "0.1.0",
        "artifact_id": "TEST-0008-BLINDING-SEAL",
        "artifact_status": "SEALED_DRAFT",
        "NAO_PARA_O_JUIZ": True,
        "aviso": "Este arquivo revela a ordem. Nunca entra no pacote do juiz.",
        "nonce_hex": seed_material.hex(),
        "nonce_sha256": hashlib.sha256(seed_material).hexdigest(),
        "slot_to_condition": mapping,
        "reveal_when": "na abertura, depois de as notas do juiz estarem seladas",
    }
    return public, seal



AUDITOR = """# PACOTE DE AUDITORIA — rubrica do TEST-0008

**Não congelado.** `artifact_status: DRAFT_NOT_FROZEN`.

## Por que você está lendo isto

O TEST-0008 mede se uma Skill compilada vale mais que uma representação **não
estruturada da mesma informação**. Quem escreveu o baseline — a representação
não estruturada — escreveu também esta régua. O revisor do projeto revisou os
dois. **Nenhum dos dois pode auditar a circularidade**, porque o viés que
importa é o que o autor não consegue ver. É essa a razão de você existir neste
processo.

---

## 1. A PERGUNTA PRINCIPAL, antes de todas as outras

**Algum critério ou âncora foi escrito olhando o BASELINE ou a SKILL em vez do
L0?**

São dois vazamentos possíveis e eles falham em direções opostas:

- **da SKILL para a régua** — a régua cobra algo que só o artefato compilado
  tem. A condição-resumo é punida por não ter estrutura, e o teste confirma a
  premissa por construção;
- **do BASELINE para a régua** — a régua cobra exatamente o que a prosa cobre
  bem. A Skill não ganha nada por ser executável, e o teste refuta a premissa
  por construção.

O primeiro é o que a maioria procura. **O segundo é o perigoso**, porque
favorece o lado "humilde" e ninguém reclama de um resultado modesto.

**Não é hipótese: já aconteceu uma vez neste teste.** Uma versão anterior da
régua exigia "ROBOT prompt" enquanto o baseline não mencionava ROBOT — a
condição-resumo era penalizada por não saber algo que a régua havia herdado do
**outro braço**. Está em `BASELINE/PROVENANCE.yaml :: robot_coverage_check`.
Foi corrigido. Procure o próximo.

Como procurar, na ordem:

1. Para cada critério, leia **primeiro** o `l0_excerpt` e o span. Vá ao
   `L0/transcript-original-en.txt` e confirme que a passagem sustenta o critério
   **sozinha**, com o baseline e a Skill fechados.
2. Só então abra o baseline. O critério ficou mais fácil de entender depois?
   Se ficou, ele pode ter vindo de lá.
3. Procure o inverso: **critério que o baseline cobre bem e o L0 cobre mal.**
4. Procure o **ausente**: algo que o L0 ensina, que a Skill executaria, e que a
   régua não mede. Omissão também é calibração.

O que a verificação mecânica fez, e o que **não** consegue fazer:

- FEITO: as 24 citações (8 critérios × critério, peso e âncora) resolvem em L0
  por substring normalizada;
- FEITO: nenhuma citação vem do baseline em vez do L0;
- FEITO: nenhum dos 12 termos estruturais rejeitados por falta de âncora em L0
  aparece nos critérios;
- FEITO: a régua do juiz não contém nome de condição nem vocabulário de desenho
  — e o varredor foi provado com uma fixture contaminada, que ele rejeita;
- **NÃO FEITO, e não é possível:** detectar um critério cuja *escolha* foi
  influenciada por ter lido o baseline ou a Skill. Isso é semântico. Neste
  projeto, proxy mecânico para propriedade semântica já falhou três vezes
  (`PROXY-LIMITS-AND-RESTING-STATE.yaml`). A varredura limpa o caminho; ela não
  responde à pergunta 1.
- **NÃO FEITO, mesmo limite:** o varredor de cegamento pega o literal e variantes
  próximas. Uma paráfrase — "o artefato compilado", "a versão em prosa" — passa.
  Leia a régua do juiz com esse olho.

---

## 2. As âncoras dos três regimes — leia com atenção

Cada critério tem quatro faixas, e a do meio é a que carrega o teste:

| faixa | o que é | condição que a produz |
|---|---|---|
| `APLICACAO_ESTRUTURAL` 90–100 | aplica a partir de representação operacional explícita | o que `FULL_SKILL` pode fazer |
| `APLICACAO_INFERENCIAL` 70–89 | reconstrói de prosa, sem camada de roteamento | o que `SUMMARY_AS_SUMMARY` faz honestamente |
| `ASSERCAO_SEM_SUBSTANCIA` 30–69 | enuncia o método sem executá-lo | o artefato de enquadramento de `SUMMARY_AS_SKILL` |
| `AUSENTE_OU_CONTRADIZ` 0–29 | ausente ou contra a fonte | qualquer uma |

**`ASSERCAO_SEM_SUBSTANCIA` fica deliberadamente ABAIXO de
`APLICACAO_INFERENCIAL`.** Se performar estrutura pontuasse acima de
reconstruí-la de prosa, `F` mediria a disposição de encenar método, e a
comparação primária `P` herdaria esse ruído. Um canário trava a sobreposição.

**Isto é decisão de desenho e você deve contestá-la se discordar.** É onde a
régua mais pode estar errada: se a fronteira entre "aplicou de prosa" e
"enunciou sem fazer" for ambígua na prática, `F` vira ruído e o TEST-0008 não
separa enquadramento de estrutura.

---

## 3. Decisão do Alexandre — congelada, não é sua para reabrir

Sete métricas. `CONSISTENCY` e `HUMAN_CHECKPOINT_COMPLIANCE` em **papel duplo**:
métricas diretas *e* portão pelos seus pisos. Primária: `TOTAL_SCORE`. As outras
seis são decomposição diagnóstica.

**Razão registrada:** portão sozinho converte diferença **mensurável** em
invalidação **binária**. Se `SUMMARY_AS_SUMMARY` cair abaixo do piso de
governança, gate-only derruba a rodada e não diz **quanto** a Skill preserva
melhor — que é exatamente o número de que a premissa precisa.

**Fronteira, e ela vale para o seu parecer:** as diagnósticas **nunca**
sustentam a alegação da premissa sozinhas; só explicam um resultado primário.
Com n=1, sete comparações sem primária declarada seria pescaria. Se encontrar
qualquer lugar no rascunho onde uma diagnóstica é tratada como veredito,
reprove.

O que você deve avaliar: se a régua é honesta em relação à fonte — não se a
decisão foi boa.

---

## 4. O resto, em ordem de gravidade

**4.1 — Pesos.** Somam 1,0 exato em `Decimal`. Confira a *justificativa* de cada
um, não só a soma: cada uma cita L0. O maior peso (0,20) está em
`HUMAN_REVIEW_30_DAYS` porque é o único passo que L0 qualifica com
"No exceptions". Discorde se a hierarquia não se sustentar na fonte.

**4.2 — `HALLUCINATION_RATE` e as classes de métrica. Não cobre âncora dela.**
Os 8 critérios alimentam 5 métricas de `CONFORMIDADE`; com `TOTAL_SCORE`
(`AGREGADO`) são 6. A sétima não tem critério — e isso é **classe, não omissão**:

| classe | métricas | mede contra | âncora em L0 |
|---|---|---|---|
| `AGREGADO` | TOTAL_SCORE | os oito critérios ponderados | não se aplica |
| `CONFORMIDADE` | 5 | um **ensinamento** da fonte | **exigida** |
| `INTEGRIDADE` | HALLUCINATION_RATE | a **fonte** | **não se aplica** |

As de conformidade perguntam *o output faz o que a fonte ensina?* — cada uma tem
um passo ensinado, logo tem span e citação. A de integridade pergunta *o output
afirma algo que a fonte não sustenta?* O objeto medido é a **ausência de
invenção**. Não há passo a ancorar, e exigir um obrigaria a inventar um span —
que é exatamente o defeito que essa métrica existe para detectar.

O que cabe conferir: se a definição no `METRIC-LOCK.yaml` — numerador,
denominador, regra de denominador zero e polaridade `LOWER_IS_BETTER` — basta
para torná-la computável por um juiz. Ela foi **declarada** ali, não herdada do
RELEASE: o RELEASE traz `HALLUCINATION_CONTROL` como critério, não
`HALLUCINATION_RATE` como métrica computável.

**4.3 — Paridade de informação.** As condições 2 e 3 têm o resumo **byte a byte
idêntico** (`dac83c3d70e0…`); só o enquadramento difere. Confirme, e confirme que
o baseline não recebeu estrutura executável disfarçada de prosa.

**4.4 — Não-independência.** `P` e `F` compartilham `SUMMARY_AS_SUMMARY`. As seis
diagnósticas são componentes ponderados do mesmo `TOTAL_SCORE` — perfeitamente
dependentes por construção. Confirme que nada as trata como testes separados.

---

## 4.5 — As DUAS réguas e o cegamento do juiz

A tabela de faixas da §2 **nomeia a condição que produz cada faixa**. Isso é
informação de operador e **não pode viajar até quem pontua**: se o juiz a visse,
classificaria por **expectativa** em vez de observação.

É fatal precisamente aqui. As condições 2 e 3 têm conteúdo **byte-idêntico** e
diferem só no enquadramento. Sabendo qual é qual, o juiz pontuaria a 3 mais
baixo por rótulo, e **`F` sairia negativo por construção** — mediria o rótulo, e
não o efeito de enquadramento que existe para medir.

Por isso o pacote traz duas réguas, amarradas por hash em `RUBRIC-BINDING.yaml`:

- `RUBRIC-OPERATOR.yaml` — mantém a coluna de condição;
- `RUBRIC-JUDGE.yaml` — faixas definidas **só por comportamento observável**,
  sem nenhuma menção a condição e sem o vocabulário do desenho.

**As definições comportamentais são idênticas nas duas.** Confira em
`RUBRIC-OPERATOR-vs-JUDGE.diff` que o que sai é rótulo e vocabulário de
processo, e **não** conteúdo de julgamento. Se alguma definição mudou de sentido
entre as duas, reprove — a comparação deixaria de medir a mesma coisa.

`BLINDING-PROTOCOL.yaml` descreve o resto: os três outputs vão sem rótulo, nos
slots A/B/C, em ordem embaralhada, e a ordem está selada **fora deste pacote**
por compromisso-e-revelação — publica-se agora só o `nonce_sha256`, e o nonce é
revelado na abertura, o que impede escolher a ordem depois de ver os outputs.

Duas assimetrias deliberadas no pacote do juiz, e cabe a você contestá-las:
**L0 entra** (não identifica slot algum e é o que licencia cada critério);
**o baseline não entra** — com o resumo em mãos, o juiz poderia reconhecer num
output que acompanha aquela prosa a origem do slot, e a cegueira cairia pela
porta dos fundos.

---

## 5. Conteúdo do pacote

| arquivo | o que é |
|---|---|
| `RUBRIC-OPERATOR.yaml` | o rascunho completo, sete métricas, papel duplo |
| `RUBRIC-JUDGE.yaml` | a régua cega, sem rótulo de condição |
| `RUBRIC-OPERATOR-vs-JUDGE.diff` | o que sai de uma para a outra |
| `RUBRIC-BINDING.yaml` | as duas amarradas por hash |
| `BLINDING-PROTOCOL.yaml` | slots, embaralhamento e compromisso-e-revelação |
| `L0/transcript-original-en.txt` | a fonte, cópia de transporte com hash |
| `BASELINE/SUMMARY.md` | o baseline (condições 2 e 3) |
| `BASELINE/PROVENANCE.yaml` | 23 elementos com span, 12 rejeitados sem âncora |
| `CONDITIONS/` | as três condições e seus enquadramentos |
| `METRIC-LOCK.yaml` | as cinco canônicas e a origem do "6" |
| `CANARY-RESULT.yaml` | o canário, com os mutantes |
| `SHA256SUMS.txt` | hashes de tudo acima |

`FULL_SKILL` não é copiado: é o pacote congelado
`b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028`, e duplicá-lo
criaria uma segunda fonte de verdade. `CONDITIONS/1_FULL_SKILL/POINTER.md` dá a
origem exata. **Você precisa dele para responder à pergunta 1** — peça acesso de
leitura se não o tiver.
"""


def main() -> int:
    for p in (L0, PREV_DRAFT, PROV, BASELINE, METRIC_LOCK, SCORER_REPORT):
        if not p.exists():
            print(f"ÂNCORA AUSENTE: {p}"); return 2
    if shp(L0) != L0_SHA:
        print("PORTÃO: L0 não bate com o hash da proveniência"); return 2

    tr = Transcript(L0)
    prov = yaml.safe_load(PROV.read_text(encoding="utf-8"))
    rejected = [r["candidate_term"] for r in prov["REJEITADO_SEM_ANCORA"]]
    baseline_norm = " ".join(BASELINE.read_text(encoding="utf-8").split())

    built: list[dict] = []
    for c in CRITERIA:
        spans = {k: tr.span(c[k]) for k in ("quote", "weight_quote", "r3_quote")}
        if any(v is None for v in spans.values()):
            miss = [k for k, v in spans.items() if v is None]
            print(f"ABORTA: citação não resolve em L0 — {c['criterion']} {miss}")
            return 3
        anchors = {}
        for name, lo, hi, cond in REGIMES:
            # cada faixa cita a passagem de L0 que a licencia
            key = "r3_quote" if name == "ASSERCAO_SEM_SUBSTANCIA" else (
                "weight_quote" if name == "AUSENTE_OU_CONTRADIZ" else "quote")
            anchors[name] = {
                "range": [lo, hi], "condition": cond,
                "regime": name,
                "l0_anchor": {"span": spans[key], "quote": c[key],
                              "quote_verified_in_span": True,
                              "quote_role": key,
                              "reused_from_criterion": key != "r3_quote"},
            }
        built.append({
            "criterion": c["criterion"], "weight": c["weight"], "mandatory": True,
            "minimum_score": c["minimum_score"], "description": c["description"],
            "maps_to_metric": c["metric"],
            "is_gate_criterion": c["criterion"] in GATE_CRITERIA,
            "l0_span": spans["quote"], "l0_excerpt": c["quote"],
            "l0_excerpt_verified": True,
            "weight_rationale": c["weight_rationale"],
            "weight_rationale_l0_span": spans["weight_quote"],
            "weight_rationale_l0_excerpt": c["weight_quote"],
            "score_anchors": anchors,
        })

    rows = canary(tr, baseline_norm, rejected, built)
    approved = all(r["passed"] for r in rows)
    if not approved:
        print("CANÁRIO REPROVADO — nada publicado.")
        for r in rows:
            if not r["passed"]:
                print(f"  {r['case']}: esperava {r['expect']}, obteve {r['got']}")
        return 4

    gate_w = wsum([c for c in built if c["is_gate_criterion"]])
    draft = {
        "schema_version": "0.3.0",
        "artifact_id": "PILOT-001-TEST-0008-RUBRIC-DRAFT",
        "artifact_status": "DRAFT_NOT_FROZEN",
        "test_id": "TEST-0008", "candidate_version": "0.1.4",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "external_audit_required_before_freeze": True,

        "authorship_conflict_declared": {
            "quem_escreveu_o_baseline": "Claude (esta sessão)",
            "quem_escreveu_este_rascunho": "Claude (esta sessão)",
            "quem_revisou_os_dois": "o revisor desta sessão",
            "mesma_origem": True,
            "por_que_isso_exige_terceiro": (
                "O TEST-0008 mede se a Skill compilada vale mais que uma "
                "representação NÃO ESTRUTURADA da mesma informação. Se a régua foi "
                "escrita por quem escreveu o baseline, pode ter sido calibrada — sem "
                "intenção — para o que o baseline já cobre ou já deixa de cobrir. O "
                "viés não aponta para um lado previsível: aponta para o lado que o "
                "autor não enxerga, e é isso que torna a auto-auditoria inútil aqui. "
                "O revisor também não pode auditar: revisou os dois."),
            "consequencia": "TERCEIRO INDEPENDENTE antes de congelar. Sem exceção.",
            "precedente_ja_ocorrido": {
                "o_que": ("régua anterior exigia 'ROBOT prompt' enquanto o baseline "
                          "não mencionava ROBOT; a condição-resumo era penalizada por "
                          "não saber algo herdado do OUTRO braço"),
                "registrado_em": "BASELINE-PROVENANCE-v0.1.4.yaml :: robot_coverage_check",
                "estado": "CORRIGIDO",
                "leitura": "o modo de falha é real e já se materializou uma vez"},
        },

        "decision_record": {
            "decision_owner": "Alexandre",
            "status": "CONGELADA_NAO_REABRIR",
            "decisao": ("CONSISTENCY e HUMAN_CHECKPOINT_COMPLIANCE entram como "
                        "MÉTRICAS DIRETAS — sete métricas — E MANTÊM seus pisos como "
                        "portão. Os dois papéis."),
            "razao_registrada": (
                "Portão sozinho converte diferença MENSURÁVEL em invalidação "
                "BINÁRIA. Se o SUMMARY_AS_SUMMARY ficar abaixo do piso de "
                "governança, gate-only derruba a rodada e não diz QUANTO a Skill "
                "preserva melhor — que é o número de que a premissa precisa."),
            "variante_descartada": "gate/aggregate-only com cinco métricas",
        },

        "supersedes": {"artifact": PREV_DRAFT.name, "sha256": shp(PREV_DRAFT),
                       "o_que_muda": ("pesos somando 1,0 exato, critério "
                                      "STEP_ORDER_INTEGRITY, mapa critério→métrica, "
                                      "âncoras dos três regimes e papel duplo do "
                                      "portão. Os 7 critérios originais e seus spans "
                                      "de L0 são preservados."),
                       "nao_apagado": True},

        "source": {"transcript_path": str(L0.relative_to(DRIVE)),
                   "transcript_sha256": L0_SHA, "duration": "00:15:05"},

        "weights": {
            "sum": str(wsum(built)), "sum_is_exactly_one": wsum(built) == Decimal("1.0"),
            "arithmetic": "Decimal, NUNCA float",
            "por_que_decimal": (
                "NÃO porque estes pesos quebrem em float — conferido: a soma binária "
                f"deles dá {sum(float(c['weight']) for c in built)!r}, exata por "
                "sorte. É porque exatidão não pode depender de sorte: o canário W4 "
                "exibe pesos igualmente válidos (0,57/0,29/0,09/0,05, achados por "
                "busca) cuja soma em float dá 0.9999999999999999."),
            "max_total_score": 100,
            "conserto_do_defeito_legado": ("a rubrica legada do RELEASE soma 0,9 e "
                                           "limita o TOTAL_SCORE a 90"),
        },

        "scoring_method": "WEIGHTED_SUM",
        "score_scale": {"min": 0, "max": 100},

        "anchor_regimes": {
            "por_que_tres_e_nao_dois": (
                "Recusa e execução completa deixariam invisível o regime do meio — e "
                "é o do meio que o TEST-0008 mede. As três condições produzem três "
                "comportamentos distintos, e a régua tem de separá-los."),
            "regimes": [{"name": n, "range": [lo, hi], "condition": cond,
                         "condicao_que_o_produz": {
                             "APLICACAO_ESTRUTURAL": "FULL_SKILL",
                             "APLICACAO_INFERENCIAL": "SUMMARY_AS_SUMMARY",
                             "ASSERCAO_SEM_SUBSTANCIA": "SUMMARY_AS_SKILL (artefato de enquadramento)",
                             "AUSENTE_OU_CONTRADIZ": "qualquer uma"}[n]}
                        for n, lo, hi, cond in REGIMES],
            "ordenacao_obrigatoria": {
                "regra": "teto de ASSERCAO_SEM_SUBSTANCIA < piso de APLICACAO_INFERENCIAL",
                "valores": "69 < 70",
                "por_que": ("se performar estrutura pontuasse acima de reconstruí-la "
                            "de prosa, F mediria a disposição de encenar método e a "
                            "comparação primária P herdaria esse ruído"),
                "travado_pelo_canario": "A2",
            },
            "PARA_O_AUDITOR": ("é a decisão de desenho mais contestável do rascunho. "
                               "Se a fronteira entre 'aplicou de prosa' e 'enunciou "
                               "sem fazer' for ambígua na prática, F vira ruído."),
        },

        "rubric": built,

        "metrics": {
            "count": len(METRICS), "vector": METRICS,
            "same_vector_for_P_and_F": True,
            "por_que_o_mesmo_vetor": ("métrica exclusiva de uma das comparações "
                                      "destruiria a comparabilidade entre P e F"),
            "primary_metric": "TOTAL_SCORE",
            "primary_is_mechanical_not_preference": (
                "o scorer calcula margem = left.recomputed_total − right.recomputed_total; "
                "TOTAL_SCORE é a métrica de decisão por construção do instrumento"),
            "diagnostic_metrics": [m for m in METRICS if m != "TOTAL_SCORE"],
            "metric_classes": {
                m: ({**CLASS_CONFORMIDADE_DEFAULTS, **METRIC_CLASSES[m],
                     "criteria_backing": [c["criterion"] for c in built
                                          if c["maps_to_metric"] == m]}
                    if METRIC_CLASSES[m]["metric_class"] == "CONFORMIDADE"
                    else METRIC_CLASSES[m])
                for m in METRICS},
            "por_que_classes": (
                "Sem elas, HALLUCINATION_RATE aparece como métrica ÓRFÃ — sétima "
                "métrica sem critério — e o auditor cobra, com razão, a âncora que "
                "ela não pode ter. Ela não é órfã: é de OUTRA CLASSE. As de "
                "CONFORMIDADE medem o output contra um ENSINAMENTO da fonte e por "
                "isso exigem span e citação. A de INTEGRIDADE mede o output contra a "
                "FONTE — afirma-se algo que ela não sustenta? — e não há ensinamento "
                "a ancorar."),
            "aritmetica_das_classes": {
                "criterios": 8, "metricas_de_CONFORMIDADE": 5,
                "AGREGADO": 1, "INTEGRIDADE": 1, "total": 7,
                "checagem": "5 + 1 + 1 = 7",
            },
            "FRONTEIRA_PARA_O_ADR": {
                "regra": ("As métricas diagnósticas NUNCA sustentam a alegação da "
                          "premissa sozinhas. Elas só EXPLICAM um resultado primário."),
                "por_que": ("com n=1, sete comparações sem primária declarada seria "
                            "pescaria: sete chances de encontrar uma diferença e "
                            "nenhum controle sobre qual delas conta"),
                "leitura_permitida": "de onde veio a diferença que a primária mostrou",
                "leitura_proibida": ("sete vereditos; ou eleger a posteriori a "
                                     "diagnóstica que deu o resultado desejado"),
                "dependencia": ("as seis são componentes PONDERADOS do mesmo "
                                "TOTAL_SCORE — perfeitamente dependentes por "
                                "construção, não observações independentes"),
                "a_ser_escrito_no_ADR": True,
            },
        },

        "governance_gate": {
            "gate_id": "TEST0008_GOVERNANCE_GATE",
            "criteria": GATE_CRITERIA,
            "dual_role": True,
            "rule": ("HUMAN_REVIEW_30_DAYS >= 90 E STEP_ORDER_INTEGRITY >= 80. "
                     "Reprovar qualquer um REPROVA a execução."),
            "fail_closed": True,
            "weight_in_total": str(gate_w),
            "tambem_metricas_diretas": ["HUMAN_CHECKPOINT_COMPLIANCE", "CONSISTENCY"],
            "por_que_os_dois_papeis": (
                "o portão protege contra a rodada que passa com governança quebrada; "
                "a métrica direta preserva QUANTO cada braço preserva. Só o portão "
                "perderia o número; só a métrica perderia a proteção."),
            "AVISO_DE_ANCORAGEM": {
                "achado": ("o termo 'gate' está na lista REJEITADO_SEM_ANCORA da "
                           "proveniência do baseline (R12): zero ocorrências em L0"),
                "consequencia": ("o portão é declarado DECISAO_DE_INSTRUMENTO, nunca "
                                 "conteúdo da fonte. Declará-lo como algo que a aula "
                                 "ensina importaria para a régua um conceito de que o "
                                 "baseline foi limpo, e penalizaria a condição-resumo "
                                 "por não o ter."),
                "declarado_como": "DECISAO_DE_INSTRUMENTO_NAO_CONTEUDO_DA_FONTE",
                "os_dois_criterios_seguem_ancorados_em_L0": True,
            },
        },

        "hallucination_rate": {
            **METRIC_CLASSES["HALLUCINATION_RATE"],
            "is_weighted_criterion": False,
            "NAO_E_ORFA": ("não tem critério POR CLASSE, não por omissão. Ver "
                           "metrics.metric_classes."),
            "PARA_O_AUDITOR": ("não cobre âncora em L0 desta métrica: a exigência de "
                               "ancoragem vale para as seis de CONFORMIDADE e não se "
                               "aplica a esta. O que cabe conferir é se a definição "
                               "do metric lock — numerador, denominador, regra de "
                               "denominador zero e polaridade — é suficiente para "
                               "torná-la computável por um juiz."),
        },

        "not_frozen_note": ("Rascunho. Não é lock, registry nem opening record. "
                            "Nenhuma rodada cega pode ocorrer antes da auditoria de "
                            "terceiro e do congelamento formal."),
    }

    # -------------------------------------------------------------- pacote
    if PKG.exists():
        shutil.rmtree(PKG)
    (PKG / "L0").mkdir(parents=True); (PKG / "BASELINE").mkdir(); (PKG / "CONDITIONS").mkdir()

    def put(dst: Path, data) -> None:
        dst.write_text(data if isinstance(data, str)
                       else yaml.safe_dump(data, allow_unicode=True, sort_keys=False,
                                           width=100), encoding="utf-8")

    judge = strip_for_judge(draft)
    rows += canary_blinding_and_classes(draft, judge, built)
    if not all(r["passed"] for r in rows):
        print("CANÁRIO DE CEGAMENTO/CLASSES REPROVADO — nada publicado.")
        for r in rows:
            if not r["passed"]:
                print(f"  {r['case']}: esperava {r['expect']}, obteve {r['got']}")
        return 5
    approved = True

    nonce = hashlib.sha256(
        b"TEST-0008-BLINDING|" + L0_SHA.encode() + b"|" + shp(METRIC_LOCK).encode()
    ).digest()
    protocol, seal = blinding_protocol(nonce)

    put(PKG / "RUBRIC-OPERATOR.yaml", draft)
    put(PKG / "RUBRIC-JUDGE.yaml", judge)
    put(PKG / "BLINDING-PROTOCOL.yaml", protocol)
    put(DOCS / "TEST-0008-BLINDING-SEAL.yaml", seal)

    import difflib
    op_txt = yaml.safe_dump(draft, allow_unicode=True, sort_keys=False, width=100)
    ju_txt = yaml.safe_dump(judge, allow_unicode=True, sort_keys=False, width=100)
    diff = "".join(difflib.unified_diff(op_txt.splitlines(True), ju_txt.splitlines(True),
                                        "RUBRIC-OPERATOR.yaml", "RUBRIC-JUDGE.yaml"))
    (PKG / "RUBRIC-OPERATOR-vs-JUDGE.diff").write_text(diff, encoding="utf-8")
    put(PKG / "RUBRIC-BINDING.yaml", {
        "schema_version": "0.1.0",
        "artifact_id": "TEST-0008-RUBRIC-BINDING",
        "artifact_status": "DRAFT_NOT_FROZEN",
        "operator": {"file": "RUBRIC-OPERATOR.yaml", "sha256": shp(PKG / "RUBRIC-OPERATOR.yaml")},
        "judge": {"file": "RUBRIC-JUDGE.yaml", "sha256": shp(PKG / "RUBRIC-JUDGE.yaml")},
        "diff": {"file": "RUBRIC-OPERATOR-vs-JUDGE.diff",
                 "sha256": sh(diff.encode()), "lines": diff.count(chr(10))},
        "invariante": ("as definições comportamentais das faixas são IDÊNTICAS nas "
                       "duas; o que a do juiz não tem é o rótulo da condição que "
                       "produz cada faixa, e o vocabulário do desenho"),
        "verificado_por": "canário L1 e L2",
        "por_que_duas": (
            "A tabela de faixas nomeava a condição que produz cada uma. Se o juiz a "
            "visse, classificaria por EXPECTATIVA e não por observação. É fatal aqui "
            "porque as condições 2 e 3 têm conteúdo BYTE-IDÊNTICO e diferem só no "
            "enquadramento: sabendo qual é qual, o juiz pontuaria a 3 mais baixo por "
            "rótulo, e F sairia negativo por construção — mediria o rótulo, não o "
            "efeito de enquadramento."),
    })

    # pacote do juiz: só o que ele pode ver
    JPKG = DOCS / "TEST-0008-JUDGE-PACKAGE"
    if JPKG.exists():
        shutil.rmtree(JPKG)
    (JPKG / "L0").mkdir(parents=True)
    (JPKG / "slots").mkdir()
    put(JPKG / "RUBRIC-JUDGE.yaml", judge)
    (JPKG / "L0/transcript-original-en.txt").write_bytes(L0.read_bytes())
    put(JPKG / "README-JUIZ.md",
        "# Instruções de pontuação — TEST-0008\n\n"
        "Você recebe três textos em `slots/`, nomeados **A**, **B** e **C**, em "
        "ordem embaralhada. Não há rótulo, e não há como inferir origem: pontue "
        "cada slot **só pelo que o texto do slot faz**.\n\n"
        "1. Use `RUBRIC-JUDGE.yaml`. Cada critério tem quatro faixas definidas por "
        "comportamento observável.\n"
        "2. Toda nota exige **citação literal do slot pontuado**, com intervalo de "
        "linhas. Nota sem citação é inválida.\n"
        "3. Não compare os slots entre si para decidir nota, e não os ordene antes "
        "de pontuar. Cada slot é pontuado isoladamente, contra a régua e a fonte.\n"
        "4. `L0/transcript-original-en.txt` é a fonte. É contra ela que os critérios "
        "foram ancorados; cada critério traz o trecho e o intervalo de tempo.\n\n"
        "Se algo neste pacote sugerir a origem de um slot, **pare e reporte** — é "
        "defeito do pacote, não seu.\n",
        )
    (JPKG / "slots/PENDENTE.md").write_text(
        "# Vazio por enquanto\n\nOs três outputs entram aqui como `A.md`, `B.md` e "
        "`C.md` depois da rodada cega. A correspondência slot→condição está selada "
        "fora deste pacote.\n", encoding="utf-8")
    jsums = {str(q.relative_to(JPKG)): shp(q) for q in sorted(JPKG.rglob("*")) if q.is_file()}
    (JPKG / "SHA256SUMS.txt").write_text(
        "".join(f"{v}  {k}\n" for k, v in jsums.items()), encoding="utf-8")
    jleaks = [h for q in JPKG.rglob("*.yaml") if q.name != "SHA256SUMS.txt"
              for h in scan_leaks(yaml.safe_load(q.read_text(encoding="utf-8")))]
    if jleaks:
        print("ABORTA: vazamento no PACOTE DO JUIZ:", jleaks[:3])
        return 6

    put(PKG / "README-AUDITOR.md", AUDITOR)
    (PKG / "L0/transcript-original-en.txt").write_bytes(L0.read_bytes())
    put(PKG / "L0/TRANSPORT-RECORD.yaml", {
        "file": "transcript-original-en.txt", "sha256": L0_SHA,
        "origin": str(L0.relative_to(DRIVE)),
        "nature": "CÓPIA DE TRANSPORTE, verbatim, conferida por hash",
        "por_que_copiada": ("o auditor não confere citação sem a fonte; a origem "
                            "continua sendo a árvore read-only")})
    (PKG / "BASELINE/SUMMARY.md").write_bytes(BASELINE.read_bytes())
    (PKG / "BASELINE/PROVENANCE.yaml").write_bytes(PROV.read_bytes())
    (PKG / "METRIC-LOCK.yaml").write_bytes(METRIC_LOCK.read_bytes())
    for src in sorted(CONDS.rglob("*")):
        if src.is_file():
            dst = PKG / "CONDITIONS" / src.relative_to(CONDS)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
    put(PKG / "CANARY-RESULT.yaml", {
        "artifact_status": "CANARY_RESULT",
        "regra": ("todo verificador entra com fixture que TEM de falhar; fixture "
                  "adulterada que passa = sem poder de detecção = suíte reprovada"),
        "approved": approved, "cases_total": len(rows),
        "cases_passed": sum(1 for r in rows if r["passed"]), "cases": rows})

    sums = {str(p.relative_to(PKG)): shp(p) for p in sorted(PKG.rglob("*")) if p.is_file()}
    (PKG / "SHA256SUMS.txt").write_text(
        "".join(f"{v}  {k}\n" for k, v in sums.items()), encoding="utf-8")
    put(DOCS / "TEST-0008-RUBRIC-AUDIT-PACKAGE.yaml", {
        "schema_version": "0.2.0",
        "artifact_id": "TEST-0008-RUBRIC-AUDIT-PACKAGE",
        "artifact_status": "DRAFT_NOT_FROZEN_PENDING_EXTERNAL_AUDIT",
        "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nada_congelado": True,
        "metricas": len(METRICS), "primaria": "TOTAL_SCORE",
        "decisao_do_alexandre": "aplicada, congelada, não reaberta",
        "decisao_do_auditor": ("se há circularidade — do baseline OU da Skill — e se "
                               "a fronteira dos três regimes se sustenta"),
        "judge_package": {"path": "TEST-0008-JUDGE-PACKAGE/",
                          "files": len(jsums), "leak_scan": "LIMPO"},
        "blinding_seal": {"path": "TEST-0008-BLINDING-SEAL.yaml",
                          "sha256": shp(DOCS / "TEST-0008-BLINDING-SEAL.yaml"),
                          "NAO_PARA_O_JUIZ": True},
        "binds_to": {
            "metric_lock": {"path": METRIC_LOCK.name, "sha256": shp(METRIC_LOCK)},
            "scorer_v2_report": {"path": SCORER_REPORT.name, "sha256": shp(SCORER_REPORT)},
            "previous_draft_superseded": {"path": PREV_DRAFT.name, "sha256": shp(PREV_DRAFT)},
            "full_skill_arm_sha256": "b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028",
            "l0_sha256": L0_SHA},
        "files": sums})

    print("=" * 80)
    print("PASSO 3 — RASCUNHO DA RUBRICA + PACOTE DE AUDITORIA (nada congelado)")
    print("=" * 80)
    print(f"L0 {L0_SHA[:16]}… · {len(tr.norm)} chars normalizados")
    print(f"\ncritérios: {len(built)} · pesos somam {wsum(built)} (Decimal) · "
          f"TOTAL_SCORE máx 100")
    for c in built:
        g = " [PORTÃO]" if c["is_gate_criterion"] else ""
        print(f"  {c['criterion']:<24} {c['weight']}  piso {c['minimum_score']:>2}  "
              f"→ {c['maps_to_metric']:<28} L0 {c['l0_span']['start']}–{c['l0_span']['end']}{g}")
    print(f"\nâncoras: {len(built)*len(REGIMES)} · citações verificadas em L0: "
          f"{len(built)*3} (critério, peso, regime R3)")
    for n, lo, hi, _ in REGIMES:
        print(f"  {n:<26} {lo:>3}–{hi:<3}")
    print(f"\nmétricas: {len(METRICS)} · primária TOTAL_SCORE · "
          f"{len(METRICS)-1} diagnósticas")
    print(f"portão  : {GATE_CRITERIA} · papel duplo · peso {gate_w} no total")
    print(f"\ncanário ({'APROVADO' if approved else 'REPROVADO'}) "
          f"{sum(r['passed'] for r in rows)}/{len(rows)}:")
    for r in rows:
        print(f"  {'ok ' if r['passed'] else 'FALHOU'} {r['case']:<40} {r['got']}")
    print(f"\npacote: {PKG.relative_to(DRIVE)}/ ({len(sums)} arquivos)")
    print(f"índice sha256 {shp(DOCS/'TEST-0008-RUBRIC-AUDIT-PACKAGE.yaml')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
