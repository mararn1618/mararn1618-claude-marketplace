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
