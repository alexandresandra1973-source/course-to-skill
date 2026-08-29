# HANDOFF — MADRUGADA 3

*Sessão autônoma. Três frentes. Zero chamadas nas frentes B e C; **3 chamadas no total**, todas no canário.*

## PRONTO

### Frente B — COURSE-GAP-REPORT retroativo *(era o que você mais queria ver)*

`docs/COURSE-GAP-REPORT-RETROATIVO.md` · `c3f1295b3bc3b535…`

Três categorias separadas, porque confundi-las inverte o significado: **lacuna do curso** (culpa do curso) · **não alcançado** (limite da medição) · **qualidade da transcrição** (culpa do insumo).

**Duas correções materiais no caminho:**

1. Os quatro campos UNDEFINED (`autonomy`, `precedence`, `missing_input_action`, `iteration_limit`) são do **PILOT-002**, não do PILOT-001. O PILOT-001 tem o seu próprio conjunto e é maior: **169 campos vazios**, dos quais **84 são pedagógicos** e o resto é metadado.
2. Os **2.151s / 49,1%** de território virgem são da rodada **antiga de 44 evidências**. Recomputado sobre as 448 e descontando as janelas de held-out: **0s (0.0%)** — ou seja, **nenhum trecho de um minuto inteiro ficou sem cobertura**. O virgem total caiu para 772s (17.6%).

> Sem descontar o held-out explicitamente, a janela de 44:40–50:00 aparece como o maior 'bloco virgem' do corpus. É a **quarta vez** que essas janelas contaminam um número meu.

### Frente A — arnês e canário do compilador evidência→Skill

`compiler-s3/` · canário estático **15/15** · canário fail-closed com chamada real **APROVADO**

As três decisões que você mandou estão implementadas:

- **RG-013-001 parametrizado**, RG-013-004 byte a byte (`50848d02…` conferido por canário). A policy derivada declara `derived_from` com os campos parametrizados e os imutáveis. **A condição de escopo exige justificativa**: sem `EVIDENCE_CITED` ou `DECISAO_DE_INSTRUMENTO` o derivador levanta erro — silêncio não passa.
- **MODEL_INFERENCE separado** pelo detector de corrupção: PILOT-002 tem **10 correções de transcrição** (contam como curso) e **78 inferências genuínas** (não contam). PILOT-001: 2 e 7. Regra apoiada **só** em inferência genuína vira lacuna do curso — testado no canário.
- **Esquema subconjunto** com os quatro preservados por nome; **30 campos legados descartados**, cada um com o motivo escrito, em `ctss/schema.py`.

**O canário F é o que prova a política.** Sem os dois YAML, a resposta real foi a recusa canônica **byte a byte**, sem vazar um passo de metodologia. Com os recursos presentes, executou citando `evidence_id` e recusou **apenas** a parte não coberta.

### Frente C

`docs/ESTADO-DO-PROJETO.md` · `78cb8fc2e7605022…`

## O QUE TRAVOU

**Nada travou por bloqueio externo.** Duas paradas foram por instrução sua:

1. **As 41 chamadas da compilação real não foram gastas** — você mandou parar no canário.
2. **A rubrica do TEST-0008 não foi enviada ao auditor** — o teste de vazamento reprovou nas três rodadas.

**Duas coisas quebraram e eu consertei o desenho, não o verificador:**

- o detector de rota do `SKILL.md` acusava a **própria redação canônica** ("hard runtime stops *when* emitted") — troquei heurística de marcador por **reconstrução exata a partir do template**;
- o critério do controle F2 reprovava por conter `METHOD_NOT_DEFINED` em qualquer lugar, confundindo **recusar o pedido inteiro** com **recusar a parte não coberta** — que é a política funcionando. Reavaliei a **mesma** resposta com o critério certo, sem gastar chamada nova.

## O QUE VOCÊ DECIDE

| # | decisão | custo |
|---|---|---|
| 1 | **soltar as 41 chamadas** da compilação evidência→Skill | ~41 chamadas |
| 2 | rubrica do TEST-0008: mudar desenho, ou aceitar o vazamento residual e enviar | zero |
| 3 | `GENUINE_INFERENCE` no PILOT-002 é **78 de 448 (17,4%)**. Se muitas regras se apoiarem só nelas, o COURSE-GAP-REPORT vai dizer que o curso ensina menos do que parece. Confirmar que é isso que se quer medir | zero |

**A minha recomendação para a #1: soltar.** O arnês está fechado por canário em todos os pontos que você listou, o custo é o mesmo do PASS 2 que já rodou duas vezes sem incidente, e é a única frente que destrava as outras — os 10 casos cegos do PILOT-002 estão parados esperando uma Skill existir.
