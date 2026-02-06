---
description: "Create a structured Markdown project plan with phases, tasks, ownership, and acceptance criteria."
---

# Plan Documents — Reference

## What is a Plan?

A structured, human-readable project plan in Markdown. It tracks phases, tasks, ownership, and acceptance criteria. Designed to be used collaboratively between humans and AI agents in Obsidian.

## Rules

### Structure

1. **Header** — title, ticket reference, last-updated date
2. **Living document notice** — blockquote stating the plan may change, but human must approve changes
3. **Reference & context files** — table listing all input/output files the plan depends on (file path + purpose)
4. **Phases** — numbered sections, each with a goal, tasks, acceptance criteria, and artifacts

### Phases

- Each phase has a **Goal** (one sentence)
- Phases are sequential — later phases depend on earlier ones
- Typical progression: Analysis → Development → Preparation → Execution → Implementation

### Tasks

- Tasks are **bullet points with checkboxes** (`- [ ]` / `- [x]`)
- Format: `- [ ] **{phase}.{number}** ({owner}) {description}`
- Owner is always annotated: `AI`, `HUMAN — {name}`, or `AI + HUMAN — {name}`
- Tasks should be concrete and verifiable — not vague
- When an AI agent completes a task, it checks off the checkbox

### Acceptance Criteria

- Listed as checkboxes after the tasks: `- [ ] {criterion}`
- Measurable and specific — not "looks good" but "each option has a pros/cons table"
- Checked off when met

### Artifacts

- Listed after acceptance criteria
- Reference the output files that this phase produces

### General

- Use bold for task numbers and phase names
- Keep everything scannable — no long paragraphs
- Reference files use backtick formatting: `path/to/file.md`
- The reference table in the header must be kept up to date as new files are created

## Updating the Plan

- AI agents may **suggest** changes (new tasks, reordering, scope changes)
- AI agents must **not** modify the plan without human approval
- When updating: change the `Last Updated` date and check off completed items

## Example Plan

```markdown
# Project X — Plan

**Ticket:** PROJ-1234 | **Last Updated:** 2026-02-06

> **Living document.** This plan may be updated as work progresses. Any changes to scope, tasks, or phases must be discussed with and approved by {human name} before being applied.

## Reference & Context Files

| File | Purpose |
|---|---|
| `context/requirements.md` | Original requirements from stakeholder |
| `context/email-thread.md` | Email discussion with key decisions |
| `output/analysis.md` | Analysis document produced in Phase 1 |
| `workshop/presentation.md` | Slide deck for alignment meeting |

---

## Phase 1: Research & Analysis

**Goal:** Understand the problem space and document findings.

- [x] **1.1** (AI) Gather requirements from ticket and context files
- [x] **1.2** (AI) Analyze current system and document findings
- [x] **1.3** (HUMAN — Alice) Validate findings and add missing context
- [x] **1.4** (AI) Write analysis document (`output/analysis.md`)

**Acceptance Criteria:**
- [x] Current state documented with diagrams
- [x] Key challenges identified
- [x] Stakeholder concerns captured

**Artifacts:** `output/analysis.md`

---

## Phase 2: Option Development

**Goal:** Create detailed options for the team to evaluate.

- [x] **2.1** (AI) Develop Option 1 — full detail
- [ ] **2.2** (AI) Develop Option 2 — full detail
- [ ] **2.3** (HUMAN — Alice) Review options for accuracy
- [ ] **2.4** (HUMAN — Alice + AI) Define Option 3 (compromise)
- [ ] **2.5** (AI) Develop Option 3 — full detail

**Acceptance Criteria:**
- [ ] Each option has: description, impact table, pros/cons, open points
- [ ] All options follow the same structure
- [ ] Options reviewed by Alice

**Artifacts:** `workshop/01-option-a.md`, `workshop/02-option-b.md`, `workshop/03-option-c.md`

---

## Phase 3: Workshop & Decision

**Goal:** Align stakeholders and choose an option.

- [ ] **3.1** (AI) Create presentation slides
- [ ] **3.2** (HUMAN — Alice) Review and finalize presentation
- [ ] **3.3** (HUMAN — Alice) Schedule and run the workshop
- [ ] **3.4** (HUMAN — all) Reach decision
- [ ] **3.5** (AI) Document decision and action items

**Acceptance Criteria:**
- [ ] One option chosen
- [ ] Decision rationale documented
- [ ] Action items assigned with owners

---

## Phase 4: Implementation

**Goal:** Execute the chosen option.

- [ ] **4.1** (AI + HUMAN — Bob) Create implementation plan
- [ ] **4.2** (HUMAN — Bob) Execute implementation
- [ ] **4.3** (HUMAN — Alice) Communicate to stakeholders

**Acceptance Criteria:**
- [ ] Implementation complete
- [ ] Stakeholders informed
```
