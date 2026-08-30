# PRE_FREEZE_AUDIT_FAIL — Course-to-Skill Multi-Source

**Data:** 2026-08-30 · **Máquina:** `LenovoAIO27ARR9`
**Resultado:** **FAIL** — 1 `DIVERGE_MATERIAL`
**Consequência aplicada:** nada commitado · nada congelado · ETAPA B e ETAPA C **não executadas**
**Escrita nesta sessão:** somente `~/prefreeze-work/`. Zero escrita em `/mnt/g`. Zero escrita no repo.

---

## G0 / G1 — PORTÕES (ambos PASS)

```
uname -s = Linux · hostname = LenovoAIO27ARR9 · /mnt/g/Meu Drive montado · repo existe
git fetch origin                       → exit 0
git rev-parse HEAD                     → a049354d67d0374490138979c0a520a4abe2d495
git rev-parse origin/main              → a049354d67d0374490138979c0a520a4abe2d495
git status --porcelain                 → (vazio)
git ls-files | wc -l                   → 460
```

Insumos G1 (recomputados, `stat -c%s` + `sha256sum`):

| arquivo | bytes | sha256 |
|---|---|---|
| `COURSE-TO-SKILL-MULTI-SOURCE-DESIGN-REVIEW-v0.md` | 39.700 | `ae4d4efd9b916f8bf3f0333dc6d8f2dc02dfd8f830537235a04de15726b975b6` |
| `…ARCHITECTURE-PROPOSAL-v1-SHA913753.md` | 46.313 | `913753700e72758d22add234509c507cde8de004c8464ceaa718ebea13fdaab5` |
| `…ARCHITECTURE-PROPOSAL-v1.1.md` | 23.511 | `f2f9f4b755e0ed66703a4e3d9d436b5ccc01b8f5d6c8b5377cfa6f7786aa8b33` |

Os três batem. `…PROPOSAL-v1.md` (46.327 B) existe na mesma pasta e **não foi tocado**.

---

## ESPAÇOS DE DECLARAÇÃO INSPECIONADOS

1. Arquivos do repo (`git ls-files` = 460) · 2. ADRs (`_mirror/docs/adr/ADR-0001…0014`, `_mirror/pilots/PILOT-002/adr/`, `ADR-ACERVO-001`) · 3. Manifests (`COMPILATION_MANIFEST.yaml` de bundle e de PASS2, `manifest.yaml`, `SOURCE-MANIFEST`, `MIRROR-MANIFEST-N6`) · 4. Freezes (`FREEZE-RECORD-*` de compiler-v2 0.2.0/0.2.1/0.2.2 e compiler-s3 0.1.0/0.1.1, `SHA256SUMS.txt`, selos, freeze records de heldout/vault/blinding) · 5. Erratas e pendências (`ERRATA-*`, `PENDENCY-*`) · 6. Runners (`p00*_*.py`, `_mirror/pilots/PILOT-004/runners/`, `cts/`) · 7. **Mensagens de commit** (`git log --all --format='%H%n%B'`) · 8. Drive, leitura (`Chat GPT/Course-to-Skill*`).

Toda busca por **radical**, nunca por forma literal. **Controles positivos** (todos ≠ 0):
`226`→5 em PILOT-002-CLOSURE.md · `precedence`→4 · `evidence_id`→90 repo / 66 drive ·
`segment_id`→63 / 46 · `compiler_version`→38 arquivos · `BASELINE_MANIFEST_20260810`→16 ·
`sincroniza` em mensagens de commit→1. **Busca validada.**

---

## TABELA A1–A18

