# ARCHITECTURE FREEZE — ERRATA DE IDENTIDADE QUALIFICADA v1

**Classe:** `GIT_NATIVE_BY_DESIGN` · **Data:** 2026-08-30 · **Ator:** Alexandre Sandra
**Natureza:** **ADITIVA**. O Architecture Freeze original **não é reescrito**.

| artefato | sha256 |
|---|---|
| `COURSE-TO-SKILL-MULTI-SOURCE-ARCHITECTURE-FREEZE.md` (original, preservado) | `6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b` |
| `identity_audit_measure.py` (instrumento) | `e46da697e4a9c2326757cf52748ef5cdfd6dd1593b54b0f6408432082beb345e` |
| `out-identity-audit/identity-measurements.json` (medições) | `20ac4127add8b666f1f3068318651da1240456fff986c0e8403de22a00cfb184` |

> **Todo número desta errata foi lido de `identity-measurements.json`.** Nenhum foi
> digitado à mão. O instrumento é mecânico, offline e read-only; recomputá-lo reproduz
> os mesmos valores sobre os seis Source Packages selados da Round 3.

---

## 1. O QUE FOI MEDIDO

População: **1129** objetos endereçáveis com identificador
local, nos seis Source Packages selados da Round 3.

| package | `artifact` | `source_anchor` | `evidence` | `claim` | `rule_candidate` | `workflow_candidate` | `workflow_step` | `anti_pattern_candidate` | total |
|---|---|---|---|---|---|---|---|---|---|
| RUN-1/A | 2 | 44 | 44 | 38 | 13 | 6 | 19 | 4 | **170** |
| RUN-1/B | 2 | 56 | 56 | 43 | 19 | 4 | 23 | 3 | **206** |
| RUN-2/A | 2 | 44 | 44 | 41 | 13 | 6 | 19 | 4 | **173** |
| RUN-2/B | 2 | 56 | 56 | 42 | 19 | 4 | 23 | 3 | **205** |
| RUN-3/A | 2 | 44 | 44 | 42 | 13 | 6 | 19 | 4 | **174** |
| RUN-3/B | 2 | 56 | 56 | 38 | 19 | 4 | 23 | 3 | **201** |
| **total** | **12** | **300** | **300** | **244** | **96** | **30** | **126** | **21** | **1129** |

| chave | objetos | tuplas distintas | colisões | cross-kind | same-kind |
|---|---|---|---|---|---|
| `(source_package_hash, local_id)` — **forma congelada** | 1129 | 1108 | **21** | **21** | **0** |
| `(source_package_hash, entity_kind, local_id)` | 1129 | 1129 | **0** | 0 | 0 |

Veredito do instrumento: **`TYPED_QUALIFICATION_IS_UNIQUE`**.

As **21** colisões são **21/21 cross-kind** e
**0 same-kind**. Envolvem 7 `local_id` distintos, todos no par
`rule_candidate` × `anti_pattern_candidate`:

| package | `local_id` | kinds |
|---|---|---|
| RUN-1/A | `R-0095` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-1/A | `R-0098` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-1/A | `R-0101` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-1/A | `R-0102` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-1/B | `R-0109` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-1/B | `R-0112` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-1/B | `R-0124` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-2/A | `R-0095` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-2/A | `R-0098` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-2/A | `R-0101` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-2/A | `R-0102` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-2/B | `R-0109` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-2/B | `R-0112` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-2/B | `R-0124` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-3/A | `R-0095` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-3/A | `R-0098` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-3/A | `R-0101` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-3/A | `R-0102` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-3/B | `R-0109` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-3/B | `R-0112` | `anti_pattern_candidate` × `rule_candidate` |
| RUN-3/B | `R-0124` | `anti_pattern_candidate` × `rule_candidate` |

Sobreposição lexical **medida** entre conjuntos de `local_id` por kind — não deduzida de
prefixo. Único par não nulo em 8 kinds:

| par | interseção | tamanho dos conjuntos |
|---|---|---|
| `rule_candidate` × `anti_pattern_candidate` | **7** | 32 e 7 |

Os **7** ids de `anti_pattern_candidate` são **todos** emprestados de
`rule_candidate` — `round-3/run_round3.py` constrói o anti-pattern com o `local_id` da rule
de origem. Não é acidente estatístico; é construção.

### Consequências já observadas em execução real

1. A **execução 1 da Round 4** foi classificada `PILOT_MS_000B_ROUND_4_INVALID` porque um
   índice por `local_id` confundiu objetos distintos — registrado em
   `ROUND-4-EXEC-1-INVALID.md` (`c98082b5d7739475d8042f2b602fd45f645909d76f50044fbd3ab175056a8b01`).
2. Nos Fusion Packages da Round 4, **21** tuplas `(source_package_hash, local_id)`
   aparecem **simultaneamente** em `admitted_candidate_refs` e em
   `rejected_candidate_refs_NOT_CONSUMABLE`. Sob a forma congelada, *consumível* e
   *não consumível* deixam de ser conjuntos disjuntos.
3. Das **420** referências qualificadas persistidas na Round 4,
   **105 (25.0%)** são ambíguas se a tupla for lida sozinha.

---

## 2. CLÁUSULAS SUPERSEDIDAS — E SOMENTE ESTAS

Nenhuma outra decisão do freeze é tocada. `E1–E5`, `E7–E12`, os demais `I1–I30` e os
demais `D1–D37` permanecem exatamente como congelados.

### Forma ANTIGA — preservada aqui verbatim, e preservada no freeze original

