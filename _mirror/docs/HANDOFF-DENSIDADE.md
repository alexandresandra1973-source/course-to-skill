# HANDOFF — densidade

`2026-08-11T03:49:49+00:00` · gerado por `handoff_densidade.py` · READ-ONLY sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/` · **nada congelado**, nenhuma conversa aberta.

## Veredito de densidade, em uma linha

**NÃO EMITIDO: o transcript do candidato não foi obtido; o PILOT-001 mediu 3.249 decisões/min em 15.08 min e REPROVA o teste da uma página (49 bullets > 45), então a régua está calibrada e falta só a segunda fonte.**

## Pronto

| artefato | sha256 | bytes |
|---|---|---|
| `PRE-RUN-CHAIN-v0.1.4.md` | `1908a3dfdfa13017…` | 4735 |
| `SOURCE-DENSITY-COMPARISON.md` | `db61636606cba36c…` | 3044 |
| `PILOT-002-CANDIDATE-METADATA.yaml` | `1c0971d3b8cc4176…` | 2373 |
| `BLIND_RUN_READY/ANCHOR-LINES.md` | `4b9ee60904b895cf…` | 665 |
| `BLIND_RUN_READY/CANDIDATE-ATTACHMENTS.md` | `6ac55e85e1da7d8f…` | 1571 |
| `BLIND_RUN_READY/JUDGE-ATTACHMENTS.md` | `edc929fa7f2fafbd…` | 1351 |
| `BLIND_RUN_READY/JUDGE-BLIND-RUN-INSTRUCTIONS-v0.1.4.md` | `56420146fe414b08…` | 2799 |
| `BLIND_RUN_READY/README-ABERTURA.md` | `507828189ec6461f…` | 631 |
| `BLIND_RUN_READY/SHA256SUMS.txt` | `7e5506515838568e…` | 678 |

- **Freezers extraídos e conferidos**: `freeze_margin_lock.py` (pacote F4) e `freeze_pre_run_registry.py` (pacote F3-TRISTATE), ambos batendo com o manifesto do próprio pacote. Nenhum foi editado.
- **Árvore `v0.1.4/`** criada em `docs/`, com a nota de que os artefatos v0.1.4 hoje moram sob `v0.1.3/`.
- **BLIND_RUN_READY completa**, incluindo o `JUDGE-BLIND-RUN-INSTRUCTIONS-v0.1.4.md` derivado da v0.1.3 e marcado como derivado no cabeçalho.
- **PILOT-001 medido**: 49 pontos de decisão, 3.249/min, teste da uma página **None**.
- **Metadados do PILOT-002 apurados**: vídeo `7l6bXLAKyEI`, 01:21:37 (4897s), 14 capítulos.

## Travou

**A cadeia de lock, em dois pontos independentes. Não congelei nada.**

1. `freeze_margin_lock.py` recusa: a função `structural_role` aceita só o papel genérico ou o nome de artefato **da v0.1.3**, cravado no código. Isolei a causa trocando apenas o `arm_id` numa cópia em `/tmp` — com o nome genérico o freezer congela. É amarração de versão, não erro de conteúdo.
2. `freeze_pre_run_registry.py` tem `candidate_version` **fixo em `0.1.3`**. Sondado, carimbaria 0.1.3 no registry e no opening record de uma rodada v0.1.4 — afirmação falsa dentro dos artefatos que existem para provar integridade. Esse é o bloqueio decisivo: o primeiro tem contorno, este não.

**O transcript do PILOT-002.** O YouTube devolve as legendas com HTTP 200 e corpo vazio (exige PO token) e a API de player responde `LOGIN_REQUIRED` ou `UNPLAYABLE` em ANDROID_VR, IOS, WEB e MWEB. Parei a medição, como mandado. Não estimei nada.

**Achado lateral:** o artigo do freeCodeCamp anuncia "1.5-hour watch", mas o vídeo tem 01:21:37 — 4897s contra 5400s.

## À mão, ao acordar

1. **Cole o transcript** do vídeo `7l6bXLAKyEI` em `docs/PILOT-002-transcript.txt` e rode `python3 source_density.py`. O veredito sai sozinho — a métrica e a metade do PILOT-001 já estão prontas.
2. **Peça um patch F5** que estenda `structural_role` para aceitar o arm_id da 0.1.4, e que troque o `candidate_version` fixo do registry por parâmetro. Com auditoria, como os anteriores.
3. **Rode a cadeia** de novo depois do F5: `prerun_chain_v014.py` refaz tudo e publica sozinho.
4. **Mova** o pacote de braços v0.1.4 e a árvore `v0.1.4/` para dentro de `Course-to-Skill/`.
5. **Só então** abra as conversas cegas, seguindo o `README-ABERTURA.md`.

## Decisões que sobraram

**a) Como corrigir os dois hardcodes.** Patch F5 nos freezers, ou reemitir o relatório estrutural com `arm_id` genérico? O segundo resolve só metade e deixa o `candidate_version` errado. Recomendo o patch.
**b) O limiar da v0.1.4** continua em aberto desde a sessão anterior: reconfirmar 34,0 herdado ou pré-declarar regra própria.
**c) Se o PILOT-002 não qualificar**, decidir se procura outra fonte ou se aceita um corpus de fontes finas com o custo estatístico que isso traz.

