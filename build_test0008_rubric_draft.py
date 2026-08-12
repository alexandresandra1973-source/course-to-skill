#!/usr/bin/env python3
"""PASSO 3 — rascunho da rubrica do TEST-0008, duas variantes, para auditoria.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/. NÃO congela nada.
Zero chamadas de modelo.

Continuidade: os 7 critérios ancorados em L0 vêm do rascunho anterior
(TEST-0008-RUBRIC-DRAFT-v0.1.4.yaml, a6c27d8268db06ee…), que não tinha pesos.
Este trabalho acrescenta pesos somando 1,0 exato, um oitavo critério para
CONSISTENCY, o mapa critério→métrica e as duas variantes. O rascunho anterior é
declarado SUPERSEDIDO por hash, não apagado.

REGRA DURA: toda citação tem de resolver em L0 por substring normalizada. Uma
que não resolva ABORTA a geração — não vira aviso.
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


def sh(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def shp(p: Path) -> str:
    return sh(p.read_bytes())


def fmt(s: int) -> str:
    return f"{s // 60}:{s % 60:02d}"


class Transcript:
    """L0 normalizado com mapa de posição -> marca temporal."""

    def __init__(self, path: Path) -> None:
        raw = path.read_text(encoding="utf-8")
        marks = [(m.start(), m.end(), int(m.group(1)) * 60 + int(m.group(2)))
                 for m in MARK.finditer(raw)]
        self.segments: list[tuple[int, int, int]] = []   # (norm_start, norm_end, seg_s)
        parts: list[str] = []
        pos = 0
        # texto antes da primeira marca fica ancorado em 0
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
        self.mark_times = [s for _, _, s in self.segments]

    def find(self, quote: str) -> tuple[int, int] | None:
        q = " ".join(quote.split())
        i = self.norm.find(q)
        if i < 0:
            return None
        return i, i + len(q)

    def span(self, quote: str) -> dict | None:
        loc = self.find(quote)
        if loc is None:
            return None
        a, b = loc
        start = next((s for x, y, s in self.segments if x <= a <= y), 0)
        end_seg_i = next((k for k, (x, y, s) in enumerate(self.segments) if x <= b <= y), None)
        if end_seg_i is None:
            end = self.mark_times[-1]
        elif end_seg_i + 1 < len(self.segments):
            end = self.segments[end_seg_i + 1][2]
        else:
            end = self.segments[end_seg_i][2]
        return {"source": "youtube:YkdAx2XjWDs", "start": fmt(start), "end": fmt(end),
                "start_s": start, "end_s": end}


# --------------------------------------------------------------- os critérios
# Peso: JUSTIFICADO EM L0, não por preferência. A justificativa de cada peso cita
# o que L0 diz sobre a importância daquele passo. Está pré-declarada aqui, antes
# de qualquer nota existir.
CRITERIA = [
    {"criterion": "OUTCOME_CONTRACT", "weight": "0.18",
     "metric": "DECISION_ACCURACY", "minimum_score": 80,
     "description": "Declara outcome, input, output e boundaries antes de escolher ferramenta.",
     "quote": "Step one, start with the outcome. Before you open anything, write down three things. What information you'll give, what output you want back, and clear boundaries.",
     "weight_rationale_quote": "You'll end up automating a task instead of owning an outcome.",
     "weight_rationale": "L0 nomeia partir da ferramenta como o erro mais comum; segundo maior peso."},
    {"criterion": "ROBOT_PROMPT_STRUCTURE", "weight": "0.12",
     "metric": "METHODOLOGY_FIDELITY", "minimum_score": 85,
     "description": "Escreve as instruções com role, objective, boundaries, output e tone.",
     "quote": "Structure your system prompt using this robot framework. role, objective, boundaries, output, tone. Every great agent prompt has all five.",
     "weight_rationale_quote": "Vague instructions equal vague output every time.",
     "weight_rationale": "L0 trata o system prompt como determinante da qualidade da saída."},
    {"criterion": "TOOL_SELECTION", "weight": "0.10",
     "metric": "DECISION_ACCURACY", "minimum_score": 80,
     "description": "Escolhe plataforma e conecta só as ferramentas que o outcome exige.",
     "quote": "Step three, choose your platform and connect the tools. This is where you choose what you're building in and what it's going to connect to.",
     "weight_rationale_quote": "The model matters less than you think.",
     "weight_rationale": "L0 relativiza a escolha de plataforma; peso deliberadamente menor."},
    {"criterion": "MEMORY_CONTEXT", "weight": "0.08",
     "metric": "EXECUTION_QUALITY", "minimum_score": 75,
     "description": "Alimenta o agente com contexto de negócio, não só instruções.",
     "quote": "Step four, feed it memory. This is what separates a generic bot from one that actually understands your business.",
     "weight_rationale_quote": "you give it context about who you are, who you serve, and what good looks like for you",
     "weight_rationale": "Passo presente em L0 e sem qualificador de criticidade; peso baixo."},
    {"criterion": "TESTING_ITERATION", "weight": "0.12",
     "metric": "EXECUTION_QUALITY", "minimum_score": 80,
     "description": "Roda de três a cinco vezes, registra falhas e volta ao prompt.",
     "quote": "Step five, test it, break it, fix it. Run it three to five times.",
     "weight_rationale_quote": "Go back to the system prompt and tighten it.",
     "weight_rationale": "L0 dá procedimento numérico explícito; passo verificável."},
    {"criterion": "HUMAN_REVIEW_30_DAYS", "weight": "0.20",
     "metric": "HUMAN_CHECKPOINT_COMPLIANCE", "minimum_score": 90,
     "description": "Mantém revisão humana de toda saída nos primeiros 30 dias.",
     "quote": "Step six, add a human in the loop for the first 30 days. Review every output before it goes anywhere.",
     "weight_rationale_quote": "Any agent that touches money, messaging, or the customer needs a review step in the first 30 days. No exceptions.",
     "weight_rationale": "MAIOR PESO: é o único passo que L0 qualifica com 'No exceptions'."},
    {"criterion": "MEASUREMENT", "weight": "0.08",
     "metric": "EXECUTION_QUALITY", "minimum_score": 75,
     "description": "Fecha com as duas perguntas de medição e a decisão de expandir ou refazer.",
     "quote": "In step seven, measure it with these two questions. Is it saving you at least 2 hours a week?",
     "weight_rationale_quote": "If both are yes, expand it. If either's a no, go back and rebuild it.",
     "weight_rationale": "Passo final, critério binário simples; peso baixo."},
    {"criterion": "STEP_ORDER_INTEGRITY", "weight": "0.12",
     "metric": "CONSISTENCY", "minimum_score": 80,
     "description": "Mantém a ordem dos passos e a precedência declarada entre opções.",
     "quote": "If any of the tools we just covered do what you need, start there. Open Claw is the one you reach for when you have a specific piece of software that nothing else can connect to.",
     "weight_rationale_quote": "But that's the wrong starting point.",
     "weight_rationale": "L0 trata a ORDEM como conteúdo, não como forma: começar no lugar errado é o erro nomeado."},
]

ANCHOR_LEVELS = [
    ("complete", 90, 100, "Presente, específico e no lugar certo da sequência."),
    ("partial", 60, 89, "Presente mas genérico, incompleto ou fora de ordem."),
    ("weak", 30, 59, "Mencionado de passagem, sem conteúdo operacional."),
    ("absent", 0, 29, "Ausente, ou contradiz o que a fonte estabelece."),
]

# HALLUCINATION_RATE não é critério ponderado. Ver `hallucination_rate` abaixo.


# ------------------------------------------------------------------- canário
def weight_sum(items, key="weight") -> Decimal:
    """Soma EXATA. Em binário, 0.18+0.12+0.10+0.08+0.12+0.20+0.08+0.12 != 1.0.

    Usar float aqui reprovaria a rubrica correta. É um erro de instrumento que
    parece um erro de rubrica, e por isso entra no canário como caso próprio.
    """
    return sum((Decimal(str(i[key])) for i in items), Decimal("0"))


def check_weights(items) -> tuple[bool, str, Decimal]:
    s = weight_sum(items)
    if s != Decimal("1.0"):
        return False, f"WEIGHT_SUM_NOT_ONE: {s}", s
    return True, "ACCEPTED", s


def canary(tr: Transcript, baseline_norm: str, rejected_terms: list[str]) -> list[dict]:
    rows: list[dict] = []

    def rec(case, expect, got, ok, note=""):
        rows.append({"case": case, "expect": expect, "got": got, "passed": ok,
                     "note": note})

    ok, code, s = check_weights(CRITERIA)
    rec("W1_SOMA_EXATA_UM", "ACEITA", f"{code} soma={s}", ok)

    legacy = [{"weight": w} for w in ("0.3", "0.2", "0.2", "0.2")]      # a legada, 0,9
    okL, codeL, sL = check_weights(legacy)
    rec("W2_SOMA_0_9_A_LEGADA", "REJEITA", f"{codeL}", not okL,
        "a rubrica legada do RELEASE soma 0,9 e limita o TOTAL_SCORE a 90")

    over = [dict(c) for c in CRITERIA]; over[0]["weight"] = "0.28"
    okO, codeO, _ = check_weights(over)
    rec("W3_SOMA_1_1", "REJEITA", codeO, not okO)

    # Poder de detecção do verificador EXATO. Nos pesos deste rascunho a soma em
    # binário calha de dar 1.0 — conferido, e é sorte, não propriedade. Um outro
    # conjunto igualmente válido derruba o verificador em float. É esse conjunto
    # que entra aqui: o instrumento tem de aceitá-lo, e o mutante em float não o
    # aceita.
    fsum_this = sum(float(c["weight"]) for c in CRITERIA)
    # conjunto achado por busca, não por asserção: soma exata 1, float 0.9999999999999999
    alt = [{"weight": w} for w in ("0.57", "0.29", "0.09", "0.05")]
    okA, codeA, sA = check_weights(alt)
    fsum_alt = sum(float(a["weight"]) for a in alt)
    float_rejects_valid = (fsum_alt != 1.0)
    rec("W4_CONJUNTO_VALIDO_QUE_O_FLOAT_RECUSA", "EXATO aceita E float recusaria",
        f"Decimal={sA} aceita={okA} · float={fsum_alt!r} recusaria={float_rejects_valid}",
        okA and float_rejects_valid,
        f"nos pesos DESTE rascunho a soma em float calha de dar {fsum_this!r} — "
        f"sorte, não propriedade; por isso a checagem é em Decimal")

    # citações
    bad = [c["criterion"] for c in CRITERIA if tr.find(c["quote"]) is None]
    rec("Q1_TODA_CITACAO_RESOLVE_EM_L0", "todas resolvem",
        "todas" if not bad else bad, not bad)
    fake = "This lesson explains the compiled skill routing gate precedence schema"
    rec("Q2_CITACAO_FABRICADA", "REJEITA", "não resolve" if tr.find(fake) is None
        else "RESOLVEU", tr.find(fake) is None)

    # circularidade mecanizável: citação que resolve no BASELINE e não em L0
    leaked = [c["criterion"] for c in CRITERIA
              if tr.find(c["quote"]) is None
              and " ".join(c["quote"].split()) in baseline_norm]
    rec("C1_CITACAO_VINDA_DO_BASELINE", "nenhuma",
        "nenhuma" if not leaked else leaked, not leaked)
    probe = " ".join(("The lesson's central reframe is to stop asking which task can "
                      "be automated").split())
    in_base = probe in baseline_norm
    in_l0 = tr.find(probe) is not None
    rec("C1_CITACAO_VINDA_DO_BASELINE", "detector tem poder: frase só-do-baseline é reconhecível",
        f"no baseline={in_base} em L0={in_l0}", in_base and not in_l0,
        "é a prova de que o detector distinguiria uma citação lida do baseline")

    # termo REJEITADO_SEM_ANCORA aparecendo em critério
    text_all = " ".join(json.dumps(c, ensure_ascii=False) for c in CRITERIA).lower()
    hits = [t for t in rejected_terms if t.lower() in text_all]
    rec("C2_TERMO_SEM_ANCORA_EM_L0", "nenhum termo estrutural rejeitado nos critérios",
        "nenhum" if not hits else hits, not hits,
        "os 12 termos foram rejeitados do baseline por não existirem em L0")

    # piso obrigatório coerente
    badmin = [c["criterion"] for c in CRITERIA
              if not (0 <= c["minimum_score"] <= 100)]
    rec("F1_PISOS_NO_INTERVALO", "todos em [0,100]",
        "ok" if not badmin else badmin, not badmin)
    return rows


# ------------------------------------------------------------------ variantes
HEADER_DECLARATION = {
    "artifact_status": "DRAFT_NOT_FROZEN",
    "external_audit_required_before_freeze": True,
    "authorship_conflict_declared": {
        "quem_escreveu_o_baseline": "Claude (esta sessão)",
        "quem_escreveu_este_rascunho": "Claude (esta sessão)",
        "mesma_pessoa": True,
        "por_que_isso_e_um_problema": (
            "O TEST-0008 existe para medir se a Skill compilada vale mais que uma "
            "representação não estruturada da MESMA informação. Se a régua foi "
            "escrita por quem escreveu o baseline, ela pode ter sido calibrada — "
            "sem intenção — para o que o baseline já diz ou já deixa de dizer. "
            "Isso não enviesa a medição para um lado previsível: enviesa para o "
            "lado que o autor não consegue ver, que é o que torna a auto-auditoria "
            "inútil aqui."),
        "quem_tambem_nao_pode_auditar": (
            "O revisor desta sessão declarou que revisou o baseline junto e por "
            "isso também não pode auditar a circularidade."),
        "consequencia": "TERCEIRO INDEPENDENTE, antes de congelar. Sem exceção.",
        "precedente_documentado": {
            "o_que_aconteceu": (
                "Uma versão anterior da régua exigia 'ROBOT prompt' enquanto o "
                "baseline não mencionava ROBOT. A condição-resumo era penalizada "
                "por não saber algo que a régua havia herdado do OUTRO braço."),
            "registrado_em": "BASELINE-PROVENANCE-v0.1.4.yaml :: robot_coverage_check",
            "por_que_importa": (
                "É exatamente o modo de falha que o auditor procura, já ocorrido "
                "uma vez neste teste e corrigido. Não é hipótese."),
        },
    },
}


def build_variant(letter: str, tr: Transcript, criteria: list[dict]) -> dict:
    direct = letter == "A"
    metrics = ["TOTAL_SCORE", "DECISION_ACCURACY", "METHODOLOGY_FIDELITY",
               "EXECUTION_QUALITY", "HALLUCINATION_RATE"]
    if direct:
        metrics += ["CONSISTENCY", "HUMAN_CHECKPOINT_COMPLIANCE"]

    gate_criteria = ["HUMAN_REVIEW_30_DAYS", "STEP_ORDER_INTEGRITY"]
    gate_weight = weight_sum([c for c in criteria if c["criterion"] in gate_criteria])

    doc = {
        "schema_version": "0.2.0",
        "artifact_id": f"PILOT-001-TEST-0008-RUBRIC-DRAFT-VARIANT-{letter}",
        "test_id": "TEST-0008", "candidate_version": "0.1.4",
        "variant": letter,
        "variant_name": ("CONSISTENCY e HUMAN_CHECKPOINT_COMPLIANCE como MÉTRICAS DIRETAS"
                         if direct else
                         "CONSISTENCY e HUMAN_CHECKPOINT_COMPLIANCE como GATE/AGGREGATE-ONLY"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        **HEADER_DECLARATION,

        "supersedes": {"artifact": PREV_DRAFT.name, "sha256": shp(PREV_DRAFT),
                       "o_que_muda": ("acrescenta pesos somando 1,0 exato, o critério "
                                      "STEP_ORDER_INTEGRITY, o mapa critério→métrica e "
                                      "as duas variantes. Os 7 critérios e seus spans "
                                      "de L0 são preservados."),
                       "nao_apagado": True},

        "source": {"transcript_path": str(L0.relative_to(DRIVE)),
                   "transcript_sha256": L0_SHA, "duration": "00:15:05"},

        "weights": {
            "sum": str(weight_sum(criteria)),
            "sum_is_exactly_one": weight_sum(criteria) == Decimal("1.0"),
            "arithmetic": "Decimal, NUNCA float",
            "por_que_decimal": (
                "NÃO porque estes pesos quebrem em float — conferido: a soma binária "
                f"deles dá {sum(float(c['weight']) for c in criteria)!r}, exata por "
                "sorte. É porque a exatidão não pode depender de sorte: o canário W4 "
                "exibe um conjunto de pesos igualmente válido — 0,57/0,29/0,09/0,05, achado "
                "por busca — cuja soma em float dá 0.9999999999999999, e que um "
                "verificador em float recusaria."),
            "soma_binaria_deste_conjunto": repr(sum(float(c["weight"]) for c in criteria)),
            "max_total_score": 100,
            "conserto_do_defeito_legado": ("a rubrica legada do RELEASE soma 0,9 e "
                                           "limita o TOTAL_SCORE a 90"),
        },

        "scoring_method": "WEIGHTED_SUM",
        "score_scale": {"min": 0, "max": 100},
        "rubric": criteria,

        "metrics": {
            "count": len(metrics),
            "vector": metrics,
            "same_vector_for_P_and_F": True,
            "por_que_o_mesmo_vetor": ("métrica exclusiva de uma das comparações "
                                      "destruiria a comparabilidade entre P e F"),
            "primary_metric": "TOTAL_SCORE",
            "primary_is_mechanical_not_preference": (
                "o scorer calcula margem = left.recomputed_total − right.recomputed_total. "
                "TOTAL_SCORE é a métrica de decisão por construção do instrumento; "
                "eleger outra exigiria reescrever o scorer."),
            "secondary_metrics_are_decomposition_not_tests": {
                "declared": True,
                "por_que": ("as demais métricas são componentes PONDERADOS do mesmo "
                            "TOTAL_SCORE. São perfeitamente dependentes por "
                            "construção — não são observações independentes e não "
                            "podem receber correção de múltiplas comparações nem "
                            "entrar em teste de hipótese separado."),
                "leitura_permitida": "diagnóstico: de onde veio a diferença",
                "leitura_proibida": "N testes independentes com N vereditos",
            },
        },

        "hallucination_rate": {
            "is_weighted_criterion": False,
            "por_que_nao": ("mede AUSÊNCIA de afirmação não sustentada, não a "
                            "presença de um passo ensinado. É a única métrica "
                            "canônica sem âncora POSITIVA em L0, e forçá-la a virar "
                            "critério ponderado exigiria inventar um span."),
            "definicao_vem_de": "TEST-0008-METRIC-LOCK.yaml",
            "polarity": "LOWER_IS_BETTER",
            "sinal_invertido_antes_de_entrar_em_margem": True,
            "PARA_O_AUDITOR": ("confirmar se aceitar uma métrica canônica sem âncora "
                               "positiva em L0 é admissível, ou se ela deve sair do "
                               "vetor. Esta é uma decisão de desenho, não um fato."),
        },
    }

    if direct:
        doc["variant_A_direct_metrics"] = {
            "CONSISTENCY": {"from_criterion": "STEP_ORDER_INTEGRITY",
                            "weight": "0.12", "minimum_score": 80},
            "HUMAN_CHECKPOINT_COMPLIANCE": {"from_criterion": "HUMAN_REVIEW_30_DAYS",
                                            "weight": "0.20", "minimum_score": 90},
            "reported_per_comparison": True,
            "quantidades_reportadas": len(metrics) * 2,
            "o_que_isto_torna_observavel": (
                "o efeito de ENQUADRAMENTO (F) sobre o comportamento de checkpoint "
                "humano especificamente — que é literalmente a hipótese do TEST-0008: "
                "'a Skill deve integrar escolha contextual de plataforma e revisão "
                "humana inicial com maior consistência que o resumo'."),
        }
    else:
        doc["variant_B_gate"] = {
            "gate_id": "TEST0008_GOVERNANCE_GATE",
            "criteria": gate_criteria,
            "rule": ("HUMAN_REVIEW_30_DAYS >= 90 E STEP_ORDER_INTEGRITY >= 80. "
                     "Reprovar qualquer uma REPROVA a execução, independentemente "
                     "do TOTAL_SCORE."),
            "fail_closed": True,
            "weight_still_in_total": str(gate_weight),
            "reported_per_comparison": False,
            "quantidades_reportadas": len(metrics) * 2,
            "AVISO_DE_ANCORAGEM_PARA_O_AUDITOR": {
                "achado": ("o termo 'gate' está na lista REJEITADO_SEM_ANCORA da "
                           "proveniência do baseline (R12): zero ocorrências em L0. "
                           "É forma estrutural do runtime compilado."),
                "consequencia": ("a variante B só é legítima se o portão for "
                                 "declarado como decisão de INSTRUMENTO DE MEDIÇÃO, "
                                 "nunca como algo que a fonte ensina. Declará-lo "
                                 "como conteúdo da aula importaria para a régua um "
                                 "conceito que o baseline foi limpo de conter — e "
                                 "penalizaria a condição-resumo por não o ter."),
                "declarado_como": "DECISAO_DE_INSTRUMENTO_NAO_CONTEUDO_DA_FONTE",
                "os_dois_criterios_seguem_ancorados": True,
            },
        }
    return doc


AUDITOR_CHECKLIST = """# PACOTE DE AUDITORIA — rubrica do TEST-0008

