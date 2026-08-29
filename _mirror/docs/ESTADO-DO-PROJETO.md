# ESTADO DO PROJETO — 2026-08-12

*Para o Alexandre, sem lembrar de metade. Três páginas. Gerado por script.*

## O que o projeto é, em uma frase

**Um avaliador de curso.** Transforma um curso em Skill executável, roda a Skill, e descobre se o método do curso entrega o que promete. A regra que sustenta tudo: se a Skill preencher lacunas com conhecimento do modelo, ela avalia o **modelo**, não o curso.

---

## 1. O QUE EXISTE E ESTÁ MEDIDO

### compiler-v2 — extração de evidência. **Funciona.**

| | PILOT-001 | PILOT-002 |
|---|---|---|
| evidências | 149 | **448** (era 44) |
| cobertura de L0 | 90,61% | **82.39%** |
| portão | SATISFIED, 0 revarreduras | SATISFIED, 0 revarreduras |
| rejeições | — | 0 |

O colapso de 44 evidências foi diagnosticado como **seleção, não truncamento**, e consertado por duas decisões: PASS 2 roda **um segmento por chamada**, e há um portão de cobertura com revarredura dirigida. Congelado, canário 6/6.

### O teto por chamada — **medido causalmente**

Dividir um segmento em três rende **1,500×** mais evidência. Zero fusões na dedup, então não é duplicação de fronteira. O conserto que isso nomeia — subdividir segmentos longos no PASS 1 — está **identificado e não aplicado**.

### TEST-0008 — instrumento pronto, rubrica em auditoria

- **metric lock**: 5 métricas canônicas, lidas do RELEASE por hash; o "6" resolvido como união 0007∪0008
- **scorer-v2**: duas comparações (P e F) na mesma execução, derivado do F7 por patch, **zero regressão** no TEST-0007 (canônico idêntico, margem 44,0)
- **rubrica**: 8 critérios ancorados em L0, pesos somando 1,0 exato, quatro faixas de comportamento

### compiler-s3 — evidência→Skill. **Arnês e canário prontos, não rodado.**

- canário estático: **15/15**
- canário de recusa fail-closed **com chamada real**: **APROVADO** — a recusa saiu byte a byte igual ao template canônico, e o controle com os recursos presentes executou citando evidence_id

---

## 2. O QUE ESTÁ ABERTO

| frente | estado | quem decide |
|---|---|---|
| compilar as 448 em Skill | arnês pronto, **41 chamadas não gastas** | Alexandre |
| rubrica do TEST-0008 | **vaza por paráfrase**, 3 rodadas de conserto | revisor |
| pisos da rubrica | baixados para 70 nos não-portão | feito |
| subdividir segmentos no PASS 1 | conserto nomeado, não aplicado | Alexandre |
| bandas de enquadramento (F) | variância do avaliador **não medida** | bloqueador 3 da ADR |

### O bloqueio da rubrica, em uma linha

Três rodadas de teste de vazamento mostraram um padrão: **toda instrução que a régua dá para neutralizar um confundidor descreve o confundidor.** Fechei três canais e cada conserto abriu o seguinte. O que resta são opções de desenho, não de redação.

---

## 3. O QUE FOI ABANDONADO, E POR QUÊ

| abandonado | por quê |
|---|---|
| medidor de densidade por regex | REPROVADO no canário: sem poder de detecção |
| aviso claim×literal | disparava 40%, zero verdadeiro positivo além do rótulo do modelo |
| TTR como proxy de densidade | correlação +0,003 |
| explicar a razão 1,515 pelo teto | nenhum expoente a explica: o mecanismo satura em 1,13 |
| variante gate-only da rubrica | converte diferença mensurável em reprovação binária |
| comparabilidade de esquema com PILOT-001 | servia à pergunta de densidade, fora do caminho crítico |

**Padrão que se repetiu quatro vezes:** proxy mecânico para propriedade semântica falha neste projeto. Está registrado; não tentar um quinto.

---

## 4. PENDÊNCIAS COM DONO

| # | pendência | dono |
|---|---|---|
| 1 | rodar as 41 chamadas da compilação evidência→Skill | **Alexandre** |
| 2 | rubrica do TEST-0008 vaza: mudar desenho ou aceitar | **revisor** |
| 3 | subdividir segmentos longos no PASS 1 (pós-pilotos, §12) | **Alexandre** |
| 4 | medir variância do avaliador do TEST-0008 | **Alexandre** |
| 5 | estabilidade do PASS 1 nunca medida | **não agendada** |
| 6 | 10 casos cegos do PILOT-002 intactos, esperando Skill | **bloqueado por 1** |

---

*Gerado por script. Nenhum número digitado à mão.*
