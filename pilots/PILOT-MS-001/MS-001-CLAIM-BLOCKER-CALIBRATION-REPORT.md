# MS-001 — CLAIM BLOCKER CALIBRATION REPORT (v0.1 → v0.3)

*Calibração read-only executada em 2026-08-30. Zero chamadas de modelo, zero embedding,
zero rede. Três versões de desenho, todas preservadas.*

## Classificações históricas

| versão | sha256 | classificação |
|---|---|---|
| **v0.1** | `08e689f826f4b3da854134bad49a5f76d0516855bba663c865c30605f87ea28b` | `NON_QUALIFYING_INTERNAL_FEATURE_CONTRADICTION` |
| **v0.2** | `3add33b38f1017ed3198c041dba06a19acbe47e63a7f4d8418361debbbcfcf30` | `NON_QUALIFYING_DIAGNOSTIC_RECOVERY` |
| **v0.3** | `fa62c8159f2cef53ce435d56b3f7f68aedea950acb6ea47822bff8767059cba8` | **`BLOCKER_FEATURE_MODEL_QUALIFIED`** |

## v0.1 — a contradição interna

Congelada **antes** de qualquer métrica. **Nenhuma variante satisfez; `BC4` falhou em todas.**

Causa medida: `api`, `vps`, `qr` e `n8n` estavam declarados como `NAMED_OBJECTS` congelados
**no mesmo documento** que fixava `min_len = 4`, tornando-os indetectáveis. `V5`, que depende
de `shared_named ≥ 1`, nunca poderia disparar sobre eles. As duas claims do falso conflito —
`CL-0014` (*"chave de API global"*) e `CL-0002` (*"chave de API do Groq"*) — compartilhavam
apenas o token `chave`.

| var | retidos | redução | BC4 |
|---|---|---|---|
| V1 | 56 | 94,81% | **XX** |
| V5 / V2 | 36 | 96,67% | **XX** |
| V3 | 3 | 99,72% | **XX** |
| V4 / V6 | 0 | 100% | **XX** |

## v0.2 — recuperação diagnóstica, com efeito colateral

Única mudança: `min_len` 4 → 2. Recuperou os aliases curtos e **de fato resgatou `BC4`** —
divulgado sem atenuação na época. Mas abriu o canal de content-token para palavras
funcionais: **23 de 39 pares retidos de V3 (59%) dependiam de `em`, `no`, `um`, `não`, `os`**.
`não` escapava porque a stopword list tinha `nao` sem acento e o tokenizador preserva acentos.

## v0.3 — três canais separados

```
texto normalizado → Channel A conceitos → Channel B objetos → Channel C tokens
```

| canal | detecção | `min_len` |
|---|---|---|
| **A** Frozen Concepts | catálogo congelado sobre o texto normalizado | não se aplica |
| **B** Named Objects | catálogo congelado sobre o texto normalizado | não se aplica |
| **C** Content Tokens | tokenizador lexical geral | **4** (restaurado da v0.1) |

Única correção mecânica: chave de comparação de stopword passa a `casefold + accent-insensitive`.
**Lista semântica não redesenhada.** Negação preservada como `qualifier_token` separado,
intacta na Claim.

**Nenhum conceito, alias, objeto, stopword, variante, mapeamento ou regra de seleção foi
acrescentado, removido ou reordenado.** Os `control-mappings` da v0.2 e da v0.3 são
**byte-idênticos** (`231b3801…`) — prova de que não houve remapeamento conveniente.

| var | retidos | redução | cov B | cov C | BC1 | BC2 | BC3 | BC4 | BC5 |
|---|---|---|---|---|---|---|---|---|---|
| **V1** | **97** | **91,02%** | **22/30** | **16/36** | OK | OK | OK | OK | OK |
| V5 | 37 | 96,57% | 14/30 | 9/36 | OK | OK | OK | OK | OK |
| **V2** | **37** | **96,57%** | 14/30 | 9/36 | OK | OK | OK | OK | OK |
| V4 | 14 | 98,70% | 7/30 | 2/36 | OK | XX | OK | XX | OK |
| V3 | 3 | 99,72% | 2/30 | 3/36 | OK | XX | OK | XX | OK |
| V6 | 14 | 98,70% | 7/30 | 2/36 | OK | XX | OK | XX | OK |

**Short-token audit: nenhum token < 4 no Channel C, em nenhum dos 1.080 pares.**
`FEATURE_CHANNEL_LEAK = AUSENTE`. **Functional bridge: 37/37 `CONCEPT_OR_OBJECT_SUPPORTED`,
zero `FUNCTIONAL_OR_LOW_INFORMATION_SUSPECT`** — o problema da v0.2 desapareceu.

`BC4` passa por `api_tool` detectado no **Channel A**, não por `chave` + palavra funcional.

## Divulgação

**As v0.2 e v0.3 foram criadas após observar as versões anteriores.** As três estão
preservadas com suas métricas. A escolha automática da regra de seleção sob v0.3 foi `V2`;
a decisão externa de governança escolheu `V1`, registrada separadamente.

## Classificação

# `BLOCKER_FEATURE_MODEL_QUALIFIED` (v0.3)
