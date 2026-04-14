# mararn1618-workstreams — Design

**Status:** approved 2026-04-14
**Version target:** 0.1.0

## Purpose

A marketplace skill that turns any folder into a stateless, resumable workspace for Claude Code. The session can be killed at any time and a fresh session must be able to pick up the same workstream without loss of context. All state lives on disk, not in the conversation.

## Goals

- Cross-session statelessness: any fresh Claude session in a scaffolded folder can resume an existing workstream from on-disk state alone.
- Topic isolation: each workstream has its own folder, own worklog, own decisions, own inputs.
- Self-maintaining index: the top-level `CLAUDE.md` lists active and archived workstreams and is updated automatically by the skill.
- Low ceremony: KISS. The user should not have to manually manage files.

## Non-goals (v1)

- Per-workstream memory with summarization, bumping, or housekeeping.
- Subagent-per-workstream isolation.
- A `context/output/` folder for generated artifacts.
- Fully automatic archiving without user confirmation.
- Memory file rotation with ISO-dated snapshots.

Memory-related ideas from the original braindump are deferred. They can be revisited in a future version if worklog/decisions on their own prove insufficient.

## Interface constraints

The skill must work in interface channels that do not expose Claude Code harness commands. The primary example is the Discord plugin: messages arrive as regular channel messages, so neither the user nor the agent can invoke `/clear` or any other harness slash command mid-session. The agent also has no tool to clear its own context window.

Implication: mid-session context clearing is not available in every channel the user may speak through. The skill's on-disk protocol must therefore be strong enough that the agent can re-orient correctly regardless of whether context was cleared. Both failure modes — session died, or session accumulated stale context — are handled by the same mechanism: trust the disk, re-read the workstream files, do not rely on prior turns.

This constraint motivates the workstream switching rule in the Runtime protocol below.

## Scaffold

The skill exposes a setup action that, given a root folder, creates:

```
<root>/
├── CLAUDE.md        # gate + skill summary + index
└── _archive/        # empty, created upfront
```

`_archive/` exists from day one so the archiving action has a target without special-casing its own creation.

## CLAUDE.md template

Three sections, in this order. The top-level `CLAUDE.md` is always loaded into context by Claude Code, so it is the one reliable enforcement point.

### 1. Hard gate

A bold, imperative directive at the very top, modelled on `superpowers:using-superpowers`:

> **BEFORE your first response in this folder, you MUST invoke the `mararn1618-workstreams` skill via the Skill tool. This is non-negotiable. The skill contains the protocol for how work in this folder happens — you cannot respond correctly without it.**

### 2. Skill summary

Two to three lines describing what the skill does and why Claude must load it. This exists so the agent sees *why* the gate matters, not just that it exists.

### 3. Workstream index

Auto-maintained bullet list. Each entry is one line: folder name plus a one-line hook.

```markdown
## Active workstreams
- 2026-04-mein-cooles-thema — one-line hook
- 2026-04-other-topic — one-line hook

## Archived (_archive/)
- 2026-02-old-topic — one-line hook
```

If there are no workstreams, the sections still exist but are empty. Archived workstreams remain in the index so the agent knows they exist but does not load them by default.

## Workstream folder layout

```
2026-04-topic-slug/
├── README.md          # description, goals, optional non-goals
├── worklog.md         # append-only, ISO-timestamped one-liners
├── decisions.md       # append-only, 2-4 line entries
└── context/input/     # dated inputs: YYYY-MM-DD_<name>.<ext>
```

### Folder naming

`YYYY-MM-<topic-slug>/`. No `workstream_` prefix — the root folder only contains workstreams, `_archive/`, and `CLAUDE.md`, so the prefix is redundant. The date prefix sorts chronologically.

### README.md

User-owned canonical document describing the workstream. Contains: description, goals, and optionally non-goals. Single file, not separate goals/non-goals files. The agent may **propose** updates but must not silently rewrite it (see Runtime protocol).

### worklog.md

Append-only. One line per entry, prefixed with ISO timestamp. Kept short on purpose so a fresh session can read the whole tail quickly on resume. Example:

```
- 2026-04-14T10:23Z — created workstream, stubbed README with goal: X
- 2026-04-14T10:41Z — ran script Y, produced ./out/report.csv
- 2026-04-14T10:55Z — user clarified scope: only EU markets
```

### decisions.md

Append-only. Entries are 2-4 lines: date, decision, one-line rationale. Lower frequency than worklog. Example:

```markdown
## 2026-04-14 — use Postgres, not SQLite
Decided because multi-user access is in scope; SQLite locking would block the second user.
```

