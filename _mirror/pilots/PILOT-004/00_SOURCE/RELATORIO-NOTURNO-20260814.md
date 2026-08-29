# RELATÓRIO NOTURNO — PILOT-004 · madrugada de 14/08/2026

Máquina: bot-04. Sessão autônoma, sem interação. Fila T1→T2→T3→T4.

## Placar

| tarefa | estado | chamadas |
|---|---|---|
| T1 — BLOCO 3 (evidência→Skill) | **FALHOU — bloqueio real** | 0 |
| T2 — baseline classe C em EN | **CONCLUÍDA** | 9 |
| T3 — BLOCO 4 preliminar | **NÃO EXECUTADA** (depende de T1) | 0 |
| T4 — este relatório | **CONCLUÍDA** | 0 |

**Custo real: 9 chamadas de API** de um teto de 60 (R1). Sobraram 51.

Nenhum retry em laço (R2 respeitado: 2 tentativas no T1 e parada). Drive esteve
disponível a noite toda, sem necessidade de acionar R3. A chave foi lida do
`~/.zshenv` só no instante de rodar, nunca impressa, copiada nem publicada (R5).

---

## T1 — FALHOU

O estágio evidência→Skill é do **compiler-s3**, cujo `ctss/classify.py` não
importa nesta máquina: depende de `scan_source_corruption.py` e
`detector_recall_fix.py`, ambos só na Lenovo, em `/home/mtx/course-to-skill-claude`.
Mesmo padrão do `cts/` no BLOCO 2b.

Dos 4 caminhos da pré-classificação, **P1, P2 e P4 estão indisponíveis** (o P4
precisa ainda de um terceiro insumo, `distance-lines-*.json`, que vem de `/tmp`
da Lenovo). Só o **P3 (ALIAS)** é local — justamente onde entrariam os alias
`Suitech` e `Metaed`.

Não reimplementei os detectores: seria trocar o instrumento de medição por um
que escrevi sem ter visto o original, contaminando em silêncio a comparação com
`TRANSCRIPTION_CORRECTION: 47` e `PARAPHRASE: 59` do P003. **R4 →
PENDENTE-ALEXANDRE.**

Detalhe completo, com as duas tentativas: `T1-BLOCO3-FALHOU.md`.

## T2 — CONCLUÍDA, e fecha a pendência do BLOCO 2b

Reprocessei o PILOT-001-v2 no bot-04 com o mesmo runner e o mesmo extractor
(`bd17ca41…`), insumos do Drive com hash conferido contra o manifesto dele
(L0 `068b4998…` CONFERE, tmap `845cea7d…` CONFERE). Tudo em `p001v2-remac/`;
**nada do P001-v2 histórico foi tocado**.

| | PT (P004) | EN (P001v2-remac) |
|---|---|---|
| drafts retornados / aceitos | 134 / 134 | 175 / 175 |
| **aceitos só após normalização** | **0** | **108** |
| rejeições | 0 | 0 |
| avisos (classe C) | 54 | 79 |
| **classe C por evidência** | **40,30%** | **45,14%** |

**Os 40% do português não eram degradação** — a taxa em inglês é ~5 pontos mais
alta. E a diferença que mais importa está noutra linha: **0 contra 108** em
dependência de normalização. Em PT, as 134 citações casaram literalmente de
primeira; em EN, 62% só passaram depois da normalização de formato.

Com isso a conclusão do objetivo secundário deixa de ser parcial: a travessia de
idioma sumiu (classe A = 0 contra 66% e 78% de travessia estrutural em P001-v2 e
P003-v2) **e nada tomou o lugar dela**.

Detalhe: `M4C-BASELINE-EN-vs-PT.md` e `M4C-BASELINE-EN-vs-PT.json`.

## T3 — NÃO EXECUTADA

Condição de entrada é "só se T1 produziu Skill válida". Não há Skill. Não gastei
chamada para produzir um resultado que não significaria nada.

