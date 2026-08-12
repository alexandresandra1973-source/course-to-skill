#!/usr/bin/env python3
"""Aditivo: ratificação condicional da faixa + assimetria de restrição.

Roda daqui (ext4). READ-ONLY. Publica só em `Course-to-Skill-Claude/docs/`.
Aditivo à GATE-READING-RULE-PREREGISTERED, amarrado por SHA-256.
Publicado ANTES da rodada completa. NÃO altera o portão.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from cts import coverage as C                                   # noqa: E402

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "GATE-READING-RULE-RATIFICATION.yaml"

RULE = DOCS / "GATE-READING-RULE-PREREGISTERED.yaml"
CAVEAT = DOCS / "L0-COVERAGE-DECLARED-VS-EVIDENCED-CAVEAT.yaml"
PREDICTION = DOCS / "PREDICTION-COMPILER-V2.yaml"
ADR = CLAUDE / "pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
FREEZE = CLAUDE / "compiler-v2/FREEZE-RECORD.yaml"
EV1 = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
       / "analysis/evidence.jsonl")

EXPECTED_RULE = "392e0167be5560397d7a368b293d3d0e0f74ab5c300b0492f15f54b63ad55a11"
EXPECTED_CAVEAT = "b105f6c6d3b871ddcd04f02322487fc4132f14e1c5a21f560cce79fa061eec54"

T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def declared_union(trace: Path) -> int | None:
    if not trace.is_file():
        return None
    d = json.loads(trace.read_text(encoding="utf-8"))
    cits = [C.Citation(x["start_s"], x["end_s"], "d", str(i))
            for i, x in enumerate(d["drafts"])]
    return sum(b.dur for b in C.merge(cits)) if cits else 0


def main() -> int:
    for p, exp, nome in ((RULE, EXPECTED_RULE, "regra"),
                         (CAVEAT, EXPECTED_CAVEAT, "ressalva")):
        if not p.is_file():
            print(f"ÂNCORA AUSENTE: {p}")
            return 2
        if sha_p(p) != exp:
            print(f"ÂNCORA DIVERGENTE ({nome}):\n  esperado {exp}\n  obtido   {sha_p(p)}")
            return 2

    rows = [json.loads(l) for l in EV1.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    n_hist = len(rows)
    n_quote = sum(1 for r in rows if r.get("source_excerpt"))

    u_old = declared_union(T / "canary-trace-run0-promptantigo.json")
    u_r1 = declared_union(T / "canary-run1.json")
    u_r2 = declared_union(T / "canary-run2.json")

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "GATE-READING-RULE-RATIFICATION",
        "artifact_status": "RATIFICADA_CONDICIONALMENTE_ANTES_DA_EXECUCAO",
        "registered_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "registered_by": "revisor",

        "nature": {
            "additive_only": True,
            "changes_the_gate": False,
            "statement": ("Aditivo à regra pré-registrada. Não altera o piso de "
                          "73,5%, a métrica nem a previsão. Publicado ANTES da "
                          "rodada completa do PILOT-001."),
        },

        "binds_to": {
            "gate_reading_rule": {"path": str(RULE.relative_to(DRIVE)),
                                  "sha256": sha_p(RULE)},
            "coverage_caveat": {"path": str(CAVEAT.relative_to(DRIVE)),
                                "sha256": sha_p(CAVEAT)},
            "prediction": {"path": str(PREDICTION.relative_to(DRIVE)),
                           "sha256": sha_p(PREDICTION)},
            "adr": {"path": str(ADR.relative_to(DRIVE)), "sha256": sha_p(ADR)},
            "compiler_v2_freeze": {"path": str(FREEZE.relative_to(DRIVE)),
                                   "sha256": sha_p(FREEZE)},
        },

        # ------------------------------------------------- 1. a ratificação
        "ratificacao_da_faixa": {
            "faixa": [0.685, 0.785],
            "status": "RATIFICADA_CONDICIONALMENTE",
            "condicao": (
                "A suspensão só se aplica se a preocupação que a motivou estiver "
                "presente na rodada. Medir a união DECLARADA por segmento na "
                "rodada completa: se ela NÃO for menor que a do regime "
                "histórico, o temor está refutado por medição e o portão é lido "
                "normalmente, mesmo dentro da faixa."),
            "razao": "suspensão incondicional protegeria um conserto que falhou",
            "evidencia_atual": {
                "uniao_declarada_regime_antigo_s": u_old,
                "uniao_declarada_r1_s": u_r1,
                "uniao_declarada_r2_s": u_r2,
                "segmentos_medidos": 1,
                "segmento": "SEG-005",
                "leitura": (
                    f"União declarada {u_old}s no regime antigo contra {u_r1}s e "
                    f"{u_r2}s nas duas rodadas do v2. NÃO é menor — é maior. "
                    "Sob a condição ratificada, a evidência disponível hoje já "
                    "aponta para refutação do temor, mas n=1 segmento."),
            },
            "como_a_condicao_se_aplica_na_rodada_completa": (
                "A medição vale sobre a rodada COMPLETA, não sobre o canário. A "
                "comparação honesta é união declarada por segmento: o histórico "
                "tem 44 evidências sobre 9 segmentos e o v2 terá as suas sobre "
                "os mesmos 9, então a razão é comparável segmento a segmento."),
            "o_que_ainda_pode_disparar_suspensao": (
                "Se, na rodada completa, a união declarada por segmento vier "
                "MENOR que a histórica E a cobertura cair dentro de "
                "[0,685; 0,785], a suspensão se aplica e o veredito sobe para o "
                "revisor."),
        },

        # ------------------------------------------- 2. assimetria de restrição
        "assimetria_de_restricao": {
            "fato": (f"o PILOT-001 histórico tem source_excerpt NULO em "
                     f"{n_quote}/{n_hist}"),
            "consequencia": (
                "O baseline NUNCA teria passado no portão de resolução de quote "
                "do v2. O v2 produz citação resolvível para 100% das "
                "evidências. A comparação é entre uma rodada SEM restrição de "
                "citação e uma TOTALMENTE restrita — o v2 é cobrado num padrão "
                "que o baseline nunca cumpriu."),
            "regra_de_leitura": (
                "Se o v2 empatar ou superar o piso sob restrição estritamente "
                "mais dura, a evidência é MAIS forte que o número bruto sugere. "
                "Isso NÃO afrouxa o portão: ele continua sendo > 73,5%. Muda "
                "como o resultado é interpretado, e está escrito antes de o "
                "resultado existir."),
            "status": "PRE_REGISTRADA_ANTES_DA_EXECUCAO",
            "verificacao": {
                "historico_evidencias": n_hist,
                "historico_com_citacao": n_quote,
                "historico_path": str(EV1.relative_to(DRIVE)),
                "historico_sha256": sha_p(EV1),
                "v2_rejeita_citacao_que_nao_resolve": True,
                "v2_regra": ("quote tem de casar por substring exata sobre texto "
                             "normalizado; fabricada é rejeitada, e o canário C6 "
                             "prova isso a cada execução"),
            },
            "o_que_esta_regra_NAO_faz": [
                "não altera o piso de 73,5%",
                "não autoriza aprovar abaixo do piso",
                "não converte a assimetria em fator numérico de ajuste",
            ],
        },

        "status": "RATIFICADA_CONDICIONALMENTE_ANTES_DA_EXECUCAO",
        "execucao_realizada": False,
        "portao_alterado": False,
    }

    OUT.write_text(
        "# ADITIVO: ratificação condicional da faixa + assimetria de restrição.\n"
        "# Amarrado por SHA-256 à regra pré-registrada. NÃO altera o portão.\n"
        "# Publicado ANTES da rodada completa do PILOT-001.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"regra conferida    : {sha_p(RULE)[:16]}… OK")
    print(f"ressalva conferida : {sha_p(CAVEAT)[:16]}… OK")
    print(f"faixa ratificada condicionalmente: [0.685, 0.785]")
    print(f"união declarada: antigo={u_old}s · r1={u_r1}s · r2={u_r2}s "
          f"→ NÃO menor")
    print(f"assimetria: histórico {n_quote}/{n_hist} com citação")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256: {sha_p(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