**Este rascunho NÃO está congelado.** `artifact_status: DRAFT_NOT_FROZEN`.

## Por que você está lendo isto

O TEST-0008 mede se uma Skill compilada vale mais que uma representação **não
estruturada da mesma informação**. Quem escreveu o baseline (a representação não
estruturada) escreveu também esta régua. Quem revisou o baseline também não pode
auditar. Nenhum dos dois consegue ver o próprio viés — é essa a razão de você
existir neste processo.

---

## 1. A PERGUNTA PRINCIPAL, e ela vem antes de todas as outras

**Algum critério ou âncora foi escrito olhando o BASELINE em vez do L0?**

É a circularidade que o teste existe para medir. Se a régua foi calibrada
— mesmo sem intenção — para o que o baseline já diz, ou para o que ele já deixa
de dizer, o resultado do TEST-0008 mede a régua, não a Skill.

**Não é hipótese: já aconteceu uma vez neste teste.** Uma versão anterior da
régua exigia "ROBOT prompt" enquanto o baseline não mencionava ROBOT. A
condição-resumo era penalizada por não saber algo que a régua havia herdado do
**outro braço**. Está registrado em `BASELINE-PROVENANCE-v0.1.4.yaml ::
robot_coverage_check`. Foi corrigido. Procure o próximo.

