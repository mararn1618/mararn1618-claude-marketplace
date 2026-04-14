---
description: "Turn any folder into a stateless, resumable Claude workspace. Scaffold CLAUDE.md + _archive/, create per-topic workstream folders with README/worklog/decisions/context/input, enforce write-to-disk discipline so sessions are interchangeable, and archive stale workstreams with user confirmation."
---

# Workstreams — Stateless, Resumable Work in a Folder

This skill turns a folder into a place where Claude can work on long-lived topics without depending on session context. Each topic ("workstream") is its own subfolder with a worklog, decision log, README, and dated inputs. A top-level `CLAUDE.md` lists all workstreams and forces every fresh session to load this skill before responding. If the session dies, a new one can pick up from disk alone.

## When to use this skill

- You are in a folder that already contains a `CLAUDE.md` gate pointing at this skill. The gate is mandatory — you must follow the runtime protocol below.
- The user asks you to scaffold a new workstreams folder.
- The user asks to start, resume, switch, or archive a workstream.
- The user hands over an input file (transcript, email, screenshot, etc.) in a workstreams folder — it must be saved per the input rules below.

## When NOT to use

- Trivial one-off questions or chitchat in a workstreams folder — skip the workstream logic, answer directly. Do not create a workstream for "what time is it".
- Folders that do not contain a `CLAUDE.md` gate pointing at this skill. Do not unilaterally scaffold — ask first.

## Scaffold action (set up a new workstreams folder)

Use when the user asks to scaffold a workstreams folder, OR when the current folder has no `CLAUDE.md` and the user confirms they want it scaffolded.

1. Create `_archive/` at the root (empty directory, use a `.gitkeep` file so git tracks it).
2. Create `CLAUDE.md` at the root with the exact template below, substituting nothing except what the template says to substitute.
3. Report what was created and stop. Do not create any workstream yet — wait for the user to describe a topic first.

### CLAUDE.md template (write this verbatim)

```markdown
# Workstreams Folder

> **BEFORE your first response in this folder, you MUST invoke the `mararn1618-workstreams` skill via the Skill tool. This is non-negotiable. The skill contains the protocol for how work in this folder happens — you cannot respond correctly without it.**

## About this folder

This folder uses the `mararn1618-workstreams` skill. Each topic lives as its own workstream directory with a README, worklog, decisions log, and dated inputs. The `_archive/` folder holds stale workstreams. When you load the skill, follow the runtime protocol exactly — it assumes the session may die at any time and that all state lives on disk.

## Active workstreams

_(none yet — add entries as workstreams are created)_

## Archived (_archive/)

_(none yet)_
```

### Verification after scaffolding

- `ls -la` at the root shows `CLAUDE.md` and `_archive/`.
- `cat CLAUDE.md` shows the gate paragraph at the top.
- Report to the user: "Scaffolded the folder. Next time you start a session here, the gate will force the skill to load. Tell me about the first topic you want to work on and I'll create a workstream for it."

## Workstream folder layout

Every workstream is a sibling directory at the root of the workstreams folder. The layout is:

```
YYYY-MM-<topic-slug>/
├── README.md          # description, goals, optional non-goals (user-owned)
├── worklog.md         # append-only, one ISO-timestamped line per entry
├── decisions.md       # append-only, 2-4 line entries
└── context/input/     # user-provided inputs, filename-prefixed with YYYY-MM-DD_
```

### Naming rules

- Folder name: `YYYY-MM-<slug>/`. Year-month prefix is the month the workstream was created, based on today's date at the time of creation. Slug is lowercase, hyphen-separated, derived from the topic. Ask the user to confirm the slug before creating.
- No `workstream_` or other prefix — the root folder contains only workstreams, `_archive/`, and `CLAUDE.md`, so the prefix would be redundant.
- Input filenames: `YYYY-MM-DD_<original-name>.<ext>`. Date is the date the input was handed over (today, when saving). Preserve the original extension.

### File roles

**`README.md`** — canonical description of the workstream. Structure:

```markdown
# <Topic title>

## Description

Short paragraph describing what this workstream is about.

## Goals

- First goal
- Second goal

## Non-goals (optional)

- Explicit thing this workstream is NOT about
```

