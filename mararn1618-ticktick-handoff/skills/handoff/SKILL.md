---
description: "Scan TickTick for tasks tagged with 'ai', 'handoff', or 'delegate', work on them autonomously, track status via Kanban columns in the Handoff project, and notify via Telegram."
---

# TickTick Handoff

Work on tasks tagged with `ai`, `handoff`, or `delegate` across **all** TickTick projects. The user can add any of these tags to any task and Claude will pick it up. Status is tracked via Kanban columns in the **👊Handoff** project.

## MCP Dependency

This skill requires the **TickTick MCP server** (`mcp__claude_ai_Ticktick_MCP_official__*` tools).
If TickTick tools are not available, stop and tell the user to configure the TickTick MCP server.

## Notification Dependency

This skill uses the **notify-telegram** skill (`/notify-telegram:notify`) for user notifications.
If Telegram is not configured (`~/.claude/telegram.env` missing), warn the user and offer to set it up.

## Critical: Column Updates Must Be Separate API Calls

**NEVER bundle `columnId` changes with `title` or `content` changes in a single `update_task` call.** The TickTick API silently ignores column changes when other fields are updated simultaneously.

Always use **two sequential calls**:
1. First call: update title, content, dueDate, etc.
2. Second call: update columnId only

## Constants

### Handoff Project

| Key | Value |
|-----|-------|
| Project ID | `69b03f471194d102ebcb3044` |
| Project Name | 👊Handoff |
| View Mode | kanban |

### Column IDs

| Column | ID | AI behavior |
|--------|----|-------------|
| **Backlog** | `69b03f5a01cb1102ebcb3046` | Skip -- AI does not pick these up automatically |
| **Todo** | `69b03f6b03bc9102ebcb3375` | Ready for AI pickup |
| **In Progress** | `69b03f7303879102ebcb348f` | AI is currently working on it |
| **Blocked** | `69c65b34fc1f51066dabb200` | AI needs human input |
| **Done** | `69b03f76038b9102ebcb3496` | Finished, awaiting user review |

### Delegation Tags

Any of these tags marks a task for Claude: **`ai`**, **`handoff`**, **`delegate`**

All three are synonyms. The user can use whichever they prefer.

### Status Icons (Title Prefix)

Status is tracked via columns, but icons are added to the title for visual clarity:

| Status | Icon prefix | Example title |
|--------|-------------|---------------|
| Backlog / Todo | *(none)* | `Kaufland Karte freischalten` |
| In Progress | `✴️` | `✴️ Kaufland Karte freischalten` |
| Blocked | `⛔️` | `⛔️ Kaufland Karte freischalten` |
| Done | `✅` | `✅ Kaufland Karte freischalten` |

When changing status, **replace** the existing icon (if any) with the new one. Strip any old `[ai:*]` prefixes if encountered (migration from v0.5).

## Workflow

### Step 1: Scan All Projects

Find all tasks tagged for Claude. Run three filter queries (one per tag):

```
mcp__claude_ai_Ticktick_MCP_official__filter_tasks(filter={tag: ["ai"], status: [0]})
mcp__claude_ai_Ticktick_MCP_official__filter_tasks(filter={tag: ["handoff"], status: [0]})
mcp__claude_ai_Ticktick_MCP_official__filter_tasks(filter={tag: ["delegate"], status: [0]})
```

Deduplicate by task ID (a task may have multiple tags).

Also load the Handoff project to get column definitions:

```
mcp__claude_ai_Ticktick_MCP_official__get_project_with_undone_tasks(project_id="69b03f471194d102ebcb3044")
```

Display a summary:

```
🤖 AI Tasks
─────────────────
Backlog:     X tasks (skipped)
Todo:        X tasks
In Progress: X tasks
Blocked:     X tasks
Done:        X tasks

Pending from other projects:
  🏠 Haus -- 1 task (will move to 👊Handoff)
  ...
```

### Step 2: Route & Classify

For each tagged task, determine its situation:

