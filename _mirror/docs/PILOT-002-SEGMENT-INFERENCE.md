# PILOT-002 — SEGMENT INFERENCE (PASS 1)

**Gerado:** `2026-08-12T00:01:54+00:00` · gerador `pilot002_segment_inference.py` · **somente medição**, READ-ONLY.

Relatório gerado por script; nenhum número foi digitado.


> ## ⚠ A contagem do PILOT-002 é INFERIDA, não lida
>
> O PILOT-001 tem `analysis/temporal-map.yaml` com 9 segmentos declarados — **artefato lido**. O PILOT-002 **não persistiu** o mapa equivalente, e nenhum arquivo dele declara contagem de segmento. O que este relatório diz sobre o PASS 1 do PILOT-002 é **estimativa a partir do padrão temporal das 44 evidências**. Não é medição, e nenhuma linha daqui deve ser citada como se fosse leitura de artefato.


## 0. Insumos

| insumo | sha256 | conteúdo | extensão |
|---|---|---|---|
| PILOT-001 · `temporal-map.yaml` | `c08c32e73731a50b…` | **9 segmentos declarados** | 0:00–14:45 |
| PILOT-001 · `evidence.jsonl` | `2eb266b1fa1c965b…` | 44 com timestamp | 905s |
| PILOT-002 · L0 cortado | `85ea229011a989ea…` | — | 4384s |
| PILOT-002 · EVIDENCE | `a23c837d37cbc9e6…` | 44 evidências | **mapa temporal: NÃO EXISTE** |

> O mapa do PILOT-001 cobre 0:00–14:45 (885s) contra 905s de duração nominal; os 20s finais são a cauda sem marca já registrada no `L0_COVERAGE_MAP`.


## 1. Os 9 segmentos reais do PILOT-001

| segmento | faixa | dur | tópico | evidências |
|---|---|---|---|---|
| SEG-001 | 0:00–1:00 | 60s | Building Your First AI Agent | 1 |
| SEG-002 | 1:00–2:15 | 75s | Is Your Marketing Team Breaking? | 5 |
| SEG-003 | 2:15–3:24 | 69s | What is an AI Agent? | 4 |
| SEG-004 | 3:24–5:49 | 145s | Why Everyone Is Building AI Agents? | 8 |
| SEG-005 | 5:49–7:19 | 90s | Which AI Agents Should You Build First? | 5 |
| SEG-006 | 7:19–9:08 | 109s | What Platform Should You Use? | 5 |
| SEG-007 | 9:08–12:23 | 195s | How to Build an AI Agent Step by Step | 12 |
| SEG-008 | 12:23–13:45 | 82s | Live Build Challenge | 3 |
| SEG-009 | 13:45–14:45 | 60s | Closing Guidance | 1 |

**44 evidências em 9 segmentos = 4.89 por segmento** — mas a média esconde a forma: mínimo **1**, máximo **12**, mediana 5. `SEG-007` sozinho tem 12 evidências; `SEG-001` e `SEG-009` têm 1. A distribuição por segmento é tudo menos uniforme.


## 2. Calibração no PILOT-001 — **o método REPROVA**

A curva é uma escada; cada linha traz o menor X que produz aquela contagem.

| X (s) | grupos | nota |
|---|---|---|
| ≥ 1 | 11 |  |
| ≥ 5 | 10 |  |
| ≥ 6 | 8 |  |
| ≥ 9 | 7 |  |
| ≥ 10 | 5 |  |
| ≥ 14 | 4 |  |
| ≥ 19 | 3 |  |
| ≥ 31 | 2 |  |
| ≥ 74 | 1 |  |

### ⛔ Nenhum X produz 9 grupos no PILOT-001

A curva **pula** a contagem 9: salta de **10** grupos (X=5s) direto para **8** grupos (X=6s). Não existe limiar que reproduza os 9 segmentos reais.


Isto é o teste de validade do método, e ele **falha no único caso onde a resposta é conhecida.** O que vem a seguir mede o quanto falha, porque 'errou por um' e 'não recupera nada' autorizam conclusões muito diferentes.


### 2.1 Os limites recuperados batem com os reais?

Os 8 limites internos reais são `1:00`, `2:15`, `3:24`, `5:49`, `7:19`, `9:08`, `12:23`, `13:45`.

| X (s) | grupos | acertos (tol 0s) | falsos | tol 15s | tol 30s |
|---|---|---|---|---|---|
| 1 | 11 | 6 | 4 | 7 | 7 |
| 5 | 10 | 6 | 3 | 7 | 7 |
| 6 | 8 | 4 | 3 | 5 | 5 |
| 9 | 7 | 3 | 3 | 4 | 4 |

**Melhor reconstrução: X=5s → 10 grupos** (contra 9 reais), com **6 dos 8** limites internos acertados exatamente e 3 falsos.


