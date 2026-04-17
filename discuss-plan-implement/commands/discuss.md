---
description: "Bilateral alignment conversation for one story. Writes a discussion summary to docs/discussions/YYYY-MM-DD_HH-MM_<slug>.md. No code is written in this phase."
model: opus
---

# /discuss

You are in the **discussion phase** of the `discuss-plan-implement` workflow.

## Purpose

Reach **complete** alignment with the human on what to build before any code is written. "Complete" means no silent gaps, no unstated assumptions, and no unresolved contradictions between what the human said and what the code/context implies.

Your job in this phase is to actively hunt for:
- **Missing scenarios** the human hasn't mentioned (edge cases, error paths, adjacent features the change will touch).
- **Contradictions** between parts of the request, or between the request and what you see in the code.
- **Gaps where you'd otherwise guess** — places you'd need to make a judgment call without the human's input.

Surface each of these explicitly and get a human answer. Reading existing files is fine; writing code is not.

**Scale the effort to the complexity of the topic.** A one-line fix or a rename doesn't need a scenario expedition — one or two sanity checks are enough. A cross-cutting change, a new feature, or anything touching shared state deserves real gap-hunting. Err on the side of more questions when the blast radius is large, fewer when it's obviously contained.

## Rules

1. **Do not write any code.** Reading existing files is fine, but no edits, no new files, no commits.
2. **Ask 1-2 clarifying questions at a time** — not a wall of ten questions.
3. **Invite the human to ask questions back.** At least once, say something like: "Anything I should clarify about my approach?"
4. **Surface assumptions explicitly.** "I'm assuming X. Is that correct?"
5. **Explore alternatives at forks.** "We could approach this as A or B — here's the tradeoff."
6. **Hunt for gaps and contradictions, don't just confirm the happy path.** After context gathering, ask yourself: what scenarios has the human not mentioned? Where does the request contradict the code or itself? Where would I guess if forced to act now? Raise those explicitly, scaled to the complexity of the topic.
7. **Proactively gather context.** Before asking questions, use `Glob`, `Grep`, `Read` to understand project structure, find files relevant to the topic, and check existing patterns.

## Flow

1. Read the human's topic / story description from their message.
2. **Context gathering:** scan the project and read files relevant to the topic. Questions should be informed by actual code.
3. Ask 1-2 focused clarifying questions.
4. Iterate with the human until alignment is reached. Let them ask you questions too.
5. When alignment is reached (e.g., human says "looks good", "let's plan this", or explicitly asks to move on), write the discussion file.

## Output

Write to `docs/discussions/YYYY-MM-DD_HH-MM_<slug>.md` where:
- `YYYY-MM-DD` is today's date.
- `HH-MM` is current local hour and minute (24h, hyphen-separated).
- `<slug>` is a snake_case summary of the story (e.g., `add_jwt_auth`).

Example: `2026-04-17_13-26_add_jwt_auth.md`.

Create the `docs/discussions/` directory if it does not exist.

**File format (exact structure):**

```markdown
---
story: "<one-line story statement>"
created: <YYYY-MM-DD HH:MM>
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
