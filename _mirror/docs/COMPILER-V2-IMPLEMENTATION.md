# COMPILER v2 — IMPLEMENTAÇÃO

**Gerado:** `2026-08-12T01:40:24+00:00` · gerador `compiler_v2_freeze_report.py` · READ-ONLY sobre as árvores protegidas.

Relatório gerado por script. Nenhum número, hash ou citação foi digitado: cada citação da Fase 1 é extraída do arquivo real, com a linha em que aparece.


> **NADA FOI RECOMPILADO.** Nem PILOT-001, nem PILOT-002. A entrega é a implementação congelada, o canário aprovado e este relatório.


## FASE 1 — verificação do spec (portão)

### 1.1 Onde vive o prompt do compilador

| caminho | papel | sha256 | linhas | bytes |
|---|---|---|---|---|
| `Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1/course-to-skill-compiler-v0.1.1-pilot-ready/course-to-skill-compiler-v0.1.1-pilot-ready/prompts/lesson-analyzer.md` | RELEASE (extraído) | `d6205a8870044453…` | 1888 | 28965 |
| `Course-to-Skill/course-to-skill-compiler/prompts/lesson-analyzer.md` | cópia de trabalho | `5233d68f0ff2cc43…` | 1862 | 27677 |
| `Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1/course-to-skill-compiler-v0.1.1-pilot-ready.zip :: course-to-skill-compiler-v0.1.1-pilot-ready/prompts/lesson-analyzer.md` | RELEASE (dentro do zip) | `d6205a8870044453…` | 1888 | 28965 |

**A versão do RELEASE é `d6205a8870044453d1c0354a927234f33937c0a4ada0e76868ac50754c87edbf`** (1888 linhas). O arquivo extraído e o que está dentro do zip batem byte a byte.


> **Existe uma segunda versão.** A cópia de trabalho em `Course-to-Skill/course-to-skill-compiler/prompts/lesson-analyzer.md` tem hash diferente (`5233d68f0ff2cc43…`, 1862 linhas contra 1888). **Toda a Fase 1 foi conferida contra a do RELEASE**, que é a que o piloto usou.


### 1.2 A sequência real dos PASSes

```text
PASS 0 — Intake
PASS 1 — Temporal Mapping
PASS 2 — Evidence Extraction
PASS 3 — Decision Mining
PASS 4 — Workflow Mining
PASS 5 — Principle / Anti-pattern Mining
PASS 6 — Questions / Tools / Quality Gates
PASS 7 — Test Candidate Generation
PASS 8 — Skeptic Review
PASS 9 — Consolidation
PASS 10 — Pilot Readiness Decision
```

| linha | cabeçalho da seção |
|---|---|
| 321 | `# 11. PASS 0 — INTAKE` |
| 357 | `# 12. PASS 1 — TEMPORAL MAP` |
| 388 | `# 13. PASS 2 — EVIDENCE EXTRACTION` |
| 520 | `# 15. PASS 3 — DECISION MINING` |
| 673 | `# 19. PASS 4 — WORKFLOW MINING` |
| 797 | `# 24. PASS 5 — PRINCIPLE MINING` |
| 859 | `# 26. PASS 6 — QUESTIONS` |
| 957 | `# 29. PASS 7 — TEST CANDIDATE GENERATION` |
| 1187 | `# 32. PASS 8 — SKEPTIC REVIEW` |
| 1323 | `# 39. PASS 9 — CONSOLIDATION` |
| 1417 | `# 42. PASS 10 — PILOT READINESS DECISION` |

### 1.3 PASS 1 — texto literal (linhas 357–388)

```text
# 12. PASS 1 — TEMPORAL MAP

Divida a aula em segmentos semânticos.

Exemplo:

```text
SEG-001 | 00:00:00–00:04:12 | introdução
SEG-002 | 00:04:12–00:11:35 | conceito
SEG-003 | 00:11:35–00:19:44 | demonstração
SEG-004 | 00:19:44–00:27:10 | comparação
SEG-005 | 00:27:10–00:33:05 | exceções
```

## Regras

Não segmentar apenas por tempo.

Um novo segmento deve representar mudança relevante de:

- objetivo;
- conceito;
- demonstração;
- problema;
- decisão;
- ferramenta;
- exemplo;
- exceção.

---
```