```
linha 86: | **E6** | Identidade global por qualificação: `(source_package_hash, local_id)`. Nenhum artefato histórico é renumerado | `CONGELADA` |
linha 496: | **I4** | Todo identificador citado em qualquer produto é **qualificado** `(source_package_hash, local_id)` | zero `local_id` nu |
linha 515: | **I23** | Atribuição a fonte só no nível de **ELEMENTO**, por id qualificado | canário de atribuição falsa |
linha 534: | **D5** | Identidade qualificada `(source_package_hash, local_id)`, **sem renumerar histórico** |
```

**Insuficiência material, medida:** `(source_package_hash, local_id)` **não é injetiva**
sobre a população real — 1129 objetos colapsam em 1108 tuplas.
O texto declara *"identidade global"* e entrega uma chave que colide. Não é implementação
defeituosa: é a chave que é insuficiente.

### Forma NOVA — normativa a partir desta errata

```
GLOBAL_OBJECT_IDENTITY = (source_package_hash, entity_kind, local_id)
```

| componente | definição |
|---|---|
| `source_package_hash` | identifica o **conjunto selado** de uma compilação |
| `entity_kind` | **tipo canônico** do objeto **segundo o schema** — nunca nome de exibição arbitrário |
| `local_id` | o identificador local **existente**. **Nenhum histórico é renumerado** |

`entity_kind` canônicos para a população hoje medida:

- `artifact`
- `source_anchor`
- `evidence`
- `claim`
- `rule_candidate`
- `workflow_candidate`
- `workflow_step`
- `anti_pattern_candidate`

A lista é **extensível por schema futuro**. Todo kind usado em identidade tem de ser
**canônico, estável e inequívoco** — um kind novo entra por registro aditivo, nunca por
convenção implícita nem por prefixo lexical.

**A segunda cláusula de `E6` é preservada integralmente:** *"Nenhum artefato histórico é
renumerado"*. Esta errata acrescenta um componente à chave; não renumera nada.

---

## 3. UNICIDADE — CONGELADA

**Dentro de um Source Package:** `(entity_kind, local_id)` **DEVE** ser único.

**Entre produtos e packages:** `(source_package_hash, entity_kind, local_id)` **DEVE** ser único.

Um `local_id` **pode legitimamente repetir entre `entity_kind` diferentes.** Isso é
necessário, não tolerado: preserva

```
rule_candidate        R-0095
anti_pattern_candidate R-0095
```

como **objetos diferentes**, que é o que eles são.

---

## 4. REFERÊNCIAS `SELF` — EXCEÇÃO CONTROLADA

Os Source Packages da Round 3 **não são invalidados** por suas referências `SELF` não
carregarem `entity_kind`.

Uma referência interna pode usar

```json
{ "ref_scope": "SELF", "local_id": "..." }
```

**somente se** o campo — e portanto o schema que o contém — determina **inequivocamente** o
tipo do alvo. Nesses casos o kind é **`schema-implied`**:

| campo | `entity_kind` implicado |
|---|---|
| `claim.evidence_refs` | `evidence` |
| `evidence.anchor_ref` | `source_anchor` |
| `source_anchor.artifact_ref` | `artifact` |

Se o campo **puder apontar para mais de um kind**, `entity_kind` torna-se **obrigatório**.

Uma `SELF` ref genérica — `{ref_scope: SELF, local_id: X}` — cujo kind de destino **não** é
determinado pelo schema é **`INVALID_REF`**.

---

## 5. REFERÊNCIAS QUE CRUZAM FRONTEIRA

Toda referência que cruza a fronteira do Source Package **deve carregar explicitamente, na
própria referência**:

```json
{ "source_package_hash": "...", "entity_kind": "...", "local_id": "..." }
```

**É proibido depender de:** prefixo lexical · campo irmão opcional · conhecimento externo ·
heurística do consumidor.

> **A referência tem de resolver sozinha.** Uma ref que só resolve porque o registro que a
> contém carrega um `kind` ao lado não satisfaz esta cláusula.

Isto supersede a exigência de `I4` na sua **forma**, e a mantém no seu **propósito**: o
canário de `I4` deixa de ser *"zero `local_id` nu"* e passa a ser *"zero referência de
fronteira sem `entity_kind`"*.

---

## 6. `I23` — ATUALIZAÇÃO ADITIVA DE INTERPRETAÇÃO

`| **I23** | Atribuição a fonte só no nível de **ELEMENTO**, por id qualificado | canário de atribuição falsa |`

A **regra substantiva de proveniência não muda**: atribuição a fonte continua só no nível de
**elemento**, e o canário de atribuição falsa continua valendo. O que muda é o que "id
qualificado" significa: qualquer atribuição ou aresta de proveniência que referencie objeto
de Source Package usa a nova `GLOBAL_OBJECT_IDENTITY`.

---

## 7. O QUE ESTA ERRATA **NÃO** FAZ

- não reabre a arquitetura;
- não renumera `local_id` algum;
- não recompila, reabre ou resela Source Package algum;
- não altera os quatro produtos, o contrato de selo, o namespace `SELF` como mecanismo, a
  fronteira Fusion↔MTX, nem `I26`;
- não reescreve o Architecture Freeze original, que permanece byte-idêntico e selado;
- não altera os artefatos históricos das Rounds 1, 2, 3 e 4.

## 8. CLASSIFICAÇÃO

# `ARCHITECTURE_FROZEN_WITH_IDENTITY_ERRATA`

**Não** `ARCHITECTURE_REOPENED`.
