# ADR-ACERVO-001 — Canonicidade de `PILOT-003-ACCOUNT-AUDIT.md`

**Status:** ACCEPTED
**Data:** 2026-08-29
**Decisor:** Alexandre Sandra — dono do acervo
**Escopo:** um único artefato, `docs/PILOT-003-ACCOUNT-AUDIT.md`. Nada além dele.
**Natureza:** aditivo. Nenhum artefato preexistente é editado por este ato.

---

## 1. DECISÃO

| conteúdo | tamanho | papel a partir desta decisão |
|---|---|---|
| `3dba046df2179319fc15e38e3005c2848053adfa9bc8e1a8ffe8a9613a993f1e` | 33.479 B | **`CANONICAL_ARTIFACT`** de `PILOT-003-ACCOUNT-AUDIT.md` |
| `08f9acfcd32611e864ad4d77783020a03068362ee0afe6ae584d8bdccf0f1c7d` | 30.984 B | **`PREVIOUS_STATE_SUPERSEDED`** |

`3dba046d…` é o corpo da rodada 3 acrescido de uma nota de correção de **48 linhas /
2.495 bytes** anexada ao topo. `08f9acfc…` é o estado anterior do mesmo arquivo,
preservado como blob histórico versionado.

Ambos permanecem onde estão. Nenhum dos dois é editado, copiado, movido ou apagado por
este ato.

---

## 2. NATUREZA DO ATO

**Esta decisão CRIA a primeira declaração formal de canonicidade para este artefato.**
Não é constatação, não é descoberta, não é confirmação de um estado prévio. Antes deste
documento, o acervo **não continha nenhuma declaração de canonicidade** para este
arquivo — nem em favor de um lado, nem do outro.

O fato que torna isso verdade, recomputado:

1. **Em arquivos versionados**, a única declaração de hash para este artefato estava em
   `_mirror/MIRROR-MANIFEST-N6-20260829.tsv`
   (sha256 `7bdba931244d59720ab9c038513a8abae631a0a8160549b0e904d2f6575544d0`),
   **linha 156**, que declara o lado do Drive com status **`CONFERIR`** — isto é,
   *pendência de conferência*, não canonicidade:
   ```
   docs/PILOT-003-ACCOUNT-AUDIT.md<TAB>30984<TAB>08f9acfc…<TAB>2026-08-13T03:09:19Z<TAB>CONFERIR<TAB>sim<TAB>nao
   ```
   É a única linha `CONFERIR` do manifesto inteiro
   (`awk -F'\t' '$5=="CONFERIR"' … | wc -l` → 1).

2. **Na mensagem do commit `378d764352661eb81ee3c0e6a5d0a52ec4e26332`** — artefato
   versionado e imutável — os **dois** hashes já estavam declarados, com o status que
   esta decisão vem encerrar:
   ```
   docs/PILOT-003-ACCOUNT-AUDIT.md: DIVERGENT_CONTENT - DECISION_REQUIRED.
     drive 08f9acfc...  git 3dba046d...  Nenhum lado alterado.
   ```

Ou seja: existiam **duas** declarações de hash e **zero** declarações de canonicidade.
Uma delas pedia conferência; a outra pedia decisão, explicitamente
(`DECISION_REQUIRED`). Este ADR é essa decisão, tomada agora e não antes.

> **Nota de precisão.** Um relatório de investigação anterior desta mesma frente
> (`ITEM2-CANONICITY-CHECK.md`, §6) afirmou que a linha 156 do manifesto era a **única**
> declaração de hash do acervo para este arquivo. Essa afirmação era incompleta: a
> varredura cobriu arquivos, não mensagens de commit, e por isso não viu a declaração de
> `378d764`. Corrigido acima. A correção **reforça** a conclusão em vez de enfraquecê-la
> — havia mais registro do problema do que se supunha, e ainda assim nenhuma decisão.

---

## 3. BASE DE EVIDÊNCIA

### 3.1 Relatórios de investigação

| relatório | bytes | sha256 |
|---|---|---|
| `ITEM2-DIVERGENCE-REPORT.md` | 23.831 | `d3ce2f0b203800ddca85d1e2ab29c4c41bcb7bb08205c4cb5da7aac609b9e63a` |
| `ITEM2-CANONICITY-CHECK.md` | 22.556 | `0c8f78ba4bf9253cfd37fa60647c7fd51cf2ed06371f0235e25ecd8d57f3aa6e` |

> **GAP DECLARADO.** Os dois relatórios vivem hoje **apenas em `~/n6-passo0/`, fora do
> controle de versão**. Não estão no git, não estão no Drive, não têm cópia redundante.
> Os hashes acima são a única amarra entre esta decisão e a investigação que a
> fundamenta. Se esses arquivos forem perdidos, a evidência de suporte deste ADR fica
> irrecuperável — os fatos permanecem reproduzíveis a partir do git, mas o percurso que
> os estabeleceu, não. Registrar esse gap é parte da decisão; fechá-lo é ato separado e
> não foi tomado aqui.

### 3.2 Os três fatos que sustentam a decisão

