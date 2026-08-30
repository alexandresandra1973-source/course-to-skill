# PILOT-MS-000B / ROUND 2 — VEREDITO

**Classificação:** **`PILOT_MS_000B_PASS`** · **15/15 portões válidos**
**Data:** 2026-08-30 · **Opening Record:** `5789a6d42773350fe9e41ddc74370027bfa34b9058ab8168bf425ac53a56f1e8`
**Round 1:** `INVALID_INSTRUMENT`, preservada byte-a-byte e **não reutilizada**.

---

## 1. OS QUATRO DEFEITOS DA ROUND 1, CORRIGIDOS POR PROPRIEDADE TESTADA

| # | defeito | correção | prova |
|---|---|---|---|
| 1 | tokenizer colava pontuação | pontuação **periférica** removida, interior preservado | 4 equivalências positivas + **5 negativas** que não podem colapsar |
| 2 | isolamento por estatística de vocabulário | substituído por **controles de proveniência/asserção** | `JC-CROSS-A-IN-B` e `JC-CROSS-B-IN-A` ambos `NOT_ENTAILED` |
| 3 | juiz sem controle negativo | **5 controles bloqueantes antes** de qualquer claim gerada | 5/5, com os três estados exercitados |
| 4 | consolidador sem ramo `INVALID` | classificador de três classes com **precedência de `INVALID` sobre `FAIL`** | 7/7 fixtures, incluindo `FX-PRECED` |

## 2. O JUIZ DEMONSTROU PODER DISCRIMINANTE — o ponto que faltava

| controle | esperado | obtido | justificativa do juiz |
|---|---|---|---|
| `JC-POSITIVE` | `ENTAILED` | **`ENTAILED`** | *"A claim apenas reafirma isso, sem adicionar fato novo."* |
| `JC-NEGATIVE` | `NOT_ENTAILED` | **`NOT_ENTAILED`** | *"A primeira parte segue da evidência, mas a evidência nada diz sobre o GitHub cobrar taxa… é fato e causalidade novos."* |
| `JC-INDETERMINATE` | `INDETERMINATE` | **`INDETERMINATE`** | *"…tocando o assunto, mas não informa nada sobre preferência da maioria; insuficiente para confirmar ou negar."* |
| `JC-CROSS-A-IN-B` | `NOT_ENTAILED` | **`NOT_ENTAILED`** | *"A evidência trata de MCP…; não menciona inspeção de mudanças nem seções verde/vermelha."* |
| `JC-CROSS-B-IN-A` | `NOT_ENTAILED` | **`NOT_ENTAILED`** | *"A evidência trata de controle de versão…; não menciona MCP nem analogia com porta USB."* |

Em `JC-NEGATIVE` o juiz **separou a parte implicada da acrescentada** em vez de aprovar o
conjunto — é discriminação real, não rótulo.

## 3. SOBRE O 100% `ENTAILED` NAS CLAIMS REAIS

**257/257 `ENTAILED`, zero `NOT_ENTAILED`, zero `INDETERMINATE`, zero rejeições.**

Na Round 1 esse mesmo resultado foi motivo de ressalva. **Aqui não é**, e a diferença é
exatamente a que o Opening Record §9 declarou antes da execução:

> *"100% `ENTAILED` nas claims reais **pode ser válido** — desde que os controles negativo e
> indeterminate tenham sido corretamente rejeitados. Não se reprova um resultado por ser
> 100%; reprova-se instrumento incapaz de discriminar."*

O instrumento **provou que discrimina** e ainda assim aprovou todas as claims reais. A
leitura que sobra é a do gerador: ele foi instruído a não acrescentar nada e obedeceu,
produzindo reformulações conservadoras genuinamente implicadas.

**Limitação declarada, não escondida:** esta rodada não estabelece a taxa de entailment de
um gerador *não* restringido. Mede este gerador, com este prompt.

## 4. RESULTADOS

### Identidade
100 `local_id` · **44 colisões nuas deliberadas** (`EV-0001`… em ambos) · **100 identidades
qualificadas distintas** · **0** referências cross-package nuas · **0** claims no pacote
errado · hashes distintos `115ae350…` e `737fc71a…`.

