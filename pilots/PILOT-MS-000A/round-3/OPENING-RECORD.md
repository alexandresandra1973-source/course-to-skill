# PILOT-MS-000A / ROUND 3 — OPENING RECORD

**Status:** `DECLARED_BEFORE_ANY_EVALUATIVE_RUN`
**Data:** 2026-08-30 · **Máquina:** `LenovoAIO27ARR9`, ext4
**Rodada:** `ROUND 3` — própria, **não** reutiliza o Opening Record da ROUND 1
(`bb4427c458e21f2938ce0ee0a9d084676d0d2a681d061b686ef5481aeec281e6`).

**Architecture Freeze:** `ARCHITECTURE_FROZEN`
· freeze `6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b`
· selo `f35016cbedf4617a45a4b03a89acefb01495d6d50651b77065b26c7fd901a0c3`

**Julgamento:** `MECHANICAL / OFFLINE`. Zero chamadas de modelo. Nenhum LLM julga fixture.

---

## 1. POR QUE EXISTE UMA ROUND 3

| rodada | resultado | por quê |
|---|---|---|
| ROUND 1 | `INVALID_FIXTURE` | `C4` construída com `"0"*64` sem aspas; o YAML leu como inteiro. Abortou na asserção estrutural, **antes de qualquer veredito**. Preservada intacta |
| ROUND 2 | `PASS`, com duas ressalvas | reutilizou o Opening Record da ROUND 1; e `C4` plantava `0`×64 — sintaticamente válido, mas **placeholder**, não o hash de um produtor real |
| **ROUND 3** | esta | Opening Record próprio; `C4` com **duas identidades de produtor reais e divergentes** |

**Nenhuma rodada anterior é reescrita, renomeada ou apagada.** A ROUND 2 permanece
byte-idêntica no commit `449504f`.

## 2. A CORREÇÃO DE C4 — o que muda substantivamente

A ROUND 2 provava *"o hash declarado difere do real"*. Isso é fraco: um verificador que
apenas rejeitasse valores suspeitos — `0`×64 é visivelmente artificial — passaria sem
nunca comparar identidades de produtor.

A ROUND 3 planta o caso forte:

- **`TOOLCHAIN-A.txt`** — o produtor **realmente presente** no conjunto selado de `C4`;
- **`TOOLCHAIN-B.txt`** — um **segundo produtor real**, com conteúdo diferente, vivendo em
  `fixtures/TOOLCHAINS/`, fora de qualquer conjunto selado;
- o selo declara `toolchain_path: TOOLCHAIN-A.txt` mas `toolchain_sha256` = **o sha256 real
  de `TOOLCHAIN-B.txt`**.

Os dois valores são sha256 verdadeiros de arquivos existentes. O defeito é
**divergência de identidade de produtor**, não dado malformado.

> `C4` tem de disparar **`PRODUCER_IDENTITY_MISMATCH`**, e **não** algo como
> `INVALID_SHA256_FORMAT`. Se disparar por formato, o canário não prova o que se propõe.

## 3. INSTRUMENTO — reutilizado sem alteração

`seal_verifier.py` (`63cfe229de85713a2717b2d9cd3cd6d49de871b10bad255284af379259dc717f`)
e `identity_verifier.py` (`51aede028a9e3069faad6bdfb1912a6cada2259918a1a8cf760e8e21691f7c84`),
importados do diretório do piloto, **byte-idênticos aos da ROUND 2**.

**O instrumento não era o problema — a fixture era.** Trocar o instrumento entre rodadas
destruiria a comparabilidade e transformaria o piloto em ajuste até passar.

## 4. PORTÃO PRÉ-EXECUÇÃO

`structural_proof.py` prova **mecanicamente**, sem usar o verificador, que cada fixture
contém o defeito pretendido. Roda **antes** da avaliação. Se qualquer prova falhar:
**`ROUND_3_INVALID` e PARA** — não se conserta e continua dentro da mesma rodada.

## 5. MATRIZ ESPERADA — declarada agora, não alterável depois

| fixture | classe | esperado | código de falha esperado |
|---|---|---|---|
| `HAPPY` | `SEAL_INTEGRITY` | **`PASS`** | — |
| `C1` | `SEAL_INTEGRITY` | **`FAIL`** | `SHARED_MUTABLE_DIRECTORY` |
| `C2` | `SEAL_INTEGRITY` | **`FAIL`** | `DOES_NOT_VALIDATE_IN_PLACE` |
| `C3` | `SEAL_INTEGRITY` | **`FAIL`** | `SEAL_SELF_REFERENCE` |
| `C4` | `SEAL_INTEGRITY` | **`FAIL`** | **`PRODUCER_IDENTITY_MISMATCH`** |
| `C5` | `PACKAGE_IDENTITY` | **`FAIL`** | `GLOBAL_ID_COLLISION` + identidade qualificada distinta |
| `C6` | `PACKAGE_IDENTITY` | **`FAIL`** | `NAKED_LOCAL_ID` |
| `CTRL-INVALID` | `SEAL_INTEGRITY` | **`INVALID`** | `SEAL_RECORD_UNPARSEABLE` |

**O código esperado tem de estar presente.** `FAIL` pelo motivo errado conta como
resultado inesperado e derruba a rodada.

### C5 — três asserções, não uma
1. `local_id` **pode** repetir entre pacotes — legal, não é o defeito;
2. identidade **nua** tem de **colidir** → `GLOBAL_ID_COLLISION`;
3. identidade **qualificada** tem de permanecer **distinta**.

### `CTRL-INVALID`
Controle do instrumento, não um sétimo defeito: prova que o verificador distingue
**"não consegui avaliar"** de **"detectei defeito"**. Se voltar `FAIL`, a rodada é
`INVALID`.

## 6. ISOLAMENTO

Fixtures **sintéticas e descartáveis**, geradas por `build_fixtures.py`. **Nenhuma é
mutação de artefato histórico.** O piloto não lê `_mirror/`, `cts/`, `compiler-*`, runners,
pilotos históricos nem o Drive.

## 7. CRITÉRIO

`PILOT_MS_000A_PASS` só se: portão estrutural 8/8 · `HAPPY` → `PASS` · `C1`–`C6` → `FAIL`
com o código esperado presente · `CTRL-INVALID` → `INVALID` · C5 com as três asserções ·
zero inesperados · execuções = matriz · outputs persistidos e hashes conferindo.

Defeito plantado que escape → `PILOT_MS_000A_FAIL`. Instrumento ou fixture incorretos →
`PILOT_MS_000A_INVALID`, **e PARA** — a correção vai para rodada nova e separada.
