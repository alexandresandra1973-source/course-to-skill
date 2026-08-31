# DECISION RECORD — INDEPENDÊNCIA DAS FONTES A / B / C

`decision_id`: **`DR-MS-002-INDEP-001`** · Data: 2026-08-31 · Natureza: **ADITIVA**
Escopo: **PILOT-MS-002** e **somente** os artefatos congelados pelos hashes abaixo.

## 1. Classificação

| par | classificação |
|---|---|
| `MS002-SRC-A` × `MS002-SRC-B` | **`DECLARED_INDEPENDENT`** |
| `MS002-SRC-A` × `MS002-SRC-C` | **`DECLARED_INDEPENDENT`** |
| `MS002-SRC-B` × `MS002-SRC-C` | **`DECLARED_INDEPENDENT`** |

Não se declara independência metafísica. `DECLARED_INDEPENDENT` significa: nenhuma
evidência de dependência foi encontrada nos sinais mecanicamente mensuráveis abaixo, e a
declaração está atada a estes bytes.

## 2. Artefatos atados

| `source_id` | `SOURCE_CONTENT_HASH` |
|---|---|
| `MS002-SRC-A` | `2880a4c3996f5abcddbe81a3c8cdf9fee3d57bf30c6f1baeb283b2246a98367e` |
| `MS002-SRC-B` | `2a6ab098868e0714e5d4bc5cebb8018216d78f0243ee890b2c531516fbda7862` |
| `MS002-SRC-C` | `ed967fae27146d9aa9cc45769672f751d8eb199bc6ed7564bbb5fdb4a226fab7` |

Se um artefato mudar de hash, esta declaração **não** se transfere: exige nova auditoria.

Os hashes de B e C são **byte-idênticos** aos congelados em `DR-MS-001-INDEP-001`, de modo
que a base de evidência daquela decisão se aplica sem reaquisição. A decisão, porém, é
nova: a anterior tinha escopo explicitamente restrito ao PILOT-MS-001.

## 3. Base registrada — medida mecanicamente, sem chamada de modelo

| sinal | A | B | C |
|---|---|---|---|
| autor / canal | Nick Saraev | Anderson Adelino \| IA e Automações | Guilherme Lazarotto |
| `channel_id` | `UCbo-KbSjJDG6JWQ_MTZ_rNA` | `UCI5WcISxqiFfoh4mse1s-HA` | `UCO0x-39c7EttOhmFAsngfgg` |
| `video_id` | `yulWjh3rq28` | `dtAoZYMEzcM` | `NvrBpnbNfv4` |
| publicação | 2026-08-08 | 2026-06-24 | 2025-02-19 |
| idioma | en | pt | pt |
| duração | 6,05 h | 17,6 min | 13,7 min |

Três autores distintos, três canais distintos, três datas distintas, dois idiomas.
A antecede B em 45 dias; C antecede ambos em mais de 16 meses.

### Cross-references — verificação mecânica

Busca literal, no texto de cada fonte, por marcas de autoria e produto das outras duas
(`nick saraev`, `saraev`, `leftclick`, `anderson adelino`, `zenithon`,
`guilherme lazarotto`, `lazarotto`, `n8n fácil`):

    A menciona marcas de B: NENHUMA      A menciona marcas de C: NENHUMA
    B menciona marcas de A: NENHUMA      B menciona marcas de C: NENHUMA
    C menciona marcas de A: NENHUMA      C menciona marcas de B: NENHUMA

Nenhuma fonte cita, credita ou referencia qualquer das outras.

### Vocabulário compartilhado — sinal de assunto, não de dependência

| termo | A | B | C |
|---|---|---|---|
| claude code | sim | não* | não |
| evolution api | não | sim | sim |
| whatsapp | sim | sim | sim |
| n8n | não | não | sim |
| redis | não | não | sim |
| instagram | sim | não | não |

\* O ASR de B transcreve "Claude Code" como **"Cloud Code"**. O termo está presente no
conteúdo, ausente do texto literal. Isto é um defeito de ASR **preservado**, não corrigido,
e é registrado aqui porque afeta qualquer canal lexical construído sobre o texto de B.

B e C compartilham "Evolution API" e "WhatsApp"; as três compartilham "WhatsApp". Isso é
sobreposição de **assunto**, não evidência de dependência editorial.

## 4. O que NÃO foi verificado

Não foi possível verificar mecanicamente: se algum autor assistiu ao material de outro sem
creditar; dependência via terceiros (documentação da Evolution API, cursos intermediários);
material compartilhado fora do texto (código, imagens, slides). Essas vias permanecem
**abertas** e são a razão de a classificação ser `DECLARED_INDEPENDENT` — declarada sobre
evidência registrada — e não uma alegação de independência absoluta.

## 5. Condição de morte

    K11 — reaquisição que produza bytes diferentes invalida esta declaração.