### Proveniência
**257/257 = 100%** resolvem `claim → evidence → anchor → slice → CUT → FULL`. Zero quebradas.

### Claims
| run | raw | rejeitadas | seladas | `ENTAILED` | `NOT_ENTAILED` | `INDETERMINATE` |
|---|---|---|---|---|---|---|
| RUN-1 | 84 | 0 | 84 | 84 | 0 | 0 |
| RUN-2 | 87 | 0 | 87 | 87 | 0 | 0 |
| RUN-3 | 86 | 0 | 86 | 86 | 0 | 0 |

### Variância — KILL-2
84 / 87 / 86 · **máx/mín = 1,0357× ≤ 1,5×**.
Sobreposição textual normalizada entre runs: **5 · 3 · 15** · **núcleo comum aos três: 0**.

> **Achado registrado, não um portão:** a população é estável (1,04×) mas a **redação** quase
> nunca coincide. Zero claims idênticas nos três runs. A estabilidade é de *quantidade*, não
> de *forma* — e isso é informação para o `MS-001`, onde a taxonomia de relações vai
> depender de comparar claims entre fontes.

### Preservação de workflow — DESIGN C
| pacote | workflows | steps | struct source == struct fusion |
|---|---|---|---|
| A | 6 | 19 | **idêntico nos 3 runs** |
| B | 4 | 23 | **idêntico nos 3 runs** |

Nenhuma reconstrução silenciosa. A fusão **transportou**.

### Blocagem
Regra declarada antes: `shared_content_tokens >= 2`.

| run | pares possíveis | sobreviventes | redução | controles positivos |
|---|---|---|---|---|
| RUN-1 | 1.763 | 193 | **89,05%** | 2/2 |
| RUN-2 | 1.892 | 162 | **91,44%** | 2/2 |
| RUN-3 | 1.848 | 148 | **91,99%** | 2/2 |

`BLK-CTRL-01` sobreviveu por `['github','repository']` e `BLK-CTRL-02` por
`['remote','repository']` — os mesmos controles que a Round 1 eliminou por defeito de
tokenização. **Nenhum threshold de redução foi definido**; os ~90% são medição, não meta.

### Isolamento
Controles `A→B` e `B→A` corretos · **0** trocas falsas de proveniência · **0** ids nus ·
**0** claims atribuídas ao pacote errado. **Contagem de palavras comuns não foi usada.**

### Relações
`IDENTICAL` mecânica sobre 193 / 162 / 148 pares: **0** em todos os runs — coerente com o
núcleo comum zero. `UNRELATED` permanece default, não rótulo. **Nenhum modelo produziu
relação** (`D15`).

### `COMPILE-TRACE` e custo
**10/10 chamadas** registradas, campos completos, **config idêntica entre runs**,
`claude-opus-5` resolvido em todas. **10 de 24** do cap. **76.370** tokens de entrada,
**35.931** de saída.

### KILL
**KILL-1** camada selada byte-idêntica antes e depois · **KILL-2** 1,0357× ≤ 1,5× ·
**KILL-3** 257/257 seladas `ENTAILED`.

## 5. MATRIZ ESPERADO × OBSERVADO

| item | esperado | observado |
|---|---|---|
| tokenizer controls | 4 pos + 5 neg | **9/9** |
| consolidator controls | 7 fixtures, `INVALID` precede `FAIL` | **7/7** |
| judge controls | 3 estados + 2 cross-source | **5/5** |
| blocker positive controls | 100% sobrevivem | **2/2 nos 3 runs** |
| proveniência | 100% | **257/257** |
| sealed `ENTAILED` | 100% | **257/257** |
| workflow | 100% preservado | **6/6 travessias** |
| isolamento | 0 falsa atribuição | **0** |
| chamadas | ≤ 24 | **10** |

## 6. FORA DE ESCOPO — confirmado

Zero `MS-001` · zero corpus de marketing · zero Operationalization · zero Router · zero
Skill Pack · `SOURCE = chapter` **permanece exceção de piloto**, não contrato de produção ·
zero `N1–N9` · o `.docx` de 6 h **não foi lido**. `latest wins` não foi usado; nenhum
`SUPERSEDES` produzido.
