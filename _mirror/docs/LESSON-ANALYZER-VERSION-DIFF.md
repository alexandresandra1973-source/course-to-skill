# LESSON-ANALYZER — DIFF DAS DUAS VERSÕES

**Gerado:** `2026-08-12T01:57:49+00:00` · gerador `lesson_analyzer_version_diff.py` · READ-ONLY nas duas árvores.

Relatório gerado por script; nenhuma linha, número ou hash foi digitado.


## 1. As duas versões

| caminho | papel | sha256 | linhas |
|---|---|---|---|
| `Course-to-Skill/course-to-skill-compiler/prompts/lesson-analyzer.md` | cópia de trabalho | `5233d68f0ff2cc43fa35588b1ff6be8506c19e502478ca0688c946e60062cfcc` | 1862 |
| `Course-to-Skill-Compiler/01_TOOL/releases/v0.1.1/course-to-skill-compiler-v0.1.1-pilot-ready/course-to-skill-compiler-v0.1.1-pilot-ready/prompts/lesson-analyzer.md` | RELEASE v0.1.1 | `d6205a8870044453d1c0354a927234f33937c0a4ada0e76868ac50754c87edbf` | 1888 |

O release dentro do zip tem sha256 `d6205a8870044453d1c0354a927234f33937c0a4ada0e76868ac50754c87edbf` — idêntico ao extraído.


Diferença de tamanho: **+26 linhas**.


## 2. Faixas de PASS em cada versão

| PASS | cópia de trabalho | release | posição |
|---|---|---|---|
| PASS 0 | L321–356 | L321–356 | iguais |
| PASS 1 | L357–387 | L357–387 | iguais |
| PASS 2 | L388–454 | L388–454 | iguais |
| PASS 3 | L520–563 | L520–563 | iguais |
| PASS 4 | L673–702 | L673–702 | iguais |
| PASS 5 | L797–839 | L797–839 | iguais |
| PASS 6 | L859–886 | L859–886 | iguais |
| PASS 7 | L957–972 | L957–972 | iguais |
| PASS 8 | L1187–1206 | L1187–1206 | iguais |
| PASS 9 | L1323–1348 | L1323–1348 | iguais |
| PASS 10 | L1417–1463 | L1417–1463 | iguais |

### 2.1 Conteúdo dos passes críticos, por hash

Prova independente do portão: se o hash do bloco bate, o passe é idêntico byte a byte, sem depender de como o diff alinhou as linhas.

| PASS | hash (trabalho) | hash (release) | veredito |
|---|---|---|---|
| PASS 1 | `a72e7f18c032f505c749eead…` | `a72e7f18c032f505c749eead…` | **IDÊNTICO** |
| PASS 2 | `783fda4d1aa686ba5cd63328…` | `783fda4d1aa686ba5cd63328…` | **IDÊNTICO** |

## 3. Diff completo

**2 bloco(s) de diferença.**


### Bloco 1 — metadado de versão — sem efeito sobre instrução

| localização |
|---|
| trabalho L4–4: (antes da primeira seção — cabeçalho do documento) |
| release L4–4: (antes da primeira seção — cabeçalho do documento) |

```diff
-**Version:** `0.1.0`  
+**Version:** `0.1.1`  
```

### Bloco 2 — acréscimo fora de qualquer PASS

| localização |
|---|
| release L1863–1888: # 55. FINAL QUESTION |

```diff
+
+---
+
+# v0.1.1 HARDENING ADDENDUM — HELD-OUT LOCK & TEST CLOSURE
+
+## H1. Pre-modeling held-out lock
+
+Antes de entregar registros ao Methodology Modeler:
+
+1. identificar, quando o volume de fonte permitir, casos adequados para avaliação futura;
+2. criar `held-out-registry.yaml` usando `schemas/held-out-registry.schema.yaml`;
+3. marcar `created_before_modeling: true` e `locked: true`;
+4. retirar esses casos do pacote consumido pelo modelador;
+5. nunca incluir reference answer em contexto acessível ao agente avaliado.
+
+Se não houver diversidade/material suficiente, registrar `registry_status: NOT_AVAILABLE` e `pilot_only: true`. Não selecionar held-out retroativamente depois de a Skill ter sido compilada.
+
+## H2. Candidate-test input closure
+
+Ao gerar cada test candidate, cruzar o caso com `required_inputs` da ADR/workflow relacionada.
+
+- Se o comportamento esperado exige decisão direta (`should_ask_user: false`), preencher todos os inputs REQUIRED relevantes.
+- Se um REQUIRED foi removido deliberadamente, o teste deve ser `MISSING_INPUT`/`EDGE_CASE` e esperar pergunta/stop correspondente.
+- Se não for possível fechar os inputs sem inventar contexto, marcar o teste `BLOCKED`.
+
+Registrar `TEST_DESIGN_FAILURE` quando a expectativa contradiz os inputs fornecidos.
```


