# mararn1618-workstreams Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a marketplace plugin `mararn1618-workstreams` (v0.1.0) that turns any folder into a stateless, resumable Claude Code workspace via an on-disk worklog, decision log, README, dated inputs, and a self-maintained `CLAUDE.md` index.

**Architecture:** Pure instructional skill — no executable code. The deliverable is a set of markdown/JSON files (`plugin.json`, `SKILL.md`) that tell Claude how to scaffold a folder, create/resume workstreams, enforce the worklog/decisions discipline, and archive stale workstreams. The protocol runs entirely through Claude's normal file tools.

**Tech Stack:** Markdown with YAML frontmatter, JSON (plugin manifest + marketplace registry). No build, no tests-as-code — verification is done by reading each section for unambiguity and by a manual end-to-end dry-run in a scratch folder.

**Spec:** `mararn1618-workstreams/DESIGN.md`

**Repo conventions (verified):**
- Plugin dir: `<plugin>/.claude-plugin/plugin.json` with `{name, version, description, author, repository}`
- Skill dir: `<plugin>/skills/<slug>/SKILL.md` with `description:` frontmatter
- Registration: append entry to `.claude-plugin/marketplace.json`, `version` must match `plugin.json`
- Skill slug for this plugin: `workstreams`
- Plugin fully-qualified name in the gate text: `mararn1618-workstreams`

---

## File Structure

```
mararn1618-workstreams/
├── DESIGN.md                                  # (already exists)
├── PLAN.md                                    # (this file)
├── .claude-plugin/
│   └── plugin.json                            # plugin manifest, v0.1.0
└── skills/
    └── workstreams/
        └── SKILL.md                           # runtime protocol + scaffold action
```

Also modified: `/Users/work1618/code/_mararn1618-claude-marketplace/.claude-plugin/marketplace.json` — append one entry.

Responsibilities:
- `plugin.json`: plugin identity + version. Small, static.
- `SKILL.md`: the skill body. Everything Claude needs to know to run the protocol. Written as sections with short imperative rules.
- `marketplace.json`: registry entry so the plugin is discoverable.

---

## Task 1: Create plugin manifest

**Files:**
- Create: `mararn1618-workstreams/.claude-plugin/plugin.json`

- [ ] **Step 1: Create the plugin directory structure**

Run:
```bash
mkdir -p mararn1618-workstreams/.claude-plugin mararn1618-workstreams/skills/workstreams
```

Expected: no output, both directories exist.

Verify:
```bash
ls -d mararn1618-workstreams/.claude-plugin mararn1618-workstreams/skills/workstreams
```
Expected: both paths listed.

- [ ] **Step 2: Write `plugin.json`**

File content (exact):
```json
{
  "name": "mararn1618-workstreams",
  "description": "Turn any folder into a stateless, resumable Claude workspace: per-topic workstream folders with worklog, decisions, dated inputs, and a self-maintained CLAUDE.md index. Kill the session anytime, resume from disk.",
  "version": "0.1.0",
  "author": {
    "name": "mararn1618"
  },
  "repository": "https://github.com/mararn1618/mararn1618-claude-marketplace"
}
```

- [ ] **Step 3: Verify JSON is valid and fields are correct**

Run:
```bash
python3 -c "import json; d=json.load(open('mararn1618-workstreams/.claude-plugin/plugin.json')); print(d['name'], d['version'])"
```
Expected output: `mararn1618-workstreams 0.1.0`

- [ ] **Step 4: Commit**

```bash
git add mararn1618-workstreams/.claude-plugin/plugin.json
git commit -m "feat(mararn1618-workstreams): add plugin manifest v0.1.0"
```

---

## Task 2: Write SKILL.md — frontmatter, title, overview

**Files:**
- Create: `mararn1618-workstreams/skills/workstreams/SKILL.md`

This task creates the file with just the opening sections so the skill is loadable and discoverable. Subsequent tasks append further sections.

- [ ] **Step 1: Write the initial SKILL.md**

File content (exact):
```markdown
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
```

- [ ] **Step 2: Verify frontmatter parses and file is well-formed**

