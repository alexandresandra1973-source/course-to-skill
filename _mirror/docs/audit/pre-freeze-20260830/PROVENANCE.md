# PROVENANCE — PRE-FREEZE AUDIT, rodada de 2026-08-30

**O que é este diretório.** A **evidência histórica** de uma rodada de auditoria que
terminou bloqueando o freeze da arquitetura multi-source. Um único artefato, preservado
byte a byte.

**Materializado no git em:** 2026-08-30.
**Classe:** `GIT_NATIVE_BY_DESIGN` — nasce no git, não tem contraparte no Drive por
desenho, não deve ser enviado para lá, e não pode ser removido por sincronização baseada
na origem.

---

## O artefato

| campo | valor |
|---|---|
| arquivo | `PRE_FREEZE_AUDIT_FAIL.md` |
| bytes | 16770 |
| sha256 | `b9e607e2742facc27d255da8f13b5bb4029f3d783d656787ab15a8b516126677` |
| caminho original | `~/prefreeze-work/PRE_FREEZE_AUDIT_FAIL.md` |
| resultado da rodada | **`FREEZE_BLOCKED`** |

Linha de resultado, copiada do próprio relatório:

> **Resultado:** **FAIL** — 1 `DIVERGE_MATERIAL`

---

## O que este relatório registra

A auditoria confrontou 18 afirmações factuais (A1–A18) contra o corpus real. Uma delas
foi classificada `DIVERGE_MATERIAL`: **o número `139/226 = 61,50%`, usado como baseline de
`REPRODUCED_FROM` nos documentos de design, não existe no corpus.** `139` pertence à
população de regras com `precedence: UNDEFINED` do PILOT-002 e `226` à população de
citações das três rodadas cegas — a razão cruza populações. Esse achado é o que bloqueou
o freeze e o que motivou a medição real, preservada em
`_mirror/docs/measurements/reproduced-from-baseline-20260830/`.

## O que este relatório NÃO incorpora

**Nada posterior à sua própria rodada.** Ele foi preservado exatamente como escrito,
sem incorporar o resultado da medição que veio depois, sem corrigir suas próprias
recomendações à luz dela, e sem qualquer melhoria de texto. É o registro do estado do
conhecimento **naquele momento** — é isso que o torna evidência.

Quem quiser o baseline medido deve ler o diretório de medições, não este.

---

## Integridade

- Cópia **byte-idêntica** ao original: `shutil.copyfile`, sem preservação de modo, modo
  final `644`. Nenhuma transformação de conteúdo, nenhum recálculo, nenhum ajuste de
  timestamp interno.
- Verificação: sha256 do destino idêntico ao da origem, conferido no ato da cópia.
- O original em `~/prefreeze-work/` permanece **intacto** — reconferido por sha256 após
  a cópia.
- `SHA256SUMS.txt` neste diretório cobre todos os arquivos, gerado por `sha256sum`.
