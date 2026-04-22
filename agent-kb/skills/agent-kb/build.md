# Build Operation

Scan free-form source paths, cluster findings into numbered domain folders, write curated articles, and create routing files. Optionally scrub for sensitive data at the end.

---

## Step 0: Parse Arguments

The arguments after `build` are: `<target-path> <source1> [source2] ...`

- **First argument** = target path where the KB will be created.
- **Remaining arguments** = source paths to scan (files, folders, URLs). At least one source is required.

If fewer than 2 arguments total, print usage and stop:

```
Usage: /agent-kb build <target-path> <source1> [source2] ...
Example: /agent-kb build ./my-kb ~/notes/project-x ~/transcripts/2026-04
```

### Guard: target already exists

If the target path already exists and contains a `CLAUDE.md`, stop:

> "A knowledge base already exists at `<target-path>`. Delete it first or choose a different target path."

If the target path exists but is empty or has no `CLAUDE.md`, proceed (the build will populate it).

---

## Step 1: Understand the Topic

Before scanning, ask the user one question:

> "What is this knowledge base about? Give me a one-line topic and (optionally) who the primary reader is."

Use the answer to guide relevance filtering in subsequent phases. If the user already provided this context in the conversation before invoking the skill, skip the question and use what they said.

---

## Step 2: Scan Sources (PARALLEL)

Create the target directory if it does not exist.

For each source path, spawn **one sub-agent** using the Agent tool. Send all Agent calls in a **single message** so they run concurrently.

Each sub-agent receives this prompt (adapt the topic from Step 1):

```
You are a source scanner for building a knowledge base about: "<topic>".

Your assigned source path: <source-path>

Instructions:
1. If the path is a directory, use Glob to find all readable files (*.md, *.txt, *.json, *.yaml, *.html, *.csv, *.pdf). For very large directories (>200 files), prioritize files by relevance to the topic.
2. If the path is a single file, read it.
3. Read each relevant file. Skip binary files, images, and files clearly unrelated to the topic.
4. Produce a structured summary with these sections:

## Source: <source-path>
### Files scanned: <count>
### Key topics found
- <bullet list of distinct topics/themes discovered>
### Key entities
- <people, systems, components, processes mentioned>
### Key facts and decisions
- <concrete facts, decisions, dates, numbers worth preserving>
### Relationships
- <how topics/entities connect to each other>
### Notable quotes or passages
- <verbatim passages that are particularly valuable, with source file attribution>
### Source file inventory
- <file-path> -- <one-line description of what this file contains>

Be thorough but compress. The summary should capture everything a knowledge base article author needs without re-reading the originals.
```

Sub-agent configuration:
- `model: "opus"` (strongest model for accurate summarization)
- `allowed-tools: Read, Glob, Grep, Bash`
- Give each agent a descriptive `name` like `scanner-1`, `scanner-2`, etc.

After all sub-agents return, write all summaries to `<target-path>/_build/scan-summaries.md`. This avoids overloading the main agent's context for large source sets. Read from this file during Step 3 clustering. Delete the `_build/` directory at the end of the build (Step 7).

If a scanner sub-agent fails or returns incomplete results, retry it once. If it fails again, report the issue to the user and continue with the remaining summaries.

---

## Step 3: Cluster into Domains and Plan Articles (SEQUENTIAL)

Review all source summaries from Step 2. Identify domain clusters by grouping related topics, then plan specific article filenames per domain.

Rules:
- Each cluster must contain enough material for **at least 2 articles**.
- The first cluster should always be orientation/overview material (glossary, reading order, project summary).
- Clusters are numbered: `01-`, `02-`, ..., in recommended reading order.
- Later-numbered clusters may assume context from earlier ones.
- No "miscellaneous" or "other" catch-all clusters.
- Aim for 5-15 domains, but scale with source volume. 3-4 folders is fine for small source sets.

**Plan article filenames** for each domain. This produces an **article registry** that every writer sub-agent will receive in Step 4, enabling accurate cross-domain linking.

Present the proposed structure to the user:

```
## Proposed KB Structure

Topic: <topic from Step 1>
Source paths scanned: <count>
Total files processed: <count across all scanners>

01-orientation/    "Orientation & Overview"
  - readme.md: "Two-paragraph project summary and ownership model"
  - glossary.md: "Terms and acronyms by domain"
  - reading-order.md: "Audience-specific reading paths"

02-<domain>/    "<Domain Title>"
  - <article-name>.md: "<one-line description>"
  - <article-name>.md: "<one-line description>"

03-<domain>/    "<Domain Title>"
  ...

Shall I proceed with this structure, or would you like changes?
```

Wait for user confirmation. If they request changes, adjust and re-present. Do not proceed to Step 4 until the user confirms.

