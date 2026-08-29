"""Extractor real do PASS 2 — uma chamada de modelo POR SEGMENTO.

Implementa o Protocol `ctsc2.model.Extractor`. É o único lugar do compilador v2
que fala com um modelo; o resto da máquina não sabe que ele existe.

DECISÃO A, no código e não só no prompt
---------------------------------------
Cada invocação recebe UM segmento. O texto entregue ao modelo é fatiado pelo
intervalo desse segmento antes da chamada: não existe caminho aqui que entregue
a aula inteira, nem por engano de prompt.

O QUE NÃO É DELEGADO AO MODELO
------------------------------
- **Numeração.** O modelo não emite ID. Quem numera é o `IdAllocator` global.
- **Escopo.** Marcas fora do intervalo do segmento são REJEITADAS em código.
- **Veracidade da citação.** A `quote` tem de aparecer literalmente no texto do
  segmento; se não aparecer, a evidência é rejeitada. É o mesmo portão que o
  `VALIDATION_REPORT` do PILOT-002 já aplicava por re-fatiamento.

Rejeição é DADO, não silêncio: cada descarte entra no rastro com o motivo.
"""
from __future__ import annotations

import difflib
import json
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Callable

from ..model import EvidenceDraft, Segment

MODEL = "claude-opus-5"
MAX_TOKENS = 16000
EFFORT = "high"

MARK_RE = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")


def normalize_for_match(s: str) -> str:
    """Normalização DECLARADA e determinística, aplicada aos DOIS lados.

    Faz exatamente duas coisas, ambas de FORMATO:
      1. remove as marcas de tempo `**M:SS**`, que são estrutura do transcript e
         não fala — o modelo, ao citar através de uma fronteira de marca, omite
         a marca porque ela não é conteúdo;
      2. colapsa espaço em branco, incluindo as quebras duplas entre blocos.

    NÃO faz casamento difuso, NÃO usa similaridade, NÃO toca em pontuação, letra
    ou palavra. Uma citação fabricada continua não casando depois disto — é essa
    a fronteira entre normalizar formato e afrouxar o portão, e o canário C6
    existe para prová-la a cada execução.
    """
    return " ".join(MARK_RE.sub(" ", s).split())


def quote_matches(qn: str, tn: str) -> bool:
    """Casamento EXATO de substring sobre texto já normalizado.

    Função de módulo de propósito: é a costura que o canário C6 troca pelo
    mutante difuso. Uma regra de casamento que nenhum teste consegue substituir
    é uma regra que nenhum teste consegue verificar.
    """
    return bool(qn) and qn in tn

# Categorias do PASS 2 do spec do release. Congeladas: acrescentar categoria é
# mudança de spec, não de extractor.
CATEGORIES = [
    "CONCEPT", "PRINCIPLE", "PROCEDURE", "DECISION", "RATIONALE", "EXAMPLE",
    "COUNTEREXAMPLE", "ANTI_PATTERN", "EXCEPTION", "QUALITY_CRITERION",
    "QUESTION", "TOOL_USAGE", "CONSTRAINT", "WARNING",
]
EPISTEMIC = ["SOURCE_EXPLICIT", "MODEL_INFERENCE", "GENERAL_KNOWLEDGE"]

