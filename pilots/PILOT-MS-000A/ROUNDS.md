# PILOT-MS-000A — ÍNDICE DE RODADAS

Documento **aditivo**. Nenhuma rodada anterior é reescrita, renomeada ou apagada.

| rodada | o que foi | classificação | artefatos |
|---|---|---|---|
| **ROUND 1** | primeira tentativa; abortou na asserção estrutural de `C4` **antes** de qualquer veredito ser observado, gravado ou classificado | **`INVALID_FIXTURE`** | `out/RUN-0-INVALID.md` · `OPENING-RECORD.md` (`bb4427c4…`) |
| **ROUND 2** | rodada corrigida e executada; 8/8 esperado | `PILOT_MS_000A_PASS` — **superada pela ROUND 3**, ver ressalvas | `out/summary.json` · `out/PILOT-MS-000A-REPORT.md` · `out/raw-results.jsonl` · `fixtures/` · commit `449504f` |
| **ROUND 3** | rodada sob disciplina estrita: Opening Record **próprio**, e `C4` reconstruído com **dois produtores reais e divergentes** | ver `round-3/out/` | `round-3/` |

## ROUND 1 — `INVALID_FIXTURE`

**Motivo:** `C4 fixture construction invalid before evaluative execution`.

O gerador escrevia o hash falso de `C4` como `"0" * 64` **sem aspas** no YAML; o parser leu
o valor como **inteiro**. A asserção estrutural do runner abortou. **Nenhum veredito foi
observado, gravado ou classificado.** Não é `FAIL` do seal verifier — é fixture inválida.

Preservados sem alteração: o Opening Record original
(`bb4427c458e21f2938ce0ee0a9d084676d0d2a681d061b686ef5481aeec281e6`), a expectativa
declarada, e o registro que demonstrou o defeito.

## ROUND 2 — executada, com duas ressalvas que a ROUND 3 corrige

A ROUND 2 rodou e devolveu `PILOT_MS_000A_PASS` com 8/8 resultados esperados. Ela fica
**preservada como está**. Duas ressalvas, registradas aqui e não escondidas:

1. **Reutilizou o Opening Record da ROUND 1.** As expectativas eram as mesmas e não foram
   alteradas, mas a disciplina mais estrita exige record próprio por rodada — um record
   selado para um conjunto de fixtures que se revelou defeituoso não deve cobrir o
   conjunto corrigido.
2. **`C4` plantou `0` × 64.** É sintaticamente um sha256 válido, mas é **placeholder** —
   não é o hash de um produtor real. O canário provava *"o hash declarado difere do
   real"*, e não a coisa mais forte: **duas identidades de produtor válidas e
   divergentes**. Do jeito que estava, um verificador que apenas rejeitasse valores
   suspeitos passaria no teste sem provar `PRODUCER_IDENTITY_MISMATCH`.

## ROUND 3 — o que muda

- **Opening Record próprio**, selado antes de qualquer execução avaliativa.
- **`C4` reconstruído:** o selo declara `toolchain_path: TOOLCHAIN-A.txt` — o produtor
  realmente presente — mas com o `toolchain_sha256` de **`TOOLCHAIN-B.txt`, um segundo
  artefato de produtor real e diferente**. Ambos os hashes são sha256 reais de arquivos
  existentes; o defeito é **divergência de identidade**, não dado malformado.
- **Prova estrutural de todas as fixtures como portão pré-execução**, com abort em
  `ROUND_3_INVALID` se qualquer uma não contiver o defeito pretendido.
- **Verificadores reutilizados sem alteração.** O instrumento não era o problema; a fixture
  era. Trocar o instrumento entre rodadas invalidaria a comparação.