After confirmation, build the **article registry**: a flat list of every planned article across all domains with its path and description. This registry is passed to every writer in Step 4.

---

## Step 4: Write Articles (PARALLEL)

For each domain cluster, spawn **one sub-agent** using the Agent tool. Send all Agent calls in a **single message** so they run concurrently.

Each sub-agent receives:
- The domain's cluster assignment (folder name, title, which topics belong here)
- The relevant source summaries (only the portions that map to this domain)
- The target path for the domain folder
- The **article registry** from Step 3 (all planned articles across all domains, with paths and descriptions)

Sub-agent prompt template:

```
You are a knowledge base article writer.

Your domain: <NN>-<domain-name> ("<Domain Title>")
Target folder: <target-path>/<NN>-<domain-name>/
Topic context: <topic from Step 1>
Today's date: <YYYY-MM-DD>

Planned articles for YOUR domain:
<list of filenames + descriptions from the article registry for this domain>

Full article registry (all domains — use for cross-linking):
<paste the complete article registry from Step 3>

Source material for this domain:
<paste relevant source summary sections>

Instructions:
1. Write the planned articles for your domain. Stick to the planned filenames unless there is a strong reason to deviate (and report any deviations in your manifest).
2. For each article:
   a. Write YAML frontmatter with three fields:
      ---
      title: <article title>
      scope: <what this article covers and when an agent should read it>
      updated: <today's date YYYY-MM-DD>
      ---
   b. Open with a one-line framing sentence stating what this article is about.
   c. Structure the body with H2/H3 headings.
   d. Cross-link to articles in other domains using the article registry and relative paths (e.g., `../05-c4m-integration/vdm-overview.md`). Weave links into the prose where they add context.
   e. Attribute sources: mention the original file path or document name.
3. Create the domain folder if it does not exist.
4. Write all article files to the folder.
5. Return a manifest listing every file you wrote with a one-line description. Flag any filename deviations from the plan.

Format rules:
- Prose-first, pointer-rich. A cold reader must understand the article standalone.
- Compress, do not copy verbatim. Distill the source into clean, navigable knowledge.
- No "generated by AI" footers, no version metadata, no watermarks.
- Tables welcome for structured comparisons.
- Article filenames: lowercase kebab-case, no number prefixes.

Quality bar: an article is done when (1) it stands alone, (2) claims trace to sources, (3) it compresses rather than copies, (4) vocabulary is consistent.
```

Sub-agent configuration:
- `model: "opus"`
- `allowed-tools: Read, Write, Glob, Bash`
- Give each agent a name like `writer-01-orientation`, `writer-02-business`, etc.

After all sub-agents return, collect all manifests.

---

## Step 5: Create Routing Files (SEQUENTIAL)

After all articles are written, create the CLAUDE.md and AGENTS.md routing files.

### 5a: Subfolder routing files

For each domain folder:

1. List all `.md` files in the folder (excluding `CLAUDE.md` and `AGENTS.md`) using Glob.
2. Read the first 5 lines of each article to extract the frontmatter `title` and `scope`.
3. Build the Contents table with one row per article.
4. Write `CLAUDE.md` using the subfolder format from reference.md.
5. Copy the identical content to `AGENTS.md`.

### 5b: Root routing file

1. List all numbered domain folders.
2. Read each folder's `CLAUDE.md` to extract its `scope` and `description` frontmatter.
3. Build the root Contents table with one row per folder.
4. Write the root `CLAUDE.md` using the root format from reference.md, incorporating:
   - The topic from Step 1 as the KB title/description.
   - A "How to navigate" section.
   - The Contents table.
5. Copy the identical content to `AGENTS.md`.

---

## Step 6: Scrub (PARALLEL, after confirmation)

After the KB is fully built, proceed to the scrub phase. Read [scrub.md](scrub.md) and follow its instructions.

---

## Step 7: Report

Print a summary:

```
## Knowledge Base Built

Target: <target-path>
Topic: <topic>
Domains: <count> folders
Articles: <count> total
Sources scanned: <count> paths

Structure:
  01-<name>/  (<N> articles)
  02-<name>/  (<N> articles)
  ...

Routing files: CLAUDE.md + AGENTS.md at every level.

The KB is ready. Any agent can query it by reading <target-path>/CLAUDE.md (or AGENTS.md) and navigating the Contents tables.
```

Clean up: delete `<target-path>/_build/` if it exists.

---

## Important Rules

- Never modify source files. The build is read-only on sources, write-only on the target.
- Always create both CLAUDE.md and AGENTS.md with identical content.
- Article filenames are kebab-case, no number prefixes.
- Folder names are numbered with zero-padded two-digit prefixes.
- All sub-agents must use `model: "opus"` for quality.
- Sub-agents for scanning (Step 2) and writing (Step 4) must be spawned in a single message each (parallel, not sequential).