| Situation | Action |
|-----------|--------|
| In 👊Handoff, Column = In Progress | Resume (highest priority) |
| In 👊Handoff, Column = Blocked | Check if unblocked (second priority) |
| In 👊Handoff, Column = Todo | Pick up (third priority) |
| In 👊Handoff, Column = Backlog | Skip |
| In 👊Handoff, Column = Done | Skip |
| **In another project** | Move to 👊Handoff (see below), then treat as Todo |

**Moving from another project:**

1. Note the source project in the task content:
   ```
   📍 Origin: <Project Name> (<project_id>)
   ```
2. Move the task:
   ```
   mcp__claude_ai_Ticktick_MCP_official__move_task(moves=[{
     taskId: "<id>",
     fromProjectId: "<source_project_id>",
     toProjectId: "69b03f471194d102ebcb3044"
   }])
   ```
3. Set column to Todo (separate call -- see "Critical" section above):
   ```
   mcp__claude_ai_Ticktick_MCP_official__update_task(task_id="<id>", task={
     projectId: "69b03f471194d102ebcb3044",
     columnId: "69b03f6b03bc9102ebcb3375"
   })
   ```

### Step 3: Pick Up a Task

Priority order:

1. **In Progress** -- Resume these first. They were interrupted mid-work.
2. **Blocked** -- Re-read the task content. Look for the feedback form (`YOUR INPUT NEEDED`). If the human has replaced the `___` blanks with actual answers, the task is unblocked -- move it to In Progress and resume. If `___` blanks remain unfilled, skip it.
3. **Todo** -- Pick up new work.

If there are no actionable tasks, tell the user and stop.

### Step 4: Move to In Progress

Update title first, then column in a **separate call** (see "Critical" section):

```
// Call 1: update title
mcp__claude_ai_Ticktick_MCP_official__update_task(task_id="<id>", task={
  projectId: "69b03f471194d102ebcb3044",
  title: "✴️ <clean task title>"
})

// Call 2: update column (must be separate!)
mcp__claude_ai_Ticktick_MCP_official__update_task(task_id="<id>", task={
  projectId: "69b03f471194d102ebcb3044",
  columnId: "69b03f7303879102ebcb348f"
})
```

"Clean task title" means: strip any existing status icon (✴️/⛔️/✅) or old `[ai:*]` prefix from the front.

### Step 5: Work on the Task

Read the task content carefully. It may contain:
- **Skills needed** -- what tools/skills are required
- **Context** -- background information
- **Problem** -- what needs to be solved
- **Solution** -- expected approach or constraints
- Links, screenshots, or references

Do the actual work. This could be:
- Code changes, research, analysis, file operations
- Browser automation, API calls
- Anything the task describes

**Add progress notes** to the task content as you work. Append to existing content, never overwrite. Use this format:

```
---
### 🤖 Claude Session -- YYYY-MM-DD
**Status:** In Progress / Blocked / Done
**What I did:**
- <bullet points of actions taken>

**Result:**
<outcome or findings>

**Blockers / Questions:**
- <if any, otherwise remove this section>
---
```

### Step 6: Handle Blockers

If you need human input or cannot proceed:

1. **Move to Blocked column** and update the title icon. **Set the due date to today** so it appears on the human's Today list. Use **two separate calls**:
   ```
   // Call 1: update title + due date
   mcp__claude_ai_Ticktick_MCP_official__update_task(task_id="<id>", task={
     projectId: "69b03f471194d102ebcb3044",
     title: "⛔️ <clean task title>",
     dueDate: "<today as YYYY-MM-DDT00:00:00.000+0000>"
   })

   // Call 2: update column (must be separate!)
   mcp__claude_ai_Ticktick_MCP_official__update_task(task_id="<id>", task={
     projectId: "69b03f471194d102ebcb3044",
     columnId: "69c65b34fc1f51066dabb200"
   })
   ```

