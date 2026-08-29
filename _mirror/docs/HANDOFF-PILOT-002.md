# HANDOFF — PILOT-002

`2026-08-11T04:01:51+00:00` · gerado por `handoff_pilot002.py` · READ-ONLY sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/` · nenhuma conversa cega aberta · rubrica do TEST-0008 intocada.

## Held-out — a linha que importa

**O held-out do PILOT-002 foi cortado ANTES de qualquer extração: o lock `HELDOUT-LOCK-PILOT-002.yaml` está `SEALED_BEFORE_EXTRACTION`, retirou 86 dos 818 segmentos (10.5%) por span declarado, e nenhum L1, compilação ou rubrica foi produzido para este piloto.**

## Pronto

| artefato | sha256 | bytes |
|---|---|---|
| `PILOT-002-VAULT-SEAL.yaml` | `62dc993e2d56f654…` | 1660 |
| `HELDOUT-LOCK-PILOT-002.yaml` | `2e40c375761f8436…` | 6375 |
| `L0_COVERAGE_MAP-PILOT-002.md` | `e4f66cfa977ffaca…` | 3212 |
| `PRE-RUN-CHAIN-v0.1.4.md` | `2e90dd557ff98fef…` | 4735 |
| `BLIND_RUN_READY/ANCHOR-LINES.md` | `4b9ee60904b895cf…` | 665 |
| `BLIND_RUN_READY/CANDIDATE-ATTACHMENTS.md` | `6ac55e85e1da7d8f…` | 1571 |
| `BLIND_RUN_READY/JUDGE-ATTACHMENTS.md` | `edc929fa7f2fafbd…` | 1351 |
| `BLIND_RUN_READY/JUDGE-BLIND-RUN-INSTRUCTIONS-v0.1.4.md` | `56420146fe414b08…` | 2799 |
| `BLIND_RUN_READY/README-ABERTURA.md` | `507828189ec6461f…` | 631 |
| `BLIND_RUN_READY/SHA256SUMS.txt` | `e4b81a22fea03e00…` | 678 |

### Frente B — G0, G1, G2

- **G0.** L0 ingerido no vault por conteúdo. 819 marcas de tempo, primeira `0:00`, última **`1:21:35`** — confere com a esperada `1:21:35`. Timestamps sobreviveram à cópia: **True** (819 indexadas pelo vault, nenhuma perdida).
- **G1.** Corte por span, não por sorteio. Lock idêntico nas **2** execuções: **True**. L0 íntegro `43b58271feb0a1d5…` (819 marcas) · L0 CORTADO `85ea229011a989ea…` (733 marcas).
- **G2.** Mapa de cobertura do L0 cortado, no formato do PILOT-001.

### Frente A

- Freezers extraídos dos pacotes F4 e F3-TRISTATE, ambos conferindo com o manifesto de origem. Nenhum editado.
- Árvore `v0.1.4/` criada em `Course-to-Skill-Claude/docs/`.
- `BLIND_RUN_READY` publicada com as duas listas de anexo, SHA256SUMS e README de 15 linhas.

## Travou

**A cadeia de lock da v0.1.4, pelos mesmos dois hardcodes da sessão anterior. Continua sem congelar.** Não houve patch F5 desde então:

1. `freeze_margin_lock.py` — `structural_role` aceita só o papel genérico ou o nome de artefato da **v0.1.3**. Diagnóstico refeito: trocando apenas o `arm_id` numa cópia em `/tmp`, o freezer congela.
2. `freeze_pre_run_registry.py` — `candidate_version` fixo em `0.1.3`; carimbaria versão falsa no registry e no opening record.

Por isso **a segunda linha de âncora continua bloqueada**: ela é o hash do opening record, que não existe.

### Divergências de caminho encontradas nesta sessão

- A fonte foi pedida em `pilots/PILOT-002/00_SOURCE/L0-transcript.txt`. O que existe é `Course-to-Skill-Claude/pilots/PILOT-002/00_SOURCE/L0-transcript.txt.docx` — **`.docx`**, e sob `Course-to-Skill-Claude/`, não `Course-to-Skill/`. Sorte: é a árvore gravável, então deu para normalizar e gerar o `.txt` no lugar esperado.
- Os artefatos v0.1.4 seguem morando sob `v0.1.3/`.

### Resíduo declarado no lock

As duas linhas de título das seções retiradas **permanecem** no corpus de treino: elas não têm marca de tempo, logo não são endereçáveis por span e um corte por span não as alcança. Mantidas de propósito — removê-las seria cortar além do span pedido. São 2:

- `## Understanding Permission Modes (Plan, Accept Edits, Auto, Bypass)` (abre em `11:55`)
- `## Managing Your Context Window and Token Usage` (abre em `44:40`)

O conteúdo saiu inteiro: **zero** marcas das duas seções ficaram fora dos spans declarados.

## À mão, ao acordar

1. **Decidir sobre o resíduo:** apagar as duas linhas de título do corpus de treino, ou aceitar que o rótulo do assunto retirado fique visível.
2. **Pedir o patch F5** dos freezers: estender `structural_role` para o arm_id da 0.1.4 e trocar o `candidate_version` fixo por parâmetro. Com auditoria, como os anteriores.
3. **Rodar `prerun_chain_v014.py`** de novo depois do F5 — ele refaz a cadeia e publica sozinho.
4. **Mover** a árvore `v0.1.4/` e o pacote de braços para dentro de `Course-to-Skill/`.
5. **Colar o transcript do PILOT-002** em `docs/PILOT-002-transcript.txt` e rodar `source_density.py` para fechar o veredito de densidade que ficou pendente — agora a fonte existe, é só apontar o script para ela.

## Decisões que sobraram

**a)** Como corrigir os dois hardcodes: patch nos freezers (recomendo) ou reemitir o relatório estrutural com `arm_id` genérico — o segundo resolve metade e deixa a versão errada carimbada.
**b)** O limiar da v0.1.4: reconfirmar 34,0 herdado ou pré-declarar regra própria. Aberto desde duas sessões atrás.
**c)** O resíduo de título do held-out do PILOT-002.

