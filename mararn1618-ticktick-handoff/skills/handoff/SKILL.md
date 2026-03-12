---
description: "Scan all TickTick projects for tasks tagged with [ai:Todo], work on them autonomously, track status via [ai:In Progress], [ai:Blocked], and [ai:Done] title prefixes, and notify via Telegram. Works across any project — just add [ai:Todo] to any task title."
---

# TickTick Handoff

Work on tasks tagged with `[ai:Todo]` across **all** TickTick projects. The user can add `[ai:Todo]` to any task title in any project and Claude will pick it up. Tasks that need human input are moved to `[ai:Blocked]` and re-checked on subsequent runs.

## MCP Dependency

This skill requires the **TickTick MCP server** (`mcp__ticktick__*` tools).
If TickTick tools are not available, stop and tell the user to configure the TickTick MCP server.

## Notification Dependency

This skill uses the **notify-telegram** skill (`/notify-telegram:notify`) for user notifications.
If Telegram is not configured (`~/.claude/telegram.env` missing), warn the user and offer to set it up.

## Status Tracking

Track task status via **title prefixes**:

| Prefix | Meaning |
|---|---|
| `[ai:Todo]` | Ready to be picked up by Claude |
| `[ai:In Progress] ✴️` | Claude is currently working on it |
| `[ai:Blocked] ⛔️` | Claude needs human input — waiting for unblock |
| `[ai:Done] ✅` | Claude finished — awaiting user review |

The icon goes **after the prefix, before the task name** — e.g. `[ai:Blocked] ⛔️ Kaufland Karte freischalten`.

Tasks without an `[ai:*]` prefix are **not for Claude** — never touch them.

Use `mcp__ticktick__update_task` to update the task title with the appropriate prefix.

## Workflow

### Step 1: Scan All Projects

Search across all projects for tasks tagged for Claude:

```
mcp__ticktick__search_tasks(search_term="ai:")
```

From the results, filter tasks whose titles contain `[ai:Todo]`, `[ai:In Progress]`, `[ai:Blocked]`, or `[ai:Done]` (case-insensitive match on the prefix).

Display a summary grouped by project:

```
🤖 AI Tasks
─────────────────
[ai:Todo]:        X tasks
[ai:In Progress]: X tasks
[ai:Blocked]:     X tasks
[ai:Done]:        X tasks

By project:
  🦥 CWP — 2 tasks ([ai:Todo])
  🏠 Haus — 1 task ([ai:Blocked])
  ...
```

### Step 2: Pick Up a Task

Priority order:

1. **`[ai:In Progress]`** — Resume these first. They were interrupted mid-work.
2. **`[ai:Blocked]`** — Re-read the task content. Look for the feedback form (`✏️ YOUR INPUT NEEDED`). If the human has replaced the `___` blanks with actual answers, the task is unblocked — move it back to `[ai:In Progress]` and resume work using the provided answers. Also check for any other new information added below the form. If `___` blanks remain unfilled, the task is still blocked — skip it.
3. **`[ai:Todo]`** — Pick up new work.

If there are no actionable tasks (no Todo, no In Progress, no unblocked Blocked tasks), tell the user and stop.

### Step 3: Move to [ai:In Progress]

Replace `[ai:Todo]` with `[ai:In Progress]` in the task title. Keep the rest of the title unchanged.

```
mcp__ticktick__update_task(
  task_id="<id>",
  project_id="<task's project_id>",
  title="[ai:In Progress] ✴️ <original title without [ai:Todo] prefix>"
)
```

### Step 4: Work on the Task

Read the task content carefully. It may contain:
- **Skills needed** — what tools/skills are required
- **Context** — background information
- **Problem** — what needs to be solved
- **Solution** — expected approach or constraints
- Links, screenshots, or references

Do the actual work. This could be:
- Code changes, research, analysis, file operations
- Browser automation, API calls
- Anything the task describes

**Add progress notes** to the task content as you work, using `mcp__ticktick__update_task` with updated `content`. Append to existing content, never overwrite. Use this format:

```
---
### 🤖 Claude Session — YYYY-MM-DD
**Status:** In Progress / Blocked / Done
**What I did:**
- <bullet points of actions taken>

**Result:**
<outcome or findings>

**Blockers / Questions:**
- <if any, otherwise remove this section>
---
```

