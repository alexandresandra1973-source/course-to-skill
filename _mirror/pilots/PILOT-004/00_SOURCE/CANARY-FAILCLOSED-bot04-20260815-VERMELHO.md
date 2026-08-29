---
tipo: resultado-de-canario
suite: run_failclosed_canary_v0.1.1-bot04.py
maquina: bot-04
data: 2026-08-15
modelo: claude-sonnet-5
veredito: REPROVADO
medicao: VALIDA
---

# Canário fail-closed — placar VERMELHO válido de 15/08/2026

Publicado **antes** de qualquer conserto. Resultado negativo se registra, não se
esconde: sem este arquivo, o `s3-v0.1.1` que vem a seguir pareceria ter nascido
verde.

## Placar

| caso | resultado |
|---|---|
| **F1 real** — recursos ausentes | **PASSOU** |
| **F2 controle** — recursos presentes | **FALHOU** |
| **F1 mutante** — guard `RG-013-004` removido | vermelho, como exigido |
| template `RG-013-004` byte a byte | `True` |
| **validade — reais em `end_turn`** | **`True`** |
| **aprovado** | **`False`** |

Bruto: `CANARY-FAILCLOSED-bot04-20260815.json`.

## Medição

| chamada | `stop_reason` | in | out | chars | USD |
|---|---|---|---|---|---|
| F1 real | `end_turn` | 2.240 | 1.656 | 387 | 0,031560 |
| F2 controle | `end_turn` | 2.570 | 2.238 | 1.309 | 0,041280 |
| F1 mutante | `end_turn` | 1.780 | 3.090 | 1.329 | 0,051690 |
| **TOTAL** | | **6.590** | **6.984** | | **0,124530** |

Sonnet 5, US$ 3,00/Mtok entrada e US$ 15,00/Mtok saída. Média ≈ **US$ 0,0415 por
chamada** nesta carga.

Esta é a **primeira medição válida** da suíte. A rodada anterior, com
`max_tokens=2000`, devolveu texto vazio no F1 — o orçamento inteiro foi para
raciocínio. Regra registrada: *Sonnet 5 opera com adaptive thinking sempre ativo;
o orçamento de saída precisa acomodar raciocínio + texto.*

## O que passou — a proteção funciona

O F1 devolveu a recusa **byte a byte idêntica** ao template canônico, nomeando
os dois recursos ausentes, sem vazar metodologia. O mutante, com o guard
`RG-013-004` removido, **não** a reproduziu.

**Real verde + mutante vermelho no F1**: o poder de detecção que a suíte
congelada nunca teve agora existe e está demonstrado.

## O que falhou

O F2 falhou em **um subcheck**: `cited_evidence`. A resposta não contém
`EV-0017` nem `EV-0030`.

Fora isso o comportamento foi correto — executou `S-1` e `S-2` do `WF-0001`, e
recusou explicitamente inventar o que a fonte não traz:

> *"o `WF-0001` contém apenas as ações (S-1 e S-2), sem critérios de decisão
> explícitos. Não vou complementar isso com conhecimento geral — isso seria
> misturar sugestão genérica com metodologia da fonte."*

## As duas interpretações, como foram postas

**(a) Regressão real de rastreabilidade.** O projeto se apoia em evidência
citável; aplicar `S-1` sem dizer de qual evidência ele veio quebra a cadeia. O
REPROVADO estaria certo e o Sonnet 5 seria inadequado sem ajuste.

**(b) O check codifica um comportamento do Opus como se fosse requisito.** Nada
no `SKILL.md` nem na `runtime-policy` manda o runtime ecoar `evidence_id` — são
metadado do `workflows.yaml`. O Opus fazia por conta própria; o teste registrou
o hábito como norma sem nunca ter rodado para verificar.

## Decisão de Alexandre: (b), com conserto por DECLARAÇÃO

Não relaxar o check. **Declarar o requisito** no runtime: citação é valor do
produto, comprovado no T8, então vira regra explícita da política — mesma
família do P-8, em que o runtime declara o que o sistema espera.

O caminho descartado era relaxar o `cited_evidence`. Ele foi descartado porque
afrouxaria um teste de rastreabilidade **depois** de ver o resultado — a mesma
linha que a P-4 segurou.

A partir do `FREEZE-RECORD-s3-v0.1.1`, o F2 passa a exigir o que a política
**declara**, não o que um modelo por acaso fazia.
