# PILOT-MS-000B — PRE-IMPLEMENTATION DESIGN REPORT

**Rodada:** `READ-ONLY CORPUS AUDIT + PILOT SPECIFICATION`. **Nada implementado.**
**Data:** 2026-08-30 · **Máquina:** `LenovoAIO27ARR9`
**HEAD:** `10ec796e0fad45174e3acde703a91b45c7d20ce2` · **Drive:** somente leitura, zero escrita.
**Este relatório vive em `~/ms000b-design/`, fora do repositório. Zero commit nesta rodada.**

---

## 1. GATE RESULT — **PASS**

| verificação | resultado |
|---|---|
| `HEAD == origin/main` | `10ec796e0fad45174e3acde703a91b45c7d20ce2` |
| working tree | limpa (0 linhas) · 566 arquivos versionados |
| Architecture Freeze | `6d0eb7dd…` · selo `f35016cb…` |
| Freeze Record valida no lugar | **17 membros, 0 divergências** |
| MS-000A ROUND 3 | `SHA256SUMS` **0 falhas** · `PILOT_MS_000A_PASS` · opening record `a11fff65…` |
| Drive | read-only |

---

## 2. ESTADO ACEITO DO MS-000A — conteúdo do futuro `DECISION_RECORD`

> **Onde entra:** este record **não é criado nesta rodada** — criá-lo aqui misturaria
> execução com desenho. Ele deve entrar no **primeiro commit da implementação do MS-000B**,
> como `pilots/PILOT-MS-000B/DECISION-RECORD-MS-000A-ACCEPTED.md`, ou antes disso num
> commit próprio de governança se Alexandre preferir separá-lo.

```
decision_id      : DR-MS-000A-001
decision         : MS_000A_ACCEPTED
ator             : Design Review externa
data             : 2026-08-30
base             : PILOT-MS-000A ROUND 3
```

**Evidência canônica de aceitação — ROUND 3**
`pilots/PILOT-MS-000A/round-3/` · opening record `a11fff651aca8797aa39aaca928fa4f06744478fdd29f8501c16979885c3be45`
· commit `10ec796e0fad45174e3acde703a91b45c7d20ce2` · 8/8 esperado, 0 inesperado, 0 defeito escapado.

**Rodadas preservadas, não promovidas**

| rodada | estatuto |
|---|---|
| ROUND 1 | **`INVALID_FIXTURE`** — abortou na asserção estrutural de C4 antes de qualquer veredito. Preservada intacta |
| ROUND 2 | **`NON_QUALIFYING_FOR_FINAL_ACCEPTANCE`** — reutilizou o Opening Record da ROUND 1 e tinha C4 insuficiente (placeholder `0`×64). Preservada, não reescrita |

**Estatuto dos contratos**

| contrato | estatuto |
|---|---|
| `SEAL CONTRACT` | `READY_FOR_EXPERIMENTAL_USE` |
| `PACKAGE IDENTITY CONTRACT` | `READY_FOR_EXPERIMENTAL_USE` |
| qualquer componente | **nenhum autorizado para produção** |

### O que foi provado
As sete condições de `SEALED` **detectam** os defeitos estruturais medidos: diretório
mutável compartilhado · selo que não valida no lugar · auto-referência · divergência de
identidade de produtor. E a identidade cross-package **rejeita `local_id` nu** e **mantém
qualificação distinta sob colisão**. O verificador aceita o caminho feliz e distingue
`INVALID` de `FAIL`.

### O que NÃO foi provado
Nada semântico. Nenhum Source Package real foi selado. Nenhuma claim foi gerada,
comparada ou fundida. Os verificadores rodaram sobre **fixtures sintéticas**, não sobre
corpus. `I1–I30` seguem **sem verificadores implementados** — só as famílias exercitadas
por C1–C6 têm instrumento. Nada foi medido sobre custo, blocagem, `ENTAILED_BY`, preservação
de workflow ou isolamento entre fontes.

---

## 3. CANDIDATOS DE CORPUS

### O achado que determina tudo

**Não existe, no acervo, um curso com duas aulas gravadas separadamente pelo mesmo autor.**
Todos os quatro pilotos são **um vídeo = um curso = uma transcrição**:

| piloto | fonte | língua | duração | L0 |
|---|---|---|---|---|
| PILOT-001 | HubSpot AI Agent, uma aula | en | — | não versionado como L0 |
| PILOT-002 | Claude Code course | en | 4.895 s | `43b58271…` (full) · `85ea2290…` (CUT) |
| PILOT-003 | Ecommerce Google Ads, `c6qEURhNsYw` | en | 13.857 s | `04fda222…` |
| PILOT-004 | Meta Business Suite, `GNOHB166vWY`, Filipe Detrey | pt | 903 s | `607f5a98…` |

`available-transcripts.json` do P004 lista **uma** transcrição. Nenhum `SOURCE-MANIFEST`
declara mais de uma fonte.

**Porém:** o L0 do **PILOT-002 traz 14 fronteiras de capítulo declaradas pela própria
fonte** (linhas `## …` na transcrição original). Fatiar ali **não é fabricar corpus** — a
fronteira já está no material. Os L0 do P003 e do P004 têm **uma** linha `##` (só o título),
portanto não oferecem fronteira declarada.

### Integridade dos capítulos do PILOT-002

O `L0-transcript-CUT.txt` — o L0 de que a `EVIDENCE.jsonl` foi de fato extraída — teve a
janela de held-out removida, e a remoção foi **alinhada a capítulo**: os capítulos **6** e
**10** saíram inteiros (33 e 53 marcas, 0 evidências). Os outros **12 estão intactos**.

### Pares candidatos — todos adjacentes, ambos intactos, estrutura ordenada nos dois

| par | capítulos | chars | ev A | ev B | pares A×B | regras | workflows | steps | segmentos |
|---|---|---|---|---|---|---|---|---|---|
| **P-A** | 12+13 · GitHub / MCP e CLI | 23.964 | 44 | 56 | **2.464** | 32 | 10 | 30 | 7 |
| **P-B** | 11+12 · Slash Commands / GitHub | 17.032 | 25 | 44 | **1.100** | 22 | 9 | 30 | 5 |
| **P-C** | 2+3 · Instalar Claude Code / Escolher IDE | 5.946 | 8 | 22 | **176** | 12 | 4 | 9 | 2 |

*(Existem ainda 7+8 e 8+9, com 3.843 e 3.721 pares — ricos demais para auditoria humana
integral, e por isso não recomendados nesta etapa.)*

---

## 4. CORPUS RECOMENDADO — **P-A: capítulos 12 + 13 do PILOT-002**

**`Managing Version Control with GitHub`** (3.202–3.762 s) **+**
**`Connecting Tools & Deploying Apps via MCP and CLI`** (3.767–4.312 s)

**Justificativa objetiva, não conveniência:**

1. **Sequenciais e adjacentes** — sem lacuna entre eles; a fronteira é declarada pela fonte.
2. **Ambos intactos** no L0 que a evidência usou — zero marcas removidas nos dois.
3. **Espaço de pares não-trivial: 2.464.** Blocagem só é mensurável com espaço grande o
   bastante para haver o que bloquear. P-C, com 176 pares, mediria blocagem no ruído.
4. **Estrutura ordenada nos dois lados** — 10 workflows e 30 steps distribuídos entre eles.
   Preservação de workflow, que é o critério crítico do DESIGN C, precisa de workflow dos
   **dois** lados; um par com workflow só de um lado não testaria travessia.
5. **Sobreposição temática real e não trivial:** os dois tratam de conectar o Claude Code a
   serviços externos e publicar — git/GitHub e MCP/CLI se sobrepõem em autenticação, setup
   de credencial e fluxo de deploy. Há o que corroborar, complementar e especializar.
6. **Auditável por humano:** 23.964 chars ≈ 4.000 palavras por capítulo. Uma sessão de
   leitura, não um mutirão.
7. **Custo baixo:** 7 segmentos no intervalo → **~7 chamadas de PASS 2** sob a regra
   congelada de um segmento por chamada. O P002 inteiro custou 41.

**Alternativa mais barata, se o orçamento apertar:** **P-B (11+12)**, 5 segmentos, 1.100
pares, 17k chars. **Alternativa mínima para auditoria exaustiva:** **P-C (2+3)** — mas
declaro que 176 pares é fraco para medir blocagem.

### Descartados, com motivo

