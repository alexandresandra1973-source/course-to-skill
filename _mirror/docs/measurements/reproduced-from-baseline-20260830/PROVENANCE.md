# PROVENANCE — medição de `REPRODUCED_FROM`, 2026-08-30

**O que é este diretório.** O **instrumento e a evidência completa** da primeira medição
real do predicado `REPRODUCED_FROM` sobre os bundles selados do projeto. Opening record,
script, fixtures de controle, saída bruta por evidence, sumário e relatórios.

**Materializado no git em:** 2026-08-30.
**Classe:** `GIT_NATIVE_BY_DESIGN` — nasce no git, sem contraparte no Drive por desenho,
não deve ser enviado para lá, e não pode ser removido por sincronização baseada na origem.

---

## Rodada de origem e resultado

| campo | valor |
|---|---|
| classificação | **`BASELINE_ESTABLISHED`** |
| baseline agregado | **2921/3045 = 95.9278%** |
| fórmula | `PASS / (PASS + FAIL)` sobre elegíveis |
| examinado | 3045 |
| `NOT_APPLICABLE` | 0 |
| `INVALID` | 0 |
| `IN_REGION` / `OUT_OF_REGION` / `LOCATOR_UNRESOLVED` | 2921 / 0 / 0 |
| opening record | `35cd4abf5df72758c1d0e9019c757e8503c1a1aba02fea8ffef0b22babba8634` |
| tolerância do locator secundário | 30 s |

### Por bundle

| bundle | examinado | elegíveis | PASS | FAIL | baseline |
|---|---|---|---|---|---|
| P002 | 448 | 448 | 421 | 27 | 93.9732% |
| P003 | 2463 | 2463 | 2366 | 97 | 96.0617% |
| P004 | 134 | 134 | 134 | 0 | 100.0000% |

### L0 elegível — resolvido por sha256 declarado pelo próprio bundle

| bundle | arquivo | sha256 |
|---|---|---|
| P002 | `_mirror/pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt` | `85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29` |
| P003 | `_mirror/pilots/PILOT-003/00_SOURCE/L0-transcript.txt` | `04fda222febbaeece075f0096274ae8be00a7eedd5582006dd99d6ccc465e192` |
| P004 | `_mirror/pilots/PILOT-004/00_SOURCE/L0-transcript.txt` | `607f5a986bada49e81e8fcf3f1bce3ed2cdb63798ad6bcd4a8ab32018f2cb3f5` |

**Todos os números acima foram lidos de `out/reproduced-from-summary.json`**, que foi
emitido pelo script. Nenhum foi digitado.

---

## O que esta medição substitui

O baseline anterior de `REPRODUCED_FROM`, `139/226 = 61,50%`, está **invalidado** — a
razão cruza duas populações distintas. O achado está registrado em
`_mirror/docs/audit/pre-freeze-20260830/PRE_FREEZE_AUDIT_FAIL.md`. O número invalidado
**não entrou em nenhum cálculo desta medição**, nem como referência nem como expectativa;
está declarado assim no opening record, escrito antes de rodar.

O novo número não é o mesmo objeto que o antigo pretendia ser: mede a aresta
`EVIDENCE → SOURCE_ANCHOR` sobre a população de **evidences dos três bundles**, com
denominador declarado antes e prova de inclusão numerador ⊆ denominador.

## Ordem de execução, e por que ela importa

1. Opening record escrito e **hasheado antes de qualquer medição** — fixa população,
   elegibilidade, denominador, predicado, normalizações taxativas e política de língua.
2. Fixtures de controle rodadas **antes** da população, fora dela: uma que tem de dar
   `PASS`, uma que tem de dar `FAIL`. Ambas se comportaram como desenhadas.
3. Integridade dos três `EVIDENCE.jsonl` verificada por sha256; L0 de cada bundle
   resolvido **por igualdade de hash** sobre `git ls-files`, nunca por semelhança de nome.
4. Medição, com toda a saída emitida pelo script.

O opening record **não foi editado** depois de hasheado.

---

## Inventário

| arquivo | o que é |
|---|---|
| `REPRODUCED_FROM_MEASUREMENT_OPENING_RECORD.md` | o record selado antes da medição |
| `measure_reproduced_from.py` | o instrumento; read-only sobre repo e Drive |
| `build_fixtures.py` | construtor das fixtures de controle |
| `fixtures/fixture-cases.json` | os dois controles, fora da população |
| `out/reproduced-from-raw.jsonl` | um registro por evidence: id, bundle, estado, motivo |
| `out/reproduced-from-summary.json` | contagens, asserções e integridade |
| `out/REPRODUCED-FROM-BASELINE-REPORT.md` | relatório gerado pelo script |
| `out/SUPPORTED-BY-12-226-LOCATION.md` | localização documental do `12/226` |
| `out/POSTHOC-FAIL-BREAKDOWN.md` | diagnóstico posterior, fora da medição selada |

---

## Integridade

- Cópias **byte-idênticas** aos originais: `shutil.copyfile`, modo final `644`. Nenhuma
  transformação de conteúdo, nenhum recálculo, nenhum ajuste de timestamp interno.
- Cada uma verificada por sha256 contra a origem no ato da cópia.
- Os originais em `~/reproduced-from-baseline/` permanecem **intactos** — reconferidos
  por sha256 após a cópia.
- A medição **não foi reexecutada** nesta fatia. Estes são os artefatos daquela execução.
- `SHA256SUMS.txt` neste diretório cobre todos os arquivos, gerado por `sha256sum`.