Run:
```bash
head -3 mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: three lines — `---`, a `description:` line, `---`.

Run:
```bash
wc -l mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: a small number (file is just the opening sections, ~25 lines).

- [ ] **Step 3: Commit**

```bash
git add mararn1618-workstreams/skills/workstreams/SKILL.md
git commit -m "feat(mararn1618-workstreams): add SKILL.md frontmatter and overview"
```

---

## Task 3: Append scaffold action

**Files:**
- Modify: `mararn1618-workstreams/skills/workstreams/SKILL.md` (append section)

This section tells the skill how to set up a previously-unscaffolded folder.

- [ ] **Step 1: Append the scaffold section**

Append to end of `SKILL.md`:

````markdown

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
````

- [ ] **Step 2: Verify the appended section is present and the template is intact**

Run:
```bash
grep -n "## Scaffold action" mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: one match.

Run:
```bash
grep -c "BEFORE your first response" mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: `1` (the gate phrase appears exactly once — inside the template).

- [ ] **Step 3: Commit**

```bash
git add mararn1618-workstreams/skills/workstreams/SKILL.md
git commit -m "feat(mararn1618-workstreams): add scaffold action with CLAUDE.md template"
```

---

## Task 4: Append workstream folder layout section

**Files:**
- Modify: `mararn1618-workstreams/skills/workstreams/SKILL.md` (append)

- [ ] **Step 1: Append the folder layout section**

Append to end of `SKILL.md`:

````markdown

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
````

- [ ] **Step 2: Verify the section was added cleanly**

Run:
```bash
grep -n "^## " mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: shows the section headers in order — `When to use`, `When NOT to use`, `Scaffold action`, `Workstream folder layout`. (The `###` subheaders should not appear with this pattern.)

- [ ] **Step 3: Commit**

```bash
git add mararn1618-workstreams/skills/workstreams/SKILL.md
git commit -m "feat(mararn1618-workstreams): document workstream folder layout and file roles"
```

---

## Task 5: Append runtime protocol — session start

**Files:**
- Modify: `mararn1618-workstreams/skills/workstreams/SKILL.md` (append)

- [ ] **Step 1: Append the session-start section**

Append to end of `SKILL.md`:

````markdown

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
````

- [ ] **Step 2: Verify the section was added and the ordered steps are intact**

Run:
```bash
grep -n "^[0-9]\. \*\*" mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: 7 matches (steps 1–7 of the runtime protocol).

- [ ] **Step 3: Commit**

```bash
git add mararn1618-workstreams/skills/workstreams/SKILL.md
git commit -m "feat(mararn1618-workstreams): add session-start runtime protocol"
```

---

## Task 6: Append discipline rules — worklog, decisions, README, inputs, switching

**Files:**
- Modify: `mararn1618-workstreams/skills/workstreams/SKILL.md` (append)

These are the rigid rules that make on-disk state trustworthy.

- [ ] **Step 1: Append the discipline section**

Append to end of `SKILL.md`:

````markdown

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
````

- [ ] **Step 2: Verify all five rules are present**

Run:
```bash
grep -nE "^### Rule [1-5] —" mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: 5 matches, in order `Rule 1` through `Rule 5`.

- [ ] **Step 3: Commit**

```bash
git add mararn1618-workstreams/skills/workstreams/SKILL.md
git commit -m "feat(mararn1618-workstreams): add discipline rules for worklog, decisions, README, inputs, switching"
```

---

## Task 7: Append archiving action

**Files:**
- Modify: `mararn1618-workstreams/skills/workstreams/SKILL.md` (append)

- [ ] **Step 1: Append the archiving section**

Append to end of `SKILL.md`:

````markdown

## Archiving action

Triggered by either the session-start bulk prompt (Step 7 of session-start protocol) or an explicit user request like "archive the X workstream".

For each workstream to archive:

1. **Move the folder** into `_archive/`, preserving its name.
   ```bash
   git mv <YYYY-MM-slug> _archive/<YYYY-MM-slug>
   ```
   If the folder is not tracked by git, use `mv` instead. Always move the whole folder as a single unit — do not leave artifacts behind.

