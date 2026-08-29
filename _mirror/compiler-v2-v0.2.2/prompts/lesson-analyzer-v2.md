# lesson-analyzer v2 — DELTA sobre o release v0.1.1

**Base:** `course-to-skill-compiler-v0.1.1-pilot-ready/prompts/lesson-analyzer.md`
sha256 `d6205a8870044453d1c0354a927234f33937c0a4ada0e76868ac50754c87edbf` (1888 linhas).

**Autoridade da mudança:** ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE,
sha256 `b8cddc93b74a65d6cbc2ad6859e4e3b8a4a81404137d4f95260f1b92668cf3f8`.

Este arquivo é **delta**, não cópia. O original não foi tocado — ele vive em
árvore READ-ONLY. Tudo o que não aparece aqui permanece exatamente como no
v0.1.1, incluindo PASS 0 e PASS 3 a PASS 10.

---

## O que NÃO muda

O **PASS 1 permanece literalmente igual**. A medição do PASS 1 (9 segmentos em
905s no PILOT-001, 41 em 4.384s no PILOT-002 — 100,6 e 106,9 segundos por
segmento) mostrou que ele já escala com a duração da fonte sem ter regra de
proporcionalidade. Mexer nele seria consertar o que não está quebrado e
destruir a comparabilidade entre os dois pilotos.

Texto preservado, sem uma vírgula de diferença:

> Divida a aula em segmentos semânticos.
> (…exemplo de SEG-001 a SEG-005…)
> Não segmentar apenas por tempo.

O exemplo de cinco segmentos permanece **exemplo de formato**. Ele nunca foi, e
continua não sendo, alvo de contagem.

---

## Mudança 1 — PASS 2 passa a ser invocado POR SEGMENTO

**Texto v0.1.1 (linha 390):**

> Percorra cada segmento e extraia **unidades atômicas**.

**Defeito:** a frase descreve um percurso, mas a invocação era única sobre a
aula inteira. Com um orçamento de saída global, todos os segmentos competem
pelo mesmo total, e a densidade por segmento cai na proporção inversa do
tamanho da fonte. Foi o que aconteceu: 4,89 evidências/segmento no PILOT-001
contra 1,07 no PILOT-002, com o total travado em 44 nos dois.

**Texto v2, que substitui a linha 390:**

> Você está extraindo de **UM único segmento**, identificado no cabeçalho desta
> chamada. O escopo desta invocação é apenas o intervalo desse segmento.
>
> Extraia dele **todas** as unidades atômicas que a fonte sustenta, até
> **exaurir o segmento** sob as regras de atomicidade abaixo.
>
> Não racione. Não distribua esforço pensando em outros segmentos: você não os
> verá nesta chamada e eles não competem com este.
>
> Se o segmento não contiver metodologia extraível, devolva **zero** unidades.
> Zero é uma resposta válida e será registrada como tal. **Não invente unidade
> para preencher espaço.**

### Regras de escopo desta chamada

- Extraia somente do intervalo `[start, end]` deste segmento.
- Os IDs dos segmentos vizinhos são informados **apenas** para você saber onde
  seu escopo termina. Não extraia deles.
- **Não numere as evidências.** O ID é atribuído pelo compilador, com um
  alocador global. Numerar aqui quebraria a unicidade entre chamadas.

### O que continua valendo do v0.1.1

Categorias, regra de atomicidade (com o exemplo `EV-0007` ruim contra
`EV-0007…EV-0011` bom) e a pergunta obrigatória "Consigo apontar exatamente
onde isso aparece?" — todos preservados sem alteração.

---

## Mudança 2 — novo passe de cobertura e saturação

O v0.1.1 tem **zero** ocorrências de cobertura, saturação, revarredura ou
completude em suas 1888 linhas. Não havia critério de parada: a extração
terminava quando o modelo parava, e nada media se a fonte tinha sido esgotada.

**Novo passe, inserido entre o PASS 2 e o PASS 3:**

> ### PASS 2.5 — PORTÃO DE COBERTURA E SATURAÇÃO
>
> Depois que **todos** os segmentos completarem o PASS 2:
>
> 1. calcule a cobertura de L0 pela união dos spans citados;
> 2. compare com o piso de aceitação **congelado antes da execução**;
> 3. se a cobertura não superar o piso, identifique os blocos descobertos;
> 4. revarra **apenas os segmentos que tocam esses blocos** — nunca a aula toda;
> 5. recalcule e repita até satisfazer o piso ou atingir a condição de parada.
>
> A revarredura é **dirigida**. Revarrer tudo reintroduziria a varredura
> monolítica que a Mudança 1 acabou de remover.

O piso, o número máximo de iterações e a condição de parada por progresso zero
não são escolhas do modelo: vivem em `ctsc2/thresholds.py`, congelados.

---

## Mudança 3 — artefatos obrigatórios

- `temporal-map.yaml` passa a ser **obrigatório**, persistido e hasheado
  **antes** do PASS 2. A dependência é estrutural no código: `run_pass2()` exige
  o handle do mapa em disco e não há caminho que permita extrair sem ele.
- O `COMPILATION_MANIFEST` passa a registrar contagem de segmentos, yield por
  segmento (**inclusive zero**), cobertura, limiar, resultado do portão e
  iterações de revarredura.

---

## Proibições que este delta carrega

Nenhuma das mudanças acima introduz, e o compilador v2 recusa-se a ter:

- alvo de contagem total de evidências — nem 44, nem 200;
- mínimo de evidências por segmento;
- cota de densidade;
- geração proporcional ao tempo decorrido.

O número aproximado de **200** que aparece na ADR é **diagnóstico**: é o que a
densidade do PILOT-001 daria se aplicada aos 41 segmentos do PILOT-002. Ele
mede o tamanho do buraco. Ele **nunca** é meta.

> A invariante é: o esforço de extração acompanha o conteúdo semântico, e a
> conclusão é julgada por cobertura, não por um total de saída globalmente
> limitado.

Um segmento curto e denso pode legitimamente render mais que um segmento longo
e repetitivo. É por isso que o piso é de cobertura e não de contagem.
