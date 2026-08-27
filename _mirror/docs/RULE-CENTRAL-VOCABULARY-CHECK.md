# REGRA DO PRODUTO — conferir o vocabulário central do domínio antes dos rótulos epistêmicos

**Status:** REGRA_ATIVA · registrada 2026-08-12 · vale para todo pipeline curso→Skill

## As duas ocorrências

| piloto | domínio | termo central | forma correta no L0 | corrompido |
|---|---|---|---|---|
| PILOT-002 | Claude Code | **Claude** | 13 de 146 | **91,1%** |
| PILOT-003 | Google Ads e-commerce | **ROAS** | 0 de 12 (`rows`, `roads`) | **91,7%** |

Dois domínios sem relação, dois cursos, dois instrutores, duas transcrições
automáticas — e o mesmo termo quebrado: o **mais central**.

## Por que é estrutural, e não azar

O termo central de um domínio é, quase por definição, o **mais raro e técnico**
do vocabulário do texto. É jargão, sigla ou nome de produto. É exatamente a
classe que o ASR erra, porque o modelo de linguagem por trás dele prefere a
palavra comum: `Claude` vira `claw`, `ROAS` vira `rows`.

O resto do vocabulário sai bem. No PILOT-003, `keyword`, `bidding`,
`Merchant Center` e `negative keyword` saem 100% corretos; `Google Ads` 97,6%;
`conversion` 99,7%. **A corrupção se concentra no termo que mais importa.**

## O dano se ninguém confere

O extrator marca `MODEL_INFERENCE` quando a claim não reproduz a citação. Se a
citação diz `rows` e a claim diz `ROAS`, o rótulo é tecnicamente correto e a
leitura é falsa: **a fonte ensinou, o ASR estragou, e o avaliador registra como
contribuição do modelo.**

Sem a conferência, o produto penaliza o curso por erro da transcrição. É o
oposto do que ele existe para medir.

## A regra

**Todo pipeline curso→Skill confere o vocabulário central do domínio ANTES de
confiar nos rótulos epistêmicos.**

Procedimento, e as duas primeiras etapas são mecânicas:

1. levantar os termos técnicos mais frequentes das evidências e do L0;
2. para cada um, contar as formas variantes plausíveis e medir a proporção da
   forma correta;
3. onde a forma correta for minoria, registrar **alias declarado por medição** —
   nunca por limiar de similaridade. `claude`~`claw` dá 0,60 e `roas`~`rows` dá
   0,50: os dois cairiam junto com lixo se a regra fosse similaridade.

O alias entra no caminho 3 do classificador, com a medição que o sustenta escrita
ao lado dele no código.

## O que a regra não cobre

Termo central que o ASR corrompe de forma INCONSISTENTE — ora certo, ora errado,
ora de duas maneiras diferentes — ainda escapa parcialmente. Os dois casos vistos
foram consistentes. Não afirmo que todos serão.
