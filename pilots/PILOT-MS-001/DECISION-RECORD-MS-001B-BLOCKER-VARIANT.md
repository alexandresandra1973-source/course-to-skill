# DECISION RECORD — `MS_001B_BLOCKER_VARIANT = V1`

**`decision_id`:** `DR-MS-001B-VARIANT-001` · **Data:** 2026-08-30
**Ator:** Design Review externa · **Classe:** `GIT_NATIVE_BY_DESIGN` · **Natureza:** **ADITIVA**

## D1 — A decisão

```
MS_001B_BLOCKER_VARIANT = V1
```

Supersede **somente** a escolha automática de `V2` feita pela regra de seleção da calibração,
**e somente para fins do MS-001B**.

## D2 — O que NÃO é modificado

`BLOCKER-DESIGN-v0.3.json` (`fa62c8159f2cef53ce435d56b3f7f68aedea950acb6ea47822bff8767059cba8`) permanece
**byte-idêntico**. Não mudam: variantes · conceitos · aliases · objetos nomeados · stopwords ·
control mappings · tokenizer · canais de feature · regra de seleção.

## D3 — Base

Ambas as variantes passam `BC1`–`BC5` sob a v0.3 qualificada.

| | V1 | V2 |
|---|---|---|
| pares retidos | **97** | 37 |
| redução | 91,02% | 96,57% |
| cobertura B | **22/30** | 14/30 |
| cobertura C | **16/36** | 9/36 |
| `FEATURE_CHANNEL_LEAK` | ausente | ausente |

> **MS-001B é experimento de descoberta e classificação semântica. Entre variantes já
> qualificadas, prioriza-se recall suficiente antes do juiz semântico. 97 pares ainda reduzem
> 91,02% do universo e permanecem operacionalmente pequenos.**

## D4 — O que esta decisão NÃO afirma

**Não afirma que V1 seja "mais correta semanticamente" que V2.** V1 oferece o trade-off
experimental escolhido: mais recall, mais pares que o juiz provavelmente marcará
`UNRELATED`. Esse custo é aceito deliberadamente.

## D5 — Momento

Tomada **antes de qualquer julgamento semântico real**. Nenhum resultado de relação existia
quando esta decisão foi registrada. Trocar de variante **depois** de ver resultados
semânticos seria `HARD STOP 4`.
