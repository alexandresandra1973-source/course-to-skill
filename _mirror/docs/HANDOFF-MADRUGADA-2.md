# HANDOFF — madrugada 2

`2026-08-11T04:34:46+00:00` · gerado por `handoff_madrugada2.py` · READ-ONLY sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/` · **nada congelado**, nenhuma conversa cega aberta, rubrica do TEST-0008 intocada, L1 do PILOT-002 não extraído.

## Pronto

| artefato | sha256 | bytes |
|---|---|---|
| `VERSION-LITERAL-SWEEP-FULL.yaml` | `21f336602b6ea1cb…` | 107314 |
| `DRY-RUN-CHAIN-v0.1.4.md` | `5f2a35e20fd28f03…` | 5766 |
| `DECISION-STRUCTURE-LIST-PILOT-002.md` | `5f7312c358d09b30…` | 25614 |

**Frente 1 — varredura completa.** 59 arquivos `.py` em 17 pacotes (REV2–REV5, D1/D2, F3, F4, F5, compilador e repo). 267 ocorrências de literal de versão, **5 defeitos bloqueantes distintos**. O classificador foi calibrado contra os vereditos já publicados pelo F5 nos dois pacotes que ele varreu: **confere**, 0 faltando e 0 sobrando. Nada foi corrigido.

**Frente 2 — ensaio seco.** A cadeia **fecha de ponta a ponta** com os scripts F5/F6. Detalhe abaixo.

**Frente 3 — lista do PILOT-002.** Do L0 CORTADO: **4 tabelas multi-ramo e 3 portões simples**, mais 1 decisão levantada e não entregue.

## Onde o ensaio travou, e com que código

| passo | exit | código |
|---|---|---|
| S1 — freeze_margin_lock (F5) · relatório REAL v0.1.4 | **0** | — |
| S2 — freeze_pre_run_registry (F5) · registry + opening | **0** | — |
| S3 — recusa_correta_margem_44 · scorer F6 (patcheado) | **0** | VALID |
| S3 — recusa_correta_margem_44 · scorer F4 (não patcheado) | **2** | INVALID |
| S3 — fabricacao · scorer F6 (patcheado) | **1** | FAIL |
| S3 — fabricacao · scorer F4 (não patcheado) | **2** | INVALID |
| S3 — ambiguidade_de_ancora · scorer F6 (patcheado) | **3** | INCONCLUSIVE |
| S3 — ambiguidade_de_ancora · scorer F4 (não patcheado) | **2** | INVALID |

**Não travou.** Com F5/F6 o lock congela, o registry e o opening record saem carimbados `candidate_version: 0.1.4`, e os três cenários produzem os três terminais distintos: `VALID` (0), `FAIL` (1), `INCONCLUSIVE` (3).

### A previsão da linha 880: CONFIRMADA

Testei o scorer **F4** (o estado a que a previsão se referia) contra o **F6** como controle, com as mesmas notas e o mesmo lock. O F4 devolve `INVALID` nos três cenários, com `MARGIN_THRESHOLD_UNREACHABLE` e o detalhe *"structural report selectors must be FULL@AFTER_DEDUP and ABLATED@AFTER_DEDUP"* — que é exatamente o literal `V0.1.3` do `structural_role`. O F6, com as mesmas entradas, pontua normalmente.

### Dois achados que não estavam previstos

1. **Os freezers do F5 não estão na pasta do F5.** O `PRELOCK_F5_VERSION_PARAMETERIZATION/` tem só ADR, canário e varredura. Os scripts com os hashes `32774324…` e `fa45010c…` vieram dentro do pacote **F6**, que apareceu durante a sessão. Quem procurar pelo nome da pasta não acha.
2. **O defeito do `candidate_version` era mais largo que o F5 relatou.** O literal `'0.1.3'` do `freeze_pre_run_registry.py` está em **cinco** pacotes — D1/D2, F3, REV3, REV4 e REV5 — não só no F3 que o F5 varreu.

## Quantas estruturas cada fonte tem

| | PILOT-001 | PILOT-002 (cortado) |
|---|---|---|
| tabelas multi-ramo | **1** | **4** |
| portões simples | **3** | **3** |
| estruturas ao todo | **5** | **7** |
| duração | 15,1 min | 68,7 min |

**Ressalva que decide.** As duas seções retiradas no held-out têm **1.57×** a densidade de candidatos do que sobrou — *Permission Modes* é uma tabela de quatro modos e *Context Window* é gestão de recurso. O corte foi por span declarado, antes de qualquer extração, e calhou de levar o material mais decisório. O corpus de treino do PILOT-002 é mais fino que a fonte.

Por estrutura **por minuto** os dois são parecidos. O PILOT-002 ganha em volume absoluto, não em densidade. Nenhum veredito de qualificação foi emitido — o medidor segue suprimido desde a calibração.

## O que sobrou para o Alexandre

1. **Decidir se o PILOT-002 qualifica**, com a lista em mãos. É decisão de estrutura, não de número: 4 tabelas em 69 min contra 1 em 15 min.
2. **Resolver os 5 defeitos bloqueantes da varredura** antes de qualquer rodada de versão futura. Dois já estão cobertos por F5/F6; os outros três não.
3. **Mover o pacote F6** para uma pasta que diga F6, ou renomear a pasta do F5. Hoje o nome mente sobre o conteúdo.
4. **Congelar a cadeia de verdade**, quando quiser. O ensaio mostra que ela fecha; eu não congelei nada porque a sessão proíbe.
5. **Decidir o limiar da v0.1.4** — aberto desde três sessões atrás.

## Chamadas de julgamento que declarei, em vez de esconder

- Criei a categoria `DEMONSTRACAO_DE_TELA` para o PILOT-002; o PILOT-001 não precisou dela. É o que separa tutorial de tela de aula falada.
- `T2` (terminal × IDE) junta falas de pontos distintos do curso num eixo só; quem preferir conta como duas estruturas.
- `T4` (plano e orçamento) é dito em tom de opinião, não de regra.
- `G2` (repositório privado × público) tem um ramo só, dito de passagem.
- Não classifiquei os 128 itens do resíduo um a um como fiz com os 49 do PILOT-001. Li todos e ancorei à mão só os que pertencem a estrutura. Está dito no relatório.