| descartado | motivo |
|---|---|
| PILOT-003 e PILOT-004 fatiados | **uma só** linha `##` no L0 — não há fronteira declarada pela fonte; fatiar seria fabricar |
| PILOT-002 full × CUT | não são duas aulas: o CUT é o **mesmo** conteúdo menos a janela de held-out. Zero independência |
| PILOT-001 × PILOT-002 | autores e cursos diferentes — é o problema de arbitragem que o MS-000B **não** é |
| `CLAUDE CODE MARKETING FULL COURSE (6 HOURS).docx` | 17 capítulos `Capítulo N:` reais e 533.339 chars — **é** multi-aula. Mas: (a) não está selado nem versionado; (b) exigiria extração de L0 de `.docx`, que é implementação e está vetada nesta rodada; (c) **ambiguidade com as fontes reservadas** — é material de "Claude Code para marketing" e a lista reservada inclui "Claude Code + Evolution API + WhatsApp". **Não uso sem decisão de Alexandre.** Fica registrado como o melhor candidato *futuro* para um MS-000B mais realista |

---

## 5. HASHES E LOCALIZADORES DOS INSUMOS

| artefato | sha256 | papel |
|---|---|---|
| `_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt` | `85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29` | **L0 pai recomendado** — é o que a evidência do P002 usou |
| `_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript.txt` | `43b58271feb0a1d518ae6f81ab29836eb9c7f2bec5eb02e53f70c7bd1eb514ed` | L0 completo, com os capítulos 6 e 10 |
| `_mirror/pilots/PILOT-002-v2/EVIDENCE.jsonl` | `64853f7ac06a470f09333a80469b38e443ea5ce7aa3aee2e116ea1877059abfd` | **controle de proveniência** — 448 evidências já ancoradas |
| `_mirror/pilots/PILOT-002-v2/temporal-map.yaml` | 41 segmentos | mapa de segmentação |
| `_mirror/pilots/PILOT-002-v2/skill/knowledge/workflows.yaml` | — | workflows e steps de referência |

**Uso o CUT como pai** porque é contra ele que as 448 evidências existentes resolvem — o
que dá ao MS-000B um **controle de proveniência gratuito**: os anchors dos capítulos 12 e 13
já foram medidos em `REPRODUCED_FROM` (`95,9278%` agregado, P002 `421/448 = 93,9732%`).

> **Os L0 pais são SELADOS e não podem ser tocados.** As fatias são artefatos **novos e
> derivados**, com `derived_from: 85ea2290…` e o intervalo de linhas registrado. Byte-fiéis
> ao trecho, sem reescrita.

---

## 6. DEFINIÇÃO DE `SOURCE` — a decisão de desenho mais importante desta rodada

### A pergunta

`SOURCE = aula individual` **ou** `SOURCE = curso` com `ARTIFACT = aula`?

### A tensão, dita sem suavizar

A cadeia de proveniência congelada é
`SOURCE → ARTIFACT → SOURCE_ANCHOR → EVIDENCE → CLAIM`. Em produção, o mapeamento
**natural** é `SOURCE = curso`, `ARTIFACT = aula`: um curso é uma fonte com autoridade e
perfil próprios, e suas aulas são artefatos dentro dele.

**Mas sob esse mapeamento, duas aulas do mesmo curso viram dois artifacts dentro de UM
Source Package — e o MS-000B não exercitaria nada do que precisa medir.** Sem dois
`source_package_hash` distintos não há identidade qualificada para testar, não há par
cross-package, não há blocagem entre pacotes, não há travessia de fronteira. O piloto
mediria a si mesmo.

### A decisão proposta

> **Para o MS-000B: `SOURCE = capítulo`.** Cada capítulo é compilado **isolado** e selado
> como **seu próprio Source Package**, com `source_package_hash` próprio, derivado da sua
> própria fatia de L0.

**Confronto com o Architecture Freeze — é legítimo:**

- **E1** — o Compiler permanece estritamente source-local, uma fonte por execução. Cada
  fatia é uma execução isolada. ✔
- **E2** — a fronteira `SOURCE → COMPILE ISOLATED → PACKAGE ASSEMBLY → VALIDATE/SEAL →
  SOURCE PACKAGE` é percorrida **duas vezes**, uma por capítulo. ✔
