# discuss-plan-implement Plugin Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `discuss-plan-implement` plugin per the spec at `docs/superpowers/specs/2026-04-14-discuss-plan-implement-design.md`. It provides three slash commands for a bilateral discuss → plan → implement workflow, with Phase C execution using Claude Code's native Team feature for implementer + advisor/fixer GAN-style verification.

**Architecture:** A Claude Code plugin consisting of `plugin.json`, three command `.md` files (each is a complete prompt for its respective slash command), a README, and a registration entry in `.claude-plugin/marketplace.json`. No code execution — the plugin is entirely declarative markdown + JSON. "Testing" is limited to JSON validation and file-existence checks; functional testing happens at runtime when a user invokes the commands.

**Tech Stack:** Markdown, JSON. No runtime dependencies. Claude Code plugin format v1.

**Note on TDD:** This plan does not follow strict TDD because the artifacts are static declarative files (markdown prompts + JSON manifests), not executable code. Each task produces one file; verification is structural (JSON valid, file exists, frontmatter parseable) rather than behavioral (assertion-based tests). The functional "test" of this plugin is a manual smoke-test run through all three commands, which is covered in Task 8.

---

## File Structure

Files to create or modify, relative to the repo root `/Users/work1618/.superset/worktrees/_mararn1618-claude-marketplace/mararn1618-discuss_plan_implement/`:

| Path | Purpose |
|---|---|
| `discuss-plan-implement/.claude-plugin/plugin.json` | Plugin manifest |
| `discuss-plan-implement/commands/discuss.md` | `/discuss` command prompt |
| `discuss-plan-implement/commands/create-plan.md` | `/create-plan` command prompt |
| `discuss-plan-implement/commands/implement-plan.md` | `/implement-plan` command prompt |
| `discuss-plan-implement/README.md` | Usage docs |
| `.claude-plugin/marketplace.json` | Add registration entry for the new plugin |

---

## Task 1: Create plugin skeleton and manifest

**Files:**
- Create dir: `discuss-plan-implement/.claude-plugin/`
- Create dir: `discuss-plan-implement/commands/`
- Create: `discuss-plan-implement/.claude-plugin/plugin.json`

- [ ] **Step 1: Create directories**

```bash
mkdir -p discuss-plan-implement/.claude-plugin discuss-plan-implement/commands
```

- [ ] **Step 2: Write plugin.json**

File `discuss-plan-implement/.claude-plugin/plugin.json`:

```json
{
  "name": "discuss-plan-implement",
  "version": "0.1.0",
  "description": "Minimal discuss -> plan -> implement workflow for one story at a time. Phase C uses Claude Code Teams for parallel implementers and a clean-context advisor/fixer GAN verification loop.",
  "author": {
    "name": "Markus Arndt"
  }
}
```

- [ ] **Step 3: Validate JSON**

Run: `jq . discuss-plan-implement/.claude-plugin/plugin.json`
Expected: valid JSON output, exit code 0.

---

## Task 2: Write `commands/discuss.md`

**Files:**
- Create: `discuss-plan-implement/commands/discuss.md`

- [ ] **Step 1: Write the command prompt**

File `discuss-plan-implement/commands/discuss.md`:

````markdown
---
description: "Bilateral alignment conversation for one story. Writes a discussion summary to docs/discussions/YYYY-MM-DD-<slug>.md. No code is written in this phase."
model: opus
---

# /discuss

You are in the **discussion phase** of the `discuss-plan-implement` workflow.

## Purpose

Reach alignment with the human on what to build before any code is written. Reading existing files is fine; writing code is not.

## Rules

1. **Do not write any code.** Reading existing files is fine, but no edits, no new files, no commits.
2. **Ask 1-2 clarifying questions at a time** — not a wall of ten questions.
3. **Invite the human to ask questions back.** At least once, say something like: "Anything I should clarify about my approach?"
4. **Surface assumptions explicitly.** "I'm assuming X. Is that correct?"
5. **Explore alternatives at forks.** "We could approach this as A or B — here's the tradeoff."
6. **Proactively gather context.** Before asking questions, use `Glob`, `Grep`, `Read` to understand project structure, find files relevant to the topic, and check existing patterns.

## Flow

1. Read the human's topic / story description from their message.
2. **Context gathering:** scan the project and read files relevant to the topic. Questions should be informed by actual code.
3. Ask 1-2 focused clarifying questions.
4. Iterate with the human until alignment is reached. Let them ask you questions too.
5. When alignment is reached (e.g., human says "looks good", "let's plan this", or explicitly asks to move on), write the discussion file.