Quando T1 destravar, o T3 roda como escrito: contexto mínimo autorizado, sem
fornecer dados do Business Suite, registrando verbatim o que a Skill pede, o que
recomenda, onde para por `METHOD_NOT_DEFINED`/`UNDEFINED` e se cai em conselho
genérico.

---

## PENDENTE-ALEXANDRE

**P-1 · Publicar os detectores da Lenovo.** `scan_source_corruption.py`,
`detector_recall_fix.py`, o gerador do `distance-lines-*.json` e um manifesto de
hash. Sem eles o BLOCO 3 não roda. Com eles, ~13 chamadas.

**P-2 · O compiler-s3 não tem freeze.** Ele é quem compila a Skill
(`compiler: compiler-s3/0.1.0` no manifesto do P003-v2), e não tem
FREEZE-RECORD nenhum — só dois resultados de canário sem registro que os ancore
a um conjunto de arquivos. Recomendo repetir para o s3 o que fizemos para o v2
(inventário + canário datado + freeze próprio) **antes** de compilar a Skill do
P004. Decisão sua.

**P-3 · Imprecisão na instrução do T1.** "Compilar com o compiler selado no
v0.2.1" — o v0.2.1 sela o **compiler-v2**, que faz PASS 1 e PASS 2, não
evidência→regra. Quem faz é o compiler-s3. Vale corrigir o texto do bloco.

**P-4 · M1/M2 contra o remac?** O reprocessamento rendeu 175 evidências contra
as 149 históricas, com o mesmo L0 e o mesmo temporal-map. Os M1/M2 do BLOCO 2b
usaram os números históricos e **não foram refeitos** — mudar o denominador
depois de ver o resultado seria trocar o critério com o jogo em andamento. Se
quiser recalculados, é decisão sua. Para referência, sem substituir nada: com o
remac a densidade do P001-v2 seria 0,19337 ev/s contra 0,14839 do P004 (razão
0,767, contra 0,901 do cálculo histórico).

**P-5 · A causa das 175 × 149.** Pode ser o extractor (o histórico rodou na
Lenovo, com código sem contraparte conferível — `R1_ABERTO_SEM_CONTRAPARTE`) ou
variação normal do modelo. Não dá para separar as duas com o que está publicado.

**P-6 · 13 segmentos fora da banda 7–11.** Continua aberto do bloco anterior:
segui porque a banda é faixa de comparabilidade com `variance_flag`, não piso de
portão. Se você a considera portão duro, o PASS 1 precisa ser refeito.

---

## Estado dos critérios do PILOT-004

| | estado |
|---|---|
| **C1** cobertura evidência→regra >80% | **não avaliável** — depende do BLOCO 3 (T1) |
| **C2** GAP-REPORT específico e verdadeiro | **não avaliável** — idem |
| **C3** aplicação ao Business Suite real da MTX | **não avaliável** — depende de T1, e a conferência é com você |
| **C4** modo de falha (conselho genérico) | **não avaliável** — idem |
| objetivo secundário (fonte em português) | **CONCLUÍDO e sustentado** |

O que a noite entregou foi o fechamento do objetivo secundário. Os quatro
critérios do piloto seguem todos travados atrás do mesmo bloqueio: o compilador
de Skill não roda nesta máquina.


---
---

# PARTE 2 — madrugada de 14/08, continuação

Retomada com as decisões do Alexandre/auditor registradas (P-2 sim, P-3
corrigido, P-4 não recalcular, P-5 e P-6 abertos como diagnóstico).

## Placar da parte 2

| tarefa | estado | chamadas |
|---|---|---|
| T5 — sync e instalação das dependências do s3 | **CONCLUÍDA** | 0 |
| T6 — congelar o compiler-s3 | **CONCLUÍDA** | 0 |
| T7 — BLOCO 3 (evidência→Skill) | **CONCLUÍDA** | 13 |
| T8 — BLOCO 4 preliminar | **CONCLUÍDA** | 2 |
| T9 — este relatório | **CONCLUÍDA** | 0 |

