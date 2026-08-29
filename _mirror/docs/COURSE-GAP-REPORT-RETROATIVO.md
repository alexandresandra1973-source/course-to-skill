# COURSE-GAP-REPORT — RETROATIVO E PARCIAL

> ## ⚠ Leia isto antes dos números
> **Este relatório é RETROATIVO e PARCIAL.** A Skill executável que o avaliador de curso deveria produzir **ainda não existe**. O que está aqui foi reconstruído dos artefatos já medidos, e serve para mostrar **a FORMA da saída** — não para avaliar os dois cursos.
> 
> Um relatório completo diria *"o método deste curso funciona quando executado"*. Este diz apenas *"eis o que o curso deixou de especificar, e eis o que ainda não conseguimos medir"*.

Gerado por `publish_course_gap_report.py`. Nenhum número digitado à mão. Zero chamadas de modelo.

---

## As três categorias, e por que separá-las importa

| | o que é | de quem é a falha |
|---|---|---|
| **A — LACUNA DO CURSO** | o curso não ensinou o que a execução exigiria | **do curso** |
| **B — NÃO ALCANÇADO** | a extração não chegou àquele trecho | **da medição** |
| **C — QUALIDADE DA FONTE** | a transcrição está corrompida | **do insumo** |

**Confundir A com B inverte o significado.** Território não alcançado lido como lacuna do curso reprova um curso que talvez ensine muito bem o que não foi medido. E lacuna do curso lida como falha de medição absolve um curso que de fato não ensinou.

---

# A · LACUNAS DO CURSO

## PILOT-001 — *How to Build Your First AI Agent*

A Skill compilada tem **8 regras de decisão** e **1 workflow**. Ao montá-la, **169 campos** ficaram vazios.

Desses, **85 são metadados** — quem é o professor, número de versão, data de criação. Não dizem nada sobre o curso.

**84 são lacunas de verdade.** São perguntas que quem tentar executar o método vai fazer, e que a aula não responde:

| o que faltou | quantas vezes | a pergunta que o curso não responde |
|---|---|---|
| `ask_user_if_missing` | 27 | o que perguntar ao usuário quando falta um insumo |
| `steps` | 16 | os passos concretos de um procedimento |
| `precedence` | 8 | qual regra ganha quando duas se aplicam ao mesmo tempo |
| `approval_before` | 8 | que ação exige aprovação humana antes de executar |
| `level` | 7 | o grau de autonomia declarado |
| `tools` | 6 | com que ferramenta cada passo é executado |
| `required_inputs` | 4 | o que é obrigatório ter antes de começar |
| `optional_inputs` | 3 | o que ajuda mas não bloqueia |
| `decision_points` | 2 | onde o procedimento bifurca e com que critério |
| `loops` | 1 | o que se repete e sob que condição de parada |
| `behavior` | 1 | como o agente se comporta nesse ponto |
| `outputs` | 1 | o que o passo entrega |

**A maior é `ask_user_if_missing`, 27 vezes.** O curso ensina o que fazer quando tudo está disponível. Não ensina o que perguntar quando falta alguma coisa — e faltar alguma coisa é o caso normal.

### As lacunas com timestamp

Cada uma aponta o minuto da aula onde a resposta deveria estar:

| regra | campo vazio | trecho da aula |
|---|---|---|
| `ADR-0001` — Começar pelo outcome, não pela tarefa | `precedence` | 1:30–1:55 |
| `ADR-0001` — Começar pelo outcome, não pela tarefa | `ask_user_if_missing` | 1:30–1:55 |
| `ADR-0001` — Começar pelo outcome, não pela tarefa | `level` | 1:30–1:55 |
| `ADR-0001` — Começar pelo outcome, não pela tarefa | `approval_before` | 1:30–1:55 |
| `ADR-0002` — Escolher o primeiro agente pelo gap de maior custo de tempo | `precedence` | 5:49–14:09 |
| `ADR-0002` — Escolher o primeiro agente pelo gap de maior custo de tempo | `ask_user_if_missing` | 5:49–14:09 |
| `ADR-0002` — Escolher o primeiro agente pelo gap de maior custo de tempo | `level` | 5:49–14:09 |
| `ADR-0002` — Escolher o primeiro agente pelo gap de maior custo de tempo | `approval_before` | 5:49–14:09 |
| `ADR-0003` — Escolher plataforma conforme contexto atual | `precedence` | 7:19–8:59 |
| `ADR-0003` — Escolher plataforma conforme contexto atual | `ask_user_if_missing` | 7:19–8:59 |
| `ADR-0003` — Escolher plataforma conforme contexto atual | `level` | 7:19–8:59 |
| `ADR-0003` — Escolher plataforma conforme contexto atual | `approval_before` | 7:19–8:59 |
| `ADR-0004` — Definir input, output e boundaries antes da plataforma | `precedence` | 9:08–9:46 |
| `ADR-0004` — Definir input, output e boundaries antes da plataforma | `ask_user_if_missing` | 9:08–9:46 |

