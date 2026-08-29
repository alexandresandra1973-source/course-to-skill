# HANDOFF — sessão de madrugada

`2026-08-11T03:14:32+00:00` · gerado por `handoff_madrugada.py` · READ-ONLY sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/` · nada congelado, nenhuma conversa aberta.

## 1. Pronto

| artefato | sha256 | bytes |
|---|---|---|
| `STRUCTURAL-CEILING-REPORT-v0.1.4.yaml` | `a3d659f34db29087…` | 18673 |
| `BASELINE-SUMMARY-v0.1.4.md` | `dac83c3d70e0e38d…` | 6242 |
| `BASELINE-PROVENANCE-v0.1.4.yaml` | `4cf74c31e53d7d87…` | 18494 |
| `TEST-0008-RUBRIC-DRAFT-v0.1.4.yaml` | `a6c27d8268db06ee…` | 7522 |
| `TEST-0008-METRICS-DISCREPANCY.md` | `371e80a709ad197f…` | 8321 |
| `LESSON-DURATION-AUDIT-v0.1.4.md` | `6e6c8decd07155b0…` | 3450 |
| `BLIND_RUN_READY-v0.1.4/ANCHOR-LINES.md` | `119f2de21f47b2df…` | 570 |
| `BLIND_RUN_READY-v0.1.4/CANDIDATE-ATTACHMENTS.md` | `a25be0774d68a479…` | 1648 |
| `BLIND_RUN_READY-v0.1.4/JUDGE-ATTACHMENTS.md` | `d4658c7a13300c10…` | 1408 |
| `BLIND_RUN_READY-v0.1.4/README-ABERTURA.md` | `0613041961c10976…` | 654 |
| `BLIND_RUN_READY-v0.1.4/SHA256SUMS.txt` | `38d92a50dbb46d4a…` | 574 |

**FRENTE A** — portão de hash **PASS** (5 artefatos); cinco checks estruturais recomputados dos bytes, todos PASS; teto **60.0**, banda **[34.0; 60.0]**. Portão dos canários: **PASS**, 5/5.

**FRENTE B** — baseline com 23/23 elementos, cada um com span de L0 e citação verificada pelo script; 12/12 formas estruturais rejeitadas por falta de âncora. ROBOT e os cinco componentes cobertos (`9:46-10:02`): **True**. Resumo das condições 2 e 3 byte-idêntico: **True**. Régua em `DRAFT_NOT_FROZEN`.

**FRENTE C** — duração real da fonte confirmada em três evidências independentes; conclusão no relatório.

## 2. O que divergiu e travou

**A4 travou — não congelei nada.** `freeze_margin_lock.py` e `freeze_pre_run_registry.py` não existem no repositório. A tarefa mandava usar "os scripts já auditados"; escrever scripts de congelamento novos na madrugada e usá-los seria justamente o contrário disso. A cadeia margin lock → registry → opening record continua por fazer.

**Caminho de entrada, de novo.** `Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007/ARMS_WORDING_FROZEN` não existe. Achei os três braços por conteúdo em `Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007/ARMS_WORDING_FROZEN/PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN.zip`. Os hashes conferem, então é divergência de caminho, não de conteúdo — mas é a segunda sessão seguida em que isso aparece.

**A5 saiu em outro lugar.** A pasta foi pedida dentro de `Course-to-Skill/`, que esta sessão declarou read-only absoluto. Montei em `docs/BLIND_RUN_READY-v0.1.4/` e ela só REFERENCIA os pacotes por hash, sem copiar. Mover é decisão sua.

**Falta o `JUDGE-BLIND-RUN-INSTRUCTIONS` da v0.1.4.** Só existe o da v0.1.3. Não gerei: seria inventar artefato congelado. Por isso a linha de âncora do juiz está PENDENTE.

**Duas descobertas do próprio teste da Frente B**, ambas corrigidas e registradas: os títulos de seção do YouTube vêm colados ao fim do segmento e partiam citações ao meio; e `routing` ocorre em L0 uma vez, em 8:10, como "lead routing" — sentido diferente do roteamento entre recursos.

## 3. O que fazer à mão ao acordar

1. **Decidir o limiar** da v0.1.4 (ver §4) — nada abaixo disso destrava.
2. **Escrever/recuperar** `freeze_margin_lock.py` e `freeze_pre_run_registry.py`, com auditoria, e só então rodar a cadeia.
3. **Reemitir e congelar** o `JUDGE-BLIND-RUN-INSTRUCTIONS` para a v0.1.4.
4. **Criar** a árvore `v0.1.4/06_COMPARISON_ARMS/TEST-0007/` e mover para lá o pacote de braços e a pasta `BLIND_RUN_READY`.
5. **Mandar auditar por terceiro** o `TEST-0008-RUBRIC-DRAFT-v0.1.4.yaml` antes de congelar — quem escreveu o baseline (eu) escreveu o rascunho da régua, e é exatamente a circularidade que o TEST-0008 mede.
6. **Só depois** abrir as conversas cegas, seguindo o `BLIND_RUN_READY-v0.1.4/README-ABERTURA.md`.

## 4. Decisões que sobraram para você

**a) O limiar da v0.1.4.** A banda [34.0; 60.0] não mudou da v0.1.3, porque a Opção B mudou o candidato e não a régua. Reconfirmar 34,0 herdado, ou pré-declarar regra própria para o estímulo novo? Não derivei nem congelei limiar.

**b) Quem audita a régua do 0008.** Precisa ser alguém que não escreveu o baseline. Sem isso o teste mede a si mesmo.

**c) Onde mora a v0.1.4.** Hoje os artefatos v0.1.4 vivem sob a árvore `v0.1.3/`. Enquanto isso não for resolvido, todo caminho declarado em tarefa vai continuar não batendo.