**Custo da noite inteira: 24 chamadas de 60.** Parte 1: 9. Parte 2: 15
(13 do T7, 2 do T8 — a primeira execução do T8 truncou em `max_tokens` antes das
seções que carregam C3b e C4, e foi refeita com teto maior; as duas contam).
Sobraram 36. O canário fail-closed do s3 gastou 0: quebrou antes da chamada.

## T5 — dependências instaladas, P4 continua indisponível

`lenovo-s3-deps/` chegou: **3/3 conferem** contra o `DEPS-HASHES`. Instalados em
`~/course-to-skill-claude/` e reconferidos depois da instalação.

O `ctss/classify.py` insere `/home/mtx/course-to-skill-claude` no `sys.path` —
caminho da Lenovo. Resolvido por `PYTHONPATH` no ambiente; **o arquivo não foi
editado**.

**P1, P2 e P3 disponíveis. P4 não.** Veio o `distance-lines-PILOT-003-v2.json`,
não o do P004 nem o gerador. Reusá-lo classificaria evidência do P004 pela
distância medida de outra evidência do P003 — os `evidence_id` colidem entre
pilotos. Rodou com `paraphrase_ids` vazio, limitação declarada no freeze e
visível no GAP-REPORT como `distância: (não medida)`.

## T6 — compiler-s3 congelado pela primeira vez

`FREEZE-RECORD-s3-v0.1.0.yaml`, publicado ao lado, nada sobrescrito.

```
inventory_set_sha256  115a3773dec3f171072b3769e3ca09d6c52cead0c8000f8455efbafeac4d927c
sha256 do freeze      b2f64851b3ae41deccf4229eeb5a5842172dfa988c30a6d89459c58cfb6fb1e8
14 arquivos selados
veredito              FREEZE-COM-CANARIO-PARCIAL
```

- **canário estático: APROVADO 15/15** no bot-04, com data. Não herdado.
- **canário fail-closed: NÃO EXECUTÁVEL.** `KeyError: 'name'` em
  `ctss/emit.py:54`. A fixture chama `render_router(workflows=[{'workflow_id':
  'WF-0001'}])` sem a chave `name`, que o `render_router` atual exige — o
  docstring dele registra a mudança. **A fixture não acompanhou o `emit.py`.**

Consequência: o `CANARY-FAILCLOSED-RESULT.json` guardado (`approved: true`)
**não é reproduzível** neste estado de código. Mesmo padrão do compiler-v2 no
BLOCO 1. Não consertei a fixture: seria alterar o compilador que o registro sela.

Por isso o veredito não é `FREEZE-SEM-CANARIO` (a suíte estática rodou inteira e
passou) nem freeze com canário completo (a única proteção fail-closed com chamada
real não é exercitada).

## T7 — BLOCO 3 · **C1 PASSA**

**Pré-classificação antes de qualquer regra:** SOURCE_EXPLICIT 119 ·
GENUINE_INFERENCE 9 · TRANSCRIPTION_CORRECTION 6.

**Vocabulário central conferido no ASR: 92,9% corrompido** (13 de 14 menções a
"Meta Business Suite"). Formas: `Metabusiness` ×4, `Metabus` ×3, `Suitch` ×2,
`Meta Business Suitech`, `Metabusness`, `suitch`, `MetaS`. Isso põe o P004 na
mesma faixa de **P002 (91,1%, Claude)** e **P003 (91,7%, ROAS)** — três pilotos,
dois idiomas, mesmo fenômeno. Os alias foram declarados em memória;
`classify.py` permanece byte-idêntico. O controle por token achou mais dois:
`insights` → "insightes"/"insites" e `reels` → "reals".

| | |
|---|---|
| regras / passos / workflows | 32 / 44 / 12 |
| **C1 cobertura evidência→regra** | **83,58%** (112/134) · limiar >80% · **PASSA** |
| evidências sem disposição | 0 |
| erros de validação / roteador | 0 / 0 |
| template fail-closed byte-a-byte | true |

**Controle positivo: 16/17 (94,1%), tem poder. Controle negativo: 12/12 ausentes
dos dois lados. INVENÇÕES: nenhuma. LACUNA NOSSA: nenhuma real** — o único token
marcado (`stories`) é artefato da forma que escolhi; a fonte diz "story" e a
Skill traz "story".