Como procurar, na ordem:

1. Para cada critério, leia **primeiro** o `l0_excerpt` e o span. Vá ao
   `L0/transcript-original-en.txt` e confirme que a passagem sustenta o critério
   **sozinha**, sem o baseline aberto.
2. Só então leia o baseline. Pergunte: este critério ficou mais fácil de
   entender depois de ler o baseline? Se ficou, ele pode ter sido escrito de lá.
3. Procure o inverso, que é mais difícil de ver: **critério que o baseline
   cobre bem e o L0 cobre mal.** Um critério assim favorece o baseline e ninguém
   reclama — por isso passa.
4. Procure critério **ausente**: algo que o L0 ensina, que a Skill compilada
   provavelmente executa, e que a régua não mede. Omissão também é calibração.

O que a verificação mecânica já fez, e o que ela **não** consegue fazer:

- FEITO: toda citação resolve em L0 por substring normalizada;
- FEITO: nenhuma citação vem do baseline em vez do L0;
- FEITO: nenhum dos 12 termos estruturais rejeitados por falta de âncora em L0
  aparece nos critérios;
- **NÃO FEITO, e não é possível:** detectar um critério cuja *escolha* foi
  influenciada por ter lido o baseline. Isso é semântico. Neste projeto,
  proxy mecânico para propriedade semântica já falhou três vezes
  (`PROXY-LIMITS-AND-RESTING-STATE.yaml`). Não confie na varredura para
  responder à pergunta 1. Ela só limpa o caminho.