## Output

Write to `docs/discussions/YYYY-MM-DD-<slug>.md` where:
- `YYYY-MM-DD` is today's date.
- `<slug>` is a kebab-case summary of the story (e.g., `add-jwt-auth`).

Create the `docs/discussions/` directory if it does not exist.

**File format (exact structure):**

```markdown
---
story: "<one-line story statement>"
created: <YYYY-MM-DD>
---

# Discussion: <topic>

## Intent
<1-3 sentences: what the human wants and why>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>

## Key Decisions
- <decision + rationale>

## Constraints
- <technical, business, or scope constraints surfaced>

## Out of Scope
- <explicitly excluded>

## Open Questions
- <anything unresolved — omit this section if there are none>
```

The `Acceptance Criteria` and `Out of Scope` sections flow verbatim into the plan in the next phase, so write them in the exact format shown.

## Exit

After writing the file, tell the human:

> Discussion written to `docs/discussions/<filename>.md`.
> Ready for `/discuss-plan-implement:create-plan` when you are.

Stop. Do not invoke the next phase — the human decides.
````

- [ ] **Step 2: Verify file exists and has frontmatter**

Run: `head -5 discuss-plan-implement/commands/discuss.md`
Expected output starts with:
```
---
description:
```

---

## Task 3: Write `commands/create-plan.md`

**Files:**
- Create: `discuss-plan-implement/commands/create-plan.md`

- [ ] **Step 1: Write the command prompt**

File `discuss-plan-implement/commands/create-plan.md`:

````markdown
---
description: "Turn a discussion summary into an executable plan with parallelism-annotated tasks. Writes to docs/plans/YYYY-MM-DD-<slug>.md."
model: opus
---

# /create-plan

You are in the **create-plan phase** of the `discuss-plan-implement` workflow.

## Purpose

Turn the most recent discussion summary into a concrete, executable plan with tasks annotated for parallel execution by sub-agent teammates.

## Flow

1. **Find the input discussion.** Look at `docs/discussions/` and load the most recent file (by filename date, newest first). If multiple files share the latest date, list them and ask the human which to use. If there are no discussion files, ask the human to run `/discuss-plan-implement:discuss` first or describe the story inline.

2. **Extract inherited sections.** Copy the following sections **verbatim** from the discussion into the plan — these are the single source of truth, do not paraphrase:
   - `Acceptance Criteria`
   - `Out of Scope`

3. **Gather technical context** as needed: file structure, dependencies, existing code patterns. Use `Glob`, `Grep`, `Read`.

4. **Draft tasks.** For each task, decide:
   - **Title** (concise, actionable)
   - **Group** (`A`, `B`, `C`, ...) — tasks in the same group run in parallel. Groups execute in order (A finishes, then B, then C).
   - **Depends on** (optional) — cross-group task references like `T1`, if a later task specifically needs a specific earlier task's output.
   - **Files** — exact paths that will be created or modified.
   - **Done when** — a specific verifiable condition.
   - **Description** — 1-3 sentences.

   **Be conservative with parallelism.** Only mark tasks as parallel when they are *obviously* independent (e.g., they touch different files). Sequential is safer. Race conditions waste time.

5. **Draft Advisor Checks** — additional checks the final advisor should verify, beyond acceptance criteria. Examples: "All tasks marked complete", "Tests pass: <command>", project-specific style rules.

6. **Write the plan file** to `docs/plans/YYYY-MM-DD-<slug>.md`. Use the same slug as the discussion file. Create the directory if needed. If a plan already exists for this slug, ask the human: overwrite or use a new slug.

7. **Present the plan inline** and ask the human to review. If changes are requested, edit the file and re-present.

8. Do NOT enter Claude Code plan mode. Plannotator is out of scope for v1.

## Output

File format (exact structure, frontmatter required):