**Uma lacuna nossa que o controle por token não pegaria, e a própria Skill achou
depois:** o `runtime-policy.yaml` emitido referencia `knowledge/questions.yaml`,
`Q-0001` e `ADR-0004` — **nenhum dos três existe no pacote**. Dois guards mandam
fazer uma pergunta canônica cujo enunciado não está no runtime. **O PILOT-003-v2
tem o mesmo defeito.** É do compiler-s3, herdado da política canônica.

Limitação declarada: o T7 pedia checkpoint incremental; o `run_compile.py`
congelado grava o rastro só no fim e não tem retomada. Rodei o original sem
modificar — fidelidade ao compilador recém-congelado, com 36 chamadas de folga
para refazer inteiro se caísse. Não caiu.

## T8 — BLOCO 4 preliminar · **C4 não acionado**

A Skill **pede 15 itens específicos**, cada um com caminho na interface e id de
regra. O melhor sinal do C3b: reconheceu que peças de moto não cai em nenhuma das
três trilhas da fonte e **pediu a classificação em vez de escolher uma**.

Para em `MISSING_REQUIRED_INPUT` nomeando o campo faltante (`input`) e em
`METHOD_NOT_DEFINED` em quatro pontos específicos — trilhas de campanha, **como
conectar** o WhatsApp, criação de página/conta de anúncio, e pixel (fora de
escopo pela própria fonte). Registra `autonomy: UNDEFINED` em 100% dos passos e
regras, com a consequência dita: nada ali autoriza execução autônoma.

Não é conselho genérico: toda recomendação vem com passo, caminho e id; traz
proibições da fonte; traz uma decisão fechada e justificada (não contratar
ferramenta paga de agendamento, R-0015); e recusa onde a fonte não ensina.

## Estado dos quatro critérios

| | estado |
|---|---|
| **C1** cobertura evidência→regra >80% | **PASSA — 83,58%** |
| **C2** GAP-REPORT específico e verdadeiro | **material reunido** — 5 candidatos conferíveis por timestamp; avaliação é do Alexandre |
| **C3** aplicação ao Business Suite real | **metade b satisfeita**; metade a depende da conta real |
| **C4** modo de falha (conselho genérico) | **não acionado** em preliminar |
| objetivo secundário (fonte em português) | **CONCLUÍDO e sustentado** (parte 1) |

## PENDENTE-ALEXANDRE — atualizado

Fechadas na parte 2: **P-1** (dependências chegaram), **P-2** (s3 congelado),
**P-3** (corrigido no texto).

Abertas:

**P-4** M1/M2 contra o remac — mantido como decidido: números históricos ficam, o
remac entra como segunda linha declarada (razão **0,767**).
**P-5** causa das 175 × 149 — diagnóstico, sem ação.
**P-6** 13 segmentos fora da banda 7–11 — diagnóstico, sem ação.

**P-7 · NOVA · fixture do canário fail-closed do s3 desatualizada.** Consertar é
alterar o compilador recém-congelado. Enquanto não for, a proteção fail-closed
não é exercitada por teste e o resultado guardado não é reproduzível.

**P-8 · NOVA · `questions.yaml`, `Q-0001` e `ADR-0004` referenciados e ausentes**
no runtime emitido, no P004 **e** no P003-v2. Dois guards prescrevem uma pergunta
que o pacote não contém. Defeito do compiler-s3, não do piloto.

**P-9 · NOVA · gerador do `distance-lines`.** Sem ele o caminho P4 (PARAPHRASE)
fica indisponível para todo piloto novo. O arquivo do P003 não serve para o P004.

## Para amanhã

O que depende de você: avaliar o **C2** contra os 5 candidatos, e rodar a
**metade a do C3** — aplicar a Skill ao Business Suite real da MTX e conferir se
as configurações que ela recomenda batem com a conta. A Skill está em
`pilots/PILOT-004/skill/`, com `SKILL.md`, `knowledge/` e o GAP-REPORT.