---

## 2. As outras coisas, em ordem de gravidade

**2.1 — Pesos.** Somam 1,0 exato, em `Decimal`. Confira a *justificativa* de
cada peso, não só a soma: cada uma cita L0. O maior peso (0,20) está em
`HUMAN_REVIEW_30_DAYS` porque é o único passo que L0 qualifica com
"No exceptions". Discorde se achar que a hierarquia não se sustenta na fonte.

**2.2 — A escolha entre as variantes A e B não é sua.** É do Alexandre. O que
se pede de você é dizer se alguma das duas é **inadmissível**, e por quê.
Atenção especial ao aviso da variante B: o termo "gate" **não tem âncora em L0**
(R12 da proveniência). O portão só é legítimo declarado como instrumento de
medição. Se ele aparecer descrito como algo que a aula ensina, reprove.

**2.3 — `HALLUCINATION_RATE`.** É a única métrica canônica sem âncora
**positiva** em L0, porque mede ausência. Está fora do vetor ponderado e sua
definição (numerador, denominador, denominador zero, polaridade) foi
**declarada**, não herdada do RELEASE — o RELEASE tem `HALLUCINATION_CONTROL`
como critério, não `HALLUCINATION_RATE` como métrica computável. Decida se uma
métrica assim pode ficar no vetor.

