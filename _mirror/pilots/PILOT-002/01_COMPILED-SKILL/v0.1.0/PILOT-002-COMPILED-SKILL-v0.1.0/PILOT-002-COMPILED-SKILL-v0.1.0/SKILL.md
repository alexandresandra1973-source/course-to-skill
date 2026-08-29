---
name: pilot-002-claude-code-foundations
description: Source-grounded Claude Code foundations workflow compiled only from PILOT-002 L0-transcript-CUT.txt.
---

# PILOT-002 — Claude Code Foundations

## Source lock

Use only the compiled rules below and their linked evidence records. Do not fill missing operational policy from general knowledge. The source-derived defaults for `autonomy`, `precedence`, `missing_input_action`, and `iteration_limit` are `UNDEFINED`; do not invent them.

## Purpose

Guide a user through the source-taught Claude Code foundations: local setup, IDE/project organization, sessions, `/goal` planning, reusable skills, file structure, context commands present in the cut, Git/GitHub version control, MCP/CLI connections, and deployment examples. [E001, E002, E003, E012, E029, E036]

## Workflow

### 1. Establish the local working environment

- Treat the material as beginner-oriented; do not assume prior developer experience. [E001]
- For installation, direct the user to the Claude Code quick-start/native-install flow for the user operating system. Do not fabricate an installation command that is not present in the cut. [E002]
- Prefer an IDE workflow when the user needs both terminal access and visible file changes; the demonstrated IDE is VS Code. [E003]
- Open or create a dedicated project folder and keep project files organized there. [E004]

### 2. Start and recover sessions

- Start Claude Code from the IDE terminal with `claude`. [E005]
- Use `/resume` when the user wants to return to a previous session. [E006]
- Do not invent session-retention guarantees beyond what the source demonstrates.

### 3. Plan before using the autonomous goal loop

- `/goal` is a source-explicit capability that can loop autonomously, evaluate the generated output against initial requirements, feed back corrections, and continue until the requirements are met. [E007]
- The demonstrated sequence gathers requirements and expectations in plan mode before execution; use that sequence as the preferred compiled workflow, while preserving that it is an inference from the example rather than a universal platform rule. [E008]
- The planning example asks implementation questions before producing the plan. Use questions only when the user or task context calls for them; do not treat this example as a defined global `missing_input_action`. [E009, E017]
- If source assets are already available for a reference-based build, prefer localizing them before execution rather than making the model guess; this is a compilation inference from the demonstrated refinement. [E010]
- Do not promote `bypass permission` into a default. The cut does not contain the complete permission-mode definitions, so the Skill default permission/autonomy policy remains `UNDEFINED`. [E043]

### 4. Distinguish local output from deployed output

- A development-server link in the demonstrated local run is local-only. Do not present it as a shareable public deployment. [E011]

### 5. Build and use reusable skills

- Treat a skill as a reusable workflow/guide/SOP that instructs the model how to perform a repeatable process. [E012]
- The fix-ticket example demonstrates a master workflow that can coordinate ticket intake, reproduction, research, implementation, review, verification, version control, deployment, and human handoff. Preserve it as an example; do not make every skill use that exact pipeline. [E013]
- When installing a skill/plugin, preserve the source distinction between user/global scope and project/collaborator scope. [E014]
- Reload plugins after installation when following the demonstrated installation flow. [E015]
- Trigger a skill either by natural-language instruction or by its slash command when available. [E016]

### 6. Interpret the project file structure

- `.md` files are documentation/written documentation. [E018]
- `package.json` contains dependency information and commands used by the application. [E019]
- `public` holds public assets such as logos and images. [E020]
- The demonstrated `eval` folder is created by `/goal` for requirement evaluation and is described as temporary/deletable after completion. [E021]
- `components` contains reusable application pieces that are assembled into the larger application. [E022]
- Preserve the source distinction between universal agent material in `.agents` and Claude Code-specific material in `.claude`. [E023]
- Preserve the source distinction between universal rules in `AGENTS.md` and Claude Code-specific rules in `CLAUDE.md`; do not invent a conflict-precedence rule between them. [E024]

### 7. Use only context/session commands taught in the cut

- `/compact` summarizes older conversation context. [E025]
- `/model` changes the active model. [E026]
- Rewind can restore code and conversation to a previous checkpoint. [E027]
- Plugins can be uninstalled through plugin management; the source also demonstrates deleting an installed skill folder and restarting Claude Code. [E028]
- The cut omits the earlier portion of the context-window section; do not reconstruct missing context-management rules.

### 8. Add version control for maintained work

- Use GitHub as the demonstrated project version-control service when version history/rollback is needed. [E029, E042]
- Treat commits as inspectable versions and branches as separate lines of change. [E030, E031]
- Do not commit sensitive information to cloud version control. [E032]
- The demonstrated VS Code flow is stage -> commit -> sync/push. [E033]
- Collaborators can work on the same repository, and past changes can be restored. [E034]
- When reverting a specific change, the source demonstrates using the commit ID as the target supplied to Claude Code. [E035]

### 9. Connect external tools with MCP or CLI

- MCP is the source-taught standardized bridge between the AI agent and external tools/services. [E036]
- CLI is terminal command execution; MCP exposes a standardized tool bridge. [E037]
- Use the source tradeoff when helping a user choose: CLI for speed/token efficiency; MCP for stronger access-control/team/audit characteristics, at the cost of more context-token overhead. [E038]

### 10. Deploy and handle destructive remote actions carefully

- The deployment example logs into Vercel, creates a project through the connected CLI, and deploys the current application. Preserve this as a demonstrated example, not a universal deployment requirement. [E039]
- Before a destructive remote deletion, verify the exact target and avoid unrelated projects. This safeguard is a compilation inference from the deletion example, not a separately stated universal platform rule. [E040]

### 11. Keep agents, skills, and tools conceptually separate

- Skills are repeatable SOP/workflows; MCPs/CLIs are tools/connectors; agents are specialist executors that can use skills, and skills can call tools. [E041]

## Source-bounded safety and unknowns

- `autonomy`: `UNDEFINED` as a Skill default. `/goal` autonomous looping is a capability, not a default policy.
- `precedence`: `UNDEFINED`. The source describes system-prompt locations but does not define a complete conflict-precedence rule.
- `missing_input_action`: `UNDEFINED`. Clarification questions appear in examples but are not stated as a universal rule.
- `iteration_limit`: `UNDEFINED`. `/goal` has a source-stated completion condition (requirements met), but no maximum iteration count is taught in the cut.
- Permission-mode definitions are incomplete in the cut. Do not reconstruct them.
- Context-window instruction is incomplete in the cut. Do not reconstruct the omitted portion.
- Do not use pricing/model claims from the FAQ as stable operational policy without a separate authorized source; they are not required for this Skill.

## Epistemic behavior

When adding or modifying any rule in this Skill, classify its support as exactly one of:

- `SOURCE_EXPLICIT`: directly stated by the authorized L0 cut.
- `MODEL_INFERENCE`: a compilation/generalization derived from source behavior or structure.
- `GENERAL_KNOWLEDGE`: outside knowledge. This compiled package uses none as source input.

Every evidence record must contain a non-empty `source_excerpt` with an exact line span, local citation, and quote that resolves against `L0-transcript-CUT.txt`.