- **E6** — identidade qualificada `(source_package_hash, local_id)` passa a ter **dois**
  package hashes reais para qualificar. ✔
- **E10** — fusão incremental com *k*=2: um conjunto de pares novo. ✔

**E é honesto sobre o que não é:** os dois pacotes **não são fontes independentes**. Mesmo
autor, mesma gravação, mesmo curso, mesma língua. O estado congelado correto é
**`source_independence: KNOWN_DEPENDENT`**, declarado desde o início e **não** `UNKNOWN`.

Isso é **exatamente adequado ao MS-000B**, que por desenho **não** é o piloto de arbitragem
entre autoridades. Corroboração entre esses dois pacotes **não** conta como evidência
independente, e o piloto tem de reportá-la nos dois campos exigidos por `I15`.

### Limitação declarada, para revisão antes de produção

`SOURCE = capítulo` é **escolha de escopo do piloto**, não o mapeamento de produção. Antes
de qualquer uso real, `SOURCE = curso / ARTIFACT = aula` tem de ser reavaliado — e a
diferença precisa de `DECISION_RECORD` próprio. Registrar isso agora evita que uma
conveniência de piloto vire contrato por inércia.

---

## 7. POR QUE ISSO EXERCITA MAIS DE UM SOURCE PACKAGE

| o que o piloto precisa medir | só existe com 2 packages? |
|---|---|
| identidade qualificada distinta sob `local_id` repetido | **sim** — com um package não há o que qualificar |
| colisão global nua entre pacotes | **sim** |
| pares cross-package e blocagem | **sim** — 2.464 pares no par recomendado |
| travessia Source Package → Fusion sem re-derivação | **sim** |
| isolamento (informação de A não aparece como de B) | **sim** |
| `fusion_id` por conjunto ordenado de hashes | **sim** — precisa de ≥2 hashes |

Ambos os capítulos numerarão evidências a partir de `EV-0001` — **reproduzindo de propósito
a colisão N9 sobre corpus real**, agora com qualificação para resolvê-la. É o canário C5 do
MS-000A saindo da fixture sintética para o material verdadeiro.

---

## 8. COMPONENTES MÍNIMOS A IMPLEMENTAR — YAGNI aplicado

| # | componente | por que é indispensável |
|---|---|---|
| 1 | **L0 slicer** com proveniência ao pai selado | sem ele não há duas fontes |
| 2 | **Package assembly** + `SOURCE-PROFILE` | `D11` exige `SOURCE-PROFILE` como membro obrigatório |
| 3 | **`SOURCE_ANCHOR`** por evidência | `E5`, e é o que `LOCATED_IN`/`REPRODUCED_FROM` medem |
| 4 | **`COMPILE-TRACE` com partição de chamadas** | `I19` — o único invariante que os pilotos históricos **nunca** satisfizeram |
| 5 | **Seal** usando o `seal_verifier` do MS-000A, sem alteração | contrato já `READY_FOR_EXPERIMENTAL_USE` |
| 6 | **Envelope de qualificação** `(source_package_hash, local_id)` + `identity_verifier` do MS-000A | `E6`, `I4` |
| 7 | **Geração de claims experimental** + `ENTAILED_BY` | `D35`, `I29` |
| 8 | **Source-local candidates** com workflow/sequência preservada | **DESIGN C** — é o critério crítico |
| 9 | **Blocagem experimental** com controles positivos plantados | mede para produzir threshold futuro |
| 10 | **Detecção mínima de relação** — só `IDENTICAL` (mecânica) e o par candidato para `CORROBORATES`/`COMPLEMENTS`/`SPECIALIZES` | `D15`: relação mecanicamente decidível nunca por modelo |
| 11 | **Fusion Package experimental** com `fusion_id` sem `mtx_policy_hash` | `I26` |

### Explicitamente ADIADO — não implementar no MS-000B

`Operationalization` · `OPERATIONAL PACKAGE` · `MTX-POLICY` · applicability · `SKILL PACK` ·
router · progressive disclosure · token budgeting · precedência e adjudicação · a taxonomia
completa de relações · `SUPERSEDES` · `PRESUPPOSES` · `DECLARATION-SPACE-INDEX` · embeddings ·
banco vetorial · qualquer threshold.

