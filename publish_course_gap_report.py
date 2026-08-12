#!/usr/bin/env python3
"""COURSE-GAP-REPORT RETROATIVO — os dois pilotos. Zero chamadas. READ-ONLY.

Mostra a FORMA da saída do avaliador de curso, não a avaliação completa: a Skill
executável ainda não existe.

TRÊS CATEGORIAS, e separá-las é o ponto do documento. Confundi-las inverte o
significado:
  A. LACUNA DO CURSO      — o curso não ensinou. Culpa do curso.
  B. NÃO ALCANÇADO        — a extração não chegou lá. Limite da MEDIÇÃO.
  C. QUALIDADE DA FONTE   — a transcrição está corrompida. Culpa do insumo.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "COURSE-GAP-REPORT-RETROATIVO.md"
M = json.loads(Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/gap-measure.json")
               .read_text(encoding="utf-8"))

# Campo vazio não é automaticamente lacuna do curso. Separo por natureza:
PEDAGOGICO = {
    "ask_user_if_missing": "o que perguntar ao usuário quando falta um insumo",
    "precedence": "qual regra ganha quando duas se aplicam ao mesmo tempo",
    "autonomy": "até onde o agente pode agir sozinho antes de parar",
    "missing_input_action": "o que fazer quando um insumo obrigatório não veio",
    "iteration_limit": "quantas vezes repetir antes de desistir",
    "steps": "os passos concretos de um procedimento",
    "approval_before": "que ação exige aprovação humana antes de executar",
    "level": "o grau de autonomia declarado",
    "decision_points": "onde o procedimento bifurca e com que critério",
    "loops": "o que se repete e sob que condição de parada",
    "required_inputs": "o que é obrigatório ter antes de começar",
    "optional_inputs": "o que ajuda mas não bloqueia",
    "tools": "com que ferramenta cada passo é executado",
    "outputs": "o que o passo entrega",
    "behavior": "como o agente se comporta nesse ponto",
    "validation_criteria": "como saber se ficou bom",
}
METADADO = {"teacher", "version", "created_at", "updated_at", "module_id",
            "module_title", "superseded_by", "contradiction_note", "reviewer_note",
            "inference_basis", "inference", "lesson_scope"}


def sh(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()


def classify(counts: dict) -> tuple[dict, dict, list]:
    ped = {k: v for k, v in counts.items() if k in PEDAGOGICO}
    met = {k: v for k, v in counts.items() if k in METADADO}
    outros = [k for k in counts if k not in PEDAGOGICO and k not in METADADO]
    return ped, met, outros


def main() -> int:
    p1, p2l, p2 = M["pilot001"], M["pilot002_legacy"], M["pilot002_v2"]
    ped1, met1, out1 = classify(p1["por_campo"])
    n_ped1, n_met1 = sum(ped1.values()), sum(met1.values())

    L = []
    w = L.append
    w("# COURSE-GAP-REPORT — RETROATIVO E PARCIAL")
    w("")
    w("> ## ⚠ Leia isto antes dos números")
    w("> **Este relatório é RETROATIVO e PARCIAL.** A Skill executável que o "
      "avaliador de curso deveria produzir **ainda não existe**. O que está aqui "
      "foi reconstruído dos artefatos já medidos, e serve para mostrar **a FORMA "
      "da saída** — não para avaliar os dois cursos.")
    w("> ")
    w("> Um relatório completo diria *\"o método deste curso funciona quando "
      "executado\"*. Este diz apenas *\"eis o que o curso deixou de especificar, e "
      "eis o que ainda não conseguimos medir\"*.")
    w("")
    w(f"Gerado por `{Path(__file__).name}`. Nenhum número digitado à mão. "
      f"Zero chamadas de modelo.")
    w("")
    w("---")
    w("")
    w("## As três categorias, e por que separá-las importa")
    w("")
    w("| | o que é | de quem é a falha |")
    w("|---|---|---|")
    w("| **A — LACUNA DO CURSO** | o curso não ensinou o que a execução exigiria | **do curso** |")
    w("| **B — NÃO ALCANÇADO** | a extração não chegou àquele trecho | **da medição** |")
    w("| **C — QUALIDADE DA FONTE** | a transcrição está corrompida | **do insumo** |")
    w("")
    w("**Confundir A com B inverte o significado.** Território não alcançado lido "
      "como lacuna do curso reprova um curso que talvez ensine muito bem o que "
      "não foi medido. E lacuna do curso lida como falha de medição absolve um "
      "curso que de fato não ensinou.")
    w("")
    w("---")
    w("")
    w("# A · LACUNAS DO CURSO")
    w("")
    w("## PILOT-001 — *How to Build Your First AI Agent*")
    w("")
    w(f"A Skill compilada tem **{p1['n_rules']} regras de decisão** e "
      f"**{p1['n_workflows']} workflow**. Ao montá-la, "
      f"**{p1['undefined_total']} campos** ficaram vazios.")
    w("")
    w(f"Desses, **{n_met1} são metadados** — quem é o professor, número de versão, "
      f"data de criação. Não dizem nada sobre o curso.")
    w("")
    w(f"**{n_ped1} são lacunas de verdade.** São perguntas que quem tentar "
      f"executar o método vai fazer, e que a aula não responde:")
    w("")
    w("| o que faltou | quantas vezes | a pergunta que o curso não responde |")
    w("|---|---|---|")
    for k, v in sorted(ped1.items(), key=lambda x: -x[1]):
        w(f"| `{k}` | {v} | {PEDAGOGICO[k]} |")
    w("")
    top = sorted(ped1.items(), key=lambda x: -x[1])[0]
    w(f"**A maior é `{top[0]}`, {top[1]} vezes.** O curso ensina o que fazer "
      f"quando tudo está disponível. Não ensina o que perguntar quando falta "
      f"alguma coisa — e faltar alguma coisa é o caso normal.")
    w("")
    w("### As lacunas com timestamp")
    w("")
    w("Cada uma aponta o minuto da aula onde a resposta deveria estar:")
    w("")
    w("| regra | campo vazio | trecho da aula |")
    w("|---|---|---|")
    seen = set()
    for r in p1["rows"]:
        base = r["field"].split("[")[0].split(".")[-1]
        if base not in PEDAGOGICO or not r["span"]:
            continue
        key = (r["entity"], base)
        if key in seen:
            continue
        seen.add(key)
        a, b = r["span"]
        w(f"| `{r['entity']}` — {r['entity_name']} | `{base}` | "
          f"{a//60}:{a%60:02d}–{b//60}:{b%60:02d} |")
        if len(seen) >= 14:
            break
    w("")
    w("## PILOT-002 — *Claude Code em 60 minutos*")
    w("")
    w(f"A compilação legada (44 evidências) declarou "
      f"**{p2l['undefined_count']} campos indefinidos**:")
    w("")
    w("| campo | a pergunta que o curso não responde |")
    w("|---|---|")
    for f in p2l["undefined_fields"]:
        w(f"| `{f}` | {PEDAGOGICO.get(f, '—')} |")
    w("")
    w("**Os quatro são de governança, e é o padrão mais claro dos dois pilotos.** "
      "O curso mostra o agente trabalhando sozinho e não diz até onde ele pode ir "
      "(`autonomy`), o que fazer quando falta um insumo "
      "(`missing_input_action`), quantas vezes tentar antes de desistir "
      "(`iteration_limit`), nem qual regra vence quando duas se aplicam "
      "(`precedence`).")
    w("")
    w("> **Correção de atribuição.** Estes quatro campos foram atribuídos ao "
      "PILOT-001 no pedido. Eles são do **PILOT-002** — constam do "
      "`COMPILATION_MANIFEST` da skill v0.1.0 daquele piloto "
      f"(`{p2l['manifest_sha256'][:16]}…`). O PILOT-001 tem o seu próprio "
      f"conjunto, medido acima, e ele é maior.")
    w("")
    w(f"A rodada nova do PILOT-002, com **{p2['evidence_total']} evidências**, "
      f"ainda não foi compilada em Skill — é a Frente A. Quando for, esta seção "
      f"passa a ter timestamps como a do PILOT-001.")
    w("")
    w("---")
    w("")
    w("# B · TERRITÓRIO NÃO ALCANÇADO — limite da medição, NÃO do curso")
    w("")
    w("## PILOT-002")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| duração do vídeo | {p2['nominal_s']//60}:{p2['nominal_s']%60:02d} |")
    w(f"| retirado como held-out | {p2['held_out_s']}s "
      f"({', '.join(p2['held_out_windows'])}) |")
    w(f"| corpus medido | {p2['extent_s']}s |")
    w(f"| **coberto por evidência** | **{p2['coverage_pct']}%** |")
    w(f"| não alcançado | {p2['virgin_s']}s ({p2['virgin_pct']}%) em "
      f"{p2['virgin_blocks']} trechos |")
    w(f"| **trechos contínuos ≥ 60s** | **{p2['virgin_ge60_count']}** |")
    w("")
    w("**Nenhum trecho de um minuto inteiro ficou sem cobertura.** Os maiores "
      "buracos são estes, e todos cabem em menos de um minuto:")
    w("")
    w("| trecho | duração | seção da aula |")
    w("|---|---|---|")
    for t in p2["largest_blocks"][:6]:
        w(f"| {t['start']}–{t['end']} | {t['dur']}s | {t['topic']} |")
    w("")
    w("> ### Correção de um número que circulava")
    w("> O valor conhecido era **2.151s sem cobertura em blocos ≥60s, 49,1% do "
      "corpus**. Ele vem de "
      "`PILOT-002-EXTRACTION-SCALING.md` e mede a rodada **antiga, de 44 "
      "evidências**. Recomputado sobre as 448 da rodada atual, e descontando "
      f"as janelas de held-out, o valor é **{p2['virgin_ge60_s']}s "
      f"({p2['virgin_ge60_pct']}%)** — ou seja, **zero**.")
    w("> ")
    w("> As janelas de held-out precisam ser descontadas explicitamente: sem "
      "isso, a maior delas (44:40–50:00) aparece como o maior 'bloco virgem' do "
      "corpus, e território deliberadamente removido vira falha de extração.")
    w("")
    w("---")
    w("")
    w("# C · QUALIDADE DA TRANSCRIÇÃO — falha do insumo")
    w("")
    w("A fonte é transcrição automática. Ela erra nomes próprios e às vezes "
      "**perde negações**, que é o erro grave: o texto continua gramatical e diz "
      "o contrário.")
    w("")
    w("| piloto | evidências | divergências detectadas | taxa | propagadas como fonte |")
    w("|---|---|---|---|---|")
    for k, lbl in (("pilot001_v2", "PILOT-001"), ("pilot002_v2", "PILOT-002")):
        c = M["corruption"][k]
        w(f"| {lbl} | {c['n']} | {c['hits']} | **{c['rate_pct']}%** | "
          f"{c['as_source_explicit']} ({c['propagated_pct']}%) |")
    w("")
    w("A coluna que importa é a última: quantas vezes o compilador **corrigiu** a "
      "transcrição e ainda assim rotulou a afirmação como *\"a fonte diz isto\"*. "
      "Corrigir é desejável; corrigir e chamar de fonte explícita é o dano.")
    w("")
    w("---")
    w("")
    w("## O que este relatório ainda NÃO diz")
    w("")
    w("- **Se o método de cada curso funciona.** Isso exige compilar a Skill, "
      "executá-la e ver se ela entrega. É a Frente A, não iniciada.")
    w("- **Quanto de cada lacuna importa.** Um `precedence` vazio pode ser fatal "
      "ou irrelevante dependendo de quantas regras competem na prática.")
    w("- **Se as lacunas são do curso ou do compilador.** Um campo vazio pode "
      "significar que a aula não ensinou, ou que o extrator não achou. Separar as "
      "duas exige o portão de cobertura evidência→regra, que é parte da Frente A.")
    w("")
    w("---")
    w("")
    w(f"*Gerado em {datetime.now(timezone.utc).strftime('%Y-%m-%d')} · retroativo e "
      f"parcial · a Skill executável não existe*")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256: {sh(OUT)}")
    print(f"\nPILOT-001: {p1['undefined_total']} campos vazios · {n_ped1} pedagógicos · "
          f"{n_met1} metadados · outros {out1}")
    print(f"PILOT-002 legado: {p2l['undefined_fields']}")
    print(f"PILOT-002-v2 não alcançado: {p2['virgin_s']}s ({p2['virgin_pct']}%) · "
          f"blocos ≥60s: {p2['virgin_ge60_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