## 4. Classificação

| # | operação | linhas (trabalho) | linhas (release) | classificação |
|---|---|---|---|---|
| 1 | replace | L4–4 | L4–4 | metadado de versão — sem efeito sobre instrução |
| 2 | insert | — | L1863–1888 | acréscimo fora de qualquer PASS |

## 5. PORTÃO

> ### ✅ PORTÃO ABERTO — nenhuma diferença toca PASS 1 ou PASS 2
>
> Os 2 blocos de diferença ficam **inteiramente fora** dos dois passes que o diagnóstico do colapso mediu. As faixas de linha do PASS 1 e do PASS 2 são idênticas nas duas versões e o texto dentro delas é o mesmo byte a byte.
>
> **Consequência:** mesmo sem saber qual das duas versões compilou o PILOT-002, o diagnóstico do colapso não é afetado — as duas dizem exatamente a mesma coisa sobre segmentação e extração.


## 6. Qual das duas compilou o PILOT-002? NÃO SABEMOS

Isto não é dedução, é ausência de registro. Nenhum artefato da compilação do PILOT-002 grava a versão do prompt:

| artefato | caminho | estado | registra o prompt? |
|---|---|---|---|
| COMPILATION_MANIFEST do PILOT-002 | `Course-to-Skill-Claude/pilots/PILOT-002/01_COMPILED-SKILL/v0.1.0/COMPILATION_MANIFEST.yaml` | existe | não |
| GOVERNANCE.yaml do PILOT-002 | `Course-to-Skill-Claude/pilots/PILOT-002/01_COMPILED-SKILL/v0.1.0/GOVERNANCE.yaml` | existe | não |
| VALIDATION_REPORT.md do PILOT-002 | `Course-to-Skill-Claude/pilots/PILOT-002/01_COMPILED-SKILL/v0.1.0/VALIDATION_REPORT.md` | existe | não |
| SCOPE-LOCK pré-compilação | `Course-to-Skill/PILOT-002/00_PRECOMPILE_GOVERNANCE/PILOT-002-PRECOMPILE-SCOPE-LOCK.yaml` | existe | não |
| ADR de pipeline limpo, pré-compilação | `Course-to-Skill/PILOT-002/00_PRECOMPILE_GOVERNANCE/ADR-PILOT002-FIRST-CLEAN-PIPELINE-VALIDATION.md` | existe | não |

**0 de 5 artefatos registram a versão do prompt.**


### O que existiria em disco, se existisse, e decidiria a questão

| evidência que decidiria | força | estado real |
|---|---|---|
| `compiler_version` ou `prompt_sha256` no `COMPILATION_MANIFEST` | decidiria sozinho | **não existe** — o manifesto grava entrada, evidências e campos indefinidos, mas nada sobre o compilador |
| hash do prompt no `GOVERNANCE.yaml` | decidiria sozinho | **não existe** — grava `scope_lock` e `adr` por prefixo, não o prompt |
| registro de execução / log da compilação | decidiria sozinho | **não existe** na árvore |
| cópia do prompt dentro do pacote compilado | decidiria sozinho | **não existe** — o pacote traz SKILL, EVIDENCE, GOVERNANCE, MANIFEST e VALIDATION, nenhum prompt |
| mtime dos arquivos | não decide | prova apenas que as duas versões já existiam antes da compilação |

> **Registrado como incerteza aberta.** Pelo §5 a resposta não muda o diagnóstico do colapso, porque a diferença não toca os passes medidos. Mas ela continua desconhecida, e o compilador v2 já corrige isso: o `COMPILATION_MANIFEST` v2 grava `compiler_version` e o hash do `temporal-map`, de modo que a mesma pergunta não vai ficar sem resposta na próxima compilação.


---

**Escopo:** somente leitura e comparação. Nenhum arquivo de `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado. O único arquivo escrito é este relatório.
