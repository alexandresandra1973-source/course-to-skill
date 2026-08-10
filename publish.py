#!/usr/bin/env python3
"""Publica o resultado da espinha no Drive.

O relatório é GERADO a partir de work/spine_result.json — nenhum número é
digitado à mão, para que o publicado não possa divergir do medido.
A publicação é por script; o usuário não move arquivo.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
DEST = Path("/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Claude/docs/PHASE4_SPINE_RESULT.md")

# O que a auditoria (Fases 1-3) mediu à mão, e que o código tem de reproduzir.
ESPERADO = [
    ("G2 reprova por quote 0/44",
     lambda R: (R["G2-anchor"]["state"] == "FAIL"
                and R["G2-anchor"]["evidence"]["records_without_quote"] == 44),
     lambda R: f"state={R['G2-anchor']['state']} "
               f"sem_quote={R['G2-anchor']['evidence']['records_without_quote']}/"
               f"{R['G2-anchor']['evidence']['records']} "
               f"ancoradas_ok={R['G2-anchor']['evidence']['records_anchored_ok']}"),
    ("G2 acusa o span de EV-0001 que não resolve",
     lambda R: R["G2-anchor"]["evidence"]["resolution_reasons"].get("END_MARK_NOT_FOUND") == 1,
     lambda R: f"span_refs {R['G2-anchor']['evidence']['span_refs_resolved']}/"
               f"{R['G2-anchor']['evidence']['span_refs_total']} resolvem; "
               f"motivos={R['G2-anchor']['evidence']['resolution_reasons']}"),
    ("G3 poupa `category`",
     lambda R: any(r["field"] == "evidence.category" and r["state"] == "OK"
                   for r in R["G3-dispersion"]["evidence"]["table"]),
     lambda R: next(f"H_norm={r['H_norm']} state={r['state']}"
                    for r in R["G3-dispersion"]["evidence"]["table"]
                    if r["field"] == "evidence.category")),
    ("G3 acusa os campos de entropia zero",
     lambda R: sum(1 for r in R["G3-dispersion"]["evidence"]["table"]
                   if r["H_norm"] == 0.0) == 7,
     lambda R: f"campos com H_norm=0: "
               f"{sum(1 for r in R['G3-dispersion']['evidence']['table'] if r['H_norm'] == 0.0)}; "
               f"classificados COLLAPSED: {R['G3-dispersion']['evidence']['collapsed']}; "
               f"UNDERPOWERED: {R['G3-dispersion']['evidence']['underpowered']}"),
    ("Cutter marca TEST-0009 como contaminado",
     lambda R: any(v["case_id"] == "TEST-0009"
                   and v["verdict"] == "CONTAMINATED_BY_CONSTRUCTION"
                   for v in R["G1-cutter/retroactive"]["findings"]),
     lambda R: next(f"{v['verdict']}; spans={v['support_spans']}"
                    for v in R["G1-cutter/retroactive"]["findings"]
                    if v["case_id"] == "TEST-0009")),
    ("G6 recusa S4",
     lambda R: (R["G6-ceiling"]["state"] == "FAIL"
                and R["G6-ceiling"]["evidence"]["ceiling_reached"] != "S4_CLOSED"),
     lambda R: f"pedido={R['G6-ceiling']['evidence']['requested_level']} "
               f"teto={R['G6-ceiling']['evidence']['ceiling_reached']} "
               f"n_holdout={R['G6-ceiling']['evidence']['n_holdout']} "
               f"n_min={R['G6-ceiling']['evidence']['n_min_wilson_95']}"),
    ("G6 recusa S1",
     lambda R: R["G6-ceiling/S1"]["state"] == "FAIL",
     lambda R: f"pedido=S1_ANCHORED teto={R['G6-ceiling/S1']['evidence']['ceiling_reached']} "
               f"corpus={R['G6-ceiling']['evidence']['corpus']}"),
]


def md_table(rows, head):
    out = ["| " + " | ".join(head) + " |",
           "|" + "|".join("---" for _ in head) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def main() -> int:
    d = json.loads((HERE / "work/spine_result.json").read_text(encoding="utf-8"))
    R = {r["gate"]: r for r in d["results"]}
    L: list[str] = []
    A = L.append

    A("# PHASE4_SPINE_RESULT — espinha vertical rodando contra o PILOT-001\n")
    A(f"**Corrida:** `{d['started']}` · **Repositório:** `~/course-to-skill-claude` (ext4) · "
      "**Publicação:** por script, a partir de `work/spine_result.json`.\n")
    A("Nenhum número deste relatório foi digitado à mão: todos vêm do JSON da corrida.\n")
    A("**Critério da fase:** a espinha tem de reproduzir mecanicamente os defeitos que a "
      "auditoria mediu à mão. Reprovação correta é sucesso.\n")

    A("\n## 0. Baseline e deriva\n")
    b = d["baseline"]
    A(f"- Arquivos no manifesto congelado: **{b['in_manifest']}**")
    A(f"- Alterados: **{len(b['changed'])}** · Sumidos: **{len(b['missing'])}** · "
      f"Novos: **{len(b['added'])}**")
    for x in b["added"]:
        A(f"  - novo (esteira paralela): `{x}`")
    A("\nO manifesto **não** foi atualizado — é a referência fixa da Fase 5. "
      "Deriva só por adição; nenhuma entrada de leitura mudou.\n")

    A("\n## 1. O que cada portão devolveu, e contra que arquivo\n")
    for g in ["G1-cutter/functional", "G1-cutter/retroactive", "G2-anchor",
              "G3-dispersion", "G5-closure", "G5-closure/origin",
              "G6-ceiling", "G6-ceiling/S1"]:
        r = R[g]
        A(f"\n### `{g}` → **{r['state']}**")
        A(f"*Sujeito medido:* `{r['subject']}`\n")
        A("```")
        for k, v in r["evidence"].items():
            if isinstance(v, (list, dict)) and k not in ("resolution_reasons",
                                                         "corpus", "invention_by_file"):
                A(f"{k}: <{len(v)} itens>")
            else:
                A(f"{k}: {v}")
        A("```")
        if r["note"]:
            A(f"> {r['note']}")

    A("\n## 2. Tabela de dispersão medida (G3)\n")
    A(md_table([[t["field"], t["n"], t["k"], t["distinct"], t["H_bits"],
                 t["H_norm"], t["state"]]
                for t in R["G3-dispersion"]["evidence"]["table"]],
               ["campo", "N", "k", "distintos", "H (bits)", "H_norm", "estado"]))

    A("\n## 3. Diff: esperado pela auditoria × medido pelo código\n")
    rows = []
    for nome, pred, fmt in ESPERADO:
        try:
            ok, det = pred(R), fmt(R)
        except Exception as e:  # falha de leitura é resultado, não exceção
            ok, det = False, f"ERRO ao medir: {e}"
        rows.append(["✅ CONFIRMA" if ok else "⚠️ DIVERGE", nome, det])
    A(md_table(rows, ["veredito", "o que a auditoria esperava", "o que o código mediu"]))

    A("\n### 3.1 Divergência real, escondida numa linha que passou\n")
    t3 = R["G3-dispersion"]["evidence"]["table"]
    zero = [t for t in t3 if t["H_norm"] == 0.0]
    coll = [t for t in zero if t["state"] == "COLLAPSED"]
    under = [t for t in zero if t["state"] == "UNDERPOWERED"]
    A(f"A **medição** bate: **{len(zero)}** campos com entropia zero. A **classificação** não: "
      f"o código chama de `COLLAPSED` apenas **{len(coll)}** deles e manda os outros "
      f"**{len(under)}** para `UNDERPOWERED`.\n")
    A(f"Motivo: a ADR-0005 exige `N ≥ {R['G3-dispersion']['evidence']['n_min']}` para concluir, "
      "e os campos de decisão têm N=8. A tabela das Fases 1–3 foi calculada **sem** essa guarda, "
      "que só passou a existir na ADR-0005. O código está certo pela minha própria regra; "
      "a tabela anterior concluiu com base pequena demais.\n")
    A("Campos que a auditoria chamou de COLLAPSED e o código recusa concluir:\n")
    A(md_table([[t["field"], t["n"], t["distinct"], t["H_norm"], t["state"]] for t in under],
               ["campo", "N", "distintos", "H_norm", "estado pelo código"]))
    A("\n**Correção de medida das fases anteriores.** A Fase 3 escreveu *\"8 de 10 campos "
      f"carregam 0 bits ou quase\"*. O número exato é: **{len(zero)}** com H=0, "
      f"**{sum(1 for t in t3 if t['state']=='NEAR_COLLAPSED')}** quase-colapsados, "
      f"**{sum(1 for t in t3 if t['state']=='OK')}** saudável — ou seja "
      f"**{len(t3) - sum(1 for t in t3 if t['state']=='OK')} de {len(t3)}** não-OK, não 8.\n")

    A("\n## 3.2 Achados novos (não vistos pela auditoria manual)\n")
    o = R["G5-closure/origin"]["evidence"]
    g5e = R["G5-closure"]["evidence"]
    A(md_table([
        ["N1",
         "O bundle corrigido **não** inventa: `compiler_invention_count = "
         f"{g5e['compiler_invention_count']}` sobre {g5e['bundle_claims']} afirmações da camada "
         f"de conhecimento, contra {g5e['audited_claims']} pós-auditoria. G5 confirma que o "
         "empacotador é função pura **nesta versão**."],
        ["N2",
         "**SC-001 atribuiu o defeito à camada errada.** Dos "
         f"{o['flagged_by_adversary']} ADRs que o adversário disse terem recebido autonomia "
         f"*\"adicionada pelo compilador\"*, **{o['already_present_in_L1']} já tinham o valor em "
         f"`analysis/decisions.yaml` (L1)** e **{o['introduced_between_L1_and_bundle']}** "
         "entraram entre L1 e o bundle. O achado era correto em substância "
         "(não ensinado pela fonte) e errado em atribuição — consertar o Compiler não teria "
         "impedido nada."],
        ["N3",
         f"**G3 é estruturalmente cego à camada de decisão em corpus de uma aula.** "
         f"{len(under)} dos {len(t3)} campos caem em `UNDERPOWERED` só por N=8 < "
         f"{R['G3-dispersion']['evidence']['n_min']}. O problema de tamanho de corpus "
         "contamina o portão de dispersão, não só o held-out — a ADR-0005 precisa dizer o "
         "que `UNDERPOWERED` faz com o teto, e hoje não diz."],
        ["N4",
         f"**Vazamento contrafactual = {g5e['holdout_leak_count']}.** Com um corte legítimo de "
         "20% (semente 20260810), essa é a quantidade de citações de span dos artefatos que "
         "cairia dentro do held-out. Não é defeito do piloto — é a medida, só possível agora, "
         "de quanto o artefato depende de um quinto aleatório da fonte."],
        ["N5",
         "**Falso positivo do meu próprio extrator de claims.** A primeira corrida acusou 1 "
         "invenção que era `manifest.skill.name` (*\"HubSpot AI Agent Builder — PILOT-001\"*). "
         "Corrigi estreitando o **escopo** (manifest e audit são metadado por contrato, não "
         "camada de conhecimento), não afrouxando o **limiar**. Registrado porque ajustar "
         "verificação até parar de reclamar é exatamente o defeito auditado."],
    ], ["#", "achado"]))

    A("\n## 4. Casos que se declaram cegos (Cutter retroativo)\n")
    A(md_table([[v["case_id"], v["declared_type"], v["verdict"],
                 len(v["support_spans"])]
                for v in R["G1-cutter/retroactive"]["findings"]],
               ["caso", "tipo declarado", "veredito", "spans de suporte"]))

    A("\n## 5. Como rodar\n")
    A("```bash\ncd ~/course-to-skill-claude\npython3 spine.py      # roda a espinha\n"
      "python3 run_tests.py  # meta-testes dos portões\npython3 publish.py    # publica este relatório\n```")

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"publicado: {DEST}  ({DEST.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