**Sobre `OPERATIONAL PACKAGE` e `I28`:** `I28` exige que o **Skill Pack** se construa sempre
de um Operational Package. O MS-000B **não constrói Skill Pack**, então `I28` não é acionado
e o Operational Package **não é necessário**. Sem Skill Pack, sem Operational Package.

---

## 9. PROPOSTA DE OPENING RECORD DO MS-000B

Estrutura a selar **antes** de qualquer execução avaliativa:

```
identificacao   : PILOT-MS-000B, data, maquina, HEAD, Architecture Freeze + selo
corpus          : L0 pai 85ea2290… ; capitulos 12 e 13 ; intervalos de linha e de tempo
                  hashes das duas fatias, computados no ato
SOURCE          : SOURCE = capitulo (decisao da secao 6, com a limitacao declarada)
independencia   : KNOWN_DEPENDENT, declarado antes de rodar
metodo          : particao de chamadas declarada ; 1 segmento por chamada ; modelo e versao
medicoes        : as oito da secao 10, cada uma com denominador declarado ANTES
controles       : positivos plantados para blocagem ; canario de isolamento
thresholds      : NENHUM. Esta rodada descobre baseline, nao aprova nada
```

---

## 10. MEDIÇÕES PRÉ-DECLARADAS

| # | medição | denominador declarado antes | forma |
|---|---|---|---|
| 1 | **Identity** — colisões globais nuas; `local_id` preservados; qualificação distinta | total de `local_id` dos dois pacotes | mecânico |
| 2 | **Provenance** — `package → claim → evidence → anchor → L0` resolve | todas as claims | mecânico, 100% ou falha (`I5`) |
| 3 | **Claim — variância** entre execuções independentes | conjunto de claims por execução | ≥2 execuções; reportar divergência |
| 4 | **`ENTAILED_BY`** pelo método congelado | claims elegíveis | julgamento com rubrica pré-registrada, output selado |
| 5 | **Workflow preservation** — sequência, condições e exceções sobrevivem à travessia | workflows e steps source-local dos dois pacotes | mecânico: comparar ordem e cardinalidade antes/depois |
| 6 | **Candidate admission** — distribuição dos sinais | candidatos gerados | **medir, não aprovar** |
| 7 | **Blocking** — candidatos, pares possíveis, pares bloqueados, **recall sobre pares conhecidos plantados** | 2.464 pares A×B | com controles positivos |
| 8 | **Cost** — chamadas, tokens, população de claims, pares antes/depois | — | do runner |
| 9 | **Isolation** — informação de A não aparece como proveniente de B | todas as claims/candidatos | canário plantado nos dois sentidos |

**Nenhum threshold é escolhido nesta rodada nem na próxima.** O MS-000B **produz** os
números de que o `MS-001` precisará.

### Sobre precedência — a trava

MS-000B **não é** o piloto de conflito entre autoridades. Mesmo autor e capítulos
sequenciais reduzem o problema, **mas não o eliminam**, e a redução não autoriza atalho:

> **`latest wins` continua proibido.** Ordem temporal pode informar a leitura de progressão
> dentro do mesmo curso, mas **qualquer `SUPERSEDES` precisa de sinal de versão no texto,
> com citação obrigatória** — nunca metadado, nunca posição, nunca `mtime`.

Conflito sem base textual vai para `NOT_YET_ADJUDICATED` ou `ESCALATED_TO_HUMAN`, **não**
para resolução silenciosa.

---

## 11. CRITÉRIOS `PASS` / `FAIL` / `INVALID` / `KILL`

**`MS_000B_PASS`** — proveniência resolve 100% · zero colisão global não qualificada ·
qualificação distinta · workflow preservado sem re-derivação silenciosa · isolamento sem
vazamento · todas as nove medições produzidas com denominador declarado antes · controles
positivos de blocagem recuperados · outputs persistidos com hash.

**`MS_000B_FAIL`** — qualquer defeito real escapa: proveniência que não resolve · colisão
que passa · workflow re-derivado em silêncio · informação de A atribuída a B.

**`MS_000B_INVALID`** — instrumento, fixture ou corpus incorretos; medição não permite
concluir. **Correção vai para rodada nova e separada**, como no MS-000A.