| # | Afirmação | Resultado |
|---|---|---|
| A1 | ancoragem 226/226 · 12/226 (5,3%) · **139/226 (61,50%)** | **DIVERGE_MATERIAL** |
| A2 | precedence UNDEFINED 93,3% / 88,7% / 96,9% | CONFERE |
| A3 | P003 2.463 ev · 835 regras · bundle 880.321 B · piso 411.658 tk | CONFERE |
| A4 | N9 — três pilotos numeram de `EV-0001` | CONFERE |
| A5 | N1/N2 — `RT-CITE-001` e `questions.yaml`; 3 manifests → `compiler-s3/0.1.0` | CONFERE |
| A6 | N4 — `artifact_id` repetido nos três manifests | CONFERE |
| A7 | N5 — manifesto do P002 lista a si mesmo e diverge | CONFERE |
| A8 | selo — 4 arquivos alterados; FREEZE do v0.2.2 idêntico ao 0.2.0 e falha no lugar | CONFERE |
| A9 | workflows de passo único 34,9% / 25,3% / 33,3% | CONFERE |
| A10 | sem compile-trace · revarredura 0 · campos do portão escritos pelos runners | CONFERE |
| A11 | SKILL.md declara `LOAD ORDER` + `required_executable_resources` + `fail_closed` | **DIVERGE_COSMETICO** |
| A12 | marcadores multi-source = ZERO | **DIVERGE_COSMETICO** |
| A13 | `PENDENCY-SOURCE-LANGUAGE-FIELD.md` existe; zero campo de língua | CONFERE |
| A14 | commit `378d764` — taxonomia, os 12, D2, proibição de `--delete`; 12→14 | **DIVERGE_COSMETICO** |
| A15 | origem do "1,5× por particionamento de chamadas" | CONFERE (localizado) |
| A16 | `RULE-SEARCH-BY-RADICAL.md` existe | **DIVERGE_COSMETICO** |
| A17 | braço ablado do TEST-0007 — manifest congelado declara os três | **DIVERGE_COSMETICO** |
| A18 | PROPOSAL v0 original no Drive | **NOT_LOCATED** (não bloqueante) |

**13 CONFERE · 5 DIVERGE_COSMETICO · 1 DIVERGE_MATERIAL · 1 NOT_LOCATED**
(A16/A17 são cosméticos e A18 é não-bloqueante; o total soma 18 com A1 contando uma vez.)

---

# A DIVERGÊNCIA MATERIAL

## A1 — o número do meio dos três não existe no corpus

### Afirmação

> `LOCATED_IN` 226/226 (100%) · **`REPRODUCED_FROM` 139/226 (61,50%)** · `SUPPORTED_BY` 12/226 (5,3%)

Aparece em `…DESIGN-REVIEW-v0.md:57, 98, 246, 420, 422` · `…PROPOSAL-v1-SHA913753.md:166, 208` · `…PROPOSAL-v1.1.md:28, 188`.

### Evidência

**O que o corpus mede (`_mirror/docs/PILOT-002-CLOSURE.md`):**

```
173: | identificadores citados nas três rodadas | 226 |
174: | que existem no bundle | 226 — verificado mecanicamente contra o índice |
175: | que foram verificados quanto a ancorar o que dizem ancorar | 12 |
176: | cobertura da verificação | 12 ÷ 226 = 5,3% |
```
→ **226/226 CONFERE. 12/226 = 5,3% CONFERE.**

**O que o corpus NÃO mede.** Busca exaustiva por radical:

```
grep -rIn -e '61,5' -e '61.5' .                    → 0 ocorrências no repo inteiro
git log --all --format='%H%n%B' | grep '61,5'      → 0
grep -rIn '139/226' <repo> <drive>                 → só os três documentos de design
```

**De onde vêm 139 e 226 no corpus real — populações diferentes:**

```
_mirror/docs/PILOT-002-CLOSURE.md:213
  "139 de 149 regras do PILOT-002 — 93,3% — têm precedence: UNDEFINED"
```
Recomputado por script (`decision-rules.yaml`): `UNDEFINED=139`, `rule_id=149`, `139/149 = 93,2886%`.
**139 é a contagem de regras sem precedência.** É o numerador de A2, não de ancoragem.

```
_mirror/docs/PILOT-002-CLOSURE.md:75
  "| E4 citação reencontrada verbatim no L0 cortado | 72 |"
```
**A medição mecânica de reencontro verbatim que o corpus tem é E4 = 72, sobre 149 regras — 48,3221%.** Não é 139, não é sobre 226, não é 61,50%.

