# discuss-plan-implement — Design Spec

**Date:** 2026-04-14
**Author:** Markus Arndt (bilateral brainstorm with Claude)
**Status:** Approved, moving to implementation plan

## 1. Purpose

A minimal Claude Code plugin that provides a structured three-command workflow for completing one story at a time:

- `/discuss-plan-implement:discuss` — bilateral alignment conversation, writes a discussion summary
- `/discuss-plan-implement:create-plan` — turns the discussion into a concrete executable plan
- `/discuss-plan-implement:implement-plan` — executes the plan using two sequential Claude Code Teams: an Implementer team that writes code, then an Advisor team that does a clean-context GAN-style verification

This plugin is a lightweight alternative to `superpowers` (felt slow in practice) and a complement to the existing `ralph` plugin (which is for long-running autonomous runs, not interactive one-story work).

## 2. Principles

- **Zero always-on context cost.** No `SKILL.md` files, no hooks, no `SessionStart` side effects. Commands are loaded only when invoked.
- **Phase gates, not phase enforcement.** Each command is standalone. The human decides when to move between phases.
- **File-based state.** All artifacts are markdown files committed to the repo, readable by future sessions and by humans.
- **Clean context boundaries for verification.** Advisors never see implementer chatter.
- **Three commands, one story.** Not designed for overnight autonomous runs — use `ralph` for that.

## 3. Plugin structure

```
discuss-plan-implement/
├── .claude-plugin/
│   └── plugin.json              # name, version, description
├── commands/
│   ├── discuss.md
│   ├── create-plan.md
│   └── implement-plan.md
└── README.md
```

No `skills/`, no `hooks/`. Marketplace registration is added to the existing `.claude-plugin/marketplace.json`.

## 4. File artifacts (in the user's project)

```
<project>/
└── docs/
    ├── discussions/
    │   └── YYYY-MM-DD-<slug>.md     # /discuss output
    └── plans/
        └── YYYY-MM-DD-<slug>.md     # /create-plan output, mutated by /implement-plan
```

Both files are committed. Slugs are derived from the story topic in kebab-case.

### Discussion file format

```markdown
---
story: "<one-line story statement>"
created: <YYYY-MM-DD>
---

# Discussion: <topic>

## Intent
<1-3 sentences: what the human wants and why>

## Acceptance Criteria
- [ ] <criterion 1>   ← flow verbatim into the plan
- [ ] <criterion 2>

## Key Decisions
- <decision + rationale>

## Constraints
- <technical, business, or scope constraints surfaced>

## Out of Scope
- <explicitly excluded>   ← flows verbatim into the plan

## Open Questions
- <anything unresolved>
```

### Plan file format

```markdown
---
story: "<one-line story statement>"
discussion: docs/discussions/YYYY-MM-DD-<slug>.md
created: <YYYY-MM-DD>
max_advisor_rounds: 3
---

# Plan: <title>

**Story:** <one sentence>
**Discussion:** [<filename>](<relative path>)

## Acceptance Criteria
*(from discussion — final advisor verifies each)*

- [ ] <criterion 1>
- [ ] <criterion 2>

## Out of Scope
- <item 1>
- <item 2>

## Tasks
*(tasks with the same `group` run in parallel; groups run in order A → B → C)*

- [ ] **T1: <title>**
  - **Group:** A
  - **Files:** `<path>`
  - **Done when:** <verifiable condition>
  - <1-3 sentence description>

- [ ] **T2: <title>**
  - **Group:** A
  - **Files:** `<path>`
  - **Done when:** <verifiable condition>

- [ ] **T3: <title>**
  - **Group:** B
  - **Depends on:** T1
  - **Files:** `<path>`
  - **Done when:** <verifiable condition>

## Advisor Checks
*(clean-context advisor verifies, in addition to acceptance criteria)*

- [ ] All tasks marked complete
- [ ] <custom checks>

## Progress Log
<!-- appended by /implement-plan as work proceeds -->
```

### Format improvements over `create-markdown-plan`

1. **YAML frontmatter** with story, discussion link, max advisor rounds
2. **Acceptance criteria at top level** (not per-phase) — single source of truth for the advisor
3. **Flat task list, no phases** — phases add ceremony for one-story scope
4. **`group: A|B|C`** per task for explicit parallelism
5. **`Depends on:`** optional field for cross-group edges
6. **`Done when:`** per task — finer granularity than phase-level acceptance criteria
7. **`Out of Scope` section** — prevents sub-agent drift
8. **`Advisor Checks` section** — distinct from per-task done-when, runs once at end
9. **No owner annotations** (`AI`/`HUMAN`) — this plugin is AI-execution-only
10. **Progress Log** — append-only trail of what happened

## 5. Command semantics

### `/discuss`

1. Loads no files up-front. Reads topic from user message.
2. **Proactive context gathering:** scans relevant project files (Glob/Grep/Read) before asking clarifying questions so questions are informed by actual code.
3. Asks clarifying questions **1-2 at a time** (not wall-of-questions). Invites the user to ask questions back.
4. Surfaces assumptions explicitly. Briefly explores alternatives at forks.
5. **No code is written in this phase.** Reading is fine, writing is not.
6. When alignment is reached, writes `docs/discussions/YYYY-MM-DD-<slug>.md`.
7. Presents the path and suggests running `/create-plan`.

### `/create-plan`

