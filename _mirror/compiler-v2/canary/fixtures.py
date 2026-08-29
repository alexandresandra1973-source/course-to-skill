"""Fixtures do canário. Aritmética escolhida ANTES, para os limiares não serem
ajustados depois de ver resultado.

Extensão de todas as fixtures: 1000s. Piso do portão: 0,735 (congelado).
  - cobertura 0,50 → ABAIXO, tem de disparar revarredura;
  - cobertura 0,80 → ACIMA, tem de encerrar sem revarredura.
Os dois valores ficam longe do piso de propósito: um canário que passe raspando
no limiar testa arredondamento, não comportamento.
"""
from __future__ import annotations

from ctsc2.model import EvidenceDraft, Segment

EXTENT_S = 1000

SEGS_2 = [Segment("SEG-001", 0, 500, "primeira metade"),
          Segment("SEG-002", 500, 1000, "segunda metade")]

SEGS_3 = [Segment("SEG-001", 0, 300, "abertura"),
          Segment("SEG-002", 300, 600, "trecho sem metodologia"),
          Segment("SEG-003", 600, 1000, "fechamento")]

# Duas afirmações VIZINHAS e DISTINTAS na fronteira 500s. Parecença lexical
# alta de propósito: é isso que tenta a deduplicação agressiva.
BOUNDARY_LEFT = "abrir o terminal e digitar claude para iniciar a sessao"
BOUNDARY_RIGHT = "abrir o terminal e digitar claude resume para retomar a sessao"


class _Base:
    name = "base"

    def extract(self, segment: Segment, context: dict, iteration: int):
        raise NotImplementedError


class BoundaryDistinct(_Base):
    """C1 — duas vizinhas distintas na fronteira. Ambas TÊM de sobreviver.

    Cobertura total 1,0 para o portão não disparar e o canário medir só dedup.
    """
    name = "boundary_distinct"

    def extract(self, segment, context, iteration):
        if iteration:
            return []
        if segment.segment_id == "SEG-001":
            return [EvidenceDraft("instalar o compilador antes de comecar", 0, 480),
                    EvidenceDraft(BOUNDARY_LEFT, 480, 500)]
        return [EvidenceDraft(BOUNDARY_RIGHT, 500, 520),
                EvidenceDraft("encerrar a sessao ao terminar", 520, 1000)]


class TrueDuplicate(_Base):
    """C2 — a revarredura reemite a MESMA afirmação. Tem de fundir.

    PASS 2 cobre 0–500 (0,50 < piso) → portão dispara → revarredura em SEG-002
    devolve uma duplicata exata do PASS 2 mais uma unidade nova.
    """
    name = "true_duplicate"
    DUP = "o compilador exige um mapa temporal persistido"

    def extract(self, segment, context, iteration):
        if iteration == 0:
            return [EvidenceDraft(self.DUP, 0, 500)] if segment.segment_id == "SEG-001" else []
        if segment.segment_id == "SEG-002":
            return [EvidenceDraft(self.DUP, 0, 500),                 # duplicata exata
                    EvidenceDraft("a revarredura e dirigida aos blocos descobertos",
                                  500, 950)]
        return []


class ZeroYieldMiddle(_Base):
    """C3 — o segmento do meio não produz nada. Tem de aparecer no rastro."""
    name = "zero_yield_middle"

    def extract(self, segment, context, iteration):
        if iteration:
            return []
        if segment.segment_id == "SEG-001":
            return [EvidenceDraft("declarar o resultado antes de construir", 0, 300)]
        if segment.segment_id == "SEG-003":
            return [EvidenceDraft("revisar o resultado contra o contrato", 600, 1000)]
        return []          # SEG-002: zero, de propósito


class BelowThreshold(_Base):
    """C4 — 0,50 no PASS 2. Tem de disparar revarredura e subir para 0,95."""
    name = "below_threshold"

    def extract(self, segment, context, iteration):
        if iteration == 0:
            return [EvidenceDraft("primeira unidade", 0, 500)] \
                if segment.segment_id == "SEG-001" else []
        if segment.segment_id == "SEG-002":
            return [EvidenceDraft("unidade achada na revarredura", 500, 950)]
        return []


class AboveThreshold(_Base):
    """C5 — 0,80 no PASS 2. Tem de encerrar SEM revarredura."""
    name = "above_threshold"

    def extract(self, segment, context, iteration):
        if iteration:
            # Se isto for chamado, o portão revarreu quando não devia.
            raise AssertionError("revarredura disparada acima do limiar")
        if segment.segment_id == "SEG-001":
            return [EvidenceDraft("primeira unidade", 0, 500)]
        return [EvidenceDraft("segunda unidade", 500, 800)]


CASES = {
    "C1_boundary_distinct": (BoundaryDistinct(), SEGS_2),
    "C2_true_duplicate": (TrueDuplicate(), SEGS_2),
    "C3_zero_yield_visible": (ZeroYieldMiddle(), SEGS_3),
    "C4_below_threshold_rescans": (BelowThreshold(), SEGS_2),
    "C5_above_threshold_stops": (AboveThreshold(), SEGS_2),
}


# ---------------------------------------------------------------- C6
# Fixture OBRIGATÓRIA da normalização de citação. Não passa pelo pipeline: exerce
# o validador do extractor real, que é onde a normalização vive.
#
# A pergunta que ela responde é a única que importa depois de afrouxar um
# casamento: a normalização recupera citação LEGÍTIMA sem deixar passar citação
# FABRICADA? Se a fabricada passar, o conserto virou afrouxamento.
SEG_C6 = Segment("SEG-001", 0, 60, "fixture de citação")

# Texto com as três coisas que quebravam o casamento estrito: marca inline,
# espaço duplo e quebra dupla entre blocos.
C6_TEXT = (
    "the outcome is simple. Every Monday morning,  \n\n"
    "**0:12**\n\n"
    "your team has a clear briefing on what the market  is doing.\n\n"
    "**0:20**\n\n"
    "It tracks trending topics."
)

# Legítima: existe na fonte, mas atravessa uma marca — o caso real das 5.
C6_QUOTE_LEGITIMA = ("Every Monday morning, your team has a clear briefing on "
                     "what the market is doing.")
# Legítima com a marca preservada, como 7 das 10 aceitas fizeram.
C6_QUOTE_COM_MARCA = ("the outcome is simple. Every Monday morning,  \n\n"
                      "**0:12**\n\nyour team has a clear briefing")
# FABRICADA LONGE: mesmo assunto e vocabulário, conteúdo inventado.
C6_QUOTE_FABRICADA = ("Every Monday morning, your team receives a detailed "
                      "report on what your competitors have launched.")
# FABRICADA PERTO: a fonte diz "what the market is doing"; esta diz "is
# planning". UMA palavra trocada, e ela inverte o que a fonte afirma.
#
# É esta que importa. Uma fabricação distante qualquer regra rejeita — inclusive
# uma regra ruim —, então testar só com ela dá um canário sem poder. A
# fabricação PRÓXIMA é a que um casamento difuso aceita e o exato rejeita, e é
# também a que causa dano real: evidência com citação quase certa é a que
# ninguém confere.
C6_QUOTE_FABRICADA_PROXIMA = ("your team has a clear briefing on what the "
                              "market is planning")