Limites reais recuperados: `1:00`, `2:15`, `5:49`, `7:19`, `9:08`, `12:23`.  
Limites reais **perdidos**: `3:24`, `13:45`.  
Limites **falsos** inventados: `4:16`, `13:22`, `13:55`.


> **Leitura honesta do teste.** O método não é ruído: 6 de 8 fronteiras reais caem exatamente no lugar certo, o que é muito acima do acaso. Mas ele **não reproduz a contagem**, erra duas fronteiras e inventa outras. Serve para dizer que a segmentação do PASS 1 deixou marca no padrão de evidências; **não serve para contar segmentos com precisão de unidade.** Toda inferência sobre o PILOT-002 daqui em diante herda essa margem.


## 3. Varredura de X — PILOT-002

| X (s) | grupos | nota |
|---|---|---|
| ≥ 7 | 30 |  |
| ≥ 13 | 29 |  |
| ≥ 23 | 28 |  |
| ≥ 24 | 26 |  |
| ≥ 27 | 25 |  |
| ≥ 29 | 24 |  |
| ≥ 37 | 23 |  |
| ≥ 41 | 22 |  |
| ≥ 42 | 21 |  |
| ≥ 45 | 20 |  |
| ≥ 46 | 19 |  |
| ≥ 47 | 17 |  |
| ≥ 59 | 16 |  |
| ≥ 62 | 15 |  |
| ≥ 70 | 14 | ← 14 (capítulos) |
| ≥ 71 | 13 |  |
| ≥ 91 | 12 |  |
| ≥ 125 | 11 |  |
| ≥ 130 | 10 |  |
| ≥ 135 | 9 | ← 9 |
| ≥ 155 | 8 |  |
| ≥ 165 | 6 |  |
| ≥ 170 | 5 |  |
| ≥ 175 | 4 |  |
| ≥ 180 | 3 |  |
| ≥ 185 | 2 |  |
| ≥ 220 | 1 |  |

- Para o PILOT-002 chegar a **9 grupos** seria preciso X de **135–150s**.

- Para o PILOT-002 chegar a **14 grupos (capítulos)** seria preciso X de **70–70s**.


## 4. O teste aplicado ao PILOT-002

| régua | X aplicado | grupos no PILOT-002 | hipótese que testa |
|---|---|---|---|
| **ABSOLUTO** — mesmo X | 5s | **34** | PASS 1 com segmentos de DURAÇÃO fixa |
| **PROPORCIONAL** — X × razão de extensão | 24s (5 × 4.84) | **26** | PASS 1 com NÚMERO fixo de segmentos |

**As duas réguas dão 34 e 26 grupos. Nenhuma chega perto de 9, e nenhuma chega perto de 14.**


> Mesmo a régua proporcional — que já corrige o fato de o PILOT-002 ter a mesma contagem de evidências sobre uma fonte 4.84× maior — devolve 26 grupos. A correção de escala não salva a hipótese.


## 5. Por que as duas réguas falham: ladrilho × ilhas

O método tem uma premissa escondida — que as evidências **ladrilham** a fonte, tocando-se dentro de um segmento e separando-se entre segmentos. Ela vale num piloto e não vale no outro:

| piloto | lacunas ≤ 0 | % | lacuna mediana | união dos spans | % da fonte |
|---|---|---|---|---|---|
| PILOT-001 | 33/43 | **77%** | 0s | 665s | **73%** |
| PILOT-002 | 9/43 | **21%** | 41s | 1630s | **37%** |

> **Conferência cruzada:** a união dos spans dá 665s no PILOT-001 e 1630s no PILOT-002 — os mesmos valores que o `PILOT-002-COVERAGE-REPORT` obteve por outro caminho, e que dão 73.5% e 37.2% de cobertura. Duas medições independentes chegando ao mesmo número é evidência de que a geometria usada aqui está certa.


**No PILOT-001, 77% das lacunas são zero ou negativas** — as evidências se encostam e se sobrepõem, formando um ladrilho contínuo. É por isso que existe um limiar pequeno que separa blocos: as únicas lacunas positivas são as fronteiras.


**No PILOT-002, só 21%** — as evidências são **ilhas isoladas**, com lacuna mediana de 41s. Não há ladrilho para trincar. Agrupar por lacuna nesse regime não recupera segmento: apenas conta evidências, e a contagem de grupos tende ao número de evidências à medida que X diminui.


> É esta a razão de fundo, e ela é mais informativa que a contagem que a tarefa pediu: **os dois pilotos têm geometrias de evidência estruturalmente diferentes.** O PILOT-001 ladrilha a fonte; o PILOT-002 a amostra por pontos. Um método que pressupõe ladrilho não consegue medir o outro regime — e é o mesmo fato que já explicava a queda de cobertura de 73,5% para 37,2%.