The README is **user-owned**. You may propose updates but must not silently rewrite it. See the discipline rules below.

**`worklog.md`** — append-only diary. Header at top is `# Worklog`. Each entry is one line, ISO-timestamped, starting with `- `. Example:

```markdown
# Worklog

- 2026-04-14T10:23Z — created workstream, stubbed README with goal: investigate latency regression
- 2026-04-14T10:41Z — ran `./bench.sh`, baseline saved to ./out/baseline.csv
- 2026-04-14T10:55Z — user clarified scope: only EU markets, not NA
```

The ISO timestamp format is `YYYY-MM-DDTHH:MMZ` (UTC, minute precision — seconds are noise). If you do not know the current time, read it from the environment (`date -u +%Y-%m-%dT%H:%MZ`) before writing the entry.

**`decisions.md`** — append-only decision log. Header at top is `# Decisions`. Each entry is a `## YYYY-MM-DD — <decision headline>` section followed by one to three short lines of rationale. Example:

```markdown
# Decisions

## 2026-04-14 — use Postgres, not SQLite
Multi-user access is in scope. SQLite's writer lock would block the second user. Postgres adds an ops dependency but it is already part of the stack.
```

**`context/input/`** — every file the user hands over lands here, prefixed with the date: `YYYY-MM-DD_<original-name>.<ext>`. This applies to transcripts, emails, screenshots, PDFs, anything. Do not drop inputs in the workstream root or elsewhere.

No `context/output/` folder in v1. Generated artifacts (source code, reports) land wherever the task naturally puts them. The worklog records what was produced and where, so a fresh session can find it.

## Runtime protocol — on the first user message of a session

Follow these steps in order. Do not skip.

1. **Read `CLAUDE.md`** at the root of the workstreams folder. Pay attention to the Active workstreams and Archived sections.

2. **Triviality check.** If the user's message is a quick factual question, chitchat, or otherwise has no continuation and does not touch any existing workstream topic, skip workstream logic entirely and answer directly. Do not create a workstream for trivial things. Examples of trivial: "what time is it?", "hi", "can you explain regex?". Examples of non-trivial: "let's continue the latency work", "I got a transcript from the meeting with Alex", "I want to start figuring out X".

3. **Topic match.** If non-trivial, scan the Active workstreams index for plausible matches with the user's topic. Look at the slugs and the one-line hooks.

4. **Confirm before acting.**
   - If one workstream plausibly matches: ask the user in plain language, *"Is this about the `<slug>` workstream?"*. Wait for confirmation. Do not assume.
   - If nothing plausibly matches but the topic seems substantial: ask the user, *"This looks like a new topic. Should I start a new workstream for it?"*. Wait for confirmation.
   - If the user's message explicitly names an archived workstream: ask whether they want to revive it from `_archive/` or keep it archived and branch a new workstream.

5. **On confirmed existing workstream:** read the workstream's `README.md` in full, read the tail (last ~30 lines) of `worklog.md`, and read `decisions.md` in full. Then proceed with the user's request using that loaded context.

6. **On confirmed new workstream:**
   a. Ask the user for a short slug (lowercase, hyphen-separated).
   b. Compute today's `YYYY-MM` prefix and create the folder `YYYY-MM-<slug>/`.
   c. Ask the user for a short description and at least one goal (and optional non-goals) — write these into `README.md` using the template in the Workstream folder layout section.
   d. Create empty `worklog.md` and `decisions.md` with just their `# Worklog` / `# Decisions` headers.
   e. Create `context/input/` (empty directory — use `.gitkeep` if the folder is under git).
   f. Update `CLAUDE.md`: add the new workstream to the Active workstreams list with a one-line hook (one sentence summarizing the topic).
   g. Append the first worklog entry: `- <ISO timestamp> — created workstream`.
   h. Report to the user what was created.

7. **Archive check.** After steps 1–6, check every active workstream's `worklog.md` mtime. If any are older than 30 days, surface a single prompt: *"These workstreams haven't been touched in >30 days: X, Y, Z. Archive them? [y/N]"*. Do this at most once per session and only at session start. If the user says yes, follow the Archiving action section for each.

### How to check mtimes