### 1.4 PASS 2 — texto literal (linhas 388–455, início)

```text
# 13. PASS 2 — EVIDENCE EXTRACTION

Percorra cada segmento e extraia **unidades atômicas**.

Use IDs sequenciais:

```text
EV-0001
EV-0002
EV-0003
...
```

## Categorias disponíveis

```text
CONCEPT
PRINCIPLE
PROCEDURE
DECISION
RATIONALE
EXAMPLE
COUNTEREXAMPLE
ANTI_PATTERN
EXCEPTION
QUALITY_CRITERION
QUESTION
TOOL_USAGE
CONSTRAINT
WARNING
```

## Atomicidade

Uma evidência deve representar preferencialmente **uma única afirmação ou comportamento**.

Ruim:

```text
EV-0007:
```


Regra de ID no original: linha 392: `Use IDs sequenciais:`


### 1.5 Instruções de quantidade, cota, teto ou parada

Varredura por `no m[aá]ximo|no m[ií]nimo|at least|at most|pelo menos|limite…` nas 1888 linhas devolveu **3 acerto(s)**. Cada um classificado:

| linha | texto literal | é cota? |
|---|---|---|
| 709 | `- existem pelo menos duas ações relacionadas?` | NÃO é cota — critério do checklist de WORKFLOW (PASS 4), sobre o material da fonte, não sobre volume de extração |
| 763 | `- limite;` | NÃO é cota — campo a REGISTRAR sobre um laço encontrado na fonte (PASS 4), não instrução ao extractor |
| 764 | `- comportamento se limite for atingido.` | NÃO é cota — campo a REGISTRAR sobre um laço encontrado na fonte (PASS 4), não instrução ao extractor |

**Nenhum é alvo, teto ou cota de contagem para a extração.**


### 1.6 Passe de cobertura, saturação ou revarredura

Varredura por `cobertura|coverage|satura|revarr|rescan|re-scan|completude|completeness|exaustiv`: **0 ocorrência(s)** em 1888 linhas.


**Zero. Não existe passe de cobertura, saturação ou revarredura no spec do release.** Não há critério de parada: a extração termina quando o modelo para, e nada mede se a fonte foi esgotada.


### 1.7 PORTÃO

| # | alegação anterior | veredito | evidência |
|---|---|---|---|
| G1 | PASS 1 diz 'divida a aula em segmentos semânticos' | **CONFIRMA** | linha 359: `Divida a aula em segmentos semânticos.` |
| G2 | PASS 1 traz exemplo de exatamente CINCO segmentos | **CONFIRMA** | 5 linhas `SEG-xxx |` no bloco do PASS 1: `SEG-001 | 00:00:00–00:04:12 | introdução`; `SEG-002 | 00:04:12–00:11:35 | conceito`; `SEG-003 | 00:11:35–00:19:44 | demonstração`; `SEG-004 | 00:19:44–00:27:10 | comparação`; `SEG-005 | 00:27:10–00:33:05 | exceções` |
| G3 | PASS 1 diz 'não segmentar apenas por tempo' | **CONFIRMA** | linha 373: `Não segmentar apenas por tempo.` |
| G4 | PASS 2 diz 'percorra cada segmento e extraia unidades atômicas' | **CONFIRMA** | linha 390: `Percorra cada segmento e extraia **unidades atômicas**.` |
| G5 | nenhum alvo, teto ou cota de contagem em passe nenhum | **CONFIRMA** | 3 acerto(s) de termo de quantidade em 1888 linhas; todos classificados como não-cota |
| G6 | nenhum passe de cobertura, saturação ou revarredura | **CONFIRMA** | 0 ocorrência(s) de `cobertura|coverage|satura|revarr|rescan|re-scan|completude|completeness|exaustiv` em 1888 linhas |
| G7 | um único PASS de extração de evidência | **CONFIRMA** | `PASS 0 — Intake`; `PASS 1 — Temporal Mapping`; `PASS 2 — Evidence Extraction`; `PASS 3 — Decision Mining`; `PASS 4 — Workflow Mining`; `PASS 5 — Principle / Anti-pattern Mining`; `PASS 6 — Questions / Tools / Quality Gates`; `PASS 7 — Test Candidate Generation`; `PASS 8 — Skeptic Review`; `PASS 9 — Consolidation`; `PASS 10 — Pilot Readiness Decision` |

> ### ✅ PORTÃO ABERTO
>
> O spec real **confirma** o que havia sido reportado pela leitura do outro modelo, nos sete pontos. Nenhuma divergência material. A Fase 2 está autorizada.


---

## FASE 2 — implementação

### 2.1 A ADR, achada por hash

| item | valor |
|---|---|
| autoridade | `b8cddc93b74a65d6cbc2ad6859e4e3b8a4a81404137d4f95260f1b92668cf3f8` |
| encontrada em | `Course-to-Skill-Claude/pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md` |

> **Existe cópia divergente da ADR na árvore.** Achei o arquivo com o mesmo nome noutro lugar, com conteúdo diferente:

| caminho | sha256 | bate com a autoritativa? |
|---|---|---|
| `Course-to-Skill/PILOT-002/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md` | `35e8d00c278f9b99…` | **não — divergente** |

> Usei **só** a que casa com o hash informado. A outra está na árvore READ-ONLY e não foi tocada.


### 2.2 Arquitetura entregue

```text
PASS 1 → temporal-map.yaml persistido e hasheado
       → PASS 2[SEG-001] → PASS 2[SEG-002] → … → PASS 2[SEG-N]
       → dedup → portão de cobertura/saturação
       → revarredura DIRIGIDA aos blocos descobertos → dedup
       → COMPILATION_MANIFEST
