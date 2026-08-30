# `MS_001A_INSTRUMENT_INVALID` — execução 1 do PILOT-MS-001A

**Data:** 2026-08-30 · Opening Record vigente
`6085247024692705032c7e97f697f5658597e1a8997976ec8167187de5e924f7`,
pushed em `6c01ff5fcf9ab52c65d09bc0fac57cd8d8653fc4` **antes** da primeira chamada.

Classificação pelo §12 do próprio Opening Record e pelos §15/§16 do bloco de execução:
**persistir a execução inválida e PARAR. Zero retry.**

## 1. Chamadas executadas

| call | papel | rótulo | resultado |
|---|---|---|---|
| 1 | `EXTRACTOR_CONTROL` | `EC` | **PASS 6/6** |
| 2 | `ENTAILMENT_CONTROL` | `JE` | **FALHA** |

**2 de 10** chamadas do cap consumidas. As oito restantes **não** foram queimadas — o
Opening Record autoriza término antecipado sem gastar o resto.

`resolved_model = claude-opus-5`, igual ao `model_requested`. A verificação de resolução,
que era função da call 1, **passou**.

## 2. Call 1 — `EC1`–`EC6` PASS

| controle | resultado |
|---|---|
| `EC1` claim suportada com `evidence_ref` correta | **OK** |
| `EC2` **armadilha** recusada — *"a VPS da HostGator é a mais rápida do mercado"* não foi emitida | **OK** |
| `EC3` candidate com provenance não vazia | **OK** |
| `EC4` `claim_temp_ref` resolvendo no mesmo bundle | **OK** |
| `EC5` nenhum candidate derivado do trecho factual não-operacional | **OK** |
| `EC6` qualificador *"para quem está começando"* preservado | **OK** |

Schema estrito: **zero erros**. O extractor se comportou como o instrumento exige.

## 3. Call 2 — dois defeitos, ambos MEUS

### Defeito 1 — o prompt e o schema do juiz **discordam entre si**

`ENTAILMENT-PROMPT-v1.txt` manda o modelo emitir:

```json
{"verdicts":[{"temporary_claim_id":"TC-nnn","state":"...","why":"..."}]}
```

`ENTAILMENT-SCHEMA-v2.json` exige:

```
required: ["claim_id", "judgment", "entail_why", "evidence_refs_checked"]
```

O modelo emitiu `["state","temporary_claim_id","why"]` — **exatamente o que o prompt pediu**.
Escrevi o prompt na v1 e o schema na v2 e **não reconciliei os dois**. O `evidence_refs_checked`,
que existe justamente para provar que o juiz não acrescenta Evidence, **o prompt nunca pediu**.

Defeito de instrumento. O modelo obedeceu.

### Defeito 2 — o fixture `JE4` é ambíguo sob as minhas próprias regras

| claim | esperado | obtido |
|---|---|---|
| `CL-9001` | `ENTAILED` | `ENTAILED` ✔ |
| `CL-9002` | `NOT_ENTAILED` | `NOT_ENTAILED` ✔ |
| `CL-9003` | `NOT_ENTAILED` | `NOT_ENTAILED` ✔ |
| `CL-9004` | `INDETERMINATE` | **`NOT_ENTAILED`** ✘ |

Razão dada pelo juiz:

> *"A evidence apenas descreve o passo de voltar ao painel e verificar o resultado, sem
> qualquer informação de duração que sustente 'menos de um minuto'."*

A regra 3 do meu próprio prompt diz: *"Se a evidence citada não trata do assunto da claim, é
`NOT_ENTAILED`, não `INDETERMINATE`."* No `JE4` a evidence **trata do assunto** (verificar o
resultado) mas **não trata do atributo** (duração). Minha regra não distingue esses dois casos,
e a leitura do juiz é defensável sob o texto que eu mesmo escrevi.

**O fixture não isola a fronteira que pretendia isolar.** `JE4` existia para provar
`NOT_ENTAILED ≠ INDETERMINATE`; do jeito que está, ele testa uma fronteira que o prompt não
define.

## 4. O que isto NÃO é

**Não é falha do modelo.** Três de quatro vereditos batem, e o quarto é justificado por uma
regra minha que é omissa. O extractor passou nos seis controles, incluindo a armadilha.

**Não é falha do produto.** Nenhum Source Package foi montado. Nenhuma Claim real gerada.
O corpus congelado permanece byte-idêntico.

## 5. Orçamento

`executed_calls = 2` · `HARD_CAP = 10` · `RETRY = 0`.

Uma execução corrigida precisaria de **10 chamadas próprias**, o que somaria **12** contra um
cap declarado de **10**. Não gasto isso por conta própria: o cap é do Opening Record, e
estourá-lo silenciosamente seria pior do que o defeito que o causou.

## 6. O que precisa ser corrigido antes de uma execução 2

1. **Reconciliar `ENTAILMENT-PROMPT` e `ENTAILMENT-SCHEMA`** numa única forma, incluindo
   `evidence_refs_checked` no que o prompt pede.
2. **Reescrever `JE4`**, ou acrescentar ao prompt a regra que hoje falta: distinguir
   *evidence fora do assunto* de *evidence dentro do assunto mas silenciosa sobre o atributo
   afirmado*. A segunda é o caso `INDETERMINATE` que eu queria testar.
3. **Novo Opening Record ou adendo selado**, porque ambos os artefatos estão hasheados no
   Opening Record atual, e alterá-los sem registro é exatamente o `INVALID` que ele prevê.
4. **Autorização explícita de orçamento** para as chamadas da execução 2.

## 7. Classificação

# `MS_001A_INSTRUMENT_INVALID`

Execução 1 encerrada. Raw de ambas as chamadas preservado em `out/raw/`. Nada apagado.