**A aritmética que fecha o diagnóstico:**
```
139/226 = 61,5044%   ← o número dos documentos
139/149 = 93,2886%   ← o que 139 realmente mede (precedence UNDEFINED)
 72/149 = 48,3221%   ← o que o corpus realmente mede de verbatim (E4)
 12/226 =  5,3097%   ← confere
```
`139/226` combina **numerador da população de regras (149)** com **denominador da população de citações (226)**. São conjuntos distintos, medidos por instrumentos distintos, em rodadas distintas.

### Impacto — por que é MATERIAL e não cosmético

O número não é decorativo; é a **evidência motivadora** de decisões congeláveis:

| onde | o que apoia |
|---|---|
| v0 §57, §98 · v1 §166 | a tese "os três predicados colapsam num campo só" — **D7** (três relações de ancoragem, `NOT_APPLICABLE ≠ MISSING`), **E5** |
| v1 §208 | a *previsão congelada antes de qualquer rodada* |
| v1.1 §1.3 | a **retratação registrada** — argumenta sobre "derrubar `REPRODUCED_FROM` abaixo de 61,50%" |
| v1.1 §7.2 e **I29** | "os três números conhecidos (100% · 61,50% · 5,3%) são propriedades desse salto" |
| **D35** | validade de claim em dois saltos, com `REPRODUCED_FROM` como régua do salto de baixo |

O efeito real: **o predicado do meio não tem medição nenhuma.** Não é que o número esteja impreciso — é que `REPRODUCED_FROM` / `QUOTED_FROM` nunca foi medido sobre a população de 226. Congelar `I29` e `D35` citando três números medidos, quando dois são medidos e um é construído, reproduz exatamente o defeito que este projeto criou o portão da busca por radical para pegar: **número sem procedência em script** (`I16`).

Agrava: `I16` é ela própria um invariante da v1 — "nenhum relatório traz número digitado à mão". Congelar a arquitetura com `61,50%` dentro dela viola o invariante no ato do freeze.

### Errata OU reabertura — recomendação

**Reabertura**, não errata. Errata bastaria se o número estivesse mal escrito; aqui a medição não existe. Três saídas, todas de Alexandre:

1. **Medir.** Rodar sobre as 226 citações o mesmo arnês do teste de falso-negativo, comparando cada citação com o texto do L0. Barato — o CLOSURE §3.1 já o descreve como "a próxima medição a fazer, e é barata". Sai um `REPRODUCED_FROM` real e a v1.1 congela com três números medidos.
2. **Rebaixar.** Reescrever §7.2/`I29`/`D35` com **dois** números medidos (100% e 5,3%) e declarar `REPRODUCED_FROM` como **`NOT_YET_MEASURED`**. A tese do colapso sobrevive: 100% × 5,3% já a prova sozinha. `D7` e `E5` não caem.
3. **Substituir pelo que existe.** Usar E4 = 72/149 (48,32%) como a medição mecânica real, **declarando a mudança de população** — mas então não é o mesmo denominador dos outros dois, e o trio deixa de ser comparável. Menos recomendado.

Em qualquer caso, a §1.3 da v1.1 (retratação do critério de morte) precisa ser reescrita: ela argumenta contra um número que não existe. **A conclusão da retratação continua certa** — o critério da v1 era vazio — mas por uma razão adicional à que ela dá.

---

# AS CINCO DIVERGÊNCIAS COSMÉTICAS

Nenhuma muda a verdade de um D/I. Todas são **erro de localizador**: a substância existe, o artefato apontado é outro. Cada uma tem errata de uma linha.

## A11 — `required_executable_resources` e `fail_closed` não estão no `SKILL.md`

**Afirmação:** "SKILL.md vigente: `## LOAD ORDER — MANDATORY` + `required_executable_resources` + `fail_closed`".

**Medido:**
```
                                 SKILL.md   manifest.yaml
## LOAD ORDER — MANDATORY           1/1/1        —
required_executable_resources       0/0/0       3/3
fail_closed                         0/0/0       3/3
```
(ordem: PILOT-002-v2 / PILOT-003-v2 / PILOT-004)

`_mirror/pilots/PILOT-003-v2/skill/manifest.yaml` (`schema_version: 0.3.0`) declara
`required_executable_resources:` e `fail_closed_on_missing_executable_resource: true`
dentro do bloco `runtime:`. Os três elementos do contrato existem no bundle vigente; **dois vivem no `manifest.yaml`, não no `SKILL.md`.**