```markdown
---
story: "<one-line story statement from discussion>"
discussion: docs/discussions/YYYY-MM-DD-<slug>.md
created: <YYYY-MM-DD>
max_advisor_rounds: 3
---

# Plan: <title>

**Story:** <one sentence from discussion>
**Discussion:** [<filename>](../discussions/<filename>)

## Acceptance Criteria
*(from discussion — final advisor verifies each)*

- [ ] <copied verbatim from discussion>

## Out of Scope
- <copied verbatim from discussion>

## Tasks
*(tasks with the same `group` run in parallel; groups run in order A -> B -> C)*

- [ ] **T1: <title>**
  - **Group:** A
  - **Files:** `<path>`
  - **Done when:** <verifiable condition>
  - <1-3 sentence description>

- [ ] **T2: <title>**
  - **Group:** A
  - **Files:** `<path>`
  - **Done when:** <verifiable condition>
  - <description>

- [ ] **T3: <title>**
  - **Group:** B
  - **Depends on:** T1
  - **Files:** `<path>`
  - **Done when:** <verifiable condition>
  - <description>

## Advisor Checks
*(clean-context advisor verifies, in addition to acceptance criteria)*

- [ ] All tasks marked complete
- [ ] <custom check>

## Progress Log
<!-- appended by /implement-plan -->
```

## Exit

After the human approves the plan, say:

> Plan written to `docs/plans/<filename>.md`.
> Ready for `/discuss-plan-implement:implement-plan` when you are.

Stop. Do not invoke the next phase — the human decides.
````

- [ ] **Step 2: Verify file exists and has frontmatter**

Run: `head -5 discuss-plan-implement/commands/create-plan.md`
Expected output starts with:
```
---
description:
```

---

## Task 4: Write `commands/implement-plan.md`

This is the most complex command. The prompt wires up two sequential Claude Code Teams using `TeamCreate`, spawns teammates via `Agent`, coordinates them via `SendMessage`, and cleans up via `TeamDelete`.

**Files:**
- Create: `discuss-plan-implement/commands/implement-plan.md`

- [ ] **Step 1: Write the command prompt**

File `discuss-plan-implement/commands/implement-plan.md`:

````markdown
---
description: "Execute an approved plan using two sequential Claude Code Teams: an Implementer team that writes code in parallel groups, then an Advisor team that does clean-context GAN-style verification via an Advisor<->Fixer loop."
model: opus
---

# /implement-plan

You are in the **implement-plan phase** of the `discuss-plan-implement` workflow. You are the **lead** of two sequential Claude Code Teams.

## Purpose

Execute the approved plan by:
- **Phase A:** Spawn an Implementer team that writes code in parallel by group.
- **Phase B:** Spawn a fresh Advisor team (clean context) that verifies the work via an Advisor<->Fixer GAN-style loop.
- **Phase C:** Report final status to the human.

## Role rules

- **You only orchestrate.** You do not write code yourself (that's the implementer team's job) and you do not verify code yourself (that's the advisor team's job).
- **You are the only writer to the plan file.** Teammates DM you when they finish; you edit the plan to mark `[x]` and append to Progress Log. This avoids race conditions.
- **Teams must be cleaned up on exit**, even on errors. Always call `TeamDelete` before exiting a phase.

## Step 0 — Load and parse the plan

1. List `docs/plans/` and load the most recent plan file by filename date. If multiple share the latest date, list them and ask the human which to use.
2. Parse the YAML frontmatter and body. Extract:
   - `story`
   - `discussion` (path for reference)
   - `max_advisor_rounds` (default 3)
   - Task list (title, group, depends_on, files, done-when, checkbox state)
   - Acceptance Criteria
   - Advisor Checks
3. **Resumption:** If the Progress Log already has entries from a prior run, this is a resumption. Start from the first unchecked task in the first unfinished group.

## Step 1 — Phase A: Implementer team

### 1a. Create team

Use `TeamCreate` with `team_name` = `dpi-impl-<YYYYMMDD-HHMM>` and description referencing the plan file.

### 1b. Execute groups sequentially (A -> B -> C ...)

For each group that has unchecked tasks:

1. **Spawn all teammates in the current group in a single message (parallel tool calls)** using the `Agent` tool with `team_name` set to the team created above. Use `name` = `impl-T<n>`. Use `subagent_type` = `general-purpose` (it has Read/Write/Edit/Bash).

2. **Teammate prompt template** (substitute the bracketed values):

   ```
   You are an implementer teammate named `impl-T<n>` on team `<team_name>`. Your job is to complete a single task from the plan.

   Task: T<n> - <title>
   Files to create or modify: <files>
   Done when: <done-when condition>

   Description:
   <description from plan>

   Plan file: <plan file path>
   Discussion file (for context only): <discussion file path>
   Story: <story>

   RULES:
   - Only modify files listed in "Files". Do not touch anything else.
   - Do NOT edit the plan file. Only the lead updates the plan.
   - If you need something from another teammate (their output or coordination), DM them by name via SendMessage. Only do this if the plan explicitly has a dependency.
   - When done, verify the Done-when condition is met. Then DM the lead with: "Task T<n> complete: <one-line summary of what you did>".
   - If blocked, DM the lead with: "Task T<n> blocked: <reason>".

   Do not read files outside your scope unnecessarily — it wastes context.

   Begin.
   ```