```


### 2.3 Como cada exigência foi cumprida

| exigência | onde | como |
|---|---|---|
| DECISÃO A — PASS 2 por segmento | `ctsc2/extraction.py::run_pass2` | laço por segmento; o extractor recebe UM `Segment` por chamada. Não existe caminho no código que entregue a aula inteira. |
| nunca varredura monolítica | `ctsc2/extraction.py::_local_context` | o contexto local passa só IDs e limites dos vizinhos, nunca o conteúdo deles |
| DECISÃO B — portão depois do PASS 2 | `ctsc2/coverage_gate.py::run_gate` | mede, e enquanto não superar o piso, revarre |
| usa `cts/coverage.py` | `ctsc2/coverage_gate.py::load_coverage_module` | importa `cts.coverage` e **pina o hash** do módulo: métrica diferente quebra a comparabilidade e o portão avisa |
| revarredura dirigida | `ctsc2/coverage_gate.py::segments_for_blocks` | só os segmentos que intersectam bloco descoberto |
| temporal-map antes do PASS 2 | `ctsc2/temporal_map.py::write_and_seal` | `run_pass2` exige o handle e falha sem mapa em disco — dependência estrutural, não lembrete |
| manifesto completo | `ctsc2/manifest.py::build` | segmentos, yield por segmento, cobertura, limiar, resultado, iterações, hash do mapa |
| yield por segmento, inclusive ZERO | `ctsc2/extraction.py::SegmentYield` | uma linha por segmento, sempre; `run_pass2` levanta erro se o rastro não tiver o mesmo tamanho da lista de segmentos |
| IDs únicos e sequenciais entre chamadas | `ctsc2/model.py::IdAllocator` | alocador global monotônico; o extractor é proibido de numerar |
| limiar congelado > 73,5% | `ctsc2/thresholds.py::GatePolicy.satisfied` | `coverage > 0.735`, estritamente maior |

### 2.4 As proibições, e onde elas são visíveis

| proibição | estado no manifesto |
|---|---|
| alvo de contagem | ausente — `no_quota_declaration.count_target: null` |
| mínimo por segmento | ausente — `min_per_segment: null` |
| geração proporcional ao tempo | ausente — `proportional_to_time: false` |
| os ~200 | só como diagnóstico, nunca como cota |

> A busca por um alvo de contagem no código não devolve nada porque não há nada: nem constante, nem parâmetro, nem valor-padrão. O único número que decide alguma coisa é o piso de **cobertura**.


### 2.5 Condição de parada, que a ADR deixou em aberto

A §5 manda repetir "até o limiar ser satisfeito **ou uma condição de parada definida** ser atingida", sem fixar qual. Declarei-a **antes** de qualquer execução, em `ctsc2/thresholds.py`:

| parâmetro | valor congelado |
|---|---|
| máximo de iterações de revarredura | 3 |
| parada por progresso zero | sim — iteração que não acrescenta evidência nova encerra |

> A parada por progresso zero é o que impede laço infinito **sem** inventar cota: se a revarredura dirigida não achou mais nada nos blocos descobertos, repetir não vai achar.


---

## FASE 3 — canário

Cada caso roda **duas vezes**: contra a implementação real, onde tem de passar, e contra um mutante que encarna o defeito, onde tem de falhar. **Se o mutante passa, o caso não tem poder de detecção e a suíte inteira reprova**, mesmo com a execução real verde.

| caso | real passa | mutante falha | mutante injetado |
|---|---|---|---|
| C1_boundary_distinct | ✅ | ✅ | dedup por semelhança lexical (limiar 0,80) |
| C2_true_duplicate | ✅ | ✅ | dedup só por evidence_id — nunca funde |
| C3_zero_yield_visible | ✅ | ✅ | rastro omite segmento de yield zero |
| C4_below_threshold_rescans | ✅ | ✅ | portão sempre satisfeito — nunca revarre |
| C5_above_threshold_stops | ✅ | ✅ | portão sempre revarre — ignora o piso |


**C1_boundary_distinct**  
real: as duas vizinhas distintas sobreviveram, com proveniência  
mutante (`dedup por semelhança lexical (limiar 0,80)`): vizinha fundida: esquerda=ok, direita=PERDIDA


**C2_true_duplicate**  
real: duplicata real fundida (1 fusão(ões))  
mutante (`dedup só por evidence_id — nunca funde`): duplicata sobreviveu 2× (esperado 1), fusões=0


**C3_zero_yield_visible**  
real: segmento de yield zero visível no rastro (['SEG-001', 'SEG-002', 'SEG-003'])  
mutante (`rastro omite segmento de yield zero`): rastro tem 2 segmentos, esperado 3


**C4_below_threshold_rescans**  
real: revarredura disparada: 0.50 → 0.95 em 1 iteração(ões)  
mutante (`portão sempre satisfeito — nunca revarre`): cobertura abaixo do piso não disparou revarredura


**C5_above_threshold_stops**  
real: encerrou sem revarredura com cobertura 0.80 > 0.735  
mutante (`portão sempre revarre — ignora o piso`): revarreu 1× acima do piso


> ### ✅ SUÍTE APROVADA — 5/5


### 3.1 O que o C2 pegou de verdade

O canário não foi decorativo. Na primeira execução o **C2 reprovou** contra a implementação real: a fusão da duplicata acontecia dentro do portão, entre iterações, e **não subia para o manifesto**. A duplicata era corretamente fundida e o rastro de auditoria não registrava a fusão — exatamente o que a §9.7 da ADR manda enxergar. Corrigido em `GateResult.merges`.


Depois disso o C2 passou mas o **mutante também passou**, o que é o outro modo de falha: o mutante trocava `dedup` só em uma das três ligações e nunca alcançava o caminho real. Corrigido movendo o import para o topo de `coverage_gate.py` e trocando a função em **todas** as ligações. Sem essa segunda correção o C2 pareceria verde sem testar nada.


---

## Congelamento

| arquivo | sha256 | bytes |
|---|---|---|
| `README.md` | `c448246ff67f59e643469835dbc7ee987672793e205c35f60100a2d68bfefee9` | 2231 |
| `canary/canary-results.json` | `21114e40832d9680035b2d8cea4aa3b29b508d6df4d0a69941fb372de9e88aed` | 1779 |
| `canary/fixtures.py` | `240c296a5e02c34707cc6c3a508e6f09b46387b754976bcd24434d64f4a9979b` | 4606 |
| `canary/mutants.py` | `0765a0ae0330e532609cbde9b86a57ae1e509f19b4b3118e921ab62de7ede666` | 6931 |
| `canary/run_canary.py` | `95cc95bf2afa2b673bd23f4cb49dcd943c7631e764c01218d43288308393e6da` | 7252 |
| `ctsc2/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `ctsc2/coverage_gate.py` | `fd16ee3f6782f3b10eb8e2087169999bc6c9f528a10040e962f931274905ef1c` | 7029 |
| `ctsc2/dedup.py` | `527d04013bb470bf7cecc655598bcafbe7f7f70e474761d8f95facbdad1aa0df` | 3866 |
| `ctsc2/extraction.py` | `c472f5f918d03e39b9d673218c48978dbd5f8f31a53ad5072855c27c664e3ee1` | 5812 |
| `ctsc2/manifest.py` | `6d206cb556d7af978d68ca264b00093dcc37f6c4f278c3bef087bb624f48ed91` | 5537 |
| `ctsc2/model.py` | `9d9edcce4159a7ceb42dccec50d41ac2c631cd048d23ff3b1e607595898e55e5` | 3811 |
| `ctsc2/pipeline.py` | `f22dcae86197e7b0ef2eaf758eef333b236374cdaa521086e167b96dc5afddb3` | 3425 |
| `ctsc2/temporal_map.py` | `aa76c52ac8117a0ec6372f532a381bfaa950d1fd9ed01b45fcb4ca18a7f8273a` | 3168 |
| `ctsc2/thresholds.py` | `344a40edcf6a441b012b29a5d375c17caef430f4b0df978e7e451fb6f97f0942` | 4656 |
| `prompts/lesson-analyzer-v2.md` | `b6cb365cafee8ce4248e0f8c8a79d587af44a1b6fa79f7381635e4d10a5cfed1` | 5496 |

