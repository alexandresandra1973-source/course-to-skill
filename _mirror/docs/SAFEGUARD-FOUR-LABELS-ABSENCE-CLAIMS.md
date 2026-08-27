# SALVAGUARDA — quatro etiquetas, em ordem, antes de alegar ausência

**Status:** REGRA_ATIVA · 2026-08-12 · obrigatória para todo COURSE-GAP-REPORT

## Por que existe

A saída principal do produto — *"o curso não cobre X"* — tem exatamente a mesma
forma quando o medidor está quebrado. Sete versões de um medidor de temas
produziram achados falsos com essa cara. Quem lê o relatório não tem como
separar. A salvaguarda é o que permite separar.

## As quatro etiquetas, NESTA ordem

**1. LACUNA_DE_MEDICAO** — buscar o termo NAS EVIDÊNCIAS, por token, **sem
exigir ordem nem adjacência**. Se aparecer, o defeito é do medidor. Nem do curso,
nem da extração. **Esta checagem vem primeiro e é a que faltava.**

**2. LACUNA_DE_EXTRACAO** — termo aparece MUITAS vezes em L0 (> 20) e não
aparece nas evidências. Defeito NOSSO. Reportar como tal, nunca como avaliação
do curso.

**3. COBERTURA_RASA_DO_CURSO** — termo aparece POUCAS vezes em L0 (<= 20) e a
extração acompanhou. **Único achado que pode ser dito como avaliação do curso.**

**4. BUSCA_INVALIDA_POR_IDIOMA** — nenhum token do tema aparece no L0. Os temas
saem do PASS 1 em português e o L0 é inglês: zero aqui não distingue ausência de
tradução. NÃO é alegação sobre o curso.

## O caso que obrigou a acrescentar a etiqueta 1

`youtube instream`: 30 ocorrências em L0, 0 "menções" segundo o medidor de temas.
A salvaguarda de três etiquetas rotulou **LACUNA_DE_EXTRACAO** — defeito nosso.

Falso. O diagnóstico encontrou **39 evidências citando `instream`**, com conteúdo
denso: *"Anúncios instream garantem um tempo forçado de visualização de 5
segundos"*, *"o instream é escalado para 8.000, 12.000 e 16.000 dólares por
dia"*. O tema tinha cobertura excelente.

A causa: o medidor procurava o bigrama adjacente `youtube instream`, e as claims
dizem *"anúncio instream do YouTube"* — as duas palavras existem, fora de ordem
e não adjacentes.

Sem a etiqueta 1, o relatório teria dito "a extração falhou no YouTube" e alguém
teria ido consertar uma extração que funciona.

## Efeito da etiqueta 1 no PILOT-003

Aplicada aos sete temas suspeitos, **cinco mudaram de veredito**:

| tema | L0 | evidências | antes | depois |
|---|---|---|---|---|
| kpi view | 36 | 47 | rasa | **LACUNA_DE_MEDICAO** |
| youtube instream | 30 | 39 | extração | **LACUNA_DE_MEDICAO** |
| cpc manual | 21 | 26 | rasa | **LACUNA_DE_MEDICAO** |
| com conversão | 31 | 25 | rasa | **LACUNA_DE_MEDICAO** |
| setup técnico | 19 | 22 | rasa | **LACUNA_DE_MEDICAO** |
| caso 45k | 1 | 1 | rasa | cobertura rasa |
| **negative keyword** | **3** | **2** | rasa | **cobertura rasa** |

## O único achado sobrevivente, e por que ele é confiável

**`negative keyword`: 3 ocorrências em 3h50m de curso de Google Ads.**

Ele sobreviveu por uma razão ESTRUTURAL, e ela tem de estar escrita ao lado do
achado sempre que ele for citado:

> **Termo inglês buscado em texto inglês, sem tradução e sem reordenação no
> caminho.** Não passou por PASS 1 (que traduz), não virou bigrama adjacente, não
> dependeu de acento. As sete falhas de medição vieram todas de tradução, ordem
> ou diacrítico. Este achado não toca nenhuma das três.

Nenhum achado de ausência entra num relatório sem essa cadeia explícita: qual
transformação ele atravessou, e por que ela não podia quebrá-lo.