2. **Add session notes with a feedback form** -- Append a session block to the task content that includes a structured feedback form:

   ```
   ---
   ### 🤖 Claude Session -- YYYY-MM-DD
   **Status:** Blocked
   **What I did:**
   - <bullet points of actions taken>

   **Blocker:** <one-line summary of why you're stuck>

   YOUR INPUT NEEDED
   > <question>: ___
   > <question>: ___
   > <question>: ___
   ---
   ```

   **Form rules:**
   - Each `>` line is one question. Keep questions short and specific.
   - `___` marks where the human should type their answer (they replace `___` with their response).
   - Only ask what you actually need -- 1 to 4 questions max.
   - If a question has known options, list them: `> Provider (AWS / GCP / Azure)?: ___`
   - If a question is optional, mark it: `> Notes (optional): ___`

3. **Notify via Telegram** -- Send a notification via `/notify-telegram:notify`:
   ```
   🤖 AI Task: Blocked

   Task: <task title>

   <one-line summary of what you need>
   Please check the task in TickTick and fill in the form.
   ```

4. **Move on** -- Continue to the next actionable task (Step 3 priority order), or stop if none remain.

### Step 7: Verify Completion and Move to Done

Before marking a task done, **verify that the work actually meets the task's goals:**

1. **Check for acceptance criteria** -- Re-read the task content. Look for explicit goals, acceptance criteria, expected outcomes, or success conditions.
2. **Evaluate completion:**
   - If **criteria are defined**: only proceed if all criteria are met. If not, continue working or move to Blocked (Step 6).
   - If **no criteria are defined**: use your best judgment.
3. **Move to Done column** and update the title icon. **Set the due date to today**. Use **two separate calls**:
   ```
   // Call 1: update title + due date
   mcp__claude_ai_Ticktick_MCP_official__update_task(task_id="<id>", task={
     projectId: "69b03f471194d102ebcb3044",
     title: "✅ <clean task title>",
     dueDate: "<today as YYYY-MM-DDT00:00:00.000+0000>"
   })

   // Call 2: update column (must be separate!)
   mcp__claude_ai_Ticktick_MCP_official__update_task(task_id="<id>", task={
     projectId: "69b03f471194d102ebcb3044",
     columnId: "69b03f76038b9102ebcb3496"
   })
   ```

4. Add final session notes to the task content (see Step 5 format).

5. Send a Telegram notification via `/notify-telegram:notify`:
   ```
   🤖 AI Task: Completed

   Task: <task title>

   <brief summary of what was done>
   ```

### Step 8: Continue

After completing a task, check for more tasks and repeat from Step 3.
When all tasks are processed, notify the user:

```
🤖 All AI tasks processed -- nothing left to pick up.
```

## Legacy Migration

If you encounter tasks with old-style `[ai:Todo]`, `[ai:In Progress]`, `[ai:Blocked]`, or `[ai:Done]` title prefixes (from v0.5):

1. Add the `ai` tag to the task if not already present
2. Strip the `[ai:*]` prefix from the title
3. Add the appropriate status icon
4. Move the task to the correct column based on the old prefix:
   - `[ai:Todo]` -> Todo column
   - `[ai:In Progress]` -> In Progress column
   - `[ai:Blocked]` -> Blocked column, keep ⛔️ icon
   - `[ai:Done]` -> Done column, keep ✅ icon

Do this silently as part of normal processing.

## Backlog Tasks

Tasks in the **Backlog** column are not picked up automatically. If the user asks Claude to review, prioritize, or suggest from the backlog, Claude may do so -- but never start working on a Backlog task without being asked.

## Rules

1. **NEVER check off / complete tasks** -- the user reviews and closes them personally
2. **NEVER touch tasks without a delegation tag** (`ai`, `handoff`, `delegate`) -- those are not for Claude
3. **NEVER move to Done unless goals and acceptance criteria (if defined) are met** -- if you can't finish, move to Blocked instead
4. **Always add session notes** to task content for continuity across sessions
5. **Always notify via Telegram** when a task is done, blocked, or unblocked
6. **Preserve existing task content** -- append your notes, never overwrite
7. **Always re-check Blocked tasks** for new information before picking up new Todo tasks
8. **Keep delegation tags** -- never remove the `ai`/`handoff`/`delegate` tag, even after Done (history)
