# DECISION RECORD — `MS_000A_ACCEPTED`

**`decision_id`:** `DR-MS-000A-001`
**Decisão:** **`MS_000A_ACCEPTED`**
**Ator:** Design Review externa
**Data:** 2026-08-30
**Base:** `PILOT-MS-000A`, ROUND 3
**Política vigente:** `ARCHITECTURE FREEZE` `6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b`,
selo `f35016cbedf4617a45a4b03a89acefb01495d6d50651b77065b26c7fd901a0c3`
**Classe:** `GIT_NATIVE_BY_DESIGN` · registro **aditivo**; nenhuma rodada é reescrita

---

## 1. AS TRÊS RODADAS, COM ESTATUTO DISTINTO

| rodada | estatuto | evidência |
|---|---|---|
| **ROUND 1** | **`INVALID_FIXTURE`** | `round 1`: `out/RUN-0-INVALID.md`. A fixture `C4` foi construída com `"0"*64` sem aspas; o YAML leu como inteiro. Abortou na asserção estrutural **antes de qualquer veredito** ser observado, gravado ou classificado. **Não é `FAIL` do seal verifier** |
| **ROUND 2** | **`NON_QUALIFYING_FOR_FINAL_ACCEPTANCE`** | executou e devolveu 8/8 esperado, **mas** reutilizou o Opening Record da ROUND 1 e a `C4` plantava um **placeholder**, não o hash de um produtor real. Preservada byte-idêntica, **não promovida** |
| **ROUND 3** | **evidência canônica de aceitação** | `pilots/PILOT-MS-000A/round-3/` · Opening Record próprio `a11fff651aca8797aa39aaca928fa4f06744478fdd29f8501c16979885c3be45` · commit `10ec796e0fad45174e3acde703a91b45c7d20ce2` · **8/8 esperado, 0 inesperado, 0 defeito escapado** |

Nenhuma rodada foi apagada. O índice está em `ROUNDS.md`.

## 2. ESTATUTO DOS CONTRATOS

| contrato | estatuto |
|---|---|
| `SEAL CONTRACT` | **`READY_FOR_EXPERIMENTAL_USE`** |
| `PACKAGE IDENTITY CONTRACT` | **`READY_FOR_EXPERIMENTAL_USE`** |
| qualquer componente | **NENHUM autorizado para produção** |

## 3. O QUE O MS-000A PROVOU

As sete condições de `SEALED` **detectam** os defeitos estruturais que este projeto mediu:
diretório mutável compartilhado · selo que não valida no lugar · auto-referência ·
divergência de identidade de produtor — esta última com **duas identidades reais e
divergentes**, não placeholder. A identidade cross-package **rejeita `local_id` nu** e
**mantém qualificação distinta sob colisão**. O verificador **aceita** o caminho feliz e
**distingue `INVALID` de `FAIL`**.

## 4. O QUE O MS-000A **NÃO** PROVOU — limites explícitos

- **Nada semântico.** Nenhuma claim gerada, comparada ou fundida.
- **Nenhum Source Package real** foi selado — os verificadores rodaram sobre **fixtures
  sintéticas**, não sobre corpus.
- **`I1–I30` seguem sem verificadores implementados.** Só as famílias exercitadas por
  C1–C6 têm instrumento; os demais invariantes continuam intenção, não predicado rodando.
- **Nada medido** sobre custo, blocagem, `ENTAILED_BY`, preservação de workflow, variância
  de geração ou isolamento entre fontes.
- **Nenhuma autorização de produção** decorre daqui.

## 5. SUPERSESSÃO

Registro **aditivo**. Não supera nem altera nenhum record anterior. Alteração futura só por
novo registro com cadeia de supersessão explícita.