3. **Wait for completion messages.** Monitor your inbox for messages from each `impl-T<n>` teammate. Messages starting with "Task T<n> complete:" mean success; "Task T<n> blocked:" means failure.

### 1c. Handle each completion message

When a teammate reports completion:
- Edit the plan file: change that task's `- [ ]` to `- [x]`.
- Append to Progress Log: `- <ISO timestamp> — T<n>: <summary from teammate>`.

When a teammate reports blocked:
- Spawn a fresh teammate for the same task (retry once). If it also reports blocked:
  - Mark the task with `⚠️` instead of `[x]` in the plan.
  - Append to Progress Log: `- <ISO timestamp> — T<n>: BLOCKED — <reason>`.
  - Continue with remaining tasks in the group.

### 1d. Advance groups

When all teammates in the current group have reported (or been skipped), move to the next group. Repeat 1b-1c.

### 1e. Shut down implementer team

After all groups are processed:
- DM all remaining teammates: `{"type": "shutdown_request"}` via SendMessage.
- Call `TeamDelete`.

## Step 2 — Phase B: Advisor team (clean context)

### 2a. Create fresh team

`TeamCreate` with `team_name` = `dpi-advisor-<YYYYMMDD-HHMM>`. This team starts with clean context — it knows nothing about implementer chatter.

### 2b. Spawn Advisor teammate

Use `Agent` with `team_name` set, `name` = `advisor`, `subagent_type` = `general-purpose`.

**Advisor prompt template:**

```
You are the Advisor on team `<team_name>`. Your only job is to review the code against the plan's verification criteria and find problems.

Plan file: <plan file path>
Discussion file (for context on acceptance criteria): <discussion file path>

YOUR ROLE:
1. Read the plan file. Extract these verification sources:
   - `Acceptance Criteria` (top-level section)
   - Per-task `Done when` conditions
   - `Advisor Checks` section
2. For each criterion, verify it against the current code state using Read/Grep/Bash.
3. Do a code-quality review: correctness, bugs, edge cases, obvious issues.
4. Compile findings.

VERIFICATION LOOP (max <max_advisor_rounds> rounds; you track the round counter):
- Round 1: Scan everything. If all checks pass, DM the lead: "APPROVED: all checks pass" and stop.
- If issues found, DM your teammate `fixer` with a numbered list of issues. Each issue must be specific: file path, line number (if applicable), what's wrong, what should be there instead. Wait for fixer's response.
- On fixer's response: Re-scan only the items you flagged. If all now pass, check for any other issues, then DM lead: "APPROVED: <one-line summary of what was fixed>". Stop.
- If still issues, DM fixer with the remaining issues (numbered fresh). Increment your round counter.
- If your round counter exceeds <max_advisor_rounds>, DM lead: "MAX ROUNDS EXCEEDED: <newline-separated list of unresolved issues>". Stop.

Be skeptical. Do not approve work that doesn't meet the criteria. Do not gaslight yourself into believing issues are minor if they violate an acceptance criterion.
```

### 2c. Spawn Fixer teammate

Use `Agent` with `team_name` set, `name` = `fixer`, `subagent_type` = `general-purpose`.

**Fixer prompt template:**

```
You are the Fixer on team `<team_name>`. Your only job is to take the Advisor's findings and edit code to address them.

Plan file: <plan file path>

YOUR ROLE:
- Wait for a DM from `advisor` with a numbered list of issues.
- For each issue, edit the relevant file to fix it. Be surgical: only address the issue, do not refactor or expand scope.
- When done, DM advisor back: "Fixed issues 1, 2, 3: <brief summary of each fix>".
- Do not DM the lead. Only communicate with advisor.
- Do not modify the plan file.
- Do not make changes beyond what advisor requested.
- If an advisor issue is ambiguous, make a best-effort fix and note the assumption in your response.
- If you genuinely cannot fix something (e.g., missing dependency, test infrastructure not present), DM advisor back: "Cannot fix issue N: <reason>". Advisor will decide whether to escalate to MAX ROUNDS EXCEEDED.
```

### 2d. Wait for final verdict

