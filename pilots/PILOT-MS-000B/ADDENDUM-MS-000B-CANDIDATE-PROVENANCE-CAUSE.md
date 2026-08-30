# ADDENDUM AO `MS_000B_ACCEPTED` — causa medida de `CANDIDATE_DIRECT_PROVENANCE_NOT_YET_QUALIFIED`

**`addendum_id`:** `ADD-MS-000B-PROVENANCE-001` · **Data:** 2026-08-30
**Ator:** Design Review externa · **Classe:** `GIT_NATIVE_BY_DESIGN`
**Natureza:** **ADITIVO**. O Decision Record histórico **não é modificado**.

| artefato | sha256 |
|---|---|
| `DECISION-RECORD-MS-000B-FINAL-ACCEPTANCE.md` (histórico, **preservado**) | `5e689af702a2c043adfa6be63e864465dc3d579dff2f2066787456c3fb13d4d8` |
| `PILOT-MS-001/MS-001-PRE-IMPLEMENTATION-DESIGN-REPORT.md` (base empírica) | `f82c6df14e4544bdb4df270499ee3a9ebd59fc2090b0421f1db866a089870ea7` |
| `round-3/run_round3.py` (o empacotador) | `5f8372ed101136e821d99d88773dbb829376593542878e8bb8fafee4809babc8` |

---

## 1. O QUE **NÃO** MUDA

> **`CANDIDATE_DIRECT_PROVENANCE_NOT_YET_QUALIFIED` permanece verdadeiro como resultado do
> MS-000B.**

A limitação **não é apagada**, porque continua descrevendo corretamente **o que o MS-000B
não provou**: a cadeia direta

```
SOURCE_LOCAL_CANDIDATE → claim/evidence → SOURCE_ANCHOR → ARTIFACT/L0
```

não foi demonstrada em corpus real dentro daquele piloto. Nos seis Source Packages selados,
**147 de 147 candidates** têm `evidence_refs` vazio e `claim_refs` ausente. Isso é fato e
permanece registrado.

## 2. O QUE ESTE ADDENDUM ESCLARECE — A CAUSA

A causa, medida **depois** do encerramento do MS-000B, é:

# `MS_000B_ROUND_3_PACKAGER_PROVENANCE_LOSS`

E **não**:

# ~~`HISTORICAL_CORPUS_LACKED_CANDIDATE_PROVENANCE`~~

## 3. EVIDÊNCIA — recomputada no ato deste registro

### 3.1 O corpus histórico **possuía** o lastro

Objetos candidatos históricos (rules + workflows + steps de `PILOT-002-v2`,
`PILOT-003-v2` e `PILOT-004`):

| medida | valor |
|---|---|
| objetos candidatos | **2.019** |
| com `evidence_ids` não vazio | **2.016** (99,85%) |
| refs que **resolvem** em `EVIDENCE` | **2.016/2.016 (100,00%)** |
| com `SOURCE_ANCHOR` completo | **2.016/2.016 (100,00%)** |
| `quote` localizada no L0 por `sha256` | **1.927/2.016 (95,59%)** |

Os candidates carregam `evidence_ids` **e** `segment_ids`. E
`EVIDENCE.source_excerpt` **é** o `SOURCE_ANCHOR`:
`{source_file, source_sha256, span{start_s,end_s}, quote}`. A cadeia inteira existia.

A taxa de 95,59% de localização no L0 é consistente com o baseline `REPRODUCED_FROM`
já congelado — 2921/3045 = 95,93% — aqui sob casamento mais estrito.

### 3.2 O empacotador da Round 3 **descartou** o lastro

`round-3/run_round3.py` reconstrói cada candidate a partir do YAML e grava a lista literal
vazia, em quatro lugares:

```
linha 85: W.append({"local_id":w["workflow_id"],"name":w["name"],"evidence_refs":[],
linha 90:                     "evidence_refs":[]} for i,x in enumerate(ss)]})
linha 93:     "precedence":r.get("precedence"),"evidence_refs":[]}
linha 95: A=[{"local_id":r["local_id"],"do_not":r["do_not"],"evidence_refs":[]} for r in R if r["do_not"]]
```

O campo `evidence_ids` do objeto de origem **nunca é lido**. Resultado nos pacotes selados:
**147 de 147 candidates com `evidence_refs` vazio (100,00%)**.

## 4. A DISTINÇÃO QUE FICA REGISTRADA

# `PILOT_LIMITATION != CORPUS_LIMITATION`

O MS-000B não provou a cadeia porque **o instrumento a destruiu antes da medição**, não
porque o material não a tivesse. Registrar a limitação sem registrar a causa deixaria o
acervo sugerindo insuficiência do corpus — e a medição diz o contrário.

Isto é da mesma família dos achados `D-1` a `D-8` e das duas execuções `INVALID`: **defeito
de instrumento e de método, não de produto nem de material.**

## 5. O QUE ISTO **NÃO** AUTORIZA

- **não** reabre o MS-000B;
- **não** reclassifica rodada alguma;
- **não** altera os seis Source Packages, os Fusion Packages ou qualquer veredito;
- **não** corrige `run_round3.py` — o artefato histórico permanece como está, com o defeito
  registrado e não emendado;
- **não** promove nada a produção.

## 6. O PORTÃO CONTINUA VALENDO NO MS-001

# `CANDIDATE_PROVENANCE_GATE_REQUIRED_IN_MS_001`

Mesmo com a causa esclarecida, o portão **permanece obrigatório**. O MS-001 tem de **provar
a cadeia no novo Source Package contract**, não inferi-la do corpus legado: o que está
medido é que o **material** sustenta a cadeia, não que um empacotador novo a preserve.

No MS-001, candidate sem lastro suficiente:

```
NOT_ELIGIBLE_FOR_CROSS_SOURCE_DECISION
```

E a regra dura do contrato permanece: **conjunto vazio não passa por vacuidade** — é
`NOT_ELIGIBLE`, nunca `ELIGIBLE`.
