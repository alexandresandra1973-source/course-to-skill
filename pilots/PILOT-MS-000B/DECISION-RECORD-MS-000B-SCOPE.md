# DECISION RECORD — escopo e exceções do `PILOT-MS-000B`

**`decision_id`:** `DR-MS-000B-001` · **Data:** 2026-08-30 · **Ator:** Alexandre Sandra, dono do acervo
**Base:** `MS-000B-PRE-IMPLEMENTATION-DESIGN.md`
(`a7e71315c515fe893abbbd1316aecd71a14e6d01a626ac5b84c62aa3a525bfe1`)
**Política vigente:** `ARCHITECTURE FREEZE` `6d0eb7dd…` · **Classe:** `GIT_NATIVE_BY_DESIGN`

---

## D1 — CORPUS

**`PILOT-002`, capítulos 12 + 13** — o par **P-A** do design report.
Substituição silenciosa por outro par: **proibida**.

| capítulo | título | intervalo | evidências |
|---|---|---|---|
| 12 | `Managing Version Control with GitHub` | 3.202–3.762 s | 44 (`EV-0290`–`EV-0333`) |
| 13 | `Connecting Tools & Deploying Apps via MCP and CLI` | 3.767–4.312 s | 56 (`EV-0334`–`EV-0389`) |

## D2 — `SOURCE` — EXCEÇÃO EXPERIMENTAL

> **`SOURCE = CHAPTER`** · **`scope = PILOT_MS_000B_ONLY`**

Cada capítulo gera **um Source Package próprio**, com `source_package_hash` próprio.

**Isto NÃO altera o modelo de produção.** O mapeamento natural permanece:

```
SOURCE   = curso
ARTIFACT = aula / material
```

**A exceção existe exclusivamente porque o MS-000B precisa exercitar dois
`source_package_hash`.** Sob o mapeamento de produção, dois capítulos seriam dois
*artifacts* dentro de **um** pacote — e o piloto não exercitaria identidade qualificada,
par cross-package, blocagem nem travessia de fronteira. Mediria a si mesmo.

**Legitimidade sob o freeze:** `E1` (compilador source-local; cada fatia é uma execução
isolada) · `E2` (a fronteira é percorrida duas vezes) · `E6` (dois hashes reais para
qualificar) · `E10` (fusão incremental com *k*=2).

**Reavaliação obrigatória antes de qualquer uso de produção**, por `DECISION_RECORD` próprio.

## D3 — `SOURCE INDEPENDENCE`

**Ambos os pacotes: `KNOWN_DEPENDENT`**, declarado **antes** de rodar.

Motivo: **mesmo autor · mesma gravação · mesmo curso**.

**Corroboração entre os dois NÃO conta como independência** (`E9`, `I15`). Toda
corroboração é reportada em **dois campos** — contagem e estado de independência — nunca
colapsada num escalar.

## D4 — `L0` E CADEIA DE PROVENIÊNCIA

**Pai operacional imediato: o `CUT`**, porque é o L0 contra o qual as âncoras usadas já
foram medidas — o que dá ao piloto um controle de proveniência herdado.

A cadeia inteira é preservada e registrada em todos os três níveis:

```
FULL L0  →  CUT L0  →  CHAPTER SLICE  →  SOURCE PACKAGE
```

| nível | sha256 |
|---|---|
| `FULL L0` | `43b58271feb0a1d518ae6f81ab29836eb9c7f2bec5eb02e53f70c7bd1eb514ed` |
| `CUT L0` | `85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29` |
| `CHAPTER SLICE` | computado no ato, registrado no `SOURCE-PROFILE` de cada pacote |

> **O chapter slice é artefato NOVO e derivado, de 2026-08-30.** Não se finge que sempre
> existiu. Cada slice declara `derived_from` o hash do CUT e o intervalo de linhas.
> **Os L0 pais são selados e não são escritos.**

## D5 — `.docx` DE 6 HORAS

> **`NOT AUTHORIZED FOR MS-000B`.**

Não abrir caminho de implementação a partir dele. **Não extrair. Não usar.** Nenhum código
deste piloto lê `.docx`.

## D6 — EXECUÇÕES

**`RUN-1`, `RUN-2`, `RUN-3`**, independentes, obrigatoriamente com: **mesmos dois sources ·
mesmos bytes de entrada · mesma partição · mesma configuração · mesmo model/policy ·
mesmos prompts e versionamento · mesmo código.**

**A variável observada é a variância geradora**, não alteração experimental. Qualquer
divergência de modelo, config ou partição entre runs ⇒ **`PILOT_MS_000B_INVALID`**.

---

## O QUE ESTE RECORD NÃO DECIDE

Não autoriza produção · não altera o `ARCHITECTURE FREEZE` · não inicia `MS-001` · não
libera as fontes de marketing reservadas · não escolhe threshold algum.