## PILOT-002 — *Claude Code em 60 minutos*

A compilação legada (44 evidências) declarou **4 campos indefinidos**:

| campo | a pergunta que o curso não responde |
|---|---|
| `autonomy` | até onde o agente pode agir sozinho antes de parar |
| `precedence` | qual regra ganha quando duas se aplicam ao mesmo tempo |
| `missing_input_action` | o que fazer quando um insumo obrigatório não veio |
| `iteration_limit` | quantas vezes repetir antes de desistir |

**Os quatro são de governança, e é o padrão mais claro dos dois pilotos.** O curso mostra o agente trabalhando sozinho e não diz até onde ele pode ir (`autonomy`), o que fazer quando falta um insumo (`missing_input_action`), quantas vezes tentar antes de desistir (`iteration_limit`), nem qual regra vence quando duas se aplicam (`precedence`).

> **Correção de atribuição.** Estes quatro campos foram atribuídos ao PILOT-001 no pedido. Eles são do **PILOT-002** — constam do `COMPILATION_MANIFEST` da skill v0.1.0 daquele piloto (`81d2b6c698421af3…`). O PILOT-001 tem o seu próprio conjunto, medido acima, e ele é maior.

A rodada nova do PILOT-002, com **448 evidências**, ainda não foi compilada em Skill — é a Frente A. Quando for, esta seção passa a ter timestamps como a do PILOT-001.

---

# B · TERRITÓRIO NÃO ALCANÇADO — limite da medição, NÃO do curso

## PILOT-002

| | |
|---|---|
| duração do vídeo | 81:37 |
| retirado como held-out | 513s (11:55–15:08, 44:40–50:00) |
| corpus medido | 4384s |
| **coberto por evidência** | **82.39%** |
| não alcançado | 772s (17.6%) em 91 trechos |
| **trechos contínuos ≥ 60s** | **0** |

**Nenhum trecho de um minuto inteiro ficou sem cobertura.** Os maiores buracos são estes, e todos cabem em menos de um minuto:

| trecho | duração | seção da aula |
|---|---|---|
| 80:15–80:57 | 42s | FAQ — Will This Be Outdated in a Month? |
| 53:00–53:22 | 22s | Managing Plugins and Installed Skills |
| 36:53–37:11 | 18s | File Formats, Dependencies, and Project Folders |
| 34:36–34:53 | 17s | Finding and Installing Additional Skills |
| 44:17–44:34 | 17s | AGENTS.md, CLAUDE.md, and System Prompts |
| 56:16–56:33 | 17s | Version Control Concepts with GitHub |

> ### Correção de um número que circulava
> O valor conhecido era **2.151s sem cobertura em blocos ≥60s, 49,1% do corpus**. Ele vem de `PILOT-002-EXTRACTION-SCALING.md` e mede a rodada **antiga, de 44 evidências**. Recomputado sobre as 448 da rodada atual, e descontando as janelas de held-out, o valor é **0s (0.0%)** — ou seja, **zero**.
> 
> As janelas de held-out precisam ser descontadas explicitamente: sem isso, a maior delas (44:40–50:00) aparece como o maior 'bloco virgem' do corpus, e território deliberadamente removido vira falha de extração.

---

# C · QUALIDADE DA TRANSCRIÇÃO — falha do insumo

A fonte é transcrição automática. Ela erra nomes próprios e às vezes **perde negações**, que é o erro grave: o texto continua gramatical e diz o contrário.

| piloto | evidências | divergências detectadas | taxa | propagadas como fonte |
|---|---|---|---|---|
| PILOT-001 | 149 | 5 | **3.36%** | 3 (2.01%) |
| PILOT-002 | 448 | 22 | **4.91%** | 12 (2.68%) |

A coluna que importa é a última: quantas vezes o compilador **corrigiu** a transcrição e ainda assim rotulou a afirmação como *"a fonte diz isto"*. Corrigir é desejável; corrigir e chamar de fonte explícita é o dano.

---

## O que este relatório ainda NÃO diz

- **Se o método de cada curso funciona.** Isso exige compilar a Skill, executá-la e ver se ela entrega. É a Frente A, não iniciada.
- **Quanto de cada lacuna importa.** Um `precedence` vazio pode ser fatal ou irrelevante dependendo de quantas regras competem na prática.
- **Se as lacunas são do curso ou do compilador.** Um campo vazio pode significar que a aula não ensinou, ou que o extrator não achou. Separar as duas exige o portão de cobertura evidência→regra, que é parte da Frente A.

---

*Gerado em 2026-08-12 · retroativo e parcial · a Skill executável não existe*