Monitor your inbox for a DM from `advisor`. Expected outcomes:
- `"APPROVED: <summary>"` — loop completed successfully.
- `"MAX ROUNDS EXCEEDED: <unresolved issues>"` — loop exhausted.

### 2e. Update plan with verdict

- On **APPROVED**: append to Progress Log: `- <ISO timestamp> — Advisor APPROVED: <summary>`. Check off each `Advisor Checks` bullet and each `Acceptance Criteria` bullet.
- On **MAX ROUNDS EXCEEDED**: append to Progress Log: `- <ISO timestamp> — Advisor MAX ROUNDS EXCEEDED:\n<newline-indented list of unresolved issues>`. For each unresolved item, find the matching Acceptance Criterion or Advisor Check and change its `- [ ]` to `- [⚠️]`.

### 2f. Shut down advisor team

- DM remaining teammates: `{"type": "shutdown_request"}` via SendMessage.
- Call `TeamDelete`.

## Step 3 — Phase C: Report to human

Output a summary. Format:

> **Implementation complete for story "<story>".**
>
> - Tasks: <n>/<total> completed (<n> blocked with ⚠️)
> - Advisor: <APPROVED on round <r> | MAX ROUNDS EXCEEDED>
>   - <brief note on what was fixed or what remains unresolved>
> - Plan: `docs/plans/<filename>.md`
>
> Review the plan file for the full trail.

## Error recovery

- If `TeamCreate` fails at any point, abort the phase, report the error to the human, and stop.
- If a teammate becomes unresponsive (no message within a reasonable window), retry once with a fresh teammate. If still unresponsive, mark the task `⚠️` and continue.
- On any unexpected error, ensure any active team is deleted via `TeamDelete` before exiting.
````

- [ ] **Step 2: Verify file exists and has frontmatter**

Run: `head -5 discuss-plan-implement/commands/implement-plan.md`
Expected output starts with:
```
---
description:
```

---

## Task 5: Write `README.md`

**Files:**
- Create: `discuss-plan-implement/README.md`

- [ ] **Step 1: Write README**

File `discuss-plan-implement/README.md`:

````markdown
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
````

- [ ] **Step 2: Verify file exists**

Run: `test -f discuss-plan-implement/README.md && echo OK`
Expected: `OK`

---

## Task 6: Register plugin in `marketplace.json`

**Files:**
- Modify: `.claude-plugin/marketplace.json` — append new entry to the `plugins` array

- [ ] **Step 1: Read current marketplace.json**

Use the Read tool to read `.claude-plugin/marketplace.json`. Note the current structure: it contains a `plugins` array.

- [ ] **Step 2: Append the new plugin entry**

Use the Edit tool to add a new entry to the `plugins` array. Find the last entry (currently `mararn1618-kleinanzeigen`) and add after it:

```json
    {
      "name": "discuss-plan-implement",
      "source": "./discuss-plan-implement",
      "description": "Minimal discuss -> plan -> implement workflow for one story at a time. Phase C uses Claude Code Teams for parallel implementers and a clean-context advisor/fixer GAN verification loop.",
      "version": "0.1.0"
    }
```

Make sure to add a comma after the previous entry's closing `}` and no trailing comma after the new entry (since it will be the last one).

- [ ] **Step 3: Validate JSON**

Run: `jq . .claude-plugin/marketplace.json`
Expected: valid JSON output, exit code 0, with the new entry visible.

- [ ] **Step 4: Verify version consistency**

Run:
```bash
jq -r '.plugins[] | select(.name == "discuss-plan-implement") | .version' .claude-plugin/marketplace.json
jq -r '.version' discuss-plan-implement/.claude-plugin/plugin.json
```
Expected: both output `0.1.0`.

---

## Task 7: Final structural validation

- [ ] **Step 1: Verify all plugin files exist**

Run:
```bash
ls -la discuss-plan-implement/.claude-plugin/plugin.json \
       discuss-plan-implement/commands/discuss.md \
       discuss-plan-implement/commands/create-plan.md \
       discuss-plan-implement/commands/implement-plan.md \
       discuss-plan-implement/README.md
```
Expected: all 5 files listed with non-zero size.

- [ ] **Step 2: Verify each command file has valid frontmatter**

Run:
```bash
for f in discuss-plan-implement/commands/*.md; do
  echo "=== $f ==="
  head -4 "$f"
done
```
Expected: each file starts with `---\ndescription: ...`.

- [ ] **Step 3: Verify both JSON files are still valid**

