# T7 — BLOCO 3 · compilação evidência→Skill

Compilador: **compiler-s3/0.1.0**, congelado no T6
(`FREEZE-RECORD-s3-v0.1.0.yaml`, inventário `115a3773…`).
13 chamadas, uma por segmento. Nenhum arquivo do compiler-s3 foi editado.

## Pré-classificação — rodou ANTES de qualquer regra

| classe | n | é conteúdo do curso? |
|---|---|---|
| SOURCE_EXPLICIT | 119 | sim |
| GENUINE_INFERENCE | 9 | **não** |
| TRANSCRIPTION_CORRECTION | 6 | sim |

Os 6 `TRANSCRIPTION_CORRECTION` só existem porque os alias do domínio foram
declarados. Sem eles, seriam contados contra o curso.

### Vocabulário central conferido no ASR

| termo | corretas | corrompidas | total | % corrompido |
|---|---|---|---|---|
| **Meta Business Suite** | 1 | 13 | 14 | **92,9%** |
| Meta Ads | 0 | 1 | 1 | 100% |

Formas encontradas: `Metabusiness` ×4, `Metabus` ×3, `Suitch` ×2,
`Meta Business Suitech`, `Metabusness`, `suitch`, `MetaS`, `Metaed`.

92,9% põe o P004 na mesma faixa dos anteriores: **P002 91,1%** (Claude),
**P003 91,7%** (ROAS). O ASR corrompe o nome do produto central em ~9 de cada 10
menções, em três pilotos seguidos, em dois idiomas.

Alias declarados para o P004, em memória — `classify.py` permanece byte-idêntico:

```
"Meta Business Suite" -> \b(metabus\w*|metas|suitch|suitech)\b
"Meta Ads"            -> \b(metaed|metaeds)\b
```

O nome do produto não é o único corrompido. O controle por token achou mais dois,
em nomes de funcionalidade: **`insights` → "insightes"/"insites"** e
**`reels` → "reals"**.

### Caminho P4 — INDISPONÍVEL, declarado

`PARAPHRASE` não foi medido. Veio o `distance-lines-PILOT-003-v2.json`, não o do
P004 nem o gerador. Reusá-lo classificaria evidência do P004 pela distância
medida de **outra** evidência do P003 — os `evidence_id` colidem entre pilotos.
Rodou com `paraphrase_ids` vazio. É limitação de insumo, não medição — e aparece
no GAP-REPORT como `distância: (não medida)` em cada entrada.

## Resultado da compilação

| | |
|---|---|
| regras | 32 |
| passos | 44 |
| workflows | 12 |
| **evidências consumidas** | **112 de 134** |
| **C1 — cobertura evidência→regra** | **83,58%** · limiar >80% · **PASSA** |
| evidências sem disposição | 0 |
| regras só de inferência genuína | 2 (+2 passos) |
| erros de validação / roteador | 0 / 0 |
| template fail-closed byte-a-byte | **true** |

Disposições: `CONSUMED_BY_RULE` 63 · `CONSUMED_BY_STEP` 49 ·
`NON_METHODOLOGICAL` 20 · `GAP` 2.

`UNDEFINED`: `autonomy` 76 · `iteration_limit` 76 · `missing_input_action` 76 ·
`precedence` 31.

## Controle positivo por token, e a separação que ele permite

A pergunta que o controle responde: quando o relatório diz "o curso não ensinou
X", isso é lacuna do curso ou perda do nosso pipeline?

| veredito | regra |
|---|---|
| COBERTO | token no L0 e na Skill |
| **LACUNA NOSSA** | token no L0, **fora** da Skill — o curso ensinou, o pipeline perdeu |
| CORREÇÃO DE ASR | token fora do L0, na Skill, com variante corrompida no L0 |
| **INVENÇÃO** | token fora do L0, na Skill, **sem** variante que o explique |
| LACUNA DO CURSO | token fora do L0 e fora da Skill |

Resultado com 17 tokens positivos (ensinados na fonte) e 12 negativos (conceitos
reais do Business Suite ausentes deste vídeo):

- **controle positivo: 16/17 = 94,1%** — o controle tem poder. Se o grupo
  positivo não aparecesse, o relatório estaria medindo perda do pipeline e
  chamando de lacuna do curso.
- **controle negativo: 12/12 ausentes dos dois lados · INVENÇÕES: nenhuma.**
  Nada de `lookalike`, `CBO`, `API de conversões`, `teste A/B`, `catálogo`,
  `atribuição` entrou na Skill.
- **LACUNA NOSSA: nenhuma real.** O único token marcado, `stories`, é artefato
  da forma que escolhi: a fonte diz "story" no singular e a Skill traz "story"
  3 vezes. Registrado como falso positivo do meu teste, não como perda.

## Uma lacuna NOSSA que o controle por token não pegaria — e a Skill pegou sozinha

O `knowledge/runtime-policy.yaml` emitido referencia três coisas que **não
existem** no pacote:

- `knowledge/questions.yaml` (linha 46) — arquivo não emitido
- `Q-0001` (linhas 36 e 39) — `required_question_id` sem destino
- `ADR-0004` (linha 49) — `decision_rule_id` ausente do `decision-rules.yaml`

Efeito prático: dois guards (`RG-013-002` outcome-before-routing e `RG-013-003`
build-contract) mandam **fazer uma pergunta canônica** e o enunciado dela não
existe no runtime. O guard para corretamente, mas não consegue emitir a pergunta
que ele próprio prescreve.

**O `PILOT-003-v2` tem exatamente o mesmo defeito** — mesma referência no
`runtime-policy.yaml`, mesmo `knowledge/` sem `questions.yaml`. É defeito do
compiler-s3, herdado da política canônica, não do PILOT-004. **PENDENTE-ALEXANDRE.**

## Material para o C2

O C2 pede que o GAP-REPORT diga algo **específico e verdadeiro** sobre ESTE
tutorial — não uma lacuna genérica que valeria para qualquer vídeo de Business
Suite. Candidatos, todos verificáveis contra o L0:

1. **A fonte manda seguir "a trilha do modelo de negócio" e não define nenhuma
   trilha.** R-0026 nomeia três (negócio local, venda no X1 por mensagem, venda
   direta infoprodutor/afiliado) e o curso não ensina nenhuma — 11:09–11:17 é
   uma menção de passagem dentro da propaganda do treinamento pago.
2. **O WhatsApp aparece na caixa de entrada unificada sem nunca ser conectado.**
   O runtime tem S-0041 (verificar perfis conectados) e S-0021 (responder
   WhatsApp na caixa unificada), e nenhum passo de **como** conectar.
3. **O pixel é localizado e explicitamente não tratado** (R-0030, S-0043).
4. **Criar página e criar conta de anúncio são remetidos para fora** (S-0044,
   "continuar estudando os conteúdos do canal") — dois pré-requisitos que o
   próprio tutorial declara necessários e não ensina.
5. **`autonomy: UNDEFINED` em 100% das regras e passos** — nada neste curso
   autoriza execução autônoma.

Os cinco são específicos deste vídeo e conferíveis por timestamp. A avaliação
formal do C2 fica com o Alexandre.

## Limitação declarada — checkpoint

O T7 pedia checkpoint incremental. O `run_compile.py` congelado grava o rastro só
no fim, e não tem ramo de retomada. Rodei o original sem modificar: fidelidade ao
compilador recém-congelado vale mais aqui, e o risco é baixo — 13 chamadas em
211s, com 36 chamadas de folga no teto para refazer inteiro se caísse. Não caiu.
