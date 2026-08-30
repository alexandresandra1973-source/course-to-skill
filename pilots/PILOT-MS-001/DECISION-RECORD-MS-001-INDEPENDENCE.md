# DECISION RECORD — `B_AND_C_DECLARED_INDEPENDENT_FOR_MS_001`

**`decision_id`:** `DR-MS-001-INDEP-001` · **Data:** 2026-08-30
**Ator:** Design Review externa · **Classe:** `GIT_NATIVE_BY_DESIGN` · **Natureza:** **ADITIVA**

## D1 — A declaração

# `DECLARED_INDEPENDENT`

Aplicada ao par `MS001-SRC-B` × `MS001-SRC-C`.

## D2 — ESCOPO — estrito e não transferível

Esta declaração vale **somente**:

1. para o **`PILOT-MS-001`**;
2. para os **artefatos B/C congelados por hash nesta decisão**, e nenhum outro.

| `source_id` | `SOURCE_CONTENT_HASH` (artefato de caption congelado) |
|---|---|
| `MS001-SRC-B` | `2a6ab098868e0714e5d4bc5cebb8018216d78f0243ee890b2c531516fbda7862` |
| `MS001-SRC-C` | `ed967fae27146d9aa9cc45769672f751d8eb199bc6ed7564bbb5fdb4a226fab7` |

> **Se os source artifacts mudarem de hash no futuro, esta declaração NÃO se transfere
> automaticamente.** Uma reaquisição que produza bytes diferentes exige nova auditoria e
> nova decisão. Isto é a condição de morte `K11`.

## D3 — Base registrada

Todos os sinais abaixo foram medidos mecanicamente, sem chamada de modelo:

| sinal | `MS001-SRC-B` | `MS001-SRC-C` |
|---|---|---|
| autoria / canal | Anderson Adelino \| IA e Automações | Guilherme Lazarotto - Tecnologia & Automação |
| `channel_id` | `UCI5WcISxqiFfoh4mse1s-HA` | `UCO0x-39c7EttOhmFAsngfgg` |
| `video_id` | `dtAoZYMEzcM` | `NvrBpnbNfv4` |
| data de publicação | 2026-06-24 | 2025-02-19 (**16 meses antes**) |
| cadeia editorial | Zenithon Academy | curso próprio N8N Fácil |
| domínio próprio | `zenithonacademy.com.br` | `guilhermelaz.com.br` |
| categoria | Science & Technology | Education |

- **Nenhuma referência cruzada encontrada.** Nenhuma das fontes menciona o `video_id`, o
  canal, o nome do autor ou o domínio da outra. Cada uma só se auto-referencia.
- **Nenhuma indicação de adaptação, tradução ou cópia.**
- **Zero n-gramas compartilhados de 6+ palavras** entre as duas transcrições:

| n-grama | compartilhados |
|---|---|
| 5 palavras | 2 |
| **6 palavras** | **0** |
| **8 palavras** | **0** |
| **10 palavras** | **0** |
| **12 palavras** | **0** |

## D4 — PRECISÃO OBRIGATÓRIA

Esta declaração **NÃO** significa:

> ~~prova universal de que os autores nunca compartilharam qualquer influência.~~

Significa:

> há evidência suficiente para tratá-los como **autoridades e proveniências independentes
> no experimento controlado MS-001**.

Ambos ensinam automação de WhatsApp via Evolution API — um domínio técnico com literatura
pública comum. Influência indireta por documentação compartilhada da Evolution API é
plausível e **não é excluída** por esta decisão. O que está excluído, por medição, é
dependência **direta**: mesma autoria, mesma aula, adaptação, tradução, cópia ou script comum.

## D5 — O que esta decisão substitui

O `MS-001-CONTROLLED-CORPUS-DESIGN-REPORT.md`
(`23234f936efa5542257dd9d644dae2c799b71a4e8a5fe70d03cdc05a5af71d17`) classificou o par como
`CANDIDATE_FOR_DECLARED_INDEPENDENT` e **recusou** declarar a independência ali, por não
haver Decision Record formal. Esta é a decisão formal que faltava. O relatório **não é
reescrito**.

## D6 — O que esta decisão NÃO autoriza

Não autoriza execução do MS-001 · não autoriza geração de Claims ou Candidates · não
autoriza compilação · não promove nada a produção · não transfere independência para
qualquer outro par, artefato ou piloto.