Run (the skill consumer — i.e. you — runs this when needed):
```bash
find . -maxdepth 3 -name worklog.md -mtime +30 -not -path "./_archive/*"
```
Each path printed is a stale workstream. Stale threshold is 30 days — if you want to change it, edit this number in your local copy of this skill.

## Runtime protocol — discipline rules (rigid, non-negotiable)

These rules apply during work, on every turn. They are the reason a fresh session can pick up where an old one left off. Do not rationalise skipping them.

### Rule 1 — `worklog.md`: append after every state-changing turn, before ending the turn

A turn is "state-changing" if any of these are true:

- You ran a command (shell, tool) that modified something on disk, in git, or in an external system.
- You or the user made a decision (even a small one).
- You learned something new from the user's message that affects the work (scope, constraint, preference, fact).
- You completed a task or sub-task.

When a turn is state-changing, append one line to `worklog.md` **before you finish responding**, in this format:

```
- <ISO timestamp> — <one short sentence>
```

One line. No paragraphs. If the thing is complex, split it into multiple lines but keep each line short.

**Red flags — if you catch yourself thinking any of these, STOP and write the entry now:**

| Thought | Reality |
|---|---|
| "I'll note this in the worklog at the end of the task" | The session can die before "the end of the task". Write now. |
| "This change is too small to log" | Small changes are the ones that get lost. Write now. |
| "I'll batch several entries into one" | Batching loses the order and the timestamps. One line per event. |
| "The user can see what I did from my response" | They can't, in a fresh session. Write now. |
| "I already mentioned it in my message" | Your message is not on disk. The worklog is. Write now. |

### Rule 2 — `decisions.md`: append on every non-trivial choice

Whenever you or the user picks between alternatives in a way that will affect future work, append an entry to `decisions.md`. Format:

```markdown
## YYYY-MM-DD — <decision headline>
<1–3 short lines of rationale — why this, not the alternative>
```

A "non-trivial choice" is one where, three months from now, a fresh session would benefit from knowing *why* this path was taken. Examples: choosing a library, scoping a feature in or out, committing to a data format, deciding not to do something. Not everything is a decision — "I'll use the same indentation style as the file" is not.

### Rule 3 — `README.md`: propose changes, never silently rewrite

The README is user-owned. It is the first file a fresh session reads and it must stay trustworthy.

- If the stated goals or scope in the README still match what you are doing, leave it alone.
- If you notice reality has drifted from the README (e.g. the README says the goal is X but you have been working on Y for several turns, or the user has explicitly redirected scope), surface this to the user with a specific proposal:
  *"The README still says the goal is X, but we've been working on Y. Want me to update the goals section to say `<proposed text>`?"*
- Only write to `README.md` after the user confirms. Then append a worklog entry recording the update.

### Rule 4 — `context/input/`: every handed-over file gets a dated filename

When the user hands you a file (paste, attachment, explicit "save this"), save it to `<workstream>/context/input/` with the filename prefixed `YYYY-MM-DD_`. Use today's date. Preserve the original name and extension after the prefix. Example: user sends `meeting_notes.txt` on 2026-04-14 → save as `2026-04-14_meeting_notes.txt`.

Do not drop inputs in the workstream root, in `context/`, or anywhere else. Do not rename the original portion of the filename beyond prefixing the date.

After saving, append a worklog entry: `- <ISO ts> — saved input ./context/input/<dated-filename>`.

### Rule 5 — Workstream switching: treat as a conscious reset

When the user switches from workstream A to workstream B within the same session, you **must** treat it as a reset. This rule exists because mid-session context clearing (`/clear`) is not available in every interface channel — for example, in the Discord plugin, the user cannot send harness commands. The skill must work correctly regardless.

On a switch:

1. Before leaving A: make sure A's worklog and any pending decisions are written.
2. Re-read B's `README.md` in full.
3. Tail B's `worklog.md`.
4. Read B's `decisions.md` in full.
5. Do not carry A's working state into B's turns. If something from A becomes relevant later, look it up from A's on-disk files — do not recall it from the conversation window.

Assume you have to earn B's context from disk, not from memory. If you catch yourself answering a B question using facts you remember from A without checking the files, stop and check the files.