SCHEMA = {
    "type": "object",
    "properties": {
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "start_mark": {"type": "string"},
                    "end_mark": {"type": "string"},
                    "quote": {"type": "string"},
                    "category": {"type": "string", "enum": CATEGORIES},
                    "epistemic_status": {"type": "string", "enum": EPISTEMIC},
                },
                "required": ["claim", "start_mark", "end_mark", "quote",
                             "category", "epistemic_status"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["evidence"],
    "additionalProperties": False,
}

# Estável entre chamadas de propósito: é o prefixo cacheado. Qualquer coisa que
# varie por segmento vai no turno do usuário, depois do ponto de cache.
SYSTEM = """\
Você executa o PASS 2 do Course-to-Skill Compiler: extração de evidência.

Você está extraindo de UM ÚNICO SEGMENTO, identificado no turno do usuário. O \
escopo desta chamada é apenas o intervalo desse segmento.

Extraia dele TODAS as unidades atômicas que a fonte sustenta, até exaurir o \
segmento. Não racione. Não distribua esforço pensando em outros segmentos: você \
não os verá nesta chamada e eles não competem com este.

Se o segmento não contiver metodologia extraível, devolva uma lista VAZIA. Zero \
é resposta válida e será registrada como tal. Não invente unidade para preencher \
espaço.

## Atomicidade

Uma evidência representa UMA única afirmação ou comportamento. Prefira várias \
unidades estreitas a uma unidade que empacota cinco instruções.

## Pergunta obrigatória

Para cada evidência: "Consigo apontar exatamente onde isso aparece?" Se não \
consegue, não marque como SOURCE_EXPLICIT.

## Fidelidade ao literal

`SOURCE_EXPLICIT` significa que a claim afirma o que a fonte LITERALMENTE diz.

Se a sua claim corrigir, completar, desambiguar ou normalizar o literal — \
inclusive quando o literal contém erro evidente de transcrição — o \
`epistemic_status` NÃO pode ser `SOURCE_EXPLICIT`. Use `MODEL_INFERENCE`.

A transcrição é automática e tem erros. Corrigi-los é útil e permitido; o que \
não é permitido é corrigir e chamar de fonte explícita. Exemplo: se o literal \
diz "a length post" e você entende "a LinkedIn post", escreva a claim como \
preferir, mas rotule `MODEL_INFERENCE` — e deixe a `quote` com o texto \
ORIGINAL, sem correção.

A `quote` nunca é corrigida. Ela é a fonte; a claim é a leitura dela.

## Regras de saída, verificadas em código

- `start_mark` e `end_mark` são marcas de tempo que aparecem LITERALMENTE no \
texto do segmento, no formato `M:SS` (sem os asteriscos). Marca inventada ou \
fora do segmento é rejeitada.
- `quote` é um trecho copiado LITERALMENTE do texto do segmento, sem edição, \
sem reticências, sem normalização. Citação que não casa exatamente é rejeitada.
- NÃO numere as evidências. O compilador atribui os identificadores.

Não há alvo de contagem. Nem mínimo, nem máximo.\
"""


@dataclass
class CallRecord:
    """Rastro de UMA chamada. Um por invocação, inclusive as que rendem zero."""
    segment_id: str
    iteration: int
    model: str = MODEL
    effort: str = EFFORT
    ok: bool = False
    error: str = ""
    stop_reason: str = ""
    request_id: str = ""
    latency_s: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0
    segment_chars: int = 0
    segment_marks: int = 0
    drafts_returned: int = 0
    drafts_accepted: int = 0
    rejected: list[dict] = field(default_factory=list)
    # Recuperados pela normalização: passariam pela regra ESTRITA? Guardar os
    # dois vereditos por evidência é o que permite comparar antes/depois sem
    # gastar uma segunda chamada.
    strict_pass: int = 0
    normalized_only: list[dict] = field(default_factory=list)
    # Aviso, não portão: claim que corrige o literal e se rotula SOURCE_EXPLICIT.
    warnings: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class ClaudeExtractor:
    """PASS 2 por segmento, contra a API da Anthropic.

    `text_for(segment)` devolve o texto do segmento. O extractor nunca vê mais
    do que isso.
    """

    def __init__(self, text_for: Callable[[Segment], str], *, client=None,
                 model: str = MODEL, max_tokens: int = MAX_TOKENS,
                 effort: str = EFFORT):
        self.text_for = text_for
        self.model, self.max_tokens, self.effort = model, max_tokens, effort
        self.calls: list[CallRecord] = []
        if client is not None:
            self._client = client
        else:
            import anthropic          # import tardio: a máquina roda sem o SDK
            self._client = anthropic.Anthropic()

    # ------------------------------------------------------------- validação
    @staticmethod
    def _marks(text: str) -> dict[str, int]:
        return {f"{m.group(1)}:{m.group(2)}":
                int(m.group(1)) * 60 + int(m.group(2))
                for m in MARK_RE.finditer(text)}

    @staticmethod
    def _diff(qn: str, tn: str, raw_quote: str) -> dict:
        """Onde a citação normalizada deixa de casar com a fonte normalizada.

        Acha a janela mais parecida do texto e devolve as operações de edição.
        Isto é DIAGNÓSTICO, nunca critério: o veredito já foi dado acima por
        casamento exato sobre texto normalizado.
        """
        if not qn:
            return {"diff": "QUOTE_VAZIA_APOS_NORMALIZACAO"}
        sm = difflib.SequenceMatcher(None, tn, qn, autojunk=False)
        i, j, n = sm.find_longest_match(0, len(tn), 0, len(qn))
        lo, hi = max(0, i - 40), min(len(tn), i + len(qn) + 40)
        window = tn[lo:hi]
        ops = []
        for tag, a1, a2, b1, b2 in difflib.SequenceMatcher(
                None, window, qn, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            ops.append({"op": tag, "fonte": window[a1:a2][:80],
                        "quote": qn[b1:b2][:80]})
        return {
            "quote_devolvida": raw_quote,
            "quote_normalizada": qn,
            "janela_da_fonte": window,
            "maior_trecho_comum": qn[j:j + n][:120],
            "maior_trecho_comum_chars": n,
            "cobertura_do_maior_trecho": round(n / len(qn), 3),
            "operacoes": ops[:12],
            "marcas_na_quote_devolvida": len(MARK_RE.findall(raw_quote)),
        }

    def _validate(self, raw: dict, seg: Segment, text: str,
                  marks: dict[str, int]) -> tuple[EvidenceDraft | None, dict | None]:
        def bad(reason, **extra):
            return None, {"reason": reason, "claim": (raw.get("claim") or "")[:120],
                          **extra}

        for f in ("claim", "start_mark", "end_mark", "quote"):
            if not (raw.get(f) or "").strip():
                return bad("CAMPO_VAZIO", field=f)

        a, b = raw["start_mark"].strip(), raw["end_mark"].strip()
        if a not in marks:
            return bad("MARCA_INEXISTENTE_NO_SEGMENTO", mark=a)
        if b not in marks:
            return bad("MARCA_INEXISTENTE_NO_SEGMENTO", mark=b)
        s0, s1 = marks[a], marks[b]
        if s1 < s0:
            return bad("INTERVALO_INVERTIDO", start=a, end=b)
        if not (seg.start_s <= s0 < seg.end_s and seg.start_s <= s1 <= seg.end_s):
            return bad("FORA_DO_SEGMENTO", start=a, end=b,
                       segment=[seg.start_s, seg.end_s])

        quote = raw["quote"]
        strict_ok = quote in text
        qn, tn = normalize_for_match(quote), normalize_for_match(text)
        norm_ok = quote_matches(qn, tn)
        if not norm_ok:
            return bad("CITACAO_NAO_RESOLVE", **self._diff(qn, tn, quote))

        return EvidenceDraft(
            claim=raw["claim"].strip(), start_s=s0,
            end_s=s1 if s1 > s0 else min(s0 + 1, seg.end_s),
            category=raw.get("category") or "CONCEPT",
            epistemic_status=raw.get("epistemic_status") or "SOURCE_EXPLICIT",
            quote=quote), {"strict_ok": strict_ok, "accepted": True,
                           "claim": raw["claim"], "quote": quote,
                           "epistemic_status": raw.get("epistemic_status")}

    # -------------------------------------------------------------- chamada
    def extract(self, segment: Segment, context: dict,
                iteration: int) -> list[EvidenceDraft]:
        text = self.text_for(segment)
        marks = self._marks(text)
        rec = CallRecord(segment_id=segment.segment_id, iteration=iteration,
                         model=self.model, effort=self.effort,
                         segment_chars=len(text), segment_marks=len(marks))

        head = (f"SEGMENTO {segment.segment_id} "
                f"({segment.start_s}s–{segment.end_s}s, {segment.duration}s)")
        if segment.topic:
            head += f" · tópico declarado: {segment.topic}"
        nxt = context.get("next_segment_id")
        prev = context.get("previous_segment_id")
        scope = (f"Vizinhos: anterior={prev or '—'}, seguinte={nxt or '—'}. "
                 "Eles são informados só para você saber onde seu escopo "
                 "termina; não extraia deles.")
        again = ("\n\nEsta é uma REVARREDURA dirigida deste segmento: o portão "
                 "de cobertura apontou território não coberto aqui. Procure o "
                 "que ficou de fora na primeira passada. Se não houver mais "
                 "nada que a fonte sustente, devolva lista vazia — repetir o "
                 "que já foi extraído não ajuda." if iteration else "")

        t0 = time.monotonic()
        try:
            with self._client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=[{"type": "text", "text": SYSTEM,
                         "cache_control": {"type": "ephemeral"}}],
                thinking={"type": "adaptive"},
                output_config={"effort": self.effort,
                               "format": {"type": "json_schema",
                                          "schema": SCHEMA}},
                messages=[{"role": "user", "content":
                           f"{head}\n{scope}{again}\n\n---\n{text}\n---"}],
            ) as stream:
                msg = stream.get_final_message()
        except Exception as e:
            rec.latency_s = round(time.monotonic() - t0, 2)
            rec.error = f"{type(e).__name__}: {e}"
            self.calls.append(rec)
            raise

        rec.latency_s = round(time.monotonic() - t0, 2)
        rec.request_id = getattr(msg, "_request_id", "") or ""
        rec.stop_reason = msg.stop_reason or ""
        u = msg.usage
        rec.input_tokens = getattr(u, "input_tokens", 0) or 0
        rec.output_tokens = getattr(u, "output_tokens", 0) or 0
        rec.cache_read_input_tokens = getattr(u, "cache_read_input_tokens", 0) or 0
        rec.cache_creation_input_tokens = getattr(
            u, "cache_creation_input_tokens", 0) or 0

        if msg.stop_reason == "refusal":
            rec.error = "REFUSAL"
            self.calls.append(rec)
            return []

        payload = next((b.text for b in msg.content if b.type == "text"), "")
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            rec.error = f"JSON_INVALIDO: {e}"
            self.calls.append(rec)
            return []

        raw_list = data.get("evidence") or []
        rec.drafts_returned = len(raw_list)
        out: list[EvidenceDraft] = []
        for raw in raw_list:
            draft, info = self._validate(raw, segment, text, marks)
            if draft is None:
                rec.rejected.append(info)
                continue
            out.append(draft)
            if info.get("strict_ok"):
                rec.strict_pass += 1
            else:
                # Recuperada SÓ pela normalização: é exatamente o delta
                # antes/depois, medido na mesma chamada.
                rec.normalized_only.append(
                    {"claim": info["claim"][:120],
                     "marcas_na_quote": len(MARK_RE.findall(info["quote"]))})
            w = self._warn_claim_divergence(info)
            if w:
                rec.warnings.append(w)
        rec.drafts_accepted = len(out)
        rec.ok = True
        self.calls.append(rec)
        return out

    @staticmethod
    def _warn_claim_divergence(info: dict) -> dict | None:
        """Claim que corrige o literal e ainda se rotula SOURCE_EXPLICIT.

        AVISO, não portão. A checagem é por entidade nomeada e tem falso
        positivo conhecido quando a claim é escrita noutra língua que a fonte
        (\"IA\" contra \"AI\"). Rejeitar por isto seria descartar evidência boa
        por artefato de medida; sinalizar deixa a chamada com quem revisa.
        """
        if info.get("epistemic_status") != "SOURCE_EXPLICIT":
            return None
        claim, quote = info["claim"], info["quote"].lower()
        ents = {w for w in re.findall(r"\b[A-Z][A-Za-z0-9]{2,}\b", claim)}
        missing = sorted(e for e in ents if e.lower() not in quote)
        if not missing:
            return None
        return {"reason": "CLAIM_DIVERGE_DO_LITERAL_COM_ROTULO_SOURCE_EXPLICIT",
                "entidades_ausentes_da_quote": missing,
                "claim": claim[:160], "quote": info["quote"][:160]}

    # ----------------------------------------------------------- observação
    def trace(self) -> list[dict]:
        return [c.to_dict() for c in self.calls]

    def totals(self) -> dict:
        return {
            "calls": len(self.calls),
            "ok": sum(1 for c in self.calls if c.ok),
            "errors": sum(1 for c in self.calls if not c.ok),
            "input_tokens": sum(c.input_tokens for c in self.calls),
            "output_tokens": sum(c.output_tokens for c in self.calls),
            "cache_read_input_tokens": sum(c.cache_read_input_tokens
                                           for c in self.calls),
            "cache_creation_input_tokens": sum(c.cache_creation_input_tokens
                                               for c in self.calls),
            "drafts_returned": sum(c.drafts_returned for c in self.calls),
            "drafts_accepted": sum(c.drafts_accepted for c in self.calls),
            "drafts_rejected": sum(len(c.rejected) for c in self.calls),
            "strict_pass": sum(c.strict_pass for c in self.calls),
            "recovered_by_normalization": sum(len(c.normalized_only)
                                              for c in self.calls),
            "warnings": sum(len(c.warnings) for c in self.calls),
            "latency_s": round(sum(c.latency_s for c in self.calls), 1),
        }