**2.4 — Paridade de informação.** As condições 2 e 3 têm o resumo **byte a
byte idêntico** (`dac83c3d70e0…`); só o enquadramento difere. Confirme, e
confirme que o baseline não recebeu estrutura executável disfarçada de prosa.

**2.5 — Não-independência.** P e F compartilham o braço `SUMMARY_AS_SUMMARY`.
As métricas secundárias são componentes ponderados do mesmo `TOTAL_SCORE`,
portanto perfeitamente dependentes. Confirme que nada no rascunho as trata como
testes separados.

---

## 3. O que este pacote NÃO pede

Não pede que você congele nada, escolha variante, ou avalie a Skill. Pede um
parecer sobre se a **régua** é honesta em relação à **fonte**.

## 4. Conteúdo do pacote

| arquivo | o que é |
|---|---|
| `RUBRIC-DRAFT-VARIANT-A.yaml` | variante A — métricas diretas |
| `RUBRIC-DRAFT-VARIANT-B.yaml` | variante B — gate/aggregate-only |
| `VARIANT-COMPARISON.yaml` | o que se ganha e se perde em cada uma |
| `L0/transcript-original-en.txt` | a fonte, cópia de transporte com hash |
| `BASELINE/SUMMARY.md` | o baseline (condições 2 e 3) |
| `BASELINE/PROVENANCE.yaml` | 23 elementos com span, 12 rejeitados sem âncora |
| `CONDITIONS/` | as três condições e seus enquadramentos |
| `CANARY-RESULT.yaml` | o canário da rubrica, com os mutantes |
| `SHA256SUMS.txt` | hashes de tudo acima |