**Hash do conjunto congelado:** `595b81c8f93bdf1c500122f13058fd11f1347f979205fce94ce845f681ec3c6d`  
(sha256 sobre a lista ordenada de `(caminho, sha256)` — muda se qualquer arquivo mudar.)


Módulos que definem a métrica de cobertura, pinados:

| módulo | sha256 |
|---|---|
| `cts/coverage.py` | `ea58c05efd778cb906ac4fee7669d00b7029a72e993f8077fc36231a8f97723b` |
| `cts/spans.py` | `7bcdcde2c85e2f814ec9d80b2c5aba38c1905ce17c7001ca35a3b3a42d18bb74` |

> A métrica vive fora de `compiler-v2/` (em `cts/`) e é importada. O hash acima é conferido em execução: se `cts/coverage.py` mudar, os dois pilotos deixam de ser comparáveis e o portão precisa ser reavaliado — que é a trava de comparabilidade da §12 da ADR.


## O que falta, e não foi feito

| item | estado | observação |
|---|---|---|
| extractor ligado a modelo real | **não existe** | `Extractor` é um Protocol; as únicas implementações são fixtures de canário. Ligar ao modelo é passo separado. |
| recompilação do PILOT-001 | **não feita** | proibida nesta fase |
| recompilação do PILOT-002 | **não feita** | depende do aceite do PILOT-001 corrigido (§13) |
| banda 7–11 do PASS 1 | implementada, não exercida | `pass1_in_band()` e o flag existem; só um run real os aciona |

---

**Escopo:** nenhum arquivo de `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado. Tudo o que foi escrito está em `Course-to-Skill-Claude/compiler-v2/` e neste relatório.
