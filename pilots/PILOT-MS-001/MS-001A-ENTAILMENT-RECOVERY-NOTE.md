# NOTA DE RECUPERAÇÃO — instrumento de entailment, Execução 2

**Data:** 2026-08-30 · **Natureza:** ADITIVA. A Execução 1 permanece preservada e **não é retomada**.

## 1. A causa medida do  da Execução 1

Registrada em `MS-001A-EXEC-1-INSTRUMENT-INVALID.md`
(`e4cd6118ceeceeed785f5e1b11874a6031a46f3135c91b678f1dc58d016529e9`). Dois defeitos, ambos de instrumento:

1. **prompt e schema discordavam** — o prompt mandava `{temporary_claim_id, state, why}`,
   o schema exigia `{claim_id, judgment, entail_why, evidence_refs_checked}`. O modelo
   emitiu o que o **prompt** pediu;
2. **o fixture `JE4` testava a fronteira errada** — usava Evidence pertinente mas
   **silenciosa** sobre o atributo, esperando `INDETERMINATE`.

## 2. Sobre o segundo defeito — o juiz estava certo

Sob a semântica agora congelada, evidence **do mesmo objeto porém silenciosa sobre o
atributo afirmado** é **`NOT_ENTAILED`** (caso D), não `INDETERMINATE`. O veredito
`NOT_ENTAILED` que a Execução 1 recebeu para `CL-9004` era **correto**. O fixture é que
estava errado.

Na v2 esse caso vira **`JE5`**, com o rótulo certo, e **`JE4`** passa a testar a única
situação genuinamente `INDETERMINATE`: **a fonte declarando a questão em aberto**.

## 3. O que muda — e só isto

| artefato | estado |
|---|---|
| `ENTAILMENT-PROMPT-v2.txt` | **NOVO**, `762fdd82c09e5fa02e80d8278774fbe31b4e42a72acf752901a7fba6ba6e0ff5` |
| `JUDGE-CONTROLS-JE-v2.txt` | **NOVO**, `9d5e368981ad87100036e721eda5cee8ce30b0f1aba094c7f3921337ea991b84` |
| `lib/entail_validate.py` | **NOVO**, `74e317e94deedc2cc3e338e8a8877afae94b6775f0891cc3afe97aac1457f7ea` — módulo separado |
| `ENTAILMENT-SCHEMA-v2.json` | **INALTERADO**, `b31d70083f300b1e8e05b13849720eb42d7f993bd539ab029db305f5fdaf4c07` |

**O schema não muda** porque o defeito medido estava no prompt. O prompt v2 agora exige
**exatamente** a representação que o schema já aceitava, incluindo `evidence_refs_checked`,
que o prompt v1 nunca pediu.

O validador novo vive em **módulo separado** para que `lib/validate.py` permaneça
**byte-idêntico** ao declarado no Opening Record da Execução 1
(`0faed47838971cc70d23ac307e39559abef3d0cc97d08ae4964c2a0f87fe4a32`) — a correção é focalizada, e isso é verificável.

## 4. Endurecimento de `evidence_refs_checked`

v1 exigia **subconjunto**. v2 exige **igualdade exata** com o conjunto enviado, com códigos
distintos: `E19_JUDGE_ADDED_EVIDENCE` · `E27_JUDGE_OMITTED_EVIDENCE` ·
`E26_FOREIGN_EVIDENCE`. Mais completude: `E20` omissão · `E24` duplicação ·
`E21` desconhecida · `E04b` campo extra · `E25` enum · `E23` formato antigo da v1.

## 5. Semântica congelada das três classes

**`ENTAILED`** — a Evidence sustenta a Claim inteira: conteúdo, qualificadores, condições e
escopo, sem acréscimo material.

**`NOT_ENTAILED`** — quatro casos: **(A)** contradição positiva · **(B)** generalização ou
acréscimo não sustentado · **(C)** assunto/objeto diferente · **(D)** **silêncio** sobre
atributo factual afirmado, sem expressar incerteza.

**`INDETERMINATE`** — somente quando a Evidence deixa a proposição **explicitamente**
ambígua, incerta, dependente de alternativa não resolvida ou inconclusiva.
**`INDETERMINATE` não é "não achei"; é "a fonte declara a questão em aberto".**

**`SILÊNCIO ≠ INDETERMINATE`** — e `JE5` existe para provar isso mecanicamente.

## 6. Byte-idênticos, não tocados

corpus B/C · slices · `builders.py` (anchors, Evidence N=4) · `EXTRACTION-PROMPT-v1` ·
`EXTRACTION-SCHEMA-v1` · controles `EC1`–`EC6` · `identity.py` · `gate.py` ·
`package.py` · `validate.py` · verificador de selo do MS-000A.

## 7. Contabilidade de chamadas

```
EXEC_1  calls = 2   status = INVALID   (preservada, não retomada)
EXEC_2  PLANNED = 10  HARD_CAP = 10  RETRY = 0
```

O cap de 10 é **por execução selada**. Se a Execução 2 completar,
`CUMULATIVE_MS001A_MODEL_CALLS = 12` — **isso não é violação**, e fica registrado para que
um auditor futuro não some 2+10 e declare estouro falso.
