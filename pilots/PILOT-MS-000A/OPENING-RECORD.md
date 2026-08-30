# PILOT-MS-000A — SEAL CANARY · OPENING RECORD

**Status:** `DECLARED_BEFORE_ANY_EVALUATIVE_RUN`
**Data:** 2026-08-30 · **Máquina:** `LenovoAIO27ARR9`, ext4
**Architecture Freeze:** `ARCHITECTURE_FROZEN`, commit `66b153b9d8e9c0e06a8aefeccc38cc31f605b3a6`
**Freeze doc:** `6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b`
**Freeze record:** `f35016cbedf4617a45a4b03a89acefb01495d6d50651b77065b26c7fd901a0c3`

**Este record é escrito e hasheado ANTES da primeira execução avaliatória.**
Se a execução revelar defeito de instrumento ou de fixture, o resultado é
`PILOT_MS_000A_INVALID` — **este record não é reescrito para obter PASS.**

---

## 0. O QUE ESTE PILOTO NÃO É

**Não testa multi-source semanticamente.** Não há Source Package real, Fusion, Claim Pass,
Relation Engine, Operationalization, Router, Skill Pack, `MS-000B` ou `MS-001`.

Testa **uma coisa**: se a definição de `SEALED` congelada na §13 do Architecture Freeze
**detecta os defeitos estruturais que este projeto já mediu**.

**`MECHANICAL / OFFLINE`.** Zero chamadas de modelo. Nenhum LLM julga fixture. O veredito é
comparação de hash e inspeção estrutural — determinístico e reproduzível offline.

---

## 1. AS DUAS CLASSES DE TESTE

O freeze congela duas famílias distintas, e forçá-las no mesmo algoritmo seria erro:

| classe | o que verifica | verificador | canários |
|---|---|---|---|
| **`SEAL_INTEGRITY`** | propriedades do **selo** de um conjunto | `seal_verifier.py` | C1 · C2 · C3 · C4 |
| **`PACKAGE_IDENTITY`** | propriedades da **identidade** entre pacotes | `identity_verifier.py` | C5 · C6 |

Identidade cross-package é propriedade do **envelope**, não do hashing do conjunto. Dois
verificadores, um único `PILOT-MS-000A`.

---

## 2. O QUE `seal_verifier.py` CHECA — as sete condições

Da §13 do Architecture Freeze. Cada condição vira um código de falha:

| # | condição congelada | código de falha |
|---|---|---|
| 1 | o `SEAL-RECORD` enumera **todos** os membros por caminho relativo + `sha256` | `MEMBER_SET_MISMATCH` |
| 1b | o hash declarado de cada membro confere com o arquivo | `MEMBER_HASH_MISMATCH` |
| 2 | o hash do próprio selo é registrado **fora** do conjunto selado | `SEAL_HASH_NOT_REGISTERED_EXTERNALLY` |
| 3 | o selo **valida no lugar**, contra o diretório em que vive | `DOES_NOT_VALIDATE_IN_PLACE` |
| 4 | o diretório **não é escrito por outra versão selada** | `SHARED_MUTABLE_DIRECTORY` |
| 5 | o **produtor** é referência a `TOOLCHAIN` com hash próprio, não campo de texto | `PRODUCER_IDENTITY_MISMATCH` |
| 6 | validação **determinística e offline**, sem rede, relógio ou `mtime` | `MTIME_DEPENDENCY` |
| 7 | **nenhum membro se auto-referencia** no manifesto de membros | `SEAL_SELF_REFERENCE` |

Estados de saída: **`PASS`** (todas as condições) · **`FAIL`** (≥1 condição violada, com os
códigos) · **`INVALID`** (o selo não é avaliável — ilegível, ausente, malformado).

> **`FAIL` ≠ `INVALID`.** `FAIL` é defeito detectado no objeto. `INVALID` é impossibilidade
> de avaliar. Colapsar os dois esconderia instrumento quebrado atrás de "detectou".

---

## 3. O QUE `identity_verifier.py` CHECA

| # | regra congelada (`E6`, `I4`) | código de falha |
|---|---|---|
| 1 | toda referência cross-package é **qualificada** `(source_package_hash, local_id)` | `NAKED_LOCAL_ID` |
| 2 | identidade **global nua** por `local_id` colide entre pacotes | `GLOBAL_ID_COLLISION` |
| 3 | identidade **qualificada** permanece **distinta** entre pacotes | `QUALIFIED_ID_NOT_DISTINCT` |

---

## 4. MATRIZ ESPERADA — declarada agora, não alterável depois