## 6. Evidências por grupo

| conjunto | grupos | evidências | por grupo | min–max |
|---|---|---|---|---|
| PILOT-001 · 9 segmentos REAIS (lidos) | 9 | 44 | 4.89 | 1–12 |
| PILOT-001 · grupos por lacuna (X=5s) | 10 | 44 | 4.40 | 1–12 |
| PILOT-002 · X absoluto | 34 | 44 | 1.29 | 1–4 |
| PILOT-002 · X proporcional | 26 | 44 | 1.69 | 1–4 |

O valor de referência da tarefa — 4.89 evidências por segmento no PILOT-001 — é uma média sobre uma distribuição que vai de 1 a 12. Usá-la para dividir 44 e obter contagem de segmento no PILOT-002 suporia uma regularidade que o próprio PILOT-001 não tem.


### 6.1 Os grupos do PILOT-002 na régua proporcional

| # | faixa (corpus) | dur | n | evidências |
|---|---|---|---|---|
| 1 | 0:07–0:34 | 27.0s | 1 | E001 |
| 2 | 2:49–3:17 | 28.0s | 1 | E002 |
| 3 | 4:02–4:30 | 28.0s | 1 | E003 |
| 4 | 5:16–5:49 | 33.0s | 1 | E004 |
| 5 | 8:33–8:55 | 22.0s | 1 | E005 |
| 6 | 11:05–11:36 | 31.0s | 1 | E006 |
| 7 | 12:38–14:16 | 98.0s | 2 | E007, E008 |
| 8 | 14:57–15:45 | 48.0s | 1 | E009 |
| 9 | 18:38–19:21 | 43.0s | 1 | E010 |
| 10 | 20:20–20:49 | 29.0s | 1 | E011 |
| 11 | 21:16–23:19 | 123.0s | 2 | E012, E013 |
| 12 | 26:59–29:10 | 131.0s | 4 | E014, E015, E016, E017 |
| 13 | 31:53–33:05 | 72.0s | 3 | E018, E019, E020 |
| 14 | 34:15–35:25 | 70.0s | 2 | E021, E022 |
| 15 | 38:28–40:40 | 132.0s | 2 | E023, E024 |
| 16 | 41:27–42:13 | 46.0s | 2 | E025, E026 |
| 17 | 42:55–46:27 | 212.0s | 4 | E027, E028, E029, E030 |
| 18 | 46:56–47:31 | 35.0s | 1 | E031 |
| 19 | 50:29–50:54 | 25.0s | 1 | E032 |
| 20 | 52:25–54:09 | 104.0s | 3 | E033, E034, E035 |
| 21 | 55:20–56:27 | 67.0s | 1 | E036 |
| 22 | 59:13–59:57 | 44.0s | 1 | E037 |
| 23 | 60:34–61:45 | 71.0s | 2 | E038, E039 |
| 24 | 62:32–64:26 | 114.0s | 2 | E040, E041 |
| 25 | 67:00–67:41 | 41.0s | 1 | E042 |
| 26 | 69:44–70:54 | 70.0s | 2 | E043, E044 |

## 7. Conclusão

1. **O método reprova na calibração.** Nenhum X reproduz os 9 segmentos do PILOT-001; a curva pula de 10 para 8. A melhor reconstrução (X=5s) dá 10 grupos e acerta 6/8 fronteiras.

2. **Com a margem que a calibração permite, o PILOT-002 dá 34 grupos na régua absoluta e 26 na proporcional.** Nem perto de 9, nem perto de 14.

3. **Portanto: a hipótese de um PASS 1 com ~9 segmentos no PILOT-002 NÃO se sustenta neste teste** — mas a rejeição é fraca, porque o instrumento reprovou na própria calibração. O honesto é dizer que o teste **não decide**, e não que ele decidiu contra.

4. **O achado com força é outro, e é estrutural:** as evidências do PILOT-001 ladrilham a fonte (77% de lacunas não positivas, união cobrindo 73%) e as do PILOT-002 são ilhas (21%, 37%). Qualquer método de reconstrução por vizinhança temporal vai falhar no segundo regime. Para decidir a questão do PASS 1 é preciso **o artefato**, não mais inferência.

5. **O que responderia de fato:** persistir o temporal-map na próxima compilação do PILOT-002, ou recompilar com o PASS 1 instrumentado. Enquanto isso não existir, a contagem de segmentos do PILOT-002 permanece **não observada**.


---

**Escopo:** somente medição e inferência declarada. Nenhum arquivo de `pilots/`, `Course-to-Skill/` ou `Course-to-Skill-Compiler/` foi criado, alterado, movido ou apagado. O único arquivo escrito é este relatório.
