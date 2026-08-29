# Claude Code — PILOT-002

**Skill ID:** `PILOT-002-SKILL`  **Version:** `0.1.0`  **Maturity:** `S3_EXECUTABLE`  **Production Ready:** `false`

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
- *Instalação do Claude Code na máquina local* → `WF-0001` (1 steps)
- *Deploy da aplicação com Claude Code* → `WF-0002` (2 steps)
- *quick start* → `WF-0003` (1 steps)
- *native install* → `WF-0004` (2 steps)
- *Instalar o VS Code (Google 'VS Code'/'Visual Studio Code' → link de download)* → `WF-0005` (3 steps)
- *open folder (criar e abrir pasta de projeto no VS Code)* → `WF-0006` (2 steps)
- *Color Themes* → `WF-0007` (3 steps)
- *Iniciar sessão do Claude Code no terminal do VS Code* → `WF-0008` (7 steps)
- */resume (resume a previous conversation)* → `WF-0009` (1 steps)
- *clear* → `WF-0010` (2 steps)
- *Modos de permissão do Claude Code: Plan, Accept Edits, Auto, Bypass* → `WF-0011` (2 steps)
- *Modo plan* → `WF-0012` (1 steps)
- */goal (comando de barra do Claude Code para loop autônomo)* → `WF-0013` (4 steps)
- *plan mode* → `WF-0014` (5 steps)
- */go* → `WF-0015` (2 steps)
- *fidelity bar* → `WF-0016` (5 steps)
- *plan mode / plano gerado* → `WF-0017` (1 steps)
- *build plan* → `WF-0018` (2 steps)
- *dispatch / spin up the loop* → `WF-0019` (1 steps)
- *bypass permission* → `WF-0020` (1 steps)
- *refine with ultra plan* → `WF-0021` (3 steps)
- *fix ticket skill* → `WF-0022` (11 steps)
- */plugins (discovery e instalação de plugins/skills no Claude Code)* → `WF-0024` (4 steps)
- */reload-plugins (aplicação das mudanças após instalação)* → `WF-0025` (5 steps)
- *Front-end SOP (skill de front-end design como SOP para o agente)* → `WF-0026` (1 steps)
- *front end design skill (SOP/instruções que ensinam ao Claude Code como alcançar o resultado)* → `WF-0027` (1 steps)
- *Instalação de skill externa (copiar link e pedir ao agente)* → `WF-0028` (3 steps)
- *Reload plugins* → `WF-0029` (3 steps)
- *slash goal (cria a pasta eval de avaliação)* → `WF-0030` (12 steps)
- *rewind* → `WF-0031` (8 steps)
- */model* → `WF-0032` (2 steps)
- *resume* → `WF-0034` (1 steps)
- *set up version controls using GitHub* → `WF-0035` (5 steps)
- *display the rich difference* → `WF-0036` (1 steps)
- *revert back to that specific version of the git commit* → `WF-0037` (6 steps)
- *git init (criação local da branch padrão master)* → `WF-0038` (4 steps)
- *stage all the changes, commit e sync the changes* → `WF-0039` (2 steps)
- *Collaborators (Settings do repositório)* → `WF-0040` (1 steps)
- *MCP (Model Context Protocol)* → `WF-0041` (1 steps)
- *How to use the GoHighLevel MCP (seguir documentação para conectar MCP ao modelo)* → `WF-0042` (3 steps)
- *Vercel MCP* → `WF-0044` (1 steps)
- *MCP server* → `WF-0045` (18 steps)

- Steps the source does not group under any named procedure → `WF-DEFAULT` (1 steps).

- Out-of-scope request: obey the scope guard in `knowledge/runtime-policy.yaml`.

## FAIL CLOSED

`METHOD_NOT_DEFINED` and `MISSING_REQUIRED_INPUT` are hard runtime stops when emitted by the routed policy. Do not bypass them with general knowledge.

If an executable decision/workflow resource required for the current request is unavailable, do not reconstruct it from this entrypoint, memory, or general knowledge; use the fail-closed behavior in `knowledge/runtime-policy.yaml`.

## RESPONSE DISCIPLINE

Preserve explicit user boundaries; never invent missing required inputs; distinguish source methodology from generic implementation suggestions.

## PILOT LIMITATION

Single-course pilot. Until an independent blind run succeeds, this runtime remains `S3_EXECUTABLE`, `production_ready: false`.