1. Finds the latest discussion file in `docs/discussions/` (or asks if ambiguous).
2. Copies Acceptance Criteria and Out of Scope from discussion verbatim into the plan.
3. Gathers additional technical context (file structure, patterns, dependencies).
4. Drafts tasks in the plan format. Conservative parallelism — marks tasks as parallel only when obviously independent.
5. Writes `docs/plans/YYYY-MM-DD-<slug>.md`.
6. Presents the plan inline for review. If changes requested, edits and re-presents.
7. On approval, suggests running `/implement-plan`.
8. Does NOT enter Claude Code plan mode (Plannotator out of scope for v1).

### `/implement-plan`

**Phase A — Implementer team**

1. Loads latest plan file. If multiple, asks which.
2. Parses tasks by group.
3. `TeamCreate` → team `dpi-impl-<timestamp>`.
4. For each group in order:
   - Spawn one implementer teammate per task in the group (parallel)
   - Each teammate receives: task title, files, done-when, plan path, discussion path
   - Teammates can DM each other if coordination needed
   - When a teammate finishes, it **DMs the lead** with `"Task T<n> complete: <summary>"` — the **lead** edits the plan file to mark `[x]` and append to Progress Log. This avoids race conditions from multiple teammates writing to the plan file concurrently.
   - Wait for all in group to complete before starting next group
5. Append per-task summary to plan's Progress Log.
6. `TeamDelete` on implementer team.

**Phase B — Advisor team (clean context)**

7. `TeamCreate` → team `dpi-advisor-<timestamp>`.
8. Spawn two teammates:
   - **Advisor** — reviews code against acceptance criteria, per-task done-when, code quality. Job: find problems.
   - **Fixer** — takes advisor findings, edits code to address them. Narrow role.
9. Advisor ↔ Fixer iterate via `SendMessage`:
   1. Advisor scans → "Issues: A, B, C" → DMs Fixer
   2. Fixer edits → "Fixed A, B, C" → DMs Advisor
   3. Advisor re-scans → "Approved" or "Still issues: D" → DMs Fixer
   4. Repeat up to `max_advisor_rounds`
   - **Loop termination:** Advisor is responsible for counting rounds (its prompt includes `max_advisor_rounds`). When approved, Advisor DMs the lead with `"APPROVED: <summary>"`. When max rounds hit without approval, Advisor DMs lead with `"MAX ROUNDS EXCEEDED: <remaining issues>"`. Lead monitors its inbox for either message.
10. Main agent receives final verdict. Writes it to plan's Progress Log.
11. `TeamDelete` on advisor team.

**Phase C — Report**

12. Main agent summarizes: tasks done, advisor verdict, unresolved items (if any), plan file path.

## 6. Error handling & recovery

| Scenario | Behavior |
|---|---|
| `/discuss` topic ambiguous | Ask clarifying question |
| `/create-plan` no discussion file | Ask user to run `/discuss` or describe inline |
| `/create-plan` plan already exists for slug | Ask: overwrite or new slug |
| Implementer teammate fails task | Main agent retries once; if still failing, marks task ⚠️, skips, continues |
| `TeamCreate` fails | Abort, report |
| Advisor rejects after max rounds | Mark unresolved items with ⚠️, exit cleanly with report |
| Session dies mid-run | Re-invoking `/implement-plan` reads plan state, resumes from first unchecked task |

All durable state lives in the plan file. Teams are short-lived and always deleted.

## 7. Explicitly out of scope

- TDD enforcement
- Git branch / worktree management (human manages)
- Plannotator integration
- `SessionStart`, `PreToolUse`, or any other hooks
- Auto-detection of phase (explicit commands only)
- Multi-story orchestration (one story per invocation)
- Always-on context / `SKILL.md` files

## 8. Relationship to existing plugins

| Plugin | What it does | When to reach for it |
|---|---|---|
| `discuss-plan-implement` | Interactive one-story workflow, 3 commands, Team-based execution + GAN advisor | When completing a single story with human-in-the-loop alignment |
| `ralph` | Autonomous long-running loop, state machine, file-based blockers | Overnight autonomous runs on larger projects |
| `create-markdown-plan` | Plan format reference for human-authored plans | When a human writes a multi-phase plan manually |

They coexist. This plugin copies the plan format from `create-markdown-plan` (with the improvements listed in §4) so the plugin is fully self-contained.

## 9. Versioning

Initial version: **0.1.0**

Per the marketplace's `CLAUDE.md`, version must be set in both:
- `discuss-plan-implement/.claude-plugin/plugin.json` → `"version": "0.1.0"`
- `.claude-plugin/marketplace.json` → matching entry `"version": "0.1.0"`

## 10. Success criteria for v0.1.0

- [ ] Plugin can be installed via `/plugin install discuss-plan-implement@mararn1618-claude-marketplace`
- [ ] `/discuss`, `/create-plan`, `/implement-plan` commands are discoverable
- [ ] Running all three commands on a toy story produces discussion file, plan file, and completed work
- [ ] `/implement-plan` successfully uses `TeamCreate` / `SendMessage` / `TeamDelete` without orphaned teams
- [ ] GAN-style advisor loop terminates within `max_advisor_rounds`
- [ ] Plan file contains Progress Log entries for all executed tasks
- [ ] Session recovery works: killing mid-run and re-invoking `/implement-plan` resumes from the first unchecked task
