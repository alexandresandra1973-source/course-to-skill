# ERRATA — SEMÂNTICA DOS CONTROLES DE BLOCKER BC1–BC5

Documento **aditivo**. Não altera nenhum artefato selado. Data: 2026-08-31.
Emitido em resposta ao achado DEF-2 da EXEC-3
(`MS-001B-EXEC-3-HARD-STOP-INSTRUMENT-DEFECT.md`).

---

## 1. Redação histórica

Em `blocker/control-mappings-v03.json` e nos relatórios de calibração, os cinco
conjuntos de controle receberam nomes que sugerem uma relação semântica esperada:

    BC1_genuine_overlap
    BC2_scope_difference
    BC3_specialization
    BC4_false_conflict
    BC5_unrelated

Essa redação induziu a leitura de que cada par pertencente a um bucket teria a relação
indicada pelo nome do bucket — isto é, que os 45 pares de BC1 seriam todos
semanticamente sobrepostos.

## 2. Correção

Os cinco conjuntos são construídos como **produtos cartesianos** de dois conjuntos de
Claims, um de cada Source Package:

| bucket | claims B | claims C | pares | \|B\|×\|C\| |
|---|---|---|---|---|
| BC1_genuine_overlap | 9 | 5 | 45 | 45 |
| BC2_scope_difference | 3 | 8 | 24 | 24 |
| BC3_specialization | 13 | 6 | 78 | 78 |
| BC4_false_conflict | 3 | 7 | 21 | 21 |
| BC5_unrelated | 6 | 6 | 36 | 36 |

O nome descreve o **scenario bucket de origem** dos Claims — o cenário a partir do qual
os Claims dos dois lados foram agrupados — e **não** um rótulo de relação esperado para
cada célula do produto.

Formalmente:

    BC_BUCKET_MEMBERSHIP  !=  EXPECTED_SEMANTIC_RELATION

Um produto cartesiano de Claims pertencentes ao mesmo scenario bucket não implica que
cada par tenha a relação sugerida pelo nome histórico do bucket.

E, consequentemente:

    BLOCKER RETAINS A PAIR   não implica   SEMANTIC RELATION EXISTS

## 3. Reclassificação dos dois tipos de controle

    BLOCKER_CONTROL   = BC1-BC5
                      = retention / coverage probe
                      mede se o blocker retém os pares que deveria alcançar;
                      NÃO carrega expected relation por par;
                      NÃO produz veredito PASS/FAIL de correção semântica.

    SEMANTIC_CONTROL  = J1-J10
                      = synthetic discriminant fixtures, pares curados
                      ÚNICO controle com expected semantic output por par;
                      gate discriminante de cada run: exige 10/10 PASS.

## 4. O que esta errata NÃO faz

Não cria pares BC curados depois de observar judgments. Não remapeia Claims. Não
recalibra o blocker. Não cria blocker v0.4. Não altera a variante V1. Não altera os 97
pares nem o `PAIRSET_HASH`. Não altera taxonomia, definições semânticas, semântica de
scope, o SYSTEM do prompt semântico, J1–J10, família de modelo, transporte, política de
estabilidade ou semântica de Fusion.

É uma correção **declarativa**: corrige o que os controles significam, não o que eles
contêm.

## 5. Qualificação mecânica do blocker — preservada

`blocker v0.3` permanece **`BLOCKER_FEATURE_MODEL_QUALIFIED`**. Essa qualificação nunca
dependeu de relação semântica; ela é sustentada por propriedades mecânicas, todas
intactas e reverificáveis sem modelo:

* três canais de feature;
* zero `FEATURE_CHANNEL_LEAK`;
* conceitos congelados;
* named objects congelados;
* separação de content-token;
* geração determinística de pares;
* provenance;
* identidade tipada.

O que deixa de ser alegado: que BC1–BC5 provam relações semânticas. Nunca provaram.

## 6. Variante V1 — preservada

`SELECTED_VARIANT = V1` permanece congelada. A seleção foi feita **antes** de qualquer
semantic judgment, por decisão externa de recall. Não se repete a seleção e não se
compara V1 × V2 usando judgments — isso seria seleção de variante posterior ao
resultado. A preservação é deliberadamente conservadora.

## 7. Auditoria BC daqui em diante

BC1–BC5 saem do veredito de correção semântica. Após as runs, reporta-se apenas, de
forma descritiva:

    bucket  ->  número de pares retidos  ->  distribuição de relations

Sem expected relation por par. Sem PASS/FAIL. Sem usar o resultado para alterar o
blocker, a variante ou a taxonomia.

O gate discriminante continua sendo, exclusivamente, J1–J10.
