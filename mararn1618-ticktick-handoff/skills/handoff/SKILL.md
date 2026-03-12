---
description: "Process tasks from the TickTick Handoff board. Scans for [Todo] tasks, works on them autonomously, tracks status via title prefixes, and notifies via Telegram when done or when input is needed."
---

# TickTick Handoff

Process tasks from the **👊Handoff** TickTick kanban board autonomously.

## MCP Dependency

This skill requires the **TickTick MCP server** (`mcp__ticktick__*` tools).
If TickTick tools are not available, stop and tell the user to configure the TickTick MCP server.

## Notification Dependency

This skill uses the **notify-telegram** skill (`/notify-telegram:notify`) for user notifications.
If Telegram is not configured (`~/.claude/telegram.env` missing), warn the user and offer to set it up.

## Constants

- **Project ID:** `69b03f471194d102ebcb3044`
- **Project Name:** 👊Handoff

## Status Tracking

Track task status via **title prefixes**:

| Prefix | Meaning |
|---|---|
| *(no prefix)* | Backlog — do NOT work on these |
| `[Todo]` | Ready to be picked up |
| `[In Progress]` | Currently being worked on |
| `[Done]` | Finished, awaiting user review |

Use `mcp__ticktick__update_task` to update the task title with the appropriate prefix.

## Workflow

### Step 1: Scan the Board

Fetch all tasks from the Handoff project:

```
mcp__ticktick__get_project_tasks(project_id="69b03f471194d102ebcb3044")
```

Categorize tasks by their title prefix into Backlog, [Todo], [In Progress], and [Done].

Display a summary to the user:
```
👊 Handoff Board
─────────────────
Backlog:      X tasks
[Todo]:       X tasks
[In Progress]: X tasks
[Done]:       X tasks
```

### Step 2: Pick Up a [Todo] Task

- Only pick up tasks with `[Todo]` prefix. NEVER start Backlog tasks.
- If there are `[In Progress]` tasks, resume those first before picking up new ones.
- If there are no [Todo] or [In Progress] tasks, notify the user that the board is empty and stop.

### Step 3: Move to [In Progress]

Update the task title to replace `[Todo]` with `[In Progress]`:

```
mcp__ticktick__update_task(
  task_id="<id>",
  project_id="69b03f471194d102ebcb3044",
  title="[In Progress] <original title without prefix>"
)
```

### Step 4: Work on the Task

Read the task content carefully. It may contain:
- **Context** — background information
- **Problem** — what needs to be solved
- **Solution** — expected approach or constraints
- Links, screenshots, or references

Do the actual work. This could be:
- Code changes, research, analysis, file operations
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

If you need user input or are blocked:
1. Update the task content with what you need
2. Send a Telegram notification via `/notify-telegram:notify`:
   ```
   👊 Handoff: Need your input

   Task: <task title>

   <what you need from the user>
   ```
3. Move on to the next [Todo] task if there is one, or stop and wait

### Step 6: Move to [Done]

When the task is complete:

1. Update the task title to replace `[In Progress]` with `[Done]`:
   ```
   mcp__ticktick__update_task(
     task_id="<id>",
     project_id="69b03f471194d102ebcb3044",
     title="[Done] <original title without prefix>"
   )
   ```

2. Add final session notes to the task content (see Step 4 format)

3. Send a Telegram notification via `/notify-telegram:notify`:
   ```
   👊 Handoff: Task completed

   Task: <task title>

   <brief summary of what was done>
   ```

### Step 7: Continue

After completing a task, check for more [Todo] tasks and repeat from Step 2.
When all [Todo] tasks are processed, notify the user:

```
👊 Handoff board clear — no more [Todo] tasks.
```

## Rules

1. **NEVER check off / complete tasks** — the user reviews and closes them personally
2. **NEVER start Backlog tasks** — only [Todo] and resuming [In Progress]
3. **Always add session notes** to task content for continuity across sessions
4. **Always notify via Telegram** when a task is done or when you need input
5. **Preserve existing task content** — append your notes, never overwrite
