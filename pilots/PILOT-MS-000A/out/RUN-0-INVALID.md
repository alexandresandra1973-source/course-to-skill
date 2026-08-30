# PILOT-MS-000A — RUN 0 · `PILOT_MS_000A_INVALID`

**Data:** 2026-08-30 · **Classificação:** `PILOT_MS_000A_INVALID`
**Motivo:** defeito de construção de fixture, detectado pela asserção estrutural do runner
**antes** de qualquer veredito ser observado, persistido ou classificado.

## O defeito

`build_fixtures.py` gerava o hash de toolchain falso da fixture `C4` como `"0" * 64` e o
escrevia **sem aspas** no YAML. O parser leu `0000…0` como **inteiro**, não como string de
64 caracteres. A asserção estrutural quebrou com `TypeError: 'int' object is not
subscriptable`.

## Por que isso é `INVALID` e não `FAIL`

A fixture **não continha o defeito pretendido**. O defeito de `C4` é *"o produtor declarado
tem hash diferente do produtor real"* — um sha256 textual divergente. O que a fixture
continha era um **valor de tipo errado**. O verificador provavelmente teria emitido
`PRODUCER_IDENTITY_MISMATCH` de qualquer forma, mas **pelo motivo errado** — comparação
entre `str` e `int` em vez de comparação entre dois hashes.

Um canário que dispara pelo motivo errado não prova nada sobre a definição de `SEALED`.

## O que NÃO foi feito

- **O Opening Record não foi reescrito.** Sua matriz e seu sha256
  (`bb4427c458e21f2938ce0ee0a9d084676d0d2a681d061b686ef5481aeec281e6`) permanecem os
  declarados antes de qualquer execução.
- **Nenhuma expectativa foi alterada.**
- **Nenhum resultado avaliativo foi observado**: o runner abortou dentro da asserção
  estrutural de `C4`, sem imprimir, gravar ou classificar veredito algum.

## O que foi feito

Corrigido apenas o **gerador de fixture**: o hash falso passa a ser escrito como string
YAML entre aspas, para que a divergência seja entre dois sha256 textuais, que é o defeito
que `C4` deve conter.

A execução avaliativa acontece na **RUN 1**, rodada explicitamente separada, registrada em
`out/summary.json` e `out/PILOT-MS-000A-REPORT.md`.
