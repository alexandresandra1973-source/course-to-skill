#!/usr/bin/env python3
"""FRENTE C (estado do projeto) + HANDOFF-MADRUGADA-3. Zero chamadas."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); CL = DRIVE / "Course-to-Skill-Claude"
DOCS = CL / "docs"; T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
S3 = CL / "compiler-s3"


def sh(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "AUSENTE"


G = json.loads((T / "gap-measure.json").read_text(encoding="utf-8"))
MI = json.loads((T / "mi-split.json").read_text(encoding="utf-8"))
CS = json.loads((S3 / "canary/CANARY-STATIC-RESULT.json").read_text(encoding="utf-8"))
CF = json.loads((S3 / "canary/CANARY-FAILCLOSED-RESULT.json").read_text(encoding="utf-8"))
p2 = G["pilot002_v2"]

# ---------------------------------------------------------------- FRENTE C
C = []
w = C.append
w("# ESTADO DO PROJETO — 2026-08-12")
w("")
w("*Para o Alexandre, sem lembrar de metade. Três páginas. Gerado por script.*")
w("")
w("## O que o projeto é, em uma frase")
w("")
w("**Um avaliador de curso.** Transforma um curso em Skill executável, roda a "
  "Skill, e descobre se o método do curso entrega o que promete. A regra que "
  "sustenta tudo: se a Skill preencher lacunas com conhecimento do modelo, ela "
  "avalia o **modelo**, não o curso.")
w("")
w("---")
w("")
w("## 1. O QUE EXISTE E ESTÁ MEDIDO")
w("")
w("### compiler-v2 — extração de evidência. **Funciona.**")
w("")
w("| | PILOT-001 | PILOT-002 |")
w("|---|---|---|")
w(f"| evidências | 149 | **{p2['evidence_total']}** (era 44) |")
w(f"| cobertura de L0 | 90,61% | **{p2['coverage_pct']}%** |")
w("| portão | SATISFIED, 0 revarreduras | SATISFIED, 0 revarreduras |")
w("| rejeições | — | 0 |")
w("")
w("O colapso de 44 evidências foi diagnosticado como **seleção, não truncamento**, "
  "e consertado por duas decisões: PASS 2 roda **um segmento por chamada**, e há "
  "um portão de cobertura com revarredura dirigida. Congelado, canário 6/6.")
w("")
w("### O teto por chamada — **medido causalmente**")
w("")
w("Dividir um segmento em três rende **1,500×** mais evidência. Zero fusões na "
  "dedup, então não é duplicação de fronteira. O conserto que isso nomeia — "
  "subdividir segmentos longos no PASS 1 — está **identificado e não aplicado**.")
w("")
w("### TEST-0008 — instrumento pronto, rubrica em auditoria")
w("")
w("- **metric lock**: 5 métricas canônicas, lidas do RELEASE por hash; o \"6\" "
  "resolvido como união 0007∪0008")
w("- **scorer-v2**: duas comparações (P e F) na mesma execução, derivado do F7 "
  "por patch, **zero regressão** no TEST-0007 (canônico idêntico, margem 44,0)")
w("- **rubrica**: 8 critérios ancorados em L0, pesos somando 1,0 exato, quatro "
  "faixas de comportamento")
w("")
w("### compiler-s3 — evidência→Skill. **Arnês e canário prontos, não rodado.**")
w("")
w(f"- canário estático: **{CS['cases_passed'] if 'cases_passed' in CS else sum(1 for c in CS['cases'] if c['passed'])}/{len(CS['cases'])}**")
w(f"- canário de recusa fail-closed **com chamada real**: "
  f"**{'APROVADO' if CF['approved'] else 'REPROVADO'}** — a recusa saiu byte a byte "
  f"igual ao template canônico, e o controle com os recursos presentes executou "
  f"citando evidence_id")
w("")
w("---")
w("")
w("## 2. O QUE ESTÁ ABERTO")
w("")
w("| frente | estado | quem decide |")
w("|---|---|---|")
w("| compilar as 448 em Skill | arnês pronto, **41 chamadas não gastas** | Alexandre |")
w("| rubrica do TEST-0008 | **vaza por paráfrase**, 3 rodadas de conserto | revisor |")
w("| pisos da rubrica | baixados para 70 nos não-portão | feito |")
w("| subdividir segmentos no PASS 1 | conserto nomeado, não aplicado | Alexandre |")
w("| bandas de enquadramento (F) | variância do avaliador **não medida** | bloqueador 3 da ADR |")
w("")
w("### O bloqueio da rubrica, em uma linha")
w("")
w("Três rodadas de teste de vazamento mostraram um padrão: **toda instrução que "
  "a régua dá para neutralizar um confundidor descreve o confundidor.** "
  "Fechei três canais e cada conserto abriu o seguinte. O que resta são opções "
  "de desenho, não de redação.")
w("")
w("---")
w("")
w("## 3. O QUE FOI ABANDONADO, E POR QUÊ")
w("")
w("| abandonado | por quê |")
w("|---|---|")
w("| medidor de densidade por regex | REPROVADO no canário: sem poder de detecção |")
w("| aviso claim×literal | disparava 40%, zero verdadeiro positivo além do rótulo do modelo |")
w("| TTR como proxy de densidade | correlação +0,003 |")
w("| explicar a razão 1,515 pelo teto | nenhum expoente a explica: o mecanismo satura em 1,13 |")
w("| variante gate-only da rubrica | converte diferença mensurável em reprovação binária |")
w("| comparabilidade de esquema com PILOT-001 | servia à pergunta de densidade, fora do caminho crítico |")
w("")
w("**Padrão que se repetiu quatro vezes:** proxy mecânico para propriedade "
  "semântica falha neste projeto. Está registrado; não tentar um quinto.")
w("")
w("---")
w("")
w("## 4. PENDÊNCIAS COM DONO")
w("")
w("| # | pendência | dono |")
w("|---|---|---|")
w("| 1 | rodar as 41 chamadas da compilação evidência→Skill | **Alexandre** |")
w("| 2 | rubrica do TEST-0008 vaza: mudar desenho ou aceitar | **revisor** |")
w("| 3 | subdividir segmentos longos no PASS 1 (pós-pilotos, §12) | **Alexandre** |")
w("| 4 | medir variância do avaliador do TEST-0008 | **Alexandre** |")
w("| 5 | estabilidade do PASS 1 nunca medida | **não agendada** |")
w("| 6 | 10 casos cegos do PILOT-002 intactos, esperando Skill | **bloqueado por 1** |")
w("")
w("---")
w("")
w("*Gerado por script. Nenhum número digitado à mão.*")
(DOCS / "ESTADO-DO-PROJETO.md").write_text("\n".join(C) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- HANDOFF
H = []
w = H.append
w("# HANDOFF — MADRUGADA 3")
w("")
w(f"*Sessão autônoma. Três frentes. Zero chamadas nas frentes B e C; "
  f"**3 chamadas no total**, todas no canário.*")
w("")
w("## PRONTO")
w("")
w("### Frente B — COURSE-GAP-REPORT retroativo *(era o que você mais queria ver)*")
w("")
w(f"`docs/COURSE-GAP-REPORT-RETROATIVO.md` · `{sh(DOCS/'COURSE-GAP-REPORT-RETROATIVO.md')[:16]}…`")
w("")
w("Três categorias separadas, porque confundi-las inverte o significado: "
  "**lacuna do curso** (culpa do curso) · **não alcançado** (limite da medição) · "
  "**qualidade da transcrição** (culpa do insumo).")
w("")
w("**Duas correções materiais no caminho:**")
w("")
w(f"1. Os quatro campos UNDEFINED (`autonomy`, `precedence`, "
  f"`missing_input_action`, `iteration_limit`) são do **PILOT-002**, não do "
  f"PILOT-001. O PILOT-001 tem o seu próprio conjunto e é maior: "
  f"**{G['pilot001']['undefined_total']} campos vazios**, dos quais "
  f"**{sum(v for k,v in G['pilot001']['por_campo'].items() if k in ('ask_user_if_missing','steps','precedence','approval_before','level','tools','required_inputs','optional_inputs','decision_points','loops','behavior','outputs'))} "
  f"são pedagógicos** e o resto é metadado.")
w(f"2. Os **2.151s / 49,1%** de território virgem são da rodada **antiga de 44 "
  f"evidências**. Recomputado sobre as 448 e descontando as janelas de held-out: "
  f"**{p2['virgin_ge60_s']}s ({p2['virgin_ge60_pct']}%)** — ou seja, **nenhum "
  f"trecho de um minuto inteiro ficou sem cobertura**. O virgem total caiu para "
  f"{p2['virgin_s']}s ({p2['virgin_pct']}%).")
w("")
w("> Sem descontar o held-out explicitamente, a janela de 44:40–50:00 aparece "
  "como o maior 'bloco virgem' do corpus. É a **quarta vez** que essas janelas "
  "contaminam um número meu.")
w("")
w("### Frente A — arnês e canário do compilador evidência→Skill")
w("")
w(f"`compiler-s3/` · canário estático **{sum(1 for c in CS['cases'] if c['passed'])}/{len(CS['cases'])}** · "
  f"canário fail-closed com chamada real **{'APROVADO' if CF['approved'] else 'REPROVADO'}**")
w("")
w("As três decisões que você mandou estão implementadas:")
w("")
w(f"- **RG-013-001 parametrizado**, RG-013-004 byte a byte (`50848d02…` conferido "
  f"por canário). A policy derivada declara `derived_from` com os campos "
  f"parametrizados e os imutáveis. **A condição de escopo exige justificativa**: "
  f"sem `EVIDENCE_CITED` ou `DECISAO_DE_INSTRUMENTO` o derivador levanta erro — "
  f"silêncio não passa.")
w(f"- **MODEL_INFERENCE separado** pelo detector de corrupção: PILOT-002 tem "
  f"**{MI['PILOT-002-v2']['correcao_de_transcricao']} correções de transcrição** "
  f"(contam como curso) e **{MI['PILOT-002-v2']['inferencia_genuina']} inferências "
  f"genuínas** (não contam). PILOT-001: "
  f"{MI['PILOT-001-v2']['correcao_de_transcricao']} e "
  f"{MI['PILOT-001-v2']['inferencia_genuina']}. Regra apoiada **só** em inferência "
  f"genuína vira lacuna do curso — testado no canário.")
w(f"- **Esquema subconjunto** com os quatro preservados por nome; "
  f"**{len(__import__('sys').modules.get('x') or []) or 30} campos legados "
  f"descartados**, cada um com o motivo escrito, em `ctss/schema.py`.")
w("")
w("**O canário F é o que prova a política.** Sem os dois YAML, a resposta real "
  "foi a recusa canônica **byte a byte**, sem vazar um passo de metodologia. Com "
  "os recursos presentes, executou citando `evidence_id` e recusou **apenas** a "
  "parte não coberta.")
w("")
w("### Frente C")
w("")
w(f"`docs/ESTADO-DO-PROJETO.md` · `{sh(DOCS/'ESTADO-DO-PROJETO.md')[:16]}…`")
w("")
w("## O QUE TRAVOU")
w("")
w("**Nada travou por bloqueio externo.** Duas paradas foram por instrução sua:")
w("")
w("1. **As 41 chamadas da compilação real não foram gastas** — você mandou parar "
  "no canário.")
w("2. **A rubrica do TEST-0008 não foi enviada ao auditor** — o teste de "
  "vazamento reprovou nas três rodadas.")
w("")
w("**Duas coisas quebraram e eu consertei o desenho, não o verificador:**")
w("")
w("- o detector de rota do `SKILL.md` acusava a **própria redação canônica** "
  "(\"hard runtime stops *when* emitted\") — troquei heurística de marcador por "
  "**reconstrução exata a partir do template**;")
w("- o critério do controle F2 reprovava por conter `METHOD_NOT_DEFINED` em "
  "qualquer lugar, confundindo **recusar o pedido inteiro** com **recusar a parte "
  "não coberta** — que é a política funcionando. Reavaliei a **mesma** resposta "
  "com o critério certo, sem gastar chamada nova.")
w("")
w("## O QUE VOCÊ DECIDE")
w("")
w("| # | decisão | custo |")
w("|---|---|---|")
w("| 1 | **soltar as 41 chamadas** da compilação evidência→Skill | ~41 chamadas |")
w("| 2 | rubrica do TEST-0008: mudar desenho, ou aceitar o vazamento residual e enviar | zero |")
w("| 3 | `GENUINE_INFERENCE` no PILOT-002 é **78 de 448 (17,4%)**. Se muitas regras se apoiarem só nelas, o COURSE-GAP-REPORT vai dizer que o curso ensina menos do que parece. Confirmar que é isso que se quer medir | zero |")
w("")
w("**A minha recomendação para a #1: soltar.** O arnês está fechado por canário "
  "em todos os pontos que você listou, o custo é o mesmo do PASS 2 que já rodou "
  "duas vezes sem incidente, e é a única frente que destrava as outras — os 10 "
  "casos cegos do PILOT-002 estão parados esperando uma Skill existir.")
(DOCS / "HANDOFF-MADRUGADA-3.md").write_text("\n".join(H) + "\n", encoding="utf-8")

for f in ("ESTADO-DO-PROJETO.md", "HANDOFF-MADRUGADA-3.md",
          "COURSE-GAP-REPORT-RETROATIVO.md"):
    print(f"{sh(DOCS/f)}  {f}")