### context/input/

All user-provided inputs (transcripts, emails, PDFs, screenshots) land here with a `YYYY-MM-DD_` filename prefix. Enforced by the skill whenever a file is saved from user input.

No `context/output/` folder in v1. Generated artifacts (source code, reports, etc.) live wherever the task naturally places them; the worklog records what was produced and where. `context/output/` can be added in a future version if a clear use case emerges.

## Runtime protocol

The skill's `SKILL.md` holds these rules. The gate in `CLAUDE.md` forces every session to load them before acting.

### On the first user message in a session

1. Read `CLAUDE.md` (always in context anyway — but re-read for the index).
2. If the message is clearly trivial (quick factual question, chitchat, no continuation), skip workstream logic entirely.
3. Otherwise, scan the index for a plausible match with the user's topic.
   - If matched: ask *"is this about the `<X>` workstream?"* and wait for confirmation.
   - If no match and the topic seems substantial: ask *"should I start a new workstream for this?"* and wait.
4. On confirmed existing: read that workstream's `README.md` in full, tail `worklog.md`, read `decisions.md` in full. Then proceed with the work.
5. On confirmed new: prompt the user for a short slug; create `YYYY-MM-<slug>/` with a stub `README.md` (prompting for goals and optional non-goals), empty `worklog.md` and `decisions.md`, empty `context/input/`. Update the `CLAUDE.md` index.
6. Run the archive check: for every active workstream, if `worklog.md` mtime is older than 30 days, collect into a one-line prompt *"these N workstreams haven't been touched in >30 days: X, Y, Z. Archive them? [y/N]"*. User decides in bulk.

### During work — discipline rules (rigid)

These are enforceable rules, not suggestions. The skill surfaces them as a short red-flag table so the agent cannot rationalise skipping them.

**worklog.md — append after every state-changing turn, before ending the turn.** State-changing means: ran a command that modified something, made a decision, learned something new from the user, completed a task. One ISO-timestamped line. Red flag: the thought *"I'll note this later"* is wrong; write now.

**decisions.md — append whenever a non-trivial choice is made between alternatives.** Entry is 2-4 lines: date header, the decision, one-line rationale.

**README.md — propose, never silently rewrite.** If the agent notices reality has drifted from the stated goals (e.g. we've been doing Y for three turns but README says goal is X), it surfaces this to the user: *"the README goals seem out of date, want me to update to reflect Y?"* and writes only on confirmation. Rationale: the README is the anchor a fresh session reads first, so it must stay trustworthy.

**context/input/ — always dated.** Any file handed over by the user is saved here with a `YYYY-MM-DD_` filename prefix. The skill enforces this whenever saving from user input.

**Workstream switching — treat as a conscious reset.** When the user switches from workstream A to workstream B within the same session, re-read B's `README.md`, tail B's `worklog.md`, and read B's `decisions.md`. Do not carry A's working state into B's turns. If something from A is relevant later, look it up from A's on-disk files rather than recalling it from the conversation. Assume you have to earn B's context from disk, not from memory. This rule exists because mid-session context clearing is not available in every interface channel (see Interface constraints).

### Archiving action

Triggered either by the bulk prompt on session start or by an explicit user request. Performs:

1. Move the workstream folder into `_archive/`, preserving its name.
2. Update `CLAUDE.md` index: remove the entry from **Active workstreams**, add it under **Archived (_archive/)** with the same one-line hook.

Staleness detection uses `worklog.md` filesystem mtime. Threshold: 30 days. The threshold is a constant in `SKILL.md` — users can edit their local copy but it is not configurable per folder in v1.

## Marketplace wiring

- Plugin folder: `mararn1618-workstreams/`
- `mararn1618-workstreams/.claude-plugin/plugin.json` with `"version": "0.1.0"`
- `mararn1618-workstreams/skills/workstreams/SKILL.md` containing the runtime protocol and a scaffold action
- New entry in `.claude-plugin/marketplace.json` with matching `"version": "0.1.0"` per the repo's versioning rule

## Open questions for implementation

None blocking. Minor items to decide during implementation:

- Exact frontmatter fields for `SKILL.md` (follow existing marketplace skills for consistency).
- Whether the scaffold action is a slash command, a skill invocation with an argument, or a prompt the skill walks the user through. Lean toward: the skill detects an unscaffolded folder and offers to scaffold it on first use.
- Exact wording of the hard-gate paragraph in `CLAUDE.md` — draft during implementation, keep short.
