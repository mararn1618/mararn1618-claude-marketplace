---
description: "Turn a discussion summary into an executable plan with parallelism-annotated tasks. Writes to docs/plans/YYYY-MM-DD_HH-MM_<slug>.md."
model: opus
---

# /create-plan

You are in the **create-plan phase** of the `discuss-plan-implement` workflow.

## Purpose

Turn the most recent discussion summary into a concrete, executable plan with tasks annotated for parallel execution by sub-agent teammates.

## Flow

1. **Find the input discussion.** Look at `docs/discussions/` and load the most recent file (by filename date+time, newest first — filenames sort lexicographically in chronological order). If multiple files tie, list them and ask the human which to use. If there are no discussion files, ask the human to run `/discuss-plan-implement:discuss` first or describe the story inline.

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

6. **Write the plan file** to `docs/plans/YYYY-MM-DD_HH-MM_<slug>.md` using the current local date+time and the same `<slug>` as the discussion file. Create the directory if needed. If a plan already exists for this slug (check `docs/plans/*_<slug>.md`), ask the human: overwrite the existing one or write a new timestamped file alongside it.

7. **Present the plan inline** and ask the human to review. If changes are requested, edit the file and re-present.

8. Do NOT enter Claude Code plan mode. Plannotator is out of scope for v1.

## Output

File format (exact structure, frontmatter required):

```markdown
---
story: "<one-line story statement from discussion>"
discussion: docs/discussions/YYYY-MM-DD_HH-MM_<slug>.md
created: <YYYY-MM-DD HH:MM>
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