2. **Update `CLAUDE.md`:**
   - Remove the entry from the `## Active workstreams` list.
   - Add it to the `## Archived (_archive/)` list with the same one-line hook.

3. **Append a worklog entry to the archived workstream's own `worklog.md`** before you stop working on it, so the archive has a final dated marker:
   ```
   - <ISO ts> — archived (no activity >30 days / user requested)
   ```

4. **Report to the user** which workstreams were moved.

### Reviving from archive

If the user asks to resume an archived workstream:

1. Move it back out of `_archive/` to the root.
2. Update `CLAUDE.md`: move its entry from Archived back to Active.
3. Append a worklog entry: `- <ISO ts> — revived from archive`.
4. Proceed as if resuming an active workstream (read README, tail worklog, read decisions).

### Threshold

Stale threshold for the bulk archive prompt is **30 days** (based on `worklog.md` mtime). This is hard-coded in this skill. If you want to change it, edit the `-mtime +30` value in the mtime check under the session-start protocol and here for consistency.
````

- [ ] **Step 2: Verify the archiving section and mtime constant**

Run:
```bash
grep -c "mtime +30" mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: `2` (once in session-start, once here in archiving — the two places the threshold appears).

Run:
```bash
grep -n "^## Archiving action" mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: one match.

- [ ] **Step 3: Commit**

```bash
git add mararn1618-workstreams/skills/workstreams/SKILL.md
git commit -m "feat(mararn1618-workstreams): add archiving action and revival flow"
```

---

## Task 8: Register the plugin in marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Read the current marketplace.json**

Run:
```bash
cat .claude-plugin/marketplace.json
```
Expected: the JSON from the repo root listing current plugins.

- [ ] **Step 2: Add the new plugin entry**

Append a new object to the `plugins` array, after the last existing entry (currently `mararn1618-kleinanzeigen`). The entry:

```json
{
  "name": "mararn1618-workstreams",
  "source": "./mararn1618-workstreams",
  "description": "Turn any folder into a stateless, resumable Claude workspace: per-topic workstream folders with worklog, decisions, dated inputs, and a self-maintained CLAUDE.md index. Kill the session anytime, resume from disk.",
  "version": "0.1.0"
}
```

Make sure the trailing comma is correct on the previous entry and there is NO trailing comma after the new entry.

- [ ] **Step 3: Verify JSON is valid and the new entry matches plugin.json**

Run:
```bash
python3 -c "
import json
m = json.load(open('.claude-plugin/marketplace.json'))
p = json.load(open('mararn1618-workstreams/.claude-plugin/plugin.json'))
entry = next(e for e in m['plugins'] if e['name'] == 'mararn1618-workstreams')
assert entry['version'] == p['version'], f\"version mismatch: {entry['version']} != {p['version']}\"
assert entry['source'] == './mararn1618-workstreams'
print('ok', entry['name'], entry['version'])
"
```
Expected: `ok mararn1618-workstreams 0.1.0`

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat(mararn1618-workstreams): register plugin v0.1.0 in marketplace"
```

---

## Task 9: End-to-end dry-run in a scratch folder

**Files:**
- Create (temporarily): `/tmp/workstreams-dryrun/` — a throwaway scratch folder

This is the verification step. The skill has no executable tests, so we verify by running the protocol by hand in a scratch folder and confirming each step works exactly as SKILL.md describes. If any step is ambiguous or produces the wrong output, fix the SKILL.md section and re-run.

- [ ] **Step 1: Create scratch folder**

Run:
```bash
rm -rf /tmp/workstreams-dryrun && mkdir /tmp/workstreams-dryrun
```
Expected: no output, empty folder exists.

- [ ] **Step 2: Manually perform the Scaffold action**

Following the "Scaffold action" section of SKILL.md exactly:

1. Create `/tmp/workstreams-dryrun/_archive/` (empty).
2. Create `/tmp/workstreams-dryrun/CLAUDE.md` with the exact template from SKILL.md.

Verify:
```bash
ls -la /tmp/workstreams-dryrun/
```
Expected: shows `CLAUDE.md` and `_archive/`.

```bash
grep -c "BEFORE your first response" /tmp/workstreams-dryrun/CLAUDE.md
```
Expected: `1`.

- [ ] **Step 3: Manually create a workstream**

Following the "On confirmed new workstream" steps of the session-start protocol:

- Slug: `test-topic`
- Month: `2026-04`
- Folder: `/tmp/workstreams-dryrun/2026-04-test-topic/`

Create inside it:
- `README.md` with a description, one goal, one non-goal
- `worklog.md` starting with `# Worklog\n\n- 2026-04-14T12:00Z — created workstream\n`
- `decisions.md` starting with `# Decisions\n`
- `context/input/` (empty)

