"""Meta-testes: cada portão nasce com um fixture que o faz DISPARAR e um que o
faz PASSAR. É assim que se prova que um portão novo funciona (Fase 3, §8).

Os fixtures negativos incluem o caso REAL conhecido: EV-0001, cuja marca de fim
'0:29' não existe entre as 180 marcas do transcript. Se o portão não reprovar
esse caso, o portão está quebrado.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cts import cutter
from cts.dispersion import measure
from cts.gates import g2_anchor, g3_dispersion, g5_closure, g6_ceiling
from cts.vault import Vault

TMP = Path(__file__).parent / "_tmp"
DOMAINS = {"f.x": 3, "f.y": 5}


def _vault(tmpdir: Path) -> tuple[Vault, str]:
    tmpdir.mkdir(parents=True, exist_ok=True)
    src = tmpdir / "src.txt"
    src.write_text("**0:00**\nalpha bravo\n**0:10**\ncharlie delta\n**0:20**\necho\n",
                   encoding="utf-8")
    v = Vault(tmpdir / "vault")
    o = v.ingest(src, "text/plain")
    return v, o.sha256


# ------------------------------------------------------------------ G2

def test_g2_passa_com_quote_verbatim():
    v, sha = _vault(TMP / "g2p")
    rec = [{"id": "X-1", "spans": [f"L0:{sha[:12]}:t=00:00:00-00:00:10"],
            "quote": "alpha bravo", "claim": "algo"}]
    r = g2_anchor.run(v, rec, "fixture")
    assert r.state == "PASS", r.evidence
    assert r.evidence["records_anchored_ok"] == 1


def test_g2_reprova_sem_quote():
    v, sha = _vault(TMP / "g2a")
    rec = [{"id": "X-1", "spans": [f"L0:{sha[:12]}:t=00:00:00-00:00:10"],
            "quote": None, "claim": "algo"}]
    r = g2_anchor.run(v, rec, "fixture")
    assert r.state == "FAIL"
    assert r.evidence["records_without_quote"] == 1


def test_g2_reprova_quote_que_nao_esta_no_span():
    v, sha = _vault(TMP / "g2b")
    rec = [{"id": "X-1", "spans": [f"L0:{sha[:12]}:t=00:00:00-00:00:10"],
            "quote": "texto que nao existe na fonte", "claim": "algo"}]
    r = g2_anchor.run(v, rec, "fixture")
    assert r.state == "FAIL"
    assert r.evidence["records_quote_mismatch"] == 1


def test_g2_reprova_marca_de_fim_inexistente():
    """Reproduz o caso real EV-0001: marca de fim ausente no objeto."""
    v, sha = _vault(TMP / "g2c")
    rec = [{"id": "EV-like", "spans": [f"L0:{sha[:12]}:t=00:00:00-00:00:29"],
            "quote": "alpha bravo", "claim": "algo"}]
    r = g2_anchor.run(v, rec, "fixture")
    assert r.state == "FAIL"
    assert r.evidence["resolution_reasons"].get("END_MARK_NOT_FOUND") == 1


def test_g2_reprova_objeto_fora_do_vault():
    v, _ = _vault(TMP / "g2d")
    rec = [{"id": "X-1", "spans": ["L0:deadbeefcafe:t=00:00:00-00:00:10"],
            "quote": "alpha", "claim": "algo"}]
    r = g2_anchor.run(v, rec, "fixture")
    assert r.state == "FAIL"
    assert r.evidence["resolution_reasons"].get("OBJECT_NOT_IN_VAULT") == 1


# ------------------------------------------------------------------ G3

def test_g3_reprova_campo_colapsado():
    r = g3_dispersion.run({"evidence.origin_class": ["A"] * 25},
                          {"evidence.origin_class": 3}, "fixture")
    assert r.state == "FAIL"
    assert r.evidence["collapsed_epistemic_blocking"] == 1


def test_g3_passa_com_dispersao():
    vals = (["A"] * 9 + ["B"] * 8 + ["C"] * 8)
    r = g3_dispersion.run({"evidence.origin_class": vals},
                          {"evidence.origin_class": 3}, "fixture")
    assert r.state == "PASS", r.evidence["table"]


def test_g3_nao_conclui_com_base_pequena():
    r = g3_dispersion.run({"decision.origin_class": ["A"] * 8},
                          {"decision.origin_class": 2}, "fixture")
    assert r.evidence["underpowered"] == 1
    assert r.evidence["collapsed"] == 0


def test_g3_status_operacional_nao_bloqueia():
    r = g3_dispersion.run({"evidence.status": ["ACTIVE"] * 25},
                          {"evidence.status": 5}, "fixture")
    assert r.evidence["collapsed"] == 1
    assert r.evidence["collapsed_epistemic_blocking"] == 0
    assert r.state != "FAIL"


def test_g3_entropia_bate_com_calculo_manual():
    m = measure("f.x", ["A"] * 37 + ["B"] * 4 + ["C"] * 3, 5)
    assert abs(m.entropy_bits - 0.789) < 0.002
    assert abs(m.h_norm - 0.340) < 0.002


# ------------------------------------------------------------------ G5

def _noop(s):
    return (s or "").strip().lower()


def test_g5_reprova_invencao_do_compilador():
    r = g5_closure.run(bundle_claims={"k.yaml": ["regra A", "regra INVENTADA"]},
                       audited_claims={"a.yaml": ["regra A"]},
                       normalize=_noop, subject="fixture")
    assert r.state == "FAIL"
    assert r.evidence["compiler_invention_count"] == 1


def test_g5_passa_com_subconjunto():
    r = g5_closure.run(bundle_claims={"k.yaml": ["regra A"]},
                       audited_claims={"a.yaml": ["regra A", "regra B"]},
                       normalize=_noop, subject="fixture")
    assert r.state == "PASS"


def test_g5_reprova_rubrica_que_cita_id_interno():
    r = g5_closure.run(bundle_claims={}, audited_claims={}, normalize=_noop,
                       subject="fixture",
                       rubric_text="scope: ADR-0003 e EV-0027")
    assert r.state == "FAIL"
    assert r.evidence["rubric_internal_id_kinds"] == 2


def test_g5_reprova_vazamento_de_holdout():
    r = g5_closure.run(bundle_claims={}, audited_claims={}, normalize=_noop,
                       subject="fixture",
                       holdout_spans=["L0:aaaaaaaaaaaa:t=00:08:00-00:08:30"],
                       artifact_spans=["L0:aaaaaaaaaaaa:t=00:08:05-00:08:20"])
    assert r.state == "FAIL"
    assert r.evidence["holdout_leak_count"] == 1


# ------------------------------------------------------------------ Cutter

def test_cutter_e_deterministico_e_remove_do_treino():
    v, sha = _vault(TMP / "cut")
    segs = cutter.segment_by_marks(v, sha)
    a = cutter.cut(segs, 42, 0.5)
    b = cutter.cut(segs, 42, 0.5)
    assert a["sha256"] == b["sha256"]
    train = cutter.train_corpus(segs, a)
    assert len(train) + a["n_holdout"] == len(segs)
    assert cutter.corpus_hash(train) != cutter.corpus_hash(segs)


def test_cutter_marca_cego_sem_lock_como_contaminado():
    reg = {"registry_status": "NOT_AVAILABLE", "created_before_modeling": False,
           "locked": False, "cases": []}
    out = cutter.retroactive_audit(reg, [{"case_id": "T-9",
                                          "declared_type": "BLIND_EVALUATION",
                                          "support_spans": ["L0:aaaaaaaaaaaa:t=00:08:05-00:08:20"]}])
    assert out["established"] is False
    assert out["verdicts"][0]["verdict"] == "CONTAMINATED_BY_CONSTRUCTION"


def test_cutter_aceita_cego_legitimo():
    reg = {"registry_status": "ACTIVE", "created_before_modeling": True,
           "locked": True, "cases": ["c1"],
           "spans": ["L0:aaaaaaaaaaaa:t=00:08:00-00:08:30"]}
    out = cutter.retroactive_audit(reg, [{"case_id": "T-9",
                                          "declared_type": "BLIND_EVALUATION",
                                          "support_spans": ["L0:aaaaaaaaaaaa:t=00:08:05-00:08:20"]}])
    assert out["established"] is True
    assert out["verdicts"][0]["verdict"] == "HELD_OUT_OK"


def test_cutter_detecta_recall_disfarcado_de_cego():
    reg = {"registry_status": "ACTIVE", "created_before_modeling": True,
           "locked": True, "cases": ["c1"],
           "spans": ["L0:aaaaaaaaaaaa:t=00:01:00-00:01:30"]}
    out = cutter.retroactive_audit(reg, [{"case_id": "T-9",
                                          "declared_type": "BLIND_EVALUATION",
                                          "support_spans": ["L0:aaaaaaaaaaaa:t=00:08:05-00:08:20"]}])
    assert out["verdicts"][0]["verdict"] == "RECALL_NOT_HELDOUT"


# ------------------------------------------------------------------ G6

def test_g6_n_minimo_e_calculado():
    assert g6_ceiling.min_n_for(0.80) == 16
    assert g6_ceiling.wilson_lower_perfect(16) >= 0.80
    assert g6_ceiling.wilson_lower_perfect(15) < 0.80


def test_g6_recusa_s4_sem_holdout():
    class R:
        state = "PASS"
        evidence: dict = {}
    r = g6_ceiling.run(vault_sealed=True, g2=R(), g3=R(), g4=R(), g5=R(),
                       n_holdout=0, threshold=0.80, requested_level="S5_VALIDATED",
                       subject="fixture", corpus_stats={})
    assert r.state == "FAIL"
    assert r.evidence["ceiling_reached"] == "S4_CLOSED"
    assert r.evidence["production_ready_allowed"] is False


def test_g6_recusa_s1_quando_g2_reprova():
    class OK:
        state = "PASS"
        evidence: dict = {}

    class BAD:
        state = "FAIL"
        evidence = {"records": 44, "records_anchored_ok": 0}
    r = g6_ceiling.run(vault_sealed=True, g2=BAD(), g3=OK(), g4=OK(), g5=OK(),
                       n_holdout=99, threshold=0.80, requested_level="S1_ANCHORED",
                       subject="fixture", corpus_stats={})
    assert r.state == "FAIL"
    assert r.evidence["ceiling_reached"] == "S0_INGESTED"


def test_g6_concede_s5_com_corpus_suficiente():
    class OK:
        state = "PASS"
        evidence: dict = {}
    r = g6_ceiling.run(vault_sealed=True, g2=OK(), g3=OK(), g4=OK(), g5=OK(),
                       n_holdout=16, threshold=0.80, requested_level="S5_VALIDATED",
                       subject="fixture", corpus_stats={})
    assert r.state == "PASS"
    assert r.evidence["production_ready_allowed"] is True


# ------------------------------------------------------------------ contrato

def test_portao_nunca_devolve_booleano_nu():
    v, sha = _vault(TMP / "contract")
    r = g2_anchor.run(v, [{"id": "a", "spans": [], "quote": None, "claim": "x"}],
                      "fixture")
    assert isinstance(r.state, str) and r.state in ("PASS", "FAIL", "WARN",
                                                    "UNDERPOWERED",
                                                    "NOT_ESTABLISHED", "DATA_DEFECT")
    assert r.subject and isinstance(r.evidence, dict) and r.evidence
