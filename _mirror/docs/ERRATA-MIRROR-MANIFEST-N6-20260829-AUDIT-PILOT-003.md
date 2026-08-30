# ERRATA ADITIVA — `MIRROR-MANIFEST-N6-20260829.tsv`, linha do audit do PILOT-003

**Data:** 2026-08-29
**Tipo:** aditivo. **A linha original NÃO deve ser editada e NÃO foi editada.**
**Alcance:** um único registro do manifesto. Nada mais.

---

## 1. ALVO

**Arquivo:** `_mirror/MIRROR-MANIFEST-N6-20260829.tsv`
**sha256 do manifesto (recomputado):**
`7bdba931244d59720ab9c038513a8abae631a0a8160549b0e904d2f6575544d0`
**Linha:** **156** — conferida por `grep -n 'PILOT-003-ACCOUNT-AUDIT'`, que devolve
exatamente esta e nenhuma outra.

Conteúdo da linha 156, verbatim (separadores TAB):

```
docs/PILOT-003-ACCOUNT-AUDIT.md	30984	08f9acfcd32611e864ad4d77783020a03068362ee0afe6ae584d8bdccf0f1c7d	2026-08-13T03:09:19Z	CONFERIR	sim	nao
```

| campo | valor |
|---|---|
| caminho (relativo à base do manifesto) | `docs/PILOT-003-ACCOUNT-AUDIT.md` |
| bytes | `30984` |
| sha256 | `08f9acfcd32611e864ad4d77783020a03068362ee0afe6ae584d8bdccf0f1c7d` |
| mtime_utc | `2026-08-13T03:09:19Z` |
| classificação | `CONFERIR` |

É a **única** linha com classificação `CONFERIR` em todo o manifesto
(`awk -F'\t' '$5=="CONFERIR"' … | wc -l` → 1).

---

## 2. O MANIFESTO ESTÁ CERTO

**O manifesto N6 registrou corretamente o estado observado no momento do inventário.**
O arquivo que existia no Drive naquele instante tinha, de fato, 30.984 bytes e sha256
`08f9acfc…`. Isso continua verdadeiro hoje: o arquivo do Drive segue com exatamente
esses valores, inalterado.

O manifesto também **não errou ao classificar**: `CONFERIR` significa pendência de
conferência, e havia pendência real. A classificação estava correta, e o instrumento
funcionou — foi ele que isolou este arquivo como o único ponto de divergência do acervo.

**Nada nesta errata corrige o manifesto, porque não há nada a corrigir nele.**

---

## 3. O QUE MUDOU DEPOIS

Investigação posterior estabeleceu que o conteúdo `08f9acfc…` (30.984 B) é
byte-idêntico a um estado anterior versionado do mesmo arquivo, e que o conteúdo
`3dba046d…` (33.479 B) é o estado posterior, superconjunto estrito do primeiro.

Com base nisso, uma **decisão do dono do acervo** promoveu:

| conteúdo | tamanho | papel |
|---|---|---|
| `3dba046df2179319fc15e38e3005c2848053adfa9bc8e1a8ffe8a9613a993f1e` | 33.479 B | **`CANONICAL_ARTIFACT`** |
| `08f9acfcd32611e864ad4d77783020a03068362ee0afe6ae584d8bdccf0f1c7d` | 30.984 B | **`PREVIOUS_STATE_SUPERSEDED`** — preservado, não descartado |

O conteúdo declarado na linha 156 **permanece preservado**. Ele não é lixo, não é erro e
não é candidato a remoção: é o estado anterior do artefato, guardado como tal.

---

## 4. O QUE ESTA ERRATA NÃO FAZ

**Isto NÃO invalida o snapshot N6 nem nenhum de seus números.**

- Nenhuma linha do manifesto é editada, removida ou reordenada.
- O sha256 do manifesto permanece
  `7bdba931244d59720ab9c038513a8abae631a0a8160549b0e904d2f6575544d0`.
- Nenhum dos dois audits é editado, copiado, movido ou apagado.
- Nada é escrito no Drive.
- Os demais registros do manifesto seguem válidos e não são tocados.

A errata é **leitura adicional** sobre um registro que continua verdadeiro — não uma
retificação dele.

---

## 5. PONTEIRO PARA A DECISÃO

A decisão que esta errata acompanha está registrada em:

**`_mirror/docs/ADR-ACERVO-001-CANONICIDADE-PILOT-003-ACCOUNT-AUDIT.md`**
sha256 `c5b63d02ce8d18e2fdd6601a5a20a8bfe17d3e06776aa509018ae1265561e1e8`

O ADR contém a decisão completa, a base de evidência com hashes, o registro explícito de
que o ato **cria** a primeira declaração formal de canonicidade para este artefato, e o
que o ato deliberadamente **não** decide.

---

**Classe deste documento:** `GIT_NATIVE_BY_DESIGN` — nasce no git, não tem contraparte no
Drive por desenho, não deve ser enviado para lá, e não pode ser removido por
sincronização baseada na origem.
