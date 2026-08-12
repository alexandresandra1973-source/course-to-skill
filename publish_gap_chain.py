#!/usr/bin/env python3
"""COURSE-GAP-REPORT com a CADEIA + registro das correções impostas pela medição."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); DOCS = DRIVE / "Course-to-Skill-Claude/docs"
T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
S = json.loads((T/"mi-split-v2.json").read_text(encoding="utf-8"))
L = json.loads((T/"distance-lines.json").read_text(encoding="utf-8"))["lines"]
G = json.loads((T/"gap-measure.json").read_text(encoding="utf-8"))
OUT = DOCS / "COURSE-GAP-CHAIN.md"
COR = DOCS / "MEASUREMENT-CORRECTIONS.yaml"


def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ts(s): return f"{s//60}:{s%60:02d}"


def real(pid):
    return [e for e in S[pid]["genuina"]
            if not L[e["evidence_id"]].startswith("sem distância")]


def para(pid):
    return [e for e in S[pid]["genuina"]
            if L[e["evidence_id"]].startswith("sem distância")]


# ------------------------------------------------------- correções registradas
cor = {
    "schema_version": "0.1.0",
    "artifact_id": "MEASUREMENT-IMPOSED-CORRECTIONS",
    "artifact_status": "REGISTRADO",
    "registered_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "nota": ("Correções que a medição impôs a crenças que vinham sendo carregadas. "
             "Registradas porque uma delas circulou por várias sessões."),
    "correcoes": [
        {"id": "COR-001",
         "crenca_anterior": ("os quatro campos UNDEFINED — autonomy, precedence, "
                             "missing_input_action, iteration_limit — são do PILOT-001"),
         "medido": ("são do PILOT-002. Constam do COMPILATION_MANIFEST da skill "
                    "v0.1.0 daquele piloto."),
         "manifest_sha256": G["pilot002_legacy"]["manifest_sha256"],
         "o_que_muda": ("inverte de qual curso é a lacuna de governança. O PILOT-001 "
                        f"tem o seu próprio conjunto, maior: "
                        f"{G['pilot001']['undefined_total']} campos vazios nas regras "
                        f"reais, dos quais 84 pedagógicos e 85 metadados."),
         "gravidade": "ALTA — atribuía a lacuna ao curso errado"},
        {"id": "COR-002",
         "crenca_anterior": ("o PILOT-002 tem 2.151s de território virgem em blocos "
                             "≥60s, 49,1% do corpus"),
         "medido": (f"esse número é da rodada ANTIGA de 44 evidências "
                    f"(PILOT-002-EXTRACTION-SCALING.md). Recomputado sobre as 448 da "
                    f"rodada atual, e descontando as janelas de held-out: "
                    f"{G['pilot002_v2']['virgin_ge60_s']}s "
                    f"({G['pilot002_v2']['virgin_ge60_pct']}%) — nenhum bloco ≥60s."),
         "virgem_total_atual": f"{G['pilot002_v2']['virgin_s']}s "
                               f"({G['pilot002_v2']['virgin_pct']}%)",
         "armadilha_associada": ("sem descontar o held-out explicitamente, a janela "
                                 "44:40–50:00 aparece como o maior bloco virgem do "
                                 "corpus. Quarta ocorrência dessa contaminação."),
         "gravidade": "ALTA — media a rodada errada e superestimava a falha 6,6×"},
        {"id": "COR-003",
         "crenca_anterior": "17,4% do corpus do PILOT-002 é inferência do modelo",
         "medido": (f"o rótulo MODEL_INFERENCE superestima. Das 88, "
                    f"{S['PILOT-002-v2']['transcription_correction']} são correção de "
                    f"transcrição e {S['PILOT-002-v2']['genuine_inference']} restam; "
                    f"dessas, {len(para('PILOT-002-v2'))} são paráfrase sem distância. "
                    f"Inferência com distância real: {len(real('PILOT-002-v2'))} de 448 "
                    f"= {100*len(real('PILOT-002-v2'))/448:.1f}%."),
         "por_que_o_detector_falhava": ("exigia o quase-igual CAPITALIZADO na quote; o "
                                        "ASR minusculiza. Duas âncoras novas: "
                                        "similaridade ≥0,78 em minúscula, e alias "
                                        "declarado para 'Claude'."),
         "fato_que_sustenta_o_alias": ("no L0 cortado, 133 de 146 menções (91,1%) ao "
                                       "produto central do curso estão corrompidas; "
                                       "só 13 dizem 'claude'"),
         "gravidade": "ALTA — 17,4% lido como acusação era 3,8% real"},
    ],
}
COR.write_text("# Correções que a medição impôs.\n" +
               yaml.safe_dump(cor, allow_unicode=True, sort_keys=False, width=100),
               encoding="utf-8")

# ------------------------------------------------------------------- a cadeia
M = []
w = M.append
w("# COURSE-GAP-REPORT — A CADEIA DA INFERÊNCIA")
w("")
w("> **Retroativo e parcial.** As regras de decisão ainda não existem — a "
  "compilação evidência→Skill não rodou. Esta é a cadeia no nível da "
  "**evidência**, que é o que as regras vão herdar.")
w("")
w("## Por que a cadeia, e não só a marca")
w("")
w("Dizer *\"17,4% do curso foi inferido pelo modelo\"* lê como acusação. Pode ser "
  "generalização razoável, pode ser invenção — e quem lê não tem como julgar sem "
  "ver **o que o curso disse** e **o que o modelo concluiu além disso**.")
w("")
w("## O número encolheu três vezes ao ser olhado de perto")
w("")
w("| passo | PILOT-002 | % do corpus |")
w("|---|---|---|")
w(f"| rótulo `MODEL_INFERENCE` bruto | 88 | 19,6% |")
w(f"| menos correções de transcrição | {S['PILOT-002-v2']['genuine_inference']} | "
  f"{S['PILOT-002-v2']['genuine_pct_of_corpus']}% |")
w(f"| menos paráfrases sem distância | **{len(real('PILOT-002-v2'))}** | "
  f"**{100*len(real('PILOT-002-v2'))/448:.1f}%** |")
w("")
w(f"**{100*len(real('PILOT-002-v2'))/448:.1f}% do corpus do PILOT-002 é inferência "
  f"do modelo com distância real da fonte.** No PILOT-001, "
  f"{len(real('PILOT-001-v2'))} de 149 = "
  f"{100*len(real('PILOT-001-v2'))/149:.1f}%.")
w("")
for pid, lbl in (("PILOT-002-v2", "PILOT-002 — *Claude Code em 60 minutos*"),
                 ("PILOT-001-v2", "PILOT-001 — *How to Build Your First AI Agent*")):
    rl = real(pid)
    w("---")
    w("")
    w(f"## {lbl}")
    w("")
    w(f"**{len(rl)} inferências com distância real.** Cada uma: o que o curso disse, "
      f"o que o modelo concluiu, e a distância.")
    w("")
    for e in sorted(rl, key=lambda x: x["start_s"]):
        w(f"### `{e['evidence_id']}` · **{ts(e['start_s'])}** · {e['segment_id']} "
          f"· {e['category']}")
        w("")
        w(f"> **o curso disse:** {e['quote'].strip()}")
        w("")
        w(f"**o modelo concluiu:** {e['claim']}")
        w("")
        w(f"**distância:** {L[e['evidence_id']]}")
        w("")
    p = para(pid)
    if p:
        w(f"### {len(p)} classificadas como inferência que são paráfrase")
        w("")
        w("Marcadas `MODEL_INFERENCE` pelo extrator, mas sem distância da fonte — "
          "tradução ou reordenação. **Não são lacuna do curso.**")
        w("")
        w("| evidência | onde | por quê |")
        w("|---|---|---|")
        for e in sorted(p, key=lambda x: x["start_s"])[:10]:
            w(f"| `{e['evidence_id']}` | {ts(e['start_s'])} | "
              f"{L[e['evidence_id']].replace('sem distância: ', '')} |")
        w("")
w("---")
w("")
w("## Como ler isto quando as regras existirem")
w("")
w("Cada regra de decisão vai citar `evidence_id`. Uma regra cujas evidências "
  "sejam **todas** desta lista é **lacuna do curso**: funciona, mas o curso não a "
  "ensinou — o modelo preencheu. É a diferença entre avaliar o curso e avaliar o "
  "modelo.")
w("")
w(f"*Gerado por script. As linhas de distância vieram de 6 chamadas em lotes de "
  f"12, com contabilidade dura: 57/57 evidências voltaram com linha.*")
OUT.write_text("\n".join(M) + "\n", encoding="utf-8")

print(f"{sh(OUT)}  {OUT.name}")
print(f"{sh(COR)}  {COR.name}")
for pid in S:
    print(f"  {pid}: genuina {S[pid]['genuine_inference']} · com distância "
          f"{len(real(pid))} · paráfrase {len(para(pid))}")