`FULL_SKILL` não é copiado: é o pacote congelado
`b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028`, e duplicá-lo
criaria uma segunda fonte de verdade. `CONDITIONS/1_FULL_SKILL/POINTER.md` dá a
origem exata.
"""


def main() -> int:
    for p in (L0, PREV_DRAFT, PROV, BASELINE, METRIC_LOCK, SCORER_REPORT):
        if not p.exists():
            print(f"ÂNCORA AUSENTE: {p}")
            return 2
    if shp(L0) != L0_SHA:
        print("PORTÃO: L0 não bate com o hash declarado na proveniência")
        return 2

    tr = Transcript(L0)
    prov = yaml.safe_load(PROV.read_text(encoding="utf-8"))
    rejected_terms = [r["candidate_term"] for r in prov["REJEITADO_SEM_ANCORA"]]
    baseline_norm = " ".join(BASELINE.read_text(encoding="utf-8").split())

    # ---- ancorar cada critério e cada âncora de nota; citação que não resolve ABORTA
    criteria: list[dict] = []
    for c in CRITERIA:
        span = tr.span(c["quote"])
        wspan = tr.span(c["weight_rationale_quote"])
        if span is None or wspan is None:
            print(f"ABORTA: citação não resolve em L0 — {c['criterion']}")
            return 3
        anchors = {}
        for name, lo, hi, cond in ANCHOR_LEVELS:
            anchors[name] = {
                "range": [lo, hi], "condition": cond,
                "l0_anchor": {"span": span, "quote": c["quote"],
                              "quote_verified_in_span": True},
            }
        criteria.append({
            "criterion": c["criterion"], "weight": c["weight"],
            "mandatory": True, "minimum_score": c["minimum_score"],
            "description": c["description"],
            "maps_to_metric": c["metric"],
            "l0_span": span, "l0_excerpt": c["quote"],
            "l0_excerpt_verified": True,
            "weight_rationale": c["weight_rationale"],
            "weight_rationale_l0_span": wspan,
            "weight_rationale_l0_excerpt": c["weight_rationale_quote"],
            "score_anchors": anchors,
        })

    rows = canary(tr, baseline_norm, rejected_terms)
    approved = all(r["passed"] for r in rows)
    if not approved:
        print("CANÁRIO REPROVADO — nada é publicado.")
        for r in rows:
            if not r["passed"]:
                print(f"  {r['case']}: esperava {r['expect']}, obteve {r['got']}")
        return 4

    A = build_variant("A", tr, criteria)
    B = build_variant("B", tr, criteria)

    gate_w = weight_sum([c for c in criteria
                         if c["criterion"] in ("HUMAN_REVIEW_30_DAYS",
                                               "STEP_ORDER_INTEGRITY")])
    comparison = {
        "schema_version": "0.1.0",
        "artifact_id": "TEST-0008-RUBRIC-VARIANT-COMPARISON",
        "artifact_status": "DRAFT_NOT_FROZEN",
        "decision_owner": "Alexandre",
        "nao_escolhida_aqui": True,
        "criterios_identicos_nas_duas": True,
        "por_que_criterios_identicos": (
            "TOTAL_SCORE, P e F são NUMERICAMENTE IGUAIS nas duas variantes. O que "
            "muda é o que fica VISÍVEL e o que pode REPROVAR sozinho. Manter os "
            "critérios idênticos é o que permite ao Alexandre trocar de variante sem "
            "invalidar a comparação."),
        "poder_de_deteccao_estatistico": {
            "quantificavel": False,
            "por_que": ("a variância do avaliador do TEST-0008 não foi medida — é o "
                        "bloqueador 3 da ADR, ainda aberto. Sem variância não há "
                        "poder estatístico, e inventar um número aqui seria o quarto "
                        "proxy mecânico para propriedade que não foi medida."),
            "o_que_se_reporta_no_lugar": "poder de detecção ESTRUTURAL",
        },
        "variant_A": {
            "metricas": len(A["metrics"]["vector"]), "vetor": A["metrics"]["vector"],
            "primaria": "TOTAL_SCORE",
            "ganha": [
                ("torna observável o efeito de enquadramento F sobre o comportamento "
                 "de checkpoint humano especificamente — que é a hipótese literal do "
                 "TEST-0008"),
                ("mede diferença GRADUADA: 10 pontos de diferença em checkpoint "
                 "aparecem mesmo quando os dois braços passam do piso"),
                "permite atribuir a margem a um componente, não só constatá-la",
            ],
            "perde": [
                ("14 quantidades reportadas (7 × 2 comparações). Toda leitura como "
                 "'7 testes' é errada e a declaração de decomposição passa a carregar "
                 "peso que declaração nenhuma carrega bem"),
                ("as duas métricas novas são componentes ponderados do MESMO total: "
                 "correlação 1 por construção, não informação adicional independente"),
                ("muda a lista congelada de 5 para 7 e exige rederivação do "
                 "TEST-0008-METRIC-LOCK"),
            ],
        },
        "variant_B": {
            "metricas": len(B["metrics"]["vector"]), "vetor": B["metrics"]["vector"],
            "primaria": "TOTAL_SCORE",
            "ganha": [
                "10 quantidades reportadas; nenhuma tentação de multiplicidade",
                ("o portão é FAIL-CLOSED e independente de peso: um braço que pula a "
                 "revisão humana REPROVA mesmo com total alto"),
                "preserva a lista canônica de 5 sem rederivação",
            ],
            "perde": [
                ("o portão é BINÁRIO. Só detecta diferença se um braço cruzar o piso "
                 "e o outro não. Diferença graduada de checkpoint entre braços que "
                 "ambos passam fica INVISÍVEL"),
                (f"os dois critérios continuam pesando {gate_w} no TOTAL_SCORE, mas "
                 "não é possível saber se a margem veio dali ou de execução"),
                ("a hipótese declarada do TEST-0008 deixa de ser testável no nível da "
                 "métrica e sobrevive só como passa/não-passa"),
            ],
            "ressalva_de_ancoragem": B["variant_B_gate"]["AVISO_DE_ANCORAGEM_PARA_O_AUDITOR"],
        },
        "assimetria_que_o_auditor_deve_ver": (
            "A variante A não introduz conceito novo: as duas métricas saem de "
            "critérios já ancorados em L0. A variante B introduz o conceito de "
            "PORTÃO, cujo termo foi REJEITADO da proveniência do baseline por não "
            "existir em L0. Isso não reprova B — mas obriga B a declarar o portão "
            "como instrumento, e é uma diferença de natureza entre as duas, não de "
            "grau."),
    }

    # ------------------------------------------------------------ o pacote
    if PKG.exists():
        shutil.rmtree(PKG)
    (PKG / "L0").mkdir(parents=True)
    (PKG / "BASELINE").mkdir()
    (PKG / "CONDITIONS").mkdir()

    def put(dst: Path, data) -> None:
        dst.write_text(data if isinstance(data, str)
                       else yaml.safe_dump(data, allow_unicode=True, sort_keys=False,
                                           width=100), encoding="utf-8")

    put(PKG / "RUBRIC-DRAFT-VARIANT-A.yaml", A)
    put(PKG / "RUBRIC-DRAFT-VARIANT-B.yaml", B)
    put(PKG / "VARIANT-COMPARISON.yaml", comparison)
    put(PKG / "README-AUDITOR.md", AUDITOR_CHECKLIST)
    (PKG / "L0/transcript-original-en.txt").write_bytes(L0.read_bytes())
    put(PKG / "L0/TRANSPORT-RECORD.yaml", {
        "file": "transcript-original-en.txt", "sha256": L0_SHA,
        "origin": str(L0.relative_to(DRIVE)),
        "nature": "CÓPIA DE TRANSPORTE, verbatim, conferida por hash",
        "por_que_copiada": ("o auditor não tem como conferir citação sem a fonte; a "
                            "origem continua sendo a árvore read-only")})
    (PKG / "BASELINE/SUMMARY.md").write_bytes(BASELINE.read_bytes())
    (PKG / "BASELINE/PROVENANCE.yaml").write_bytes(PROV.read_bytes())
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

    sums = {str(p.relative_to(PKG)): shp(p)
            for p in sorted(PKG.rglob("*")) if p.is_file()}
    (PKG / "SHA256SUMS.txt").write_text(
        "".join(f"{v}  {k}\n" for k, v in sums.items()), encoding="utf-8")

    idx = {
        "schema_version": "0.1.0",
        "artifact_id": "TEST-0008-RUBRIC-AUDIT-PACKAGE",
        "artifact_status": "DRAFT_NOT_FROZEN_PENDING_EXTERNAL_AUDIT",
        "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nada_congelado": True,
        "variantes": {"A": len(A["metrics"]["vector"]), "B": len(B["metrics"]["vector"])},
        "decisao_do_alexandre": "qual variante",
        "decisao_do_auditor": "se alguma é inadmissível, e se há circularidade",
        "binds_to": {
            "metric_lock": {"path": METRIC_LOCK.name, "sha256": shp(METRIC_LOCK)},
            "scorer_v2_report": {"path": SCORER_REPORT.name, "sha256": shp(SCORER_REPORT)},
            "previous_draft_superseded": {"path": PREV_DRAFT.name, "sha256": shp(PREV_DRAFT)},
            "full_skill_arm_sha256": "b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028",
        },
        "files": sums,
    }
    put(DOCS / "TEST-0008-RUBRIC-AUDIT-PACKAGE.yaml", idx)

    print("=" * 78)
    print("PASSO 3 — RASCUNHO DA RUBRICA (DUAS VARIANTES) + PACOTE DE AUDITORIA")
    print("=" * 78)
    print(f"L0 {L0_SHA[:16]}… · {len(tr.norm)} chars normalizados · "
          f"{len(tr.segments)} segmentos")
    print(f"\ncritérios: {len(criteria)} · soma dos pesos {weight_sum(criteria)} "
          f"(exata, Decimal) · TOTAL_SCORE máx 100")
    for c in criteria:
        print(f"  {c['criterion']:<24} {c['weight']}  piso {c['minimum_score']:>2}  "
              f"→ {c['maps_to_metric']:<28} L0 {c['l0_span']['start']}–{c['l0_span']['end']}")
    print(f"\ncanário ({'APROVADO' if approved else 'REPROVADO'}) "
          f"{sum(r['passed'] for r in rows)}/{len(rows)}:")
    for r in rows:
        print(f"  {'ok ' if r['passed'] else 'FALHOU'} {r['case']:<32} "
              f"espera {r['expect']}")
        print(f"      obteve: {r['got']}")
    print(f"\nvariante A: {len(A['metrics']['vector'])} métricas · primária TOTAL_SCORE")
    print(f"variante B: {len(B['metrics']['vector'])} métricas · primária TOTAL_SCORE · "
          f"portão com peso {gate_w} no total")
    print(f"\npacote: {PKG.relative_to(DRIVE)}/ ({len(sums)} arquivos)")
    print(f"índice: TEST-0008-RUBRIC-AUDIT-PACKAGE.yaml "
          f"sha256 {shp(DOCS/'TEST-0008-RUBRIC-AUDIT-PACKAGE.yaml')[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
