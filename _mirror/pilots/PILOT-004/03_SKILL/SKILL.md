# Meta Business Suite — PILOT-004

**Skill ID:** `PILOT-004-SKILL`  **Version:** `0.1.0`  **Maturity:** `S3_EXECUTABLE`  **Production Ready:** `false`

## ROLE OF THIS FILE

Runtime entrypoint and router only. Executable methodology is intentionally stored in structured resources rather than duplicated here.

## LOAD ORDER — MANDATORY

Before every answer, load/apply in this order:

1. `knowledge/runtime-policy.yaml`
2. `knowledge/decision-rules.yaml` when a methodology decision is required
3. `knowledge/workflows.yaml` when building/configuring

## DISPATCH

- Methodology decision request → `knowledge/decision-rules.yaml`.

Build/configure requests route by topic to `knowledge/workflows.yaml`:
- *portfólio empresarial* → `WF-0001` (2 steps)
- *contas vinculadas* → `WF-0002` (2 steps)
- *Meta Business Suite* → `WF-0003` (1 steps)
- *todas as ferramentas* → `WF-0005` (2 steps)
- *planner* → `WF-0006` (1 steps)
- *Planner (Meta Business Suite) — agendamento de postagens* → `WF-0007` (1 steps)
- *Criar post / programar post, story, reels ou live* → `WF-0008` (10 steps)
- *Caixa de entrada como central de atendimento* → `WF-0009` (1 steps)
- *Automações* → `WF-0010` (4 steps)
- *Criar campanha por dentro do Gerenciador de Anúncios (Gerenciador de Anúncios > Campanhas > criar)* → `WF-0011` (9 steps)
- *Configurações > Usuários > Pessoas* → `WF-0012` (8 steps)

- Steps the source does not group under any named procedure → `WF-DEFAULT` (3 steps).

- Out-of-scope request: obey the scope guard in `knowledge/runtime-policy.yaml`.

## FAIL CLOSED

`METHOD_NOT_DEFINED` and `MISSING_REQUIRED_INPUT` are hard runtime stops when emitted by the routed policy. Do not bypass them with general knowledge.

If an executable decision/workflow resource required for the current request is unavailable, do not reconstruct it from this entrypoint, memory, or general knowledge; use the fail-closed behavior in `knowledge/runtime-policy.yaml`.

## RESPONSE DISCIPLINE

Preserve explicit user boundaries; never invent missing required inputs; distinguish source methodology from generic implementation suggestions.

## PILOT LIMITATION

Single-course pilot. Until an independent blind run succeeds, this runtime remains `S3_EXECUTABLE`, `production_ready: false`.
