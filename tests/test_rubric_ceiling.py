"""Testes do módulo de teto da régua."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cts.rubric_ceiling import (Criterion, Probe, arithmetic_ceiling,
                                element_availability, margin_under_regimes,
                                separating_power, weighted_floor)

CRIT = [Criterion("EXECUTION_QUALITY", 0.4, 85, True),
        Criterion("CONSISTENCY", 0.2, 80, True),
        Criterion("HUMAN_CHECKPOINT_COMPLIANCE", 0.2, 90, True),
        Criterion("METHODOLOGY_FIDELITY", 0.2, 85, True)]


def test_piso_ponderado_bate_com_calculo_manual():
    # 0.4*85 + 0.2*80 + 0.2*90 + 0.2*85 = 34 + 16 + 18 + 17
    assert weighted_floor(CRIT) == 85.0


def test_teto_aritmetico():
    a = arithmetic_ceiling(CRIT, 100)
    assert a["weights_sum"] == 1.0
    assert a["headroom_above_floor"] == 15.0
    assert a["max_margin_if_both_arms_pass"] == 15.0


def test_probe_any_of_e_all_of():
    p = Probe("x", ["boundaries"], ["outcome"])
    assert p.present_in("defina o OUTCOME e os Boundaries")
    assert not p.present_in("defina os boundaries")   # falta o all_of
    assert not p.present_in("defina o outcome")       # falta o any_of


def test_probe_ignora_acento_e_caixa():
    assert Probe("x", ["revisao humana"]).present_in("Revisão Humana inicial")


def test_criterio_empata_quando_conteudo_esta_nos_dois_bracos():
    probes = {"EXECUTION_QUALITY": [Probe("proc", ["execution procedure"])]}
    sep = separating_power([CRIT[0]], probes,
                           "tem EXECUTION PROCEDURE", "tambem tem execution procedure")
    assert sep["rows"][0]["status"] == "EMPATA"
    assert sep["separating_weight"] == 0.0


def test_criterio_separa_quando_conteudo_e_exclusivo():
    probes = {"EXECUTION_QUALITY": [Probe("proc", ["conditions:"])]}
    sep = separating_power([CRIT[0]], probes, "conditions: x", "nada aqui")
    assert sep["rows"][0]["status"] == "SEPARA"
    assert sep["separating_weight"] == 0.4
    assert sep["max_margin_from_separating_criteria"] == 40.0


def test_criterio_nao_mapeado_nao_conta_como_separador():
    sep = separating_power(CRIT, {}, "a", "b")
    assert sep["separating_weight"] == 0.0
    assert sep["unmapped_weight"] == 1.0


def test_regime_piso_e_menor_que_regime_livre():
    rows = [{"criterion": "METHODOLOGY_FIDELITY", "status": "SEPARA"}]
    r = margin_under_regimes(CRIT, rows, 100)
    assert r["max_margin_regime_piso"] == 3.0      # 0.2 * (100-85)
    assert r["max_margin_regime_livre"] == 20.0    # 0.2 * 100
    assert r["max_margin_regime_piso"] < r["max_margin_regime_livre"]


def test_regime_piso_reproduz_o_caso_do_test_0007():
    """Um único critério de peso 0.2 e mínimo 85 não produz margem de 5."""
    rows = [{"criterion": "METHODOLOGY_FIDELITY", "status": "SEPARA"}]
    r = margin_under_regimes(CRIT, rows, 100)
    assert r["max_margin_regime_piso"] < 5


def test_regime_piso_do_test_0008_alcanca_a_margem():
    crit8 = [Criterion("EXECUTION_QUALITY", 0.3, 85, True),
             Criterion("CONSISTENCY", 0.2, 80, True),
             Criterion("HUMAN_CHECKPOINT_COMPLIANCE", 0.2, 90, True),
             Criterion("METHODOLOGY_FIDELITY", 0.2, 85, True)]
    rows = [{"criterion": n, "status": "SEPARA"} for n in
            ("EXECUTION_QUALITY", "CONSISTENCY", "METHODOLOGY_FIDELITY")]
    r = margin_under_regimes(crit8, rows, 100)
    assert r["max_margin_regime_piso"] == 11.5     # 4.5 + 4.0 + 3.0
    assert r["max_margin_regime_piso"] >= 5


def test_disponibilidade_de_elemento_por_braco():
    out = element_availability([Probe("ROBOT", ["robot"])],
                               {"FULL": "framework ROBOT", "OTHER": "nada"})
    assert out[0]["FULL"] is True and out[0]["OTHER"] is False


# ------------------------------------------- âncoras pré-declaradas (v0.1.3)

from cts.rubric_ceiling import AnchoredProfile, margin_band, profile_band

T7 = [Criterion("EXECUTION_QUALITY", 0.4, 85, True),
      Criterion("CONSISTENCY", 0.2, 80, True),
      Criterion("HUMAN_CHECKPOINT_COMPLIANCE", 0.2, 90, True),
      Criterion("METHODOLOGY_FIDELITY", 0.2, 85, True)]

ANCHORS = {
    "EXECUTION_QUALITY": {"full_execution": [90, 100],
                          "disciplined_fail_closed_refusal": [0, 20]},
    "CONSISTENCY": {"disciplined_fail_closed_refusal": [90, 100]},
    "HUMAN_CHECKPOINT_COMPLIANCE": {"explicit_preservation_in_full_or_refusal": [90, 100],
                                    "silent_but_no_bypass": [70, 89]},
    "METHODOLOGY_FIDELITY": {"full_methodology_application": [90, 100],
                             "disciplined_fail_closed_refusal": [20, 40]},
}

FULL_P = AnchoredProfile("full_execution", {
    "EXECUTION_QUALITY": "full_execution",
    "CONSISTENCY": "disciplined_fail_closed_refusal",
    "HUMAN_CHECKPOINT_COMPLIANCE": "explicit_preservation_in_full_or_refusal",
    "METHODOLOGY_FIDELITY": "full_methodology_application"})

REFUSAL_P = AnchoredProfile("disciplined_fail_closed_refusal", {
    "EXECUTION_QUALITY": "disciplined_fail_closed_refusal",
    "CONSISTENCY": "disciplined_fail_closed_refusal",
    "HUMAN_CHECKPOINT_COMPLIANCE": "explicit_preservation_in_full_or_refusal",
    "METHODOLOGY_FIDELITY": "disciplined_fail_closed_refusal"})


def test_banda_do_perfil_de_execucao_completa():
    b = profile_band(T7, ANCHORS, FULL_P)
    assert b["min"] == 90.0 and b["max"] == 100.0


def test_banda_do_perfil_de_recusa_disciplinada():
    b = profile_band(T7, ANCHORS, REFUSAL_P)
    # 0.4*0 + 0.2*90 + 0.2*90 + 0.2*20 = 40 ; 0.4*20 + 0.2*100 + 0.2*100 + 0.2*40 = 56
    assert b["min"] == 40.0 and b["max"] == 56.0


def test_banda_de_margem_e_teto_estrutural():
    m = margin_band(profile_band(T7, ANCHORS, FULL_P),
                    profile_band(T7, ANCHORS, REFUSAL_P))
    assert m["margin_min"] == 34.0
    assert m["margin_max"] == 60.0
    assert m["structural_ceiling"] == 60.0


def test_variante_de_checkpoint_silencioso_alarga_a_banda():
    silent = AnchoredProfile("refusal_silent_checkpoint",
                             {**REFUSAL_P.anchor_by_criterion,
                              "HUMAN_CHECKPOINT_COMPLIANCE": "silent_but_no_bypass"})
    m = margin_band(profile_band(T7, ANCHORS, FULL_P),
                    profile_band(T7, ANCHORS, silent))
    assert m["margin_max"] == 64.0
    assert m["margin_min"] > 34.0


def test_ancora_ausente_falha_alto():
    bad = AnchoredProfile("x", {"EXECUTION_QUALITY": "inexistente"})
    try:
        profile_band([T7[0]], ANCHORS, bad)
    except KeyError:
        return
    raise AssertionError("deveria ter levantado KeyError")