**`KILL`** — herdados do freeze, sem limiar novo:
- **KILL-1, mecânico e sem limiar (`I30`):** a geração de claims altera **um byte** da
  camada selada abaixo. Igualdade de hash antes/depois. Qualquer diferença → morte.
- **KILL-2:** variância entre execuções acima da tolerância pré-declarada, com teto de
  referência no **1,500× medido** do extractor.
- **KILL-3:** piso de `ENTAILED_BY` — **método congelado, número no opening record do
  piloto**, nunca antes.

---

## 12. ORÇAMENTO EXPERIMENTAL PROPOSTO

Extrapolado do medido no P002 — 41 invocações de PASS 2 para 448 evidências, 10,93 ev/chamada:

| item | estimativa |
|---|---|
| segmentos no par recomendado | **7** |
| chamadas de PASS 2 (1 segmento/chamada, regra congelada) | **~7 por execução** |
| execuções para medir variância de claim | **2 a 3** → **14 a 21 chamadas** |
| evidências esperadas | **~100** (44+56 já medidas no par) |
| pares cross-package antes da blocagem | **2.464** |
| julgamento de `ENTAILED_BY` | amostra pré-declarada, não o conjunto todo |

Ordem de grandeza: **dezenas de chamadas**, não centenas. O par P-B baixa para ~5
chamadas/execução; o P-C, para ~2.

---

## 13. RISCOS

| # | risco | mitigação |
|---|---|---|
| 1 | **`SOURCE = capítulo` vira contrato por inércia** | limitação declarada na §6; `DECISION_RECORD` obrigatório antes de produção |
| 2 | **Os dois pacotes não são independentes** e corroboração pode ser lida como confirmação | `KNOWN_DEPENDENT` declarado antes de rodar; `I15` exige dois campos |
| 3 | **Fatiar o L0 toca artefato selado** | fatias são artefatos **novos**, `derived_from` o hash do pai; o pai não é escrito |
| 4 | **`I19` nunca foi satisfeito por piloto nenhum** — e o `COMPILE-TRACE` do P004 se perdeu em `/tmp` | gravar o trace em caminho versionado, **não** em diretório volátil |
| 5 | **Blocagem sem algoritmo escolhido** pode virar escolha implícita | medir com controles positivos plantados; algoritmo **não** congela nesta rodada |
| 6 | **Sobreposição temática pode ser fraca demais** e a fusão não achar nada | par recomendado tem sobreposição real (setup/credencial/deploy); se der zero relação, é achado, não falha |
| 7 | **Amostra de `ENTAILED_BY` pequena** repete o `5,3%` do P002 | amostra pré-declarada e o número reportado como cobertura, não como qualidade |
| 8 | **Contaminação por conhecer o corpus** — o P002 já foi auditado | os controles de blocagem são plantados por script, com seleção estrutural, não por escolha |

---

## 14. DECISÕES AINDA NECESSÁRIAS ANTES DE CÓDIGO

**Só Alexandre pode fechar:**

1. **O par:** P-A (12+13, recomendado) · P-B (11+12, mais barato) · P-C (2+3, mínimo).
2. **`SOURCE = capítulo` aceito** para o MS-000B, com a limitação da §6 registrada?
3. **L0 pai:** CUT `85ea2290…` (recomendado, dá controle de proveniência gratuito) ou full
   `43b58271…`?
4. **O `.docx` de 6 horas** está ou não dentro das fontes reservadas? Se estiver liberado,
   é o melhor candidato para um MS-000B mais realista — mas exigiria extração de L0.
5. **Quantas execuções** para variância de claim: 2 ou 3?
6. **Onde entra o `DECISION_RECORD` do `MS_000A_ACCEPTED`** — commit próprio de governança
   ou junto do primeiro commit do MS-000B?

**Não decidido por mim de propósito.** Nenhuma dessas é escolha técnica com resposta única.

---

## 15. CLASSIFICAÇÃO

# `MS_000B_READY_FOR_IMPLEMENTATION`

Existe corpus adequado no acervo, com fronteira declarada pela fonte e integridade
verificada. A definição de `SOURCE` está resolvida com a limitação dita. Os componentes
mínimos estão delimitados e o adiado está explícito. As medições e os critérios estão
propostos sem inventar limiar.

**Condicionado às seis decisões da §14.** Nenhuma linha de código foi escrita.
