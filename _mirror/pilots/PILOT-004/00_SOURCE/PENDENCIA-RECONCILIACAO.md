# PENDÊNCIA DE RECONCILIAÇÃO — bot-04 × Lenovo

Status: **R2 FECHADA · R3 FECHADA · R1 ABERTO SEM CONTRAPARTE**.
Aberta em 2026-08-13, atualizada em 2026-08-14 no bot-04.

Existe hoje um `ext4` na Lenovo que rodou o PILOT-003 e um Google Drive que o
bot-04 enxerga. Ninguém conferiu se são o mesmo código. Enquanto não conferir,
qualquer comparação entre o P004 (bot-04) e os pilotos anteriores (Lenovo)
carrega uma incerteza não medida.

## R1 — `ctsc2/extractors/` (o item do BLOCO 2, item 5)

Não consta do FREEZE-RECORD 0.2.0 e é o que efetivamente chama o modelo.

| arquivo | sha256 no Drive (bot-04) | bytes |
|---|---|---|
| `ctsc2/extractors/__init__.py` | conferir no `COMPILER-V2-INVENTORY-bot04.yaml` | 0 |
| `ctsc2/extractors/claude_extractor.py` | conferir no `COMPILER-V2-INVENTORY-bot04.yaml` | 18.139 |

Conferir contra o `ext4` que rodou o P003. Se bater, a comparabilidade retroativa
P003 × P004 fecha. Se não bater, o P003 foi extraído por um código diferente do
que o P004 vai usar, e a diferença precisa ser descrita antes de comparar
qualquer número de evidência.

## R2 — `cts/` (descoberta neste bloco, virou bloqueio ativo)

`cts/coverage.py` e `cts/spans.py` **não existem no Drive** nem em lugar nenhum
do bot-04. Vivem só na Lenovo, em `/home/mtx/course-to-skill-claude/`.

Isto é mais grave que R1 e mudou de natureza: deixou de ser reconciliação e
virou **bloqueio de execução** — sem `cts/`, 5 dos 6 casos do canário não rodam
no bot-04, e o PASS 2 não fecha o portão de cobertura. Ver
`CANARY-BOT04-BLOCKED.md`.

Pinos de hash já conhecidos, do `COMPILATION_MANIFEST.yaml` do PILOT-001-v2:

- `cts/coverage.py` → `ea58c05efd778cb906ac4fee7669d00b7029a72e993f8077fc36231a8f97723b`
- `cts/spans.py` → `7bcdcde2c85e2f814ec9d80b2c5aba38c1905ce17c7001ca35a3b3a42d18bb74`

Conferir a cópia da Lenovo contra esses pinos ao sincronizar. O P003 registra os
mesmos módulos — se o hash da Lenovo divergir do pino do P001-v2, então a métrica
de cobertura mudou entre pilotos e **M3 da régua de idioma não é comparável**
sem ressalva.

## R3 — `canary/`, os 4 arquivos alterados após o freeze

`canary-results.json`, `fixtures.py`, `mutants.py`, `run_canary.py` cresceram
~1h15 depois do freeze de 0.2.0 e trouxeram o caso **C6**. O resultado guardado
(6/6 verde) foi produzido em máquina com `cts/` — presumivelmente a Lenovo, mas
a lista de caminhos de busca inclui um caminho de Mac, então a origem **não está
provada**. Confirmar com a Lenovo qual máquina gerou o `68917b69…` e em que data.

Sem isso, o único atestado de que o C6 protege o `claude_extractor.py` é um JSON
sem procedência.

## Ordem sugerida

1. **R2** — destrava o canário e o PASS 2. É o caminho crítico.
2. **R3** — no mesmo passo: com `cts/` presente, roda-se o canário no bot-04 e o
   resultado passa a ter procedência local e data.
3. **R1** — fecha a comparabilidade retroativa. Pode vir depois do PASS 1 sem
   perda, desde que antes de comparar P003 × P004.

Ao fechar R2 e R3, o `COMPILER-V2-INVENTORY-bot04.yaml` vira o corpo do
`FREEZE-RECORD-v0.2.1.yaml`, com o placar do canário datado no bot-04 — que é o
que o BLOCO 2 pediu e não pôde ser entregue.


---

# ATUALIZAÇÃO 2026-08-14 — desfecho de cada item

## R1 → `R1_ABERTO_SEM_CONTRAPARTE`

O `EXTRACTORS-HASHES-EXT4-LENOVO-20260813.txt` chegou **vazio (0 bytes)**, e
esse é o resultado final da Lenovo: nem a pasta `extractors/` nem
`claude_extractor*.py` existem em `~/course-to-skill-claude` de lá.

Caminho alternativo tentado, conforme instruído: varredura por pino do extractor
em `pilots/PILOT-003`, `pilots/PILOT-003-v2` e `docs/` — todo hash de 64 hex com
`claude_extractor` ou `extractors/` no contexto. **Zero pinos encontrados.**
Nenhum artefato publicado do P003 pina o hash do extractor.

Registrado como **R1_ABERTO_SEM_CONTRAPARTE**. Não bloqueou canário, v0.2.1 nem
PASS 1+2, por decisão do Alexandre.

Consequência que fica: a cópia do Drive é a única em disco e passa a ser a
referência a partir do v0.2.1, que a sela com
`sha256 = bd17ca4147d8ee7dc68cc2969e0132b7d4d5ca11403083c6537b019d2b09db5c`.
Não há como conferir retroativamente se foi este mesmo código que extraiu o
PILOT-003 — a comparação P003×P004 carrega essa incerteza, agora nomeada.

## R2 → **FECHADA**

O `cts/` chegou. Conferência dupla:

- **(a) contra o manifesto da Lenovo:** 16/16 arquivos conferem, 0 divergentes,
  0 ausentes, 0 extras.
- **(b) contra os pinos do `COMPILATION_MANIFEST.yaml` do PILOT-001-v2:**
  `cts/coverage.py` → `ea58c05e…` **CONFERE**; `cts/spans.py` → `7bcdcde2…`
  **CONFERE**.

Instalado em `/Users/alexandresandra/course-to-skill-claude/cts/` e reconferido
**depois** da instalação: 16/16 OK. M3 é comparável entre P001-v2 e P004.

## R3 → **FECHADA por consequência**

A dúvida era a procedência do `canary-results.json` 6/6, porque a lista de
caminhos de busca incluía um caminho de Mac. A dúvida perdeu objeto: o canário
foi executado **no bot-04**, com data, e deu 6/6 com poder real em todos os
casos. O placar do v0.2.1 é local e datado; nada foi herdado.

## Pendência nova aberta neste bloco — classe C sem baseline

Os artefatos publicados do P001-v2 e do P003-v2 têm `EVIDENCE.jsonl` e
`COMPILATION_MANIFEST.yaml`, mas **não os registros de chamada**, onde ficam os
avisos do validador de citação. Por isso os 54 avisos
`CLAIM_DIVERGE_DO_LITERAL_COM_ROTULO_SOURCE_EXPLICIT` do P004 (40% das
evidências) **não têm com o que ser comparados**.

Para fechar: publicar o checkpoint do P001-v2, se existir na Lenovo, ou
reprocessar o P001-v2 com o runner atual e contar a mesma classe lá. Enquanto
isso não acontecer, a conclusão do objetivo secundário fica parcial — ver
`REGUA-M1-M4-RESULTADO.md`.
