---
description: "Produce a condensed session-handover document so a fresh Claude session can continue your current work without context loss. Writes to docs/handovers/YYYY-MM-DD_HH-MM_<topic_hint>.md. Works standalone - no dependency on the other skills in this plugin."
model: opus
---

# /handover-session

You are producing a **session-handover document** for the current conversation. The goal: a fresh Claude session with no memory of this conversation should be able to pick up the work and continue seamlessly, using only the handover document plus the files it references.

This skill is **self-contained**. It does not require the other `discuss-plan-implement` skills to have been run, and it does not auto-search for their outputs. Invoke it from any session at any point - inside a discuss-plan-implement workflow, inside another plugin's workflow, or in a plain ad-hoc session.

## Purpose

Preserve context. Long sessions accumulate decisions, findings, constraints, user preferences, and scope boundaries that live only in the conversation. If the session ends (context limit, machine switch, teammate taking over, extended break, day-end), that context is lost. A handover document captures everything significant so the next agent starts warm.

The document must be:
- **Self-sufficient** - a fresh agent starts here and has everything needed.
- **Condensed** - not a conversation dump; synthesized findings only.
- **Skimmable** - structured so a new agent can orient in 5 minutes.
- **Honest** - captures open threads and unknowns, not just decisions.

## Rules

1. **Do not write code.** This is a documentation-only step.
2. **Do not invent content.** If you do not remember something, either omit it or flag it as unknown. Never fabricate decisions, stakeholders, findings, or constraints.
3. **Inherit hard constraints from the current conversation.** Especially surface explicit do-not rules, scope limits, sensitivity constraints, and file-path restrictions the user has stated. These must be visible in the handover.
4. **Plain Markdown only.** No tool-specific syntax (no Obsidian wiki-links `[[...]]`, no file embeds `![[...]]`). The handover may be read in any environment.
5. **Do not auto-search for prior-phase artifacts.** If the user has referenced a discussion, plan, spec, ticket, or other document, record that reference by path. Do not scan `docs/discussions/`, `docs/plans/`, or any other conventional directory looking for context. Treat prior-phase artifacts as optional context the user supplies, never as required inputs.
6. **Synthesize the topic hint yourself.** Do not ask the user to write the filename. Propose a concise snake_case phrase that packs the workstream and its context, show it to the user, and accept an override if they want a different one.

## Flow

1. **Confirm the topic hint.** Synthesize a concise snake_case hint from the conversation that packs the workstream and context (e.g., `borrower_portal_handover_to_christof_plan`, `invoice_pdf_parser_debug_edge_cases`). Show it to the user; accept an override.
2. **Confirm the output directory.** Default `docs/handovers/` (create if missing). Accept an override.
3. **Compose the filename:** `YYYY-MM-DD_HH-MM_<topic_hint>.md` using current local date and time.
4. **Synthesize the handover** from conversation memory (see Output).
5. **Write the file.**
6. **Report the path** to the human in the exit format.

## Output

Write to `<output_dir>/<filename>` where:
- `<output_dir>` defaults to `docs/handovers/`.
- `<filename>` is `YYYY-MM-DD_HH-MM_<topic_hint>.md`:
  - `YYYY-MM-DD` - today's date.
  - `HH-MM` - current local hour and minute (24h, hyphen-separated).
  - `<topic_hint>` - concise snake_case phrase describing what the session was about.

Examples of good filenames:
- `2026-04-17_10-13_borrower_portal_handover_to_christof_plan.md`
- `2026-04-17_14-02_invoice_pdf_parser_debug_edge_cases.md`
- `2026-04-17_16-45_kyma_deployment_iam_config_alignment.md`

Create the output directory if it does not exist.

**File format (exact structure):**

```markdown
---
created: <YYYY-MM-DD HH:MM>
purpose: <one-sentence statement of what workstream this handover preserves>
# Optional - include only when the user has referenced these:
# discussion: <path>
# plan: <path>
# spec: <path>
# ticket: <id or url>
---

# Session Handover: <workstream name>

## Mission
<1-2 paragraphs: what the workstream is, current status, what outcome is being worked toward.>

## Scope constraint
<Hard limits: working directories, files / folders to avoid, anything the user explicitly said not to touch. Make these visible.>

## The user
<Role, preferences, communication style, anything about how they like to work. Distilled from conversation, not invented.>

## Stakeholders (if any)
<People, teams, or external parties relevant to the workstream. Omit section if none.>

## Key decisions
<List of decisions reached with the user during this session. Each decision: what was decided + why (rationale from conversation). Do not invent decisions that were not made.>

## Constraints
<Technical, organizational, time, or sensitivity constraints surfaced in the session.>

## Out of scope
<Explicitly excluded items.>

## Significant findings
<Distilled research outputs, analyses, discoveries. Group by topic. Not every detail - only what a new agent needs so it does not repeat the work.>

## Open threads and risks
<Unresolved questions, decisions pending, risks identified. Be honest - do not hide unknowns.>

## Relevant files and locations
<Tree or list of key files the next agent will touch or reference. Annotate what each contains.>

## External references
<URLs, SharePoint links, tickets, wiki pages, other docs - whatever the user mentioned.>

## Where to pick up
<Most likely next actions, in order. What would a fresh agent do first?>

## Communication preferences
<Distilled from conversation: terseness, language, formatting rules, sensitivity rules.>

## References
- <paths to any internal documents the user referenced>
```

## Exit

After writing the file, tell the human:

> Handover written to `<output_dir>/<filename>`.
> A fresh Claude session can continue from this file plus the referenced materials.

Stop.