Update `/tmp/workstreams-dryrun/CLAUDE.md`: add `- 2026-04-test-topic — test topic for dry-run` under `## Active workstreams`.

Verify:
```bash
ls /tmp/workstreams-dryrun/2026-04-test-topic/
```
Expected: `README.md`, `context`, `decisions.md`, `worklog.md`.

```bash
grep "2026-04-test-topic" /tmp/workstreams-dryrun/CLAUDE.md
```
Expected: one match, under the Active workstreams section.

- [ ] **Step 4: Exercise the discipline rules**

Append a state-changing worklog entry:
```bash
printf -- "- 2026-04-14T12:05Z — dry-run exercising discipline rules\n" >> /tmp/workstreams-dryrun/2026-04-test-topic/worklog.md
```

Simulate an input: create a fake input file and save it with the dated prefix:
```bash
echo "pretend transcript" > /tmp/fake_transcript.txt
cp /tmp/fake_transcript.txt /tmp/workstreams-dryrun/2026-04-test-topic/context/input/2026-04-14_fake_transcript.txt
rm /tmp/fake_transcript.txt
```

Verify:
```bash
ls /tmp/workstreams-dryrun/2026-04-test-topic/context/input/
```
Expected: `2026-04-14_fake_transcript.txt`.

```bash
tail -n 2 /tmp/workstreams-dryrun/2026-04-test-topic/worklog.md
```
Expected: last two entries (creation + dry-run).

- [ ] **Step 5: Exercise the archiving action**

Move the workstream to `_archive/`:
```bash
mv /tmp/workstreams-dryrun/2026-04-test-topic /tmp/workstreams-dryrun/_archive/
```

Update `/tmp/workstreams-dryrun/CLAUDE.md` by hand: remove the entry from Active workstreams and add it under `## Archived (_archive/)`.

Verify:
```bash
ls /tmp/workstreams-dryrun/_archive/
```
Expected: `2026-04-test-topic`.

```bash
grep -A1 "^## Archived" /tmp/workstreams-dryrun/CLAUDE.md
```
Expected: section header followed by the archived entry.

- [ ] **Step 6: Compare the dry-run against SKILL.md**

Re-read `mararn1618-workstreams/skills/workstreams/SKILL.md` from top to bottom. For every step you performed in the dry-run, check that SKILL.md describes it unambiguously enough for a fresh Claude session to do the same thing without asking follow-ups.

For each ambiguity or missing detail you find, edit SKILL.md inline, then re-run the relevant dry-run step.

Specific sanity checks:
- A fresh session reading only `CLAUDE.md` and `SKILL.md` could figure out what to do with a non-trivial message.
- The runtime protocol steps are in clear order.
- The discipline rules are unambiguous about *when* to write (not just what to write).
- The archiving threshold number appears in both places and matches.
- No TBDs, no "see above", no unresolved references.

- [ ] **Step 7: Clean up scratch folder**

Run:
```bash
rm -rf /tmp/workstreams-dryrun
```
Expected: no output, scratch folder gone.

- [ ] **Step 8: If SKILL.md was edited during the dry-run, commit the fixes**

Run:
```bash
git status
```

If `SKILL.md` shows as modified:
```bash
git add mararn1618-workstreams/skills/workstreams/SKILL.md
git commit -m "fix(mararn1618-workstreams): resolve ambiguities found in dry-run"
```

If not modified, skip this step.

---

## Task 10: Final repo check and version consistency