**Impacto:** `E8`/`D22`/§11 **intactos** — os dois contratos de runtime existem e o legado é fail-closed. **Risco operacional real:** um script de empacotamento que verifique o contrato varrendo `SKILL.md` concluirá, erradamente, que ele não existe.

**Errata:** trocar "SKILL.md" por "`SKILL.md` (LOAD ORDER) + `manifest.yaml` (`runtime.required_executable_resources`, `runtime.fail_closed_on_missing_executable_resource`)".

## A12 — a varredura multi-source não é literalmente zero no Drive

**Medido (repo · Drive-excluindo-os-docs-de-design):**
```
source_id            0 · 3        multi_source   0 · 0
cross_source         0 · 0        source_set     0 · 0
source_package_hash  0 · 0        fusion_id      0 · 0
CONTROLE: evidence_id 90 · 66  |  segment_id 63 · 46
```
Os 3 hits de `source_id` são: `Course-to-Skill/course-to-skill-compiler/evidence.schema.yaml` (`required: [source_id, source_type]`), o schema equivalente do release v0.1.1, e `PILOT-001-HubSpot-AI-Agent/analysis/evidence.jsonl`. **Todos da linhagem v0.1.x abandonada**, e semanticamente é um localizador **intra-curso** (`source_id: "SRC-M01-L01-VIDEO"`), não um marcador de multi-fonte.

**Impacto:** nenhum sobre D/I. Reforça a tese: o pipeline vigente (v2/s3) **não tem dimensão de fonte** — o campo existia no schema legado e foi perdido na migração.

**Errata:** "zero no repo; no Drive, `source_id` sobrevive apenas como homônimo intra-curso no schema v0.1.x abandonado; `multi_source`, `cross_source`, `source_set` = zero em ambos".

## A14 — `--delete` não aparece na mensagem do commit

**Medido:** `git log -1 --format=%B 378d764` contém `GIT_NATIVE_BY_DESIGN` (1×), `12 arquivos` (1×), `unidirecional` (1×), `Drive -> Git` (1×), **`--delete` (0×)**.
Busca por radical: `--delete` não existe em **nenhum** arquivo do repo, em **nenhuma** mensagem de commit, e no Drive **apenas nos três documentos de design**.

A proibição está lá, sem nomear a flag (linhas 14–15):
> `12 arquivos sao GIT_NATIVE_BY_DESIGN: existem so no git, nao sao ausencias, nunca podem ser removidos por sincronizacao baseada na origem.`

O resto de A14 **confere**: 12 à época; `a049354` adicionou exatamente os dois arquivos —
`ADR-ACERVO-001-…md` 8.652 B `c5b63d02ce8d18e2fdd6601a5a20a8bfe17d3e06776aa509018ae1265561e1e8` e
`ERRATA-MIRROR-MANIFEST-N6-…md` 3.888 B `0d45635a9a3ccfb1f8f64a1fe590e773c1f4fc62a9a274c9814773ac963a40bc` — logo 12 → 14.

**Errata:** "proibição de remoção por sincronização baseada na origem (a mensagem não nomeia a flag `--delete`; a formulação é semântica)".

## A16 — o arquivo tem outro nome

**Afirmado:** `RULE-SEARCH-BY-RADICAL.md`. **Real:** `_mirror/docs/RULE-SEARCH-BY-RADICAL-NOT-LITERAL-FORM.md` (5.169 B). Existe, sustenta `I17`. **Errata:** usar o nome completo.

## A17 — o contrato do braço ablado está na rubrica, não no manifesto do braço

**Afirmação:** "manifest congelado [do braço ablado] declara `required_executable_resources` + `fail_closed` + recusa contratual".

**Medido nos manifests congelados dos braços** (`…/TEST-0007/PILOT-001-TEST-0007-ARM-A|ARM-B/…/runtime-bundle/manifest.yaml`, `schema_version: 0.1.0`): `required_executable_resources` **0** · `fail_closed` **0** · recusa **0**. Não têm bloco `runtime:` nenhum.