| fixture | classe | veredito esperado | **código de falha esperado** |
|---|---|---|---|
| `HAPPY` | `SEAL_INTEGRITY` | **`PASS`** | — |
| `C1` | `SEAL_INTEGRITY` | **`FAIL`** | `SHARED_MUTABLE_DIRECTORY` |
| `C2` | `SEAL_INTEGRITY` | **`FAIL`** | `DOES_NOT_VALIDATE_IN_PLACE` |
| `C3` | `SEAL_INTEGRITY` | **`FAIL`** | `SEAL_SELF_REFERENCE` |
| `C4` | `SEAL_INTEGRITY` | **`FAIL`** | `PRODUCER_IDENTITY_MISMATCH` |
| `C5` | `PACKAGE_IDENTITY` | **`FAIL`** | `GLOBAL_ID_COLLISION`, **e** identidade qualificada distinta |
| `C6` | `PACKAGE_IDENTITY` | **`FAIL`** | `NAKED_LOCAL_ID` |
| `CTRL-INVALID` | `SEAL_INTEGRITY` | **`INVALID`** | `SEAL_RECORD_UNPARSEABLE` |

**`CTRL-INVALID` é controle do instrumento, não um sétimo defeito.** Existe para provar que
o verificador distingue "não consegui avaliar" de "detectei defeito". Se ele voltar `FAIL`,
o instrumento está colapsando as duas categorias e a rodada é `INVALID`.

### Sobre C5 — três asserções, não uma

1. `local_id` **pode** repetir entre pacotes — isso é legal e não é o defeito;
2. identidade **global nua** tem de **colidir** → `GLOBAL_ID_COLLISION`;
3. identidade **qualificada** tem de permanecer **distinta**.

As três precisam valer. Só (2) é a falha; (1) e (3) são propriedades que o teste prova
junto, e sem elas o canário não provaria o que se propõe.

---

## 5. DETECTAR PELO MOTIVO CERTO

**Não basta o veredito bater.** O runner exige, para cada canário negativo, que o **código
de falha esperado esteja presente** entre os códigos emitidos. Um `FAIL` pelo motivo errado
conta como **resultado inesperado** e derruba a rodada.

É a diferença entre um verificador que funciona e um que reprova tudo.

---

## 6. AS FIXTURES CONTÊM MESMO O DEFEITO? — asserção independente

Antes de rodar o verificador, o runner executa uma **asserção estrutural independente** por
fixture, que confirma que o defeito pretendido está fisicamente presente. Exemplos:

- `C3`: o `members[]` do selo **contém** o nome do próprio selo;
- `C1`: o diretório contém **dois** selos declarando versões diferentes;
- `C4`: o `sha256` de toolchain declarado **difere** do hash real do artefato de toolchain.

**Se a asserção falhar, a fixture não contém o defeito** e a rodada é `INVALID` — não `FAIL`.
Isso impede o modo de falha em que "6 testes passaram" significa apenas que o runner rodou.

---

## 7. ISOLAMENTO

Todas as fixtures são **sintéticas e descartáveis**, geradas por `build_fixtures.py`.
**Nenhuma é mutação de artefato histórico.** Os artefatos que originaram os defeitos —
`compiler-v2`, `compiler-s3`, os manifests do P002, os `EVIDENCE.jsonl` — **não são lidos,
copiados nem tocados** por este piloto.

Não são modificados: Compiler · `compiler-v2-v0.2.2` · `compiler-s3-v0.1.1` · `cts/` ·
runners históricos · `PILOT-001..004` · freezes e manifests históricos · `_mirror/` ·
`N1–N9` · Drive.

---

## 8. CRITÉRIO DE PASS

`PILOT_MS_000A_PASS` **somente se todas** valerem:

1. portão de abertura `PASS`;
2. asserção estrutural confirma o defeito em **cada** fixture negativa;
3. `HAPPY` → `PASS`;
4. `C1`–`C6` → `FAIL`, **cada um com o código esperado presente**;
5. `CTRL-INVALID` → `INVALID`, não `FAIL`;
6. C5: colisão nua **e** distinção qualificada, ambas provadas;
7. **zero resultados inesperados**;
8. nenhum teste passa por ausência de execução — o runner conta execuções e compara com a
   matriz;
9. outputs persistidos, hashes conferem;
10. nenhum artefato histórico modificado; Drive read-only.

Qualquer defeito plantado que **escape** → `PILOT_MS_000A_FAIL`.
Instrumento ou fixture incorretos → `PILOT_MS_000A_INVALID`, e a correção vai para uma
**rodada nova e explicitamente separada**.
