# REGRA DO PRODUTO — buscar por RADICAL, nunca por forma literal

**Status:** REGRA_ATIVA · registrada 2026-08-27 · vale para toda verificação do projeto

## O padrão, na sétima ocorrência

Toda verificação deste projeto que buscou **forma literal** perdeu variantes. Sete
vezes, em contextos sem relação entre si.

| # | Onde | Buscou a forma | Perdeu |
|---|---|---|---|
| 1–6 | matcher de temas do PILOT-003 | forma exata do tema | seis erros de casamento: tradução pt↔en, reordenação de palavras, diacrítico, plural, corrupção do ASR, maiúscula |
| 7 | addendum de resíduo do PILOT-002 | `/compact`, `/context` **com barra** | `compact` sem barra em `50:00`; `percentage of the context window` em `9:12` e `51:16` |

O caso 7 é o mais caro, porque a busca literal produziu uma **declaração positiva
de limpeza**: o addendum listou `/compact` e `/context` em `verified_clean` e
declarou a seção de janela de contexto `LIMPA`. Ela não estava. O termo estava lá
sem a barra, no primeiro bloco depois do corte.

## Por que a forma literal falha estruturalmente

O que se busca é um **conceito**; o que se digita é **uma** de suas grafias. As
outras existem e não estão na consulta:

- **afixo** — `compact` / `/compact` / `compacting` / `compaction`;
- **flexão** — `permission` / `permissions`; `mode` / `modes`;
- **tradução** — `termos` / `terms`; `agentes` / `Agents`;
- **corrupção do ASR** — `Claude` → `claw`; `ROAS` → `rows`;
- **paráfrase falada** — `/context` nunca é dito, mas *"percentage of the context
  window that we have consumed"* ensina a mesma coisa;
- **ordem** — `negative keyword` / `keyword negative`.

Numa transcrição automática de fala, a forma canônica é a **menos** provável: o
instrutor fala, não digita. Buscar a grafia canônica em texto falado é buscar
justamente a forma que tende a não estar lá.

## A regra

> **Toda verificação que conclui ausência busca por RADICAL ou TOKEN, nunca por
> forma exata. Concluir "não está" a partir de busca literal é proibido.**

Procedimento:

1. reduzir o alvo ao **radical** — `compact`, não `/compact`; `permiss`, não
   `permissions`; `window`, não `context window`;
2. varrer com o radical e **listar todas** as ocorrências com marca de tempo;
3. classificar cada ocorrência à mão em **verdadeira** ou **falso positivo**;
4. **publicar os falsos positivos**, não descartá-los em silêncio.

O passo 4 não é zelo: é o que torna a varredura auditável. Uma varredura por
radical que reporta só os acertos é indistinguível de uma varredura literal com
sorte.

## O custo, declarado

Busca por radical **produz ruído**, e ruído é o preço. Na varredura do
`ADDENDUM-2` do PILOT-002, cinco radicais deram falso positivo:

| radical | casou com | é o que se procurava? |
|---|---|---|
| `rot` | `protocol` | não — `context rot` tem zero ocorrências |
| `fresh` | `refresh`, `fresh design` | não — `fresh context` não aparece |
| `window` | `Windows`, o sistema operacional | em 1 de 5 ocorrências, não |
| `clear` | `clear a terminal`, `clear plan` | não — `/clear` não aparece |
| `flag` | `flagging`, num diff | não — não é flag de linha de comando |

**Cinco falsos positivos é um resultado bom, não ruim.** Eles custam uma leitura
manual cada. A alternativa — busca literal — custou uma declaração de limpeza
errada num artefato congelado, e essa só foi descoberta porque a Skill, ao ser
testada, citou uma regra sobre `/compact` que segundo o addendum não deveria
existir.

## Aplicação retroativa

Esta regra foi aplicada retroativamente ao addendum de resíduo do PILOT-002. O
resultado está em `HELDOUT-RESIDUE-ADDENDUM-2-PILOT-002.yaml`, como **aditivo**:
o lock, os casos congelados, o freeze record e o addendum 1 não foram tocados.

Achou **cinco vazamentos novos**, dois deles corrigindo declarações positivas de
limpeza do addendum 1:

- **RES2-001** — `claw dangerously skip` em `29:02`. O addendum 1 declarava
  BC-005 *"segue como estava"*. Metade da resposta esperada de BC-005 é a flag de
  pular permissões, e ela está no corpo falado, fora do vão escondido.
- **RES2-003** — `compact` sem barra em `50:00`, o primeiro bloco depois do corte.
  Produziu `R-0087` no bundle compilado.

## Onde mais aplicar, e ainda não foi

- **as declarações `verified_clean` do PILOT-001** — mesma forma de artefato,
  mesma vulnerabilidade, nunca revarridas por radical;
- **o `COURSE-GAP-REPORT` dos três pilotos** — toda alegação de ausência que ele
  faz veio de busca literal;
- **as quatro salvaguardas de alegação de ausência** — `SAFEGUARD-FOUR-LABELS-ABSENCE-CLAIMS.md`
  regula como declarar ausência, mas não impõe o método de busca. Esta regra é a
  peça que faltava.

## O que a regra não cobre

Conceito ensinado **sem nenhum termo em comum** com o alvo — paráfrase total.
`RES2-004` só foi encontrado porque o radical `window` sobreviveu à paráfrase. Se
o instrutor tivesse dito *"quanto da memória já foi gasta"*, nenhum radical do
alvo casaria. **Busca por radical reduz o falso negativo; não o elimina.**
