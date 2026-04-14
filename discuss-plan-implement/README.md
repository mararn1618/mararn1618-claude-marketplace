# discuss-plan-implement

A minimal Claude Code plugin for a bilateral **discuss → plan → implement** workflow, scoped to one story at a time.

Three explicit slash commands, zero always-on context cost, file-based state that survives sessions. Designed as a lightweight alternative to heavier workflow plugins, and a complement to `ralph` (which is for long-running autonomous runs).

## Commands

| Command | Purpose | Output |
|---|---|---|
| `/discuss-plan-implement:discuss` | Bilateral alignment conversation. No code is written. | `docs/discussions/YYYY-MM-DD-<slug>.md` |
| `/discuss-plan-implement:create-plan` | Turn a discussion into a concrete executable plan with parallelism annotations. | `docs/plans/YYYY-MM-DD-<slug>.md` |
| `/discuss-plan-implement:implement-plan` | Execute the plan using two sequential Claude Code Teams: an Implementer team for parallel task execution, then a clean-context Advisor team for GAN-style verification. | Code changes + updated plan file with Progress Log |

## Workflow

```
/discuss-plan-implement:discuss
        |
        v
docs/discussions/2026-04-14-my-story.md
        |
        v
/discuss-plan-implement:create-plan
        |
        v
docs/plans/2026-04-14-my-story.md
        |
        v
/discuss-plan-implement:implement-plan
        |
        +-- Phase A: Implementer team (parallel per group)
        |     +-- impl-T1, impl-T2 (group A, parallel)
        |     +-- impl-T3, impl-T4 (group B, parallel)
        |     +-- ...
        |
        +-- Phase B: Advisor team (fresh context)
        |     +-- advisor <-> fixer (GAN-style loop)
        |
        +-- Phase C: Report
```

## Design principles

- **Zero always-on context cost.** No `SKILL.md` files, no hooks. Commands load only when invoked.
- **Phase gates, not phase enforcement.** Each command is standalone. The human decides when to move between phases.
- **File-based state.** All artifacts are markdown files committed to the repo. Sessions can be resumed; humans can read the full trail.
- **Clean context boundaries for verification.** Advisors never see implementer chatter.
- **One story per invocation.** Not designed for overnight autonomous runs — use `ralph` for that.

## Plan file format

Plans use a format derived from `create-markdown-plan` with extensions for parallel task groups, per-task "done when" conditions, and advisor checks. See the spec at `docs/superpowers/specs/2026-04-14-discuss-plan-implement-design.md` for the full schema.

Key additions over `create-markdown-plan`:

- YAML frontmatter with story, discussion link, `max_advisor_rounds`
- Acceptance criteria at top level (inherited from discussion)
- Flat task list (no phases) with `group: A|B|C` for parallelism
- Per-task `Done when:` conditions
- `Out of Scope` section (prevents sub-agent drift)
- Separate `Advisor Checks` section for clean-context verification

## Relationship to other plugins in this marketplace

| Plugin | Use case |
|---|---|
| `discuss-plan-implement` | Interactive one-story work with human-in-the-loop alignment |
| `ralph` | Autonomous overnight runs for multi-day projects |
| `create-markdown-plan` | Reference format for human-authored multi-phase plans |

They coexist; pick based on the shape of the work.

## Installation

```
/plugin marketplace add mararn1618/claude-marketplace
/plugin install discuss-plan-implement@mararn1618-claude-marketplace
```

## Version

**0.1.0** — Initial release.