**(i) O arquivo do Drive é byte-idêntico a um estado anterior versionado; o do git é o
posterior.**
```
git cat-file blob ed00f8b:_mirror/docs/PILOT-003-ACCOUNT-AUDIT.md | sha256sum
  → 08f9acfcd32611e864ad4d77783020a03068362ee0afe6ae584d8bdccf0f1c7d   (= arquivo do Drive)
git cat-file blob 8becb52:_mirror/docs/PILOT-003-ACCOUNT-AUDIT.md | sha256sum
  → 3dba046df2179319fc15e38e3005c2848053adfa9bc8e1a8ffe8a9613a993f1e   (= arquivo do git)
```
`ed00f8b` CommitDate `2026-08-27T14:42:32-03:00` · `8becb52` CommitDate
`2026-08-27T15:34:10-03:00`. A ordem é provada por igualdade de conteúdo entre blob
versionado e arquivo em disco, não por metadado de tempo.

**(ii) Removendo o bloco de 48 linhas do arquivo do git, o do Drive é reproduzido byte a
byte, com resíduo zero.**
```
sed '7,54d' <git>  | sha256sum → 08f9acfcd32611e864ad4d77783020a03068362ee0afe6ae584d8bdccf0f1c7d
sha256sum <drive>              → 08f9acfcd32611e864ad4d77783020a03068362ee0afe6ae584d8bdccf0f1c7d
bloco: 48 linhas · 2.495 bytes ·  30.984 + 2.495 = 33.479  → resíduo 0
```

**(iii) O arquivo do git é superconjunto estrito do arquivo do Drive.** O Drive não
contém uma única linha ausente do git. A diferença é inteiramente um acréscimo em um
único ponto, no topo.

---

## 4. SOBRE `p003-apply4.md`

`_mirror/pilots/PILOT-003-v2/apply/p003-apply4.md` · 39.667 B ·
sha256 `fb21a9296d0db3cfec05faac5ddfbe092b9c4ca0c0038ec5ac2f27a522263e99` ·
commit `8becb52139a03960b147efc6398e378c1ace2165`, CommitDate `2026-08-27T15:34:10-03:00`.

Registrado **somente o que está provado**: é uma **reanálise posterior** da mesma conta,
que usa a **mesma janela** de dados da conta, incorpora **novos insumos de negócio**,
**troca o KPI para o primário** e **já trabalha com a aritmética corrigida**.

**Este ato NÃO declara que `p003-apply4.md` substitui formalmente
`PILOT-003-ACCOUNT-AUDIT.md`.** A substituição documental **não está provada pelo
acervo**: o candidato não menciona o artefato antigo por nome, caminho ou hash, e nenhum
inventário registra a substituição. Essa é uma **segunda decisão, que não foi tomada
aqui** e permanece em aberto.

---

## 5. RETRATAÇÃO DE MÉTODO

Uma afirmação feita antes nesta mesma frente **estava errada** e é retratada aqui.

**O que se afirmou:** que o `mtime` de um arquivo ser *anterior* ao commit que o versionou
provaria que o `mtime` era inválido.

**Por que está errado:** `mtime` anterior ao commit é **comportamento normal** — escreve-se
o arquivo, commita-se depois. A anterioridade não é anomalia nenhuma e não prova nada
contra o carimbo.

**O que de fato provou a ordem entre as versões:** SHA-256, blob e commit — igualdade de
conteúdo entre o arquivo em disco e um blob versionado identificado, com a data do
commit correspondente. Nenhuma conclusão desta frente dependeu de `mtime`, e nenhuma
muda por causa desta retratação.

**Alcance da desconfiança de `mtime`, corrigido:** ela permanece válida
**especificamente para o lado DrvFs/Drive** — travessia Windows↔WSL, sincronização do
Google Drive e cópia sem preservação de tempo. **Não** vale como regra geral, e em
particular **não** vale contra os carimbos do lado ext4, que são coerentes e utilizáveis.

---

## 6. CLASSE DESTE PRÓPRIO DOCUMENTO

**`GIT_NATIVE_BY_DESIGN`.**

Este ADR nasce no git. **Não tem contraparte no Drive por desenho** — sua ausência lá não
é lacuna de espelhamento, é a forma correta do artefato. **Não deve ser enviado para o
Drive**, e **não pode ser removido por sincronização baseada na origem**: qualquer
processo que trate "ausente no Drive" como "remover do git" destruiria este registro.

A mensagem do commit `378d764` declara **12 arquivos** nessa classe. Com este ADR e a
errata que o acompanha
(`ERRATA-MIRROR-MANIFEST-N6-20260829-AUDIT-PILOT-003.md`), a classe passa de **12 para
14**.

---

## 7. O QUE ESTE ATO NÃO FAZ

- **Não edita** `_mirror/MIRROR-MANIFEST-N6-20260829.tsv` — nem uma linha, nem um espaço.
- **Não edita** nenhum dos dois audits, de nenhum dos dois lados.
- **Não copia** em direção nenhuma: nem git→Drive, nem Drive→git.
- **Não apaga** nada.
- **Não reescreve histórico**: sem amend, rebase, reset, revert ou force-push.
- **Não altera** os defeitos históricos N1..N9, que seguem preservados como estão.
- **Não declara** `p003-apply4.md` substituto formal do audit (§4).
- **Não invalida** o snapshot N6 nem nenhum de seus números.
- **D2 — espelho unidirecional Drive → Git — permanece integralmente válido.**