### Step 5: Handle Blockers

If you need human input or cannot proceed:

1. **Move to `[ai:Blocked]`** — Replace `[ai:In Progress]` with `[ai:Blocked]` in the task title and **set the due date to today** so it appears on the human's Today list:
   ```
   mcp__ticktick__update_task(
     task_id="<id>",
     project_id="<task's project_id>",
     title="[ai:Blocked] ⛔️ <original title without prefix>",
     due_date="<today's date as YYYY-MM-DDT00:00:00+0000>"
   )
   ```

2. **Add session notes with a feedback form** — Append a session block to the task content that includes a structured feedback form. The form must be compact, visually distinct, and make it obvious where the human should type. Use this format:

   ```
   ---
   ### 🤖 Claude Session — YYYY-MM-DD
   **Status:** Blocked
   **What I did:**
   - <bullet points of actions taken>

   **Blocker:** <one-line summary of why you're stuck>

   ✏️ YOUR INPUT NEEDED
   ▸ <question>: ___
   ▸ <question>: ___
   ▸ <question>: ___
   ---
   ```

   **Form rules:**
   - Each `▸` line is one question. Keep questions short and specific.
   - `___` marks where the human should type their answer (they replace `___` with their response).
   - Only ask what you actually need — 1 to 4 questions max.
   - If a question has known options, list them: `▸ Provider (AWS / GCP / Azure)?: ___`
   - If a question is optional, mark it: `▸ Notes (optional): ___`
   - Do not use box-drawing characters (`│┌└`) — keep lines clean so the human can easily type answers.

   **Example** — task about setting up a cloud deployment:
   ```
   ✏️ YOUR INPUT NEEDED
   ▸ Which cloud provider (AWS / GCP / Azure)?: ___
   ▸ Monthly budget cap?: ___
   ▸ Preferred region (optional): ___
   ```

3. **Notify via Telegram** — Send a notification via `/notify-telegram:notify`. Tell the human to check the task and fill in the form:
   ```
   🤖 AI Task: Blocked — need your input

   Project: <project name>
   Task: <task title>

   <one-line summary of what you need>
   → Please fill in the form in the task description.
   ```

4. **Move on** — Continue to the next actionable task (Step 2 priority order), or stop if none remain.

### Step 6: Verify Completion and Move to [ai:Done]

Before marking a task done, **verify that the work actually meets the task's goals:**

1. **Check for acceptance criteria** — Re-read the task content. Look for explicit goals, acceptance criteria, expected outcomes, or success conditions defined by the human.
2. **Evaluate completion:**
   - If **criteria are defined**: only proceed if all criteria are met. If some criteria are not met, either continue working or move to `[ai:Blocked]` (Step 5) explaining what's remaining.
   - If **no criteria are defined**: use your best judgment — does the work fulfill the intent of the task title and description?
3. **Move to `[ai:Done]`** — Only when satisfied. **Set the due date to today** so it appears on the human's Today list for review:
   ```
   mcp__ticktick__update_task(
     task_id="<id>",
     project_id="<task's project_id>",
     title="[ai:Done] ✅ <original title without prefix>",
     due_date="<today's date as YYYY-MM-DDT00:00:00+0000>"
   )
   ```

4. Add final session notes to the task content (see Step 4 format)

5. Send a Telegram notification via `/notify-telegram:notify`:
   ```
   🤖 AI Task: Completed

   Project: <project name>
   Task: <task title>

   <brief summary of what was done and how criteria were met>
   ```

### Step 7: Continue

After completing a task, check for more [ai:Todo] tasks and repeat from Step 2.
When all tasks are processed, notify the user:

```
🤖 All [ai:Todo] tasks processed — nothing left to pick up.
```

## Rules

1. **NEVER check off / complete tasks** — the user reviews and closes them personally
2. **NEVER touch tasks without `[ai:*]` prefix** — those are not for Claude
3. **NEVER mark `[ai:Done]` unless goals and acceptance criteria (if defined) are met** — if you can't finish, move to `[ai:Blocked]` instead
4. **Always add session notes** to task content for continuity across sessions
5. **Always notify via Telegram** when a task is done, blocked, or unblocked
6. **Preserve existing task content** — append your notes, never overwrite
7. **Always re-check `[ai:Blocked]` tasks** for new information before picking up new `[ai:Todo]` tasks
