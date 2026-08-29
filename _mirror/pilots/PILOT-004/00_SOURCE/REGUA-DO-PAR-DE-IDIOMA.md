# RÉGUA DO PAR DE IDIOMA — declarada ANTES do PASS 1

PILOT-001-v2 (EN) × PILOT-004 (PT). Registrada em 2026-08-13, com o L0 do P004
já selado (`607f5a98…`) e **nenhum PASS executado**.

Este documento declara **o que se compara e como se mede**. Não prevê valores.
Nenhum número de resultado aparece aqui por escolha: prever seria criar âncora
para reinterpretar o resultado depois.

## Por que este par isola idioma

| | PILOT-001-v2 | PILOT-004 |
|---|---|---|
| extent | 905 s | 903 s |
| idioma | EN | PT (pt-BR) |
| transcrição | — | ASR auto-gerada, faixa única |
| compilador | compiler-v2/0.2.0-frozen | a definir (ver bloqueio do canário) |

**2 segundos de diferença em 905** — 0,22%. É o par de escala mais próximo que
existe no conjunto de pilotos. O P003 (13.857 s) não serve de par: qualquer
diferença ali se confunde com efeito de tamanho de corpus. Com o P001-v2, a
escala está controlada e o idioma é a variável que sobra.

O que **não** está controlado, e precisa ser lido junto: domínio (Google Ads ×
Meta Business Suite), autor, ano, e formato (aula × tutorial de visão geral).
A régua isola idioma **contra escala**, não contra tudo.

## As quatro medidas

### M1 — densidade de evidência por segundo
`evidence.total ÷ extent_s`, nas duas pontas.
Base do P001-v2: 149 ÷ 905. Base do P004: a apurar ÷ 903.
Denominadores praticamente iguais, então a razão entre as densidades é
essencialmente a razão entre as contagens brutas.

### M2 — yield por segmento
`evidence.aggregate_yield_per_segment`, campo já emitido pelo
`COMPILATION_MANIFEST`. P001-v2: 16,5556 sobre 9 segmentos.
Ler **sempre junto com a contagem de segmentos**: a banda de comparabilidade
congelada é **7–11** (`pass1_band_inclusive`). O P001-v2 caiu em 9, dentro da
banda. A estimativa do P004 é 7–10, também dentro. Se o PASS 1 do P004 sair da
banda, o manifesto marca `variance_flag` e **M2 vira diagnóstico, não
comparação** — regra que já vale para o par 4,89 do P001 histórico.

### M3 — cobertura do L0
`coverage_gate.l0_coverage_pct`, métrica `L0_UNION_SPAN_COVERAGE`, piso
congelado 0,735, comparação `strictly_greater`. P001-v2: 90,61%.
Registrar também `rescan_iterations` e `stop_reason`: uma cobertura alta obtida
com revarredura não é o mesmo fenômeno que uma obtida sem
(`THRESHOLD_SATISFIED_WITHOUT_RESCAN`).

Ressalva de método: M3 só é comparável se os dois lados usarem o **mesmo**
`cts/coverage.py`. O módulo é pinado por hash
(`ea58c05e…` no P001-v2). Confirmar o pino antes de comparar — ver
`PENDENCIA-RECONCILIACAO.md`.

### M4 — falhas de medição por idioma
Contagem de ocorrências, com a lista nominal, não só o total.
Referência: **6 ocorrências no PILOT-003** (fonte EN, alvo PT).
No P004 a fonte é PT e o alvo é PT, então não existe travessia de idioma.

Classificar cada ocorrência em uma das três:

- **A — travessia PT×EN**: a evidência atravessou idiomas em algum ponto
  (citação em uma língua, claim em outra; termo traduzido que não confere com a
  fonte). É a classe das 6 do P003. Expectativa estrutural no P004: zero, porque
  não há travessia. Se aparecer, a causa **não** era tradução.
- **B — ASR em português**: erro introduzido pela transcrição automática, não
  por idioma cruzado. Já há caso conhecido no L0 do P004 — "Meta Business
  Suitech" em 0:03 e "Metaed" em 14:56. Contar à parte: é ruído de fonte, e o
  P001-v2 tem o análogo dele em inglês.
- **C — validador de citação**: `CITACAO_NAO_RESOLVE` e afins, emitidos pelo
  `_validate` do `claude_extractor`. Contar por segmento. Esta classe testa se o
  validador de citação, escrito e exercitado em inglês, se comporta igual sobre
  texto português.

## O que decide a hipótese

A hipótese do objetivo secundário é: *as 6 do P003 eram falha de tradução*.

- **Sustentada** se a classe A for zero ou quase, e A+B+C não recolocarem em PT
  um problema equivalente.
- **Refutada** se A+B+C reproduzirem volume comparável às 6. Aí a causa era
  outra — extração, validador, ou ASR — e a troca de idioma não a tocou.

Um total baixo em A **com** total alto em C não sustenta a hipótese: só move o
problema de lugar. Por isso as três classes são contadas separadamente e a lista
nominal é obrigatória.

## Ordem de leitura

M4 primeiro. M1, M2 e M3 medem quanto o pipeline produziu; M4 mede se o que ele
produziu é confiável em português. Densidade alta com M4 alta é pior que
densidade baixa com M4 zero — e é exatamente o cenário que o **C4** do
manifesto (só conselho genérico) não pegaria sozinho.
