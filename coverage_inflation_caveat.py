#!/usr/bin/env python3
"""Ressalva: a métrica de cobertura de L0 conta SPAN DECLARADO, não evidenciado.

Roda daqui (ext4). READ-ONLY. Publica só em `Course-to-Skill-Claude/docs/`.

NÃO altera o portão. Amarra-se por SHA-256 ao PREDICTION e à ADR para que quem
ler 73,5% ou 37,2% saiba o que o número mede.

O achado nasce do canário do SEG-005: a `quote` de uma evidência sustenta
tipicamente cerca de metade do intervalo que a evidência DECLARA. Como o
numerador da cobertura é a união dos intervalos declarados, e nada verifica que
a citação cubra o intervalo, a cobertura mede território DECLARADO — não
território EXIBIDO.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from cts import coverage as C                                     # noqa: E402

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
CLAUDE = DRIVE / "Course-to-Skill-Claude"
DOCS = CLAUDE / "docs"
OUT = DOCS / "L0-COVERAGE-DECLARED-VS-EVIDENCED-CAVEAT.yaml"

PREDICTION = DOCS / "PREDICTION-COMPILER-V2.yaml"
RATIFICATION = DOCS / "PREDICTION-COMPILER-V2-BAND-RATIFICATION.yaml"
CORRECTION = DOCS / "PREDICTION-COMPILER-V2-BAND-CORRECTION.yaml"
ADR = CLAUDE / "pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
FREEZE = CLAUDE / "compiler-v2/FREEZE-RECORD.yaml"
COVERAGE_MODULE = Path(__file__).parent / "cts/coverage.py"

TRACE = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude"
             "/canary-trace-run0-promptantigo.json")
L0 = (DRIVE / "Course-to-Skill/pilots/PILOT-001-HubSpot-AI-Agent"
      / "sources/transcript/transcript-original-en.txt")

EXPECTED = {
    PREDICTION: "4963fd27d4640c4831306e74b0dc9f624ef5fe409f6c46f48c7f46fbeda1b44d",
    ADR: "b8cddc93b74a65d6cbc2ad6859e4e3b8a4a81404137d4f95260f1b92668cf3f8",
}
MARK = re.compile(r"\*\*(\d{1,3}):([0-5]\d)\*\*")


def sha_p(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm(s: str) -> str:
    return " ".join(MARK.sub(" ", s).split())


def measure() -> dict:
    """Mede, no rastro real do canário, declarado × sustentado."""
    d = json.loads(TRACE.read_text(encoding="utf-8"))
    drafts = d["drafts"]

    blocks = L0.read_text(encoding="utf-8").split("\n\n")
    idx = [(i, int(m.group(1)) * 60 + int(m.group(2)))
           for i, b in enumerate(blocks) if (m := MARK.fullmatch(b.strip()))]
    keep = []
    for k, (i, s) in enumerate(idx):
        if 340 <= s < 450:
            end = idx[k + 1][0] if k + 1 < len(idx) else len(blocks)
            keep.extend(blocks[i:end])
    seg_raw = "\n\n".join(keep)
    seg_norm = norm(seg_raw)

    pos, mpos = 0, []
    for part in re.split(r"(\*\*\d{1,3}:[0-5]\d\*\*)", seg_raw):
        m = MARK.fullmatch(part)
        if m:
            mpos.append((pos, int(m.group(1)) * 60 + int(m.group(2))))
        else:
            n = norm(part)
            pos += len(n) + (1 if n else 0)

    def qspan(q):
        qn = norm(q)
        at = seg_norm.find(qn)
        if at < 0:
            return None
        a, b = at, at + len(qn)
        before = [s for p, s in mpos if p <= a]
        inside = [s for p, s in mpos if a <= p <= b]
        st = before[-1] if before else mpos[0][1]
        en = inside[-1] if inside else st
        return (st, en if en > st else st + 1)

    decl = [C.Citation(x["start_s"], x["end_s"], "d", str(i))
            for i, x in enumerate(drafts)]
    spans = [(i, qspan(x["quote"])) for i, x in enumerate(drafts)]
    sup = [C.Citation(a, b, "s", str(i)) for i, sp in spans if sp
           for a, b in [sp]]
    ud = sum(b.dur for b in C.merge(decl))
    us = sum(b.dur for b in C.merge(sup))
    ratios = sorted((sp[1] - sp[0]) / (drafts[i]["end_s"] - drafts[i]["start_s"])
                    for i, sp in spans if sp)
    return {
        "fonte_do_rastro": str(TRACE),
        "piloto": "PILOT-001", "segmento": "SEG-005",
        "evidencias": len(drafts),
        "com_quote_localizavel": len(sup),
        "uniao_declarada_s": ud,
        "uniao_sustentada_s": us,
        "razao_uniao": round(us / ud, 3) if ud else None,
        "razao_por_evidencia": {
            "mediana": round(ratios[len(ratios) // 2], 2),
            "min": round(min(ratios), 2), "max": round(max(ratios), 2)},
    }


def main() -> int:
    for p, exp in EXPECTED.items():
        if not p.is_file():
            print(f"ÂNCORA AUSENTE: {p}")
            return 2
        if sha_p(p) != exp:
            print(f"ÂNCORA DIVERGENTE: {p}\n  esperado {exp}\n  obtido   {sha_p(p)}")
            return 2
    if not TRACE.is_file():
        print(f"RASTRO AUSENTE: {TRACE} — a ressalva precisa da medição real.")
        return 2

    m = measure()
    hist = Fraction(735, 1000)

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "L0-COVERAGE-DECLARED-VS-EVIDENCED-CAVEAT",
        "artifact_status": "RESSALVA_PUBLICADA_ANTES_DA_RECOMPILACAO",
        "published_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,

        "nature": {
            "additive_only": True,
            "changes_the_gate": False,
            "statement": ("Ressalva. NÃO altera o piso de 73,5%, não altera a "
                          "métrica e não altera a previsão. Registra o que o "
                          "número mede, para quem for lê-lo."),
        },

        "binds_to": {
            "prediction": {"path": str(PREDICTION.relative_to(DRIVE)),
                           "sha256": sha_p(PREDICTION)},
            "adr": {"path": str(ADR.relative_to(DRIVE)), "sha256": sha_p(ADR)},
            "band_ratification": {"path": str(RATIFICATION.relative_to(DRIVE)),
                                  "sha256": sha_p(RATIFICATION)}
            if RATIFICATION.is_file() else None,
            "band_correction": {"path": str(CORRECTION.relative_to(DRIVE)),
                                "sha256": sha_p(CORRECTION)}
            if CORRECTION.is_file() else None,
            "compiler_v2_freeze": {"path": str(FREEZE.relative_to(DRIVE)),
                                   "sha256": sha_p(FREEZE)},
            "coverage_metric_module": {"path": "cts/coverage.py",
                                       "sha256": sha_p(COVERAGE_MODULE)},
        },

        # -------------------------------------------------------- o achado
        "achado": {
            "o_que_a_metrica_conta": (
                "O numerador da cobertura de L0 é a UNIÃO DOS SPANS DECLARADOS "
                "pelas evidências — `start`/`end` de cada registro. Nada no "
                "pipeline verifica que a `quote` da evidência cubra o intervalo "
                "que ela declara."),
            "o_que_foi_medido": (
                "No canário do SEG-005 do PILOT-001, a citação exibida sustenta "
                f"{m['razao_uniao']:.1%} da união dos intervalos declarados. Por "
                f"evidência, a mediana é {m['razao_por_evidencia']['mediana']:.2f} "
                f"(min {m['razao_por_evidencia']['min']:.2f}, max "
                f"{m['razao_por_evidencia']['max']:.2f})."),
            "consequencia": (
                "73,5% e 37,2% medem território que as evidências DECLARAM "
                "cobrir, não território que elas EXIBEM. O portão `> 73,5%` "
                "herda a mesma inflação, porque compara dois números computados "
                "da mesma forma."),
        },

        "medicao": m,

        # ------------------------------------------------------- os limites
        "o_que_esta_ressalva_NAO_estabelece": [
            "que o fator de inflação seja 0,51 no corpus inteiro — foi medido em "
            "UM segmento, 10 evidências, UMA rodada, sob o prompt ANTIGO",
            "que a cobertura evidenciada do PILOT-001 histórico seja 73,5% × 0,51",
            "que o portão deva mudar",
            "que a métrica esteja errada — ela mede o que mede, de forma "
            "consistente; o que faltava era dizer o que é",
        ],
        "por_que_nao_extrapolo": (
            "A união de spans declarados não escala linearmente com a união de "
            "spans sustentados: spans declarados que se sobrepõem colapsam na "
            "união, e spans sustentados podem colapsar em proporção diferente. "
            "Multiplicar 73,5% por 0,51 seria inventar um número."),

        # --------------------------------------------- o risco para o portão
        "risco_para_a_comparacao_do_portao": {
            "por_que_a_comparacao_ainda_vale": (
                "O piso de 73,5% e a cobertura da rodada corrigida usam a MESMA "
                "definição de métrica, congelada em `cts/coverage.py` e pinada "
                "por hash. Comparar dois números igualmente inflados continua "
                "sendo comparação válida."),
            "onde_ela_quebra": (
                "Se o compilador corrigido declarar spans mais APERTADOS que o "
                "antigo — plausível, porque a extração por segmento produz "
                "unidades mais estreitas — a inflação cai, e a cobertura "
                "corrigida fica SUBESTIMADA em relação ao piso histórico. O "
                "portão ficaria mais difícil de passar sem que nada tenha "
                "piorado. O erro, nesse caso, é conservador: reprova quem "
                "merecia passar, não o contrário."),
            "o_que_mediria_isso": (
                "Aplicar a mesma medição declarado×sustentado às 44 evidências "
                "do PILOT-001 histórico e às da rodada corrigida, e comparar os "
                "dois fatores de inflação. Só então se sabe se a comparação do "
                "portão é entre iguais."),
            "estado": "NAO_MEDIDO",
        },

        "recomendacao": (
            "Manter o portão como está para a primeira rodada corrigida — mudar "
            "limiar depois de ver resultado continua proibido. Reportar, junto "
            "com a cobertura, o fator declarado×sustentado das duas pontas, para "
            "que a comparação seja lida com o que ela tem de ressalva."),

        "status": "RESSALVA_PUBLICADA_ANTES_DA_RECOMPILACAO",
        "portao_alterado": False,
    }

    OUT.write_text(
        "# RESSALVA — a cobertura de L0 conta SPAN DECLARADO, não evidenciado.\n"
        "# NÃO altera o portão, a métrica nem a previsão. Amarrada por SHA-256.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"união declarada  : {m['uniao_declarada_s']}s")
    print(f"união sustentada : {m['uniao_sustentada_s']}s")
    print(f"razão            : {m['razao_uniao']}")
    print(f"por evidência    : mediana {m['razao_por_evidencia']['mediana']} "
          f"(min {m['razao_por_evidencia']['min']}, max {m['razao_por_evidencia']['max']})")
    print(f"portão alterado  : não")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256: {sha_p(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
