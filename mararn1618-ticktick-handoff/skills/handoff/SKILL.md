---
description: "Scan all TickTick projects for tasks tagged with [ai:Todo], work on them autonomously, track status via [ai:In Progress] and [ai:Done] title prefixes, and notify via Telegram. Works across any project — just add [ai:Todo] to any task title."
---

# TickTick Handoff

Work on tasks tagged with `[ai:Todo]` across **all** TickTick projects. The user can add `[ai:Todo]` to any task title in any project and Claude will pick it up.

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
| `[ai:In Progress]` | Claude is currently working on it |
| `[ai:Done]` | Claude finished — awaiting user review |

Tasks without an `[ai:*]` prefix are **not for Claude** — never touch them.

Use `mcp__ticktick__update_task` to update the task title with the appropriate prefix.

## Workflow

### Step 1: Scan All Projects

Search across all projects for tasks tagged for Claude:

```
mcp__ticktick__search_tasks(search_term="ai:")
```

From the results, filter tasks whose titles contain `[ai:Todo]`, `[ai:In Progress]`, or `[ai:Done]` (case-insensitive match on the prefix).

Display a summary grouped by project:

```
🤖 AI Tasks
─────────────────
[ai:Todo]:        X tasks
[ai:In Progress]: X tasks
[ai:Done]:        X tasks

By project:
  🦥 CWP — 2 tasks ([ai:Todo])
  🏠 Haus — 1 task ([ai:In Progress])
  ...
```

### Step 2: Pick Up an [ai:Todo] Task

- Only pick up tasks with `[ai:Todo]` prefix.
- If there are `[ai:In Progress]` tasks, resume those first before picking up new ones.
- If there are no `[ai:Todo]` or `[ai:In Progress]` tasks, tell the user and stop.

### Step 3: Move to [ai:In Progress]

Replace `[ai:Todo]` with `[ai:In Progress]` in the task title. Keep the rest of the title unchanged.

```
mcp__ticktick__update_task(
  task_id="<id>",
  project_id="<task's project_id>",
  title="[ai:In Progress] <original title without [ai:Todo] prefix>"
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

If you need user input or are blocked:
1. Update the task content with what you need
2. Send a Telegram notification via `/notify-telegram:notify`:
   ```
   🤖 AI Task: Need your input

   Project: <project name>
   Task: <task title>

   <what you need from the user>
   ```
3. Move on to the next [ai:Todo] task if there is one, or stop and wait

### Step 6: Move to [ai:Done]

When the task is complete:

1. Replace `[ai:In Progress]` with `[ai:Done]` in the task title:
   ```
   mcp__ticktick__update_task(
     task_id="<id>",
     project_id="<task's project_id>",
     title="[ai:Done] <original title without prefix>"
   )
   ```

2. Add final session notes to the task content (see Step 4 format)

3. Send a Telegram notification via `/notify-telegram:notify`:
   ```
   🤖 AI Task: Completed

   Project: <project name>
   Task: <task title>

   <brief summary of what was done>
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
3. **Always add session notes** to task content for continuity across sessions
4. **Always notify via Telegram** when a task is done or when you need input
5. **Preserve existing task content** — append your notes, never overwrite