**Files:**
- Read: `mararn1618-workstreams/.claude-plugin/plugin.json`
- Read: `.claude-plugin/marketplace.json`
- Read: `mararn1618-workstreams/skills/workstreams/SKILL.md`

- [ ] **Step 1: Version consistency check**

Run:
```bash
python3 -c "
import json
p = json.load(open('mararn1618-workstreams/.claude-plugin/plugin.json'))
m = json.load(open('.claude-plugin/marketplace.json'))
entry = next(e for e in m['plugins'] if e['name'] == 'mararn1618-workstreams')
assert p['version'] == entry['version'] == '0.1.0', f\"mismatch: plugin={p['version']}, market={entry['version']}\"
print('versions ok:', p['version'])
"
```
Expected: `versions ok: 0.1.0`

- [ ] **Step 2: Description consistency check**

Run:
```bash
python3 -c "
import json
p = json.load(open('mararn1618-workstreams/.claude-plugin/plugin.json'))
m = json.load(open('.claude-plugin/marketplace.json'))
entry = next(e for e in m['plugins'] if e['name'] == 'mararn1618-workstreams')
assert p['description'] == entry['description'], 'descriptions differ'
print('descriptions ok')
"
```
Expected: `descriptions ok`

- [ ] **Step 3: Skill file size sanity check**

Run:
```bash
wc -l mararn1618-workstreams/skills/workstreams/SKILL.md
```
Expected: a reasonable number (roughly 200–350 lines). If it's under 100, something got lost; if over 500, it's probably too verbose for a v1 skill.

- [ ] **Step 4: Git status clean**

Run:
```bash
git status
```
Expected: `nothing to commit, working tree clean`. All prior commits should already be in place.

- [ ] **Step 5: Recap to the user**

Report what was shipped: plugin folder created, `plugin.json` at v0.1.0, `SKILL.md` with all seven section groups (overview, when-to-use, scaffold, folder layout, session-start protocol, discipline rules, archiving), marketplace entry added, dry-run passed. Mention that the skill is ready to use by scaffolding a folder and starting a session there.

---

## Self-Review

Spec coverage check against `DESIGN.md`:

- **Purpose / goals / non-goals** → covered by Task 2 (overview) and indirectly by Tasks 3–7 (the rules).
- **Interface constraints (Discord no-clear)** → covered by Task 6 Rule 5 (switching rule), which explicitly cites the constraint.
- **Scaffold action (CLAUDE.md template, `_archive/`)** → Task 3.
- **CLAUDE.md template with gate, summary, index** → Task 3 (template written verbatim).
- **Workstream folder layout, naming, file roles** → Task 4.
- **README user-owned, propose-not-rewrite** → Task 6 Rule 3.
- **worklog discipline with red-flag table** → Task 6 Rule 1.
- **decisions log** → Task 6 Rule 2.
- **Dated inputs** → Task 6 Rule 4.
- **Runtime protocol on first message, topic matching, confirm-before-acting, new and existing workstreams** → Task 5.
- **Archive check with 30-day mtime + bulk prompt** → Task 5 step 7 + Task 7.
- **Archiving action (move + index update)** → Task 7.
- **Marketplace wiring: plugin.json, SKILL.md, marketplace.json registration with matching version** → Tasks 1, 2-7, 8.
- **Open questions from DESIGN.md "Open questions for implementation"** → Resolved in Task 2 (frontmatter uses existing `description` convention) and Task 5 (scaffold action is invoked on demand, not automatically, and uses explicit language "Use when the user asks to scaffold...").

No gaps found.

Placeholder scan: no TBDs, no "implement later", no "similar to Task N" without code, no unresolved function/method references. Every step that writes content includes the exact content.

Type consistency: file paths, section headers, and rule numbers are consistent throughout. The `YYYY-MM-<slug>/` format is used identically in Tasks 4, 5, 7, 9. The `worklog.md` entry format is used identically in Tasks 4, 5, 6, 9. The archiving threshold `30` appears in both places (session-start Step 7 and archiving section) and Task 7 Step 2 explicitly verifies the count is 2.
