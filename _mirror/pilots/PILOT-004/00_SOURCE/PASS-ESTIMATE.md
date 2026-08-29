# PILOT-004 — estimativa de segmentos e chamadas (antes do PASS 1)

Base: números **reais** do PILOT-003, escalados para o extent do PILOT-004.
Nenhum PASS foi executado.

| | PILOT-003 (real) | PILOT-004 (estimado) |
|---|---|---|
| extent | 13.857 s (3:50:57) | 903 s (15:03) |
| chars brutos | 334.303 | 16.383 |
| janelas do PASS 1 | 12 | **1** |
| s por janela | 1.155 | 903 (cabe em uma) |
| `target_segment_s` | 135 | 135 (mesmo parâmetro) |
| segmentos | 148 (média real 93,6 s) | **7 a 10** |
| invocações do PASS 2 | 148 (1 por segmento) | **7 a 10** |
| evidências | 2.463 (16,64/segmento) | **60 a 165** (ver ressalva) |

**Total de chamadas estimado para PASS 1 + PASS 2: 8 a 11.**
No PILOT-003 foram 160 (12 + 148). Cerca de 1/15 do custo.

## Como cada número foi obtido

- **Janelas do PASS 1:** 13857 ÷ 12 = 1154,75 s por janela no P003. 903 s cabe
  em uma única janela. Se o runner tiver piso de 2 janelas, são 2.
- **Segmentos:** dois métodos. Pelo parâmetro, 903 ÷ 135 = 6,7 → 7. Pela
  densidade real do P003 (93,6 s por segmento, o modelo cortou mais fino que o
  alvo), 903 ÷ 93,6 = 9,6 → 10. Faixa 7–10.
- **PASS 2:** `execution_mode: PER_SEGMENT`, 1 invocação por segmento, sem
  retentativa (P003: 148 invocações para 148 segmentos, 0 erros, 0 zero-yield).
- **Evidências:** limite superior 165 vem de escalar por chars (1 evidência a
  cada 136 chars no P003) e por segmento (16,64 × 10).

## Ressalva sobre a faixa de evidências

O limite superior assume a mesma densidade de conteúdo operável de um curso de
4 horas. Um tutorial de visão geral de 15 minutos tende a render menos por
minuto — daí o piso de 60. Este é o número a acompanhar para o critério **C4**:
poucas evidências e genéricas é exatamente o modo de falha declarado.

Referência de contexto: o `coverage_gate` do P003 fechou em **78,86%** de
cobertura do L0 (limiar 0,735). Não confundir com o **C1** do P004, que é
cobertura evidência→regra >80% — métrica diferente, medida depois.