**Onde a evidência realmente está** — `TEST-0007-RUBRIC-v0.1.3.yaml` (8.629 B, sha256 `66aa33c0c39430fc02a23fc536a475eda8afbd6b18c0f34b01ef075ebf522e9f`), congelada:
```
189:  - code: ROUTING_INTEGRITY_BYPASS
190:    automatic_fail: true
191:    condition: >-
192:      Required executable resources are absent but the run proceeds as if the
193:      target workflow were available, contrary to fail_closed_on_missing_executable_resource.
202:  refusal_scoring_is_predeclared: true
205:    ABLATED@AFTER_DEDUP package hashes from the frozen arm record.
```

**Impacto:** §11.2 / `D22` / `D23` **intactos** — a recusa contratual do braço ablado foi pré-declarada e congelada, com `automatic_fail`. Só o localizador está errado.

**Errata:** "a rubrica congelada `TEST-0007-RUBRIC-v0.1.3.yaml` (`ROUTING_INTEGRITY_BYPASS`, `refusal_scoring_is_predeclared: true`); os `manifest.yaml` dos braços são v0.1.1 e não carregam o contrato".

---

# A18 — NOT_LOCATED (não bloqueia)

`COURSE-TO-SKILL MULTI-SOURCE — ARCHITECTURE PROPOSAL v0` — o documento que a `DESIGN REVIEW v0` declara como seu objeto (linha 3) — **não existe** no Drive nem no repo.

```
find "/mnt/g/Meu Drive/Chat GPT" -iname '*MULTI-SOURCE*'
  29/08 23:19  39.700  …DESIGN-REVIEW-v0.md
  29/08 23:41  46.327  …ARCHITECTURE-PROPOSAL-v1.md
  29/08 23:52  23.511  …ARCHITECTURE-PROPOSAL-v1.1.md
  30/08 00:02  46.313  …ARCHITECTURE-PROPOSAL-v1-SHA913753.md
```
`CLAUDE_ARCHITECTURE_PROPOSAL.md` (10/08, 35.687 B, sha256 `1b5dd5d87cce731e754e65bd79f8ea956299fecee8587008d887b09ebec015e1`) **não é** ele: é a proposta da Fase 3, com **0** ocorrências de "multi-source".

**Limitação declarada:** a cadeia arquivável é `DESIGN REVIEW v0 → v1 → v1.1`. O **v0 revisado não é arquivável** — só a revisão dele. Quando o freeze acontecer, isto tem de constar como limitação, não ser silenciado.

---

# ACHADOS INCIDENTAIS (fora de A1–A18, registrados sem classificar)

1. **`compile-trace` escrito em `/tmp`.** `_mirror/compiler-s3-v0.1.1/run_compile.py:35` define `TRACE = T / f"compile-trace-{PILOT}.json"` e o próprio comentário (linha 26) registra: *"O compile-trace do PILOT-004 foi PERDIDO na limpeza do /tmp"*. Reforça `I19` com uma causa concreta: não é só que ninguém registrou a partição — o artefato era gravado em diretório volátil.
2. **`revarredura` em P003/P004 não é "0", é campo ausente.** P001-v2 e P002 têm `rescan_iterations: 0`; P003 e P004 **não têm o bloco**. O caminho nunca existiu nesses manifests. Mais forte que o afirmado.
3. **`files:` do manifesto do P002 lista nomes nus.** Além do auto-hash divergente (A7/N5), três entradas — `decision-rules.yaml`, `runtime-policy.yaml`, `workflows.yaml` — não resolvem a partir do diretório do manifesto: os arquivos vivem em `knowledge/`. Resolução relativa quebrada, além do N5.

---

# ESTADO FINAL DA SESSÃO

```
git status --porcelain            → (vazio)
git rev-parse HEAD                → a049354d67d0374490138979c0a520a4abe2d495
git ls-files | wc -l              → 460
escrita em /mnt/g                 → NENHUMA
arquivos novos no repo            → NENHUM
commits criados                   → NENHUM
multi-source/ criado              → NÃO
MIRROR-GOVERNANCE-MATERIALIZED-…  → NÃO criado
```

**ARCHITECTURE_FREEZE não executado. Classificação: `FREEZE_BLOCKED`.**