Run:
```bash
jq . discuss-plan-implement/.claude-plugin/plugin.json > /dev/null && echo "plugin.json OK"
jq . .claude-plugin/marketplace.json > /dev/null && echo "marketplace.json OK"
```
Expected: `plugin.json OK` and `marketplace.json OK`.

---

## Task 8: Manual smoke test guidance (for the human, not executed by the plan)

**Note:** This is not an automated task; it's documentation for the human on how to verify the plugin works end-to-end after installation. Skip in automated execution.

After the plugin is installed in a Claude Code session:

1. `/discuss-plan-implement:discuss` with a toy story ("add a debug logger to foo.ts"). Verify that the assistant asks questions, does not write code, and eventually produces a file at `docs/discussions/YYYY-MM-DD-add-debug-logger.md` with the right structure.
2. `/discuss-plan-implement:create-plan`. Verify it loads the discussion, asks for review, and produces a plan file with the right frontmatter and task format.
3. `/discuss-plan-implement:implement-plan`. Verify:
   - `TeamCreate` is called for `dpi-impl-*`
   - Implementer teammates are spawned in parallel per group
   - Teammates report back via `SendMessage`
   - The plan file is updated with `[x]` marks and Progress Log entries
   - `TeamDelete` is called and no orphaned team directories remain in `~/.claude/teams/`
   - A second team `dpi-advisor-*` is created
   - Advisor and fixer teammates are spawned
   - Final verdict reaches the lead
   - The plan file has the final verdict in Progress Log
   - Everything is cleaned up

---

## Task 9: Commit the plugin

**Files:**
- Stage: spec, plan, plugin files, marketplace.json

- [ ] **Step 1: Review what will be committed**

Run: `git status`
Expected files (new):
- `docs/superpowers/specs/2026-04-14-discuss-plan-implement-design.md`
- `docs/superpowers/plans/2026-04-14-discuss-plan-implement.md`
- `discuss-plan-implement/.claude-plugin/plugin.json`
- `discuss-plan-implement/commands/discuss.md`
- `discuss-plan-implement/commands/create-plan.md`
- `discuss-plan-implement/commands/implement-plan.md`
- `discuss-plan-implement/README.md`

Expected files (modified):
- `.claude-plugin/marketplace.json`

- [ ] **Step 2: Stage specific files**

Run:
```bash
git add docs/superpowers/specs/2026-04-14-discuss-plan-implement-design.md
git add docs/superpowers/plans/2026-04-14-discuss-plan-implement.md
git add discuss-plan-implement/
git add .claude-plugin/marketplace.json
```

- [ ] **Step 3: Commit**

Use HEREDOC format for commit message.

Run:
```bash
git commit -m "$(cat <<'EOF'
feat(discuss-plan-implement): v0.1.0 -- 3-command bilateral workflow plugin

Adds a minimal discuss -> plan -> implement workflow plugin for
one-story interactive work. Phase A runs an Implementer team
(parallel tasks by group). Phase B runs a fresh-context Advisor
team with an Advisor<->Fixer GAN-style loop for verification.
Co-exists with ralph (long-running) and create-markdown-plan
(plan format reference).

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 4: Verify commit**

Run: `git log --oneline -1`
Expected: shows the new commit with message starting "feat(discuss-plan-implement)".

---

## Self-review checklist

Coverage check against spec §3, §4, §5, §6, §7:

- [x] Plugin structure (§3) → Task 1 creates dirs + plugin.json
- [x] Discussion file format (§4) → Task 2's discuss.md prompt specifies it verbatim
- [x] Plan file format (§4) → Task 3's create-plan.md prompt specifies it verbatim
- [x] `/discuss` semantics (§5) → Task 2
- [x] `/create-plan` semantics (§5) → Task 3
- [x] `/implement-plan` semantics including Team creation, parallel groups, Advisor<->Fixer loop (§5) → Task 4
- [x] Error handling (§6) → Task 4 includes teammate failure retry, TeamCreate abort, max rounds marking
- [x] Recovery (§6) → Task 4 Step 0 includes resumption logic reading existing Progress Log
- [x] Out of scope (§7) → Tasks 2-4 explicitly do not include hooks, SessionStart, plan mode, etc.
- [x] Success criteria (§10) → Task 7 validates plugin structure; Task 8 documents manual smoke test; Task 9 commits
- [x] Marketplace registration and version consistency → Task 6

**No placeholders** — all file content is written inline in the plan. Every step has either a shell command or a complete file content block.
