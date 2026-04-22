---
name: agent-kb
description: "Build agent-first knowledge bases from free-form sources. Scans source paths in parallel, clusters findings into numbered domain folders, writes curated prose-first articles, and generates CLAUDE.md + AGENTS.md routing files at every level. Includes automatic sensitive-data scrubbing. Use when the user says 'build a knowledge base', 'create a KB from these sources', 'make this queryable for agents', 'agent-first KB', 'knowledge base from my notes', 'scan these sources into a KB', 'organize my notes for handover', 'create a handover package', 'turn these docs into something an agent can read', 'make my research queryable', 'index these files for AI', 'onboarding knowledge base', 'compile notes into a KB', or explicitly invokes /agent-kb. Also trigger when the user has a collection of scattered notes, transcripts, or documents about a topic and wants them consolidated into a structured, navigable knowledge base."
argument-hint: build <target-path> <source1> [source2] ...
context: fork
agent: general-purpose
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# agent-kb

Build agent-first knowledge bases from free-form sources. The result is a self-contained folder tree with numbered domain folders, curated markdown articles, and CLAUDE.md + AGENTS.md routing files that any AI agent can navigate.

Read [reference.md](reference.md) first. It defines the output format: routing file structure, article frontmatter, folder naming, and the dual CLAUDE.md/AGENTS.md convention.

## Subcommand Routing

Check `$ARGUMENTS`. If `$ARGUMENTS` is completely empty, skip to the **Help Text** section below.

Parse the **first word** of `$ARGUMENTS` to determine the operation.

| First word | Remaining words | Instruction file |
|------------|-----------------|------------------|
| `build` | `<target-path> <source1> [source2] ...` (required) | [build.md](build.md) |
| `help` | -- | Show the Help Text below |

If the first word does not match any row above, assume it is a path and treat the entire `$ARGUMENTS` as if prefixed with `build`. Read [build.md](build.md).

After reading reference.md, read and follow the instruction file from the matched row.

## Help Text

Only show this when `$ARGUMENTS` is empty or the first word is `help`. Output and stop:

```
## agent-kb

Build agent-first knowledge bases from free-form sources.

Usage:
  /agent-kb build <target-path> <source1> [source2] ...   -- Scan sources, build KB at target
  /agent-kb <target-path> <source1> [source2] ...         -- Same (build is the default)

Examples:
  /agent-kb build ./my-kb ~/notes/project-x ~/transcripts/2026-04
  /agent-kb ./handover-kb ~/obsidian/project ~/confluence-export ~/code/src

The build pipeline:
  1. Scan    -- read each source path in parallel (one sub-agent per source)
  2. Cluster -- propose numbered domain folders from all findings
  3. Write   -- produce curated articles in parallel (one sub-agent per domain)
  4. Index   -- create CLAUDE.md + AGENTS.md routing files at every level
  5. Scrub   -- (after confirmation) scan for sensitive data in parallel

Output: a self-contained folder tree queryable by any AI agent via its CLAUDE.md / AGENTS.md routing hierarchy.
```
