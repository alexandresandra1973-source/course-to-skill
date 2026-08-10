"""Testes do módulo de cobertura de L0."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cts import coverage as C


def test_conversao_de_tempo():
    assert C.hhmmss_to_s("00:08:05") == 485
    assert C.mark_to_s("8:05") == 485
    assert C.fmt(485) == "8:05"
    assert C.fmt(60) == "1:00"


def test_merge_une_sobrepostos_e_adjacentes():
    cits = [C.Citation(0, 10, "evidence", "a"),
            C.Citation(5, 20, "evidence", "b"),
            C.Citation(30, 40, "evidence", "c")]
    m = C.merge(cits)
    assert [(b.start, b.end) for b in m] == [(0, 20), (30, 40)]


def test_merge_preserva_disjuntos():
    m = C.merge([C.Citation(0, 5, "x", "1"), C.Citation(10, 15, "x", "2")])
    assert len(m) == 2


def test_complemento_pega_inicio_meio_e_fim():
    cov = C.merge([C.Citation(10, 20, "x", "1"), C.Citation(30, 40, "x", "2")])
    gaps = C.complement(cov, 0, 60)
    assert [(g.start, g.end) for g in gaps] == [(0, 10), (20, 30), (40, 60)]


def test_complemento_vazio_quando_tudo_coberto():
    cov = C.merge([C.Citation(0, 100, "x", "1")])
    assert C.complement(cov, 0, 100) == []


def test_complemento_soma_com_cobertura_da_extensao():
    cov = C.merge([C.Citation(10, 20, "x", "1"), C.Citation(50, 55, "x", "2")])
    gaps = C.complement(cov, 0, 90)
    assert sum(b.dur for b in cov) + sum(g.dur for g in gaps) == 90


def test_texto_do_intervalo_pega_os_segmentos_certos():
    txt = "**0:00**\nalfa\n**0:10**\nbravo\n**0:20**\ncharlie\n"
    idx = C.mark_index(txt)
    assert C.text_for(txt, idx, 0, 10) == "alfa"
    assert C.text_for(txt, idx, 10, 30) == "bravo charlie"
    assert C.text_for(txt, idx, 100, 200) == ""


def test_triagem_marca_descarte_sem_metodo():
    v, m = C.classify("Everything we're talking about is covered in a free guide "
                      "HubSpot put together. Drop your time in the comments.")
    assert v == C.DESCARTE
    assert m["plug"] and m["cta"] and not m["metodo"]


def test_triagem_marca_candidato_com_metodo():
    v, m = C.classify("If you already use Zapier, make sure you review every output "
                      "for at least the first weeks.")
    assert v == C.CANDIDATO
    assert m["metodo"]


def test_triagem_plug_domina_marcador_de_metodo():
    """O outro do PILOT-001: tem 'if you' mas esta vendendo o guia."""
    v, m = C.classify("If you want to go deeper on any of this, I highly recommend "
                      "checking out the free guide.")
    assert m["metodo"] and m["plug"]
    assert v == C.DESCARTE
    assert m["_regra_v1_so_metodo"] == C.CANDIDATO   # divergencia registrada


def test_triagem_cta_domina_marcador_de_metodo():
    v, m = C.classify("Make sure you pause this and drop your time in the comments.")
    assert v == C.DESCARTE


def test_strip_de_heading_nao_injeta_marcador():
    txt = "## How to Build an AI Agent Step by Step\nso now you know what to build."
    v, m = C.classify(txt)
    assert "step " not in " ".join(m["metodo"])
    assert v == C.DESCARTE


def test_triagem_devolve_os_marcadores_para_auditoria():
    v, m = C.classify("")
    assert v == C.DESCARTE
    assert set(C.MARKERS) <= set(m)
    assert "_regra_v1_so_metodo" in m   # a regra antiga viaja junto, para diff


def test_marcadores_nao_sao_vazios():
    for k, v in C.MARKERS.items():
        assert v, k
